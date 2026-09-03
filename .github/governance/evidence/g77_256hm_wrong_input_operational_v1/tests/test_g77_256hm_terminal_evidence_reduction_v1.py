#!/usr/bin/env python3
"""Repository-only authentication of terminal G77-256HM evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
RUNTIME = HM / "operation_state/runtime_export"
RECEIPTS = HM / "operation_state/receipts"
VERDICT = (
    "FAIL_CLOSED__G77_256HM_WRONG_INPUT_OPERATIONAL_PROOF_NOT_PROVEN__"
    "GUEST_BOOTSTRAP_EXPECTED_HARNESS_HASH_MISMATCH_BEFORE_REQUEST__E05_7_OF_18__"
    "ONE_OPERATION_ONLY__NO_RETRY__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            assert key not in result, f"duplicate JSON key: {key}"
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    assert isinstance(value, dict)
    assert raw == canonical_bytes(value)
    return value


def envelope(path: Path, key: str) -> dict[str, Any]:
    value = load_unique(path)
    assert value[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value[key])).hexdigest()
    return value[key]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_base_existing_grant_consumption_and_receipts() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == "45495c09edf55cc201e3d146ea77e713f579166b"
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == "37ba96de335ee91851ff682f8cd97cf4e49ab5f5"
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
    grant = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    assert sha256(grant) == "e21c8ea41df3c0bcc37bb5d80b64a8a648ac2725fdab9712ab0086cf097ac4b5"
    authority = load_unique(HM / "G77_256HM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json")
    assert authority["authorization_sha256"] == hashlib.sha256(canonical_bytes(authority["authorization"])).hexdigest()
    assert authority["authorization"]["authorization_source_sha256"] == sha256(grant)
    assert authority["authorization"]["authorization_reusable"] is False
    assert authority["authorization"]["network_authorized"] is False
    assert authority["authorization"]["retry_limit"] == authority["authorization"]["repair_limit"] == authority["authorization"]["replay_limit"] == 0
    checkpoint = envelope(HM / "G77_256HM_AUTHORITY_VALIDATION_CHECKPOINT_V1.json", "checkpoint")
    assert checkpoint["authority_consumed"] == checkpoint["authority_validated"] == 1
    pre = load_unique(RECEIPTS / "G77_256HM_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256HM_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["vector"] == post["vector"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0


def test_serial_and_guest_evidence_prove_pre_request_failure() -> None:
    serial = HM / "G77_256HM_SERIAL_CONSOLE_V1.log"
    assert sha256(serial) == "a0d0f592f657c0e846088d45c3d5c9c1cb8d62e72b94e1bf674948b5ab1cb846"
    raw = serial.read_bytes()
    assert b"G77_256FM_BOOT_MARKER=PASS" in raw
    assert b"G77_256FM_HARNESS_EXIT_STATUS=40" in raw
    records = [json.loads(line) for line in (RUNTIME / "G77_256HM_RAW_EXECUTION_EVIDENCE_V1.jsonl").read_text().splitlines()]
    assert len(records) == 2
    assert records[0]["facts"]["first_failure"] == "RuntimeError: EN harness hash mismatch"
    counters = records[0]["facts"]["execution_counters"]
    assert counters["vm_boot_count"] == counters["vm_creation_count"] == 1
    assert counters["e05_case_execution_count"] == counters["p11_entry_count"] == counters["p11_operational_invocation_count"] == 0


def test_reducers_counters_teardown_and_final_seal() -> None:
    independent = envelope(HM / "G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json", "reduction")
    terminal = envelope(HM / "G77_256HM_SPCE_TERMINAL_REDUCTION_V1.json", "reduction")
    expected = {
        "human_operational_authority": 1, "authority_consumption": 1,
        "pre": 1, "fm_operational_launcher_invocation": 1, "qemu": 1,
        "vm_creation": 1, "vm_boot": 1, "operation_attempt": 1,
        "wrong_input_operation": 0, "request": 0, "p11_entry": 0,
        "protected_invocation": 0, "protected_effect": 0, "retry": 0,
        "repair_and_continue": 0, "operational_replay": 0, "e05_credit": 0,
    }
    assert independent["counter_reduction"] == terminal["operational_counters"] == expected
    assert terminal["reducers"]["authoritative_gy_verdict"] == "FAIL_CLOSED__REQUEST_COUNT_INVALID"
    assert terminal["reducers"]["agreement"] == "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0"
    assert terminal["e05"] == {"before": "7/18", "after": "7/18", "credit": 0}
    assert terminal["terminal_control"]["verdict"] == VERDICT
    teardown = envelope(HM / "G77_256HM_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json", "checkpoint")
    assert teardown["host_teardown"]["transient_root_absent"] is True
    assert teardown["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256hm_wrong_input_operational_v1").exists()
    final = envelope(HM / "G77_256HM_SPCE_FINAL_EXECUTION_SEAL_V1.json", "seal")
    assert final["operation_count"] == final["qemu_count"] == final["vm_boot_count"] == 1
    assert final["request_count"] == final["p11_entry_count"] == final["protected_invocation_count"] == final["protected_effect_count"] == 0
    assert final["retry_count"] == final["repair_count"] == final["replay_count"] == 0
    assert final["final_result"] == VERDICT


def test_all_hm_json_canonical_and_report_has_exact_six_headings() -> None:
    for path in sorted(HM.rglob("*.json")):
        load_unique(path)
    report = (ROOT / "docs/governance/G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1.md").read_text()
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(VERDICT)
