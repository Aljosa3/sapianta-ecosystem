from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KW = ROOT / ".github/governance/evidence/g77_256kw_fresh_expired_operational_recommissioning_v1"
RUNTIME = KW / "operation_state/runtime_export"
TERMINAL = "I__KW_PROVIDER_RECOVERY__NEW_RUNTIME_EXPORT_CUSTODY_EDGE_FOUND__CLASSIFIED__FAIL_CLOSED__NO_RETRY"
HUMAN_SHA256 = "692b106107c5959e55a727d19a1bb5cfda783b4ac91a4b6d525c1e6fee6a43bd"
HANDOFF_SHA256 = "08e4018bd8a8bc8a43e61f0f00c53e94d4a9c6688c83ab1b4caf3cd493319832"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == canonical_bytes(value)
    return value


def inner(path: Path, key: str) -> dict:
    envelope = load(path)
    value = envelope[key]
    assert envelope[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def test_exact_human_authority_and_canonical_digest_chain() -> None:
    source = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff_path = KW / "G77_256KW_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    binding_path = KW / "G77_256KW_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
    assert len(source.read_bytes()) == 1213
    assert sha256(source) == HUMAN_SHA256
    assert sha256(handoff_path) == HANDOFF_SHA256
    handoff = inner(handoff_path, "authorization")
    binding = inner(binding_path, "invocation_binding")
    assert handoff["authorization_source_sha256"] == HUMAN_SHA256
    assert handoff["authorized_repository_head"] == "681538ccd9b6faaeebff15d96881134eaef00d7e"
    assert handoff["authorized_repository_tree"] == "53164b7f60d982727bebd9a5c77d5688ee283ade"
    assert {
        HANDOFF_SHA256,
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    } == {HANDOFF_SHA256}


def test_single_consumption_single_attempt_and_no_replay() -> None:
    consumption = inner(KW / "G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    attempt = inner(KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json", "attempt")
    result = inner(KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_RESULT_V1.json", "result")
    pre = load(KW / "operation_state/receipts/G77_256KW_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load(KW / "operation_state/receipts/G77_256KW_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert consumption["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert consumption["authority_state_after"] == "CONSUMED"
    assert consumption["operational_counters"]["authority_consumption_count"] == 1
    assert attempt["invocation_count"] == 1
    assert result["process_exit_status"] == 0
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert post["process_exit_status"] == 0
    assert result["retry_count"] == result["repair_retry_count"] == result["replay_count"] == 0


def test_guest_failure_is_before_vector_request_entry_invocation_and_effect() -> None:
    records = [json.loads(line) for line in (RUNTIME / "G77_256KW_RAW_EXECUTION_EVIDENCE_V1.jsonl").read_text().splitlines()]
    assert len(records) == 15
    assert len([r for r in records if str(r.get("record_type", "")).startswith("commissioning_P")]) == 12
    failures = [r for r in records if r.get("record_type") == "first_failure"]
    assert len(failures) == 1
    assert "Permission denied: '/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'" in failures[0]["facts"]["first_failure"]
    assert not any(r.get("record_type") in {"operation_request", "expired_denial", "protected_invocation", "protected_effect"} for r in records)
    teardown = load(RUNTIME / "G77_256KW_GUEST_TEARDOWN_SEAL_V1.json")
    counters = teardown["execution_counters"]
    assert counters["vm_boot_count"] == counters["vm_creation_count"] == 1
    assert counters["e05_case_execution_count"] == 0
    assert counters["p11_entry_count"] == counters["p11_operational_invocation_count"] == 0


def test_terminal_reduction_exact_counters_and_new_edge() -> None:
    reduction = inner(KW / "G77_256KW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "reduction")
    assert reduction["terminal"] == TERMINAL
    assert reduction["initial_recovery_branch"] == "R1"
    assert reduction["terminal_recovery_branch"] == "R3"
    assert reduction["failure_novelty_and_convergence_check"]["failure_class"] == "NEW_SEMANTIC_EDGE"
    assert reduction["e05"] == {
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "kw_credit": "VERIFIED__0",
    }
    assert reduction["ex"] == {"ex_reconstructed": "VERIFIED__0", "ex_reused": "VERIFIED__17_OF_17"}
    expected = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_invocation_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_start_count": 1,
        "vm_start_count": 1,
        "operation_attempt_count": 1,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    assert reduction["operational_counters"] == expected
    assert reduction["terminality"]["auto_continuable"] is False
    assert reduction["terminality"]["human_review_required"] is True


def test_every_kw_json_is_canonical_and_supported_envelopes_are_sealed() -> None:
    seal_keys = ("authorization", "invocation_binding", "checkpoint", "attempt", "result", "request", "proof", "observation", "reduction")
    for path in KW.rglob("*.json"):
        value = load(path)
        for key in seal_keys:
            if isinstance(value.get(key), dict) and f"{key}_sha256" in value:
                assert value[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value[key])).hexdigest(), path


def test_g48_exactly_six_h1_and_five_slovenian_questions() -> None:
    report = (KW / "G77_256KW_PHASE_B_G48_IMPLEMENTATION_REPORT_V1.md").read_text()
    assert re.findall(r"^# .+$", report, re.MULTILINE) == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert len(re.findall(r"^\d\. (?:Katere|Ali)", report, re.MULTILINE)) == 5
    assert report.rstrip().endswith(TERMINAL)
