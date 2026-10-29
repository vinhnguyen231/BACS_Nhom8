"""Chapter 4 -- Non-functional Requirements.

Implements a lightweight quality-attribute-scenario model and NFR
verification tracking, aligned with ISO/IEC 25010 characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class QualityCharacteristic(str, Enum):
    FUNCTIONAL_SUITABILITY = "Functional Suitability"
    PERFORMANCE_EFFICIENCY = "Performance Efficiency"
    COMPATIBILITY = "Compatibility"
    USABILITY = "Usability"
    RELIABILITY = "Reliability"
    SECURITY = "Security"
    MAINTAINABILITY = "Maintainability"
    PORTABILITY = "Portability"


@dataclass
class QualityAttributeScenario:
    """The 6-part quality attribute scenario structure from Chapter 4."""

    source: str
    stimulus: str
    artifact: str
    environment: str
    response: str
    response_measure: str
    characteristic: QualityCharacteristic = QualityCharacteristic.PERFORMANCE_EFFICIENCY

    def to_requirement_text(self, nfr_id: str) -> str:
        """Render the scenario as a single NFR statement, roughly following
        the worked examples in the Chapter 4 lecture deck."""
        return (
            f"{nfr_id}: When {self.stimulus.lower()} occurs on {self.artifact} "
            f"under {self.environment}, the system shall {self.response.lower()}, "
            f"meeting: {self.response_measure}."
        )


@dataclass
class NFRVerification:
    """Tracks how a specific NFR will be / was verified (Chapter 2 + 4)."""

    nfr_id: str
    characteristic: QualityCharacteristic
    method: str
    threshold: str
    result: str | None = None
    passed: bool | None = None


def nfr_pass_rate(verifications: list[NFRVerification]) -> float:
    """Fraction of *completed* NFR verifications that passed."""
    completed = [v for v in verifications if v.passed is not None]
    if not completed:
        return 0.0
    return sum(1 for v in completed if v.passed) / len(completed)


def coverage_by_characteristic(verifications: list[NFRVerification]) -> dict[str, int]:
    """Count how many NFRs are being tracked per ISO/IEC 25010 characteristic --
    useful for spotting neglected categories (Chapter 4's elicitation checklist)."""
    counts: dict[str, int] = {c.value: 0 for c in QualityCharacteristic}
    for v in verifications:
        counts[v.characteristic.value] += 1
    return counts
