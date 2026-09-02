#!/usr/bin/env python3
"""Bind the committed HA WRONG_INPUT capability without operation or semantics drift."""

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
EXPECTED_HEAD = "f7d732edb822163d9fb8da2578ac7e79d3ab5398"
EXPECTED_TREE = "53b1ab0c7de92c7355234a3d99d455a113db74c4"
EXPECTED_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
EXPECTED_GZ_HEAD = "20a435d36f84e99c90b872f892061a1dce86d151"
EXPECTED_GY_HEAD = "2b6f904ca93c980f6c6078333cdf61c49fa54e87"
EXPECTED_GY_TREE = "09e68a5bb4e6c7fda4aeab73d0fccf2f24d3ff52"
CASE_CLASS = "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1

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
GZ_CANDIDATE = Path(
    ".github/governance/evidence/g77_256gz_wrong_input_post_commit_readiness_v1/"
    "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
)
GZ_CANDIDATE_SHA256 = "ab94e3f000a43da75fe7f4791bf38a13b0babed7673f4e21ff248c27df353ee9"
DU_VALIDATOR = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_VALIDATOR_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4fe6147608d27dc233ff512304d"

HA_MATERIAL_SHA256 = {
    Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"): "71de43ff66826736b26bc44fb9f514ba3c7efb1ae6a98a24589d1732cd7cfef3",
    Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py"): "45b97e99122146ec3aa95f45fe5ac71381ca1a11e83b7355438b988608f52fca",
    Path(".github/governance/evidence/g77_256gd_fresh_operation_context_v1/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json"): "21eeaf51f079c1410187f046cb52f66643527b03c65b9e3690fcf0fd582a1915",
    Path(".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"): "7f92bcd5fa3c8530e8e8e7c0807d679c5693ce4cbe71cf435a8f4e0b87fcb00c",
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/G77_256HA_NEXT_DEVELOPMENT_SPECIFICATION_V1.json"): "b07ff82a61443b5330c941a79cb844e9a19c543779fd5ab624351dc524c7d600",
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/G77_256HA_SPCE_TERMINAL_REDUCTION_V1.json"): "94426a648191017bdf1be32592b6fb0d7e3c3525ca625c5e39616322ca5b40bb",
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"): "fb83002e5567c2a109bfb977270865e6fb085e39f551d1068d03537a3b1d6230",
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/static/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"): "e78d6de0fb98628d543824cf9feb203a1068c0bc9e2bff2703b1cb1a6d9a4dde",
    Path(".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/tests/test_g77_256ha_wrong_input_route_binding_v1.py"): "061a492b1e94b980954fa81891d72331ca68823bfabfb6ab961ec73cd975d1e7",
    Path("docs/governance/G77_256HA_WRONG_INPUT_OPERATION_CONTEXT_GUEST_ADAPTER_AND_GN_PRESENTATION_BINDING_V1.md"): "ed906b36aca72bde7121405628ac1aa5c31a773d2726cb975fa1acadfd8f0169",
}

OLD_GN_SHA256 = "0f5f91bdbf8a70ecd4d6fddce71be05cfd4a4a26b60a418212c8d97f6e42629a"
NEW_GN_SHA256 = HA_MATERIAL_SHA256[next(path for path in HA_MATERIAL_SHA256 if "g77_256gn_" in str(path))]
OLD_FM_SHA256 = "8cdc99f9fa909e67d396232889791befe3304a3c488d9a4f9802e9bf9b89f444"
NEW_FM_SHA256 = HA_MATERIAL_SHA256[next(path for path in HA_MATERIAL_SHA256 if path.name == "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py")]


class PostHABindingError(ValueError):
    """Deterministic fail-closed post-HA binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise PostHABindingError("GIT_IDENTITY_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise PostHABindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise PostHABindingError(f"CANONICAL_JSON_INVALID__{path.name}")
    return value


def authenticate_committed_ha(repository_root: Path) -> dict[str, Any]:
    """Authenticate HA material against both bytes and committed Git blobs."""

    root = repository_root.resolve()
    observed = {
        "head": _git(root, "rev-parse", "HEAD"),
        "tree": _git(root, "rev-parse", "HEAD^{tree}"),
        "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
        "remote_tracking_head": _git(root, "rev-parse", f"origin/{EXPECTED_BRANCH}"),
    }
    expected = {
        "head": EXPECTED_HEAD,
        "tree": EXPECTED_TREE,
        "branch": EXPECTED_BRANCH,
        "remote_tracking_head": EXPECTED_HEAD,
    }
    if observed != expected:
        raise PostHABindingError("EXACT_COMMITTED_HA_CHECKPOINT_MISMATCH")
    for path, expected_sha256 in HA_MATERIAL_SHA256.items():
        absolute = root / path
        if absolute.is_symlink() or not absolute.is_file():
            raise PostHABindingError(f"HA_MATERIAL_PATH_INVALID__{path.name}")
        if sha256_path(absolute) != expected_sha256:
            raise PostHABindingError(f"HA_MATERIAL_HASH_MISMATCH__{path.name}")
        committed_blob = _git(root, "rev-parse", f"HEAD:{path.as_posix()}")
        worktree_blob = _git(root, "hash-object", path.as_posix())
        if committed_blob != worktree_blob:
            raise PostHABindingError(f"HA_MATERIAL_NOT_COMMITTED_EXACTLY__{path.name}")
    return observed | {"material_count": len(HA_MATERIAL_SHA256)}


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


def validate_explicit_ha_owner_rebind(
    reference: dict[str, Any], candidate: dict[str, Any]
) -> None:
    """Permit only exact HA HEAD/tree and committed GN/FM identity rebindings."""

    for envelope in (reference, candidate):
        expected_seal = hashlib.sha256(canonical_bytes(envelope["manifest"])).hexdigest()
        if envelope.get("manifest_sha256") != expected_seal:
            raise PostHABindingError("CANDIDATE_MANIFEST_SEAL_INVALID")
    expected = {
        ("manifest", "required_head"): (EXPECTED_GY_HEAD, EXPECTED_HEAD),
        ("manifest", "source_tree"): (EXPECTED_GY_TREE, EXPECTED_TREE),
        ("manifest", "extension_bindings", 4, "sha256"): (OLD_GN_SHA256, NEW_GN_SHA256),
        ("manifest", "extension_bindings", 5, "sha256"): (OLD_FM_SHA256, NEW_FM_SHA256),
        ("manifest_sha256",): (reference["manifest_sha256"], candidate["manifest_sha256"]),
    }
    if _leaf_differences(reference, candidate) != expected:
        raise PostHABindingError("CANDIDATE_SEMANTICS_CHANGED_OUTSIDE_EXPLICIT_HA_REBIND")
    selected = candidate["manifest"].get("selected_case")
    if selected != {
        "case_class": CASE_CLASS,
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise PostHABindingError("WRONG_INPUT_VECTOR_IDENTITY_MISMATCH")
    required_observations = {
        "WRONG_INPUT_INPUT_IDENTITY_MUTATION_ONLY",
        "RECORD_IDENTITY_DEPENDENT_RECOMPUTATION_ONLY",
        "SEMANTIC_MUTATION_COUNT__ONE",
        "WRONG_ATTEMPT_SEMANTICS_PRESERVED",
        "CANDIDATE_SEMANTICS_CHANGED_GUARD_REQUIRED",
    }
    if not required_observations.issubset(candidate["manifest"].get("observations", [])):
        raise PostHABindingError("WRONG_INPUT_SEMANTIC_FIREWALL_INCOMPLETE")


def build_post_ha_candidate(repository_root: Path) -> dict[str, Any]:
    """Build one current candidate and prove the exact permitted HA rebind."""

    root = repository_root.resolve()
    authenticate_committed_ha(root)
    if sha256_path(root / GY_PRODUCER) != GY_PRODUCER_SHA256:
        raise PostHABindingError("GY_PRODUCER_HASH_MISMATCH")
    if sha256_path(root / GY_BINDER) != GY_BINDER_SHA256:
        raise PostHABindingError("GY_BINDER_HASH_MISMATCH")
    if sha256_path(root / GZ_CANDIDATE) != GZ_CANDIDATE_SHA256:
        raise PostHABindingError("GZ_REFERENCE_CANDIDATE_HASH_MISMATCH")
    producer = _load_module(root / GY_PRODUCER, "g77_256hb_committed_gy_producer")
    candidate = producer.build_candidate(root)
    reference = _load_canonical(root / GZ_CANDIDATE)
    validate_explicit_ha_owner_rebind(reference, candidate)
    du = _load_module(root / DU_VALIDATOR, "g77_256hb_existing_du")
    if set(du.validate_envelope(candidate, root, expected_head=EXPECTED_HEAD).values()) != {"PASS"}:
        raise PostHABindingError("DU_NOT_PASS")
    return candidate


def instantiate_post_ha_binding(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Delegate DU/EB/EE materialization to the authenticated GY binder."""

    root = repository_root.resolve()
    candidate = build_post_ha_candidate(root)
    gy = _load_module(root / GY_BINDER, "g77_256hb_reused_gy_binder")
    original_builder = gy.build_post_commit_candidate
    gy.build_post_commit_candidate = lambda _root: deepcopy(candidate)
    try:
        result = gy.instantiate_post_commit_binding(
            repository_root=root,
            output_root=output_root,
        )
    finally:
        gy.build_post_commit_candidate = original_builder
    if (result.get("du"), result.get("eb"), result.get("ee")) != ("PASS", "PASS", "PASS"):
        raise PostHABindingError("CURRENT_HA_DU_EB_EE_NOT_PASS")
    return {
        **result,
        "schema_id": "G77_256HB_POST_HA_LIVE_BINDING_RESULT_V1",
        "binding_owner": "G77_256HB_EXPLICIT_HA_OWNER_REBIND_ADAPTER_V1",
        "reused_materialization_owner": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1",
        "explicit_permitted_rebindings": [
            "HA_HEAD",
            "HA_TREE",
            "GN_COMMITTED_FILE_SHA256",
            "FM_COMMITTED_FILE_SHA256",
            "DERIVED_MANIFEST_SHA256",
        ],
        "candidate_semantics_changed": False,
    }


if __name__ == "__main__":
    raise SystemExit("repository-only binding owner; no operational CLI entry point")
