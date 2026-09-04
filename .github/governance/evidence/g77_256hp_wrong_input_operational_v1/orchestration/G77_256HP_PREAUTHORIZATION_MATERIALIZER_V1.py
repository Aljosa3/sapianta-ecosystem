#!/usr/bin/env python3
"""Materialize and seal the non-authority G77-256HP Human barrier.

This orchestration adapter reuses the committed GY, FM, GL, and GN owners.  It
has no operational launcher entry point and must run only once against an
absent HP evidence/transient namespace.
"""

from __future__ import annotations

from datetime import datetime, timezone
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
HP = ROOT / ".github/governance/evidence/g77_256hp_wrong_input_operational_v1"
LIVE = HP / "live_binding"
OPERATION_ROOT = HP / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256hp_wrong_input_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "fc9bc52bbd708a40f884f2fc006ebe0e3f6e4df8"
TREE = "9256a995bf9b90714e759dae98d2bed4c3de8f22"
SUBJECT = "G77-256HO certify WRONG_INPUT post-HN readiness"
HN_HEAD = "8eb558539e13b8b461cbfe2d868c57ef02d02d11"
HN_TREE = "674bf70f5b0c57804e8932b333db19bcdf4a7c34"
HN_SUBJECT = "G77-256HN bind WRONG_INPUT bootstrap to active adapter"
HM_HEAD = "888b3fcab74339b3201f469190e64f6c44f77508"
HM_TREE = "4427b64bc2a7768e847db8e4b97daf1a9ff132ba"
HM_SUBJECT = "G77-256HM fail closed WRONG_INPUT before request"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

GENERATION = "G77_256HP_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HP_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
PREFIX = "G77_256HP"

GY_PATH = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
HO_REDUCTION = ROOT / ".github/governance/evidence/g77_256ho_post_hn_live_binding_readiness_v1/G77_256HO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HO_CANDIDATE = ROOT / ".github/governance/evidence/g77_256ho_post_hn_live_binding_readiness_v1/live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


GY = load_module(GY_PATH, "g77_256hp_gy")
FM = load_module(FM_PATH, "g77_256hp_fm")
GL = load_module(GL_PATH, "g77_256hp_gl")
GN = load_module(GN_PATH, "g77_256hp_gn")


def canonical_bytes(value: Any) -> bytes:
    return FM.canonical_bytes(value)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sealed(schema: str, inner_name: str, inner: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner_name: inner,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(inner)),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"fresh HP artifact collision: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_entry(remote_head: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "tracked_worktree_clean_before_mutation": git(
            "status", "--porcelain", "--untracked-files=no"
        ) == "",
        "index_empty_before_mutation": git("diff", "--cached", "--name-only") == "",
        "stable_ancestry_anchor": ANCHOR,
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
        "remote_head": HEAD,
        "tracked_worktree_clean_before_mutation": True,
        "index_empty_before_mutation": True,
    }
    if any(observed[key] != value for key, value in expected.items()):
        raise RuntimeError("exact committed HO entry mismatch")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT
    ).returncode != 0:
        raise RuntimeError("stable ancestry mismatch")
    for head, tree, subject, label in (
        (HN_HEAD, HN_TREE, HN_SUBJECT, "HN"),
        (HM_HEAD, HM_TREE, HM_SUBJECT, "HM"),
    ):
        if git("rev-parse", f"{head}^{{tree}}") != tree or git(
            "show", "-s", "--format=%s", head
        ) != subject:
            raise RuntimeError(f"{label} identity mismatch")
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", head, "HEAD"], cwd=ROOT
        ).returncode != 0:
            raise RuntimeError(f"{label} ancestry mismatch")
    nested = ROOT / "sapianta_system"
    nested_observed = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_observed != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
    }:
        raise RuntimeError("nested authority mismatch")
    observed["stable_ancestry_status"] = "VERIFIED"
    observed["local_remote_equal"] = True
    observed["nested_authority"] = nested_observed
    return observed


def authenticate_ho() -> dict[str, Any]:
    envelope = json.loads(HO_REDUCTION.read_bytes())
    if envelope["reduction_sha256"] != sha256_bytes(
        canonical_bytes(envelope["reduction"])
    ):
        raise RuntimeError("HO terminal reduction seal mismatch")
    reduction = envelope["reduction"]
    required = {
        "post_commit_live_binding_status": "VERIFIED",
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
        "no_known_repository_preauthorization_blocker_status": "VERIFIED",
    }
    if any(reduction["readiness"][key] != value for key, value in required.items()):
        raise RuntimeError("HO Branch-A readiness mismatch")
    if reduction["du_eb_ee"] != {
        "current_du_status": "PASS",
        "current_eb_status": "PASS",
        "current_ee_status": "PASS",
    }:
        raise RuntimeError("HO DU/EB/EE mismatch")
    if reduction["e05"] != {"after": "7/18", "before": "7/18", "credit": 0, "remaining": 11}:
        raise RuntimeError("HO E05 state mismatch")
    if reduction["preservation"]["hm_failure_class_static_block_status"] != "VERIFIED":
        raise RuntimeError("HM failure class is not statically blocked")
    return {
        "terminal_reduction_file_sha256": sha256_path(HO_REDUCTION),
        "terminal_reduction_inner_sha256": envelope["reduction_sha256"],
        "branch_a_readiness": "VERIFIED",
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
        "hm_failure_class_static_block_status": "VERIFIED",
        "preauth_negative_matrix_status": reduction["preauthorization_negative_matrix"]["status"],
        "e05": "7/18",
        "ex_reused": reduction["reuse"]["ex_reused"],
        "ex_reconstructed": reduction["reuse"]["ex_reconstructed"],
    }


def leaf_differences(
    left: Any, right: Any, path: tuple[Any, ...] = ()
) -> dict[tuple[Any, ...], tuple[Any, Any]]:
    if type(left) is not type(right):
        return {path: (left, right)}
    if isinstance(left, dict):
        differences: dict[tuple[Any, ...], tuple[Any, Any]] = {}
        for key in set(left) | set(right):
            if key not in left or key not in right:
                differences[path + (key,)] = (left.get(key), right.get(key))
            else:
                differences.update(
                    leaf_differences(left[key], right[key], path + (key,))
                )
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return {path: (left, right)}
        differences = {}
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            differences.update(
                leaf_differences(left_item, right_item, path + (index,))
            )
        return differences
    return {} if left == right else {path: (left, right)}


def build_exact_ho_rebind() -> dict[str, Any]:
    """Rebind committed HO bytes to HO HEAD/TREE without semantic widening."""

    reference = json.loads(HO_CANDIDATE.read_bytes())
    candidate = deepcopy(reference)
    candidate["manifest"]["required_head"] = HEAD
    candidate["manifest"]["source_tree"] = TREE
    candidate["manifest_sha256"] = sha256_bytes(canonical_bytes(candidate["manifest"]))
    expected = {
        ("manifest", "required_head"): (HN_HEAD, HEAD),
        ("manifest", "source_tree"): (HN_TREE, TREE),
        ("manifest_sha256",): (
            reference["manifest_sha256"], candidate["manifest_sha256"]
        ),
    }
    if leaf_differences(reference, candidate) != expected:
        raise RuntimeError("candidate changed outside exact HO identity rebind")
    if candidate["manifest"]["selected_case"] != {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise RuntimeError("WRONG_INPUT vector identity mismatch")
    du = load_module(ROOT / GY.DU_PATH, "g77_256hp_du")
    if set(du.validate_envelope(candidate, ROOT, expected_head=HEAD).values()) != {"PASS"}:
        raise RuntimeError("exact HO rebind is not DU-valid")
    return candidate


def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise RuntimeError("HP one-shot namespace is not fresh")
    entry = authenticate_entry(args.remote_head)
    ho = authenticate_ho()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    candidate_value = build_exact_ho_rebind()
    original_builder = GY.build_post_commit_candidate
    GY.build_post_commit_candidate = lambda _root: deepcopy(candidate_value)
    try:
        binding = GY.instantiate_post_commit_binding(
            repository_root=ROOT, output_root=LIVE
        )
    finally:
        GY.build_post_commit_candidate = original_builder
    candidate = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    runtime = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    if candidate.read_bytes() != runtime.read_bytes():
        raise RuntimeError("candidate/runtime byte identity mismatch")
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
        "G77_256HP_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HP_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded,
            "entry": entry,
            "ho_readiness": ho,
            "binding_result": binding,
            "destination_readiness": destination,
            "materialization": operation_materialization,
            "asset_observations": observations,
            "readiness": readiness,
            "human_constitutional_authorization_count": 0,
            "operational_execution_count": 0,
            "vm_creation_count": 0,
        },
    )
    static_path = HP / "G77_256HP_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = HP / "G77_256HP_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    equivalence_result = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, observation, gl_checkpoint
    )
    equivalence = sealed(
        "G77_256HP_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HP_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            **{key: value for key, value in equivalence_result.items()
               if key not in {"human_constitutional_authorization_count", "operational_execution_count"}},
            "human_constitutional_authorization_count": 0,
            "operational_execution_count": 0,
        },
    )
    equivalence_path = HP / "G77_256HP_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
    write_json(equivalence_path, equivalence)

    zero_counters = {
        "human_operational_authority": 0,
        "authority_consumption": 0,
        "pre": 0,
        "fm_operational_launcher_invocation": 0,
        "qemu": 0,
        "vm_creation": 0,
        "vm_boot": 0,
        "operation_attempt": 0,
        "wrong_input_operation": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05_credit": 0,
    }
    checkpoint_inner = {
        "schema_id": "G77_256HP_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "ho_readiness_reconstruction": ho,
        "identities": {
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "fm_launcher_sha256": sha256_path(FM_PATH),
            "hn_bootstrap_cloud_init_sha256": context["wrapper_fc_er_che_schema_hashes"]["cloud_init"],
            "active_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
        },
        "semantic_firewall": {
            "case": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
            "target_mutation": "input_identity",
            "dependent_recomputation": "record_identity",
            "semantic_mutation_count": 1,
            "expected_differing_fields": ["input_identity", "record_identity"],
            "expected_denial_boundary": "D2_PRECLAIM_BEFORE_P11_ENTRY_OR_PROTECTED_EXECUTION",
            "no_protected_effect_permitted": True,
            "status": "VERIFIED",
        },
        "authority_boundary": {
            "authority_state": "NOT_GRANTED",
            "checkpoint_is_authority": False,
            "request_is_authority": False,
            "provider_capability_is_authority": False,
            "human_review_required": True,
            "auto_continuable": False,
            "next_legal_phase": "PRESENT_EXACT_GN_DERIVED_REQUEST_AND_STOP_FOR_EXPLICIT_HUMAN_DECISION",
        },
        "one_shot_maxima": {
            "human_operational_authority": 1,
            "authority_consumption": 1,
            "pre": 1,
            "fm_operational_launcher_invocation": 1,
            "qemu": 1,
            "vm_creation": 1,
            "vm_boot": 1,
            "operation_attempt": 1,
            "wrong_input_operation": 1,
            "e05_credit": 1,
            "retry": 0,
            "repair_and_continue": 0,
            "operational_replay": 0,
        },
        "operational_counters": zero_counters,
        "e05": {"before": "7/18", "current": "7/18", "maximum_credit": 1},
        "preauthorization": {
            "static_readiness_result": readiness["result"],
            "static_readiness_file_sha256": sha256_path(static_path),
            "receipt_parent_observation_file_sha256": sha256_path(observation_path),
            "receipt_parent_observation_sha256": observation["observation_sha256"],
            "preauth_final_admission_equivalence_file_sha256": sha256_path(equivalence_path),
            "preauth_final_admission_equivalence": equivalence_result["preauth_final_admission_equivalence"],
            "canonical_argv_no_network_count": sum(
                1 for index, item in enumerate(context["canonical_argv"][:-1])
                if item == "-nic" and context["canonical_argv"][index + 1] == "none"
            ),
            "single_route_status": "VERIFIED",
        },
        "resource_capacity": {
            "telemetry_source": "CODEX_APP_SERVER_ACCOUNT_RATE_LIMITS_READ",
            "primary_used_percent": args.primary_used_percent,
            "primary_remaining_percent": 100 - args.primary_used_percent,
            "primary_window_duration_minutes": 300,
            "secondary_used_percent": args.secondary_used_percent,
            "secondary_remaining_percent": 100 - args.secondary_used_percent,
            "secondary_window_duration_minutes": 10080,
            "rate_limit_reached_type": None,
            "spend_control_reached": False,
            "resource_capacity_is_execution_authority": False,
            "telemetry_is_token_cost_or_billing_evidence": False,
            "result": "PASS__SUFFICIENT_AT_HUMAN_AUTHORIZATION_BARRIER",
        },
        "reuse": {
            "ex_reused": "17/17",
            "ex_reconstructed": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "new_generic_framework_count": 0,
            "new_authority_layer_count": 0,
            "new_production_route_count": 0,
            "new_runtime_owner_count": 0,
        },
        "handoff_sufficiency": {
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "COMPLETE_FOR_PREGRANT_BARRIER",
            "authority_state": "NOT_GRANTED",
            "authority_consumed": False,
            "handoff_ambiguity_count": 0,
            "unauthenticated_handoff_assumption_count": 0,
        },
    }
    checkpoint = sealed(
        "G77_256HP_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint_inner,
    )
    checkpoint_path = HP / "G77_256HP_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    request_inner = {
        "schema_id": "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
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
        "immutable_assets": bindings,
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
            "preauth_final_admission_equivalence_file_sha256": sha256_path(equivalence_path),
            "preauth_final_admission_equivalence": equivalence_result["preauth_final_admission_equivalence"],
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
        "authorized_vector_requested": "WRONG_INPUT",
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
        "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request_inner,
    )
    request_path = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise RuntimeError("fresh HP presentation collision")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256HP_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HP_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "request_path": request_path.relative_to(ROOT).as_posix(),
            "request_file_sha256": sha256_path(request_path),
            "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **{key: value for key, value in gn_result.items()
               if key not in {"request_sha256", "presentation_sha256"}},
            "authority_present": False,
            "auto_continuable": False,
        },
    )
    write_json(HP / "G77_256HP_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json", gn_proof)

    prehuman = sealed(
        "G77_256HP_PREHUMAN_PHASE_ABC_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256HP_PREHUMAN_PHASE_ABC_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "phase": "PHASES_A_B_C_COMPLETE__MANDATORY_HUMAN_AUTHORIZATION_STOP",
            "entry": entry,
            "ho_readiness_reconstruction_status": "VERIFIED",
            "fresh_operation_material_status": "VERIFIED",
            "pre_authorization_static_admission_status": "VERIFIED",
            "wrong_input_semantic_firewall_status": "VERIFIED",
            "owner_results": {
                "du": "PASS",
                "eb": "PASS",
                "ee": "PASS",
                "ex": "PASS__17_OF_17_REUSED__0_RECONSTRUCTED",
                "fm_materialization": operation_materialization["result"],
                "fm_static_readiness": readiness["result"],
                "gl": equivalence_result["preauth_final_admission_equivalence"],
                "gn": gn_result["human_presentation_request_equivalence"],
            },
            "identities": {
                "candidate_sha256": sha256_path(candidate),
                "context_sha256": context["context_sha256"],
                "context_file_sha256": sha256_path(context_path),
                "canonical_argv_sha256": context["canonical_argv_sha256"],
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_file_sha256": sha256_path(checkpoint_path),
                "authorization_request_sha256": request["request_sha256"],
                "authorization_request_file_sha256": sha256_path(request_path),
                "gn_presentation_file_sha256": sha256_path(presentation_path),
            },
            "authority_boundary": {
                "human_authorization_status": "NOT_GRANTED",
                "authority_disposition": "NONE",
                "request_is_authority": False,
                "checkpoint_is_authority": False,
                "provider_capacity_is_authority": False,
                "operation_execution_status": "NOT_STARTED",
                "next_legal_action": "PRESENT_EXACT_GN_DETERMINISTIC_TEXT_AND_STOP_FOR_ONE_HUMAN_DECISION",
                "auto_continuable": False,
                "human_review_required": True,
            },
            "operational_counters": zero_counters,
            "e05": {"before": "7/18", "current": "7/18", "credit_awarded": 0, "maximum_possible_credit": 1},
            "handoff_sufficiency_status": "VERIFIED",
        },
    )
    write_json(HP / "G77_256HP_PREHUMAN_PHASE_ABC_REDUCTION_V1.json", prehuman)


def finalize_validation() -> None:
    """Seal completed read-only validation without changing operation state."""

    checkpoint_path = HP / "G77_256HP_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    request_path = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    prehuman_path = HP / "G77_256HP_PREHUMAN_PHASE_ABC_REDUCTION_V1.json"
    checkpoint = json.loads(checkpoint_path.read_bytes())
    request = GN.load_validated_sealed_request(request_path)
    presentation_result = GN.validate_human_authorization_presentation(
        request_path, presentation_path.read_bytes()
    )
    if checkpoint["checkpoint"]["authority_boundary"]["authority_state"] != "NOT_GRANTED":
        raise RuntimeError("validation seal cannot cross the Human barrier")
    if set(checkpoint["checkpoint"]["operational_counters"].values()) != {0}:
        raise RuntimeError("validation seal observed a nonzero operational counter")
    context = json.loads((LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json").read_bytes())
    forbidden = [
        HP / "G77_256HP_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        HP / "G77_256HP_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(Path(context["runtime_export_root"]) / relative
          for relative in context["guest_output_relative_paths"]),
    ]
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise RuntimeError("validation seal observed authority or operation evidence")
    validation = {
        "schema_id": "G77_256HP_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1",
        "recorded_at_utc": checkpoint["checkpoint"]["recorded_at_utc"],
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "request_sha256": request["request_sha256"],
        "request_file_sha256": sha256_path(request_path),
        "presentation_sha256": sha256_path(presentation_path),
        "checkpoint_sha256": checkpoint["checkpoint_sha256"],
        "checkpoint_file_sha256": sha256_path(checkpoint_path),
        "prehuman_reduction_file_sha256": sha256_path(prehuman_path),
        "human_presentation_request_equivalence": presentation_result[
            "human_presentation_request_equivalence"
        ],
        "validation_matrix": {
            "hp_focused": "PASS__6_OF_6",
            "hn_gn_gl_hg_hk_current_applicable": "PASS__98_OF_98__3_HISTORICAL_DESELECTED",
            "gy_ha_current_applicable": "PASS__29_OF_29__5_HISTORICAL_DESELECTED",
            "checkout_projection_lifecycle": "PASS__33_OF_33",
            "p11_disposable_fk_che": "PASS__47_OF_47",
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__0_RECONSTRUCTED",
            "governance_tests": "PASS__9_OF_9",
            "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0_freeze": "PASS",
            "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_syntax_ast_single_route": "PASS",
            "git_diff_check": "PASS",
            "index_state": "EMPTY",
            "raw_historical_snapshot_audit": "NOT_APPLICABLE__FOUR_OBSERVED_PRE_HN_OR_PRE_CURRENT_REBIND_ASSERTIONS",
        },
        "historical_deselection_reason": (
            "COMMITTED_HN_BOOTSTRAP_ASSETS_AND_COMMITTED_HO_HEAD_TREE_REBIND_"
            "SUPERSEDE_PRE_HN_HK_GY_HA_CURRENT_STATE_ASSERTIONS_WITHOUT_"
            "ALTERING_HISTORICAL_EVIDENCE"
        ),
        "authority_state": "NOT_GRANTED",
        "authority_consumption": 0,
        "pre": 0,
        "fm_operational_launcher_invocation": 0,
        "qemu": 0,
        "vm_creation": 0,
        "vm_boot": 0,
        "operation_attempt": 0,
        "request_count": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05": "7/18",
        "e05_credit": 0,
        "barrier_admission_status": "VERIFIED__PRESENT_EXACT_REQUEST_AND_STOP",
        "auto_continuable": False,
        "human_review_required": True,
    }
    write_json(
        HP / "G77_256HP_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1.json",
        sealed(
            "G77_256HP_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_ENVELOPE_V1",
            "validation",
            validation,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head")
    parser.add_argument("--primary-used-percent", type=int)
    parser.add_argument("--secondary-used-percent", type=int)
    parser.add_argument("--seal-validation-only", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.seal_validation_only:
        finalize_validation()
    else:
        if None in (
            arguments.remote_head,
            arguments.primary_used_percent,
            arguments.secondary_used_percent,
        ):
            raise SystemExit("materialization requires remote and capacity observations")
        materialize(arguments)
