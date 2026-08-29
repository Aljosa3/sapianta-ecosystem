#!/usr/bin/env python3
"""Execute the exact FF QEMU argv once and persist fresh B1 call-site evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
GENERATION_IDENTITY = "G77_256FF_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
REQUIRED_HEAD = "92ccdedb2d846c91878bf7a5b2ac958c547d60a1"
REQUIRED_TREE = "7cf4ab8dc22849db2445a80bf9e1dcae639747b0"
CANDIDATE_SHA256 = "371663c5afec8baa9513da0a6e14566ffe1a8f9f62d2e274a47a90dcd43f4447"
ADAPTER_SHA256 = "b63a2e622f2c069a97863176e87e6255fac37ad61edcb44e6a201f033127a323"
ROOT = ".github/governance/evidence/g77_256ff_wrong_attempt_operational_v1"
VECTOR = f"{ROOT}/raw/G77_256FF_QEMU_ARGV_V1.json"
PRE_RECEIPT = f"{ROOT}/raw/G77_256FF_B1_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST_RECEIPT = f"{ROOT}/raw/G77_256FF_B1_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
CANONICALIZER = ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"
CANONICALIZER_SHA256 = "00b2676f1c8360d7c1a3188095520f4592639e174f6b25e198e3036744d948ac"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def git(repository_root: Path, argument: str) -> str:
    return subprocess.check_output(["git", "rev-parse", argument], cwd=repository_root, text=True).strip()


def receipt(*, phase: str, argv: list[str], digest: str, vector_sha256: str,
            executable_sha256: str, started_ns: int, completed_ns: int | None,
            exit_status: int | None) -> dict[str, Any]:
    return {
        "schema_id": f"G77_256FF_B1_{phase}_EXECUTED_QEMU_ARGV_RECEIPT_V1",
        "generation_identity": GENERATION_IDENTITY,
        "required_head": REQUIRED_HEAD,
        "required_tree": REQUIRED_TREE,
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


def main() -> int:
    repository_root = Path.cwd().resolve()
    if git(repository_root, "HEAD") != REQUIRED_HEAD or git(repository_root, "HEAD^{tree}") != REQUIRED_TREE:
        raise RuntimeError("required Git baseline mismatch")
    pre_path = repository_root / PRE_RECEIPT
    post_path = repository_root / POST_RECEIPT
    if pre_path.exists() or post_path.exists():
        raise RuntimeError("FF launcher receipt already exists; retry prohibited")
    argv = json.loads((repository_root / VECTOR).read_text(encoding="utf-8"))
    if not isinstance(argv, list) or not argv or argv[0] != "/usr/bin/qemu-system-x86_64":
        raise RuntimeError("exact QEMU argv invalid")
    if argv.count("-nic") != 1 or argv[argv.index("-nic") + 1] != "none":
        raise RuntimeError("no-network QEMU vector invalid")
    canonicalizer = load_canonicalizer(repository_root)
    digest = canonicalizer.argv_sha256(argv)
    vector_sha = sha256_path(repository_root / VECTOR)
    executable_sha = sha256_path(Path(argv[0]))
    started = time.time_ns()
    write_atomic(pre_path, receipt(
        phase="PRE", argv=argv, digest=digest, vector_sha256=vector_sha,
        executable_sha256=executable_sha, started_ns=started,
        completed_ns=None, exit_status=None,
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
            completed_ns=completed, exit_status=status,
        ))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
