#!/usr/bin/env python3
"""Build the sole repository-only FD WRONG_ATTEMPT preflight candidate."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any


REQUIRED_HEAD = "08b7e7406396b7d6d93023baa30bc689a3aa572f"
REQUIRED_TREE = "b68657113493475e68a9cd36f02e69e0d53ab6b1"
GENERATION_ID = "G77_256FD_REPOSITORY_ONLY_WRONG_ATTEMPT_CANDIDATE_SCHEMA_ALIGNMENT_AND_PREFLIGHT_V1"
ROOT = ".github/governance/evidence/g77_256fd_wrong_attempt_schema_alignment_v1"
EI_PATH = ".github/governance/evidence/g77_256ei_producer_hardening_v1/producer/G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_V1.py"
EI_SHA256 = "501ec44273fce69b5eb5b30112ab857819d41066fb5f4afec4a7101110968ac9"
EB_SEAL = ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/G77_256EB_FINAL_VALIDATION_SEAL_V1.json"
EE_SEAL = ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/G77_256EE_FINAL_VALIDATION_SEAL_V1.json"

LINEAGE = (
    ("G77_256EX_COMMON_SUBSTRATE_CERTIFICATE", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"),
    ("G77_256EX_FINAL_VALIDATION_SEAL", ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_FINAL_VALIDATION_SEAL_V1.json"),
    ("G77_256EW_CANONICAL_SUBSTRATE_MANIFEST", ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"),
    ("G77_256EU_PROSPECTIVE_COUNTER_MODEL", ".github/governance/evidence/g77_256eu_p11_entry_semantics_v1/G77_256EU_P11_ENTRY_SEMANTIC_MODEL_AND_REGRESSION_MATRIX_V1.json"),
    ("G77_256EZ_FINAL_VALIDATION_SEAL", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/G77_256EZ_FINAL_VALIDATION_SEAL_V1.json"),
    ("G77_256EM_AUTHORITATIVE_FRONTIER_MATRIX", ".github/governance/evidence/g77_256em_post_ek_frontier_reduction_v1/G77_256EM_SPCE_PHASE_D_REDUCTION_CHECKPOINT_V1.json"),
    ("G77_256FA_AUTHORITATIVE_6_OF_18_FRONTIER", ".github/governance/evidence/g77_256fa_consumed_operational_v1/G77_256FA_SPCE_PHASE_D_FINAL_CHECKPOINT_V1.json"),
    ("G77_256FC_FAIL_CLOSED_FINAL_SEAL", ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/G77_256FC_FINAL_VALIDATION_SEAL_V1.json"),
    ("G48_REPORTING_STANDARD", "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md"),
)

EXTENSIONS = (
    ("G77_256FD_SPCE_PHASE_A_CHECKPOINT", f"{ROOT}/G77_256FD_SPCE_PHASE_A_CHECKPOINT_V1.json"),
    ("G77_256FD_WRONG_ATTEMPT_VECTOR_EVIDENCE", f"{ROOT}/binding/G77_256FD_WRONG_ATTEMPT_VECTOR_EVIDENCE_V1.json"),
    ("G77_256FD_WRONG_ATTEMPT_PREFLIGHT_ADAPTER", f"{ROOT}/binding/G77_256FD_WRONG_ATTEMPT_PREFLIGHT_ADAPTER_V1.py"),
    ("G77_256FC_WRONG_ATTEMPT_OPERATIONAL_ADAPTER", ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"),
    ("G77_256EZ_STATIC_BINDING_GUARD", ".github/governance/evidence/g77_256ez_static_ee_binding_hardening_v1/validation/G77_256EZ_STATIC_EE_RUNTIME_PATH_BINDING_REGRESSION_V1.py"),
)


def git(repository_root: Path, *arguments: str) -> str:
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
        "current_spce_phase": "PHASE_B_FD_WRONG_ATTEMPT_SCHEMA_ALIGNED_REPOSITORY_PREFLIGHT_CANDIDATE",
        "phase_sequence": 1,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [
            du._seal_binding(repository_root, "G77_256EB_FINAL_VALIDATION_SEAL_V1", EB_SEAL),
            du._seal_binding(repository_root, "G77_256EE_FINAL_VALIDATION_SEAL_V1", EE_SEAL),
        ],
        "execution_counters": du.zero_execution_counters(),
        "case_counters": {"e05_case_execution_count": 0, "wrong_attempt_case_count": 0},
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
            "constitutional_frontier": "FD_REPOSITORY_ONLY_WRONG_ATTEMPT_SCHEMA_ALIGNMENT_AND_DU_EB_EE_PREFLIGHT",
            "exact_next_legal_action": "RUN_DU_ONCE_THEN_EB_THEN_EE_IF_EACH_PRECEDING_VALIDATOR_PASSES__STOP_WITHOUT_OPERATIONAL_EXECUTION",
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": {
            "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
            "case_id": "G77_256FD_E05_WRONG_ATTEMPT_PREFLIGHT_PATTERN_001",
        },
        "first_failure_or_current_result": "PENDING__DU_EB_EE_REPOSITORY_PREFLIGHT_REQUIRED",
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": ei.canonicalize_prohibitions(
            du, du.REQUIRED_PROHIBITED_ACTIONS
        ),
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "HUMAN_AUTHORIZED_SAME_G77_256FD_CROSS_ACCOUNT_REPOSITORY_ONLY_CONTINUATION",
            "P11_E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT_VECTOR_ONLY",
            "AUTHORIZED_ATTEMPT_IDENTITY_G77_256FD_E05_AUTHORIZED_ATTEMPT_PATTERN_001",
            "SUPPLIED_WRONG_ATTEMPT_IDENTITY_G77_256FD_E05_SUPPLIED_WRONG_ATTEMPT_PATTERN_002",
            "ISOLATED_SEMANTIC_MUTATION_FIELD_ATTEMPT_IDENTITY",
            "OBLIGATION_ID_P11_E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
            "OTHER_VECTOR_MUTATION_COUNT_ZERO",
            "ALL_FIVE_DISPLACED_FACTS_HASH_BOUND_BY_VECTOR_EVIDENCE_EXTENSION",
            "EX_CERTIFIED_COMMON_SUBSTRATE_REUSED_NOT_RECONSTRUCTED",
            "REPOSITORY_ONLY_NO_MATERIALIZATION_NO_VM_NO_P11_NO_E05_CREDIT",
            "E05_REMAINS_SIX_OF_EIGHTEEN_AND_WRONG_ATTEMPT_UNSATISFIED",
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
    parser.add_argument("--runtime-output", type=Path, required=True)
    args = parser.parse_args()
    repository_root = args.repo_root.resolve()
    output = args.output.resolve()
    runtime_output = args.runtime_output.resolve()
    if output.exists() or runtime_output.exists():
        raise RuntimeError("FD candidate or runtime projection already exists")
    ei = load_ei(repository_root)
    du = ei.load_du(repository_root)
    payload = du.canonical_bytes(build(repository_root))
    output.parent.mkdir(parents=True, exist_ok=True)
    runtime_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    runtime_output.write_bytes(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
