"""Chapter 11 -- Requirements Elicitation and Analysis Techniques.

Implements:
  - ElicitationSession: a structured record of an elicitation session
  - Assumption: a logged assumption with resolution status
  - elicitation_coverage(): fraction of the stakeholder register engaged
  - kano_summary(): tally requirements by Kano category

This is the final module of the course toolkit, closing the loop back to
Chapter 1's Requirement/RequirementSet as the ultimate destination for
everything elicited and analyzed here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

VALID_ASSUMPTION_STATUSES = {"Open", "Confirmed", "Rejected"}
VALID_KANO_CATEGORIES = {"Basic", "Performance", "Excitement"}


@dataclass
class ElicitationSession:
    """A single elicitation session record (Chapter 11 elicitation plan)."""

    session_id: str
    technique: str
    stakeholders: list[str] = field(default_factory=list)
    date_held: date = field(default_factory=date.today)
    findings: list[str] = field(default_factory=list)


@dataclass
class Assumption:
    """A logged assumption pending or confirmed resolution (Chapter 11)."""

    assumption_id: str
    description: str
    owner: str
    status: str = "Open"

    def __post_init__(self):
        if self.status not in VALID_ASSUMPTION_STATUSES:
            raise ValueError(f"status must be one of {VALID_ASSUMPTION_STATUSES}")

    def resolve(self, status: str) -> None:
        if status not in ("Confirmed", "Rejected"):
            raise ValueError("resolve() only accepts 'Confirmed' or 'Rejected'")
        self.status = status


def elicitation_coverage(engaged_stakeholder_ids, register_stakeholder_ids) -> float:
    """Fraction of the Chapter 5 stakeholder register actually engaged
    during elicitation (Chapter 11 coverage metric)."""
    register = set(register_stakeholder_ids)
    if not register:
        return 0.0
    engaged = set(engaged_stakeholder_ids) & register
    return len(engaged) / len(register)


def open_assumptions(assumptions: list[Assumption]) -> list[Assumption]:
    """Assumptions still awaiting resolution -- a red flag if the project
    is approaching baseline (Chapter 3)."""
    return [a for a in assumptions if a.status == "Open"]


def kano_summary(kano_classifications: dict[str, str]) -> dict[str, int]:
    """Tally requirement IDs by Kano category (Chapter 11).

    kano_classifications maps requirement_id -> category ("Basic",
    "Performance", or "Excitement").
    """
    counts: dict[str, int] = {c: 0 for c in VALID_KANO_CATEGORIES}
    for req_id, category in kano_classifications.items():
        if category not in VALID_KANO_CATEGORIES:
            raise ValueError(f"Unknown Kano category for {req_id}: {category}")
        counts[category] += 1
    return counts
