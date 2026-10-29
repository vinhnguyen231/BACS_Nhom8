"""Chapter 1 -- Requirements Specification and Documentation.

Core data model for a single requirement, its attributes, and requirement
type enumeration, as introduced in Chapter 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RequirementType(str, Enum):
    BUSINESS = "Business"
    STAKEHOLDER = "Stakeholder"
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-functional"
    CONSTRAINT = "Constraint"
    BUSINESS_RULE = "Business Rule"


class Priority(str, Enum):
    MUST = "Must have"
    SHOULD = "Should have"
    COULD = "Could have"
    WONT = "Won't have (this release)"


class Status(str, Enum):
    PROPOSED = "Proposed"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"
    VERIFIED = "Verified"
    DEFERRED = "Deferred"
    REJECTED = "Rejected"


@dataclass
class Requirement:
    """A single, uniquely identified requirement with management attributes.

    Attributes mirror the "Common Requirement Attributes" table in Chapter 1:
    unique id, priority, status, source, rationale, owner, release, and
    verification method.
    """

    req_id: str
    statement: str
    req_type: RequirementType
    priority: Priority = Priority.SHOULD
    status: Status = Status.PROPOSED
    source: str = ""
    rationale: str = ""
    owner: str = ""
    release: str = ""
    verification_method: str = "Test"

    def is_testable(self) -> bool:
        """Very lightweight heuristic check used as a teaching aid.

        Flags statements that likely violate the 'verifiable' characteristic
        covered in Chapter 1 (e.g. contain vague adjectives, or lack a
        modal verb such as 'shall').
        """
        vague_words = {
            "fast", "quickly", "slow", "user-friendly", "easy",
            "flexible", "robust", "efficient", "optimal", "etc",
            "as appropriate", "support", "handle",
        }
        text = self.statement.lower()
        has_vague_word = any(word in text for word in vague_words)
        has_modal = "shall" in text
        return has_modal and not has_vague_word

    def __str__(self) -> str:
        return f"[{self.req_id}] ({self.req_type.value}, {self.priority.value}) {self.statement}"


@dataclass
class RequirementSet:
    """A collection of requirements for one system or feature area."""

    name: str
    requirements: list[Requirement] = field(default_factory=list)

    def add(self, requirement: Requirement) -> None:
        if any(r.req_id == requirement.req_id for r in self.requirements):
            raise ValueError(f"Duplicate requirement ID: {requirement.req_id}")
        self.requirements.append(requirement)

    def by_type(self, req_type: RequirementType) -> list[Requirement]:
        return [r for r in self.requirements if r.req_type == req_type]

    def untestable(self) -> list[Requirement]:
        """Requirements that fail the lightweight testability heuristic."""
        return [r for r in self.requirements if not r.is_testable()]

    def count_by_priority(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.requirements:
            counts[r.priority.value] = counts.get(r.priority.value, 0) + 1
        return counts
