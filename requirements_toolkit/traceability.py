"""Chapter 1 -- Requirements Traceability Matrix (RTM) utilities.

Used again in Chapter 3 (change impact analysis) and Chapter 9 (tool support).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DesignElement:
    id: str
    satisfies: list[str] = field(default_factory=list)  # requirement IDs


@dataclass
class TestCase:
    # Tell pytest this is a domain model, not a test class to collect --
    # it matches pytest's default `Test*` class-discovery pattern otherwise.
    __test__ = False

    id: str
    verifies: list[str] = field(default_factory=list)  # requirement IDs


def build_traceability_matrix(requirements, design_elements: list[DesignElement], test_cases: list[TestCase]) -> dict:
    """Build a traceability matrix: req_id -> {source, design_links, test_links}."""
    matrix = {}
    for req in requirements:
        matrix[req.req_id] = {
            "source": getattr(req, "source", ""),
            "design_links": [d.id for d in design_elements if req.req_id in d.satisfies],
            "test_links": [t.id for t in test_cases if req.req_id in t.verifies],
        }
    return matrix


def find_untested_requirements(matrix: dict) -> list[str]:
    """Requirement IDs with no linked test case -- a coverage gap."""
    return [rid for rid, links in matrix.items() if not links["test_links"]]


def find_orphan_requirements(matrix: dict) -> list[str]:
    """Requirement IDs with no recorded source -- likely gold-plating (Ch.1)."""
    return [rid for rid, links in matrix.items() if not links["source"]]


def coverage_report(matrix: dict) -> str:
    total = len(matrix)
    untested = find_untested_requirements(matrix)
    orphans = find_orphan_requirements(matrix)
    lines = [
        f"Total requirements: {total}",
        f"Untested requirements: {len(untested)} {untested}",
        f"Requirements without a source: {len(orphans)} {orphans}",
        f"Test coverage: {100 * (total - len(untested)) / total:.1f}%" if total else "Test coverage: N/A",
    ]
    return "\n".join(lines)
