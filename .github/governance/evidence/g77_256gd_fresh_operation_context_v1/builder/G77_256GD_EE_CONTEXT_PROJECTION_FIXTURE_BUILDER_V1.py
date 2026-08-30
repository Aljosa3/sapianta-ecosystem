#!/usr/bin/env python3
"""Build a TEST_ONLY/NON_AUTHORITY context projection for unchanged EE flow."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess


LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CANDIDATE = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
PREFIX = "G77_256GDVALID01"


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--operation-root", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.repo_root.resolve()
    launcher_path = root / LAUNCHER
    spec = importlib.util.spec_from_file_location("g77_256gd_ee_fixture_owner", launcher_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing FM owner import failed")
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    operation_root = arguments.operation_root.resolve()
    if operation_root.exists():
        raise RuntimeError("EE context fixture operation root already exists")
    context = launcher.build_operation_context(
        repository_root=root,
        repository_head=git(root, "rev-parse", "HEAD"),
        repository_tree=git(root, "rev-parse", "HEAD^{tree}"),
        generation_identity=(
            PREFIX
            + "_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity=PREFIX + "_OPERATION_001",
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=operation_root,
        transient_root=Path("/tmp/g77_256gd_ee_binding_transient_v1"),
    )
    runtime = Path(context["runtime_export_root"])
    runtime.mkdir(parents=True, exist_ok=False)
    (runtime / launcher.fresh_context.GUEST_CONTEXT_FILENAME).write_bytes(
        launcher.canonical_bytes(context)
    )
    Path(context["runtime_manifest_path"]).write_bytes((root / CANDIDATE).read_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
