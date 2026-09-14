"""Focused authority-free tests for G77-256LO lifecycle discovery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
LO = ROOT / ".github/governance/evidence/g77_256lo_phase_a_phase_b_lifecycle_discovery_v1"
VERIFIER = LO / "analysis/G77_256LO_PHASE_A_TO_PHASE_B_LIFECYCLE_DISCOVERY_V1.py"
REPORT = LO / "G77_256LO_G48_IMPLEMENTATION_REPORT_V1.md"
SPEC = importlib.util.spec_from_file_location("g77_256lo_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def test_ln_entry_sources_and_nested_authority_are_authenticated() -> None:
    entry = V.authenticate_entry()
    assert entry["entry_head"] == V.ENTRY_HEAD
    assert entry["entry_tree"] == V.ENTRY_TREE
    V.authenticate_sources()


def test_fm_owns_three_existing_identities_but_not_committed_review_transition() -> None:
    owners = V.authenticate_fm_identity_model()
    assert owners["phase_a_repository_identity_owner"].startswith("FM_BUILD")
    assert owners["current_admission_identity_owner"].startswith("FM_AUTHENTICATE")
    assert owners["runtime_checkout_identity_owner"] == "FM_GOVERNED_CHECKOUT_IDENTITY"
    assert owners["committed_review_object_identity_owner"] == "ABSENT"


def test_li_through_ln_trace_preserves_static_vs_operational_distinction() -> None:
    trace = V.authenticate_wrong_scope_trace()
    assert trace["LI"].endswith("SELF_INVALIDATED")
    assert "STATIC_READINESS" in trace["LJ"]
    assert "SKIPPED_OPERATIONAL_CURRENT_ADMISSION" in trace["LM"]
    assert "REJECTED" in trace["LN"]


def test_all_seven_operational_precedents_avoid_a_committed_phase_a_boundary() -> None:
    cases = [V.authenticate_wrong_caller_precedent(), *V.authenticate_modern_precedents()]
    assert [case["vector"] for case in cases] == [
        "WRONG_CALLER", "WRONG_ATTEMPT", "WRONG_INPUT", "WRONG_CONTRACT",
        "WRONG_PROVENANCE", "FUTURE", "EXPIRED",
    ]
    assert all(case["phase_a_preparatory_commit_occurred"] is True for case in cases)
    assert all(case["operation_specific_phase_a_committed_before_phase_b"] is False for case in cases)
    assert all(case["phase_b_repository_relation"] == "SAME_COMMIT" for case in cases)
    assert all(case["authority_transfer"] == "NO" for case in cases)
    assert all(case["proof_transfer"] == "NO" for case in cases)
    assert all(case["e05_credit_transfer"] == "NO" for case in cases)


def test_existing_same_head_ordering_is_safe_but_does_not_answer_primary_question() -> None:
    V.authenticate_kv_precedent()
    reduction = V.build_reduction()
    target = reduction["target_lifecycle_requirement"]
    assessment = reduction["cross_vector_reuse_assessment"]
    assert target["committed_operation_specific_phase_a_required"] is True
    assert target["universal_constitutional_requirement"] == "NOT_PROVEN"
    assert len(assessment) == 8
    assert assessment[0]["vector"] == "WRONG_SCOPE"
    assert assessment[0]["e05_status"].startswith("UNSAT")
    assert all(case["authority_transfer"] == "NO" for case in assessment)
    assert all(case["proof_transfer"] == "NO" for case in assessment)
    assert all(case["e05_credit_transfer"] == "NO" for case in assessment)
    primary = reduction["primary_answer"]
    assert primary["satisfies_committed_phase_a_successor_requirement"] is False
    assert primary["production_mutation_required"] is True
    assert primary["implemented"] is False


def test_naive_fixes_are_rejected_and_future_stale_proofs_remain_possible() -> None:
    security = V.build_reduction()["security_assessment"]
    for key in (
        "arbitrary_ancestor_acceptance", "sealed_object_rebind", "mutable_branch_identity",
        "fm_bypass", "wrong_scope_only_route", "coherent_copy_inherits_approval",
    ):
        assert security[key].startswith("REJECT__")
    assert "NO_COPY_ACCEPTANCE" in security["coherent_copy_impact"]
    assert "NO_ANCESTOR_ACCEPTANCE" in security["stale_identity_impact"]


def test_terminal_reduction_is_sealed_zero_authority_and_zero_operation() -> None:
    result = V.verify()
    reduction = result["reduction"]
    envelope = json.loads(V.REDUCTION.read_text())
    assert result["terminal"] == V.TERMINAL
    assert reduction["outcome"] == "E__MINIMUM_PRODUCTION_CAPABILITY_GAP_PROVEN"
    assert hashlib.sha256(V.canonical_bytes(reduction)).hexdigest() == envelope["reduction_sha256"]
    assert set(reduction["operational_counters"].values()) == {0}
    assert set(reduction["architecture"].values()) == {0, 1}
    assert reduction["e05"] == {"before": "12/18", "lo_credit": 0, "after": "12/18", "wrong_scope": "UNSAT"}


def test_g48_report_has_exactly_six_h1_and_five_exact_reuse_questions() -> None:
    text = REPORT.read_text()
    assert [line for line in text.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    questions = (
        "1. Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "2. Katere nove zmogljivosti (če sploh) nastanejo?",
        "3. Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "4. Ali implementacija ustvarja vzporedni tok?",
        "5. Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(text.count(question) == 1 for question in questions)
    assert text.rstrip().endswith(V.TERMINAL)
