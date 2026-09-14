"""Authority-free tests for the fresh G77-256LQ WRONG_SCOPE review object."""

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
    "g77_256lq_wrong_scope_fresh_phase_a_review_object_v1/analysis/"
    "G77_256LQ_PHASE_A_REVIEW_OBJECT_VERIFIER_V1.py"
)
SPEC = importlib.util.spec_from_file_location("g77_256lq_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def test_full_replay_reaches_only_human_decision_boundary() -> None:
    first = V.verify()
    second = V.verify()
    assert first == second
    assert first["terminal"] == V.TERMINAL
    assert first["transition"]["state"] in {
        "PENDING_IMMUTABLE_COMMIT_R",
        "IMMUTABLE_REVIEW_IDENTITY_R_COMMITTED__SUCCESSOR_C_REQUIRED",
        "LP_EXACT_TRANSITION_COMPATIBILITY_VERIFIED",
    }


def test_one_canonical_review_object_has_exact_whole_and_inner_hashes() -> None:
    envelope = V.load_canonical(V.REVIEW)
    inner = envelope["review_object"]
    assert len(list(V.LQ.glob("*PHASE_A_REVIEW_OBJECT*.json"))) == 1
    assert envelope["review_object_sha256"] == hashlib.sha256(
        V.canonical_bytes(inner)
    ).hexdigest()
    assert V.sha256_path(V.REVIEW) == V.verify()["review_object_whole_sha256"]


def test_exact_context_scope_and_single_mismatch_are_bound() -> None:
    context = V.load_canonical(V.CONTEXT)
    review = V.load_canonical(V.REVIEW)["review_object"]
    V.FM.fresh_context.validate_context(context, repository_root=ROOT)
    assert review["CANONICAL_CONTEXT_BINDING"] == {
        "path": V.CONTEXT.relative_to(ROOT).as_posix(),
        "context_sha256": context["context_sha256"],
        "whole_file_sha256": V.sha256_path(V.CONTEXT),
        "repository_head": V.ENTRY_HEAD,
        "repository_tree": V.ENTRY_TREE,
        "preauthority_static_readiness_file_sha256": V.sha256_path(V.READINESS),
    }
    mismatch = review["ISOLATED_MISMATCH"]
    assert mismatch["field"] == "authority_scope"
    assert mismatch["expected"] == V.EXPECTED_SCOPE
    assert mismatch["presented"] == V.PRESENTED_SCOPE
    assert mismatch["independent_semantic_mutation_count"] == 1


def test_authority_operation_p11_and_effect_remain_absent() -> None:
    review = V.load_canonical(V.REVIEW)["review_object"]
    expected = {
        "AUTHORITY": "NONE",
        "AUTHORITY_CREATED": "NO",
        "AUTHORITY_CONSUMED": "NO",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "READINESS": "READY_FOR_HUMAN_DECISION",
        "ONE_SHOT_LIMIT": 1,
        "RETRY_LIMIT": 0,
    }
    assert all(review[field] == value for field, value in expected.items())
    assert set(review["STATE_COUNTERS"].values()) == {0}
    assert review["CANDIDATE_HUMAN_ACT_MATERIAL"]["is_authority"] is False


def test_receipt_parent_is_ready_empty_and_nonoperational() -> None:
    context = V.load_canonical(V.CONTEXT)
    readiness = V.load_canonical(V.READINESS)["checkpoint"]
    observation = V.GL.validate_bound_observation(
        ROOT, context, readiness["receipt_parent_claim"]
    )
    assert observation["receipt_parent_ready"] is True
    assert observation["receipt_files_absent"] is True
    assert observation["receipt_namespace_unused"] is True
    assert observation["authority_count"] == 0
    assert observation["operational_execution_count"] == 0


def test_lm_ln_authority_and_approval_cannot_transfer() -> None:
    previous = V.load_canonical(V.REVIEW)["review_object"]["PREVIOUS_LIFECYCLE"]
    assert previous == {
        "LM_OBJECT_REUSED": False,
        "LM_OR_LN_AUTHORITY_REUSED": False,
        "OLD_APPROVAL_INHERITED": False,
        "state": "HISTORICAL_ONLY__TERMINAL__NONTRANSFERABLE",
    }


def test_coherent_copy_and_branch_name_are_not_review_identity(tmp_path: Path) -> None:
    context = V.load_canonical(V.CONTEXT)
    copied = tmp_path / V.CONTEXT.name
    copied.write_bytes(V.CONTEXT.read_bytes())
    assert copied.read_bytes() == V.CONTEXT.read_bytes()
    assert V.FM._committed_review_context_path(ROOT, context) == V.CONTEXT.relative_to(ROOT).as_posix()
    transition = V.load_canonical(V.REVIEW)["review_object"]["LP_TRANSITION_BINDING"]
    assert transition["coherent_copy_sufficient"] is False
    assert transition["branch_name_sufficient"] is False
    assert transition["ancestry_sufficient"] is False


@pytest.mark.parametrize(
    ("field", "wrong"),
    (
        ("AUTHORIZED_SCOPE", V.PRESENTED_SCOPE),
        ("PRESENTED_SCOPE", V.EXPECTED_SCOPE),
        ("AUTHORITY", "PRESENT"),
        ("OPERATION_STATE", "STARTED"),
        ("P11_STATE", "ENTERED"),
        ("PROTECTED_EFFECT", "PRESENT"),
    ),
)
def test_resealed_semantic_or_boundary_mutation_differs_from_review_seal(
    field: str, wrong: str
) -> None:
    envelope = V.load_canonical(V.REVIEW)
    mutated = copy.deepcopy(envelope["review_object"])
    mutated[field] = wrong
    mutated_sha = hashlib.sha256(V.canonical_bytes(mutated)).hexdigest()
    assert mutated_sha != envelope["review_object_sha256"]


def test_noncanonical_or_duplicate_json_is_rejected(tmp_path: Path) -> None:
    pretty = tmp_path / "pretty.json"
    pretty.write_text(json.dumps(V.load_canonical(V.REVIEW), indent=2) + "\n")
    with pytest.raises(V.LQVerificationError, match="NONCANONICAL_JSON"):
        V.load_canonical(pretty)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"schema_id":"a","schema_id":"b"}\n')
    with pytest.raises(V.LQVerificationError, match="DUPLICATE_JSON_KEY"):
        V.load_canonical(duplicate)


def test_forward_compatibility_and_e05_remain_bounded() -> None:
    reduction = V.load_canonical(V.REDUCTION)["reduction"]
    assert reduction["forward_compatibility"] == {
        "AMBIGUOUS": "UNCHANGED",
        "STALE": "STRONGER__FRESH_IDENTITY_AND_NO_ANCESTRY_AUTHORITY",
        "REVOKED": "UNCHANGED",
        "SUPERSEDED": "UNCHANGED",
        "WRONG_SCOPE": "STRONGER_STATIC_BINDING_ONLY__OPERATIONAL_UNSAT",
        "COHERENT_COPY": "STRONGER__LP_CANONICAL_PATH_IDENTITY_BOUND",
    }
    assert reduction["e05"] == {
        "BEFORE": "12/18",
        "LQ_CREDIT": 0,
        "AFTER": "12/18",
        "FRONTIER": "WRONG_SCOPE",
        "WRONG_SCOPE": "UNSAT__OPERATIONAL_DENIAL_NOT_PERFORMED",
    }
    assert reduction["ex"] == {
        "REUSED": "VERIFIED__17_OF_17",
        "RECONSTRUCTED": "VERIFIED__0",
    }
