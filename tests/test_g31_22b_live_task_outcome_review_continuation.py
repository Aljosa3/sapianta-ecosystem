from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import os

import pytest

from aigol.cli import aicli
from aigol.runtime import codex_task_outcome_human_review_runtime as review_runtime
from aigol.runtime.codex_worker_activation_binding_runtime import (
    reconstruct_codex_worker_activation_binding,
    reconstruct_codex_worker_activation_replay,
)
from aigol.runtime.codex_transport_to_worker_result_capture_binding_runtime import (
    reconstruct_codex_worker_result_capture_binding,
)
from aigol.runtime.codex_worker_result_to_semantic_validation_binding_runtime import (
    reconstruct_codex_worker_semantic_validation_binding,
)
from test_g31_20f_disposable_repository_scope_grounding_fixture_contract import (
    CREATED_AT,
    _workspace,
)


LIVE_REQUEST = (
    "Fix Summary test: inspect aigol/runtime/human_interface.py and "
    "tests/test_human_interface.py; return a minimal Status:-to-Summary: unified "
    "diff; do not edit files."
)
EXACT_TWO_TARGET_DIFF = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f'Status: {value}'\n"
    "+    return f'Summary: {value}'\n"
    "--- a/tests/test_human_interface.py\n"
    "+++ b/tests/test_human_interface.py\n"
    "@@ -2,2 +2,2 @@\n"
    " def test_render_summary():\n"
    "-    assert render_summary('ready') == \"Summary: ready\"\n"
    "+    assert render_summary('ready') == 'Summary: ready'\n"
)


class RecordingRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=EXACT_TWO_TARGET_DIFF, stderr="")


def _run(tmp_path: Path, session: str, final_command: str | None):
    workspace = _workspace(tmp_path, name=f"{session}-workspace")
    runtime_root = tmp_path / f"{session}-runtime"
    inputs = [LIVE_REQUEST, "/send", "/approve", "/approve", "/approve"]
    if final_command is not None:
        inputs.append(final_command)
    output: list[str] = []
    values = iter(inputs)
    runner = RecordingRunner()
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=runtime_root,
            workspace=workspace,
            input_reader=lambda _prompt: next(values),
            output_writer=output.append,
            worker_process_runner=runner,
        )
    finally:
        os.chdir(previous)
    return result, output, runtime_root / session, workspace, runner


def test_satisfied_continuation_binds_exact_bytes_and_stops(tmp_path: Path) -> None:
    result, output, root, workspace, runner = _run(
        tmp_path, "G31-22B-SATISFIED", "/satisfied"
    )
    runtime = result["runtime_result"]
    review = runtime["codex_task_outcome_review_capture"]
    packet = review["task_outcome_review_packet_artifact"]
    decision = runtime["codex_task_outcome_human_decision_capture"]

    assert len(LIVE_REQUEST) < 180
    assert result["human_execution_decision_count"] == 3
    assert result["human_task_outcome_decision_count"] == 1
    assert result["total_human_decision_count"] == 4
    assert len(runner.calls) == 1
    assert runner.calls[0][0][:2] == ["codex", "exec"]
    assert runner.calls[0][1]["shell"] is False
    assert runner.calls[0][1]["timeout"] == 60
    assert packet["exact_worker_output"]["text"] == EXACT_TWO_TARGET_DIFF
    assert packet["task_outcome_observations"][
        "both_grounded_filenames_referenced_in_output"
    ] is True
    assert decision["task_outcome_decision"] == review_runtime.TASK_OUTCOME_SATISFIED
    assert runtime["task_outcome_satisfaction_evaluated"] is True
    assert runtime["task_outcome_satisfied"] is True
    assert runtime["result_accepted"] is False
    assert runtime["repository_mutation_authorized"] is False
    assert runtime["repository_mutated"] is False
    assert runtime["additional_worker_process_started"] is False
    assert runtime["task_outcome_review_count"] == 1
    assert runtime["task_outcome_review_replay_created"] is True
    assert result["exit_reason"] == "TASK_OUTCOME_HUMAN_DECISION_RECORDED"
    assert "Exact Proposed Output:\n" + EXACT_TWO_TARGET_DIFF in "\n".join(output)
    assert "Capture Identity:" in "\n".join(output)
    assert "GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY" in "\n".join(output)
    _reconstruct_all(runtime, review, root, workspace)


@pytest.mark.parametrize(
    ("command", "outcome", "rework"),
    (
        ("/unsatisfied", review_runtime.TASK_OUTCOME_UNSATISFIED, False),
        ("/rework", review_runtime.REWORK_REQUESTED, True),
    ),
)
def test_unsatisfied_and_rework_stop_without_retry(
    tmp_path: Path, command: str, outcome: str, rework: bool
) -> None:
    result, _, _, _, runner = _run(tmp_path, f"G31-22B-{outcome}", command)
    runtime = result["runtime_result"]

    assert len(runner.calls) == 1
    assert result["total_human_decision_count"] == 4
    assert runtime["task_outcome_review_status"] == outcome
    assert runtime["task_outcome_satisfaction_evaluated"] is True
    assert runtime["task_outcome_satisfied"] is False
    assert runtime["rework_requested"] is rework
    assert runtime["automatic_retry_performed"] is False
    assert runtime["additional_worker_process_started"] is False
    assert runtime["repository_mutation_authorized"] is False
    assert runtime["result_accepted"] is False


def test_exact_review_is_displayed_before_any_task_outcome_decision(
    tmp_path: Path,
) -> None:
    result, output, _, _, runner = _run(tmp_path, "G31-22B-PENDING", None)
    runtime = result["runtime_result"]

    assert len(runner.calls) == 1
    assert result["pending_task_outcome_decision"] is True
    assert result["human_execution_decision_count"] == 3
    assert result["human_task_outcome_decision_count"] == 0
    assert "codex_task_outcome_human_decision_capture" not in runtime
    rendered = "\n".join(output)
    assert EXACT_TWO_TARGET_DIFF in rendered
    assert "Use /satisfied, /unsatisfied, or /rework" in rendered


def _reconstruct_all(runtime: dict, review: dict, root: Path, workspace: Path) -> None:
    common = {
        "activation_capture": runtime["codex_worker_activation_capture"],
        "governed_execution_capture": runtime["governed_worker_execution_capture"],
        "execution_candidate_capture": runtime["worker_execution_candidate_capture"],
        "session_root": root,
        "workspace": workspace,
    }
    activation = reconstruct_codex_worker_activation_binding(**common)
    assert activation["activation_replay_hash"]
    assert reconstruct_codex_worker_activation_replay(
        runtime["codex_worker_activation_capture"]["activation_replay_reference"]
    )["replay_artifact_count"] == 3
    assert reconstruct_codex_worker_result_capture_binding(
        binding_capture=runtime["codex_worker_result_capture_binding_capture"],
        **common,
    )["replay_artifact_count"] == 4
    assert reconstruct_codex_worker_semantic_validation_binding(
        validation_binding_capture=runtime[
            "codex_worker_semantic_validation_binding_capture"
        ],
        result_capture_binding_capture=runtime[
            "codex_worker_result_capture_binding_capture"
        ],
        **common,
    )["replay_artifact_count"] == 4
    assert review_runtime.reconstruct_codex_task_outcome_review(
        review_capture=review,
        result_capture_binding_capture=runtime[
            "codex_worker_result_capture_binding_capture"
        ],
        validation_binding_capture=runtime[
            "codex_worker_semantic_validation_binding_capture"
        ],
        **common,
    )["review_replay_artifact_count"] == 2
