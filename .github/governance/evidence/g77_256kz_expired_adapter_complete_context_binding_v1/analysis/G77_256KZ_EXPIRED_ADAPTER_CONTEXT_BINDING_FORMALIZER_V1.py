#!/usr/bin/env python3
"""Build the repository-only KZ complete-context binding reduction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
KZ = ROOT / (
    ".github/governance/evidence/"
    "g77_256kz_expired_adapter_complete_context_binding_v1"
)
JR_ADAPTER = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
FC_ADAPTER = ROOT / (
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FM_LAUNCHER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
KY_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256ky_fresh_expired_operational_recommissioning_v1/"
    "G77_256KY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
)
FORMALIZER = KZ / "analysis/G77_256KZ_EXPIRED_ADAPTER_CONTEXT_BINDING_FORMALIZER_V1.py"
TESTS = KZ / "tests/test_g77_256kz_expired_adapter_context_binding_v1.py"
REDUCTION = KZ / "G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

GENERATION = "G77-256KZ"
GENERATION_IDENTITY = "G77_256KZ_EXPIRED_ADAPTER_COMPLETE_CONTEXT_BINDING_V1"
TERMINAL = (
    "A__KZ_EXPIRED_ADAPTER_COMPLETE_CONTEXT_BINDING_REPOSITORY_CONFORMANCE_"
    "VERIFIED__NO_OPERATION__NO_E05_CREDIT"
)
ENTRY_HEAD = "4babca95f92d0d2827c08175d8ac4403bb1f76d9"
ENTRY_TREE = "f42f1e89d29140e1ee4c10bec1ce12fec5fce1f7"
ENTRY_SUBJECT = "G77-256KY terminalize expired context binding failure"
JR_BEFORE_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
FC_SHA256 = "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
FM_BEFORE_SHA256 = "76c82e3701abbd14e9003f356ed326c7bc179935198a060910118d8c40d92aa6"
FM_SHA256 = "a58dd3c14e377de6cc59e4709eae56ba3f1185863da4f953314c3b4baf4e424c"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sealed(path: Path, key: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope):
        raise RuntimeError(f"NONCANONICAL_JSON__{path}")
    value = envelope.get(key)
    if not isinstance(value, dict):
        raise RuntimeError(f"MISSING_INNER_OBJECT__{path}__{key}")
    if envelope.get(f"{key}_sha256") != hashlib.sha256(
        canonical_bytes(value)
    ).hexdigest():
        raise RuntimeError(f"INNER_SEAL_INVALID__{path}__{key}")
    return value


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"MODULE_LOAD_FAILED__{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_trace() -> dict[str, Any]:
    if sha256(FC_ADAPTER) != FC_SHA256:
        raise RuntimeError("FC_ADAPTER_CHANGED_OUTSIDE_KZ")
    if sha256(P11) != P11_SHA256:
        raise RuntimeError("P11_CHANGED_OUTSIDE_KZ")
    if sha256(FM_LAUNCHER) != FM_SHA256:
        raise RuntimeError("FM_CHANGED_OUTSIDE_KZ")
    fc = FC_ADAPTER.read_text(encoding="utf-8")
    jr = JR_ADAPTER.read_text(encoding="utf-8")
    fm = FM_LAUNCHER.read_text(encoding="utf-8")
    p11 = P11.read_text(encoding="utf-8")
    required = (
        ('"authorized_context_sha256": context["context_sha256"]', fm),
        (f'"{sha256(JR_ADAPTER)}"', fm),
        ('operation_context_sha256=fresh_operation_context["context_sha256"]', fc),
        ('"authorized_context_sha256": gate.operation_context_sha256', jr),
        ('validated_act.metadata.get("authorized_context_sha256")', p11),
        ('_fail("Human authorization does not bind the complete sealed context")', p11),
    )
    if not all(token in source for token, source in required):
        raise RuntimeError("COMPLETE_CONTEXT_BINDING_TRACE_INCOMPLETE")
    return {
        "source_owner": "EXISTING_FM_SEALED_HANDOFF_AND_CONTEXT_OWNER",
        "source_field": "authorized_context_sha256",
        "first_component_with_field": "FM_CANONICAL_HUMAN_AUTHORIZATION_HANDOFF",
        "last_component_with_field": "P11_COMMISSIONING_GATE_OPERATION_CONTEXT_SHA256",
        "first_component_without_field_pre_kz": "FC_DERIVED_CANONICAL_HUMAN_ACT_METADATA",
        "loss_transformation": "FC_CREATE_INPUT_AND_AUTHORITY_REPLACES_ORIGINAL_ACT_METADATA",
        "act_construction_owner": FC_ADAPTER.relative_to(ROOT).as_posix(),
        "specialization_owner": JR_ADAPTER.relative_to(ROOT).as_posix(),
        "shared_or_vector_specific": "SHARED_TEMPLATE_LOSS__EXPIRED_SPECIFIC_REQUIRED_DELTA",
        "existing_schema_support": "VERIFIED__CANONICAL_METADATA_AND_P11_EQUALITY_GUARD",
        "existing_context_binding_precedent": (
            "VERIFIED__FM_HANDOFF_AND_JM_P11_COMPLETE_CONTEXT_BINDING"
        ),
        "minimum_repair_owner": (
            "EXISTING_JR_EXPIRED_SPECIALIZATION_AND_EXISTING_FM_EXPIRED_"
            "ADMISSION_HASH_BINDING"
        ),
        "post_kz_binding_expression": "gate.operation_context_sha256",
        "independent_substitute_digest_count": 0,
    }


def authenticate_ky_classification() -> dict[str, Any]:
    ky = load_sealed(KY_REDUCTION, "reduction")
    prior = ky["failure_novelty_and_convergence_check"]
    if prior["failure_class"] != "HARNESS_OR_TEST_ARTIFACT":
        raise RuntimeError("KY_CLASSIFICATION_DRIFT")
    return {
        "failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "novelty": prior["novelty"],
        "affected_invariant": prior["affected_invariant"],
        "previous_closest_edge": prior["previous_closest_edge"],
        "semantic_difference": prior["semantic_difference"],
        "production_behavior_impact": prior["production_behavior_impact"],
        "new_capability_required": prior["new_capability_required"],
        "new_proof_required": (
            "VERIFIED__KZ_ADAPTER_PROPAGATION_CONFORMANCE_COMPLETE__A_DISTINCT_"
            "FUTURE_FRESH_OPERATIONAL_PROOF_REMAINS"
        ),
        "convergence_signal": (
            "VERIFIED__STATIC_BINDING_EDGE_CLOSED_WITHOUT_REPEATING_OPERATION"
        ),
        "repetition_pressure": prior["repetition_pressure"],
        "verification_amplification_risk": prior["verification_amplification_risk"],
        "classification_confidence": "VERIFIED__HIGH",
    }


def build_reduction() -> dict[str, Any]:
    trace = authenticate_trace()
    return {
        "schema_id": "G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": GENERATION,
        "generation_identity": GENERATION_IDENTITY,
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "terminal": TERMINAL,
        "entry": {
            "head": ENTRY_HEAD,
            "tree": ENTRY_TREE,
            "subject": ENTRY_SUBJECT,
            "branch": "g77-256fl-wrong-attempt-preboot-blocker",
            "remote_equality": "VERIFIED",
            "index_state": "EMPTY",
            "worktree_state": "CLEAN_BEFORE_KZ",
        },
        "binding_trace": trace,
        "failure_novelty_and_convergence_check": authenticate_ky_classification(),
        "minimum_delta": {
            "minimum_missing_capability": (
                "BOUNDED_EXISTING_FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_ALIGNMENT"
            ),
            "minimum_missing_proof": (
                "REPOSITORY_PROOF_OF_FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_"
                "ALIGNMENT__THEN_DISTINCT_FRESH_OPERATIONAL_OBSERVATION"
            ),
            "minimum_legal_next_delta": (
                "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_FC_DERIVED_INPUT_"
                "AUTHORIZATION_REFERENCE_ALIGNMENT__NO_KZ_OPERATION"
            ),
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "FC_DERIVED_ACT_CONSTRUCTION_TEMPLATE",
            "reusable_component": FC_ADAPTER.relative_to(ROOT).as_posix(),
            "shared_adapter_or_vector_specific": (
                "SHARED_FC_TEMPLATE__FAMILY_LOCAL_EXPIRED_SPECIALIZATION"
            ),
            "affected_vectors": [
                "EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT",
                "WRONG_INPUT", "WRONG_PROVENANCE",
            ],
            "unaffected_vectors": (
                "ALL_NON_EXPIRED_VECTORS_BYTE_UNCHANGED_BY_KZ"
            ),
            "reuse_invariant": (
                "COMMON_PROOF_REUSE_IS_NOT_VECTOR_OPERATIONAL_PROOF_OR_AUTHORITY_TRANSFER"
            ),
            "vector_specific_residue": (
                "EXPIRED_PRECLAIM_DENIAL_REQUIRES_DISTINCT_OPERATIONAL_PROOF"
            ),
            "reuse_preconditions": (
                "AUTHENTICATED_SEALED_CONTEXT_AND_EXISTING_FAMILY_LOCAL_SPECIALIZATION"
            ),
            "revalidation_required": "VERIFIED__PER_VECTOR_OPERATIONAL_PROOF",
            "expected_future_proof_reduction": (
                "ESTIMATED__STATIC_CONTEXT_PROPAGATION_NEED_NOT_BE_REDISCOVERED"
            ),
            "shared_owner_is_shared_defect": False,
            "shared_defect_is_shared_required_delta": False,
        },
        "architecture": {
            "p11_mutation": 0,
            "production_mutation": 2,
            "production_files_changed": [
                JR_ADAPTER.relative_to(ROOT).as_posix(),
                FM_LAUNCHER.relative_to(ROOT).as_posix(),
            ],
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "parallel_flow": "NO",
            "production_route": "1_TO_1",
        },
        "repository_conformance_proof": {
            "upstream_authenticated_digest_exists": "VERIFIED",
            "act_path_receives_exact_gate_digest": "VERIFIED",
            "canonical_act_metadata_contains_field": "VERIFIED",
            "exact_equality_to_sealed_context": "VERIFIED",
            "independent_substitute_digest": "ABSENT",
            "missing_wrong_different_stale_malformed": "VERIFIED__FAIL_CLOSED",
            "correct_binding": (
                "VERIFIED__PASSES_UNCHANGED_CONTEXT_GUARD__NEXT_EXISTING_INPUT_"
                "AUTHORIZATION_REFERENCE_EDGE_LOCALIZED"
            ),
            "non_reusable": "PRESERVED",
            "non_transferable": "PRESERVED",
            "vector_identity": "PRESERVED__EXPIRED",
            "p11_guard": "UNCHANGED",
            "new_authority_path": "ABSENT",
            "alternate_production_route": "ABSENT",
        },
        "frontier": {
            "pre_kz_last_verified_edge": (
                "P11_CUSTODY_FAIL_CLOSED_ON_MISSING_COMPLETE_CONTEXT_BINDING"
            ),
            "post_kz_last_verified_edge": (
                "EXPIRED_ACT_REPOSITORY_CONFORMANCE_TO_COMPLETE_CONTEXT_BINDING"
            ),
            "pre_kz_first_broken_edge": (
                "EXPIRED_ADAPTER_OMITS_AUTHORIZED_CONTEXT_SHA256"
            ),
            "post_kz_first_broken_edge": (
                "FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_REMAINS_BOUND_TO_ER_ACT_"
                "IDENTITY_AFTER_FC_ACT_IDENTITY_REPLACEMENT"
            ),
            "first_unverified_operational_edge": (
                "CONTEXT_BOUND_ACT_WITH_ALIGNED_INPUT_AUTHORIZATION_REFERENCE_THEN_"
                "EXPIRED_DENIAL_BEFORE_P11_ENTRY"
            ),
            "constitutional_frontier_movement": (
                "VERIFIED__REPOSITORY_BINDING_EDGE_CLOSED__OPERATIONAL_EDGE_UNCHANGED"
            ),
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
        },
        "operational_counters": {
            "qemu_start_count": 0,
            "vm_start_count": 0,
            "operation_attempt_count": 0,
            "authority_consumption_count": 0,
            "operational_authorization_count": 0,
            "operation_request_count": 0,
            "p11_entry_count": 0,
            "protected_invocation_count": 0,
            "protected_effect_count": 0,
        },
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "kz_credit": "VERIFIED__0",
            "expired_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "proof_separation": {
            "repository_proof": "VERIFIED",
            "reused_human_authority_structure": "VERIFIED__NO_NEW_AUTHORITY",
            "adapter_owner_conformance_proof": "VERIFIED",
            "unchanged_p11_guard_proof": "VERIFIED",
            "operational_proof": "NOT_PERFORMED",
            "e05_acceptance_proof": "NOT_CREATED",
        },
        "validation": {
            "kz_focused": "VERIFIED__12_PASSED",
            "jm_and_p11_supporting": (
                "VERIFIED__29_PASSED__1_EXPECTED_HISTORICAL_STATE_BOUND_FAILURE__"
                "JM_EXPECTS_P11_DIRTY_DURING_ITS_ORIGINAL_GENERATION"
            ),
            "functional_context_or_p11_regression_failures": 0,
            "governance_conformance_tests": "VERIFIED__9_PASSED",
            "conformance_engine": (
                "VERIFIED__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS"
            ),
            "canonical_json_and_inner_seal": "VERIFIED",
            "python_ast_and_compile": "VERIFIED",
            "g48_h1_count": 6,
            "g48_reuse_question_count": 5,
            "git_diff_check": "VERIFIED__PASS",
            "bounded_mutation_audit": "VERIFIED__TWO_EXISTING_PRODUCTION_FILES",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "governance": {
            "governance_efficience": (
                "ESTIMATED__HIGH__ONE_EXISTING_OWNER_DELTA_AVOIDS_REPEATED_OPERATION"
            ),
            "overengineering_risk": "ESTIMATED__LOW__NO_GENERIC_OR_SHARED_BASE_CHANGE",
            "repetition_pressure": "VERIFIED__REDUCED_BY_STATIC_EDGE_CLOSURE",
            "verification_amplification_risk": (
                "ESTIMATED__LOW_AFTER_FOCUSED_END_TO_END_REPOSITORY_PROOF"
            ),
            "project_state": "VERIFIED__KZ_REPOSITORY_ONLY_TERMINAL",
            "informal_project_progress_estimate": (
                "ESTIMATED__EXPIRED_STATIC_BINDING_READY__OPERATIONAL_PROOF_OPEN"
            ),
            "constitutional_health_evidence": (
                "VERIFIED__UNCHANGED_FAIL_CLOSED_P11__ZERO_AUTHORITY_AND_OPERATION"
            ),
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": (
                "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
            ),
            "cognition_provenance": (
                "VERIFIED__CURRENT_SESSION_AND_AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY"
            ),
            "cognition_assisted_handoff": (
                "VERIFIED__SAME_SESSION_CHECKPOINT_REUSED_WITH_TARGETED_REAUTHENTICATION"
            ),
            "candidate_capability": (
                "VERIFIED__REPOSITORY_CONFORMANT_EXPIRED_CONTEXT_BOUND_ACT_CONSTRUCTION"
            ),
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE",
            "constitutional_continuation_progress": (
                "VERIFIED__KY_FAILURE_LOCALIZATION_TO_KZ_STATIC_REPAIR"
            ),
        },
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "same_session_continuation": "VERIFIED__YES",
            "previous_session_context_reused": "VERIFIED__YES",
            "repository_evidence_primary": "VERIFIED__YES",
            "handoff_ambiguity_count": 0,
            "binding_owner_ambiguity_count": 0,
            "authority_state_ambiguity_count": 0,
            "operational_attempt_ambiguity_count": 0,
        },
        "hac_hai_hae": (
            "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED"
        ),
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
            "prompt_context_reuse_ratio": (
                "NOT_MEASURED__NO_GOVERNED_TOKEN_ATTRIBUTION_INSTRUMENT"
            ),
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_BASELINE_OR_DENOMINATOR",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
        },
        "artifact_hashes": {
            "jr_adapter_after": sha256(JR_ADAPTER),
            "jr_adapter_before": JR_BEFORE_SHA256,
            "fc_unchanged": sha256(FC_ADAPTER),
            "fm_after": sha256(FM_LAUNCHER),
            "fm_before": FM_BEFORE_SHA256,
            "p11_unchanged": sha256(P11),
            FORMALIZER.relative_to(ROOT).as_posix(): sha256(FORMALIZER),
            TESTS.relative_to(ROOT).as_posix(): sha256(TESTS),
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    REDUCTION.write_bytes(canonical_bytes(envelope))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    if arguments.write:
        write_reduction()
    else:
        print(json.dumps(build_reduction(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
