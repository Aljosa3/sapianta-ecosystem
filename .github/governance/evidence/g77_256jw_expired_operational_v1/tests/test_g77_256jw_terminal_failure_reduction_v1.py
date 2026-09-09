#!/usr/bin/env python3
"""Focused repository-only tests for the G77-256JW terminal reduction."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
JW = ROOT / ".github/governance/evidence/g77_256jw_expired_operational_v1"
REDUCER_PATH = JW / "analysis/G77_256JW_OPERATIONAL_FAILURE_REDUCER_V1.py"
REDUCTION_PATH = JW / "G77_256JW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
REPORT_PATH = JW / "G77_256JW_G48_IMPLEMENTATION_REPORT_V1.md"

spec = importlib.util.spec_from_file_location("g77_256jw_terminal_reducer", REDUCER_PATH)
assert spec is not None and spec.loader is not None
reducer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reducer
spec.loader.exec_module(reducer)


def test_existing_one_shot_evidence_reduces_without_operation_replay() -> None:
    reduction = reducer.analyze()
    assert reduction["terminal"] == reducer.TERMINAL
    assert reduction["authority"]["state"] == "VERIFIED__CONSUMED_NONREUSABLE"
    assert reduction["operational_counters"] == {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
        "expired_check_count": 0,
        "request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    assert reduction["recovery"] == {
        "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
        "recovery_source_generation": "G77-256JW",
        "new_generation_created": "VERIFIED__NO",
        "recovery_existing_delta_authenticated": "VERIFIED__YES",
        "recovery_duplicate_authority_consumption_count": "VERIFIED__0",
        "recovery_duplicate_operation_count": "VERIFIED__0",
        "recovery_operation_replay_count": "VERIFIED__0",
        "pre_recovery_jw_file_count_including_bytecode": 31,
        "pre_recovery_jw_file_count_excluding_bytecode": 30,
        "pre_recovery_path_inventory_sha256": "009e5e769501b4e3a95524cea2915dfe73df9e31fb8b9f3e5273866c44ae03df",
        "pre_recovery_file_hash_manifest_sha256": "930d3a3e5a3206686e4271dfeaa3b2df0b8904414e2aaddf96b1f038d7afbc9a",
        "pre_recovery_reducer_sha256": "55f61b59d0e43a5cddeaffa2b5b3806720ffbfaab645584a081b581368c9b625",
        "pre_recovery_reduction_sha256": "514749904b792b05dd0b7507a39d166e84eda5c818c59c3e5df9f276be2642c2",
        "pre_recovery_report_sha256": "4788eecd2009c58d3d8e15a3dea50f11a90a1b0fb62509e0fe334be3352e092f",
        "durable_and_transient_serial_byte_identity": "VERIFIED__SHA256_6de3f0ec500b19f189aac07ba1612c89e86305e8fb8c0d2e7f3195bcea580144",
    }


def test_traceback_parser_distinguishes_source_echo_from_terminal_failure() -> None:
    serial = (
        b'prefix raise RuntimeError("sealed operation context checkout binding mismatch")\r\n'
        b"prefix RuntimeError: sealed operation context checkout binding mismatch\r\n"
    )
    assert reducer.traceback_failure_cardinality(serial) == {
        "phrase_occurrence_count": 2,
        "source_echo_occurrence_count": 1,
        "terminal_runtime_error_occurrence_count": 1,
    }


def test_role_localization_is_exact_and_repair_is_deferred() -> None:
    reduction = reducer.analyze()
    mismatch = reduction["role_mismatch"]
    assert mismatch["differing_sealed_fields"] == ["repository_head", "repository_tree"]
    assert mismatch["checkout_binding_matches_stable_runtime_checkout"] is True
    assert mismatch["er_loader_requires_role_identity_collapse"] is True
    assert reduction["frontier"]["minimum_legal_next_delta"] == (
        "SEPARATE_REPOSITORY_ONLY_ER_CONTEXT_CHECKOUT_ROLE_SEPARATION_REPAIR_GENERATION"
    )


def test_sealed_terminal_reduction_matches_read_only_analysis() -> None:
    envelope = reducer.load_canonical(REDUCTION_PATH)
    reduction = reducer.analyze()
    assert envelope["reduction"] == reduction
    assert envelope["reduction_sha256"] == reducer.sha256_bytes(
        reducer.canonical_bytes(reduction)
    )


def test_g48_structure_recovery_fields_and_final_verdict() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for question in (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ):
        assert report.count(question) == 1
    assert "RECOVERY_TYPE: `SAME_GENERATION_PROVIDER_LIMIT_RECOVERY`" in report
    assert "RECOVERY_DUPLICATE_AUTHORITY_CONSUMPTION_COUNT: `VERIFIED__0`" in report
    assert report.rstrip().endswith(reducer.TERMINAL)


def test_reducer_has_no_operational_launcher_or_repair_path() -> None:
    source = REDUCER_PATH.read_text(encoding="utf-8")
    assert "qemu-system-x86_64" not in source
    assert "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py" not in source
    assert "--write" in source
    assert "TERMINAL_REDUCTION_ALREADY_EXISTS" in source
