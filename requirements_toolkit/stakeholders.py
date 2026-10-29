"""Chapter 5 -- Collaborating with Stakeholders.

Implements:
  - Stakeholder: power/interest/attitude profile
  - quadrant classification per the Power/Interest grid
  - engagement_plan(): recommended engagement strategy per quadrant
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Power(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Interest(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


VALID_ATTITUDES = {"Champion", "Neutral", "Skeptic", "Blocker"}

ENGAGEMENT_STRATEGY = {
    "Manage closely": "Weekly working sessions; involve in every major decision.",
    "Keep satisfied": "Monthly summary updates; consult on high-impact changes.",
    "Keep informed": "Bi-weekly newsletter; open feedback channel.",
    "Monitor": "Quarterly summary; no dedicated engagement needed.",
}


@dataclass
class Stakeholder:
    """A stakeholder profile per the Chapter 5 stakeholder register template."""

    name: str
    role: str
    power: Power
    interest: Interest
    attitude: str = "Neutral"

    def __post_init__(self):
        if self.attitude not in VALID_ATTITUDES:
            raise ValueError(f"attitude must be one of {VALID_ATTITUDES}")

    def quadrant(self) -> str:
        """Classify into the Power/Interest grid (Chapter 5)."""
        high_power = self.power == Power.HIGH
        high_interest = self.interest == Interest.HIGH
        if high_power and high_interest:
            return "Manage closely"
        if high_power:
            return "Keep satisfied"
        if high_interest:
            return "Keep informed"
        return "Monitor"

    def engagement_plan(self) -> str:
        return ENGAGEMENT_STRATEGY[self.quadrant()]


def stakeholders_needing_close_management(stakeholders: list[Stakeholder]) -> list[Stakeholder]:
    """Convenience filter -- who should the analyst prioritize engaging?"""
    return [s for s in stakeholders if s.quadrant() == "Manage closely"]


def blockers(stakeholders: list[Stakeholder]) -> list[Stakeholder]:
    """Stakeholders actively opposed -- flagged for dedicated conflict-resolution
    attention per the Chapter 5 conflict resolution framework."""
    return [s for s in stakeholders if s.attitude == "Blocker"]
