"""Chapter 8 -- Safety-Critical System Requirements.

Implements:
  - Hazard: severity/likelihood classification and computed risk level
  - SafetyRequirement: a requirement traced to one or more hazards, with
    an assigned integrity level
  - FMEAEntry: failure mode analysis with Risk Priority Number (RPN)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CATASTROPHIC = "Catastrophic"
    CRITICAL = "Critical"
    MARGINAL = "Marginal"
    NEGLIGIBLE = "Negligible"


class Likelihood(str, Enum):
    FREQUENT = "Frequent"
    PROBABLE = "Probable"
    OCCASIONAL = "Occasional"
    REMOTE = "Remote"
    IMPROBABLE = "Improbable"


_SEVERITY_SCORE = {
    Severity.CATASTROPHIC: 4,
    Severity.CRITICAL: 3,
    Severity.MARGINAL: 2,
    Severity.NEGLIGIBLE: 1,
}
_LIKELIHOOD_SCORE = {
    Likelihood.FREQUENT: 5,
    Likelihood.PROBABLE: 4,
    Likelihood.OCCASIONAL: 3,
    Likelihood.REMOTE: 2,
    Likelihood.IMPROBABLE: 1,
}


@dataclass
class Hazard:
    """A hazard per the Chapter 8 hazard analysis process."""

    hazard_id: str
    description: str
    severity: Severity
    likelihood: Likelihood

    def risk_score(self) -> int:
        """Simple severity x likelihood risk score (higher = more urgent)."""
        return _SEVERITY_SCORE[self.severity] * _LIKELIHOOD_SCORE[self.likelihood]

    def risk_level(self) -> str:
        """Coarse risk classification per the Chapter 8 risk matrix."""
        score = self.risk_score()
        if score >= 15:
            return "High"
        if score >= 8:
            return "Medium"
        return "Low"


@dataclass
class SafetyRequirement:
    """A safety requirement traced to hazard(s), with an integrity level
    (e.g., SIL 1-4 per IEC 61508, or A-E per DO-178C)."""

    req_id: str
    statement: str
    hazard_ids: list[str] = field(default_factory=list)
    integrity_level: str = ""
    verification_method: str = ""


@dataclass
class FMEAEntry:
    """A single Failure Mode and Effects Analysis row (Chapter 8)."""

    component: str
    failure_mode: str
    effect: str
    severity_score: int   # 1-10
    occurrence_score: int  # 1-10
    detection_score: int   # 1-10

    def __post_init__(self):
        for name, value in (
            ("severity_score", self.severity_score),
            ("occurrence_score", self.occurrence_score),
            ("detection_score", self.detection_score),
        ):
            if not (1 <= value <= 10):
                raise ValueError(f"{name} must be between 1 and 10, got {value}")

    def rpn(self) -> int:
        """Risk Priority Number = Severity x Occurrence x Detection."""
        return self.severity_score * self.occurrence_score * self.detection_score


def highest_priority_failure_modes(entries: list[FMEAEntry], top_n: int = 3) -> list[FMEAEntry]:
    """The failure modes most urgently needing a mitigating requirement,
    ranked by Risk Priority Number (Chapter 8)."""
    return sorted(entries, key=lambda e: e.rpn(), reverse=True)[:top_n]


def requirements_without_hazard_trace(requirements: list[SafetyRequirement]) -> list[str]:
    """Safety requirements missing a hazard trace -- a Chapter 8 red flag,
    since every safety requirement must trace to a specific hazard."""
    return [r.req_id for r in requirements if not r.hazard_ids]
