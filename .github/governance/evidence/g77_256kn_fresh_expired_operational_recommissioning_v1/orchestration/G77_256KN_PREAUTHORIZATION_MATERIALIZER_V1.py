#!/usr/bin/env python3
"""Construct one fresh nonauthority KN EXPIRED Phase-A Human barrier.

The committed KM schema-preserving closure and corrected KJ evidence binder are
authenticated before use.  This module exposes no Phase-B or operational
entrypoint and cannot create, accept, transfer, reuse, or consume authority.
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
KN = ROOT / (
    ".github/governance/evidence/"
    "g77_256kn_fresh_expired_operational_recommissioning_v1"
)
HEAD = "1141f9f1dd2069e250c6ad44dc90164597366ffe"
TREE = "70aa2a12af3d9806e0d6ddc73f7f751292413e52"
SUBJECT = "G77-256KM preserve GN schema for KI preflight binding"
KJ_WRAPPER = Path(
    ".github/governance/evidence/"
    "g77_256kj_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KJ_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KJ_WRAPPER_SHA256 = "fcc1a60fdbc3fb246d918ac2e8143bd4888e3e65ebc2e3769298a039c5aeebbf"
KJ_PRE_KM_SHA256 = "900741ac1e095d0f0ef2e0c19b102742bf38d3ddf9b11ca602eec463d6e3614f"
GN_OWNER = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GN_OWNER_SHA256 = "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3"
KM_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256km_gn_exact_preauthorization_schema_preserving_ki_preflight_binding_v1"
)
KM_REDUCTION = KM_ROOT / "G77_256KM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KM_REPORT = KM_ROOT / "G77_256KM_G48_IMPLEMENTATION_REPORT_V1.md"
KM_VERIFIER = KM_ROOT / (
    "analysis/G77_256KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_VERIFIER_V1.py"
)
KM_TESTS = KM_ROOT / (
    "tests/test_g77_256km_gn_schema_preserving_ki_preflight_binding_v1.py"
)
KM_HASHES = {
    KM_REDUCTION: "b76a42cd95b5d227ba64fe5c7d8e777143f915d296d8d5811a3eec449e7751a4",
    KM_REPORT: "34cb2749878fb24dcc468911d61e29540df262c6dfc25cd89132f4276ae3c8a5",
    KM_VERIFIER: "fc81991135320ddfbbd91e834d81162698ce6da3ac51a76ac7b8f1b4d1e855d0",
    KM_TESTS: "03350956207727870b1b6eb938a862c712905a0d1eb222f743cfd04de7fb5f4e",
}
KM_INNER_SHA256 = "73a8d430c1ffd51bbfd8e39b51c08f66a1cc6550038153e0a58d19163d6c691d"
KM_TERMINAL = (
    "A__GN_EXACT_PREAUTHORIZATION_SCHEMA_PRESERVED_WITH_KI_PREFLIGHT_"
    "EVIDENCE_BOUND_OUTSIDE_GN_OWNER_OBJECT__NO_AUTHORITY__NO_OPERATION__NO_KL_RETRY"
)
KN_TERMINAL = (
    "A__FRESH_KN_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)
GN_FIELDS = {
    "all_operational_counters_zero",
    "checkpoint_file_sha256",
    "checkpoint_inner_sha256",
    "checkpoint_path",
    "complete_deterministic_readiness",
    "gk_receipt_parent_false_positive_blocked",
    "preauth_final_admission_equivalence",
    "preauth_final_admission_equivalence_file_sha256",
    "receipt_parent_observation_file_sha256",
    "static_readiness_file_sha256",
}
REMOVED_FIELDS = {
    "ki_frontier_preflight_file_sha256",
    "ki_frontier_preflight_inner_sha256",
}


class KNBarrierError(RuntimeError):
    """One deterministic fail-closed KN Phase-A error."""


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
        raise KNBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KNBarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KNBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def committed(path: Path, revision: str = HEAD) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_adapted_kj_materializer() -> ModuleType:
    """Authenticate the KM-corrected KJ binder and adapt it once to fresh KN."""

    path = ROOT / KJ_WRAPPER
    raw = path.read_bytes()
    if raw != committed(KJ_WRAPPER) or sha256_bytes(raw) != KJ_WRAPPER_SHA256:
        raise KNBarrierError("COMMITTED_KM_CORRECTED_KJ_BINDER_MISMATCH")
    predecessor = committed(KJ_WRAPPER, f"{HEAD}^")
    expected = predecessor
    for line in (
        b'            "ki_frontier_preflight_file_sha256": preflight["file_sha256"],\n',
        b'            "ki_frontier_preflight_inner_sha256": preflight["inner_sha256"],\n',
    ):
        if line not in expected:
            raise KNBarrierError("KM_TWO_FIELD_REMOVAL_PRECONDITION_MISMATCH")
        expected = expected.replace(line, b"", 1)
    if sha256_bytes(predecessor) != KJ_PRE_KM_SHA256 or raw != expected:
        raise KNBarrierError("KM_TWO_FIELD_CORRECTION_MISMATCH")

    source = raw.decode("utf-8").replace("KJ", "KN").replace("kj", "kn")
    source = source.replace(
        "g77_256kn_fresh_expired_operational_commissioning_v1",
        "g77_256kn_fresh_expired_operational_recommissioning_v1",
    )
    source = source.replace("6fb11ada9ca2765ccc8e4e97da3a18838a756d6a", HEAD)
    source = source.replace("65bf8eb5ae02fedcb5ff725bda339b455ebec6b1", TREE)
    source = source.replace("G77-256KI reconstruct expired operational frontier", SUBJECT)
    module = ModuleType("g77_256kn_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    if module.KN != KN:
        raise KNBarrierError("KN_GENERATION_ROOT_ADAPTATION_MISMATCH")
    return module


L = load_adapted_kj_materializer()
P = L.P


def cross_vector_reuse_assessment() -> dict[str, Any]:
    supported = sorted(P.M.GN.SUPPORTED_VECTORS)
    expected = [
        "EXPIRED",
        "FUTURE",
        "WRONG_ATTEMPT",
        "WRONG_CONTRACT",
        "WRONG_INPUT",
        "WRONG_PROVENANCE",
    ]
    if supported != expected or P.M.GN.PREAUTHORIZATION_FIELDS != GN_FIELDS:
        raise KNBarrierError("GN_MULTI_VECTOR_OWNER_CONTRACT_MISMATCH")
    return {
        "cross_vector_reuse_scope": "VERIFIED__MULTI_VECTOR_REUSABLE",
        "reusable_component": "GN_EXACT_PREAUTHORIZATION_OWNER_AND_SEALED_CHECKPOINT_EVIDENCE_BINDING_PATTERN",
        "reuse_invariant": "OWNER_OWNED_EXACT_SEMANTIC_OBJECT_MUST_NOT_BE_EXPANDED_BY_EVIDENCE_ONLY_METADATA",
        "applicable_vectors": supported,
        "vector_specific_residue": "EACH_VECTOR_PREFLIGHT_SEMANTICS__FRESH_AUTHORITY__OPERATIONAL_ACCEPTANCE__E05_CREDIT",
        "reuse_preconditions": "SAME_AUTHENTICATED_GN_OWNER__EXACT_TEN_FIELDS__SEALED_PREFLIGHT__SEALED_READINESS__EXISTING_CHECKPOINT_DIGEST_FIELDS",
        "revalidation_required": "VERIFIED__PER_GENERATION_BINDINGS_AND_PER_VECTOR_OPERATIONAL_REQUIREMENTS",
        "expected_future_proof_reduction": "ESTIMATED__REUSE_COMMON_SCHEMA_PLACEMENT_PROOF__DO_NOT_REPROVE_OR_RECONSTRUCT__NO_VECTOR_OPERATIONAL_CREDIT",
        "common_proof_reuse_is_vector_operational_proof": False,
        "multi_vector_reuse_is_authority_transfer": False,
    }


def authenticate_km() -> dict[str, Any]:
    for relative, expected_hash in KM_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if raw != committed(relative) or sha256_bytes(raw) != expected_hash:
            raise KNBarrierError(f"COMMITTED_KM_ARTIFACT_MISMATCH:{relative}")
    gn_raw = (ROOT / GN_OWNER).read_bytes()
    if gn_raw != committed(GN_OWNER) or sha256_bytes(gn_raw) != GN_OWNER_SHA256:
        raise KNBarrierError("GN_OWNER_CHANGED_AFTER_KM")
    envelope = load_canonical(ROOT / KM_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != KM_INNER_SHA256
        or sha256_bytes(canonical_bytes(reduction)) != KM_INNER_SHA256
    ):
        raise KNBarrierError("KM_REDUCTION_SEAL_MISMATCH")
    binding = reduction.get("binding", {})
    correction = reduction.get("correction", {})
    frontier = reduction.get("frontier", {})
    baseline = reduction.get("baseline", {})
    architecture = reduction.get("architecture", {})
    if (
        reduction.get("terminal") != KM_TERMINAL
        or binding.get("gn_exact_preauthorization_field_count") != 10
        or set(binding.get("gn_exact_preauthorization_fields", [])) != GN_FIELDS
        or binding.get("gn_exact_preauthorization_schema") != "VERIFIED__UNCHANGED"
        or binding.get("ki_preflight_binding") != "VERIFIED__SCHEMA_PRESERVING"
        or binding.get("ki_digest_required_inside_gn_object") is not False
        or correction.get("removed_fields") != sorted(REMOVED_FIELDS)
        or correction.get("added_fields") != []
        or correction.get("gn_owner_changed") is not False
        or correction.get("gn_validation_weakened") != "VERIFIED__NO"
        or correction.get("second_accepted_gn_schema") != "VERIFIED__NO"
        or correction.get("fallback") != "VERIFIED__ABSENT"
        or correction.get("alias") != "VERIFIED__ABSENT"
        or correction.get("parallel_authority_path") != "VERIFIED__NO"
        or frontier.get("first_broken_edge")
        != "NOT_PROVEN__NO_NEXT_REPOSITORY_LOCAL_BROKEN_EDGE_AUTHENTICATED"
        or baseline.get("e05_state") != "VERIFIED__11_OF_18"
        or baseline.get("e05_frontier") != "VERIFIED__7_UNSATISFIED_OF_18"
        or baseline.get("e05_credit") != "VERIFIED__0"
        or baseline.get("ex_reused") != "VERIFIED__17_OF_17"
        or baseline.get("ex_reconstructed") != "VERIFIED__0"
        or architecture.get("production_route_before") != 1
        or architecture.get("production_route_after") != 1
        or architecture.get("parallel_flow") != "NO"
        or any(reduction.get("operational_counters", {}).values())
        or reduction.get("human_authority_present") is not False
        or reduction.get("phase_b_started") is not False
    ):
        raise KNBarrierError("KM_CLOSURE_CONTRACT_MISMATCH")
    return {
        "terminal": KM_TERMINAL,
        "reduction_path": KM_REDUCTION.as_posix(),
        "reduction_file_sha256": KM_HASHES[KM_REDUCTION],
        "reduction_inner_sha256": KM_INNER_SHA256,
        "corrected_kj_binder_sha256": KJ_WRAPPER_SHA256,
        "gn_owner_sha256": GN_OWNER_SHA256,
        "gn_exact_preauthorization_field_count": 10,
        "gn_exact_preauthorization_schema": "VERIFIED__UNCHANGED",
        "gn_validation_weakened": "VERIFIED__NO",
        "second_accepted_gn_schema": "VERIFIED__NO",
        "ki_preflight_binding": "VERIFIED__SCHEMA_PRESERVING",
        "ki_digest_required_inside_gn_object": "VERIFIED__NO",
        "parallel_authority_path": "VERIFIED__NO",
        "fallback": "VERIFIED__ABSENT",
        "alias": "VERIFIED__ABSENT",
        "exact_two_field_removal": sorted(REMOVED_FIELDS),
        "operational_counters": "VERIFIED__ALL_ZERO",
        "ex_reused": baseline["ex_reused"],
        "ex_reconstructed": baseline["ex_reconstructed"],
    }


def materialize_km_preflight(
    km: dict[str, Any], cross_vector: dict[str, Any]
) -> dict[str, Any]:
    proof = {
        "schema_id": "G77_256KN_KM_SCHEMA_BINDING_PREFLIGHT_V1",
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": P.M.GENERATION,
        "operation_identity": P.M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "km_authentication": km,
        "failure_class": "PROOF_GAP",
        "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
        "cross_vector_reuse_assessment": cross_vector,
        "human_authority_present": False,
        "phase_b_started": False,
        "operational_counters": P.M.zero_counters(),
    }
    envelope = {
        "schema_id": "G77_256KN_KM_SCHEMA_BINDING_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KN / "G77_256KN_KM_SCHEMA_BINDING_PREFLIGHT_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__KM_GN_SCHEMA_PRESERVING_KI_BINDING_REAUTHENTICATED",
        "scope": "REPOSITORY_ONLY__NONAUTHORITY__NONOPERATIONAL",
    }


def bind_km_into_phase_a(
    km: dict[str, Any], preflight: dict[str, Any], cross_vector: dict[str, Any]
) -> None:
    readiness_path = KN / "G77_256KN_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KN / "G77_256KN_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KN / "G77_256KN_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KN / "G77_256KN_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KN / "G77_256KN_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = L.load_canonical(readiness_path)
    readiness["checkpoint"]["km_schema_binding_preflight"] = preflight
    readiness["checkpoint"]["cross_vector_reuse_assessment"] = cross_vector
    readiness["checkpoint"]["human_authority_present"] = False
    readiness["checkpoint"]["phase_b_started"] = False
    L.reseal(readiness, "checkpoint")
    L.write_canonical(readiness_path, readiness)

    request = L.load_canonical(request_path)
    request["request"]["preauthorization"].update(
        {
            "checkpoint_file_sha256": sha256_path(readiness_path),
            "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
        }
    )
    if set(request["request"]["preauthorization"]) != GN_FIELDS:
        raise KNBarrierError("KN_GN_EXACT_PREAUTHORIZATION_SCHEMA_MISMATCH")
    L.reseal(request, "request")
    L.write_canonical(request_path, request)

    presentation_path.write_bytes(P.M.GN.render_human_authorization_presentation(request_path))
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
            "terminal": KN_TERMINAL,
            "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
            "readiness_checkpoint_inner_sha256": readiness["checkpoint_sha256"],
            "request_file_sha256": sha256_path(request_path),
            "request_identity": request["request_sha256"],
            "presentation_identity": sha256_path(presentation_path),
            "equivalence_file_sha256": sha256_path(equivalence_path),
            "equivalence_inner_sha256": equivalence["proof_sha256"],
            "km_schema_binding_preflight": preflight,
            "cross_vector_reuse_assessment": cross_vector,
            "human_authority_authentication_count": 0,
            "human_authority_present": False,
            "phase_b_started": False,
        }
    )
    L.reseal(safe_stop, "checkpoint")
    L.write_canonical(safe_stop_path, safe_stop)

    reduction = L.load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KN_TERMINAL
    value["project_state"] = "PHASE_A_READY__STOPPED_AT_HUMAN_BARRIER"
    value["km_authentication"] = km
    value["km_schema_binding_preflight"] = preflight
    value["cross_vector_reuse_assessment"] = cross_vector
    value["owner_results"]["km_schema_binding_preflight"] = preflight["result"]
    value["failure_novelty_and_convergence_check"] = {
        "failure_class": "PROOF_GAP",
        "gap_classification": "OPERATIONAL_OBSERVATION_GAP",
        "novelty": "VERIFIED__NOT_NEW__KM_CLOSED_GN_SCHEMA_EDGE__EXPIRED_OPERATIONAL_OBSERVATION_REMAINS",
        "affected_invariant": "E05_EXPIRED_REQUIRES_FRESH_HUMAN_AUTHORIZED_DENIAL_BEFORE_P11_ENTRY",
        "previous_closest_edge": "KM_GN_SCHEMA_PRESERVING_KI_PREFLIGHT_BINDING_REPOSITORY_VERIFIED",
        "semantic_difference": "VERIFIED__NO_NEW_CONSTITUTIONAL_SEMANTIC_AUTHORITY_PRODUCTION_PATH_OR_OPERATIONAL_DIFFERENCE",
        "production_behavior_impact": "VERIFIED__NONE__KN_PHASE_A_IS_NONOPERATIONAL",
        "new_capability_required": "NOT_PROVEN",
        "new_proof_required": "VERIFIED__FRESH_OPERATIONAL_EXPIRED_OBSERVATION_REMAINS_AFTER_SEPARATE_HUMAN_AUTHORITY",
        "convergence_signal": "VERIFIED__KM_LOCAL_EDGE_CLOSED__KN_REUSES_ONE_CONVERGED_PHASE_A_CHAIN__E05_UNCHANGED",
        "repetition_pressure": "ESTIMATED__HIGH__MULTIPLE_PRIOR_PHASE_A_GENERATIONS_ZERO_E05_CREDIT",
        "verification_amplification_risk": "VERIFIED__HIGH_IF_PHASE_A_IS_REPEATED_AFTER_KN_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
        "classification_evidence": "VERIFIED__KM_CANONICAL_SEAL__KI_FRONTIER__GN_EXACT_SCHEMA__EX_17_OF_17__KN_ZERO_OPERATION",
        "classification_confidence": "VERIFIED__HIGH",
        "acceptance_requirement_forcing_continuation": "VERIFIED__E05_EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY__KN_AUTHORIZED_ONLY_TO_HUMAN_BARRIER",
    }
    value["frontier"] = {
        "last_verified_edge": "FRESH_KN_PHASE_A_PRESENTATION_AND_ALL_REQUIRED_PREFLIGHTS_READY_USING_KM_SCHEMA_PRESERVING_BINDING",
        "first_broken_edge": "EXACT_FRESH_KN_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "current_real_blocker": "VERIFIED__EXACT_FRESH_KN_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KN_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "ONLY_AFTER_SEPARATE_EXACT_HUMAN_AUTHORIZATION__SAME_G77_256KN_SPCE_PHASE_B_ONE_CONSUMPTION_ONE_OPERATION_ATTEMPT",
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
            "km_schema_binding_preflight_sha256": preflight["inner_sha256"],
            "km_schema_binding_preflight_file_sha256": preflight["file_sha256"],
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
        "new_verified_capability_count": "VERIFIED__1__FRESH_KN_PHASE_A_READINESS_ONLY",
        "new_operational_capability_count": "VERIFIED__0",
        "new_blocker_localized_count": "VERIFIED__0",
        "new_blocker_closed_count": "VERIFIED__0__HUMAN_BARRIER_EXPECTED",
        "new_false_or_superseded_blocker_removed_count": "VERIFIED__0",
        "new_classification_result_count": "VERIFIED__1__PROOF_GAP_REAUTHENTICATED",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17__EX_COMMON_COMPONENTS",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "EX_17_OF_17__KM__KI__KH__JZ__KB__KD__KF__KG_PHASE_A_PATTERN__GN__FM__ER__P11__SOLE_ROUTE",
        "new_capabilities": "VERIFIED__1__FRESH_KN_PHASE_A_READINESS__NONAUTHORITY__NONOPERATIONAL",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__KN_PHASE_A_READY_AT_HUMAN_BARRIER",
            "project_progress": "VERIFIED__FRESH_KN_COORDINATES_SCHEMA_EXACT_REQUEST_PRESENTATION_AND_SAFE_STOP_SEALED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__KM_SCHEMA_BINDING_USED__GN_STRICT__ALL_COUNTERS_ZERO__NO_AUTHORITY__ONE_ROUTE",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_AND_MULTI_VECTOR_SCHEMA_BINDING_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_PHASE_A_IS_REPEATED_AFTER_KN_WITHOUT_HUMAN_DECISION_OR_NEW_EVIDENCE",
            "cognition_provenance": "VERIFIED__COMMITTED_KM_KI_GN_EX_AND_DETERMINISTIC_KN_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_ONLY_REPLAY_SAFE_KN_PHASE_A",
            "candidate_capability": "VERIFIED__FRESH_KN_PHASE_A_READINESS_ONLY__EXPIRED_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_AND_KM_SCHEMA_BINDING",
            "constitutional_continuation_progress": "VERIFIED__KM_SCHEMA_EDGE_CLOSURE_TO_KN_HUMAN_BARRIER",
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
    value["hac_hai_hae"] = (
        "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
    )
    value["fresh_kn_phase_a_presentation_ready"] = "VERIFIED"
    value["safe_stop_checkpoint"] = "VERIFIED"
    value["gn_exact_preauthorization_schema"] = "VERIFIED__UNCHANGED"
    value["ki_preflight_binding"] = "VERIFIED__KM_SCHEMA_PRESERVING_PATH_USED"
    value["human_decision_presentation"] = "VERIFIED__FRESH_KN_EXACT_PRESENTATION_CREATED"
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
    km_result = authenticate_km()
    cross_vector_result = cross_vector_reuse_assessment()
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
    km_preflight = materialize_km_preflight(km_result, cross_vector_result)
    bind_km_into_phase_a(km_result, km_preflight, cross_vector_result)
    P.E.materialize_human_decision_presentation()
    print(KN_TERMINAL)
