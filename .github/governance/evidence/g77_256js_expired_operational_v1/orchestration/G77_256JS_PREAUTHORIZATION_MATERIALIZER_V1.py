#!/usr/bin/env python3
"""Materialize the nonauthority G77-256JS EXPIRED Human barrier.

The executable surface authenticates the committed JR capability, reuses the
existing FM/GL/GN owners, materializes one exact operation context without
invoking QEMU, renders the sealed Human presentation, and stops.  It contains
no authority-consumption or operational-launch call.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
JS = ROOT / ".github/governance/evidence/g77_256js_expired_operational_v1"
LIVE = JS / "live_binding"
OPERATION_ROOT = JS / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256js_expired_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
SUBJECT = "G77-256JR bind EXPIRED Human-authority materialization and presentation"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

PREFIX = "G77_256JS"
VECTOR = "EXPIRED"
GENERATION = PREFIX + "_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = PREFIX + "_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
JR_TERMINAL = "A__EXPIRED_HUMAN_AUTHORITY_MATERIALIZATION_AND_PRESENTATION_BINDING_REPOSITORY_VERIFIED"

JR_ROOT = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1"
)
JR_REDUCTION = JR_ROOT / "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JR_ADAPTER = JR_ROOT / "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
JR_CLOUD_INIT = JR_ROOT / "static/G77_256JR_CLOUD_INIT_USER_DATA_V1.yaml"
JR_SEED = JR_ROOT / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V1.img"
FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GL_PATH = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
GN_PATH = Path(
    ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/"
    "presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)

EXPECTED_JR_HASHES = {
    JR_ADAPTER: "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2",
    JR_CLOUD_INIT: "bcf626825e5d253fd0d6ae3af33f8ed26ad2d6b405d1203294c196eae1b421ee",
    JR_SEED: "47a79fe9b4dad751ab232789465753fabd27ff7db2443f3af3a99058e48fb516",
}


class JSBarrierError(RuntimeError):
    """One deterministic fail-closed preauthorization error."""


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JSBarrierError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256js_fm")
GL = load_module(GL_PATH, "g77_256js_gl")
GN = load_module(GN_PATH, "g77_256js_gn")


def canonical_bytes(value: Any) -> bytes:
    return FM.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sealed(schema: str, inner_name: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: value,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(value)),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise JSBarrierError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "tracked_worktree_clean": git(
            "status", "--porcelain", "--untracked-files=no"
        ) == "",
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "worktree_clean_before_first_mutation": True,
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
        "remote_head": HEAD,
        "tracked_worktree_clean": True,
        "index_empty": True,
    }
    if any(observed[key] != value for key, value in expected.items()):
        raise JSBarrierError("EXACT_RATIFIED_JR_ENTRY_MISMATCH")
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        if not line.startswith("?? " + JS.relative_to(ROOT).as_posix() + "/"):
            raise JSBarrierError("JS_BOUNDED_WORKTREE_SCOPE_VIOLATION")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"],
        cwd=ROOT,
        check=False,
    ).returncode:
        raise JSBarrierError("CONSTITUTIONAL_ANCESTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "remote_tag": nested_remote_tag,
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
        "remote_tag": NESTED_HEAD,
    }:
        raise JSBarrierError("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "direct_remote_equality": "VERIFIED",
        "nested_authority": nested_state,
    }


def authenticate_jr() -> dict[str, Any]:
    raw = (ROOT / JR_REDUCTION).read_bytes()
    envelope = json.loads(raw)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != sha256_bytes(
        canonical_bytes(reduction)
    ):
        raise JSBarrierError("JR_TERMINAL_REDUCTION_SEAL_MISMATCH")
    if reduction.get("terminal") != JR_TERMINAL:
        raise JSBarrierError("JR_TERMINAL_MISMATCH")
    if reduction.get("e05") != {
        "after": "VERIFIED__11_OF_18",
        "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }:
        raise JSBarrierError("JR_E05_MISMATCH")
    if set(reduction.get("operational_counters", {}).values()) != {"VERIFIED__0"}:
        raise JSBarrierError("JR_OPERATIONAL_COUNTER_MISMATCH")
    reuse = reduction.get("reuse", {})
    if reuse.get("ex_reused") != "VERIFIED__17_OF_17" or reuse.get(
        "ex_reconstructed"
    ) != "VERIFIED__0":
        raise JSBarrierError("JR_EX_REUSE_MISMATCH")
    route = reduction.get("route_binding", {})
    if (
        route.get("derived_vector") != VECTOR
        or route.get("production_route_before") != "VERIFIED__1"
        or route.get("production_route_after") != "VERIFIED__1"
        or route.get("production_route_delta") != "VERIFIED__0"
        or route.get("adapter_source_sha256") != EXPECTED_JR_HASHES[JR_ADAPTER]
        or route.get("preclaim_coordinate_unix_ns") != 1000
    ):
        raise JSBarrierError("JR_ROUTE_BINDING_MISMATCH")
    for path, expected_hash in EXPECTED_JR_HASHES.items():
        committed = subprocess.check_output(["git", "show", f"{HEAD}:{path}"], cwd=ROOT)
        if committed != (ROOT / path).read_bytes() or sha256_bytes(committed) != expected_hash:
            raise JSBarrierError(f"JR_COMMITTED_ASSET_MISMATCH:{path}")
    return {
        "terminal": JR_TERMINAL,
        "capability": (
            "VERIFIED__EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_"
            "MATERIALIZATION_AND_PRESENTATION_REPOSITORY_CAPABILITY"
        ),
        "terminal_file_sha256": sha256_bytes(raw),
        "terminal_inner_sha256": envelope["reduction_sha256"],
        "ex_reused": reuse["ex_reused"],
        "ex_reconstructed": reuse["ex_reconstructed"],
        "route": route,
        "human_authority_assurance_status": reduction[
            "human_authority_assurance_status"
        ],
    }


def authenticate_expired_semantics() -> dict[str, Any]:
    adapter = load_module(JR_ADAPTER, "g77_256js_expired_adapter")
    coordinates = adapter.authenticate_expired_semantics(ROOT)
    expected = {
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
    }
    if coordinates != expected:
        raise JSBarrierError("EXPIRED_COORDINATE_MISMATCH")
    transformed = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix=PREFIX
    )
    required = (
        'denial_error == "one-use Human act expired before PRECLAIM"',
        'after.state.value == "EXPIRED"',
        "after.revision == 1",
        "differing_fields == []",
    )
    if not all(token in transformed for token in required):
        raise JSBarrierError("EXPIRED_SPECIALIZATION_MISMATCH")
    return {
        "vector": VECTOR,
        "submission_time_unix_ns": 500,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
        "governed_preclaim_coordinate_unix_ns": 1000,
        "truth_table": {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"},
        "expected_owner_transition": "AVAILABLE_TO_EXPIRED",
        "expected_owner_revision_transition": "0_TO_1",
        "expected_denial_reason": "one-use Human act expired before PRECLAIM",
        "expected_denial_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        "wall_clock_is_governed_preclaim_authority": False,
        "caller_selectable_coordinate_count": 0,
        "provider_selectable_coordinate_count": 0,
        "human_selectable_coordinate_count": 0,
    }


def zero_counters() -> dict[str, int]:
    return {
        "operational_authorization": 0,
        "authority_consumption": 0,
        "pre_operational": 0,
        "fm_operational_invocation": 0,
        "qemu": 0,
        "vm": 0,
        "operation_attempt": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
    }


def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise JSBarrierError("JS_ONE_SHOT_NAMESPACE_NOT_FRESH")
    entry = authenticate_entry(args.remote_head, args.nested_remote_tag)
    jr = authenticate_jr()
    expired = authenticate_expired_semantics()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )

    source_candidate = ROOT / FM.CANDIDATE
    if sha256_path(source_candidate) != FM.CANDIDATE_SHA256:
        raise JSBarrierError("FM_CANONICAL_CANDIDATE_MISMATCH")
    candidate = LIVE / "candidate" / source_candidate.name
    runtime = LIVE / "runtime_projection" / source_candidate.name
    candidate.parent.mkdir(parents=True, exist_ok=False)
    runtime.parent.mkdir(parents=True, exist_ok=False)
    candidate.write_bytes(source_candidate.read_bytes())
    runtime.write_bytes(source_candidate.read_bytes())
    if candidate.read_bytes() != runtime.read_bytes():
        raise JSBarrierError("CANDIDATE_RUNTIME_BYTE_MISMATCH")

    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=HEAD,
        repository_tree=TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=OPERATION_ROOT,
        transient_root=TRANSIENT_ROOT,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    if context["preclaim_temporal_binding"]["coordinate_unix_ns"] != 1000:
        raise JSBarrierError("CONTEXT_PRECLAIM_COORDINATE_MISMATCH")
    context_path = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    write_json(context_path, context)
    destination = FM.preauth_fresh_checkout_destination_readiness(ROOT, context)
    operation_materialization = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=context_path,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    observations = FM.observe_context_assets(ROOT, context, candidate.relative_to(ROOT))
    readiness = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HEAD,
        observed_tree=TREE,
        repository_clean=git("status", "--porcelain", "--untracked-files=no") == "",
        observed_asset_sha256=observations,
        candidate_source_path=candidate.relative_to(ROOT),
    )
    static = sealed(
        "G77_256JS_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JS_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded,
            "entry": entry,
            "jr_reconstruction": jr,
            "expired_semantics": expired,
            "candidate_source": FM.CANDIDATE,
            "candidate_source_sha256": sha256_path(source_candidate),
            "destination_readiness": destination,
            "materialization": operation_materialization,
            "asset_observations": observations,
            "readiness": readiness,
            "human_operational_authority": 0,
            "operational_execution_count": 0,
        },
    )
    static_path = JS / "G77_256JS_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = JS / "G77_256JS_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    gl_result = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, observation, gl_checkpoint
    )
    equivalence = sealed(
        "G77_256JS_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JS_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            **gl_result,
        },
    )
    equivalence_path = JS / "G77_256JS_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
    write_json(equivalence_path, equivalence)

    counters = zero_counters()
    checkpoint_inner = {
        "schema_id": "G77_256JS_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "jr_terminal_reconstruction": jr,
        "expired_semantics": expired,
        "identities": {
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "fm_launcher_sha256": sha256_path(ROOT / FM_PATH),
            "expired_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
            "temporal_binding_sha256": sha256_bytes(
                canonical_bytes(context["preclaim_temporal_binding"])
            ),
            "p11_consumer_path": FM.P11_CONSUMER_RELATIVE,
        },
        "authority_boundary": {
            "authority_state": "NOT_GRANTED",
            "checkpoint_is_authority": False,
            "request_is_authority": False,
            "prompt_is_authority": False,
            "provider_capability_is_authority": False,
            "human_review_required": True,
            "auto_continuable": False,
            "next_legal_phase": "PRESENT_EXACT_GN_DERIVED_REQUEST_AND_STOP_FOR_EXPLICIT_HUMAN_DECISION",
        },
        "one_shot_maxima": {
            "operational_authorization": 1,
            "authority_consumption": 1,
            "pre_operational": 1,
            "fm_operational_invocation": 1,
            "qemu": 1,
            "vm": 1,
            "operation_attempt": 1,
            "retry": 0,
            "repair_retry": 0,
            "replay": 0,
        },
        "operational_counters": counters,
        "e05": {"before": "11/18", "current": "11/18", "maximum_credit": 1},
        "preauthorization": {
            "static_readiness_result": readiness["result"],
            "static_readiness_file_sha256": sha256_path(static_path),
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "receipt_parent_observation_sha256": observation["observation_sha256"],
            "preauth_final_admission_equivalence_file_sha256": sha256_path(
                equivalence_path
            ),
            "preauth_final_admission_equivalence": gl_result[
                "preauth_final_admission_equivalence"
            ],
            "single_route_status": "VERIFIED",
        },
        "architecture": {
            "p11_implementation_mutation_count": 0,
            "production_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
        },
        "handoff_sufficiency": {
            "status": "VERIFIED",
            "state_completeness": "COMPLETE_FOR_PREGRANT_BARRIER",
            "authority_state": "NOT_GRANTED",
            "authority_consumed": False,
            "ambiguity_count": 0,
            "unauthenticated_assumption_count": 0,
        },
    }
    checkpoint = sealed(
        "G77_256JS_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint_inner,
    )
    checkpoint_path = JS / "G77_256JS_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    request_inner = {
        "schema_id": "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
        "recorded_at_utc": recorded,
        "request_class": "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository": {
            "branch": BRANCH,
            "head": HEAD,
            "tree": TREE,
            "remote_head": args.remote_head,
            "stable_ancestry_anchor": ANCHOR,
        },
        "immutable_assets": context["qemu_executable_base_seed_checkout_bindings"],
        "live_binding": {
            "candidate_sha256": sha256_path(candidate),
            "context_sha256": context["context_sha256"],
            "context_file_sha256": sha256_path(context_path),
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "du": "PASS",
            "eb": "PASS",
            "ee": "PASS",
            "candidate_semantics_changed": False,
            "candidate_binding_regeneration_required": True,
            "receipt_parent": context["receipt_parent"],
        },
        "preauthorization": {
            "static_readiness_file_sha256": sha256_path(static_path),
            "checkpoint_file_sha256": sha256_path(checkpoint_path),
            "checkpoint_inner_sha256": checkpoint["checkpoint_sha256"],
            "checkpoint_path": checkpoint_path.relative_to(ROOT).as_posix(),
            "complete_deterministic_readiness": "PASS",
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "preauth_final_admission_equivalence_file_sha256": sha256_path(
                equivalence_path
            ),
            "preauth_final_admission_equivalence": gl_result[
                "preauth_final_admission_equivalence"
            ],
            "gk_receipt_parent_false_positive_blocked": "YES",
            "all_operational_counters_zero": True,
        },
        "requested_authority_semantics": {
            "authorization_kind": "FRESH_HUMAN_CONSTITUTIONAL_OPERATIONAL_AUTHORIZATION",
            "explicit": True,
            "fresh": True,
            "one_shot": True,
            "reusable": False,
            "transferable": False,
            "generation_bound": True,
            "operation_bound": True,
            "head_bound": True,
            "tree_bound": True,
            "candidate_bound": True,
            "context_bound": True,
            "canonical_argv_bound": True,
            "checkpoint_bound": True,
            "authorization_request_bound": True,
            "governed_launcher_activation_limit": 1,
            "qemu_execution_limit": 1,
            "vm_boot_limit": 1,
            "operation_attempt_limit": 1,
            "network_authorized": False,
            "retry_limit": 0,
            "repair_limit": 0,
            "replay_limit": 0,
            "replacement_authority_authorized": False,
            "second_attempt_authorized": False,
            "successor_generation_authorized": False,
        },
        "authorized_vector_requested": VECTOR,
        "request_is_authority": False,
        "checkpoint_is_authority": False,
        "resource_capacity_is_authority": False,
        "provider_permission_is_authority": False,
        "provider_permission_confirmation_count": 0,
        "human_constitutional_authorization_count": 0,
        "human_terminal_review_count": 0,
        "governed_launcher_activations": 0,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "wrong_attempt_execution_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "pre_count": 0,
        "post_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_execution_count": 0,
        "replay_execution_count": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }
    request = sealed(
        "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request_inner,
    )
    request_path = JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise JSBarrierError("FRESH_PRESENTATION_COLLISION")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256JS_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256JS_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "request_path": request_path.relative_to(ROOT).as_posix(),
            "request_file_sha256": sha256_path(request_path),
            "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **gn_result,
            "authority_present": False,
            "auto_continuable": False,
        },
    )
    write_json(JS / "G77_256JS_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json", gn_proof)

    reduction = sealed(
        "G77_256JS_PREHUMAN_PHASE_A_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256JS_PREHUMAN_PHASE_A_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "terminal": "HUMAN_AUTHORIZATION_REQUIRED",
            "phase": "PREAUTHORIZATION_STOP",
            "entry": entry,
            "jr_reconstruction": jr,
            "expired_semantics": expired,
            "owner_results": {
                "ex": "PASS__17_OF_17_REUSED__0_RECONSTRUCTED",
                "fm_materialization": operation_materialization["result"],
                "fm_static_readiness": readiness["result"],
                "gl": gl_result["preauth_final_admission_equivalence"],
                "gn": gn_result["human_presentation_request_equivalence"],
            },
            "identities": {
                "candidate_sha256": sha256_path(candidate),
                "context_sha256": context["context_sha256"],
                "context_file_sha256": sha256_path(context_path),
                "canonical_argv_sha256": context["canonical_argv_sha256"],
                "operation_identity": OPERATION,
                "request_sha256": request["request_sha256"],
                "request_file_sha256": sha256_path(request_path),
                "presentation_sha256": sha256_path(presentation_path),
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_file_sha256": sha256_path(checkpoint_path),
                "temporal_binding_sha256": checkpoint_inner["identities"][
                    "temporal_binding_sha256"
                ],
            },
            "authority_boundary": {
                "human_operational_authority": "VERIFIED__0",
                "authority_consumption": "VERIFIED__0",
                "operation_execution": "NOT_STARTED",
                "next_legal_action": "PRESENT_EXACT_GN_TEXT_AND_STOP_FOR_EXPLICIT_HUMAN_AUTHORIZATION",
                "auto_continuable": False,
                "human_review_required": True,
            },
            "operational_counters": counters,
            "e05": {
                "before": "VERIFIED__11_OF_18",
                "current": "VERIFIED__11_OF_18",
                "credit": "VERIFIED__0",
                "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
                "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            },
            "architecture": checkpoint_inner["architecture"],
            "proof_yield": {
                "new_verified_capability_count": "VERIFIED__0__OPERATION_NOT_PERFORMED",
                "new_blocker_localized_count": "VERIFIED__0",
                "e05_credit": "VERIFIED__0",
                "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
            },
            "reuse_impact_assessment": {
                "existing_certified_capabilities_reused": "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__FM__FC__ER__GN__P11",
                "new_capabilities": "NONE__PREAUTHORIZATION_ONLY",
                "existing_capability_became_unreachable": False,
                "parallel_flow_created": False,
                "production_path_count_effect": "UNCHANGED__1_TO_1",
            },
            "governance_dashboard": {
                "project_progress": "VERIFIED__JS_EXACT_PREAUTHORIZATION_BARRIER_MATERIALIZED",
                "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
                "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_READY_FOR_ONE_EXPLICIT_HUMAN_DECISION",
                "constitutional_health_evidence": "VERIFIED__AUTHORITY_SEPARATION_AND_ZERO_OPERATION_PRESERVED",
                "shadow_automation_status": "VERIFIED__ABSENT",
                "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
                "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_REUSED_ONE_ROUTE_PRESERVED",
                "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_LOCAL_ORCHESTRATION_ONLY",
                "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
                "cognition_assisted_handoff": "NOT_APPLICABLE__NO_PROVIDER_RECOVERY",
                "candidate_capability": "VERIFIED__EXACT_EXPIRED_OPERATION_CANDIDATE_AT_HUMAN_BARRIER",
                "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_EXPIRED_SPECIALIZATION",
                "constitutional_continuation_progress": "VERIFIED__JR_TO_JS_PREAUTHORIZATION_STOP",
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
                "last_verified_edge": "EXACT_GN_DERIVED_EXPIRED_PRESENTATION_AT_HUMAN_BARRIER",
                "first_broken_edge": "FRESH_HUMAN_OPERATIONAL_AUTHORITY_NOT_PRESENT",
                "minimum_missing_capability": "EXPLICIT_HUMAN_AUTHORIZATION_OF_THE_EXACT_SEALED_REQUEST",
                "minimum_legal_next_delta": "HUMAN_REVIEW_AND_EXACT_AUTHORIZATION_OR_REJECTION",
            },
            "human_authority_assurance_status": jr[
                "human_authority_assurance_status"
            ],
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    write_json(JS / "G77_256JS_PREHUMAN_PHASE_A_REDUCTION_V1.json", reduction)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    materialize(parse_args())
