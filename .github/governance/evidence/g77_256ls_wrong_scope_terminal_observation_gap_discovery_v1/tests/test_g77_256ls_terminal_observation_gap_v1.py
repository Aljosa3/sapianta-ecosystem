from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
LS = ROOT / ".github/governance/evidence/g77_256ls_wrong_scope_terminal_observation_gap_discovery_v1"
VERIFIER = LS / "analysis/G77_256LS_TERMINAL_OBSERVATION_GAP_VERIFIER_V1.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("g77_256ls_verifier", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_full_read_only_discovery_verification() -> None:
    verifier = load_verifier()
    assert verifier.verify() == verifier.TERMINAL


def test_lr_state_b_cardinality_and_unknowns_remain_exact() -> None:
    verifier = load_verifier()
    state = verifier.authenticate_lr_artifacts()
    assert state["cardinality"] == {
        "authority_consumed_count": 1,
        "authority_created_count": 1,
        "constitutional_cardinality_conflict": False,
        "human_decision_count": 1,
        "operation_attempt_count": 1,
        "retry_count": 0,
    }
    assert state["operation"]["p11_entry_count"].startswith("UNKNOWN__")
    assert state["operation"]["protected_effect_count"].startswith("UNKNOWN__")


def test_pipeline_localizes_first_unverified_edge_without_inference() -> None:
    verifier = load_verifier()
    pipeline = verifier.authenticate_decision_and_report()["observation_pipeline"]
    status = {item["edge"].split("__", 1)[0]: item["status"] for item in pipeline}
    assert status["A"] == "PROVEN"
    assert status["D"] == "PROVEN"
    assert status["E"] == "NOT_OBSERVED__FIRST_UNVERIFIED_EDGE"
    assert status["F"] == "UNKNOWN"
    assert status["G"] == "UNKNOWN"
    assert status["H"] == "UNKNOWN"


def test_serial_classification_does_not_promote_absence_to_zero() -> None:
    verifier = load_verifier()
    serial = verifier.authenticate_decision_and_report()["serial_analysis"]
    assert serial["boot_evidence"] == "PROVEN"
    assert serial["guest_start_evidence"].startswith("PROVEN__")
    for field in (
        "governed_execution_start_evidence",
        "wrong_scope_evaluation_evidence",
        "denial_evidence",
        "p11_evidence",
        "protected_effect_evidence",
        "terminal_exit_evidence",
    ):
        assert serial[field].startswith("INCONCLUSIVE__")


def test_failure_is_harness_proof_lifetime_not_production_semantics() -> None:
    verifier = load_verifier()
    value = verifier.authenticate_decision_and_report()["failure_novelty_and_convergence"]
    assert value["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert value["production_behavior_impact"] == (
        "NONE_PROVEN__GOVERNED_GUEST_EXECUTION_NOT_OBSERVED"
    )


def test_ls_has_zero_execution_and_zero_route_delta() -> None:
    verifier = load_verifier()
    discovery = verifier.authenticate_decision_and_report()
    assert set(discovery["execution_counters_ls"].values()) == {0}
    architecture = discovery["architecture"]
    assert architecture["production_files_changed"] == 0
    assert architecture["owner_delta"] == 0
    assert architecture["route_delta"] == 0
    assert (architecture["route_count_before"], architecture["route_count_after"]) == (1, 1)


def test_no_retry_or_authority_transfer_is_authorized() -> None:
    verifier = load_verifier()
    envelope = __import__("json").loads(verifier.DECISION.read_bytes())
    decision = envelope["decision"]
    assert decision["operational_retry_authorized"] == "NO"
    assert decision["operational_retry_required"] == (
        "NO_DECISION_IN_LS__DEPENDS_ON_FUTURE_GOVERNED_DELTA"
    )
    assert envelope["discovery"]["capability_specification"]["authority_effect"].startswith("NONE__")
