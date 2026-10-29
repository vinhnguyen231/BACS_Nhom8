import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.diagrams import (
    ClassModel, Relationship, find_undefined_classes,
    find_undocumented_data_terms, relationship_count_by_kind,
)


def test_relationship_rejects_invalid_kind():
    with pytest.raises(ValueError):
        Relationship("Borrower", "Loan", "1..*", kind="friendship")


def test_find_undefined_classes_detects_missing_target():
    classes = [ClassModel("Borrower"), ClassModel("Loan")]
    relationships = [
        Relationship("Borrower", "Loan", "1..*"),
        Relationship("Loan", "Book", "*..1"),  # Book not defined
    ]
    assert find_undefined_classes(relationships, classes) == ["Book"]


def test_find_undefined_classes_empty_when_consistent():
    classes = [ClassModel("Borrower"), ClassModel("Loan")]
    relationships = [Relationship("Borrower", "Loan", "1..*")]
    assert find_undefined_classes(relationships, classes) == []


def test_find_undocumented_data_terms():
    classes = [
        ClassModel("Loan", attributes=["dueDate: date", "activeLoanCount: int"]),
    ]
    known_terms = {"dueDate"}
    missing = find_undocumented_data_terms(classes, known_terms)
    assert missing == ["Loan.activeLoanCount"]


def test_find_undocumented_data_terms_all_known():
    classes = [ClassModel("Loan", attributes=["dueDate: date"])]
    assert find_undocumented_data_terms(classes, {"dueDate"}) == []


def test_relationship_count_by_kind():
    relationships = [
        Relationship("A", "B", kind="association"),
        Relationship("A", "C", kind="composition"),
        Relationship("B", "C", kind="composition"),
    ]
    counts = relationship_count_by_kind(relationships)
    assert counts["association"] == 1
    assert counts["composition"] == 2
    assert counts["aggregation"] == 0
