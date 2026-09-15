"""Pure verification for the fresh, authority-free G77-256LV Phase A."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[5]
VERIFIER = ROOT / (
    ".github/governance/evidence/"
    "g77_256lv_fresh_wrong_scope_phase_a_review_object_v1/analysis/"
    "G77_256LV_PHASE_A_REVIEW_OBJECT_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lv_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def test_full_replay_is_deterministic_and_stops_at_human_boundary() -> None:
    first = V.verify()
    second = V.verify()
    assert first == second
    assert first["terminal"] == V.TERMINAL
    assert first["transition"]["transition_is_authority"] is False
    assert first["transition"]["transition_consumable"] is False


def test_exactly_one_fresh_review_object_has_inner_and_whole_hashes() -> None:
    envelope = V.load_canonical(V.REVIEW)
    assert len(list(V.LV.glob("*PHASE_A_REVIEW_OBJECT*.json"))) == 1
    assert envelope["review_object_sha256"] == hashlib.sha256(
        V.canonical_bytes(envelope["review_object"])
    ).hexdigest()
    assert V.sha256_path(V.REVIEW) == V.verify()["review_object_whole_sha256"]
    assert len({V.LIFECYCLE_ID, V.OBJECT_ID, V.REVIEW_ID, V.CONTEXT_ID, V.PRESENTATION_ID}) == 5


def test_exact_lu_context_scope_and_single_mismatch_are_bound() -> None:
    context = V.load_canonical(V.CONTEXT)
    review = V.load_canonical(V.REVIEW)["review_object"]
    V.FM.fresh_context.validate_context(context, repository_root=V.ROOT)
    assert context["repository_head"] == V.ENTRY_HEAD
    assert context["repository_tree"] == V.ENTRY_TREE
    assert review["AUTHORIZED_SCOPE"] == V.AUTHORIZED_SCOPE
    assert review["PRESENTED_SCOPE"] == V.PRESENTED_SCOPE
    assert review["ISOLATED_MISMATCH"] == {
        "field": "authority_scope",
        "expected": V.AUTHORIZED_SCOPE,
        "presented": V.PRESENTED_SCOPE,
        "independent_semantic_mutation_count": 1,
        "preserved_dimensions": [
            "authority_kind",
            "authority_lifecycle_state",
            "attempt_identity",
            "input_identity",
            "contract_identity",
            "provenance_identity",
            "validity_interval_and_currentness",
            "target_owner_and_revision",
            "caller_identity",
        ],
    }


def test_authority_human_decision_operation_and_effect_boundary() -> None:
    review = V.load_canonical(V.REVIEW)["review_object"]
    assert review["ARTIFACT_CLASS"] == "HUMAN_REVIEW_OBJECT__NONAUTHORITY__NONCONSUMABLE__NONOPERATIONAL"
    assert review["AUTHORITY_STATE"] == "NONE"
    assert review["HUMAN_DECISION_STATE"] == "PENDING"
    assert review["OPERATION_STATE"] == "NOT_STARTED"
    assert review["RETRY_LIMIT"] == 0
    assert review["P11_STATE"] == "NOT_ENTERED"
    assert review["PROTECTED_EFFECT_STATE"] == "NONE_IN_LV"
    assert set(review["STATE_COUNTERS"].values()) == {0}
    assert review["CANDIDATE_HUMAN_ACT_MATERIAL"]["is_authority"] is False


def test_lq_lr_nonreuse_and_historical_unknown_preserved() -> None:
    previous = V.load_canonical(V.REVIEW)["review_object"]["PREVIOUS_LIFECYCLE"]
    assert previous["LQ_APPROVAL_REUSED"] is False
    assert previous["LR_AUTHORITY_REUSED"] is False
    assert previous["LR_INVOCATION_REUSED"] is False
    assert previous["LR_RECEIPT_NAMESPACE_REUSED"] is False
    assert previous["LR_OPERATION_IDENTITY_REUSED"] is False
    assert previous["LR_OUTCOME"] == "UNKNOWN__PRESERVED_WITHOUT_ZERO_ENCODING"


def test_receipt_namespace_is_fresh_empty_and_nonoperational() -> None:
    context = V.load_canonical(V.CONTEXT)
    checkpoint = V.load_canonical(V.READINESS)["checkpoint"]
    observation = V.GL.validate_bound_observation(
        V.ROOT, context, checkpoint["receipt_parent_claim"]
    )
    assert observation["receipt_parent_ready"] is True
    assert observation["receipt_files_absent"] is True
    assert observation["receipt_namespace_unused"] is True
    assert observation["authority_count"] == 0
    assert observation["operational_execution_count"] == 0
    assert "g77_256lr" not in context["receipt_parent"].lower()


def test_lt_lu_are_readiness_not_authority_or_operational_proof() -> None:
    predecessor = V.load_canonical(V.REVIEW)["review_object"]["PREDECESSOR_READINESS"]
    assert predecessor == {
        "LT_CAPABILITY": "IMPLEMENTED__READINESS_ONLY__NONAUTHORITY",
        "LU_INTEGRATION": "PROVEN__STATIC_ONLY__NONOPERATIONAL",
        "authority_or_permission_transferred": False,
        "acceptance_credit_transferred": False,
    }


def test_transition_rejects_generic_identity_and_remains_nonauthority() -> None:
    review = V.load_canonical(V.REVIEW)["review_object"]
    transition = review["LP_TRANSITION_BINDING"]
    assert transition["ancestry_sufficient"] is False
    assert transition["branch_name_sufficient"] is False
    assert transition["coherent_copy_sufficient"] is False
    assert transition["transition_is_authority"] is False
    assert transition["transition_consumable"] is False


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("AUTHORIZED_SCOPE", V.PRESENTED_SCOPE),
        ("PRESENTED_SCOPE", V.AUTHORIZED_SCOPE),
        ("AUTHORITY_STATE", "PRESENT"),
        ("HUMAN_DECISION_STATE", "APPROVED"),
        ("OPERATION_STATE", "STARTED"),
        ("P11_STATE", "ENTERED"),
        ("PROTECTED_EFFECT_STATE", "PRESENT"),
    ),
)
def test_resealed_boundary_mutation_changes_inner_hash(field: str, wrong: str) -> None:
    envelope = V.load_canonical(V.REVIEW)
    mutated = copy.deepcopy(envelope["review_object"])
    mutated[field] = wrong
    assert hashlib.sha256(V.canonical_bytes(mutated)).hexdigest() != envelope["review_object_sha256"]


def test_noncanonical_and_duplicate_json_fail_closed(tmp_path: Path) -> None:
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(V.load_canonical(V.REVIEW), indent=2) + "\n")
    with pytest.raises(V.LVVerificationError, match="NONCANONICAL_JSON"):
        V.load_canonical(pretty)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema_id":"a","schema_id":"b"}\n')
    with pytest.raises(V.LVVerificationError, match="DUPLICATE_JSON_KEY"):
        V.load_canonical(duplicate)


def test_forward_compatibility_ex_and_e05_remain_bounded() -> None:
    reduction = V.load_canonical(V.REDUCTION)["reduction"]
    assert "WEAKER" not in set(reduction["forward_compatibility"].values())
    assert reduction["ex"] == {
        "EX_REUSED": "VERIFIED__17_OF_17",
        "EX_RECONSTRUCTED": "VERIFIED__0",
    }
    assert reduction["e05"] == {
        "E05_BEFORE": "12/18",
        "LV_E05_CREDIT": 0,
        "E05_AFTER": "12/18",
        "WRONG_SCOPE_STATUS": "UNSAT",
    }


def test_terminal_decision_contains_required_boundary_and_frontier() -> None:
    decision = V.load_canonical(V.DECISION)["decision"]
    assert decision == V.build_decision(V.load_canonical(V.CONTEXT))
    assert decision["MINIMUM_MISSING_CAPABILITY"] == "NONE"
    assert decision["MINIMUM_LEGAL_NEXT_DELTA"] == "INDEPENDENT_HUMAN_REVIEW_AND_DECISION_OVER_EXACT_LV_OBJECT"
    assert decision["OPERATIONAL_RETRY_AUTHORIZED"] == "NO"


def test_presentation_hash_and_content_recompute_exactly() -> None:
    result = V.verify()
    assert result["presentation_sha256"] == V.sha256_path(V.PRESENTATION)
    text = V.PRESENTATION.read_text(encoding="utf-8")
    assert text == V.render_presentation(
        V.load_canonical(V.CONTEXT), V.load_canonical(V.REVIEW)
    )
    assert "HUMAN_DECISION_STATE = PENDING" in text
