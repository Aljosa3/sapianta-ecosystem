#!/usr/bin/env python3
"""Read-only authentication of terminal G77-256JE recovery evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
JE = ROOT / ".github/governance/evidence/g77_256je_future_fresh_human_authorized_operational_denial_v1"
RECEIPTS = JE / "operation_state/receipts"
RUNTIME = JE / "operation_state/runtime_export"
HEAD = "393f887f62d56811092ff6ee5aacb273f3c10d83"
TREE = "d304bb2b5543ba04e8b8b1e8fdf96f9cb9067ea5"
GENERATION = "G77_256JE_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JE_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
TERMINAL = "N__REQUEST_NOT_CREATED__CURRENT_FM_CONTEXT_OWNER_REJECTED_SEALED_OPERATION_PROJECTION_AS_NOT_NAMESPACE_BOUND"
SERIAL_SHA256 = "37b1d2cb48252797f90b3b8f94f8e537dad8dfbddda25a7d3e94c3c99001d73d"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result, f"duplicate JSON key: {path.name}:{key}"
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def envelope(path: Path, key: str) -> dict[str, Any]:
    outer = load_unique(path)
    assert outer[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(outer[key])).hexdigest()
    return outer[key]


def test_exact_jd_baseline_and_consumed_authority() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == HEAD
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == TREE
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    checkpoint = envelope(JE / "G77_256JE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    assert checkpoint["generation_identity"] == GENERATION
    assert checkpoint["operation_identity"] == OPERATION
    assert checkpoint["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1
    assert checkpoint["authority_reusable"] is False
    assert checkpoint["final_admission_validation"] == "PASS"
    assert checkpoint["admission_result"] == "ADMIT_TO_BOOT_BOUNDARY_ONLY"


def test_one_correlated_no_network_qemu_operation() -> None:
    pre = load_unique(RECEIPTS / "G77_256JE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256JE_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["generation_identity"] == post["generation_identity"] == GENERATION
    assert pre["operation_identity"] == post["operation_identity"] == OPERATION
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert pre["vector"] == post["vector"]
    assert post["completed_unix_ns"] > post["started_unix_ns"]
    assert post["process_exit_status"] == 0
    argv = post["vector"]["argv"]
    assert argv.count("-nic") == 1 and argv[argv.index("-nic") + 1] == "none"
    assert post["candidate_sha256"] == "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
    assert post["context_sha256"] == "1e04e1d34e77dd0605eb03e21c2c8f51dc99b3c68fbe60b01f539f9ad0b590c3"
    assert post["vector"]["canonical_argv_sha256"] == "92256e675832e3a43b39cf3bf7e3699d418707da2d22a0c0ff9d1a7d5a72afb3"


def test_serial_proves_pre_request_namespace_failure_and_poweroff() -> None:
    serial = JE / "G77_256JE_SERIAL_CONSOLE_V1.log"
    assert sha256(serial) == SERIAL_SHA256
    payload = serial.read_bytes()
    assert b"G77_256FM_BOOT_MARKER=PASS" in payload
    assert b"sealed operation projection is not namespace-bound" in payload
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in payload
    assert b"Powering off." in payload and b"reboot: Power down" in payload
    assert b"operational Human act is not current" not in payload
    for relative in load_unique(JE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")["guest_output_relative_paths"]:
        assert not (RUNTIME / relative).exists()


def test_terminal_reduction_and_g48_shape() -> None:
    reduction = envelope(JE / "G77_256JE_SPCE_TERMINAL_REDUCTION_V1.json", "reduction")
    assert reduction["terminal"] == TERMINAL
    assert reduction["e05"] == {"after": "VERIFIED__10_OF_18", "before": "VERIFIED__10_OF_18", "credit": "VERIFIED__0", "future": "NOT_PROVEN_OPERATIONALLY"}
    expected = {
        "authorization_presentation": "VERIFIED__1", "human_authorization": "VERIFIED__1",
        "authority_consumption": "VERIFIED__1", "pre": "VERIFIED__1",
        "fm_operational_invocation": "VERIFIED__1", "qemu": "VERIFIED__1",
        "vm": "VERIFIED__1", "vm_boot": "VERIFIED__1", "operation_attempt": "VERIFIED__1",
        "request": "VERIFIED__0", "future_denial": "VERIFIED__0", "p11_entry": "VERIFIED__0",
        "protected_invocation": "VERIFIED__0", "protected_effect": "VERIFIED__0",
        "retry": "VERIFIED__0", "repair_retry": "VERIFIED__0", "replay": "VERIFIED__0",
    }
    assert reduction["operational_counters"] == expected
    assert reduction["shadow_automation"]["status"] == "VERIFIED__ABSENT"
    report = (JE / "G77_256JE_G48_IMPLEMENTATION_REPORT_V1.md").read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(TERMINAL)
