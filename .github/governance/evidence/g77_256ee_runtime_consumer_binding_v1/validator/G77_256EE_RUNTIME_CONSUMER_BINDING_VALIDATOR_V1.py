#!/usr/bin/env python3
"""Bind one EB-validated Canonical V1 candidate to its exact runtime path."""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
from types import ModuleType
from typing import Any, Callable

import jsonschema


ENVELOPE_SCHEMA_ID = "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_ENVELOPE_V1"
RECEIPT_SCHEMA_ID = "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_V1"
RECEIPT_VERSION = "1.0.0"
GENERATION_IDENTITY = "G77_256EE_REPOSITORY_ONLY_RUNTIME_CONSUMER_BINDING_HARDENING_V1"
VALIDATION_MODE = "PRE_MATERIALIZATION_RUNTIME_CONSUMER_BINDING"
VALIDATION_PROFILE = "DU_EB_CANONICAL_V1_RUNTIME_CONSUMER_BINDING_V1"
VALIDATOR_IDENTITY = "G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1"
VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V1.py"
)
SCHEMA_IDENTITY = "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1"
SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "G77_256EE_RUNTIME_CONSUMER_BINDING_RECEIPT_SCHEMA_V1.json"
)
EB_VALIDATOR_IDENTITY = "G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1"
EB_VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EB_VALIDATOR_SHA256 = "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43"
DU_VALIDATOR_IDENTITY = "G77_256DU_PRE_MATERIALIZATION_CONSUMER_VALIDATOR_V1"
DU_VALIDATOR_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_VALIDATOR_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
DU_SCHEMA_IDENTITY = "SAPIANTA_SPCE_CONTINUATION_MANIFEST_SCHEMA_V1"
DU_SCHEMA_RELATIVE_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
)
DU_SCHEMA_SHA256 = "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}$")
PROHIBITED_ACTIONS = [
    "AUTOMATIC_COPY_OR_RENAME_AFTER_BINDING",
    "AUTOMATIC_REPAIR",
    "COMMISSIONING",
    "E05_EXECUTION",
    "EXECUTION_REPLAY",
    "HUMAN_OPERATIONAL_ACT_CREATION",
    "MATERIALIZATION",
    "P11_ENTRY",
    "P12_ENTRY",
    "PRODUCTION_ROUTE",
    "RUNTIME_PATH_FALLBACK",
    "SYMLINK_SUBSTITUTION",
    "VM_BOOT",
    "VM_CREATION",
    "WRONG_CALLER_RETRY",
]


class BindingError(ValueError):
    """One deterministic fail-closed pre-materialization rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fail(code: str, message: str) -> None:
    raise BindingError(code, message)


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        _fail("IMPLEMENTATION_IMPORT_FAILED", f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_implementations(repository_root: Path) -> tuple[ModuleType, ModuleType]:
    eb_path = repository_root / EB_VALIDATOR_RELATIVE_PATH
    du_path = repository_root / DU_VALIDATOR_RELATIVE_PATH
    du_schema_path = repository_root / DU_SCHEMA_RELATIVE_PATH
    if sha256_path(eb_path) != EB_VALIDATOR_SHA256:
        _fail("EB_VALIDATOR_HASH_MISMATCH", "committed EB validator bytes differ")
    if sha256_path(du_path) != DU_VALIDATOR_SHA256:
        _fail("DU_VALIDATOR_HASH_MISMATCH", "committed DU validator bytes differ")
    if sha256_path(du_schema_path) != DU_SCHEMA_SHA256:
        _fail("DU_SCHEMA_HASH_MISMATCH", "committed DU schema bytes differ")
    return (
        _load_module(eb_path, "g77_256eb_validator_for_ee"),
        _load_module(du_path, "g77_256du_validator_for_ee"),
    )


def _git(repository_root: Path, *arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *arguments], cwd=repository_root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise BindingError("GIT_BINDING_UNAVAILABLE", "Git identity unavailable") from exc


def _authenticate_git(
    repository_root: Path, required_head: str, required_tree: str
) -> None:
    if GIT_OBJECT_RE.fullmatch(required_head or "") is None:
        _fail("REQUIRED_HEAD_FORMAT_INVALID", "required HEAD is not a Git identity")
    if GIT_OBJECT_RE.fullmatch(required_tree or "") is None:
        _fail("REQUIRED_TREE_FORMAT_INVALID", "required tree is not a Git identity")
    if _git(repository_root, "rev-parse", "HEAD") != required_head:
        _fail("REQUIRED_HEAD_MISMATCH", "actual HEAD differs from required HEAD")
    if _git(repository_root, "rev-parse", "HEAD^{tree}") != required_tree:
        _fail("REQUIRED_TREE_MISMATCH", "actual tree differs from required tree")
    if _git(repository_root, "rev-parse", f"{required_head}^{{tree}}") != required_tree:
        _fail("REQUIRED_TREE_MISMATCH", "required tree does not belong to required HEAD")


def _relative(repository_root: Path, path: Path, field: str) -> tuple[str, Path]:
    root = repository_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError:
        _fail("PATH_OUTSIDE_REPOSITORY", f"{field} escapes repository")
    return relative, resolved


def _repo_file(repository_root: Path, path: Path, field: str) -> tuple[str, Path]:
    relative, resolved = _relative(repository_root, path, field)
    if not resolved.is_file():
        _fail("BOUND_FILE_ABSENT", f"{field} is absent")
    if path.is_symlink() or resolved.is_symlink():
        _fail("SYMLINK_SUBSTITUTION_REJECTED", f"{field} cannot be a symlink")
    return relative, resolved


def _repo_dir(repository_root: Path, path: Path, field: str) -> tuple[str, Path]:
    relative, resolved = _relative(repository_root, path, field)
    if not resolved.is_dir():
        _fail("BOUND_DIRECTORY_ABSENT", f"{field} is absent")
    if path.is_symlink() or resolved.is_symlink():
        _fail("SYMLINK_SUBSTITUTION_REJECTED", f"{field} cannot be a symlink")
    return relative, resolved


def _load_json_canonical(path: Path, code: str) -> tuple[bytes, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError(code, f"{path} is not UTF-8 JSON") from exc
    if raw != canonical_bytes(value):
        _fail(code, f"{path} is not canonical sorted compact JSON plus LF")
    return raw, value


def _manifest_binding(
    path: Path, du: ModuleType, *, expected_head: str, runtime: bool
) -> tuple[bytes, dict[str, Any], str]:
    code = (
        "RUNTIME_CANONICAL_SERIALIZATION_INVALID"
        if runtime
        else "CANDIDATE_CANONICAL_SERIALIZATION_INVALID"
    )
    raw, envelope = _load_json_canonical(path, code)
    if not isinstance(envelope, dict) or not isinstance(envelope.get("manifest"), dict):
        _fail(code, "manifest envelope structure is absent")
    inner = sha256_bytes(canonical_bytes(envelope["manifest"]))
    if envelope.get("manifest_sha256") != inner:
        _fail("MANIFEST_INNER_SHA256_MISMATCH", "manifest inner identity differs")
    if envelope["manifest"].get("required_head") != expected_head:
        _fail("CANDIDATE_REQUIRED_HEAD_MISMATCH", "manifest required HEAD differs")
    return raw, envelope, inner


def _eval_harness_path(node: ast.AST, values: dict[str, PurePosixPath]) -> PurePosixPath:
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Path"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        return PurePosixPath(node.args[0].value)
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Div)
        and isinstance(node.right, ast.Constant)
        and isinstance(node.right.value, str)
    ):
        return _eval_harness_path(node.left, values) / node.right.value
    _fail("HARNESS_PATH_DECLARATION_UNSUPPORTED", "harness path declaration is not static")


def extract_harness_paths(harness_path: Path) -> tuple[PurePosixPath, PurePosixPath]:
    try:
        tree = ast.parse(harness_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise BindingError("HARNESS_PARSE_FAILED", "harness is not parseable Python") from exc
    values: dict[str, PurePosixPath] = {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id in {"RAW_ROOT", "CONTINUATION_MANIFEST_PATH"}:
            values[target.id] = _eval_harness_path(statement.value, values)
    if set(values) != {"RAW_ROOT", "CONTINUATION_MANIFEST_PATH"}:
        _fail("HARNESS_EXPECTED_PATH_DECLARATION_MISSING", "required harness declarations absent")
    runtime_root = values["RAW_ROOT"]
    expected = values["CONTINUATION_MANIFEST_PATH"]
    if not runtime_root.is_absolute() or not expected.is_absolute():
        _fail("HARNESS_EXPECTED_PATH_INVALID", "harness paths must be absolute")
    try:
        relative = expected.relative_to(runtime_root)
    except ValueError:
        _fail("HARNESS_EXPECTED_PATH_INVALID", "expected path escapes harness runtime root")
    if str(relative) in {"", "."} or ".." in relative.parts:
        _fail("HARNESS_EXPECTED_PATH_INVALID", "expected runtime filename is invalid")
    return runtime_root, expected


def _runtime_actual(
    repository_root: Path,
    export_root: Path,
    relative_runtime: PurePosixPath,
) -> tuple[str, Path]:
    candidate = export_root.joinpath(*relative_runtime.parts)
    if not candidate.exists() and not candidate.is_symlink():
        alternate_files = [item for item in export_root.rglob("*") if item.is_file()]
        if alternate_files:
            _fail(
                "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
                "runtime export contains input only at an alternate path",
            )
        _fail("EXPECTED_RUNTIME_PATH_ABSENT", "harness-expected runtime input is absent")
    if candidate.is_symlink():
        _fail("SYMLINK_SUBSTITUTION_REJECTED", "runtime input cannot be a symlink")
    relative, resolved = _relative(repository_root, candidate, "runtime_consumer.actual_path")
    mode = resolved.lstat().st_mode
    if not stat.S_ISREG(mode):
        _fail("RUNTIME_FILE_KIND_INVALID", "runtime input must be a regular file")
    return relative, resolved


def _implementation_bindings(repository_root: Path) -> list[dict[str, str]]:
    values = [
        (VALIDATOR_IDENTITY, VALIDATOR_RELATIVE_PATH),
        (SCHEMA_IDENTITY, SCHEMA_RELATIVE_PATH),
        (EB_VALIDATOR_IDENTITY, EB_VALIDATOR_RELATIVE_PATH),
        (DU_VALIDATOR_IDENTITY, DU_VALIDATOR_RELATIVE_PATH),
        (DU_SCHEMA_IDENTITY, DU_SCHEMA_RELATIVE_PATH),
    ]
    return [
        {
            "identity": identity,
            "path": path,
            "file_sha256": sha256_path(repository_root / path),
        }
        for identity, path in values
    ]


def _schema(repository_root: Path) -> dict[str, Any]:
    return json.loads((repository_root / SCHEMA_RELATIVE_PATH).read_bytes())


def validate_binding(
    repository_root: Path,
    candidate_path: Path,
    eb_receipt_path: Path,
    harness_path: Path,
    runtime_export_root: Path,
    guest_runtime_root: str,
    *,
    required_head: str,
    required_tree: str,
) -> dict[str, Any]:
    """Validate and return one self-authenticating runtime-consumer receipt."""
    _authenticate_git(repository_root, required_head, required_tree)
    eb, du = _load_implementations(repository_root)
    candidate_relative, candidate = _repo_file(
        repository_root, candidate_path, "validated_candidate.path"
    )
    eb_relative, eb_receipt = _repo_file(
        repository_root, eb_receipt_path, "candidate_bound_eb_receipt.path"
    )
    harness_relative, harness = _repo_file(
        repository_root, harness_path, "harness_binding.path"
    )
    export_relative, export_root = _repo_dir(
        repository_root, runtime_export_root, "runtime_consumer.repository_export_root"
    )

    try:
        eb_result = eb.verify_receipt_file(repository_root, eb_receipt)
    except Exception as exc:
        code = getattr(exc, "code", "EB_RECEIPT_REAUTHENTICATION_FAILED")
        raise BindingError(code, "candidate-bound EB receipt did not reauthenticate") from exc
    if eb_result.get("overall_result") != "PASS":
        _fail("EB_RECEIPT_REAUTHENTICATION_FAILED", "EB receipt result is not PASS")
    _, eb_envelope = _load_json_canonical(eb_receipt, "EB_RECEIPT_CANONICAL_INVALID")
    eb_candidate = eb_envelope["receipt"]["candidate_binding"]
    if eb_candidate.get("path") != candidate_relative:
        _fail("EB_CANDIDATE_PATH_MISMATCH", "candidate argument differs from EB receipt")

    candidate_raw, candidate_envelope, candidate_inner = _manifest_binding(
        candidate, du, expected_head=required_head, runtime=False
    )
    try:
        du_result = du.validate_file(candidate, repository_root, expected_head=required_head)
    except Exception as exc:
        code = getattr(exc, "code", "DU_CANDIDATE_VALIDATION_FAILED")
        raise BindingError(code, "candidate did not pass DU Canonical V1") from exc
    if any(value != "PASS" for value in du_result.values()):
        _fail("DU_CANDIDATE_VALIDATION_FAILED", "candidate did not pass all DU gates")

    harness_runtime_root, harness_expected = extract_harness_paths(harness)
    provided_guest_root = PurePosixPath(guest_runtime_root)
    if provided_guest_root != harness_runtime_root:
        _fail(
            "HARNESS_RUNTIME_ROOT_MISMATCH",
            "provided guest runtime root differs from authenticated harness declaration",
        )
    expected_relative = harness_expected.relative_to(harness_runtime_root)
    runtime_relative, runtime = _runtime_actual(
        repository_root, export_root, expected_relative
    )
    runtime_raw, runtime_envelope, runtime_inner = _manifest_binding(
        runtime, du, expected_head=required_head, runtime=True
    )
    if runtime_raw != candidate_raw:
        _fail("RUNTIME_BYTES_DIFFER", "runtime bytes differ from validated candidate")
    if runtime_inner != candidate_inner or runtime_envelope != candidate_envelope:
        _fail("RUNTIME_SEMANTIC_IDENTITY_MISMATCH", "runtime manifest semantics differ")

    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "receipt_version": RECEIPT_VERSION,
        "generation_identity": GENERATION_IDENTITY,
        "validation_mode": VALIDATION_MODE,
        "validation_profile": VALIDATION_PROFILE,
        "validated_candidate": {
            "path": candidate_relative,
            "file_sha256": sha256_bytes(candidate_raw),
            "inner_sha256": candidate_inner,
            "canonical_serialization_state": "CANONICAL_V1_JSON",
        },
        "candidate_bound_eb_receipt": {
            "path": eb_relative,
            "file_sha256": sha256_path(eb_receipt),
            "inner_sha256": eb_envelope["receipt_inner_sha256"],
            "independent_verification": "PASS",
        },
        "runtime_consumer": {
            "guest_runtime_root": str(harness_runtime_root),
            "expected_path": str(harness_expected),
            "expected_relative_path": str(expected_relative),
            "repository_export_root": export_relative,
            "actual_path": runtime_relative,
            "file_sha256": sha256_bytes(runtime_raw),
            "inner_sha256": runtime_inner,
            "file_kind": "REGULAR_FILE",
            "symlink": False,
            "projection_completed_before_binding": True,
        },
        "harness_binding": {
            "path": harness_relative,
            "file_sha256": sha256_path(harness),
            "runtime_root_declaration": str(harness_runtime_root),
            "expected_continuation_path": str(harness_expected),
        },
        "identity_results": {
            "candidate_runtime_byte_identity": "PASS",
            "candidate_runtime_semantic_identity": "PASS",
            "harness_expected_path_identity": "PASS",
        },
        "implementation_bindings": _implementation_bindings(repository_root),
        "git_binding": {
            "required_head": required_head,
            "required_tree": required_tree,
        },
        "pre_materialization_runtime_path_binding_result": "PASS",
        "prohibited_actions": PROHIBITED_ACTIONS,
        "receipt_is_authority": False,
        "auto_continuable": False,
    }
    envelope = {
        "schema_id": ENVELOPE_SCHEMA_ID,
        "receipt": receipt,
        "receipt_inner_sha256": sha256_bytes(canonical_bytes(receipt)),
    }
    jsonschema.Draft202012Validator(_schema(repository_root)).validate(envelope)
    return envelope


def _require_hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail("RECEIPT_SCHEMA_INVALID", f"{field} must be lowercase SHA-256")
    return value


def verify_receipt_envelope(
    repository_root: Path, envelope: Any
) -> dict[str, str]:
    """Reauthenticate every candidate/runtime/harness/Git claim in a receipt."""
    try:
        jsonschema.Draft202012Validator(_schema(repository_root)).validate(envelope)
    except jsonschema.ValidationError as exc:
        raise BindingError("RECEIPT_SCHEMA_INVALID", "binding receipt schema rejected") from exc
    if envelope["schema_id"] != ENVELOPE_SCHEMA_ID:
        _fail("RECEIPT_SCHEMA_INVALID", "envelope identity differs")
    receipt = envelope["receipt"]
    embedded_inner = _require_hash(envelope["receipt_inner_sha256"], "receipt_inner_sha256")
    if embedded_inner != sha256_bytes(canonical_bytes(receipt)):
        _fail("RECEIPT_INNER_SHA256_MISMATCH", "receipt inner identity differs")
    if (
        receipt["schema_id"] != RECEIPT_SCHEMA_ID
        or receipt["receipt_version"] != RECEIPT_VERSION
        or receipt["generation_identity"] != GENERATION_IDENTITY
        or receipt["validation_mode"] != VALIDATION_MODE
        or receipt["validation_profile"] != VALIDATION_PROFILE
    ):
        _fail("RECEIPT_SCHEMA_INVALID", "receipt identity, version, mode, or profile differs")
    git_binding = receipt["git_binding"]
    _authenticate_git(
        repository_root,
        git_binding["required_head"],
        git_binding["required_tree"],
    )
    if receipt["implementation_bindings"] != _implementation_bindings(repository_root):
        _fail("IMPLEMENTATION_BINDING_MISMATCH", "validator or schema bytes differ")
    eb, du = _load_implementations(repository_root)

    candidate_binding = receipt["validated_candidate"]
    candidate_relative, candidate = _repo_file(
        repository_root,
        repository_root / candidate_binding["path"],
        "validated_candidate.path",
    )
    if candidate_relative != candidate_binding["path"]:
        _fail("CANDIDATE_PATH_MISMATCH", "candidate path is not canonical")
    candidate_raw, candidate_envelope, candidate_inner = _manifest_binding(
        candidate,
        du,
        expected_head=git_binding["required_head"],
        runtime=False,
    )
    if sha256_bytes(candidate_raw) != candidate_binding["file_sha256"]:
        _fail("CANDIDATE_FILE_SHA256_MISMATCH", "candidate bytes differ from receipt")
    if candidate_inner != candidate_binding["inner_sha256"]:
        _fail("CANDIDATE_INNER_SHA256_MISMATCH", "candidate inner identity differs")

    eb_binding = receipt["candidate_bound_eb_receipt"]
    eb_relative, eb_receipt = _repo_file(
        repository_root,
        repository_root / eb_binding["path"],
        "candidate_bound_eb_receipt.path",
    )
    if eb_relative != eb_binding["path"] or sha256_path(eb_receipt) != eb_binding["file_sha256"]:
        _fail("EB_RECEIPT_FILE_SHA256_MISMATCH", "EB receipt path or bytes differ")
    _, eb_envelope = _load_json_canonical(eb_receipt, "EB_RECEIPT_CANONICAL_INVALID")
    if eb_envelope.get("receipt_inner_sha256") != eb_binding["inner_sha256"]:
        _fail("EB_RECEIPT_INNER_SHA256_MISMATCH", "EB receipt inner identity differs")
    try:
        eb_result = eb.verify_receipt_file(repository_root, eb_receipt)
    except Exception as exc:
        code = getattr(exc, "code", "EB_RECEIPT_REAUTHENTICATION_FAILED")
        raise BindingError(code, "EB receipt did not reauthenticate") from exc
    if eb_result.get("overall_result") != "PASS":
        _fail("EB_RECEIPT_REAUTHENTICATION_FAILED", "EB result differs")
    if eb_envelope["receipt"]["candidate_binding"]["path"] != candidate_binding["path"]:
        _fail("EB_CANDIDATE_PATH_MISMATCH", "EB receipt names a different candidate")

    harness_binding = receipt["harness_binding"]
    harness_relative, harness = _repo_file(
        repository_root,
        repository_root / harness_binding["path"],
        "harness_binding.path",
    )
    if harness_relative != harness_binding["path"]:
        _fail("HARNESS_PATH_MISMATCH", "harness path is not canonical")
    if sha256_path(harness) != harness_binding["file_sha256"]:
        _fail("HARNESS_FILE_SHA256_MISMATCH", "harness bytes differ")
    harness_root, harness_expected = extract_harness_paths(harness)
    if harness_binding["runtime_root_declaration"] != str(harness_root):
        _fail("HARNESS_RUNTIME_ROOT_DECLARATION_MISMATCH", "harness root binding differs")
    if harness_binding["expected_continuation_path"] != str(harness_expected):
        _fail(
            "HARNESS_EXPECTED_PATH_DECLARATION_MISMATCH",
            "harness expected-path binding differs",
        )

    runtime_binding = receipt["runtime_consumer"]
    if runtime_binding["guest_runtime_root"] != str(harness_root):
        _fail("HARNESS_RUNTIME_ROOT_MISMATCH", "runtime root differs from harness")
    if runtime_binding["expected_path"] != str(harness_expected):
        _fail("HARNESS_EXPECTED_PATH_MISMATCH", "runtime expected path differs from harness")
    expected_relative = harness_expected.relative_to(harness_root)
    if runtime_binding["expected_relative_path"] != str(expected_relative):
        _fail("RUNTIME_RELATIVE_PATH_MISMATCH", "runtime relative path differs")
    export_relative, export_root = _repo_dir(
        repository_root,
        repository_root / runtime_binding["repository_export_root"],
        "runtime_consumer.repository_export_root",
    )
    if export_relative != runtime_binding["repository_export_root"]:
        _fail("RUNTIME_EXPORT_ROOT_MISMATCH", "runtime export root is not canonical")
    runtime_relative, runtime = _runtime_actual(repository_root, export_root, expected_relative)
    if runtime_relative != runtime_binding["actual_path"]:
        _fail(
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            "receipt actual path differs from harness-derived path",
        )
    runtime_raw, runtime_envelope, runtime_inner = _manifest_binding(
        runtime,
        du,
        expected_head=git_binding["required_head"],
        runtime=True,
    )
    if sha256_bytes(runtime_raw) != runtime_binding["file_sha256"]:
        _fail("RUNTIME_FILE_SHA256_MISMATCH", "runtime bytes differ from receipt")
    if runtime_inner != runtime_binding["inner_sha256"]:
        _fail("RUNTIME_INNER_SHA256_MISMATCH", "runtime inner identity differs")
    if runtime_raw != candidate_raw:
        _fail("RUNTIME_BYTES_DIFFER", "runtime bytes differ from candidate")
    if runtime_envelope != candidate_envelope or runtime_inner != candidate_inner:
        _fail("RUNTIME_SEMANTIC_IDENTITY_MISMATCH", "runtime semantics differ")
    if receipt["identity_results"] != {
        "candidate_runtime_byte_identity": "PASS",
        "candidate_runtime_semantic_identity": "PASS",
        "harness_expected_path_identity": "PASS",
    }:
        _fail("IDENTITY_RESULT_MISMATCH", "identity results differ")
    if receipt["pre_materialization_runtime_path_binding_result"] != "PASS":
        _fail("OVERALL_RESULT_INVALID", "binding result is not PASS")
    if receipt["prohibited_actions"] != PROHIBITED_ACTIONS:
        _fail("PROHIBITED_ACTIONS_MISMATCH", "fail-closed prohibitions differ")
    if receipt["receipt_is_authority"] is not False or receipt["auto_continuable"] is not False:
        _fail("AUTHORITY_SEMANTICS_INVALID", "receipt cannot be authority or auto-continuable")
    return {
        "candidate_bound_eb_receipt_reauthentication": "PASS",
        "candidate_runtime_byte_identity": "PASS",
        "candidate_runtime_semantic_identity": "PASS",
        "git_head_tree_binding": "PASS",
        "harness_identity_and_expected_path": "PASS",
        "post_binding_artifact_reauthentication": "PASS",
        "pre_materialization_runtime_path_binding_result": "PASS",
        "receipt_inner_authenticity": "PASS",
        "schema_validity": "PASS",
    }


def verify_receipt_file(repository_root: Path, receipt_path: Path) -> dict[str, str]:
    raw, envelope = _load_json_canonical(receipt_path, "RECEIPT_CANONICAL_INVALID")
    if not raw:
        _fail("RECEIPT_CANONICAL_INVALID", "receipt is empty")
    return verify_receipt_envelope(repository_root, envelope)


def _rehash_ee(envelope: dict[str, Any]) -> None:
    envelope["receipt_inner_sha256"] = sha256_bytes(canonical_bytes(envelope["receipt"]))


def _negative(
    case_id: str,
    expected_code: str,
    operation: Callable[[], None],
) -> dict[str, Any]:
    try:
        operation()
    except Exception as exc:
        observed = getattr(exc, "code", type(exc).__name__)
        return {
            "case_id": case_id,
            "expected_rejection": expected_code,
            "observed_rejection": observed,
            "result": "PASS" if observed == expected_code else "FAIL",
        }
    return {
        "case_id": case_id,
        "expected_rejection": expected_code,
        "observed_rejection": "NOT_REJECTED",
        "result": "FAIL",
    }


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _different_candidate(base: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(base)
    value["manifest"].setdefault("observations", []).append(
        "G77_256EE_NEGATIVE_DIFFERENT_CANDIDATE"
    )
    value["manifest_sha256"] = sha256_bytes(canonical_bytes(value["manifest"]))
    return value


def _temp_eb_receipt(
    eb: ModuleType,
    source_envelope: dict[str, Any],
    candidate_relative: str,
) -> dict[str, Any]:
    value = deepcopy(source_envelope)
    receipt = value["receipt"]
    receipt["candidate_binding"]["path"] = candidate_relative
    vector = list(receipt["canonical_argument_vector"])
    vector[3] = candidate_relative
    receipt["canonical_argument_vector"] = vector
    receipt["validation_command_identity_sha256"] = sha256_bytes(eb.canonical_bytes(vector))
    value["receipt_inner_sha256"] = sha256_bytes(eb.canonical_bytes(receipt))
    return value


def run_self_test(
    repository_root: Path,
    candidate_path: Path,
    eb_receipt_path: Path,
    harness_path: Path,
    runtime_export_root: Path,
    guest_runtime_root: str,
    *,
    required_head: str,
    required_tree: str,
) -> dict[str, Any]:
    """Execute the positive fixture and all fifteen required regressions."""
    positive = validate_binding(
        repository_root,
        candidate_path,
        eb_receipt_path,
        harness_path,
        runtime_export_root,
        guest_runtime_root,
        required_head=required_head,
        required_tree=required_tree,
    )
    positive_verification = verify_receipt_envelope(repository_root, positive)
    cases: list[dict[str, Any]] = [{
        "case_id": "POSITIVE_CANDIDATE_EQUALS_AUTHENTICATED_RUNTIME_INPUT",
        "expected_result": "PASS",
        "observed_result": positive_verification[
            "pre_materialization_runtime_path_binding_result"
        ],
        "result": "PASS",
    }]
    eb, _ = _load_implementations(repository_root)
    _, positive_candidate = _load_json_canonical(
        candidate_path.resolve(), "CANDIDATE_CANONICAL_SERIALIZATION_INVALID"
    )
    _, source_eb = _load_json_canonical(
        eb_receipt_path.resolve(), "EB_RECEIPT_CANONICAL_INVALID"
    )
    expected_name = PurePosixPath(
        positive["receipt"]["runtime_consumer"]["expected_relative_path"]
    )

    with tempfile.TemporaryDirectory(prefix=".g77_256ee_selftest_", dir=repository_root) as raw_tmp:
        temporary_root = Path(raw_tmp)

        absent_export = temporary_root / "absent-export"
        absent_export.mkdir()
        cases.append(_negative(
            "EXPECTED_RUNTIME_PATH_ABSENT",
            "EXPECTED_RUNTIME_PATH_ABSENT",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                absent_export, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        wrong_export = temporary_root / "wrong-export"
        wrong_export.mkdir()
        (wrong_export / "alternate.json").write_bytes(candidate_path.read_bytes())
        cases.append(_negative(
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                wrong_export, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        changed_export = temporary_root / "changed-export"
        changed_runtime = changed_export.joinpath(*expected_name.parts)
        changed_runtime.parent.mkdir(parents=True, exist_ok=True)
        one_byte_changed = bytearray(candidate_path.read_bytes())
        digest_start = one_byte_changed.index(b'"manifest_sha256":"') + len(
            b'"manifest_sha256":"'
        )
        one_byte_changed[digest_start] = (
            ord("0") if one_byte_changed[digest_start] != ord("0") else ord("1")
        )
        changed_runtime.write_bytes(one_byte_changed)
        cases.append(_negative(
            "RUNTIME_BYTES_DIFFER_BY_ONE_BYTE",
            "MANIFEST_INNER_SHA256_MISMATCH",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                changed_export, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        def tampered(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
            def operation() -> None:
                value = deepcopy(positive)
                mutator(value)
                _rehash_ee(value)
                verify_receipt_envelope(repository_root, value)
            return operation

        cases.append(_negative(
            "RUNTIME_SHA_MISMATCH",
            "RUNTIME_FILE_SHA256_MISMATCH",
            tampered(lambda value: value["receipt"]["runtime_consumer"].update(
                {"file_sha256": "0" * 64}
            )),
        ))
        cases.append(_negative(
            "RUNTIME_INNER_SHA_MISMATCH",
            "RUNTIME_INNER_SHA256_MISMATCH",
            tampered(lambda value: value["receipt"]["runtime_consumer"].update(
                {"inner_sha256": "0" * 64}
            )),
        ))

        candidate_copy = temporary_root / "candidate-copy.json"
        candidate_copy.write_bytes(candidate_path.read_bytes())
        candidate_copy_relative = candidate_copy.relative_to(repository_root).as_posix()
        temp_eb = _temp_eb_receipt(eb, source_eb, candidate_copy_relative)
        temp_eb_path = temporary_root / "candidate-copy-eb-receipt.json"
        temp_eb_path.write_bytes(eb.canonical_bytes(temp_eb))
        candidate_copy.write_bytes(canonical_bytes(_different_candidate(positive_candidate)))
        cases.append(_negative(
            "CANDIDATE_CHANGED_AFTER_EB_VALIDATION",
            "CANDIDATE_FILE_SHA256_MISMATCH",
            lambda: validate_binding(
                repository_root, candidate_copy, temp_eb_path, harness_path,
                runtime_export_root, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        changed = _different_candidate(positive_candidate)
        different_export = temporary_root / "different-candidate-export"
        _write(different_export.joinpath(*expected_name.parts), changed)
        cases.append(_negative(
            "RUNTIME_DERIVED_FROM_DIFFERENT_CANDIDATE",
            "RUNTIME_BYTES_DIFFER",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                different_export, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        cases.append(_negative(
            "HARNESS_SHA_MISMATCH",
            "HARNESS_FILE_SHA256_MISMATCH",
            tampered(lambda value: value["receipt"]["harness_binding"].update(
                {"file_sha256": "0" * 64}
            )),
        ))
        cases.append(_negative(
            "HARNESS_EXPECTED_PATH_DECLARATION_MISMATCH",
            "HARNESS_EXPECTED_PATH_DECLARATION_MISMATCH",
            tampered(lambda value: value["receipt"]["harness_binding"].update(
                {"expected_continuation_path": "/mnt/g77-evidence/other.json"}
            )),
        ))
        cases.append(_negative(
            "REQUIRED_HEAD_MISMATCH",
            "REQUIRED_HEAD_MISMATCH",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                runtime_export_root, guest_runtime_root,
                required_head="0" * 40, required_tree=required_tree,
            ),
        ))
        cases.append(_negative(
            "REQUIRED_TREE_MISMATCH",
            "REQUIRED_TREE_MISMATCH",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                runtime_export_root, guest_runtime_root,
                required_head=required_head, required_tree="0" * 40,
            ),
        ))

        noncanonical_export = temporary_root / "noncanonical-export"
        noncanonical_path = noncanonical_export.joinpath(*expected_name.parts)
        noncanonical_path.parent.mkdir(parents=True, exist_ok=True)
        noncanonical_path.write_text(json.dumps(positive_candidate, indent=2) + "\n")
        cases.append(_negative(
            "NON_CANONICAL_RUNTIME_MANIFEST",
            "RUNTIME_CANONICAL_SERIALIZATION_INVALID",
            lambda: validate_binding(
                repository_root, candidate_path, eb_receipt_path, harness_path,
                noncanonical_export, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        cases.append(_negative(
            "VALID_CANDIDATE_MISSING_RUNTIME_BINDING",
            "RECEIPT_SCHEMA_INVALID",
            tampered(lambda value: value["receipt"].pop("runtime_consumer")),
        ))
        cases.append(_negative(
            "VALID_RUNTIME_MISSING_CANDIDATE_BOUND_EB_RECEIPT",
            "BOUND_FILE_ABSENT",
            lambda: validate_binding(
                repository_root, candidate_path, temporary_root / "absent-eb.json",
                harness_path, runtime_export_root, guest_runtime_root,
                required_head=required_head, required_tree=required_tree,
            ),
        ))

        post_export = temporary_root / "post-binding-export"
        post_runtime = post_export.joinpath(*expected_name.parts)
        post_runtime.parent.mkdir(parents=True, exist_ok=True)
        post_runtime.write_bytes(candidate_path.read_bytes())
        post_receipt = validate_binding(
            repository_root, candidate_path, eb_receipt_path, harness_path,
            post_export, guest_runtime_root,
            required_head=required_head, required_tree=required_tree,
        )
        post_runtime.rename(post_runtime.with_name("substituted.json"))
        cases.append(_negative(
            "POST_BINDING_RENAME_OR_SUBSTITUTION",
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            lambda: verify_receipt_envelope(repository_root, post_receipt),
        ))

        cases.append(_negative(
            "RUNTIME_ACTUAL_PATH_RECEIPT_SUBSTITUTION",
            "RUNTIME_PATH_DIFFERS_FROM_HARNESS_EXPECTATION",
            tampered(lambda value: value["receipt"]["runtime_consumer"].update(
                {"actual_path": value["receipt"]["runtime_consumer"]["actual_path"] + ".other"}
            )),
        ))

    overall = "PASS" if all(item["result"] == "PASS" for item in cases) else "FAIL"
    return {
        "schema_id": "G77_256EE_RUNTIME_CONSUMER_BINDING_REGRESSION_EVIDENCE_V1",
        "generation_identity": GENERATION_IDENTITY,
        "required_head": required_head,
        "required_tree": required_tree,
        "positive_fixture_result": positive_verification,
        "case_count": len(cases),
        "positive_case_count": 1,
        "negative_case_count": len(cases) - 1,
        "cases": cases,
        "all_required_negative_regressions_present": True,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "e05_case_execution_count": 0,
        "production_route_count": 0,
        "overall_result": overall,
        "auto_continuable": False,
    }


def _failure(error: BindingError) -> bytes:
    return canonical_bytes({
        "schema_id": "G77_256EE_RUNTIME_CONSUMER_BINDING_FAILURE_V1",
        "failure_code": error.code,
        "pre_materialization_runtime_path_binding_pass_claimed": False,
        "overall_result": "FAIL_CLOSED",
    })


def main() -> int:
    parser = argparse.ArgumentParser(
        description="G77-256EE candidate-to-runtime continuation binding validator"
    )
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--validate-binding", action="store_true")
    modes.add_argument("--verify-receipt", type=Path)
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--eb-receipt", type=Path)
    parser.add_argument("--harness", type=Path)
    parser.add_argument("--runtime-export-root", type=Path)
    parser.add_argument("--guest-runtime-root")
    parser.add_argument("--required-head")
    parser.add_argument("--required-tree")
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--evidence-output", type=Path)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    try:
        if args.verify_receipt is not None:
            result = verify_receipt_file(repository_root, args.verify_receipt)
            print(canonical_bytes(result).decode(), end="")
            return 0
        required = (
            args.candidate, args.eb_receipt, args.harness, args.runtime_export_root,
            args.guest_runtime_root, args.required_head, args.required_tree,
        )
        if any(value is None for value in required):
            parser.error("validation and self-test modes require all binding arguments")
        if args.validate_binding:
            if args.receipt_output is None:
                parser.error("--validate-binding requires --receipt-output")
            envelope = validate_binding(
                repository_root, args.candidate, args.eb_receipt, args.harness,
                args.runtime_export_root, args.guest_runtime_root,
                required_head=args.required_head, required_tree=args.required_tree,
            )
            args.receipt_output.write_bytes(canonical_bytes(envelope))
            print(canonical_bytes(envelope).decode(), end="")
            return 0
        evidence = run_self_test(
            repository_root, args.candidate, args.eb_receipt, args.harness,
            args.runtime_export_root, args.guest_runtime_root,
            required_head=args.required_head, required_tree=args.required_tree,
        )
        if args.evidence_output is not None:
            args.evidence_output.write_bytes(canonical_bytes(evidence))
        print(canonical_bytes(evidence).decode(), end="")
        return 0 if evidence["overall_result"] == "PASS" else 1
    except BindingError as exc:
        print(_failure(exc).decode(), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
