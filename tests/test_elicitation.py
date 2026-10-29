import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.elicitation import (
    ElicitationSession, Assumption, elicitation_coverage,
    open_assumptions, kano_summary,
)


def test_elicitation_session_stores_findings():
    session = ElicitationSession(
        session_id="ES-01",
        technique="JAD workshop",
        stakeholders=["Head Librarian", "Partner Library Director"],
        findings=["Partner libraries want a 3-day fulfillment SLA"],
    )
    assert len(session.findings) == 1
    assert "Head Librarian" in session.stakeholders


def test_assumption_default_status_is_open():
    a = Assumption("A-01", "Assume max 20 concurrent renewals", "BA")
    assert a.status == "Open"


def test_assumption_rejects_invalid_status():
    with pytest.raises(ValueError):
        Assumption("A-02", "desc", "BA", status="Maybe")


def test_assumption_resolve_to_confirmed():
    a = Assumption("A-03", "desc", "BA")
    a.resolve("Confirmed")
    assert a.status == "Confirmed"


def test_assumption_resolve_rejects_invalid_target_status():
    a = Assumption("A-04", "desc", "BA")
    with pytest.raises(ValueError):
        a.resolve("Open")


def test_elicitation_coverage_full():
    coverage = elicitation_coverage(
        engaged_stakeholder_ids=["S1", "S2", "S3"],
        register_stakeholder_ids=["S1", "S2", "S3"],
    )
    assert coverage == 1.0


def test_elicitation_coverage_partial():
    coverage = elicitation_coverage(
        engaged_stakeholder_ids=["S1"],
        register_stakeholder_ids=["S1", "S2", "S3", "S4"],
    )
    assert coverage == 0.25


def test_elicitation_coverage_empty_register_is_zero():
    assert elicitation_coverage(["S1"], []) == 0.0


def test_open_assumptions_filters_correctly():
    a1 = Assumption("A-01", "desc", "BA", status="Open")
    a2 = Assumption("A-02", "desc", "BA", status="Confirmed")
    assert open_assumptions([a1, a2]) == [a1]


def test_kano_summary_counts_correctly():
    classifications = {
        "FR-1": "Basic",
        "FR-2": "Performance",
        "FR-3": "Performance",
        "FR-4": "Excitement",
    }
    summary = kano_summary(classifications)
    assert summary["Basic"] == 1
    assert summary["Performance"] == 2
    assert summary["Excitement"] == 1


def test_kano_summary_rejects_unknown_category():
    with pytest.raises(ValueError):
        kano_summary({"FR-1": "Unknown"})
