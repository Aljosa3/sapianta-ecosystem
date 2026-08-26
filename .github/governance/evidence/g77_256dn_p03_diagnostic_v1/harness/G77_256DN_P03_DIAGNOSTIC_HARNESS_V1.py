#!/usr/bin/env python3
"""One bounded, non-operational P03-only diagnostic evidence instrument."""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import pwd
import grp
import shutil
import socket
import stat
import subprocess
import sys
from typing import Any


SCHEMA_ID = "G77_256DN_P03_RAW_EVIDENCE_V1"
HARNESS_ID = "G77_256DN_P03_DIAGNOSTIC_HARNESS_V1"
FIXTURE_ROOT = Path("/run/g77-256dn-p03")
PARENT = FIXTURE_ROOT / "ipc"
TARGET = PARENT / "p11_da_disposable_custody_v1.sock"
CHECKOUT = Path("/mnt/aigol")
RAW_ROOT = Path("/mnt/g77-evidence")
RAW_PATH = RAW_ROOT / "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl"
SEAL_PATH = RAW_ROOT / "G77_256DN_SPCE_EXECUTION_SEAL_V1.json"
HARNESS_PATH = Path("/mnt/g77-harness/G77_256DN_P03_DIAGNOSTIC_HARNESS_V1.py")
ROLES = {
    "issuance": {"uid": 1, "gid": 1, "groups": [4]},
    "caller": {"uid": 2, "gid": 2, "groups": [4]},
}
EFFECTS = (
    "create",
    "bind",
    "unlink",
    "rename",
    "replace",
    "chmod",
    "chown",
    "symlink",
    "hardlink",
)
ACCEPTED_ERRNOS = {errno.EACCES, errno.EPERM, errno.EROFS}


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def append_record(value: dict[str, Any]) -> None:
    value = {"schema_id": SCHEMA_ID, **value}
    with RAW_PATH.open("ab", buffering=0) as handle:
        handle.write(canonical_bytes(value))
        os.fsync(handle.fileno())


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def type_name(mode: int) -> str:
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISCHR(mode):
        return "character"
    if stat.S_ISBLK(mode):
        return "block"
    return "unknown"


def identity(path: Path, *, missing_ok: bool = False) -> dict[str, Any] | None:
    try:
        value = path.lstat()
    except FileNotFoundError:
        if missing_ok:
            return None
        raise
    try:
        resolved = str(path.resolve(strict=True))
    except FileNotFoundError:
        resolved = None
    return {
        "path": str(path),
        "realpath": resolved,
        "device": value.st_dev,
        "device_major": os.major(value.st_dev),
        "device_minor": os.minor(value.st_dev),
        "inode": value.st_ino,
        "type": type_name(value.st_mode),
        "owner_uid": value.st_uid,
        "owner_name": pwd.getpwuid(value.st_uid).pw_name,
        "group_gid": value.st_gid,
        "group_name": grp.getgrgid(value.st_gid).gr_name,
        "mode": f"{stat.S_IMODE(value.st_mode):04o}",
        "st_mode": f"{value.st_mode:o}",
    }


def same_target(before: dict[str, Any], after: dict[str, Any] | None) -> bool:
    if after is None:
        return False
    return all(after[key] == before[key] for key in ("device", "inode", "type"))


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", "-c", f"safe.directory={CHECKOUT}", *args],
        cwd=CHECKOUT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    ).stdout.strip()


def mount_context(expected_head: str, expected_tree: str) -> dict[str, Any]:
    mounts = Path("/proc/self/mounts").read_text(encoding="utf-8").splitlines()
    mountinfo = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
    checkout_mounts = [line for line in mounts if f" {CHECKOUT} " in line]
    statvfs = os.statvfs(CHECKOUT)
    observed_head = run_git("rev-parse", "HEAD")
    observed_tree = run_git("rev-parse", "HEAD^{tree}")
    status = run_git("status", "--porcelain")
    filesystem_type = subprocess.run(
        ["stat", "-f", "-c", "%T", str(CHECKOUT)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    ).stdout.strip()
    return {
        "record_type": "probe_context",
        "guest_mount_table": mounts,
        "guest_mountinfo": mountinfo,
        "checkout_mount_lines": checkout_mounts,
        "checkout_filesystem_type": filesystem_type,
        "checkout_head_expected": expected_head,
        "checkout_head_observed": observed_head,
        "checkout_tree_expected": expected_tree,
        "checkout_tree_observed": observed_tree,
        "checkout_status_porcelain": status,
        "checkout_statvfs_read_only": bool(statvfs.f_flag & os.ST_RDONLY),
        "checkout_mount_read_only": bool(checkout_mounts) and all(
            "ro" in line.split()[3].split(",") for line in checkout_mounts
        ),
        "guest_os_release": Path("/etc/os-release").read_text(encoding="utf-8").splitlines(),
    }


def candidate_path(role: str, effect: str) -> Path | None:
    if effect in {"create", "bind", "rename", "replace", "symlink", "hardlink"}:
        return PARENT / f".g77-256dn-{role}-{effect}-source"
    return None


def prepare_source(role: str, effect: str) -> dict[str, Any] | None:
    source = candidate_path(role, effect)
    if source is None or effect not in {"rename", "replace"}:
        return None
    source.write_text("same-filesystem-source", encoding="utf-8")
    os.chown(source, ROLES[role]["uid"], ROLES[role]["gid"])
    os.chmod(source, 0o600)
    return {
        "created_by": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
        "identity": identity(source),
        "inside_endpoint_parent": source.parent.resolve(strict=True) == PARENT.resolve(strict=True),
    }


def perform_effect(role: str, effect: str) -> dict[str, Any]:
    actor = {
        "pid": os.getpid(),
        "uid": os.getuid(),
        "gid": os.getgid(),
        "groups": os.getgroups(),
    }
    source = candidate_path(role, effect)
    parent_before = identity(PARENT)
    target_before = identity(TARGET)
    source_before = identity(source, missing_ok=True) if source is not None else None
    same_filesystem = (
        source_before["device"] == target_before["device"]
        if source_before is not None and effect in {"rename", "replace"}
        else None
    )
    operation_succeeded = False
    errno_number = 0
    errno_name = "NONE"
    try:
        if effect == "create":
            fd = os.open(source, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        elif effect == "bind":
            probe_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                probe_socket.bind(str(source))
            finally:
                probe_socket.close()
        elif effect == "unlink":
            TARGET.unlink()
        elif effect == "rename":
            source.rename(TARGET)
        elif effect == "replace":
            os.replace(source, TARGET)
        elif effect == "chmod":
            os.chmod(TARGET, 0o600)
        elif effect == "chown":
            os.chown(TARGET, actor["uid"], actor["gid"])
        elif effect == "symlink":
            os.symlink(TARGET, source)
        elif effect == "hardlink":
            os.link(TARGET, source)
        else:
            raise RuntimeError(f"unsupported effect: {effect}")
        operation_succeeded = True
    except OSError as exc:
        errno_number = int(exc.errno or 0)
        errno_name = errno.errorcode.get(errno_number, "UNKNOWN")
    source_after = identity(source, missing_ok=True) if source is not None else None
    target_after = identity(TARGET, missing_ok=True)
    if operation_succeeded:
        classification = "SUCCESSFUL_PROHIBITED_EFFECT"
    elif effect in {"rename", "replace"} and (
        same_filesystem is False or errno_number == errno.EXDEV
    ):
        classification = "CROSS_FILESYSTEM_PROBE_FAILURE"
    elif errno_number in ACCEPTED_ERRNOS:
        classification = "CUSTODY_PERMISSION_DENIAL"
    else:
        classification = "UNEXPECTED_PROBE_FAILURE"
    return {
        "record_type": "probe",
        "role": role,
        "effect": effect,
        "actor": actor,
        "endpoint_parent_before": parent_before,
        "target_before": target_before,
        "source_before": source_before,
        "source_inside_endpoint_parent": (
            source is not None and source.parent.resolve(strict=True) == PARENT.resolve(strict=True)
        ),
        "source_and_target_same_device": same_filesystem,
        "operation_succeeded": operation_succeeded,
        "errno_number": errno_number,
        "errno_symbolic_name": errno_name,
        "source_exists_after": source_after is not None,
        "source_after": source_after,
        "target_after": target_after,
        "target_identity_preserved_after": same_target(target_before, target_after),
        "classification": classification,
    }


def child_probe(role: str, effect: str, write_fd: int) -> None:
    try:
        binding = ROLES[role]
        os.setgroups(binding["groups"])
        os.setgid(binding["gid"])
        os.setuid(binding["uid"])
        payload = {"ok": True, "record": perform_effect(role, effect)}
    except BaseException as exc:
        payload = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "role": role,
            "effect": effect,
            "actor": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
        }
    os.write(write_fd, canonical_bytes(payload))
    os.close(write_fd)
    os._exit(0 if payload["ok"] else 111)


def run_probe(role: str, effect: str) -> dict[str, Any]:
    prepared = prepare_source(role, effect)
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        child_probe(role, effect, write_fd)
    os.close(write_fd)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(read_fd, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    os.close(read_fd)
    waited_pid, status_value = os.waitpid(pid, 0)
    payload = json.loads(b"".join(chunks))
    if not payload.get("ok"):
        raise RuntimeError(f"probe child failed: {payload}; wait={waited_pid}/{status_value}")
    record = payload["record"]
    record["source_preparation"] = prepared
    return record


def create_fixture() -> socket.socket:
    FIXTURE_ROOT.mkdir(mode=0o755)
    PARENT.mkdir(mode=0o750)
    os.chown(FIXTURE_ROOT, 0, 0)
    os.chown(PARENT, 3, 4)
    os.chmod(PARENT, 0o750)
    custody = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    custody.bind(str(TARGET))
    custody.listen(4)
    os.chown(TARGET, 3, 4)
    os.chmod(TARGET, 0o660)
    return custody


def write_seal(result: str, records: list[dict[str, Any]], raw_sha256: str) -> None:
    seal = {
        "schema_id": "G77_256DN_SPCE_EXECUTION_SEAL_V1",
        "phase": "PHASE_B_P03_ONLY_LIVE_DIAGNOSTIC",
        "result": result,
        "raw_evidence_path": str(RAW_PATH),
        "raw_evidence_sha256": raw_sha256,
        "probe_count": len(records),
        "accepted_denial_count": sum(
            record["classification"] == "CUSTODY_PERMISSION_DENIAL" for record in records
        ),
        "successful_prohibited_effect_count": sum(
            record["classification"] == "SUCCESSFUL_PROHIBITED_EFFECT" for record in records
        ),
        "cross_filesystem_failure_count": sum(
            record["classification"] == "CROSS_FILESYSTEM_PROBE_FAILURE" for record in records
        ),
        "unexpected_failure_count": sum(
            record["classification"] == "UNEXPECTED_PROBE_FAILURE" for record in records
        ),
        "p11_entry_count": 0,
        "e01_e12_execution_count": 0,
        "p12_entry_count": 0,
        "production_route_count": 0,
        "automatic_retry_count": 0,
        "second_vm_count": 0,
        "seal_is_authority": False,
    }
    SEAL_PATH.write_bytes(canonical_bytes(seal))
    with SEAL_PATH.open("rb") as handle:
        os.fsync(handle.fileno())


def main() -> int:
    if len(sys.argv) != 5:
        raise SystemExit("expected: HARNESS_SHA256 SCHEMA_SHA256 EXPECTED_HEAD EXPECTED_TREE")
    expected_harness_sha256, schema_sha256, expected_head, expected_tree = sys.argv[1:]
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists() or SEAL_PATH.exists():
        raise SystemExit("evidence sink is not empty")
    actual_harness_sha256 = sha256_path(HARNESS_PATH)
    if actual_harness_sha256 != expected_harness_sha256:
        raise SystemExit("harness hash mismatch")
    records: list[dict[str, Any]] = []
    custody: socket.socket | None = None
    result = "FAIL_CLOSED__PREREQUISITE"
    try:
        context = mount_context(expected_head, expected_tree)
        append_record({
            "record_type": "harness_authentication",
            "harness_id": HARNESS_ID,
            "harness_path": str(HARNESS_PATH),
            "harness_sha256_expected": expected_harness_sha256,
            "harness_sha256_observed": actual_harness_sha256,
            "evidence_schema_sha256": schema_sha256,
            "actor": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
        })
        append_record(context)
        context_ok = all((
            context["checkout_head_observed"] == expected_head,
            context["checkout_tree_observed"] == expected_tree,
            context["checkout_status_porcelain"] == "",
            context["checkout_mount_read_only"],
            context["checkout_statvfs_read_only"],
        ))
        if not context_ok:
            append_record({"record_type": "prerequisite_failure", "gate": "CHECKOUT_CONTEXT", "context": context})
            result = "FAIL_CLOSED__CHECKOUT_CONTEXT"
            return 20
        custody = create_fixture()
        append_record({
            "record_type": "fixture",
            "created_by": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
            "endpoint_parent": identity(PARENT),
            "target": identity(TARGET),
        })
        result = "PASS__18_OF_18_ACCEPTED_PERMISSION_DENIALS"
        for role in ("issuance", "caller"):
            for effect in EFFECTS:
                record = run_probe(role, effect)
                records.append(record)
                append_record(record)
                if record["classification"] != "CUSTODY_PERMISSION_DENIAL":
                    result = f"FAIL_CLOSED__{record['classification']}__{role}__{effect}"
                    break
                if not record["target_identity_preserved_after"]:
                    result = f"FAIL_CLOSED__TARGET_IDENTITY_CHANGED__{role}__{effect}"
                    break
                if effect in {"rename", "replace"} and not (
                    record["source_inside_endpoint_parent"]
                    and record["source_and_target_same_device"]
                    and record["source_exists_after"]
                ):
                    result = f"FAIL_CLOSED__SOURCE_POSTCONDITION__{role}__{effect}"
                    break
            if not result.startswith("PASS__"):
                break
        aggregate = {
            "record_type": "aggregate",
            "result": result,
            "probe_count": len(records),
            "accepted_denial_count": sum(
                record["classification"] == "CUSTODY_PERMISSION_DENIAL" for record in records
            ),
            "rename_replace_probe_count": sum(
                record["effect"] in {"rename", "replace"} for record in records
            ),
            "same_filesystem_rename_replace_count": sum(
                record["effect"] in {"rename", "replace"}
                and record["source_and_target_same_device"] is True
                for record in records
            ),
            "successful_prohibited_effect_count": sum(
                record["classification"] == "SUCCESSFUL_PROHIBITED_EFFECT" for record in records
            ),
            "cross_filesystem_failure_count": sum(
                record["classification"] == "CROSS_FILESYSTEM_PROBE_FAILURE" for record in records
            ),
            "unexpected_failure_count": sum(
                record["classification"] == "UNEXPECTED_PROBE_FAILURE" for record in records
            ),
            "all_target_identities_preserved": all(
                record["target_identity_preserved_after"] for record in records
            ),
            "decision_rule": [
                "operation_succeeded=>SUCCESSFUL_PROHIBITED_EFFECT",
                "rename_or_replace_and_different_device_or_EXDEV=>CROSS_FILESYSTEM_PROBE_FAILURE",
                "errno_in_EACCES_EPERM_EROFS=>CUSTODY_PERMISSION_DENIAL",
                "otherwise=>UNEXPECTED_PROBE_FAILURE",
            ],
        }
        append_record(aggregate)
        raw_sha256 = sha256_path(RAW_PATH)
        write_seal(result, records, raw_sha256)
        return 0 if result.startswith("PASS__") else 30
    except BaseException as exc:
        append_record({
            "record_type": "harness_failure",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "result": result,
            "actor": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
        })
        raw_sha256 = sha256_path(RAW_PATH)
        write_seal(result, records, raw_sha256)
        return 40
    finally:
        if custody is not None:
            custody.close()
        shutil.rmtree(FIXTURE_ROOT, ignore_errors=True)
        append_record({
            "record_type": "teardown",
            "fixture_root_absent": not FIXTURE_ROOT.exists(),
            "actor": {"pid": os.getpid(), "uid": os.getuid(), "gid": os.getgid()},
        })
        write_seal(result, records, sha256_path(RAW_PATH))


if __name__ == "__main__":
    raise SystemExit(main())
