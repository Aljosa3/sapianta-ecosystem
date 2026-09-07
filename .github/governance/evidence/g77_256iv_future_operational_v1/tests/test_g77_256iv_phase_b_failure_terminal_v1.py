#!/usr/bin/env python3
"""Repository-only authentication of the consumed G77-256IV Phase B terminal."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
IV = ROOT / ".github/governance/evidence/g77_256iv_future_operational_v1"
RECEIPTS = IV / "operation_state/receipts"
RUNTIME = IV / "operation_state/runtime_export"
REPORT = IV / "G77_256IV_G48_IMPLEMENTATION_REPORT_V1.md"
VERDICT = (
    "FAIL_CLOSED__G77_256IV_FUTURE_OPERATIONAL_PROOF_NOT_PROVEN__"
    "GUEST_AIGOL_IMPORT_ROOT_ABSENT_BEFORE_REQUEST__E05_10_OF_18__"
    "ONE_OPERATION_ONLY__NO_RETRY__HUMAN_REVIEW_REQUIRED"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        assert key not in value, f"duplicate JSON key: {key}"
        value[key] = item
    return value


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    assert isinstance(value, dict)
    assert raw == canonical_bytes(value)
    return value


def inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_unique(path)
    assert envelope[f"{key}_sha256"] == hashlib.sha256(
        canonical_bytes(envelope[key])
    ).hexdigest()
    return envelope[key]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_base_grant_authority_and_single_consumption() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "30bb9fd8d983e56362d7c95fd5d15581da27f703"
    )
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == (
        "1e9d8b76771b3cdb94e13db80bac3b097395fcf4"
    )
    grant = IV / "G77_256IV_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    assert sha256(grant) == "0e56c08ea281b377770165c3e22ca0455fc56747ea87211db3dcc284677dbe56"
    handoff = load_unique(IV / "G77_256IV_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json")
    authorization = handoff["authorization"]
    assert handoff["authorization_sha256"] == hashlib.sha256(canonical_bytes(authorization)).hexdigest()
    assert authorization["authorization_source_sha256"] == sha256(grant)
    assert authorization["authorized_vector"] == "FUTURE"
    assert authorization["future_operational_attempt_limit"] == 1
    assert authorization["retry_limit"] == authorization["repair_limit"] == authorization["replay_limit"] == 0
    assert authorization["authorization_reusable"] is False
    checkpoint = inner(
        IV / "G77_256IV_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "checkpoint",
    )
    assert checkpoint["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert checkpoint["authority_state_after"] == "CONSUMED"
    assert checkpoint["authority_consumed"] == 1
    assert checkpoint["operational_counters"]["authority_consumption"] == 1


def test_one_no_network_pre_post_receipt_pair() -> None:
    pre = load_unique(RECEIPTS / "G77_256IV_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256IV_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert pre["vector"] == post["vector"]
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
    assert post["process_exit_status"] == 0
    argv = pre["vector"]["argv"]
    assert argv.count("-nic") == 1 and argv[argv.index("-nic") + 1] == "none"
    assert pre["vector"]["canonical_argv_sha256"] == (
        "141b1eb43c88dba58d51dde7baf8fa6a4bbb477784a6fed94c46e5b8d810fd95"
    )


def test_serial_proves_boot_and_pre_request_import_failure() -> None:
    serial_path = IV / "G77_256IV_SERIAL_CONSOLE_V1.log"
    serial = serial_path.read_bytes()
    assert sha256(serial_path) == "492353716186284bb13653e8f8db4483d77798aa9613dc7c283918cceecbd6ec"
    assert b"G77_256FM_BOOT_MARKER=PASS" in serial
    assert b'File "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py", line 20' in serial
    assert b"from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import" in serial
    assert b"ModuleNotFoundError: No module named 'aigol'" in serial
    assert b"G77_256FM_HARNESS_EXIT_STATUS=1" in serial
    assert not (RUNTIME / "G77_256IV_RAW_EXECUTION_EVIDENCE_V1.jsonl").exists()
    assert not (RUNTIME / "G77_256IV_GUEST_EXECUTION_SEAL_V1.json").exists()


def test_terminal_counters_failure_frontier_and_zero_credit() -> None:
    terminal = inner(IV / "G77_256IV_SPCE_TERMINAL_REDUCTION_V1.json", "reduction")
    counters = terminal["operational_counters"]
    assert terminal["terminal"] == "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST"
    assert counters["human_operational_authority"] == counters["authority_consumption"] == 1
    assert counters["pre"] == counters["fm_operational_launcher_invocation"] == 1
    assert counters["qemu"] == counters["vm_creation"] == counters["vm_boot"] == 1
    assert counters["operation_attempt"] == 1
    for key in (
        "future_operation", "request", "future_denial", "p11_entry",
        "protected_invocation", "protected_effect", "retry", "repair_retry",
        "replay", "second_consumption", "e05_credit",
    ):
        assert counters[key] == 0
    assert terminal["e05"] == {"before": "10/18", "credit": 0, "after": "10/18"}
    assert terminal["exact_failure"] == "ModuleNotFoundError: No module named 'aigol'"
    assert terminal["terminal_control"]["verdict"] == VERDICT


def test_teardown_base_image_and_final_seal() -> None:
    assert not Path("/tmp/g77_256iv_future_operational_v1").exists()
    assert sha256(Path("/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img")) == (
        "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733"
    )
    teardown = inner(IV / "G77_256IV_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json", "checkpoint")
    assert teardown["host_teardown"]["state"] == "TEARDOWN_COMPLETE"
    assert teardown["host_teardown"]["transient_root_absent"] is True
    assert teardown["base_image"]["byte_identical"] is True
    assert subprocess.run(
        ["pgrep", "-f", "^/usr/bin/qemu-system-x86_64.*g77_256iv"],
        stdout=subprocess.DEVNULL,
        check=False,
    ).returncode != 0
    final = inner(IV / "G77_256IV_SPCE_FINAL_EXECUTION_SEAL_V1.json", "seal")
    assert final["authority_consumed"] == final["operation_count"] == final["qemu_count"] == 1
    assert final["request_count"] == final["future_denial_count"] == final["p11_entry_count"] == 0
    assert final["retry_count"] == final["repair_count"] == final["replay_count"] == 0
    assert final["final_result"] == VERDICT
    for relative, identity in final["artifacts"].items():
        assert sha256(IV / relative) == identity


def test_all_iv_json_and_python_are_canonical_or_ast_valid() -> None:
    for path in IV.rglob("*.json"):
        value = load_unique(path)
        for key in ("authorization", "checkpoint", "observation", "proof", "reduction", "request", "seal"):
            seal_key = f"{key}_sha256"
            if key in value and seal_key in value:
                assert value[seal_key] == hashlib.sha256(canonical_bytes(value[key])).hexdigest()
    for path in IV.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_report_six_headings_metrics_inventory_and_empty_index() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    required = {
        "Reuse Impact Assessment", "Infrastructure Amortization", "CCWIM",
        "Cognition Provenance", "Prompt Externalization Metrics",
        "PROJECT_PROGRESS_ESTIMATE", "CONSTITUTIONAL_HEALTH_EVIDENCE",
        "SHADOW_AUTOMATION_STATUS", "CONSTITUTIONAL_FRONTIER_DISTANCE",
        "E05_FRONTIER_DISTANCE", "SELECTED_E05_LOCAL_FRONTIER_DISTANCE",
        "GOVERNANCE_EFFICIENCE", "ARCHITECTURAL_GOVERNANCE_EFFICIENCE",
        "PROOF_REUSE_EFFICIENCY", "COGNITION_ASSISTED_HANDOFF",
        "AIGOL_CODEX_WORK_SHARE", "OVERENGINEERING_RISK",
        "PROOF_PROCESS_OVERHEAD_RISK", "COGNITION_PROVENANCE",
        "CANDIDATE_CAPABILITY", "SHADOW_DESIGN_TARGET",
        "CONSTITUTIONAL_CONTINUATION_PROGRESS", "PROMPT_CONTEXT_REUSE_RATIO",
        "REPOSITORY_DERIVED_EXECUTION_CONTEXT_RATIO",
        "CONSTITUTIONAL_PROMPT_EXTERNALIZATION_RATIO", "TOKEN_BENCHMARK",
        "LLM_COST_REDUCTION_RATIO", "LCRR", "E05_GENERATIONS_PER_CREDIT",
        "OPERATIONAL_ATTEMPTS_PER_CREDIT", "MARGINAL_E05_GENERATION_COST",
        "MARGINAL_NEW_INFRASTRUCTURE_PER_E05_CREDIT",
        "INFRASTRUCTURE_AMORTIZATION_SIGNAL", "EXPECTED_NEXT_CREDIT_GENERATION_COUNT",
    }
    assert all(token in report for token in required)
    assert report.rstrip().endswith(f"`{VERDICT}`")
    observed = [path for path in IV.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    assert len(observed) == 39
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert len(status) == 39
    assert all(line.startswith("?? ") and str(IV.relative_to(ROOT)) in line for line in status)
    assert subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip() == ""
