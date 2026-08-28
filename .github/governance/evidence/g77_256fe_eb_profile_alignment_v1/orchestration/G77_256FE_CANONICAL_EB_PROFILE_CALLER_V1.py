#!/usr/bin/env python3
"""Invoke canonical EB once with its exact committed validation profile."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess


REQUIRED_HEAD = "1f29ecc1d8f70d66abb9f0e532edd8c4ab11c25b"
REQUIRED_TREE = "48ff619755cdae77a73b34b3d5bbd39c8d768b7e"
EB_VALIDATOR_PATH = Path(
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V1.py"
)
EB_VALIDATOR_SHA256 = "8e8171f757213f064cec463868408364175772e766615bd276ed7f0e28306b43"
EB_CANONICAL_PROFILE_ID = (
    "CANONICAL_V1_PRE_MATERIALIZATION_FOUR_GATE_CANDIDATE_BOUND_V1"
)
INVOCATION_LIMIT = 1
AUTOMATIC_RETRY = False


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository_root, text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    validator = repository_root / EB_VALIDATOR_PATH
    candidate = args.candidate.resolve()
    receipt = args.receipt_output.resolve()
    if git(repository_root, "rev-parse", "HEAD") != REQUIRED_HEAD:
        raise RuntimeError("required HEAD mismatch")
    if git(repository_root, "rev-parse", "HEAD^{tree}") != REQUIRED_TREE:
        raise RuntimeError("required tree mismatch")
    if sha256_path(validator) != EB_VALIDATOR_SHA256:
        raise RuntimeError("canonical EB validator identity mismatch")
    if not candidate.is_file():
        raise RuntimeError("candidate is absent")
    if receipt.exists():
        raise RuntimeError("EB receipt already exists; second invocation forbidden")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "python",
        str(validator),
        "--repo-root",
        str(repository_root),
        "--validate-candidate",
        str(candidate),
        "--receipt-output",
        str(receipt),
        "--required-head",
        REQUIRED_HEAD,
        "--required-tree",
        REQUIRED_TREE,
        "--validation-profile",
        EB_CANONICAL_PROFILE_ID,
    ]
    return subprocess.run(command, cwd=repository_root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
