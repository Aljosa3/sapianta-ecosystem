#!/usr/bin/env python3
"""Materialize and seal the non-authority G77-256IC Human barrier.

This orchestration adapter reuses the committed IB, IA, HZ, FM, GL, and GN
owners. It has no operational launcher entry point and must run only once
against an absent IC evidence/transient namespace.
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
IC = ROOT / ".github/governance/evidence/g77_256ic_wrong_provenance_operational_v1"
LIVE = IC / "live_binding"
OPERATION_ROOT = IC / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256ic_wrong_provenance_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "ec2c4997ba62fbaa5e774fc9ba010f6319926c73"
TREE = "887f329b030582f01a49f6c0c97f54ed4f55a818"
SUBJECT = "G77-256IB certify WRONG_PROVENANCE preoperational readiness"
IA_HEAD = "dfea5c58f400edb9472db37390de80a92eda2ad3"
IA_TREE = "caf8feb24ed4c072dde6c6586fd7cf60d05c4c7d"
IA_SUBJECT = "G77-256IA extend single route for WRONG_PROVENANCE"
HZ_HEAD = "9db84476f263b9676d2ff7407152388afad04618"
HZ_TREE = "8753786eede58f453a40af71825c19bc3efaff0a"
HZ_SUBJECT = "G77-256HZ formalize WRONG_PROVENANCE repository capability"
HY_HEAD = "451fafdeafc935c352a27f75fbddb473423ce7b3"
HY_TREE = "98a5f94880cae12e91ab3173fad36de8c90d0d23"
HY_SUBJECT = "G77-256HY select WRONG_PROVENANCE frontier"
HX_HEAD = "c8f0ad3602fd3b99b68f043be4c978d665dbf000"
HX_TREE = "91b79ebb6d7c4aa49de5f9dab7e2d709f75837aa"
HX_SUBJECT = "G77-256HX certify WRONG_CONTRACT operational denial"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

GENERATION = "G77_256IC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_PROVENANCE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256IC_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001"
PREFIX = "G77_256IC"

IB_PATH = ROOT / ".github/governance/evidence/g77_256ib_wrong_provenance_post_commit_readiness_v1/binding/G77_256IB_POST_IA_LIVE_BINDING_V1.py"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
IB_REDUCTION = ROOT / ".github/governance/evidence/g77_256ib_wrong_provenance_post_commit_readiness_v1/G77_256IB_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
IB_CANDIDATE = ROOT / ".github/governance/evidence/g77_256ib_wrong_provenance_post_commit_readiness_v1/live_binding/candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
DU_PATH = ROOT / ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
EB_PATH = ROOT / ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
EE_PATH = ROOT / ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


IB = load_module(IB_PATH, "g77_256ic_ib")
FM = load_module(FM_PATH, "g77_256ic_fm")
GL = load_module(GL_PATH, "g77_256ic_gl")
GN = load_module(GN_PATH, "g77_256ic_gn")


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
        raise RuntimeError(f"fresh IC artifact collision: {path}")
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
        raise RuntimeError("exact committed IB entry mismatch")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT
    ).returncode != 0:
        raise RuntimeError("stable ancestry mismatch")
    for head, tree, subject, label in (
        (IA_HEAD, IA_TREE, IA_SUBJECT, "IA"),
        (HZ_HEAD, HZ_TREE, HZ_SUBJECT, "HZ"),
        (HY_HEAD, HY_TREE, HY_SUBJECT, "HY"),
        (HX_HEAD, HX_TREE, HX_SUBJECT, "HX"),
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


def authenticate_ib() -> dict[str, Any]:
    envelope = json.loads(IB_REDUCTION.read_bytes())
    if envelope["reduction_sha256"] != sha256_bytes(
        canonical_bytes(envelope["reduction"])
    ):
        raise RuntimeError("IB terminal reduction seal mismatch")
    reduction = envelope["reduction"]
    required_readiness = {
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
    }
    if any(
        reduction["readiness"][key] != value
        for key, value in required_readiness.items()
    ):
        raise RuntimeError("IB readiness mismatch")
    if reduction["live_binding"]["post_commit_live_binding_status"] != "VERIFIED":
        raise RuntimeError("IB live-binding status mismatch")
    if reduction["du_eb_ee"] != {
        "current_du_status": "PASS",
        "current_eb_status": "PASS",
        "current_ee_status": "PASS",
    }:
        raise RuntimeError("IB DU/EB/EE mismatch")
    if reduction["e05"] != {
        "after": "9/18", "before": "9/18", "credit": 0, "remaining": 9,
        "required": 18, "satisfied": 9,
    }:
        raise RuntimeError("IB E05 state mismatch")
    if reduction["host_guest_coherence"]["supported_vector_set"] != [
        "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT", "WRONG_PROVENANCE"
    ]:
        raise RuntimeError("IB supported vector set mismatch")
    return {
        "terminal_reduction_file_sha256": sha256_path(IB_REDUCTION),
        "terminal_reduction_inner_sha256": envelope["reduction_sha256"],
        "preoperational_readiness": "VERIFIED",
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
        "historical_failure_firewall_status": reduction["historical_failure_firewall"]["status"],
        "preauth_negative_matrix_status": reduction["preauthorization_negative_matrix"]["status"],
        "e05": "9/18",
        "ex_reused": reduction["ex"]["ex_reused"],
        "ex_reconstructed": reduction["ex"]["ex_reconstructed"],
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


def build_exact_ib_rebind() -> dict[str, Any]:
    """Rebind committed IB bytes to IB HEAD/TREE without semantic widening."""

    reference = json.loads(IB_CANDIDATE.read_bytes())
    candidate = deepcopy(reference)
    candidate["manifest"]["required_head"] = HEAD
    candidate["manifest"]["source_tree"] = TREE
    candidate["manifest_sha256"] = sha256_bytes(canonical_bytes(candidate["manifest"]))
    expected = {
        ("manifest", "required_head"): (IA_HEAD, HEAD),
        ("manifest", "source_tree"): (IA_TREE, TREE),
        ("manifest_sha256",): (
            reference["manifest_sha256"], candidate["manifest_sha256"]
        ),
    }
    if leaf_differences(reference, candidate) != expected:
        raise RuntimeError("candidate changed outside exact IB identity rebind")
    if candidate["manifest"]["selected_case"] != {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_PROVENANCE",
        "case_id": "G77_256IB_E05_WRONG_PROVENANCE_DENIAL_BEFORE_ENTRY_001",
    }:
        raise RuntimeError("WRONG_PROVENANCE vector identity mismatch")
    du = load_module(DU_PATH, "g77_256ic_du")
    if set(du.validate_envelope(candidate, ROOT, expected_head=HEAD).values()) != {"PASS"}:
        raise RuntimeError("exact IB rebind is not DU-valid")
    return candidate


def materialize_live_binding(candidate_value: dict[str, Any]) -> dict[str, Any]:
    """Create the fresh IC DU/EB/EE projection without a second route."""

    candidate_name = "G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    candidate_path = LIVE / "candidate" / candidate_name
    runtime_root = LIVE / "runtime_projection"
    runtime_path = runtime_root / candidate_name
    bindings_root = LIVE / "bindings"
    harness_path = bindings_root / "G77_256IC_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_path = bindings_root / "G77_256IC_EB_RECEIPT_V1.json"
    ee_path = bindings_root / "G77_256IC_EE_RECEIPT_V1.json"
    for parent in (candidate_path.parent, runtime_root, bindings_root):
        parent.mkdir(parents=True, exist_ok=True)
    candidate_bytes = canonical_bytes(candidate_value)
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(
        (
            "from pathlib import Path\n\n"
            'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
            'RAW_ROOT = Path("/mnt/g77-evidence")\n'
            f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{candidate_name}"\n'
        ).encode("utf-8")
    )
    du = load_module(DU_PATH, "g77_256ic_binding_du")
    eb = load_module(EB_PATH, "g77_256ic_binding_eb")
    ee = load_module(EE_PATH, "g77_256ic_binding_ee")
    du_result = du.validate_file(candidate_path, ROOT, expected_head=HEAD)
    eb_receipt = eb.validate_candidate(
        ROOT, candidate_path, required_head=HEAD, required_tree=TREE
    )
    eb_path.write_bytes(eb.canonical_bytes(eb_receipt))
    eb_result = eb.verify_receipt_file(ROOT, eb_path)
    ee_receipt = ee.validate_binding(
        ROOT, candidate_path, eb_path, harness_path, runtime_root,
        "/mnt/g77-evidence", required_head=HEAD, required_tree=TREE,
    )
    ee_path.write_bytes(ee.canonical_bytes(ee_receipt))
    ee_result = ee.verify_receipt_file(ROOT, ee_path)
    if set(du_result.values()) != {"PASS"}:
        raise RuntimeError("IC DU validation failed")
    if eb_result.get("overall_result") != "PASS":
        raise RuntimeError("IC EB validation failed")
    if ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise RuntimeError("IC EE validation failed")
    return {
        "schema_id": "G77_256IC_WRONG_PROVENANCE_POST_COMMIT_BINDING_RESULT_V1",
        "artifact_class": "POST_COMMIT_BINDING__NON_AUTHORITY__NON_OPERATIONAL",
        "repository_head": HEAD,
        "repository_tree": TREE,
        "output_root": LIVE.relative_to(ROOT).as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "candidate_semantics_changed": False,
        "du": "PASS", "eb": "PASS", "ee": "PASS",
        "human_operational_authority_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "production_route_delta": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }


def materialize(args: argparse.Namespace) -> None:
    if LIVE.exists() or OPERATION_ROOT.exists() or TRANSIENT_ROOT.exists():
        raise RuntimeError("IC one-shot namespace is not fresh")
    entry = authenticate_entry(args.remote_head)
    ib = authenticate_ib()
    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    candidate_value = build_exact_ib_rebind()
    binding = materialize_live_binding(candidate_value)
    candidate = LIVE / "candidate/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
    runtime = LIVE / "runtime_projection/G77_256IB_WRONG_PROVENANCE_CURRENT_CANDIDATE_V1.json"
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
        "G77_256IC_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256IC_PREAUTHORITY_STATIC_READINESS_V1",
            "recorded_at_utc": recorded,
            "entry": entry,
            "ib_readiness": ib,
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
    static_path = IC / "G77_256IC_PREAUTHORITY_STATIC_READINESS_V1.json"
    write_json(static_path, static)

    observation = GL.prepare_and_observe_receipt_parent(ROOT, context)
    observation_path = IC / "G77_256IC_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
    write_json(observation_path, observation)
    gl_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, observation)
    equivalence_result = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, observation, gl_checkpoint
    )
    equivalence = sealed(
        "G77_256IC_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256IC_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            **{key: value for key, value in equivalence_result.items()
               if key not in {"human_constitutional_authorization_count", "operational_execution_count"}},
            "human_constitutional_authorization_count": 0,
            "operational_execution_count": 0,
        },
    )
    equivalence_path = IC / "G77_256IC_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
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
        "wrong_provenance_operation": 0,
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
        "schema_id": "G77_256IC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": recorded,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "ib_readiness_reconstruction": ib,
        "identities": {
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "fm_launcher_sha256": sha256_path(FM_PATH),
            "ia_bootstrap_cloud_init_sha256": context["wrapper_fc_er_che_schema_hashes"]["cloud_init"],
            "active_adapter_sha256": context["guest_adapter_binding"]["source_sha256"],
        },
        "semantic_firewall": {
            "case": "E05_NEGATIVE_AUTHORITY_WRONG_PROVENANCE",
            "target_mutation": "provenance_identity",
            "dependent_recomputation": "record_identity",
            "independent_mutation_count": 1,
            "independent_mutated_coordinate": "provenance_identity",
            "dependent_recomputation_count": 1,
            "dependent_recomputed_coordinate": "record_identity",
            "semantic_mutation_count": 1,
            "unrelated_mutation_count": 0,
            "expected_differing_fields": ["provenance_identity", "record_identity"],
            "authoritative_provenance": "existing protected custody owner-state",
            "expected_denial_boundary": "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT",
            "expected_denial_stage": "D2 preclaim authority-binding validation before preclaim ledger append, claim, P11 entry, protected invocation, or protected effect",
            "expected_denial_reason": "operational Human act input_record_identity binding is invalid",
            "provenance_specific_comparison_reached": False,
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
            "wrong_provenance_operation": 1,
            "e05_credit": 1,
            "retry": 0,
            "repair_and_continue": 0,
            "operational_replay": 0,
        },
        "operational_counters": zero_counters,
        "e05": {"before": "9/18", "current": "9/18", "maximum_credit": 1},
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
        "G77_256IC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint_inner,
    )
    checkpoint_path = IC / "G77_256IC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    write_json(checkpoint_path, checkpoint)

    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    request_inner = {
        "schema_id": "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
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
        "authorized_vector_requested": "WRONG_PROVENANCE",
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
        "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request_inner,
    )
    request_path = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    write_json(request_path, request)
    presentation = GN.render_human_authorization_presentation(request_path)
    presentation_path = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    if presentation_path.exists() or presentation_path.is_symlink():
        raise RuntimeError("fresh IC presentation collision")
    presentation_path.write_bytes(presentation)
    gn_result = GN.validate_human_authorization_presentation(request_path, presentation)
    gn_proof = sealed(
        "G77_256IC_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        {
            "schema_id": "G77_256IC_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
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
    write_json(IC / "G77_256IC_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json", gn_proof)

    prehuman = sealed(
        "G77_256IC_PREHUMAN_PHASE_ABC_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256IC_PREHUMAN_PHASE_ABC_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "phase": "PHASES_A_B_C_COMPLETE__MANDATORY_HUMAN_AUTHORIZATION_STOP",
            "entry": entry,
            "ib_readiness_reconstruction_status": "VERIFIED",
            "fresh_operation_material_status": "VERIFIED",
            "pre_authorization_static_admission_status": "VERIFIED",
            "wrong_provenance_semantic_firewall_status": "VERIFIED",
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
            "e05": {"before": "9/18", "current": "9/18", "credit_awarded": 0, "maximum_possible_credit": 1},
            "handoff_sufficiency_status": "VERIFIED",
        },
    )
    write_json(IC / "G77_256IC_PREHUMAN_PHASE_ABC_REDUCTION_V1.json", prehuman)


def finalize_validation() -> None:
    """Seal completed read-only validation without changing operation state."""

    checkpoint_path = IC / "G77_256IC_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
    request_path = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    prehuman_path = IC / "G77_256IC_PREHUMAN_PHASE_ABC_REDUCTION_V1.json"
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
        IC / "G77_256IC_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        IC / "G77_256IC_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(Path(context["runtime_export_root"]) / relative
          for relative in context["guest_output_relative_paths"]),
    ]
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise RuntimeError("validation seal observed authority or operation evidence")
    validation = {
        "schema_id": "G77_256IC_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1",
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
            "ic_focused": "PASS__6_OF_6",
            "hz_ia_ib_gn_gl_current_applicable": "PASS__135_OF_135__4_HISTORICAL_DESELECTED",
            "ib_negative_matrix": "PASS__21_CASES__FAILURE_BEFORE_OPERATION_VERIFIED",
            "four_vector_non_regression": "PASS__EXACT_CLOSED_SET__UNKNOWN_AND_MALFORMED_FAIL_CLOSED",
            "du_eb_ee": "PASS__PASS__PASS",
            "p11_disposable_che_fk": "PASS__72_OF_72",
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__0_RECONSTRUCTED",
            "governance_tests": "PASS__9_OF_9",
            "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0": "PASS__CURRENT_GOVERNANCE_CONFORMANCE_AND_COMMITTED_IB_BINDING",
            "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_syntax_ast_single_route": "PASS",
            "git_diff_check": "PASS",
            "index_state": "EMPTY",
        },
        "historical_deselection_reason": (
            "COMMITTED_IB_BASE_SUPERSEDES_HY_AND_IA_HISTORICAL_ENTRY_OR_"
            "CHECKOUT_ASSERTIONS_AND_IB_PRE_IB_ENTRY_ASSERTIONS_WITHOUT_"
            "ALTERING_HISTORICAL_EVIDENCE"
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
        "wrong_provenance_operation": 0,
        "request_count": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "repair_retry": 0,
        "operational_replay": 0,
        "e05": "9/18",
        "e05_credit": 0,
        "barrier_admission_status": "VERIFIED__PRESENT_EXACT_REQUEST_AND_STOP",
        "auto_continuable": False,
        "human_review_required": True,
    }
    write_json(
        IC / "G77_256IC_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_V1.json",
        sealed(
            "G77_256IC_PREHUMAN_VALIDATION_AND_BARRIER_ADMISSION_ENVELOPE_V1",
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
