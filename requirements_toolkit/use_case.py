"""Chapter 6 -- Use Case Modeling and Scenario Descriptions.

Implements a structured UseCase model (main flow + extensions) and a
helper to bootstrap functional-requirement stubs from it, following the
Chapter 6 derivation process (main flow step -> FR, extension -> FR).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .requirement import Requirement, RequirementType, Priority


@dataclass
class Extension:
    """An alternate/exception flow branching from a main flow step
    (e.g., step_ref="5a")."""

    step_ref: str
    condition: str
    system_response: str


@dataclass
class UseCase:
    """A fully-dressed use case per the Chapter 6 template."""

    uc_id: str
    name: str
    primary_actor: str
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    main_flow: list[str] = field(default_factory=list)
    extensions: list[Extension] = field(default_factory=list)

    def scenario_count(self) -> int:
        """Main flow counts as one scenario; each extension is another."""
        return 1 + len(self.extensions)


def derive_requirement_stubs(use_case: UseCase, id_prefix: str) -> list[Requirement]:
    """Bootstrap draft functional requirements from a use case's main flow
    and extensions, following the Chapter 6 derivation process.

    This produces *stubs* -- an analyst should still review and refine
    each generated requirement statement (per the Chapter 1/2 quality bar).
    """
    stubs: list[Requirement] = []
    for i, step in enumerate(use_case.main_flow, start=1):
        stubs.append(Requirement(
            req_id=f"{id_prefix}.{i}",
            statement=f"The system shall {step.lower()}" if not step.lower().startswith("the system shall") else step,
            req_type=RequirementType.FUNCTIONAL,
            priority=Priority.MUST,
            source=f"{use_case.uc_id} main flow step {i}",
        ))
    for ext in use_case.extensions:
        stubs.append(Requirement(
            req_id=f"{id_prefix}.ext.{ext.step_ref}",
            statement=f"If {ext.condition.lower()}, then the system shall {ext.system_response.lower()}",
            req_type=RequirementType.FUNCTIONAL,
            priority=Priority.MUST,
            source=f"{use_case.uc_id} extension {ext.step_ref}",
        ))
    return stubs


def scenario_coverage(use_case: UseCase, tested_step_refs: set[str]) -> float:
    """Fraction of the use case's flows (main + extensions) that have at
    least one associated test case, per the Chapter 6 scenario coverage
    metric. "main" counts as covered if present in tested_step_refs.
    """
    total = use_case.scenario_count()
    if total == 0:
        return 0.0
    covered = 0
    if "main" in tested_step_refs:
        covered += 1
    covered += sum(1 for ext in use_case.extensions if ext.step_ref in tested_step_refs)
    return covered / total
