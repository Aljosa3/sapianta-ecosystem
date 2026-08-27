#!/usr/bin/env python3
"""Atomically persist and independently authenticate one canonical checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any


SENTINELS = (b"PLACEHOLDER", b"TODO", b"FIXME", b"TEMP_HASH", b"UNSEALED")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CheckpointError(ValueError):
    """One deterministic fail-closed checkpoint persistence error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_duplicate_free(path: Path) -> Any:
    def object_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise CheckpointError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=object_hook,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CheckpointError(f"non-finite JSON value: {value}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckpointError("checkpoint JSON is not valid UTF-8 JSON") from exc


def sentinel_count(payload: bytes) -> int:
    upper = payload.upper()
    return sum(upper.count(item) for item in SENTINELS)


def authenticate_bytes(raw: bytes) -> dict[str, Any]:
    try:
        envelope = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CheckpointError("persisted checkpoint is not UTF-8 JSON") from exc
    if raw != canonical_bytes(envelope):
        raise CheckpointError("persisted checkpoint is not canonical JSON plus LF")
    if set(envelope) != {"schema_id", "checkpoint", "checkpoint_sha256"}:
        raise CheckpointError("checkpoint envelope fields differ")
    if not isinstance(envelope["schema_id"], str) or not envelope["schema_id"]:
        raise CheckpointError("checkpoint envelope schema identity is absent")
    if not isinstance(envelope["checkpoint"], dict):
        raise CheckpointError("checkpoint payload must be an object")
    embedded = envelope["checkpoint_sha256"]
    if not isinstance(embedded, str) or SHA256_RE.fullmatch(embedded) is None:
        raise CheckpointError("checkpoint embedded inner hash is not SHA-256")
    computed = sha256_bytes(canonical_bytes(envelope["checkpoint"]))
    if embedded != computed:
        raise CheckpointError("checkpoint embedded and computed inner hashes differ")
    observed_sentinels = sentinel_count(raw)
    if observed_sentinels != 0:
        raise CheckpointError("checkpoint contains a forbidden sentinel")
    return {
        "schema_id": "G77_256ER_ATOMIC_CHECKPOINT_AUTHENTICATION_RESULT_V1",
        "checkpoint_sha256": computed,
        "persisted_bytes_sha256": sha256_bytes(raw),
        "sentinel_count": observed_sentinels,
        "authentication_result": "PASS",
    }


def authenticate_path(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise CheckpointError("persisted checkpoint must be a regular non-symlink file")
    return authenticate_bytes(path.read_bytes())


def write_all(fd: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        written = os.write(fd, payload[offset:])
        if written <= 0:
            raise CheckpointError("checkpoint write made no progress")
        offset += written


def persist(checkpoint_path: Path, output: Path, envelope_schema_id: str) -> dict[str, Any]:
    checkpoint = load_duplicate_free(checkpoint_path)
    if not isinstance(checkpoint, dict):
        raise CheckpointError("checkpoint payload must be an object")
    inner_sha256 = sha256_bytes(canonical_bytes(checkpoint))
    envelope = {
        "schema_id": envelope_schema_id,
        "checkpoint": checkpoint,
        "checkpoint_sha256": inner_sha256,
    }
    final_bytes = canonical_bytes(envelope)
    if sentinel_count(final_bytes) != 0:
        raise CheckpointError("final checkpoint bytes contain a forbidden sentinel")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp-{os.getpid()}")
    if output.exists() or output.is_symlink():
        raise CheckpointError("checkpoint output already exists")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        write_all(fd, final_bytes)
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.replace(temporary, output)
        directory_fd = os.open(output.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)

    result = authenticate_path(output)
    if result["checkpoint_sha256"] != inner_sha256:
        raise CheckpointError("independent reread inner hash differs")
    return {
        **result,
        "durable_atomic_persistence": "PASS__FILE_FSYNC__ATOMIC_REPLACE__DIRECTORY_FSYNC",
        "independent_reread": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--persist", type=Path)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--envelope-schema-id")
    args = parser.parse_args()
    try:
        if args.verify is not None:
            if args.output is not None or args.envelope_schema_id is not None:
                parser.error("--verify accepts no persistence arguments")
            result = authenticate_path(args.verify)
        else:
            if args.output is None or not args.envelope_schema_id:
                parser.error("--persist requires --output and --envelope-schema-id")
            result = persist(args.persist, args.output, args.envelope_schema_id)
        print(canonical_bytes(result).decode(), end="")
        return 0
    except (CheckpointError, OSError) as exc:
        failure = {
            "schema_id": "G77_256ER_ATOMIC_CHECKPOINT_FAILURE_V1",
            "failure": str(exc),
            "authentication_result": "FAIL_CLOSED",
        }
        print(canonical_bytes(failure).decode(), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
