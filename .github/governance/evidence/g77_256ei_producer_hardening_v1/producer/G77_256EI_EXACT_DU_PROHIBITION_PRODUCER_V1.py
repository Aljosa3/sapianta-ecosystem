#!/usr/bin/env python3
"""Build one non-operational Canonical V1 fixture with exact DU prohibitions."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any, Iterable


REQUIRED_HEAD = "da84f3e5c732c5467ea4f56db0338217f0929022"
REQUIRED_TREE = "dbf4bfab2e3d90160998036042396b25491e6841"
DU_VALIDATOR_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
DU_SCHEMA_PATH = (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_SCHEMA_V1.json"
)
DU_VALIDATOR_SHA256 = "27457993a4e6b778cc65356cd9b17a1bf2665f4e6147608d27dc233ff512304d"
DU_SCHEMA_SHA256 = "a21ba1567c65101a5f178afdfefb5d500c97fc2cc6a9eb9da6c9fb4cc914478e"
EVIDENCE_ROOT = ".github/governance/evidence/g77_256ei_producer_hardening_v1"
PRODUCER_PATH = f"{EVIDENCE_ROOT}/producer/G77_256EI_EXACT_DU_PROHIBITION_PRODUCER_V1.py"
REGRESSION_PATH = (
    f"{EVIDENCE_ROOT}/validation/G77_256EI_PRODUCER_HARDENING_REGRESSION_V1.py"
)
PHASE_A_PATH = f"{EVIDENCE_ROOT}/G77_256EI_SPCE_PHASE_A_CHECKPOINT_V1.json"
POSITIVE_FIXTURE_PATH = (
    f"{EVIDENCE_ROOT}/fixtures/G77_256EI_POSITIVE_CANONICAL_V1_CANDIDATE_V1.json"
)
EXPECTED_DU_PROHIBITIONS = frozenset({
    "VM_CREATION",
    "VM_BOOT",
    "HUMAN_OPERATIONAL_ACT_CREATION",
    "P11_ENTRY",
    "P12_ENTRY",
    "E05_EXECUTION",
    "PRODUCTION_ROUTE",
    "EXECUTION_REPLAY",
})
LINEAGE = (
    (
        "G77_256CD_P11_E05_OBLIGATION_DEFINITION",
        "docs/governance/G77_256CD_P11_PRE_IMPLEMENTATION_EVIDENCE_GENERATION_AND_VALIDATION_PLAN_V1.md",
    ),
    (
        "G77_256DU_CANONICAL_V1_CONTRACT",
        ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
        "G77_256DU_CANONICAL_CONTINUATION_MANIFEST_CONTRACT_V1.md",
    ),
    (
        "G77_256EB_CANDIDATE_BOUND_VALIDATION_CAPABILITY",
        ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v1/"
        "G77_256EB_FINAL_VALIDATION_SEAL_V1.json",
    ),
    (
        "G77_256EE_RUNTIME_CONSUMER_BINDING_CAPABILITY",
        ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v1/"
        "G77_256EE_FINAL_VALIDATION_SEAL_V1.json",
    ),
    (
        "G77_256EG_REJECTED_CANDIDATE",
        ".github/governance/evidence/g77_256eg_p11_operational_v1/raw/"
        "G77_256EG_CANONICAL_CONTINUATION_MANIFEST_PRE_MATERIALIZATION_V1.json",
    ),
    (
        "G77_256EG_FIRST_AUTHORITATIVE_FAILURE",
        ".github/governance/evidence/g77_256eg_p11_operational_v1/"
        "G77_256EG_PRE_MATERIALIZATION_ADMISSION_FAILURE_V1.json",
    ),
    (
        "G77_256EH_TRUTHFUL_FAIL_CLOSED_FINALIZATION",
        "docs/governance/"
        "G77_256EH_CROSS_ACCOUNT_SPCE_RECOVERY_AND_TRUTHFUL_FAIL_CLOSED_"
        "FINALIZATION_OF_INTERRUPTED_G77_256EG_V1.md",
    ),
    (
        "G48_REPORTING_STANDARD",
        "docs/governance/G48_00_CONSTITUTIONAL_EVIDENCE_REPORTING_STANDARD_V1.md",
    ),
)


class ProducerHardeningError(ValueError):
    """One fail-closed producer-hardening rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def git(repository_root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository_root, text=True
    ).strip()


def authenticate_baseline(repository_root: Path) -> None:
    if git(repository_root, "rev-parse", "HEAD") != REQUIRED_HEAD:
        raise ProducerHardeningError("REQUIRED_HEAD_MISMATCH", "required HEAD differs")
    if git(repository_root, "rev-parse", "HEAD^{tree}") != REQUIRED_TREE:
        raise ProducerHardeningError("REQUIRED_TREE_MISMATCH", "required tree differs")


def load_du(repository_root: Path) -> ModuleType:
    validator = repository_root / DU_VALIDATOR_PATH
    schema = repository_root / DU_SCHEMA_PATH
    if _sha256(validator) != DU_VALIDATOR_SHA256:
        raise ProducerHardeningError(
            "DU_VALIDATOR_IDENTITY_MISMATCH", "committed DU validator bytes differ"
        )
    if _sha256(schema) != DU_SCHEMA_SHA256:
        raise ProducerHardeningError(
            "DU_SCHEMA_IDENTITY_MISMATCH", "committed DU schema bytes differ"
        )
    spec = importlib.util.spec_from_file_location("g77_256du_validator_v1", validator)
    if spec is None or spec.loader is None:
        raise ProducerHardeningError("DU_IMPORT_FAILED", "DU validator import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual = frozenset(module.REQUIRED_PROHIBITED_ACTIONS)
    if actual != EXPECTED_DU_PROHIBITIONS:
        raise ProducerHardeningError(
            "DU_VOCABULARY_IDENTITY_MISMATCH",
            "committed DU required vocabulary differs from authenticated EI baseline",
        )
    return module


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse_vocabulary_reinterpretation(
    du: ModuleType, proposed_required: Iterable[str]
) -> None:
    if frozenset(proposed_required) != frozenset(du.REQUIRED_PROHIBITED_ACTIONS):
        raise ProducerHardeningError(
            "DU_VOCABULARY_REINTERPRETATION_FORBIDDEN",
            "producer cannot replace or reinterpret DU required tokens",
        )


def canonicalize_prohibitions(
    du: ModuleType, values: Iterable[str]
) -> list[str]:
    supplied = list(values)
    if any(not isinstance(value, str) or not value for value in supplied):
        raise ProducerHardeningError(
            "PROHIBITION_TOKEN_INVALID", "prohibitions must be non-empty strings"
        )
    required = frozenset(du.REQUIRED_PROHIBITED_ACTIONS)
    canonical = sorted(set(supplied) | required)
    if not required.issubset(canonical):
        raise ProducerHardeningError(
            "REQUIRED_DU_PROHIBITION_ABSENT",
            "producer output omitted an exact DU required token",
        )
    return canonical


def assert_exact_required_tokens(du: ModuleType, values: Iterable[str]) -> None:
    required = frozenset(du.REQUIRED_PROHIBITED_ACTIONS)
    actual = frozenset(values)
    missing = required - actual
    if missing:
        raise ProducerHardeningError(
            "REQUIRED_DU_PROHIBITION_ABSENT",
            f"producer output omitted exact DU tokens: {sorted(missing)}",
        )


def extension(
    du: ModuleType, repository_root: Path, identity: str, relative_path: str
) -> dict[str, str]:
    return {
        "identity": identity,
        "path": relative_path,
        "sha256": du.sha256_path(repository_root / relative_path),
    }


def build(repository_root: Path) -> dict[str, Any]:
    authenticate_baseline(repository_root)
    du = load_du(repository_root)
    refuse_vocabulary_reinterpretation(du, EXPECTED_DU_PROHIBITIONS)
    envelope = du.build_du_fixture(repository_root)
    manifest = envelope["manifest"]
    exact_prohibitions = canonicalize_prohibitions(
        du, du.REQUIRED_PROHIBITED_ACTIONS
    )
    assert_exact_required_tokens(du, exact_prohibitions)
    manifest.update({
        "generation_identity": (
            "G77_256EI_REPOSITORY_ONLY_POSITIVE_CANONICAL_V1_"
            "PRODUCER_HARDENING_FIXTURE_V1"
        ),
        "required_head": REQUIRED_HEAD,
        "source_tree": REQUIRED_TREE,
        "current_spce_phase": "PHASE_C_REPOSITORY_ONLY_PRODUCER_VALIDATION",
        "phase_sequence": 0,
        "prior_manifest_sha256": None,
        "completed_phase_seals": [],
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
                "REPOSITORY_ONLY_EXACT_DU_PROHIBITION_PRODUCER_HARDENING"
            ),
            "exact_next_legal_action": (
                "HUMAN_REVIEW_AND_OPTIONAL_COMMIT_OF_G77_256EI__THEN_"
                "SEPARATE_HUMAN_AUTHORIZATION_FOR_ANY_FRESH_OPERATIONAL_GENERATION"
            ),
            "continuation_mode": "PRE_MATERIALIZATION_VALIDATION_ONLY",
            "requires_human_review": True,
        },
        "selected_case": None,
        "first_failure_or_current_result": (
            "PENDING_REPOSITORY_ONLY_DU_AND_EB_VALIDATION__NO_OPERATIONAL_AUTHORITY"
        ),
        "teardown_state": "NOT_APPLICABLE",
        "final_execution_seal": None,
        "prohibited_actions": exact_prohibitions,
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "auto_continuable": False,
        "observations": [
            "NON_OPERATIONAL_POSITIVE_PRODUCER_HARDENING_FIXTURE",
            "EXACT_DU_PROHIBITION_VOCABULARY_IS_AUTHORITATIVE",
            "QUALIFIED_REPLACEMENTS_CANNOT_SUBSTITUTE_FOR_EXACT_DU_TOKENS",
            "NO_VM_MATERIALIZATION_BOOT_COMMISSIONING_P11_E05_P12_OR_PRODUCTION",
            "WRONG_CALLER_REMAINS_UNSATISFIED_AND_E05_REMAINS_FOUR_OF_EIGHTEEN",
        ],
        "extension_bindings": [
            extension(du, repository_root, "G77_256EI_PHASE_A", PHASE_A_PATH),
            extension(du, repository_root, "G77_256EI_HARDENED_PRODUCER", PRODUCER_PATH),
            extension(du, repository_root, "G77_256EI_REGRESSION_RUNNER", REGRESSION_PATH),
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
    expected_output = repository_root / POSITIVE_FIXTURE_PATH
    if args.output.resolve() != expected_output.resolve():
        raise ProducerHardeningError(
            "OUTPUT_SCOPE_INVALID", "EI CLI may create only the authorized positive fixture"
        )
    du = load_du(repository_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(du.canonical_bytes(build(repository_root)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
