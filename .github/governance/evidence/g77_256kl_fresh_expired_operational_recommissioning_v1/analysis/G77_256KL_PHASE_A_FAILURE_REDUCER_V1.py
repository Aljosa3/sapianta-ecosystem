#!/usr/bin/env python3
"""Reduce the one-shot KL Phase-A GN schema failure without repair or retry."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KL = Path(
    ".github/governance/evidence/"
    "g77_256kl_fresh_expired_operational_recommissioning_v1"
)
HEAD = "c625542a01873fd6a4bc4bd9f1306e7f2f48a4ae"
TREE = "8d6cf10756adac4931f931d2e90b42bf49c8d26c"
SUBJECT = "G77-256KK verify KJ Phase A harness path binding"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
TERMINAL = (
    "M__KL_PHASE_A_FAIL_CLOSED_AT_GN_EXACT_SEALED_REQUEST_SCHEMA_"
    "VALIDATION_BEFORE_HUMAN_DECISION_PRESENTATION_OR_KK_BINDING"
)
KK_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kk_kj_phase_a_harness_path_binding_correction_v1/"
    "G77_256KK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
KK_REDUCTION_SHA256 = "b3e8d160c61aeede9a23233b168cf46179ed993f0f92d509446ec62e3540f862"
KK_INNER_SHA256 = "f5fe831eb1bbc232ade6ebf76b35383e61a606a0c97363be0990f6decdef4736"
GN_OWNER = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GN_OWNER_SHA256 = "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3"
JV_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jv_expired_gn_request_schema_binding_repair_v1/"
    "G77_256JV_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JV_REDUCTION_SHA256 = "ffd562a24c0d9d209af3fe2552fff75db373727ce7a10f2343958765ec42971f"
WRAPPER = KL / "orchestration/G77_256KL_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCER = KL / "analysis/G77_256KL_PHASE_A_FAILURE_REDUCER_V1.py"
TESTS = KL / "tests/test_g77_256kl_phase_a_fail_closed_v1.py"
REPORT = KL / "G77_256KL_G48_IMPLEMENTATION_REPORT_V1.md"
OUTPUT = KL / "G77_256KL_SPCE_PHASE_A_TERMINAL_FAIL_CLOSED_REDUCTION_V1.json"
READINESS = KL / "G77_256KL_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
REQUEST = KL / "G77_256KL_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
AUTH_PRESENTATION = KL / "G77_256KL_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
SAFE_STOP = KL / "G77_256KL_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
PREHUMAN = KL / "G77_256KL_PREHUMAN_PHASE_A_REDUCTION_V1.json"
KI_PREFLIGHT = KL / "G77_256KL_KI_FRONTIER_PREFLIGHT_V1.json"
HUMAN_DECISION = KL / "G77_256KL_HUMAN_DECISION_PRESENTATION_V1.txt"
KK_PREFLIGHT = KL / "G77_256KL_KK_CLOSURE_PREFLIGHT_V1.json"
TRANSIENT_ROOT = Path(
    "/tmp/g77_256kl_fresh_expired_operational_recommissioning_v1"
)
LAST_OPERATIONAL_EDGE = (
    "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_"
    "NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
)
FIRST_UNVERIFIED_OPERATIONAL_EDGE = (
    "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
)


class KLReductionError(RuntimeError):
    """One deterministic fail-closed KL reduction error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def git(*arguments: str, nested: bool = False) -> str:
    command = ["git"]
    if nested:
        command.extend(["-C", "sapianta_system"])
    command.extend(arguments)
    return subprocess.run(
        command, cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def committed(path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HEAD}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KLReductionError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value))
    ):
        raise KLReductionError(f"INNER_SEAL_MISMATCH:{inner}")
    return value


def load_gn_owner():
    path = ROOT / GN_OWNER
    if path.read_bytes() != committed(GN_OWNER) or sha256_path(GN_OWNER) != GN_OWNER_SHA256:
        raise KLReductionError("COMMITTED_GN_OWNER_MISMATCH")
    specification = importlib.util.spec_from_file_location("g77_256kl_gn_reducer", path)
    if specification is None or specification.loader is None:
        raise KLReductionError("GN_OWNER_IMPORT_SPEC_INVALID")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


GN = load_gn_owner()


def verify_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
    }
    if observed != {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
    } or remote_head != HEAD:
        raise KLReductionError(f"ENTRY_IDENTITY_MISMATCH:{observed}")
    if git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise KLReductionError("TRACKED_OR_INDEX_MUTATION_DETECTED")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    prefix = KL.as_posix() + "/"
    if not untracked or any(not path.startswith(prefix) for path in untracked):
        raise KLReductionError(f"UNBOUNDED_UNTRACKED_SCOPE:{untracked}")
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
    } or nested_remote_tag != NESTED_HEAD:
        raise KLReductionError(f"NESTED_AUTHORITY_MISMATCH:{nested}")
    return {
        **observed,
        "remote_head": remote_head,
        "remote_equality": "VERIFIED__DIRECT_BRANCH_LS_REMOTE_AT_ENTRY",
        "worktree_entry_state": "VERIFIED__CLEAN_BEFORE_FIRST_KL_MUTATION",
        "index_entry_state": "VERIFIED__EMPTY_BEFORE_FIRST_KL_MUTATION",
        "nested_authority": {
            **nested,
            "immutable_ref": "refs/tags/sapianta-system-nested-authority-3183bab-v1",
            "remote_tag_equal": "VERIFIED__DIRECT_LS_REMOTE_AT_ENTRY",
        },
    }


def verify_kk() -> dict[str, Any]:
    raw = (ROOT / KK_REDUCTION).read_bytes()
    if raw != committed(KK_REDUCTION) or sha256_bytes(raw) != KK_REDUCTION_SHA256:
        raise KLReductionError("COMMITTED_KK_REDUCTION_MISMATCH")
    envelope = load_canonical(KK_REDUCTION)
    reduction = verify_seal(envelope, "reduction")
    if (
        envelope["reduction_sha256"] != KK_INNER_SHA256
        or reduction.get("terminal")
        != "A__KJ_PHASE_A_HARNESS_PATH_BINDING_REPOSITORY_VERIFIED__NO_AUTHORITY__NO_OPERATION__NO_KJ_RETRY"
        or reduction.get("binding", {}).get("kj_phase_a_harness_path_binding")
        != "VERIFIED"
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise KLReductionError("KK_CLOSURE_CONTRACT_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "file_sha256": KK_REDUCTION_SHA256,
        "inner_sha256": KK_INNER_SHA256,
        "path_binding": "VERIFIED",
        "ex_reused": reduction["baseline"]["ex_reused"],
        "ex_reconstructed": reduction["baseline"]["ex_reconstructed"],
        "successor_reauthentication": reduction["baseline"][
            "successor_reauthentication"
        ],
    }


def verify_jv() -> dict[str, Any]:
    raw = (ROOT / JV_REDUCTION).read_bytes()
    if raw != committed(JV_REDUCTION) or sha256_bytes(raw) != JV_REDUCTION_SHA256:
        raise KLReductionError("COMMITTED_JV_REDUCTION_MISMATCH")
    envelope = json.loads(raw)
    reduction = envelope.get("reduction", {})
    if (
        envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal")
        != "A__GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED"
        or reduction.get("gn_contract", {}).get("contract_conclusion")
        != "A_AND_D__GN_V1_IS_VECTOR_INDEPENDENT__JU_USED_WRONG_PROJECTION"
    ):
        raise KLReductionError("JV_GN_CONTRACT_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "file_sha256": JV_REDUCTION_SHA256,
        "gn_contract_conclusion": reduction["gn_contract"]["contract_conclusion"],
    }


def verify_partial_state() -> dict[str, Any]:
    readiness_envelope = load_canonical(READINESS)
    readiness = verify_seal(readiness_envelope, "checkpoint")
    request_envelope = load_canonical(REQUEST)
    request = verify_seal(request_envelope, "request")
    safe_envelope = load_canonical(SAFE_STOP)
    safe = verify_seal(safe_envelope, "checkpoint")
    reduction_envelope = load_canonical(PREHUMAN)
    reduction = verify_seal(reduction_envelope, "reduction")
    ki_envelope = load_canonical(KI_PREFLIGHT)
    verify_seal(ki_envelope, "proof")

    expected = set(GN.PREAUTHORIZATION_FIELDS)
    actual = set(request.get("preauthorization", {}))
    extras = actual - expected
    if extras != {
        "ki_frontier_preflight_file_sha256",
        "ki_frontier_preflight_inner_sha256",
    } or expected - actual:
        raise KLReductionError(f"UNEXPECTED_GN_FIELD_DIFFERENCE:{sorted(extras)}")
    try:
        GN.load_validated_sealed_request(ROOT / REQUEST)
    except GN.PresentationBindingError as exc:
        if str(exc) != "SEALED_REQUEST_PREAUTHORIZATION_INVALID":
            raise KLReductionError(f"UNEXPECTED_GN_FAILURE:{exc}") from exc
    else:
        raise KLReductionError("GN_SCHEMA_FAILURE_NOT_REPRODUCIBLE")

    counter_sets = [
        readiness.get("operational_counters", {}),
        safe.get("operational_counters", {}),
        reduction.get("operational_counters", {}),
    ]
    if any(any(counters.values()) for counters in counter_sets):
        raise KLReductionError("NONZERO_OPERATIONAL_COUNTER")
    if (ROOT / HUMAN_DECISION).exists() or (ROOT / KK_PREFLIGHT).exists():
        raise KLReductionError("FAILURE_BOUNDARY_ADVANCED_UNEXPECTEDLY")
    if not (ROOT / AUTH_PRESENTATION).is_file():
        raise KLReductionError("PREFAILURE_AUTHORIZATION_PRESENTATION_NOT_FOUND")
    if not TRANSIENT_ROOT.is_dir() or not (TRANSIENT_ROOT / "checkout").is_dir():
        raise KLReductionError("PHASE_A_TRANSIENT_CHECKOUT_NOT_PRESERVED")

    identities = readiness["identities"]
    return {
        "generation": readiness["generation_identity"],
        "operation": readiness["operation_identity"],
        "candidate_sha256": identities["candidate_sha256"],
        "context": identities["context_sha256"],
        "context_file_sha256": identities["context_file_sha256"],
        "canonical_argv_sha256": identities["canonical_argv_sha256"],
        "temporal_binding": identities["temporal_binding_sha256"],
        "request_identity": request_envelope["request_sha256"],
        "request_file_sha256": sha256_path(REQUEST),
        "authorization_presentation_sha256": sha256_path(AUTH_PRESENTATION),
        "authorization_presentation_state": "NOT_VALID__STALE_AFTER_REQUEST_RESEAL_BEFORE_GN_REVALIDATION",
        "readiness_checkpoint": readiness_envelope["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(READINESS),
        "safe_stop_checkpoint": safe_envelope["checkpoint_sha256"],
        "safe_stop_checkpoint_file_sha256": sha256_path(SAFE_STOP),
        "safe_stop_state": "NOT_PROVEN__PRE_KI_CHECKPOINT_STALE_RELATIVE_TO_MUTATED_REQUEST",
        "ki_frontier_preflight_file_sha256": sha256_path(KI_PREFLIGHT),
        "gn_expected_preauthorization_fields": sorted(expected),
        "gn_actual_preauthorization_fields": sorted(actual),
        "gn_unexpected_fields": sorted(extras),
        "gn_exception": "PresentationBindingError: SEALED_REQUEST_PREAUTHORIZATION_INVALID",
        "human_decision_presentation": "NOT_CREATED__FAIL_CLOSED_BEFORE_PRESENTATION",
        "kk_closure_preflight": "NOT_CREATED__FAIL_CLOSED_BEFORE_KK_BINDING",
        "transient_root": str(TRANSIENT_ROOT),
        "transient_root_state": "PRESENT__PHASE_A_MATERIALIZED_CHECKOUT__NONAUTHORITY__NO_VM",
        "fresh_kl_phase_a_presentation_ready": "NOT_PROVEN",
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


def build_reduction(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    entry = verify_entry(remote_head, nested_remote_tag)
    kk = verify_kk()
    jv = verify_jv()
    partial = verify_partial_state()
    return {
        "schema_id": "G77_256KL_PHASE_A_FAIL_CLOSED_REDUCTION_V1",
        "terminal": TERMINAL,
        "mode": "SPCE_PHASE_A__FAIL_CLOSED__NO_AUTHORITY__NO_OPERATION__NO_REPAIR__NO_RETRY",
        "vector": "EXPIRED",
        "entry": entry,
        "kk_authentication": kk,
        "jv_gn_contract_authentication": jv,
        "partial_phase_a_state": partial,
        "failure": {
            "failure_class": "EVIDENCE_OR_REPORTING_DEFECT",
            "exact_exception": partial["gn_exception"],
            "failure_boundary": "INHERITED_KJ_KI_BINDING_AFTER_KI_PREFLIGHT_AND_REQUEST_RESEAL_BEFORE_GN_PRESENTATION_REVALIDATION_KK_BINDING_OR_HUMAN_DECISION_PRESENTATION",
            "novelty": "VERIFIED__NEW_INHERITED_KJ_KI_PREFLIGHT_FIELDS_ADDED_TO_GN_EXACT_PREAUTHORIZATION_OBJECT__NO_NEW_PRODUCTION_SEMANTICS",
            "affected_invariant": "GN_EXACT_SEALED_REQUEST_SCHEMA_PRESERVATION_DURING_PHASE_A_PREFLIGHT_BINDING",
            "previous_closest_edge": "JV_GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION_REPOSITORY_VERIFIED",
            "semantic_difference": "VERIFIED__TWO_KI_PREFLIGHT_DIGEST_FIELDS_ADDED_BEYOND_AUTHENTICATED_GN_PREAUTHORIZATION_FIELD_SET",
            "production_behavior_impact": "VERIFIED__NONE__FAILURE_PRECEDED_HUMAN_DECISION_AUTHORITY_AND_OPERATION",
            "new_capability_required": "NOT_PROVEN",
            "new_proof_required": "VERIFIED__GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_MUST_BE_PROVEN_SEPARATELY",
            "convergence_signal": "VERIFIED__KK_PATH_EDGE_CLOSED__NEXT_LOCAL_PHASE_A_EVIDENCE_EDGE_LOCALIZED__KI_OPERATIONAL_FRONTIER_UNCHANGED",
            "repetition_pressure": "ESTIMATED__HIGH_IF_PARTIAL_KL_PHASE_A_IS_REPAIRED_OR_RETRIED_IN_PLACE",
            "verification_amplification_risk": "VERIFIED__HIGH_IF_SCHEMA_FAILURE_IS_PATCHED_AND_PHASE_A_RETRIED_RECURSIVELY",
            "classification_evidence": "VERIFIED__AUTHENTICATED_GN_EXACT_FIELD_SET__SEALED_KL_REQUEST_EXTRA_FIELDS__EXACT_PRESENTATION_BINDING_EXCEPTION",
            "classification_confidence": "VERIFIED__HIGH",
        },
        "frontier": {
            "last_verified_operational_edge": LAST_OPERATIONAL_EDGE,
            "first_unverified_operational_edge": FIRST_UNVERIFIED_OPERATIONAL_EDGE,
            "last_verified_edge": "FRESH_KL_BASE_PHASE_A_COORDINATES_AND_KI_PREFLIGHT_MATERIALIZED_BEFORE_GN_SCHEMA_REVALIDATION",
            "first_broken_edge": "INHERITED_KJ_KI_PREFLIGHT_FIELDS_EXPAND_GN_EXACT_PREAUTHORIZATION_FIELD_SET",
            "current_real_blocker": "VERIFIED__KL_SEALED_REQUEST_PREAUTHORIZATION_FIELD_SET_REJECTED_BY_AUTHENTICATED_GN_OWNER",
            "minimum_missing_capability": "VERIFIED__PHASE_A_EVIDENCE_BINDING_COMPATIBILITY_WITH_AUTHENTICATED_GN_EXACT_SCHEMA__NOT_A_PRODUCTION_CAPABILITY",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_CORRECTION__NO_KL_RETRY_OR_OPERATION",
        },
        "baseline": {
            "e05_state": "VERIFIED__11_OF_18",
            "e05_frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "e05_credit": "VERIFIED__0",
            "kl_phase_a_e05_credit": "VERIFIED__0",
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
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0__PHASE_A_NOT_COMPLETE",
            "new_operational_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1__GN_EXACT_PREAUTHORIZATION_SCHEMA_BINDING",
            "new_blocker_closed_count": "VERIFIED__0",
            "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
            "new_classification_result_count": "VERIFIED__1__EVIDENCE_OR_REPORTING_DEFECT",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
        },
        "governance": {
            "project_state": "VERIFIED__KL_PHASE_A_FAIL_CLOSED_BEFORE_HUMAN_DECISION_PRESENTATION",
            "project_progress": "VERIFIED__FRESH_COORDINATES_PARTIALLY_MATERIALIZED__GN_SCHEMA_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__KL_PHASE_A_NOT_READY__SEPARATE_EVIDENCE_BINDING_CORRECTION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__GN_FAIL_CLOSED__ZERO_AUTHORITY_AND_OPERATION__NO_REPAIR_OR_RETRY",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__MEDIUM__EXACT_SCHEMA_OWNER_STOPPED_INVALID_PRESENTATION",
            "overengineering_risk": "ESTIMATED__HIGH_IF_REPAIRED_OR_RETRIED_WITHIN_KL",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_AND_EXACT_GN_EXCEPTION_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SEALED_FAIL_CLOSED_KL_REDUCTION",
            "candidate_capability": "NOT_PROVEN__KL_PHASE_A_PRESENTATION_NOT_READY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_UNCHANGED_AND_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__KK_TO_KL_PARTIAL_PHASE_A__STOPPED_AT_GN_SCHEMA_EDGE",
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES_UNTIL_NEW_KL_LOCAL_SCHEMA_FAILURE",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "reuse_impact_assessment": {
            "1_katere_obstojece_certificirane_zmogljivosti_se_ponovno_uporabijo": "VERIFIED__EX_17_OF_17__JZ__KB__KD__KF__KG__KH__KI__KJ__KK__JV__GN",
            "2_katere_nove_zmogljivosti_ce_sploh_nastanejo": "VERIFIED__NO_NEW_CAPABILITY__ONE_FAILURE_CLASSIFICATION_ONLY",
            "3_ali_katera_obstojeca_zmogljivost_postane_nedosegljiva": "VERIFIED__NO",
            "4_ali_implementacija_ustvarja_vzporedni_tok": "VERIFIED__NO",
            "5_ali_zmanjsuje_ali_povecuje_stevilo_produkcijskih_poti": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "artifact_bindings": {
            path.as_posix(): sha256_path(path) for path in (WRAPPER, REDUCER, TESTS, REPORT)
        },
        "human_authority_present": False,
        "phase_b_started": False,
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256KL_PHASE_A_FAIL_CLOSED_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    parser.add_argument("--emit", action="store_true")
    arguments = parser.parse_args()
    expected = envelope(build_reduction(arguments.remote_head, arguments.nested_remote_tag))
    if arguments.emit:
        print(canonical_bytes(expected).decode("utf-8"), end="")
        return 0
    observed = load_canonical(OUTPUT)
    if observed != expected:
        raise KLReductionError("PERSISTED_REDUCTION_MISMATCH")
    print(TERMINAL)
    print("FAILURE_CLASS=EVIDENCE_OR_REPORTING_DEFECT")
    print("OPERATIONAL_EFFECT=0")
    print("E05_CREDIT=VERIFIED__0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
