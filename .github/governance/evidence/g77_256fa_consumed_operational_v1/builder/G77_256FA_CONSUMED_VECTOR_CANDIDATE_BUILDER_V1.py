#!/usr/bin/env python3
"""Build the one fresh FA CONSUMED candidate from committed common producers."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


REQUIRED_HEAD = "7297f014ec8ba0940bbe08994a5e48f00e0bb059"
REQUIRED_TREE = "c1ad5878e05c8002cb806a5934108d65ca1efde7"
GENERATION_ID = "G77_256FA_ONE_FRESH_HUMAN_AUTHORIZED_CONSUMED_OPERATIONAL_COMMISSIONING_V1"
ROOT = ".github/governance/evidence/g77_256fa_consumed_operational_v1"
EI_PATH = (
    ".github/governance/evidence/g77_256ei_producer_hardening_v1/producer/"
    "G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_V1.py"
)
EI_SHA256 = "501ec44273fce69b5eb5b30112ab857819d41066fb5f4afec4a7101110968ac9"
EB_SEAL = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "G77_256EB_FINAL_VALIDATION_SEAL_V1.json"
)
EE_SEAL = (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "G77_256EE_FINAL_VALIDATION_SEAL_V1.json"
)
EXTENSIONS = (
    ("G77_256FA_CONSUMED_VECTOR_ADAPTER", f"{ROOT}/harness/G77_256FA_CONSUMED_VECTOR_ADAPTER_V1.py"),
    ("G77_256ER_REUSED_RAW_EVIDENCE_SCHEMA", ".github/governance/evidence/g77_256er_p11_operational_v1/G77_256ER_RAW_EVIDENCE_SCHEMA_V1.json"),
    ("G77_256FA_CLOUD_INIT_META_DATA", f"{ROOT}/raw/G77_256FA_CLOUD_INIT_META_DATA_V1.yaml"),
    ("G77_256FA_CLOUD_INIT_NETWORK_CONFIG", f"{ROOT}/raw/G77_256FA_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"),
    ("G77_256FA_CLOUD_INIT_USER_DATA", f"{ROOT}/raw/G77_256FA_CLOUD_INIT_USER_DATA_V1.yaml"),
    ("G77_256ER_REUSED_ATOMIC_CHECKPOINT_WRITER", ".github/governance/evidence/g77_256er_p11_operational_v1/checkpoint/G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py"),
    ("G77_256ER_REUSED_QEMU_ARGV_BINDING", ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"),
    ("G77_256EZ_REUSED_STATIC_BINDING_FIXTURE", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/binding/G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_FIXTURE_V1.py"),
    ("G77_256EZ_REUSED_STATIC_BINDING_GUARD", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/validation/G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_REGRESSION_V1.py"),
)
LINEAGE = (
    ("G77_256EX_COMMON_SUBSTRATE_CERTIFICATE", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"),
    ("G77_256EX_FINAL_VALIDATION_SEAL", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json"),
    ("G77_256EW_CANONICAL_SUBSTRATE_MANIFEST", ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"),
    ("G77_256EU_PROSPECTIVE_COUNTER_MODEL", ".github/governance/evidence/g77_256eu_p11_entry_semantics_v1/G77_256EU_P11_ENTRY_SEMANTIC_MODEL_AND_REGRESSION_MATRIX_V1.json"),
    ("G77_256EZ_FINAL_VALIDATION_SEAL", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/G77_256EZ_FINAL_VALIDATION_SEAL_V1.json"),
    ("G77_256EM_AUTHORITATIVE_5_OF_18_FRONTIER", ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json"),
    ("G77_256EY_HISTORICAL_FAIL_CLOSED_EVIDENCE", ".github/governance/evidence/g77_256ey_consumed_operational_v1/G77_256EY_FINAL_VALIDATION_SEAL_V1.json"),
    ("G48_REPORTING_STANDARD", "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md"),
)


def git(repository_root: Path, *arguments: str) -> str:
    import subprocess
    return subprocess.check_output(
        ["git", *arguments], cwd=repository_root, text=True
    ).strip()


def load_ei(repository_root: Path) -> ModuleType:
    path = repository_root / EI_PATH
    spec = importlib.util.spec_from_file_location("g77_256ei_reused_producer_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("EI producer import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module._sha256(path) != EI_SHA256:
        raise RuntimeError("EI producer identity mismatch")
    return module


def build(repository_root: Path) -> dict[str, Any]:
    if git(repository_root, "rev-parse", "HEAD") != REQUIRED_HEAD:
        raise RuntimeError("required HEAD mismatch")
    if git(repository_root, "rev-parse", "HEAD^{tree}") != REQUIRED_TREE:
        raise RuntimeError("required tree mismatch")
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    envelope = du.build_du_fixture(repository_root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": GENERATION_ID,
        "required_head": REQUIRED_HEAD,
        "source_tree": REQUIRED_TREE,
        "current_spce_phase": "PHASE_B_FA_CONSUMED_VECTOR_CANDIDATE",
        "phase_sequence": 1,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [
            du._seal_binding(repository_root, "G77_256EB_FINAL_VALIDATION_SEAL_V1", EB_SEAL),
            du._seal_binding(repository_root, "G77_256EE_FINAL_VALIDATION_SEAL_V1", EE_SEAL),
        ],
        "execution_counters": du.zero_execution_counters(),
        "case_counters": {"e05_case_execution_count": 0, "consumed_reuse_case_count": 0},
        "authority_state": {
            "lifecycle_state": "NOT_CREATED", "act_identity": None,
            "owner_revision": None, "authority_survives": False,
            "transferable": False, "reusable": False,
        },
        "lineage_bindings": [
            du._lineage_binding(repository_root, identity, path)
            for identity, path in LINEAGE
        ],
        "frontier_state": {
            "constitutional_frontier": "ONE_HUMAN_AUTHORIZED_FA_CONSUMED_E05_VECTOR",
            "exact_next_legal_action": "FRESH_DU_EB_EE_EZ_PREFLIGHT_BEFORE_ONE_MATERIALIZATION",
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_CONSUMED",
            "case_id": "G77_256FA_E05_CONSUMED_AUTHORITY_REUSE_DENIAL_001",
        },
        "first_failure_or_current_result": "PENDING__PHASE_B_AND_OPERATIONAL_VALIDATION_REQUIRED",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": ei.canonicalize_prohibitions(du, du.REQUIRED_PROHIBITED_ACTIONS),
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "HUMAN_SELECTED_VECTOR_CONSUMED_ONLY",
            "EX_CERTIFIED_COMMON_SUBSTRATE_REFERENCED_NOT_RECONSTRUCTED",
            "EZ_STATIC_EE_BINDING_REUSED",
            "FRESH_B1_B2_B6_OPERATIONAL_EVIDENCE_REQUIRED",
            "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT",
            "ONE_CANDIDATE_ONE_VM_ONE_BOOT_ONE_VECTOR_ZERO_RETRY",
            "E05_REMAINS_FIVE_OF_EIGHTEEN_UNTIL_INDEPENDENT_REDUCTION",
        ],
        "extension_bindings": [
            {"identity": identity, "path": path, "sha256": du.sha256_path(repository_root / path)}
            for identity, path in EXTENSIONS
        ],
    })
    return {
        "schema_id": "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1",
        "manifest": manifest,
        "manifest_sha256": du.sha256_bytes(du.canonical_bytes(manifest)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    payload = du.canonical_bytes(build(repository_root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.runtime_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    args.runtime_output.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
