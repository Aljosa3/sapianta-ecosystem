#!/usr/bin/env python3
"""Bind committed HK through existing GY/FM/DU/EB/EE owners; never operate."""

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
EXPECTED_HEAD = "64847500b3f81b3f00f7ec5563313eec2999b549"
EXPECTED_TREE = "cb272c800adc89ad226a7822e9762cf25acdfbd4"
EXPECTED_SUBJECT = "G77-256HK bind WRONG_INPUT bootstrap to committed HG"
EXPECTED_HJ_HEAD = "0977c05efaab001eb5d3f15e17c3f180158b722c"
EXPECTED_HJ_TREE = "35197458a1a5cba0fdbfe32d1ee6e54bdd0cf862"
EXPECTED_HI_HEAD = "934bbeb87b41fcd94b02221cb7c4d6d7a02fd636"
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
FM_LAUNCHER_SHA256 = "e11bc4c05468910ca9cc1dbc6b4ea4122c22d36c5021718148d8d3f52407d94f"
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_CONTEXT_OWNER_SHA256 = "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
HK_CLOUD_INIT = Path(
    ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1/static/"
    "G77_256HK_CLOUD_INIT_USER_DATA_V1.yaml"
)
HK_CLOUD_INIT_SHA256 = "f10425de141e2f790b4b57fe00aa59c345aeb4e2c0e58e3a2b57cbaf602ff666"
HK_SEED = Path(
    ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1/static/"
    "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)
HK_SEED_SHA256 = "6346b9f02b236d71f2698b01a0d607549ad4d9d779a72b5168658994c519913d"
HJ_REFERENCE = Path(
    ".github/governance/evidence/g77_256hj_post_hi_live_binding_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
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
HK_REDUCTION = Path(
    ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1/"
    "G77_256HK_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
HK_TEST = Path(
    ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1/tests/"
    "test_g77_256hk_current_hg_bootstrap_binding_v1.py"
)
HK_REPORT = Path(
    "docs/governance/"
    "G77_256HK_CURRENT_HG_WRONG_INPUT_GUEST_BOOTSTRAP_CHECKOUT_ARGUMENT_"
    "BINDING_CORRECTION_V1.md"
)

AUTHENTICATED_MATERIAL_SHA256 = {
    FM_LAUNCHER: FM_LAUNCHER_SHA256,
    FM_CONTEXT_OWNER: FM_CONTEXT_OWNER_SHA256,
    HK_CLOUD_INIT: HK_CLOUD_INIT_SHA256,
    HK_SEED: HK_SEED_SHA256,
    HK_REDUCTION: "72df14d5c41d83b1914b486359588b3c600e5bd24332b4f913a36492b7206e25",
    HK_TEST: "216291effcde1abfe1dbfd1c1e2cbef913cc934be6e5bc6166ac24e22c805bd9",
    HK_REPORT: "b440863a794b8c3630453e6cb394572d66fd247896328e7a47b57e4f16ab3e31",
    HJ_REFERENCE: "3e2907030cd1342d5f2d88736b5a892fc65ceb5e077aded7d83ddd51d8d63c62",
    GY_BINDER: "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00",
    GY_PRODUCER: "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22",
    GY_REDUCER: "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7",
}


class PostHKBindingError(ValueError):
    """Deterministic fail-closed post-HK binding rejection."""


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
        raise PostHKBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, object_path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", object_path], cwd=root, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as exc:
        raise PostHKBindingError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHKBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PostHKBindingError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHKBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_committed_hk(repository_root: Path) -> dict[str, Any]:
    """Authenticate committed HK and all current owners from Git objects."""

    root = repository_root.resolve()
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "log", "-1", "--format=%s"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
    }
    expected = {
        "branch": EXPECTED_BRANCH,
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "subject": EXPECTED_SUBJECT,
        "remote_tracking_head": EXPECTED_HEAD,
    }
    if observed != expected:
        raise PostHKBindingError("EXACT_COMMITTED_HK_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", STABLE_ANCESTRY_ANCHOR, "HEAD"],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        raise PostHKBindingError("STABLE_ANCESTRY_MISSING")
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
        raise PostHKBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    for path, expected_sha256 in AUTHENTICATED_MATERIAL_SHA256.items():
        current = root / path
        committed = _git_bytes(root, f"{EXPECTED_HEAD}:{path.as_posix()}")
        if (
            current.is_symlink()
            or not current.is_file()
            or sha256_path(current) != expected_sha256
            or sha256_bytes(committed) != expected_sha256
            or current.read_bytes() != committed
        ):
            raise PostHKBindingError(f"HK_MATERIAL_IDENTITY_MISMATCH__{path.name}")
    hk = load_canonical(root / HK_REDUCTION)["reduction"]
    required_hk = {
        "terminal_branch": "BRANCH_A__BOOTSTRAP_CORRECTION_VERIFIED",
        "current_hg_bootstrap_binding_acceptance_status": "VERIFIED",
        "hj_failure_class_static_block_status": "VERIFIED",
        "hg_projection_correction_preservation_status": "VERIFIED",
        "wrong_input_semantic_firewall_status": "VERIFIED",
        "post_commit_live_binding_status": "NOT_PROVEN",
        "preoperational_readiness_status": "NOT_PROVEN",
        "next_operational_generation_eligible": "NOT_PROVEN",
    }
    observed_hk = {
        "terminal_branch": hk["readiness"]["terminal_branch"],
        "current_hg_bootstrap_binding_acceptance_status": hk["negative_matrix"]["current_hg_acceptance"],
        "hj_failure_class_static_block_status": hk["preservation"]["hj_failure_class_static_block_status"],
        "hg_projection_correction_preservation_status": hk["preservation"]["hg_projection_correction_preservation_status"],
        "wrong_input_semantic_firewall_status": hk["preservation"]["wrong_input_semantic_firewall_status"],
        "post_commit_live_binding_status": hk["readiness"]["post_commit_live_binding_status"],
        "preoperational_readiness_status": hk["readiness"]["preoperational_readiness_status"],
        "next_operational_generation_eligible": hk["readiness"]["next_operational_generation_eligible"],
    }
    if observed_hk != required_hk or hk["e05"]["after"] != "7/18":
        raise PostHKBindingError("HK_BRANCH_A_RECONSTRUCTION_FAILED")
    return observed | {
        "material_count": len(AUTHENTICATED_MATERIAL_SHA256),
        "fm_launcher_sha256": FM_LAUNCHER_SHA256,
        "cloud_init_sha256": HK_CLOUD_INIT_SHA256,
        "seed_sha256": HK_SEED_SHA256,
        "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
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
                differences.update(_leaf_differences(left[key], right[key], path + (key,)))
        return differences
    if isinstance(left, list):
        if len(left) != len(right):
            return {path: (left, right)}
        differences = {}
        for index, (left_item, right_item) in enumerate(zip(left, right, strict=True)):
            differences.update(_leaf_differences(left_item, right_item, path + (index,)))
        return differences
    return {} if left == right else {path: (left, right)}


def validate_exact_hk_rebind(reference: dict[str, Any], candidate: dict[str, Any]) -> None:
    """Allow only HK HEAD/tree, committed launcher identity, and derived seal."""

    for envelope in (reference, candidate):
        if envelope.get("manifest_sha256") != sha256_bytes(
            canonical_bytes(envelope["manifest"])
        ):
            raise PostHKBindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
    expected = {
        ("manifest", "required_head"): (
            reference["manifest"]["required_head"], EXPECTED_HEAD
        ),
        ("manifest", "source_tree"): (
            reference["manifest"]["source_tree"], EXPECTED_TREE
        ),
        ("manifest", "extension_bindings", 5, "sha256"): (
            reference["manifest"]["extension_bindings"][5]["sha256"],
            FM_LAUNCHER_SHA256,
        ),
        ("manifest_sha256",): (
            reference["manifest_sha256"], candidate["manifest_sha256"]
        ),
    }
    if _leaf_differences(reference, candidate) != expected:
        raise PostHKBindingError("CANDIDATE_CHANGED_OUTSIDE_EXACT_HK_REBIND")
    if candidate["manifest"].get("selected_case") != {
        "case_class": CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise PostHKBindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")


def build_post_hk_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_committed_hk(root)
    producer = _load_module(root / GY_PRODUCER, "g77_256hl_gy_producer")
    candidate = producer.build_candidate(root)
    validate_exact_hk_rebind(load_canonical(root / HJ_REFERENCE), candidate)
    return candidate


def build_post_hk_context(
    *, repository_root: Path, candidate_path: Path, operation_root: Path,
    transient_root: Path
) -> dict[str, Any]:
    """Delegate the non-authority context to the existing FM owner."""

    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hl_fm_context_owner")
    candidate_relative = candidate_path.resolve().relative_to(root)
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=EXPECTED_HEAD,
        repository_tree=EXPECTED_TREE,
        generation_identity=(
            "G77_256HL_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HL_WRONG_INPUT_PREOPERATIONAL_READINESS_001",
        identity_namespace_prefix="G77_256HL",
        operation_evidence_root=operation_root,
        transient_root=transient_root,
        candidate_source_path=candidate_relative,
    )
    validate_current_hk_context(root, context, candidate_relative)
    return context


def validate_current_hk_context(
    repository_root: Path, context: dict[str, Any], candidate_source_path: Path
) -> None:
    """Reject any context not bound to exact committed HK and HG/HK assets."""

    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hl_context_validator")
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate_source_path
    )
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    if (
        context["repository_head"] != EXPECTED_HEAD
        or context["repository_tree"] != EXPECTED_TREE
        or checkout["head"] != EXPECTED_HG_HEAD
        or checkout["tree"] != EXPECTED_HG_TREE
        or Path(seed["path"]).resolve() != (root / HK_SEED).resolve()
        or seed["sha256"] != HK_SEED_SHA256
        or hashes["cloud_init"] != HK_CLOUD_INIT_SHA256
        or hashes[launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY]
        != FM_CONTEXT_OWNER_SHA256
    ):
        raise PostHKBindingError("CURRENT_HG_CHECKOUT_HK_BOOTSTRAP_COHERENCE_MISMATCH")


def instantiate_post_hk_binding(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Create only current candidate/context and fresh DU/EB/EE evidence."""

    root = repository_root.resolve()
    output = output_root.resolve()
    candidate = build_post_hk_candidate(root)
    gy = _load_module(root / GY_BINDER, "g77_256hl_reused_gy_binder")
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
    context = build_post_hk_context(
        repository_root=root,
        candidate_path=candidate_path,
        operation_root=Path("/tmp/g77_256hl/operation_state"),
        transient_root=Path("/tmp/g77_256hl/transient"),
    )
    launcher = _load_module(root / FM_LAUNCHER, "g77_256hl_context_serializer")
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    if (result.get("du"), result.get("eb"), result.get("ee")) != (
        "PASS", "PASS", "PASS"
    ):
        raise PostHKBindingError("CURRENT_HK_DU_EB_EE_NOT_PASS")
    return result | {
        "schema_id": "G77_256HL_POST_HK_LIVE_BINDING_RESULT_V1",
        "binding_owner": "G77_256HL_EXACT_HK_IDENTITY_REBIND_ADAPTER_V1",
        "reused_materialization_owner": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1",
        "reused_context_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1",
        "context_path": context_path.relative_to(root).as_posix(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "checkout_head": EXPECTED_HG_HEAD,
        "checkout_tree": EXPECTED_HG_TREE,
        "cloud_init_sha256": HK_CLOUD_INIT_SHA256,
        "seed_sha256": HK_SEED_SHA256,
        "candidate_semantics_changed": False,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
    }


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    """Reduce persisted evidence to full post-HK repository readiness."""

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
    authenticate_committed_hk(root)
    validate_exact_hk_rebind(load_canonical(root / HJ_REFERENCE), candidate_value)
    if candidate.read_bytes() != runtime.read_bytes():
        raise PostHKBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    validate_current_hk_context(root, context, candidate.relative_to(root))
    if context["candidate_manifest_sha256"] != sha256_path(candidate):
        raise PostHKBindingError("PERSISTED_CONTEXT_CURRENT_IDENTITY_MISMATCH")
    bootstrap = context["qemu_executable_base_seed_checkout_bindings"]
    if (
        bootstrap["checkout"]["head"] != EXPECTED_HG_HEAD
        or bootstrap["checkout"]["tree"] != EXPECTED_HG_TREE
        or bootstrap["seed"]["sha256"] != HK_SEED_SHA256
        or context["wrapper_fc_er_che_schema_hashes"]["cloud_init"]
        != HK_CLOUD_INIT_SHA256
    ):
        raise PostHKBindingError("PERSISTED_BOOTSTRAP_CHECKOUT_COHERENCE_MISMATCH")
    counters = {key: 0 for key in (
        "authority_consumption", "e05_credit", "fm_operational_launcher_invocation",
        "human_operational_authority", "operation_attempt", "operational_replay",
        "p11_entry", "pre", "protected_effect", "protected_invocation", "qemu",
        "repair_and_continue", "request", "retry", "vm_boot", "vm_creation",
        "wrong_input_operation"
    )}
    negative_cases = [
        "MISSING_CURRENT_CANDIDATE", "WRONG_CANDIDATE_IDENTITY",
        "STALE_LAUNCHER_IDENTITY", "WRONG_LAUNCHER_IDENTITY",
        "MISSING_CURRENT_CONTEXT", "WRONG_CONTEXT_IDENTITY",
        "STALE_CHECKOUT_OWNER", "WRONG_CHECKOUT_OWNER", "MIXED_CHECKOUT_HEAD_TREE",
        "STALE_BOOTSTRAP_PAIR", "WRONG_BOOTSTRAP_PAIR", "MIXED_BOOTSTRAP_HEAD_TREE",
        "CANDIDATE_RUNTIME_MISMATCH", "INVALID_GUEST_PROJECTION", "MISSING_DU",
        "STALE_DU", "MISSING_EB", "STALE_EB", "MISSING_EE", "STALE_EE",
        "AUTHORITY_SUBSTITUTION_ATTEMPT", "DUPLICATE_JSON_KEY"
    ]
    return {
        "schema_id": "G77_256HL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HL",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry_authentication": {
            "status": "VERIFIED", "branch": EXPECTED_BRANCH, "head": EXPECTED_HEAD,
            "tree": EXPECTED_TREE, "subject": EXPECTED_SUBJECT,
            "remote_head": EXPECTED_HEAD, "stable_ancestry_anchor": STABLE_ANCESTRY_ANCHOR,
            "entry_worktree_state": "CLEAN", "index_state": "EMPTY",
            "nested_authority_head": NESTED_AUTHORITY_HEAD,
            "nested_authority_tree": NESTED_AUTHORITY_TREE,
            "nested_authority_state": "CLEAN__DETACHED__PINNED"
        },
        "hk_frontier": {
            "authentication_status": "VERIFIED",
            "branch": "BRANCH_A__BOOTSTRAP_CORRECTION_VERIFIED",
            "last_verified_edge": "CURRENT_HG_GUEST_BOOTSTRAP_BINDING_REPOSITORY_CAPABILITY_WITH_HJ_BOOTSTRAP_FAILURE_CLASS_STATICALLY_BLOCKED",
            "first_unproven_edge": "POST_HK_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_REAUTHENTICATION",
            "minimum_missing_capability": "POST_HK_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_REAUTHENTICATION",
            "minimum_legal_next_development_delta": "AFTER_HUMAN_COMMIT_ONLY__ONE_BOUNDED_REPOSITORY_ONLY_POST_HK_LIVE_BINDING_AND_READINESS_REAUTHENTICATION__NO_OPERATION"
        },
        "committed_identities": {
            "hk_head": EXPECTED_HEAD, "hk_tree": EXPECTED_TREE,
            "fm_launcher_sha256": FM_LAUNCHER_SHA256,
            "hk_cloud_init_sha256": HK_CLOUD_INIT_SHA256,
            "hk_nocloud_seed_sha256": HK_SEED_SHA256,
            "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
            "hg_checkout_head": EXPECTED_HG_HEAD, "hg_checkout_tree": EXPECTED_HG_TREE
        },
        "dependency_discovery": {
            "post_hk_dependency_set": ["CURRENT_CANDIDATE_LAUNCHER_HASH", "CURRENT_RUNTIME_PROJECTION", "CURRENT_CONTEXT_CLOUD_INIT_AND_SEED", "CURRENT_DU", "CURRENT_EB", "CURRENT_EE", "AUTHORITY_FREE_STATIC_READINESS"],
            "post_hk_rebind_required_set": ["GY_WRONG_INPUT_CANDIDATE_HK_HEAD_TREE_LAUNCHER_HASH_AND_SEAL", "BYTE_IDENTICAL_RUNTIME_PROJECTION", "FM_FRESH_OPERATION_CONTEXT_HK_IDENTITY_CANDIDATE_HASH_AND_HK_BOOTSTRAP"],
            "post_hk_fresh_receipt_required_set": ["DU_CURRENT_VALIDATION_RESULT", "EB_CANDIDATE_BOUND_RECEIPT", "EE_RUNTIME_CONSUMER_BINDING_RECEIPT"],
            "post_hk_revalidation_required_set": ["HG_CHECKOUT_HK_BOOTSTRAP_COHERENCE", "HG_PROJECTION", "GY_HA_SEMANTIC_FIREWALL", "HF_HH_HJ_BLOCKER_NON_REGRESSION", "PREAUTHORIZATION_NEGATIVE_MATRIX", "AUTHORITY_FREE_STATIC_READINESS"],
            "post_hk_unchanged_reuse_set": ["HG_CHECKOUT_AND_CONTEXT_OWNER_BYTES", "GY_WRONG_INPUT_SEMANTICS", "HA_GUEST_ADAPTER", "FM_CONTEXT_BUILDER_AND_VALIDATORS", "DU_EB_EE_VALIDATORS", "P11_CHE_FK", "EX_COMMON_SUBSTRATE_17_OF_17"],
            "post_hk_historical_non_applicable_set": ["HF_OPERATIONAL_HISTORY", "HJ_RECEIPTS_AS_CURRENT_HK_RECEIPTS", "HK_PRECOMMIT_SNAPSHOT_REBUILDS"]
        },
        "reuse": {
            "reuse_search_status": "VERIFIED",
            "reused_binder_set": ["GY_BINDER", "FM_CONTEXT_BUILDER"],
            "reused_owner_set": ["FM_SOLE_LAUNCHER", "HG_COMMITTED_CHECKOUT", "HK_BOOTSTRAP_PAIR", "GY_WRONG_INPUT_OWNERS", "P11_CHE_FK", "EX_COMMON_SUBSTRATE"],
            "reused_validator_set": ["DU", "EB", "EE", "FM_IMMUTABLE_CONTEXT", "FM_CHECKOUT_OWNER", "FM_BOOTSTRAP", "HG_PROJECTION", "GY_REDUCER", "GOVERNANCE_CONFORMANCE"],
            "new_generic_framework_required": False, "ex_reused": "17/17", "ex_reconstructed": 0
        },
        "live_binding": {
            "post_hk_candidate_binding_status": "VERIFIED",
            "post_hk_candidate_identity_status": "VERIFIED",
            "post_hk_launcher_binding_status": "VERIFIED",
            "post_hk_bootstrap_binding_status": "VERIFIED",
            "post_hk_checkout_binding_status": "VERIFIED",
            "post_hk_runtime_projection_status": "VERIFIED",
            "candidate_runtime_identity_equality_status": "VERIFIED",
            "runtime_projection_route_count": 1,
            "post_hk_context_binding_status": "VERIFIED",
            "fm_context_owner_binding_status": "VERIFIED",
            "current_hg_checkout_owner_binding_status": "VERIFIED",
            "current_hg_bootstrap_binding_status": "VERIFIED",
            "checkout_bootstrap_identity_coherence_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "candidate_sha256": sha256_path(candidate),
            "candidate_inner_sha256": candidate_value["manifest_sha256"],
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "eb_receipt_sha256": sha256_path(eb_receipt),
            "ee_receipt_sha256": sha256_path(ee_receipt),
            "ee_harness_sha256": sha256_path(harness)
        },
        "du_eb_ee": {
            "du_status": "PASS", "eb_status": "PASS", "ee_status": "PASS",
            "du_reauthentication_status": "VERIFIED__FRESH_CURRENT_RESULT",
            "eb_reauthentication_status": "VERIFIED__FRESH_CURRENT_RECEIPT",
            "ee_reauthentication_status": "VERIFIED__FRESH_CURRENT_RECEIPT",
            "current_applicability_status": "VERIFIED_INDEPENDENTLY"
        },
        "coherence_and_non_regression": {
            "stale_pre_hg_bootstrap_rejection_status": "VERIFIED",
            "hg_projection_binding_status": "VERIFIED",
            "host_canonical_binding_status": "VERIFIED",
            "guest_projection_binding_status": "VERIFIED",
            "projection_equivalence_status": "VERIFIED",
            "host_binding_preservation_status": "VERIFIED",
            "unauthorized_mutation_rejection_status": "VERIFIED",
            "hf_failure_class_static_block_status": "VERIFIED",
            "hh_failure_class_static_block_status": "VERIFIED",
            "hj_failure_class_static_block_status": "VERIFIED",
            "hk_bootstrap_correction_preservation_status": "VERIFIED"
        },
        "semantic_firewall": {
            "case": CASE_CLASS, "target_mutation": TARGET_MUTATION,
            "dependent_recomputation": DEPENDENT_RECOMPUTATION,
            "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
            "expected_differing_fields": ["input_identity", "record_identity"],
            "wrong_input_semantic_firewall_status": "VERIFIED",
            "same_class_review_status": "VERIFIED", "gy_reducer_semantics_status": "VERIFIED",
            "wrong_input_binding_status": "VERIFIED"
        },
        "preauthorization_negative_matrix": {
            "status": "VERIFIED", "case_count": len(negative_cases),
            "failure_before_authority_status": "VERIFIED", "cases": negative_cases
        },
        "proof_impact": {
            "changed_owner_set": ["FM_CURRENT_BOOTSTRAP_ASSET_SELECTION", "HK_CLOUD_INIT", "HK_NOCLOUD_SEED"],
            "dependent_proof_set": ["CURRENT_CANDIDATE_LAUNCHER_HASH", "CURRENT_CONTEXT_CLOUD_INIT_AND_SEED", "CURRENT_DU_EB_EE", "AUTHORITY_FREE_STATIC_READINESS"],
            "invalidated_proof_frontier": ["HJ_CANDIDATE_CONTEXT_DU_EB_EE_AS_CURRENT_POST_HK_LIVE_BINDING"],
            "revalidated_proof_set": ["HL_FOCUSED", "HK_FOCUSED", "HJ_APPLICABLE", "HI_APPLICABLE", "HG_PROJECTION", "GY_HA_SEMANTICS", "GOVERNANCE_CONFORMANCE", "EX", "LAYER0"],
            "reused_unchanged_proof_set": ["HJ_COMMITTED_HISTORY", "HD_HISTORICAL_ASSETS", "HG_CONTEXT_OWNER_AND_PROJECTION", "GY_HA_WRONG_INPUT_SEMANTICS", "P11_CHE_FK", "EX_17_OF_17"]
        },
        "readiness": {
            "terminal_branch": "BRANCH_A__FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "no_known_repository_preauthorization_blocker_status": "VERIFIED",
            "preoperational_readiness_status": "VERIFIED",
            "next_operational_generation_eligible": "VERIFIED",
            "authorized": False,
            "last_verified_edge": "FULL_POST_HK_AUTHORITY_FREE_STATIC_READINESS_FOR_ONE_WRONG_INPUT_ROUTE",
            "first_unproven_edge": "ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION"
        },
        "capability_boundary": {
            "candidate_capability": "VERIFIED",
            "post_hk_live_binding_candidate_capability": "VERIFIED",
            "post_hk_live_binding_repository_capability": "VERIFIED",
            "post_hk_live_binding_operational_capability": "NOT_PROVEN",
            "current_hg_guest_bootstrap_binding_candidate_capability": "VERIFIED",
            "current_hg_guest_bootstrap_binding_repository_capability": "VERIFIED",
            "current_hg_guest_bootstrap_binding_operational_capability": "NOT_PROVEN",
            "projection_aware_validation_repository_capability": "VERIFIED",
            "wrong_input_candidate_capability": "VERIFIED",
            "wrong_input_repository_capability": "VERIFIED",
            "wrong_input_operational_capability": "NOT_PROVEN"
        },
        "reuse_impact": {
            "existing_capability_unreachable": False,
            "new_capability_created": "POST_HK_COMMITTED_IDENTITY_LIVE_BINDING_AND_REPOSITORY_PREOPERATIONAL_READINESS_ONLY",
            "parallel_flow_created": False, "production_route_before": 1,
            "production_route_after": 1, "production_route_delta": 0
        },
        "operational_counters": counters,
        "e05": {"before": "7/18", "credit": 0, "after": "7/18", "remaining": 11},
        "validation": {
            "hl_focused": "PASS__12_OF_12", "hk_focused": "PASS__20_OF_20",
            "hj_applicable": "PASS__3_OF_3__10_HISTORICAL_OR_INVALIDATED_DESELECTED",
            "hi_applicable": "PASS__7_OF_7__5_HISTORICAL_MATERIALIZATION_CASES_DESELECTED",
            "hg_projection": "PASS__10_OF_10",
            "gy_ha_semantics": "PASS__28_OF_28__6_HISTORICAL_SNAPSHOTS_DESELECTED",
            "full_authority_free_static_readiness": "PASS__STATIC_READINESS_PASS__ZERO_AUTHORITY__ZERO_QEMU",
            "governance_tests": "PASS__9_OF_9",
            "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__ZERO_RECONSTRUCTED",
            "layer_0_freeze": "PASS", "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_ast_syntax": "PASS", "single_route": "PASS", "git_diff_check": "PASS"
        },
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE"},
            "cross_worker_state_recovery_level": {"status": "VERIFIED", "value": "COMMITTED_HK_RECONSTRUCTED"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "value": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED", "value": "BOUNDED_HL_COMMISSION_ONLY"},
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_identity_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_memory_required": {"status": "VERIFIED", "value": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED", "value": "YES"},
            "intra_task_cross_worker_continuation": {"status": "NOT_APPLICABLE"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "value": "ZERO_DETECTED"},
            "same_worker_provider_reset_resume": {"status": "NOT_APPLICABLE"},
            "handoff_sufficiency_status": {"status": "VERIFIED"},
            "handoff_prompt_eligibility": {"status": "VERIFIED", "value": "HUMAN_REVIEW_ONLY"},
            "handoff_state_completeness": {"status": "VERIFIED"},
            "handoff_reconstruction_required": {"status": "VERIFIED"},
            "handoff_reconstruction_success": {"status": "VERIFIED"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "value": 0},
            "unauthenticated_handoff_assumption_count": {"status": "VERIFIED", "value": 0}
        },
        "metrics": {
            "project_progress_estimate": {"status": "ESTIMATED", "value": "POST_HK_REPOSITORY_READINESS_COMPLETE"},
            "constitutional_health_evidence": {"status": "VERIFIED"},
            "shadow_automation_status": {"status": "VERIFIED", "value": "ABSENT"},
            "constitutional_frontier_distance": {"status": "VERIFIED", "value": "ONE_SEPARATELY_HUMAN_AUTHORIZED_OPERATIONAL_GENERATION"},
            "e05_frontier_distance": {"status": "VERIFIED", "value": 11},
            "selected_e05_local_frontier_distance": {"status": "VERIFIED", "value": "ONE_FUTURE_HUMAN_OPERATIONAL_GENERATION"},
            "governance_efficiency": {"status": "ESTIMATED", "value": "TARGETED_AFFECTED_FRONTIER"},
            "architectural_governance_efficiency": {"status": "VERIFIED", "value": "ONE_ROUTE_RETAINED"},
            "proof_reuse_efficiency": {"status": "ESTIMATED", "value": "HIGH__EX_17_OF_17_AND_EXISTING_OWNERS_REUSED"},
            "cognition_assisted_handoff": {"status": "VERIFIED"},
            "aigol_codex_work_share": {"status": "NOT_MEASURED"},
            "overengineering_risk": {"status": "ESTIMATED", "value": "LOW"},
            "proof_process_overhead_risk": {"status": "ESTIMATED", "value": "MEDIUM"},
            "cognition_provenance": {"status": "VERIFIED", "value": "REPOSITORY_BYTES_GIT_OBJECTS_AND_COMMISSION_SCOPE"},
            "shadow_design_target": {"status": "NOT_APPLICABLE"},
            "constitutional_continuation_progress": {"status": "VERIFIED", "value": "PREOPERATIONAL_READINESS_VERIFIED"},
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
            "infrastructure_amortization_signal": {"status": "ESTIMATED", "value": "POSITIVE_REUSE_SIGNAL_WITH_ZERO_CREDIT"},
            "workers_used": {"status": "VERIFIED", "value": 1},
            "provider_capacity_start": {"status": "NOT_MEASURED"},
            "provider_capacity_end": {"status": "NOT_MEASURED"},
            "provider_capacity_consumed": {"status": "NOT_MEASURED"},
            "wall_time": {"status": "NOT_MEASURED"},
            "llm_execution_efficiency": {"status": "ESTIMATED", "value": "TARGETED_REVALIDATION_WITH_REUSE"},
            "revalidation_case_count": {"status": "VERIFIED", "value": 122},
            "new_code": {"status": "VERIFIED", "value": "ONE_THIN_HL_BINDER_AND_ONE_FOCUSED_TEST_MODULE"},
            "reused_code": {"status": "VERIFIED", "value": "GY_FM_DU_EB_EE_HK_HG_HI_HJ_HA_EX_OWNERS"},
            "new_proof": {"status": "VERIFIED", "value": "HL_12_CASES"},
            "reused_proof": {"status": "VERIFIED", "value": "EX_17_OF_17"},
            "revalidated_proof": {"status": "VERIFIED", "value": 122},
            "reconstructed_proof": {"status": "VERIFIED", "value": 0},
            "new_generic_framework_count": {"status": "VERIFIED", "value": 0},
            "new_production_route_count": {"status": "VERIFIED", "value": 0},
            "new_authority_layer_count": {"status": "VERIFIED", "value": 0},
            "reused_infrastructure_count": {"status": "VERIFIED", "value": 10},
            "complexity_classification": {"status": "VERIFIED", "value": "A__PRIMARILY_REUSE_AND_REBINDING"}
        },
        "terminal_control": {
            "auto_continuable": False, "human_review_required": True,
            "minimum_missing_capability": "ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION",
            "minimum_legal_next_development_delta": "AFTER_HUMAN_COMMIT_ONLY__ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION",
            "verdict": "PASS__G77_256HL_FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED__ONE_ROUTE__ZERO_AUTHORITY__ZERO_OPERATION__WRONG_INPUT_OPERATIONAL_CAPABILITY_NOT_PROVEN__E05_7_OF_18__HUMAN_REVIEW_REQUIRED"
        }
    }


def write_terminal_reduction(
    *, repository_root: Path, live_root: Path, output_path: Path
) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    envelope = {
        "schema_id": "G77_256HL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise PostHKBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
