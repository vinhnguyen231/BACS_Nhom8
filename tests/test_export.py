import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json

from requirements_toolkit.requirement import Requirement, RequirementSet, RequirementType, Priority
from requirements_toolkit.validation import ReviewDefect
from requirements_toolkit.nfr import NFRVerification, QualityCharacteristic
from requirements_toolkit.export import export_to_csv, export_to_json, build_dashboard_summary


def make_requirement_set():
    rs = RequirementSet(name="Demo")
    rs.add(Requirement("FR-1", "The system shall lock the account after 3 failed attempts.", RequirementType.FUNCTIONAL, Priority.MUST))
    rs.add(Requirement("FR-2", "The system should handle logins efficiently.", RequirementType.FUNCTIONAL, Priority.COULD))
    return rs


def test_export_to_csv_includes_header_and_rows():
    rs = make_requirement_set()
    csv_text = export_to_csv(rs)
    lines = csv_text.strip().splitlines()
    assert lines[0] == "req_id,req_type,priority,status,statement"
    assert len(lines) == 3  # header + 2 requirements
    assert "FR-1" in lines[1]


def test_export_to_json_round_trips_requirement_ids():
    rs = make_requirement_set()
    json_text = export_to_json(rs)
    data = json.loads(json_text)
    ids = [d["req_id"] for d in data]
    assert ids == ["FR-1", "FR-2"]


def test_export_to_json_is_valid_json():
    rs = make_requirement_set()
    json_text = export_to_json(rs)
    parsed = json.loads(json_text)
    assert isinstance(parsed, list)
    assert parsed[0]["req_type"] == "Functional"


def test_build_dashboard_summary_combines_metrics():
    rs = make_requirement_set()
    defects = [ReviewDefect("FR-1", "Minor", "typo")]
    verifications = [
        NFRVerification("NFR-1", QualityCharacteristic.PERFORMANCE_EFFICIENCY, "Load test", "p95<=2s", passed=True),
    ]
    matrix = {
        "FR-1": {"source": "x", "design_links": [], "test_links": ["TC-1"]},
        "FR-2": {"source": "x", "design_links": [], "test_links": []},
    }
    summary = build_dashboard_summary(rs, defects, verifications, matrix)

    assert summary["total_requirements"] == 2
    assert summary["ambiguity_rate"] == 0.5
    assert summary["defect_density"] == 0.5
    assert summary["nfr_pass_rate"] == 1.0
    assert summary["untested_requirements"] == ["FR-2"]
