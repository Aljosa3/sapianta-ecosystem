"""Focused authority-free proof for G77-256LM receipt-parent Phase A."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lm_wrong_scope_receipt_parent_phase_a_v1/analysis/"
    "G77_256LM_PHASE_A_LIFECYCLE_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lm_lifecycle", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_ll_entry_terminal_and_nested_authority_are_authenticated() -> None:
    repository = V.authenticate_repository()
    assert repository["entry_head"] == V.ENTRY_HEAD
    assert repository["entry_tree"] == V.ENTRY_TREE
    V.authenticate_sources()


def test_root_cause_is_existing_authority_free_materialization() -> None:
    fact = V.root_cause_fact()
    assert fact["classification"].startswith("B__EXISTING_DERIVED_AUTHORITY_FREE")
    assert fact["authenticated_owner"] == "EXISTING_GA_CERTIFIED_FM_PREPARE_RECEIPT_PARENT"
    assert fact["creation_is_authority_free"] is True
    assert fact["creation_is_operational_attempt"] is False
    assert fact["new_capability_required"] == "NO"
    assert fact["production_owner_or_route_change_required"] is False


def test_existing_gl_fm_owner_revalidates_exact_receipt_parent() -> None:
    context = V.load_canonical(V.CONTEXT)
    claim = V.load_canonical(V.OBSERVATION)
    observed = V.GL.validate_bound_observation(V.ROOT, context, claim)
    assert observed["receipt_parent"] == context["receipt_parent"]
    assert observed["receipt_parent_ready"] is True
    assert observed["receipt_namespace_unused"] is True
    assert observed["authority_count"] == 0
    assert observed["operational_execution_count"] == 0


def test_preauthorization_matches_unchanged_final_admission_subcheck() -> None:
    context = V.load_canonical(V.CONTEXT)
    claim = V.load_canonical(V.OBSERVATION)
    checkpoint = V.GL.reduce_preauthorization_checkpoint(V.ROOT, context, claim)
    proof = V.GL.validate_preauth_final_admission_equivalence(
        V.ROOT, context, claim, checkpoint
    )
    assert proof["preauth_final_admission_equivalence"] == V.GL.EQUIVALENCE_RESULT
    assert proof["human_constitutional_authorization_count"] == 0
    assert proof["operational_execution_count"] == 0


def test_exactly_one_fresh_wrong_scope_decision_object_is_sealed() -> None:
    envelope = V.load_canonical(V.DECISION)
    decision = envelope["decision_object"]
    assert envelope["decision_object_sha256"] == V.sha256_bytes(
        V.canonical_bytes(decision)
    )
    assert len(list(V.LM.glob("*DECISION_OBJECT*.json"))) == 1
    assert decision["DECISION_OBJECT_ID"] == V.DECISION_ID
    assert decision["CANONICAL_OPERATION_ID"] == V.OPERATION
    assert decision["VECTOR"] == "WRONG_SCOPE"


def test_scope_is_the_only_independent_semantic_mismatch() -> None:
    decision = V.load_canonical(V.DECISION)["decision_object"]
    mismatch = decision["ISOLATED_SCOPE_MISMATCH"]
    assert mismatch["independent_semantic_mutation_count"] == 1
    assert mismatch["independent_semantic_mutation_field"] == "authority_scope"
    assert mismatch["expected"] == V.EXPECTED_SCOPE
    assert mismatch["presented"] == V.PRESENTED_SCOPE


def test_all_authority_operation_entry_and_effect_counters_are_zero() -> None:
    decision = V.load_canonical(V.DECISION)["decision_object"]
    reduction = V.load_canonical(V.REDUCTION)["reduction"]
    assert set(decision["STATE_COUNTERS"].values()) == {0}
    assert set(reduction["operational_counters"].values()) == {0}
    assert decision["AUTHORITY_STATE"] == "NONE"
    assert decision["OPERATION_STATE"] == "NOT_STARTED"
    assert decision["P11_ENTRY_STATE"] == "NOT_ENTERED"
    assert decision["PROTECTED_EFFECT_STATE"] == "NONE"


def test_ll_authority_and_cross_vector_credit_do_not_transfer() -> None:
    reduction = V.load_canonical(V.REDUCTION)["reduction"]
    assert reduction["ll_authority"]["reused"] is False
    assert reduction["ll_authority"]["transfer"] == "NO"
    rows = reduction["cross_vector_reuse_assessment"]
    assert [row["VECTOR"] for row in rows] == [
        "WRONG_SCOPE", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT",
        "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE", "EXPIRED",
    ]
    assert all(
        row["AUTHORITY_TRANSFER"] == row["PROOF_TRANSFER"]
        == row["E05_CREDIT_TRANSFER"] == "NO"
        for row in rows
    )


def test_replay_is_deterministic_and_stops_at_human_boundary() -> None:
    first = V.verify()
    second = V.verify()
    assert first == second
    assert first["terminal"] == V.TERMINAL
    assert first["receipt_parent_ready"] is True
    assert first["authority_creation_count"] == 0
    assert first["operation_attempt_count"] == 0
    assert first["ready_for_human_decision"] is True


def test_human_presentation_binds_whole_file_and_inner_identities() -> None:
    envelope = V.load_canonical(V.DECISION)
    text = V.PRESENTATION.read_text(encoding="utf-8")
    assert V.sha256_path(V.DECISION) in text
    assert envelope["decision_object_sha256"] in text
    assert "THIS OBJECT IS NOT AUTHORIZED." in text
    assert "LL AUTHORITY IS TERMINAL AND MUST NOT BE REUSED." in text
    assert "READY_FOR_HUMAN_DECISION = YES" in text
