#!/usr/bin/env python3
"""Materialize one fresh nonauthority KL EXPIRED Phase-A Human barrier.

The committed KJ wrapper is namespace-adapted only after the separately
committed KK path-binding closure is authenticated.  This file creates no
Human authority and exposes no Phase-B or operational invocation entrypoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KL = ROOT / (
    ".github/governance/evidence/"
    "g77_256kl_fresh_expired_operational_recommissioning_v1"
)
HEAD = "c625542a01873fd6a4bc4bd9f1306e7f2f48a4ae"
TREE = "8d6cf10756adac4931f931d2e90b42bf49c8d26c"
SUBJECT = "G77-256KK verify KJ Phase A harness path binding"
KJ_WRAPPER = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KJ_WRAPPER_SHA256 = (
    "900741ac1e095d0f0ef2e0c19b102742bf38d3ddf9b11ca602eec463d6e3614f"
)
KJ_OLD_WRAPPER = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_commissioning_v1/orchestration/"
    "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KK_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kk_kj_phase_a_harness_path_binding_correction_v1/"
    "G77_256KK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
KK_REDUCTION_SHA256 = (
    "b3e8d160c61aeede9a23233b168cf46179ed993f0f92d509446ec62e3540f862"
)
KK_INNER_SHA256 = (
    "f5fe831eb1bbc232ade6ebf76b35383e61a606a0c97363be0990f6decdef4736"
)
KK_TERMINAL = (
    "A__KJ_PHASE_A_HARNESS_PATH_BINDING_REPOSITORY_VERIFIED__"
    "NO_AUTHORITY__NO_OPERATION__NO_KJ_RETRY"
)
KL_TERMINAL = (
    "A__FRESH_KL_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)


class KLBarrierError(RuntimeError):
    """One deterministic fail-closed KL Phase-A error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KLBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def load_adapted_kj_materializer() -> ModuleType:
    """Authenticate KJ and adapt its established Phase-A owner to fresh KL."""

    path = ROOT / KJ_WRAPPER
    raw = path.read_bytes()
    committed = subprocess.check_output(
        ["git", "show", f"{HEAD}:{KJ_WRAPPER.as_posix()}"], cwd=ROOT
    )
    if raw != committed or sha256_bytes(raw) != KJ_WRAPPER_SHA256:
        raise KLBarrierError("COMMITTED_KJ_WRAPPER_IDENTITY_MISMATCH")
    if (ROOT / KJ_OLD_WRAPPER).exists() or (ROOT / KJ_OLD_WRAPPER).is_symlink():
        raise KLBarrierError("KJ_INVALID_COMMISSIONING_PATH_REAPPEARED")
    source = raw.decode("utf-8").replace("KJ", "KL").replace("kj", "kl")
    source = source.replace(
        "g77_256kl_fresh_expired_operational_commissioning_v1",
        "g77_256kl_fresh_expired_operational_recommissioning_v1",
    )
    source = source.replace(
        "6fb11ada9ca2765ccc8e4e97da3a18838a756d6a", HEAD
    )
    source = source.replace(
        "65bf8eb5ae02fedcb5ff725bda339b455ebec6b1", TREE
    )
    source = source.replace(
        "G77-256KI reconstruct expired operational frontier", SUBJECT
    )
    module = ModuleType("g77_256kl_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    if module.KL != KL or module.P.E.WRAPPER_PATH != KJ_WRAPPER.__class__(
        KL.relative_to(ROOT) / "orchestration/G77_256KL_PREAUTHORIZATION_MATERIALIZER_V1.py"
    ):
        raise KLBarrierError("KL_AUTHENTICATED_OWNER_PATH_PROJECTION_MISMATCH")
    return module


L = load_adapted_kj_materializer()
P = L.P


def authenticate_kk_closure() -> dict[str, Any]:
    raw = (ROOT / KK_REDUCTION).read_bytes()
    committed = subprocess.check_output(
        ["git", "show", f"{HEAD}:{KK_REDUCTION.as_posix()}"], cwd=ROOT
    )
    if raw != committed or sha256_bytes(raw) != KK_REDUCTION_SHA256:
        raise KLBarrierError("COMMITTED_KK_REDUCTION_IDENTITY_MISMATCH")
    envelope = load_canonical(ROOT / KK_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != KK_INNER_SHA256
        or sha256_bytes(canonical_bytes(reduction)) != KK_INNER_SHA256
    ):
        raise KLBarrierError("KK_REDUCTION_SEAL_MISMATCH")
    binding = reduction.get("binding", {})
    baseline = reduction.get("baseline", {})
    architecture = reduction.get("architecture", {})
    frontier = reduction.get("frontier", {})
    if (
        reduction.get("terminal") != KK_TERMINAL
        or binding.get("kj_phase_a_harness_path_binding") != "VERIFIED"
        or binding.get("corrected_path") != KJ_WRAPPER.as_posix()
        or binding.get("invalid_path_absent") is not True
        or binding.get("accepted_wrapper_location_count") != 1
        or binding.get("fallback_owner") != "VERIFIED__ABSENT"
        or binding.get("second_route") != "VERIFIED__ABSENT"
        or binding.get("wrapper_file_sha256") != KJ_WRAPPER_SHA256
        or binding.get("wrapper_bytes_equal_committed_kj_candidate") is not True
        or reduction.get("fresh_kj_phase_a_presentation_ready") != "NOT_PROVEN"
        or any(reduction.get("operational_counters", {}).values())
        or architecture.get("production_route_before") != 1
        or architecture.get("production_route_after") != 1
        or architecture.get("parallel_flow") != "NO"
        or baseline.get("e05_state") != "VERIFIED__11_OF_18"
        or baseline.get("e05_frontier") != "VERIFIED__7_UNSATISFIED_OF_18"
        or baseline.get("e05_credit") != "VERIFIED__0"
        or baseline.get("ex_reused") != "VERIFIED__17_OF_17"
        or baseline.get("ex_reconstructed") != "VERIFIED__0"
    ):
        raise KLBarrierError("KK_CLOSURE_CONTRACT_MISMATCH")
    return {
        "terminal": KK_TERMINAL,
        "reduction_file_sha256": KK_REDUCTION_SHA256,
        "reduction_inner_sha256": KK_INNER_SHA256,
        "kj_phase_a_harness_path_binding": "VERIFIED",
        "kj_invalid_commissioning_path_binding": "VERIFIED__CLOSED__ABSENT",
        "authenticated_owner_expected_path": "VERIFIED__BOUND",
        "wrapper_path": KJ_WRAPPER.as_posix(),
        "wrapper_sha256": KJ_WRAPPER_SHA256,
        "operational_counters": "VERIFIED__ALL_ZERO",
        "production_route": "VERIFIED__1_TO_1",
        "fresh_kj_phase_a_presentation_ready": "NOT_PROVEN",
        "frontier": frontier,
        "ex_successor_reauthentication": baseline[
            "successor_reauthentication"
        ],
    }


def materialize_kk_preflight(kk: dict[str, Any]) -> dict[str, Any]:
    proof = {
        "schema_id": "G77_256KL_KK_CLOSURE_PREFLIGHT_V1",
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": P.M.GENERATION,
        "operation_identity": P.M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "kk_authentication": kk,
        "prior_failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "prior_failure_novelty": "VERIFIED__NEW_KJ_LOCAL_WRAPPER_PATH_NAMING_MISMATCH__NO_NEW_PRODUCTION_SEMANTICS",
        "prior_affected_invariant": "PHASE_A_DETERMINISTIC_AUTHENTICATED_OWNER_TO_WRAPPER_PATH_BINDING",
        "prior_edge_status": "VERIFIED__CLOSED_BY_KK",
        "current_higher_level_failure_class": "PROOF_GAP",
        "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
        "human_authority_present": False,
        "phase_b_started": False,
        "operational_counters": P.M.zero_counters(),
    }
    envelope = {
        "schema_id": "G77_256KL_KK_CLOSURE_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KL / "G77_256KL_KK_CLOSURE_PREFLIGHT_V1.json"
    L.write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__KK_PATH_BINDING_CLOSURE_REAUTHENTICATED",
        "scope": "REPOSITORY_ONLY__NONAUTHORITY__NONOPERATIONAL",
    }


def bind_kk_into_phase_a(kk: dict[str, Any], preflight: dict[str, Any]) -> None:
    readiness_path = KL / "G77_256KL_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KL / "G77_256KL_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KL / "G77_256KL_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KL / "G77_256KL_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KL / "G77_256KL_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KL / "G77_256KL_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = L.load_canonical(readiness_path)
    readiness["checkpoint"]["kk_closure_preflight"] = preflight
    L.reseal(readiness, "checkpoint")
    L.write_canonical(readiness_path, readiness)

    request = L.load_canonical(request_path)
    request["request"]["preauthorization"].update(
        {
            "checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
            "kk_closure_preflight_file_sha256": preflight["file_sha256"],
            "kk_closure_preflight_inner_sha256": preflight["inner_sha256"],
        }
    )
    L.reseal(request, "request")
    L.write_canonical(request_path, request)

    presentation_path.write_bytes(
        P.M.GN.render_human_authorization_presentation(request_path)
    )
    gn_result = P.M.GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    equivalence = L.load_canonical(equivalence_path)
    equivalence["proof"].update(
        {
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn_result,
        }
    )
    L.reseal(equivalence, "proof")
    L.write_canonical(equivalence_path, equivalence)

    safe_stop = L.load_canonical(safe_stop_path)
    safe_stop["checkpoint"].update(
        {
            "terminal": KL_TERMINAL,
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "readiness_checkpoint_inner_sha256": readiness["checkpoint_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_file_sha256": sha256_path(equivalence_path),
            "equivalence_inner_sha256": equivalence["proof_sha256"],
            "kk_closure_preflight": preflight,
            "human_authority_authentication_count": 0,
            "human_authority_present": False,
            "phase_b_started": False,
        }
    )
    L.reseal(safe_stop, "checkpoint")
    L.write_canonical(safe_stop_path, safe_stop)

    reduction = L.load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KL_TERMINAL
    value["project_state"] = "PHASE_A_READY__STOPPED_AT_HUMAN_BARRIER"
    value["kk_authentication"] = kk
    value["kk_closure_preflight"] = preflight
    value["owner_results"]["kk_closure_preflight"] = preflight["result"]
    value["prior_failure_novelty_and_convergence_check"] = {
        "failure_class": "HARNESS_OR_TEST_ARTIFACT",
        "novelty": "VERIFIED__NEW_KJ_LOCAL_WRAPPER_PATH_NAMING_MISMATCH__NO_NEW_PRODUCTION_SEMANTICS",
        "affected_invariant": "PHASE_A_DETERMINISTIC_AUTHENTICATED_OWNER_TO_WRAPPER_PATH_BINDING",
        "previous_closest_edge": "KG_PHASE_A_WRAPPER_AT_AUTHENTICATED_OPERATIONAL_RECOMMISSIONING_DIRECTORY",
        "semantic_difference": "VERIFIED__DIRECTORY_TOKEN_RECOMMISSIONING_VERSUS_COMMISSIONING_ONLY",
        "production_behavior_impact": "VERIFIED__NONE",
        "new_capability_required": "NOT_PROVEN",
        "new_proof_required": "VERIFIED__CORRECTED_KJ_PHASE_A_HARNESS_PATH_BINDING_REPROVEN_BY_KK",
        "convergence_signal": "VERIFIED__KI_OPERATIONAL_FRONTIER_UNCHANGED__KJ_LOCAL_PATH_EDGE_CLOSED",
        "repetition_pressure": "ESTIMATED__REDUCED_BY_SEPARATE_NONRECURSIVE_KK_CORRECTION",
        "verification_amplification_risk": "VERIFIED__CONTAINED__NO_KJ_RETRY_OR_PROOF_SCOPE_EXPANSION",
        "classification_evidence": "VERIFIED__COMMITTED_KJ_AND_KK_SEALED_REDUCTIONS",
        "classification_confidence": "VERIFIED__HIGH",
        "acceptance_requirement_forcing_continuation": "VERIFIED__KI_OPERATIONAL_OBSERVATION_GAP_REQUIRES_FRESH_HUMAN_AUTHORIZED_OBSERVATION",
    }
    value["frontier"] = {
        "last_verified_edge": "FRESH_KL_PHASE_A_PRESENTATION_AND_ALL_REQUIRED_PREFLIGHTS_READY",
        "first_broken_edge": "EXACT_FRESH_KL_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "current_real_blocker": "VERIFIED__EXACT_FRESH_KL_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KL_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "ONLY_AFTER_SEPARATE_EXACT_HUMAN_AUTHORIZATION__SAME_G77_256KL_SPCE_PHASE_B_ONE_CONSUMPTION_ONE_OPERATION_ATTEMPT",
    }
    value["identities"].update(
        {
            "request_sha256": request["request_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "readiness_checkpoint_sha256": readiness["checkpoint_sha256"],
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_sha256": safe_stop["checkpoint_sha256"],
            "checkpoint_file_sha256": sha256_path(safe_stop_path),
            "kk_closure_preflight_sha256": preflight["inner_sha256"],
            "kk_closure_preflight_file_sha256": preflight["file_sha256"],
        }
    )
    value["architecture"] = {
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
    }
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__1__PHASE_A_READINESS_ONLY",
        "new_operational_capability_count": "VERIFIED__0",
        "new_blocker_localized_count": "VERIFIED__0",
        "new_blocker_closed_count": "VERIFIED__0__HUMAN_BARRIER_EXPECTED",
        "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
        "new_classification_result_count": "VERIFIED__0__KI_AND_KK_CLASSIFICATIONS_REAUTHENTICATED",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "EX_17_OF_17__JZ__KB__KD__KF__KG__KH__KI__KJ__KK__GN__FM__ER__P11__SOLE_ROUTE",
        "new_capabilities": "VERIFIED__1__FRESH_KL_PHASE_A_READINESS__NONAUTHORITY__NONOPERATIONAL",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__KL_PHASE_A_READY_AT_HUMAN_BARRIER",
            "project_progress": "VERIFIED__FRESH_KL_COORDINATES_SEALED_AND_PRESENTED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__ALL_PHASE_A_COUNTERS_ZERO__HISTORICAL_AUTHORITY_UNAVAILABLE__ONE_ROUTE_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_AND_EXISTING_PHASE_A_OWNER_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PHASE_A_IS_REPEATED_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
            "cognition_provenance": "VERIFIED__COMMITTED_CANONICAL_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KL_PHASE_A",
            "candidate_capability": "VERIFIED__FRESH_KL_PHASE_A_READINESS_ONLY__EXPIRED_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_BINDING",
            "constitutional_continuation_progress": "VERIFIED__KK_CLOSURE_TO_KL_HUMAN_BARRIER",
        }
    )
    value["fresh_kl_phase_a_presentation_ready"] = "VERIFIED"
    value["human_authority_present"] = False
    value["phase_b_started"] = False
    value["auto_continuable"] = False
    value["human_review_required"] = True
    L.reseal(reduction, "reduction")
    L.write_canonical(reduction_path, reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    kk_result = authenticate_kk_closure()
    ki_result = L.authenticate_ki()
    kf_result = P.authenticate_kf()
    rebound_result = P.rebind_kf_launcher_identity()
    kd_proof = P.E.authenticate_kd_interface_before_presentation()
    kb_result = P.E.K.authenticate_kb()
    jz_result = P.E.K.K.authenticate_jz()
    e05_frontier_result = P.E.K.K.authenticate_e05_frontier()
    P.M.materialize(arguments)
    namespace_result = P.E.augment_namespace_preflight(
        P.E.K.materialize_namespace_preflight(kb_result)
    )
    jz_readiness = P.E.K.K.materialize_jz_readiness(jz_result)
    P.E.K.K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    P.E.K.bind_namespace_into_phase_a(kb_result, namespace_result)
    kd_result = P.E.materialize_kd_preflight(kd_proof)
    P.E.bind_kd_preflight_into_phase_a(kd_result)
    kf_preflight = P.materialize_kf_preflight(kf_result, rebound_result)
    P.bind_kf_into_phase_a(kf_result, kf_preflight)
    ki_preflight = L.materialize_ki_preflight(ki_result)
    L.bind_ki_into_phase_a(ki_result, ki_preflight)
    kk_preflight = materialize_kk_preflight(kk_result)
    bind_kk_into_phase_a(kk_result, kk_preflight)
    P.E.materialize_human_decision_presentation()
    print(KL_TERMINAL)
