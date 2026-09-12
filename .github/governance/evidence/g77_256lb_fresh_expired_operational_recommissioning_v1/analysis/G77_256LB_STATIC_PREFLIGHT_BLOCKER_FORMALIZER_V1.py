#!/usr/bin/env python3
"""Formalize the LB authority-free cloud-init adapter-digest blocker."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LB = ROOT / ".github/governance/evidence/g77_256lb_fresh_expired_operational_recommissioning_v1"
ENTRY_HEAD = "f185e8fcb773f8f93fc0f8763bcb984f0de90e6d"
ENTRY_TREE = "e4ed372a6a009ce0a4a223339ebb90cc3a32d95e"
ENTRY_SUBJECT = "G77-256LA align EXPIRED input authorization reference"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
LA_REDUCTION = ROOT / ".github/governance/evidence/g77_256la_expired_input_authorization_reference_alignment_v1/G77_256LA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KZ_REDUCTION = ROOT / ".github/governance/evidence/g77_256kz_expired_adapter_complete_context_binding_v1/G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JX_REDUCTION = ROOT / ".github/governance/evidence/g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/G77_256JX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JR = ROOT / ".github/governance/evidence/g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
FM = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
CLOUD = ROOT / ".github/governance/evidence/g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/static/G77_256JX_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = ROOT / ".github/governance/evidence/g77_256jx_er_admission_runtime_checkout_role_separation_repair_v1/static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V3.img"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
LA_REDUCTION_SHA256 = "c3918d26b73e72e5378e0970de9d2c133b56fb1d51638214752dbafbe774c699"
KZ_REDUCTION_SHA256 = "c1ecb63dbdbf5bab8637f570e4e0aa61be3132d4aac3031eda2b857b735c1c15"
JX_REDUCTION_SHA256 = "db9309de5e3940d7547d887c869f080057cb96ca93200e77f73431d091731a59"
JR_SHA256 = "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344"
FM_SHA256 = "4931b5777750448c4608d7a40736b2b67f061f6191b86da5c0309e189ec52bb4"
CLOUD_SHA256 = "d427ea791a6a34412af12f6fb4b8f6d6597db120d037bd13e99c9cb64f52f859"
SEED_SHA256 = "dda34ab8566eb3b3111783dc6d3a112ce88515ed6caf8f40469d0600c0e87fa4"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
PRESENTED_ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
KZ_ADAPTER_SHA256 = "4160ba7c21ecfbcb22731f7d3fba07161c8cfb2b66900069537779059201ba37"
TERMINAL = "A__LB_STATIC_CLOUD_INIT_ADAPTER_DIGEST_BINDING_BLOCKER_LOCALIZED__REPOSITORY_ONLY__NO_HUMAN_AUTHORITY__NO_OPERATION"
REDUCTION = LB / "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"


class LBFormalizationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed(path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT
    )


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value):
        raise LBFormalizationError(f"NONCANONICAL_JSON:{path}")
    return value


def authenticate_dependency(path: Path, expected: str) -> None:
    raw = path.read_bytes()
    if raw != committed(path) or sha256_bytes(raw) != expected:
        raise LBFormalizationError(f"COMMITTED_DEPENDENCY_MISMATCH:{path}")


def cloud_command() -> list[str]:
    commands = [
        line.strip()
        for line in CLOUD.read_text(encoding="utf-8").splitlines()
        if "/usr/bin/python3 /mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py" in line
    ]
    if len(commands) != 1:
        raise LBFormalizationError("CLOUD_BOOTSTRAP_COMMAND_AMBIGUOUS")
    return shlex.split(commands[0])


def authenticate_la() -> dict[str, Any]:
    authenticate_dependency(LA_REDUCTION, LA_REDUCTION_SHA256)
    envelope = load_canonical(LA_REDUCTION)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise LBFormalizationError("LA_REDUCTION_SEAL_MISMATCH")
    if (
        reduction.get("terminal") != "A__LA_EXPIRED_INPUT_AUTHORIZATION_REFERENCE_REPOSITORY_CONFORMANCE_VERIFIED__STATIC_PREOPERATIONAL_CHAIN_READY__NO_OPERATION__NO_E05_CREDIT"
        or reduction.get("static_readiness", {}).get("static_pre_operational_chain_complete") != "VERIFIED"
        or reduction.get("e05", {}).get("state") != "VERIFIED__11_OF_18"
    ):
        raise LBFormalizationError("LA_TERMINAL_CONTRACT_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "file_sha256": LA_REDUCTION_SHA256,
        "claimed_static_readiness": "VERIFIED",
        "e05_state": "VERIFIED__11_OF_18",
        "proof_scope": "CONTEXT_AND_INPUT_AUTHORIZATION_REFERENCE_TRAVERSAL_TO_P11_TEMPORAL_EVALUATION_BOUNDARY__NOT_A_UNIVERSAL_FUTURE_GENERATED_ASSET_CURRENCY_CLAIM",
        "proof_invalidated": "VERIFIED__NO",
    }


def authenticate_predecessor_trace() -> dict[str, Any]:
    authenticate_dependency(KZ_REDUCTION, KZ_REDUCTION_SHA256)
    authenticate_dependency(JX_REDUCTION, JX_REDUCTION_SHA256)
    kz = load_canonical(KZ_REDUCTION)["reduction"]
    jx = load_canonical(JX_REDUCTION)["reduction"]
    if (
        kz.get("artifact_hashes", {}).get("jr_adapter_after") != KZ_ADAPTER_SHA256
        or kz.get("artifact_hashes", {}).get("jr_adapter_before") != PRESENTED_ADAPTER_SHA256
        or jx.get("implementation", {}).get("adapter_after_sha256") != PRESENTED_ADAPTER_SHA256
        or jx.get("implementation", {}).get("cloud_sha256") != CLOUD_SHA256
        or jx.get("implementation", {}).get("seed_sha256") != SEED_SHA256
    ):
        raise LBFormalizationError("PREDECESSOR_DIGEST_LINEAGE_MISMATCH")
    return {
        "jx_adapter_cloud_init_seed_digest": PRESENTED_ADAPTER_SHA256,
        "kz_adapter_digest_after_context_binding_repair": KZ_ADAPTER_SHA256,
        "la_adapter_digest_after_reference_alignment": JR_SHA256,
        "first_stale_transition": "KZ_CHANGED_JR_ADAPTER_FROM_JX_DIGEST_WITHOUT_REISSUING_JX_CLOUD_INIT_OR_NOCLOUD_SEED",
        "la_effect": "LA_CHANGED_JR_ADAPTER_AGAIN_AND_ALIGNED_FM_ADMISSION_PIN__JX_GENERATED_BOOTSTRAP_PROJECTION_REMAINED_OUTSIDE_LA_BOUNDED_TRAVERSAL",
    }


def authenticate_static_mismatch() -> dict[str, Any]:
    for path, expected in ((JR, JR_SHA256), (FM, FM_SHA256), (CLOUD, CLOUD_SHA256), (SEED, SEED_SHA256), (P11, P11_SHA256)):
        authenticate_dependency(path, expected)
    command = cloud_command()
    if len(command) != 7 or command[2] != PRESENTED_ADAPTER_SHA256:
        raise LBFormalizationError("CLOUD_COMMAND_CONTRACT_MISMATCH")
    projected = subprocess.check_output(
        ["isoinfo", "-i", str(SEED), "-R", "-x", "/user-data"],
        stderr=subprocess.DEVNULL,
    )
    if projected != CLOUD.read_bytes():
        raise LBFormalizationError("NOCLOUD_USER_DATA_PROJECTION_MISMATCH")
    fm_text = FM.read_text(encoding="utf-8")
    if f'EXPIRED_ADMISSION_ADAPTER_SHA256 = (\n    "{JR_SHA256}"' not in fm_text:
        raise LBFormalizationError("FM_CURRENT_ADAPTER_PIN_MISMATCH")
    if PRESENTED_ADAPTER_SHA256 == JR_SHA256:
        raise LBFormalizationError("EXPECTED_STATIC_MISMATCH_ABSENT")
    return {
        "source_bytes_owner": JR.relative_to(ROOT).as_posix(),
        "source_sha256": JR_SHA256,
        "canonical_digest_owner": "JR_EXPIRED_ADMISSION_ADAPTER_CURRENT_COMMITTED_BYTES",
        "expected_launcher_adapter_digest": JR_SHA256,
        "expected_digest_owner": "FM_EXPIRED_ADMISSION_ADAPTER_SHA256",
        "presented_cloud_init_adapter_digest": PRESENTED_ADAPTER_SHA256,
        "presented_digest_owner": "JX_CLOUD_INIT_BOOTSTRAP_COMMAND_ARGUMENT_1",
        "launcher_contract_owner": "FM_PROVE_GUEST_ADAPTER_BINDING",
        "cloud_init_or_nocloud_projection_owner": "JX_EXPIRED_CLOUD_INIT_SOURCE_AND_JX_EXPIRED_NOCLOUD_SEED_V3_USER_DATA",
        "jx_binding_owner": "G77_256JX_ER_ADMISSION_RUNTIME_CHECKOUT_ROLE_SEPARATION_REPAIR_V1",
        "first_component_with_current_digest": "JR_EXPIRED_VECTOR_ADAPTER_CURRENT_COMMITTED_BYTES",
        "last_component_with_current_digest": "FM_EXPIRED_ADMISSION_ADAPTER_SHA256_AND_CONTEXT_GUEST_ADAPTER_BINDING_SOURCE_SHA256",
        "first_component_with_stale_digest": "JX_CLOUD_INIT_PRE_REQUEST_ARGUMENT_1",
        "stale_binding_transformation": "KZ_AND_LA_CHANGED_THE_JR_ADAPTER_BYTES_AND_FM_ADMISSION_PIN_WHILE_THE_EXISTING_JX_GENERATED_CLOUD_INIT_AND_SEED_PROJECTION_RETAINED_THE_JX_DIGEST",
        "generated_projection": CLOUD.relative_to(ROOT).as_posix(),
        "sealed_or_hashed_artifact": SEED.relative_to(ROOT).as_posix(),
        "current_projected_adapter_sha256": JR_SHA256,
        "fm_expected_adapter_sha256": JR_SHA256,
        "cloud_init_presented_adapter_sha256": PRESENTED_ADAPTER_SHA256,
        "nocloud_user_data_equals_cloud_init": "VERIFIED",
        "mismatch": "VERIFIED__CURRENT_PROJECTED_ADAPTER_DIGEST_DIFFERS_FROM_CLOUD_INIT_PRE_REQUEST_DIGEST",
        "fail_closed_surface": "FM_AUTHORITY_FREE_STATIC_READINESS__CLOUD_INIT_PRE_REQUEST_ARGUMENT_BINDING",
        "fail_closed_validator": "FM.PROVE_GUEST_ADAPTER_BINDING.BOOTSTRAP_GUEST_COMMAND_ARGUMENTS_EQUALS_COMMAND_BINDINGS",
        "failure_point": "AUTHORITY_FREE_STATIC_READINESS_AFTER_VISIBILITY_AND_CHECKOUT_PREFLIGHT__BEFORE_AUTHORITY_HANDOFF_PROOF_COMPLETION__BEFORE_ANY_QEMU_CALL",
        "observed_exception": "RuntimeError: cloud-init pre-request argument binding mismatch",
    }


def build_reduction() -> dict[str, Any]:
    la = authenticate_la()
    lineage = authenticate_predecessor_trace()
    mismatch = authenticate_static_mismatch()
    return {
        "schema_id": "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256LB",
        "generation_identity": "G77_256LB_STATIC_CLOUD_INIT_ADAPTER_DIGEST_BINDING_BLOCKER_V1",
        "commissioned_identity_family": "G77_256LB_FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING_V1",
        "operation_identity": "NOT_ALLOCATED_IN_DURABLE_LB_EVIDENCE",
        "generation_phase": "PHASE_A_AUTHORITY_FREE_STATIC_PREFLIGHT__TERMINAL_BLOCKER_REDUCTION",
        "collision_status": "VERIFIED__NO_SECOND_LB_DIRECTORY_OR_COMMITTED_LB_IDENTITY",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "terminal": TERMINAL,
        "entry": {
            "branch": BRANCH,
            "head": ENTRY_HEAD,
            "tree": ENTRY_TREE,
            "subject": ENTRY_SUBJECT,
            "remote_equality": "VERIFIED",
            "nested_head": NESTED_HEAD,
            "nested_tree": NESTED_TREE,
            "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL",
        },
        "la_terminal_authentication": la,
        "digest_lineage": lineage,
        "static_blocker": mismatch,
        "classification": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": "VERIFIED__NEWLY_EXPOSED_POST_LA_BOOTSTRAP_DIGEST_STALENESS__NOT_A_NEW_CONSTITUTIONAL_CAPABILITY_CLASS",
            "affected_invariant": "CLOUD_INIT_PRE_REQUEST_ADAPTER_DIGEST_MUST_EQUAL_THE_CURRENT_PROJECTED_EXPIRED_ADAPTER_DIGEST",
            "previous_closest_edge": "LA_STATIC_CONTEXT_AND_INPUT_AUTHORIZATION_REFERENCE_CONFORMANCE",
            "semantic_difference": "LA_UPDATED_THE_JR_ADAPTER_AND_FM_ADMISSION_PIN_BUT_THE_BOUND_JX_CLOUD_INIT_AND_NOCLOUD_SEED_STILL_PRESENT_THE_PRE_KZ_ADAPTER_DIGEST",
            "production_behavior_impact": "VERIFIED__FAIL_CLOSED_DURING_AUTHORITY_FREE_STATIC_READINESS_BEFORE_HUMAN_AUTHORITY_OR_OPERATION",
            "new_capability_required": "VERIFIED__NO__EXISTING_BOOTSTRAP_BINDING_AND_NOCLOUD_PROJECTION_MECHANISM",
            "new_proof_required": "REPOSITORY_ONLY_CURRENT_ADAPTER_DIGEST_TO_CLOUD_INIT_TO_NOCLOUD_SEED_EXACT_PROJECTION_AND_FULL_AUTHORITY_FREE_STATIC_READINESS",
            "convergence_signal": "VERIFIED__KY_TO_KZ_TO_LA_DATA_PATH_EDGES_CLOSED__LB_EXPOSES_THE_NEXT_BOOTSTRAP_IDENTITY_EDGE",
            "repetition_pressure": "VERIFIED__OPERATION_MUST_NOT_BE_REPEATED_WHILE_STATIC_PREFLIGHT_FAILS",
            "verification_amplification_risk": "ESTIMATED__LOW_AFTER_STATIC_LOCALIZATION__HIGH_IF_BYPASSED_OR_REPROVED_OPERATIONALLY",
            "overengineering_risk": "ESTIMATED__HIGH_IF_DISCOVERY_REPAIR_AND_OPERATION_ARE_COMBINED_IN_LB",
            "classification_evidence": "COMMITTED_JX_KZ_LA_DIGEST_LINEAGE__CURRENT_JR_AND_FM_BYTES__EXACT_JX_CLOUD_INIT_COMMAND__BYTE_EQUAL_NOCLOUD_USER_DATA__FM_FAIL_CLOSED_VALIDATOR",
            "classification_confidence": "VERIFIED__HIGH__EXACT_DIGEST_COMPARISON_AND_DETERMINISTIC_FAIL_CLOSED_EXCEPTION",
        },
        "convergence": {
            "authenticated_sequence": ["G77-256KY", "G77-256KZ", "G77-256LA", "G77-256LB"],
            "authenticated_explanation": "C__EXISTING_JX_PROJECTION_BECAME_STALE_AT_KZ_AND_WAS_NOT_EXERCISED_BY_THE_BOUNDED_KZ_OR_LA_STATIC_TRAVERSALS",
            "pre_lb_last_verified_edge": "LA_CONTEXT_AND_INPUT_AUTHORIZATION_REFERENCE_CONFORMANCE_TO_P11_TEMPORAL_EVALUATION_BOUNDARY",
            "post_lb_last_verified_edge": "CURRENT_JR_ADAPTER_AND_FM_ADMISSION_DIGEST_EQUALITY_PLUS_JX_SEED_SOURCE_PROJECTION_IDENTITY",
            "pre_lb_first_unverified_edge": "FRESH_EXPIRED_OPERATIONAL_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY",
            "post_lb_first_broken_edge": "FM_BOOTSTRAP_EXPECTED_CURRENT_JR_ADAPTER_DIGEST_EQUALS_JX_CLOUD_INIT_PRE_REQUEST_ARGUMENT_DIGEST",
            "constitutional_frontier_movement": "VERIFIED__NEXT_STATIC_BOOTSTRAP_IDENTITY_EDGE_LOCALIZED_WITHOUT_OPERATION__NO_NEW_CAPABILITY",
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
            "la_proof_invalidated": "VERIFIED__NO__LA_BOUNDED_TRAVERSAL_SCOPE_RETAINED",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "COMMON_FM_BOOTSTRAP_DIGEST_AND_NOCLOUD_PROJECTION_PATTERN",
            "reusable_component": "EXISTING_CLOUD_INIT_PRE_REQUEST_DIGEST_BINDING_AND_SEED_SOURCE_PROJECTION_CHECK",
            "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "shared_owner_or_vector_specific": "SHARED_FM_VALIDATION_MECHANISM__VECTOR_SPECIFIC_GENERATED_BOOTSTRAP_ASSETS",
            "shared_generated_projection": "VERIFIED__PATTERN_SHARED__BYTES_AND_SEEDS_VECTOR_SPECIFIC",
            "shared_binding_rule": "BOOTSTRAP_ARGUMENT_ADAPTER_DIGEST_MUST_EQUAL_CURRENT_CONTEXT_BOUND_ADAPTER_SOURCE_DIGEST",
            "shared_defect": "VERIFIED__NO__ONLY_EXPIRED_JX_PROJECTION_PROVEN_STALE",
            "shared_required_delta": "VERIFIED__NO__ONLY_EXPIRED_REISSUE_IS_SUPPORTED",
            "affected_vectors": ["EXPIRED"],
            "unaffected_vectors": ["FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
            "vector_specific_residue": "EXPIRED_JR_ADAPTER_DIGEST_AND_EXPIRED_NOCLOUD_SEED",
            "reuse_preconditions": "VECTOR_LOCAL_ADAPTER_DIGEST_AND_EXACT_SEED_SOURCE_PROJECTION",
            "revalidation_required": "VERIFIED__PER_VECTOR_AND_PER_GENERATION",
            "expected_future_proof_reduction": "ESTIMATED__REUSE_THE_STATIC_BINDING_CHECK__NO_OPERATIONAL_OR_E05_CREDIT_TRANSFER",
            "authority_transfer": "VERIFIED__NO",
            "operational_proof_transfer": "VERIFIED__NO",
            "e05_credit_transfer": "VERIFIED__NO",
        },
        "minimum_next": {
            "minimum_missing_capability": "NO_NEW_CAPABILITY__CURRENT_EXPIRED_BOOTSTRAP_DIGEST_PROJECTION_IS_MISSING",
            "minimum_missing_proof": "CURRENT_JR_DIGEST_TO_CLOUD_INIT_TO_NOCLOUD_SEED_EXACT_PROJECTION__FM_AUTHORITY_FREE_STATIC_READINESS_PASS",
            "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_GENERATION__ALIGN_EXISTING_EXPIRED_CLOUD_INIT_PRE_REQUEST_DIGEST_TO_CURRENT_JR_ADAPTER__REGENERATE_EXACT_NOCLOUD_SEED__REBIND_EXISTING_FM_EXPIRED_SEED_IDENTITY__NO_NEW_ROUTE__THEN_REPEAT_PHASE_A_STATIC_READINESS",
            "human_authority_before_repair": "FORBIDDEN",
            "operation_before_repair": "FORBIDDEN",
            "repair_and_operational_proof_same_authority_lifecycle": "FORBIDDEN",
        },
        "frontier": {
            "last_verified_edge": "LA_CONTEXT_AND_AUTHORIZATION_REFERENCE_CONFORMANCE_PLUS_CURRENT_FM_AND_JR_DIGEST_AUTHENTICATION",
            "first_broken_edge": "EXPIRED_CLOUD_INIT_PRE_REQUEST_ADAPTER_DIGEST_EQUALS_CURRENT_PROJECTED_ADAPTER_DIGEST",
            "first_unverified_operational_edge": "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY__DEFERRED_BEHIND_STATIC_BLOCKER",
            "constitutional_frontier_movement": "VERIFIED__STATIC_BOOTSTRAP_IDENTITY_EDGE_LOCALIZED_WITHOUT_OPERATION",
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
            "static_pre_operational_chain_complete": "NOT_PROVEN__BLOCKED_AT_EXPIRED_BOOTSTRAP_ADAPTER_DIGEST_PROJECTION",
            "fresh_operational_attempt_readiness": "NOT_READY",
            "readiness_blocker": "FM_EXPECTS_DF87_CURRENT_JR_DIGEST_WHILE_JX_CLOUD_INIT_AND_NOCLOUD_SEED_PRESENT_F24D_JX_DIGEST",
            "next_static_edge": "CURRENT_JR_ADAPTER_DIGEST_TO_JX_CLOUD_INIT_ARGUMENT_TO_REISSUED_NOCLOUD_SEED_TO_FM_STATIC_VALIDATOR",
        },
        "architecture": {
            "production_mutation": 0,
            "p11_mutation": 0,
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "parallel_flow": "NO",
            "production_route": "1_TO_1",
        },
        "operational_counters": {
            "human_authority_count": 0,
            "authority_consumption_count": 0,
            "operation_request_count": 0,
            "operation_attempt_count": 0,
            "qemu_start_count": 0,
            "vm_start_count": 0,
            "p11_entry_count": 0,
            "protected_invocation_count": 0,
            "protected_effect_count": 0,
            "retry_count": 0,
            "repair_retry_count": 0,
            "replay_count": 0,
        },
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_status": "NOT_PROVEN_OPERATIONALLY",
            "current_generation_credit": "VERIFIED__0",
        },
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "proof_separation": {
            "repository_static_blocker_proof": "VERIFIED",
            "human_authority": "NOT_CREATED",
            "operational_proof": "NOT_PERFORMED",
            "e05_acceptance_proof": "NOT_CREATED",
        },
        "lifecycle_decision": {
            "continuation_type": "CROSS_ACCOUNT_SAME_GENERATION",
            "previous_session_termination_cause": "EXTERNAL_CODEX_USAGE_LIMIT",
            "active_generation_committed_at_entry": False,
            "active_generation_terminal_at_entry": False,
            "selected_scope": "A__LB_DISCOVERY_AND_STATIC_PREFLIGHT_BLOCKER_TERMINALIZATION_ONLY",
            "repair_in_lb": "FORBIDDEN__ONE_EDGE_ONE_GENERATION_AND_SEALED_ASSET_CASCADE_DEFERRED",
            "human_authority_created": False,
            "authority_consumed": False,
            "qemu_or_vm_operation": False,
            "partial_artifact_disposition": {
                "static_preflight_blocker_formalizer": "COMPLETE",
                "phase_a_success_artifacts": "REMOVE_AS_INCOMPLETE__ALREADY_ABSENT_AT_CROSS_ACCOUNT_ENTRY",
                "candidate_continuation_manifest": "REMOVE_AS_INCOMPLETE__ALREADY_ABSENT_AT_CROSS_ACCOUNT_ENTRY",
                "historical_inputs": "DO_NOT_TOUCH",
            },
        },
        "proof_yield": {
            "result": "NEW_STATIC_PREFLIGHT_EDGE_LOCALIZED__ZERO_AUTHORITY_CONSUMED__ZERO_OPERATION_SPENT",
            "next_delta_narrowing": "VERIFIED__EXACT_JX_CLOUD_INIT_AND_NOCLOUD_SEED_REISSUE_CHAIN_LOCALIZED",
            "new_operational_proof": "VERIFIED__0",
            "new_e05_credit": "VERIFIED__0",
        },
        "metrics": {
            "project_state": "VERIFIED__LB_REPOSITORY_ONLY_STATIC_PREFLIGHT_BLOCKER_TERMINAL",
            "informal_project_progress_estimate": "ESTIMATED__LA_STATIC_SEMANTIC_CHAIN_RETAINED__EXPIRED_BOOTSTRAP_PROJECTION_REPAIR_REMAINS",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_BEFORE_AUTHORITY_OR_OPERATION__EXACT_STALE_PROJECTION_LOCALIZED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficiency": "ESTIMATED__HIGH__STATIC_DISCOVERY_SPENT_ZERO_AUTHORITY_AND_ZERO_OPERATION",
            "overengineering_risk": "ESTIMATED__LOW_FOR_LB_TERMINALIZATION__HIGH_IF_REPAIR_OR_OPERATION_IS_ADDED",
            "cognition_provenance": "DURABLE_REPOSITORY_EVIDENCE__HUMAN_PROVIDED_CROSS_ACCOUNT_HANDOFF__CURRENT_ACCOUNT_REAUTHENTICATION",
            "cognition_assisted_handoff": "VERIFIED__DURABLE_FACTS_INDEPENDENTLY_REAUTHENTICATED__NO_HIDDEN_REASONING_CLAIM",
            "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_READINESS_BLOCKED_STATICALLY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_VECTOR_LOCAL_BOOTSTRAP_ASSETS",
            "constitutional_continuation_progress": "VERIFIED__LA_TO_LB_NEXT_STATIC_EDGE_LOCALIZED__NO_E05_MOVEMENT",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED",
        },
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "cross_account_continuation": "VERIFIED__SAME_GENERATION",
            "predecessor_commit_authenticated": "VERIFIED__YES",
            "predecessor_remote_equality": "VERIFIED__YES",
            "active_generation_reused": "VERIFIED__YES",
            "previous_session_durable_evidence_reused": "VERIFIED__YES",
            "current_account_reauthentication": "VERIFIED__YES",
            "repository_evidence_primary": "VERIFIED__YES",
            "human_decision_boundary_preserved": "VERIFIED__YES",
            "handoff_ambiguity_count": 0,
            "binding_owner_ambiguity_count": 0,
            "authority_state_ambiguity_count": 0,
            "operational_attempt_ambiguity_count": 0,
        },
        "periodic_metrics": {
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR",
            "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
        },
        "validation": {
            "lb_focused": "VERIFIED__8_PASSED",
            "digest_recomputation_and_nocloud_projection": "VERIFIED__PASS",
            "la_kz_relevant_regression": "VERIFIED__18_PASSED__6_HISTORICAL_STATE_BOUND_TESTS_DESELECTED",
            "historical_state_bound_limitation": "VISIBLE__FULL_LA_KZ_RUN_HAS_6_EXPECTED_CURRENT_STATE_FAILURES_FROM_ORIGINAL_DIRTY_DIFF_PRE_LA_HASHES_OR_PRE_LA_FAILURE_EDGE",
            "canonical_json_and_inner_seal": "VERIFIED__PASS",
            "python_ast_and_compile": "VERIFIED__PASS",
            "g48_h1_count": 6,
            "g48_reuse_question_count": 5,
            "governance_conformance": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "bounded_mutation_audit": "VERIFIED__LB_EVIDENCE_ONLY",
            "git_diff_check": "VERIFIED__PASS",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256LB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    REDUCTION.write_bytes(canonical_bytes(envelope))


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    def git(*args: str, nested: bool = False) -> str:
        command = ["git"] + (["-C", "sapianta_system"] if nested else []) + list(args)
        return subprocess.check_output(command, cwd=ROOT, text=True).strip()
    if (
        git("branch", "--show-current") != BRANCH
        or git("rev-parse", "HEAD") != ENTRY_HEAD
        or git("rev-parse", "HEAD^{tree}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", "HEAD") != ENTRY_SUBJECT
        or remote_head != ENTRY_HEAD
        or git("diff", "--name-only")
        or git("diff", "--cached", "--name-only")
        or nested_remote_tag != NESTED_HEAD
        or git("rev-parse", "HEAD", nested=True) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", nested=True) != NESTED_TREE
        or git("status", "--porcelain", nested=True)
        or git("branch", "--show-current", nested=True)
    ):
        raise LBFormalizationError("ENTRY_OR_NESTED_AUTHORITY_MISMATCH")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    if any(not value.startswith(LB.relative_to(ROOT).as_posix() + "/") for value in untracked):
        raise LBFormalizationError("UNBOUNDED_MUTATION_SCOPE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    args = parser.parse_args()
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    write_reduction()
    print(TERMINAL)
