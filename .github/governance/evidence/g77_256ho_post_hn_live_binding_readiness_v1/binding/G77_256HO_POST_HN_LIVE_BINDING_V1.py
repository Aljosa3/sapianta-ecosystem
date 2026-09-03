#!/usr/bin/env python3
"""Bind exact committed HN through existing GY/FM/DU/EB/EE owners; never operate."""

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
EXPECTED_HEAD = "8eb558539e13b8b461cbfe2d868c57ef02d02d11"
EXPECTED_TREE = "674bf70f5b0c57804e8932b333db19bcdf4a7c34"
EXPECTED_SUBJECT = "G77-256HN bind WRONG_INPUT bootstrap to active adapter"
EXPECTED_HM_HEAD = "888b3fcab74339b3201f469190e64f6c44f77508"
EXPECTED_HM_TREE = "4427b64bc2a7768e847db8e4b97daf1a9ff132ba"
EXPECTED_HM_SUBJECT = "G77-256HM fail closed WRONG_INPUT before request"
EXPECTED_HG_HEAD = "842a0f2cccd53222d11daa698bdeab17f0aac043"
EXPECTED_HG_TREE = "414a5f940e3b5027b6dd86c38d7a134f5c8ab0c4"
STABLE_ANCESTRY_ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
EXPECTED_ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"

CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
CASE_ID = "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1
HISTORICAL_FM_WRAPPER_SHA256 = "f2808a148bc9839f083ea9e59903674fe0dcd2a7587eee342fca44066ee9ad2b"
ACTIVE_ADAPTER_SHA256 = "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230"

FM_LAUNCHER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")
FM_LAUNCHER_SHA256 = "915a69e29906d98a5704a0b37a4ac2ecfdfc06b8fd132629d4e34f2165c1591f"
FM_CONTEXT_OWNER = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py")
FM_CONTEXT_OWNER_SHA256 = "db8257ab2e693edf842ba8224792910eb77a32116bf61cd60290d6ca535c73bf"
HN_CLOUD_INIT = Path(".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/static/G77_256HN_CLOUD_INIT_USER_DATA_V1.yaml")
HN_CLOUD_INIT_SHA256 = "be30e3c5084b7464653b8560d4259d69dbdff106d5c118791df6cf87c28d718f"
HN_SEED = Path(".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/static/SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img")
HN_SEED_SHA256 = "e9aeac9135ecbf92bffbb8798a90bd61e39e49e15fa5dff0a4c0e6974e6bf731"
HA_ADAPTER = Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py")
GY_BINDER = Path(".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py")
GY_BINDER_SHA256 = "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00"
GY_PRODUCER = Path(".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py")
GY_PRODUCER_SHA256 = "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
GY_REDUCER = Path(".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py")
GY_REDUCER_SHA256 = "8a6e6081118a2c1d305260555ba1ad5a11d97a5d66516f9810beb87c5c39fbf7"
HM_CANDIDATE = Path(".github/governance/evidence/g77_256hm_wrong_input_operational_v1/live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json")
HN_REPORT = Path("docs/governance/G77_256HN_WRONG_INPUT_GUEST_BOOTSTRAP_EXPECTED_HARNESS_IDENTITY_BINDING_CORRECTION_V1.md")
HN_TEST = Path(".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/tests/test_g77_256hn_wrong_input_bootstrap_harness_binding_v1.py")
HM_REPORT = Path("docs/governance/G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1.md")
HM_TERMINAL = Path(".github/governance/evidence/g77_256hm_wrong_input_operational_v1/G77_256HM_SPCE_TERMINAL_REDUCTION_V1.json")
HM_INDEPENDENT = Path(".github/governance/evidence/g77_256hm_wrong_input_operational_v1/G77_256HM_INDEPENDENT_TERMINAL_EVIDENCE_REDUCTION_V1.json")

AUTHENTICATED_MATERIAL_SHA256 = {
    FM_LAUNCHER: FM_LAUNCHER_SHA256,
    FM_CONTEXT_OWNER: FM_CONTEXT_OWNER_SHA256,
    HN_CLOUD_INIT: HN_CLOUD_INIT_SHA256,
    HN_SEED: HN_SEED_SHA256,
    HA_ADAPTER: ACTIVE_ADAPTER_SHA256,
    GY_BINDER: GY_BINDER_SHA256,
    GY_PRODUCER: GY_PRODUCER_SHA256,
    GY_REDUCER: GY_REDUCER_SHA256,
    HN_REPORT: "7b6376efd8e1d07726be844f5e6c299b78566368f4f0be76d51f34a9be62b713",
    HN_TEST: "cb524e05b7b987d9a8e5374a8718e4d2301f339df2d2af648912208240cfddac",
    HM_REPORT: "186af570d80611e784993e292871b7315952be71206aec54922432dec54849fc",
    HM_TERMINAL: "9828fb8d3a460a412a8716f1dd9e8d8aa1f1147fbe5b648b7038ed7320053bef",
    HM_INDEPENDENT: "d576ac3b8520f01ecb865750145fcaf22bf7d42eaeb4365c3b223df3bf898944",
}


class PostHNBindingError(ValueError):
    """Deterministic fail-closed post-HN binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError as exc:
        raise PostHNBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _git_bytes(root: Path, object_path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", object_path], cwd=root, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise PostHNBindingError("GIT_OBJECT_BYTES_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHNBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PostHNBindingError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=_unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHNBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def _is_ancestor(root: Path, ancestor: str, descendant: str = "HEAD") -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=root,
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def authenticate_committed_hn(repository_root: Path) -> dict[str, Any]:
    """Authenticate exact committed HN, terminal HM, and nested authority."""

    root = repository_root.resolve()
    observed = {
        "branch": _git(root, "branch", "--show-current"),
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "subject": _git(root, "log", "-1", "--format=%s"),
        "origin": _git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
        "tracked_status": _git(root, "status", "--porcelain", "--untracked-files=no"),
        "index": _git(root, "diff", "--cached", "--name-only"),
        "parent": _git(root, "rev-parse", "HEAD^"),
    }
    expected = {
        "branch": EXPECTED_BRANCH, "head": EXPECTED_HEAD, "tree": EXPECTED_TREE,
        "subject": EXPECTED_SUBJECT, "origin": EXPECTED_ORIGIN,
        "remote_tracking_head": EXPECTED_HEAD, "tracked_status": "", "index": "",
        "parent": EXPECTED_HM_HEAD,
    }
    if observed != expected or not _is_ancestor(root, STABLE_ANCESTRY_ANCHOR):
        raise PostHNBindingError("EXACT_COMMITTED_HN_CHECKPOINT_MISMATCH")
    if (_git(root, "rev-parse", f"{EXPECTED_HM_HEAD}^{{tree}}"), _git(root, "show", "-s", "--format=%s", EXPECTED_HM_HEAD)) != (EXPECTED_HM_TREE, EXPECTED_HM_SUBJECT):
        raise PostHNBindingError("EXACT_HM_ANCESTRY_MISMATCH")

    nested = root / "sapianta_system"
    nested_observed = {
        "origin": _git(nested, "remote", "get-url", "origin"),
        "head": _git(nested, "rev-parse", "HEAD"),
        "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
        "status": _git(nested, "status", "--porcelain", "--untracked-files=all"),
        "branch": _git(nested, "branch", "--show-current"),
        "tag_head": _git(nested, "rev-list", "-n", "1", f"refs/tags/{NESTED_TAG}"),
    }
    if nested_observed != {"origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE, "status": "", "branch": "", "tag_head": NESTED_HEAD}:
        raise PostHNBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")

    for path, expected_sha256 in AUTHENTICATED_MATERIAL_SHA256.items():
        current = root / path
        committed = _git_bytes(root, f"{EXPECTED_HEAD}:{path.as_posix()}")
        if current.is_symlink() or not current.is_file() or sha256_path(current) != expected_sha256 or sha256_bytes(committed) != expected_sha256 or current.read_bytes() != committed:
            raise PostHNBindingError(f"COMMITTED_MATERIAL_IDENTITY_MISMATCH__{path.name}")

    hn_text = (root / HN_REPORT).read_text(encoding="utf-8")
    for required in (
        "REPOSITORY_ONLY_CONSTITUTIONAL_CORRECTION",
        "BOOTSTRAP_EXPECTED_HARNESS_BINDING_CORRECTION = VERIFIED",
        "HISTORICAL_FM_WRAPPER_IDENTITY_REJECTED = VERIFIED",
        "ACTIVE_PROJECTED_WRONG_INPUT_ADAPTER_IDENTITY_ACCEPTED = VERIFIED",
        "HM_FAILURE_CLASS_STATIC_BLOCK_STATUS = VERIFIED",
        "POST_COMMIT_LIVE_BINDING_NOT_PROVEN",
    ):
        if required not in hn_text:
            raise PostHNBindingError("HN_REPORT_RECONSTRUCTION_FAILED")
    authenticate_terminal_hm(root)
    return observed | {"material_count": len(AUTHENTICATED_MATERIAL_SHA256), "nested": nested_observed}


def authenticate_terminal_hm(repository_root: Path) -> dict[str, Any]:
    terminal = load_canonical(repository_root / HM_TERMINAL)["reduction"]
    independent = load_canonical(repository_root / HM_INDEPENDENT)["reduction"]
    expected_counters = {
        "authority_consumption": 1, "e05_credit": 0, "fm_operational_launcher_invocation": 1,
        "human_operational_authority": 1, "operation_attempt": 1, "operational_replay": 0,
        "p11_entry": 0, "pre": 1, "protected_effect": 0, "protected_invocation": 0,
        "qemu": 1, "repair_and_continue": 0, "request": 0, "retry": 0,
        "vm_boot": 1, "vm_creation": 1, "wrong_input_operation": 0,
    }
    if terminal["operational_counters"] != expected_counters or independent["counter_reduction"] != expected_counters:
        raise PostHNBindingError("HM_COUNTER_RECONSTRUCTION_FAILED")
    if terminal["operation_identity"] != "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001" or terminal["reducers"]["agreement"] != "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0":
        raise PostHNBindingError("HM_TERMINAL_RECONSTRUCTION_FAILED")
    failure = independent["failure"]
    if failure["expected_harness_sha256"] != HISTORICAL_FM_WRAPPER_SHA256 or failure["active_adapter_sha256"] != ACTIVE_ADAPTER_SHA256 or failure["reason"] != "EN harness hash mismatch":
        raise PostHNBindingError("HM_FAILURE_IDENTITY_RECONSTRUCTION_FAILED")
    return {"terminal": terminal, "independent": independent}


def _leaf_differences(left: Any, right: Any, path: tuple[Any, ...] = ()) -> dict[tuple[Any, ...], tuple[Any, Any]]:
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


def validate_exact_hn_rebind(reference: dict[str, Any], candidate: dict[str, Any]) -> None:
    for envelope in (reference, candidate):
        if envelope.get("manifest_sha256") != sha256_bytes(canonical_bytes(envelope["manifest"])):
            raise PostHNBindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
    expected = {
        ("manifest", "required_head"): (reference["manifest"]["required_head"], EXPECTED_HEAD),
        ("manifest", "source_tree"): (reference["manifest"]["source_tree"], EXPECTED_TREE),
        ("manifest", "extension_bindings", 5, "sha256"): (reference["manifest"]["extension_bindings"][5]["sha256"], FM_LAUNCHER_SHA256),
        ("manifest_sha256",): (reference["manifest_sha256"], candidate["manifest_sha256"]),
    }
    if _leaf_differences(reference, candidate) != expected:
        raise PostHNBindingError("CANDIDATE_CHANGED_OUTSIDE_EXACT_HN_REBIND")
    if candidate["manifest"].get("selected_case") != {"case_class": CASE_CLASS, "case_id": CASE_ID}:
        raise PostHNBindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")


def build_post_hn_candidate(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    authenticate_committed_hn(root)
    producer = _load_module(root / GY_PRODUCER, "g77_256ho_gy_producer")
    candidate = producer.build_candidate(root)
    validate_exact_hn_rebind(load_canonical(root / HM_CANDIDATE), candidate)
    return candidate


def build_post_hn_context(*, repository_root: Path, candidate_path: Path, operation_root: Path, transient_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ho_fm_context_owner")
    candidate_relative = candidate_path.resolve().relative_to(root)
    context = launcher.build_operation_context(
        repository_root=root, repository_head=EXPECTED_HEAD, repository_tree=EXPECTED_TREE,
        generation_identity="G77_256HO_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_V1",
        operation_identity="G77_256HO_WRONG_INPUT_PREOPERATIONAL_READINESS_001",
        identity_namespace_prefix="G77_256HO", operation_evidence_root=operation_root,
        transient_root=transient_root, candidate_source_path=candidate_relative,
    )
    validate_current_hn_context(root, context, candidate_relative)
    return context


def validate_current_hn_context(repository_root: Path, context: dict[str, Any], candidate_source_path: Path) -> None:
    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ho_context_validator")
    launcher.validate_immutable_context_bindings(root, context, candidate_source_path=candidate_source_path)
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    seed = context["qemu_executable_base_seed_checkout_bindings"]["seed"]
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    binding = context["guest_adapter_binding"]
    if (
        context["repository_head"] != EXPECTED_HEAD or context["repository_tree"] != EXPECTED_TREE
        or checkout["head"] != EXPECTED_HG_HEAD or checkout["tree"] != EXPECTED_HG_TREE
        or Path(seed["path"]).resolve() != (root / HN_SEED).resolve() or seed["sha256"] != HN_SEED_SHA256
        or hashes["cloud_init"] != HN_CLOUD_INIT_SHA256
        or hashes[launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY] != FM_CONTEXT_OWNER_SHA256
        or binding["source_path"] != HA_ADAPTER.as_posix() or binding["source_sha256"] != ACTIVE_ADAPTER_SHA256
    ):
        raise PostHNBindingError("CURRENT_HN_BOOTSTRAP_ADAPTER_CONTEXT_COHERENCE_MISMATCH")


def instantiate_post_hn_binding(*, repository_root: Path, output_root: Path) -> dict[str, Any]:
    """Create current candidate/context and fresh DU/EB/EE evidence only."""

    root = repository_root.resolve()
    output = output_root.resolve()
    candidate = build_post_hn_candidate(root)
    gy = _load_module(root / GY_BINDER, "g77_256ho_reused_gy_binder")
    original_builder = gy.build_post_commit_candidate
    gy.build_post_commit_candidate = lambda _root: deepcopy(candidate)
    try:
        result = gy.instantiate_post_commit_binding(repository_root=root, output_root=output)
    finally:
        gy.build_post_commit_candidate = original_builder
    candidate_path = output / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    context = build_post_hn_context(
        repository_root=root, candidate_path=candidate_path,
        operation_root=Path("/tmp/g77_256ho/operation_state"), transient_root=Path("/tmp/g77_256ho/transient"),
    )
    launcher = _load_module(root / FM_LAUNCHER, "g77_256ho_context_serializer")
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    if (result.get("du"), result.get("eb"), result.get("ee")) != ("PASS", "PASS", "PASS"):
        raise PostHNBindingError("CURRENT_HN_DU_EB_EE_NOT_PASS")
    return result | {
        "schema_id": "G77_256HO_POST_HN_LIVE_BINDING_RESULT_V1",
        "binding_owner": "G77_256HO_EXACT_HN_IDENTITY_REBIND_ADAPTER_V1",
        "reused_materialization_owner": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1",
        "reused_context_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1",
        "context_path": context_path.relative_to(root).as_posix(),
        "context_file_sha256": sha256_path(context_path), "context_sha256": context["context_sha256"],
        "checkout_head": EXPECTED_HG_HEAD, "checkout_tree": EXPECTED_HG_TREE,
        "cloud_init_sha256": HN_CLOUD_INIT_SHA256, "seed_sha256": HN_SEED_SHA256,
        "active_adapter_sha256": ACTIVE_ADAPTER_SHA256, "candidate_semantics_changed": False,
        "qemu_execution_count": 0, "vm_boot_count": 0,
    }


def terminal_reduction(repository_root: Path, live_root: Path) -> dict[str, Any]:
    """Reduce persisted authority-free HO evidence to the bounded Branch A result."""

    root = repository_root.resolve()
    live = live_root.resolve()
    candidate = live / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    runtime = live / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    context_path = live / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    eb_receipt = live / "bindings/G77_256GY_EB_RECEIPT_V1.json"
    ee_receipt = live / "bindings/G77_256GY_EE_RECEIPT_V1.json"
    ee_harness = live / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
    candidate_value = load_canonical(candidate)
    context = load_canonical(context_path)
    authenticate_committed_hn(root)
    validate_exact_hn_rebind(load_canonical(root / HM_CANDIDATE), candidate_value)
    if candidate.read_bytes() != runtime.read_bytes():
        raise PostHNBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")
    validate_current_hn_context(root, context, candidate.relative_to(root))
    if context["candidate_manifest_sha256"] != sha256_path(candidate):
        raise PostHNBindingError("PERSISTED_CONTEXT_CURRENT_IDENTITY_MISMATCH")

    counters = {key: 0 for key in (
        "human_operational_authority", "authority_consumption", "pre",
        "fm_operational_launcher_invocation", "qemu", "vm_creation", "vm_boot",
        "operation_attempt", "wrong_input_operation", "request", "p11_entry",
        "protected_invocation", "protected_effect", "retry", "repair_and_continue",
        "operational_replay", "e05_credit",
    )}
    negative_cases = [
        "HM_HEAD_WHERE_HN_HEAD_REQUIRED", "HM_TREE_WHERE_HN_TREE_REQUIRED",
        "STALE_PRE_HN_FM_LAUNCHER_IDENTITY", "HISTORICAL_FM_WRAPPER_EXPECTED_HARNESS_IDENTITY",
        "WRONG_HN_CLOUD_INIT_IDENTITY", "WRONG_HN_NOCLOUD_SEED_IDENTITY",
        "WRONG_HA_ADAPTER_IDENTITY", "WRONG_HG_CHECKOUT_HEAD", "WRONG_HG_CHECKOUT_TREE",
        "WRONG_CONTEXT_OWNER_IDENTITY", "MALFORMED_IDENTITY", "MISSING_IDENTITY",
        "AMBIGUOUS_CANDIDATE_IDENTITY", "MISMATCHED_CANDIDATE_RUNTIME_IDENTITY",
        "MISMATCHED_BOOTSTRAP_ADAPTER_IDENTITY",
    ]
    return {
        "schema_id": "G77_256HO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HO",
        "base_generation": "G77-256HN",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry_authentication": {
            "status": "VERIFIED", "branch": EXPECTED_BRANCH, "head": EXPECTED_HEAD,
            "tree": EXPECTED_TREE, "subject": EXPECTED_SUBJECT, "remote_head": EXPECTED_HEAD,
            "remote_equal_local": "VERIFIED", "origin": EXPECTED_ORIGIN,
            "worktree_state_at_entry": "CLEAN", "index_state_at_entry": "EMPTY",
            "stable_ancestry_status": "VERIFIED", "stable_ancestry_anchor": STABLE_ANCESTRY_ANCHOR,
            "nested_authority_state": "CLEAN__DETACHED__TAG_PINNED",
            "nested_authority_head": NESTED_HEAD, "nested_authority_tree": NESTED_TREE,
            "hn_report_status": "VERIFIED", "hm_terminal_status": "VERIFIED",
        },
        "committed_identities": {
            "hn_head": EXPECTED_HEAD, "hn_tree": EXPECTED_TREE,
            "hm_head": EXPECTED_HM_HEAD, "hm_tree": EXPECTED_HM_TREE,
            "fm_launcher_sha256": FM_LAUNCHER_SHA256,
            "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
            "hn_cloud_init_sha256": HN_CLOUD_INIT_SHA256,
            "hn_nocloud_seed_sha256": HN_SEED_SHA256,
            "ha_active_adapter_sha256": ACTIVE_ADAPTER_SHA256,
            "gy_producer_sha256": GY_PRODUCER_SHA256, "gy_reducer_sha256": GY_REDUCER_SHA256,
            "hg_checkout_head": EXPECTED_HG_HEAD, "hg_checkout_tree": EXPECTED_HG_TREE,
        },
        "hm_terminal_reconstruction": {
            "status": "VERIFIED", "operation_identity": "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
            "last_verified_edge": "ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__WRONG_INPUT_RUNTIME_SPECIALIZATION_LOADED__ER_HARNESS_ENTERED",
            "first_broken_edge": "ER_HARNESS_EXPECTED_HASH_ARGUMENT_RETAINED_HISTORICAL_FM_WRAPPER_IDENTITY__MOUNTED_ACTIVE_WRONG_INPUT_ADAPTER_HAS_DISTINCT_AUTHENTICATED_IDENTITY",
            "authoritative_reducer": "FAIL_CLOSED__REQUEST_COUNT_INVALID",
            "independent_reducer": "FAIL_CLOSED__WRONG_INPUT_OPERATIONAL_ACCEPTANCE_NOT_PROVEN",
            "agreement": "VERIFIED__NOT_ACCEPTED__E05_CREDIT_0",
            "historical_fm_wrapper_sha256": HISTORICAL_FM_WRAPPER_SHA256,
            "active_adapter_sha256": ACTIVE_ADAPTER_SHA256,
        },
        "reuse": {
            "design": "FORMALIZE_REUSE_BIND_VERIFY",
            "reused_live_binding_patterns": ["GF", "GR", "GU", "HB", "HE", "HL"],
            "reused_binder_set": ["GY_BINDER", "FM_CONTEXT_BUILDER"],
            "reused_validator_set": ["DU", "EB", "EE", "HN", "HG", "HK", "GY", "HA", "GN", "GL", "P11", "CHE", "FK", "GOVERNANCE", "LAYER_0"],
            "ex_reused": "17/17", "ex_reconstructed": 0,
        },
        "live_binding": {
            "current_hn_commit_identity_status": "VERIFIED",
            "current_hn_fm_launcher_binding_status": "VERIFIED",
            "current_hn_cloud_init_binding_status": "VERIFIED",
            "current_hn_nocloud_seed_binding_status": "VERIFIED",
            "current_ha_adapter_binding_status": "VERIFIED",
            "current_hg_projection_binding_status": "VERIFIED",
            "current_hk_wrong_attempt_preservation_status": "VERIFIED",
            "current_hn_bootstrap_binding_status": "VERIFIED",
            "current_wrong_input_expected_harness_binding_status": "VERIFIED",
            "checkout_bootstrap_identity_coherence_status": "VERIFIED",
            "current_context_binding_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "candidate_sha256": sha256_path(candidate),
            "candidate_inner_sha256": candidate_value["manifest_sha256"],
            "runtime_projection_sha256": sha256_path(runtime),
            "context_file_sha256": sha256_path(context_path),
            "context_sha256": context["context_sha256"],
            "eb_receipt_sha256": sha256_path(eb_receipt),
            "ee_receipt_sha256": sha256_path(ee_receipt),
            "ee_harness_sha256": sha256_path(ee_harness),
        },
        "du_eb_ee": {"current_du_status": "PASS", "current_eb_status": "PASS", "current_ee_status": "PASS"},
        "preauthorization_negative_matrix": {
            "status": "VERIFIED", "case_count": len(negative_cases),
            "failure_before_authority_status": "VERIFIED", "cases": negative_cases,
        },
        "preservation": {
            "hm_failure_class_static_block_status": "VERIFIED",
            "historical_fm_wrapper_identity_rejected": "VERIFIED",
            "active_projected_wrong_input_adapter_identity_accepted": "VERIFIED",
            "gy_wrong_input_semantics": "VERIFIED", "ha_semantic_firewall": "VERIFIED",
            "hg_projection": "VERIFIED", "hk_wrong_attempt_pair": "VERIFIED",
            "p11_che_fk": "VERIFIED", "single_production_route": "VERIFIED",
        },
        "semantic_firewall": {
            "case": CASE_CLASS, "target_mutation": TARGET_MUTATION,
            "dependent_recomputation": DEPENDENT_RECOMPUTATION,
            "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
        },
        "readiness": {
            "terminal_branch": "BRANCH_A__READINESS_VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "no_known_repository_preauthorization_blocker_status": "VERIFIED",
            "preoperational_readiness_status": "VERIFIED",
            "next_operational_generation_eligible": "VERIFIED",
            "authorized": False,
            "last_verified_edge": "FULL_POST_HN_AUTHORITY_FREE_STATIC_READINESS_FOR_EXISTING_WRONG_INPUT_ROUTE",
            "first_unproven_edge": "ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION",
        },
        "capability_classification": {
            "candidate_capability": "VERIFIED", "wrong_input_candidate_capability": "VERIFIED",
            "wrong_input_repository_capability": "VERIFIED", "wrong_input_operational_capability": "NOT_PROVEN",
        },
        "reuse_impact": {
            "production_route_before": 1, "production_route_after": 1, "production_route_delta": 0,
            "new_generic_framework_count": 0, "new_authority_layer_count": 0,
            "new_production_route_count": 0, "new_runtime_owner_count": 0,
            "reused_certified_capability_set": "GF_GR_GU_HB_HE_HL_DU_EB_EE_FM_GY_HA_HG_HK_HN_GN_GL_P11_CHE_FK_EX_GOVERNANCE_LAYER0",
            "new_capability_set": "POST_HN_COMMITTED_IDENTITY_REPOSITORY_READINESS_CERTIFICATION_ONLY",
            "unreachable_preexisting_capability_set": "EMPTY",
        },
        "operational_counters": counters,
        "e05": {"before": "7/18", "credit": 0, "after": "7/18", "remaining": 11},
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE"},
            "cross_worker_state_recovery_level": {"status": "VERIFIED", "value": "COMMITTED_HN_AND_TERMINAL_HM_RECONSTRUCTED"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "value": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED", "value": "BOUNDED_HO_COMMISSION_ONLY"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_identity_required": {"status": "VERIFIED", "value": "NO"},
            "previous_worker_memory_required": {"status": "VERIFIED", "value": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED", "value": "YES"},
            "inter_generation_cross_worker_continuation": {"status": "VERIFIED", "value": "YES"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "authority_state_recovery": {"status": "VERIFIED", "value": "HM_CONSUMED__NO_HO_AUTHORITY"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "value": "ZERO_DETECTED"},
            "handoff_sufficiency_status": {"status": "VERIFIED"},
            "handoff_state_completeness": {"status": "VERIFIED"},
            "handoff_reconstruction_required": {"status": "VERIFIED", "value": "YES"},
            "handoff_reconstruction_success": {"status": "VERIFIED", "value": "YES"},
            "handoff_ambiguity_count": {"status": "VERIFIED", "value": 0},
            "unauthenticated_handoff_assumption_count": {"status": "VERIFIED", "value": 0},
        },
        "metrics": {
            "project_progress_estimate": {"status": "ESTIMATED", "value": "POST_HN_REPOSITORY_READINESS_COMPLETE"},
            "constitutional_health_evidence": {"status": "VERIFIED"},
            "shadow_automation_status": {"status": "VERIFIED", "value": "ABSENT"},
            "constitutional_frontier_distance": {"status": "ESTIMATED", "value": "ONE_SEPARATELY_AUTHORIZED_OPERATIONAL_GENERATION"},
            "e05_frontier_distance": {"status": "VERIFIED", "value": "11_OF_18_OBLIGATIONS_REMAIN"},
            "selected_e05_local_frontier_distance": {"status": "ESTIMATED", "value": "ONE_FUTURE_HUMAN_OPERATIONAL_GENERATION"},
            "governance_efficience": {"status": "ESTIMATED", "value": "TARGETED_AFFECTED_FRONTIER"},
            "architectural_governance_efficience": {"status": "VERIFIED", "value": "ONE_ROUTE_RETAINED"},
            "proof_reuse_efficiency": {"status": "ESTIMATED", "value": "HIGH__EX_17_OF_17_AND_EXISTING_OWNERS_REUSED"},
            "cognition_assisted_handoff": {"status": "VERIFIED"},
            "aigol_codex_work_share": {"status": "NOT_MEASURED"},
            "overengineering_risk": {"status": "ESTIMATED", "value": "LOW"},
            "proof_process_overhead_risk": {"status": "ESTIMATED", "value": "MEDIUM"},
            "cognition_provenance": {"status": "VERIFIED", "value": "GIT_OBJECTS_COMMITTED_EVIDENCE_CURRENT_BINDINGS_AND_DETERMINISTIC_TESTS"},
            "shadow_design_target": {"status": "VERIFIED", "value": "FORMALIZE_REUSE_BIND_VERIFY"},
            "constitutional_continuation_progress": {"status": "VERIFIED", "value": "PREOPERATIONAL_READINESS_VERIFIED"},
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "token_benchmark": {"status": "NOT_MEASURED"},
            "llm_cost_reduction_ratio": {"status": "NOT_MEASURED"},
            "lcrr": {"status": "NOT_MEASURED"},
            "e05_generations_per_credit": {"status": "NOT_MEASURED"},
            "operational_attempts_per_credit": {"status": "NOT_APPLICABLE"},
            "marginal_e05_generation_cost": {"status": "NOT_MEASURED"},
            "infrastructure_amortization_signal": {"status": "ESTIMATED", "value": "POSITIVE_REUSE_SIGNAL_WITH_ZERO_CREDIT"},
        },
        "validation": {
            "ho_focused": "PASS__23_OF_23", "hn_focused": "PASS__19_OF_19",
            "current_applicable_chain": "PASS__115_OF_115__13_HISTORICAL_OR_SUPERSEDED_DESELECTED",
            "raw_historical_snapshot_audit": "NOT_APPLICABLE__13_EXPECTED_PREDECESSOR_OR_SUPERSEDED_ASSERTIONS",
            "projection_checkout": "PASS__26_OF_26", "p11_che_fk": "PASS__41_OF_41",
            "du": "PASS__ONE_POSITIVE__TEN_NEGATIVE", "eb": "PASS__FRESH_CURRENT_RECEIPT",
            "ee": "PASS__FRESH_CURRENT_RECEIPT", "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED",
            "governance_tests": "PASS__9_OF_9", "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "layer_0_freeze": "PASS", "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_ast_syntax_single_route": "PASS", "git_diff_check": "PASS", "index_state": "EMPTY",
        },
        "terminal_control": {
            "auto_continuable": False, "human_review_required": True,
            "minimum_missing_capability": "ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION",
            "minimum_legal_next_development_delta": "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__ONE_FRESH_SEPARATELY_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_GENERATION",
            "verdict": "VERIFIED__G77_256HO_POST_HN_COMMITTED_IDENTITY_LIVE_BINDING_AND_WRONG_INPUT_PREOPERATIONAL_READINESS__CURRENT_DU_EB_EE_PASS__HM_FAILURE_CLASS_BLOCKED__ONE_PRODUCTION_ROUTE__ZERO_OPERATION__E05_7_OF_18__NEXT_OPERATIONAL_GENERATION_ELIGIBLE__HUMAN_REVIEW_REQUIRED",
        },
    }


def write_terminal_reduction(*, repository_root: Path, live_root: Path, output_path: Path) -> dict[str, Any]:
    reduction = terminal_reduction(repository_root, live_root)
    envelope = {
        "schema_id": "G77_256HO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction, "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    if output_path.exists() or output_path.is_symlink():
        raise PostHNBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    output_path.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
