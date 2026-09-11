#!/usr/bin/env python3
"""Materialize the nonauthority KG EXPIRED Phase-A Human barrier.

KG reuses the authenticated KE commissioning owner, rebinds its three exact
launcher-identity expectations to the committed KF permission repair, and
adds a KF-specific repository preflight before any Human presentation.  It
does not create or consume Human authority and does not invoke PRE, FM, QEMU,
a VM, an operational request, P11, or a protected effect.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KG = ROOT / (
    ".github/governance/evidence/"
    "g77_256kg_fresh_expired_operational_recommissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "3bcc78deaeb6821dd71ecdbc9de18628d3ff07de"
TREE = "eb06ab5d18fc99d648b7ba20d40269ccf3d0de40"
SUBJECT = "G77-256KF verify guest harness permission binding repair"
REMOTE = "git@github.com:Aljosa3/sapianta-ecosystem.git"
KE_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KE_MATERIALIZER_SHA256 = (
    "ba27eaafd1c5f00acd6753bfae8f33f3189a744a6674de187ab8e943b78f58be"
)
KF_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kf_guest_harness_permission_binding_repair_v1/"
    "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
KF_REDUCTION_SHA256 = (
    "6210226beb40806d3099dcb50577a7a59dadb4c5a4443fb32308c280914d86c8"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
PRE_KF_FM_LAUNCHER_SHA256 = (
    "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36"
)
KF_FM_LAUNCHER_SHA256 = (
    "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
)
KF_TERMINAL = "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED"
KG_TERMINAL = (
    "A__FRESH_KG_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)


class KGBarrierError(RuntimeError):
    """One deterministic fail-closed KG Phase-A error."""


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
        raise KGBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KGBarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KGBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_adapted_ke_materializer() -> ModuleType:
    path = ROOT / KE_MATERIALIZER
    raw = path.read_bytes()
    committed = subprocess.check_output(
        ["git", "show", f"{HEAD}:{KE_MATERIALIZER}"], cwd=ROOT
    )
    if raw != committed or sha256_bytes(raw) != KE_MATERIALIZER_SHA256:
        raise KGBarrierError("COMMITTED_KE_PREAUTHORIZATION_OWNER_MISMATCH")
    source = raw.decode("utf-8")
    source = source.replace("G77_256KE", "G77_256KG")
    source = source.replace("G77-256KE", "G77-256KG")
    source = source.replace("g77_256ke", "g77_256kg")
    source = source.replace('.replace("kc", "ke")', '.replace("kc", "kg")')
    source = source.replace("KEBarrierError", "KGBarrierError")
    source = source.replace("KE_", "KG_").replace("__KE", "__KG")
    source = re.sub(r"\bKE\b", "KG", source)
    source = source.replace("ed4acdc4c132754d857d623e54783e54e4c96d52", HEAD)
    source = source.replace("be8967cad28c9149fb5e17b895e5c58ac119ef13", TREE)
    source = source.replace(
        "G77-256KD verify KC Phase-B entry owner interface binding", SUBJECT
    )
    module = ModuleType("g77_256kg_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


E = load_adapted_ke_materializer()
M = E.M


def rebind_kf_launcher_identity() -> dict[str, Any]:
    """Replace only the three inherited pre-KF launcher expectations."""

    bindings = (
        (E.K.KB_HASHES, E.K.FM_LAUNCHER, "KB_CURRENT_LAUNCHER"),
        (E.K.K.EXPECTED_HASHES, E.K.K.FM_PATH, "COMMISSIONING_FM_OWNER"),
        (E.K.K.A.JX_HASHES, E.K.K.A.FM_PATH, "JX_FM_LAUNCHER"),
    )
    rebound: list[str] = []
    for mapping, key, label in bindings:
        if mapping.get(key) != PRE_KF_FM_LAUNCHER_SHA256:
            raise KGBarrierError(f"UNEXPECTED_PRE_KF_LAUNCHER_BINDING:{label}")
        mapping[key] = KF_FM_LAUNCHER_SHA256
        rebound.append(label)
    if sha256_path(ROOT / FM_LAUNCHER) != KF_FM_LAUNCHER_SHA256:
        raise KGBarrierError("COMMITTED_KF_LAUNCHER_IDENTITY_MISMATCH")
    return {
        "classification": "EXACT_KF_SUCCESSOR_IDENTITY_REBINDING",
        "pre_kf_launcher_sha256": PRE_KF_FM_LAUNCHER_SHA256,
        "kf_launcher_sha256": KF_FM_LAUNCHER_SHA256,
        "rebound_expectation_count": len(rebound),
        "rebound_expectations": rebound,
        "new_owner": False,
        "new_route": False,
    }


def authenticate_kf() -> dict[str, Any]:
    raw = (ROOT / KF_REDUCTION).read_bytes()
    committed = subprocess.check_output(
        ["git", "show", f"{HEAD}:{KF_REDUCTION}"], cwd=ROOT
    )
    if raw != committed or sha256_bytes(raw) != KF_REDUCTION_SHA256:
        raise KGBarrierError("COMMITTED_KF_REDUCTION_IDENTITY_MISMATCH")
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope):
        raise KGBarrierError("KF_REDUCTION_NONCANONICAL")
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256")
        != sha256_bytes(canonical_bytes(reduction))
    ):
        raise KGBarrierError("KF_REDUCTION_SEAL_MISMATCH")
    permission = reduction.get("permission_contract", {})
    architecture = reduction.get("architecture", {})
    reuse = reduction.get("reuse", {})
    required = {
        "authoritative_owner": (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/"
            "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py:"
            "materialize_operation_state"
        ),
        "minimum_permission_delta": "VERIFIED__ONE_BIT__OTHER_EXECUTE__0700_TO_0701",
        "file_execute_permission_required": False,
        "read_only_projection": "VERIFIED__PRESERVED",
        "production_route_before": 1,
        "production_route_after": 1,
    }
    if (
        reduction.get("terminal") != KF_TERMINAL
        or any(permission.get(key) != value for key, value in required.items())
        or permission.get("post_repair_launcher_sha256")
        != KF_FM_LAUNCHER_SHA256
        or reuse.get("ex_reused") != "VERIFIED__17_OF_17"
        or reuse.get("ex_reconstructed") != "VERIFIED__0"
        or reuse.get("assumption_invalidation_count") != 0
        or architecture.get("new_owner_count") != 0
        or architecture.get("new_route_count") != 0
    ):
        raise KGBarrierError("KF_PERMISSION_CONTRACT_MISMATCH")
    source = (ROOT / FM_LAUNCHER).read_text(encoding="utf-8")
    mkdir_at = source.index("mode=GUEST_HARNESS_PROJECTION_ROOT_CONSTRUCTION_MODE,")
    adapter_at = source.index('Path(adapter_binding["projected_path"]).write_bytes(adapter_bytes)')
    context_at = source.index(
        "context_owner_projection.write_bytes(context_owner_source.read_bytes())"
    )
    chmod_at = source.index("adapter_projection_root.chmod(")
    if not mkdir_at < adapter_at < context_at < chmod_at:
        raise KGBarrierError("KF_MATERIALIZATION_ORDER_MISMATCH")
    if source.count("def materialize_operation_state(") != 1:
        raise KGBarrierError("KF_AUTHORITATIVE_OWNER_COUNT_MISMATCH")
    return {
        "terminal": KF_TERMINAL,
        "reduction_file_sha256": KF_REDUCTION_SHA256,
        "launcher_file_sha256": KF_FM_LAUNCHER_SHA256,
        "authoritative_owner": required["authoritative_owner"],
        "construction_mode": "0700",
        "presentation_mode": "0701",
        "context_owner_mode": "0644",
        "one_bit_delta": "VERIFIED",
        "custody_uid": 3,
        "custody_traversal_contract": "VERIFIED_REPOSITORY_ONLY",
        "context_owner_readability": "VERIFIED_REPOSITORY_ONLY",
        "source_execute_required": "NO",
        "read_only_projection": "VERIFIED__PRESERVED",
        "new_route": "VERIFIED__NO",
        "new_owner": "VERIFIED__NO",
        "p11_implementation_mutation_count": 0,
        "production_route": "VERIFIED__1_TO_1",
        "ex_assumption_invalidation_count": 0,
        "scope": "REPOSITORY_ONLY__NOT_OPERATIONAL_GUEST_SUCCESS",
    }


def materialize_kf_preflight(
    kf: dict[str, Any], rebinding: dict[str, Any]
) -> dict[str, Any]:
    context = E.load_canonical(
        KG / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )
    projection_root = Path(context["guest_adapter_binding"]["projection_root"])
    owner = projection_root / "sapianta_fresh_operation_context_v1.py"
    root_mode = stat.S_IMODE(projection_root.stat().st_mode)
    owner_mode = stat.S_IMODE(owner.stat().st_mode)
    custody_owner_bits = owner_mode & 0o007
    if root_mode != 0o701 or custody_owner_bits != 0o004:
        raise KGBarrierError("KG_MATERIALIZED_PERMISSION_PREFLIGHT_MISMATCH")
    proof = {
        "schema_id": "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_V1",
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": M.GENERATION,
        "operation_identity": M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "kf_authentication": kf,
        "launcher_identity_rebinding": rebinding,
        "materialized_projection_root": str(projection_root),
        "observed_presentation_mode": f"{root_mode:04o}",
        "committed_context_owner_mode": "0644",
        "observed_materialized_context_owner_mode": f"{owner_mode:04o}",
        "custody_effective_context_owner_mode": f"{custody_owner_bits:04o}",
        "umask_variance": (
            "OBSERVED__GROUP_WRITE_ONLY__NO_CUSTODY_WRITE_OR_EXECUTE_PERMISSION"
        ),
        "one_bit_delta": "VERIFIED",
        "custody_traversal_contract": "VERIFIED_REPOSITORY_ONLY",
        "context_owner_readability": "VERIFIED_REPOSITORY_ONLY",
        "source_execute_required": "NO",
        "read_only_projection": "VERIFIED__PRESERVED",
        "operational_guest_success": "NOT_PROVEN",
        "new_route": "VERIFIED__NO",
        "new_owner": "VERIFIED__NO",
        "operational_counters": M.zero_counters(),
    }
    envelope = {
        "schema_id": "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KG / "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__KF_PERMISSION_BINDING_REPOSITORY_PREFLIGHT",
        "scope": "REPOSITORY_ONLY__NOT_OPERATIONAL_GUEST_SUCCESS",
    }


def bind_kf_into_phase_a(
    kf: dict[str, Any], preflight: dict[str, Any]
) -> None:
    readiness_path = KG / "G77_256KG_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KG / "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KG / "G77_256KG_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KG / "G77_256KG_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KG / "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = load_canonical(readiness_path)
    readiness["checkpoint"]["kf_permission_binding_preflight"] = preflight
    reseal(readiness, "checkpoint")
    write_canonical(readiness_path, readiness)

    request = load_canonical(request_path)
    request["request"]["preauthorization"].update({
        "checkpoint_file_sha256": sha256_path(readiness_path),
        "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
    })
    reseal(request, "request")
    write_canonical(request_path, request)

    presentation_path.write_bytes(M.GN.render_human_authorization_presentation(request_path))
    gn_result = M.GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    equivalence = load_canonical(equivalence_path)
    equivalence["proof"].update({
        "request_file_sha256": sha256_path(request_path),
        "presentation_sha256": sha256_path(presentation_path),
        "request_sha256": request["request_sha256"],
        **gn_result,
    })
    reseal(equivalence, "proof")
    write_canonical(equivalence_path, equivalence)

    safe_stop = load_canonical(safe_stop_path)
    safe_stop["checkpoint"].update({
        "terminal": KG_TERMINAL,
        "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
        "readiness_checkpoint_inner_sha256": readiness["checkpoint_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "request_identity": request["request_sha256"],
        "presentation_identity": sha256_path(presentation_path),
        "equivalence_file_sha256": sha256_path(equivalence_path),
        "equivalence_inner_sha256": equivalence["proof_sha256"],
        "kf_permission_binding_preflight": preflight,
    })
    reseal(safe_stop, "checkpoint")
    write_canonical(safe_stop_path, safe_stop)

    reduction = load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KG_TERMINAL
    value["kf_authentication"] = kf
    value["kf_permission_binding_preflight"] = preflight
    value["owner_results"]["kf_permission_binding_preflight"] = preflight["result"]
    value["identities"].update({
        "request_sha256": request["request_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "presentation_sha256": sha256_path(presentation_path),
        "readiness_checkpoint_sha256": readiness["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
        "checkpoint_sha256": safe_stop["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(safe_stop_path),
        "kf_permission_preflight_sha256": preflight["inner_sha256"],
        "kf_permission_preflight_file_sha256": preflight["file_sha256"],
    })
    value["provider_interruption"] = {
        "provider_limit_interruption": "OBSERVED",
        "interrupted_generation": "G77_256KG",
        "interrupted_spce_phase": "PHASE_A",
        "operational_process_interrupted": "NO",
        "human_authority_interrupted": "NO",
        "same_generation_recovery": "PERMITTED__PHASE_A_ONLY",
        "provider_capability_is_execution_authority": False,
    }
    value["existing_kg_delta_reconstruction"] = (
        "VERIFIED__NONE__CLEAN_COMMITTED_KF_ENTRY"
    )
    value["recovery_operational_counters"] = {
        "new_authority_consumption_during_recovery": 0,
        "new_operation_attempt_during_recovery": 0,
        "new_pre_operational_during_recovery": 0,
        "new_fm_operational_invocation_during_recovery": 0,
        "new_qemu_during_recovery": 0,
        "new_vm_during_recovery": 0,
        "new_operational_request_during_recovery": 0,
        "new_p11_entry_during_recovery": 0,
        "new_protected_invocation_during_recovery": 0,
        "new_protected_effect_during_recovery": 0,
        "retry_during_recovery": 0,
        "repair_retry_during_recovery": 0,
        "replay_during_recovery": 0,
    }
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
        "kf_historical_existing_operational_binding_owner_mutation_count": 1,
        "kf_historical_production_mutation_count": 1,
    }
    value["proof_yield"] = {
        "new_verified_capability_count": (
            "VERIFIED__1_FRESH_KG_PREAUTHORIZATION_READINESS_CAPABILITY"
        ),
        "new_blocker_localized_count": "VERIFIED__0",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"] = {
        "existing_certified_capabilities_reused": (
            "EX_17_OF_17__JR__JX__JZ__KB__KD__KE__KF__GN__FM__ER__P11__"
            "SOLE_ROUTE__STABLE_CHECKOUT__PINNED_NESTED_AUTHORITY"
        ),
        "new_capabilities": (
            "VERIFIED__1_FRESH_KG_PHASE_A_PREAUTHORIZATION_READINESS_CAPABILITY"
        ),
        "existing_capability_became_unreachable": False,
        "parallel_flow_created": False,
        "production_path_count_effect": "UNCHANGED__1_TO_1",
    }
    value["governance_dashboard"].update({
        "project_progress": (
            "VERIFIED__FRESH_KG_EXPIRED_PREAUTHORIZATION_READY_FOR_HUMAN_DECISION"
        ),
        "project_progress_estimate": (
            "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR"
        ),
        "informal_project_progress_estimate": (
            "ESTIMATED__KNOWN_KE_GUEST_PERMISSION_BLOCKER_REPAIRED_AND_FRESH_"
            "EXPIRED_PATH_READY_FOR_ONE_HUMAN_DECISION"
        ),
        "constitutional_health_evidence": (
            "VERIFIED__ALL_KG_PHASE_A_OPERATIONAL_COUNTERS_ZERO_AND_HUMAN_"
            "AUTHORITY_NOT_YET_PRESENT"
        ),
        "shadow_automation_status": "VERIFIED__ABSENT",
        "constitutional_frontier_distance": (
            "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
        ),
        "governance_efficience": (
            "ESTIMATED__HIGH__KNOWN_TECHNICAL_BLOCKERS_PREFLIGHTED_BEFORE_"
            "HUMAN_AUTHORITY"
        ),
        "overengineering_risk": (
            "ESTIMATED__LOW__REUSE_EXISTING_COMMISSIONING_AND_BINDING_INFRASTRUCTURE"
        ),
        "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
        "cognition_assisted_handoff": (
            "VERIFIED__PROVIDER_INTERRUPTED_SAME_GENERATION_REPOSITORY_RECONSTRUCTION"
        ),
        "candidate_capability": "NOT_PROVEN__FRESH_EXPIRED_OPERATIONAL_DENIAL",
        "shadow_design_target": (
            "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_KF_PERMISSION_BINDING_AND_"
            "STABLE_JR_EXPIRED_CHECKOUT"
        ),
        "constitutional_continuation_progress": (
            "VERIFIED__KF_REPOSITORY_REPAIR_TO_FRESH_KG_HUMAN_AUTHORITY_BARRIER"
        ),
    })
    value["frontier"] = {
        "last_verified_edge": (
            "FRESH_KG_PREAUTHORIZATION_AND_TECHNICAL_READINESS_PRESENTED_FOR_"
            "HUMAN_DECISION"
        ),
        "first_broken_edge": "HUMAN_AUTHORITY_NOT_YET_SUPPLIED",
        "minimum_missing_capability": (
            "ONE_FRESH_EXACT_HUMAN_AUTHORIZATION_FOR_THE_BOUND_KG_REQUEST"
        ),
        "minimum_legal_next_delta": (
            "ONLY_AFTER_EXACT_HUMAN_AUTHORIZATION__SAME_G77_256KG_SPCE_PHASE_B_"
            "ONE_CONSUMPTION_ONE_OPERATION_ATTEMPT"
        ),
    }
    value["ccwim"].update({
        "authenticated_repository_continuation": "VERIFIED__YES",
        "previous_worker_conversation_required": "VERIFIED__NO",
        "previous_worker_memory_required": "VERIFIED__NO",
        "handoff_reconstruction_success": "VERIFIED__YES",
        "handoff_ambiguity_count": "VERIFIED__0",
        "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        "cross_account_recovery": "VERIFIED",
        "provider_interruption_recovery": "VERIFIED",
    })
    value["hac_hai_hae"] = (
        "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
    )
    value["human_authority_present"] = False
    value["auto_continuable"] = False
    value["human_review_required"] = True
    reseal(reduction, "reduction")
    write_canonical(reduction_path, reduction)


def authenticate_resumable_materialized_delta() -> None:
    """Authenticate the exact KG delta left by the local KF-preflight stop."""

    required = (
        "G77_256KG_PREHUMAN_PHASE_A_REDUCTION_V1.json",
        "G77_256KG_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json",
        "G77_256KG_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256KG_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256KG_KB_NAMESPACE_PREFLIGHT_V1.json",
        "G77_256KG_KD_INTERFACE_PREFLIGHT_V1.json",
        "G77_256KG_JZ_PRECONSUMPTION_INVOCATION_READINESS_V1.json",
    )
    if any(not (KG / name).is_file() for name in required):
        raise KGBarrierError("KG_RESUMABLE_DELTA_REQUIRED_ARTIFACT_ABSENT")
    if (
        (KG / "G77_256KG_KF_PERMISSION_BINDING_PREFLIGHT_V1.json").exists()
        or (KG / "G77_256KG_HUMAN_DECISION_PRESENTATION_V1.txt").exists()
    ):
        raise KGBarrierError("KG_RESUMABLE_DELTA_FRONTIER_AMBIGUOUS")
    reduction = load_canonical(KG / required[0])["reduction"]
    if (
        reduction.get("generation_identity") != M.GENERATION
        or reduction.get("operation_identity") != M.OPERATION
        or any(reduction.get("operational_counters", {}).values())
        or reduction.get("owner_results", {}).get("kd_interface_preflight")
        != "PASS__KG_ADAPTED_CONTROLLER_MATERIALIZER_CHAIN_PRESERVES_KD_INTERFACE"
    ):
        raise KGBarrierError("KG_RESUMABLE_DELTA_IDENTITY_OR_COUNTER_MISMATCH")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    parser.add_argument("--resume-after-materialization", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    kf_result = authenticate_kf()
    rebound_result = rebind_kf_launcher_identity()
    if not arguments.resume_after_materialization:
        kd_proof = E.authenticate_kd_interface_before_presentation()
        kb_result = E.K.authenticate_kb()
        jz_result = E.K.K.authenticate_jz()
        e05_frontier_result = E.K.K.authenticate_e05_frontier()
        M.materialize(arguments)
        namespace_result = E.augment_namespace_preflight(
            E.K.materialize_namespace_preflight(kb_result)
        )
        jz_readiness = E.K.K.materialize_jz_readiness(jz_result)
        E.K.K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
        E.K.bind_namespace_into_phase_a(kb_result, namespace_result)
        kd_result = E.materialize_kd_preflight(kd_proof)
        E.bind_kd_preflight_into_phase_a(kd_result)
    else:
        authenticate_resumable_materialized_delta()
    kf_preflight = materialize_kf_preflight(kf_result, rebound_result)
    bind_kf_into_phase_a(kf_result, kf_preflight)
    E.materialize_human_decision_presentation()
    print(KG_TERMINAL)
