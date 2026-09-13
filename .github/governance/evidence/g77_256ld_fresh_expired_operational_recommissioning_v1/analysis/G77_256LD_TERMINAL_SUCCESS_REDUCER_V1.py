#!/usr/bin/env python3
"""Reduce the immutable one-shot LD observation to exact EXPIRED acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LD = ROOT / ".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1"
RUNTIME = LD / "operation_state/runtime_export"
RECEIPTS = LD / "operation_state/receipts"
OUTPUT = LD / "G77_256LD_SPCE_TERMINAL_SUCCESS_REDUCTION_V1.json"
FINAL_SEAL = LD / "G77_256LD_SPCE_FINAL_EXECUTION_SEAL_V1.json"
GENERATION = "G77_256LD_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LD_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
TERMINAL = (
    "A__LD_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_"
    "OPERATIONALLY_PROVEN__ONE_AUTHORITY__ONE_ATTEMPT__NO_RETRY__E05_12_OF_18"
)
HEAD = "98d059beaa148746d397d48bad9e898b1f9c2297"
TREE = "d1aadf9da3f66b2699f9b4c32647a2fe65c060cc"
SOURCE_SHA256 = "1efca9d2575cd46756e820493e97ec6b737f20f056c9261c672e495279c0db5e"
CONTEXT_SHA256 = "5b68f72437d0b9c5bdbe94024f1c6d94a8e2f01364826862b982124651c21812"
AUTHORITY_DIGEST = "67d74841f798cd81f6ddce8779fbea9a7446fc5cad1bb53f493732ba821d6ad4"
RAW_SHA256 = "12fa97ca74956c281cf70cae80f81412fe75e4442b764b451c1691f17a2c1da7"

INPUT_HASHES = {
    "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt": SOURCE_SHA256,
    "G77_256LD_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json": AUTHORITY_DIGEST,
    "G77_256LD_PRECONSUMPTION_INVOCATION_BINDING_V1.json": "cdde8481629235af93ef3f00a377d11439831df3b019d81f98a8db7c47586def",
    "G77_256LD_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json": "1bdc1f6cca1842654180a2d55440ce79b84bb8eaf58b41b147c10990f8217fe3",
    "G77_256LD_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json": "9a396cbe8f75c9776e425c12fad277413ebb046dde83d428b26d0080643d091a",
    "G77_256LD_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json": "0e4292cc8e7b250592555c105af4b28c3593dd3c3ef8b3cc4cdbb1b782ba0a73",
    "G77_256LD_FM_OPERATIONAL_INVOCATION_RESULT_V1.json": "e802a0c1cc987c6fce8337da3fc74aaf64ff5c2ba14e76bbc08e45287e339e85",
    "operation_state/receipts/G77_256LD_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "388ebc1b66616110d33b657e597eefd3c187fa90602ef98eeae60fca2e9fd0d7",
    "operation_state/receipts/G77_256LD_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json": "3203c5167c9ab01ace12eaf7d2fde2f633255d1cb0351d209d9fa56ee087788d",
    "operation_state/runtime_export/G77_256LD_RAW_EXECUTION_EVIDENCE_V1.jsonl": RAW_SHA256,
    "operation_state/runtime_export/G77_256LD_PRE_ACT_CHECKPOINT_V1.json": "53e8c1178b8e1e949b0b0daa4dea102933287cf04e8f8f06295a5a9faea19922",
    "operation_state/runtime_export/G77_256LD_AUTHORITY_CHECKPOINT_V1.json": "a2744dd8b850640d2ab02ecfa3adcc2ee7c752c88ecd64d4881df05f36ae7f4c",
    "operation_state/runtime_export/G77_256LD_GUEST_EXECUTION_SEAL_V1.json": "950218771e0c908f57c5e64ac422832df0f30cd8a441560a1cc849d1c8d0595f",
    "operation_state/runtime_export/G77_256LD_GUEST_TEARDOWN_SEAL_V1.json": "ceca92b22fe1c93dd68db0d229943d4952a10d3bd8a0c80123ca622247e8f2fe",
    "operation_state/runtime_export/G77_256LD_CONTINUATION_MANIFEST_TERMINAL_V1.json": "af6bd152c6b38fe419a183193f9b4d129b7d027ef4b613c3b7f6de8ed6f6286f",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"NONCANONICAL_JSON:{path.name}")
    return value


def inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"SEAL_MISMATCH:{path.name}")
    return value


def raw_records() -> list[dict[str, Any]]:
    path = RUNTIME / "G77_256LD_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if [record.get("record_sequence") for record in records] != list(range(31)):
        raise RuntimeError("RAW_SEQUENCE_MISMATCH")
    if any(record.get("schema_id") != "G77_256ER_RAW_EXECUTION_EVIDENCE_V1" for record in records):
        raise RuntimeError("RAW_SCHEMA_MISMATCH")
    return records


def one(records: list[dict[str, Any]], record_type: str) -> dict[str, Any]:
    matches = [record for record in records if record.get("record_type") == record_type]
    if len(matches) != 1:
        raise RuntimeError(f"RAW_RECORD_CARDINALITY:{record_type}")
    return matches[0]["facts"]


def authenticate_observation() -> dict[str, Any]:
    for relative, expected in INPUT_HASHES.items():
        if sha256_path(LD / relative) != expected:
            raise RuntimeError(f"IMMUTABLE_OPERATION_ARTIFACT_MISMATCH:{relative}")
    if len((LD / "G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt").read_bytes()) != 1381:
        raise RuntimeError("HUMAN_SOURCE_BYTE_COUNT_MISMATCH")

    handoff = inner(LD / "G77_256LD_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json", "authorization")
    binding = inner(LD / "G77_256LD_PRECONSUMPTION_INVOCATION_BINDING_V1.json", "invocation_binding")
    preconsumption = inner(LD / "G77_256LD_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json", "checkpoint")
    consumption = inner(LD / "G77_256LD_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    attempt = inner(LD / "G77_256LD_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json", "attempt")
    result = inner(LD / "G77_256LD_FM_OPERATIONAL_INVOCATION_RESULT_V1.json", "result")
    pre = load_canonical(RECEIPTS / "G77_256LD_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_canonical(RECEIPTS / "G77_256LD_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    guest_execution = load_canonical(RUNTIME / "G77_256LD_GUEST_EXECUTION_SEAL_V1.json")
    teardown = load_canonical(RUNTIME / "G77_256LD_GUEST_TEARDOWN_SEAL_V1.json")
    terminal_manifest = inner(RUNTIME / "G77_256LD_CONTINUATION_MANIFEST_TERMINAL_V1.json", "manifest")
    records = raw_records()

    digests = {
        AUTHORITY_DIGEST,
        binding.get("authenticated_canonical_authority_digest"),
        binding.get("sealed_invocation_authority_digest"),
        binding.get("final_fm_argv_authority_digest"),
        preconsumption.get("bindings", {}).get("human_authority_handoff_sha256"),
        consumption.get("authority_handoff_file_sha256"),
        attempt.get("authority_handoff_file_sha256"),
        pre.get("execution_authority_file_sha256"),
        post.get("execution_authority_file_sha256"),
    }
    if digests != {AUTHORITY_DIGEST}:
        raise RuntimeError("AUTHORITY_DIGEST_CHAIN_MISMATCH")
    if (
        handoff.get("authorization_source_sha256") != SOURCE_SHA256
        or handoff.get("authorized_context_sha256") != CONTEXT_SHA256
        or handoff.get("authorized_generation_identity") != GENERATION
        or handoff.get("authorized_operation_identity") != OPERATION
        or handoff.get("authorized_vector") != "EXPIRED"
        or handoff.get("expired_operational_attempt_limit") != 1
        or handoff.get("retry_limit") != 0
        or handoff.get("repair_limit") != 0
        or handoff.get("replay_limit") != 0
        or handoff.get("authorization_reusable") is not False
    ):
        raise RuntimeError("AUTHORITY_BINDING_OR_LIMIT_MISMATCH")
    zero_before = preconsumption.get("operational_counters", {}).copy()
    zero_before.pop("operational_authorization_count", None)
    if (
        preconsumption.get("authority_state") != "GRANTED_UNCONSUMED"
        or preconsumption.get("operational_counters", {}).get("operational_authorization_count") != 1
        or any(zero_before.values())
        or consumption.get("authority_state_before") != "GRANTED_UNCONSUMED"
        or consumption.get("authority_state_after") != "CONSUMED"
        or consumption.get("operational_counters", {}).get("authority_consumption_count") != 1
        or attempt.get("invocation_count") != 1
        or result.get("invocation_count") != 1
        or result.get("process_exit_status") != 0
        or result.get("process_exception") is not None
        or any(result.get(key) != 0 for key in ("retry_count", "repair_retry_count", "replay_count"))
        or pre.get("execution_attempt_count") != 1
        or post.get("execution_attempt_count") != 1
        or pre.get("started_unix_ns") != post.get("started_unix_ns")
        or post.get("process_exit_status") != 0
    ):
        raise RuntimeError("ONE_SHOT_HOST_COUNTER_OR_RESULT_MISMATCH")

    created = one(records, "human_operational_act_created")
    denied = one(records, "expired_denial_complete")
    reduced = one(records, "p11_attempt_result")
    producer_consumer = one(records, "b6_producer_consumer_reduction")
    act = created.get("human_authority_act", {})
    authorized_input = denied.get("authorized_input_record", {})
    if (
        created.get("creation_count") != 1
        or act.get("metadata", {}).get("authorized_context_sha256") != CONTEXT_SHA256
        or act.get("metadata", {}).get("generation_identity") != GENERATION
        or act.get("metadata", {}).get("non_reusable") is not True
        or act.get("metadata", {}).get("non_transferable") is not True
        or authorized_input.get("authorization_reference") != act.get("authority_act_identity")
        or act.get("payload", {}).get("case_id") != OPERATION
        or act.get("payload", {}).get("valid_from_unix_ns") != 100
        or act.get("payload", {}).get("valid_until_unix_ns") != 1000
        or denied.get("owner_state_before") != {"revision": 0, "state": "AVAILABLE"}
        or denied.get("owner_state_after") != {"revision": 1, "state": "EXPIRED"}
        or denied.get("denial_error") != "one-use Human act expired before PRECLAIM"
        or denied.get("denial_point") != "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT"
        or denied.get("p11_entry_count") != 0
        or denied.get("invocation_count") != 0
        or denied.get("protected_effect_count") != 0
        or denied.get("output_present") is not False
        or reduced.get("result") != "PASS__ONE_VALID_ACT__ONE_ISOLATED_EXPIRED_REQUEST_DENIED_AT_D2_BEFORE_PRECLAIM_ENTRY_CLAIM_INVOCATION_OR_EFFECT"
        or reduced.get("expired_invariant_pass") is not True
        or reduced.get("prospective_b6_counters") != {
            "boundary_request_count": 1,
            "p11_entry_count": 0,
            "p11_operational_invocation_count": 0,
            "pre_attempt_denial_count": 1,
            "protected_effect_count": 0,
        }
        or producer_consumer.get("producer_consumer_agreement") is not True
        or producer_consumer.get("denied_request_entry_increment") != 0
        or producer_consumer.get("denied_request_invocation_increment") != 0
        or producer_consumer.get("denied_request_effect_increment") != 0
    ):
        raise RuntimeError("EXPIRED_ACCEPTANCE_OBSERVATION_MISMATCH")

    guest_counters = guest_execution.get("execution_counters", {})
    if (
        guest_execution.get("generation_identity") != GENERATION
        or guest_execution.get("case_id") != OPERATION
        or guest_execution.get("operational_result") != "PASS__EXPIRED_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT"
        or guest_execution.get("first_failure") is not None
        or teardown.get("raw_evidence_sha256") != RAW_SHA256
        or teardown.get("raw_record_count") != 31
        or teardown.get("teardown_state") != "COMPLETE"
        or teardown.get("first_failure") is not None
        or guest_counters.get("e05_case_execution_count") != 1
        or guest_counters.get("p11_entry_count") != 0
        or guest_counters.get("p11_operational_invocation_count") != 0
        or guest_counters.get("automatic_retry_count") != 0
        or guest_counters.get("execution_replay_count") != 0
        or guest_counters.get("repair_and_continue_count") != 0
        or guest_counters.get("vm_boot_count") != 1
        or terminal_manifest.get("authority_state", {}).get("authority_survives") is not False
        or terminal_manifest.get("authority_state", {}).get("reusable") is not False
        or terminal_manifest.get("authority_state", {}).get("transferable") is not False
        or terminal_manifest.get("first_failure_or_current_result") != "PASS__E05_EXPIRED_DENIAL__GUEST_TEARDOWN_COMPLETE"
    ):
        raise RuntimeError("GUEST_SEAL_OR_TEARDOWN_MISMATCH")
    return {
        "authority_act_identity": act["authority_act_identity"],
        "authorization_reference": authorized_input["authorization_reference"],
        "request_identity": denied["request_identity"],
        "denial_point": denied["denial_point"],
        "denial_error": denied["denial_error"],
        "owner_state_before": denied["owner_state_before"],
        "owner_state_after": denied["owner_state_after"],
        "recorded_at_utc": result["recorded_at_utc"],
    }


def operational_counters() -> dict[str, int]:
    return {
        "human_authority_source_count": 1,
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_invocation_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_start_count": 1,
        "vm_start_count": 1,
        "operation_attempt_count": 1,
        "operation_request_count": 1,
        "expired_denial_count": 1,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "second_operation_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "authority_transfer_count": 0,
        "historical_authority_reuse_count": 0,
        "alternate_authority_path_count": 0,
        "p11_bypass_count": 0,
        "parallel_route_count": 0,
    }


def build_reduction() -> dict[str, Any]:
    observation = authenticate_observation()
    return {
        "schema_id": "G77_256LD_SPCE_TERMINAL_SUCCESS_REDUCTION_V1",
        "terminal": TERMINAL,
        "result_class": "SUCCESSFUL_ACCEPTANCE_OBSERVATION",
        "generation": "G77-256LD",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "vector": "EXPIRED",
        "target_acceptance_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
        "recorded_at_utc": observation["recorded_at_utc"],
        "entry": {"head": HEAD, "tree": TREE, "subject": "G77-256LC reissue EXPIRED bootstrap digest projection", "branch": "g77-256fl-wrong-attempt-preboot-blocker", "remote_head": HEAD, "remote_equality": "VERIFIED__DIRECT_LS_REMOTE", "stable_ancestry": "VERIFIED"},
        "nested_authority": {"head": "3183bab71f8f30397c0309dd2e6d846d14a11f66", "tree": "7c32ec05efc2be43297849bc38ec8766514a523d", "tag": "sapianta-system-nested-authority-3183bab-v1", "state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL"},
        "human_authority": {"source_path": ".github/governance/evidence/g77_256ld_fresh_expired_operational_recommissioning_v1/G77_256LD_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt", "source_byte_count": 1381, "source_sha256": SOURCE_SHA256, "canonical_handoff_sha256": AUTHORITY_DIGEST, "authentication": "VERIFIED__EXACT_HUMAN_CREATED_SOURCE", "binding": "VERIFIED__EXACT_GENERATION_OPERATION_VECTOR_REQUEST_CONTEXT_AND_SOURCE", "consumption": "VERIFIED__ONCE", "reusable": False, "transferable": False, "survives": False},
        "operational_observation": {**observation, "acceptance_requirement": "AVAILABLE_TO_EXPIRED_AT_GOVERNED_PRECLAIM_COORDINATE_BEFORE_P11_OPERATIONAL_ENTRY_WITH_ZERO_PROTECTED_INVOCATION_AND_EFFECT", "governed_preclaim_coordinate_unix_ns": 1000, "result": "PASS__EXPIRED_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT", "raw_evidence_sha256": RAW_SHA256, "raw_record_count": 31, "teardown_state": "COMPLETE"},
        "operational_counters": operational_counters(),
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__12_OF_18", "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18", "frontier_after": "VERIFIED__6_UNSATISFIED_OF_18", "expired": "VERIFIED__PROVEN_OPERATIONALLY", "current_generation_credit": "VERIFIED__1"},
        "failure_novelty_and_convergence_check": {"failure_class": "PROOF_GAP", "novelty": "NO_KNOWN_STATIC_FAILURE__FRESH_OPERATIONAL_OBSERVATION_WAS_ABSENT_AND_IS_NOW_SUPPLIED", "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_DENIAL_BEFORE_ATTEMPT_WITH_ZERO_EFFECT", "previous_closest_edge": "LD_CURRENT_MATERIALIZED_PREOPERATIONAL_CHAIN_AND_PRESENTATION_READY", "semantic_difference": "FRESH_OPERATIONAL_EXPIRED_DENIAL_NOW_OBSERVED", "production_behavior_impact": "NONE__EXPECTED_FAIL_CLOSED_PATH_OBSERVED", "new_capability_required": "NO", "new_proof_required": "SATISFIED__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_OBSERVATION", "convergence_signal": "LD_FRESH_EXPIRED_OPERATIONAL_ACCEPTANCE_OBSERVED__E05_FRONTIER_MOVED_11_TO_12", "repetition_pressure": "REDUCED__NO_SECOND_EXPIRED_OPERATION_REQUIRED", "verification_amplification_risk": "HIGH_IF_OPERATION_IS_REPEATED_AFTER_ACCEPTANCE", "classification_confidence": "VERIFIED__HIGH"},
        "cross_vector_reuse_assessment": {"cross_vector_reuse_scope": "COMMON_PHASE_A_FM_GN_ER_P11_EX_INFRASTRUCTURE", "shared_owner_or_vector_specific": "SHARED_OWNERS__LD_OPERATIONAL_PROOF_VECTOR_SPECIFIC", "shared_preoperational_infrastructure": "VERIFIED__YES", "shared_authority_mechanism": "VERIFIED__YES__NO_AUTHORITY_TRANSFER", "shared_binding_rules": "VERIFIED__COMMON__PER_GENERATION_REVALIDATION_REQUIRED", "shared_defect": "VERIFIED__NO", "shared_required_delta": "VERIFIED__NO__LD_CONCERNS_EXPIRED_ONLY", "affected_vectors": ["EXPIRED"], "unaffected_vectors": ["FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"], "reuse_preconditions": "FRESH_PER_VECTOR_AUTHORITY_AND_EXACT_OPERATIONAL_BINDING", "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR", "expected_future_proof_reduction": "COMMON_STATIC_AND_AUTHORITY_MECHANISM_REUSABLE__NO_OPERATIONAL_OR_E05_CREDIT_TRANSFER"},
        "frontier": {"last_verified_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY", "first_broken_edge": "NONE_OBSERVED_IN_LD_SCOPE", "first_unverified_operational_edge": "NEXT_E05_VECTOR_NOT_SELECTED_IN_LD", "minimum_missing_capability": "NONE_FOR_EXPIRED_ACCEPTANCE", "minimum_missing_proof": "NONE_FOR_EXPIRED_ACCEPTANCE", "minimum_legal_next_delta": "STOP__INDEPENDENT_HUMAN_HEAD_TREE_REMOTE_AUTHENTICATION_BEFORE_ANY_SUCCESSOR"},
        "governance": {"project_state": "VERIFIED__LD_TERMINAL_EXPIRED_ACCEPTANCE_PROVEN", "informal_project_progress_estimate": "ESTIMATED__E05_MOVED_TO_12_OF_18_WITH_SIX_UNSATISFIED", "constitutional_health_evidence": "VERIFIED__ONE_AUTHORITY__ONE_ATTEMPT__FAIL_CLOSED_DENIAL__ZERO_EFFECT__NO_RETRY", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "governance_efficiency": "ESTIMATED__HIGH__EX_17_OF_17_AND_EXISTING_OWNER_ROUTE_REUSED", "overengineering_risk": "ESTIMATED__HIGH_IF_ACCEPTED_EXPIRED_EDGE_IS_REPEATED", "cognition_provenance": "INDEPENDENTLY_HUMAN_AUTHENTICATED_LC_CHECKPOINT + DURABLE_LD_PHASE_A_WORKSPACE + FRESH_HUMAN_CREATED_AUTHORIZATION_SOURCE_SHA256_1efca9d2575cd46756e820493e97ec6b737f20f056c9261c672e495279c0db5e + DURABLE_ONE_SHOT_LD_PHASE_B_OPERATIONAL_EVIDENCE + HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF + CURRENT_ACCOUNT_INDEPENDENT_REAUTHENTICATION", "cognition_assisted_handoff": "DURABLE_EVIDENCE_ONLY__NO_HIDDEN_REASONING_CONTINUITY", "candidate_capability": "VERIFIED__ONE_FRESH_EXPIRED_OPERATIONAL_DENIAL", "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE", "constitutional_continuation_progress": "VERIFIED__LD_PHASE_A_HUMAN_BARRIER_TO_EXPIRED_ACCEPTANCE"},
        "reuse_impact_assessment": {"existing_certified_capabilities_reused": "LC__EX_17_OF_17__KM__KI__JZ__KB__KD__KF__GN__FM__ER__P11__SOLE_ROUTE", "new_capabilities": "ONE_VECTOR_SPECIFIC_FRESH_EXPIRED_OPERATIONAL_ACCEPTANCE_OBSERVATION__NO_NEW_PRODUCTION_CAPABILITY", "existing_capability_became_unreachable": False, "parallel_flow_created": False, "production_path_count_effect": "UNCHANGED__1_TO_1"},
        "architecture": {"production_mutation": 0, "p11_mutation": 0, "new_owner": 0, "new_route": 0, "new_registry": 0, "new_generic_abstraction": 0, "new_constitutional_concept": 0, "parallel_flow": "NO", "production_route": "1_TO_1"},
        "proof_yield": {"authority_spent": 1, "operation_spent": 1, "new_operational_observation_count": 1, "e05_credit": 1, "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "periodic_metrics": {"aigol_codex_work_share": "NOT_MEASURED__NO_GOVERNED_ATTRIBUTION_DENOMINATOR", "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT", "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED", "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR", "full_ccwim": "NOT_MEASURED__NO_GOVERNED_FULL_CCWIM_DENOMINATOR_OR_SCHEMA"},
        "ccwim": {"authenticated_repository_continuation": "VERIFIED", "cross_account_continuation": "SAME_G77_256LD_GENERATION", "predecessor_terminal_authenticated": "VERIFIED", "predecessor_commit_authenticated": "VERIFIED", "predecessor_remote_equality": "VERIFIED", "nested_authority_authenticated": "VERIFIED", "repository_evidence_primary": "VERIFIED", "active_generation_reused": "VERIFIED", "dirty_workspace_reauthenticated": "VERIFIED__LD_ONLY", "previous_session_durable_evidence_reused": "VERIFIED", "current_account_reauthentication": "VERIFIED", "human_decision_boundary_preserved": "VERIFIED", "human_source_authenticated": "VERIFIED", "human_source_byte_count": 1381, "human_source_sha256": SOURCE_SHA256, "authority_bound": "VERIFIED", "authority_consumed": "VERIFIED__ONCE", "operation_performed": "VERIFIED__ONCE", "handoff_ambiguity_count": 0, "binding_owner_ambiguity_count": 0, "authority_state_ambiguity_count": 0, "operational_attempt_ambiguity_count": 0},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED",
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "terminality": {"auto_continuable": False, "human_review_required": True, "second_operation_allowed": False, "successor_generation_created": False, "required_next": "INDEPENDENT_HUMAN_HEAD_TREE_REMOTE_AUTHENTICATION"},
    }


def envelope(inner_name: str, schema: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, inner_name: value, f"{inner_name}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def build_final_seal(reduction_file_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LD_SPCE_FINAL_EXECUTION_SEAL_V1",
        "terminal": TERMINAL,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "result_class": "SUCCESSFUL_ACCEPTANCE_OBSERVATION",
        "human_source_sha256": SOURCE_SHA256,
        "authority_handoff_sha256": AUTHORITY_DIGEST,
        "authority_consumed": 1,
        "operation_attempted": 1,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "e05": {"before": "11_OF_18", "after": "12_OF_18", "credit": 1},
        "terminal_reduction_sha256": reduction_file_sha256,
        "artifacts": dict(sorted(INPUT_HASHES.items())),
        "auto_continuable": False,
        "human_review_required": True,
    }


def materialize() -> None:
    if OUTPUT.exists() or FINAL_SEAL.exists():
        raise RuntimeError("TERMINAL_ARTIFACT_COLLISION")
    reduction = envelope("reduction", "G77_256LD_SPCE_TERMINAL_SUCCESS_REDUCTION_ENVELOPE_V1", build_reduction())
    OUTPUT.write_bytes(canonical_bytes(reduction))
    seal_value = build_final_seal(sha256_path(OUTPUT))
    FINAL_SEAL.write_bytes(canonical_bytes(envelope("seal", "G77_256LD_SPCE_FINAL_EXECUTION_SEAL_ENVELOPE_V1", seal_value)))
    print(TERMINAL)


def verify() -> None:
    expected_reduction = build_reduction()
    if inner(OUTPUT, "reduction") != expected_reduction:
        raise RuntimeError("TERMINAL_REDUCTION_CONTENT_MISMATCH")
    expected_seal = build_final_seal(sha256_path(OUTPUT))
    if inner(FINAL_SEAL, "seal") != expected_seal:
        raise RuntimeError("FINAL_EXECUTION_SEAL_CONTENT_MISMATCH")
    print(TERMINAL)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    arguments = parser.parse_args()
    materialize() if arguments.mode == "materialize" else verify()


if __name__ == "__main__":
    main()
