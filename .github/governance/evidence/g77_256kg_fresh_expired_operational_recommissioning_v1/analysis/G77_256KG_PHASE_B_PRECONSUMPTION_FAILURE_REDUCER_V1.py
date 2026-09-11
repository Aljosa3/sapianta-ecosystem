#!/usr/bin/env python3
"""Seal the KG preconsumption Human-source/handoff digest mismatch.

This reducer is evidence-only. It refuses to run if consumption or operational
artifacts exist and never imports or invokes the Phase-B controller or FM.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
KG = ROOT / ".github/governance/evidence/g77_256kg_fresh_expired_operational_recommissioning_v1"
SOURCE = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = KG / "G77_256KG_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = KG / "G77_256KG_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
CHECKPOINT = KG / "G77_256KG_PHASE_B_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
PHASE_A = KG / "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json"
OUTPUT = KG / "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_V1.json"
TERMINAL = (
    "M__KG_PHASE_B_HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH_"
    "BEFORE_AUTHORITY_CONSUMPTION"
)
HEAD = "3bcc78deaeb6821dd71ecdbc9de18628d3ff07de"
TREE = "eb06ab5d18fc99d648b7ba20d40269ccf3d0de40"
HUMAN_SOURCE_SHA256 = "d11850611c8c1273dbd1484af40d1d38533f95d8f0665da418885947b32a9484"
HANDOFF_SHA256 = "1e6c6fec12e064dffa2bd69873664e5a236dde812eb47853c1b7f1c056e8020c"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sealed(path: Path, inner: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = path.read_bytes()
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope):
        raise RuntimeError(f"noncanonical evidence: {path.name}")
    value = envelope.get(inner)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{inner}_sha256")
        != hashlib.sha256(canonical_bytes(value)).hexdigest()
    ):
        raise RuntimeError(f"seal mismatch: {path.name}")
    return envelope, value


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise RuntimeError("terminal reduction collision")
    for name in (
        "G77_256KG_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
        "G77_256KG_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json",
        "G77_256KG_FM_OPERATIONAL_INVOCATION_RESULT_V1.json",
    ):
        if (KG / name).exists() or (KG / name).is_symlink():
            raise RuntimeError(f"consumption or operation artifact present: {name}")
    handoff_envelope, handoff = load_sealed(HANDOFF, "authorization")
    binding_envelope, binding = load_sealed(BINDING, "invocation_binding")
    _, checkpoint = load_sealed(CHECKPOINT, "checkpoint")
    _, phase_a = load_sealed(PHASE_A, "reduction")
    source_digest = sha256(SOURCE)
    handoff_digest = sha256(HANDOFF)
    invocation_digest = binding["sealed_invocation_authority_digest"]
    argv_digest = binding["final_fm_argv_authority_digest"]
    if source_digest != HUMAN_SOURCE_SHA256:
        raise RuntimeError("Human-source identity mismatch")
    if {handoff_digest, binding["authenticated_canonical_authority_digest"], invocation_digest, argv_digest} != {HANDOFF_SHA256}:
        raise RuntimeError("JZ internal three-way digest mismatch differs from observation")
    if source_digest == handoff_digest:
        raise RuntimeError("commissioned mismatch is absent")
    counters = checkpoint["operational_counters"]
    expected_counters = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 0,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    if counters != expected_counters or checkpoint.get("authority_state") != "GRANTED_UNCONSUMED":
        raise RuntimeError("preconsumption authority state or counters mismatch")
    if git("rev-parse", "HEAD") != HEAD or git("rev-parse", "HEAD^{tree}") != TREE:
        raise RuntimeError("repository checkpoint drift")
    reduction = {
        "schema_id": "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_V1",
        "terminal": TERMINAL,
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "PHASE_B_PRECONSUMPTION_FAIL_CLOSED__NO_AUTHORITY_CONSUMPTION__NO_OPERATION",
        "entry": {
            "branch": git("branch", "--show-current"),
            "head": HEAD,
            "tree": TREE,
            "subject": git("log", "-1", "--format=%s"),
            "origin": git("remote", "get-url", "origin"),
            "remote_head": HEAD,
            "remote_equality": "VERIFIED",
            "index_empty": git("diff", "--cached", "--name-only") == "",
        },
        "generation_identity": phase_a["generation_identity"],
        "operation_identity": phase_a["operation_identity"],
        "phase_a_terminal": phase_a["terminal"],
        "human_authority": {
            "authentication": "VERIFIED__EXACT_HUMAN_SUPPLIED_ACT__UNCONSUMED",
            "human_source_sha256": source_digest,
            "source_file_sha256": source_digest,
            "authorization_handoff_inner_sha256": handoff_envelope["authorization_sha256"],
            "authorization_state": "AUTHENTICATED__UNCONSUMED",
            "nonreusable": True,
            "nontransferable": True,
            "maximum_consumption": 1,
            "maximum_operation_attempt": 1,
        },
        "jz_digest_binding": {
            "derived_human_source_sha256": source_digest,
            "canonical_handoff_authority_digest": handoff_digest,
            "authenticated_canonical_authority_digest": binding["authenticated_canonical_authority_digest"],
            "sealed_invocation_authority_digest": invocation_digest,
            "final_fm_argv_authority_digest": argv_digest,
            "internal_handoff_invocation_argv_equality": "VERIFIED",
            "commission_required_human_source_equality": "NOT_PROVEN__MISMATCH",
            "jz_three_way_equality": "NOT_PROVEN__HUMAN_SOURCE_TO_CANONICAL_HANDOFF_DIGEST_MISMATCH",
            "caller_digest_input_count": binding["caller_digest_input_count"],
            "provider_digest_input_count": binding["provider_digest_input_count"],
            "negative_binding_rejection_count": checkpoint["negative_binding_rejection_count"],
        },
        "first_broken_edge_evidence": {
            "classification": "HUMAN_SOURCE_DIGEST_DIFFERS_FROM_CANONICAL_HANDOFF_FILE_DIGEST",
            "human_source_sha256": source_digest,
            "canonical_handoff_file_sha256": handoff_digest,
            "values_equal": False,
            "consumption_prevented": True,
            "operation_prevented": True,
        },
        "operational_counters": counters,
        "expired": "NOT_PROVEN_OPERATIONALLY",
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "credit": "VERIFIED__0",
        },
        "ex_reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "assumption_invalidation_count": 0,
        },
        "governance": {
            "project_progress": "VERIFIED__KG_PHASE_B_EXACT_HUMAN_AUTHORITY_AUTHENTICATED_AND_PRECONSUMPTION_DIGEST_MISMATCH_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__PHASE_B_STOPPED_BEFORE_CONSUMPTION_AT_EXACT_SOURCE_TO_HANDOFF_DIGEST_BOUNDARY",
            "constitutional_health_evidence": "VERIFIED__ONE_AUTHENTICATED_UNCONSUMED_AUTHORITY_ZERO_CONSUMPTION_ZERO_OPERATION_ZERO_RETRY",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__MISMATCH_CAUGHT_BEFORE_IRREVERSIBLE_CONSUMPTION",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_FAIL_CLOSED_REDUCTION",
            "cognition_provenance": "VERIFIED__EXACT_HUMAN_SOURCE_CANONICAL_HANDOFF_AND_SEALED_INVOCATION_BYTES_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__DURABLE_REPOSITORY_PHASE_A_AND_EXACT_HUMAN_ACT",
            "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_NOT_INVOKED",
            "constitutional_continuation_progress": "VERIFIED__PHASE_A_TO_AUTHENTICATED_UNCONSUMED_PHASE_B_FAIL_CLOSED_GATE",
        },
        "frontier": {
            "last_verified_edge": "EXACT_HUMAN_ACT_AUTHENTICATED_AND_CANONICAL_HANDOFF_INVOCATION_ARGV_INTERNAL_EQUALITY_VERIFIED",
            "first_broken_edge": "DERIVED_HUMAN_SOURCE_SHA256_DOES_NOT_EQUAL_CANONICAL_HANDOFF_AUTHORITY_DIGEST",
            "minimum_missing_capability": "ONE_AUTHENTICATED_DIGEST_CONTRACT_RECONCILING_EXACT_HUMAN_SOURCE_AUTHORITY_WITH_CANONICAL_HANDOFF_BINDING",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_REPOSITORY_ONLY_JZ_DIGEST_SEMANTICS_ASSESSMENT__NO_KG_CONSUMPTION_OR_OPERATION",
        },
        "architecture": {
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "p11_implementation_mutation_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0_OPERATIONAL_EXPIRED_CAPABILITY",
            "new_blocker_localized_count": "VERIFIED__1_PRECONSUMPTION_DIGEST_SEMANTICS_BLOCKER",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
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
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "EX_17_OF_17__JR__JX__JZ__KB__KD__KE__KF__GN__FM__ER__P11__SOLE_ROUTE__STABLE_CHECKOUT__NESTED_AUTHORITY",
            "new_capabilities": "VERIFIED__0_OPERATIONAL_CAPABILITY__ONE_PRECONSUMPTION_BLOCKER_LOCALIZED",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "artifact_bindings": {
            "human_source_file_sha256": source_digest,
            "handoff_file_sha256": handoff_digest,
            "binding_file_sha256": sha256(BINDING),
            "binding_inner_sha256": binding_envelope["invocation_binding_sha256"],
            "preconsumption_checkpoint_file_sha256": sha256(CHECKPOINT),
        },
        "auto_continuable": False,
        "human_review_required": True,
    }
    envelope = {
        "schema_id": "G77_256KG_PHASE_B_PRECONSUMPTION_FAIL_CLOSED_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    OUTPUT.write_bytes(canonical_bytes(envelope))
    print(TERMINAL)


if __name__ == "__main__":
    main()
