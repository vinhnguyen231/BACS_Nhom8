import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from requirements_toolkit.stakeholders import (
    Stakeholder, Power, Interest,
    stakeholders_needing_close_management, blockers,
)


def test_quadrant_manage_closely():
    s = Stakeholder("Mai", "Head Librarian", Power.HIGH, Interest.HIGH, "Champion")
    assert s.quadrant() == "Manage closely"


def test_quadrant_keep_satisfied():
    s = Stakeholder("CIO", "University CIO", Power.HIGH, Interest.LOW)
    assert s.quadrant() == "Keep satisfied"


def test_quadrant_keep_informed():
    s = Stakeholder("Front desk", "Staff", Power.LOW, Interest.HIGH)
    assert s.quadrant() == "Keep informed"


def test_quadrant_monitor():
    s = Stakeholder("Visitor", "General public", Power.LOW, Interest.LOW)
    assert s.quadrant() == "Monitor"


def test_engagement_plan_matches_quadrant():
    s = Stakeholder("Mai", "Head Librarian", Power.HIGH, Interest.HIGH)
    assert "Weekly" in s.engagement_plan()


def test_invalid_attitude_raises():
    with pytest.raises(ValueError):
        Stakeholder("X", "Role", Power.LOW, Interest.LOW, attitude="Furious")


def test_stakeholders_needing_close_management_filters_correctly():
    s1 = Stakeholder("A", "R1", Power.HIGH, Interest.HIGH)
    s2 = Stakeholder("B", "R2", Power.LOW, Interest.LOW)
    result = stakeholders_needing_close_management([s1, s2])
    assert result == [s1]


def test_blockers_filters_by_attitude():
    s1 = Stakeholder("A", "R1", Power.MEDIUM, Interest.MEDIUM, attitude="Blocker")
    s2 = Stakeholder("B", "R2", Power.MEDIUM, Interest.MEDIUM, attitude="Champion")
    assert blockers([s1, s2]) == [s1]
