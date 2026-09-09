#!/usr/bin/env python3
"""Reduce JU's GN request-schema blocker without authority or operation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JU = ROOT / ".github/governance/evidence/g77_256ju_expired_operational_v1"
MATERIALIZER_PATH = JU / "orchestration/G77_256JU_PREAUTHORIZATION_MATERIALIZER_V1.py"
REQUEST = JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
CHECKPOINT = JU / "G77_256JU_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
CONTEXT = JU / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REDUCTION = JU / "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
TERMINAL = "M__FRESH_EXPIRED_PREAUTHORIZATION_GN_REQUEST_SCHEMA_MISMATCH"


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


M = load_module(MATERIALIZER_PATH, "g77_256ju_blocker_materializer")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RuntimeError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def canonical_bytes(value: Any) -> bytes:
    return M.canonical_bytes(value)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical evidence: {path.name}")
    return value


def authenticate_boundary() -> dict[str, Any]:
    entry = M.authenticate_entry(M.HEAD, M.NESTED_HEAD)
    jt = M.authenticate_jt()
    expired = M.authenticate_expired_semantics()
    request = load_canonical(REQUEST)
    checkpoint = load_canonical(CHECKPOINT)
    context = load_canonical(CONTEXT)
    for envelope, inner_name in ((request, "request"), (checkpoint, "checkpoint")):
        inner = envelope[inner_name]
        expected = hashlib.sha256(canonical_bytes(inner)).hexdigest()
        if envelope[f"{inner_name}_sha256"] != expected:
            raise RuntimeError(f"inner seal mismatch: {inner_name}")

    request_inner = request["request"]
    request_extra = sorted(set(request_inner) - M.GN.REQUEST_FIELDS)
    request_missing = sorted(M.GN.REQUEST_FIELDS - set(request_inner))
    live = request_inner["live_binding"]
    live_extra = sorted(set(live) - M.GN.LIVE_BINDING_FIELDS)
    live_missing = sorted(M.GN.LIVE_BINDING_FIELDS - set(live))
    observed = {
        "request_extra_fields": request_extra,
        "request_missing_fields": request_missing,
        "live_binding_extra_fields": live_extra,
        "live_binding_missing_fields": live_missing,
    }
    expected_observed = {
        "request_extra_fields": ["expired_execution_count"],
        "request_missing_fields": ["wrong_attempt_execution_count"],
        "live_binding_extra_fields": [
            "expired_adapter_sha256",
            "temporal_binding_sha256",
        ],
        "live_binding_missing_fields": ["du", "eb", "ee"],
    }
    if observed != expected_observed:
        raise RuntimeError("GN request-schema mismatch changed")
    try:
        M.GN.load_validated_sealed_request(REQUEST)
    except M.GN.PresentationBindingError as exc:
        rejection = str(exc)
    else:
        raise RuntimeError("GN unexpectedly accepted malformed JU request")
    if rejection != "SEALED_REQUEST_FIELDS_INVALID":
        raise RuntimeError("GN rejection token changed")

    identities = checkpoint["checkpoint"]["identities"]
    if (
        context["context_sha256"] != identities["context_sha256"]
        or context["canonical_argv_sha256"] != identities["canonical_argv_sha256"]
        or context["candidate_manifest_sha256"] != identities["candidate_sha256"]
        or context["generation_identity"] != M.GENERATION
        or context["operation_identity"] != M.OPERATION
        or (
            context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"],
            context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"],
        )
        != (M.JR_HEAD, M.JR_TREE)
    ):
        raise RuntimeError("materialized preauthorization identity mismatch")

    prohibited = [
        JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        JU / "G77_256JU_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json",
        JU / "G77_256JU_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        JU / "G77_256JU_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        JU / "G77_256JU_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        JU / "G77_256JU_PREHUMAN_PHASE_A_REDUCTION_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
    ]
    if any(path.exists() or path.is_symlink() for path in prohibited):
        raise RuntimeError("authority, presentation, or operation artifact unexpectedly exists")
    if subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("index is not empty")
    return {
        "entry": entry,
        "jt": jt,
        "expired": expired,
        "request_schema_difference": observed,
        "gn_rejection": rejection,
        "identities": {
            **identities,
            "request_sha256": request["request_sha256"],
            "request_file_sha256": sha256_path(REQUEST),
            "checkpoint_sha256": checkpoint["checkpoint_sha256"],
            "checkpoint_file_sha256": sha256_path(CHECKPOINT),
            "presentation_identity": "NOT_MATERIALIZED",
        },
    }


def build_reduction() -> dict[str, Any]:
    proof = authenticate_boundary()
    counters = {
        key: "VERIFIED__0"
        for key in (
            "operational_authorization_count",
            "authority_consumption_count",
            "pre_operational_count",
            "fm_operational_invocation_count",
            "qemu_count",
            "vm_count",
            "operation_attempt_count",
            "request_count",
            "p11_entry_count",
            "protected_invocation_count",
            "protected_effect_count",
            "retry_count",
            "repair_retry_count",
            "replay_count",
        )
    }
    return {
        "schema_id": "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1",
        "generation": "G77-256JU",
        "mode": "FAIL_CLOSED_PREHUMAN_REPOSITORY_REDUCTION",
        "terminal": TERMINAL,
        "phase": "FAIL_CLOSED_BEFORE_HUMAN_AUTHORIZATION_PRESENTATION",
        "entry": proof["entry"],
        "jt_reconstruction": proof["jt"],
        "expired_semantics": proof["expired"],
        "blocker": {
            "last_completed_stage": "SEALED_PREAUTHORIZATION_CHECKPOINT_AND_REQUEST_MATERIALIZED",
            "first_failed_stage": "GN_EXACT_SEALED_REQUEST_VALIDATION",
            "gn_rejection": proof["gn_rejection"],
            **proof["request_schema_difference"],
            "production_defect_proven": False,
            "retry_performed": False,
            "repair_retry_performed": False,
        },
        "identities": proof["identities"],
        "authority_boundary": {
            "authorization_request_materialization_count": "VERIFIED__1",
            "authorization_presentation_count": "VERIFIED__0",
            "human_authority_present": False,
            "authority_consumed": False,
            "request_is_authority": False,
            "checkpoint_is_authority": False,
            "provider_capability_is_authority": False,
        },
        "operational_counters": counters,
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__JS__JT__FM__FC__ER__GN__P11",
            "new_capabilities": "VERIFIED__0",
            "existing_capability_became_unreachable": "VERIFIED__NO",
            "parallel_flow_created": "VERIFIED__NO",
            "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1__GN_EXACT_REQUEST_SCHEMA_MISMATCH",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "governance_dashboard": {
            "project_progress": "VERIFIED__JU_PREAUTHORIZATION_REQUEST_SCHEMA_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_BLOCKED_BEFORE_HUMAN_PRESENTATION",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_ZERO_AUTHORITY_ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EXACT_PREHUMAN_STOP",
            "overengineering_risk": "ESTIMATED__LOW__NO_PRODUCTION_REPAIR",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_AND_MATERIALIZED_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "NOT_APPLICABLE__NO_PROVIDER_RECOVERY",
            "candidate_capability": "NOT_PROVEN__GN_PRESENTATION_NOT_MATERIALIZED",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__JT_TO_JU_BLOCKER_LOCALIZATION",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": "SEALED_PREAUTHORIZATION_CHECKPOINT_AND_REQUEST_MATERIALIZED",
            "first_broken_edge": "GN_EXACT_SEALED_REQUEST_VALIDATION",
            "minimum_missing_capability": "GN_COMPATIBLE_EXPIRED_AUTHORIZATION_REQUEST_PROJECTION",
            "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_EXPIRED_GN_REQUEST_SCHEMA_BINDING_REPAIR_GENERATION",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256JU_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    if REDUCTION.exists() or REDUCTION.is_symlink():
        raise RuntimeError("JU reduction collision")
    REDUCTION.write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    write_reduction()
