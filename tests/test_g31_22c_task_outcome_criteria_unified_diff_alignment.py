from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import os

import pytest

from aigol.cli import aicli
from aigol.runtime import codex_task_outcome_human_review_runtime as review_runtime
from aigol.runtime import codex_worker_activation_binding_runtime as activation_runtime
from aigol.runtime.codex_task_outcome_human_review_runtime import (
    TASK_OUTCOME_SATISFIED,
    prepare_codex_task_outcome_review,
    record_codex_task_outcome_human_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
)
from test_g31_18_codex_transport_to_worker_result_capture_binding import _capture
from test_g31_20_codex_result_to_semantic_validation_binding import _validate
from test_g31_20f_disposable_repository_scope_grounding_fixture_contract import (
    CREATED_AT,
    _workspace,
)


ALIGNMENT_REQUEST = (
    "Fix Summary test: inspect aigol/runtime/human_interface.py and "
    "tests/test_human_interface.py; return a minimal Status:-to-Summary: unified "
    "diff; do not edit files."
)
SOURCE_ONLY_DIFF = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f\"Status: {value}\"\n"
    "+    return f\"Summary: {value}\"\n"
)
TEST_DIFF = (
    "--- a/tests/test_human_interface.py\n"
    "+++ b/tests/test_human_interface.py\n"
    "@@ -3,2 +3,2 @@\n"
    " def test_render_summary():\n"
    "-    assert render_summary(\"ready\") == \"Summary: ready\"\n"
    "+    assert render_summary('ready') == 'Summary: ready'\n"
)


def _review(tmp_path: Path, session: str, stdout: str):
    workspace = _workspace(tmp_path, name=f"{session}-workspace")
    runtime_root = tmp_path / f"{session}-runtime"
    values = iter([ALIGNMENT_REQUEST, "/send", "/approve", "/approve", "/exit"])
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=runtime_root,
            workspace=workspace,
            input_reader=lambda _prompt: next(values),
            output_writer=lambda _value: None,
        )
    finally:
        os.chdir(previous)
    runtime = result["runtime_result"]
    root = runtime_root / session
    runner = RecordingRunner(stdout=stdout)
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", runner
    )
    capture = _capture(runtime, activation, root, workspace)
    validation = _validate(runtime, activation, capture, root, workspace)
    review = prepare_codex_task_outcome_review(
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        prepared_at=CREATED_AT,
        replay_dir=root / "review",
    )
    return runtime, activation, capture, validation, review, root, workspace, runner


def _satisfied(values, *, destination: str = "decision"):
    runtime, activation, capture, validation, review, root, workspace, _ = values
    return record_codex_task_outcome_human_decision(
        review_capture=review,
        task_outcome_decision=TASK_OUTCOME_SATISFIED,
        decision_reason="Human confirmed the exact valid grounded unified diff.",
        decided_by="human.operator",
        decided_at=CREATED_AT,
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        human_decision_replay_dir=root / destination,
    )


def test_source_only_diff_is_valid_for_grounded_implementation_test_pair(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22C-SOURCE-ONLY", SOURCE_ONLY_DIFF)
    review = values[4]
    packet = review["task_outcome_review_packet_artifact"]
    observations = packet["task_outcome_observations"]
    decision = _satisfied(values)

    assert packet["pre_execution_task_outcome_criteria"]["criteria_version"] == (
        "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V2"
    )
    assert observations["unified_diff_syntactically_valid"] is True
    assert observations["changed_paths"] == ["aigol/runtime/human_interface.py"]
    assert observations["at_least_one_grounded_implementation_target_changed"] is True
    assert observations["all_changed_paths_grounded"] is True
    assert observations["both_grounded_filenames_referenced_in_output"] is False
    assert observations["grounded_file_inspection_proven"] is False
    assert observations["requested_semantic_change_present"] is True
    assert packet["task_outcome_satisfaction_eligible"] is True
    assert decision["task_outcome_satisfied"] is True
    assert decision["result_accepted"] is False
    assert decision["repository_mutation_authorized"] is False
    assert decision["repository_mutated"] is False


def test_legitimate_diff_may_change_both_grounded_files(tmp_path: Path) -> None:
    values = _review(tmp_path, "G31-22C-BOTH", SOURCE_ONLY_DIFF + TEST_DIFF)
    observations = values[4]["task_outcome_review_packet_artifact"][
        "task_outcome_observations"
    ]

    assert observations["unified_diff_syntactically_valid"] is True
    assert observations["changed_paths"] == [
        "aigol/runtime/human_interface.py",
        "tests/test_human_interface.py",
    ]
    assert observations["all_changed_paths_grounded"] is True
    assert _satisfied(values)["task_outcome_satisfied"] is True


@pytest.mark.parametrize(
    ("name", "output", "error_fragment"),
    (
        (
            "fake-empty-test",
            SOURCE_ONLY_DIFF
            + "--- a/tests/test_human_interface.py\n"
            + "+++ b/tests/test_human_interface.py\n",
            "empty or change-free",
        ),
        (
            "ungrounded",
            SOURCE_ONLY_DIFF
            + "--- a/docs/other.md\n+++ b/docs/other.md\n"
            + "@@ -1 +1 @@\n-old\n+new\n",
            "ungrounded path",
        ),
        (
            "malformed",
            "--- a/aigol/runtime/human_interface.py\n"
            "+++ b/aigol/runtime/human_interface.py\n"
            "@@ malformed @@\n-Status:\n+Summary:\n",
            "malformed unified-diff hunk",
        ),
        (
            "missing-semantic-change",
            SOURCE_ONLY_DIFF.replace("Summary:", "State:"),
            "requested semantic change is absent",
        ),
        (
            "traversal",
            "--- a/../human_interface.py\n+++ b/../human_interface.py\n"
            "@@ -1 +1 @@\n-Status:\n+Summary:\n",
            "path traversal",
        ),
        (
            "absolute",
            "--- /tmp/human_interface.py\n+++ /tmp/human_interface.py\n"
            "@@ -1 +1 @@\n-Status:\n+Summary:\n",
            "absolute unified-diff path",
        ),
        (
            "renamed",
            "--- a/aigol/runtime/human_interface.py\n"
            "+++ b/tests/test_human_interface.py\n"
            "@@ -1 +1 @@\n-Status:\n+Summary:\n",
            "renamed or substituted",
        ),
        (
            "git-header-substitution",
            "diff --git a/aigol/runtime/human_interface.py "
            "b/tests/test_human_interface.py\n"
            "--- a/aigol/runtime/human_interface.py\n"
            "+++ b/aigol/runtime/human_interface.py\n"
            "@@ -1 +1 @@\n-Status:\n+Summary:\n",
            "renamed or substituted",
        ),
    ),
)
def test_invalid_diff_cannot_be_recorded_as_satisfied(
    tmp_path: Path, name: str, output: str, error_fragment: str
) -> None:
    values = _review(tmp_path, f"G31-22C-{name}", output)
    packet = values[4]["task_outcome_review_packet_artifact"]
    blockers = packet["deterministic_satisfaction_blockers"]

    assert packet["task_outcome_satisfaction_eligible"] is False
    assert any(error_fragment in item for item in (
        packet["task_outcome_observations"]["unified_diff_errors"] + blockers
    ))
    with pytest.raises(FailClosedRuntimeError, match="satisfaction failed closed"):
        _satisfied(values)
    assert not (values[5] / "decision").exists()


def test_future_criteria_are_bound_before_execution_and_immutable(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22C-BOUND", SOURCE_ONLY_DIFF)
    activation = values[1]
    criteria = activation["synthesis_preflight_capture"]["worker_execution_contract"][
        "task_outcome_criteria"
    ]

    assert criteria["established_before_worker_execution"] is True
    assert criteria["established_stage"] == "BEFORE_THIRD_HUMAN_ACTIVATION_DECISION"
    assert criteria["grounded_target_semantics"][
        "unchanged_grounded_test_target_allowed"
    ] is True
    assert criteria["inspection_evidence_contract"][
        "unified_diff_proves_file_inspection"
    ] is False
    assert criteria["criteria_hash"] == activation["activation_approval_artifact"][
        "task_outcome_criteria_hash"
    ]

    changed = deepcopy(activation)
    changed["synthesis_preflight_capture"]["worker_execution_contract"][
        "task_outcome_criteria"
    ]["requirements"].append("POST_EXECUTION_SUBSTITUTION")
    with pytest.raises(FailClosedRuntimeError):
        activation_runtime.reconstruct_codex_worker_activation_binding(
            activation_capture=changed,
            governed_execution_capture=values[0]["governed_worker_execution_capture"],
            execution_candidate_capture=values[0]["worker_execution_candidate_capture"],
            session_root=values[5],
            workspace=values[6],
        )


def test_legacy_v1_criteria_remain_reconstructable_without_reinterpretation(
    tmp_path: Path,
) -> None:
    values = _review(tmp_path, "G31-22C-LEGACY", SOURCE_ONLY_DIFF)
    runtime, _, _, _, _, root, workspace, _ = values
    lineage = activation_runtime._reconstruct_lineage(
        runtime["governed_worker_execution_capture"],
        runtime["worker_execution_candidate_capture"],
        root,
        workspace,
    )
    legacy = activation_runtime._grounded_worker_execution_contract(
        lineage,
        criteria_version=activation_runtime.LEGACY_TASK_OUTCOME_CRITERIA_VERSION,
    )["task_outcome_criteria"]

    assert legacy["criteria_version"] == "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1"
    assert legacy["requirements"] == [
        "HUMAN_MUST_REVIEW_EXACT_OUTPUT_AGAINST_EXACT_AUTHORIZED_TASK",
        "OUTPUT_TYPE_MUST_EQUAL_PREAUTHORIZED_OUTPUT_TYPE",
        "OUTPUT_TARGETS_MUST_NOT_EXCEED_GROUNDED_TARGETS",
        "PATCH_MUST_REMAIN_UNAPPLIED_DURING_TASK_OUTCOME_REVIEW",
        "TASK_SATISFACTION_MUST_NOT_IMPLY_RESULT_ACCEPTANCE",
        "TASK_SATISFACTION_MUST_NOT_AUTHORIZE_REPOSITORY_MUTATION",
    ]
    assert "grounded_target_semantics" not in legacy
    assert "inspection_evidence_contract" not in legacy
    historic_observations = review_runtime._output_observations(
        SOURCE_ONLY_DIFF,
        allowed_targets={
            "aigol/runtime/human_interface.py",
            "tests/test_human_interface.py",
        },
        implementation_targets={"aigol/runtime/human_interface.py"},
        criteria=legacy,
    )
    assert historic_observations["both_grounded_filenames_referenced_in_output"] is False
    assert review_runtime.DECISION_TO_HUMAN_DECISION[
        review_runtime.TASK_OUTCOME_UNSATISFIED
    ] == "REJECT"
