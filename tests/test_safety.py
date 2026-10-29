import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.safety import (
    Hazard, Severity, Likelihood, SafetyRequirement, FMEAEntry,
    highest_priority_failure_modes, requirements_without_hazard_trace,
)


def test_hazard_risk_level_high_for_catastrophic_frequent():
    h = Hazard("H-01", "Arm moves unexpectedly", Severity.CATASTROPHIC, Likelihood.FREQUENT)
    assert h.risk_level() == "High"


def test_hazard_risk_level_low_for_negligible_improbable():
    h = Hazard("H-02", "Minor cosmetic issue", Severity.NEGLIGIBLE, Likelihood.IMPROBABLE)
    assert h.risk_level() == "Low"


def test_hazard_risk_score_ordering():
    high = Hazard("H-01", "x", Severity.CRITICAL, Likelihood.PROBABLE)
    low = Hazard("H-02", "y", Severity.MARGINAL, Likelihood.REMOTE)
    assert high.risk_score() > low.risk_score()


def test_fmea_entry_rejects_out_of_range_scores():
    with pytest.raises(ValueError):
        FMEAEntry("Sensor", "Fails to detect", "Doors open unsafely", 11, 3, 4)


def test_fmea_entry_rpn_computation():
    entry = FMEAEntry("Sensor", "Fails to detect", "Doors open unsafely", 9, 3, 4)
    assert entry.rpn() == 108


def test_highest_priority_failure_modes_ranks_by_rpn():
    e1 = FMEAEntry("A", "fails", "minor", 2, 2, 2)   # RPN 8
    e2 = FMEAEntry("B", "fails", "major", 9, 5, 5)    # RPN 225
    e3 = FMEAEntry("C", "fails", "moderate", 5, 4, 3)  # RPN 60
    ranked = highest_priority_failure_modes([e1, e2, e3], top_n=2)
    assert ranked == [e2, e3]


def test_requirements_without_hazard_trace_flags_missing():
    r1 = SafetyRequirement("SR-1", "Do the safe thing", hazard_ids=["H-01"])
    r2 = SafetyRequirement("SR-2", "Do another thing", hazard_ids=[])
    assert requirements_without_hazard_trace([r1, r2]) == ["SR-2"]


def test_requirements_without_hazard_trace_empty_when_all_traced():
    r1 = SafetyRequirement("SR-1", "Do the safe thing", hazard_ids=["H-01"])
    assert requirements_without_hazard_trace([r1]) == []
