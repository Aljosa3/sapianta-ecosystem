#!/usr/bin/env python3
"""Focused fail-closed tests for read-only G77-256JH recovery reduction."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
JH = ROOT / ".github/governance/evidence/g77_256jh_future_fresh_human_authorized_operational_denial_v1"
REDUCER_PATH = JH / "analysis/G77_256JH_OPERATIONAL_DENIAL_REDUCER_V1.py"
spec = importlib.util.spec_from_file_location("g77_256jh_operational_denial_reducer", REDUCER_PATH)
assert spec is not None and spec.loader is not None
reducer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reducer
spec.loader.exec_module(reducer)


def copy_evidence(tmp_path: Path) -> Path:
    destination = tmp_path / JH.name
    shutil.copytree(JH, destination)
    return destination


def write_canonical(path: Path, value: dict[str, object]) -> None:
    path.write_bytes(reducer.canonical_bytes(value))


def test_complete_durable_recovery_reduces_to_terminal_a() -> None:
    reduction = reducer.analyze()
    assert reduction["terminal"] == reducer.TERMINAL
    assert reduction["recovery_mode"] == "SAME_GENERATION_POST_OPERATION_RECOVERY__NO_AUTHORIZATION_OR_OPERATION_REPLAY"
    assert reduction["authority"]["state"] == "VERIFIED__CONSUMED_NONREUSABLE"
    assert reduction["authority"]["final_admission"] == "VERIFIED__PASS"
    assert reduction["operational_counters"] == {
        "human_authorization_count": 1, "authority_consumption_count": 1,
        "pre_operational_count": 1, "fm_operational_invocation_count": 1,
        "qemu_count": 1, "vm_count": 1, "vm_boot_count": 1,
        "operation_attempt_count": 1, "request_count": 1, "future_denial_count": 1,
        "p11_entry_count": 0, "protected_invocation_count": 0,
        "protected_effect_count": 0, "retry_count": 0, "repair_retry_count": 0,
        "replay_count": 0, "second_authority_consumption_count": 0,
        "second_pre_count": 0, "second_fm_invocation_count": 0,
        "second_qemu_count": 0, "second_vm_count": 0,
        "second_operation_attempt_count": 0,
    }
    assert reduction["e05"] == {
        "before": "VERIFIED__10_OF_18", "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__1", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "selected_local_frontier_distance": "VERIFIED__0__FUTURE_DENIAL_TARGET_SATISFIED",
    }
    limitation = reduction["inherited_continuation_manifest_limitation"]
    assert limitation["status"] == "VERIFIED__PRESENT_AND_PRESERVED"
    assert limitation["hidden_or_rewritten"] is False


def test_sealed_reduction_and_exact_six_heading_report() -> None:
    envelope = reducer.load_canonical(JH / "G77_256JH_SPCE_TERMINAL_REDUCTION_V1.json")
    assert envelope["reduction_sha256"] == reducer.sha256_bytes(reducer.canonical_bytes(envelope["reduction"]))
    assert envelope["reduction"]["terminal"] == reducer.TERMINAL
    report = (JH / "G77_256JH_G48_IMPLEMENTATION_REPORT_V1.md").read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reducer.TERMINAL)
    assert "SAME_GENERATION_POST_OPERATION_RECOVERY" in report
    assert "INTRA_GENERATION_CROSS_WORKER_CONTINUATION = VERIFIED__JH_PROVIDER_LIMIT_POST_OPERATION_RECOVERY" in report


def test_duplicate_receipt_fails_closed(tmp_path: Path) -> None:
    evidence = copy_evidence(tmp_path)
    receipts = evidence / "operation_state/receipts"
    shutil.copy2(
        receipts / "G77_256JH_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
        receipts / "G77_256JH_SECOND_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
    )
    with pytest.raises(reducer.ReductionError, match="RECEIPT_PAIR_CARDINALITY"):
        reducer.analyze(evidence)


def test_future_semantic_drift_fails_closed(tmp_path: Path) -> None:
    evidence = copy_evidence(tmp_path)
    path = evidence / "G77_256JH_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    envelope = reducer.load_canonical(path)
    envelope["checkpoint"]["future_semantics"]["valid_from"] = 500
    envelope["checkpoint_sha256"] = reducer.sha256_bytes(reducer.canonical_bytes(envelope["checkpoint"]))
    write_canonical(path, envelope)
    with pytest.raises(reducer.ReductionError, match="FUTURE_TIME_SEMANTICS"):
        reducer.analyze(evidence)


def test_historical_denial_mutation_fails_closed(tmp_path: Path) -> None:
    evidence = copy_evidence(tmp_path)
    path = evidence / "operation_state/runtime_export/G77_256JH_AUTHORITY_CHECKPOINT_V1.json"
    checkpoint = reducer.load_canonical(path)
    checkpoint["denial_error"] = "wrong reason"
    write_canonical(path, checkpoint)
    with pytest.raises(reducer.ReductionError, match="HISTORICAL_EVIDENCE_MUTATION"):
        reducer.analyze(evidence)


def test_noncanonical_request_fails_closed(tmp_path: Path) -> None:
    evidence = copy_evidence(tmp_path)
    path = evidence / "G77_256JH_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    value = json.loads(path.read_text())
    path.write_text(json.dumps(value, indent=2) + "\n")
    with pytest.raises(reducer.ReductionError, match="NONCANONICAL_JSON"):
        reducer.analyze(evidence)
