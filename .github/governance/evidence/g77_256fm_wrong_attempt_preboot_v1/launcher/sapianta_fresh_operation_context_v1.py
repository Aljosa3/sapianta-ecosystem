#!/usr/bin/env python3
"""Canonical fresh-operation context owned by the existing FM execution route."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import struct
from typing import Any, Iterable


SCHEMA_ID = "SAPIANTA_FRESH_OPERATION_CONTEXT_V1"
SCHEMA_VERSION = "1.0.0"
CONSTITUTIONAL_ANCHOR_HEAD = "5c972e9960987ab27420395b54ace693df097e7b"
MOUNT_TAG = "g77_evidence"
GUEST_MOUNT_ROOT = "/mnt/g77-evidence"
GUEST_CONTEXT_FILENAME = "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANONICAL_ARGV_DOMAIN = b"SAPIANTA_G77_256ER_CANONICAL_QEMU_ARGV_V1\x00"
U64 = struct.Struct(">Q")
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
IDENTITY = re.compile(r"^G77_256[A-Z0-9]{2,32}(?:_[A-Z0-9]+)+$")
PREFIX = re.compile(r"^G77_256[A-Z0-9]{2,32}$")
FORBIDDEN_HISTORICAL_PREFIXES = frozenset({
    "G77_256FM", "G77_256FW", "G77_256FY", "G77_256FZ",
    "G77_256GA", "G77_256GB", "G77_256GC",
})
FORBIDDEN_HISTORICAL_PATH_MARKERS = tuple(
    value.lower() + "_" for value in FORBIDDEN_HISTORICAL_PREFIXES
)

CONTEXT_FIELDS = frozenset({
    "context_schema_version",
    "generation_identity",
    "operation_identity",
    "identity_namespace_prefix",
    "repository_head",
    "repository_tree",
    "constitutional_anchor_head",
    "operation_evidence_root",
    "transient_root",
    "overlay_path",
    "serial_path",
    "receipt_parent",
    "pre_receipt_path",
    "post_receipt_path",
    "runtime_export_root",
    "runtime_manifest_path",
    "guest_context_path",
    "guest_output_relative_paths",
    "guest_fixture_root",
    "canonical_argv",
    "canonical_argv_sha256",
    "authorization_binding_policy",
    "candidate_manifest_sha256",
    "wrapper_fc_er_che_schema_hashes",
    "qemu_executable_base_seed_checkout_bindings",
    "context_sha256",
})

AUTHORIZATION_BINDING_POLICY = {
    "authorization_must_bind": [
        "context_sha256",
        "canonical_argv_sha256",
        "generation_identity",
        "operation_identity",
        "repository_head",
        "repository_tree",
        "constitutional_anchor_head",
        "immutable_assets",
        "one_shot_limits",
        "zero_retry_repair_replay",
        "no_network_policy",
    ],
    "authorization_artifact_hash_in_context": False,
    "authorization_reusable": False,
    "network_authorized": False,
    "one_shot": True,
    "repair_limit": 0,
    "replay_limit": 0,
    "retry_limit": 0,
}

FC_IDENTITY_TOKENS = (
    "G77_256FC_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1",
    "G77_256FC_AUTHORITY_CHECKPOINT_V1",
    "G77_256FC_AUTHORITY_RECORDED",
    "G77_256FC_AUTHORITY_RESULT_001",
    "G77_256FC_AUTHORIZATION",
    "G77_256FC_CANONICAL_BINDING_ADAPTER",
    "G77_256FC_CHE_ENTRY_001",
    "G77_256FC_CONTINUATION_001",
    "G77_256FC_CONTINUATION_MANIFEST_TERMINAL_V1",
    "G77_256FC_CONTINUATION_MANIFEST_V1",
    "G77_256FC_CONVERSATION_001",
    "G77_256FC_DELIVERY_001",
    "G77_256FC_E05_AUTHORIZED_ATTEMPT_001",
    "G77_256FC_E05_SUPPLIED_WRONG_ATTEMPT_002",
    "G77_256FC_E05_WRONG_ATTEMPT_BASELINE_INPUT_001",
    "G77_256FC_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001",
    "G77_256FC_E05_WRONG_ATTEMPT_DENIAL_OUTCOME_001",
    "G77_256FC_E05_WRONG_ATTEMPT_FAIL_CLOSED_CONTRACT_V1",
    "G77_256FC_E05_WRONG_ATTEMPT_FAIL_CLOSED_V1",
    "G77_256FC_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001",
    "G77_256FC_EXISTING_RUNTIMELEDGER_REPLAY_CONTEXT_V1",
    "G77_256FC_GUEST_EXECUTION_SEAL_V1",
    "G77_256FC_GUEST_TEARDOWN_SEAL_V1",
    "G77_256FC_HUMAN_AUTHORIZATION_CHANNEL",
    "G77_256FC_IDEMPOTENCY_001",
    "G77_256FC_INTERACTION_001",
    "G77_256FC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1",
    "G77_256FC_ORDER_001",
    "G77_256FC_OWNER_PROJECTION_001",
    "G77_256FC_P10_ONE_DENIAL_ZERO_RETRY_INVENTORY_V1",
    "G77_256FC_PRESENTATION_001",
    "G77_256FC_PRE_ACT_CHECKPOINT_V1",
    "G77_256FC_RAW_EXECUTION_EVIDENCE_V1",
    "G77_256FC_REQUEST_001",
    "G77_256FC_RESPONSE_001",
    "G77_256FC_SESSION_001",
    "G77_256FC_WRONG_ATTEMPT_CUSTODY_REQUEST_001",
    "G77_256FC_WRONG_ATTEMPT_EVIDENCE_RUN_001",
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1",
)


class ContextError(ValueError):
    """One deterministic fail-closed context rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def argv_sha256(argv: list[str]) -> str:
    encoded: list[bytes] = []
    for index, argument in enumerate(argv):
        if not isinstance(argument, str) or "\x00" in argument:
            raise ContextError(f"canonical argv element {index} invalid")
        encoded.append(argument.encode("utf-8", errors="strict"))
    payload = CANONICAL_ARGV_DOMAIN + U64.pack(len(encoded)) + b"".join(
        U64.pack(len(argument)) + argument for argument in encoded
    )
    return sha256_bytes(payload)


def derived_identity_tokens(prefix: str) -> tuple[str, ...]:
    _validate_prefix(prefix)
    return tuple(token.replace("G77_256FC", prefix) for token in FC_IDENTITY_TOKENS)


def guest_output_relative_paths(prefix: str) -> list[str]:
    _validate_prefix(prefix)
    return [
        f"{prefix}_RAW_EXECUTION_EVIDENCE_V1.jsonl",
        "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl",
        "G77_256DN_SPCE_EXECUTION_SEAL_V1.json",
        f"{prefix}_PRE_ACT_CHECKPOINT_V1.json",
        f"{prefix}_AUTHORITY_CHECKPOINT_V1.json",
        f"{prefix}_GUEST_EXECUTION_SEAL_V1.json",
        f"{prefix}_GUEST_TEARDOWN_SEAL_V1.json",
        f"{prefix}_CONTINUATION_MANIFEST_TERMINAL_V1.json",
    ]


def derive_canonical_argv(
    *,
    overlay_path: Path,
    serial_path: Path,
    seed_path: Path,
    checkout_path: Path,
    wrapper_host_root: Path,
    dn_harness_host_root: Path,
    runtime_export_root: Path,
) -> list[str]:
    values = (
        overlay_path,
        serial_path,
        seed_path,
        checkout_path,
        wrapper_host_root,
        dn_harness_host_root,
        runtime_export_root,
    )
    if any(not value.is_absolute() for value in values):
        raise ContextError("canonical argv paths must be absolute")
    return [
        "/usr/bin/qemu-system-x86_64",
        "-machine", "pc,accel=tcg",
        "-cpu", "max",
        "-smp", "2",
        "-m", "1536",
        "-display", "none",
        "-monitor", "none",
        "-serial", f"file:{serial_path}",
        "-no-reboot",
        "-nic", "none",
        "-drive", f"file={overlay_path},if=virtio,format=qcow2",
        "-drive", f"file={seed_path},if=virtio,format=raw,readonly=on",
        "-virtfs",
        f"local,path={checkout_path},mount_tag=aigol_checkout,security_model=none,readonly=on",
        "-virtfs",
        f"local,path={wrapper_host_root},mount_tag=fm_harness,security_model=none,readonly=on",
        "-virtfs",
        f"local,path={dn_harness_host_root},mount_tag=g77_harness,security_model=none,readonly=on",
        "-virtfs",
        f"local,path={runtime_export_root},mount_tag={MOUNT_TAG},security_model=none",
    ]


def seal_context(context: dict[str, Any]) -> dict[str, Any]:
    if "context_sha256" in context:
        raise ContextError("context must be unsealed before sealing")
    sealed = dict(context)
    sealed["context_sha256"] = sha256_bytes(canonical_bytes(context))
    return sealed


def build_context(
    *,
    repository_root: Path,
    repository_head: str,
    repository_tree: str,
    generation_identity: str,
    operation_identity: str,
    identity_namespace_prefix: str,
    operation_evidence_root: Path,
    transient_root: Path,
    candidate_manifest_sha256: str,
    wrapper_fc_er_che_schema_hashes: dict[str, str],
    qemu_executable_base_seed_checkout_bindings: dict[str, Any],
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    operation_evidence_root = operation_evidence_root.absolute()
    transient_root = transient_root.absolute()
    prefix = identity_namespace_prefix
    _validate_prefix(prefix)
    receipt_parent = operation_evidence_root / "receipts"
    runtime_export = operation_evidence_root / "runtime_export"
    overlay = transient_root / "guest-overlay.qcow2"
    serial = transient_root / "serial.log"
    manifest = runtime_export / f"{prefix}_CONTINUATION_MANIFEST_V1.json"
    bindings = qemu_executable_base_seed_checkout_bindings
    argv = derive_canonical_argv(
        overlay_path=overlay,
        serial_path=serial,
        seed_path=Path(bindings["seed"]["path"]),
        checkout_path=Path(bindings["checkout"]["path"]),
        wrapper_host_root=repository_root / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness"
        ),
        dn_harness_host_root=repository_root / (
            ".github/governance/evidence/g77_256dn_p03_diagnostic_v1/harness"
        ),
        runtime_export_root=runtime_export,
    )
    context = {
        "context_schema_version": SCHEMA_VERSION,
        "generation_identity": generation_identity,
        "operation_identity": operation_identity,
        "identity_namespace_prefix": prefix,
        "repository_head": repository_head,
        "repository_tree": repository_tree,
        "constitutional_anchor_head": CONSTITUTIONAL_ANCHOR_HEAD,
        "operation_evidence_root": str(operation_evidence_root),
        "transient_root": str(transient_root),
        "overlay_path": str(overlay),
        "serial_path": str(serial),
        "receipt_parent": str(receipt_parent),
        "pre_receipt_path": str(receipt_parent / f"{prefix}_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"),
        "post_receipt_path": str(receipt_parent / f"{prefix}_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"),
        "runtime_export_root": str(runtime_export),
        "runtime_manifest_path": str(manifest),
        "guest_context_path": f"{GUEST_MOUNT_ROOT}/{GUEST_CONTEXT_FILENAME}",
        "guest_output_relative_paths": guest_output_relative_paths(prefix),
        "guest_fixture_root": f"/run/{prefix.lower().replace('_', '-')}-p11",
        "canonical_argv": argv,
        "canonical_argv_sha256": argv_sha256(argv),
        "authorization_binding_policy": AUTHORIZATION_BINDING_POLICY,
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "wrapper_fc_er_che_schema_hashes": wrapper_fc_er_che_schema_hashes,
        "qemu_executable_base_seed_checkout_bindings": bindings,
    }
    sealed = seal_context(context)
    validate_context(sealed, repository_root=repository_root)
    return sealed


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ContextError("context JSON contains duplicate keys")
        value[key] = item
    return value


def load_context(path: Path, *, repository_root: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContextError("context file absent, symlinked, or non-regular")
    raw = path.read_bytes()
    try:
        context = json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextError("context JSON malformed") from exc
    if not isinstance(context, dict):
        raise ContextError("context JSON root must be an object")
    if raw != canonical_bytes(context):
        raise ContextError("context JSON is not canonical")
    validate_context(context, repository_root=repository_root)
    return context


def _validate_prefix(prefix: Any) -> None:
    if not isinstance(prefix, str) or PREFIX.fullmatch(prefix) is None:
        raise ContextError("identity namespace prefix malformed")
    if prefix in FORBIDDEN_HISTORICAL_PREFIXES or prefix == "G77_256FC":
        raise ContextError("historical identity namespace prefix reuse prohibited")


def _absolute_canonical_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContextError(f"{field} missing or malformed")
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts or str(path) != os.path.normpath(value):
        raise ContextError(f"{field} is not a canonical safe absolute path")
    return path


def _assert_no_symlink_components(path: Path, *, allow_missing: bool) -> None:
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ContextError(f"symlink-sensitive path layout prohibited: {path}")
        if not cursor.exists():
            if allow_missing:
                return
            raise ContextError(f"required path component absent: {cursor}")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_hash_map(value: Any, field: str) -> None:
    if not isinstance(value, dict) or not value:
        raise ContextError(f"{field} missing or malformed")
    for key, digest in value.items():
        if not isinstance(key, str) or not key or not isinstance(digest, str):
            raise ContextError(f"{field} entry malformed")
        if HEX_64.fullmatch(digest) is None:
            raise ContextError(f"{field} SHA-256 malformed")


def validate_context(context: dict[str, Any], *, repository_root: Path) -> dict[str, Any]:
    if set(context) != CONTEXT_FIELDS:
        raise ContextError("context fields missing, unknown, or duplicated")
    if context["context_schema_version"] != SCHEMA_VERSION:
        raise ContextError("context schema version mismatch")
    if context["constitutional_anchor_head"] != CONSTITUTIONAL_ANCHOR_HEAD:
        raise ContextError("constitutional anchor mismatch")
    if HEX_40.fullmatch(str(context["repository_head"])) is None:
        raise ContextError("repository HEAD malformed")
    if HEX_40.fullmatch(str(context["repository_tree"])) is None:
        raise ContextError("repository tree malformed")
    prefix = context["identity_namespace_prefix"]
    _validate_prefix(prefix)
    for field in ("generation_identity", "operation_identity"):
        value = context[field]
        if not isinstance(value, str) or IDENTITY.fullmatch(value) is None:
            raise ContextError(f"{field} malformed")
        if not value.startswith(prefix + "_"):
            raise ContextError(f"{field} not derived from identity namespace prefix")
    if context["generation_identity"] == context["operation_identity"]:
        raise ContextError("generation and operation identities must be distinct")
    expected_generation = (
        f"{prefix}_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
        "OPERATIONAL_COMMISSIONING_V1"
    )
    if context["generation_identity"] != expected_generation:
        raise ContextError("generation identity is not the canonical FC-derived identity")

    fresh_fields = (
        "operation_evidence_root", "transient_root", "overlay_path", "serial_path",
        "receipt_parent", "pre_receipt_path", "post_receipt_path",
        "runtime_export_root", "runtime_manifest_path",
    )
    paths = {field: _absolute_canonical_path(context[field], field) for field in fresh_fields}
    for field, path in paths.items():
        if any(marker in str(path).lower() for marker in FORBIDDEN_HISTORICAL_PATH_MARKERS):
            raise ContextError(f"{field} reuses a historical namespace")
        _assert_no_symlink_components(path, allow_missing=True)
    operation_root = paths["operation_evidence_root"]
    transient_root = paths["transient_root"]
    if operation_root == transient_root or _is_relative_to(operation_root, transient_root) or _is_relative_to(transient_root, operation_root):
        raise ContextError("operation and transient mutable roots overlap")
    expected_descendants = {
        "receipt_parent": operation_root / "receipts",
        "runtime_export_root": operation_root / "runtime_export",
        "overlay_path": transient_root / "guest-overlay.qcow2",
        "serial_path": transient_root / "serial.log",
    }
    for field, expected in expected_descendants.items():
        if paths[field] != expected:
            raise ContextError(f"{field} is not canonically derived")
    if paths["pre_receipt_path"].parent != paths["receipt_parent"] or paths["post_receipt_path"].parent != paths["receipt_parent"]:
        raise ContextError("receipt paths escape the context receipt parent")
    if paths["runtime_manifest_path"].parent != paths["runtime_export_root"]:
        raise ContextError("runtime manifest escapes the context runtime export")
    mutable_destinations = [
        paths["overlay_path"], paths["serial_path"], paths["pre_receipt_path"],
        paths["post_receipt_path"], paths["runtime_manifest_path"],
        *(paths["runtime_export_root"] / item for item in context["guest_output_relative_paths"]),
        paths["runtime_export_root"] / GUEST_CONTEXT_FILENAME,
    ]
    if len(mutable_destinations) != len(set(mutable_destinations)):
        raise ContextError("duplicated mutable output destination")

    outputs = context["guest_output_relative_paths"]
    if not isinstance(outputs, list) or outputs != guest_output_relative_paths(prefix):
        raise ContextError("guest output sink declaration incomplete or noncanonical")
    for item in outputs:
        path = Path(item)
        if path.is_absolute() or len(path.parts) != 1 or path.name != item:
            raise ContextError("guest output relative path unsafe")
    if context["guest_context_path"] != f"{GUEST_MOUNT_ROOT}/{GUEST_CONTEXT_FILENAME}":
        raise ContextError("guest context path mismatch")
    expected_fixture_root = f"/run/{prefix.lower().replace('_', '-')}-p11"
    if context["guest_fixture_root"] != expected_fixture_root:
        raise ContextError("guest fixture root is not derived from identity namespace prefix")
    if context["authorization_binding_policy"] != AUTHORIZATION_BINDING_POLICY:
        raise ContextError("authorization binding policy mismatch")
    if HEX_64.fullmatch(str(context["candidate_manifest_sha256"])) is None:
        raise ContextError("candidate manifest SHA-256 malformed")
    _validate_hash_map(context["wrapper_fc_er_che_schema_hashes"], "wrapper/FC/ER/CHE/schema hashes")

    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    if not isinstance(bindings, dict) or set(bindings) != {"qemu_executable", "base", "seed", "checkout"}:
        raise ContextError("QEMU/base/seed/checkout bindings incomplete")
    for field in ("qemu_executable", "base", "seed"):
        binding = bindings[field]
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise ContextError(f"{field} binding malformed")
        _absolute_canonical_path(binding["path"], f"{field}.path")
        if HEX_64.fullmatch(str(binding["sha256"])) is None:
            raise ContextError(f"{field} binding hash malformed")
    checkout = bindings["checkout"]
    if not isinstance(checkout, dict) or set(checkout) != {"path", "head", "tree", "detached", "clean", "read_only_mount"}:
        raise ContextError("checkout binding malformed")
    _absolute_canonical_path(checkout["path"], "checkout.path")
    if HEX_40.fullmatch(str(checkout["head"])) is None or HEX_40.fullmatch(str(checkout["tree"])) is None:
        raise ContextError("checkout Git binding malformed")
    if checkout["detached"] is not True or checkout["clean"] is not True or checkout["read_only_mount"] is not True:
        raise ContextError("checkout exact detached/clean/read-only contract missing")

    repository_root = repository_root.resolve()
    expected_argv = derive_canonical_argv(
        overlay_path=paths["overlay_path"],
        serial_path=paths["serial_path"],
        seed_path=Path(bindings["seed"]["path"]),
        checkout_path=Path(checkout["path"]),
        wrapper_host_root=repository_root / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness",
        dn_harness_host_root=repository_root / ".github/governance/evidence/g77_256dn_p03_diagnostic_v1/harness",
        runtime_export_root=paths["runtime_export_root"],
    )
    if context["canonical_argv"] != expected_argv:
        raise ContextError("canonical argv changed outside approved operation slots")
    digest = argv_sha256(expected_argv)
    if context["canonical_argv_sha256"] != digest:
        raise ContextError("canonical argv seal mismatch")
    if expected_argv.count("-nic") != 1 or expected_argv[expected_argv.index("-nic") + 1] != "none":
        raise ContextError("no-network canonical argv contract violated")
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    if context["context_sha256"] != sha256_bytes(canonical_bytes(unsealed)):
        raise ContextError("context seal mismatch")
    if len(FC_IDENTITY_TOKENS) != 39 or len(set(derived_identity_tokens(prefix))) != 39:
        raise ContextError("full 39-token guest identity family derivation failed")
    return context


def complete_mutable_sink_paths(context: dict[str, Any]) -> tuple[Path, ...]:
    runtime_root = Path(context["runtime_export_root"])
    return (
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(runtime_root / item for item in context["guest_output_relative_paths"]),
    )


def validate_freshness(
    context: dict[str, Any],
    *,
    overlay_materialized: bool = False,
) -> dict[str, Any]:
    sinks = complete_mutable_sink_paths(context)
    collisions = [str(path) for path in sinks if path.exists() or path.is_symlink()]
    if collisions:
        raise ContextError("mutable output collision: " + ",".join(collisions))
    overlay = Path(context["overlay_path"])
    if overlay_materialized:
        if overlay.is_symlink() or not overlay.is_file():
            raise ContextError("materialized overlay absent or unsafe")
    elif overlay.exists() or overlay.is_symlink():
        raise ContextError("overlay collision or prior consumption")
    runtime_export = Path(context["runtime_export_root"])
    if runtime_export.exists():
        if runtime_export.is_symlink() or not runtime_export.is_dir():
            raise ContextError("runtime export collision or unsafe state")
        allowed = {
            Path(context["runtime_manifest_path"]),
            runtime_export / GUEST_CONTEXT_FILENAME,
        }
        unexpected = {path for path in runtime_export.iterdir() if path not in allowed}
        if unexpected:
            raise ContextError("runtime export contains undeclared writable sink")
    return {
        "complete_sink_count": len(sinks),
        "complete_sink_absence": "PASS",
        "overlay_fresh": "PASS",
        "runtime_export_fresh": "PASS",
        "guest_fixture_fresh": "DEFERRED_TO_GUEST_DEFENSE_IN_DEPTH",
    }


def assert_paths_absent(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.exists() or path.is_symlink():
            raise ContextError(f"path collision: {path}")
