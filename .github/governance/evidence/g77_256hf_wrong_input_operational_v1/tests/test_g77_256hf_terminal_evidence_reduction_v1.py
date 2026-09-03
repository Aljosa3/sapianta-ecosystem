#!/usr/bin/env python3
"""Repository-only authentication of terminal G77-256HF evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
EVIDENCE = ROOT / ".github/governance/evidence/g77_256hf_wrong_input_operational_v1"
RUNTIME = EVIDENCE / "operation_state/runtime_export"
RECEIPTS = EVIDENCE / "operation_state/receipts"
VERDICT = (
    "FAIL_CLOSED__G77_256HF_WRONG_INPUT_OPERATIONAL_PROOF_NOT_PROVEN__"
    "GUEST_CONTEXT_ARGV_PROJECTION_MISMATCH_BEFORE_REQUEST__E05_7_OF_18__"
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
    assert path.read_bytes() == canonical_bytes(value)
    return value


def assert_envelope(path: Path, payload: str, seal: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert envelope[seal] == hashlib.sha256(
        canonical_bytes(envelope[payload])
    ).hexdigest()
    return envelope


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_base_authority_and_receipts() -> None:
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip() == "161f3eedff5398b8fac2eafb828344058427fc63"
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip() == "b53580d7af9d01cd56ddcc37d240664addecad32"
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""

    source = EVIDENCE / "G77_256HF_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    assert sha256(source) == "af185e2ff2e53596500c7720f42e566b7a1b177a74081db1665283d348c01cdc"
    handoff = load_unique(
        EVIDENCE / "G77_256HF_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    )
    authorization = handoff["authorization"]
    assert handoff["authorization_sha256"] == hashlib.sha256(
        canonical_bytes(authorization)
    ).hexdigest() == "84da1b61f29fd286465c23cd2fdb96f0211de0d422efe3be233fdfb7c5364724"
    assert authorization["authorization_source_sha256"] == sha256(source)
    assert authorization["authorization_present"] is True
    assert authorization["authorized_vector"] == "WRONG_INPUT"
    assert authorization["wrong_input_operational_attempt_limit"] == 1
    assert authorization["authorization_reusable"] is False
    assert authorization["network_authorized"] is False
    assert authorization["retry_limit"] == authorization["repair_limit"] == authorization["replay_limit"] == 0

    pre = load_unique(RECEIPTS / "G77_256HF_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256HF_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["vector"] == post["vector"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0


def test_serial_proves_boot_and_pre_request_context_failure() -> None:
    serial_path = EVIDENCE / "G77_256HF_SERIAL_CONSOLE_V1.log"
    serial = serial_path.read_bytes()
    assert sha256(serial_path) == "401ce0a9d244e5b77bce6ee89f72b800d7804c54b3483e69f8b72260796821be"
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial
    assert b"sapianta_fresh_operation_context_v1.py" in serial
    assert b"canonical argv changed outside approved operation slots" in serial
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial
    assert not (RUNTIME / "G77_256HF_RAW_EXECUTION_EVIDENCE_V1.jsonl").exists()
    assert not (RUNTIME / "G77_256HF_GUEST_EXECUTION_SEAL_V1.json").exists()


def test_terminal_reductions_counters_and_zero_credit() -> None:
    independent = assert_envelope(
        EVIDENCE / "G77_256HF_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json",
        "reduction",
        "reduction_sha256",
    )["reduction"]
    terminal = assert_envelope(
        EVIDENCE / "G77_256HF_SPCE_TERMINAL_REDUCTION_V1.json",
        "reduction",
        "reduction_sha256",
    )["reduction"]
    expected = {
        "human_operational_authority": 1,
        "pre": 1,
        "fm_operational_launcher_invocation": 1,
        "qemu": 1,
        "vm_creation": 1,
        "vm_boot": 1,
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


def test_teardown_and_final_seal() -> None:
    pre = assert_envelope(
        EVIDENCE / "G77_256HF_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json",
        "checkpoint",
        "checkpoint_sha256",
    )["checkpoint"]
    post = assert_envelope(
        EVIDENCE / "G77_256HF_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json",
        "checkpoint",
        "checkpoint_sha256",
    )["checkpoint"]
    assert pre["host_lifecycle"]["state"] == "PRE_TEARDOWN_OBSERVED"
    assert post["host_teardown"]["state"] == "TEARDOWN_COMPLETE"
    assert post["host_teardown"]["transient_root_absent"] is True
    assert post["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256hf_wrong_input_operational_v1").exists()
    assert subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256hf"],
        stdout=subprocess.DEVNULL,
        check=False,
    ).returncode != 0

    seal = assert_envelope(
        EVIDENCE / "G77_256HF_SPCE_FINAL_EXECUTION_SEAL_V1.json",
        "seal",
        "seal_sha256",
    )["seal"]
    assert seal["authority_consumed"] == 1
    assert seal["operation_count"] == seal["qemu_count"] == seal["vm_boot_count"] == 1
    assert seal["request_count"] == seal["p11_entry_count"] == 0
    assert seal["protected_invocation_count"] == seal["protected_effect_count"] == 0
    assert seal["retry_count"] == seal["repair_count"] == seal["replay_count"] == 0
    assert seal["final_result"] == VERDICT


def test_all_hf_json_is_unique_key_canonical_and_g48_has_six_headings() -> None:
    paths = sorted(EVIDENCE.rglob("*.json"))
    assert paths
    for path in paths:
        load_unique(path)
    report = (
        ROOT
        / "docs/governance/G77_256HF_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1.md"
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
