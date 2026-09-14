"""Focused authority-free tests for the G77-256LK Human decision boundary."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lk_wrong_scope_fresh_phase_a_decision_v1/analysis/"
    "G77_256LK_PHASE_A_DECISION_OBJECT_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lk_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_lj_base_and_stable_runtime_are_authenticated() -> None:
    repository = V.authenticate_repository()
    assert repository["base_head"] == V.BASE_HEAD
    assert repository["base_tree"] == V.BASE_TREE
    V.authenticate_sources()
    model = V.authenticate_wrong_scope_static_semantics()
    assert model["independent_semantic_mutation_count"] == 1
    assert model["independent_semantic_mutation_set"] == [
        f"authority_scope:{V.EXPECTED_SCOPE}->{V.PRESENTED_SCOPE}"
    ]


def test_exactly_one_fresh_sealed_decision_object_exists() -> None:
    decision = V.authenticate_decision_object()
    assert decision["DECISION_OBJECT_ID"] == V.DECISION_ID
    assert decision["VECTOR"] == "WRONG_SCOPE"
    assert decision["ISOLATED_SCOPE_MISMATCH"][
        "independent_semantic_mutation_count"
    ] == 1
    assert len(list(V.LK.glob("*DECISION_OBJECT*.json"))) == 1


def test_candidate_material_is_review_only_and_not_human_authority() -> None:
    candidate = V.authenticate_decision_object()["CANDIDATE_HUMAN_ACT_MATERIAL"]
    assert candidate["is_authority"] is False
    assert candidate["human_authority_source_bytes_state"] == "ABSENT"
    assert candidate["human_actor_identity_state"] == "ABSENT"
    assert candidate["authority_act_identity_state"].startswith("UNMATERIALIZED")
    assert candidate["payload_digest_state"] == "UNMATERIALIZED"


def test_all_authority_operation_and_effect_counters_are_zero() -> None:
    counters = V.authenticate_decision_object()["STATE_COUNTERS"]
    assert counters
    assert set(counters.values()) == {0}


def test_human_presentation_is_exactly_bound_to_sealed_object() -> None:
    decision = V.authenticate_decision_object()
    V.authenticate_presentation(decision)


def test_replay_is_deterministic_and_stops_at_human_boundary() -> None:
    first = V.verify()
    second = V.verify()
    assert first == second
    assert first["terminal"] == V.TERMINAL
    assert first["authority_creation_count"] == 0
    assert first["operation_attempt_count"] == 0
    assert first["ready_for_human_decision"] is True


def test_terminal_reduction_is_canonical_sealed_and_complete() -> None:
    envelope = V.load_canonical(V.REDUCTION)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == V.sha256_bytes(
        V.canonical_bytes(reduction)
    )
    assert reduction["terminal"] == V.TERMINAL
    assert reduction["decision_object"]["count"] == 1
    assert reduction["phase_a"]["independent_semantic_mutation_count"] == 1
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {
        "AFTER": "12/18",
        "BEFORE": "12/18",
        "FRONTIER": "WRONG_SCOPE",
        "LK_CREDIT": 0,
        "WRONG_SCOPE": (
            "UNSAT__PHASE_A_READY__HUMAN_DECISION_PENDING__OPERATIONAL_UNPROVEN"
        ),
    }
    assert [row["VECTOR"] for row in reduction["cross_vector_reuse_assessment"]] == [
        "WRONG_SCOPE", "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT",
        "WRONG_CONTRACT", "WRONG_PROVENANCE", "FUTURE", "EXPIRED",
    ]
    assert all(
        row["AUTHORITY_TRANSFER"] == row["PROOF_TRANSFER"]
        == row["E05_CREDIT_TRANSFER"] == "NO"
        for row in reduction["cross_vector_reuse_assessment"]
    )


def test_g48_report_has_exactly_six_required_h1_headings() -> None:
    text = V.REPORT.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert text.rstrip().endswith(V.TERMINAL)
    assert "THIS OBJECT IS NOT AUTHORIZED" in text
    assert "APPROVAL HAS NOT YET BEEN GIVEN" in text
    assert "NO OPERATION MAY START FROM THIS GENERATION" in text
