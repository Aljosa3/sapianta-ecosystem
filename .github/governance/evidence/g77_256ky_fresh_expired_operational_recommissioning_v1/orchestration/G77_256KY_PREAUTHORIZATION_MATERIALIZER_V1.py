#!/usr/bin/env python3
"""Materialize the fresh current-HEAD KY EXPIRED Human-decision barrier only.

The adapter reuses the committed KW/KN Phase-A owner chain, authenticates the
committed KX repository repair, and stops before Human authority or operation.
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
KY = ROOT / (
    ".github/governance/evidence/"
    "g77_256ky_fresh_expired_operational_recommissioning_v1"
)
HEAD = "d19208af9d9633c764838399e5a86a441e9386ef"
TREE = "40207213a9359f536f9e6380c113c67f5ac6ab3f"
SUBJECT = "G77-256KX bind runtime export custody traversal"
KW_HEAD = "681538ccd9b6faaeebff15d96881134eaef00d7e"
KW_TREE = "53164b7f60d982727bebd9a5c77d5688ee283ade"
KW_SUBJECT = "G77-256KV localize fresh current-head authority lifecycle"
KW_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256kw_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KW_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KW_MATERIALIZER_SHA256 = (
    "db8b64f59c291a4be12cc660ee2e624c1d50b253446fc0e2c7f07db7a79adca6"
)
KX_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kx_existing_fm_runtime_export_custody_permission_binding_repair_v1/"
    "G77_256KX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
KX_REDUCTION_SHA256 = (
    "fee33a1d275fbfbbb6038ea63c5ec9b0da6d4af67f93d768c5ad7ed9f959cbcc"
)
KX_FM_LAUNCHER_SHA256 = (
    "76c82e3701abbd14e9003f356ed326c7bc179935198a060910118d8c40d92aa6"
)
TERMINAL = (
    "A__KY_FRESH_CURRENT_HEAD_EXPIRED_HUMAN_DECISION_PRESENTATION_READY__"
    "NO_HUMAN_AUTHORITY__NO_HANDOFF__NO_BINDING__NO_CONSUMPTION__"
    "NO_PHASE_B__NO_OPERATION"
)
PURPOSE = (
    "Perform exactly one future fresh Human-authorized EXPIRED operational "
    "attempt after the KX runtime-export custody repair, to observe whether "
    "EXPIRED is denied before P11 entry."
)


class KYBarrierError(RuntimeError):
    """One deterministic fail-closed KY Phase-A error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed(path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HEAD}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise KYBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KYBarrierError(f"MISSING_INNER:{inner}")
    if envelope.get(f"{inner}_sha256") != sha256_bytes(canonical_bytes(value)):
        raise KYBarrierError(f"INNER_SEAL_MISMATCH:{inner}")
    return value


def load_adapted_kw_materializer() -> ModuleType:
    raw = (ROOT / KW_MATERIALIZER).read_bytes()
    if raw != committed(KW_MATERIALIZER) or sha256_bytes(raw) != KW_MATERIALIZER_SHA256:
        raise KYBarrierError("COMMITTED_KW_PHASE_A_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KW", "KY").replace("kw", "ky")
    source = source.replace(KW_HEAD, HEAD).replace(KW_TREE, TREE)
    source = source.replace(KW_SUBJECT, SUBJECT)
    module = ModuleType("g77_256ky_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(ROOT / KW_MATERIALIZER), "exec"), module.__dict__)
    if module.KY != KY:
        raise KYBarrierError("KY_GENERATION_ROOT_ADAPTATION_MISMATCH")
    return module


B = load_adapted_kw_materializer()
# Public verification aliases preserve the authenticated KW owner interface.
W = B.W
DU_VALIDATOR = B.DU_VALIDATOR
DU_VALIDATOR_SHA256 = B.DU_VALIDATOR_SHA256
load_authenticated_module = B.load_authenticated_module


def authenticate_kx() -> dict[str, Any]:
    path = ROOT / KX_REDUCTION
    raw = path.read_bytes()
    if raw != committed(KX_REDUCTION) or sha256_bytes(raw) != KX_REDUCTION_SHA256:
        raise KYBarrierError("COMMITTED_KX_REDUCTION_MISMATCH")
    reduction = verify_seal(load_canonical(path), "reduction")
    kw = reduction.get("kw_terminal_authentication", {})
    contract = reduction.get("owner_and_minimum_permission_contract", {})
    if (
        reduction.get("terminal")
        != "A__KX_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_BINDING_REPAIR_VERIFIED__REPOSITORY_ONLY__NO_OPERATION"
        or kw.get("terminal")
        != "I__KW_PROVIDER_RECOVERY__NEW_RUNTIME_EXPORT_CUSTODY_EDGE_FOUND__CLASSIFIED__FAIL_CLOSED__NO_RETRY"
        or kw.get("authority", {}).get("state")
        != "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
        or kw.get("operational_counters", {}).get("authority_consumption_count") != 1
        or kw.get("operational_counters", {}).get("operation_attempt_count") != 1
        or any(
            kw.get("operational_counters", {}).get(key) != 0
            for key in ("retry_count", "repair_retry_count", "replay_count")
        )
        or contract.get("after")
        != "PRIVATE_CONSTRUCTION_0700_THEN_SEARCH_ONLY_PRESENTATION_0701"
        or contract.get("context_write") != "DENIED"
        or contract.get("production_route_before") != 1
        or contract.get("production_route_after") != 1
        or reduction.get("e05", {}).get("after") != "VERIFIED__11_OF_18"
        or reduction.get("ex", {}).get("ex_reused") != "VERIFIED__17_OF_17"
    ):
        raise KYBarrierError("KX_OR_KW_CONTRACT_MISMATCH")
    fm = B.W.P.M.FM
    if (
        fm.RUNTIME_EXPORT_ROOT_CONSTRUCTION_MODE != 0o700
        or fm.RUNTIME_EXPORT_ROOT_PRESENTATION_MODE != 0o701
    ):
        raise KYBarrierError("CURRENT_FM_RUNTIME_EXPORT_REPAIR_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "reduction_path": KX_REDUCTION.as_posix(),
        "reduction_file_sha256": KX_REDUCTION_SHA256,
        "kw_terminal": kw["terminal"],
        "kw_authority": kw["authority"]["state"],
        "kw_authority_consumption_count": 1,
        "kw_operation_attempt_count": 1,
        "kw_retry_count": 0,
        "kw_repair_retry_count": 0,
        "kw_replay_count": 0,
        "repair": "VERIFIED__EXISTING_FM_OWNER__0700_CONSTRUCTION__0701_PRESENTATION__CONTEXT_READ_WITHOUT_WRITE",
        "scope": "REPOSITORY_ONLY__NO_POST_REPAIR_OPERATIONAL_PROOF",
    }


def exact_operational_counters() -> dict[str, int]:
    return B.exact_operational_counters()


def rebind_kx_launcher_identity() -> dict[str, Any]:
    """Advance inherited pre-KF owner expectations to the committed KX owner."""

    owner = B.W.P
    bindings = (
        (owner.E.K.KB_HASHES, owner.E.K.FM_LAUNCHER, "KB_CURRENT_LAUNCHER"),
        (owner.E.K.K.EXPECTED_HASHES, owner.E.K.K.FM_PATH, "COMMISSIONING_FM_OWNER"),
        (owner.E.K.K.A.JX_HASHES, owner.E.K.K.A.FM_PATH, "JX_FM_LAUNCHER"),
    )
    rebound: list[str] = []
    for mapping, key, label in bindings:
        if mapping.get(key) != owner.PRE_KF_FM_LAUNCHER_SHA256:
            raise KYBarrierError(f"UNEXPECTED_INHERITED_LAUNCHER_BINDING:{label}")
        mapping[key] = KX_FM_LAUNCHER_SHA256
        rebound.append(label)
    if sha256_path(ROOT / owner.FM_LAUNCHER) != KX_FM_LAUNCHER_SHA256:
        raise KYBarrierError("COMMITTED_KX_LAUNCHER_IDENTITY_MISMATCH")
    return {
        "classification": "EXACT_KX_SUCCESSOR_IDENTITY_REBINDING",
        "kx_launcher_sha256": KX_FM_LAUNCHER_SHA256,
        "rebound_expectation_count": len(rebound),
        "rebound_expectations": rebound,
        "new_owner": False,
        "new_route": False,
    }


def bind_kx_frontier(kx: dict[str, Any], cross_vector: dict[str, Any]) -> None:
    safe_path = KY / "G77_256KY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KY / "G77_256KY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
    safe = B.W.load_canonical(safe_path)
    safe["checkpoint"].update(
        {
            "terminal": TERMINAL,
            "human_decision_presentation_status": "VERIFIED__READY_FOR_HUMAN_DECISION",
            "human_authority_status": "NOT_PROVEN__NO_FRESH_KY_HUMAN_ACT_YET",
            "human_authority_handoff_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "preconsumption_binding_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "authority_consumption_count": 0,
            "operation_attempt_count": 0,
        }
    )
    B.W.reseal(safe, "checkpoint")
    B.W.write_canonical(safe_path, safe)

    envelope = B.W.load_canonical(reduction_path)
    value = envelope["reduction"]
    value["identities"]["checkpoint_sha256"] = safe["checkpoint_sha256"]
    value["identities"]["checkpoint_file_sha256"] = sha256_path(safe_path)
    value.update(
        {
            "terminal": TERMINAL,
            "kx_repair_authentication": kx,
            "failure_novelty_and_convergence_check": {
                "failure_class": "PROOF_GAP",
                "novelty": "VERIFIED__NO_NEW_CAPABILITY_EDGE__KX_REPAIRED_THE_KW_EDGE_REPOSITORY_ONLY",
                "affected_invariant": "GUEST_CUSTODY_MUST_LOAD_SEALED_OPERATION_CONTEXT_BEFORE_GATE_WITHOUT_WRITE_AUTHORITY",
                "previous_closest_edge": "KW_RUNTIME_EXPORT_ROOT_0700_CUSTODY_TRAVERSAL_FAILURE",
                "semantic_difference": "VERIFIED__KX_REPOSITORY_CAPABILITY_EXISTS_BUT_POST_REPAIR_GUEST_LOAD_AND_EXPIRED_DENIAL_ARE_UNOBSERVED",
                "production_behavior_impact": "VERIFIED__NONE__KY_PHASE_A_ONLY",
                "new_capability_required": "VERIFIED__NO",
                "new_proof_required": "VERIFIED__ONE_FRESH_HUMAN_AUTHORIZED_POST_KX_OPERATIONAL_OBSERVATION",
                "convergence_signal": "VERIFIED__KW_EDGE_CLOSED_BY_KX_AND_FRONTIER_RETURNS_TO_OPERATIONAL_OBSERVATION",
                "repetition_pressure": "VERIFIED__HIGH__E05_REMAINS_11_OF_18_ACROSS_MULTIPLE_GENERATIONS",
                "verification_amplification_risk": "ESTIMATED__HIGH_IF_PHASE_A_PROOF_IS_REPEATED_WITHOUT_ONE_BOUNDED_OPERATIONAL_OBSERVATION",
                "classification_evidence": "VERIFIED__COMMITTED_KW_TERMINAL__COMMITTED_KX_SEALED_REPAIR__CURRENT_FM_0700_TO_0701_OWNER",
                "classification_confidence": "VERIFIED__HIGH",
                "acceptance_requirement_forcing_continuation": "VERIFIED__EXPIRED_REMAINS_NOT_PROVEN_OPERATIONALLY__E05_REMAINS_11_OF_18",
            },
            "cross_vector_reuse_assessment": {
                **cross_vector,
                "cross_vector_reuse_scope": "VERIFIED__MULTI_VECTOR_REUSABLE",
                "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
                "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_MUST_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
                "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
                "vector_specific_residue": "FRESH_EXPIRED_HUMAN_ACT__POST_KX_CONTEXT_LOAD__EXPIRED_DENIAL_BEFORE_P11_ENTRY",
                "reuse_preconditions": "EXACT_GENERATION_VECTOR_HEAD_TREE_AND_FRESH_HUMAN_SOURCE",
                "revalidation_required": "VERIFIED__PER_GENERATION_AND_PER_VECTOR",
                "expected_future_proof_reduction": "ESTIMATED__COMMON_AUTHORITY_AND_RUNTIME_EXPORT_INFRASTRUCTURE_REUSED__NO_VECTOR_CREDIT_TRANSFER",
                "fm_runtime_export_presentation": "VERIFIED__COMMON_E05_INFRASTRUCTURE",
                "authority_transfer": "VERIFIED__NO",
                "e05_credit_transfer": "VERIFIED__NO",
                "operational_proof_transfer": "VERIFIED__NO",
            },
            "authorization_base_head": HEAD,
            "authorization_base_tree": TREE,
            "operation_context_head": HEAD,
            "operation_context_tree": TREE,
            "presentation_head": HEAD,
            "presentation_tree": TREE,
            "human_decision_presentation_status": "VERIFIED__READY_FOR_HUMAN_DECISION",
            "human_authority_status": "NOT_PROVEN__NO_FRESH_KY_HUMAN_ACT_YET",
            "human_authority_handoff_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "preconsumption_binding_status": "NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
            "operational_counters": exact_operational_counters(),
            "fresh_ky_phase_a_presentation_ready": "VERIFIED",
            "fresh_kw_phase_a_presentation_ready": "NOT_APPLICABLE__KY_GENERATION",
            "human_decision_presentation": "VERIFIED__FRESH_KY_EXACT_PRESENTATION_CREATED",
            "human_authority_present": False,
            "phase_b_started": False,
            "auto_continuable": False,
            "human_review_required": True,
            "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        }
    )
    value["frontier"] = {
        "last_verified_operational_edge": "VERIFIED__KW_ONE_ATTEMPT_REACHED_GUEST_COMMISSIONING_P01_TO_P12_THEN_CONTEXT_PERMISSION_FAILURE",
        "first_unverified_operational_edge": "NOT_PROVEN__POST_KX_GUEST_CONTEXT_LOAD_THEN_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
        "last_verified_edge": "VERIFIED__KX_REPOSITORY_RUNTIME_EXPORT_PERMISSION_CONTRACT_AND_KY_PHASE_A_PRESENTATION",
        "first_broken_edge": "NOT_PROVEN__NO_POST_KX_OPERATIONAL_FAILURE_AUTHENTICATED",
        "current_real_blocker": "VERIFIED__FRESH_KY_HUMAN_DECISION_NOT_YET_PRESENT",
        "minimum_missing_capability": "NOT_PROVEN__NO_NEW_CAPABILITY_GAP__FRESH_POST_KX_OPERATIONAL_OBSERVATION_MISSING",
        "minimum_legal_next_delta": "ONLY_AFTER_SEPARATE_HUMAN_ACT__SAME_KY_GENERATION_HANDOFF_BIND_ADMIT_CONSUME_ONCE_OPERATE_ONCE__NO_INTERVENING_COMMIT",
    }
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__0__PHASE_A_READINESS_IS_NOT_OPERATIONAL_CAPABILITY",
        "new_operational_capability_count": "VERIFIED__0",
        "new_operational_observation_count": "VERIFIED__0",
        "new_e05_credit_count": "VERIFIED__0",
        "new_human_decision_presentation_count": "VERIFIED__1",
        "ex_proof_reuse_count": "VERIFIED__17",
        "ex_reconstruction_count": "VERIFIED__0",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": "EX_17_OF_17__JP_JO__FM_KX_RUNTIME_EXPORT__GN__JZ__GL__ER__P11__CANONICAL_HUMAN_AUTHORITY_SERIALIZER__ONE_SHOT_GUARDS",
        "new_capabilities": "VERIFIED__0__ONE_FRESH_KY_PHASE_A_INSTANCE_ONLY",
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update(
        {
            "project_state": "VERIFIED__KY_PHASE_A_READY_AT_HUMAN_DECISION_BARRIER",
            "project_progress": "VERIFIED__POST_KX_CURRENT_HEAD_CANDIDATE_CONTEXT_REQUEST_AND_PRESENTATION_SEALED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__KX_REPAIR_COMMITTED_AND_KY_PHASE_A_COMPLETE__SEPARATE_HUMAN_DECISION_REQUIRED",
            "constitutional_health_evidence": "VERIFIED__CURRENT_HEAD_EQUALITY__FM_KX_PERMISSION_CONTRACT__GN_EXACT_SCHEMA__NO_AUTHORITY_OR_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EXISTING_OWNER_CHAIN_REUSED",
            "overengineering_risk": "ESTIMATED__HIGH_IF_NEW_OWNER_ROUTE_OR_REPAIR_IS_ADDED_IN_PHASE_A",
            "cognition_provenance": "VERIFIED__COMMITTED_KW_KX_AND_REPOSITORY_OWNER_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__REPOSITORY_DERIVED_KX_TO_KY_CONTINUATION__NO_MEMORY_AUTHORITY",
            "candidate_capability": "NOT_PROVEN__POST_KX_EXPIRED_OPERATIONAL_DENIAL_REMAINS_UNOBSERVED",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ONE_SHOT_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__KX_REPOSITORY_REPAIR_TO_KY_HUMAN_DECISION_BARRIER",
        }
    )
    B.W.reseal(envelope, "reduction")
    B.W.write_canonical(reduction_path, envelope)


def materialize_human_decision_presentation() -> None:
    request_path = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    authorization_path = KY / "G77_256KY_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    readiness_path = KY / "G77_256KY_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    safe_path = KY / "G77_256KY_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    context_path = KY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    target = KY / "G77_256KY_HUMAN_DECISION_PRESENTATION_V1.txt"
    request_envelope = load_canonical(request_path)
    request = verify_seal(request_envelope, "request")
    readiness = load_canonical(readiness_path)
    safe = load_canonical(safe_path)
    context = load_canonical(context_path)
    lines = [
        "G77-256KY HUMAN DECISION PRESENTATION V1",
        "NONAUTHORITY: review only; this presentation does not record or infer approval.",
        f"GENERATION {request['generation_identity']}",
        f"OPERATION {request['operation_identity']}",
        "VECTOR EXPIRED",
        f"PURPOSE {PURPOSE}",
        f"CANDIDATE_SHA256 {context['candidate_manifest_sha256']}",
        f"CONTEXT_SHA256 {context['context_sha256']}",
        f"CONTEXT_FILE_SHA256 {sha256_path(context_path)}",
        f"CANONICAL_ARGV_SHA256 {context['canonical_argv_sha256']}",
        f"TEMPORAL_BINDING_SHA256 {sha256_bytes(canonical_bytes(context['preclaim_temporal_binding']))}",
        f"REQUEST_IDENTITY_SHA256 {request_envelope['request_sha256']}",
        f"REQUEST_FILE_SHA256 {sha256_path(request_path)}",
        f"AUTHORIZATION_PRESENTATION_SHA256 {sha256_path(authorization_path)}",
        f"READINESS_CHECKPOINT_SHA256 {readiness['checkpoint_sha256']}",
        f"SAFE_STOP_CHECKPOINT_SHA256 {safe['checkpoint_sha256']}",
        f"AUTHORIZATION_BASE_HEAD {HEAD}",
        f"AUTHORIZATION_BASE_TREE {TREE}",
        f"OPERATION_CONTEXT_HEAD {HEAD}",
        f"OPERATION_CONTEXT_TREE {TREE}",
        f"PRESENTATION_HEAD {HEAD}",
        f"PRESENTATION_TREE {TREE}",
        "EXPECTED_ROUTE FM -> ER -> P11",
        "REQUESTED_SCOPE ONE fresh KY generation; ONE EXPIRED operation; at most ONE future Human authority consumption; at most ONE future operational attempt.",
        "NOT_AUTHORIZED NO_REPLAY; NO_REPAIR_RETRY; NO_SECOND_OPERATION; NO_ALTERNATE_AUTHORITY_PATH; NO_P11_BYPASS; NO_PARALLEL_ROUTE; NO_AUTHORITY_TRANSFER; NO_HISTORICAL_AUTHORITY_REUSE; NO_EXPANSION_OF_PRODUCTION_BEHAVIOR.",
        "ONE_SHOT_LIMIT AUTHORITY_CONSUMPTION_MAXIMUM=1; OPERATION_ATTEMPT_MAXIMUM=1.",
        "RETRY_LIMIT 0",
        "REPAIR_RETRY_LIMIT 0",
        "REPLAY_LIMIT 0",
        "E05_STATE VERIFIED__11_OF_18",
        "E05_FRONTIER VERIFIED__7_UNSATISFIED_OF_18",
        "KY_E05_CREDIT VERIFIED__0",
        "EXPIRED NOT_PROVEN_OPERATIONALLY",
        "HUMAN_DECISION_PRESENTATION VERIFIED__READY_FOR_HUMAN_DECISION",
        "HUMAN_AUTHORITY NOT_PROVEN__NO_FRESH_KY_HUMAN_ACT_YET",
        "HUMAN_AUTHORITY_HANDOFF NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "PRECONSUMPTION_BINDING NOT_APPLICABLE__HUMAN_ACT_NOT_YET_PRESENT",
        "AUTHORITY_CONSUMPTION 0",
        "PHASE_B_STARTED FALSE",
        "OPERATION_ATTEMPT 0",
        "AUTO_CONTINUABLE FALSE",
        "HUMAN_REVIEW_REQUIRED TRUE",
        "STOP AT THE HUMAN DECISION BARRIER.",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    B.install_entry_scope_filter()
    kx_result = authenticate_kx()
    kv_result = B.authenticate_kv()
    candidate_reissue_result = B.materialize_current_candidate_source()
    km_result = B.W.authenticate_km()
    cross_vector_result = B.cross_vector_reuse_assessment()
    ki_result = B.W.L.authenticate_ki()
    kf_result = B.W.P.authenticate_kf()
    rebound_result = rebind_kx_launcher_identity()
    kd_proof = B.W.P.E.authenticate_kd_interface_before_presentation()
    kb_result = B.W.P.E.K.authenticate_kb()
    jz_result = B.W.P.E.K.K.authenticate_jz()
    e05_frontier_result = B.W.P.E.K.K.authenticate_e05_frontier()
    B.W.P.M.materialize(arguments)
    namespace_result = B.W.P.E.augment_namespace_preflight(
        B.W.P.E.K.materialize_namespace_preflight(kb_result)
    )
    jz_readiness = B.W.P.E.K.K.materialize_jz_readiness(jz_result)
    B.W.P.E.K.K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    B.W.P.E.K.bind_namespace_into_phase_a(kb_result, namespace_result)
    kd_result = B.W.P.E.materialize_kd_preflight(kd_proof)
    B.W.P.E.bind_kd_preflight_into_phase_a(kd_result)
    kf_preflight = B.W.P.materialize_kf_preflight(kf_result, rebound_result)
    B.W.P.bind_kf_into_phase_a(kf_result, kf_preflight)
    ki_preflight = B.W.L.materialize_ki_preflight(ki_result)
    B.W.L.bind_ki_into_phase_a(ki_result, ki_preflight)
    km_preflight = B.W.materialize_km_preflight(km_result, cross_vector_result)
    B.W.bind_km_into_phase_a(km_result, km_preflight, cross_vector_result)
    B.bind_kv_lifecycle(kv_result, cross_vector_result, candidate_reissue_result)
    bind_kx_frontier(kx_result, cross_vector_result)
    materialize_human_decision_presentation()
    print(TERMINAL)
