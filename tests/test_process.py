import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from requirements_toolkit.process import (
    ProcessStage, ProcessModel, RigorLevel, maturity_score, MATURITY_PRACTICES,
)


def make_process_model():
    return ProcessModel(
        project_name="Campus Room Booking System",
        stages=[
            ProcessStage("Elicitation", RigorLevel.STRUCTURED, ["Interviews", "JAD workshop"]),
            ProcessStage("Specification", RigorLevel.STRUCTURED, ["SRS drafted", "NFRs specified"]),
            ProcessStage("Safety Review", RigorLevel.FULL_PLAN_DRIVEN, ["Hazard analysis"]),
        ],
    )


def test_total_activities_sums_across_stages():
    model = make_process_model()
    assert model.total_activities() == 5


def test_rigor_distribution_counts_correctly():
    model = make_process_model()
    dist = model.rigor_distribution()
    assert dist[RigorLevel.STRUCTURED.value] == 2
    assert dist[RigorLevel.FULL_PLAN_DRIVEN.value] == 1
    assert dist[RigorLevel.LIGHTWEIGHT.value] == 0


def test_maturity_score_level_1_with_no_practices():
    assert maturity_score(set()) == 1


def test_maturity_score_level_3_with_two_practices():
    practices = {"documented_process", "consistent_across_projects"}
    assert maturity_score(practices) == 3


def test_maturity_score_level_5_with_all_practices():
    assert maturity_score(set(MATURITY_PRACTICES)) == 5


def test_maturity_score_ignores_unknown_practices():
    practices = {"documented_process", "some_unrelated_practice"}
    assert maturity_score(practices) == 2
