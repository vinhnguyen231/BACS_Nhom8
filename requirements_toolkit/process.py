"""Chapter 10 -- Software Requirements Engineering Processes.

Models a project's tailored RE process as a sequence of stages with
associated rigor levels, and computes a lightweight CMMI-inspired
maturity score based on which practices are present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RigorLevel(str, Enum):
    LIGHTWEIGHT = "Lightweight"
    STRUCTURED = "Structured"
    FULL_PLAN_DRIVEN = "Full plan-driven"


@dataclass
class ProcessStage:
    """One stage of a tailored RE process (Chapter 10), e.g. "Elicitation"."""

    name: str
    rigor: RigorLevel
    activities: list[str] = field(default_factory=list)


@dataclass
class ProcessModel:
    """A project's tailored end-to-end RE process."""

    project_name: str
    stages: list[ProcessStage] = field(default_factory=list)

    def total_activities(self) -> int:
        return sum(len(s.activities) for s in self.stages)

    def rigor_distribution(self) -> dict[str, int]:
        """How many stages fall at each rigor level -- a quick sanity
        check on whether rigor allocation matches the project's risk profile."""
        counts: dict[str, int] = {r.value: 0 for r in RigorLevel}
        for s in self.stages:
            counts[s.rigor.value] += 1
        return counts


# Practices checked for the lightweight maturity self-assessment (Chapter 10).
MATURITY_PRACTICES = [
    "documented_process",
    "consistent_across_projects",
    "quality_metrics_tracked",
    "process_retrospectives_held",
]


def maturity_score(practices_present: set[str]) -> int:
    """A simplified CMMI-inspired maturity score (1-5), based on how many
    of the Chapter 10 MATURITY_PRACTICES are present.

    0 practices -> Level 1 (Initial)
    1 practice  -> Level 2 (Managed)
    2 practices -> Level 3 (Defined)
    3 practices -> Level 4 (Quantitatively Managed)
    4 practices -> Level 5 (Optimizing)
    """
    count = len(practices_present & set(MATURITY_PRACTICES))
    return min(count + 1, 5)
