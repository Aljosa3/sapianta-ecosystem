#!/usr/bin/env python3
"""Bind committed HD identity through existing GY/FM/DU/EB/EE owners."""

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
EXPECTED_HEAD = "2d7cf0e83620225238095684b2f2175a6f274556"
EXPECTED_TREE = "8b47e75336db898c5e8aad766471c2081716c315"
EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
EXPECTED_HC_HEAD = "a5fde262c8833922375a10e79c745c0ff19e698e"
EXPECTED_HC_TREE = "c265719bc048a9ab686e290d1952280d5584a43e"
CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1

HB_REFERENCE = Path(
    ".github/governance/evidence/g77_256hb_post_ha_live_binding_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
HB_REFERENCE_SHA256 = "fb60a1d3a800b3918909f1958e733dbe3529ed28ed20f1a4c2ce084116771b07"
GY_BINDER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/"
    "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
)
GY_BINDER_SHA256 = "bc4f4d9c4a9492a9e0d83b2b837b4e722d985f813cb9d365f7b6b9183c3b5c00"
GY_PRODUCER = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
GY_PRODUCER_SHA256 = "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_LAUNCHER_SHA256 = "a434d2ed4990c4c06167538b4f6805a46a69fbf2f303e357a5c0f59257a647dc"
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_CONTEXT_OWNER_SHA256 = "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca"
HD_CLOUD_INIT = Path(
    ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/"
    "G77_256HD_CLOUD_INIT_USER_DATA_V1.yaml"
)
HD_CLOUD_INIT_SHA256 = "95038a31879b3654607ae82533e9b043fee47e7cc157efdad1b7654a11664421"
HD_SEED = Path(
    ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/static/"
    "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)
HD_SEED_SHA256 = "15910599577a84545d79d49383747ce22e630d1cb3f1228509b307487a2261cf"
HD_TEST = Path(
    ".github/governance/evidence/g77_256hd_guest_context_owner_binding_v1/tests/"
    "test_g77_256hd_guest_context_owner_binding_v1.py"
)
HD_TEST_SHA256 = "65bdec5b8e8962cd30362b876280797028b83eb69a33be6791c5d614a1375213"
HD_REPORT = Path(
    "docs/governance/G77_256HD_GUEST_CONTEXT_OWNER_BINDING_CORRECTION_V1.md"
)
HD_REPORT_SHA256 = "e271ffdf9aaf9845920d46202144b833e990f28a30a9191c7bca946c39cfc356"

HD_MATERIAL_SHA256 = {
    FM_LAUNCHER: FM_LAUNCHER_SHA256,
    FM_CONTEXT_OWNER: FM_CONTEXT_OWNER_SHA256,
    HD_CLOUD_INIT: HD_CLOUD_INIT_SHA256,
    HD_SEED: HD_SEED_SHA256,
    HD_TEST: HD_TEST_SHA256,
    HD_REPORT: HD_REPORT_SHA256,
}


class PostHDBindingError(ValueError):
    """Deterministic fail-closed post-HD binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise PostHDBindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHDBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHDBindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_committed_hd(repository_root: Path) -> dict[str, Any]:
    """Authenticate exact committed HD material by bytes and Git blobs."""

    root = repository_root.resolve()
    observed = {
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
        "tracked_status": _git(root, "status", "--porcelain", "--untracked-files=no"),
        "index": _git(root, "diff", "--cached", "--name-only"),
    }
    expected = {
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "branch": EXPECTED_BRANCH,
        "remote_tracking_head": EXPECTED_HEAD,
        "tracked_status": "",
        "index": "",
    }
    if observed != expected:
        raise PostHDBindingError("EXACT_COMMITTED_HD_CHECKPOINT_MISMATCH")
    for path, expected_sha256 in HD_MATERIAL_SHA256.items():
        absolute = root / path
        if absolute.is_symlink() or not absolute.is_file():
            raise PostHDBindingError(f"HD_MATERIAL_PATH_INVALID__{path.name}")
        if sha256_path(absolute) != expected_sha256:
            raise PostHDBindingError(f"HD_MATERIAL_HASH_MISMATCH__{path.name}")
        if _git(root, "rev-parse", f"HEAD:{path.as_posix()}") != _git(
            root, "hash-object", path.as_posix()
        ):
            raise PostHDBindingError(f"HD_MATERIAL_NOT_COMMITTED_EXACTLY__{path.name}")
    return observed | {"material_count": len(HD_MATERIAL_SHA256)}


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


def validate_explicit_hd_rebind(
    reference: dict[str, Any], candidate: dict[str, Any]
) -> None:
    """Permit only exact HD HEAD/tree/FM identity and derived-seal changes."""

    for envelope in (reference, candidate):
        expected_seal = hashlib.sha256(canonical_bytes(envelope["manifest"])).hexdigest()
        if envelope.get("manifest_sha256") != expected_seal:
            raise PostHDBindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
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
        raise PostHDBindingError(
            "CANDIDATE_SEMANTICS_CHANGED_OUTSIDE_EXPLICIT_HD_REBIND"
        )
    selected = candidate["manifest"].get("selected_case")
    if selected != {
        "case_class": CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise PostHDBindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")


def build_post_hd_candidate(repository_root: Path) -> dict[str, Any]:
    """Build one committed-HD candidate and prove the exact permitted rebind."""

    root = repository_root.resolve()
    authenticate_committed_hd(root)
    for path, expected in (
        (HB_REFERENCE, HB_REFERENCE_SHA256),
        (GY_BINDER, GY_BINDER_SHA256),
        (GY_PRODUCER, GY_PRODUCER_SHA256),
    ):
        if sha256_path(root / path) != expected:
            raise PostHDBindingError(f"REUSED_OWNER_HASH_MISMATCH__{path.name}")
    producer = _load_module(root / GY_PRODUCER, "g77_256he_committed_gy_producer")
    candidate = producer.build_candidate(root)
    validate_explicit_hd_rebind(_load_canonical(root / HB_REFERENCE), candidate)
    return candidate


def build_post_hd_context(
    *, repository_root: Path, candidate_path: Path, operation_root: Path, transient_root: Path
) -> dict[str, Any]:
    """Delegate committed HD context construction to the existing FM owner."""

    root = repository_root.resolve()
    launcher = _load_module(root / FM_LAUNCHER, "g77_256he_existing_fm_owner")
    candidate_relative = candidate_path.resolve().relative_to(root)
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=EXPECTED_HEAD,
        repository_tree=EXPECTED_TREE,
        generation_identity=(
            "G77_256HE_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256HE_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
        identity_namespace_prefix="G77_256HE",
        operation_evidence_root=operation_root,
        transient_root=transient_root,
        candidate_source_path=candidate_relative,
    )
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate_relative
    )
    if (
        launcher.CHECKOUT_HEAD != EXPECTED_HC_HEAD
        or launcher.CHECKOUT_TREE != EXPECTED_HC_TREE
        or launcher.CLOUD_INIT_SHA256 != HD_CLOUD_INIT_SHA256
        or launcher.EXPECTED_ASSET_SHA256[launcher.SEED] != HD_SEED_SHA256
        or context["wrapper_fc_er_che_schema_hashes"][
            launcher.FRESH_OPERATION_CONTEXT_OWNER_HASH_KEY
        ]
        != FM_CONTEXT_OWNER_SHA256
    ):
        raise PostHDBindingError("HD_BOOTSTRAP_OR_CONTEXT_OWNER_BINDING_MISMATCH")
    return context


def instantiate_post_hd_binding(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Materialize repository-only HD context and DU/EB/EE evidence."""

    root = repository_root.resolve()
    output = output_root.resolve()
    candidate = build_post_hd_candidate(root)
    gy = _load_module(root / GY_BINDER, "g77_256he_reused_gy_binder")
    original_builder = gy.build_post_commit_candidate
    gy.build_post_commit_candidate = lambda _root: deepcopy(candidate)
    try:
        result = gy.instantiate_post_commit_binding(
            repository_root=root,
            output_root=output,
        )
    finally:
        gy.build_post_commit_candidate = original_builder
    candidate_path = output / (
        "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    context = build_post_hd_context(
        repository_root=root,
        candidate_path=candidate_path,
        operation_root=Path("/tmp/g77_256he/operation_state"),
        transient_root=Path("/tmp/g77_256he/transient"),
    )
    launcher = _load_module(root / FM_LAUNCHER, "g77_256he_context_serializer")
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    if (result.get("du"), result.get("eb"), result.get("ee")) != (
        "PASS",
        "PASS",
        "PASS",
    ):
        raise PostHDBindingError("CURRENT_HD_DU_EB_EE_NOT_PASS")
    return {
        **result,
        "schema_id": "G77_256HE_POST_HD_LIVE_BINDING_RESULT_V1",
        "binding_owner": "G77_256HE_EXPLICIT_HD_IDENTITY_REBIND_ADAPTER_V1",
        "reused_materialization_owner": (
            "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1"
        ),
        "reused_context_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1",
        "context_path": context_path.resolve().relative_to(root).as_posix(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "checkout_head": EXPECTED_HC_HEAD,
        "checkout_tree": EXPECTED_HC_TREE,
        "hd_bootstrap_sha256": HD_CLOUD_INIT_SHA256,
        "hd_seed_sha256": HD_SEED_SHA256,
        "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
        "explicit_permitted_rebindings": [
            "HD_HEAD",
            "HD_TREE",
            "FM_COMMITTED_FILE_SHA256",
            "DERIVED_MANIFEST_SHA256",
        ],
        "candidate_semantics_changed": False,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
    }


def write_terminal_reduction(
    *, repository_root: Path, output_path: Path
) -> dict[str, Any]:
    """Seal the bounded HE repository-only terminal reduction once."""

    root = repository_root.resolve()
    output = output_path.resolve()
    if output.exists() or output.is_symlink():
        raise PostHDBindingError("TERMINAL_REDUCTION_OUTPUT_COLLISION")
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise PostHDBindingError("TERMINAL_REDUCTION_OUTSIDE_REPOSITORY") from exc
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise PostHDBindingError("TERMINAL_REDUCTION_PARENT_INVALID")

    live_root = output.parent / "live_binding"
    candidate = live_root / (
        "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    runtime = live_root / (
        "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    )
    context = live_root / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    eb_receipt = live_root / "bindings/G77_256GY_EB_RECEIPT_V1.json"
    ee_receipt = live_root / "bindings/G77_256GY_EE_RECEIPT_V1.json"
    harness = live_root / "bindings/G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
    loaded_context = _load_canonical(context)
    loaded_candidate = _load_canonical(candidate)
    if candidate.read_bytes() != runtime.read_bytes():
        raise PostHDBindingError("CANDIDATE_RUNTIME_BYTE_IDENTITY_MISMATCH")

    counters = {
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
    }
    reduction: dict[str, Any] = {
        "schema_id": "G77_256HE_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256HE",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "entry_authentication": {
            "branch": EXPECTED_BRANCH,
            "head": EXPECTED_HEAD,
            "tree": EXPECTED_TREE,
            "subject": "G77-256HD bind FM context owner into guest checkout",
            "remote_head": EXPECTED_HEAD,
            "stable_ancestry_anchor": "5c972e9960987ab27420395b54ace693df097e7b",
            "entry_worktree_state": "CLEAN",
            "index_state": "EMPTY",
            "nested_authority_head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "nested_authority_tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "nested_authority_state": "CLEAN__DETACHED__PINNED",
        },
        "live_binding": {
            "binding_owner": "G77_256HE_EXPLICIT_HD_IDENTITY_REBIND_ADAPTER_V1",
            "binder_sha256": sha256_path(Path(__file__)),
            "reused_materialization_owner": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1",
            "reused_context_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1",
            "candidate_sha256": sha256_path(candidate),
            "candidate_inner_sha256": loaded_candidate["manifest_sha256"],
            "candidate_runtime_sha256": sha256_path(runtime),
            "candidate_runtime_byte_identity": "PASS",
            "context_file_sha256": sha256_path(context),
            "context_sha256": loaded_context["context_sha256"],
            "eb_receipt_sha256": sha256_path(eb_receipt),
            "ee_receipt_sha256": sha256_path(ee_receipt),
            "ee_harness_sha256": sha256_path(harness),
            "repository_head": EXPECTED_HEAD,
            "repository_tree": EXPECTED_TREE,
            "checkout_head": EXPECTED_HC_HEAD,
            "checkout_tree": EXPECTED_HC_TREE,
            "fm_launcher_sha256": FM_LAUNCHER_SHA256,
            "fm_context_owner_sha256": FM_CONTEXT_OWNER_SHA256,
            "hd_cloud_init_sha256": HD_CLOUD_INIT_SHA256,
            "hd_seed_sha256": HD_SEED_SHA256,
            "candidate_semantics_changed": False,
            "exact_permitted_rebindings": [
                "HD_HEAD",
                "HD_TREE",
                "FM_COMMITTED_FILE_SHA256",
                "DERIVED_MANIFEST_SHA256",
            ],
        },
        "du_eb_ee": {
            "du_status": "PASS",
            "eb_status": "PASS",
            "ee_status": "PASS",
            "current_hd_committed_binding_proof": True,
            "historical_receipts_reused_as_current_proof": False,
        },
        "hd_failure_class_reauthentication": {
            "fm_context_owner_checkout_binding_status": "VERIFIED",
            "host_checkout_guest_byte_identity_status": "VERIFIED",
            "host_checkout_guest_hash_identity_status": "VERIFIED",
            "hc_failure_class_static_block_status": "VERIFIED",
            "preauthority_missing_owner_rejection_status": "VERIFIED",
            "preauthority_wrong_hash_rejection_status": "VERIFIED",
            "preauthority_stale_checkout_rejection_status": "VERIFIED",
            "same_class_review_status": "VERIFIED",
        },
        "semantic_firewall": {
            "case": CASE_CLASS,
            "target_mutation": TARGET_MUTATION,
            "dependent_recomputation": DEPENDENT_RECOMPUTATION,
            "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
            "expected_differing_fields": ["input_identity", "record_identity"],
            "unexpected_drift_rejection": "PASS__5_OF_5",
        },
        "proof_impact": {
            "changed_owner_set": [
                "G77_256HE_EXPLICIT_HD_IDENTITY_REBIND_ADAPTER_V1"
            ],
            "dependent_proof_set": [
                "CURRENT_HD_CANDIDATE_AND_RUNTIME_IDENTITY",
                "DU_EB_EE_CURRENT_RECEIPTS",
                "FM_CONTEXT_AND_HD_BOOTSTRAP_BINDING",
                "HC_CHECKOUT_AND_CONTEXT_OWNER_IDENTITY",
                "HE_TERMINAL_EVIDENCE",
            ],
            "invalidated_proof_frontier": [
                "ABSENT_POST_COMMIT_HD_CANDIDATE_CONTEXT_AND_RECEIPTS",
                "TWO_PRECOMMIT_HD_SNAPSHOT_GATES",
            ],
            "revalidated_proof_set": (
                "HE_11__HD_APPLICABLE_6__GOVERNANCE_9__ENGINE_20__EX_12__LAYER0_1"
            ),
            "reused_unchanged_proof_set": (
                "HC_HB_HA_GZ_GY_GX_GW_GV_FY_GP_GQ_GT_GU_GN_GL_ER_P11_CHE_FK__"
                "EX_17_OF_17"
            ),
            "historical_non_applicable_count": 19,
        },
        "ex": {
            "status": "PASS",
            "reused": "17/17",
            "reconstructed": 0,
            "regressions": "12/12 PASS",
        },
        "validation": {
            "focused_he": "PASS__11_OF_11",
            "applicable_hd": "PASS__6_OF_6__TWO_SNAPSHOT_GATES_NON_APPLICABLE",
            "governance_conformance_tests": "PASS__9_OF_9",
            "governance_engine": (
                "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS"
            ),
            "layer_0_freeze": "PASS",
            "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED",
            "canonical_json_duplicate_keys_inner_seals": "PASS",
            "python_ast_single_route_semantic_firewall": "PASS",
            "git_diff_check": "PASS",
            "operational_credit_from_tests": False,
        },
        "readiness_reduction": {
            "terminal_branch": "BRANCH_A__REPOSITORY_READY",
            "post_commit_live_binding_status": "VERIFIED",
            "fm_context_owner_checkout_binding_status": "VERIFIED",
            "hd_bootstrap_binding_status": "VERIFIED",
            "du_status": "PASS",
            "eb_status": "PASS",
            "ee_status": "PASS",
            "no_known_repository_preauthorization_blocker": "VERIFIED",
            "preoperational_readiness_status": "VERIFIED",
            "next_operational_generation_eligible": "VERIFIED",
            "certified_is_authorized": False,
        },
        "reuse_impact": {
            "existing_capability_unreachable": False,
            "new_capability_created": (
                "POST_HD_COMMITTED_IDENTITY_AND_REPOSITORY_READINESS_CERTIFICATION_ONLY"
            ),
            "parallel_flow_created": False,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
        },
        "operational_counters": counters,
        "e05": {
            "before": "7/18",
            "after": "7/18",
            "credit_awarded": 0,
            "remaining": 11,
        },
        "metrics": {
            "files_changed": {"status": "VERIFIED", "value": 10},
            "focused_test_count": {"status": "VERIFIED", "value": 11},
            "revalidated_test_count": {"status": "VERIFIED", "value": 26},
            "reused_test_or_proof_count": {"status": "VERIFIED", "value": 276},
            "historical_non_applicable_count": {"status": "VERIFIED", "value": 19},
            "revalidation_case_count": {"status": "VERIFIED", "value": 59},
            "llm_execution_efficiency": {"status": "NOT_MEASURED"},
            "workers_used": {"status": "VERIFIED", "value": 1},
            "provider_capacity_start": {"status": "NOT_MEASURED"},
            "provider_capacity_end": {"status": "NOT_MEASURED"},
            "provider_capacity_consumed": {"status": "NOT_MEASURED"},
            "wall_time": {"status": "NOT_MEASURED"},
            "token_benchmark": {"status": "NOT_MEASURED"},
            "llm_cost_reduction_ratio_lcrr": {"status": "NOT_MEASURED"},
            "caor": {"status": "NOT_MEASURED"},
            "formalize_reuse_bind_verify_compliance": {"status": "VERIFIED"},
            "wrong_input_repository_capability": {"status": "VERIFIED"},
            "wrong_input_operational_capability": {"status": "NOT_PROVEN"},
        },
        "ccwim": {
            "ccwim_maturity_level": {"status": "ESTIMATED", "value": "L4_LIKE"},
            "cross_worker_state_recovery_level": {"status": "NOT_APPLICABLE"},
            "repository_derived_context_ratio": {"status": "ESTIMATED", "value": "DOMINANT"},
            "human_handoff_information_required": {"status": "VERIFIED"},
            "prompt_context_reuse_ratio": {"status": "NOT_MEASURED"},
            "previous_worker_conversation_required": {"status": "VERIFIED", "value": "NO"},
            "authenticated_repository_continuation": {"status": "VERIFIED"},
            "intra_task_cross_worker_continuation": {"status": "NOT_APPLICABLE"},
            "uncommitted_delta_recovery": {"status": "NOT_APPLICABLE"},
            "cross_worker_constitutional_drift": {"status": "VERIFIED", "value": "ZERO_DETECTED"},
            "same_worker_provider_reset_resume": {"status": "NOT_PROVEN"},
        },
        "terminal_control": {
            "auto_continuable": False,
            "human_review_required": True,
            "operation_performed": False,
            "next_frontier": (
                "SEPARATE_HUMAN_REVIEW_COMMIT_RELEASE_AND_FRESH_OPERATIONAL_GENERATION"
            ),
            "verdict": (
                "CERTIFIED__G77_256HE_POST_HD_LIVE_BINDING_AND_REPOSITORY_"
                "PREOPERATIONAL_READINESS_VERIFIED__NEXT_OPERATIONAL_GENERATION_"
                "ELIGIBLE_BUT_NOT_AUTHORIZED__E05_7_OF_18__ZERO_OPERATION__"
                "HUMAN_REVIEW_REQUIRED"
            ),
        },
    }
    envelope = {
        "schema_id": "G77_256HE_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    output.write_bytes(canonical_bytes(envelope))
    return envelope


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
