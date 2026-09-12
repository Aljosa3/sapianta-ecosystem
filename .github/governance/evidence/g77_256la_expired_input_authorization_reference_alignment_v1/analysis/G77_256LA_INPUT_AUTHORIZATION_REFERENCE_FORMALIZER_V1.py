#!/usr/bin/env python3
"""Build the repository-only LA authorization-reference reduction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
LA = ROOT / (
    ".github/governance/evidence/"
    "g77_256la_expired_input_authorization_reference_alignment_v1"
)
JR = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
)
FC = ROOT / (
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
ER = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FM = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
KZ_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256kz_expired_adapter_complete_context_binding_v1/"
    "G77_256KZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
FORMALIZER = LA / "analysis/G77_256LA_INPUT_AUTHORIZATION_REFERENCE_FORMALIZER_V1.py"
TESTS = LA / "tests/test_g77_256la_input_authorization_reference_v1.py"
REDUCTION = LA / "G77_256LA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

GENERATION = "G77-256LA"
IDENTITY = "G77_256LA_EXPIRED_INPUT_AUTHORIZATION_REFERENCE_ALIGNMENT_V1"
TERMINAL = (
    "A__LA_EXPIRED_INPUT_AUTHORIZATION_REFERENCE_REPOSITORY_CONFORMANCE_"
    "VERIFIED__STATIC_PREOPERATIONAL_CHAIN_READY__NO_OPERATION__NO_E05_CREDIT"
)
KZ_TERMINAL = (
    "A__KZ_EXPIRED_ADAPTER_COMPLETE_CONTEXT_BINDING_REPOSITORY_CONFORMANCE_"
    "VERIFIED__NO_OPERATION__NO_E05_CREDIT"
)
ENTRY_HEAD = "044a034bab81dd78697690f652f6038a9fdbff49"
ENTRY_TREE = "38b7b12b5e830eb0f63b7264e138308811825af7"
ENTRY_SUBJECT = "G77-256KZ preserve complete context binding in act construction"
JR_BEFORE = "4160ba7c21ecfbcb22731f7d3fba07161c8cfb2b66900069537779059201ba37"
JR_AFTER = "df87b85f40ab9b6a286c8114c931cedc90f485c0e9992271aef92cbf1549e344"
FM_BEFORE = "a58dd3c14e377de6cc59e4709eae56ba3f1185863da4f953314c3b4baf4e424c"
FM_AFTER = "4931b5777750448c4608d7a40736b2b67f061f6191b86da5c0309e189ec52bb4"
FC_SHA256 = "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sealed(path: Path, key: str) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    value = envelope[key]
    if raw != canonical_bytes(envelope):
        raise RuntimeError(f"NONCANONICAL__{path}")
    if envelope[f"{key}_sha256"] != hashlib.sha256(
        canonical_bytes(value)
    ).hexdigest():
        raise RuntimeError(f"SEAL_INVALID__{path}")
    return value


def load(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"LOAD_FAILED__{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_predecessor() -> dict[str, Any]:
    kz = sealed(KZ_REDUCTION, "reduction")
    if kz["terminal"] != KZ_TERMINAL:
        raise RuntimeError("KZ_TERMINAL_DRIFT")
    if kz["frontier"]["post_kz_first_broken_edge"] != (
        "FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_REMAINS_BOUND_TO_ER_ACT_"
        "IDENTITY_AFTER_FC_ACT_IDENTITY_REPLACEMENT"
    ):
        raise RuntimeError("KZ_FRONTIER_DRIFT")
    return {
        "predecessor_generation": "G77-256KZ",
        "predecessor_terminal": KZ_TERMINAL,
        "predecessor_committed": "VERIFIED",
        "predecessor_pushed": "VERIFIED",
        "predecessor_remote_equal": "VERIFIED",
        "successor_generation": GENERATION,
        "successor_identity": IDENTITY,
        "successor_mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
    }


def authenticate_trace() -> dict[str, Any]:
    if sha256(JR) != JR_AFTER or sha256(FM) != FM_AFTER:
        raise RuntimeError("LA_EXISTING_OWNER_BINDING_DRIFT")
    if sha256(FC) != FC_SHA256 or sha256(P11) != P11_SHA256:
        raise RuntimeError("SHARED_OWNER_OR_P11_CHANGED")
    er = ER.read_text()
    fc = FC.read_text()
    jr = JR.read_text()
    p11 = P11.read_text()
    required = (
        ('"authorization_reference": ACT_ID', er),
        ('"authority_act_identity": ACT_ID', fc),
        ('"authorization_reference": ACT_ID', jr),
        ('input_record["authorization_reference"]', p11),
        ("validated_act.authority_act_identity", p11),
        ('"authorized_context_sha256": gate.operation_context_sha256', jr),
    )
    if not all(token in source for token, source in required):
        raise RuntimeError("AUTHORIZATION_REFERENCE_TRACE_INCOMPLETE")
    return {
        "original_er_act_identity": "G77_256ER_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001",
        "fc_derived_act_identity": "ACT_ID__FC_NAMESPACE_SPECIALIZED_TO_EXPIRED",
        "input_authorization_reference_source": "ER_INPUT_RECORD_ACT_ID",
        "input_authorization_reference_owner": "FC_DERIVED_INPUT_CONSTRUCTION",
        "reference_value_before_fc_transformation": "ER_ACT_ID",
        "reference_value_after_fc_transformation_pre_la": "ER_ACT_ID__STALE",
        "expected_reference_target": "DERIVED_ACT.AUTHORITY_ACT_IDENTITY",
        "act_identity_replacement_owner": "FC_CREATE_INPUT_AND_AUTHORITY",
        "first_component_with_correct_reference": "ER_INPUT_AND_ER_ACT",
        "last_component_with_correct_reference_pre_la": "ER_CREATE_INPUT_AND_AUTHORITY",
        "first_component_with_stale_or_misaligned_reference": "FC_DERIVED_INPUT_RECORD",
        "loss_or_misalignment_transformation": (
            "FC_REPLACES_ACT_IDENTITY_WITHOUT_REBINDING_INPUT_AUTHORIZATION_REFERENCE"
        ),
        "downstream_validator": (
            "P11BOUNDEDCONSUMER._VALIDATE_AUTHORITY_SOURCES_EXACT_EQUALITY"
        ),
        "existing_schema_support": "VERIFIED__REQUIRED_NONEMPTY_INPUT_FIELD",
        "existing_identity_binding_precedent": (
            "VERIFIED__ER_INPUT_REFERENCE_EQUALS_ER_ACT_ID_AND_P11_REQUIRES_EQUALITY"
        ),
        "minimum_repair_owner": (
            "EXISTING_JR_EXPIRED_SPECIALIZATION_AND_EXISTING_FM_EXPIRED_ADMISSION_PIN"
        ),
        "post_la_reference_expression": "ACT_ID",
        "alternate_reference_count": 0,
    }


def build_reduction() -> dict[str, Any]:
    return {
        "schema_id": "G77_256LA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": GENERATION,
        "generation_identity": IDENTITY,
        "terminal": TERMINAL,
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry": {
            "head": ENTRY_HEAD,
            "tree": ENTRY_TREE,
            "subject": ENTRY_SUBJECT,
            "branch": "g77-256fl-wrong-attempt-preboot-blocker",
            "remote_head": ENTRY_HEAD,
            "remote_equality": "VERIFIED",
            "stable_ancestry": "VERIFIED",
            "index_state": "EMPTY",
            "worktree_state": "CLEAN",
            "nested_head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "nested_tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL",
        },
        "lifecycle": authenticate_predecessor(),
        "identity_trace": authenticate_trace(),
        "classification": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": (
                "VERIFIED__NEWLY_EXPOSED_FC_DERIVED_REFERENCE_PRESERVATION_OMISSION__"
                "NOT_A_NEW_CONSTITUTIONAL_FAILURE_CLASS"
            ),
            "affected_invariant": (
                "P11_INPUT_AUTHORIZATION_REFERENCE_MUST_EQUAL_THE_ASSOCIATED_"
                "CANONICAL_HUMAN_ACT_IDENTITY"
            ),
            "previous_closest_edge": (
                "ER_CORRECT_REFERENCE_BINDING_AND_P11_EXACT_REFERENCE_EQUALITY_GUARD"
            ),
            "semantic_difference": (
                "FC_REPLACES_ACT_IDENTITY_BUT_PRESERVES_STALE_ER_INPUT_REFERENCE"
            ),
            "production_behavior_impact": (
                "VERIFIED__FAIL_CLOSED_BEFORE_P11_ENTRY_INVOCATION_OR_EFFECT"
            ),
            "new_capability_required": "VERIFIED__NO__EXISTING_REFERENCE_MECHANISM",
            "new_proof_required": (
                "REFERENCE_ALIGNMENT_CONFORMANCE_AND_BOUNDED_STATIC_CHAIN_READINESS"
            ),
            "convergence_signal": (
                "VERIFIED__KY_TO_KZ_TO_LA_FIRST_BROKEN_EDGE_MOVED_FORWARD"
            ),
            "repetition_pressure": "VERIFIED__REDUCED_BY_STATIC_TRAVERSAL",
            "verification_amplification_risk": (
                "ESTIMATED__LOW__NO_OPERATION_USED_FOR_DISCOVERY"
            ),
            "classification_evidence": (
                "ER_INPUT_AND_ACT__FC_TRANSFORMATION__P11_EQUALITY__KZ_LATER_FAILURE"
            ),
            "classification_confidence": "VERIFIED__HIGH",
        },
        "human_authority_identity_conservation": {
            "provenance": "PRESERVED",
            "act_identity": "PRESERVED_AS_DERIVED_ACT_OWNER_IDENTITY",
            "authorization_reference": "ALIGNED_TO_DERIVED_ACT_IDENTITY",
            "delegation_identity": "UNCHANGED",
            "non_reusability": "PRESERVED",
            "non_transferability": "PRESERVED",
            "complete_context_binding": "PRESERVED_FROM_KZ",
            "authority_conservation": "PRESERVED__NO_NEW_AUTHORITY_OR_SCOPE",
        },
        "cross_vector_reuse_assessment": {
            "cross_vector_reuse_scope": "FC_DERIVED_ACT_AND_INPUT_TRANSFORMATION",
            "reusable_component": FC.relative_to(ROOT).as_posix(),
            "shared_owner_or_vector_specific": (
                "SHARED_FC_TEMPLATE__EXPIRED_FAMILY_LOCAL_REPAIR"
            ),
            "shared_transformation": True,
            "shared_defect": "VERIFIED__TEMPLATE_LEVEL_IF_VECTOR_REACHES_THIS_GUARD",
            "shared_required_delta": (
                "NOT_PROVEN__LA_ACCEPTANCE_SCOPE_IS_EXPIRED_ONLY"
            ),
            "affected_vectors": [
                "EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT",
                "WRONG_INPUT", "WRONG_PROVENANCE",
            ],
            "unaffected_vectors": "ALL_NON_EXPIRED_OWNER_BYTES_UNCHANGED_BY_LA",
            "reuse_invariant": (
                "COMMON_PROOF_REUSE_IS_NOT_VECTOR_OPERATIONAL_PROOF_OR_AUTHORITY_TRANSFER"
            ),
            "vector_specific_residue": "EXPIRED_TEMPORAL_DENIAL_OPERATIONAL_PROOF",
            "reuse_preconditions": "EXISTING_FC_DERIVATION_AND_VECTOR_LOCAL_BINDING",
            "revalidation_required": "VERIFIED__PER_VECTOR_ACCEPTANCE_AND_OPERATION",
            "expected_future_proof_reduction": (
                "ESTIMATED__REFERENCE_TARGET_SEMANTICS_REUSABLE__NO_CREDIT_TRANSFER"
            ),
        },
        "architecture": {
            "p11_mutation": 0,
            "production_mutation": 2,
            "production_files_changed": [
                JR.relative_to(ROOT).as_posix(), FM.relative_to(ROOT).as_posix()
            ],
            "new_owner": 0,
            "new_route": 0,
            "new_registry": 0,
            "new_generic_abstraction": 0,
            "new_constitutional_concept": 0,
            "parallel_flow": "NO",
            "production_route": "1_TO_1",
        },
        "conformance": {
            "act_identity_owner_unambiguous": "VERIFIED",
            "reference_source_and_target_unambiguous": "VERIFIED",
            "derived_reference_exactly_aligned": "VERIFIED",
            "stale_er_identity_absent": "VERIFIED",
            "alternate_reference": "ABSENT",
            "missing_wrong_different_malformed_stale": "VERIFIED__FAIL_CLOSED",
            "correct_reference_guard": "VERIFIED__PASS",
            "kz_context_binding": "VERIFIED__PRESERVED",
            "gate_owned_context_digest": "VERIFIED__EXACT",
            "non_reusable_non_transferable_expired_identity": "VERIFIED__PRESERVED",
            "p11_guard": "UNCHANGED",
            "new_authority_path": "ABSENT",
            "production_route": "ONE_TO_ONE",
        },
        "static_readiness": {
            "static_pre_operational_chain_complete": "VERIFIED",
            "fresh_operational_attempt_readiness": "READY__REPOSITORY_ONLY",
            "readiness_blocker": "NONE_KNOWN_AT_STATIC_TEMPORAL_BOUNDARY",
            "next_static_edge": "NONE_KNOWN",
            "readiness_is_operational_proof": False,
        },
        "frontier": {
            "previous_last_verified_edge": (
                "EXPIRED_ACT_REPOSITORY_CONFORMANCE_TO_COMPLETE_CONTEXT_BINDING"
            ),
            "current_last_verified_edge": (
                "CONTEXT_AND_REFERENCE_BOUND_ACT_PASSES_P11_AUTHORITY_SOURCE_"
                "VALIDATION_TO_TEMPORAL_EVALUATION_BOUNDARY"
            ),
            "previous_first_broken_edge": (
                "FC_DERIVED_INPUT_AUTHORIZATION_REFERENCE_STALE_AFTER_ACT_REPLACEMENT"
            ),
            "current_first_broken_edge": (
                "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_OBSERVATION_NOT_PERFORMED"
            ),
            "first_unverified_operational_edge": (
                "EXPIRED_DENIAL_AT_GOVERNED_PRECLAIM_BEFORE_P11_ENTRY"
            ),
            "constitutional_frontier_movement": (
                "VERIFIED__STATIC_REFERENCE_EDGE_CLOSED_TO_TEMPORAL_BOUNDARY"
            ),
            "e05_frontier_movement": "VERIFIED__NONE__11_OF_18_REMAINS",
        },
        "minimum_next": {
            "minimum_missing_capability": (
                "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY"
            ),
            "minimum_missing_proof": (
                "DISTINCT_FRESH_OPERATIONAL_OBSERVATION_SATISFYING_E05_ACCEPTANCE"
            ),
            "minimum_legal_next_delta": (
                "AFTER_HUMAN_REVIEW__DISTINCT_FRESH_EXPIRED_OPERATIONAL_GENERATION"
            ),
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
            "current_generation_credit": "VERIFIED__0",
            "expired_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "proof_separation": {
            "repository_proof": "VERIFIED",
            "identity_authorization_reference_conformance": "VERIFIED",
            "reused_human_authority_structure": "VERIFIED__NO_NEW_AUTHORITY",
            "kz_complete_context_binding_preservation": "VERIFIED",
            "operational_proof": "NOT_PERFORMED",
            "e05_acceptance_proof": "NOT_CREATED",
        },
        "reuse": {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"},
        "governance": {
            "governance_efficience": "ESTIMATED__HIGH__ONE_STATIC_EDGE_ONE_REPAIR",
            "overengineering_risk": "ESTIMATED__LOW__NO_SHARED_BASE_OR_P11_CHANGE",
            "repetition_pressure": "VERIFIED__LOWERED",
            "verification_amplification_risk": "ESTIMATED__LOW",
            "project_state": "VERIFIED__LA_REPOSITORY_ONLY_TERMINAL",
            "informal_project_progress_estimate": (
                "ESTIMATED__STATIC_EXPIRED_CHAIN_READY_TO_TEMPORAL_BOUNDARY"
            ),
            "constitutional_health_evidence": (
                "VERIFIED__IDENTITY_AND_CONTEXT_CONSERVATION__ZERO_OPERATION"
            ),
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": (
                "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
            ),
            "cognition_provenance": "VERIFIED__KZ_AND_TARGETED_REPOSITORY_EVIDENCE",
            "cognition_assisted_handoff": "VERIFIED__COMMITTED_KZ_REDUCTION_REUSED",
            "candidate_capability": "VERIFIED__STATIC_PREOPERATIONAL_CHAIN_READINESS",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__KZ_TO_LA_EDGE_ADVANCE",
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
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_DEFINITIONS_NOT_LOCATED",
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_TOKEN_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED__PROVIDER_TELEMETRY_EXCLUDED",
            "lcrr": "NOT_MEASURED__NO_FORMAL_COST_DENOMINATOR",
            "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
        },
        "validation": {
            "la_focused": "VERIFIED__12_PASSED",
            "supporting_regressions": (
                "VERIFIED__29_PASSED__1_HISTORICAL_STATE_BOUND_TEST_DESELECTED"
            ),
            "governance_conformance": "VERIFIED__9_PASSED",
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
        "artifact_hashes": {
            "jr_before": JR_BEFORE,
            "jr_after": sha256(JR),
            "fm_before": FM_BEFORE,
            "fm_after": sha256(FM),
            "fc_unchanged": sha256(FC),
            "p11_unchanged": sha256(P11),
            FORMALIZER.relative_to(ROOT).as_posix(): sha256(FORMALIZER),
            TESTS.relative_to(ROOT).as_posix(): sha256(TESTS),
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256LA_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    REDUCTION.write_bytes(canonical_bytes(envelope))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
    else:
        print(json.dumps(build_reduction(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
