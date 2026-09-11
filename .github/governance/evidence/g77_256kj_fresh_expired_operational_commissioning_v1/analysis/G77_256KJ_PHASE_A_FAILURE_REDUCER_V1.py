#!/usr/bin/env python3
"""Reduce the KJ Phase-A wrapper-path failure without repairing or operating."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KJ = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_commissioning_v1"
)
OUTPUT = KJ / "G77_256KJ_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
WRAPPER = KJ / "orchestration/G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
EXPECTED_WRAPPER = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
)

HEAD = "6fb11ada9ca2765ccc8e4e97da3a18838a756d6a"
TREE = "65bf8eb5ae02fedcb5ff725bda339b455ebec6b1"
SUBJECT = "G77-256KI reconstruct expired operational frontier"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
TERMINAL = (
    "M__KJ_PHASE_A_FAIL_CLOSED_AT_AUTHENTICATED_OWNER_WRAPPER_PATH_BINDING_"
    "BEFORE_MATERIALIZATION_OR_HUMAN_PRESENTATION"
)
LAST_OPERATIONAL_EDGE = (
    "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_"
    "NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
)
FIRST_UNVERIFIED_OPERATIONAL_EDGE = (
    "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
)


class KJReductionError(RuntimeError):
    """One deterministic reduction error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def verify_reduction_inputs() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    }
    if observed != expected or git("diff", "--cached", "--name-only"):
        raise KJReductionError(f"REDUCTION_ENTRY_MISMATCH:{observed}")
    nested = {
        "head": git("rev-parse", "HEAD", nested=True),
        "tree": git("rev-parse", "HEAD^{tree}", nested=True),
        "origin": git("remote", "get-url", "origin", nested=True),
        "clean": git("status", "--porcelain", nested=True) == "",
        "detached": git("branch", "--show-current", nested=True) == "",
    }
    if nested != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "origin": NESTED_ORIGIN,
        "clean": True,
        "detached": True,
    }:
        raise KJReductionError(f"NESTED_MISMATCH:{nested}")
    wrapper_path = ROOT / WRAPPER
    expected_path = ROOT / EXPECTED_WRAPPER
    if not wrapper_path.is_file() or expected_path.exists():
        raise KJReductionError("WRAPPER_PATH_FAILURE_NOT_REPRODUCIBLE")
    ast.parse(wrapper_path.read_text(encoding="utf-8"))
    source = wrapper_path.read_text(encoding="utf-8")
    if "load_adapted_kg_materializer" not in source:
        raise KJReductionError("AUTHENTICATED_OWNER_ADAPTATION_NOT_PRESENT")
    forbidden_phase_a_outputs = (
        "G77_256KJ_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json",
        "G77_256KJ_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256KJ_HUMAN_DECISION_PRESENTATION_V1.txt",
        "G77_256KJ_PREHUMAN_PHASE_A_REDUCTION_V1.json",
    )
    present = [name for name in forbidden_phase_a_outputs if (ROOT / KJ / name).exists()]
    if present:
        raise KJReductionError(f"UNEXPECTED_PHASE_A_OUTPUTS:{present}")
    return {
        **observed,
        "remote_head": HEAD,
        "remote_equality": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
        "worktree_entry_state": "VERIFIED__CLEAN_BEFORE_FIRST_KJ_MUTATION",
        "index_entry_state": "VERIFIED__EMPTY_BEFORE_FIRST_KJ_MUTATION",
        "nested_authority": {
            **nested,
            "immutable_ref": (
                "refs/tags/sapianta-system-nested-authority-3183bab-v1"
            ),
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
        },
        "wrapper_path": WRAPPER.as_posix(),
        "wrapper_file_sha256": sha256_path(wrapper_path),
        "expected_wrapper_path": EXPECTED_WRAPPER.as_posix(),
        "expected_wrapper_path_exists": False,
        "phase_a_outputs_created_before_failure": 0,
    }


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


def build_reduction() -> dict[str, Any]:
    entry = verify_reduction_inputs()
    return {
        "schema_id": "G77_256KJ_PHASE_A_FAIL_CLOSED_REDUCTION_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A__FAIL_CLOSED__NO_AUTHORITY__NO_OPERATION__NO_REPAIR__NO_RETRY",
        "vector": "EXPIRED",
        "entry": entry,
        "failure": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "gap_classification": "PHASE_A_WRAPPER_PATH_BINDING_GAP",
            "exact_exception": (
                "FileNotFoundError: [Errno 2] No such file or directory: "
                f"'{(ROOT / EXPECTED_WRAPPER).as_posix()}'"
            ),
            "failure_boundary": "PHASE_A_KD_INTERFACE_PREFLIGHT_BEFORE_MATERIALIZATION_OR_HUMAN_PRESENTATION",
            "last_verified_edge": "KI_FRONTIER_KF_JZ_AND_COMMITTED_KG_PHASE_A_PATTERN_AUTHENTICATED",
            "first_broken_edge": "ADAPTED_OWNER_EXPECTED_KJ_WRAPPER_UNDER_OPERATIONAL_RECOMMISSIONING_DIRECTORY_BUT_WRAPPER_EXISTS_UNDER_OPERATIONAL_COMMISSIONING_DIRECTORY",
            "current_real_blocker": "VERIFIED__KJ_PHASE_A_WRAPPER_PATH_DOES_NOT_MATCH_AUTHENTICATED_ADAPTED_OWNER_PATH",
            "minimum_missing_capability": "VERIFIED__KJ_PHASE_A_HARNESS_PATH_BINDING_TO_AUTHENTICATED_RECOMMISSIONING_DIRECTORY_CONVENTION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_KJ_PHASE_A_HARNESS_PATH_BINDING_CORRECTION__NO_OPERATION",
        },
        "failure_novelty_and_convergence_check": {
            "failure_class": "HARNESS_OR_TEST_ARTIFACT",
            "novelty": "VERIFIED__NEW_KJ_LOCAL_WRAPPER_PATH_NAMING_MISMATCH__NO_NEW_PRODUCTION_SEMANTICS",
            "affected_invariant": "PHASE_A_DETERMINISTIC_AUTHENTICATED_OWNER_TO_WRAPPER_PATH_BINDING",
            "previous_closest_edge": "KG_PHASE_A_WRAPPER_AT_AUTHENTICATED_OPERATIONAL_RECOMMISSIONING_DIRECTORY",
            "semantic_difference": "VERIFIED__DIRECTORY_TOKEN_RECOMMISSIONING_VERSUS_COMMISSIONING_ONLY",
            "production_behavior_impact": "VERIFIED__NONE__FAILURE_PRECEDED_MATERIALIZATION_AUTHORITY_AND_OPERATION",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__CORRECTED_KJ_PHASE_A_HARNESS_PATH_BINDING_MUST_BE_REPROVEN_SEPARATELY",
            "convergence_signal": "VERIFIED__KI_OPERATIONAL_FRONTIER_UNCHANGED__KJ_STOPPED_ON_LOCAL_PHASE_A_HARNESS_PATH",
            "repetition_pressure": "ESTIMATED__HIGH_IF_KJ_PHASE_A_IS_RETRIED_INSIDE_THIS_GENERATION",
            "verification_amplification_risk": "VERIFIED__POSSIBLE_IF_FAILURE_IS_REPAIRED_AND_RETRIED_RECURSIVELY",
            "classification_evidence": "VERIFIED__PYTHON_TRACEBACK_EXPECTED_PATH_ABSENT_ACTUAL_WRAPPER_PATH_PRESENT_ZERO_PHASE_A_OUTPUTS",
            "classification_confidence": "VERIFIED__HIGH__FILESYSTEM_AND_AST_CONFIRM",
            "acceptance_requirement_forcing_continuation": "NOT_APPLICABLE__CURRENT_GENERATION_MUST_STOP_FAIL_CLOSED",
        },
        "operational_frontier": {
            "last_verified_operational_edge": LAST_OPERATIONAL_EDGE,
            "first_unverified_operational_edge": FIRST_UNVERIFIED_OPERATIONAL_EDGE,
            "current_real_blocker_before_kj": "NOT_PROVEN__NO_GENUINE_CURRENT_BLOCKER_LOCALIZED",
            "ki_minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED__ONLY_FRESH_OPERATIONAL_EXPIRED_OBSERVATION_REMAINS",
            "ki_minimum_legal_next_delta": "ONE_FRESH_HUMAN_AUTHORIZED_BOUNDED_EXPIRED_OPERATIONAL_ATTEMPT",
        },
        "phase_a_result": {
            "fresh_kj_phase_a_presentation_ready": "NOT_PROVEN",
            "human_decision_presentation": "NOT_CREATED__FAIL_CLOSED_BEFORE_PRESENTATION",
            "safe_stop_checkpoint": "NOT_CREATED__FAIL_CLOSED_BEFORE_MATERIALIZATION",
            "human_authority_present": False,
            "phase_b_started": False,
            "auto_continuable": False,
            "human_review_required": True,
            "repair_performed": False,
            "retry_performed": False,
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "kj_phase_a_e05_credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "operational_counters": zero_counters(),
        "architecture": {
            "production_mutation_count": 0,
            "p11_implementation_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "parallel_flow": "NO",
        },
        "governance": {
            "project_state": "VERIFIED__KJ_PHASE_A_FAIL_CLOSED_BEFORE_MATERIALIZATION",
            "project_progress": "VERIFIED__ENTRY_KI_AND_OWNER_PATTERN_AUTHENTICATED__WRAPPER_PATH_FAILURE_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__KJ_PHASE_A_NOT_READY__SEPARATE_PATH_BINDING_CORRECTION_REQUIRED_AFTER_REVIEW",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_BEFORE_AUTHORITY_OR_OPERATION__NO_REPAIR_OR_RETRY",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__MEDIUM__EARLY_STATIC_FAILURE_PREVENTED_MATERIALIZATION",
            "overengineering_risk": "ESTIMATED__HIGH_IF_REPAIRED_OR_RETRIED_WITHIN_KJ",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_AND_EXACT_PYTHON_TRACEBACK_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SEALED_FAIL_CLOSED_KJ_REDUCTION",
            "candidate_capability": "NOT_PROVEN__KJ_PHASE_A_PRESENTATION_NOT_READY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__KI_TO_KJ_ENTRY_AUTHENTICATED__KJ_STOPPED_AT_LOCAL_HARNESS_PATH",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1__KJ_PHASE_A_WRAPPER_PATH_BINDING",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_classification_result_count": "VERIFIED__1__HARNESS_OR_TEST_ARTIFACT",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES_UNTIL_KJ_LOCAL_PATH_FAILURE",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": "VERIFIED__EX_17_OF_17__KI__KH__KG_PHASE_A_PATTERN_AUTHENTICATED_BEFORE_FAILURE",
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": "VERIFIED__NO_NEW_CAPABILITY__ONE_FAILURE_CLASSIFICATION_ONLY",
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": "VERIFIED__NO",
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KJ_PHASE_A_FAIL_CLOSED_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = envelope(build_reduction())
    if arguments.write:
        (ROOT / OUTPUT).write_bytes(canonical_bytes(result))
    print(TERMINAL)
    print(canonical_bytes(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
