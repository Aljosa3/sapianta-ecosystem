#!/usr/bin/env python3
"""Bind committed HI identity through existing GY/FM/DU/EB/EE owners; never operate."""

from __future__ import annotations

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

EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
EXPECTED_HEAD = "934bbeb87b41fcd94b02221cb7c4d6d7a02fd636"
EXPECTED_TREE = "39c8d03d8480dd01f1dc43e93b2de1885c1faac0"
EXPECTED_SUBJECT = "G77-256HI bind FM checkout to committed HG"
EXPECTED_HH_HEAD = "f784bb7afe1d1f8279ba9d58edbda92dc26329c8"
EXPECTED_HH_TREE = "32bd68a38962f1b0e0d73dd40cb988ef398455f0"
EXPECTED_HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
EXPECTED_HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
STABLE_ANCESTRY_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_AUTHORITY_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_AUTHORITY_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1

FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_LAUNCHER_SHA256 = "e03b583c9aff4c54cce803ac41ccecba44f3d3a41f850ea0cda71eae4ea8c90e"
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_CONTEXT_OWNER_SHA256 = "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
HH_REFERENCE = Path(
    ".github/governance/evidence/g77_256hh_post_hg_live_binding_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HH_REFERENCE_SHA256 = "7ab5997938bbb618b949930e1cd2e3be2f145175110a8ef6bccc0571eb39e194"
HI_REDUCTION = Path(
    ".github/governance/evidence/g77_256hi_current_hg_checkout_owner_binding_v1/"
    "G77_256HI_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
HI_TEST = Path(
    ".github/governance/evidence/g77_256hi_current_hg_checkout_owner_binding_v1/"
    "tests/test_g77_256hi_current_hg_checkout_owner_binding_v1.py"
)
HI_REPORT = Path(
    "docs/governance/G77_256HI_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_CORRECTION_V1.md"
)
GY_BINDER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/"
    "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
)
GY_PRODUCER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
GY_REDUCER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/"
    "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)

AUTHENTICATED_MATERIAL_SHA256 = {
    FM_LAUNCHER: FM_LAUNCHER_SHA256,
    FM_CONTEXT_OWNER: FM_CONTEXT_OWNER_SHA256,
    HI_REDUCTION: "401ce4bfa616ed48b1e7797cbd8b1383e5d2402325e1ee9bd73929d6c0506284",
    HI_TEST: "7bef4a58e3b80f75722f92996bff88edcaab737d18971ea70f0a4bd8744e3508",
    HI_REPORT: "860bf42c0e7b1a1f7b912326b4d4657c5a92bc41599cd11ddaeaea64dae2fe5d",
    HH_REFERENCE: HH_REFERENCE_SHA256,
    GY_BINDER: "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00",
    GY_PRODUCER: "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22",
    GY_REDUCER: "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7",
}


class PostHIBindingError(ValueError):
    """Deterministic fail-closed post-HI binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise PostHIBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, object_path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", object_path], cwd=root, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        raise PostHIBindingError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHIBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PostHIBindingError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHIBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_committed_hi(repository_root: Path) -> dict[str, Any]:
    """Authenticate committed HI and its production bytes from Git objects."""

    root = repository_root.resolve()
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "log", "-1", "--format=%s"),
        "remote_tracking_head": _git(
            root, "rev-parse", f"origin/{EXPECTED_BRANCH}"
        ),
    }
    expected = {
        "branch": EXPECTED_BRANCH,
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "subject": EXPECTED_SUBJECT,
        "remote_tracking_head": EXPECTED_HEAD,
    }
    if observed != expected:
        raise PostHIBindingError("EXACT_COMMITTED_HI_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", STABLE_ANCESTRY_ANCHOR, "HEAD"],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        raise PostHIBindingError("STABLE_ANCESTRY_MISSING")
    nested = root / "sapianta_system"
    if {
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "branch": _git(nested, "branch", "--show-current"),
    } != {
        "head": NESTED_AUTHORITY_HEAD,
        "tree": NESTED_AUTHORITY_TREE,
        "status": "",
        "branch": "",
    }:
        raise PostHIBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    for path, expected_sha256 in AUTHENTICATED_MATERIAL_SHA256.items():
        current = root / path
        committed_bytes = _git_bytes(root, f"{EXPECTED_HEAD}:{path.as_posix()}")
        if (
            current.is_symlink()
            or not current.is_file()
            or sha256_path(current) != expected_sha256
            or sha256_bytes(committed_bytes) != expected_sha256
            or current.read_bytes() != committed_bytes
        ):
            raise PostHIBindingError(f"HI_MATERIAL_IDENTITY_MISMATCH__{path.name}")
    launcher_source = _git_bytes(root, f"{EXPECTED_HEAD}:{FM_LAUNCHER.as_posix()}")
    if (
        b'CHECKOUT_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"' not in launcher_source
        or b'CHECKOUT_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"' not in launcher_source
    ):
        raise PostHIBindingError("HI_COMMITTED_HG_CHECKOUT_SELECTION_MISSING")
    return observed | {
        "material_count": len(AUTHENTICATED_MATERIAL_SHA256),
        "fm_launcher_sha256": sha256_bytes(launcher_source),
        "fm_context_owner_sha256": sha256_bytes(
            _git_bytes(root, f"{EXPECTED_HG_HEAD}:{FM_CONTEXT_OWNER.as_posix()}")
        ),
    }


def _leaf_differences(
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
                    _leaf_differences(left[key], right[key], path + (key,))
                )
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return {path: (left, right)}
        differences = {}
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            differences.update(
                _leaf_differences(left_item, right_item, path + (index,))
            )
        return differences
    return {} if left == right else {path: (left, right)}


def validate_exact_hi_rebind(
    reference: dict[str, Any], candidate: dict[str, Any]
) -> None:
    """Allow only HI HEAD/tree, committed launcher identity, and derived seal."""

    for envelope in (reference, candidate):
        if envelope.get("manifest_sha256") != sha256_bytes(
            canonical_bytes(envelope["manifest"])
        ):
            raise PostHIBindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
    expected = {
        ("manifest", "required_head"): (
            reference["manifest"]["required_head"],
            EXPECTED_HEAD,
        ),
        ("manifest", "source_tree"): (
            reference["manifest"]["source_tree"],
            EXPECTED_TREE,
        ),
        ("manifest", "extension_bindings", 5, "sha256"): (
            reference["manifest"]["extension_bindings"][5]["sha256"],
            FM_LAUNCHER_SHA256,
        ),
        ("manifest_sha256",): (
            reference["manifest_sha256"],
            candidate["manifest_sha256"],
        ),
    }
    if _leaf_differences(reference, candidate) != expected:
        raise PostHIBindingError("CANDIDATE_CHANGED_OUTSIDE_EXACT_HI_REBIND")
    if candidate["manifest"].get("selected_case") != {
        "case_class": CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise PostHIBindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")


def build_post_hi_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_committed_hi(root)
    producer = _load_module(root / GY_PRODUCER, "g77_256hj_gy_producer")
    candidate = producer.build_candidate(root)
    validate_exact_hi_rebind(load_canonical(root / HH_REFERENCE), candidate)
    return candidate


def build_post_hi_context(
    *,
    repository_root: Path,
    candidate_path: Path,
    operation_root: Path,
    transient_root: Path,
) -> dict[str, Any]:
    """Delegate current context construction to the existing FM owner."""

    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hj_fm_context_owner")
    candidate_relative = candidate_path.resolve().relative_to(root)
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=EXPECTED_HEAD,
        repository_tree=EXPECTED_TREE,
        generation_identity=(
            "G77_256HJ_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HJ_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HJ",
        operation_evidence_root=operation_root,
        transient_root=transient_root,
        candidate_source_path=candidate_relative,
    )
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate_relative
    )
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    checkout_owner = _git_bytes(
        root, f"{checkout['head']}:{FM_CONTEXT_OWNER.as_posix()}"
    )
    if (
        checkout["head"] != EXPECTED_HG_HEAD
        or checkout["tree"] != EXPECTED_HG_TREE
        or sha256_bytes(checkout_owner) != FM_CONTEXT_OWNER_SHA256
        or context["wrapper_fc_er_che_schema_hashes"][
            launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
        ]
        != FM_CONTEXT_OWNER_SHA256
    ):
        raise PostHIBindingError("CURRENT_HG_CHECKOUT_OWNER_BINDING_MISMATCH")
    return context


def instantiate_post_hi_binding(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Create only current candidate/context and fresh DU/EB/EE evidence."""

    root = repository_root.resolve()
    output = output_root.resolve()
    candidate = build_post_hi_candidate(root)
    gy = _load_module(root / GY_BINDER, "g77_256hj_reused_gy_binder")
    original_builder = gy.build_post_commit_candidate
    gy.build_post_commit_candidate = lambda _root: deepcopy(candidate)
    try:
        result = gy.instantiate_post_commit_binding(
            repository_root=root, output_root=output
        )
    finally:
        gy.build_post_commit_candidate = original_builder
    candidate_path = output / (
        "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    context = build_post_hi_context(
        repository_root=root,
        candidate_path=candidate_path,
        operation_root=Path("/tmp/g77_256hj/operation_state"),
        transient_root=Path("/tmp/g77_256hj/transient"),
    )
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hj_context_serializer")
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    if (result.get("du"), result.get("eb"), result.get("ee")) != (
        "PASS",
        "PASS",
        "PASS",
    ):
        raise PostHIBindingError("CURRENT_HI_DU_EB_EE_NOT_PASS")
    return result | {
        "schema_id": "G77_256HJ_POST_HI_LIVE_BINDING_RESULT_V1",
        "binding_owner": "G77_256HJ_EXACT_HI_IDENTITY_REBIND_ADAPTER_V1",
        "reused_materialization_owner": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1",
        "reused_context_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1",
        "context_path": context_path.relative_to(root).as_posix(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "checkout_head": EXPECTED_HG_HEAD,
        "checkout_tree": EXPECTED_HG_TREE,
        "checkout_owner_sha256": FM_CONTEXT_OWNER_SHA256,
        "candidate_semantics_changed": False,
        "exact_permitted_rebindings": [
            "HI_HEAD",
            "HI_TREE",
            "FM_COMMITTED_LAUNCHER_SHA256",
            "DERIVED_MANIFEST_SHA256",
        ],
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
    }


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    """Reduce persisted current evidence to the bounded Branch A result."""

    root = repository_root.resolve()
    live = live_root.resolve()
    candidate = live / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    runtime = live / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    eb_receipt = live / "bindings/G77_256GY_EB_RECEIPT_V1.json"
    ee_receipt = live / "bindings/G77_256GY_EE_RECEIPT_V1.json"
    harness = live / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
    candidate_value = load_canonical(candidate)
    context = load_canonical(context_path)
    if candidate.read_bytes() != runtime.read_bytes():
        raise PostHIBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    validate_exact_hi_rebind(load_canonical(root / HH_REFERENCE), candidate_value)
    if (
        context["repository_head"] != EXPECTED_HEAD
        or context["repository_tree"] != EXPECTED_TREE
        or context["candidate_manifest_sha256"] != sha256_path(candidate)
    ):
        raise PostHIBindingError("PERSISTED_CONTEXT_CURRENT_IDENTITY_MISMATCH")
    counters = {
        "authority_consumption": 0,
        "e05_credit": 0,
        "fm_operational_launcher_invocation": 0,
        "human_operational_authority": 0,
        "operation_attempt": 0,
        "operational_replay": 0,
        "p11_entry": 0,
        "pre": 0,
        "protected_effect": 0,
        "protected_invocation": 0,
        "qemu": 0,
        "repair_and_continue": 0,
        "request": 0,
        "retry": 0,
        "vm_boot": 0,
        "vm_creation": 0,
        "wrong_input_operation": 0,
    }
    return {
        "schema_id": "G77_256HJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HJ",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry_authentication": {
            "status": "VERIFIED",
            "branch": EXPECTED_BRANCH,
            "head": EXPECTED_HEAD,
            "tree": EXPECTED_TREE,
            "subject": EXPECTED_SUBJECT,
            "remote_head": EXPECTED_HEAD,
            "stable_ancestry_anchor": STABLE_ANCESTRY_ANCHOR,
            "entry_worktree_state": "CLEAN",
            "index_state": "EMPTY",
            "nested_authority_head": NESTED_AUTHORITY_HEAD,
            "nested_authority_tree": NESTED_AUTHORITY_TREE,
            "nested_authority_state": "CLEAN__DETACHED__PINNED",
        },
        "hi_frontier": {
            "authentication_status": "VERIFIED",
            "branch": "BRANCH_A__STALE_BINDING_CORRECTION_VERIFIED",
            "last_verified_edge": (
                "EXACT_CURRENT_HG_FM_CHECKOUT_OWNER_BINDING_REPOSITORY_CAPABILITY_"
                "WITH_HH_FAILURE_CLASS_STATICALLY_BLOCKED"
            ),
            "first_unproven_edge": (
                "POST_HI_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_"
                "REAUTHENTICATION"
            ),
            "minimum_missing_capability": (
                "POST_HI_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_"
                "REAUTHENTICATION"
            ),
        },
        "dependency_discovery": {
            "post_hi_dependency_set": [
                "CURRENT_CANDIDATE_REPOSITORY_HEAD_TREE_AND_FM_LAUNCHER_HASH",
                "CURRENT_RUNTIME_PROJECTION",
                "CURRENT_FRESH_OPERATION_CONTEXT",
                "CURRENT_DU_EB_EE_APPLICABILITY",
                "PREOPERATIONAL_READINESS_REDUCTION",
            ],
            "post_hi_rebind_required_set": [
                "GY_WRONG_INPUT_CANDIDATE_HI_HEAD_TREE_LAUNCHER_HASH_AND_SEAL",
                "BYTE_IDENTICAL_RUNTIME_PROJECTION",
                "FM_FRESH_OPERATION_CONTEXT_HI_IDENTITY_AND_CANDIDATE_HASH",
            ],
            "post_hi_unchanged_reuse_set": [
                "HG_CHECKOUT_AND_CONTEXT_OWNER_BYTES",
                "GY_WRONG_INPUT_SEMANTICS",
                "HA_GUEST_ADAPTER",
                "FM_CONTEXT_BUILDER",
                "DU_EB_EE_VALIDATORS",
                "P11_CHE_FK",
                "EX_COMMON_SUBSTRATE_17_OF_17",
            ],
            "post_hi_fresh_receipt_required_set": [
                "DU_CURRENT_VALIDATION_RESULT",
                "EB_CANDIDATE_BOUND_RECEIPT",
                "EE_RUNTIME_CONSUMER_BINDING_RECEIPT",
            ],
            "post_hi_historical_non_applicable_set": [
                "HF_TERMINAL_OPERATIONAL_HISTORY",
                "HH_TERMINAL_BRANCH_B_RECEIPTS_AS_CURRENT_HI_RECEIPTS",
                "HI_PRECOMMIT_SNAPSHOT_REBUILDS",
            ],
        },
        "live_binding": {
            "post_hi_committed_identity_status": "VERIFIED",
            "post_hi_candidate_binding_status": "VERIFIED",
            "post_hi_runtime_projection_binding_status": "VERIFIED",
            "post_hi_launcher_identity_binding_status": "VERIFIED",
            "post_hi_checkout_owner_binding_status": "VERIFIED",
            "post_hi_context_owner_binding_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "candidate_sha256": sha256_path(candidate),
            "candidate_inner_sha256": candidate_value["manifest_sha256"],
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "eb_receipt_sha256": sha256_path(eb_receipt),
            "ee_receipt_sha256": sha256_path(ee_receipt),
            "ee_harness_sha256": sha256_path(harness),
            "fm_launcher_sha256": FM_LAUNCHER_SHA256,
            "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
            "checkout_head": EXPECTED_HG_HEAD,
            "checkout_tree": EXPECTED_HG_TREE,
            "candidate_semantics_changed": False,
        },
        "du_eb_ee": {
            "du_status": "PASS",
            "eb_status": "PASS",
            "ee_status": "PASS",
            "du_reauthentication_status": "VERIFIED__FRESH_CURRENT_RESULT",
            "eb_reauthentication_status": "VERIFIED__FRESH_CURRENT_RECEIPT",
            "ee_reauthentication_status": "VERIFIED__FRESH_CURRENT_RECEIPT",
            "current_applicability_status": "VERIFIED_INDEPENDENTLY",
        },
        "projection_preservation": {
            "hg_projection_binding_status": "VERIFIED",
            "host_canonical_binding_status": "VERIFIED",
            "guest_projection_binding_status": "VERIFIED",
            "projection_equivalence_status": "VERIFIED",
            "host_binding_preservation_status": "VERIFIED",
            "unauthorized_mutation_rejection_status": "VERIFIED",
            "wrong_input_bootstrap_checkout_argument_binding_status": (
                "NOT_PROVEN__HD_CLOUD_INIT_ENCODES_PRE_HG_HEAD_TREE"
            ),
        },
        "semantic_firewall": {
            "case": CASE_CLASS,
            "target_mutation": TARGET_MUTATION,
            "dependent_recomputation": DEPENDENT_RECOMPUTATION,
            "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
            "expected_differing_fields": ["input_identity", "record_identity"],
            "wrong_input_semantic_firewall_status": "VERIFIED",
            "same_class_review_status": "VERIFIED",
            "gy_reducer_semantics_status": "VERIFIED",
            "wrong_input_binding_status": "VERIFIED",
        },
        "hh_failure_class_non_regression": {
            "hh_failure_class_static_block_status": "VERIFIED",
            "stale_pre_hg_owner_rejection_status": "VERIFIED",
            "wrong_owner_rejection_status": "VERIFIED",
            "missing_owner_rejection_status": "VERIFIED",
            "malformed_owner_rejection_status": "VERIFIED",
            "ambiguous_owner_rejection_status": "VERIFIED",
        },
        "preauthorization_negative_matrix": {
            "status": "VERIFIED__11_OF_11",
            "cases": [
                "MISSING_CURRENT_CANDIDATE",
                "WRONG_CANDIDATE_IDENTITY",
                "STALE_LAUNCHER_IDENTITY",
                "WRONG_CHECKOUT_OWNER",
                "STALE_CHECKOUT_OWNER",
                "MISSING_CHECKOUT_OWNER",
                "INVALID_PROJECTION",
                "WRONG_OWNER_HASH",
                "MISSING_REQUIRED_CURRENT_RECEIPT",
                "STALE_REQUIRED_CURRENT_RECEIPT",
                "CANDIDATE_RUNTIME_PROJECTION_MISMATCH",
            ],
        },
        "proof_impact": {
            "changed_owner_set": ["FM_SOLE_LAUNCHER_CHECKOUT_HEAD_TREE_BINDING"],
            "dependent_proof_set": [
                "CURRENT_HI_CANDIDATE_AND_RUNTIME_IDENTITY",
                "CURRENT_HI_CONTEXT_AND_LAUNCHER_BINDING",
                "CURRENT_DU_EB_EE",
                "HG_CHECKOUT_CONTEXT_OWNER_PROJECTION",
                "PREAUTHORIZATION_NEGATIVE_MATRIX",
                "HJ_READINESS_REDUCTION",
            ],
            "invalidated_proof_frontier": [
                "HH_CANDIDATE_HEAD_TREE_LAUNCHER_HASH_AS_CURRENT",
                "HH_DU_EB_EE_RECEIPTS_AS_CURRENT_HI_RECEIPTS",
                "ABSENT_POST_HI_CONTEXT_AND_READINESS",
            ],
            "revalidated_proof_set": [
                "HJ_FOCUSED",
                "HI_FOCUSED_OWNER",
                "HH_APPLICABLE",
                "HG_PROJECTION",
                "GY_HA_SEMANTIC_FIREWALL",
                "DU_EB_EE",
                "GOVERNANCE_CONFORMANCE",
                "EX",
                "LAYER0",
            ],
            "reused_unchanged_proof_set": [
                "HG_CONTEXT_OWNER_BYTES",
                "GY_HA_SEMANTICS",
                "P11_CHE_FK",
                "EX_17_OF_17",
                "HF_HG_HH_HI_HISTORICAL_EVIDENCE",
            ],
        },
        "reuse": {
            "reuse_search_status": "VERIFIED",
            "reused_binder_set": ["GY_BINDER", "FM_CONTEXT_BUILDER"],
            "reused_owner_set": [
                "FM_SOLE_LAUNCHER",
                "HG_COMMITTED_CHECKOUT",
                "GY_WRONG_INPUT_OWNERS",
                "P11_CHE_FK",
                "EX_COMMON_SUBSTRATE",
            ],
            "reused_validator_set": [
                "DU",
                "EB",
                "EE",
                "FM_IMMUTABLE_CONTEXT",
                "FM_CHECKOUT_OWNER",
                "HG_PROJECTION",
                "GY_REDUCER",
                "GOVERNANCE_CONFORMANCE",
            ],
            "new_generic_framework_required": False,
            "ex_reused": "17/17",
            "ex_reconstructed": 0,
        },
        "readiness": {
            "terminal_branch": "BRANCH_B__READINESS_NOT_PROVEN",
            "post_commit_live_binding_status": "VERIFIED",
            "fm_context_owner_binding_status": "VERIFIED",
            "hi_checkout_owner_binding_status": "VERIFIED",
            "hg_projection_binding_status": "VERIFIED",
            "du_status": "PASS",
            "eb_status": "PASS",
            "ee_status": "PASS",
            "hh_failure_class_static_block_status": "VERIFIED",
            "preauth_negative_matrix_status": "VERIFIED",
            "same_class_review_status": "VERIFIED",
            "wrong_input_bootstrap_checkout_argument_binding_status": (
                "NOT_PROVEN__STALE_PRE_HG_HEAD_TREE"
            ),
            "no_known_repository_preauthorization_blocker_status": (
                "NOT_PROVEN__CURRENT_STATIC_READINESS_BLOCKER"
            ),
            "preoperational_readiness_status": "NOT_PROVEN",
            "next_operational_generation_eligible": "NOT_PROVEN",
            "authorized": False,
            "last_verified_edge": (
                "POST_HI_CANDIDATE_CONTEXT_DU_EB_EE_AND_EXACT_HG_CHECKOUT_"
                "OWNER_BINDING"
            ),
            "first_broken_edge": (
                "WRONG_INPUT_AUTHORITY_FREE_STATIC_READINESS_REJECTS_HD_CLOUD_"
                "INIT_PRE_HG_CHECKOUT_ARGUMENT_BINDING"
            ),
        },
        "capability_boundary": {
            "candidate_capability": "VERIFIED",
            "post_hi_live_binding_candidate_capability": "VERIFIED",
            "post_hi_live_binding_repository_capability": "VERIFIED",
            "post_hi_live_binding_operational_capability": "NOT_PROVEN",
            "current_hg_checkout_owner_binding_repository_capability": "VERIFIED",
            "projection_aware_validation_repository_capability": "VERIFIED",
            "wrong_input_candidate_capability": "VERIFIED",
            "wrong_input_repository_capability": "VERIFIED",
            "wrong_input_operational_capability": "NOT_PROVEN",
        },
        "reuse_impact": {
            "existing_capability_unreachable": False,
            "new_capability_created": (
                "POST_HI_COMMITTED_IDENTITY_LIVE_BINDING_AND_REPOSITORY_"
                "PREOPERATIONAL_READINESS_ONLY"
            ),
            "parallel_flow_created": False,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
        },
        "operational_counters": counters,
        "e05": {"before": "7/18", "credit": 0, "after": "7/18", "remaining": 11},
        "validation": {
            "hj_focused": "PASS__13_OF_13__BRANCH_B_BLOCKER_AUTHENTICATED",
            "hi_focused_owner": "PASS__12_OF_12",
            "checkout_and_projection": "PASS__31_OF_31",
            "wrong_input_applicable": "PASS__29_OF_29__5_HISTORICAL_DESELECTED",
            "hh_applicable": "PASS__3_OF_3__5_HISTORICAL_DESELECTED",
            "affected_checkout_projection": (
                "FAIL_CLOSED__WRONG_INPUT_BOOTSTRAP_ARGUMENTS_STALE_PRE_HG"
            ),
            "wrong_input_semantic_firewall": "PASS__NO_SEMANTIC_BROADENING",
            "governance_tests": "PASS__9_OF_9",
            "governance_engine": (
                "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS"
            ),
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__ZERO_RECONSTRUCTED",
            "layer_0_freeze": "PASS",
            "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_ast_syntax": "PASS",
            "git_diff_check": "PASS",
        },
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE"},
            "cross_worker_state_recovery_level": {
                "status": "VERIFIED",
                "value": "COMMITTED_HI_RECONSTRUCTED",
            },
            "repository_derived_context_ratio": {
                "status": "ESTIMATED",
                "value": "DOMINANT",
            },
            "human_handoff_information_required": {
                "status": "VERIFIED",
                "value": "BOUNDED_HJ_COMMISSION_ONLY",
            },
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "previous_worker_conversation_required": {
                "status": "VERIFIED",
                "value": "NO",
            },
            "authenticated_repository_continuation": {"status": "VERIFIED"},
            "intra_task_cross_worker_continuation": {"status": "NOT_APPLICABLE"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "cross_worker_constitutional_drift": {
                "status": "VERIFIED",
                "value": "ZERO_DETECTED",
            },
            "same_worker_provider_reset_resume": {"status": "NOT_APPLICABLE"},
            "handoff_sufficiency_status": {"status": "VERIFIED"},
            "handoff_prompt_eligibility": {
                "status": "VERIFIED",
                "value": "REPOSITORY_ONLY_HJ_ELIGIBLE__OPERATION_INELIGIBLE",
            },
            "handoff_state_completeness": {"status": "VERIFIED"},
            "handoff_reconstruction_required": {"status": "VERIFIED"},
            "handoff_reconstruction_success": {"status": "VERIFIED"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "value": 0},
            "unauthenticated_handoff_assumption_count": {
                "status": "VERIFIED",
                "value": 0,
            },
        },
        "metrics": {
            "project_progress_estimate": {
                "status": "ESTIMATED",
                "value": "POST_HI_BINDING_COMPLETE__ONE_STATIC_BOOTSTRAP_BLOCKER_OPEN",
            },
            "constitutional_health_evidence": {"status": "VERIFIED"},
            "shadow_automation_status": {
                "status": "VERIFIED",
                "value": "ABSENT",
            },
            "constitutional_frontier_distance": {
                "status": "VERIFIED",
                "value": "ONE_REPOSITORY_CORRECTION_TO_PREOPERATIONAL_ELIGIBILITY",
            },
            "e05_frontier_distance": {"status": "VERIFIED", "value": 11},
            "selected_e05_local_frontier_distance": {
                "status": "VERIFIED",
                "value": "ONE_REPOSITORY_CORRECTION_PLUS_FUTURE_HUMAN_OPERATION",
            },
            "governance_efficiency": {
                "status": "ESTIMATED",
                "value": "TARGETED_AFFECTED_FRONTIER",
            },
            "architectural_governance_efficiency": {
                "status": "VERIFIED",
                "value": "ONE_ROUTE_RETAINED",
            },
            "proof_reuse_efficiency": {
                "status": "ESTIMATED",
                "value": "HIGH__EX_17_OF_17_AND_EXISTING_OWNERS_REUSED",
            },
            "cognition_assisted_handoff": {"status": "VERIFIED"},
            "aigol_codex_work_share": {"status": "NOT_MEASURED"},
            "overengineering_risk": {"status": "ESTIMATED", "value": "LOW"},
            "proof_process_overhead_risk": {
                "status": "ESTIMATED",
                "value": "MEDIUM",
            },
            "cognition_provenance": {
                "status": "VERIFIED",
                "value": "REPOSITORY_BYTES_GIT_OBJECTS_AND_COMMISSION_SCOPE",
            },
            "shadow_design_target": {"status": "NOT_APPLICABLE"},
            "constitutional_continuation_progress": {
                "status": "VERIFIED",
                "value": "POST_HI_BINDING_VERIFIED_AND_NEXT_BLOCKER_LOCALIZED",
            },
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "token_benchmark": {"status": "NOT_MEASURED"},
            "llm_cost_reduction_ratio_lcrr": {"status": "NOT_MEASURED"},
            "e05_generations_per_credit": {"status": "NOT_MEASURED"},
            "operational_attempts_per_credit": {"status": "NOT_APPLICABLE"},
            "new_infrastructure_per_credit": {"status": "NOT_APPLICABLE"},
            "new_code_per_credit": {"status": "NOT_APPLICABLE"},
            "new_proof_per_credit": {"status": "NOT_APPLICABLE"},
            "reused_proof_per_credit": {"status": "NOT_APPLICABLE"},
            "marginal_e05_generation_cost": {"status": "NOT_APPLICABLE"},
            "infrastructure_amortization_signal": {
                "status": "ESTIMATED",
                "value": "POSITIVE_REUSE_SIGNAL_WITH_ZERO_CREDIT",
            },
            "workers_used": {"status": "VERIFIED", "value": 1},
            "provider_capacity_start": {"status": "NOT_MEASURED"},
            "provider_capacity_end": {"status": "NOT_MEASURED"},
            "provider_capacity_consumed": {"status": "NOT_MEASURED"},
            "wall_time": {"status": "NOT_MEASURED"},
            "llm_execution_efficiency": {
                "status": "ESTIMATED",
                "value": "TARGETED_REVALIDATION_WITH_REUSE",
            },
            "revalidation_case_count": {"status": "VERIFIED", "value": 130},
            "new_code": {
                "status": "VERIFIED",
                "value": "ONE_HJ_BINDER_AND_ONE_FOCUSED_TEST_MODULE",
            },
            "reused_code": {
                "status": "VERIFIED",
                "value": "GY_FM_DU_EB_EE_HG_HA_EX_OWNERS",
            },
            "new_proof": {"status": "VERIFIED", "value": "HJ_13_CASES"},
            "reused_proof": {"status": "VERIFIED", "value": "EX_17_OF_17"},
            "revalidated_proof": {"status": "VERIFIED", "value": 130},
            "reconstructed_proof": {"status": "VERIFIED", "value": 0},
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "minimum_missing_capability": (
                "EXACT_CURRENT_HG_WRONG_INPUT_GUEST_BOOTSTRAP_CHECKOUT_ARGUMENT_"
                "BINDING_WITHOUT_ROUTE_OR_SEMANTIC_EXPANSION"
            ),
            "minimum_legal_next_development_delta": (
                "ONE_BOUNDED_REPOSITORY_ONLY_CURRENT_HG_WRONG_INPUT_GUEST_"
                "BOOTSTRAP_CHECKOUT_ARGUMENT_BINDING_CORRECTION__NO_OPERATION"
            ),
            "verdict": (
                "FAIL_CLOSED__G77_256HJ_POST_HI_LIVE_BINDING_VERIFIED__CURRENT_"
                "WRONG_INPUT_BOOTSTRAP_STILL_BINDS_PRE_HG_CHECKOUT_ARGUMENTS__"
                "PREOPERATIONAL_READINESS_NOT_PROVEN__ZERO_OPERATION__"
                "E05_7_OF_18__HUMAN_REVIEW_REQUIRED"
            ),
        },
    }


def write_terminal_reduction(
    *, repository_root: Path, live_root: Path, output_path: Path
) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    envelope = {
        "schema_id": "G77_256HJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise PostHIBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
