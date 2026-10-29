import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from requirements_toolkit.nfr import (
    QualityCharacteristic, QualityAttributeScenario, NFRVerification,
    nfr_pass_rate, coverage_by_characteristic,
)


def make_scenario():
    return QualityAttributeScenario(
        source="5,000 concurrent shoppers",
        stimulus="Submits a search query",
        artifact="Search service",
        environment="peak holiday traffic",
        response="return ranked results",
        response_measure="95% of queries respond within 2 seconds",
        characteristic=QualityCharacteristic.PERFORMANCE_EFFICIENCY,
    )


def test_scenario_to_requirement_text_includes_id_and_measure():
    scenario = make_scenario()
    text = scenario.to_requirement_text("NFR-1.1")
    assert text.startswith("NFR-1.1:")
    assert "95% of queries respond within 2 seconds" in text


def test_nfr_pass_rate_ignores_incomplete_verifications():
    verifications = [
        NFRVerification("NFR-1", QualityCharacteristic.PERFORMANCE_EFFICIENCY, "Load test", "p95<=2s", passed=True),
        NFRVerification("NFR-2", QualityCharacteristic.SECURITY, "Pen test", "no injection", passed=False),
        NFRVerification("NFR-3", QualityCharacteristic.USABILITY, "Usability test", "SUS>=75", passed=None),
    ]
    assert nfr_pass_rate(verifications) == 0.5


def test_nfr_pass_rate_empty_list_is_zero():
    assert nfr_pass_rate([]) == 0.0


def test_coverage_by_characteristic_counts_correctly():
    verifications = [
        NFRVerification("NFR-1", QualityCharacteristic.PERFORMANCE_EFFICIENCY, "Load test", "p95<=2s"),
        NFRVerification("NFR-2", QualityCharacteristic.PERFORMANCE_EFFICIENCY, "Load test", "p99<=1s"),
        NFRVerification("NFR-3", QualityCharacteristic.SECURITY, "Pen test", "no injection"),
    ]
    coverage = coverage_by_characteristic(verifications)
    assert coverage[QualityCharacteristic.PERFORMANCE_EFFICIENCY.value] == 2
    assert coverage[QualityCharacteristic.SECURITY.value] == 1
    assert coverage[QualityCharacteristic.PORTABILITY.value] == 0
