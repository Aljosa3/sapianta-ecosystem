#!/usr/bin/env python3
"""Materialize the nonauthority KC EXPIRED Phase-A Human barrier.

The committed KA Phase-A construction is authenticated and adapted only for
fresh KC-local identities and the committed KB entry checkpoint.  The exact
KC operation namespace is then passed through the current KB-repaired guest
context owner before presentation.  No Human authority is created or consumed
and no PRE, FM operation, QEMU, VM, request, denial, or P11 path is invoked.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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
KC = ROOT / (
    ".github/governance/evidence/"
    "g77_256kc_fresh_expired_operational_recommissioning_v1"
)
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "2b0a1ff1d7bc3e071392a786dfb64c2eac392df3"
TREE = "2b7e42af265f20404ad467c6f1069df56cc388f8"
SUBJECT = "G77-256KB verify EXPIRED guest namespace binding repair"
KA_MATERIALIZER = Path(
    ".github/governance/evidence/"
    "g77_256ka_fresh_expired_operational_recommissioning_v1/orchestration/"
    "G77_256KA_PREAUTHORIZATION_MATERIALIZER_V1.py"
)
KA_MATERIALIZER_SHA256 = (
    "55063bb55944cf2a44874667c6d2cde6d18135754afa36071b88899cba718263"
)
KB_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256kb_expired_guest_context_namespace_binding_repair_v1"
)
KB_REDUCTION = KB_ROOT / "G77_256KB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
KB_REPORT = KB_ROOT / "G77_256KB_G48_IMPLEMENTATION_REPORT_V1.md"
KB_FORMALIZER = KB_ROOT / "analysis/G77_256KB_NAMESPACE_BINDING_FORMALIZER_V1.py"
KB_TEST = KB_ROOT / "tests/test_g77_256kb_namespace_binding_v1.py"
FM_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
KB_HASHES = {
    KB_REDUCTION: "5510a20044fbf21f30a0f3cd53f60bc599fee1dee56d0b4693ee6c82d5a0fbca",
    KB_REPORT: "723d66e5e4f5ad702400cc8d4850686a58da9a3e375861979363667d6b46aee1",
    KB_FORMALIZER: "d9c9a47e7a568bb32168c4d3cea8c5bb60c0013f357b9e89199dfc01dc394de4",
    KB_TEST: "e5e5cb075892d8306e1265bdc08265455adfa3875e1621f150091b5efbb57323",
    FM_OWNER: "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b",
    FM_LAUNCHER: "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36",
}
KB_TERMINAL = "A__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_REPOSITORY_VERIFIED"
KC_TERMINAL = (
    "A__FRESH_KC_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
)
KC_NAMESPACE = "g77_256kc_fresh_expired_operational_recommissioning_v1"
HISTORICAL_NAMESPACE = "g77_256kc_expired_operational_v1"


class KCBarrierError(RuntimeError):
    """One deterministic fail-closed KC Phase-A error."""


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
        raise KCBarrierError(f"NONCANONICAL_JSON:{path}")
    return value


def reseal(envelope: dict[str, Any], inner: str) -> None:
    value = envelope.get(inner)
    if not isinstance(value, dict):
        raise KCBarrierError(f"MISSING_INNER:{inner}")
    envelope[f"{inner}_sha256"] = sha256_bytes(canonical_bytes(value))


def write_canonical(path: Path, value: dict[str, Any], *, fresh: bool = False) -> None:
    if fresh and (path.exists() or path.is_symlink()):
        raise KCBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise KCBarrierError(f"MODULE_UNAVAILABLE:{path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_adapted_ka_materializer() -> ModuleType:
    path = ROOT / KA_MATERIALIZER
    raw = path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{HEAD}:{KA_MATERIALIZER}"], cwd=ROOT)
    if raw != committed or sha256_bytes(raw) != KA_MATERIALIZER_SHA256:
        raise KCBarrierError("COMMITTED_KA_PREAUTHORIZATION_OWNER_MISMATCH")
    source = raw.decode("utf-8").replace("KA", "KC").replace("ka", "kc")
    source = source.replace(
        "g77_256kc_fresh_expired_operational_recommissioning_v1",
        KC_NAMESPACE,
    )
    source = source.replace("128bb145969a7b9ccebb8812b24216e00c7db04c", HEAD)
    source = source.replace("47d09bc1d2ecf0529601ba65085651d01c325a7c", TREE)
    source = source.replace(
        "G77-256JZ verify FM authority digest preconsumption binding", SUBJECT
    )
    source = source.replace(
        "97f1cb4dc4e9da7fd70efcc2a2713defd71e7aa7152f5dfc81229d7b738cbe29",
        KB_HASHES[FM_LAUNCHER],
    )
    module = ModuleType("g77_256kc_authenticated_preauthorization_owner")
    module.__file__ = str(Path(__file__).resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


K = load_adapted_ka_materializer()
M = K.M
M.KC = KC
M.LIVE = KC / "live_binding"
M.OPERATION_ROOT = KC / "operation_state"
M.TRANSIENT_ROOT = Path("/tmp/g77_256kc_fresh_expired_operational_recommissioning_v1")


def authenticate_kb() -> dict[str, Any]:
    identities: dict[str, str] = {}
    for relative, expected in KB_HASHES.items():
        path = ROOT / relative
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{relative}"], cwd=ROOT)
        if path.read_bytes() != committed or sha256_path(path) != expected:
            raise KCBarrierError(f"COMMITTED_KB_DEPENDENCY_MISMATCH:{relative}")
        identities[relative.as_posix()] = expected
    envelope = load_canonical(ROOT / KB_REDUCTION)
    reduction = envelope.get("reduction", {})
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        raise KCBarrierError("KB_REDUCTION_SEAL_MISMATCH")
    namespace = reduction.get("namespace_binding", {})
    if (
        reduction.get("terminal") != KB_TERMINAL
        or reduction.get("candidate_capability")
        != "VERIFIED__EXPIRED_GUEST_CONTEXT_NAMESPACE_BINDING_COMPATIBILITY_REPOSITORY_ONLY"
        or namespace.get("root_cause_classification")
        != "OVERLY_NARROW_GUEST_OWNER_VALIDATION__VECTOR_FIRST_ONLY_RULE_OMITTED_GOVERNED_FRESHNESS_QUALIFIED_FORM"
        or namespace.get("post_repair_owner_sha256") != KB_HASHES[FM_OWNER]
        or reduction.get("reuse", {}).get("ex_reused") != "VERIFIED__17_OF_17"
        or reduction.get("reuse", {}).get("ex_reconstructed") != "VERIFIED__0"
    ):
        raise KCBarrierError("KB_CONTRACT_MISMATCH")
    return {
        "terminal": KB_TERMINAL,
        "capability": reduction["candidate_capability"],
        "root_cause_classification": namespace["root_cause_classification"],
        "artifact_hashes": identities,
        "owner_sha256": KB_HASHES[FM_OWNER],
        "launcher_sha256": KB_HASHES[FM_LAUNCHER],
        "ka_terminal": (
            "M__KA_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CONTEXT_"
            "NAMESPACE_BINDING_BEFORE_REQUEST"
        ),
        "ka_authority": "CONSUMED__NONREUSABLE__NONTRANSFERABLE",
        "kb_scope": "REPOSITORY_ONLY__NOT_OPERATIONAL_EXPIRED_PROOF",
    }


def rejection(owner: ModuleType, context: dict[str, Any], operation_root: Path) -> str:
    try:
        owner._derive_sealed_host_repository_root(context, operation_root)
    except owner.ContextError as exc:
        return str(exc)
    raise KCBarrierError(f"NEGATIVE_NAMESPACE_ACCEPTED:{operation_root}")


def materialize_namespace_preflight(kb: dict[str, Any]) -> dict[str, Any]:
    owner = load_module(ROOT / FM_OWNER, "g77_256kc_current_context_owner")
    context_path = KC / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context = load_canonical(context_path)
    exact_root = KC / "operation_state"
    projection = owner.validate_sealed_canonical_argv(
        context, validation_repository_root=owner.GUEST_REPOSITORY_ROOT
    )
    if (
        Path(context["operation_evidence_root"]) != exact_root
        or exact_root.parent.name != KC_NAMESPACE
        or projection.get("projection_status") != "EXACT_GUEST_PROJECTION"
        or projection.get("host_canonical_identity") != str(ROOT)
    ):
        raise KCBarrierError("EXACT_KC_NAMESPACE_PREFLIGHT_MISMATCH")
    historical_root = ROOT / ".github/governance/evidence" / HISTORICAL_NAMESPACE / "operation_state"
    if owner._derive_sealed_host_repository_root(context, historical_root) != ROOT:
        raise KCBarrierError("HISTORICAL_NAMESPACE_REGRESSION")
    evidence = ROOT / ".github/governance/evidence"
    negatives = {
        "wrong_vector": rejection(owner, context, evidence / "g77_256kc_fresh_future_operational_v1" / "operation_state"),
        "wrong_generation": rejection(owner, context, evidence / "g77_256kb_fresh_expired_operational_v1" / "operation_state"),
        "malformed_namespace": rejection(owner, context, evidence / "g77_256kc" / "operation_state"),
        "empty_namespace": rejection(owner, context, evidence / "" / "operation_state"),
        "prefix_only": rejection(owner, context, evidence / "g77_256kc" / "operation_state"),
        "projection_root_mismatch": rejection(owner, context, KC / "runtime_export"),
        "runtime_role_confusion": rejection(owner, context, exact_root / "extra"),
    }
    proof = {
        "schema_id": "G77_256KC_KB_NAMESPACE_PREFLIGHT_V1",
        "artifact_class": "REPOSITORY_PREFLIGHT__NONAUTHORITY__NONOPERATIONAL",
        "generation_identity": M.GENERATION,
        "operation_identity": M.OPERATION,
        "repository_head": HEAD,
        "repository_tree": TREE,
        "actual_namespace": KC_NAMESPACE,
        "operation_evidence_root": str(exact_root),
        "context_path": context_path.relative_to(ROOT).as_posix(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "repository_marker": "/".join(owner.REPOSITORY_EVIDENCE_MARKER),
        "host_runtime_role": "HOST_ADMISSION_TO_GUEST_PROJECTION__JR_RUNTIME_CHECKOUT_DISTINCT",
        "seed_repository_agreement": "VERIFIED__IMMUTABLE_CONTEXT_BINDINGS",
        "context_seal": "VERIFIED",
        "canonical_argv_binding": "VERIFIED",
        "immutable_binding_checks": "VERIFIED",
        "current_owner_sha256": sha256_path(ROOT / FM_OWNER),
        "current_launcher_sha256": sha256_path(ROOT / FM_LAUNCHER),
        "exact_kc_result": projection,
        "historical_accepted_namespace": HISTORICAL_NAMESPACE,
        "historical_accepted_result": "VERIFIED__ACCEPTED",
        "negative_rejections": negatives,
        "negative_rejection_count": len(negatives),
        "same_owner_relation_to_ka": "VERIFIED__CURRENT_KB_REPAIRED_OWNER_SUCCEEDS_OWNER_THAT_REJECTED_KA",
        "proof_scope": "REPOSITORY_PREFLIGHT_ONLY__NOT_OPERATIONAL_EXPIRED_PROOF",
        "operational_counters": M.zero_counters(),
        "kb_authentication": kb,
    }
    envelope = {
        "schema_id": "G77_256KC_KB_NAMESPACE_PREFLIGHT_ENVELOPE_V1",
        "proof": proof,
        "proof_sha256": sha256_bytes(canonical_bytes(proof)),
    }
    path = KC / "G77_256KC_KB_NAMESPACE_PREFLIGHT_V1.json"
    write_canonical(path, envelope, fresh=True)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "file_sha256": sha256_path(path),
        "inner_sha256": envelope["proof_sha256"],
        "actual_namespace": KC_NAMESPACE,
        "result": "PASS__CURRENT_KB_REPAIRED_OWNER_ACCEPTED_EXACT_KC_NAMESPACE",
        "scope": proof["proof_scope"],
    }


def bind_namespace_into_phase_a(kb: dict[str, Any], preflight: dict[str, Any]) -> None:
    checkpoint_path = KC / "G77_256KC_PREAUTHORIZATION_READINESS_CHECKPOINT_V1.json"
    request_path = KC / "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = KC / "G77_256KC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    equivalence_path = KC / "G77_256KC_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    safe_stop_path = KC / "G77_256KC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    reduction_path = KC / "G77_256KC_PREHUMAN_PHASE_A_REDUCTION_V1.json"

    checkpoint = load_canonical(checkpoint_path)
    checkpoint["checkpoint"]["kb_namespace_preflight"] = preflight
    reseal(checkpoint, "checkpoint")
    write_canonical(checkpoint_path, checkpoint)

    request = load_canonical(request_path)
    request["request"]["preauthorization"].update({
        "checkpoint_file_sha256": sha256_path(checkpoint_path),
        "checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
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
    stop = safe_stop["checkpoint"]
    stop.update({
        "terminal": KC_TERMINAL,
        "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
        "readiness_checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "request_identity": request["request_sha256"],
        "presentation_identity": sha256_path(presentation_path),
        "equivalence_file_sha256": sha256_path(equivalence_path),
        "equivalence_inner_sha256": equivalence["proof_sha256"],
        "kb_namespace_preflight": preflight,
    })
    reseal(safe_stop, "checkpoint")
    write_canonical(safe_stop_path, safe_stop)

    reduction = load_canonical(reduction_path)
    value = reduction["reduction"]
    value["terminal"] = KC_TERMINAL
    value["kb_authentication"] = kb
    value["kb_namespace_preflight"] = preflight
    value["owner_results"]["kb_namespace_preflight"] = preflight["result"]
    value["identities"].update({
        "request_sha256": request["request_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "presentation_sha256": sha256_path(presentation_path),
        "readiness_checkpoint_sha256": checkpoint["checkpoint_sha256"],
        "readiness_checkpoint_file_sha256": sha256_path(checkpoint_path),
        "checkpoint_sha256": safe_stop["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(safe_stop_path),
        "kb_namespace_preflight_sha256": preflight["inner_sha256"],
        "kb_namespace_preflight_file_sha256": preflight["file_sha256"],
    })
    value["proof_yield"] = {
        "new_verified_capability_count": "VERIFIED__1_PREAUTHORIZATION_CAPABILITY",
        "new_blocker_localized_count": "VERIFIED__0",
        "e05_credit": "VERIFIED__0",
        "proof_reuse_count": "VERIFIED__17",
    }
    value["reuse_impact_assessment"].update({
        "existing_certified_capabilities_reused": "EX_17_OF_17__JZ__JX__JT__JR__JV_GN__FM__GL__ER__P11__KA_HISTORY__KB_REPAIR__LAYER_0__PINNED_NESTED_AUTHORITY",
        "new_capabilities": "VERIFIED__1__FRESH_KC_PREAUTHORIZATION_CAPABILITY__NONAUTHORITY",
    })
    value["governance_dashboard"].update({
        "project_progress": "VERIFIED__KC_FRESH_EXPIRED_PREAUTHORIZATION_AND_NAMESPACE_PREFLIGHT_MATERIALIZED",
        "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_READY_FOR_ONE_EXPLICIT_BOUND_KC_HUMAN_DECISION",
        "constitutional_health_evidence": "VERIFIED__KB_NAMESPACE_PREFLIGHT_AUTHORITY_SEPARATION_ZERO_OPERATION_AND_ONE_ROUTE_PRESERVED",
        "cognition_assisted_handoff": "VERIFIED__CROSS_ACCOUNT_REPOSITORY_ONLY_HANDOFF",
        "constitutional_continuation_progress": "VERIFIED__KB_TO_KC_PREAUTHORIZATION_SAFE_STOP",
    })
    value["frontier"] = {
        "last_verified_edge": "FRESH_KC_EXPIRED_PREAUTHORIZATION_AND_KB_NAMESPACE_PREFLIGHT_READY",
        "first_broken_edge": "EXACT_FRESH_KC_HUMAN_AUTHORIZATION_NOT_YET_SUPPLIED",
        "minimum_missing_capability": "EXACT_FRESH_HUMAN_AUTHORIZATION_FOR_BOUND_KC_EXPIRED_OPERATION",
        "minimum_legal_next_delta": "SAME_GENERATION_SPCE_PHASE_B_ONLY_AFTER_EXPLICIT_HUMAN_ACT",
    }
    reseal(reduction, "reduction")
    write_canonical(reduction_path, reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    kb_result = authenticate_kb()
    jz_result = K.authenticate_jz()
    e05_frontier_result = K.authenticate_e05_frontier()
    M.materialize(arguments)
    namespace_result = materialize_namespace_preflight(kb_result)
    jz_readiness = K.materialize_jz_readiness(jz_result)
    K.finalize_phase_a(jz_result, jz_readiness, e05_frontier_result)
    bind_namespace_into_phase_a(kb_result, namespace_result)
    print(KC_TERMINAL)
