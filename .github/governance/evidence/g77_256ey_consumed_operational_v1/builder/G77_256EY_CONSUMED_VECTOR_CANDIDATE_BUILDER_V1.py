#!/usr/bin/env python3
"""Build one fresh EY CONSUMED candidate from committed common producers."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


REQUIRED_HEAD = "de2fcd66f61e3263e243949f18b0a2cef3a94f8b"
REQUIRED_TREE = "e06cfcff68c63db691587167bad6bb5410f104ac"
GENERATION_ID = (
    "G77_256EY_FIRST_ONE_BOUNDED_OPERATIONAL_E05_CONSUMER_OF_CERTIFIED_"
    "P11_SPCE_COMMON_SUBSTRATE_V1"
)
ROOT = ".github/governance/evidence/g77_256ey_consumed_operational_v1"
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
    ("G77_256EY_CONSUMED_VECTOR_ADAPTER", f"{ROOT}/harness/G77_256EY_CONSUMED_VECTOR_ADAPTER_V1.py"),
    ("G77_256ER_REUSED_RAW_EVIDENCE_SCHEMA", ".github/governance/evidence/g77_256er_p11_operational_v1/G77_256ER_RAW_EVIDENCE_SCHEMA_V1.json"),
    ("G77_256EY_CLOUD_INIT_META_DATA", f"{ROOT}/raw/G77_256EY_CLOUD_INIT_META_DATA_V1.yaml"),
    ("G77_256EY_CLOUD_INIT_NETWORK_CONFIG", f"{ROOT}/raw/G77_256EY_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"),
    ("G77_256EY_CLOUD_INIT_USER_DATA", f"{ROOT}/raw/G77_256EY_CLOUD_INIT_USER_DATA_V1.yaml"),
    ("G77_256ER_REUSED_ATOMIC_CHECKPOINT_WRITER", ".github/governance/evidence/g77_256er_p11_operational_v1/checkpoint/G77_256ER_ATOMIC_CHECKPOINT_WRITER_V1.py"),
    ("G77_256ER_REUSED_QEMU_ARGV_BINDING", ".github/governance/evidence/g77_256er_p11_operational_v1/qemu_vector/G77_256ER_CANONICAL_QEMU_ARGV_V1.py"),
)
LINEAGE = (
    ("G77_256EX_COMMON_SUBSTRATE_CERTIFICATE", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"),
    ("G77_256EX_FINAL_VALIDATION_SEAL", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json"),
    ("G77_256EW_CANONICAL_SUBSTRATE_MANIFEST", ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"),
    ("G77_256EU_PROSPECTIVE_COUNTER_MODEL", ".github/governance/evidence/g77_256eu_p11_entry_semantics_v1/G77_256EU_P11_ENTRY_SEMANTIC_MODEL_AND_REGRESSION_MATRIX_V1.json"),
    ("G77_256EM_AUTHORITATIVE_5_OF_18_FRONTIER", ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json"),
    ("G77_256ER_HISTORICAL_CONSUMED_CONTEXT_ONLY", ".github/governance/evidence/g77_256er_p11_operational_v1/G77_256ER_SPCE_FINAL_EXECUTION_SEAL_V1.json"),
    ("G77_256ES_HISTORICAL_FAIL_CLOSED_REPORT_ONLY", "docs/governance/G77_256ES_CROSS_ACCOUNT_SPCE_FAIL_CLOSED_CONTINUATION_AND_FINALIZATION_OF_INTERRUPTED_G77_256ER_AFTER_P11_ENTRY_COUNT_BOUND_VIOLATION_V1.md"),
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
        "current_spce_phase": "PHASE_B_CONSUMED_VECTOR_CANDIDATE",
        "phase_sequence": 1,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [
            du._seal_binding(repository_root, "G77_256EB_FINAL_VALIDATION_SEAL_V1", EB_SEAL),
            du._seal_binding(repository_root, "G77_256EE_FINAL_VALIDATION_SEAL_V1", EE_SEAL),
        ],
        "execution_counters": du.zero_execution_counters(),
        "case_counters": {
            "e05_case_execution_count": 0,
            "consumed_reuse_case_count": 0,
        },
        "authority_state": {
            "lifecycle_state": "NOT_CREATED",
            "act_identity": None,
            "owner_revision": None,
            "authority_survives": False,
            "transferable": False,
            "reusable": False,
        },
        "lineage_bindings": [
            du._lineage_binding(repository_root, identity, path)
            for identity, path in LINEAGE
        ],
        "frontier_state": {
            "constitutional_frontier": "ONE_HUMAN_SELECTED_CONSUMED_E05_VECTOR",
            "exact_next_legal_action": "FRESH_EB_EE_AND_PHASE_C_ACCEPTANCE_BEFORE_ONE_MATERIALIZATION",
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_CONSUMED",
            "case_id": "G77_256EY_E05_CONSUMED_AUTHORITY_REUSE_DENIAL_001",
        },
        "first_failure_or_current_result": "PENDING__PHASE_B_AND_C_VALIDATION_REQUIRED",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": ei.canonicalize_prohibitions(
            du, du.REQUIRED_PROHIBITED_ACTIONS
        ),
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "HUMAN_SELECTED_VECTOR_CONSUMED_ONLY",
            "EX_CERTIFIED_COMMON_SUBSTRATE_REFERENCED_NOT_RECONSTRUCTED",
            "FRESH_ACT_FIRST_AUTHORIZED_EFFECT_THEN_ONE_POST_CONSUMED_REQUEST",
            "POST_CONSUMED_REQUEST_MUST_DENY_BEFORE_SECOND_ADMITTED_P11_ENTRY",
            "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT",
            "ONE_FIRST_EFFECT_AND_ZERO_SECOND_PROTECTED_EFFECT_REQUIRED",
            "FRESH_B1_B2_B6_EVIDENCE_REQUIRED",
            "E05_REMAINS_FIVE_OF_EIGHTEEN_UNTIL_INDEPENDENT_REDUCTION",
        ],
        "extension_bindings": [
            {
                "identity": identity,
                "path": path,
                "sha256": du.sha256_path(repository_root / path),
            }
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
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(du.canonical_bytes(build(repository_root)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
