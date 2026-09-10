#!/usr/bin/env python3
"""Materialize the nonauthority KE EXPIRED Phase-A Human barrier.

The committed KC Phase-A construction is authenticated and adapted only for
fresh KE-local identities and the remote-ratified KD entry. Before any Human
presentation is rendered, the adapted materializer projection is checked for
the interface property repaired by KD. No Human authority is created or
consumed and no PRE, FM operation, QEMU, VM, denial, or P11 path is invoked.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KE = ROOT / (
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "ed4acdc4c132754d857d623e54783e54e4c96d52"
TREE = "be8967cad28c9149fb5e17b895e5c58ac119ef13"
SUBJECT = "G77-256KD verify KC Phase-B entry owner interface binding"
KC_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256kc_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KC_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KC_MATERIALIZER_SHA256 = (
    "f41a7b9942a1de0b1825bdda3676d04968d857d01f7370551844abcde16de1d2"
)
KD_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256kd_kc_phase_b_entry_owner_interface_binding_repair_v1/"
    "G77_256KD_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
KD_REDUCTION_SHA256 = (
    "212be6f74d95173a00828c8db544150982d3154fc64e49893dc8b52bd7bc8fde"
)
KD_TERMINAL = (
    "A__KC_PHASE_B_PRECONSUMPTION_ENTRY_OWNER_INTERFACE_BINDING_"
    "REPOSITORY_VERIFIED"
)
KE_TERMINAL = (
    "A__FRESH_KE_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)
WRAPPER_PATH = Path(
    ".github/governance/evidence/"
    "g77_256ke_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KE_PREAUTHORIZATION_MATERIALIZER_V1.py"
)


class KEBarrierError(RuntimeError):
    """One deterministic fail-closed KE Phase-A error."""


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
        raise KEBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KEBarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KEBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_adapted_kc_materializer() -> ModuleType:
    path = ROOT / KC_MATERIALIZER
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{KC_MATERIALIZER}"], cwd=ROOT)
    if raw != committed or sha256_bytes(raw) != KC_MATERIALIZER_SHA256:
        raise KEBarrierError("COMMITTED_KC_PREAUTHORIZATION_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KC", "KE").replace("kc", "ke")
    source = source.replace("2b0a1ff1d7bc3e071392a786dfb64c2eac392df3", HEAD)
    source = source.replace("2b7e42af265f20404ad467c6f1069df56cc388f8", TREE)
    source = source.replace(
        "G77-256KB verify EXPIRED guest namespace binding repair", SUBJECT
    )
    module = ModuleType("g77_256ke_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


K = load_adapted_kc_materializer()
M = K.M


def authenticate_kd_interface_before_presentation() -> dict[str, Any]:
    raw = (ROOT / KD_REDUCTION).read_bytes()
    if sha256_bytes(raw) != KD_REDUCTION_SHA256:
        raise KEBarrierError("KD_REDUCTION_IDENTITY_MISMATCH")
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope):
        raise KEBarrierError("KD_REDUCTION_NONCANONICAL")
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise KEBarrierError("KD_REDUCTION_SEAL_MISMATCH")
    if (
        reduction.get("terminal") != KD_TERMINAL
        or reduction.get("root_cause", {}).get("classification")
        != "OWNER_ROLE_PROJECTION_MISMATCH__KC_NAMESPACE_WRAPPER_ADDED_ONE_LAYER_WITHOUT_REBINDING_THE_REUSED_KA_CONTROLLER_CONTRACT"
        or reduction.get("post_repair", {}).get("post_repair_resolution")
        != "VERIFIED__CONTROLLER_MATERIALIZER_IS_K_AND_EXPECTED_CALL_RESOLVES_TO_K.A"
        or any(reduction.get("architecture", {}).get(key) != 0 for key in (
            "new_owner_count", "new_route_count", "new_registry_count",
            "new_generic_abstraction_count", "new_constitutional_concept_count",
        ))
        or reduction.get("architecture", {}).get("production_route_before") != 1
        or reduction.get("architecture", {}).get("production_route_after") != 1
    ):
        raise KEBarrierError("KD_REDUCTION_CONTRACT_MISMATCH")

    owner = K.K
    if K.M is not owner.M:
        raise KEBarrierError("KE_MATERIALIZER_OWNER_PROJECTION_MISMATCH")
    entry_adapter = getattr(owner, "A", None)
    entry = getattr(entry_adapter, "authenticate_entry", None)
    authoritative_entry = getattr(getattr(entry_adapter, "M", None), "authenticate_entry", None)
    if (
        not callable(entry)
        or entry is not authoritative_entry
        or tuple(inspect.signature(entry).parameters) != ("remote_head", "nested_remote_tag")
    ):
        raise KEBarrierError("KE_ENTRY_AUTHENTICATION_OWNER_MISMATCH")
    interfaces: dict[str, list[str]] = {}
    for name in ("authenticate_jz", "authenticate_e05_frontier"):
        function = getattr(owner, name, None)
        if not callable(function) or inspect.signature(function).parameters:
            raise KEBarrierError(f"KE_PHASE_B_MATERIALIZER_INTERFACE_MISMATCH:{name}")
        interfaces[name] = []

    tree = ast.parse((ROOT / WRAPPER_PATH).read_text(encoding="utf-8"))
    functions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    forbidden = {"select_owner", "fallback_owner", "register_owner", "register_route"}
    if functions & forbidden:
        raise KEBarrierError("KE_FALLBACK_SELECTOR_OR_PARALLEL_OWNER_DETECTED")
    return {
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "repository_head": HEAD,
        "repository_tree": TREE,
        "kd_terminal": KD_TERMINAL,
        "kd_reduction_file_sha256": KD_REDUCTION_SHA256,
        "root_cause": reduction["root_cause"]["classification"],
        "wrapper_identity": WRAPPER_PATH.as_posix(),
        "wrapper_file_sha256": sha256_path(ROOT / WRAPPER_PATH),
        "intended_existing_owner": "KE_MATERIALIZER.K__ADAPTED_KA_CONTRACT",
        "controller_materializer_binding": "VERIFIED__CONTROLLER_MATERIALIZER_IS_K",
        "expected_interface": "MATERIALIZER.A.authenticate_entry(remote_head, nested_remote_tag)",
        "resolved_interface": "K.A.authenticate_entry(remote_head, nested_remote_tag)",
        "authoritative_function_identity": "K.A.authenticate_entry_IS_K.A.M.authenticate_entry",
        "argument_names": list(inspect.signature(entry).parameters),
        "required_reused_interfaces": interfaces,
        "fallback_selector_parallel_owner": "VERIFIED__ABSENT",
        "preflight_order": "VERIFIED__BEFORE_MATERIALIZE_AND_HUMAN_PRESENTATION",
        "operational_counters": M.zero_counters(),
    }


def materialize_kd_preflight(proof: dict[str, Any]) -> dict[str, Any]:
    proof = {
        "schema_id": "G77_256KE_KD_INTERFACE_PREFLIGHT_V1",
        "generation_identity": M.GENERATION,
        "operation_identity": M.OPERATION,
        **proof,
    }
    envelope = {
        "schema_id": "G77_256KE_KD_INTERFACE_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KE / "G77_256KE_KD_INTERFACE_PREFLIGHT_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "result": "PASS__KE_ADAPTED_CONTROLLER_MATERIALIZER_CHAIN_PRESERVES_KD_INTERFACE",
        "scope": "REPOSITORY_PREFLIGHT_ONLY__NOT_AUTHORITY__NOT_OPERATIONAL_PROOF",
    }


def augment_namespace_preflight(preflight: dict[str, Any]) -> dict[str, Any]:
    """Add the KE-required unrelated-namespace negative to the reused KB set."""

    path = ROOT / preflight["path"]
    envelope = load_canonical(path)
    proof = envelope["proof"]
    owner = K.load_module(ROOT / K.FM_OWNER, "g77_256ke_unrelated_namespace_owner")
    context = load_canonical(
        KE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    )
    unrelated = (
        ROOT / ".github/governance/evidence/unrelated_namespace/operation_state"
    )
    proof["negative_rejections"]["unrelated_namespace"] = K.rejection(
        owner, context, unrelated
    )
    proof["negative_rejection_count"] = len(proof["negative_rejections"])
    reseal(envelope, "proof")
    write_canonical(path, envelope)
    preflight.update({
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
    })
    return preflight


def bind_kd_preflight_into_phase_a(preflight: dict[str, Any]) -> None:
    readiness_path = KE / "G77_256KE_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KE / "G77_256KE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KE / "G77_256KE_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KE / "G77_256KE_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KE / "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    readiness = load_canonical(readiness_path)
    readiness["checkpoint"]["kd_interface_preflight"] = preflight
    reseal(readiness, "checkpoint")
    write_canonical(readiness_path, readiness)

    request = load_canonical(request_path)
    request["request"]["preauthorization"].update({
        "checkpoint_file_sha256": sha256_path(readiness_path),
        "checkpoint_inner_sha256": readiness["checkpoint_sha256"],
    })
    reseal(request, "request")
    write_canonical(request_path, request)

    presentation = M.GN.render_human_authorization_presentation(request_path)
    presentation_path.write_bytes(presentation)
    gn_result = M.GN.validate_human_authorization_presentation(request_path, presentation)
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
        "terminal": KE_TERMINAL,
        "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
        "readiness_checkpoint_inner_sha256": readiness["checkpoint_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "request_identity": request["request_sha256"],
        "presentation_identity": sha256_path(presentation_path),
        "equivalence_file_sha256": sha256_path(equivalence_path),
        "equivalence_inner_sha256": equivalence["proof_sha256"],
        "kd_interface_preflight": preflight,
    })
    reseal(safe_stop, "checkpoint")
    write_canonical(safe_stop_path, safe_stop)

    reduction = load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KE_TERMINAL
    value["kd_interface_preflight"] = preflight
    value["owner_results"]["kd_interface_preflight"] = preflight["result"]
    value["identities"].update({
        "request_sha256": request["request_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "presentation_sha256": sha256_path(presentation_path),
        "readiness_checkpoint_sha256": readiness["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(readiness_path),
        "checkpoint_sha256": safe_stop["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(safe_stop_path),
        "kd_interface_preflight_sha256": preflight["inner_sha256"],
        "kd_interface_preflight_file_sha256": preflight["file_sha256"],
    })
    value["governance_dashboard"].update({
        "project_progress": "VERIFIED__KE_FRESH_EXPIRED_PREAUTHORIZATION_AND_PREFLIGHT_MATERIALIZED",
        "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_READY_FOR_ONE_EXPLICIT_BOUND_KE_HUMAN_DECISION",
        "constitutional_health_evidence": "VERIFIED__KD_INTERFACE_AND_KB_NAMESPACE_PREFLIGHTS_AUTHORITY_SEPARATION_ZERO_OPERATION_AND_ONE_ROUTE_PRESERVED",
        "constitutional_continuation_progress": "VERIFIED__KD_TO_KE_PREAUTHORIZATION_SAFE_STOP",
    })
    value["governance_dashboard"]["candidate_capability"] = (
        "VERIFIED__EXACT_KE_EXPIRED_OPERATION_CANDIDATE_AT_HUMAN_BARRIER"
    )
    value["frontier"] = {
        "last_verified_edge": "FRESH_KE_EXPIRED_PREAUTHORIZATION_AND_ALL_REQUIRED_PREFLIGHTS_READY",
        "first_broken_edge": "EXACT_FRESH_KE_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KE_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "SAME_GENERATION_SPCE_PHASE_B_ONLY_AFTER_EXPLICIT_HUMAN_ACT",
    }
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__1_PREAUTHORIZATION_CAPABILITY",
        "new_blocker_localized_count": "VERIFIED__0",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"].update({
        "existing_certified_capabilities_reused": "EX_17_OF_17__KD__KB__JZ__JX__JR__GN__FM__GL__ER__P11__KA_KC_HISTORY__LAYER_0__PINNED_NESTED_AUTHORITY",
        "new_capabilities": "VERIFIED__1__FRESH_KE_PREAUTHORIZATION_CAPABILITY__NONAUTHORITY",
    })
    reseal(reduction, "reduction")
    write_canonical(reduction_path, reduction)


def materialize_human_decision_presentation() -> Path:
    """Render the outer Human-decision view without changing GN-owned bytes."""

    reduction = load_canonical(
        KE / "G77_256KE_PREHUMAN_PHASE_A_REDUCTION_V1.json"
    )["reduction"]
    identities = reduction["identities"]
    lines = [
        "G77-256KE HUMAN DECISION PRESENTATION V1",
        "NONAUTHORITY: review only; one new explicit Human act is required.",
        f"GENERATION {reduction['generation_identity']}",
        f"OPERATION {reduction['operation_identity']}",
        f"CANDIDATE_SHA256 {identities['candidate_sha256']}",
        f"CONTEXT {identities['context_sha256']}",
        f"CONTEXT_FILE_SHA256 {identities['context_file_sha256']}",
        f"CANONICAL_ARGV_SHA256 {identities['canonical_argv_sha256']}",
        f"TEMPORAL_BINDING {identities['temporal_binding_sha256']}",
        f"REQUEST_IDENTITY {identities['request_sha256']}",
        f"REQUEST_FILE_SHA256 {identities['request_file_sha256']}",
        f"PRESENTATION_SHA256 {identities['presentation_sha256']}",
        f"READINESS_CHECKPOINT {identities['readiness_checkpoint_sha256']}",
        f"SAFE_STOP_CHECKPOINT {identities['checkpoint_sha256']}",
        "E05 VERIFIED__11_OF_18",
        "EXPECTED_RESULT EXPIRED denial before P11 entry",
        "OPERATIONAL_STATUS NOT_PROVEN until operationally observed",
        "HUMAN_AUTHORITY NOT_SUPPLIED",
        "AUTO_CONTINUABLE NO",
        "HUMAN_REVIEW_REQUIRED YES",
        "STOP AT HUMAN AUTHORITY BARRIER.",
        "",
    ]
    path = KE / "G77_256KE_HUMAN_DECISION_PRESENTATION_V1.txt"
    if path.exists() or path.is_symlink():
        raise KEBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    kd_proof = authenticate_kd_interface_before_presentation()
    kb_result = K.authenticate_kb()
    jz_result = K.K.authenticate_jz()
    e05_frontier_result = K.K.authenticate_e05_frontier()
    M.materialize(arguments)
    namespace_result = augment_namespace_preflight(
        K.materialize_namespace_preflight(kb_result)
    )
    jz_readiness = K.K.materialize_jz_readiness(jz_result)
    K.K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    K.bind_namespace_into_phase_a(kb_result, namespace_result)
    kd_result = materialize_kd_preflight(kd_proof)
    bind_kd_preflight_into_phase_a(kd_result)
    materialize_human_decision_presentation()
    print(KE_TERMINAL)
