#!/usr/bin/env python3
"""Reissue only wrapper-dependent FM candidate bindings for GD."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


SOURCE = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json"
)
WRAPPER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness/"
    "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
CONTEXT_IMPLEMENTATION = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
CLOUD_INIT_USER_DATA = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_USER_DATA_V1.yaml"
)
NOCLOUD_SEED = Path(
    ".github/governance/evidence/g77_256gh_guest_adapter_path_binding_v1/static/"
    "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1.img"
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def build(root: Path) -> dict[str, Any]:
    source = json.loads((root / SOURCE).read_bytes())
    envelope = copy.deepcopy(source)
    manifest = envelope["manifest"]
    manifest["required_head"] = git(root, "rev-parse", "HEAD")
    manifest["source_tree"] = git(root, "rev-parse", "HEAD^{tree}")
    extensions = manifest["extension_bindings"]
    wrapper = next(
        item for item in extensions if item["identity"] == "G77_256FM_WRONG_ATTEMPT_ADAPTER"
    )
    wrapper["sha256"] = sha256(root / WRAPPER)
    cloud_init = next(
        item
        for item in extensions
        if item["identity"] == "G77_256FM_CLOUD_INIT_USER_DATA"
    )
    cloud_init["sha256"] = sha256(root / CLOUD_INIT_USER_DATA)
    extensions.extend([
        {
            "identity": "SAPIANTA_FRESH_OPERATION_CONTEXT_V1_IMPLEMENTATION",
            "path": str(CONTEXT_IMPLEMENTATION),
            "sha256": sha256(root / CONTEXT_IMPLEMENTATION),
        },
        {
            "identity": "SAPIANTA_WRONG_ATTEMPT_NOCLOUD_SEED_V1",
            "path": str(NOCLOUD_SEED),
            "sha256": sha256(root / NOCLOUD_SEED),
        },
    ])
    envelope["manifest_sha256"] = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-output", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.repo_root.resolve()
    payload = canonical_bytes(build(root))
    for output in (arguments.output, arguments.runtime_output):
        target = output.resolve()
        if target.exists():
            raise RuntimeError(f"binding reissue target already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
