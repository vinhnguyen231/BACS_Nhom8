import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.requirement import (
    Requirement, RequirementSet, RequirementType, Priority,
)
from requirements_toolkit.traceability import (
    DesignElement, TestCase, build_traceability_matrix,
    find_untested_requirements, find_orphan_requirements,
)
from requirements_toolkit.srs_generator import generate_srs_skeleton, SRSMetadata


def make_requirement(req_id="FR-1", statement="The system shall log in a user."):
    return Requirement(req_id, statement, RequirementType.FUNCTIONAL, Priority.MUST)


def test_requirement_str_contains_id_and_statement():
    r = make_requirement()
    assert "FR-1" in str(r)
    assert "log in a user" in str(r)


def test_is_testable_true_for_shall_statement_without_vague_words():
    r = make_requirement()
    assert r.is_testable() is True


def test_is_testable_false_for_vague_statement():
    r = make_requirement("FR-2", "The system should handle logins efficiently.")
    assert r.is_testable() is False


def test_requirement_set_rejects_duplicate_ids():
    rs = RequirementSet(name="Test System")
    rs.add(make_requirement("FR-1"))
    with pytest.raises(ValueError):
        rs.add(make_requirement("FR-1"))


def test_requirement_set_by_type_filters_correctly():
    rs = RequirementSet(name="Test System")
    rs.add(make_requirement("FR-1"))
    nfr = Requirement("NFR-1", "The system shall respond within 2 seconds.", RequirementType.NON_FUNCTIONAL)
    rs.add(nfr)
    assert rs.by_type(RequirementType.FUNCTIONAL) == [rs.requirements[0]]
    assert rs.by_type(RequirementType.NON_FUNCTIONAL) == [nfr]


def test_traceability_matrix_flags_untested_and_orphan_requirements():
    r1 = Requirement("FR-1", "The system shall X.", RequirementType.FUNCTIONAL, source="UC-1")
    r2 = Requirement("FR-2", "The system shall Y.", RequirementType.FUNCTIONAL, source="")
    design = [DesignElement(id="DE-1", satisfies=["FR-1"])]
    tests = [TestCase(id="TC-1", verifies=["FR-1"])]
    matrix = build_traceability_matrix([r1, r2], design, tests)

    assert find_untested_requirements(matrix) == ["FR-2"]
    assert find_orphan_requirements(matrix) == ["FR-2"]


def test_generate_srs_skeleton_includes_product_name_and_sections():
    text = generate_srs_skeleton("Demo Product")
    assert "Demo Product" in text
    assert "## 3. System Features" in text
    assert "_TBD_" in text


def test_generate_srs_skeleton_with_metadata_fills_narrative_sections():
    metadata = SRSMetadata(
        introduction="This SRS covers the Demo Product.",
        purpose="Define the requirements for the Demo Product.",
        scope="Covers loan and renewal features only.",
        definitions=[("SRS", "Software Requirements Specification")],
        references=["IEEE 830-1998"],
        overall_description="A library management system.",
        external_interfaces=[("User Interfaces", "Web-based staff console.")],
        appendices=["Appendix A: Glossary"],
    )
    text = generate_srs_skeleton("Demo Product", metadata=metadata)

    assert "This SRS covers the Demo Product." in text
    assert "Define the requirements for the Demo Product." in text
    assert "Covers loan and renewal features only." in text
    assert "**SRS**: Software Requirements Specification" in text
    assert "- IEEE 830-1998" in text
    assert "A library management system." in text
    assert "**User Interfaces**: Web-based staff console." in text
    assert "- Appendix A: Glossary" in text
    # System Features still falls back to TBD since no RequirementSet was given.
    assert "## 3. System Features\n_TBD_" in text


def test_generate_srs_skeleton_metadata_partial_fields_still_tbd():
    """Fields left unset on SRSMetadata keep the original "_TBD_" fallback,
    so a document can be filled in incrementally."""
    metadata = SRSMetadata(purpose="Define the requirements.")
    text = generate_srs_skeleton("Demo Product", metadata=metadata)

    assert "Define the requirements." in text
    assert "## 1.2 Scope\n_TBD_" in text
    assert "## 1.4 References\n_TBD_" in text
