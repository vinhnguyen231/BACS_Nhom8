"""Chapter 7 -- Modeling Techniques and Diagrammatic Notations.

Lightweight structured representations of class/domain models and their
relationships, plus consistency checks against undefined class references.
Not a full diagramming tool -- focuses on catching requirements-modeling
inconsistencies early, per the Chapter 7 "diagram-text drift" pitfall.
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_RELATIONSHIP_KINDS = {"association", "aggregation", "composition", "generalization"}


@dataclass
class ClassModel:
    """A class/domain entity in the requirements model (Chapter 7)."""

    name: str
    attributes: list[str] = field(default_factory=list)


@dataclass
class Relationship:
    """A relationship between two classes, e.g. Borrower --1..*--> Loan."""

    source: str
    target: str
    multiplicity: str = ""
    kind: str = "association"

    def __post_init__(self):
        if self.kind not in VALID_RELATIONSHIP_KINDS:
            raise ValueError(f"kind must be one of {VALID_RELATIONSHIP_KINDS}")


def find_undefined_classes(relationships: list[Relationship], classes: list[ClassModel]) -> list[str]:
    """Names referenced by a relationship but not defined as a ClassModel --
    a diagram consistency error (Chapter 7)."""
    known = {c.name for c in classes}
    referenced = {r.source for r in relationships} | {r.target for r in relationships}
    return sorted(referenced - known)


def find_undocumented_data_terms(classes: list[ClassModel], data_dictionary_terms: set[str]) -> list[str]:
    """Attributes appearing on a class diagram but missing from the Chapter 1
    data dictionary -- surfaces documentation gaps between models."""
    missing = []
    for c in classes:
        for attr in c.attributes:
            term = attr.split(":")[0].strip()
            if term and term not in data_dictionary_terms:
                missing.append(f"{c.name}.{term}")
    return sorted(missing)


def relationship_count_by_kind(relationships: list[Relationship]) -> dict[str, int]:
    """Summarize how many relationships of each kind exist -- a quick sanity
    check (e.g., an all-"association", no-composition model may be under-specified)."""
    counts: dict[str, int] = {k: 0 for k in VALID_RELATIONSHIP_KINDS}
    for r in relationships:
        counts[r.kind] += 1
    return counts
