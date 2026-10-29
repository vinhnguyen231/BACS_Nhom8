import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

import pytest

from requirements_toolkit.change_management import (
    ChangeRequest, Baseline, impact_analysis, volatility, can_create_baseline,
)
from requirements_toolkit.validation import ReviewDefect


def make_cr(cr_id="CR-001", affected=None):
    return ChangeRequest(
        cr_id=cr_id,
        title="Allow partial refunds",
        description="Support partial refund amounts, not just full refunds.",
        originator="Finance stakeholder",
        affected_requirement_ids=affected or ["FR-4.5", "FR-4.6"],
    )


def test_change_request_default_status_is_submitted():
    cr = make_cr()
    assert cr.status == "Submitted"


def test_change_request_rejects_invalid_status():
    with pytest.raises(ValueError):
        ChangeRequest("CR-002", "t", "d", "o", status="Unknown")


def test_valid_transition_submitted_to_approved():
    cr = make_cr()
    cr.transition("Approved")
    assert cr.status == "Approved"


def test_valid_transition_approved_to_implemented():
    cr = make_cr()
    cr.transition("Approved")
    cr.transition("Implemented")
    assert cr.status == "Implemented"


def test_invalid_transition_raises():
    cr = make_cr()
    cr.transition("Rejected")
    with pytest.raises(ValueError):
        cr.transition("Approved")  # Rejected is terminal


def test_deferred_can_later_be_approved():
    cr = make_cr()
    cr.transition("Deferred")
    cr.transition("Approved")
    assert cr.status == "Approved"


def test_baseline_holds_included_crs():
    b = Baseline(version="v1.1", date_approved=date(2026, 2, 10), included_cr_ids=["CR-009", "CR-011"])
    assert b.version == "v1.1"
    assert "CR-009" in b.included_cr_ids


def test_impact_analysis_collects_ripple_links():
    cr = make_cr(affected=["FR-4.5"])
    matrix = {
        "FR-4.5": {"source": "BR-01", "design_links": ["DE-RefundService"], "test_links": ["TC-041", "TC-042"]},
    }
    result = impact_analysis(cr, matrix)
    assert result["design_elements"] == ["DE-RefundService"]
    assert result["test_cases"] == ["TC-041", "TC-042"]


def test_volatility_computation():
    assert volatility(baseline_count=50, added=4, changed=6, deleted=1) == pytest.approx(11 / 50)


def test_volatility_zero_baseline_returns_zero():
    assert volatility(baseline_count=0, added=1, changed=0, deleted=0) == 0.0


def test_can_create_baseline_blocks_on_open_critical_defect():
    defects = [ReviewDefect("FR-1", "Critical", "bad", resolved=False)]
    matrix = {"FR-1": {"source": "x", "design_links": [], "test_links": ["TC-1"]}}
    ok, reasons = can_create_baseline(defects, matrix)
    assert ok is False
    assert any("Critical" in r for r in reasons)


def test_can_create_baseline_blocks_on_untested_requirement():
    matrix = {"FR-1": {"source": "x", "design_links": [], "test_links": []}}
    ok, reasons = can_create_baseline([], matrix)
    assert ok is False
    assert any("test coverage" in r for r in reasons)


def test_can_create_baseline_passes_when_clean():
    matrix = {"FR-1": {"source": "x", "design_links": [], "test_links": ["TC-1"]}}
    ok, reasons = can_create_baseline([], matrix)
    assert ok is True
    assert reasons == []
