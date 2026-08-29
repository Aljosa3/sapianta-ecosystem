#!/usr/bin/env python3
"""Build the sole fresh FM FK-bound WRONG_ATTEMPT preboot candidate."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType


REQUIRED_HEAD = "7dce67ec18696ba0bad73130f3f7a84168f25277"
REQUIRED_TREE = "3cb61ec34e9593efb711dce61014dc8fdf0f6dd9"
GENERATION_ID = "G77_256FM_FRESH_FL_FK_BOUND_WRONG_ATTEMPT_CANDIDATE_AND_PREBOOT_PREPARATION_V1"
ROOT = ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1"
FF_BUILDER = ".github/governance/evidence/g77_256ff_wrong_attempt_operational_v1/builder/G77_256FF_WRONG_ATTEMPT_CANDIDATE_BUILDER_V1.py"
FF_BUILDER_SHA256 = "70bc4542b4774d6c1c79fdd0f23c4caea00d733a266e7893d5b624fc58771e12"

EXTENSIONS = (
    ("G77_256FM_PHASE_A_AUTHORITY_AND_DESIGN", f"{ROOT}/G77_256FM_SPCE_PHASE_A_AUTHORITY_AND_DESIGN_V1.json"),
    ("G77_256FM_WRONG_ATTEMPT_ADAPTER", f"{ROOT}/harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"),
    ("G77_256FC_FK_HARDENED_ADAPTER", ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"),
    ("G77_256FL_PREBOOT_REUSE_BLOCKER", ".github/governance/evidence/g77_256fl_wrong_attempt_operational_v1/raw/G77_256FL_PREBOOT_REUSE_BLOCKER_V1.json"),
    ("G77_256FK_FINAL_REDUCTION", ".github/governance/evidence/g77_256fk_che_terminal_hardening_v1/G77_256FK_SPCE_PHASE_D_FINAL_REDUCTION_V1.json"),
    ("G77_256ER_RAW_EVIDENCE_SCHEMA", ".github/governance/evidence/g77_256er_p11_operational_v1/G77_256ER_RAW_EVIDENCE_SCHEMA_V1.json"),
    ("G77_256FM_CLOUD_INIT_META_DATA", f"{ROOT}/raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"),
    ("G77_256FM_CLOUD_INIT_NETWORK_CONFIG", f"{ROOT}/raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"),
    ("G77_256FM_CLOUD_INIT_USER_DATA", f"{ROOT}/raw/G77_256FM_CLOUD_INIT_USER_DATA_V1.yaml"),
    ("G77_256ER_ATOMIC_CHECKPOINT_WRITER", ".github/governance/evidence/g77_256er_p11_operational_v1/checkpoint/G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py"),
    ("G77_256ER_CANONICAL_QEMU_ARGV", ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"),
    ("G77_256EZ_STATIC_BINDING_GUARD", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/validation/G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_REGRESSION_V1.py"),
)


def load_ff(repository_root: Path) -> ModuleType:
    path = repository_root / FF_BUILDER
    spec = importlib.util.spec_from_file_location("g77_256ff_pinned_builder_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("FF builder import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.load_ei(repository_root)._sha256(path) != FF_BUILDER_SHA256:
        raise RuntimeError("FF builder identity mismatch")
    return module


def build(repository_root: Path) -> dict:
    ff = load_ff(repository_root)
    ff.REQUIRED_HEAD = REQUIRED_HEAD
    ff.REQUIRED_TREE = REQUIRED_TREE
    ff.GENERATION_ID = GENERATION_ID
    ff.ROOT = ROOT
    ff.EXTENSIONS = EXTENSIONS
    envelope = ff.build(repository_root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION_ID,
        "current_spce_phase": "PHASE_B_FRESH_FK_BOUND_WRONG_ATTEMPT_CANDIDATE",
        "frontier_state": {
            "constitutional_frontier": "FRESH_FK_BOUND_WRONG_ATTEMPT_PREBOOT_PREPARATION",
            "exact_next_legal_action": "FRESH_DU_EB_EE_THEN_ONE_MATERIALIZATION_NO_BOOT",
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
            "case_id": "G77_256FM_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001",
        },
        "first_failure_or_current_result": "PENDING__FRESH_DU_EB_EE_AND_PREBOOT_MATERIALIZATION_REQUIRED",
        "observations": [
            "FL_FAIL_CLOSED_BLOCKER_PRESERVED",
            "COMMITTED_FK_HARDENED_FC_ADAPTER_HASH_SPECIALIZED_FOR_FM",
            "FRESH_CANDIDATE_AND_PHYSICAL_ASSETS_ONLY",
            "DU_EB_EE_REQUIRED_BEFORE_MATERIALIZATION",
            "VM_BOOT_QEMU_EXECUTION_AND_OPERATIONAL_ATTEMPT_NOT_AUTHORIZED",
            "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT",
            "E05_REMAINS_SIX_OF_EIGHTEEN",
        ],
    })
    du = ff.load_ei(repository_root).load_du(repository_root)
    envelope["manifest_sha256"] = du.sha256_bytes(du.canonical_bytes(manifest))
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    output = args.output.resolve()
    runtime_output = args.runtime_output.resolve()
    if output.exists() or runtime_output.exists():
        raise RuntimeError("FM candidate or runtime projection already exists")
    ff = load_ff(repository_root)
    du = ff.load_ei(repository_root).load_du(repository_root)
    payload = du.canonical_bytes(build(repository_root))
    output.parent.mkdir(parents=True, exist_ok=True)
    runtime_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    runtime_output.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
