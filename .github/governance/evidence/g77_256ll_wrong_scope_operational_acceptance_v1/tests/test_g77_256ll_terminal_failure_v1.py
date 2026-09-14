from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
LL = ROOT / ".github/governance/evidence/g77_256ll_wrong_scope_operational_acceptance_v1"
LK = ROOT / ".github/governance/evidence/g77_256lk_wrong_scope_fresh_phase_a_decision_v1"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_bytes())
    assert path.read_bytes() == canonical_bytes(value)
    return value


def test_exact_lk_decision_hashes_and_identity() -> None:
    path = LK / "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_V1.json"
    envelope = load(path)
    decision = envelope["decision_object"]
    assert sha256(path) == "4e263a945d3ab5bd0e4eab398df232c891347396b3fd4f7c34b83d91bf5a4adc"
    assert envelope["decision_object_sha256"] == hashlib.sha256(canonical_bytes(decision)).hexdigest()
    assert envelope["decision_object_sha256"] == "c50473b9089c66363b7a9310e55b382d8e95adebef36c7bf734e6adc39a305fc"
    assert decision["DECISION_OBJECT_ID"] == "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
    assert decision["CANONICAL_OPERATION_ID"] == "G77_256LK_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
    assert decision["VECTOR"] == "WRONG_SCOPE"


def test_one_human_source_and_one_unconsumed_nonreusable_authority() -> None:
    source = LL / "G77_256LL_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff_path = LL / "G77_256LL_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    handoff = load(handoff_path)
    authority = handoff["authorization"]
    assert len(list(LL.glob("*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*.txt"))) == 1
    assert len(list(LL.glob("*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*.json"))) == 1
    assert len(source.read_bytes()) == 1632
    assert sha256(source) == "5c74cd407850409342fbcacc142aa3559a8d59614e9ff5a1cb81e796beb93f11"
    assert sha256(handoff_path) == "7823f064c0d92da35a94a39a920a1280f2850b97a023ba5c84ac148a2029ddb9"
    assert handoff["authorization_sha256"] == hashlib.sha256(canonical_bytes(authority)).hexdigest()
    assert authority["authorization_source_sha256"] == sha256(source)
    assert authority["authorized_operation_identity"] == "G77_256LK_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
    assert authority["authorized_vector"] == "WRONG_SCOPE"
    assert authority["wrong_scope_operational_attempt_limit"] == 1
    assert authority["authorization_reusable"] is False
    assert authority["retry_limit"] == authority["repair_limit"] == authority["replay_limit"] == 0


def test_context_is_exact_and_no_network() -> None:
    context = load(LL / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    inner = {key: value for key, value in context.items() if key != "context_sha256"}
    assert context["context_sha256"] == hashlib.sha256(canonical_bytes(inner)).hexdigest()
    assert context["generation_identity"] == "G77_256LK_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
    assert context["operation_identity"] == "G77_256LK_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
    assert context["repository_head"] == "584aa26914aa5a4547070bbf91bfedf2250d205c"
    assert context["repository_tree"] == "b0c5083e3da47d23389d148c0f3bb8c776b6cbb0"
    argv = context["canonical_argv"]
    assert argv.count("-nic") == 1
    assert argv[argv.index("-nic") + 1] == "none"


def test_stop_preceded_consumption_and_every_operation_boundary() -> None:
    forbidden = [
        "G77_256LL_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
        "G77_256LL_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256LL_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256LL_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
        "operation_state/receipts/G77_256LK_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
        "operation_state/receipts/G77_256LK_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json",
        "operation_state/runtime_export/G77_256LK_RAW_EXECUTION_EVIDENCE_V1.jsonl",
        "operation_state/runtime_export/G77_256LK_AUTHORITY_CHECKPOINT_V1.json",
        "operation_state/runtime_export/G77_256LK_GUEST_EXECUTION_SEAL_V1.json",
    ]
    assert all(not (LL / relative).exists() for relative in forbidden)
    assert not (LL / "operation_state/receipts").exists()


def test_terminal_reduction_is_sealed_and_truthful() -> None:
    envelope = load(LL / "G77_256LL_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json")
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == "A__G77_256LL_AUTHORITY_BINDING_CONFLICT__STOP"
    assert reduction["preconsumption"]["failure_message"] == "durable receipt parent absent, symlinked, or non-directory"
    counters = reduction["operational_counters"]
    assert counters["human_authority_source_count"] == 1
    assert counters["authority_creation_count"] == 1
    assert counters["authority_consumption_count"] == 0
    for key in (
        "operation_attempt_count", "qemu_start_count", "vm_start_count", "retry_count",
        "operational_replay_count", "repair_retry_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count",
    ):
        assert counters[key] == 0
    assert reduction["e05"] == {
        "after": "12/18",
        "before": "12/18",
        "ll_credit": 0,
        "wrong_scope": "UNSAT__AUTHORITY_CREATED_UNCONSUMED__FINAL_ADMISSION_FAILED__OPERATIONAL_UNPROVEN",
    }


def test_g48_exactly_six_h1_headings() -> None:
    headings = [
        line for line in (LL / "G77_256LL_G48_IMPLEMENTATION_REPORT_V1.md").read_text().splitlines()
        if line.startswith("# ")
    ]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
