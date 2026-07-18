from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime.codex_task_outcome_human_review_runtime import (
    APPROVAL_SCOPE,
    REWORK_REQUESTED,
    TASK_OUTCOME_SATISFIED,
    TASK_OUTCOME_UNSATISFIED,
    prepare_codex_task_outcome_review,
    reconstruct_codex_task_outcome_human_decision,
    reconstruct_codex_task_outcome_review,
    record_codex_task_outcome_human_decision,
    render_codex_task_outcome_review,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
)
from test_g31_18_codex_transport_to_worker_result_capture_binding import _capture
from test_g31_20_codex_result_to_semantic_validation_binding import _validate
from test_g31_21b_codex_worker_prompt_fidelity_repair import _two_decisions


EXACT_DIFF = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f\"Status: {value}\"\n"
    "+    return f\"Summary: {value}\"\n"
)
DECIDED_AT = "2026-07-18T08:00:00Z"


def _validated_fixture(tmp_path: Path, session: str):
    runtime, root, workspace = _two_decisions(tmp_path, session)
    runner = RecordingRunner(stdout=EXACT_DIFF)
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", runner
    )
    capture = _capture(runtime, activation, root, workspace)
    validation = _validate(runtime, activation, capture, root, workspace)
    return runtime, activation, capture, validation, root, workspace, runner


def _review(tmp_path: Path, session: str):
    values = _validated_fixture(tmp_path, session)
    runtime, activation, capture, validation, root, workspace, _ = values
    review = prepare_codex_task_outcome_review(
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        prepared_at=DECIDED_AT,
        replay_dir=root / "task-outcome-review",
    )
    return (*values, review)


def _decide(values, outcome: str, *, destination: str = "task-outcome-decision"):
    runtime, activation, capture, validation, root, workspace, _, review = values
    return record_codex_task_outcome_human_decision(
        review_capture=review,
        task_outcome_decision=outcome,
        decision_reason=f"Human selected {outcome} after exact-byte review.",
        decided_by="human.operator",
        decided_at=DECIDED_AT,
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        human_decision_replay_dir=root / destination,
    )


def _reconstruct(values, decision):
    runtime, activation, capture, validation, root, workspace, _, review = values
    return reconstruct_codex_task_outcome_human_decision(
        decision_capture=decision,
        review_capture=review,
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
    )


def test_satisfied_human_review_binds_exact_task_bytes_and_stops_before_acceptance(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22A-SATISFIED")
    activation, review = values[1], values[-1]
    packet = review["task_outcome_review_packet_artifact"]
    criteria = packet["pre_execution_task_outcome_criteria"]
    decision = _decide(values, TASK_OUTCOME_SATISFIED)
    reconstructed = _reconstruct(values, decision)

    assert criteria["established_before_worker_execution"] is True
    assert criteria["criteria_hash"] == activation["activation_approval_artifact"][
        "task_outcome_criteria_hash"
    ]
    assert packet["exact_worker_output"]["text"] == EXACT_DIFF
    assert packet["required_output_type"] == "UNIFIED_DIFF"
    assert packet["grounded_targets"]["implementation_target"] == (
        "aigol/runtime/human_interface.py"
    )
    assert packet["grounded_targets"]["focused_test_target"] == (
        "tests/test_human_interface.py"
    )
    observations = packet["task_outcome_observations"]
    assert observations["unified_diff_markers_present"] is True
    assert observations["status_to_summary_change_present"] is True
    assert observations["additional_target_present"] is False
    assert packet["patch_applied"] is False
    assert packet["tests_run_against_applied_patch"] is False
    assert decision["approval_scope"] == APPROVAL_SCOPE
    assert decision["task_outcome_satisfaction_evaluated"] is True
    assert decision["task_outcome_satisfied"] is True
    assert decision["human_task_outcome_decision_recorded"] is True
    assert decision["governance_result_validated"] is True
    assert decision["result_accepted"] is False
    assert decision["repository_mutation_authorized"] is False
    assert decision["repository_mutated"] is False
    assert decision["implementation_authorized"] is False
    assert reconstructed["task_outcome_decision"] == TASK_OUTCOME_SATISFIED


@pytest.mark.parametrize(
    ("outcome", "satisfied", "rework"),
    (
        (TASK_OUTCOME_UNSATISFIED, False, False),
        (REWORK_REQUESTED, False, True),
    ),
)
def test_unsatisfied_and_rework_decisions_record_truth_without_execution(
    tmp_path: Path,
    outcome: str,
    satisfied: bool,
    rework: bool,
) -> None:
    values = _review(tmp_path, f"G31-22A-{outcome}")
    runner = values[-2]
    calls_before = list(runner.calls)
    decision = _decide(values, outcome)

    assert decision["task_outcome_satisfaction_evaluated"] is True
    assert decision["task_outcome_satisfied"] is satisfied
    assert decision["rework_requested"] is rework
    assert decision["automatic_retry_performed"] is False
    assert decision["additional_worker_process_started"] is False
    assert decision["repository_mutation_authorized"] is False
    assert decision["result_accepted"] is False
    assert runner.calls == calls_before


def test_missing_exact_output_bytes_fail_before_review(tmp_path: Path) -> None:
    values = _validated_fixture(tmp_path, "G31-22A-MISSING-BYTES")
    runtime, activation, capture, validation, root, workspace, _ = values
    changed = deepcopy(capture)
    changed["semantic_worker_output_artifact"]["payload"].pop("semantic_output")
    _rehash(changed["semantic_worker_output_artifact"])

    with pytest.raises(FailClosedRuntimeError, match="exact|continuity|output"):
        _prepare(runtime, activation, changed, validation, root, workspace)


def test_changed_pre_execution_criteria_fail_closed(tmp_path: Path) -> None:
    values = _validated_fixture(tmp_path, "G31-22A-CRITERIA")
    runtime, activation, capture, validation, root, workspace, _ = values
    changed = deepcopy(activation)
    criteria = changed["synthesis_preflight_capture"]["worker_execution_contract"][
        "task_outcome_criteria"
    ]
    criteria["requirements"].append("POST_EXECUTION_INVENTED_CRITERION")
    criteria["criteria_hash"] = replay_hash(
        {key: value for key, value in criteria.items() if key != "criteria_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="contract|criteria"):
        _prepare(runtime, changed, capture, validation, root, workspace)


@pytest.mark.parametrize("tamper", ("bytes", "hash"))
def test_output_and_hash_substitution_fail_closed(
    tmp_path: Path, tamper: str
) -> None:
    values = _validated_fixture(tmp_path, f"G31-22A-OUTPUT-{tamper}")
    runtime, activation, capture, validation, root, workspace, _ = values
    changed = deepcopy(capture)
    output = changed["semantic_worker_output_artifact"]
    if tamper == "bytes":
        output["payload"]["semantic_output"] += "substituted"
    else:
        output["payload"]["semantic_output_sha256"] = "0" * 64
    _rehash(output)

    with pytest.raises(FailClosedRuntimeError):
        _prepare(runtime, activation, changed, validation, root, workspace)


def test_grounding_capture_and_validation_substitution_fail_closed(
    tmp_path: Path,
) -> None:
    values = _validated_fixture(tmp_path, "G31-22A-LINEAGE")
    runtime, activation, capture, validation, root, workspace, _ = values
    changed_runtime = deepcopy(runtime)
    changed_runtime["worker_execution_candidate_capture"][
        "worker_execution_candidate_artifact"
    ]["worker_identity"]["worker_id"] = "OTHER"
    with pytest.raises(FailClosedRuntimeError):
        prepare_codex_task_outcome_review(
            result_capture_binding_capture=capture,
            validation_binding_capture=validation,
            activation_capture=activation,
            governed_execution_capture=changed_runtime[
                "governed_worker_execution_capture"
            ],
            execution_candidate_capture=changed_runtime[
                "worker_execution_candidate_capture"
            ],
            session_root=root,
            workspace=workspace,
            prepared_at=DECIDED_AT,
            replay_dir=root / "review-grounding",
        )

    changed_capture = deepcopy(capture)
    changed_capture["worker_result_capture_replay_reference"] = validation[
        "worker_result_validation_replay_reference"
    ]
    with pytest.raises(FailClosedRuntimeError):
        _prepare(runtime, activation, changed_capture, validation, root, workspace)

    changed_validation = deepcopy(validation)
    changed_validation["worker_result_validation_replay_reference"] = capture[
        "worker_result_capture_replay_reference"
    ]
    with pytest.raises(FailClosedRuntimeError):
        _prepare(runtime, activation, capture, changed_validation, root, workspace)


def test_cross_session_duplicate_review_and_repeated_decision_fail_closed(
    tmp_path: Path,
) -> None:
    values = _validated_fixture(tmp_path, "G31-22A-DUPLICATE")
    runtime, activation, capture, validation, root, workspace, _ = values
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        _prepare(
            runtime,
            activation,
            capture,
            validation,
            root,
            workspace,
            destination=tmp_path / "other-session" / "review",
        )
    review = _prepare(runtime, activation, capture, validation, root, workspace)
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        _prepare(runtime, activation, capture, validation, root, workspace)
    with pytest.raises(FailClosedRuntimeError, match="already reviewed"):
        _prepare(
            runtime,
            activation,
            capture,
            validation,
            root,
            workspace,
            destination=root / "second-review",
        )
    complete_values = (
        runtime, activation, capture, validation, root, workspace,
        RecordingRunner(), review,
    )
    _decide(complete_values, TASK_OUTCOME_SATISFIED)
    with pytest.raises(FailClosedRuntimeError, match="already recorded"):
        _decide(
            complete_values,
            TASK_OUTCOME_UNSATISFIED,
            destination="second-decision",
        )


def test_governance_invalid_result_cannot_be_reviewed_as_satisfied(
    tmp_path: Path,
) -> None:
    values = _validated_fixture(tmp_path, "G31-22A-INVALID")
    runtime, activation, capture, validation, root, workspace, _ = values
    changed = deepcopy(validation)
    changed["g31_semantic_validation_status"] = (
        "G31_CODEX_SEMANTIC_VALIDATION_FAILED_CLOSED"
    )
    changed["validation_status"] = "FAILED_CLOSED"
    changed["result_validated"] = False

    with pytest.raises(FailClosedRuntimeError):
        _prepare(runtime, activation, capture, changed, root, workspace)


def test_acceptance_and_mutation_truth_substitution_fails_reconstruction(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22A-AUTHORITY")
    decision = _decide(values, TASK_OUTCOME_SATISFIED)
    for field in ("result_accepted", "repository_mutation_authorized"):
        changed = deepcopy(decision)
        changed[field] = True
        changed["task_outcome_decision_capture_hash"] = replay_hash(
            {
                key: value
                for key, value in changed.items()
                if key != "task_outcome_decision_capture_hash"
            }
        )
        with pytest.raises(FailClosedRuntimeError, match="truth was substituted"):
            _reconstruct(values, changed)


def test_truthful_aicli_presentation_is_exact_and_non_authoritative(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22A-PRESENTATION")
    review = values[-1]
    rendered = render_codex_task_outcome_review(review)

    assert EXACT_DIFF in rendered
    assert "GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY" in rendered
    assert "TASK_OUTCOME_SATISFIED" in rendered
    assert "TASK_OUTCOME_UNSATISFIED" in rendered
    assert "REWORK_REQUESTED" in rendered
    assert "does not review, accept, authorize mutation, or execute rework" in rendered
    assert review["aicli_reviews"] is False
    assert review["aicli_accepts"] is False
    assert review["aicli_authorizes_mutation"] is False
    assert review["aicli_executes_rework"] is False


def _prepare(
    runtime,
    activation,
    capture,
    validation,
    root,
    workspace,
    *,
    destination=None,
):
    return prepare_codex_task_outcome_review(
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        prepared_at=DECIDED_AT,
        replay_dir=destination or root / "task-outcome-review",
    )


def _rehash(artifact: dict) -> None:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
