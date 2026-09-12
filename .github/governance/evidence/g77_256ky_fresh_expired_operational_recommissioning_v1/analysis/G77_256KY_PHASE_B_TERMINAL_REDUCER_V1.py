#!/usr/bin/env python3
"""Authenticate and reduce the completed KY one-shot attempt without replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KY = ROOT / ".github/governance/evidence/g77_256ky_fresh_expired_operational_recommissioning_v1"
RUNTIME = KY / "operation_state/runtime_export"
RECEIPTS = KY / "operation_state/receipts"
OBSERVATION = KY / "G77_256KY_PHASE_B_CONTEXT_BINDING_FAILURE_OBSERVATION_V1.json"
REDUCTION = KY / "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"

HEAD = "d19208af9d9633c764838399e5a86a441e9386ef"
TREE = "40207213a9359f536f9e6380c113c67f5ac6ab3f"
SUBJECT = "G77-256KX bind runtime export custody traversal"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
STABLE_ANCESTRY = "18a00df63b9d82e4f0a7c7873e3159a744c9d3da"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
GENERATION = "G77_256KY_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KY_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
AUTHORITY_DIGEST = "a0abdc283e8414b794d0765c3d074690a4c17bc938af1d34549535c1aa32ea92"
CONTEXT_SHA256 = "cb36b379fc20937e905fe766db044f65e299d46b85d0fbc12af8b5be01ea9d7a"
RECORDED_AT = "2026-09-12T07:12:19Z"
FIRST_FAILURE = (
    "RuntimeError: custody failed submitting act: {'error': 'Human authorization "
    "does not bind the complete sealed context', 'error_type': "
    "'FailClosedRuntimeError', 'message_type': 'CUSTODY_FAILURE'}"
)
TERMINAL = (
    "I__KY_ONE_SHOT_EXPIRED_ATTEMPT_TERMINATED_AT_HUMAN_ACT_CONTEXT_BINDING__"
    "FAIL_CLOSED__NO_E05_CREDIT__NO_RETRY"
)

HUMAN_SOURCE = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KY / "G77_256KY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KY / "G77_256KY_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = KY / "G77_256KY_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KY / "G77_256KY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
ATTEMPT = KY / "G77_256KY_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KY / "G77_256KY_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
PRE_RECEIPT = RECEIPTS / "G77_256KY_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = RECEIPTS / "G77_256KY_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256KY_RAW_EXECUTION_EVIDENCE_V1.jsonl"
TEARDOWN = RUNTIME / "G77_256KY_GUEST_TEARDOWN_SEAL_V1.json"
TERMINAL_MANIFEST = RUNTIME / "G77_256KY_CONTINUATION_MANIFEST_TERMINAL_V1.json"
CONTEXT_PROJECTION = RUNTIME / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
GUEST_ADAPTER = KY / "operation_state/guest_harness/G77_256KY_EXPIRED_VECTOR_ADAPTER_V1.py"
P11_OWNER = ROOT / "tests/p11_da_operational_consumer_v1.py"
EXPIRED_MODEL = ROOT / (
    ".github/governance/evidence/"
    "g77_256jj_expired_vector_deterministic_repository_formalization_v1/"
    "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)

EXPECTED_HASHES = {
    HUMAN_SOURCE: "cca776c3b01cc45d31c572cff16e95d15193bd7318cdcaf3142485cc669c92b4",
    HANDOFF: AUTHORITY_DIGEST,
    BINDING: "f74d14f1cf550df274936de496e5280e4bb26bcf2d9e5a9690adbb0d0a369934",
    PRECONSUMPTION: "962fb3f8d5db3a19574e6d3aed5fd1a6a954d79b5188d5623be871e75ca05cbf",
    CONSUMPTION: "a4c6e2a1c139e7ec61b526a37228f9278aff025e49aec18bbb702277a0e7ca50",
    ATTEMPT: "8dd229d7d91596a8f5f5ec4c6c86e21f2f2566aef79512f308dae93244229d33",
    RESULT: "e78522039a64f11448ac241704e97b1bd2f5772d27a093f3bb7dafbe2708448a",
    PRE_RECEIPT: "9f23b9f78cbc5b2495ea3b0940330677ac9afb5c4714b032a74003e055d257ab",
    POST_RECEIPT: "bc2e0843fc34051e7755546aa41de76b3e227b58abef3b72b3e126e6e48c4063",
    RAW: "7d29d4c97c5ea61bae4206ecdc90fd34eb32f39a0aa69585de7f2916bb5087ea",
    TEARDOWN: "d25e98e6e8a2f69bead870ffdda1a105ce7bd560113730bdcc01af9bdf61db34",
    TERMINAL_MANIFEST: "a0f1cbf5bec61cd75d5be179a5a7df23c8edc671b514589b751ecf053db2ebd3",
    CONTEXT_PROJECTION: "d38691138b7eafb47eb568a98acde90879406abf82244c99507aa768d38aaec7",
    GUEST_ADAPTER: "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7",
    P11_OWNER: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
    EXPIRED_MODEL: "35af335dba0b3e2e2aa7b5ec244ddbc08ff9c8bbc6e7a2e49296a93daecec8d7",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical JSON: {path.name}")
    return value


def verified(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict):
        raise RuntimeError(f"missing sealed object: {path.name}")
    if envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"inner seal mismatch: {path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        key: value,
        f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def persist_exclusive(path: Path, value: dict[str, Any]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def counters() -> dict[str, int]:
    return {
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


def authenticate(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    if (
        git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or remote_head != HEAD
        or git("merge-base", "constitutional-governance-finalize-v1", "HEAD") != STABLE_ANCESTRY
        or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
    ):
        raise RuntimeError("repository checkpoint mismatch")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("branch", "--show-current", cwd=nested)
        or git("status", "--short", cwd=nested)
        or nested_remote_tag != NESTED_HEAD
    ):
        raise RuntimeError("nested authority mismatch")
    for path, expected in EXPECTED_HASHES.items():
        if sha256(path) != expected:
            raise RuntimeError(f"durable evidence identity mismatch: {path.name}")

    source_text = HUMAN_SOURCE.read_text(encoding="utf-8")
    required_source_tokens = (
        GENERATION,
        OPERATION,
        "FM_TO_ER_TO_P11",
        "VERIFIED__11_OF_18",
        "NOT_PROVEN_OPERATIONALLY",
        "NO_REPLAY__NO_REPAIR_RETRY__NO_SECOND_OPERATION",
    )
    if len(HUMAN_SOURCE.read_bytes()) != 1208 or not all(token in source_text for token in required_source_tokens):
        raise RuntimeError("Human source byte or semantic mismatch")

    handoff = verified(HANDOFF, "authorization")
    binding = verified(BINDING, "invocation_binding")
    preconsumption = verified(PRECONSUMPTION, "checkpoint")
    consumption = verified(CONSUMPTION, "checkpoint")
    attempt = verified(ATTEMPT, "attempt")
    result = verified(RESULT, "result")
    pre = load_canonical(PRE_RECEIPT)
    post = load_canonical(POST_RECEIPT)
    teardown = load_canonical(TEARDOWN)
    terminal_manifest = verified(TERMINAL_MANIFEST, "manifest")
    records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    if [record.get("record_sequence") for record in records] != list(range(19)):
        raise RuntimeError("raw evidence sequence mismatch")
    for line, record in zip(RAW.read_bytes().splitlines(), records, strict=True):
        if line != canonical_bytes(record).rstrip(b"\n"):
            raise RuntimeError("raw record canonicalization mismatch")
    failure_records = [record for record in records if record.get("record_type") == "first_failure"]
    act_records = [record for record in records if record.get("record_type") == "human_operational_act_created"]
    if len(failure_records) != 1 or len(act_records) != 1:
        raise RuntimeError("raw lifecycle cardinality mismatch")
    act = act_records[0]["facts"]["human_authority_act"]
    forbidden_later_records = {"operation_request", "expired_denial", "protected_invocation", "protected_effect"}
    commissioning = [record for record in records if str(record.get("record_type", "")).startswith("commissioning_P")]
    if (
        handoff.get("authorization_source_sha256") != EXPECTED_HASHES[HUMAN_SOURCE]
        or handoff.get("authorized_generation_identity") != GENERATION
        or handoff.get("authorized_operation_identity") != OPERATION
        or handoff.get("authorized_repository_head") != HEAD
        or handoff.get("authorized_repository_tree") != TREE
        or handoff.get("authorized_context_sha256") != CONTEXT_SHA256
        or len({AUTHORITY_DIGEST, binding.get("authenticated_canonical_authority_digest"), binding.get("sealed_invocation_authority_digest"), binding.get("final_fm_argv_authority_digest")}) != 1
        or preconsumption.get("final_admission_validation") != "PASS"
        or preconsumption.get("admission_result") != "ADMIT_TO_BOOT_BOUNDARY_ONLY"
        or consumption.get("authority_state_before") != "GRANTED_UNCONSUMED"
        or consumption.get("authority_state_after") != "CONSUMED"
        or consumption.get("operational_counters", {}).get("authority_consumption_count") != 1
        or attempt.get("invocation_count") != 1
        or result.get("invocation_count") != 1
        or result.get("process_exit_status") != 0
        or pre.get("execution_attempt_count") != 1
        or post.get("execution_attempt_count") != 1
        or pre.get("started_unix_ns") != post.get("started_unix_ns")
        or post.get("process_exit_status") != 0
        or post.get("completed_unix_ns", 0) <= post.get("started_unix_ns", 0)
        or len(commissioning) != 12
        or any(record.get("facts", {}).get("result") != "PASS" for record in commissioning)
        or failure_records[0].get("facts", {}).get("first_failure") != FIRST_FAILURE
        or teardown.get("first_failure") != FIRST_FAILURE
        or teardown.get("raw_evidence_sha256") != EXPECTED_HASHES[RAW]
        or teardown.get("raw_record_count") != 19
        or any(record.get("record_type") in forbidden_later_records for record in records)
        or act.get("metadata", {}).get("authorized_context_sha256") is not None
        or terminal_manifest.get("checkpoint_is_authority") is not False
        or terminal_manifest.get("generation_identity") == GENERATION
    ):
        raise RuntimeError("KY authority, attempt, or first-failure mismatch")
    guest = teardown.get("execution_counters", {})
    if (
        guest.get("vm_boot_count") != 1
        or guest.get("vm_creation_count") != 1
        or guest.get("e05_case_execution_count") != 0
        or guest.get("human_operational_act_creation_count") != 1
        or guest.get("human_operational_act_submitted_count") != 0
        or guest.get("human_operational_act_claimed_count") != 0
        or guest.get("human_operational_act_invoked_count") != 0
        or guest.get("p11_entry_count") != 0
        or guest.get("p11_operational_invocation_count") != 0
        or guest.get("repair_and_continue_count") != 0
        or guest.get("execution_replay_count") != 0
    ):
        raise RuntimeError("guest terminal counters mismatch")
    owner_source = P11_OWNER.read_text(encoding="utf-8")
    guard = 'validated_act.metadata.get("authorized_context_sha256")'
    error = '_fail("Human authorization does not bind the complete sealed context")'
    if guard not in owner_source or error not in owner_source:
        raise RuntimeError("P11 complete-context guard mismatch")
    expired_model = verified(EXPIRED_MODEL, "reduction")
    expired_semantics = expired_model.get("p11_owner_semantics", {})
    if (
        expired_model.get("e05", {}).get("before") != "VERIFIED__11_OF_18"
        or expired_model.get("e05", {}).get("frontier_distance") != "VERIFIED__7_UNSATISFIED_OF_18"
        or expired_semantics.get("expired_predicate") != "preclaim_time >= available.binding.valid_until_unix_ns"
        or expired_semantics.get("state_before") != "AVAILABLE"
        or expired_semantics.get("state_after") != "EXPIRED"
        or expired_semantics.get("protected_invocation_after_denial") != 0
        or expired_semantics.get("protected_effect_after_denial") != 0
    ):
        raise RuntimeError("authenticated EXPIRED acceptance model mismatch")
    if stat.S_IMODE(RUNTIME.stat().st_mode) != 0o701 or stat.S_IMODE(CONTEXT_PROJECTION.stat().st_mode) != 0o664:
        raise RuntimeError("post-KX runtime-export presentation mismatch")
    return {
        "handoff_inner_sha256": load_canonical(HANDOFF)["authorization_sha256"],
        "binding_inner_sha256": load_canonical(BINDING)["invocation_binding_sha256"],
        "act_metadata_fields": sorted(act.get("metadata", {})),
        "terminal_manifest_generation_identity": terminal_manifest["generation_identity"],
    }


def build_observation(authenticated: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KY_PHASE_B_CONTEXT_BINDING_FAILURE_OBSERVATION_V1",
        "recorded_at_utc": RECORDED_AT,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "failure_classification": "VERIFIED__GUEST_EXPIRED_ADAPTER_CONTEXT_BINDING_OMISSION_REJECTED_BY_CUSTODY_BEFORE_SUBMIT",
        "failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "first_failure": FIRST_FAILURE,
        "post_kx_context_load": "VERIFIED__YES",
        "commissioning_result": "VERIFIED__P01_TO_P12_PASS",
        "human_operational_act_created_count": 1,
        "human_operational_act_submitted_count": 0,
        "handoff_authorized_context_sha256": CONTEXT_SHA256,
        "guest_act_authorized_context_sha256": "ABSENT",
        "guest_act_metadata_fields": authenticated["act_metadata_fields"],
        "p11_guard": "VALIDATED_ACT_METADATA_AUTHORIZED_CONTEXT_SHA256_MUST_EQUAL_COMMISSIONING_GATE_OPERATION_CONTEXT_SHA256",
        "root_cause": "VERIFIED__LEGACY_FC_DERIVED_EXPIRED_GUEST_ADAPTER_RECREATED_THE_ACT_WITHOUT_PROPAGATING_AUTHORIZED_CONTEXT_SHA256",
        "request_presented": False,
        "temporal_state_evaluated": False,
        "expired_denial_observed": False,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "raw_evidence_sha256": EXPECTED_HASHES[RAW],
        "raw_record_count": 19,
        "teardown_sha256": EXPECTED_HASHES[TEARDOWN],
        "pre_receipt_sha256": EXPECTED_HASHES[PRE_RECEIPT],
        "post_receipt_sha256": EXPECTED_HASHES[POST_RECEIPT],
        "terminal_manifest_limitation": "INHERITED_NONAUTHORITY_MANIFEST_RETAINS_FM_GENERATION_IDENTITY_AND_STALE_E05_OBSERVATION__NOT_USED_AS_KY_TERMINAL_AUTHORITY",
        "terminal_manifest_generation_identity": authenticated["terminal_manifest_generation_identity"],
        "evidence_origin": "NEWLY_RECONSTRUCTED_REPORTING_FROM_EXISTING_IMMUTABLE_RAW_OPERATIONAL_EVIDENCE",
    }


def build_reduction(authenticated: dict[str, Any], observation_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_V1",
        "terminal": TERMINAL,
        "recorded_at_utc": RECORDED_AT,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry": {
            "head": HEAD,
            "tree": TREE,
            "subject": SUBJECT,
            "branch": BRANCH,
            "origin": ORIGIN,
            "remote_head": HEAD,
            "remote_equality": "VERIFIED",
            "stable_ancestry": "VERIFIED",
            "index_state": "EMPTY",
            "tracked_diff": "EMPTY",
            "nested_head": NESTED_HEAD,
            "nested_tree": NESTED_TREE,
            "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL",
        },
        "proof_separation": {
            "repository_proof": "VERIFIED__HEAD_TREE_BRANCH_REMOTE_STABLE_ANCESTRY_AND_NESTED_AUTHORITY",
            "human_authority_proof": "VERIFIED__EXACT_DIRECT_HUMAN_UTF8_SOURCE_BYTES",
            "handoff_proof": "VERIFIED__CANONICAL_FM_OWNER_SERIALIZATION",
            "preconsumption_binding_proof": "VERIFIED__JZ_THREE_WAY_AUTHORITY_DIGEST_EQUALITY",
            "authority_consumption_proof": "VERIFIED__CONSUMED_EXACTLY_ONCE_AFTER_FINAL_ADMISSION",
            "operational_proof": "VERIFIED__ONE_COMPLETED_QEMU_VM_ATTEMPT_AND_RAW_GUEST_EVIDENCE",
            "e05_acceptance_proof": "NOT_PROVEN__NO_EXPIRED_REQUEST_OR_DENIAL",
            "post_operation_reporting_reduction": "NEWLY_RECONSTRUCTED__NO_OPERATIONAL_OBSERVATION_CREATED",
        },
        "authority": {
            "human_source_authenticated": "VERIFIED__YES",
            "handoff_authenticated": "VERIFIED__YES",
            "preconsumption_binding_authenticated": "VERIFIED__YES",
            "fm_admission_authenticated": "VERIFIED__PASS__ADMIT_TO_BOOT_BOUNDARY_ONLY",
            "authority_digest": AUTHORITY_DIGEST,
            "authority_state_before_operation": "GRANTED_UNCONSUMED",
            "authority_state_after_operation": "CONSUMED__NONREUSABLE__NONTRANSFERABLE",
            "consumption_count": 1,
            "handoff_inner_sha256": authenticated["handoff_inner_sha256"],
            "binding_inner_sha256": authenticated["binding_inner_sha256"],
        },
        "operation": {
            "process_exit_status": 0,
            "route": "FM_TO_ER_TO_P11",
            "context_load_after_kx": "VERIFIED__YES",
            "request_act_created": "VERIFIED__YES",
            "request_act_submitted": "VERIFIED__NO",
            "request_actually_presented": "VERIFIED__NO",
            "request_vector": "EXPIRED__SELECTED_AND_ACT_CREATED__NOT_PRESENTED_TO_P11_PRECLAIM",
            "request_temporal_state": "NOT_EVALUATED_OPERATIONALLY",
            "expired_decision": "NOT_OBSERVED",
            "expired_denial": "NOT_PROVEN_OPERATIONALLY",
            "denial_location": "NOT_APPLICABLE__FAILURE_BEFORE_SUBMIT_AND_PRECLAIM",
            "p11_entry": "VERIFIED__NO",
            "protected_invocation": "VERIFIED__NO",
            "protected_effect": "VERIFIED__NO",
        },
        "operational_counters": counters(),
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
            "frontier_after": "VERIFIED__7_UNSATISFIED_OF_18",
            "ky_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "acceptance_requirement": "AVAILABLE_TO_EXPIRED_AT_GOVERNED_PRECLAIM_COORDINATE_BEFORE_P11_OPERATIONAL_ENTRY_WITH_ZERO_PROTECTED_INVOCATION_AND_EFFECT",
        },
        "frontier": {
            "pre_operation_last_verified_edge": "KX_REPOSITORY_RUNTIME_EXPORT_CUSTODY_TRAVERSAL_BINDING",
            "post_operation_last_verified_edge": "POST_KX_CONTEXT_LOAD__P01_TO_P12__HUMAN_ACT_CREATION",
            "pre_operation_first_unverified_edge": "POST_KX_CONTEXT_LOAD_THEN_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
            "post_operation_first_unverified_edge": "CONTEXT_BOUND_ACT_SUBMISSION_THEN_EXPIRED_PRECLAIM_DENIAL_BEFORE_P11_ENTRY",
            "constitutional_frontier_movement": "VERIFIED__MOVED_PAST_RUNTIME_EXPORT_CONTEXT_LOAD_TO_ACT_SUBMISSION_BINDING",
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
            "last_verified_operational_edge": "ONE_AUTHORITY_CONSUMPTION_ONE_FM_QEMU_VM_ATTEMPT_CONTEXT_LOAD_P01_TO_P12_AND_ACT_CREATION",
            "last_verified_edge": "P11_CUSTODY_FAIL_CLOSED_ON_MISSING_COMPLETE_CONTEXT_BINDING",
            "first_broken_edge": "EXPIRED_GUEST_ADAPTER_DID_NOT_PROPAGATE_AUTHORIZED_CONTEXT_SHA256_INTO_CANONICAL_HUMAN_ACT_METADATA",
            "first_unverified_operational_edge": "CONTEXT_BOUND_ACT_SUBMISSION_AND_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_PRODUCTION_CAPABILITY__BOUNDED_EXISTING_EXPIRED_ADAPTER_CONTEXT_BINDING_CONFORMANCE_REQUIRED",
            "minimum_missing_proof": "REPOSITORY_PROOF_THAT_THE_EXISTING_EXPIRED_ADAPTER_PRESERVES_HANDOFF_CONTEXT_BINDING_THEN_A_SEPARATE_FUTURE_FRESH_OPERATIONAL_OBSERVATION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_EXISTING_EXPIRED_ADAPTER_CONTEXT_BINDING_REPAIR__NO_KY_RETRY_REPLAY_REPAIR_OR_OPERATION",
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": "VERIFIED__NEWLY_OBSERVED_EXPIRED_ADAPTER_BINDING_OMISSION__NOT_A_NEW_CONSTITUTIONAL_FAILURE_CLASS",
            "affected_invariant": "EVERY_OPERATIONAL_HUMAN_ACT_MUST_BIND_THE_COMPLETE_SEALED_OPERATION_CONTEXT",
            "previous_closest_edge": "JM_COMPLETE_SEALED_CONTEXT_BINDING_GUARD_AND_JH_CONTEXT_BOUND_OPERATIONAL_PRECEDENT",
            "semantic_difference": "HOST_HANDOFF_BINDS_CONTEXT_BUT_LEGACY_FC_DERIVED_GUEST_ADAPTER_RECREATES_ACT_WITHOUT_AUTHORIZED_CONTEXT_SHA256",
            "production_behavior_impact": "VERIFIED__NONE__P11_FAILS_CLOSED_BEFORE_SUBMIT_ENTRY_INVOCATION_OR_EFFECT",
            "new_capability_required": "VERIFIED__NO__EXISTING_CONTEXT_BINDING_MECHANISM_ALREADY_EXISTS",
            "new_proof_required": "VERIFIED__ADAPTER_PROPAGATION_CONFORMANCE_AND_LATER_DISTINCT_FRESH_OPERATIONAL_PROOF",
            "convergence_signal": "VERIFIED__FRONTIER_MOVED_PAST_KX_RUNTIME_EXPORT_TRAVERSAL",
            "repetition_pressure": "VERIFIED__HIGH__EXPIRED_REMAINS_11_OF_18_AFTER_THE_CONSUMED_KY_ATTEMPT",
            "verification_amplification_risk": "ESTIMATED__HIGH_IF_ANOTHER_OPERATION_PRECEDES_STATIC_END_TO_END_CONTEXT_BINDING_VALIDATION",
            "classification_evidence": "VERIFIED__HANDOFF_CONTEXT_DIGEST__RAW_ACT_METADATA__P11_GUARD__EXACT_CUSTODY_FAILURE",
            "classification_confidence": "VERIFIED__HIGH",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE",
            "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_PRECONSUMPTION_BINDING_TO_ONE_SHOT_CONSUMPTION",
            "reuse_invariant": "COMMON_PROOF_REUSE_DOES_NOT_TRANSFER_VECTOR_AUTHORITY_OPERATIONAL_PROOF_OR_E05_CREDIT",
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "vector_specific_residue": "EXPIRED_ADAPTER_CONTEXT_BINDING_AND_EXPIRED_PRECLAIM_DENIAL",
            "reuse_preconditions": "FRESH_GENERATION_VECTOR_HEAD_TREE_CONTEXT_AND_DIRECT_HUMAN_SOURCE",
            "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR",
            "expected_future_proof_reduction": "ESTIMATED__COMMON_LIFECYCLE_REUSED__NO_VECTOR_OPERATIONAL_PROOF_TRANSFER",
            "common_proof_reuse_is_vector_operational_proof": False,
            "common_e05_infrastructure_is_vector_e05_credit": False,
            "multi_vector_reuse_is_authority_transfer": False,
        },
        "evidence_provenance": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "existing_raw_operational_evidence": [EXPECTED_HASHES[PRE_RECEIPT], EXPECTED_HASHES[POST_RECEIPT], EXPECTED_HASHES[RAW], EXPECTED_HASHES[TEARDOWN]],
            "newly_reconstructed_reporting_artifacts": ["G77_256KY_PHASE_B_CONTEXT_BINDING_FAILURE_OBSERVATION_V1.json", "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json", "G77_256KY_G48_IMPLEMENTATION_REPORT_V1.md"],
            "observation_file_sha256": observation_sha256,
        },
        "architecture": {
            "production_mutation_count": 0,
            "p11_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "parallel_flow": "NO",
            "production_route": "1_TO_1",
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "EX_17_OF_17__JP_JO_GD_DU_FM_GN_JZ_GL_ER_P11_HUMAN_SERIALIZATION_ONE_SHOT_GUARDS",
            "new_capabilities": "VERIFIED__0__FAILURE_LOCALIZATION_AND_REPORTING_ONLY",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "governance_reporting": {
            "project_state": "VERIFIED__KY_TERMINAL_FAIL_CLOSED_BEFORE_OPERATION_REQUEST",
            "project_progress": "VERIFIED__KX_CONTEXT_LOAD_OPERATIONALLY_CONFIRMED_AND_NEXT_BINDING_EDGE_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATIONAL_PROOF_REMAINS_OPEN_AFTER_ONE_ADDITIONAL_EDGE_LOCALIZATION",
            "constitutional_health_evidence": "VERIFIED__P11_FAIL_CLOSED__ONE_CONSUMPTION__ONE_ATTEMPT__ZERO_RETRY__ZERO_PROTECTED_EFFECT",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficiency": "ESTIMATED__MEDIUM__ONE_SHOT_LOCALIZED_A_PRE_REQUEST_HARNESS_DEFECT_WITH_REPLAY_SAFE_EVIDENCE",
            "overengineering_risk": "ESTIMATED__HIGH_IF_EQUIVALENT_OPERATIONAL_PROOF_IS_REPEATED_BEFORE_STATIC_BINDING_REPAIR",
            "cognition_provenance": "VERIFIED__REPOSITORY_AND_SEALED_OPERATIONAL_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__PREVIOUS_WORKER_CLAIMS_USED_ONLY_AS_INSPECTION_HINTS",
            "candidate_capability": "NOT_PROVEN__EXPIRED_DENIAL",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ONE_SHOT_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__CROSS_ACCOUNT_RECOVERY_TO_TERMINAL_KY_REDUCTION",
        },
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_ATTRIBUTION_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_BASELINE_OR_DENOMINATOR",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
        },
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "cross_account_recovery": "VERIFIED",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_ambiguity_count": "VERIFIED__0",
            "binding_owner_ambiguity_count": "VERIFIED__0",
            "authority_state_ambiguity_count": "VERIFIED__0",
            "operational_attempt_ambiguity_count": "VERIFIED__0",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED",
        "proof_yield": {
            "new_verified_operational_capability_count": 0,
            "new_operational_context_load_observation_count": 1,
            "new_harness_edge_localized_count": 1,
            "new_e05_credit_count": 0,
            "ex_proof_reuse_count": 17,
        },
        "reporting_defects": [
            "PHASE_A_G48_REPORT_WAS_STALE_AFTER_PHASE_B_AND_IS_REPLACED_BY_TERMINAL_REPORT",
            "GUEST_TERMINAL_NONAUTHORITY_MANIFEST_RETAINS_INHERITED_FM_GENERATION_AND_STALE_E05_OBSERVATION",
        ],
        "terminality": {
            "auto_continuable": False,
            "human_review_required": True,
            "authority_consumed_exactly_once": True,
            "operation_attempted_exactly_once": True,
            "ky_retry_allowed": False,
            "ky_repair_retry_allowed": False,
            "ky_replay_allowed": False,
            "ky_second_attempt_allowed": False,
            "ky_authority_transfer_allowed": False,
            "terminal_stop": "ACTIVE",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    authenticated = authenticate(arguments.remote_head, arguments.nested_remote_tag)
    observation = seal(
        "G77_256KY_PHASE_B_CONTEXT_BINDING_FAILURE_OBSERVATION_ENVELOPE_V1",
        "observation",
        build_observation(authenticated),
    )
    reduction = seal(
        "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1",
        "reduction",
        build_reduction(authenticated, hashlib.sha256(canonical_bytes(observation)).hexdigest()),
    )
    if arguments.write:
        if OBSERVATION.exists() or REDUCTION.exists():
            raise RuntimeError("terminal artifact collision")
        persist_exclusive(OBSERVATION, observation)
        try:
            persist_exclusive(REDUCTION, reduction)
        except Exception:
            OBSERVATION.unlink()
            raise
    else:
        if load_canonical(OBSERVATION) != observation or load_canonical(REDUCTION) != reduction:
            raise RuntimeError("persisted terminal reduction mismatch")
    print(TERMINAL)


if __name__ == "__main__":
    main()
