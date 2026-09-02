#!/usr/bin/env python3
"""Repository-only authentication of terminal G77-256HC evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT / ".github/governance/evidence/g77_256hc_wrong_input_operational_v1"
RUNTIME = EVIDENCE / "operation_state/runtime_export"
RECEIPTS = EVIDENCE / "operation_state/receipts"
VERDICT = (
    "FAIL_CLOSED__G77_256HC_WRONG_INPUT_OPERATIONAL_PROOF_NOT_PROVEN__"
    "GUEST_CONTEXT_OWNER_ABSENT_BEFORE_REQUEST__E05_7_OF_18__"
    "ONE_OPERATION_ONLY__NO_RETRY__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def assert_envelope(path: Path, payload: str, seal: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert path.read_bytes() == canonical_bytes(envelope)
    assert envelope[seal] == hashlib.sha256(
        canonical_bytes(envelope[payload])
    ).hexdigest()
    return envelope


def test_exact_operation_receipts_and_serial_failure_boundary() -> None:
    pre = load_unique(RECEIPTS / "G77_256HC_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256HC_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["vector"]["argv"] == post["vector"]["argv"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0
    serial = (EVIDENCE / "G77_256HC_SERIAL_CONSOLE_V1.log").read_bytes()
    assert hashlib.sha256(serial).hexdigest() == (
        "7c49bb08c3cb49c18aca5936f7c31c9a669c3bcbbc012f79154626f28eff6192"
    )
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial
    assert b"FileNotFoundError" in serial
    assert b"sapianta_fresh_operation_context_v1.py" in serial
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial


def test_terminal_reducers_counters_and_zero_credit() -> None:
    independent = assert_envelope(
        EVIDENCE / "G77_256HC_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json",
        "reduction",
        "reduction_sha256",
    )["reduction"]
    terminal = assert_envelope(
        EVIDENCE / "G77_256HC_SPCE_TERMINAL_REDUCTION_V1.json",
        "reduction",
        "reduction_sha256",
    )["reduction"]
    expected = {
        "human_operational_authority": 1,
        "pre": 1,
        "fm_operational_launcher_invocation": 1,
        "qemu": 1,
        "vm_boot": 1,
        "vm_creation": 1,
        "operation_attempt": 1,
        "wrong_input": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05_credit": 0,
    }
    assert {key: value["value"] for key, value in independent["counter_reduction"].items()} == expected
    assert terminal["operational_counters"] == expected
    assert terminal["reducers"]["gy_authoritative"] == "FAIL_CLOSED__REQUEST_COUNT_INVALID"
    assert terminal["reducers"]["agreement"] == "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0"
    assert terminal["e05"] == {"before": "7/18", "after": "7/18", "credit": 0}
    assert terminal["terminal_control"]["verdict"] == VERDICT


def test_er_lifecycle_checkpoints_teardown_and_base_integrity() -> None:
    pre = assert_envelope(
        EVIDENCE / "G77_256HC_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json",
        "checkpoint",
        "checkpoint_sha256",
    )["checkpoint"]
    post = assert_envelope(
        EVIDENCE / "G77_256HC_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json",
        "checkpoint",
        "checkpoint_sha256",
    )["checkpoint"]
    assert pre["host_lifecycle"]["state"] == "PRE_TEARDOWN_OBSERVED"
    assert post["host_teardown"]["state"] == "TEARDOWN_COMPLETE"
    assert post["host_teardown"]["transient_root_absent"] is True
    assert post["host_teardown"]["qemu_process_absent"] is True
    assert post["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256hc_wrong_input_operational_v1").exists()
    assert subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256hc"],
        stdout=subprocess.DEVNULL,
        check=False,
    ).returncode != 0


def test_final_seal_and_g48_report() -> None:
    seal = assert_envelope(
        EVIDENCE / "G77_256HC_SPCE_FINAL_EXECUTION_SEAL_V1.json",
        "seal",
        "seal_sha256",
    )["seal"]
    assert seal["operation_count"] == seal["qemu_count"] == seal["vm_boot_count"] == 1
    assert seal["request_count"] == seal["p11_entry_count"] == 0
    assert seal["protected_invocation_count"] == seal["protected_effect_count"] == 0
    assert seal["retry_count"] == seal["repair_count"] == seal["replay_count"] == 0
    report = (
        ROOT
        / "docs/governance/G77_256HC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1.md"
    ).read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(VERDICT)
