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
import tempfile
import time
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sapianta_fresh_operation_context_v1 as fresh_context


GENERATION_IDENTITY = "CONTEXT_REQUIRED__NO_HISTORICAL_FY_FALLBACK"
CONSTITUTIONAL_ANCHOR_HEAD = "5c972e9960987ab27420395b54ace693df097e7b"
CANDIDATE_SHA256 = "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a"
MATERIALIZATION_SHA256 = "bad42f1361aac5e45a773242fb6a00445282f8d996ad592d15d363019eaa6baf"
MATERIALIZATION_INNER_SHA256 = "e0452f63fbbf0cc890623b63a273973914852c7e24dad11b5b95f5ed0159a1d5"
CANONICAL_ARGV_SHA256 = "40a0c1382725a68f33beb0a351e2661cec5c1851041b4fb1058626a1d1da818e"
ADAPTER_SHA256 = "f2808a148bc9839f083ea9e59903674fe0dcd2a7587eee342fca44066ee9ad2b"
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
AUTHORITY_SCHEMA = "SAPIANTA_CONTEXT_BOUND_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1"
AUTHORIZATION_SCHEMA = "SAPIANTA_CONTEXT_BOUND_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_V1"
FO_REPOSITORY_ONLY_AUTHORIZATION_SHA256 = "84054b9a8840dd58450e4f0aa5b13e38f07a09a52c27b86c67b36eabcd9833f4"
FN_SPENT_AUTHORIZATION_SHA256 = "0fb64caf25be6abac9c0c1b8071e52527447163f4b1a72c2b1508dc9f5de9658"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")

CANDIDATE = (
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
MATERIALIZATION = f"{FY_ROOT}/G77_256FY_RUNTIME_EXPORT_PREBOOT_COMPOSITION_V1.json"
WRAPPER = f"{FM_ROOT}/harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
CLOUD_INIT = f"{FM_ROOT}/raw/G77_256FM_CLOUD_INIT_USER_DATA_V1.yaml"
CLOUD_INIT_META_DATA = f"{FM_ROOT}/raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
CLOUD_INIT_NETWORK_CONFIG = f"{FM_ROOT}/raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
CLOUD_INIT_SHA256 = "3a4c989de77abec366ec5587b038a7341e71aac916d9cd9c7deba424f4a275ec"
FK_ADAPTER = ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
CANONICAL_CHE = "aigol/runtime/canonical_che_evidence_correlation_contract_v1.py"
ER_HARNESS_RELATIVE = (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
DN_HARNESS = (
    ".github/governance/evidence/g77_256dn_p03_diagnostic_v1/harness/"
    "G77_256DN_P03_DIAGNOSTIC_HARNESS_V1.py"
)
RAW_EVIDENCE_SCHEMA = (
    ".github/governance/evidence/g77_256er_p11_operational_v1/"
    "G77_256ER_RAW_EVIDENCE_SCHEMA_V1.json"
)
BASE_IMAGE = "/tmp/g77_256cw.IkqZJN/noble-server-cloudimg-amd64.img"
OVERLAY = "/tmp/g77_256fy/guest-overlay.qcow2"
SEED = (
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/"
    "g77_256gh_guest_adapter_path_binding_v1/static/"
    "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)
CHECKOUT = "/tmp/g77_256fm/checkout"
CHECKOUT_HEAD = "7dce67ec18696ba0bad73130f3f7a84168f25277"
CHECKOUT_TREE = "3cb61ec34e9593efb711dce61014dc8fdf0f6dd9"
GUEST_CHECKOUT_DESTINATION = "/mnt/aigol"
GUEST_CHECKOUT_MOUNT_TAG = "aigol_checkout"
ER_HARNESS_SHA256 = "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89"
QEMU_EXECUTABLE_SHA256 = "8a35ccba41582fc6c38b9df85fc9e35fa1d42f414d2d7d8090ee9b2f5e7c0854"

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
    CLOUD_INIT: CLOUD_INIT_SHA256,
    FK_ADAPTER: FK_ADAPTER_SHA256,
    CANONICAL_CHE: "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
    CANONICALIZER: CANONICALIZER_SHA256,
    BASE_IMAGE: "6e40c07ae715f744f84af0bec76415cc1987dd115b4b8de437818561f01a3733",
    OVERLAY: "6ea4eed169518c646774cfbe2c7b8c00646a9cdead8798f7c94c786c6b6ce8b2",
    SEED: "966f1910bbffe20fa18c4cee56ff61dcbb069348e2929bfda74e029a9dc0ec58",
}

AUTHORIZATION_FIELDS = {
    "schema_id",
    "authorization_present",
    "authorization_kind",
    "authorization_source_sha256",
    "authorized_context_sha256",
    "authorized_operation_identity",
    "authorized_generation_identity",
    "authorized_vector",
    "authorized_repository_head",
    "authorized_repository_tree",
    "authorized_constitutional_anchor_head",
    "authorized_candidate_sha256",
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


def resolve_candidate_source(
    repository_root: Path,
    candidate_source_path: Path | None = None,
) -> tuple[str, Path]:
    """Resolve one exact repository-resident candidate without a HEAD alias."""

    root = repository_root.resolve()
    supplied = Path(CANDIDATE) if candidate_source_path is None else candidate_source_path
    candidate = supplied if supplied.is_absolute() else root / supplied
    if candidate.is_symlink() or not candidate.is_file():
        raise RuntimeError("live candidate binding absent, symlinked, or non-regular")
    resolved = candidate.resolve()
    if candidate.absolute() != resolved:
        raise RuntimeError("live candidate binding cannot use a symlinked path component")
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise RuntimeError("live candidate binding must be repository-resident") from exc
    if resolved != root / relative:
        raise RuntimeError("live candidate binding path is not canonical")
    return relative, resolved


def receipt_namespace_paths(
    repository_root: Path,
    context: dict[str, Any],
) -> tuple[Path, Path, Path]:
    """Resolve only the receipt namespace declared by a validated context."""

    fresh_context.validate_context(context, repository_root=repository_root)
    parent = Path(context["receipt_parent"])
    pre_receipt = Path(context["pre_receipt_path"])
    post_receipt = Path(context["post_receipt_path"])
    operation_root = Path(context["operation_evidence_root"])
    if parent != operation_root / "receipts":
        raise RuntimeError("context receipt parent is not canonically derived")
    if pre_receipt.parent != parent or post_receipt.parent != parent:
        raise RuntimeError("context receipt paths escape their exact parent")
    if operation_root.is_symlink() or not operation_root.is_dir():
        raise RuntimeError("context operation evidence root absent or unsafe")
    if parent.is_symlink() or pre_receipt.is_symlink() or post_receipt.is_symlink():
        raise RuntimeError("receipt namespace symlink substitution prohibited")
    return parent, pre_receipt, post_receipt


def receipt_consumable_paths(
    repository_root: Path,
    context: dict[str, Any],
) -> tuple[Path, ...]:
    parent, pre_receipt, post_receipt = receipt_namespace_paths(repository_root, context)
    del parent
    complete = fresh_context.complete_mutable_sink_paths(context)
    if complete[:2] != (pre_receipt, post_receipt):
        raise RuntimeError("complete sink set receipt binding mismatch")
    return complete


def validate_receipt_parent_ready(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Read-only proof that the durable receipt parent and namespace are fresh."""

    parent, pre_receipt, post_receipt = receipt_namespace_paths(repository_root, context)
    if parent.is_symlink() or not parent.is_dir():
        raise RuntimeError("durable receipt parent absent, symlinked, or non-directory")
    if parent.resolve() != (Path(context["operation_evidence_root"]).resolve() / "receipts"):
        raise RuntimeError("durable receipt parent resolves outside the context evidence root")

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(parent, flags)
    os.close(directory)
    if not os.access(parent, os.W_OK | os.X_OK):
        raise RuntimeError("durable receipt parent is not usable by the receipt writer")

    receipt_files_absent = not pre_receipt.exists() and not post_receipt.exists()
    guest_outputs_absent = not any(
        path.exists() for path in receipt_consumable_paths(repository_root, context)[2:]
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


def prepare_receipt_parent(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Materialize and durability-probe only the exact fresh receipt parent."""

    parent, _, _ = receipt_namespace_paths(repository_root, context)
    if any(path.exists() for path in receipt_consumable_paths(repository_root, context)):
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
    return validate_receipt_parent_ready(repository_root, context)


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


def guest_harness_virtfs_argument(argv: list[str]) -> str:
    """Return the single read-only operation-local guest harness export."""

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
        flags: set[str] = set()
        for field in fields[1:]:
            if "=" in field:
                key, value = field.split("=", 1)
                if key in options:
                    raise RuntimeError("QEMU local -virtfs option ambiguous")
                options[key] = value
            else:
                if field in flags:
                    raise RuntimeError("QEMU local -virtfs flag ambiguous")
                flags.add(field)
        if options.get("mount_tag") == fresh_context.GUEST_HARNESS_MOUNT_TAG:
            if (
                set(options)
                != {"path", "mount_tag", "security_model", "readonly"}
                or options.get("readonly") != "on"
                or flags
            ):
                raise RuntimeError("guest harness QEMU export options are not exact")
            matches.append(candidate)
    if len(matches) != 1:
        raise RuntimeError("guest harness QEMU export missing or ambiguous")
    return matches[0]


def fc_guest_consumer_path(repository_root: Path, prefix: str) -> str:
    """Authenticate and derive the specialized FC/ER adapter open path."""

    source_path = repository_root / FK_ADAPTER
    if sha256_path(source_path) != FK_ADAPTER_SHA256:
        raise RuntimeError("committed FK-hardened FC adapter identity mismatch")
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    paths: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        value = node.value
        if (
            isinstance(target, ast.Attribute)
            and target.attr == "EN_HARNESS_PATH"
            and isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "Path"
            and len(value.args) == 1
            and isinstance(value.args[0], ast.Constant)
            and isinstance(value.args[0].value, str)
            and not value.keywords
        ):
            paths.append(value.args[0].value)
    if paths != [
        "/mnt/dp-harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    ]:
        raise RuntimeError("FC guest adapter consumer path missing or ambiguous")
    fresh_context._validate_prefix(prefix)
    return paths[0].replace("G77_256FC", prefix)


def prove_guest_adapter_binding(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Prove source, projection, QEMU exposure, bootstrap, and consumer identity."""

    fresh_context.validate_context(context, repository_root=repository_root)
    binding = context["guest_adapter_binding"]
    source = repository_root / binding["source_path"]
    projection_root = Path(binding["projection_root"])
    projected = Path(binding["projected_path"])
    bootstrap = Path(binding["bootstrap_projected_path"])
    if source.is_symlink() or not source.is_file():
        raise RuntimeError("adapter source absent or unsafe")
    source_sha = sha256_path(source)
    if source_sha != binding["source_sha256"]:
        raise RuntimeError("adapter source SHA-256 mismatch")
    if projection_root.is_symlink() or not projection_root.is_dir():
        raise RuntimeError("adapter projection root absent or unsafe")
    expected_entries = {projected, bootstrap}
    if set(projection_root.iterdir()) != expected_entries:
        raise RuntimeError("adapter projection stale, duplicate, or ambiguous")
    for path in expected_entries:
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("adapter projection entry absent or unsafe")
        if sha256_path(path) != source_sha or path.read_bytes() != source.read_bytes():
            raise RuntimeError("adapter source/projected exact bytes differ")

    qemu_argument = guest_harness_virtfs_argument(context["canonical_argv"])
    expected_argument = (
        f"local,path={projection_root},"
        f"mount_tag={fresh_context.GUEST_HARNESS_MOUNT_TAG},"
        "security_model=none,readonly=on"
    )
    if qemu_argument != expected_argument:
        raise RuntimeError("adapter projection/QEMU mount binding mismatch")

    cloud_init = repository_root / CLOUD_INIT
    if sha256_path(cloud_init) != context["wrapper_fc_er_che_schema_hashes"]["cloud_init"]:
        raise RuntimeError("cloud-init source identity mismatch")
    cloud_text = cloud_init.read_text(encoding="utf-8")
    mount_literal = (
        f"{fresh_context.GUEST_HARNESS_MOUNT_TAG} "
        f"{fresh_context.GUEST_HARNESS_ROOT}"
    )
    if cloud_text.count(mount_literal) != 1:
        raise RuntimeError("cloud-init guest harness mount missing or ambiguous")
    if cloud_text.count(binding["bootstrap_guest_path"]) != 1:
        raise RuntimeError("cloud-init adapter bootstrap consumer mismatch")
    seed = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["seed"]["path"]
    )
    seed_sha = sha256_path(seed)
    if seed_sha != context["qemu_executable_base_seed_checkout_bindings"]["seed"]["sha256"]:
        raise RuntimeError("NoCloud seed SHA-256 mismatch")
    seed_sources = {
        "/user-data": cloud_init,
        "/meta-data": repository_root / CLOUD_INIT_META_DATA,
        "/network-config": repository_root / CLOUD_INIT_NETWORK_CONFIG,
    }
    for member, source_path in seed_sources.items():
        try:
            projected_bytes = subprocess.check_output(
                ["isoinfo", "-i", str(seed), "-R", "-x", member],
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise RuntimeError("NoCloud seed static source projection unavailable") from exc
        if projected_bytes != source_path.read_bytes():
            raise RuntimeError(f"NoCloud seed {member} source bytes differ")
    command_bindings = (
        binding["bootstrap_guest_path"],
        binding["source_sha256"],
        context["wrapper_fc_er_che_schema_hashes"]["raw_evidence_schema"],
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"],
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"],
        sha256_path(repository_root / DN_HARNESS),
    )
    if any(cloud_text.count(value) != 1 for value in command_bindings):
        raise RuntimeError("cloud-init pre-request argument binding missing or ambiguous")

    consumer_path = fc_guest_consumer_path(
        repository_root, context["identity_namespace_prefix"]
    )
    if consumer_path != binding["guest_path"]:
        raise RuntimeError("projected adapter and guest consumer path differ")
    return {
        "result": "PREAUTHORITY_GUEST_ADAPTER_BINDING_PASS",
        "adapter_identity": binding["adapter_identity"],
        "source_path": binding["source_path"],
        "source_sha256": source_sha,
        "projected_path": str(projected),
        "projected_sha256": sha256_path(projected),
        "guest_path": binding["guest_path"],
        "guest_consumer_path": consumer_path,
        "qemu_virtfs_argument": qemu_argument,
        "nocloud_seed_sha256": seed_sha,
        "nocloud_source_projection_identity": "PASS",
        "source_projected_byte_identity": "PASS",
        "stale_generation_alias": "ABSENT_AS_DYNAMIC_SUBSTITUTE",
    }


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


def _validate_historical_fy_preboot_visibility(
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


def validate_preboot_visibility(
    repository_root: Path,
    context: dict[str, Any],
    argv: list[str],
    canonical_argv_sha256: str,
    *,
    candidate_source_path: Path | None = None,
) -> dict[str, Any]:
    """FY visibility semantics applied only to context-declared fresh paths."""

    fresh_context.validate_context(context, repository_root=repository_root)
    if argv != context["canonical_argv"]:
        raise RuntimeError("context canonical argv instance mismatch")
    if canonical_argv_sha256 != context["canonical_argv_sha256"]:
        raise RuntimeError("context canonical argv digest mismatch")
    qemu_argument = g77_evidence_virtfs_argument(argv)
    export_root = Path(context["runtime_export_root"])
    expected_argument = (
        f"local,path={export_root},mount_tag={MOUNT_TAG},security_model=none"
    )
    if qemu_argument != expected_argument:
        raise RuntimeError("runtime-export/virtfs context mismatch")
    if export_root.is_symlink() or not export_root.is_dir():
        raise RuntimeError("context runtime export absent or unsafe")
    manifest_path = Path(context["runtime_manifest_path"])
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise RuntimeError("context runtime manifest projection absent or unsafe")
    _, candidate_path = resolve_candidate_source(
        repository_root, candidate_source_path
    )
    if manifest_path.read_bytes() != candidate_path.read_bytes():
        raise RuntimeError("certified initial manifest projection bytes mismatch")
    manifest_sha = sha256_path(manifest_path)
    if manifest_sha != context["candidate_manifest_sha256"]:
        raise RuntimeError("context candidate binding mismatch")
    context_projection = export_root / fresh_context.GUEST_CONTEXT_FILENAME
    if context_projection.is_symlink() or not context_projection.is_file():
        raise RuntimeError("guest operation context projection absent or unsafe")
    projected_context = fresh_context.load_context(
        context_projection,
        repository_root=repository_root,
    )
    if projected_context != context:
        raise RuntimeError("guest context projection mismatch")
    return {
        "result": "PREBOOT_VISIBILITY_COMPOSITION_PASS",
        "host_export_root": str(export_root),
        "guest_required_path": context["guest_context_path"],
        "mapped_host_path": str(context_projection),
        "manifest_sha256": manifest_sha,
        "canonical_argv_sha256": canonical_argv_sha256,
        "qemu_virtfs_argument": qemu_argument,
        "composition_file_sha256": "CONTEXT_SEALED__NO_HISTORICAL_FY_FALLBACK",
    }


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=repository_root, text=True).strip()


def context_asset_expectations(
    context: dict[str, Any],
    candidate_source_path: Path | None = None,
) -> dict[str, str]:
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    candidate_key = CANDIDATE if candidate_source_path is None else candidate_source_path.as_posix()
    if Path(candidate_key).is_absolute() or ".." in Path(candidate_key).parts:
        raise RuntimeError("candidate asset key must be repository-relative")
    checkout_root = Path(bindings["checkout"]["path"])
    return {
        candidate_key: context["candidate_manifest_sha256"],
        WRAPPER: hashes["wrapper"],
        CLOUD_INIT: hashes["cloud_init"],
        FK_ADAPTER: hashes["fc_fk_adapter"],
        CANONICAL_CHE: hashes["canonical_che"],
        CANONICALIZER: hashes["canonicalizer"],
        RAW_EVIDENCE_SCHEMA: hashes["raw_evidence_schema"],
        DN_HARNESS: "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
        str(checkout_root / ER_HARNESS_RELATIVE): hashes["er_harness"],
        str(checkout_root / FK_ADAPTER): hashes["fc_fk_adapter"],
        str(checkout_root / CANONICAL_CHE): hashes["canonical_che"],
        bindings["qemu_executable"]["path"]: bindings["qemu_executable"]["sha256"],
        bindings["base"]["path"]: bindings["base"]["sha256"],
        bindings["seed"]["path"]: bindings["seed"]["sha256"],
    }


def validate_immutable_context_bindings(
    repository_root: Path,
    context: dict[str, Any],
    candidate_source_path: Path | None = None,
) -> None:
    fresh_context.validate_context(context, repository_root=repository_root)
    _, candidate = resolve_candidate_source(repository_root, candidate_source_path)
    if sha256_path(candidate) != context["candidate_manifest_sha256"]:
        raise RuntimeError("context live candidate binding mismatch")
    hashes = context["wrapper_fc_er_che_schema_hashes"]
    expected_hashes = {
        "wrapper": sha256_path(repository_root / WRAPPER),
        "fc_fk_adapter": FK_ADAPTER_SHA256,
        "er_harness": "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89",
        "canonical_che": "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
        "raw_evidence_schema": "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        "canonicalizer": CANONICALIZER_SHA256,
        "cloud_init": CLOUD_INIT_SHA256,
    }
    if hashes != expected_hashes:
        raise RuntimeError("context immutable wrapper/FC/ER/CHE/schema binding mismatch")
    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    checkout_path = bindings["checkout"]["path"]
    lifecycle = fresh_context.checkout_lifecycle_binding(context)
    if lifecycle == fresh_context.LEGACY_FIXED_CHECKOUT_LIFECYCLE:
        if checkout_path != CHECKOUT:
            raise RuntimeError("historical context checkout lifecycle binding mismatch")
    elif checkout_path != str(Path(context["transient_root"]) / "checkout"):
        raise RuntimeError("operation-scoped context checkout lifecycle binding mismatch")
    expected_bindings = {
        "qemu_executable": {"path": "/usr/bin/qemu-system-x86_64", "sha256": QEMU_EXECUTABLE_SHA256},
        "base": {"path": BASE_IMAGE, "sha256": EXPECTED_ASSET_SHA256[BASE_IMAGE]},
        "seed": {"path": SEED, "sha256": EXPECTED_ASSET_SHA256[SEED]},
        "checkout": {
            "path": checkout_path,
            "head": CHECKOUT_HEAD,
            "tree": CHECKOUT_TREE,
            "detached": True,
            "clean": True,
            "read_only_mount": True,
        },
    }
    if bindings != expected_bindings:
        raise RuntimeError("context immutable QEMU/base/seed/checkout binding mismatch")


def observe_context_assets(
    repository_root: Path,
    context: dict[str, Any],
    candidate_source_path: Path | None = None,
) -> dict[str, str]:
    candidate_relative, _ = resolve_candidate_source(
        repository_root, candidate_source_path
    )
    observations: dict[str, str] = {}
    for path in context_asset_expectations(context, Path(candidate_relative)):
        target = Path(path) if Path(path).is_absolute() else repository_root / path
        observations[path] = sha256_path(target)
    return observations


def authority_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def build_authority_handoff(authorization: dict[str, Any]) -> dict[str, Any]:
    """Build the one canonical envelope shape without granting authority."""

    if not isinstance(authorization, dict) or set(authorization) != AUTHORIZATION_FIELDS:
        raise RuntimeError("required execution authority field malformed, missing, or unknown")
    envelope = {
        "schema_id": AUTHORITY_SCHEMA,
        "authorization": authorization,
        "authorization_sha256": authority_sha256(authorization),
    }
    validate_authority_handoff_envelope_shape(envelope)
    return envelope


def validate_authority_handoff_envelope_shape(value: dict[str, Any]) -> None:
    """Validate exact envelope/schema/inner-seal structure, not Human semantics."""

    if set(value) != {"schema_id", "authorization", "authorization_sha256"}:
        raise RuntimeError("execution authority envelope fields malformed or unknown")
    if value.get("schema_id") != AUTHORITY_SCHEMA:
        raise RuntimeError("execution authority envelope schema mismatch")
    authorization = value.get("authorization")
    if not isinstance(authorization, dict) or set(authorization) != AUTHORIZATION_FIELDS:
        raise RuntimeError("required execution authority field malformed, missing, or unknown")
    if value.get("authorization_sha256") != authority_sha256(authorization):
        raise RuntimeError("execution authority inner seal mismatch")


def parse_authority_handoff_bytes(raw: bytes) -> dict[str, Any]:
    """Accept exactly unique-key canonical compact JSON plus one LF."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise RuntimeError("execution authority handoff contains duplicate JSON keys")
            value[key] = item
        return value

    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("execution authority handoff malformed") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError("execution authority handoff is not unique-key canonical JSON")
    validate_authority_handoff_envelope_shape(value)
    return value


def canonical_authority_handoff_bytes(
    authorization: dict[str, Any],
) -> bytes:
    """Serialize one authority object exactly as the strict loader requires."""

    envelope = build_authority_handoff(authorization)
    payload = canonical_bytes(envelope)
    if parse_authority_handoff_bytes(payload) != envelope:
        raise RuntimeError("authority handoff producer/loader semantic mismatch")
    return payload


def write_authority_handoff(
    path: Path,
    authorization: dict[str, Any],
) -> dict[str, Any]:
    """Persist one envelope through the existing canonical atomic writer."""

    envelope = build_authority_handoff(authorization)
    expected = canonical_authority_handoff_bytes(authorization)
    file_sha256 = write_atomic(path, envelope)
    loaded, loaded_sha256 = load_authority(path)
    if path.read_bytes() != expected or loaded != envelope or loaded_sha256 != file_sha256:
        raise RuntimeError("authority handoff persistence/loader equivalence mismatch")
    return {
        "authority_file_sha256": file_sha256,
        "authority_inner_sha256": envelope["authorization_sha256"],
        "canonical_byte_count": len(expected),
    }


def preauthority_serialization_fixture(
    context: dict[str, Any],
    *,
    request_sha256: str = "a" * 64,
    checkpoint_sha256: str = "b" * 64,
) -> dict[str, Any]:
    """Create deterministic test-only semantics that can never be authority."""

    if not HEX_64.fullmatch(request_sha256) or not HEX_64.fullmatch(checkpoint_sha256):
        raise RuntimeError("preauthority request/checkpoint fixture binding malformed")
    fixture_source = {
        "fixture_classification": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "request_sha256": request_sha256,
        "checkpoint_sha256": checkpoint_sha256,
        "context_sha256": context["context_sha256"],
        "generation_identity": context["generation_identity"],
        "operation_identity": context["operation_identity"],
        "repository_head": context["repository_head"],
        "repository_tree": context["repository_tree"],
        "candidate_sha256": context["candidate_manifest_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
    }
    return {
        "schema_id": AUTHORIZATION_SCHEMA,
        "authorization_present": False,
        "authorization_kind": "TEST_ONLY_NON_AUTHORITY_SERIALIZATION_FIXTURE",
        "authorization_source_sha256": hashlib.sha256(
            canonical_bytes(fixture_source)
        ).hexdigest(),
        "authorized_context_sha256": context["context_sha256"],
        "authorized_operation_identity": context["operation_identity"],
        "authorized_generation_identity": context["generation_identity"],
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_repository_head": context["repository_head"],
        "authorized_repository_tree": context["repository_tree"],
        "authorized_constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
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


def validate_preauthority_serialization_fixture(
    context: dict[str, Any],
    authorization: dict[str, Any],
    *,
    request_sha256: str = "a" * 64,
    checkpoint_sha256: str = "b" * 64,
) -> None:
    """Reject any test-only semantic binding drift before Human authority."""

    expected = preauthority_serialization_fixture(
        context,
        request_sha256=request_sha256,
        checkpoint_sha256=checkpoint_sha256,
    )
    if authorization != expected:
        raise RuntimeError("preauthority authority serialization fixture binding mismatch")


def prove_authority_handoff_canonicalization(
    context: dict[str, Any],
) -> dict[str, Any]:
    """Prove producer/loader byte equivalence without creating authority."""

    authorization = preauthority_serialization_fixture(context)
    validate_preauthority_serialization_fixture(context, authorization)
    envelope = build_authority_handoff(authorization)
    first = canonical_authority_handoff_bytes(authorization)
    second = canonical_authority_handoff_bytes(authorization)
    parsed = parse_authority_handoff_bytes(first)
    if first != second or parsed != envelope:
        raise RuntimeError("preauthority authority handoff proof is nondeterministic")
    pretty = (json.dumps(envelope, sort_keys=True, indent=2) + "\n").encode()
    try:
        parse_authority_handoff_bytes(pretty)
    except RuntimeError:
        pretty_rejected = True
    else:
        pretty_rejected = False
    if not pretty_rejected:
        raise RuntimeError("pretty authority envelope unexpectedly accepted")
    return {
        "result": "PREAUTHORITY_CANONICAL_AUTHORITY_HANDOFF_PROOF_PASS",
        "fixture_classification": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "canonical_authority_handoff_serializer_identity": "VERIFIED",
        "canonical_authority_envelope_schema": "VERIFIED",
        "canonical_authority_handoff_template": "VERIFIED",
        "canonicalization_algorithm": "SORTED_COMPACT_JSON_PLUS_LF",
        "unique_key_json_requirement": "VERIFIED",
        "canonical_compact_json_plus_lf_requirement": "VERIFIED",
        "loader_producer_canonicalization_equivalence": "VERIFIED",
        "no_pretty_print_reencoding_path": "VERIFIED",
        "no_second_serializer_path": "VERIFIED",
        "producer_output_sha256": hashlib.sha256(first).hexdigest(),
        "loader_expectation_sha256": hashlib.sha256(canonical_bytes(parsed)).hexdigest(),
        "semantic_envelope_sha256": hashlib.sha256(canonical_bytes(envelope)).hexdigest(),
        "deterministic_repeat_sha256": hashlib.sha256(second).hexdigest(),
        "canonical_byte_count": len(first),
        "human_operational_authorization_count": 0,
        "qemu_execution_count": 0,
    }


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
    context: dict[str, Any],
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
    candidate_source_path: Path | None = None,
) -> dict[str, str]:
    """Pure fail-closed admission; it performs no writes or process execution."""

    if context["repository_head"] != observed_head or context["repository_tree"] != observed_tree:
        raise RuntimeError("operation context repository binding differs from observed state")

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
        "authorized_context_sha256": context["context_sha256"],
        "authorized_generation_identity": context["generation_identity"],
        "authorized_operation_identity": context["operation_identity"],
        "authorized_vector": "WRONG_ATTEMPT",
        "authorized_constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
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
    expected_assets = context_asset_expectations(context, candidate_source_path)
    if set(observed_asset_sha256) != set(expected_assets):
        raise RuntimeError("asset observation set incomplete or unknown")
    for path, expected_sha in expected_assets.items():
        if observed_asset_sha256[path] != expected_sha:
            raise RuntimeError(f"exact asset binding mismatch: {path}")
    if canonical_argv_sha256 != context["canonical_argv_sha256"]:
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
    context: dict[str, Any],
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
    candidate_source_path: Path | None = None,
) -> dict[str, str]:
    """FO final admission extended by the existing FM preboot composition gate."""

    static_readiness = authority_free_static_readiness(
        repository_root=repository_root,
        context=context,
        observed_head=observed_head,
        observed_tree=observed_tree,
        repository_clean=repository_clean,
        observed_asset_sha256=observed_asset_sha256,
        candidate_source_path=candidate_source_path,
    )
    receipt_readiness = validate_receipt_parent_ready(repository_root, context)
    visibility = validate_preboot_visibility(
        repository_root,
        context,
        argv,
        canonical_argv_sha256,
        candidate_source_path=candidate_source_path,
    )
    admission = validate_execution_admission(
        context=context,
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
        candidate_source_path=candidate_source_path,
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
        "authority_free_static_readiness_sha256": static_readiness["readiness_sha256"],
    })
    return admission


def asset_observations(repository_root: Path) -> dict[str, str]:
    observations: dict[str, str] = {}
    for path in EXPECTED_ASSET_SHA256:
        target = Path(path) if Path(path).is_absolute() else repository_root / path
        observations[path] = sha256_path(target)
    return observations


def build_operation_context(
    *,
    repository_root: Path,
    repository_head: str,
    repository_tree: str,
    generation_identity: str,
    operation_identity: str,
    identity_namespace_prefix: str,
    operation_evidence_root: Path,
    transient_root: Path,
    candidate_source_path: Path | None = None,
) -> dict[str, Any]:
    """Build and seal one context before any Human authorization can exist."""

    hashes = {
        "wrapper": sha256_path(repository_root / WRAPPER),
        "fc_fk_adapter": FK_ADAPTER_SHA256,
        "er_harness": "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89",
        "canonical_che": "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
        "raw_evidence_schema": "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        "canonicalizer": CANONICALIZER_SHA256,
        "cloud_init": CLOUD_INIT_SHA256,
    }
    checkout_path = transient_root.absolute() / "checkout"
    bindings = {
        "qemu_executable": {"path": "/usr/bin/qemu-system-x86_64", "sha256": QEMU_EXECUTABLE_SHA256},
        "base": {"path": BASE_IMAGE, "sha256": EXPECTED_ASSET_SHA256[BASE_IMAGE]},
        "seed": {"path": SEED, "sha256": EXPECTED_ASSET_SHA256[SEED]},
        "checkout": {
            "path": str(checkout_path),
            "head": CHECKOUT_HEAD,
            "tree": CHECKOUT_TREE,
            "detached": True,
            "clean": True,
            "read_only_mount": True,
        },
    }
    _, candidate = resolve_candidate_source(repository_root, candidate_source_path)
    return fresh_context.build_context(
        repository_root=repository_root,
        repository_head=repository_head,
        repository_tree=repository_tree,
        generation_identity=generation_identity,
        operation_identity=operation_identity,
        identity_namespace_prefix=identity_namespace_prefix,
        operation_evidence_root=operation_evidence_root,
        transient_root=transient_root,
        candidate_manifest_sha256=sha256_path(candidate),
        wrapper_fc_er_che_schema_hashes=hashes,
        qemu_executable_base_seed_checkout_bindings=bindings,
    )


def preauth_fresh_checkout_destination_readiness(
    repository_root: Path,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Prove the new checkout belongs to one unused transient lifecycle.

    Destination absence is necessary but not independently sufficient. The
    exact context must use the current operation-scoped checkout binding, both
    mutable roots must be absent, and no exact Human authority source or
    canonical handoff may exist for the generation.
    """

    fresh_context.validate_context(context, repository_root=repository_root)
    operation_root = Path(context["operation_evidence_root"])
    transient_root = Path(context["transient_root"])
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    lifecycle = fresh_context.checkout_lifecycle_binding(context)
    if lifecycle != fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE:
        raise RuntimeError(
            "legacy checkout destination requires terminal lifecycle review"
        )
    if checkout.exists() or checkout.is_symlink():
        raise RuntimeError("fresh checkout destination collision")
    if transient_root.exists() or transient_root.is_symlink():
        raise RuntimeError("active or incomplete transient checkout lifecycle")
    if operation_root.exists() or operation_root.is_symlink():
        raise RuntimeError("active or incomplete operation dependency")
    evidence_root = operation_root.parent
    prefix = context["identity_namespace_prefix"]
    authority_paths = (
        evidence_root / f"{prefix}_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        evidence_root
        / f"{prefix}_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
    )
    if any(path.exists() or path.is_symlink() for path in authority_paths):
        raise RuntimeError("live authority dependency blocks checkout preparation")
    return {
        "result": "PREAUTH_FRESH_CHECKOUT_DESTINATION_READINESS_PASS",
        "property": (
            "EXACT_OPERATION_SCOPED_DESTINATION_BOUND"
            "_AND_PREVIOUS_CHECKOUT_LIFECYCLE_NOT_APPLICABLE_TO_UNIQUE_PATH"
            "_AND_REQUIRED_PERMANENT_EVIDENCE_OUTSIDE_TRANSIENT_ROOT"
            "_AND_NO_ACTIVE_OPERATION_DEPENDENCY"
            "_AND_NO_LIVE_AUTHORITY_DEPENDENCY"
            "_AND_EXISTING_SPCE_TRANSIENT_ROOT_TEARDOWN_OWNER_BOUND"
            "_AND_DESTINATION_ABSENT_BEFORE_FRESH_MATERIALIZATION"
        ),
        "checkout_path": str(checkout),
        "transient_root": str(transient_root),
        "operation_evidence_root": str(operation_root),
        "previous_checkout_lifecycle_terminal": (
            "NOT_APPLICABLE__UNIQUE_OPERATION_SCOPED_DESTINATION"
        ),
        "required_permanent_evidence_preserved": True,
        "no_active_operation_dependency": True,
        "no_live_authority_dependency": True,
        "retirement_or_preparation_owner": (
            "EXISTING_SPCE_HOST_TEARDOWN_EXACT_TRANSIENT_ROOT_OWNER"
        ),
        "destination_absent": True,
        "destination_absence_alone_sufficient": False,
        "human_operational_authorization_count": 0,
        "qemu_execution_count": 0,
    }


def materialize_operation_state(
    *,
    repository_root: Path,
    context: dict[str, Any],
    context_source_path: Path,
    candidate_source_path: Path | None = None,
) -> dict[str, Any]:
    """Explicit authority-free materialization; never called by governed main()."""

    validate_immutable_context_bindings(
        repository_root, context, candidate_source_path
    )
    fresh_context.validate_freshness(context)
    operation_scoped_checkout = (
        fresh_context.checkout_lifecycle_binding(context)
        == fresh_context.OPERATION_SCOPED_CHECKOUT_LIFECYCLE
    )
    operation_root = Path(context["operation_evidence_root"])
    transient_root = Path(context["transient_root"])
    runtime_export = Path(context["runtime_export_root"])
    for root in (operation_root, transient_root):
        if root.exists() or root.is_symlink():
            raise RuntimeError(f"fresh materialization root collision: {root}")
        if root.parent.is_symlink() or not root.parent.is_dir():
            raise RuntimeError(f"fresh materialization parent absent or unsafe: {root.parent}")
    if operation_scoped_checkout:
        preauth_fresh_checkout_destination_readiness(repository_root, context)
    checkout_binding = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    checkout_materialization = materialize_guest_self_contained_checkout(
        source_repository=repository_root,
        checkout_path=Path(checkout_binding["path"]),
        expected_head=checkout_binding["head"],
        expected_tree=checkout_binding["tree"],
    )
    operation_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    if operation_scoped_checkout:
        if transient_root.is_symlink() or not transient_root.is_dir():
            raise RuntimeError("checkout materializer did not create the transient root")
        if set(transient_root.iterdir()) != {Path(checkout_binding["path"])}:
            raise RuntimeError("transient root contains state outside checkout lifecycle")
    else:
        transient_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    runtime_export.mkdir(mode=0o700, parents=False, exist_ok=False)
    adapter_binding = context["guest_adapter_binding"]
    adapter_projection_root = Path(adapter_binding["projection_root"])
    adapter_projection_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    adapter_source = repository_root / adapter_binding["source_path"]
    adapter_bytes = adapter_source.read_bytes()
    Path(adapter_binding["projected_path"]).write_bytes(adapter_bytes)
    Path(adapter_binding["bootstrap_projected_path"]).write_bytes(adapter_bytes)
    _, candidate = resolve_candidate_source(repository_root, candidate_source_path)
    runtime_manifest = Path(context["runtime_manifest_path"])
    runtime_manifest.write_bytes(candidate.read_bytes())
    context_projection = runtime_export / fresh_context.GUEST_CONTEXT_FILENAME
    context_projection.write_bytes(context_source_path.read_bytes())
    overlay = Path(context["overlay_path"])
    subprocess.run(
        [
            "qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
            "-b", BASE_IMAGE, str(overlay),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if overlay.is_symlink() or not overlay.is_file():
        raise RuntimeError("fresh overlay materialization failed")
    return {
        "result": "FRESH_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU",
        "operation_evidence_root": str(operation_root),
        "transient_root": str(transient_root),
        "runtime_manifest_sha256": sha256_path(runtime_manifest),
        "context_projection_sha256": sha256_path(context_projection),
        "adapter_projection_sha256": sha256_path(
            Path(adapter_binding["projected_path"])
        ),
        "checkout_materialization": checkout_materialization,
        "overlay_materialized": True,
        "qemu_execution_count": 0,
    }


def _materialized_checkout_observation(
    checkout: Path, expected_head: str, expected_tree: str
) -> dict[str, Any]:
    """Reobserve one direct, detached, object-localized checkout."""

    gitdir, representation = _git_directory_from_presentation_root(checkout)
    if representation != "DIRECTORY":
        raise RuntimeError("materialized checkout must use a direct Git directory")
    common_dir = _git_common_directory(checkout, gitdir)
    if common_dir != gitdir:
        raise RuntimeError("materialized checkout common-dir must be local and direct")
    _reject_git_metadata_symlink_escape(checkout, gitdir, common_dir)
    object_directories = _reachable_object_directories(checkout, common_dir / "objects")
    if object_directories != (common_dir / "objects",):
        raise RuntimeError("materialized checkout must use one local object database")
    observed_head = _er_consumer_git(checkout, "rev-parse", "HEAD")
    observed_tree = _er_consumer_git(checkout, "rev-parse", "HEAD^{tree}")
    if observed_head != expected_head:
        raise RuntimeError("materialized checkout resolved wrong HEAD")
    if observed_tree != expected_tree:
        raise RuntimeError("materialized checkout resolved wrong TREE")
    if _er_consumer_git(checkout, "cat-file", "-t", observed_head) != "commit":
        raise RuntimeError("materialized checkout commit object is unreachable")
    if _er_consumer_git(checkout, "cat-file", "-t", observed_tree) != "tree":
        raise RuntimeError("materialized checkout tree object is unreachable")
    if _er_consumer_git(checkout, "status", "--porcelain"):
        raise RuntimeError("materialized checkout is stale or dirty")
    try:
        _er_consumer_git(checkout, "symbolic-ref", "-q", "HEAD")
    except RuntimeError:
        detached = True
    else:
        detached = False
    if not detached:
        raise RuntimeError("materialized checkout HEAD is not detached")
    return {
        "result": "GUEST_SELF_CONTAINED_CHECKOUT_MATERIALIZATION_PASS",
        "checkout_path": str(checkout),
        "expected_head": expected_head,
        "observed_head": observed_head,
        "expected_tree": expected_tree,
        "observed_tree": observed_tree,
        "git_representation": "DIRECT_GIT_DIRECTORY",
        "common_dir": str(common_dir),
        "object_database": str(object_directories[0]),
        "external_git_metadata_dependency": False,
        "external_object_database_dependency": False,
        "detached": True,
        "clean": True,
    }


def materialize_guest_self_contained_checkout(
    *,
    source_repository: Path,
    checkout_path: Path,
    expected_head: str,
    expected_tree: str,
) -> dict[str, Any]:
    """Atomically create the existing FM checkout with no borrowed Git state."""

    source = source_repository.resolve(strict=True)
    if source_repository.absolute() != source or not source.is_dir():
        raise RuntimeError("checkout source repository is not canonical")
    if not HEX_40.fullmatch(expected_head) or not HEX_40.fullmatch(expected_tree):
        raise RuntimeError("checkout expected HEAD/TREE malformed")
    if checkout_path != checkout_path.absolute():
        raise RuntimeError("checkout destination must be absolute")
    supplied_parent = checkout_path.parent
    parent_created = False
    if supplied_parent.exists() or supplied_parent.is_symlink():
        parent = supplied_parent.resolve(strict=True)
        if supplied_parent.absolute() != parent or not parent.is_dir():
            raise RuntimeError("checkout destination parent is not canonical")
        staging_parent = parent
    else:
        grandparent = supplied_parent.parent.resolve(strict=True)
        if (
            supplied_parent.parent.absolute() != grandparent
            or not grandparent.is_dir()
            or supplied_parent.absolute() != grandparent / supplied_parent.name
        ):
            raise RuntimeError("checkout destination parent is not canonical")
        parent = supplied_parent.absolute()
        staging_parent = grandparent
    destination = parent / checkout_path.name
    if destination.exists() or destination.is_symlink():
        raise RuntimeError("fresh checkout destination collision")

    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith("GIT_"):
            environment.pop(name)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull

    source_head = subprocess.run(
        ["git", "rev-parse", f"{expected_head}^{{commit}}"],
        cwd=source,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        env=environment,
    ).stdout.strip()
    source_tree = subprocess.run(
        ["git", "rev-parse", f"{expected_head}^{{tree}}"],
        cwd=source,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        env=environment,
    ).stdout.strip()
    if source_head != expected_head or source_tree != expected_tree:
        raise RuntimeError("checkout source does not resolve exact expected HEAD/TREE")

    with tempfile.TemporaryDirectory(
        dir=staging_parent, prefix=f".{destination.name}.g77_256gq_"
    ) as temporary:
        staged = Path(temporary) / "checkout"
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-local",
                "--no-checkout",
                "--",
                str(source),
                str(staged),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=300,
            env=environment,
        )
        subprocess.run(
            ["git", "checkout", "--quiet", "--detach", expected_head],
            cwd=staged,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=300,
            env=environment,
        )
        _materialized_checkout_observation(staged, expected_head, expected_tree)
        if not parent.exists():
            parent.mkdir(mode=0o700, parents=False, exist_ok=False)
            parent_created = True
        try:
            os.replace(staged, destination)
        except BaseException:
            if parent_created:
                parent.rmdir()
            raise

    return _materialized_checkout_observation(
        destination, expected_head, expected_tree
    )


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _canonical_internal_path(root: Path, candidate: Path, label: str) -> Path:
    try:
        resolved = candidate.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as exc:
        raise RuntimeError(f"checkout {label} is unreachable") from exc
    if not _inside(root, resolved):
        raise RuntimeError(f"checkout {label} escapes presentation root")
    if candidate.absolute() != resolved:
        raise RuntimeError(f"checkout {label} uses symlink indirection")
    return resolved


def _git_directory_from_presentation_root(root: Path) -> tuple[Path, str]:
    marker = root / ".git"
    if marker.is_symlink() or not marker.exists():
        raise RuntimeError("checkout .git missing or symlinked")
    if marker.is_dir():
        return _canonical_internal_path(root, marker, "gitdir"), "DIRECTORY"
    if not marker.is_file():
        raise RuntimeError("checkout .git is neither a directory nor a gitfile")
    try:
        text = marker.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError("checkout gitfile is unreadable or malformed") from exc
    lines = text.splitlines()
    if len(lines) != 1 or not lines[0].startswith("gitdir: "):
        raise RuntimeError("checkout gitfile is malformed")
    supplied = Path(lines[0][len("gitdir: "):])
    target = supplied if supplied.is_absolute() else marker.parent / supplied
    return _canonical_internal_path(root, target, "gitdir"), "GITFILE"


def _git_common_directory(root: Path, gitdir: Path) -> Path:
    marker = gitdir / "commondir"
    if not marker.exists():
        return gitdir
    if marker.is_symlink() or not marker.is_file():
        raise RuntimeError("checkout common-dir marker is unsafe")
    try:
        lines = marker.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError("checkout common-dir marker is unreadable") from exc
    if len(lines) != 1 or not lines[0]:
        raise RuntimeError("checkout common-dir marker is malformed")
    supplied = Path(lines[0])
    target = supplied if supplied.is_absolute() else gitdir / supplied
    return _canonical_internal_path(root, target, "common-dir")


def _reachable_object_directories(root: Path, primary: Path) -> tuple[Path, ...]:
    observed: list[Path] = []

    def observe(target: Path) -> None:
        object_directory = _canonical_internal_path(root, target, "object database")
        if object_directory in observed:
            return
        if not object_directory.is_dir() or not os.access(
            object_directory, os.R_OK | os.X_OK
        ):
            raise RuntimeError("checkout object database is unreadable")
        observed.append(object_directory)
        info = object_directory / "info"
        http_alternates = info / "http-alternates"
        if http_alternates.exists():
            raise RuntimeError("checkout HTTP object alternates are not guest-local")
        alternates = info / "alternates"
        if not alternates.exists():
            return
        if alternates.is_symlink() or not alternates.is_file():
            raise RuntimeError("checkout object alternates metadata is unsafe")
        try:
            lines = alternates.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            raise RuntimeError("checkout object alternates metadata is unreadable") from exc
        if not lines or any(not line or "\x00" in line for line in lines):
            raise RuntimeError("checkout object alternates metadata is malformed")
        for line in lines:
            supplied = Path(line)
            target = supplied if supplied.is_absolute() else object_directory / supplied
            resolved = target.resolve(strict=False)
            if not _inside(root, resolved):
                raise RuntimeError(
                    "checkout object alternate escapes presentation root"
                )
            observe(target)

    observe(primary)
    return tuple(observed)


def _reject_git_metadata_symlink_escape(
    root: Path, gitdir: Path, common_dir: Path
) -> None:
    for metadata_root in dict.fromkeys((gitdir, common_dir)):
        for directory, names, files in os.walk(metadata_root, followlinks=False):
            parent = Path(directory)
            for name in (*names, *files):
                path = parent / name
                if path.is_symlink():
                    raise RuntimeError("checkout Git metadata symlink prohibited")
                if not _inside(root, path.resolve(strict=True)):
                    raise RuntimeError("checkout Git metadata escapes presentation root")


def _er_consumer_git(checkout: Path, *arguments: str) -> str:
    environment = os.environ.copy()
    for name in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_INDEX_FILE",
    ):
        environment.pop(name, None)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    try:
        result = subprocess.run(
            ["git", "-c", f"safe.directory={checkout}", *arguments],
            cwd=checkout,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            env=environment,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or f"exit status {exc.returncode}"
        raise RuntimeError(f"ER guest Git consumer rejected checkout: {detail}") from exc
    return result.stdout.strip()


def _validate_guest_destination_sources(
    cloud_init_source: str, er_source: str
) -> None:
    mount = (
        "mount -t 9p -o trans=virtio,version=9p2000.L,ro "
        f"{GUEST_CHECKOUT_MOUNT_TAG} {GUEST_CHECKOUT_DESTINATION}"
    )
    if cloud_init_source.count(mount) != 1:
        raise RuntimeError("checkout guest destination mount binding mismatch")
    required_er_fragments = (
        f'CHECKOUT = Path("{GUEST_CHECKOUT_DESTINATION}")',
        '["git", "-c", f"safe.directory={CHECKOUT}", *args]',
        'cwd=CHECKOUT,',
        '"observed_head": run_git("rev-parse", "HEAD")',
        '"observed_tree": run_git("rev-parse", "HEAD^{tree}")',
    )
    if any(er_source.count(fragment) != 1 for fragment in required_er_fragments):
        raise RuntimeError("ER checkout consumer semantics binding mismatch")


def _guest_destination_contract() -> dict[str, str]:
    repository_root = Path(__file__).resolve().parents[5]
    cloud_init = repository_root / CLOUD_INIT
    er_harness = repository_root / ER_HARNESS_RELATIVE
    if sha256_path(cloud_init) != CLOUD_INIT_SHA256:
        raise RuntimeError("checkout cloud-init mount source identity mismatch")
    if sha256_path(er_harness) != ER_HARNESS_SHA256:
        raise RuntimeError("ER checkout consumer source identity mismatch")
    cloud_source = cloud_init.read_text(encoding="utf-8")
    er_source = er_harness.read_text(encoding="utf-8")
    _validate_guest_destination_sources(cloud_source, er_source)
    return {
        "cloud_init_sha256": CLOUD_INIT_SHA256,
        "er_harness_sha256": ER_HARNESS_SHA256,
        "mount_tag": GUEST_CHECKOUT_MOUNT_TAG,
        "guest_destination": GUEST_CHECKOUT_DESTINATION,
    }


def prove_guest_checkout_tree_precondition(
    context: dict[str, Any],
) -> dict[str, Any]:
    """Prove ER's Git HEAD/tree precondition using only the exported root."""

    forbidden_overrides = {
        "guest_checkout_ready",
        "preauth_guest_checkout_tree_authentication",
        "guest_checkout_destination",
    }
    if forbidden_overrides & context.keys():
        raise RuntimeError("caller-supplied guest checkout readiness override prohibited")
    destination_contract = _guest_destination_contract()
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    root = Path(checkout["path"])
    if root.absolute() != root.resolve(strict=True):
        raise RuntimeError("checkout presentation root is not canonical")
    expected_argument = (
        f"local,path={root},mount_tag={GUEST_CHECKOUT_MOUNT_TAG},"
        "security_model=none,readonly=on"
    )
    arguments = [
        context["canonical_argv"][index + 1]
        for index, value in enumerate(context["canonical_argv"][:-1])
        if value == "-virtfs"
        and f"mount_tag={GUEST_CHECKOUT_MOUNT_TAG}" in context["canonical_argv"][index + 1]
    ]
    if arguments != [expected_argument]:
        raise RuntimeError("checkout presentation binding mismatch")

    gitdir, git_representation = _git_directory_from_presentation_root(root)
    common_dir = _git_common_directory(root, gitdir)
    _reject_git_metadata_symlink_escape(root, gitdir, common_dir)
    head_path = gitdir / "HEAD"
    if head_path.is_symlink() or not head_path.is_file() or not os.access(
        head_path, os.R_OK
    ):
        raise RuntimeError("checkout HEAD is missing or unreadable")
    object_directories = _reachable_object_directories(root, common_dir / "objects")

    observed_head = _er_consumer_git(root, "rev-parse", "HEAD")
    observed_tree = _er_consumer_git(root, "rev-parse", "HEAD^{tree}")
    if observed_head != checkout["head"]:
        raise RuntimeError("checkout ER consumer resolved wrong HEAD")
    if observed_tree != checkout["tree"]:
        raise RuntimeError("checkout ER consumer resolved wrong TREE")
    if _er_consumer_git(root, "cat-file", "-t", observed_tree) != "tree":
        raise RuntimeError("checkout expected tree object is unreachable")
    if _er_consumer_git(root, "status", "--porcelain") != "":
        raise RuntimeError("checkout ER consumer observed stale or dirty checkout")
    return {
        "result": "PREAUTH_GUEST_CHECKOUT_TREE_AUTHENTICATION_PASS",
        "expected_head": checkout["head"],
        "observed_head": observed_head,
        "expected_tree": checkout["tree"],
        "observed_tree": observed_tree,
        "host_checkout_source_identity": str(root),
        "host_gitdir_identity": str(gitdir),
        "host_common_dir_identity": str(common_dir),
        "required_git_metadata": "GITDIR_COMMON_DIR_HEAD_REFS_OBJECT_DATABASE",
        "required_object_reachability": "GUEST_LOCAL_ONLY",
        "reachable_object_directories": [str(path) for path in object_directories],
        "presentation_root": str(root),
        "presentation_mechanism": "QEMU_VIRTFS_LOCAL_9P_READ_ONLY",
        "qemu_virtfs_argument": expected_argument,
        "guest_destination": GUEST_CHECKOUT_DESTINATION,
        "guest_destination_contract": destination_contract,
        "er_consumer_semantics": (
            "git -c safe.directory=/mnt/aigol rev-parse HEAD and HEAD^{tree}"
        ),
        "git_representation": git_representation,
        "caller_supplied_readiness_override": False,
    }


def validate_checkout_preboot_readiness(context: dict[str, Any]) -> dict[str, Any]:
    checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    path = Path(checkout["path"])
    if path.is_symlink() or not path.is_dir():
        raise RuntimeError("checkout missing or symlink redirected")
    if git(path, "rev-parse", "HEAD") != checkout["head"]:
        raise RuntimeError("checkout wrong HEAD")
    if git(path, "rev-parse", "HEAD^{tree}") != checkout["tree"]:
        raise RuntimeError("checkout wrong TREE")
    if git(path, "status", "--porcelain") != "":
        raise RuntimeError("checkout dirty")
    try:
        git(path, "symbolic-ref", "-q", "HEAD")
    except subprocess.CalledProcessError:
        detached = True
    else:
        detached = False
    if detached is not checkout["detached"]:
        raise RuntimeError("checkout detached-mode mismatch")
    mount_argument = next(
        (
            context["canonical_argv"][index + 1]
            for index, value in enumerate(context["canonical_argv"][:-1])
            if value == "-virtfs"
            and "mount_tag=aigol_checkout" in context["canonical_argv"][index + 1]
        ),
        None,
    )
    if not checkout["read_only_mount"] or mount_argument is None or "readonly=on" not in mount_argument:
        raise RuntimeError("checkout read-only certified mount contract missing")
    guest_tree_proof = prove_guest_checkout_tree_precondition(context)
    return {
        "checkout_exists": "PASS",
        "checkout_head_tree": "PASS",
        "checkout_clean_detached": "PASS",
        "checkout_read_only_mount": "PASS",
        "preauth_guest_checkout_tree_authentication": guest_tree_proof,
    }


def authority_free_static_readiness(
    *,
    repository_root: Path,
    context: dict[str, Any],
    observed_head: str,
    observed_tree: str,
    repository_clean: bool,
    observed_asset_sha256: dict[str, str],
    candidate_source_path: Path | None = None,
) -> dict[str, Any]:
    """Complete static determination with zero Human authorization objects."""

    validate_immutable_context_bindings(
        repository_root, context, candidate_source_path
    )
    if context["repository_head"] != observed_head or context["repository_tree"] != observed_tree:
        raise RuntimeError("static readiness repository HEAD/TREE mismatch")
    if not repository_clean:
        raise RuntimeError("static readiness repository is dirty")
    if not constitutional_anchor_is_ancestor(repository_root):
        raise RuntimeError("constitutional anchor is not ancestral")
    nested = repository_root / "sapianta_system"
    if (
        git(nested, "rev-parse", "HEAD") != "3183bab71f8f30397c0309dd2e6d846d14a11f66"
        or git(nested, "rev-parse", "HEAD^{tree}") != "7c32ec05efc2be43297849bc38ec8766514a523d"
        or git(nested, "status", "--porcelain") != ""
    ):
        raise RuntimeError("nested immutable authority mismatch")
    candidate_relative, _ = resolve_candidate_source(
        repository_root, candidate_source_path
    )
    expected_assets = context_asset_expectations(context, Path(candidate_relative))
    if observed_asset_sha256 != expected_assets:
        raise RuntimeError("authority-free immutable asset or candidate binding mismatch")
    overlay = Path(context["overlay_path"])
    if overlay.is_symlink() or not overlay.is_file():
        raise RuntimeError("fresh overlay readiness absent")
    freshness = fresh_context.validate_freshness(context, overlay_materialized=True)
    visibility = validate_preboot_visibility(
        repository_root,
        context,
        context["canonical_argv"],
        context["canonical_argv_sha256"],
        candidate_source_path=Path(candidate_relative),
    )
    checkout = validate_checkout_preboot_readiness(context)
    adapter = prove_guest_adapter_binding(repository_root, context)
    authority_handoff = prove_authority_handoff_canonicalization(context)
    reduction = {
        "result": "STATIC_READINESS_PASS",
        "phase": "AUTHORITY_FREE_STATIC_READINESS",
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "human_operational_authorization_count": 0,
        "qemu_execution_count": 0,
        "complete_freshness_closure": freshness,
        "preboot_visibility": visibility,
        "guest_adapter_binding": adapter,
        "authority_handoff_canonicalization": authority_handoff,
        "checkout_readiness": checkout,
        "one_launcher_route": True,
        "one_qemu_call_site": True,
        "automatic_retry_count": 0,
        "repair_count": 0,
        "replay_count": 0,
    }
    reduction["readiness_sha256"] = hashlib.sha256(canonical_bytes(reduction)).hexdigest()
    return reduction


def constitutional_anchor_is_ancestor(repository_root: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", CONSTITUTIONAL_ANCHOR_HEAD, "HEAD"],
        cwd=repository_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def receipt(*, context: dict[str, Any], phase: str, argv: list[str], digest: str, vector_sha256: str,
            executable_sha256: str, started_ns: int, completed_ns: int | None,
            exit_status: int | None, admission: dict[str, str]) -> dict[str, Any]:
    return {
        "schema_id": f"SAPIANTA_CONTEXT_BOUND_{phase}_EXECUTED_QEMU_ARGV_RECEIPT_V1",
        "generation_identity": context["generation_identity"],
        "operation_identity": context["operation_identity"],
        "identity_namespace_prefix": context["identity_namespace_prefix"],
        "context_sha256": context["context_sha256"],
        "authorized_repository_head": admission["authorized_repository_head"],
        "authorized_repository_tree": admission["authorized_repository_tree"],
        "constitutional_anchor_head": admission["constitutional_anchor_head"],
        "execution_authority_file_sha256": admission["execution_authority_file_sha256"],
        "human_authorization_source_sha256": admission["human_authorization_source_sha256"],
        "candidate_sha256": context["candidate_manifest_sha256"],
        "adapter_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
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
    parser.add_argument("--operation-context", required=True, type=Path)
    parser.add_argument("--operation-context-sha256", required=True)
    parser.add_argument("--live-candidate-binding", required=True, type=Path)
    parser.add_argument("--execution-authority", required=True, type=Path)
    parser.add_argument("--execution-authority-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    repository_root = Path.cwd().resolve()
    candidate_relative, _ = resolve_candidate_source(
        repository_root, arguments.live_candidate_binding
    )
    candidate_source_path = Path(candidate_relative)
    context_path = arguments.operation_context.resolve()
    if not HEX_64.fullmatch(arguments.operation_context_sha256):
        raise RuntimeError("supplied operation context hash malformed")
    if sha256_path(context_path) != arguments.operation_context_sha256:
        raise RuntimeError("operation context file hash mismatch")
    context = fresh_context.load_context(context_path, repository_root=repository_root)
    pre_path = Path(context["pre_receipt_path"])
    post_path = Path(context["post_receipt_path"])
    consumable_paths = receipt_consumable_paths(repository_root, context)
    argv = context["canonical_argv"]
    canonicalizer = load_canonicalizer(repository_root)
    digest = canonicalizer.argv_sha256(argv)
    vector_sha = hashlib.sha256(canonical_bytes(argv)).hexdigest()
    observed_head = git(repository_root, "rev-parse", "HEAD")
    observed_tree = git(repository_root, "rev-parse", "HEAD^{tree}")
    repository_clean = git(
        repository_root,
        "status",
        "--porcelain",
        "--untracked-files=no",
    ) == ""
    observed_assets = observe_context_assets(
        repository_root, context, candidate_source_path
    )
    authority_free_static_readiness(
        repository_root=repository_root,
        context=context,
        observed_head=observed_head,
        observed_tree=observed_tree,
        repository_clean=repository_clean,
        observed_asset_sha256=observed_assets,
        candidate_source_path=candidate_source_path,
    )
    authority, authority_file_sha = load_authority(arguments.execution_authority.resolve())

    # A later authority handoff cannot bridge stale preauthorization observations.
    # Reload the sealed context and independently re-observe every mutable static
    # input immediately before FO final admission and the PRE receipt boundary.
    if sha256_path(context_path) != arguments.operation_context_sha256:
        raise RuntimeError("operation context state drift after static readiness")
    final_context = fresh_context.load_context(
        context_path, repository_root=repository_root
    )
    if final_context != context:
        raise RuntimeError("operation context semantic drift after static readiness")
    final_observed_head = git(repository_root, "rev-parse", "HEAD")
    final_observed_tree = git(repository_root, "rev-parse", "HEAD^{tree}")
    final_repository_clean = git(
        repository_root,
        "status",
        "--porcelain",
        "--untracked-files=no",
    ) == ""
    final_observed_assets = observe_context_assets(
        repository_root, final_context, candidate_source_path
    )
    final_argv = final_context["canonical_argv"]
    final_digest = canonicalizer.argv_sha256(final_argv)
    if (
        final_observed_head != observed_head
        or final_observed_tree != observed_tree
        or final_repository_clean != repository_clean
        or final_observed_assets != observed_assets
        or final_argv != argv
        or final_digest != digest
    ):
        raise RuntimeError("authority-free state drift before final admission")
    admission = validate_final_admission(
        repository_root=repository_root,
        context=final_context,
        authority=authority,
        authority_file_sha256=authority_file_sha,
        supplied_authority_sha256=arguments.execution_authority_sha256,
        observed_head=final_observed_head,
        observed_tree=final_observed_tree,
        anchor_is_ancestor=constitutional_anchor_is_ancestor(repository_root),
        repository_clean=final_repository_clean,
        observed_asset_sha256=final_observed_assets,
        argv=final_argv,
        canonical_argv_sha256=final_digest,
        receipt_namespace_consumed=any(path.exists() for path in consumable_paths),
        candidate_source_path=candidate_source_path,
    )
    executable_sha = sha256_path(Path(argv[0]))
    started = time.time_ns()
    write_atomic(pre_path, receipt(
        context=context, phase="PRE", argv=argv, digest=digest, vector_sha256=vector_sha,
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
            context=context, phase="POST", argv=argv, digest=digest, vector_sha256=vector_sha,
            executable_sha256=executable_sha, started_ns=started,
            completed_ns=completed, exit_status=status, admission=admission,
        ))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
