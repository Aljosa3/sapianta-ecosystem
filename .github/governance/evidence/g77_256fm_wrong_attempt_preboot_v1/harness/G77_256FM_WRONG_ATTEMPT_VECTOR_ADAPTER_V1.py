#!/usr/bin/env python3
"""FM hash-authenticated specialization of committed FK-hardened FC semantics."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


FC_SOURCE = Path(
    "/mnt/aigol/.github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
    "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_SOURCE_SHA256 = "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
RAW_ROOT = Path("/mnt/g77-evidence")
CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256FM_CONTINUATION_MANIFEST_V1.json"
SPECIALIZATION_FROM = "G77_256FC"
SPECIALIZATION_TO = "G77_256FM"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_specialized_namespace() -> dict[str, Any]:
    if sha256_path(FC_SOURCE) != FC_SOURCE_SHA256:
        raise RuntimeError("committed FK-hardened FC adapter identity mismatch")
    source = FC_SOURCE.read_text(encoding="utf-8")
    if source.count(SPECIALIZATION_FROM) < 1 or SPECIALIZATION_TO in source:
        raise RuntimeError("FC specialization precondition invalid")
    specialized = source.replace(SPECIALIZATION_FROM, SPECIALIZATION_TO)
    namespace: dict[str, Any] = {
        "__name__": "g77_256fm_wrong_attempt_specialization_v1",
        "__file__": str(FC_SOURCE),
        "__package__": None,
    }
    exec(compile(specialized, str(FC_SOURCE), "exec"), namespace)
    if namespace.get("GENERATION_ID") != (
        "G77_256FM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
        "OPERATIONAL_COMMISSIONING_V1"
    ):
        raise RuntimeError("FM generation specialization failed")
    if namespace.get("RAW_ROOT") != RAW_ROOT:
        raise RuntimeError("FM raw-root specialization failed")
    if namespace.get("CONTINUATION_MANIFEST_PATH") != CONTINUATION_MANIFEST_PATH:
        raise RuntimeError("FM continuation-path specialization failed")
    return namespace


def main() -> int:
    namespace = load_specialized_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
