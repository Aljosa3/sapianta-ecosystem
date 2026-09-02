#!/usr/bin/env python3
"""Bind the certified WRONG_INPUT semantics to one exact post-commit checkpoint."""

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
BINDING_CLASSIFICATION = (
    "NEW_VECTOR_SPECIFIC_BINDING_OWNER_REQUIRED__"
    "REUSES_GF_REPOSITORY_IDENTITY_MECHANICS_AND_EXISTING_DU_EB_EE"
)
CANDIDATE_IDENTITY = "G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1"
TEMPLATE_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/candidate/"
    "G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1.json"
)
TEMPLATE_SHA256 = "26fa2f3a4ea4c4683c2ccde4288a39760b89c8d0329eca01502425941c03b041"
TEMPLATE_SEMANTIC_SHA256 = (
    "4cd84d3dd296612fafd209bd37abcb6bc51f361d4e3e05238d9cafd72d10c3de"
)
PRODUCER_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
PRODUCER_SHA256 = "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
SPECIFICATION_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/"
    "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1.json"
)
REDUCER_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/reducer/"
    "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
)
BINDING_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/"
    "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
)
GF_PATH = Path(
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)
DU_PATH = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
EB_PATH = Path(
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EE_PATH = Path(
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
OWNER_SHA256 = {
    GF_PATH: "7c70c02f074b3ba34392cfc4f480b28527c5600dc19606e87adc86423c6c138a",
    DU_PATH: "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    EB_PATH: "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    EE_PATH: "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
}
POST_COMMIT_TRACKED_PATHS = (
    SPECIFICATION_PATH,
    TEMPLATE_PATH,
    PRODUCER_PATH,
    REDUCER_PATH,
    BINDING_PATH,
)


class WrongInputBindingError(ValueError):
    """One deterministic fail-closed post-commit binding rejection."""


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
        raise WrongInputBindingError("GIT_CHECKPOINT_UNAVAILABLE") from exc


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongInputBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _repository_relative(root: Path, path: Path, field: str) -> Path:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise WrongInputBindingError(f"{field}_OUTSIDE_REPOSITORY") from exc
    if path.is_symlink() or resolved != root.resolve() / relative:
        raise WrongInputBindingError(f"{field}_PATH_INVALID")
    return relative


def semantic_projection(envelope: dict[str, Any]) -> dict[str, Any]:
    projection = deepcopy(envelope)
    manifest = projection.get("manifest")
    if not isinstance(manifest, dict):
        raise WrongInputBindingError("CANDIDATE_MANIFEST_INVALID")
    try:
        manifest.pop("required_head")
        manifest.pop("source_tree")
        projection.pop("manifest_sha256")
    except KeyError as exc:
        raise WrongInputBindingError("CANDIDATE_BINDING_FIELDS_MISSING") from exc
    return projection


def semantic_sha256(envelope: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(semantic_projection(envelope)))


def validate_candidate_semantics(
    candidate: dict[str, Any], template: dict[str, Any]
) -> None:
    if semantic_sha256(candidate) != semantic_sha256(template):
        raise WrongInputBindingError("CANDIDATE_SEMANTICS_CHANGED")


def _require_post_commit_files(root: Path) -> None:
    for path in POST_COMMIT_TRACKED_PATHS:
        relative = path.as_posix()
        try:
            committed_blob = _git(root, "rev-parse", f"HEAD:{relative}")
            worktree_blob = _git(root, "hash-object", relative)
        except WrongInputBindingError as exc:
            raise WrongInputBindingError(
                f"POST_COMMIT_LIVE_BINDING_REQUIRED__{path.name}"
            ) from exc
        if committed_blob != worktree_blob:
            raise WrongInputBindingError(f"POST_COMMIT_FILE_DRIFT__{path.name}")


def authenticate_template(root: Path) -> dict[str, Any]:
    if sha256_path(root / TEMPLATE_PATH) != TEMPLATE_SHA256:
        raise WrongInputBindingError("CERTIFIED_TEMPLATE_HASH_MISMATCH")
    if sha256_path(root / PRODUCER_PATH) != PRODUCER_SHA256:
        raise WrongInputBindingError("CERTIFIED_PRODUCER_HASH_MISMATCH")
    for path, expected in OWNER_SHA256.items():
        if sha256_path(root / path) != expected:
            raise WrongInputBindingError(f"EXISTING_OWNER_HASH_MISMATCH__{path.name}")
    raw = (root / TEMPLATE_PATH).read_bytes()
    template = json.loads(raw)
    if raw != canonical_bytes(template):
        raise WrongInputBindingError("CERTIFIED_TEMPLATE_NOT_CANONICAL")
    if semantic_sha256(template) != TEMPLATE_SEMANTIC_SHA256:
        raise WrongInputBindingError("CERTIFIED_TEMPLATE_SEMANTIC_IDENTITY_MISMATCH")
    selected = template["manifest"].get("selected_case")
    if selected != {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
        "case_id": "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001",
    }:
        raise WrongInputBindingError("CERTIFIED_TEMPLATE_VECTOR_IDENTITY_MISMATCH")
    return template


def build_post_commit_candidate(repository_root: Path) -> dict[str, Any]:
    """Rebind the fixed GY semantics to the exact current committed HEAD/tree."""

    root = repository_root.resolve()
    _require_post_commit_files(root)
    template = authenticate_template(root)
    producer = _load_module(root / PRODUCER_PATH, "g77_256gy_certified_producer")
    candidate = producer.build_candidate(root)
    validate_candidate_semantics(candidate, template)
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    if candidate["manifest"]["required_head"] != head:
        raise WrongInputBindingError("LIVE_CANDIDATE_HEAD_MISMATCH")
    if candidate["manifest"]["source_tree"] != tree:
        raise WrongInputBindingError("LIVE_CANDIDATE_TREE_MISMATCH")
    du = _load_module(root / DU_PATH, "g77_256gy_existing_du")
    if set(du.validate_envelope(candidate, root, expected_head=head).values()) != {"PASS"}:
        raise WrongInputBindingError("DU_NOT_PASS")
    return candidate


def _harness_bytes(runtime_filename: str) -> bytes:
    return (
        "from pathlib import Path\n\n"
        'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
        'RAW_ROOT = Path("/mnt/g77-evidence")\n'
        f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{runtime_filename}"\n'
    ).encode("utf-8")


def instantiate_post_commit_binding(
    *, repository_root: Path, output_root: Path
) -> dict[str, Any]:
    """Materialize DU/EB/EE receipts only; never create authority or execute P11."""

    root = repository_root.resolve()
    output = output_root.resolve()
    if output.exists() or output.is_symlink():
        raise WrongInputBindingError("POST_COMMIT_BINDING_OUTPUT_COLLISION")
    relative_output = _repository_relative(root, output, "POST_COMMIT_BINDING_OUTPUT")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise WrongInputBindingError("POST_COMMIT_BINDING_PARENT_INVALID")
    candidate = build_post_commit_candidate(root)
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    candidate_name = "G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_root = output / "runtime_projection"
    runtime_path = runtime_root / candidate_name
    bindings_root = output / "bindings"
    harness_path = bindings_root / "G77_256GY_EE_PATH_PROJECTION_FIXTURE_V1.py"
    eb_receipt_path = bindings_root / "G77_256GY_EB_RECEIPT_V1.json"
    ee_receipt_path = bindings_root / "G77_256GY_EE_RECEIPT_V1.json"
    for parent in (candidate_path.parent, runtime_root, bindings_root):
        parent.mkdir(parents=True, exist_ok=True)
    candidate_bytes = canonical_bytes(candidate)
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(_harness_bytes(candidate_name))
    du = _load_module(root / DU_PATH, "g77_256gy_binding_du")
    eb = _load_module(root / EB_PATH, "g77_256gy_binding_eb")
    ee = _load_module(root / EE_PATH, "g77_256gy_binding_ee")
    du_result = du.validate_file(candidate_path, root, expected_head=head)
    eb_receipt = eb.validate_candidate(
        root, candidate_path, required_head=head, required_tree=tree
    )
    eb_receipt_path.write_bytes(eb.canonical_bytes(eb_receipt))
    eb_result = eb.verify_receipt_file(root, eb_receipt_path)
    ee_receipt = ee.validate_binding(
        root,
        candidate_path,
        eb_receipt_path,
        harness_path,
        runtime_root,
        "/mnt/g77-evidence",
        required_head=head,
        required_tree=tree,
    )
    ee_receipt_path.write_bytes(ee.canonical_bytes(ee_receipt))
    ee_result = ee.verify_receipt_file(root, ee_receipt_path)
    if set(du_result.values()) != {"PASS"}:
        raise WrongInputBindingError("DU_NOT_PASS")
    if eb_result.get("overall_result") != "PASS":
        raise WrongInputBindingError("EB_NOT_PASS")
    if ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise WrongInputBindingError("EE_NOT_PASS")
    return {
        "schema_id": "G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_RESULT_V1",
        "artifact_class": "POST_COMMIT_BINDING__NON_AUTHORITY__NON_OPERATIONAL",
        "binding_classification": BINDING_CLASSIFICATION,
        "candidate_identity": CANDIDATE_IDENTITY,
        "repository_head": head,
        "repository_tree": tree,
        "output_root": relative_output.as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "candidate_semantics_changed": False,
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
        "human_operational_authority_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "production_route_delta": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }


if __name__ == "__main__":
    raise SystemExit("post-commit repository binding only; no operational CLI entry point")
