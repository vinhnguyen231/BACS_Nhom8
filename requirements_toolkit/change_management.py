"""Chapter 3 -- Managing Changing Requirements.

Implements:
  - ChangeRequest: a logged change request with status lifecycle
  - Baseline: a named, dated snapshot of approved change requests
  - impact_analysis(): uses the Chapter 1 traceability matrix to find
    ripple-affected design elements and test cases
  - volatility(): requirements volatility metric
  - can_create_baseline(): automated baseline gate (blocks on open
    Critical defects or untested requirements)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

VALID_CR_STATUSES = {"Submitted", "Approved", "Rejected", "Deferred", "Implemented"}
_STATUS_TRANSITIONS = {
    "Submitted": {"Approved", "Rejected", "Deferred"},
    "Approved": {"Implemented", "Deferred"},
    "Deferred": {"Approved", "Rejected"},
    "Rejected": set(),
    "Implemented": set(),
}


@dataclass
class ChangeRequest:
    """A single logged change request (Chapter 3 CR template)."""

    cr_id: str
    title: str
    description: str
    originator: str
    affected_requirement_ids: list[str] = field(default_factory=list)
    status: str = "Submitted"
    date_submitted: date = field(default_factory=date.today)

    def __post_init__(self):
        if self.status not in VALID_CR_STATUSES:
            raise ValueError(f"status must be one of {VALID_CR_STATUSES}")

    def transition(self, new_status: str) -> None:
        """Move the CR to a new status, enforcing the lifecycle rules
        shown in the Chapter 3 status-transition diagram."""
        if new_status not in VALID_CR_STATUSES:
            raise ValueError(f"Unknown status: {new_status}")
        allowed = _STATUS_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {self.status!r} -> {new_status!r}. "
                f"Allowed: {sorted(allowed)}"
            )
        self.status = new_status


@dataclass
class Baseline:
    """A formally approved, named snapshot of requirements (Chapter 3)."""

    version: str
    date_approved: date
    included_cr_ids: list[str] = field(default_factory=list)


def impact_analysis(change_request: ChangeRequest, traceability_matrix: dict) -> dict:
    """Find every design element and test case rippling from a CR's
    directly affected requirements, using the Chapter 1 traceability matrix.
    """
    impacted_design: set[str] = set()
    impacted_tests: set[str] = set()
    for req_id in change_request.affected_requirement_ids:
        links = traceability_matrix.get(req_id, {})
        impacted_design.update(links.get("design_links", []))
        impacted_tests.update(links.get("test_links", []))
    return {
        "requirements": list(change_request.affected_requirement_ids),
        "design_elements": sorted(impacted_design),
        "test_cases": sorted(impacted_tests),
    }


def volatility(baseline_count: int, added: int, changed: int, deleted: int) -> float:
    """Requirements volatility for a release period (Chapter 3 formula)."""
    if baseline_count == 0:
        return 0.0
    return (added + changed + deleted) / baseline_count


def can_create_baseline(open_defects, traceability_matrix: dict) -> tuple[bool, list[str]]:
    """Automated baseline gate: blocks on open Critical defects (Ch.2) or
    requirements with no linked test case in the traceability matrix (Ch.1).
    Returns (is_allowed, list_of_blocking_reasons).
    """
    reasons: list[str] = []
    critical_open = [
        d for d in open_defects
        if getattr(d, "severity", None) == "Critical" and not getattr(d, "resolved", False)
    ]
    if critical_open:
        reasons.append(f"{len(critical_open)} open Critical defect(s)")

    untested = [rid for rid, links in traceability_matrix.items() if not links.get("test_links")]
    if untested:
        reasons.append(f"{len(untested)} requirement(s) without test coverage: {untested}")

    return (len(reasons) == 0, reasons)
