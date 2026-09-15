#!/usr/bin/env python3
"""Generation-local LT parent readiness composition; no authority or operation.

The caller supplies its exact permitted generation root and exact future LT
lifecycle leaf.  This module owns only preparation and observation before LT's
existing leaf-reservation boundary.  It never imports or invokes LT, FM, an
authority owner, a launcher, QEMU, or a VM.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any


READINESS_SCHEMA = "G77_256LY_LT_PARENT_READINESS_ENVELOPE_V1"
OBSERVATION_SCHEMA = "G77_256LY_LT_PARENT_READINESS_OBSERVATION_V1"
PRECONSUMPTION_RESULT = (
    "VERIFIED__SAME_PREPARED_PARENT_OBJECT__SAME_INTENDED_LT_LEAF__LEAF_ABSENT"
)
PRECONDITION_OWNER = "GENERATION_LOCAL_CONTROLLER_SELECTING_THE_LT_STATE_LEAF"
PARENT_MODE = 0o700
PROBE_NAME = ".g77_256ly_lt_parent_durability_probe"
IDENTITY_FIELDS = (
    "device",
    "inode",
    "mode",
    "link_count",
    "size",
    "mtime_ns",
    "ctime_ns",
    "owner_uid",
)


class ReadinessError(RuntimeError):
    """Fail-closed rejection of unsafe, stale, drifted, or ambiguous state."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _absolute_normalized(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def derive_lt_paths(permitted_generation_root: Path, lifecycle_leaf: Path) -> tuple[Path, Path, Path]:
    """Derive and contain the exact immediate parent without resolving symlinks."""

    root = _absolute_normalized(permitted_generation_root)
    leaf = _absolute_normalized(lifecycle_leaf)
    parent = leaf.parent
    if leaf.name in {"", ".", ".."}:
        raise ReadinessError("LT_LIFECYCLE_LEAF_NAME_INVALID")
    try:
        relative_parent = parent.relative_to(root)
    except ValueError as exc:
        raise ReadinessError("LT_STATE_PATH_ESCAPES_PERMITTED_GENERATION_ROOT") from exc
    if any(part in {"", ".", ".."} for part in relative_parent.parts):
        raise ReadinessError("LT_STATE_PARENT_RELATION_AMBIGUOUS")
    return root, parent, leaf


def _directory_identity(observed: os.stat_result) -> dict[str, int]:
    if not stat.S_ISDIR(observed.st_mode):
        raise ReadinessError("LT_STATE_PATH_COMPONENT_NOT_DIRECTORY")
    return {
        "device": observed.st_dev,
        "inode": observed.st_ino,
        "mode": observed.st_mode,
        "link_count": observed.st_nlink,
        "size": observed.st_size,
        "mtime_ns": observed.st_mtime_ns,
        "ctime_ns": observed.st_ctime_ns,
        "owner_uid": observed.st_uid,
    }


def _open_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        return os.open(path, flags)
    except OSError as exc:
        raise ReadinessError(f"LT_STATE_DIRECTORY_UNSAFE_OR_UNOPENABLE:{path}") from exc


def _open_child_directory(parent_fd: int, name: str) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        return os.open(name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise ReadinessError(f"LT_STATE_PATH_COMPONENT_UNSAFE_OR_UNOPENABLE:{name}") from exc


def _require_path_identity(path: Path, descriptor: int, label: str) -> dict[str, int]:
    try:
        path_state = os.lstat(path)
        descriptor_state = os.fstat(descriptor)
    except OSError as exc:
        raise ReadinessError(f"{label}_IDENTITY_UNOBSERVABLE") from exc
    if stat.S_ISLNK(path_state.st_mode) or not stat.S_ISDIR(path_state.st_mode):
        raise ReadinessError(f"{label}_SYMLINK_OR_NON_DIRECTORY")
    if (path_state.st_dev, path_state.st_ino) != (
        descriptor_state.st_dev,
        descriptor_state.st_ino,
    ):
        raise ReadinessError(f"{label}_PATH_TO_OBJECT_IDENTITY_DISCONTINUITY")
    return _directory_identity(descriptor_state)


def _validate_component_safety(identity: dict[str, int], *, exact_parent: bool) -> None:
    permissions = stat.S_IMODE(identity["mode"])
    if identity["owner_uid"] != os.geteuid():
        raise ReadinessError("LT_STATE_DIRECTORY_OWNER_MISMATCH")
    if permissions & 0o022:
        raise ReadinessError("LT_STATE_DIRECTORY_GROUP_OR_OTHER_WRITABLE")
    if exact_parent and permissions != PARENT_MODE:
        raise ReadinessError("LT_STATE_PARENT_MODE_NOT_0700")


def _walk_parent(root: Path, parent: Path, *, materialize: bool) -> tuple[int, dict[str, int], dict[str, int]]:
    if root.is_symlink() or not root.is_dir():
        raise ReadinessError("PERMITTED_GENERATION_ROOT_UNSAFE_OR_MISSING")
    root_fd = _open_directory(root)
    current_fd = root_fd
    try:
        root_identity = _require_path_identity(root, root_fd, "PERMITTED_GENERATION_ROOT")
        relative = parent.relative_to(root)
        current_path = root
        for part in relative.parts:
            current_path = current_path / part
            try:
                observed = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
            except FileNotFoundError:
                if not materialize:
                    raise ReadinessError("LT_STATE_PARENT_MISSING_DURING_REOBSERVATION")
                try:
                    os.mkdir(part, PARENT_MODE, dir_fd=current_fd)
                    os.fsync(current_fd)
                except OSError as exc:
                    raise ReadinessError(f"LT_STATE_PARENT_MATERIALIZATION_FAILED:{part}") from exc
            except OSError as exc:
                raise ReadinessError(f"LT_STATE_PATH_COMPONENT_UNOBSERVABLE:{part}") from exc
            else:
                if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                    raise ReadinessError(f"LT_STATE_PATH_COMPONENT_SYMLINK_OR_NON_DIRECTORY:{part}")
            next_fd = _open_child_directory(current_fd, part)
            identity = _require_path_identity(current_path, next_fd, "LT_STATE_PATH_COMPONENT")
            _validate_component_safety(identity, exact_parent=current_path == parent)
            if materialize:
                os.fsync(next_fd)
            if current_fd != root_fd:
                os.close(current_fd)
            current_fd = next_fd
        root_identity = _require_path_identity(root, root_fd, "PERMITTED_GENERATION_ROOT")
        parent_identity = _require_path_identity(parent, current_fd, "LT_STATE_PARENT")
        _validate_component_safety(parent_identity, exact_parent=True)
        if current_fd == root_fd:
            # A permitted root used directly as the LT parent is part of the
            # exact parent contract and must therefore satisfy mode 0700.
            _validate_component_safety(root_identity, exact_parent=True)
        result_fd = os.dup(current_fd)
        return result_fd, root_identity, parent_identity
    finally:
        if current_fd != root_fd:
            os.close(current_fd)
        os.close(root_fd)


def _require_leaf_absent(parent_fd: int, leaf_name: str) -> None:
    try:
        os.stat(leaf_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            return
        raise ReadinessError("LT_LIFECYCLE_LEAF_STATE_AMBIGUOUS") from exc
    raise ReadinessError("LT_LIFECYCLE_LEAF_EXISTS_OR_STALE_RESERVATION")


def _durability_probe(parent_fd: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        probe_fd = os.open(PROBE_NAME, flags, 0o600, dir_fd=parent_fd)
    except OSError as exc:
        raise ReadinessError("LT_STATE_PARENT_DURABILITY_PROBE_CREATION_FAILED") from exc
    try:
        os.fsync(probe_fd)
    finally:
        os.close(probe_fd)
    try:
        os.unlink(PROBE_NAME, dir_fd=parent_fd)
        os.fsync(parent_fd)
    except OSError as exc:
        raise ReadinessError("LT_STATE_PARENT_DURABILITY_PROBE_CLEANUP_FAILED") from exc


def _observe(root: Path, parent: Path, leaf: Path, *, materialize: bool, probe: bool) -> dict[str, Any]:
    parent_fd, root_identity, parent_identity = _walk_parent(root, parent, materialize=materialize)
    try:
        if not os.access(parent, os.W_OK | os.X_OK):
            raise ReadinessError("LT_STATE_PARENT_NOT_USABLE")
        _require_leaf_absent(parent_fd, leaf.name)
        if probe:
            _durability_probe(parent_fd)
            _require_leaf_absent(parent_fd, leaf.name)
            parent_identity = _require_path_identity(parent, parent_fd, "LT_STATE_PARENT")
            _validate_component_safety(parent_identity, exact_parent=True)
            if root == parent:
                root_identity = parent_identity
        leaf_binding = {
            "canonical_leaf_path": str(leaf),
            "canonical_parent_path": str(parent),
            "leaf_name": leaf.name,
            "parent_device": parent_identity["device"],
            "parent_inode": parent_identity["inode"],
        }
        return {
            "schema_id": OBSERVATION_SCHEMA,
            "permitted_generation_root": str(root),
            "permitted_root_identity": root_identity,
            "lt_lifecycle_leaf": str(leaf),
            "lt_state_parent": str(parent),
            "lt_leaf_name": leaf.name,
            "parent_identity": parent_identity,
            "leaf_binding_sha256": digest(leaf_binding),
            "parent_mode_required": "0700",
            "parent_openable": True,
            "parent_usable": True,
            "parent_durability_validated": True,
            "lifecycle_leaf_absent": True,
            "stale_reservation_absent": True,
            "precondition_owner": PRECONDITION_OWNER,
            "authority_created_count": 0,
            "authority_consumed_count": 0,
            "lt_reservation_count": 0,
            "child_launch_count": 0,
            "fm_operational_invocation_count": 0,
            "qemu_start_count": 0,
            "vm_start_count": 0,
            "retry_count": 0,
        }
    finally:
        os.close(parent_fd)


def prepare_lt_parent_readiness(
    permitted_generation_root: Path,
    lifecycle_leaf: Path,
) -> dict[str, Any]:
    """Materialize only the required parent chain and seal exact readiness."""

    root, parent, leaf = derive_lt_paths(permitted_generation_root, lifecycle_leaf)
    observation = _observe(root, parent, leaf, materialize=True, probe=True)
    return {
        "schema_id": READINESS_SCHEMA,
        "observation": observation,
        "observation_sha256": digest(observation),
    }


def reobserve_before_authority_consumption(
    permitted_generation_root: Path,
    lifecycle_leaf: Path,
    readiness: dict[str, Any],
) -> dict[str, Any]:
    """Read-only proof of the same parent object and absent intended LT leaf."""

    if set(readiness) != {"schema_id", "observation", "observation_sha256"}:
        raise ReadinessError("LT_PARENT_READINESS_ENVELOPE_MALFORMED")
    if readiness.get("schema_id") != READINESS_SCHEMA:
        raise ReadinessError("LT_PARENT_READINESS_SCHEMA_MISMATCH")
    expected = readiness.get("observation")
    if not isinstance(expected, dict) or readiness.get("observation_sha256") != digest(expected):
        raise ReadinessError("LT_PARENT_READINESS_SEAL_MISMATCH")
    root, parent, leaf = derive_lt_paths(permitted_generation_root, lifecycle_leaf)
    if (
        expected.get("permitted_generation_root") != str(root)
        or expected.get("lt_state_parent") != str(parent)
        or expected.get("lt_lifecycle_leaf") != str(leaf)
        or expected.get("lt_leaf_name") != leaf.name
    ):
        raise ReadinessError("LT_PARENT_OR_LEAF_READINESS_BINDING_MISMATCH")
    current = _observe(root, parent, leaf, materialize=False, probe=False)
    if current != expected:
        raise ReadinessError("LT_PARENT_OR_LEAF_READINESS_IDENTITY_DRIFT")
    return {
        "result": PRECONSUMPTION_RESULT,
        "observation_sha256": readiness["observation_sha256"],
        "parent_identity_fields": list(IDENTITY_FIELDS),
        "leaf_binding_sha256": current["leaf_binding_sha256"],
        "authority_consumed_count": 0,
        "operation_attempt_count": 0,
    }
