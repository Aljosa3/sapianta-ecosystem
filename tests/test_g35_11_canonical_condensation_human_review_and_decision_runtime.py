from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime.canonical_governed_development_condensation_human_decision_runtime import (
    CANONICAL_CONDENSATION_APPROVE,
    CANONICAL_CONDENSATION_REJECT,
    create_canonical_condensation_human_decision,
    validate_canonical_condensation_human_decision,
)
from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
    CANONICAL_CONDENSATION_REVIEW_WARNING,
    create_canonical_condensation_human_review,
    render_canonical_condensation_human_review,
    validate_canonical_condensation_human_review,
)
from aigol.runtime.canonical_governed_development_condensation_replay import (
    reconstruct_canonical_condensation_review_decision_replay,
    record_canonical_condensation_phase1_replay,
    record_canonical_condensation_review_decision_replay,
)
from aigol.runtime.canonical_governed_development_condensation_runtime import (
    G31_CODEX_SYNTHESIS_PREFIX,
    create_canonical_condensation_proposal,
)
from aigol.runtime.canonical_governed_development_condensation_validation_runtime import (
    validate_canonical_condensation_proposal,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


REPRESENTATIONS = {
    "requested_capability": "condense",
    "user_visible_outcome": "bounded task",
    "allowed_operations": "read source",
    "prohibited_operations": "no mutation",
    "architectural_placement": "pre-G31",
    "acceptance_conditions": "all mapped",
    "testing_validation_requirements": "deterministic",
    "explicit_exclusions": "no execution",
    "safety_governance_constraints": "fail closed",
}


def _proposal(*, request_id="REQUEST-35-11", ambiguities=()):
    commitments = {
        field: value
        if field
        in {
            "requested_capability",
            "user_visible_outcome",
            "architectural_placement",
        }
        else [value]
        for field, value in REPRESENTATIONS.items()
    }
    requirements = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "requirement_type": field,
            "source_text": f"source requirement for {value}",
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    mappings = [
        {
            "requirement_id": f"REQ-{index:02d}",
            "target_field": field,
            "exact_condensed_representation": value,
        }
        for index, (field, value) in enumerate(REPRESENTATIONS.items(), start=1)
    ]
    return create_canonical_condensation_proposal(
        original_request_id=request_id,
        original_request="Review exact canonical condensation before approval.",
        clarification_evidence=[
            {
                "question_id": "QUESTION-1",
                "question": "Does approval authorize execution?",
                "answer_id": "ANSWER-1",
                "answer": "No, it approves semantic representation only.",
                "resolved": True,
            }
        ],
        clarification_complete=True,
        completed_objective_id="OBJECTIVE-35-11",
        completed_objective=(
            "Present and decide exact Model D values without G31 integration."
        ),
        project_id="SAPIANTA",
        workspace_id="/workspace/sapianta",
        session_id="SESSION-35-11",
        invocation_id="INVOCATION-35-11",
        chain_id="CHAIN-35-11",
        semantic_commitments=commitments,
        source_requirements=requirements,
        requirement_mappings=mappings,
        proposed_synthesis_body=(
            "runtime validation; " + "; ".join(REPRESENTATIONS.values())
        ),
        unresolved_ambiguities=ambiguities,
    )


def _phase1(tmp_path: Path, *, proposal=None):
    selected = proposal or _proposal()
    validation = validate_canonical_condensation_proposal(selected)
    replay_dir = tmp_path / "phase1"
    capture = record_canonical_condensation_phase1_replay(
        proposal=selected,
        validation_result=validation,
        recorded_at="2026-07-28T13:00:00Z",
        replay_dir=replay_dir,
    )
    return selected, validation, replay_dir, capture


def _review(tmp_path: Path, *, proposal=None, reviewed_by="HUMAN-1"):
    selected, validation, phase1_dir, capture = _phase1(
        tmp_path,
        proposal=proposal,
    )
    review = create_canonical_condensation_human_review(
        proposal=selected,
        validation_result=validation,
        phase1_replay_dir=phase1_dir,
        reviewed_by=reviewed_by,
        presented_at="2026-07-28T13:01:00Z",
    )
    return selected, validation, phase1_dir, capture, review


def _decision(tmp_path: Path, *, outcome=CANONICAL_CONDENSATION_APPROVE):
    proposal, validation, phase1_dir, capture, review = _review(tmp_path)
    decision = create_canonical_condensation_human_decision(
        review=review,
        phase1_replay_dir=phase1_dir,
        decision=outcome,
        decided_by="HUMAN-1",
        decided_at="2026-07-28T13:02:00Z",
    )
    return proposal, validation, phase1_dir, capture, review, decision


def _rehash_review(review):
    candidate = deepcopy(review)
    candidate.pop("review_id", None)
    candidate.pop("review_hash", None)
    digest = replay_hash(candidate)
    candidate["review_id"] = (
        "CANONICAL-CONDENSATION-REVIEW-"
        f"{digest.removeprefix('sha256:')[:24]}"
    )
    candidate["review_hash"] = digest
    return candidate


def _rehash_decision(decision):
    candidate = deepcopy(decision)
    candidate.pop("human_decision_id", None)
    candidate.pop("human_decision_hash", None)
    digest = replay_hash(candidate)
    candidate["human_decision_id"] = (
        "CANONICAL-CONDENSATION-DECISION-"
        f"{digest.removeprefix('sha256:')[:24]}"
    )
    candidate["human_decision_hash"] = digest
    return candidate


def _rehash_validation(validation):
    candidate = deepcopy(validation)
    candidate.pop("validation_id", None)
    candidate.pop("validation_hash", None)
    digest = replay_hash(candidate)
    candidate["validation_id"] = (
        "CANONICAL-CONDENSATION-VALIDATION-"
        f"{digest.removeprefix('sha256:')[:24]}"
    )
    candidate["validation_hash"] = digest
    return candidate


def test_review_presents_exact_source_proposal_validation_and_model_d(tmp_path):
    proposal, validation, phase1_dir, capture, review = _review(tmp_path)
    projection = review["model_d_projection"]

    assert review["source_request"] == proposal["source_lineage"][
        "original_request"
    ]
    assert review["condensation_proposal"] == proposal
    assert review["deterministic_validation_result"] == validation
    assert review["validation_status"] == "PASS"
    assert projection["prefix"] == G31_CODEX_SYNTHESIS_PREFIX
    assert projection["synthesis_body"] == proposal["proposed_synthesis_body"]
    assert projection["complete_projection"] == (
        projection["prefix"] + projection["synthesis_body"]
    )
    assert review["phase1_replay_reference"]["replay_family_hash"] == capture[
        "replay_family_hash"
    ]
    assert review["review_warning"] == CANONICAL_CONDENSATION_REVIEW_WARNING
    assert review["decision_pending"] is True
    assert review["execution_authorized"] is False

    rendered = render_canonical_condensation_human_review(
        review,
        phase1_replay_dir=phase1_dir,
    )
    assert proposal["source_lineage"]["original_request"][
        "original_request"
    ] in rendered
    assert projection["prefix"] in rendered
    assert projection["synthesis_body"] in rendered
    assert projection["complete_projection"] in rendered
    assert proposal["condensation_hash"] in rendered
    assert validation["validation_hash"] in rendered
    assert CANONICAL_CONDENSATION_REVIEW_WARNING in rendered


def test_explicit_approval_binds_exact_projection_without_execution(tmp_path):
    proposal, validation, phase1_dir, _, review, decision = _decision(tmp_path)
    approved = decision["approved_projection"]

    assert decision["decision"] == "APPROVE"
    assert decision["explicit_human_action"] is True
    assert decision["approval_created"] is True
    assert decision["semantic_representation_approved"] is True
    assert approved["prefix"] == proposal["projection_prefix"]
    assert approved["approved_synthesis_body"] == proposal[
        "proposed_synthesis_body"
    ]
    assert approved["approved_projection"] == proposal["proposed_projection"]
    assert approved["approved_projection"] == (
        approved["prefix"] + approved["approved_synthesis_body"]
    )
    assert decision["proposal_commitment"] == proposal["condensation_hash"]
    assert decision["validation_commitment"] == validation["validation_hash"]
    assert decision["review_commitment"] == review["review_hash"]
    assert decision["authorization_created"] is False
    assert decision["execution_authorized"] is False
    assert decision["g31_input_binding_created"] is False
    assert decision["worker_invoked"] is False
    assert decision["provider_invoked"] is False
    assert validate_canonical_condensation_human_decision(
        decision,
        review=review,
        phase1_replay_dir=phase1_dir,
    ) == decision


def test_explicit_rejection_creates_no_approved_projection(tmp_path):
    _, _, phase1_dir, _, review, decision = _decision(
        tmp_path,
        outcome=CANONICAL_CONDENSATION_REJECT,
    )

    assert decision["decision"] == "REJECT"
    assert decision["approval_created"] is False
    assert decision["semantic_representation_approved"] is False
    assert decision["approved_projection_created"] is False
    assert decision["approved_projection"] is None
    assert decision["approved_projection_artifact_hash"] is None
    assert decision["rejection_final_for_review"] is True
    assert validate_canonical_condensation_human_decision(
        decision,
        review=review,
        phase1_replay_dir=phase1_dir,
    ) == decision


def test_review_rejects_validation_failure(tmp_path):
    proposal = _proposal(ambiguities=("The target remains ambiguous.",))
    validation = validate_canonical_condensation_proposal(proposal)
    phase1_dir = tmp_path / "phase1"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T13:00:00Z",
        replay_dir=phase1_dir,
    )

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_human_review(
            proposal=proposal,
            validation_result=validation,
            phase1_replay_dir=phase1_dir,
            reviewed_by="HUMAN-1",
            presented_at="2026-07-28T13:01:00Z",
        )


def test_review_rejects_missing_proposal_validation_or_source(tmp_path):
    proposal, validation, phase1_dir, _, review = _review(tmp_path)
    for changed_proposal, changed_validation in (
        (None, validation),
        (proposal, None),
    ):
        with pytest.raises(FailClosedRuntimeError):
            create_canonical_condensation_human_review(
                proposal=changed_proposal,
                validation_result=changed_validation,
                phase1_replay_dir=phase1_dir,
                reviewed_by="HUMAN-1",
                presented_at="2026-07-28T13:01:00Z",
            )

    review["source_request"] = None
    review = _rehash_review(review)
    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_review(
            review,
            phase1_replay_dir=phase1_dir,
        )


def test_review_rejects_unsupported_validation_version(tmp_path):
    proposal, validation, phase1_dir, _ = _phase1(tmp_path)
    validation["validator_version"] = "UNSUPPORTED"
    validation = _rehash_validation(validation)

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_human_review(
            proposal=proposal,
            validation_result=validation,
            phase1_replay_dir=phase1_dir,
            reviewed_by="HUMAN-1",
            presented_at="2026-07-28T13:01:00Z",
        )


def test_review_rejects_another_proposal_or_source(tmp_path):
    _, validation, phase1_dir, _ = _phase1(tmp_path)
    other = _proposal(request_id="OTHER-REQUEST")

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_human_review(
            proposal=other,
            validation_result=validation,
            phase1_replay_dir=phase1_dir,
            reviewed_by="HUMAN-1",
            presented_at="2026-07-28T13:01:00Z",
        )


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("prefix", "runtime-validation: "),
        ("synthesis_body", "different body"),
        ("complete_projection", "different projection"),
        ("prefix_utf8_byte_count", 999),
        ("complete_projection_code_point_count", 999),
        ("complete_projection_sha256", "different-hash"),
    ],
)
def test_review_rejects_modified_model_d_values(
    tmp_path,
    field,
    replacement,
):
    _, _, phase1_dir, _, review = _review(tmp_path)
    review["model_d_projection"][field] = replacement
    review = _rehash_review(review)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_review(
            review,
            phase1_replay_dir=phase1_dir,
        )


@pytest.mark.parametrize(
    "decision",
    (
        None,
        "",
        "APPROVED",
        "approve",
        " APPROVE",
        "APPROVE ",
        "APPROVE OR REJECT",
        "YES",
    ),
)
def test_decision_requires_exact_unambiguous_explicit_outcome(
    tmp_path,
    decision,
):
    _, _, phase1_dir, _, review = _review(tmp_path)

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_human_decision(
            review=review,
            phase1_replay_dir=phase1_dir,
            decision=decision,
            decided_by="HUMAN-1",
            decided_at="2026-07-28T13:02:00Z",
        )


def test_decision_rejects_missing_review(tmp_path):
    _, _, phase1_dir, _ = _phase1(tmp_path)

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_human_decision(
            review=None,
            phase1_replay_dir=phase1_dir,
            decision="APPROVE",
            decided_by="HUMAN-1",
            decided_at="2026-07-28T13:02:00Z",
        )


def test_decision_rejects_other_review(tmp_path):
    _, _, phase1_dir, _, review, decision = _decision(tmp_path)
    other_review = deepcopy(review)
    other_review["presented_at"] = "2026-07-28T13:03:00Z"
    other_review = _rehash_review(other_review)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_decision(
            decision,
            review=other_review,
            phase1_replay_dir=phase1_dir,
        )


def test_decision_rejects_post_approval_whitespace_transformation(tmp_path):
    _, _, phase1_dir, _, review, decision = _decision(tmp_path)
    decision["exact_synthesis_body"] += " "
    decision = _rehash_decision(decision)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_decision(
            decision,
            review=review,
            phase1_replay_dir=phase1_dir,
        )


def test_review_rejects_source_or_commitment_substitution(tmp_path):
    _, _, phase1_dir, _, review = _review(tmp_path)
    for mutation in ("source", "proposal", "validation"):
        changed = deepcopy(review)
        if mutation == "source":
            changed["source_request"]["original_request"] = "other source"
        elif mutation == "proposal":
            changed["proposal_commitment"] = "sha256:other"
        else:
            changed["validation_commitment"] = "sha256:other"
        changed = _rehash_review(changed)
        with pytest.raises(FailClosedRuntimeError):
            validate_canonical_condensation_human_review(
                changed,
                phase1_replay_dir=phase1_dir,
            )


def test_unsupported_review_and_decision_schema_versions_fail_closed(tmp_path):
    _, _, phase1_dir, _, review, decision = _decision(tmp_path)
    changed_review = deepcopy(review)
    changed_review["schema_version"] = "2.0.0"
    changed_review = _rehash_review(changed_review)
    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_review(
            changed_review,
            phase1_replay_dir=phase1_dir,
        )

    changed_decision = deepcopy(decision)
    changed_decision["schema_version"] = "2.0.0"
    changed_decision = _rehash_decision(changed_decision)
    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_human_decision(
            changed_decision,
            review=review,
            phase1_replay_dir=phase1_dir,
        )


@pytest.mark.parametrize("outcome", ("APPROVE", "REJECT"))
def test_replay_reconstructs_complete_approval_or_rejection_chain(
    tmp_path,
    outcome,
):
    proposal, validation, phase1_dir, _, review, decision = _decision(
        tmp_path,
        outcome=outcome,
    )
    replay_dir = tmp_path / "phase2"
    capture = record_canonical_condensation_review_decision_replay(
        phase1_replay_dir=phase1_dir,
        review=review,
        decision=decision,
        recorded_at="2026-07-28T13:03:00Z",
        replay_dir=replay_dir,
    )
    reconstructed = reconstruct_canonical_condensation_review_decision_replay(
        replay_dir
    )

    assert reconstructed["proposal"] == proposal
    assert reconstructed["validation_result"] == validation
    assert reconstructed["review"] == review
    assert reconstructed["decision_artifact"] == decision
    assert reconstructed["decision"] == outcome
    assert len(capture["replay_files"]) == 5
    assert reconstructed["execution_authorized"] is False
    assert reconstructed["g31_input_binding_created"] is False
    if outcome == "APPROVE":
        assert reconstructed["approved_projection"] == decision[
            "approved_projection"
        ]
        assert reconstructed["approved_projection"]["approved_projection"] == (
            G31_CODEX_SYNTHESIS_PREFIX + proposal["proposed_synthesis_body"]
        )
    else:
        assert reconstructed["approved_projection"] is None
        assert reconstructed["approved_projection_created"] is False

    for index in range(3):
        phase1_file = sorted(phase1_dir.iterdir())[index]
        phase2_file = replay_dir / phase1_file.name
        assert json.loads(phase1_file.read_text(encoding="utf-8")) == json.loads(
            phase2_file.read_text(encoding="utf-8")
        )


def test_replay_rejects_missing_or_reordered_event(tmp_path):
    _, _, phase1_dir, _, review, decision = _decision(tmp_path)
    replay_dir = tmp_path / "phase2"
    record_canonical_condensation_review_decision_replay(
        phase1_replay_dir=phase1_dir,
        review=review,
        decision=decision,
        recorded_at="2026-07-28T13:03:00Z",
        replay_dir=replay_dir,
    )
    review_path = replay_dir / "003_condensation_human_review_presented.json"
    decision_path = replay_dir / "004_condensation_human_decision_recorded.json"
    review_content = review_path.read_text(encoding="utf-8")
    decision_content = decision_path.read_text(encoding="utf-8")
    review_path.write_text(decision_content, encoding="utf-8")
    decision_path.write_text(review_content, encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_canonical_condensation_review_decision_replay(replay_dir)

    decision_path.unlink()
    with pytest.raises(FailClosedRuntimeError):
        reconstruct_canonical_condensation_review_decision_replay(replay_dir)


def test_duplicate_conflicting_decision_and_approval_after_rejection_fail(
    tmp_path,
):
    _, _, phase1_dir, _, review, rejection = _decision(
        tmp_path,
        outcome="REJECT",
    )
    approval = create_canonical_condensation_human_decision(
        review=review,
        phase1_replay_dir=phase1_dir,
        decision="APPROVE",
        decided_by="HUMAN-1",
        decided_at="2026-07-28T13:04:00Z",
    )
    replay_dir = tmp_path / "phase2"
    record_canonical_condensation_review_decision_replay(
        phase1_replay_dir=phase1_dir,
        review=review,
        decision=rejection,
        recorded_at="2026-07-28T13:03:00Z",
        replay_dir=replay_dir,
    )

    with pytest.raises(FailClosedRuntimeError):
        record_canonical_condensation_review_decision_replay(
            phase1_replay_dir=phase1_dir,
            review=review,
            decision=approval,
            recorded_at="2026-07-28T13:05:00Z",
            replay_dir=replay_dir,
        )


def test_phase2_modules_do_not_import_downstream_execution_boundaries():
    runtime_root = Path(__file__).parents[1] / "aigol" / "runtime"
    module_names = (
        "canonical_governed_development_condensation_human_review_runtime.py",
        "canonical_governed_development_condensation_human_decision_runtime.py",
        "canonical_governed_development_condensation_replay.py",
    )
    forbidden = (
        "aigol.cli",
        "human_interface_runtime_entry",
        "input_binding",
        "codex_worker_activation",
        "authorization_runtime",
        "worker_runtime",
        "provider_runtime",
        "execution_gate",
        "capability_registry",
        "codex_synthesis",
        "codex_handoff",
        "task_outcome",
    )
    for module_name in module_names:
        import_lines = "\n".join(
            line
            for line in (runtime_root / module_name)
            .read_text(encoding="utf-8")
            .splitlines()
            if line.startswith(("from ", "import "))
        )
        assert not any(fragment in import_lines for fragment in forbidden)
