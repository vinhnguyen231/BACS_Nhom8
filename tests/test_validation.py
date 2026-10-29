import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.requirement import Requirement, RequirementSet, RequirementType
from requirements_toolkit.validation import (
    lint_requirement, ReviewDefect, defect_density,
    open_critical_defects, can_baseline, ambiguity_rate, testability_rate,
)


def test_lint_requirement_flags_missing_shall():
    issues = lint_requirement("The product will notify the user.")
    assert any("shall" in i for i in issues)


def test_lint_requirement_flags_ambiguous_words():
    issues = lint_requirement("The system should respond quickly.")
    assert any("ambiguous" in i for i in issues)


def test_lint_requirement_flags_compound_requirement():
    issues = lint_requirement("The system shall log in a user and record it and notify admin.")
    assert any("compound" in i for i in issues)


def test_lint_requirement_clean_statement_has_no_issues():
    issues = lint_requirement("The system shall lock the account after 3 failed login attempts.")
    assert issues == []


def test_review_defect_rejects_invalid_severity():
    with pytest.raises(ValueError):
        ReviewDefect(req_id="FR-1", severity="Blocker", description="oops")


def test_defect_density_computation():
    defects = [
        ReviewDefect("FR-1", "Major", "ambiguous"),
        ReviewDefect("FR-2", "Minor", "typo"),
    ]
    assert defect_density(defects, total_requirements=4) == 0.5


def test_open_critical_defects_excludes_resolved():
    defects = [
        ReviewDefect("FR-1", "Critical", "bad", resolved=False),
        ReviewDefect("FR-2", "Critical", "bad2", resolved=True),
    ]
    assert [d.req_id for d in open_critical_defects(defects)] == ["FR-1"]


def test_can_baseline_false_with_open_critical_defect():
    defects = [ReviewDefect("FR-1", "Critical", "bad")]
    assert can_baseline(defects) is False


def test_can_baseline_true_when_only_minor_defects():
    defects = [ReviewDefect("FR-1", "Minor", "typo")]
    assert can_baseline(defects) is True


def test_ambiguity_rate_and_testability_rate():
    rs = RequirementSet(name="Demo")
    rs.add(Requirement("FR-1", "The system shall lock the account after 3 failed attempts.", RequirementType.FUNCTIONAL))
    rs.add(Requirement("FR-2", "The system should handle logins efficiently.", RequirementType.FUNCTIONAL))

    assert ambiguity_rate(rs.requirements) == 0.5
    assert testability_rate(rs) == 0.5
