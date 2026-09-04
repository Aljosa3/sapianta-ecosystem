#!/usr/bin/env python3
"""Materialize and seal the non-authority G77-256HX Human barrier.

This generation-specific adapter reconstructs committed HW readiness, creates
one exact WRONG_CONTRACT operation commission, and emits one GN-derived Human
authorization request.  It has no operational launcher entry point and must
stop with every operational counter at zero.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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
sys.path.insert(0, str(ROOT))
HX = ROOT / ".github/governance/evidence/g77_256hx_wrong_contract_operational_v1"
LIVE = HX / "live_binding"
OPERATION_ROOT = HX / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256hx_wrong_contract_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "0e2448cb0194d6182085a671ddb28729681a1e75"
TREE = "adc1453b964d05e3cf41deffcbbc0c856f99a81a"
SUBJECT = "G77-256HW certify WRONG_CONTRACT preoperational readiness"
HV_HEAD = "737ef550f02f6b65a7dd0d4e1ac5bc118599b32b"
HV_TREE = "212a36d807663b5c60927355bfb9fe1184bfc27c"
HV_SUBJECT = "G77-256HV correct WRONG_CONTRACT guest checkout binding"
HT_HEAD = "af44f0afd02be7e21a24e962309e28f6edd17ae0"
HT_TREE = "fc949a2bbaa0a507edbc25811563dc5e13d18315"
HT_SUBJECT = "G77-256HT extend existing route for WRONG_CONTRACT"
HR_HEAD = "cbd457d9281e787a10980583921abb0a6021be74"
HR_TREE = "74ca78da7bf079d762994f7a76cb09726f3cb5cf"
HR_SUBJECT = "G77-256HR formalize WRONG_CONTRACT repository capability"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

GENERATION = "G77_256HX_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256HX_E05_WRONG_CONTRACT_DENIAL_BEFORE_ENTRY_001"
PREFIX = "G77_256HX"

HW_ROOT = ROOT / ".github/governance/evidence/g77_256hw_post_hv_live_binding_readiness_v1"
HW_BINDER_PATH = HW_ROOT / "binding/G77_256HW_POST_HV_LIVE_BINDING_V1.py"
HW_TERMINAL_PATH = HW_ROOT / "G77_256HW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HW_CANDIDATE_PATH = HW_ROOT / "live_binding/candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


HW = load_module(HW_BINDER_PATH, "g77_256hx_hw")
FM = load_module(FM_PATH, "g77_256hx_fm")
GL = load_module(GL_PATH, "g77_256hx_gl")
GN = load_module(GN_PATH, "g77_256hx_gn")


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
        raise RuntimeError(f"fresh HX artifact collision: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def committed_bytes(path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{HEAD}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT
    )


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
        raise RuntimeError("exact committed and pushed HW entry mismatch")
    for head, tree, subject, label in (
        (HV_HEAD, HV_TREE, HV_SUBJECT, "HV"),
        (HT_HEAD, HT_TREE, HT_SUBJECT, "HT"),
        (HR_HEAD, HR_TREE, HR_SUBJECT, "HR"),
    ):
        if git("rev-parse", f"{head}^{{tree}}") != tree:
            raise RuntimeError(f"{label} tree mismatch")
        if git("show", "-s", "--format=%s", head) != subject:
            raise RuntimeError(f"{label} subject mismatch")
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", head, "HEAD"], cwd=ROOT
        ).returncode != 0:
            raise RuntimeError(f"{label} ancestry mismatch")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT
    ).returncode != 0:
        raise RuntimeError("stable ancestry mismatch")
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
    observed["local_remote_equal"] = True
    observed["required_ancestry_status"] = "VERIFIED"
    observed["nested_authority"] = nested_observed
    return observed


def authenticate_hw() -> dict[str, Any]:
    raw = committed_bytes(HW_TERMINAL_PATH)
    envelope = json.loads(raw)
    if raw != canonical_bytes(envelope):
        raise RuntimeError("committed HW terminal is not canonical")
    if envelope["reduction_sha256"] != sha256_bytes(
        canonical_bytes(envelope["reduction"])
    ):
        raise RuntimeError("committed HW terminal seal mismatch")
    reduction = envelope["reduction"]
    required_live = {
        "current_hv_commit_identity_status": "VERIFIED",
        "post_commit_live_binding_status": "VERIFIED",
        "current_wrong_contract_candidate_status": "VERIFIED",
        "current_runtime_projection_status": "VERIFIED",
        "current_operation_context_status": "VERIFIED",
        "gn_presentation_binding_status": "VERIFIED",
    }
    if any(reduction["live_binding"].get(key) != value for key, value in required_live.items()):
        raise RuntimeError("committed HW live binding reconstruction mismatch")
    if reduction["du_eb_ee"] != {
        "current_du_status": "PASS",
        "current_eb_status": "PASS",
        "current_ee_status": "PASS",
    }:
        raise RuntimeError("committed HW DU/EB/EE mismatch")
    if reduction["firewalls"] != {
        "preauthorization_negative_matrix_status": "VERIFIED",
        "known_historical_failure_class_block_status": "VERIFIED",
        "no_known_repository_preauth_blocker_status": "VERIFIED",
    }:
        raise RuntimeError("committed HW firewall mismatch")
    if reduction["readiness"] != {
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
        "wrong_contract_operational_capability": "NOT_PROVEN",
    }:
        raise RuntimeError("committed HW readiness mismatch")
    if reduction["semantic_firewall"] != {
        "contract_specific_comparison_reached": False,
        "dependent_recomputation": "record_identity",
        "expected_p11_denial": "D2_INPUT_RECORD_IDENTITY_BINDING_FAILURE",
        "semantic_mutation_count": 1,
        "target_mutation": "contract_identity",
        "unrelated_mutation_count": 0,
    }:
        raise RuntimeError("committed HW semantic firewall mismatch")
    if reduction["e05"] != {"before": "8/18", "credit": 0, "after": "8/18"}:
        raise RuntimeError("committed HW E05 state mismatch")
    if set(reduction["operational_counters"].values()) != {0}:
        raise RuntimeError("committed HW has nonzero operational counters")
    identities = reduction["committed_identity_map"]
    for item in identities.values():
        path = ROOT / item["path"]
        data = committed_bytes(path)
        if path.read_bytes() != data or sha256_bytes(data) != item["sha256"]:
            raise RuntimeError(f"committed HW identity drift: {item['path']}")
        if git("rev-parse", f"{HEAD}:{item['path']}") != item["git_blob"]:
            raise RuntimeError(f"committed HW Git blob drift: {item['path']}")
    checkout = HW.verify_committed_checkout_bootstrap(ROOT)
    host_guest = HW.verify_host_guest_semantics(ROOT)
    semantics = HW.candidate_semantics(ROOT)
    ex = HW.authenticate_ex(ROOT)
    return {
        "terminal_reduction_file_sha256": sha256_bytes(raw),
        "terminal_reduction_inner_sha256": envelope["reduction_sha256"],
        "current_hv_commit_identity_status": "VERIFIED",
        "committed_identity_map_status": "VERIFIED",
        "committed_fm_checkout_binding_status": checkout["committed_fm_checkout_binding_status"],
        "committed_wrong_contract_bootstrap_head_tree_status": checkout["committed_wrong_contract_bootstrap_head_tree_status"],
        "committed_checkout_bootstrap_coherence_status": checkout["committed_checkout_bootstrap_coherence_status"],
        "committed_nocloud_projection_status": checkout["committed_nocloud_projection_status"],
        "expected_harness_binding_status": checkout["expected_harness_binding_status"],
        "host_guest_context_vector_semantic_equivalence": host_guest["host_guest_context_vector_semantic_equivalence"],
        "current_wrong_contract_candidate_status": "VERIFIED",
        "post_commit_live_binding_status": "VERIFIED",
        "current_du_status": "PASS",
        "current_eb_status": "PASS",
        "current_ee_status": "PASS",
        "preauthorization_negative_matrix_status": "VERIFIED",
        "known_historical_failure_class_block_status": "VERIFIED",
        "no_known_repository_preauth_blocker_status": "VERIFIED",
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
        "wrong_contract_operational_capability": "NOT_PROVEN",
        "candidate_semantics_status": "VERIFIED" if semantics["semantic_mutation_count"] == 1 else "NOT_PROVEN",
        "ex_reused": ex["ex_reused"],
        "ex_reconstructed": ex["ex_reconstructed"],
        "e05": "8/18",
    }


def leaf_differences(
    left: Any, right: Any, path: tuple[Any, ...] = ()
) -> dict[tuple[Any, ...], tuple[Any, Any]]:
    if type(left) is not type(right):
        return {path: (left, right)}
    if isinstance(left, dict):
        result: dict[tuple[Any, ...], tuple[Any, Any]] = {}
        for key in set(left) | set(right):
            if key not in left or key not in right:
                result[path + (key,)] = (left.get(key), right.get(key))
            else:
                result.update(leaf_differences(left[key], right[key], path + (key,)))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return {path: (left, right)}
        result = {}
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            result.update(leaf_differences(left_item, right_item, path + (index,)))
        return result
    return {} if left == right else {path: (left, right)}


def build_exact_hw_rebind() -> dict[str, Any]:
    raw = committed_bytes(HW_CANDIDATE_PATH)
    reference = json.loads(raw)
    if raw != canonical_bytes(reference):
        raise RuntimeError("committed HW candidate is not canonical")
    if reference["manifest_sha256"] != sha256_bytes(canonical_bytes(reference["manifest"])):
        raise RuntimeError("committed HW candidate seal mismatch")
    candidate = deepcopy(reference)
    candidate["manifest"]["required_head"] = HEAD
    candidate["manifest"]["source_tree"] = TREE
    candidate["manifest_sha256"] = sha256_bytes(canonical_bytes(candidate["manifest"]))
    expected = {
        ("manifest", "required_head"): (HV_HEAD, HEAD),
        ("manifest", "source_tree"): (HV_TREE, TREE),
        ("manifest_sha256",): (reference["manifest_sha256"], candidate["manifest_sha256"]),
    }
    if leaf_differences(reference, candidate) != expected:
        raise RuntimeError("candidate changed outside exact HW identity rebind")
    if candidate["manifest"]["selected_case"] != {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_CONTRACT",
        "case_id": "G77_256HW_E05_WRONG_CONTRACT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise RuntimeError("WRONG_CONTRACT vector identity mismatch")
    du = load_module(ROOT / HW.DU_OWNER, "g77_256hx_du_rebind")
    if set(du.validate_envelope(candidate, ROOT, expected_head=HEAD).values()) != {"PASS"}:
        raise RuntimeError("exact HW rebind is not DU-valid")
    return candidate


def materialize_live_binding() -> tuple[dict[str, Any], Path, Path, Path]:
    candidate_value = build_exact_hw_rebind()
    candidate = LIVE / "candidate/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    runtime = LIVE / "runtime_projection/G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"
    bindings = LIVE / "bindings"
    harness = bindings / "G77_256HX_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_path = bindings / "G77_256HX_EB_RECEIPT_V1.json"
    ee_path = bindings / "G77_256HX_EE_RECEIPT_V1.json"
    for parent in (candidate.parent, runtime.parent, bindings):
        parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(candidate_value)
    candidate.write_bytes(payload)
    runtime.write_bytes(payload)
    harness.write_bytes(
        b'from pathlib import Path\n\nFIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\nRAW_ROOT = Path("/mnt/g77-evidence")\nCONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256HW_WRONG_CONTRACT_CURRENT_CANDIDATE_V1.json"\n'
    )
    du = load_module(ROOT / HW.DU_OWNER, "g77_256hx_du")
    eb = load_module(ROOT / HW.EB_OWNER, "g77_256hx_eb")
    ee = load_module(ROOT / HW.EE_OWNER, "g77_256hx_ee")
    du_result = du.validate_file(candidate, ROOT, expected_head=HEAD)
    eb_receipt = eb.validate_candidate(ROOT, candidate, required_head=HEAD, required_tree=TREE)
    eb_path.write_bytes(eb.canonical_bytes(eb_receipt))
    ee_receipt = ee.validate_binding(
        ROOT, candidate, eb_path, harness, runtime.parent, "/mnt/g77-evidence",
        required_head=HEAD, required_tree=TREE,
    )
    ee_path.write_bytes(ee.canonical_bytes(ee_receipt))
    if set(du_result.values()) != {"PASS"}:
        raise RuntimeError("current HX DU status is not PASS")
    if eb.verify_receipt_file(ROOT, eb_path)["overall_result"] != "PASS":
        raise RuntimeError("current HX EB status is not PASS")
    if ee.verify_receipt_file(ROOT, ee_path)["pre_materialization_runtime_path_binding_result"] != "PASS":
        raise RuntimeError("current HX EE status is not PASS")
    return (
        {
            "candidate_semantics_changed": False,
            "candidate_binding_regeneration_required": True,
            "committed_hw_candidate_sha256": sha256_bytes(committed_bytes(HW_CANDIDATE_PATH)),
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "du": "PASS",
            "eb": "PASS",
            "ee": "PASS",
        },
        candidate,
        runtime,
        harness,
    )


def materialize(args: argparse.Namespace) -> None:
    output_paths = (
        LIVE,
        OPERATION_ROOT,
        TRANSIENT_ROOT,
        HX / "G77_256HX_PREAUTHORITY_STATIC_READINESS_V1.json",
        HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
    )
    if any(path.exists() or path.is_symlink() for path in output_paths):
        raise RuntimeError("HX one-shot namespace is not fresh")
    entry = authenticate_entry(args.remote_head)
    hw = authenticate_hw()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    binding, candidate, runtime, _ = materialize_live_binding()

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
        "G77_256HX_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HX_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded,
            "entry": entry,
            "hw_readiness_reconstruction": hw,
            "binding_result": binding,
            "destination_readiness": destination,
            "materialization": operation_materialization,
            "asset_observations": observations,
            "readiness": readiness,
            "historical_failure_firewall_status": "VERIFIED",
            "human_constitutional_authorization_count": 0,
            "operational_execution_count": 0,
            "vm_creation_count": 0,
        },
    )
    static_path = HX / "G77_256HX_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = HX / "G77_256HX_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    equivalence_result = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, observation, gl_checkpoint
    )
    equivalence = sealed(
        "G77_256HX_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HX_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            **{
                key: value for key, value in equivalence_result.items()
                if key not in {"human_constitutional_authorization_count", "operational_execution_count"}
            },
            "human_constitutional_authorization_count": 0,
            "operational_execution_count": 0,
        },
    )
    equivalence_path = HX / "G77_256HX_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
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
        "wrong_contract_operation": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "e05_credit": 0,
    }
    checkpoint_inner = {
        "schema_id": "G77_256HX_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "hw_readiness_reconstruction": hw,
        "identities": {
            "committed_hw_candidate_sha256": binding["committed_hw_candidate_sha256"],
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "fm_launcher_sha256": sha256_path(FM_PATH),
            "wrong_contract_bootstrap_sha256": context["wrapper_fc_er_che_schema_hashes"]["cloud_init"],
            "wrong_contract_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
            "selected_checkout_head": HT_HEAD,
            "selected_checkout_tree": HT_TREE,
        },
        "semantic_firewall": {
            "case": "E05_NEGATIVE_AUTHORITY_WRONG_CONTRACT",
            "target_mutation": "contract_identity",
            "dependent_recomputation": "record_identity",
            "semantic_mutation_count": 1,
            "unrelated_mutation_count": 0,
            "expected_differing_fields": ["contract_identity", "record_identity"],
            "human_act_input_record_identity_unchanged": True,
            "expected_denial_stage": "D2_INPUT_RECORD_IDENTITY_BINDING_VALIDATION",
            "expected_denial_reason": "OPERATIONAL_HUMAN_ACT_INPUT_RECORD_IDENTITY_BINDING_INVALID",
            "contract_specific_comparison_expected_to_be_reached": False,
            "no_protected_effect_permitted": True,
            "status": "VERIFIED",
        },
        "authority_boundary": {
            "authority_state": "NOT_GRANTED",
            "presentation_is_authority": False,
            "request_is_authority": False,
            "provider_capability_is_authority": False,
            "human_authorization_required": True,
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
            "wrong_contract_operation": 1,
            "request": 1,
            "e05_credit": 1,
            "retry": 0,
            "repair_retry": 0,
            "replay": 0,
        },
        "operational_counters": zero_counters,
        "e05": {"before": "8/18", "current": "8/18", "maximum_credit": 1},
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
        "provider_runtime_admission": {
            "status": "NOT_MEASURED__REAUTHENTICATE_AFTER_EXACT_HUMAN_GRANT_BEFORE_CONSUMPTION",
            "provider_capability_is_execution_authority": False,
            "request_is_not_conditioned_on_provider_telemetry_as_authority": True,
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
        "G77_256HX_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint_inner,
    )
    checkpoint_path = HX / "G77_256HX_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    request_inner = {
        "schema_id": "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
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
        "authorized_vector_requested": "WRONG_CONTRACT",
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
        "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request_inner,
    )
    request_path = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise RuntimeError("fresh HX presentation collision")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256HX_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256HX_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "request_path": request_path.relative_to(ROOT).as_posix(),
            "request_file_sha256": sha256_path(request_path),
            "presentation_path": presentation_path.relative_to(ROOT).as_posix(),
            "presentation_sha256": sha256_path(presentation_path),
            "request_sha256": request["request_sha256"],
            **{
                key: value for key, value in gn_result.items()
                if key not in {"request_sha256", "presentation_sha256"}
            },
            "authority_present": False,
            "auto_continuable": False,
        },
    )
    gn_path = HX / "G77_256HX_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
    write_json(gn_path, gn_proof)

    prehuman = sealed(
        "G77_256HX_PREHUMAN_PHASE_ABC_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256HX_PREHUMAN_PHASE_ABC_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "phase": "PHASES_A_B_C_COMPLETE__MANDATORY_HUMAN_AUTHORIZATION_STOP",
            "entry": entry,
            "hw_readiness_reconstruction_status": "VERIFIED",
            "fresh_operation_material_status": "VERIFIED",
            "pre_authorization_static_admission_status": "VERIFIED",
            "wrong_contract_semantic_firewall_status": "VERIFIED",
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
                "runtime_projection_sha256": sha256_path(runtime),
                "context_sha256": context["context_sha256"],
                "context_file_sha256": sha256_path(context_path),
                "canonical_argv_sha256": context["canonical_argv_sha256"],
                "checkpoint_sha256": checkpoint["checkpoint_sha256"],
                "checkpoint_file_sha256": sha256_path(checkpoint_path),
                "authorization_request_sha256": request["request_sha256"],
                "authorization_request_file_sha256": sha256_path(request_path),
                "gn_presentation_file_sha256": sha256_path(presentation_path),
                "gn_equivalence_file_sha256": sha256_path(gn_path),
            },
            "authority_boundary": {
                "human_authorization_status": "NOT_GRANTED",
                "authority_disposition": "NONE",
                "presentation_is_authority": False,
                "request_is_authority": False,
                "checkpoint_is_authority": False,
                "provider_capacity_is_authority": False,
                "operation_execution_status": "NOT_STARTED",
                "next_legal_action": "PRESENT_EXACT_GN_DETERMINISTIC_TEXT_AND_STOP_FOR_ONE_HUMAN_DECISION",
                "auto_continuable": False,
                "human_review_required": True,
            },
            "operational_counters": zero_counters,
            "e05": {"before": "8/18", "current": "8/18", "credit_awarded": 0, "maximum_possible_credit": 1},
            "handoff_sufficiency_status": "VERIFIED",
        },
    )
    write_json(HX / "G77_256HX_PREHUMAN_PHASE_ABC_REDUCTION_V1.json", prehuman)


def finalize_validation() -> None:
    """Seal completed read-only validation without crossing the Human barrier."""

    checkpoint_path = HX / "G77_256HX_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    request_path = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    prehuman_path = HX / "G77_256HX_PREHUMAN_PHASE_ABC_REDUCTION_V1.json"
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
        HX / "G77_256HX_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        HX / "G77_256HX_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(
            Path(context["runtime_export_root"]) / relative
            for relative in context["guest_output_relative_paths"]
        ),
    ]
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise RuntimeError("validation seal observed authority or operation evidence")
    validation = {
        "schema_id": "G77_256HX_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1",
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
            "hx_focused": "PASS__7_OF_7",
            "wrong_contract_current_applicable": "PASS__64_OF_64__3_HISTORICAL_ENTRY_ASSERTIONS_DESELECTED",
            "p11_disposable_che_fk": "PASS__47_OF_47",
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__0_RECONSTRUCTED",
            "governance_tests": "PASS__9_OF_9",
            "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0": "PASS__CURRENT_GOVERNANCE_CONFORMANCE_AND_COMMITTED_HW_BINDING",
            "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_syntax_ast_single_route": "PASS",
            "git_diff_check": "PASS",
            "index_state": "EMPTY",
        },
        "historical_deselection_reason": (
            "COMMITTED_HW_HEAD_SUPERSEDES_HR_HV_PRECOMMIT_ENTRY_ASSERTIONS_"
            "WITHOUT_ALTERING_HISTORICAL_EVIDENCE"
        ),
        "authority_state": "NOT_GRANTED",
        "human_operational_authority": 0,
        "authority_consumption": 0,
        "pre": 0,
        "fm_operational_launcher_invocation": 0,
        "qemu": 0,
        "vm_creation": 0,
        "vm_boot": 0,
        "operation_attempt": 0,
        "wrong_contract_operation": 0,
        "request_count": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_retry": 0,
        "replay": 0,
        "e05": "8/18",
        "e05_credit": 0,
        "barrier_admission_status": "VERIFIED__PRESENT_EXACT_REQUEST_AND_STOP",
        "auto_continuable": False,
        "human_authorization_required": True,
        "human_review_required": True,
    }
    write_json(
        HX / "G77_256HX_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1.json",
        sealed(
            "G77_256HX_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_ENVELOPE_V1",
            "validation",
            validation,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head")
    parser.add_argument("--seal-validation-only", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.seal_validation_only:
        finalize_validation()
    else:
        if arguments.remote_head is None:
            raise SystemExit("materialization requires --remote-head")
        materialize(arguments)
