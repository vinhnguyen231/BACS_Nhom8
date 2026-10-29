"""Chapter 2 -- Requirements Validation and Verification.

Implements:
  - lint_requirement(): ambiguity / compound-requirement / modal-verb checks
  - ReviewDefect: inspection defect record
  - defect_density, open_critical_defects
  - ambiguity_rate, testability_rate: requirements quality metrics
"""

from __future__ import annotations

from dataclasses import dataclass

AMBIGUOUS_WORDS = {
    "fast", "quickly", "slow", "user-friendly", "easy",
    "flexible", "robust", "efficient", "optimal", "etc",
    "as appropriate", "support", "handle", "should", "might",
}


def lint_requirement(statement: str) -> list[str]:
    """Return a list of quality issues detected in a requirement statement.

    This is a teaching-grade heuristic linter (Chapter 2), not a substitute
    for human review -- but it demonstrates how ambiguity, missing modal
    verbs, and compound requirements can be caught automatically.
    """
    issues = []
    text = statement.lower()
    if "shall" not in text:
        issues.append("Missing mandatory modal verb 'shall'.")
    found = sorted(w for w in AMBIGUOUS_WORDS if w in text)
    if found:
        issues.append(f"Contains ambiguous word(s): {found}")
    if text.count(" and ") > 1:
        issues.append("Possible compound requirement (multiple 'and').")
    return issues


@dataclass
class ReviewDefect:
    """A single defect logged during a formal inspection or walkthrough."""

    req_id: str
    severity: str  # "Critical" | "Major" | "Minor"
    description: str
    resolved: bool = False

    def __post_init__(self):
        valid = {"Critical", "Major", "Minor"}
        if self.severity not in valid:
            raise ValueError(f"severity must be one of {valid}, got {self.severity!r}")


def defect_density(defects: list[ReviewDefect], total_requirements: int) -> float:
    """Defects found per requirement reviewed."""
    return len(defects) / total_requirements if total_requirements else 0.0


def open_critical_defects(defects: list[ReviewDefect]) -> list[ReviewDefect]:
    """Unresolved Critical defects -- these should block baselining."""
    return [d for d in defects if d.severity == "Critical" and not d.resolved]


def can_baseline(defects: list[ReviewDefect]) -> bool:
    """A requirement set is ready to baseline only if no Critical defects
    remain open (Major/Minor may be deferred with sign-off)."""
    return len(open_critical_defects(defects)) == 0


def ambiguity_rate(requirements) -> float:
    """Fraction of requirements flagged by the linter for any reason."""
    if not requirements:
        return 0.0
    flagged = sum(1 for r in requirements if lint_requirement(r.statement))
    return flagged / len(requirements)


def testability_rate(requirement_set) -> float:
    """Fraction of requirements passing the Chapter 1 testability heuristic."""
    total = len(requirement_set.requirements)
    if not total:
        return 0.0
    testable = total - len(requirement_set.untestable())
    return testable / total
