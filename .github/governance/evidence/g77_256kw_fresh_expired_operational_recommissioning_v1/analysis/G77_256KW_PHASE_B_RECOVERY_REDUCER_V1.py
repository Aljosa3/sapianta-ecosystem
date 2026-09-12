#!/usr/bin/env python3
"""Authenticate and reduce the completed KW one-shot operation without replay."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
KW = ROOT / ".github/governance/evidence/g77_256kw_fresh_expired_operational_recommissioning_v1"
RUNTIME = KW / "operation_state/runtime_export"
RECEIPTS = KW / "operation_state/receipts"
OBSERVATION = KW / "G77_256KW_PHASE_B_RUNTIME_EXPORT_CUSTODY_FAILURE_OBSERVATION_V1.json"
REDUCTION = KW / "G77_256KW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
HUMAN_SOURCE = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
KN_SOURCE = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1/G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KW / "G77_256KW_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KW / "G77_256KW_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = KW / "G77_256KW_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = KW / "G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
ATTEMPT = KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = KW / "G77_256KW_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
PRE_RECEIPT = RECEIPTS / "G77_256KW_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = RECEIPTS / "G77_256KW_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW = RUNTIME / "G77_256KW_RAW_EXECUTION_EVIDENCE_V1.jsonl"
TEARDOWN = RUNTIME / "G77_256KW_GUEST_TEARDOWN_SEAL_V1.json"
TERMINAL_MANIFEST = RUNTIME / "G77_256KW_CONTINUATION_MANIFEST_TERMINAL_V1.json"
CONTEXT_PROJECTION = RUNTIME / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
FM = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"

HEAD = "681538ccd9b6faaeebff15d96881134eaef00d7e"
TREE = "53164b7f60d982727bebd9a5c77d5688ee283ade"
SUBJECT = "G77-256KV localize fresh current-head authority lifecycle"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
GENERATION = "G77_256KW_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KW_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
TERMINAL = "I__KW_PROVIDER_RECOVERY__NEW_RUNTIME_EXPORT_CUSTODY_EDGE_FOUND__CLASSIFIED__FAIL_CLOSED__NO_RETRY"
FIRST_FAILURE = "RuntimeError: custody failed before gate: {'error': \"[Errno 13] Permission denied: '/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'\", 'error_type': 'PermissionError', 'message_type': 'CUSTODY_FAILURE'}"

EXPECTED_HASHES = {
    HUMAN_SOURCE: "692b106107c5959e55a727d19a1bb5cfda783b4ac91a4b6d525c1e6fee6a43bd",
    KN_SOURCE: "56a50ef8a69761e492138d4f9f425eb2e845231bd654a731ead02fcbc34fdc96",
    HANDOFF: "08e4018bd8a8bc8a43e61f0f00c53e94d4a9c6688c83ab1b4caf3cd493319832",
    BINDING: "84dacd84f1d996bb893290310d5435da32e9954f9a811c16c02e4d2601e7be8f",
    PRECONSUMPTION: "febd79b0172b31bc45f6f8f095a8cf58c27106dad3517f7500e738a98705fb32",
    CONSUMPTION: "4017c67a7708fa0fca3194ed8024f7dc2792badb00d6ce1b43f06f210c159c21",
    ATTEMPT: "d915c8459d3a4115e4318b40867dda57898b45b591a1ec4e589c28e195f05dec",
    RESULT: "bee49270878bd88eaf57ea84c7ee2348a6a522ef6be9a70ebd9dd9ba0d1996bf",
    PRE_RECEIPT: "7291dad6e63e964fd23e4304429587a729255fb9a4aceae1e6315075ab2134dc",
    POST_RECEIPT: "2a8267226cf671c211a30a0f3d1b378de0f4c5bda68a50958e89a38e8466517a",
    RAW: "b77198c2a235a7130fedf22cba28a56535afd510a88183d56dddb3e3f8dd7080",
    TEARDOWN: "54eb9d992f0b700ff41c45e3d1f51fa4079f6ba5570e559233126adb25f882a3",
    TERMINAL_MANIFEST: "75d23e8c681db39664e1c44371f8682926cf0d0e2a02303e0cdb5bb1d43bc93e",
    FM: "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical JSON: {path.name}")
    return value


def verified(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(key)
    if not isinstance(value, dict) or envelope.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise RuntimeError(f"seal mismatch: {path.name}")
    return value


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_id": schema, key: value, f"{key}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest()}


def persist(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"terminal artifact collision: {path.name}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())


def operational_counters() -> dict[str, int]:
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
        or git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("log", "-1", "--format=%s") != SUBJECT
        or remote_head != HEAD
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
            raise RuntimeError(f"operational identity mismatch: {path.name}")

    handoff = verified(HANDOFF, "authorization")
    binding = verified(BINDING, "invocation_binding")
    preconsumption = verified(PRECONSUMPTION, "checkpoint")
    consumption = verified(CONSUMPTION, "checkpoint")
    attempt = verified(ATTEMPT, "attempt")
    result = verified(RESULT, "result")
    pre = load_canonical(PRE_RECEIPT)
    post = load_canonical(POST_RECEIPT)
    teardown = load_canonical(TEARDOWN)
    records = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    for record in records:
        if canonical_bytes(record).rstrip(b"\n") != json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"):
            raise RuntimeError("raw record canonicalization mismatch")
    failure_records = [record for record in records if record.get("record_type") == "first_failure"]
    if (
        len(HUMAN_SOURCE.read_bytes()) != 1213
        or len(KN_SOURCE.read_bytes()) != 1213
        or handoff.get("authorization_source_sha256") != EXPECTED_HASHES[HUMAN_SOURCE]
        or handoff.get("authorized_repository_head") != HEAD
        or handoff.get("authorized_repository_tree") != TREE
        or handoff.get("authorized_generation_identity") != GENERATION
        or handoff.get("authorized_operation_identity") != OPERATION
        or len({EXPECTED_HASHES[HANDOFF], binding.get("authenticated_canonical_authority_digest"), binding.get("sealed_invocation_authority_digest"), binding.get("final_fm_argv_authority_digest")}) != 1
        or preconsumption.get("final_admission_validation") != "PASS"
        or consumption.get("authority_state_before") != "GRANTED_UNCONSUMED"
        or consumption.get("authority_state_after") != "CONSUMED"
        or attempt.get("invocation_count") != 1
        or result.get("process_exit_status") != 0
        or pre.get("schema_id") != "SAPIANTA_CONTEXT_BOUND_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1"
        or post.get("schema_id") != "SAPIANTA_CONTEXT_BOUND_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1"
        or len(failure_records) != 1
        or failure_records[0].get("facts", {}).get("first_failure") != FIRST_FAILURE
        or teardown.get("first_failure") != FIRST_FAILURE
        or teardown.get("execution_counters", {}).get("vm_boot_count") != 1
        or teardown.get("execution_counters", {}).get("p11_entry_count") != 0
        or teardown.get("execution_counters", {}).get("p11_operational_invocation_count") != 0
        or teardown.get("execution_counters", {}).get("e05_case_execution_count") != 0
    ):
        raise RuntimeError("KW lifecycle or guest failure mismatch")
    export_mode = stat.S_IMODE(RUNTIME.stat().st_mode)
    context_mode = stat.S_IMODE(CONTEXT_PROJECTION.stat().st_mode)
    if export_mode != 0o700 or context_mode != 0o664:
        raise RuntimeError("runtime export permission provenance mismatch")
    if any(record.get("record_type") in {"operation_request", "expired_denial", "protected_invocation", "protected_effect"} for record in records):
        raise RuntimeError("unexpected later operational edge")
    if len([record for record in records if str(record.get("record_type", "")).startswith("commissioning_P")]) != 12:
        raise RuntimeError("commissioning prefix mismatch")
    return {
        "handoff_inner_sha256": load_canonical(HANDOFF)["authorization_sha256"],
        "binding_inner_sha256": load_canonical(BINDING)["invocation_binding_sha256"],
        "raw_record_count": len(records),
        "runtime_export_mode": f"{export_mode:04o}",
        "context_projection_mode": f"{context_mode:04o}",
    }


def build_observation(authenticated: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KW_PHASE_B_RUNTIME_EXPORT_CUSTODY_FAILURE_OBSERVATION_V1",
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "failure_classification": "VERIFIED__GUEST_CUSTODY_RUNTIME_EXPORT_PERMISSION_DENIAL_AT_SEALED_CONTEXT_LOAD",
        "exact_exception_type": "PermissionError",
        "exact_exception_errno": 13,
        "exact_exception_path": "/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        "first_failure": FIRST_FAILURE,
        "guest_custody_uid": 3,
        "guest_custody_gid": 3,
        "host_runtime_export_uid": RUNTIME.stat().st_uid,
        "host_runtime_export_gid": RUNTIME.stat().st_gid,
        "host_runtime_export_mode": authenticated["runtime_export_mode"],
        "host_context_projection_mode": authenticated["context_projection_mode"],
        "root_cause": "VERIFIED__HOST_RUNTIME_EXPORT_ROOT_MODE_0700_EXCLUDES_GUEST_CUSTODY_UID_3_TRAVERSAL_WHILE_CONTEXT_FILE_IS_READABLE",
        "prior_closest_edge": "KE_GUEST_HARNESS_ROOT_0700_DENIED_CUSTODY_CONTEXT_OWNER_IMPORT_BEFORE_KF_REPAIR",
        "semantic_difference": "KW_PASSES_KF_HARNESS_TRAVERSAL_AND_P01_TO_P12_COMMISSIONING_THEN_FAILS_ON_DISTINCT_G77_EVIDENCE_ROOT_CONTEXT_READ_BEFORE_EXPIRED_REQUEST",
        "raw_evidence_sha256": EXPECTED_HASHES[RAW],
        "raw_record_count": authenticated["raw_record_count"],
        "teardown_sha256": EXPECTED_HASHES[TEARDOWN],
        "serial_sha256": "975e6954d5186b61794b0c8d9f6e38ee08aa3ebb3e12507f9eb927cb07d5a3fc",
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def build_reduction(authenticated: dict[str, Any], observation_file_sha256: str) -> dict[str, Any]:
    states = {
        "human_source_authenticated": "VERIFIED__YES",
        "canonical_authority_handoff_materialized": "VERIFIED__YES",
        "preconsumption_binding_materialized": "VERIFIED__YES",
        "final_fm_admission_performed": "VERIFIED__YES",
        "final_fm_admission_succeeded": "VERIFIED__YES",
        "human_authority_consumed": "VERIFIED__YES",
        "operational_request_created": "VERIFIED__NO",
        "operational_attempt_started": "VERIFIED__YES",
        "fm_invoked_operational_route": "VERIFIED__YES",
        "er_invoked": "VERIFIED__YES",
        "qemu_started": "VERIFIED__YES",
        "vm_started": "VERIFIED__YES",
        "p11_entered": "VERIFIED__NO",
        "expired_denial_observed": "VERIFIED__NO",
        "protected_invocation_occurred": "VERIFIED__NO",
        "protected_effect_occurred": "VERIFIED__NO",
        "terminal_reduction_completed": "VERIFIED__YES",
    }
    return {
        "schema_id": "G77_256KW_SPCE_TERMINAL_FAILURE_REDUCTION_V1",
        "terminal": TERMINAL,
        "recorded_at_utc": now(),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "provider_interruption_recovery": "VERIFIED",
        "provider_interruption_classification": "PROVIDER_INTERRUPTION__NOT_CONSTITUTIONAL_FAILURE__NOT_NEW_GENERATION__NOT_AUTHORITY_TRANSFER",
        "entry": {"head": HEAD, "tree": TREE, "subject": SUBJECT, "branch": BRANCH, "origin": ORIGIN, "remote_head": HEAD, "remote_equality": "VERIFIED", "index_state": "EMPTY", "nested_head": NESTED_HEAD, "nested_tree": NESTED_TREE, "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL"},
        "initial_recovery_branch": "R1",
        "terminal_recovery_branch": "R3",
        "interruption_state_reconstruction": states,
        "authority": {"before": "GRANTED_UNCONSUMED", "transition": "CONSUMED_EXACTLY_ONCE_AFTER_FINAL_FM_ADMISSION", "after": "CONSUMED__NONREUSABLE__NONTRANSFERABLE", "human_source_sha256": EXPECTED_HASHES[HUMAN_SOURCE], "handoff_file_sha256": EXPECTED_HASHES[HANDOFF], "handoff_inner_sha256": authenticated["handoff_inner_sha256"], "consumption_count": 1},
        "canonical_handoff": {"state": "VERIFIED__CANONICAL_FM_OWNER_SERIALIZATION", "file_sha256": EXPECTED_HASHES[HANDOFF], "inner_sha256": authenticated["handoff_inner_sha256"]},
        "preconsumption_binding": {"state": "VERIFIED__JZ_THREE_WAY_DIGEST_EQUALITY", "file_sha256": EXPECTED_HASHES[BINDING], "inner_sha256": authenticated["binding_inner_sha256"]},
        "fm_admission": "VERIFIED__PASS__ADMIT_TO_BOOT_BOUNDARY_ONLY",
        "operation": {"attempt_count": 1, "route": "FM_TO_ER_TO_P11", "exact_operational_edge": "GUEST_CUSTODY_RUNTIME_EXPORT_CONTEXT_LOAD_BEFORE_EXPIRED_OPERATION_REQUEST", "process_exit_status": 0},
        "request_entry_invocation_effect": {"request": "VERIFIED__NO", "entry": "VERIFIED__NO", "invocation": "VERIFIED__NO__PROTECTED_INVOCATION", "effect": "VERIFIED__NO__PROTECTED_EFFECT"},
        "operational_counters": operational_counters(),
        "counter_reconciliation": {"attempt_envelope_operation_request_count": 1, "authenticated_guest_operation_request_count": 0, "resolution": "PROVISIONAL_HOST_ATTEMPT_COUNTER_WAS_EVIDENCE_REPORTING_DEFECT__RAW_GUEST_EVIDENCE_GOVERNS_VECTOR_OPERATION_REQUEST_COUNT__NO_OPERATIONAL_ARTIFACT_REWRITTEN"},
        "e05": {"before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0", "kw_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY"},
        "ex": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "frontier": {"last_verified_operational_edge": "VERIFIED__ONE_AUTHORITY_CONSUMPTION_ONE_FM_QEMU_VM_ATTEMPT_AND_GUEST_COMMISSIONING_P01_TO_P12", "first_unverified_operational_edge": "NOT_PROVEN__EXPIRED_OPERATION_REQUEST_AND_DENIAL_BEFORE_P11_ENTRY", "last_verified_edge": "VERIFIED__GUEST_CUSTODY_RUNTIME_EXPORT_PERMISSION_FAILURE_AUTHENTICATED", "first_broken_edge": "GUEST_CUSTODY_CANNOT_TRAVERSE_RUNTIME_EXPORT_ROOT_TO_READ_SEALED_OPERATION_CONTEXT", "current_real_blocker": "VERIFIED__FM_RUNTIME_EXPORT_PRESENTATION_ROOT_MODE_0700_EXCLUDES_CUSTODY_UID_3", "minimum_missing_capability": "GUEST_CUSTODY_SEARCH_ONLY_TRAVERSAL_OF_EXISTING_RUNTIME_EXPORT_ROOT_AND_READ_ONLY_CONTEXT_LOAD", "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_BINDING_REPAIR__NO_KW_RETRY_REPLAY_OR_OPERATION"},
        "failure_novelty_and_convergence_check": {"failure_class": "NEW_SEMANTIC_EDGE", "novelty": "VERIFIED__DISTINCT_RUNTIME_EXPORT_TRAVERSAL_EDGE_AFTER_KF_HARNESS_TRAVERSAL_REPAIR", "affected_invariant": "GUEST_CUSTODY_MUST_LOAD_THE_SEALED_OPERATION_CONTEXT_BEFORE_GATE_WITHOUT_WRITE_OR_PROVIDER_SUBSTITUTION", "previous_closest_edge": "KE_GUEST_HARNESS_ROOT_0700_CONTEXT_OWNER_IMPORT_DENIAL", "semantic_difference": "KW_PASSES_REPAIRED_HARNESS_IMPORT_AND_P01_TO_P12_BUT_DISTINCT_G77_EVIDENCE_ROOT_0700_BLOCKS_CONTEXT_JSON_READ", "production_behavior_impact": "VERIFIED__SOLE_OPERATIONAL_ROUTE_BLOCKED_BEFORE_EXPIRED_REQUEST__ZERO_PROTECTED_EFFECT", "new_capability_required": "VERIFIED__YES__EXISTING_FM_RUNTIME_EXPORT_PERMISSION_PRESENTATION_BINDING", "new_proof_required": "VERIFIED__REPOSITORY_PERMISSION_CONTRACT_THEN_SEPARATE_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_PROOF", "convergence_signal": "VERIFIED__FRONTIER_MOVED_PAST_KF_HARNESS_TRAVERSAL_AND_ALL_P01_TO_P12_COMMISSIONING", "repetition_pressure": "VERIFIED__HIGH__EXPIRED_REMAINS_11_OF_18_AFTER_MULTIPLE_CONSUMED_GENERATIONS", "verification_amplification_risk": "ESTIMATED__HIGH_IF_PERMISSION_ROOTS_ARE_REPAIRED_ONE_AT_A_TIME_WITHOUT_COMPLETE_TRAVERSAL_CONTRACT", "classification_evidence": "VERIFIED__RAW_GUEST_FAILURE__MODES__KE_KF_COMPARISON__FM_MATERIALIZER_SOURCE", "classification_confidence": "VERIFIED__HIGH", "acceptance_requirement_forcing_continuation": "VERIFIED__NO_WITHIN_KW__AUTHORITY_CONSUMED_AND_ATTEMPT_COMPLETE"},
        "cross_vector_reuse_assessment": {"cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE", "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN", "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION", "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"], "vector_specific_residue": "EXPIRED_OPERATIONAL_REQUEST_DENIAL_AND_RUNTIME_EXPORT_CUSTODY_TRAVERSAL", "reuse_preconditions": "EXACT_GENERATION_BINDINGS_AND_FRESH_HUMAN_SOURCE", "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR", "expected_future_proof_reduction": "ESTIMATED__COMMON_AUTHORITY_LIFECYCLE_REUSED__NO_VECTOR_CREDIT_TRANSFER", "authority_transfer": "VERIFIED__NO", "e05_credit_transfer": "VERIFIED__NO"},
        "architecture": {"production_mutation_count": 0, "p11_implementation_mutation_count": 0, "new_owner_count": 0, "new_route_count": 0, "new_registry_count": 0, "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0, "production_route_before": 1, "production_route_after": 1, "parallel_flow": "NO"},
        "governance_reporting": {"project_state": "VERIFIED__KW_SINGLE_ATTEMPT_TERMINATED_AT_NEW_PRE_REQUEST_CUSTODY_EDGE", "project_progress": "VERIFIED__KF_HARNESS_EDGE_PASSED_AND_RUNTIME_EXPORT_EDGE_LOCALIZED", "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR", "informal_project_progress_estimate": "ESTIMATED__ONE_ADDITIONAL_PRE_REQUEST_EDGE_LOCALIZED__E05_UNCHANGED", "constitutional_health_evidence": "VERIFIED__ONE_CONSUMPTION_ONE_ATTEMPT_ZERO_RETRY_ZERO_PROTECTED_EFFECT", "shadow_automation_status": "VERIFIED__ABSENT", "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR", "governance_efficience": "ESTIMATED__MEDIUM__ONE_SHOT_EDGE_LOCALIZED_WITH_REPLAY_SAFE_EVIDENCE", "overengineering_risk": "ESTIMATED__HIGH_IF_NEXT_REPAIR_DOES_NOT_MODEL_COMPLETE_GUEST_PATH_TRAVERSAL", "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_RECEIPT_RAW_GUEST_AND_TEARDOWN_EVIDENCE_PRIMARY", "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_PROVIDER_RECOVERY_FROM_DURABLE_EVIDENCE", "candidate_capability": "NOT_PROVEN__EXPIRED_DENIAL", "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE", "constitutional_continuation_progress": "VERIFIED__KW_PHASE_A_TO_CONSUMED_SINGLE_ATTEMPT_TO_NEW_EDGE_REDUCTION"},
        "proof_yield": {"new_verified_operational_capability_count": 0, "new_semantic_edge_localized_count": 1, "e05_credit": 0, "proof_reuse_count": 17},
        "ccwim": {"ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION", "authenticated_repository_continuation": "VERIFIED__YES", "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO", "handoff_reconstruction_success": "VERIFIED__YES", "handoff_ambiguity_count": "VERIFIED__0", "observed_artifact_level_cross_worker_drift": "VERIFIED__0", "cross_account_recovery": "VERIFIED", "provider_interruption_recovery": "VERIFIED"},
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "reuse_impact_assessment": {"existing_certified_capabilities_reused": "EX_17_OF_17__JP__JO__GD__DU__FM__GN__JZ__GL__ER__P11__HUMAN_SERIALIZATION__ONE_SHOT_GUARDS", "new_capabilities": "VERIFIED__0__NEW_SEMANTIC_BLOCKER_ONLY", "existing_capability_became_unreachable": False, "parallel_flow_created": False, "production_path_count_effect": "UNCHANGED__1_TO_1"},
        "observation_file_sha256": observation_file_sha256,
        "terminality": {"auto_continuable": False, "human_review_required": True, "kw_retry_allowed": False, "kw_repair_retry_allowed": False, "kw_replay_allowed": False, "kw_second_attempt_allowed": False, "kw_authority_transfer_allowed": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    arguments = parser.parse_args()
    authenticated = authenticate(arguments.remote_head, arguments.nested_remote_tag)
    observation = seal("G77_256KW_PHASE_B_RUNTIME_EXPORT_CUSTODY_FAILURE_OBSERVATION_ENVELOPE_V1", "observation", build_observation(authenticated))
    if OBSERVATION.exists():
        existing = load_canonical(OBSERVATION)
        if existing.get("observation", {}).get("first_failure") != FIRST_FAILURE:
            raise RuntimeError("existing observation mismatch")
    else:
        persist(OBSERVATION, observation)
    reduction = seal("G77_256KW_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1", "reduction", build_reduction(authenticated, sha256(OBSERVATION)))
    persist(REDUCTION, reduction)
    print(TERMINAL)


if __name__ == "__main__":
    main()
