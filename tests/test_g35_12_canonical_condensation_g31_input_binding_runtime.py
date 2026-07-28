from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unicodedata

import pytest

from aigol.runtime.canonical_governed_development_condensation_g31_input_binding_runtime import (
    CANONICAL_CONDENSATION_G31_PREFLIGHT_TUPLE_V1,
    ELIGIBLE_FOR_G31_PREFLIGHT,
    create_canonical_condensation_g31_input_binding,
    reconstruct_canonical_condensation_g31_input_binding,
    validate_canonical_condensation_g31_input_binding,
)
from aigol.runtime.canonical_governed_development_condensation_human_decision_runtime import (
    create_canonical_condensation_human_decision,
)
from aigol.runtime.canonical_governed_development_condensation_human_review_runtime import (
    create_canonical_condensation_human_review,
)
from aigol.runtime.canonical_governed_development_condensation_replay import (
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
    "user_visible_outcome": "bounded café task",
    "allowed_operations": "read source",
    "prohibited_operations": "no mutation",
    "architectural_placement": "pre-G31",
    "acceptance_conditions": "all mapped",
    "testing_validation_requirements": "deterministic",
    "explicit_exclusions": "no execution",
    "safety_governance_constraints": "fail closed",
}


def _proposal(*, request_id: str, original: str):
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
        original_request=original,
        clarification_evidence=[
            {
                "question_id": "QUESTION-1",
                "question": "Does this binding invoke G31?",
                "answer_id": "ANSWER-1",
                "answer": "No, it only prepares an exact future input.",
                "resolved": True,
            }
        ],
        clarification_complete=True,
        completed_objective_id=f"{request_id}:OBJECTIVE",
        completed_objective=(
            "Bind exact approved Model D values without invoking G31."
        ),
        project_id="SAPIANTA",
        workspace_id="/workspace/sapianta",
        session_id=f"{request_id}:SESSION",
        invocation_id=f"{request_id}:INVOCATION",
        chain_id=f"{request_id}:CHAIN",
        semantic_commitments=commitments,
        source_requirements=requirements,
        requirement_mappings=mappings,
        proposed_synthesis_body=(
            "runtime validation; " + "; ".join(REPRESENTATIONS.values())
        ),
    )


def _approved_chain(
    root: Path,
    *,
    request_id="REQUEST-35-12",
    original="Bind this exact source request.",
    decision="APPROVE",
    phase1_recorded_at="2026-07-28T14:00:00Z",
):
    proposal = _proposal(request_id=request_id, original=original)
    validation = validate_canonical_condensation_proposal(proposal)
    phase1_dir = root / "phase1"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at=phase1_recorded_at,
        replay_dir=phase1_dir,
    )
    review = create_canonical_condensation_human_review(
        proposal=proposal,
        validation_result=validation,
        phase1_replay_dir=phase1_dir,
        reviewed_by="HUMAN-1",
        presented_at="2026-07-28T14:01:00Z",
    )
    human_decision = create_canonical_condensation_human_decision(
        review=review,
        phase1_replay_dir=phase1_dir,
        decision=decision,
        decided_by="HUMAN-1",
        decided_at="2026-07-28T14:02:00Z",
    )
    phase2_dir = root / "phase2"
    record_canonical_condensation_review_decision_replay(
        phase1_replay_dir=phase1_dir,
        review=review,
        decision=human_decision,
        recorded_at="2026-07-28T14:03:00Z",
        replay_dir=phase2_dir,
    )
    return {
        "proposal": proposal,
        "validation": validation,
        "review": review,
        "decision": human_decision,
        "phase1_dir": phase1_dir,
        "phase2_dir": phase2_dir,
    }


def _rehash_binding(binding):
    candidate = deepcopy(binding)
    candidate.pop("binding_id", None)
    candidate.pop("binding_hash", None)
    digest = replay_hash(candidate)
    candidate["binding_id"] = (
        "CANONICAL-CONDENSATION-G31-BINDING-"
        f"{digest.removeprefix('sha256:')[:24]}"
    )
    candidate["binding_hash"] = digest
    return candidate


def _rewrite_wrapper(path: Path, mutate):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    mutate(wrapper)
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(
        json.dumps(wrapper, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def test_approved_chain_produces_exact_deterministic_model_d_binding(tmp_path):
    chain = _approved_chain(tmp_path)
    first = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    second = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )

    assert first == second
    assert first["binding_status"] == ELIGIBLE_FOR_G31_PREFLIGHT
    assert first["original_source_request"] == (
        "Bind this exact source request."
    )
    assert first["approved_projection_prefix"] == G31_CODEX_SYNTHESIS_PREFIX
    assert first["approved_synthesis_body"] == chain["proposal"][
        "proposed_synthesis_body"
    ]
    assert first["approved_projection"] == (
        first["approved_projection_prefix"]
        + first["approved_synthesis_body"]
    )
    assert first["g31_function_argument"] == first["approved_synthesis_body"]
    assert first["g31_final_measured_request"] == first["approved_projection"]
    assert first["authorized_task"] == first["approved_synthesis_body"]
    assert (
        first["maximum_g31_final_measured_request_code_point_count"] == 240
    )
    assert first["character_counting_contract"] == (
        "PYTHON_UNICODE_CODE_POINTS"
    )
    assert first["encoding_contract"] == "UTF-8_STRICT"
    assert (
        first["original_source_request"]
        != first["g31_function_argument"]
    )
    assert first["g31_preflight_invoked"] is False
    assert first["g31_preflight_passed"] is False
    assert first["codex_synthesis_authorized"] is False
    assert first["execution_authorized"] is False
    assert first["worker_invoked"] is False
    assert first["provider_invoked"] is False
    assert first["repository_mutated"] is False


def test_binding_preserves_exact_utf8_code_points_and_hashes(tmp_path):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )

    for value_field, commitment_field in (
        ("original_source_request", "original_source_request_commitment"),
        ("approved_projection_prefix", "approved_projection_prefix_commitment"),
        ("approved_synthesis_body", "approved_synthesis_body_commitment"),
        ("approved_projection", "approved_projection_commitment"),
        ("g31_function_argument", "g31_function_argument_commitment"),
        ("g31_final_measured_request", "g31_final_measured_request_commitment"),
        ("authorized_task", "authorized_task_commitment"),
    ):
        value = binding[value_field]
        commitment = binding[commitment_field]
        assert commitment["code_point_count"] == len(value)
        assert commitment["utf8_byte_count"] == len(value.encode("utf-8"))
        assert commitment["encoding_contract"] == "UTF-8_STRICT"
        assert commitment["character_counting_contract"] == (
            "PYTHON_UNICODE_CODE_POINTS"
        )

    assert (
        binding["approved_synthesis_body_commitment"]["utf8_byte_count"]
        > binding["approved_synthesis_body_commitment"]["code_point_count"]
    )


def test_preflight_input_tuple_is_stable_and_role_specific(tmp_path):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    input_tuple = binding["preflight_input_tuple"]

    assert input_tuple["tuple_contract"] == (
        CANONICAL_CONDENSATION_G31_PREFLIGHT_TUPLE_V1
    )
    assert input_tuple["g31_function_argument"]["value"] == binding[
        "approved_synthesis_body"
    ]
    assert input_tuple["g31_final_measured_request"]["value"] == binding[
        "approved_projection"
    ]
    assert binding["preflight_input_tuple_hash"] == replay_hash(input_tuple)


def test_binding_reconstructs_identically_without_writing_replay(tmp_path):
    chain = _approved_chain(tmp_path)
    before = sorted(path.name for path in chain["phase2_dir"].iterdir())
    created = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    reconstructed = reconstruct_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    after = sorted(path.name for path in chain["phase2_dir"].iterdir())

    assert reconstructed == created
    assert before == after
    assert created["replay_written"] is False
    assert validate_canonical_condensation_g31_input_binding(
        created,
        approved_replay_dir=chain["phase2_dir"],
    ) == created


def test_validation_pass_without_human_review_or_approval_cannot_bind(tmp_path):
    proposal = _proposal(
        request_id="REQUEST-NO-APPROVAL",
        original="No approval exists.",
    )
    validation = validate_canonical_condensation_proposal(proposal)
    phase1_dir = tmp_path / "phase1"
    record_canonical_condensation_phase1_replay(
        proposal=proposal,
        validation_result=validation,
        recorded_at="2026-07-28T14:00:00Z",
        replay_dir=phase1_dir,
    )

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=phase1_dir
        )


def test_explicit_rejection_cannot_bind(tmp_path):
    chain = _approved_chain(tmp_path, decision="REJECT")

    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=chain["phase2_dir"]
        )


def test_malformed_or_conflicting_decision_cannot_bind(tmp_path):
    chain = _approved_chain(tmp_path)
    decision_path = (
        chain["phase2_dir"]
        / "004_condensation_human_decision_recorded.json"
    )

    def malformed(wrapper):
        wrapper["artifact"]["decision"] = "APPROVE OR REJECT"

    _rewrite_wrapper(decision_path, malformed)
    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=chain["phase2_dir"]
        )

    (chain["phase2_dir"] / "005_conflicting_decision.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=chain["phase2_dir"]
        )


@pytest.mark.parametrize(
    ("field", "mutation"),
    [
        ("approved_projection_prefix", lambda value: "changed: "),
        ("approved_synthesis_body", lambda value: f"changed {value}"),
        ("approved_projection", lambda value: f"changed {value}"),
        ("g31_function_argument", lambda value: f" {value}"),
        ("g31_function_argument", lambda value: f"{value} "),
        ("g31_function_argument", lambda value: f"{value}\n"),
        (
            "g31_function_argument",
            lambda value: unicodedata.normalize("NFD", value),
        ),
        ("g31_final_measured_request", lambda value: f"{value}\n"),
        ("authorized_task", lambda value: f" {value}"),
    ],
)
def test_transformed_or_normalized_binding_values_fail_closed(
    tmp_path,
    field,
    mutation,
):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    changed = mutation(binding[field])
    assert changed != binding[field]
    binding[field] = changed
    binding = _rehash_binding(binding)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_g31_input_binding(
            binding,
            approved_replay_dir=chain["phase2_dir"],
        )


@pytest.mark.parametrize(
    ("commitment_field", "member", "replacement"),
    [
        ("approved_projection_prefix_commitment", "sha256", "other"),
        ("approved_synthesis_body_commitment", "utf8_byte_count", 999),
        ("approved_projection_commitment", "code_point_count", 999),
        ("g31_function_argument_commitment", "sha256", "other"),
        ("g31_final_measured_request_commitment", "sha256", "other"),
        ("authorized_task_commitment", "sha256", "other"),
    ],
)
def test_utf8_codepoint_or_hash_commitment_mismatch_fails_closed(
    tmp_path,
    commitment_field,
    member,
    replacement,
):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    binding[commitment_field][member] = replacement
    binding = _rehash_binding(binding)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_g31_input_binding(
            binding,
            approved_replay_dir=chain["phase2_dir"],
        )


@pytest.mark.parametrize(
    "field",
    (
        "source_request_hash",
        "proposal_hash",
        "validation_hash",
        "review_hash",
        "decision_hash",
        "approval_hash",
        "phase1_replay_family_hash",
        "approved_chain_replay_hash",
    ),
)
def test_chain_commitment_substitution_fails_closed(tmp_path, field):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    binding[field] = "sha256:other"
    binding = _rehash_binding(binding)

    with pytest.raises(FailClosedRuntimeError):
        validate_canonical_condensation_g31_input_binding(
            binding,
            approved_replay_dir=chain["phase2_dir"],
        )


def test_binding_schema_or_artifact_version_substitution_fails_closed(tmp_path):
    chain = _approved_chain(tmp_path)
    binding = create_canonical_condensation_g31_input_binding(
        approved_replay_dir=chain["phase2_dir"]
    )
    for mutate in ("binding_schema", "artifact_version"):
        changed = deepcopy(binding)
        if mutate == "binding_schema":
            changed["schema_version"] = "2.0.0"
        else:
            changed["artifact_versions"]["decision_schema_version"] = "2.0.0"
        changed = _rehash_binding(changed)
        with pytest.raises(FailClosedRuntimeError):
            validate_canonical_condensation_g31_input_binding(
                changed,
                approved_replay_dir=chain["phase2_dir"],
            )


def test_approval_cannot_be_reused_for_another_source_proposal_or_replay(
    tmp_path,
):
    first = _approved_chain(
        tmp_path / "first",
        request_id="REQUEST-FIRST",
        original="First original source.",
    )
    second = _approved_chain(
        tmp_path / "second",
        request_id="REQUEST-SECOND",
        original="Second original source.",
        phase1_recorded_at="2026-07-28T14:10:00Z",
    )
    first_decision_path = (
        first["phase2_dir"]
        / "004_condensation_human_decision_recorded.json"
    )
    first_decision = json.loads(
        first_decision_path.read_text(encoding="utf-8")
    )["artifact"]
    second_decision_path = (
        second["phase2_dir"]
        / "004_condensation_human_decision_recorded.json"
    )

    def substitute(wrapper):
        wrapper["artifact"] = first_decision

    _rewrite_wrapper(second_decision_path, substitute)
    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=second["phase2_dir"]
        )


def test_approval_cannot_be_reused_across_another_replay_chain(tmp_path):
    proposal = _proposal(
        request_id="REQUEST-SAME",
        original="Same source, distinct Replay.",
    )
    first = _approved_chain(
        tmp_path / "first",
        request_id="REQUEST-SAME",
        original="Same source, distinct Replay.",
        phase1_recorded_at="2026-07-28T14:00:00Z",
    )
    second = _approved_chain(
        tmp_path / "second",
        request_id="REQUEST-SAME",
        original="Same source, distinct Replay.",
        phase1_recorded_at="2026-07-28T15:00:00Z",
    )
    assert first["proposal"] == proposal
    first_decision = json.loads(
        (
            first["phase2_dir"]
            / "004_condensation_human_decision_recorded.json"
        ).read_text(encoding="utf-8")
    )["artifact"]
    second_decision_path = (
        second["phase2_dir"]
        / "004_condensation_human_decision_recorded.json"
    )

    def substitute(wrapper):
        wrapper["artifact"] = first_decision

    _rewrite_wrapper(second_decision_path, substitute)
    with pytest.raises(FailClosedRuntimeError):
        create_canonical_condensation_g31_input_binding(
            approved_replay_dir=second["phase2_dir"]
        )


def test_missing_reordered_or_unsupported_replay_event_fails_closed(tmp_path):
    for mutation in ("missing", "reordered", "unsupported"):
        chain = _approved_chain(tmp_path / mutation)
        review_path = (
            chain["phase2_dir"]
            / "003_condensation_human_review_presented.json"
        )
        decision_path = (
            chain["phase2_dir"]
            / "004_condensation_human_decision_recorded.json"
        )
        if mutation == "missing":
            review_path.unlink()
        elif mutation == "reordered":
            review_text = review_path.read_text(encoding="utf-8")
            decision_text = decision_path.read_text(encoding="utf-8")
            review_path.write_text(decision_text, encoding="utf-8")
            decision_path.write_text(review_text, encoding="utf-8")
        else:
            _rewrite_wrapper(
                decision_path,
                lambda wrapper: wrapper.update({"schema_version": "2.0.0"}),
            )
        with pytest.raises(FailClosedRuntimeError):
            create_canonical_condensation_g31_input_binding(
                approved_replay_dir=chain["phase2_dir"]
            )


def test_dedicated_binding_does_not_import_or_invoke_downstream_runtime():
    source = (
        Path(__file__).parents[1]
        / "aigol"
        / "runtime"
        / (
            "canonical_governed_development_condensation_"
            "g31_input_binding_runtime.py"
        )
    ).read_text(encoding="utf-8")
    import_lines = "\n".join(
        line
        for line in source.splitlines()
        if line.startswith(("from ", "import "))
    )
    forbidden = (
        "codex_worker_activation_binding_runtime",
        "preflight_codex_worker_synthesis",
        "aigol.cli",
        "human_interface_runtime_entry",
        "codex_synthesis",
        "codex_handoff",
        "authorization_runtime",
        "worker_runtime",
        "provider_runtime",
        "execution_gate",
        "task_outcome",
        "capability_registry",
    )
    assert not any(fragment in import_lines for fragment in forbidden)
    assert ".strip(" not in source
    assert "unicodedata" not in source
