"""Chapter 9 -- Tool Support for Requirements Engineering.

Implements multi-format export (CSV, JSON) for a RequirementSet, and a
cross-module dashboard summary combining metrics from Chapters 1-4, 8,
mirroring the "single source of truth, multiple views" theme of the
docs-as-code approach covered in this chapter.
"""

from __future__ import annotations

import csv
import io
import json


def export_to_csv(requirement_set) -> str:
    """Export a RequirementSet to a CSV string with ID, type, priority,
    status, and statement columns (Chapter 9 multi-format export)."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["req_id", "req_type", "priority", "status", "statement"])
    for r in requirement_set.requirements:
        writer.writerow([r.req_id, r.req_type.value, r.priority.value, r.status.value, r.statement])
    return output.getvalue()


def export_to_json(requirement_set) -> str:
    """Export a RequirementSet to a JSON string."""
    data = [
        {
            "req_id": r.req_id,
            "req_type": r.req_type.value,
            "priority": r.priority.value,
            "status": r.status.value,
            "statement": r.statement,
            "source": r.source,
        }
        for r in requirement_set.requirements
    ]
    return json.dumps(data, indent=2)


def build_dashboard_summary(requirement_set, defects, verifications, matrix) -> dict:
    """Combine metrics from multiple toolkit modules into one dashboard
    summary dict, per the Chapter 9 'metrics dashboard' worked example.

    Imports are local to avoid a hard dependency cycle between modules.
    """
    from .validation import ambiguity_rate, defect_density
    from .nfr import nfr_pass_rate

    total = len(requirement_set.requirements)
    return {
        "total_requirements": total,
        "ambiguity_rate": ambiguity_rate(requirement_set.requirements),
        "defect_density": defect_density(defects, total),
        "nfr_pass_rate": nfr_pass_rate(verifications),
        "untested_requirements": [
            rid for rid, links in matrix.items() if not links.get("test_links")
        ],
    }
