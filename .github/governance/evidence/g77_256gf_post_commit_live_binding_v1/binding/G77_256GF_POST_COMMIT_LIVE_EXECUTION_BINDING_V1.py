#!/usr/bin/env python3
"""Instantiate a current-commit candidate/context/DU/EB/EE binding without execution."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True

TEMPLATE_PATH = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
TEMPLATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
TEMPLATE_SEMANTIC_SHA256 = "df1d030fad63cc5f814af26040a39711bc268488f3a34e8fe1993574ffcfe404"
CERTIFICATION_PROVENANCE_HEAD = "7196cfe3f285ced74e0d353bac609881553d857a"
TEMPLATE_COMMIT_HEAD = "394ac2f0776a49d6ac1afabc1e21cc7fee6f7994"
BUILDER_PATH = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/builder/"
    "G77_256GD_CANDIDATE_BINDING_REISSUE_V1.py"
)
BUILDER_SHA256 = "5f0529226ec366c8c06caf19d7b7d19f89ed0751ed0c0521fe80c11ee7d906da"
LAUNCHER_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
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
    DU_PATH: "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d",
    EB_PATH: "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43",
    EE_PATH: "5e4b35b3c7e7e23e5b7209c5f56e8a70055eac9a3deef32bc288b210e80f9410",
}
PREFIX_RE = re.compile(r"^G77_256[A-Z0-9]{2,32}$")


class LiveBindingError(ValueError):
    """One deterministic fail-closed live-binding rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise LiveBindingError("GIT_CHECKPOINT_UNAVAILABLE") from exc


def load_module(path: Path, identity: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(identity, path)
    if spec is None or spec.loader is None:
        raise LiveBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repository_relative(root: Path, path: Path, field: str) -> Path:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise LiveBindingError(f"{field}_OUTSIDE_REPOSITORY") from exc
    if path.is_symlink() or resolved != root.resolve() / relative:
        raise LiveBindingError(f"{field}_PATH_INVALID")
    return relative


def semantic_projection(envelope: dict[str, Any]) -> dict[str, Any]:
    projection = deepcopy(envelope)
    manifest = projection["manifest"]
    manifest.pop("required_head")
    manifest.pop("source_tree")
    context_bindings = [
        binding
        for binding in manifest["extension_bindings"]
        if binding.get("identity")
        == "SAPIANTA_FRESH_OPERATION_CONTEXT_V1_IMPLEMENTATION"
    ]
    if len(context_bindings) != 1 or context_bindings[0].get("path") != (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
        "sapianta_fresh_operation_context_v1.py"
    ):
        raise LiveBindingError("CONTEXT_IMPLEMENTATION_BINDING_MISSING_OR_AMBIGUOUS")
    context_bindings[0]["sha256"] = "<LIVE_CONTEXT_IMPLEMENTATION_BINDING>"
    cloud_bindings = [
        binding
        for binding in manifest["extension_bindings"]
        if binding.get("identity") == "G77_256FM_CLOUD_INIT_USER_DATA"
    ]
    if len(cloud_bindings) != 1:
        raise LiveBindingError("CLOUD_INIT_BINDING_MISSING_OR_AMBIGUOUS")
    cloud_bindings[0]["sha256"] = "<LIVE_CLOUD_INIT_BINDING>"
    manifest["extension_bindings"] = [
        binding
        for binding in manifest["extension_bindings"]
        if binding.get("identity") != "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1"
    ]
    projection.pop("manifest_sha256")
    return projection


def semantic_sha256(envelope: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(semantic_projection(envelope)))


def validate_candidate_semantics(
    candidate: dict[str, Any], template: dict[str, Any]
) -> None:
    if semantic_sha256(candidate) != semantic_sha256(template):
        raise LiveBindingError("CANDIDATE_SEMANTICS_CHANGED")


def authenticate_certified_template(root: Path) -> dict[str, Any]:
    template_path = root / TEMPLATE_PATH
    builder_path = root / BUILDER_PATH
    if sha256_path(template_path) != TEMPLATE_SHA256:
        raise LiveBindingError("CERTIFIED_TEMPLATE_HASH_MISMATCH")
    if sha256_path(builder_path) != BUILDER_SHA256:
        raise LiveBindingError("CERTIFIED_BUILDER_HASH_MISMATCH")
    for path, expected in OWNER_SHA256.items():
        if sha256_path(root / path) != expected:
            raise LiveBindingError(f"EXISTING_OWNER_HASH_MISMATCH__{path.name}")
    template = json.loads(template_path.read_bytes())
    if semantic_sha256(template) != TEMPLATE_SEMANTIC_SHA256:
        raise LiveBindingError("CERTIFIED_TEMPLATE_SEMANTIC_IDENTITY_MISMATCH")
    return template


def live_harness_bytes(runtime_filename: str) -> bytes:
    return (
        "from pathlib import Path\n\n"
        'FIXTURE_CLASSIFICATION = "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL__NON_EXECUTABLE"\n'
        'RAW_ROOT = Path("/mnt/g77-evidence")\n'
        f'CONTINUATION_MANIFEST_PATH = RAW_ROOT / "{runtime_filename}"\n'
    ).encode("utf-8")


def instantiate_live_binding(
    *,
    repository_root: Path,
    output_root: Path,
    operation_evidence_root: Path,
    transient_root: Path,
    identity_namespace_prefix: str,
    require_tracked_clean: bool = True,
) -> dict[str, Any]:
    """Create one non-authority live binding for the exact current commit."""

    root = repository_root.resolve()
    output = output_root.resolve()
    operation_root = operation_evidence_root.resolve()
    transient = transient_root.resolve()
    if PREFIX_RE.fullmatch(identity_namespace_prefix) is None:
        raise LiveBindingError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    if output.exists() or output.is_symlink():
        raise LiveBindingError("LIVE_BINDING_OUTPUT_COLLISION")
    if operation_root.exists() or operation_root.is_symlink():
        raise LiveBindingError("OPERATION_EVIDENCE_ROOT_NOT_FRESH")
    if transient.exists() or transient.is_symlink():
        raise LiveBindingError("TRANSIENT_ROOT_NOT_FRESH")
    output_relative = repository_relative(root, output, "LIVE_BINDING_OUTPUT")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise LiveBindingError("LIVE_BINDING_PARENT_INVALID")
    if operation_root.parent.is_symlink() or not operation_root.parent.is_dir():
        raise LiveBindingError("OPERATION_EVIDENCE_PARENT_INVALID")
    if transient.parent.is_symlink() or not transient.parent.is_dir():
        raise LiveBindingError("TRANSIENT_PARENT_INVALID")

    head = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if require_tracked_clean and git(
        root, "status", "--porcelain", "--untracked-files=no"
    ):
        raise LiveBindingError("TRACKED_WORKTREE_NOT_CLEAN")

    template = authenticate_certified_template(root)
    builder = load_module(root / BUILDER_PATH, "g77_256gf_certified_candidate_builder")
    live_candidate = builder.build(root)
    validate_candidate_semantics(live_candidate, template)
    if live_candidate["manifest"]["required_head"] != head:
        raise LiveBindingError("LIVE_CANDIDATE_HEAD_MISMATCH")
    if live_candidate["manifest"]["source_tree"] != tree:
        raise LiveBindingError("LIVE_CANDIDATE_TREE_MISMATCH")

    candidate_name = f"{identity_namespace_prefix}_CONTINUATION_MANIFEST_V1.json"
    candidate_path = output / "candidate" / candidate_name
    runtime_root = output / "ee_runtime_projection"
    runtime_path = runtime_root / candidate_name
    eb_receipt_path = output / "bindings" / "CANDIDATE_BOUND_EB_RECEIPT_V1.json"
    ee_receipt_path = output / "bindings" / "RUNTIME_CONSUMER_EE_RECEIPT_V1.json"
    harness_path = output / "bindings" / "LIVE_EE_PATH_PROJECTION_V1.py"
    context_path = output / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
    for parent in {candidate_path.parent, runtime_root, eb_receipt_path.parent}:
        parent.mkdir(parents=True, exist_ok=False)
    candidate_bytes = canonical_bytes(live_candidate)
    candidate_path.write_bytes(candidate_bytes)
    runtime_path.write_bytes(candidate_bytes)
    harness_path.write_bytes(live_harness_bytes(candidate_name))

    candidate_relative = repository_relative(root, candidate_path, "LIVE_CANDIDATE")
    launcher = load_module(root / LAUNCHER_PATH, "g77_256gf_existing_fm_launcher")
    generation_identity = (
        f"{identity_namespace_prefix}_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    operation_identity = (
        f"{identity_namespace_prefix}_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001"
    )
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=head,
        repository_tree=tree,
        generation_identity=generation_identity,
        operation_identity=operation_identity,
        identity_namespace_prefix=identity_namespace_prefix,
        operation_evidence_root=operation_root,
        transient_root=transient,
        candidate_source_path=candidate_relative,
    )
    context_path.write_bytes(launcher.fresh_context.canonical_bytes(context))
    if launcher.fresh_context.load_context(
        context_path, repository_root=root
    ) != context:
        raise LiveBindingError("CONTEXT_CANONICAL_RELOAD_MISMATCH")
    launcher.validate_immutable_context_bindings(
        root, context, candidate_source_path=candidate_relative
    )

    du = load_module(root / DU_PATH, "g77_256gf_existing_du")
    eb = load_module(root / EB_PATH, "g77_256gf_existing_eb")
    ee = load_module(root / EE_PATH, "g77_256gf_existing_ee")
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
        raise LiveBindingError("DU_NOT_PASS")
    if eb_result.get("overall_result") != "PASS":
        raise LiveBindingError("EB_NOT_PASS")
    if ee_result.get("pre_materialization_runtime_path_binding_result") != "PASS":
        raise LiveBindingError("EE_NOT_PASS")

    return {
        "schema_id": "G77_256GF_LIVE_EXECUTION_BINDING_RESULT_V1",
        "artifact_class": "LIVE_BINDING__NON_AUTHORITY__NON_OPERATIONAL",
        "certified_template_path": TEMPLATE_PATH.as_posix(),
        "certified_template_sha256": TEMPLATE_SHA256,
        "certified_template_semantic_sha256": TEMPLATE_SEMANTIC_SHA256,
        "certification_provenance_head": CERTIFICATION_PROVENANCE_HEAD,
        "template_commit_head": TEMPLATE_COMMIT_HEAD,
        "live_execution_repository_head": head,
        "live_execution_repository_tree": tree,
        "live_binding_output_root": output_relative.as_posix(),
        "candidate_path": candidate_relative.as_posix(),
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "context_path": repository_relative(root, context_path, "CONTEXT").as_posix(),
        "context_file_sha256": sha256_path(context_path),
        "context_sha256": context["context_sha256"],
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
        "candidate_semantics_changed": False,
        "no_future_commit_hash_self_reference": True,
        "human_operational_authorization_count": 0,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--operation-evidence-root", required=True, type=Path)
    parser.add_argument("--transient-root", required=True, type=Path)
    parser.add_argument("--identity-namespace-prefix", required=True)
    parser.add_argument("--allow-dirty-tracked-worktree", action="store_true")
    arguments = parser.parse_args()
    try:
        result = instantiate_live_binding(
            repository_root=arguments.repo_root,
            output_root=arguments.output_root,
            operation_evidence_root=arguments.operation_evidence_root,
            transient_root=arguments.transient_root,
            identity_namespace_prefix=arguments.identity_namespace_prefix,
            require_tracked_clean=not arguments.allow_dirty_tracked_worktree,
        )
    except (LiveBindingError, OSError, ValueError) as exc:
        print(canonical_bytes({
            "schema_id": "G77_256GF_LIVE_EXECUTION_BINDING_FAILURE_V1",
            "overall_result": "FAIL_CLOSED",
            "failure": str(exc),
        }).decode(), end="")
        return 1
    print(canonical_bytes(result).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
