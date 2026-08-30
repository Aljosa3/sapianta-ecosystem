#!/usr/bin/env python3
"""Admit and execute the exact FM QEMU argv once after Human authorization."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
GENERATION_IDENTITY = "G77_256FY_CLASS_A_RUNTIME_EXPORT_PREBOOT_VISIBILITY_COMPOSITION_CORRECTION_V1"
CONSTITUTIONAL_ANCHOR_HEAD = "5c972e9960987ab27420395b54ace693df097e7b"
CANDIDATE_SHA256 = "a28d2c6d903ed0abafd6fecdc1979f763de4c79127018655370975d52fc05fb4"
MATERIALIZATION_SHA256 = "bad42f1361aac5e45a773242fb6a00445282f8d996ad592d15d363019eaa6baf"
MATERIALIZATION_INNER_SHA256 = "e0452f63fbbf0cc890623b63a273973914852c7e24dad11b5b95f5ed0159a1d5"
CANONICAL_ARGV_SHA256 = "40a0c1382725a68f33beb0a351e2661cec5c1851041b4fb1058626a1d1da818e"
ADAPTER_SHA256 = "b7d8f5b3478d7cfff2cadce7e36b3a12c9b4a1ac5054da867668086f84e866d7"
FK_ADAPTER_SHA256 = "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
FM_ROOT = ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
FY_ROOT = ".github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1"
RUNTIME_EXPORT = f"{FY_ROOT}/runtime_export"
RUNTIME_MANIFEST = f"{RUNTIME_EXPORT}/G77_256FM_CONTINUATION_MANIFEST_V1.json"
VECTOR = f"{FY_ROOT}/qemu/G77_256FY_QEMU_ARGV_V1.json"
PRE_RECEIPT = f"{FY_ROOT}/receipts/G77_256FY_B1_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = f"{FY_ROOT}/receipts/G77_256FY_B1_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
RAW_EXECUTION = f"{RUNTIME_EXPORT}/G77_256FM_RAW_EXECUTION_EVIDENCE_V1.jsonl"
EXECUTION_SEAL = f"{RUNTIME_EXPORT}/G77_256FM_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN_SEAL = f"{RUNTIME_EXPORT}/G77_256FM_GUEST_TEARDOWN_SEAL_V1.json"
CANONICALIZER = ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"
CANONICALIZER_SHA256 = "00b2676f1c8360d7c1a3188095520f4592639e174f6b25e198e3036744d948ac"
AUTHORITY_SCHEMA = "G77_256FY_EXECUTION_TIME_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1"
AUTHORIZATION_SCHEMA = "G77_256FY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_V1"
FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256 = "84054b9a8840dd58450e4f0aa5b13e38f07a09a52c27b86c67b36eabcd9833f4"
FN_SPENT_AUTHORIZATION_SHA256 = "0fb64caf25be6abac9c0c1b8071e52527447163f4b1a72c2b1508dc9f5de9658"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")

CANDIDATE = f"{FM_ROOT}/raw/G77_256FM_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json"
MATERIALIZATION = f"{FY_ROOT}/G77_256FY_RUNTIME_EXPORT_PREBOOT_COMPOSITION_V1.json"
WRAPPER = f"{FM_ROOT}/harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
CLOUD_INIT = f"{FM_ROOT}/raw/G77_256FM_CLOUD_INIT_USER_DATA_V1.yaml"
FK_ADAPTER = ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
CANONICAL_CHE = "aigol/runtime/canonical_che_evidence_correlation_contract_v1.py"
BASE_IMAGE = "/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img"
OVERLAY = "/tmp/g77_256fy/guest-overlay.qcow2"
SEED = "/tmp/g77_256fy/nocloud-seed.img"

MOUNT_TAG = "g77_evidence"
GUEST_MOUNT_ROOT = "/mnt/g77-evidence"
HARNESS_RELATIVE_FILENAME = "G77_256FM_CONTINUATION_MANIFEST_V1.json"
GUEST_REQUIRED_PATH = f"{GUEST_MOUNT_ROOT}/{HARNESS_RELATIVE_FILENAME}"
HOST_EXPORT_ROOT = (
    "/home/pisarna/work/sapianta-fl/"
    ".github/governance/evidence/g77_256fy_runtime_export_preboot_visibility_v1/runtime_export"
)
MAPPED_HOST_PATH = f"{HOST_EXPORT_ROOT}/{HARNESS_RELATIVE_FILENAME}"
QEMU_VIRTFS_ARGUMENT = (
    f"local,path={HOST_EXPORT_ROOT},mount_tag={MOUNT_TAG},security_model=none"
)

EXPECTED_ASSET_SHA256 = {
    CANDIDATE: CANDIDATE_SHA256,
    MATERIALIZATION: MATERIALIZATION_SHA256,
    VECTOR: "d4e38fb7c6510cec380a95f66352b272a91b40753b199e6ee2ea9774a4bcf4a3",
    RUNTIME_MANIFEST: CANDIDATE_SHA256,
    WRAPPER: ADAPTER_SHA256,
    CLOUD_INIT: "5593e4491ce10e1efffe6584284d234f9d11bbbc8383acbafd5a83a294eaacd9",
    FK_ADAPTER: FK_ADAPTER_SHA256,
    CANONICAL_CHE: "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
    CANONICALIZER: CANONICALIZER_SHA256,
    BASE_IMAGE: "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733",
    OVERLAY: "6ea4eed169518c646774cfbe2c7b8c00646a9cdead8798f7c94c786c6b6ce8b2",
    SEED: "b36a1aac42f687fe3d6b71200b5b65ec93a8a6de59b7dce31d3e6bf2c3b93c2f",
}

AUTHORIZATION_FIELDS = {
    "schema_id",
    "authorization_present",
    "authorization_kind",
    "authorization_source_sha256",
    "authorized_generation_identity",
    "authorized_vector",
    "authorized_repository_head",
    "authorized_repository_tree",
    "authorized_constitutional_anchor_head",
    "authorized_candidate_sha256",
    "authorized_materialization_sha256",
    "authorized_canonical_argv_sha256",
    "authorized_wrapper_sha256",
    "authorized_fk_adapter_sha256",
    "vm_boot_limit",
    "qemu_system_execution_limit",
    "wrong_attempt_operational_attempt_limit",
    "retry_limit",
    "repair_limit",
    "replay_limit",
    "receipt_namespace_must_be_unconsumed",
    "network_authorized",
    "provider_authorized",
    "trusted_access_authorized",
    "authorization_reusable",
    "auto_continuable",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def receipt_namespace_paths(repository_root: Path) -> tuple[Path, Path, Path]:
    """Resolve the one exact receipt parent without following substitutions."""

    root = repository_root
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise RuntimeError("repository root absent, relative, symlinked, or non-directory")
    relative_pre = Path(PRE_RECEIPT)
    relative_post = Path(POST_RECEIPT)
    expected_parent = Path(FY_ROOT) / "receipts"
    for relative in (relative_pre, relative_post, expected_parent):
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("receipt namespace path is absolute or traverses its root")
    if relative_pre.parent != expected_parent or relative_post.parent != expected_parent:
        raise RuntimeError("receipt files do not share the exact expected parent")

    cursor = root
    for part in Path(FY_ROOT).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise RuntimeError("receipt evidence root contains a symlink substitution")
    evidence_root = root / FY_ROOT
    if not evidence_root.is_dir():
        raise RuntimeError("receipt evidence root absent or non-directory")
    if evidence_root.resolve() != (root.resolve() / FY_ROOT):
        raise RuntimeError("receipt evidence root resolves outside its exact identity")
    return root / expected_parent, root / relative_pre, root / relative_post


def receipt_consumable_paths(repository_root: Path) -> tuple[Path, ...]:
    parent, pre_receipt, post_receipt = receipt_namespace_paths(repository_root)
    del parent
    return (
        pre_receipt,
        post_receipt,
        repository_root / RAW_EXECUTION,
        repository_root / EXECUTION_SEAL,
        repository_root / TEARDOWN_SEAL,
    )


def validate_receipt_parent_ready(repository_root: Path) -> dict[str, Any]:
    """Read-only proof that the durable receipt parent and namespace are fresh."""

    parent, pre_receipt, post_receipt = receipt_namespace_paths(repository_root)
    if parent.is_symlink() or not parent.is_dir():
        raise RuntimeError("durable receipt parent absent, symlinked, or non-directory")
    if parent.resolve() != ((repository_root / FY_ROOT).resolve() / "receipts"):
        raise RuntimeError("durable receipt parent resolves outside the evidence root")

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(parent, flags)
    os.close(directory)
    if not os.access(parent, os.W_OK | os.X_OK):
        raise RuntimeError("durable receipt parent is not usable by the receipt writer")

    receipt_files_absent = not pre_receipt.exists() and not post_receipt.exists()
    guest_outputs_absent = not any(
        path.exists() for path in receipt_consumable_paths(repository_root)[2:]
    )
    parent_empty = next(parent.iterdir(), None) is None
    if not receipt_files_absent:
        raise RuntimeError("receipt file collision proves namespace consumption")
    if not guest_outputs_absent:
        raise RuntimeError("guest evidence collision proves namespace consumption")
    if not parent_empty:
        raise RuntimeError("unexpected durable receipt parent content")
    return {
        "receipt_parent": str(parent),
        "receipt_parent_ready": True,
        "receipt_files_absent": True,
        "guest_outputs_absent": True,
        "receipt_namespace_unused": True,
    }


def prepare_receipt_parent(repository_root: Path) -> dict[str, Any]:
    """Materialize and durability-probe only the exact fresh receipt parent."""

    parent, _, _ = receipt_namespace_paths(repository_root)
    if any(path.exists() for path in receipt_consumable_paths(repository_root)):
        raise RuntimeError("consumed receipt or guest evidence namespace cannot be prepared")
    if parent.is_symlink():
        raise RuntimeError("durable receipt parent symlink prohibited")
    if parent.exists():
        if not parent.is_dir():
            raise RuntimeError("durable receipt parent exists as a non-directory")
        if next(parent.iterdir(), None) is not None:
            raise RuntimeError("non-empty durable receipt parent cannot be prepared as fresh")
    else:
        parent.mkdir(mode=0o700, parents=False, exist_ok=False)

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(parent, flags)
    probe_name = ".g77_256_receipt_parent_durability_probe"
    probe_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        probe = os.open(probe_name, probe_flags, 0o600, dir_fd=directory)
        try:
            os.fsync(probe)
        finally:
            os.close(probe)
        os.unlink(probe_name, dir_fd=directory)
        os.fsync(directory)
    finally:
        os.close(directory)
    return validate_receipt_parent_ready(repository_root)


def write_atomic(path: Path, value: dict[str, Any]) -> str:
    payload = canonical_bytes(value)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def load_canonicalizer(repository_root: Path) -> ModuleType:
    path = repository_root / CANONICALIZER
    if sha256_path(path) != CANONICALIZER_SHA256:
        raise RuntimeError("canonical QEMU argv implementation hash mismatch")
    spec = importlib.util.spec_from_file_location("g77_256er_qemu_argv_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical QEMU argv implementation import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json_without_duplicate_keys(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise RuntimeError("JSON contains duplicate keys")
            value[key] = item
        return value

    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("JSON artifact malformed") from exc
    if not isinstance(value, dict):
        raise RuntimeError("JSON artifact root must be an object")
    return value, raw


def wrapper_guest_contract(wrapper_path: Path) -> tuple[str, str]:
    """Read the existing FM static declarations without importing guest code."""

    tree = ast.parse(wrapper_path.read_text(encoding="utf-8"), filename=str(wrapper_path))
    raw_roots: list[str] = []
    relative_names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id == "RAW_ROOT":
            call = node.value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "Path"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant)
                and isinstance(call.args[0].value, str)
                and not call.keywords
            ):
                raw_roots.append(call.args[0].value)
        if target.id == "CONTINUATION_MANIFEST_PATH":
            expression = node.value
            if (
                isinstance(expression, ast.BinOp)
                and isinstance(expression.op, ast.Div)
                and isinstance(expression.left, ast.Name)
                and expression.left.id == "RAW_ROOT"
                and isinstance(expression.right, ast.Constant)
                and isinstance(expression.right.value, str)
            ):
                relative_names.append(expression.right.value)
    if len(raw_roots) != 1 or len(relative_names) != 1:
        raise RuntimeError("FM wrapper guest manifest contract missing or ambiguous")
    return raw_roots[0], relative_names[0]


def g77_evidence_virtfs_argument(argv: list[str]) -> str:
    matches: list[str] = []
    for index, argument in enumerate(argv):
        if argument != "-virtfs":
            continue
        if index + 1 >= len(argv):
            raise RuntimeError("QEMU -virtfs argument missing")
        candidate = argv[index + 1]
        fields = candidate.split(",")
        if not fields or fields[0] != "local":
            continue
        options: dict[str, str] = {}
        for field in fields[1:]:
            if "=" not in field:
                raise RuntimeError("QEMU local -virtfs option malformed")
            key, value = field.split("=", 1)
            if key in options:
                raise RuntimeError("QEMU local -virtfs option ambiguous")
            options[key] = value
        if options.get("mount_tag") == MOUNT_TAG:
            if set(options) != {"path", "mount_tag", "security_model"}:
                raise RuntimeError("g77_evidence QEMU export options are not exact")
            matches.append(candidate)
    if len(matches) != 1:
        raise RuntimeError("g77_evidence QEMU export missing or ambiguous")
    return matches[0]


def prove_visibility_composition(
    *,
    repository_root: Path,
    checkpoint: dict[str, Any],
    argv: list[str],
    canonical_argv_sha256: str,
) -> dict[str, Any]:
    """Existing FM preboot owner: prove the host/QEMU/guest manifest relation."""

    manifest = checkpoint.get("canonical_manifest")
    visibility = checkpoint.get("visibility_composition")
    qemu_binding = checkpoint.get("qemu_binding")
    guest_contract = checkpoint.get("guest_contract")
    if not all(isinstance(item, dict) for item in (
        manifest, visibility, qemu_binding, guest_contract,
    )):
        raise RuntimeError("preboot visibility composition fields missing")

    assert isinstance(manifest, dict)
    assert isinstance(visibility, dict)
    assert isinstance(qemu_binding, dict)
    assert isinstance(guest_contract, dict)
    if qemu_binding.get("canonical_argv_sha256") != canonical_argv_sha256:
        raise RuntimeError("composition canonical QEMU argv identity mismatch")
    qemu_argument = g77_evidence_virtfs_argument(argv)
    if qemu_argument != visibility.get("qemu_virtfs_argument"):
        raise RuntimeError("validated runtime root differs from actual QEMU export root")

    export_root_value = visibility.get("host_export_root")
    relative_filename = visibility.get("harness_relative_filename")
    guest_mount = visibility.get("guest_mount_destination")
    if not all(isinstance(item, str) and item for item in (
        export_root_value, relative_filename, guest_mount,
    )):
        raise RuntimeError("visibility path binding malformed")
    export_root = Path(export_root_value)
    if not export_root.is_absolute() or export_root.is_symlink() or not export_root.is_dir():
        raise RuntimeError("runtime export root absent, non-directory, relative, or symlinked")
    if Path(relative_filename).name != relative_filename:
        raise RuntimeError("harness-relative manifest filename is not a single path component")

    wrapper_path_value = guest_contract.get("wrapper_path")
    cloud_init_path_value = guest_contract.get("cloud_init_path")
    if not isinstance(wrapper_path_value, str) or not isinstance(cloud_init_path_value, str):
        raise RuntimeError("guest contract paths malformed")
    wrapper_path = repository_root / wrapper_path_value
    cloud_init_path = repository_root / cloud_init_path_value
    if sha256_path(wrapper_path) != guest_contract.get("wrapper_sha256"):
        raise RuntimeError("FM wrapper identity mismatch in visibility composition")
    if sha256_path(cloud_init_path) != guest_contract.get("cloud_init_sha256"):
        raise RuntimeError("FM cloud-init identity mismatch in visibility composition")
    wrapper_root, wrapper_filename = wrapper_guest_contract(wrapper_path)
    if wrapper_root != guest_mount or wrapper_filename != relative_filename:
        raise RuntimeError("FM wrapper expected guest manifest path differs from composition")
    mount_literal = f"{MOUNT_TAG} {guest_mount}"
    if cloud_init_path.read_text(encoding="utf-8").count(mount_literal) != 1:
        raise RuntimeError("cloud-init guest mount destination missing or ambiguous")

    guest_required_path = f"{guest_mount}/{relative_filename}"
    if visibility.get("guest_required_path") != guest_required_path:
        raise RuntimeError("guest required manifest path mismatch")
    mapped_host_path = export_root / relative_filename
    if visibility.get("mapped_host_path") != str(mapped_host_path):
        raise RuntimeError("host-to-guest mapped manifest path mismatch")
    if mapped_host_path.is_symlink() or not mapped_host_path.is_file():
        raise RuntimeError("required guest manifest host projection absent or unsafe")
    if mapped_host_path.resolve().parent != export_root.resolve():
        raise RuntimeError("mapped manifest escapes certified runtime export root")

    source_path_value = manifest.get("source_path")
    runtime_path_value = manifest.get("runtime_export_path")
    if not isinstance(source_path_value, str) or not isinstance(runtime_path_value, str):
        raise RuntimeError("canonical manifest paths malformed")
    source_path = repository_root / source_path_value
    runtime_path = repository_root / runtime_path_value
    if runtime_path.resolve() != mapped_host_path.resolve():
        raise RuntimeError("materialized runtime projection differs from QEMU-mapped host file")
    source_sha = sha256_path(source_path)
    runtime_sha = sha256_path(runtime_path)
    expected_sha = manifest.get("source_sha256")
    if (
        source_sha != expected_sha
        or runtime_sha != expected_sha
        or manifest.get("runtime_export_sha256") != expected_sha
        or visibility.get("manifest_sha256") != expected_sha
        or manifest.get("byte_identity") != "PASS"
    ):
        raise RuntimeError("canonical/runtime-export continuation manifest identity mismatch")
    if source_path.read_bytes() != runtime_path.read_bytes():
        raise RuntimeError("canonical/runtime-export continuation manifest bytes differ")

    return {
        "result": "PREBOOT_VISIBILITY_COMPOSITION_PASS",
        "host_export_root": str(export_root),
        "guest_required_path": guest_required_path,
        "mapped_host_path": str(mapped_host_path),
        "manifest_sha256": runtime_sha,
        "canonical_argv_sha256": canonical_argv_sha256,
        "qemu_virtfs_argument": qemu_argument,
    }


def validate_preboot_visibility(
    repository_root: Path,
    argv: list[str],
    canonical_argv_sha256: str,
) -> dict[str, Any]:
    """Authenticate the certified FY checkpoint, then run the FM proof owner."""

    path = repository_root / MATERIALIZATION
    envelope, raw = load_json_without_duplicate_keys(path)
    if hashlib.sha256(raw).hexdigest() != MATERIALIZATION_SHA256:
        raise RuntimeError("FY visibility composition evidence hash mismatch")
    if set(envelope) != {"schema_id", "checkpoint", "checkpoint_sha256"}:
        raise RuntimeError("FY visibility composition envelope fields malformed")
    if envelope["schema_id"] != "G77_256FY_RUNTIME_EXPORT_PREBOOT_COMPOSITION_ENVELOPE_V1":
        raise RuntimeError("FY visibility composition envelope schema mismatch")
    checkpoint = envelope.get("checkpoint")
    if not isinstance(checkpoint, dict):
        raise RuntimeError("FY visibility composition checkpoint malformed")
    inner_sha = hashlib.sha256(canonical_bytes(checkpoint)).hexdigest()
    if inner_sha != MATERIALIZATION_INNER_SHA256 or envelope["checkpoint_sha256"] != inner_sha:
        raise RuntimeError("FY visibility composition inner seal mismatch")

    source = checkpoint.get("source_authority")
    manifest = checkpoint.get("canonical_manifest")
    visibility = checkpoint.get("visibility_composition")
    qemu_binding = checkpoint.get("qemu_binding")
    admission = checkpoint.get("admission")
    if not all(isinstance(item, dict) for item in (
        source, manifest, visibility, qemu_binding, admission,
    )):
        raise RuntimeError("FY certified visibility binding incomplete")
    assert isinstance(source, dict)
    assert isinstance(manifest, dict)
    assert isinstance(visibility, dict)
    assert isinstance(qemu_binding, dict)
    assert isinstance(admission, dict)
    expected_bindings = {
        "source_head": source.get("head") == "5b46fce41baede9b20adecf34b9119af2da9cca8",
        "source_tree": source.get("tree") == "bdfc40c8466b923e4edc23e2bbafc387d78b47b5",
        "manifest_source": manifest.get("source_path") == f"{FM_ROOT}/runtime/{HARNESS_RELATIVE_FILENAME}",
        "manifest_runtime": manifest.get("runtime_export_path") == RUNTIME_MANIFEST,
        "manifest_sha": manifest.get("source_sha256") == CANDIDATE_SHA256,
        "host_export_root": visibility.get("host_export_root") == HOST_EXPORT_ROOT,
        "relative_filename": visibility.get("harness_relative_filename") == HARNESS_RELATIVE_FILENAME,
        "mapped_host_path": visibility.get("mapped_host_path") == MAPPED_HOST_PATH,
        "guest_mount": visibility.get("guest_mount_destination") == GUEST_MOUNT_ROOT,
        "guest_required_path": visibility.get("guest_required_path") == GUEST_REQUIRED_PATH,
        "qemu_argument": visibility.get("qemu_virtfs_argument") == QEMU_VIRTFS_ARGUMENT,
        "vector_path": qemu_binding.get("path") == VECTOR,
        "vector_file_sha": qemu_binding.get("file_sha256") == EXPECTED_ASSET_SHA256[VECTOR],
        "canonical_argv_sha": qemu_binding.get("canonical_argv_sha256") == CANONICAL_ARGV_SHA256,
        "admission_owner": admission.get("owner") == "FM_MATERIALIZATION_PREBOOT_VALIDATION_PLUS_FO_FINAL_ADMISSION_COMPOSITION_GATE",
        "mismatch_denied": admission.get("mismatch_can_reach_qemu") is False,
    }
    failed = sorted(key for key, passed in expected_bindings.items() if not passed)
    if failed:
        raise RuntimeError(f"FY certified visibility binding mismatch: {','.join(failed)}")
    if sha256_path(repository_root / VECTOR) != qemu_binding["file_sha256"]:
        raise RuntimeError("FY QEMU argv file identity mismatch")

    result = prove_visibility_composition(
        repository_root=repository_root,
        checkpoint=checkpoint,
        argv=argv,
        canonical_argv_sha256=canonical_argv_sha256,
    )
    result.update({
        "composition_file_sha256": MATERIALIZATION_SHA256,
        "composition_inner_sha256": MATERIALIZATION_INNER_SHA256,
        "final_admission_owner": admission["owner"],
    })
    return result


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=repository_root, text=True).strip()


def authority_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_authority(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("execution authority handoff malformed") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError("execution authority handoff is not unique-key canonical JSON")
    return value, hashlib.sha256(raw).hexdigest()


def validate_execution_admission(
    *,
    authority: dict[str, Any],
    authority_file_sha256: str,
    supplied_authority_sha256: str,
    observed_head: str,
    observed_tree: str,
    anchor_is_ancestor: bool,
    repository_clean: bool,
    observed_asset_sha256: dict[str, str],
    argv: list[str],
    canonical_argv_sha256: str,
    receipt_namespace_consumed: bool,
) -> dict[str, str]:
    """Pure fail-closed admission; it performs no writes or process execution."""

    if set(authority) != {"schema_id", "authorization", "authorization_sha256"}:
        raise RuntimeError("execution authority envelope fields malformed or unknown")
    if authority.get("schema_id") != AUTHORITY_SCHEMA:
        raise RuntimeError("execution authority envelope schema mismatch")
    authorization = authority.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != AUTHORIZATION_FIELDS:
        raise RuntimeError("required execution authority field malformed, missing, or unknown")
    if not HEX_64.fullmatch(supplied_authority_sha256):
        raise RuntimeError("supplied execution authority hash malformed")
    if authority_file_sha256 != supplied_authority_sha256:
        raise RuntimeError("execution authority file hash mismatch")
    if authority.get("authorization_sha256") != authority_sha256(authorization):
        raise RuntimeError("execution authority inner seal mismatch")
    if authorization["schema_id"] != AUTHORIZATION_SCHEMA:
        raise RuntimeError("Human operational authorization schema mismatch")
    source_sha = authorization["authorization_source_sha256"]
    if not isinstance(source_sha, str) or not HEX_64.fullmatch(source_sha):
        raise RuntimeError("Human operational authorization source hash malformed")
    if source_sha in {FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256, FN_SPENT_AUTHORIZATION_SHA256}:
        raise RuntimeError("non-operational or already-spent Human authorization prohibited")
    expected_authorization = {
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorized_generation_identity": GENERATION_IDENTITY,
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": CANDIDATE_SHA256,
        "authorized_materialization_sha256": MATERIALIZATION_SHA256,
        "authorized_canonical_argv_sha256": CANONICAL_ARGV_SHA256,
        "authorized_wrapper_sha256": ADAPTER_SHA256,
        "authorized_fk_adapter_sha256": FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_attempt_operational_attempt_limit": 1,
        "retry_limit": 0,
        "repair_limit": 0,
        "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False,
        "provider_authorized": False,
        "trusted_access_authorized": False,
        "authorization_reusable": False,
        "auto_continuable": False,
    }
    for field, expected in expected_authorization.items():
        if authorization[field] != expected:
            raise RuntimeError(f"execution authority binding mismatch: {field}")
    if not isinstance(observed_head, str) or not HEX_40.fullmatch(observed_head):
        raise RuntimeError("observed repository HEAD malformed")
    if not isinstance(observed_tree, str) or not HEX_40.fullmatch(observed_tree):
        raise RuntimeError("observed repository tree malformed")
    if authorization["authorized_repository_head"] != observed_head:
        raise RuntimeError("committed repository HEAD not authorized")
    if authorization["authorized_repository_tree"] != observed_tree:
        raise RuntimeError("committed repository tree not authorized")
    if not anchor_is_ancestor:
        raise RuntimeError("committed constitutional anchor not in repository ancestry")
    if not repository_clean:
        raise RuntimeError("repository state is not clean")
    if set(observed_asset_sha256) != set(EXPECTED_ASSET_SHA256):
        raise RuntimeError("asset observation set incomplete or unknown")
    for path, expected_sha in EXPECTED_ASSET_SHA256.items():
        if observed_asset_sha256[path] != expected_sha:
            raise RuntimeError(f"exact asset binding mismatch: {path}")
    if canonical_argv_sha256 != CANONICAL_ARGV_SHA256:
        raise RuntimeError("canonical QEMU argv binding mismatch")
    if not isinstance(argv, list) or not argv or argv[0] != "/usr/bin/qemu-system-x86_64":
        raise RuntimeError("exact QEMU argv invalid")
    if argv.count("-nic") != 1 or argv[argv.index("-nic") + 1] != "none":
        raise RuntimeError("no-network QEMU vector invalid")
    if receipt_namespace_consumed:
        raise RuntimeError("FM one-shot receipt namespace already consumed")
    return {
        "result": "ADMIT_TO_BOOT_BOUNDARY_ONLY",
        "authorized_repository_head": observed_head,
        "authorized_repository_tree": observed_tree,
        "constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "execution_authority_file_sha256": authority_file_sha256,
        "human_authorization_source_sha256": source_sha,
    }


def validate_final_admission(
    *,
    repository_root: Path,
    authority: dict[str, Any],
    authority_file_sha256: str,
    supplied_authority_sha256: str,
    observed_head: str,
    observed_tree: str,
    anchor_is_ancestor: bool,
    repository_clean: bool,
    observed_asset_sha256: dict[str, str],
    argv: list[str],
    canonical_argv_sha256: str,
    receipt_namespace_consumed: bool,
) -> dict[str, str]:
    """FO final admission extended by the existing FM preboot composition gate."""

    receipt_readiness = validate_receipt_parent_ready(repository_root)
    visibility = validate_preboot_visibility(
        repository_root,
        argv,
        canonical_argv_sha256,
    )
    admission = validate_execution_admission(
        authority=authority,
        authority_file_sha256=authority_file_sha256,
        supplied_authority_sha256=supplied_authority_sha256,
        observed_head=observed_head,
        observed_tree=observed_tree,
        anchor_is_ancestor=anchor_is_ancestor,
        repository_clean=repository_clean,
        observed_asset_sha256=observed_asset_sha256,
        argv=argv,
        canonical_argv_sha256=canonical_argv_sha256,
        receipt_namespace_consumed=receipt_namespace_consumed,
    )
    admission.update({
        "receipt_parent": receipt_readiness["receipt_parent"],
        "receipt_parent_ready": "PASS",
        "receipt_files_absent": "PASS",
        "receipt_namespace_unused": "PASS",
        "preboot_visibility_composition": visibility["result"],
        "runtime_export_root": visibility["host_export_root"],
        "guest_required_manifest_path": visibility["guest_required_path"],
        "runtime_manifest_sha256": visibility["manifest_sha256"],
        "visibility_composition_sha256": visibility["composition_file_sha256"],
    })
    return admission


def asset_observations(repository_root: Path) -> dict[str, str]:
    observations: dict[str, str] = {}
    for path in EXPECTED_ASSET_SHA256:
        target = Path(path) if Path(path).is_absolute() else repository_root / path
        observations[path] = sha256_path(target)
    return observations


def constitutional_anchor_is_ancestor(repository_root: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", CONSTITUTIONAL_ANCHOR_HEAD, "HEAD"],
        cwd=repository_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def receipt(*, phase: str, argv: list[str], digest: str, vector_sha256: str,
            executable_sha256: str, started_ns: int, completed_ns: int | None,
            exit_status: int | None, admission: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_id": f"G77_256FY_B1_{phase}_EXECUTED_QEMU_ARGV_RECEIPT_V1",
        "generation_identity": GENERATION_IDENTITY,
        "authorized_repository_head": admission["authorized_repository_head"],
        "authorized_repository_tree": admission["authorized_repository_tree"],
        "constitutional_anchor_head": admission["constitutional_anchor_head"],
        "execution_authority_file_sha256": admission["execution_authority_file_sha256"],
        "human_authorization_source_sha256": admission["human_authorization_source_sha256"],
        "candidate_sha256": CANDIDATE_SHA256,
        "adapter_sha256": ADAPTER_SHA256,
        "canonicalizer": {
            "path": CANONICALIZER,
            "sha256": CANONICALIZER_SHA256,
            "algorithm": "SHA256_DOMAIN_U64BE_ARGC_REPEATED_U64BE_UTF8_BYTE_LENGTH_AND_BYTES",
        },
        "vector": {
            "path": VECTOR,
            "file_sha256": vector_sha256,
            "canonical_argv_sha256": digest,
            "argv": argv,
        },
        "direct_call_site": "subprocess.run(argv, check=False)",
        "executable_path": argv[0],
        "executable_sha256": executable_sha256,
        "started_unix_ns": started_ns,
        "completed_unix_ns": completed_ns,
        "process_exit_status": exit_status,
        "execution_attempt_count": 1,
        "automatic_retry_count": 0,
        "receipt_is_authority": False,
        "auto_continuable": False,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-authority", required=True, type=Path)
    parser.add_argument("--execution-authority-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path.cwd().resolve()
    pre_path = repository_root / PRE_RECEIPT
    post_path = repository_root / POST_RECEIPT
    consumable_paths = receipt_consumable_paths(repository_root)
    argv = json.loads((repository_root / VECTOR).read_text(encoding="utf-8"))
    canonicalizer = load_canonicalizer(repository_root)
    digest = canonicalizer.argv_sha256(argv)
    vector_sha = sha256_path(repository_root / VECTOR)
    authority, authority_file_sha = load_authority(arguments.execution_authority.resolve())
    admission = validate_final_admission(
        repository_root=repository_root,
        authority=authority,
        authority_file_sha256=authority_file_sha,
        supplied_authority_sha256=arguments.execution_authority_sha256,
        observed_head=git(repository_root, "rev-parse", "HEAD"),
        observed_tree=git(repository_root, "rev-parse", "HEAD^{tree}"),
        anchor_is_ancestor=constitutional_anchor_is_ancestor(repository_root),
        repository_clean=git(repository_root, "status", "--porcelain") == "",
        observed_asset_sha256=asset_observations(repository_root),
        argv=argv,
        canonical_argv_sha256=digest,
        receipt_namespace_consumed=any(path.exists() for path in consumable_paths),
    )
    executable_sha = sha256_path(Path(argv[0]))
    started = time.time_ns()
    write_atomic(pre_path, receipt(
        phase="PRE", argv=argv, digest=digest, vector_sha256=vector_sha,
        executable_sha256=executable_sha, started_ns=started,
        completed_ns=None, exit_status=None, admission=admission,
    ))
    status = 255
    try:
        result = subprocess.run(argv, check=False)
        status = result.returncode
    finally:
        completed = time.time_ns()
        write_atomic(post_path, receipt(
            phase="POST", argv=argv, digest=digest, vector_sha256=vector_sha,
            executable_sha256=executable_sha, started_ns=started,
            completed_ns=completed, exit_status=status, admission=admission,
        ))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
