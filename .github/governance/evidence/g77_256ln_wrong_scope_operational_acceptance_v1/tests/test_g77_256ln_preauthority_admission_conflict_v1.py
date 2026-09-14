"""Focused fail-closed tests for the G77-256LN pre-authority conflict."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
LN = ROOT / (
    ".github/governance/evidence/"
    "g77_256ln_wrong_scope_operational_acceptance_v1"
)
VERIFIER = LN / "analysis/G77_256LN_PREAUTHORITY_ADMISSION_CONFLICT_VERIFIER_V1.py"
REDUCTION = LN / "G77_256LN_SPCE_PREAUTHORITY_TERMINAL_REDUCTION_V1.json"
REPORT = LN / "G77_256LN_G48_IMPLEMENTATION_REPORT_V1.md"
SPEC = importlib.util.spec_from_file_location("g77_256ln_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_lm_entry_and_sources_are_authenticated() -> None:
    entry = V.authenticate_repository()
    assert entry["entry_head"] == V.ENTRY_HEAD
    assert entry["entry_tree"] == V.ENTRY_TREE
    V.authenticate_sources()


def test_exact_decision_and_receipt_identities_are_authenticated() -> None:
    decision, context = V.authenticate_phase_a()
    assert decision["DECISION_OBJECT_ID"] == V.DECISION_ID
    assert decision["CANONICAL_OPERATION_ID"] == V.OPERATION_ID
    assert decision["ISOLATED_SCOPE_MISMATCH"][
        "independent_semantic_mutation_field"
    ] == "authority_scope"
    assert context["repository_head"] == V.LL_HEAD


def test_current_admission_rejects_the_stale_sealed_route_before_authority() -> None:
    _, context = V.authenticate_phase_a()
    conflict = V.prove_preauthority_final_admission_conflict(context)
    assert conflict["error"] == V.FAILURE
    assert conflict["sealed_materialization_head"] == V.LL_HEAD
    assert conflict["current_admission_head"] == V.ENTRY_HEAD
    assert conflict["first_failed_conjunct"].startswith("FM_AUTHORITY_FREE")


def test_no_ln_authority_operation_or_consumed_receipt_exists() -> None:
    V.authenticate_zero_authority_operation()
    result = V.verify()
    assert result["human_authority_source_count"] == 0
    assert result["authority_creation_count"] == 0
    assert result["authority_consumption_count"] == 0
    assert result["operation_attempt_count"] == 0
    assert result["qemu_start_count"] == 0
    assert result["p11_entry_count"] == 0
    assert result["protected_effect_count"] == 0


def test_terminal_reduction_is_sealed_and_truthful() -> None:
    envelope = json.loads(REDUCTION.read_text(encoding="utf-8"))
    reduction = envelope["reduction"]
    digest = hashlib.sha256(V.canonical_bytes(reduction)).hexdigest()
    assert digest == envelope["reduction_sha256"]
    assert reduction["terminal"] == V.TERMINAL
    assert reduction["failure_novelty_and_convergence_check"]["failure_class"] == (
        "DUPLICATE_OR_EQUIVALENT_EDGE"
    )
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "BEFORE": "12/18",
        "LN_CREDIT": 0,
        "AFTER": "12/18",
        "WRONG_SCOPE": "UNSAT__NO_OPERATIONAL_ATTEMPT",
    }


def test_g48_report_has_exactly_six_h1_headings() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert text.rstrip().endswith(V.TERMINAL)
