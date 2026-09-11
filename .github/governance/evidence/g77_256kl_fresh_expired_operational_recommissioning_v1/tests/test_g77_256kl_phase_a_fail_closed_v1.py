from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KL = Path(
    ".github/governance/evidence/"
    "g77_256kl_fresh_expired_operational_recommissioning_v1"
)
REDUCER = KL / "analysis/G77_256KL_PHASE_A_FAILURE_REDUCER_V1.py"
OUTPUT = KL / "G77_256KL_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
REPORT = KL / "G77_256KL_G48_IMPLEMENTATION_REPORT_V1.md"


def load_reducer():
    specification = importlib.util.spec_from_file_location(
        "g77_256kl_failure_reducer", ROOT / REDUCER
    )
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


R = load_reducer()


def load_reduction() -> tuple[dict, dict]:
    raw = (ROOT / OUTPUT).read_bytes()
    envelope = json.loads(raw)
    assert raw == R.canonical_bytes(envelope)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        R.canonical_bytes(reduction)
    ).hexdigest()
    return envelope, reduction


def test_failure_reduction_is_deterministic_and_sealed() -> None:
    observed, _ = load_reduction()
    assert observed == R.envelope(R.build_reduction(R.HEAD, R.NESTED_HEAD))


def test_exact_gn_schema_failure_is_reproduced_without_retry() -> None:
    _, reduction = load_reduction()
    failure = reduction["failure"]
    partial = reduction["partial_phase_a_state"]
    assert failure["failure_class"] == "EVIDENCE_OR_REPORTING_DEFECT"
    assert partial["gn_exception"] == (
        "PresentationBindingError: SEALED_REQUEST_PREAUTHORIZATION_INVALID"
    )
    assert partial["gn_unexpected_fields"] == [
        "ki_frontier_preflight_file_sha256",
        "ki_frontier_preflight_inner_sha256",
    ]


def test_human_presentation_safe_stop_and_kk_binding_are_not_proven() -> None:
    _, reduction = load_reduction()
    partial = reduction["partial_phase_a_state"]
    assert partial["fresh_kl_phase_a_presentation_ready"] == "NOT_PROVEN"
    assert partial["human_decision_presentation"].startswith("NOT_CREATED")
    assert partial["kk_closure_preflight"].startswith("NOT_CREATED")
    assert partial["authorization_presentation_state"].startswith("NOT_VALID")
    assert partial["safe_stop_state"].startswith("NOT_PROVEN")
    assert partial["transient_root_state"] == (
        "PRESENT__PHASE_A_MATERIALIZED_CHECKOUT__NONAUTHORITY__NO_VM"
    )
    assert R.TRANSIENT_ROOT.is_dir()
    assert not (ROOT / R.HUMAN_DECISION).exists()
    assert not (ROOT / R.KK_PREFLIGHT).exists()


def test_zero_operation_e05_and_architecture_are_preserved() -> None:
    _, reduction = load_reduction()
    assert not any(reduction["operational_counters"].values())
    assert reduction["baseline"] == {
        "e05_state": "VERIFIED__11_OF_18",
        "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "e05_credit": "VERIFIED__0",
        "kl_phase_a_e05_credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
    }
    assert reduction["architecture"]["production_route_before"] == 1
    assert reduction["architecture"]["production_route_after"] == 1
    assert reduction["architecture"]["parallel_flow"] == "NO"
    assert reduction["human_authority_present"] is False
    assert reduction["phase_b_started"] is False


def test_g48_has_exactly_six_h1_and_five_ria_questions() -> None:
    report = (ROOT / REPORT).read_text(encoding="utf-8")
    assert re.findall(r"^# .+$", report, flags=re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert len(re.findall(r"^\d+\. .+\?$", report, flags=re.MULTILINE)) == 5
