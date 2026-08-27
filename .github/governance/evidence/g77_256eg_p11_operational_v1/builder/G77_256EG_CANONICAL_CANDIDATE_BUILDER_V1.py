#!/usr/bin/env python3
"""Build the exact EG pre-materialization Canonical V1 candidate."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any


REQUIRED_HEAD = "58d130f0504883d62bf8fbaefef98219568e62fa"
REQUIRED_TREE = "fce92cb1601ad806af3ee8030ff49ca1cf81804d"
DU_VALIDATOR_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
EVIDENCE_ROOT = ".github/governance/evidence/g77_256eg_p11_operational_v1"
BUILDER_PATH = f"{EVIDENCE_ROOT}/builder/G77_256EG_CANONICAL_CANDIDATE_BUILDER_V1.py"
HARNESS_PATH = f"{EVIDENCE_ROOT}/harness/G77_256EG_P11_OPERATIONAL_HARNESS_V1.py"
RAW_SCHEMA_PATH = f"{EVIDENCE_ROOT}/G77_256EG_RAW_EVIDENCE_SCHEMA_V1.json"
META_DATA_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EG_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EG_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
USER_DATA_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EG_CLOUD_INIT_USER_DATA_V1.yaml"
EB_FINAL_SEAL_PATH = (
    ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
    "G77_256EB_FINAL_VALIDATION_SEAL_V1.json"
)
EE_FINAL_SEAL_PATH = (
    ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
    "G77_256EE_FINAL_VALIDATION_SEAL_V1.json"
)
LINEAGE = (
    (
        "G77_256CD_E05_OBLIGATION_DEFINITION",
        "docs/governance/G77_256CD_P11_PRE_IMPLEMENTATION_EVIDENCE_GENERATION_AND_VALIDATION_PLAN_V1.md",
    ),
    (
        "G77_256DU_CANONICAL_V1_CONTRACT",
        ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
        "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md",
    ),
    ("G77_256EB_CANDIDATE_BOUND_RECEIPT_CAPABILITY", EB_FINAL_SEAL_PATH),
    (
        "G77_256EC_PRESERVED_FAILED_ATTEMPT",
        ".github/governance/evidence/g77_256ec_p11_operational_v1/"
        "G77_256EC_SPCE_FINAL_EXECUTION_SEAL_V1.json",
    ),
    (
        "G77_256ED_FAIL_CLOSED_FINALIZATION",
        "docs/governance/G77_256ED_CROSS_ACCOUNT_SPCE_RESUMPTION_AND_FAIL_CLOSED_COMPLETION_OF_INTERRUPTED_G77_256EC_V1.md",
    ),
    (
        "G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT",
        ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
        "G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT_V1.md",
    ),
    ("G77_256EE_RUNTIME_CONSUMER_BINDING_CAPABILITY", EE_FINAL_SEAL_PATH),
    (
        "G48_REPORTING_STANDARD",
        "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md",
    ),
)


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository_root, text=True
    ).strip()


def load_du(repository_root: Path) -> ModuleType:
    path = repository_root / DU_VALIDATOR_PATH
    spec = importlib.util.spec_from_file_location("g77_256du_validator_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("DU validator import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extension(
    du: ModuleType, repository_root: Path, identity: str, path: str
) -> dict[str, str]:
    return {
        "identity": identity,
        "path": path,
        "sha256": du.sha256_path(repository_root / path),
    }


def build(repository_root: Path) -> dict[str, Any]:
    if git(repository_root, "rev-parse", "HEAD") != REQUIRED_HEAD:
        raise RuntimeError("required HEAD mismatch")
    if git(repository_root, "rev-parse", "HEAD^{tree}") != REQUIRED_TREE:
        raise RuntimeError("required tree mismatch")
    du = load_du(repository_root)
    envelope = du.build_du_fixture(repository_root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": (
            "G77_256EG_ONE_FRESH_BOUNDED_NON_PRODUCTION_E05_WRONG_CALLER_"
            "P11_GENERATION_V1"
        ),
        "required_head": REQUIRED_HEAD,
        "source_tree": REQUIRED_TREE,
        "current_spce_phase": "PHASE_A_PRE_MATERIALIZATION_CANDIDATE",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [
            du._seal_binding(
                repository_root, "G77_256EB_FINAL_VALIDATION_SEAL_V1", EB_FINAL_SEAL_PATH
            ),
            du._seal_binding(
                repository_root, "G77_256EE_FINAL_VALIDATION_SEAL_V1", EE_FINAL_SEAL_PATH
            ),
        ],
        "execution_counters": du.zero_execution_counters(),
        "case_counters": {
            "e05_case_execution_count": 0,
            "wrong_caller_case_count": 0,
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
            "constitutional_frontier": (
                "ONE_HUMAN_AUTHORIZED_FRESH_WRONG_CALLER_P11_E05_GENERATION"
            ),
            "exact_next_legal_action": (
                "EB_AND_EE_PRE_MATERIALIZATION_RECEIPTS_BEFORE_ONE_MATERIALIZATION"
            ),
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_CALLER",
            "case_id": "G77_256EG_E05_WRONG_CALLER_DENIAL_BEFORE_ATTEMPT_001",
        },
        "first_failure_or_current_result": (
            "PENDING__EB_AND_EE_PRE_MATERIALIZATION_VALIDATION_REQUIRED"
        ),
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": [
            "E05_EXECUTION_BEFORE_EB_EE_ADMISSION",
            "EXECUTION_REPLAY",
            "HUMAN_OPERATIONAL_ACT_CREATION_BEFORE_COMMISSIONING",
            "MATERIALIZATION_BEFORE_EB_EE_ADMISSION",
            "P12_ENTRY",
            "PRODUCTION_ROUTE",
            "SECOND_VM",
            "VM_BOOT_BEFORE_MATERIALIZATION_CHECKPOINT",
        ],
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "SELECTED_VECTOR_WRONG_CALLER_ONLY",
            "EXPECTED_D1_PEER_AUTHENTICATION_DENIAL_BEFORE_D2_AND_PRECLAIM",
            "NO_HUMAN_OPERATIONAL_ACT_REQUIRED_FOR_WRONG_CALLER_FIXTURE",
            "ZERO_UNAUTHORIZED_EFFECT_REQUIRED",
            "EB_CANDIDATE_BOUND_RECEIPT_REQUIRED",
            "EE_RUNTIME_CONSUMER_BINDING_RECEIPT_REQUIRED",
            "E05_FRONTIER_REMAINS_FOUR_OF_EIGHTEEN_UNTIL_FINAL_EVIDENCE_AUTHENTICATES",
        ],
        "extension_bindings": [
            extension(du, repository_root, "G77_256EG_CANDIDATE_BUILDER", BUILDER_PATH),
            extension(du, repository_root, "G77_256EG_P11_HARNESS", HARNESS_PATH),
            extension(du, repository_root, "G77_256EG_RAW_EVIDENCE_SCHEMA", RAW_SCHEMA_PATH),
            extension(du, repository_root, "G77_256EG_CLOUD_INIT_META_DATA", META_DATA_PATH),
            extension(du, repository_root, "G77_256EG_CLOUD_INIT_NETWORK_CONFIG", NETWORK_CONFIG_PATH),
            extension(du, repository_root, "G77_256EG_CLOUD_INIT_USER_DATA", USER_DATA_PATH),
        ],
    })
    envelope["manifest_sha256"] = du.sha256_bytes(du.canonical_bytes(manifest))
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    du = load_du(repository_root)
    args.output.write_bytes(du.canonical_bytes(build(repository_root)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
