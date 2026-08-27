#!/usr/bin/env python3
"""Build the exact EN CONSUMED pre-materialization Canonical V1 candidate."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any


REQUIRED_HEAD = "3693fbeb95b048a413a971b434d4f5326fe658a3"
REQUIRED_TREE = "7a446c16136b6f1787b904fecc991a7a285c2990"
EI_PRODUCER_PATH = (
    ".github/governance/evidence/g77_256ei_producer_hardening_v1/"
    "producer/G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_V1.py"
)
EVIDENCE_ROOT = ".github/governance/evidence/g77_256en_p11_operational_v1"
BUILDER_PATH = f"{EVIDENCE_ROOT}/builder/G77_256EN_CANONICAL_CANDIDATE_BUILDER_V1.py"
HARNESS_PATH = f"{EVIDENCE_ROOT}/harness/G77_256EN_P11_OPERATIONAL_HARNESS_V1.py"
RAW_SCHEMA_PATH = f"{EVIDENCE_ROOT}/G77_256EN_RAW_EVIDENCE_SCHEMA_V1.json"
META_DATA_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EN_CLOUD_INIT_META_DATA_V1.yaml"
NETWORK_CONFIG_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EN_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
USER_DATA_PATH = f"{EVIDENCE_ROOT}/raw/G77_256EN_CLOUD_INIT_USER_DATA_V1.yaml"
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
        "G77_256DX_E05_18_ITEM_REDUCTION",
        "docs/governance/G77_256DX_POST_DW_P11_E05_COMPLETION_REDUCTION_AND_EXACT_CD_FRONTIER_DETERMINATION_FROM_AUTHENTICATED_REPOSITORY_EVIDENCE_V1.md",
    ),
    (
        "G77_256DQ_POSITIVE_AND_STATE_TRANSITION_EVIDENCE",
        ".github/governance/evidence/g77_256dq_p11_operational_v1/G77_256DQ_SPCE_FINAL_EXECUTION_SEAL_V1.json",
    ),
    (
        "G77_256DW_CONCURRENCY_EVIDENCE",
        ".github/governance/evidence/g77_256dw_p11_operational_v1/G77_256DW_SPCE_FINAL_EXECUTION_SEAL_V1.json",
    ),
    (
        "G77_256DY_UNKNOWN_EVIDENCE",
        ".github/governance/evidence/g77_256dy_p11_operational_v1/G77_256DY_SPCE_FINAL_EXECUTION_SEAL_V1.json",
    ),
    (
        "G77_256DU_CANONICAL_V1_CONTRACT",
        ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
        "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md",
    ),
    ("G77_256EB_CANDIDATE_BOUND_RECEIPT_CAPABILITY", EB_FINAL_SEAL_PATH),
    (
        "G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT",
        ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
        "G77_256EE_RUNTIME_CONSUMER_BINDING_CONTRACT_V1.md",
    ),
    ("G77_256EE_RUNTIME_CONSUMER_BINDING_CAPABILITY", EE_FINAL_SEAL_PATH),
    (
        "G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_HARDENING",
        ".github/governance/evidence/g77_256ei_producer_hardening_v1/"
        "G77_256EI_FINAL_VALIDATION_SEAL_V1.json",
    ),
    (
        "G77_256EJ_WRONG_CALLER_FINAL_EVIDENCE",
        ".github/governance/evidence/g77_256ej_p11_operational_v1/"
        "G77_256EJ_SPCE_FINAL_EXECUTION_SEAL_V1.json",
    ),
    (
        "G77_256EK_WRONG_CALLER_COMMITTED_REPORT",
        "docs/governance/G77_256EK_CROSS_ACCOUNT_SPCE_CONTINUATION_OF_INTERRUPTED_G77_256EJ_FROM_AUTHENTICATED_PHASE_A_V1.md",
    ),
    (
        "G77_256EM_AUTHORITATIVE_5_OF_18_FRONTIER",
        ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/"
        "G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json",
    ),
    (
        "G48_REPORTING_STANDARD",
        "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md",
    ),
)


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository_root, text=True
    ).strip()


def load_ei(repository_root: Path) -> ModuleType:
    path = repository_root / EI_PRODUCER_PATH
    spec = importlib.util.spec_from_file_location("g77_256ei_producer_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("EI producer import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module._sha256(path) != "501ec44273fce69b5eb5b30112ab857819d41066fb5f4afec4a7101110968ac9":
        raise RuntimeError("EI producer identity mismatch")
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
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    envelope = du.build_du_fixture(repository_root)
    manifest = envelope["manifest"]
    manifest.update({
        "generation_identity": (
            "G77_256EN_ONE_FRESH_BOUNDED_NON_PRODUCTION_E05_CONSUMED_REUSE_"
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
            "constitutional_frontier": (
                "ONE_HUMAN_AUTHORIZED_FRESH_CONSUMED_REUSE_P11_E05_GENERATION"
            ),
            "exact_next_legal_action": (
                "EB_AND_EE_PRE_MATERIALIZATION_RECEIPTS_BEFORE_ONE_MATERIALIZATION"
            ),
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_CONSUMED",
            "case_id": "G77_256EN_E05_CONSUMED_AUTHORITY_REUSE_DENIAL_001",
        },
        "first_failure_or_current_result": (
            "PENDING__EB_AND_EE_PRE_MATERIALIZATION_VALIDATION_REQUIRED"
        ),
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": ei.canonicalize_prohibitions(
            du, du.REQUIRED_PROHIBITED_ACTIONS
        ),
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "SELECTED_VECTOR_CONSUMED_ONLY",
            "FRESH_ACT_FIRST_AUTHORIZED_EFFECT_THEN_ONE_REUSE_ATTEMPT",
            "EXPECTED_REUSE_DENIAL_AFTER_D1_AND_BEFORE_SECOND_PRECLAIM_LEDGER_APPEND",
            "ONE_FIRST_EFFECT_AND_ZERO_SECOND_PROTECTED_EFFECT_REQUIRED",
            "EB_CANDIDATE_BOUND_RECEIPT_REQUIRED",
            "EE_RUNTIME_CONSUMER_BINDING_RECEIPT_REQUIRED",
            "E05_FRONTIER_REMAINS_FIVE_OF_EIGHTEEN_UNTIL_FINAL_EVIDENCE_AUTHENTICATES",
            "EXACT_DU_PROHIBITION_VOCABULARY_DERIVED_THROUGH_COMMITTED_EI_PRODUCER",
            "QUALIFIED_PROHIBITIONS_DO_NOT_SUBSTITUTE_FOR_EXACT_DU_TOKENS",
        ],
        "extension_bindings": [
            extension(du, repository_root, "G77_256EN_CANDIDATE_BUILDER", BUILDER_PATH),
            extension(du, repository_root, "G77_256EN_P11_HARNESS", HARNESS_PATH),
            extension(du, repository_root, "G77_256EN_RAW_EVIDENCE_SCHEMA", RAW_SCHEMA_PATH),
            extension(du, repository_root, "G77_256EN_CLOUD_INIT_META_DATA", META_DATA_PATH),
            extension(du, repository_root, "G77_256EN_CLOUD_INIT_NETWORK_CONFIG", NETWORK_CONFIG_PATH),
            extension(du, repository_root, "G77_256EN_CLOUD_INIT_USER_DATA", USER_DATA_PATH),
            extension(du, repository_root, "G77_256EI_HARDENED_PRODUCER", EI_PRODUCER_PATH),
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
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    args.output.write_bytes(du.canonical_bytes(build(repository_root)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
