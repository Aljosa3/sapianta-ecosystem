from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[5]
KY = ROOT / ".github/governance/evidence/g77_256ky_fresh_expired_operational_recommissioning_v1"
RUNTIME = KY / "operation_state/runtime_export"
TERMINAL = (
    "I__KY_ONE_SHOT_EXPIRED_ATTEMPT_TERMINATED_AT_HUMAN_ACT_CONTEXT_BINDING__"
    "FAIL_CLOSED__NO_E05_CREDIT__NO_RETRY"
)
HUMAN_SHA256 = "cca776c3b01cc45d31c572cff16e95d15193bd7318cdcaf3142485cc669c92b4"
AUTHORITY_DIGEST = "a0abdc283e8414b794d0765c3d074690a4c17bc938af1d34549535c1aa32ea92"
CONTEXT_SHA256 = "cb36b379fc20937e905fe766db044f65e299d46b85d0fbc12af8b5be01ea9d7a"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    raw = path.read_bytes()
    value = json.loads(raw)
    assert raw == canonical_bytes(value), path
    return value


def inner(path: Path, key: str) -> dict:
    envelope = load(path)
    value = envelope[key]
    assert envelope[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value)).hexdigest(), path
    return value


def raw_records() -> list[dict]:
    path = RUNTIME / "G77_256KY_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [record["record_sequence"] for record in records] == list(range(19))
    return records


def test_human_source_handoff_and_preconsumption_digest_chain() -> None:
    source = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff_path = KY / "G77_256KY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    binding_path = KY / "G77_256KY_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
    assert len(source.read_bytes()) == 1208
    assert sha256(source) == HUMAN_SHA256
    assert sha256(handoff_path) == AUTHORITY_DIGEST
    handoff = inner(handoff_path, "authorization")
    binding = inner(binding_path, "invocation_binding")
    assert handoff["authorization_source_sha256"] == HUMAN_SHA256
    assert handoff["authorized_context_sha256"] == CONTEXT_SHA256
    assert handoff["authorized_repository_head"] == "d19208af9d9633c764838399e5a86a441e9386ef"
    assert handoff["authorized_repository_tree"] == "40207213a9359f536f9e6380c113c67f5ac6ab3f"
    assert {
        AUTHORITY_DIGEST,
        binding["authenticated_canonical_authority_digest"],
        binding["sealed_invocation_authority_digest"],
        binding["final_fm_argv_authority_digest"],
    } == {AUTHORITY_DIGEST}


def test_exactly_one_consumption_attempt_qemu_and_vm_with_no_retry() -> None:
    consumption = inner(KY / "G77_256KY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    attempt = inner(KY / "G77_256KY_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json", "attempt")
    result = inner(KY / "G77_256KY_FM_OPERATIONAL_INVOCATION_RESULT_V1.json", "result")
    pre = load(KY / "operation_state/receipts/G77_256KY_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load(KY / "operation_state/receipts/G77_256KY_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    assert consumption["authority_state_before"] == "GRANTED_UNCONSUMED"
    assert consumption["authority_state_after"] == "CONSUMED"
    assert consumption["operational_counters"]["authority_consumption_count"] == 1
    assert attempt["invocation_count"] == result["invocation_count"] == 1
    assert pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
    assert pre["started_unix_ns"] == post["started_unix_ns"]
    assert result["process_exit_status"] == post["process_exit_status"] == 0
    assert result["retry_count"] == result["repair_retry_count"] == result["replay_count"] == 0
    teardown = load(RUNTIME / "G77_256KY_GUEST_TEARDOWN_SEAL_V1.json")
    assert teardown["execution_counters"]["vm_boot_count"] == 1
    assert teardown["execution_counters"]["vm_creation_count"] == 1


def test_post_kx_context_load_then_exact_context_binding_failure_before_request() -> None:
    records = raw_records()
    commissioning = [record for record in records if str(record["record_type"]).startswith("commissioning_P")]
    assert len(commissioning) == 12
    assert all(record["facts"]["result"] == "PASS" for record in commissioning)
    acts = [record for record in records if record["record_type"] == "human_operational_act_created"]
    assert len(acts) == 1
    act = acts[0]["facts"]["human_authority_act"]
    assert "authorized_context_sha256" not in act["metadata"]
    failures = [record for record in records if record["record_type"] == "first_failure"]
    assert len(failures) == 1
    assert "Human authorization does not bind the complete sealed context" in failures[0]["facts"]["first_failure"]
    assert not any(
        record["record_type"] in {"operation_request", "expired_denial", "protected_invocation", "protected_effect"}
        for record in records
    )
    owner = (ROOT / "tests/p11_da_operational_consumer_v1.py").read_text()
    assert 'validated_act.metadata.get("authorized_context_sha256")' in owner
    assert '_fail("Human authorization does not bind the complete sealed context")' in owner


def test_terminal_reduction_preserves_e05_and_exact_counters() -> None:
    reduction = inner(KY / "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "reduction")
    assert reduction["terminal"] == TERMINAL
    assert reduction["failure_novelty_and_convergence_check"]["failure_class"] == "HARNESS_OR_TEST_ARTIFACT"
    assert reduction["operation"]["context_load_after_kx"] == "VERIFIED__YES"
    assert reduction["operation"]["request_actually_presented"] == "VERIFIED__NO"
    assert reduction["e05"] == {
        "acceptance_requirement": "AVAILABLE_TO_EXPIRED_AT_GOVERNED_PRECLAIM_COORDINATE_BEFORE_P11_OPERATIONAL_ENTRY_WITH_ZERO_PROTECTED_INVOCATION_AND_EFFECT",
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__11_OF_18",
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "frontier_after": "VERIFIED__7_UNSATISFIED_OF_18",
        "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
        "ky_credit": "VERIFIED__0",
    }
    assert reduction["operational_counters"] == {
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
    assert reduction["terminality"]["terminal_stop"] == "ACTIVE"
    assert reduction["terminality"]["ky_second_attempt_allowed"] is False


def test_inherited_terminal_manifest_is_nonauthority_and_not_used_as_ky_reduction() -> None:
    manifest = inner(RUNTIME / "G77_256KY_CONTINUATION_MANIFEST_TERMINAL_V1.json", "manifest")
    assert manifest["checkpoint_is_authority"] is False
    assert manifest["generation_identity"] != "G77_256KY_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
    observation = inner(KY / "G77_256KY_PHASE_B_CONTEXT_BINDING_FAILURE_OBSERVATION_V1.json", "observation")
    assert observation["terminal_manifest_generation_identity"] == manifest["generation_identity"]
    assert "NOT_USED_AS_KY_TERMINAL_AUTHORITY" in observation["terminal_manifest_limitation"]


def test_every_ky_json_is_canonical_and_supported_envelopes_are_sealed() -> None:
    seal_keys = (
        "authorization",
        "invocation_binding",
        "checkpoint",
        "attempt",
        "result",
        "request",
        "proof",
        "observation",
        "reduction",
        "manifest",
    )
    for path in KY.rglob("*.json"):
        value = load(path)
        for key in seal_keys:
            if isinstance(value.get(key), dict) and f"{key}_sha256" in value:
                assert value[f"{key}_sha256"] == hashlib.sha256(canonical_bytes(value[key])).hexdigest(), path


def test_g48_exact_six_h1_five_questions_and_terminal_verdict() -> None:
    report = (KY / "G77_256KY_G48_IMPLEMENTATION_REPORT_V1.md").read_text()
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
