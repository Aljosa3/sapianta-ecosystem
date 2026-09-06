#!/usr/bin/env python3
"""Reduce the IS FUTURE preauthorization blocker without operating."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IS_ROOT = ROOT / ".github/governance/evidence/g77_256is_future_operational_v1"
MATERIALIZER_PATH = IS_ROOT / "orchestration/G77_256IS_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCTION_PATH = IS_ROOT / "G77_256IS_SPCE_TERMINAL_PREAUTHORIZATION_BLOCKER_V1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


IS = load_module(MATERIALIZER_PATH, "g77_256is_blocker_materializer")


def canonical_bytes(value: Any) -> bytes:
    return IS.canonical_bytes(value)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduce(args: argparse.Namespace) -> dict[str, Any]:
    entry = IS.authenticate_entry(args.remote_head, args.nested_remote_tag)
    ir = IS.reconstruct_ir()
    future = IS.authenticate_future_semantics()
    identity = IS.derive_identity()
    candidate = IS_ROOT / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    runtime = IS_ROOT / "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    v2_candidate = IS_ROOT / "live_binding/v2_readiness/candidate/G77_256IS_V2_READINESS_CANDIDATE_V2.json"
    v2_runtime = IS_ROOT / "live_binding/v2_readiness/runtime_projection/G77_256IS_V2_READINESS_CANDIDATE_V2.json"
    eb_path = IS_ROOT / "live_binding/v2_readiness/bindings/G77_256IS_EB_RECEIPT_V2.json"
    ee_path = IS_ROOT / "live_binding/v2_readiness/bindings/G77_256IS_EE_RECEIPT_V2.json"
    context_path = IS_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = IS.FM.fresh_context.load_context(context_path, repository_root=ROOT)
    if candidate.read_bytes() != runtime.read_bytes() or sha256_path(candidate) != IS.FUTURE_CANDIDATE_SHA:
        raise RuntimeError("IF candidate/runtime identity mismatch")
    if v2_candidate.read_bytes() != v2_runtime.read_bytes():
        raise RuntimeError("V2 readiness candidate/runtime mismatch")
    if set(IS.DU.validate_file(v2_candidate, ROOT, expected_head=IS.IF_HEAD).values()) != {"PASS"}:
        raise RuntimeError("DU V2 reauthentication failed")
    eb_result = IS.EB.verify_receipt_file(ROOT, eb_path)
    ee_result = IS.EE.verify_receipt_file(ROOT, ee_path)
    if eb_result["overall_result"] != "PASS" or ee_result["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise RuntimeError("EB/EE V2 reauthentication failed")
    eb = IS.load_canonical(eb_path)["receipt"]
    ee = IS.load_canonical(ee_path)["receipt"]
    runtime_target = eb["runtime_target_selection_binding"]
    baseline = eb["certification_baseline"]
    if (runtime_target["head"], runtime_target["tree"]) != (IS.IF_HEAD, IS.IF_TREE):
        raise RuntimeError("runtime target is not IF")
    if baseline != {"head": IS.HEAD, "tree": IS.TREE}:
        raise RuntimeError("certification baseline is not IR")
    if ee["runtime_target_selection_binding"] != runtime_target or ee["certification_baseline"] != baseline:
        raise RuntimeError("V2 role separation disagreement")
    if (context["generation_identity"], context["operation_identity"]) != (IS.GENERATION, IS.OPERATION):
        raise RuntimeError("IS context identity mismatch")
    if (context["repository_head"], context["repository_tree"]) != (IS.HEAD, IS.TREE):
        raise RuntimeError("IS context repository identity mismatch")
    if context["candidate_manifest_sha256"] != IS.FUTURE_CANDIDATE_SHA:
        raise RuntimeError("IS context candidate mismatch")

    try:
        IS.FM.prove_guest_adapter_binding(ROOT, context)
    except RuntimeError as exc:
        exact_failure = f"{type(exc).__name__}: {exc}"
    else:
        raise RuntimeError("expected FUTURE bootstrap blocker was not reproduced")
    if exact_failure != "RuntimeError: cloud-init adapter bootstrap consumer mismatch":
        raise RuntimeError(f"unexpected blocker: {exact_failure}")
    cloud_text = (ROOT / IS.FM.FUTURE_CLOUD_INIT).read_text(encoding="utf-8")
    bootstrap_guest_path = context["guest_adapter_binding"]["bootstrap_guest_path"]
    if bootstrap_guest_path in cloud_text:
        raise RuntimeError("bootstrap consumer unexpectedly present")
    marker = "G77_256IF_FUTURE_BOOTSTRAP_PROHIBITED_UNTIL_POST_COMMIT_REBIND"
    if marker not in cloud_text:
        raise RuntimeError("committed bootstrap prohibition marker absent")

    forbidden = [
        IS_ROOT / "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        IS_ROOT / "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        IS_ROOT / "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        IS_ROOT / "G77_256IS_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        IS_ROOT / "G77_256IS_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        Path(context["pre_receipt_path"]), Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(Path(context["runtime_export_root"]) / relative for relative in context["guest_output_relative_paths"]),
    ]
    present = [str(path) for path in forbidden if path.exists() or path.is_symlink()]
    if present:
        raise RuntimeError(f"forbidden operational artifact present: {present}")

    counters = {key: 0 for key in (
        "authorization_presentation", "human_operational_authority", "authority_consumption",
        "pre", "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "future_operation", "request", "p11_entry", "protected_invocation",
        "protected_effect", "retry", "repair_retry", "replay", "e05_credit",
    )}
    missing = "COMMITTED_FUTURE_NOCLOUD_BOOTSTRAP_THAT_INVOKES_THE_EXISTING_FM_BOOTSTRAP_GUEST_PATH"
    legal = "SEPARATE_HUMAN_GOVERNED_GENERATION_FOR_FUTURE_BOOTSTRAP_AND_SEED_BINDING_THEN_POST_COMMIT_READINESS_CERTIFICATION"
    return {
        "schema_id": "G77_256IS_SPCE_TERMINAL_PREAUTHORIZATION_BLOCKER_V1",
        "terminal": "E__CONSTITUTIONAL_REGRESSION",
        "mode": "PREAUTHORIZATION_FAIL_CLOSED__NO_AUTHORITY__NO_OPERATION",
        "entry": entry, "ir_reconstruction": ir, "fresh_identity": identity,
        "future_semantics": future,
        "v2_role_separation": {
            "runtime_target": runtime_target, "certification_baseline": baseline,
            "runtime_certification_role_collapse": "VERIFIED__NO",
            "du": "PASS", "eb": "PASS", "ee": "PASS",
            "if_candidate_sha256": sha256_path(candidate),
            "v2_readiness_candidate_sha256": sha256_path(v2_candidate),
        },
        "blocker": {
            "last_verified_edge": "IF_CANDIDATE_AND_IR_BASELINE_V2_ROLE_SEPARATION__FM_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU",
            "first_broken_edge": "FM_AUTHORITY_FREE_STATIC_READINESS__FUTURE_CLOUD_INIT_ADAPTER_BOOTSTRAP_CONSUMER",
            "blocking_owner": IS.FM.FUTURE_CLOUD_INIT, "blocking_seed": IS.FM.FUTURE_SEED,
            "exact_failure": exact_failure, "bootstrap_guest_path_required": bootstrap_guest_path,
            "bootstrap_guest_path_occurrence_count": 0, "committed_prohibition_marker": marker,
            "ir_readiness_overclaim": "VERIFIED__IR_PRESENTATION_READINESS_DID_NOT_EXERCISE_FULL_FM_STATIC_BOOTSTRAP_CLOSURE",
            "minimum_missing_capability": missing, "minimum_legal_next_delta": legal,
        },
        "authority_boundary": {
            "preauthorization_presentation": "NOT_PROVEN__BLOCKED_BEFORE_SEALED_REQUEST",
            "human_authorization_action_available": "VERIFIED__NO",
            "human_operational_authority": "VERIFIED__0", "authority_consumption": "VERIFIED__0",
            "prompt_is_authority": False, "provider_capability_is_authority": False,
        },
        "operational_counters": counters,
        "e05": {"before": "10/18", "after": "10/18", "future_credit": 0,
                "satisfied": 10, "required": 18, "remaining": 8},
        "attempt_accounting": {
            "preauthorization_derivation_invocation_count": 2,
            "first_nonoperational_failure": "DU_V2_REJECTED_ARCHIVED_IF_V1_CANDIDATE__CORRECTED_BY_SEPARATING_V2_READINESS_FIXTURE_FROM_IF_RUNTIME_CANDIDATE",
            "second_nonoperational_failure": exact_failure,
            "operational_attempt_count": 0, "retry_count": 0,
            "repair_retry_count": 0, "replay_count": 0,
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__IR_IQ_IP_IO_IN_IF_IE_IC_GN_GL_FM_HUMAN_ACT_DU_EB_EE_V2_P11_CHE_FK_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__IS_SCOPED_FAILURE_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__15__IE_THROUGH_IS",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__0",
            "new_common_infrastructure_for_future": "VERIFIED__0",
            "new_vector_specific_infrastructure_for_future": "VERIFIED__0",
            "marginal_new_infrastructure_for_is": "VERIFIED__FAIL_CLOSED_EVIDENCE_ONLY",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_HIGH_BUT_OPERATIONAL_BOOTSTRAP_GAP_UNRESOLVED",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__TERMINAL_BLOCKER_AND_REPOSITORY_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED",
            "inter_generation_cross_worker_continuation": "VERIFIED__IR_TO_IS",
            "intra_generation_cross_worker_continuation": "NOT_APPLICABLE__NO_DELEGATION",
            "uncommitted_delta_recovery": "VERIFIED__BOUNDED_IS_FAILURE_EVIDENCE",
            "authority_state_recovery": "VERIFIED__NO_AUTHORITY_CREATED",
            "consumed_authority_recovery": "NOT_APPLICABLE__NO_AUTHORITY_CONSUMED",
            "post_operation_state_recovery": "NOT_APPLICABLE__NO_OPERATION",
            "operation_replay_prevention": "VERIFIED__NO_OPERATION_AND_NO_AUTHORITY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__WORKER_IDENTITY_NOT_INSTRUMENTED",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_PREAUTHORIZATION_BLOCKER",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "prompt_externalization": {
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_context": "VERIFIED__GIT_IR_IF_FM_GN_GL_DU_EB_EE_P11_CHE_FK_EX_LAYER_0_NESTED_AUTHORITY",
            "prompt_required_context": "VERIFIED__IS_COMMISSION_VECTOR_AND_SPLIT_PHASE_BOUNDARY",
            "previous_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
        },
        "metrics": {
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_BEFORE_AUTHORITY_ON_BOOTSTRAP_BINDING_REGRESSION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__COMMITTED_FUTURE_BOOTSTRAP_AND_POST_COMMIT_READINESS_THEN_FRESH_HUMAN_AUTHORITY",
            "governance_efficience": "ESTIMATED__FAIL_CLOSED_BEFORE_AUTHORITY_OR_OPERATION",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_PRODUCTION_OWNER_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__AUTHENTICATED_IR_TO_IS_REPOSITORY_CONTINUATION",
            "aigol_codex_work_share": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW_IF_NEXT_DELTA_REMAINS_BOOTSTRAP_LOCAL",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_PRIMARY",
            "candidate_capability": "VERIFIED__IF_BOUND_RUNTIME_CANDIDATE_WITH_IR_BASELINE_V2_READINESS__NOT_PREAUTHORIZATION_READY__NOT_AUTHORIZED",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "constitutional_continuation_progress": "VERIFIED__IR_READINESS_RECONSTRUCTED__IS_FULL_FM_STATIC_CLOSURE_BLOCKER_EXPOSED",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED", "e05_generations_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "operational_attempts_per_credit": "NOT_APPLICABLE__ZERO_FUTURE_OPERATIONAL_ATTEMPTS_AND_CREDIT",
            "marginal_e05_generation_cost": "NOT_MEASURED",
            "marginal_new_infrastructure_per_e05_credit": "NOT_APPLICABLE__ZERO_FUTURE_CREDIT",
            "infrastructure_amortization_signal": "ESTIMATED__REUSE_HIGH_BUT_OPERATIONAL_BOOTSTRAP_GAP_UNRESOLVED",
            "expected_next_credit_generation_count": "NOT_PROVEN",
        },
        "terminal_frontier": {
            "last_verified_edge": "IF_CANDIDATE_AND_IR_BASELINE_V2_ROLE_SEPARATION__FM_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU",
            "first_broken_edge": "FM_AUTHORITY_FREE_STATIC_READINESS__FUTURE_CLOUD_INIT_ADAPTER_BOOTSTRAP_CONSUMER",
            "minimum_missing_capability": missing, "minimum_legal_next_delta": legal,
            "auto_continuable": False, "human_review_required": True,
            "next_generation_started": False,
        },
    }


def main(args: argparse.Namespace) -> None:
    reduction = reduce(args)
    envelope = {
        "schema_id": "G77_256IS_SPCE_TERMINAL_PREAUTHORIZATION_BLOCKER_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    if REDUCTION_PATH.exists() or REDUCTION_PATH.is_symlink():
        raise RuntimeError("terminal reduction collision")
    REDUCTION_PATH.write_bytes(canonical_bytes(envelope))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
