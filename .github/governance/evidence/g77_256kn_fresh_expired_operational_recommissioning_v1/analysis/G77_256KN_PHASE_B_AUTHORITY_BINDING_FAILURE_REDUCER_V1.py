#!/usr/bin/env python3
"""Seal or verify the KN fail-closed Human-source authentication edge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KN = ROOT / ".github/governance/evidence/g77_256kn_fresh_expired_operational_recommissioning_v1"
OUTPUT = KN / "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_V1.json"
SOURCE = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"

HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
TREE = "70aa2a12af3d9806e0d6ddc73f7f751292413e52"
SUBJECT = "G77-256KM preserve GN schema for KI preflight binding"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
GENERATION = "G77_256KN_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256KN_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
CANDIDATE = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
HUMAN_DECISION_PRESENTATION = "9b95f4ad710b607b0c8607da4b2b720d5e8bf94929f4f39dc4e121cc5b5f2f12"
TERMINAL = (
    "M__KN_HUMAN_SOURCE_EXACT_BYTES_NOT_INDEPENDENTLY_AUTHENTICATABLE"
    "__NO_AUTHORITY_CONSUMPTION__NO_PHASE_B__NO_OPERATION"
)

PHASE_A_HASHES = {
    "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json":
        "f980e8cd5ac48c97bbc61a0f891f103e8305f14847a59333b39912024609831d",
    "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt":
        "71cc222249ad75b2b420d749c2d4bd66cf0bd2d982f054102384ddb14993e2ac",
    "G77_256KN_HUMAN_DECISION_PRESENTATION_V1.txt": HUMAN_DECISION_PRESENTATION,
    "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json":
        "a178e6621e9d232d48143e353660e6dba8ce524059a8ad69d0c908cd7aa07a5f",
    "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json":
        "5bc8f9a4b2c012cb45460a661aaf5642de222c1fbefc04b74ddb2abd159fc3f0",
}

FORBIDDEN_PHASE_B_ARTIFACTS = (
    "G77_256KN_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
    "G77_256KN_PRECONSUMPTION_INVOCATION_BINDING_V1.json",
    "G77_256KN_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json",
    "G77_256KN_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
    "G77_256KN_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
)


class KNAuthorityBindingError(RuntimeError):
    """Deterministic KN authority-binding failure evidence error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True
    ).strip()


def verify_envelope(path: Path, inner: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or raw != canonical_bytes(envelope):
        raise KNAuthorityBindingError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    expected = envelope.get(f"{inner}_sha256")
    if not isinstance(value, dict) or expected != hashlib.sha256(canonical_bytes(value)).hexdigest():
        raise KNAuthorityBindingError(f"SEAL_MISMATCH:{path.name}")
    return value


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_invocation_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_attempt_count": 0,
        "operation_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def authenticate_input_state() -> None:
    if (
        git("branch", "--show-current") != BRANCH
        or git("remote", "get-url", "origin") != ORIGIN
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("diff", "--name-only") != ""
        or git("diff", "--cached", "--name-only") != ""
    ):
        raise KNAuthorityBindingError("REPOSITORY_IDENTITY_OR_INDEX_DRIFT")
    for relative, expected in PHASE_A_HASHES.items():
        if sha256_path(KN / relative) != expected:
            raise KNAuthorityBindingError(f"KN_PHASE_A_IDENTITY_MISMATCH:{relative}")
    safe_stop = verify_envelope(
        KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json", "checkpoint"
    )
    if (
        safe_stop.get("terminal")
        != "A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
        or set(safe_stop.get("operational_counters", {}).values()) != {0}
    ):
        raise KNAuthorityBindingError("KN_PHASE_A_TERMINAL_OR_COUNTER_DRIFT")
    if SOURCE.exists() or SOURCE.is_symlink():
        raise KNAuthorityBindingError("UNAUTHENTICATED_KN_SOURCE_ARTIFACT_PRESENT")
    for name in FORBIDDEN_PHASE_B_ARTIFACTS:
        path = KN / name
        if path.exists() or path.is_symlink():
            raise KNAuthorityBindingError(f"PHASE_B_ARTIFACT_UNEXPECTEDLY_PRESENT:{name}")


def build_reduction() -> dict[str, Any]:
    counters = zero_counters()
    return {
        "architecture": {
            "new_constitutional_concept_count": 0,
            "new_generic_abstraction_count": 0,
            "new_owner_count": 0,
            "new_registry_count": 0,
            "new_route_count": 0,
            "p11_implementation_mutation_count": 0,
            "parallel_flow": "NO",
            "production_mutation_count": 0,
            "production_route_after": 1,
            "production_route_before": 1,
        },
        "auto_continuable": False,
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "handoff_ambiguity_count": "VERIFIED__0",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
        },
        "coordinates": {
            "candidate_sha256": CANDIDATE,
            "generation_identity": GENERATION,
            "human_decision_presentation_sha256": HUMAN_DECISION_PRESENTATION,
            "operation_identity": OPERATION,
            "phase_a_coordinates": "VERIFIED__UNCHANGED",
        },
        "cross_vector_reuse_assessment": {
            "applicable_vectors": [
                "EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT",
                "WRONG_INPUT", "WRONG_PROVENANCE",
            ],
            "common_proof_reuse_is_vector_operational_proof": False,
            "cross_vector_reuse_scope": "VERIFIED__MULTI_VECTOR_REUSABLE",
            "expected_future_proof_reduction": "ESTIMATED__REUSE_COMMON_SCHEMA_PLACEMENT_PROOF__NO_VECTOR_OPERATIONAL_CREDIT",
            "multi_vector_reuse_is_authority_transfer": False,
            "reusable_component": "GN_EXACT_PREAUTHORIZATION_OWNER_AND_SEALED_CHECKPOINT_EVIDENCE_BINDING_PATTERN",
            "reuse_invariant": "OWNER_OWNED_EXACT_SEMANTIC_OBJECT_MUST_NOT_BE_EXPANDED_BY_EVIDENCE_ONLY_METADATA",
            "reuse_preconditions": "SAME_AUTHENTICATED_GN_OWNER__EXACT_TEN_FIELDS__SEALED_PREFLIGHT__SEALED_READINESS__EXISTING_CHECKPOINT_DIGEST_FIELDS",
            "revalidation_required": "VERIFIED__PER_GENERATION_BINDINGS_AND_PER_VECTOR_OPERATIONAL_REQUIREMENTS",
            "vector_specific_residue": "EACH_VECTOR_PREFLIGHT_SEMANTICS__FRESH_AUTHORITY__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
        },
        "e05": {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "frontier_after": "VERIFIED__7_UNSATISFIED_OF_18",
            "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
            "kn_e05_credit": "VERIFIED__0",
        },
        "entry": {
            "branch": BRANCH,
            "head": HEAD,
            "index_empty": True,
            "origin": ORIGIN,
            "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE",
            "remote_head": HEAD,
            "subject": SUBJECT,
            "tracked_diff_empty": True,
            "tree": TREE,
        },
        "ex": {
            "ex_reconstructed": "VERIFIED__0",
            "ex_reused": "VERIFIED__17_OF_17",
        },
        "failure_novelty_and_convergence_check": {
            "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__AUTHORITY_AUTHENTICATION_FAILED_AND_OPERATION_IS_FORBIDDEN",
            "affected_invariant": "EXACT_HUMAN_SOURCE_BYTES_MUST_BE_AUTHENTICATED_BEFORE_AUTHORITY_BINDING_OR_CONSUMPTION",
            "classification_confidence": "VERIFIED__HIGH",
            "classification_evidence": "VERIFIED__KN_SOURCE_ARTIFACT_ABSENT__CONTINUATION_TRANSCRIPTION_EXPLICITLY_NONAUTHORITATIVE__PHASE_A_SEALS_INTACT",
            "convergence_signal": "VERIFIED__PHASE_A_CONVERGED__FIRST_REMAINING_EDGE_IS_EXACT_HUMAN_SOURCE_AUTHENTICATION",
            "failure_class": "PROOF_GAP",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__INDEPENDENTLY_AUTHENTICATABLE_EXACT_HUMAN_SOURCE_BYTES_BOUND_TO_EXISTING_KN_PRESENTATION",
            "novelty": "VERIFIED__NOT_NEW__EXISTING_AUTHORITY_PROTOCOL_REQUIRES_EXACT_SOURCE_BYTES",
            "previous_closest_edge": "KG_EXACT_HUMAN_ACT_AUTHENTICATED_BEFORE_PRECONSUMPTION_DIGEST_CHECK",
            "production_behavior_impact": "VERIFIED__NONE__STOPPED_BEFORE_PHASE_B",
            "repetition_pressure": "ESTIMATED__HIGH__E05_OPERATIONAL_OBSERVATION_REMAINS_BLOCKED_AT_HUMAN_AUTHORITY_EDGE",
            "semantic_difference": "VERIFIED__KN_HAS_NO_INDEPENDENTLY_AUTHENTICATED_SOURCE_BYTES__KG_REACHED_A_LATER_SOURCE_TO_HANDOFF_DIGEST_EDGE",
            "verification_amplification_risk": "ESTIMATED__HIGH_IF_TRANSCRIPTION_IS_REPACKAGED_OR_PHASE_A_IS_REPEATED_INSTEAD_OF_OBTAINING_AN_AUTHENTICATED_HUMAN_ACT",
        },
        "frontier": {
            "current_real_blocker": "VERIFIED__EXACT_KN_HUMAN_SOURCE_BYTES_NOT_INDEPENDENTLY_AUTHENTICATABLE",
            "first_broken_edge": "EXACT_HUMAN_SOURCE_AUTHENTICATION_FOR_THE_BOUND_KN_DECISION_OBJECT",
            "first_unverified_operational_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR",
            "last_verified_edge": "FRESH_KN_PHASE_A_PRESENTATION_AND_ALL_REQUIRED_PREFLIGHTS_READY_USING_KM_SCHEMA_PRESERVING_BINDING",
            "last_verified_operational_edge": "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD",
            "minimum_legal_next_delta": "SEPARATE_DIRECT_EXPLICIT_HUMAN_ACT_BOUND_TO_THE_EXISTING_KN_PRESENTATION__THEN_REAUTHENTICATE_WITHOUT_REBUILDING_PHASE_A",
            "minimum_missing_capability": "NOT_PROVEN__NO_NEW_REPOSITORY_CAPABILITY_GAP__EXACT_AUTHENTICATED_HUMAN_SOURCE_EVIDENCE_IS_MISSING",
        },
        "governance": {
            "candidate_capability": "NOT_PROVEN__NO_NEW_OPERATIONAL_CAPABILITY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KN_PHASE_A_AND_FAIL_CLOSED_EDGE",
            "cognition_provenance": "VERIFIED__COMMITTED_KM__SEALED_KN_PHASE_A__EXISTING_AUTHORITY_PROTOCOL_PRIMARY",
            "constitutional_continuation_progress": "VERIFIED__KN_AUTHORITY_SOURCE_FAILURE_LOCALIZED_BEFORE_IRREVERSIBLE_ACTION",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED__NO_AUTHORITY_INFERENCE__ALL_COUNTERS_ZERO__ONE_ROUTE",
            "governance_efficiency": "ESTIMATED__HIGH__FIRST_UNPROVEN_AUTHORITY_EDGE_STOPPED_BEFORE_CONSUMPTION",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_A_COMPLETE__EXACT_HUMAN_SOURCE_AUTHENTICATION_REMAINS",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PHASE_A_OR_AUTHORITY_TRANSCRIPTION_IS_RECONSTRUCTED",
            "project_progress": "VERIFIED__AUTHORITY_SOURCE_AUTHENTICATION_EDGE_LOCALIZED_FAIL_CLOSED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "project_state": "VERIFIED__KN_STOPPED_AT_AUTHORITY_BINDING_BEFORE_PHASE_B",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
        },
        "human_authority": {
            "authority_consumption_count": 0,
            "authority_previously_consumed": "VERIFIED__NO",
            "binding": "NOT_APPLICABLE__AUTHENTICATION_FAILED_BEFORE_BINDING",
            "exact_human_source_bytes_authoritative": True,
            "exact_source_artifact_present": False,
            "human_authority_authentication": "NOT_PROVEN__EXACT_HUMAN_SOURCE_BYTES_NOT_INDEPENDENTLY_AVAILABLE",
            "human_authority_present": False,
            "human_source_decision_status": "NOT_PROVEN__ONLY_NONAUTHORITATIVE_TRANSCRIPTION_AVAILABLE",
            "manually_typed_digest_is_authoritative": False,
            "provider_or_session_state_is_authority": False,
            "transcription_accepted_as_authority": False,
        },
        "human_review_required": True,
        "operational_counters": counters,
        "operational_observation": "NOT_APPLICABLE__NO_AUTHENTICATED_AUTHORITY__NO_PHASE_B__NO_OPERATION",
        "phase_a_terminal": "A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION",
        "phase_b_started": False,
        "proof_yield": {
            "new_blocker_localized_count": "VERIFIED__1__AUTHORITY_SOURCE_AUTHENTICATION",
            "new_operational_capability_count": "VERIFIED__0",
            "new_verified_capability_count": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "schema_id": "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_V1",
        "terminal": TERMINAL,
    }


def envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256KN_PHASE_B_AUTHORITY_BINDING_FAIL_CLOSED_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }


def materialize() -> None:
    authenticate_input_state()
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise KNAuthorityBindingError("FAIL_CLOSED_REDUCTION_COLLISION")
    OUTPUT.write_bytes(canonical_bytes(envelope()))
    print(TERMINAL)


def verify() -> None:
    authenticate_input_state()
    observed = verify_envelope(OUTPUT, "reduction")
    if observed != build_reduction():
        raise KNAuthorityBindingError("FAIL_CLOSED_REDUCTION_CONTENT_MISMATCH")
    print(TERMINAL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("materialize", "verify"))
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.mode == "materialize":
        materialize()
    else:
        verify()
