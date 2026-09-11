#!/usr/bin/env python3
"""Materialize the nonauthority KJ EXPIRED Phase-A Human barrier.

The committed KG Phase-A owner is adapted only to fresh KJ-local identities
and the remote-ratified KI checkpoint.  KI's sealed frontier is authenticated
and bound into the generated readiness chain.  This module creates no Human
authority and cannot invoke PRE, FM operationally, QEMU, a VM, P11, retry, or
replay.
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
KJ = ROOT / (
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_commissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "6fb11ada9ca2765ccc8e4e97da3a18838a756d6a"
TREE = "65bf8eb5ae02fedcb5ff725bda339b455ebec6b1"
SUBJECT = "G77-256KI reconstruct expired operational frontier"
REMOTE = "git@github.com:Aljosa3/sapianta-ecosystem.git"
KG_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256kg_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KG_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KG_MATERIALIZER_SHA256 = (
    "b187e9e36e5a74aaa6836bfc2f3ae30ad7eacc190125aca07563af4aeaa84da6"
)
KI_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256ki_expired_operational_frontier_assessment_v1"
)
KI_ASSESSMENT = KI_ROOT / (
    "G77_256KI_SPCE_TERMINAL_REPOSITORY_ONLY_ASSESSMENT_V1.json"
)
KI_REPORT = KI_ROOT / "G77_256KI_G48_IMPLEMENTATION_REPORT_V1.md"
KI_ASSESSOR = KI_ROOT / (
    "analysis/G77_256KI_EXPIRED_OPERATIONAL_FRONTIER_ASSESSOR_V1.py"
)
KI_TESTS = KI_ROOT / (
    "tests/test_g77_256ki_expired_operational_frontier_assessment_v1.py"
)
KI_HASHES = {
    KI_ASSESSMENT: "169d3a6feddf327a4e0bcc65927167699c73fe1b4d971c3ef2f730e583589283",
    KI_REPORT: "8b5aa81017a09584589ad62678b88df67ef3da466ca5bc32f5f8dc09c80a2331",
    KI_ASSESSOR: "d92ca24232bcd9cde0a01a352b6880e134f2a02793c0e99600d514355bd5a485",
    KI_TESTS: "b018c8f5574cb4e2f6c391c87fa431b7a2282ad6bf5df31eef26bdda379e3373",
}
KI_INNER_SHA256 = (
    "1d2b0215f1d9158e9a294ed379249e0187b6c455f9908a5fe767fad2a2143613"
)
KI_TERMINAL = (
    "A__EXPIRED_OPERATIONAL_FRONTIER_RECONSTRUCTED__NO_NEW_CAPABILITY_GAP__"
    "ONLY_FRESH_HUMAN_AUTHORIZED_OPERATIONAL_OBSERVATION_REMAINS__"
    "NO_AUTHORITY_CONSUMED__NO_OPERATION__E05_UNCHANGED"
)
KJ_TERMINAL = (
    "A__FRESH_KJ_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)


class KJBarrierError(RuntimeError):
    """One deterministic fail-closed KJ Phase-A error."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KJBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KJBarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KJBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_adapted_kg_materializer() -> ModuleType:
    """Authenticate and namespace-adapt the established Phase-A owner."""

    path = ROOT / KG_MATERIALIZER
    raw = path.read_bytes()
    committed = subprocess.check_output(
        ["git", "show", f"{HEAD}:{KG_MATERIALIZER}"], cwd=ROOT
    )
    if raw != committed or sha256_bytes(raw) != KG_MATERIALIZER_SHA256:
        raise KJBarrierError("COMMITTED_KG_PREAUTHORIZATION_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KG", "KJ").replace("kg", "kj")
    source = source.replace("3bcc78deaeb6821dd71ecdbc9de18628d3ff07de", HEAD)
    source = source.replace("eb06ab5d18fc99d648b7ba20d40269ccf3d0de40", TREE)
    source = source.replace(
        "G77-256KF verify guest harness permission binding repair", SUBJECT
    )
    module = ModuleType("g77_256kj_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


P = load_adapted_kg_materializer()


def authenticate_ki() -> dict[str, Any]:
    """Authenticate the committed KI frontier before any readiness binding."""

    for relative, expected_hash in KI_HASHES.items():
        path = ROOT / relative
        raw = path.read_bytes()
        committed = subprocess.check_output(
            ["git", "show", f"{HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if raw != committed or sha256_bytes(raw) != expected_hash:
            raise KJBarrierError(f"COMMITTED_KI_ARTIFACT_MISMATCH:{relative}")
    envelope = load_canonical(ROOT / KI_ASSESSMENT)
    assessment = envelope.get("assessment")
    if (
        not isinstance(assessment, dict)
        or envelope.get("assessment_sha256") != KI_INNER_SHA256
        or KI_INNER_SHA256 != sha256_bytes(canonical_bytes(assessment))
    ):
        raise KJBarrierError("KI_ASSESSMENT_SEAL_MISMATCH")
    classification = assessment.get("failure_novelty_and_convergence_check", {})
    frontier = assessment.get("frontier", {})
    decision = assessment.get("gap_decision", {})
    baseline = assessment.get("baseline", {})
    architecture = assessment.get("architecture", {})
    if (
        assessment.get("terminal") != KI_TERMINAL
        or assessment.get("vector") != "EXPIRED"
        or classification.get("failure_class") != "PROOF_GAP"
        or classification.get("gap_classification")
        != "OPERATIONAL_OBSERVATION_GAP"
        or frontier.get("last_verified_operational_edge")
        != "EXACT_HUMAN_AUTHORITY_AUTHENTICATED_JZ_BOUND_CONSUMED_ONCE_AND_ONE_NO_NETWORK_VM_BOOT_REACHED_GUEST_CUSTODY_LOAD"
        or frontier.get("first_unverified_operational_edge")
        != "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY_AFTER_KF_REPAIR"
        or frontier.get("current_real_blocker")
        != "NOT_PROVEN__NO_GENUINE_CURRENT_BLOCKER_LOCALIZED"
        or decision.get("minimum_missing_capability")
        != "NOT_PROVEN__NO_NEW_CAPABILITY_GAP_ESTABLISHED__ONLY_FRESH_OPERATIONAL_EXPIRED_OBSERVATION_REMAINS"
        or decision.get("minimum_legal_next_delta")
        != "ONE_FRESH_HUMAN_AUTHORIZED_BOUNDED_EXPIRED_OPERATIONAL_ATTEMPT"
        or decision.get("is_fresh_operational_observation_required") != "VERIFIED"
        or decision.get("is_fresh_human_authority_required_for_successor")
        != "VERIFIED"
        or baseline.get("e05_state") != "VERIFIED__11_OF_18"
        or baseline.get("e05_frontier") != "VERIFIED__7_UNSATISFIED_OF_18"
        or baseline.get("e05_credit") != "VERIFIED__0"
        or baseline.get("expired") != "NOT_PROVEN_OPERATIONALLY"
        or baseline.get("ex_reused") != "VERIFIED__17_OF_17"
        or baseline.get("ex_reconstructed") != "VERIFIED__0"
        or any(assessment.get("operational_counters", {}).values())
        or architecture.get("production_mutation_count") != 0
        or architecture.get("p11_implementation_mutation_count") != 0
        or architecture.get("production_route_before") != 1
        or architecture.get("production_route_after") != 1
    ):
        raise KJBarrierError("KI_FRONTIER_CONTRACT_MISMATCH")
    return {
        "terminal": KI_TERMINAL,
        "assessment_path": KI_ASSESSMENT.as_posix(),
        "assessment_file_sha256": KI_HASHES[KI_ASSESSMENT],
        "assessment_inner_sha256": KI_INNER_SHA256,
        "report_file_sha256": KI_HASHES[KI_REPORT],
        "assessor_file_sha256": KI_HASHES[KI_ASSESSOR],
        "tests_file_sha256": KI_HASHES[KI_TESTS],
        "failure_class": "PROOF_GAP",
        "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
        "last_verified_operational_edge": frontier[
            "last_verified_operational_edge"
        ],
        "first_unverified_operational_edge": frontier[
            "first_unverified_operational_edge"
        ],
        "last_verified_edge": frontier["last_verified_edge"],
        "first_broken_edge": frontier["first_broken_edge"],
        "current_real_blocker": frontier["current_real_blocker"],
        "minimum_missing_capability": decision["minimum_missing_capability"],
        "minimum_legal_next_delta": decision["minimum_legal_next_delta"],
        "e05_state": baseline["e05_state"],
        "e05_frontier": baseline["e05_frontier"],
        "e05_credit": baseline["e05_credit"],
        "expired": baseline["expired"],
        "ex_reused": baseline["ex_reused"],
        "ex_reconstructed": baseline["ex_reconstructed"],
        "ki_operational_counters": "VERIFIED__ALL_ZERO",
        "architecture": "VERIFIED__ZERO_MUTATION__ONE_ROUTE_PRESERVED",
    }


def materialize_ki_preflight(ki: dict[str, Any]) -> dict[str, Any]:
    proof = {
        "schema_id": "G77_256KJ_KI_FRONTIER_PREFLIGHT_V1",
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": P.M.GENERATION,
        "operation_identity": P.M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "ki_authentication": ki,
        "classification_result": "VERIFIED__PROOF_GAP__OPERATIONAL_OBSERVATION_GAP",
        "continuation_decision": "VERIFIED__ONE_FRESH_HUMAN_AUTHORIZED_BOUNDED_EXPIRED_OPERATIONAL_ATTEMPT",
        "human_authority_present": False,
        "historical_authority_available": False,
        "kg_authority_treatment": "TERMINAL__NONTRANSFERABLE__UNAVAILABLE__NOT_COPIED__NOT_CONSUMED",
        "operational_counters": P.M.zero_counters(),
    }
    envelope = {
        "schema_id": "G77_256KJ_KI_FRONTIER_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KJ / "G77_256KJ_KI_FRONTIER_PREFLIGHT_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__KI_OPERATIONAL_FRONTIER_REAUTHENTICATED",
        "scope": "REPOSITORY_ONLY__NONAUTHORITY__NONOPERATIONAL",
    }


def bind_ki_into_phase_a(
    ki: dict[str, Any], preflight: dict[str, Any]
) -> None:
    readiness_path = KJ / "G77_256KJ_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KJ / "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KJ / "G77_256KJ_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KJ / "G77_256KJ_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KJ / "G77_256KJ_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KJ / "G77_256KJ_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = load_canonical(readiness_path)
    readiness["checkpoint"]["ki_frontier_preflight"] = preflight
    readiness["checkpoint"]["human_authority_present"] = False
    readiness["checkpoint"]["phase_b_started"] = False
    reseal(readiness, "checkpoint")
    write_canonical(readiness_path, readiness)

    request = load_canonical(request_path)
    request["request"]["preauthorization"].update(
        {
            "checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
        }
    )
    reseal(request, "request")
    write_canonical(request_path, request)

    presentation_path.write_bytes(
        P.M.GN.render_human_authorization_presentation(request_path)
    )
    gn_result = P.M.GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    equivalence = load_canonical(equivalence_path)
    equivalence["proof"].update(
        {
            "request_file_sha256": sha256_path(request_path),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn_result,
        }
    )
    reseal(equivalence, "proof")
    write_canonical(equivalence_path, equivalence)

    safe_stop = load_canonical(safe_stop_path)
    checkpoint = safe_stop["checkpoint"]
    checkpoint.update(
        {
            "terminal": KJ_TERMINAL,
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "readiness_checkpoint_inner_sha256": readiness[
                "checkpoint_sha256"
            ],
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_file_sha256": sha256_path(equivalence_path),
            "equivalence_inner_sha256": equivalence["proof_sha256"],
            "ki_frontier_preflight": preflight,
            "human_authority_authentication_count": 0,
            "human_authority_present": False,
            "phase_b_started": False,
        }
    )
    reseal(safe_stop, "checkpoint")
    write_canonical(safe_stop_path, safe_stop)

    reduction = load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KJ_TERMINAL
    value["project_state"] = "PHASE_A_READY__STOPPED_AT_HUMAN_BARRIER"
    value["ki_authentication"] = ki
    value["ki_frontier_preflight"] = preflight
    value["owner_results"]["ki_frontier_preflight"] = preflight["result"]
    value["failure_novelty_and_convergence_check"] = {
        "failure_class": "PROOF_GAP",
        "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
        "novelty": "VERIFIED__NOT_NEW__KI_FRONTIER_REAUTHENTICATED",
        "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY",
        "previous_closest_edge": "KF_GUEST_CUSTODY_PERMISSION_CONTRACT_REPOSITORY_VERIFIED_AFTER_KE_REACHED_GUEST_CUSTODY_LOAD",
        "semantic_difference": "VERIFIED__NO_NEW_CONSTITUTIONAL_SEMANTIC_AUTHORITY_PRODUCTION_PATH_OR_OPERATIONAL_DIFFERENCE",
        "production_behavior_impact": "NOT_PROVEN__PHASE_A_IS_NONOPERATIONAL",
        "new_capability_required": "NOT_PROVEN",
        "new_proof_required": "VERIFIED__FRESH_OPERATIONAL_OBSERVATION_ONLY__NO_NEW_REPOSITORY_PROOF",
        "convergence_signal": "VERIFIED__PHASE_A_REUSES_CONVERGED_REPOSITORY_CAPABILITY_CHAIN_AND_STOPS_BEFORE_AUTHORITY",
        "repetition_pressure": "ESTIMATED__HIGH__MULTIPLE_PRIOR_ATTEMPTS_ZERO_E05_CREDIT",
        "verification_amplification_risk": "VERIFIED__POSSIBLE_IF_PHASE_A_IS_REPEATED_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
        "classification_evidence": "VERIFIED__KI_CANONICAL_SEAL_AND_ALL_BOUND_JZ_KB_KD_KF_PHASE_A_PREFLIGHTS",
        "classification_confidence": "VERIFIED__HIGH",
        "acceptance_requirement_forcing_continuation": "VERIFIED__E05_EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY",
    }
    value["operational_frontier"] = {
        "last_verified_operational_edge": ki["last_verified_operational_edge"],
        "first_unverified_operational_edge": ki[
            "first_unverified_operational_edge"
        ],
        "last_verified_edge": ki["last_verified_edge"],
        "first_broken_edge": ki["first_broken_edge"],
        "current_real_blocker": ki["current_real_blocker"],
        "minimum_missing_capability": ki["minimum_missing_capability"],
        "minimum_legal_next_delta": ki["minimum_legal_next_delta"],
    }
    value["frontier"] = {
        "last_verified_edge": "FRESH_KJ_PHASE_A_PRESENTATION_AND_ALL_REQUIRED_PREFLIGHTS_READY",
        "first_broken_edge": "EXACT_FRESH_KJ_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KJ_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "ONLY_AFTER_SEPARATE_EXACT_HUMAN_AUTHORIZATION__SAME_G77_256KJ_SPCE_PHASE_B_ONE_CONSUMPTION_ONE_OPERATION_ATTEMPT",
    }
    value["minimum_delta_decision"] = {
        "minimum_missing_capability": ki["minimum_missing_capability"],
        "minimum_legal_next_delta": ki["minimum_legal_next_delta"],
        "is_fresh_operational_observation_required": "VERIFIED",
        "is_fresh_human_authority_required": "VERIFIED",
        "new_capability_required": "NOT_PROVEN",
        "new_repository_proof_required": "NOT_PROVEN",
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
            "ki_frontier_preflight_sha256": preflight["inner_sha256"],
            "ki_frontier_preflight_file_sha256": preflight["file_sha256"],
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
        "new_verified_capability_count": "VERIFIED__0__PHASE_A_READINESS_EVIDENCE_ONLY",
        "new_operational_capability_count": "VERIFIED__0",
        "new_blocker_localized_count": "VERIFIED__0",
        "new_false_or_superseded_blocker_removed_count": "VERIFIED__0__KI_RESULT_REAUTHENTICATED",
        "new_classification_result_count": "VERIFIED__0__KI_CLASSIFICATION_REAUTHENTICATED",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "EX_17_OF_17__KI__KH__JZ__KB__KD__KF__KG_PHASE_A_PATTERN__GN__FM__ER__P11__SOLE_ROUTE",
        "new_capabilities": "VERIFIED__0__FRESH_KJ_PHASE_A_ARTIFACTS_ARE_READINESS_EVIDENCE_NOT_OPERATIONAL_CAPABILITY",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__KJ_PHASE_A_READY_AT_HUMAN_BARRIER",
            "project_progress": "VERIFIED__FRESH_KJ_COMMISSIONING_COORDINATES_SEALED_AND_PRESENTED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__ALL_PHASE_A_COUNTERS_ZERO__HISTORICAL_AUTHORITY_UNAVAILABLE__ONE_ROUTE_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_AND_EXISTING_PHASE_A_OWNER_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PHASE_A_IS_REPEATED_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
            "cognition_provenance": "VERIFIED__COMMITTED_CANONICAL_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KJ_PHASE_A",
            "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_BINDING",
            "constitutional_continuation_progress": "VERIFIED__KI_OPERATIONAL_OBSERVATION_GAP_TO_KJ_HUMAN_BARRIER",
        }
    )
    value["ccwim"].update(
        {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        }
    )
    value["periodic_metrics"] = {
        "aigol_codex_work_share": "NOT_MEASURED__NO_FORMAL_ATTRIBUTION_INSTRUMENT",
        "prompt_context_reuse_ratio": "NOT_MEASURED__NO_FORMAL_TOKEN_ATTRIBUTION_INSTRUMENT",
        "token_benchmark": "NOT_MEASURED__PROVIDER_AND_CONTEXT_TELEMETRY_EXCLUDED",
        "lcrr": "NOT_MEASURED__NO_FORMAL_COST_BASELINE_OR_DENOMINATOR",
        "full_ccwim": "NOT_APPLICABLE__COMPACT_CCWIM_SUFFICIENT",
    }
    value["hac_hai_hae"] = (
        "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
    )
    value["fresh_kj_phase_a_presentation_ready"] = "VERIFIED"
    value["human_authority_present"] = False
    value["phase_b_started"] = False
    value["auto_continuable"] = False
    value["human_review_required"] = True
    reseal(reduction, "reduction")
    write_canonical(reduction_path, reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    ki_result = authenticate_ki()
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
    ki_preflight = materialize_ki_preflight(ki_result)
    bind_ki_into_phase_a(ki_result, ki_preflight)
    P.E.materialize_human_decision_presentation()
    print(KJ_TERMINAL)
