from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import os

import pytest

from aigol.cli import aicli
from aigol.runtime import (
    codex_satisfied_outcome_disposable_validation_binding_runtime as disposable,
    codex_replacement_acceptance_prerequisite_binding_runtime as prerequisites,
    generated_content_acceptance_runtime as acceptance,
    human_decision_runtime as human_decision,
    human_decision_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_20f_disposable_repository_scope_grounding_fixture_contract import (
    CREATED_AT,
    _workspace,
)


REQUEST = (
    "Fix Summary test: inspect aigol/runtime/human_interface.py and "
    "tests/test_human_interface.py; return a minimal Status:-to-Summary: unified "
    "diff; do not edit files."
)
VALID_PATCH = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f'Status: {value}'\n"
    "+    return f'Summary: {value}'\n"
)


class RecordingRunner:
    def __init__(self, stdout: str = VALID_PATCH) -> None:
        self.stdout = stdout
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=self.stdout, stderr="")


def _run(tmp_path: Path, session: str, tail: list[str], *, patch: str = VALID_PATCH):
    workspace = _workspace(tmp_path, name=f"{session}-workspace")
    runtime_root = tmp_path / f"{session}-runtime"
    inputs = iter([REQUEST, "/send", "/approve", "/approve", "/approve", *tail])
    output: list[str] = []
    runner = RecordingRunner(patch)
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=runtime_root,
            workspace=workspace,
            input_reader=lambda _prompt: next(inputs),
            output_writer=output.append,
            worker_process_runner=runner,
        )
    finally:
        os.chdir(previous)
    return result, output, runtime_root / session, workspace, runner


def _forbid(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"execute": 0, "binder": 0, "accept": 0}

    def forbidden(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            calls[name] += 1
            raise AssertionError(f"{name} must not be called by R02")
        return _raise

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", forbidden("execute"))
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", forbidden("binder"))
    monkeypatch.setattr(acceptance, "accept_generated_content", forbidden("accept"))
    return calls


def test_satisfied_path_prepares_and_records_existing_disposable_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _forbid(monkeypatch)
    result, output, root, workspace, runner = _run(tmp_path, "G31-R02-APPROVE", ["/satisfied", "/approve"])
    runtime = result["runtime_result"]
    review = runtime["disposable_patch_validation_review_capture"]
    decision = runtime["disposable_patch_validation_human_decision_capture"]

    assert result["exit_reason"] == "DISPOSABLE_PATCH_VALIDATION_HUMAN_DECISION_RECORDED"
    assert result["pending_disposable_patch_validation_decision"] is False
    assert runtime["task_outcome_satisfied"] is True
    assert runtime["disposable_patch_validation_review_pending"] is False
    assert runtime["disposable_patch_validation_decision_recorded"] is True
    assert runtime["disposable_patch_validation_executed"] is False
    assert runtime["ready_for_acceptance"] is False
    assert runtime["result_accepted"] is False
    assert runtime["mutation_authorized"] is False
    assert runtime["main_repository_mutated"] is False
    assert decision["decision"] == human_decision.APPROVE
    assert runner.calls and len(runner.calls) == 1
    assert "Captured Disposable Patch Validation Review" in "\n".join(output)
    assert "Human Decision" in "\n".join(output)
    assert disposable.reconstruct_disposable_patch_validation_review(
        review_binding_capture=review,
        task_outcome_decision_capture=runtime["codex_task_outcome_human_decision_capture"],
        review_capture=runtime["codex_task_outcome_review_capture"],
        result_capture_binding_capture=runtime["codex_worker_result_capture_binding_capture"],
        validation_binding_capture=runtime["codex_worker_semantic_validation_binding_capture"],
        activation_capture=runtime["codex_worker_activation_capture"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root, source_workspace=workspace,
    )["replay_artifact_count"] == 2
    assert human_decision_runtime.reconstruct_human_decision_replay(
        decision["human_decision_replay_reference"]
    )["decision"] == human_decision.APPROVE
    assert not Path(review["disposable_patch_validation_plan_artifact"]["disposable_workspace"]).exists()
    assert calls == {"execute": 0, "binder": 0, "accept": 0}


def test_pending_and_negative_decisions_stop_without_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _forbid(monkeypatch)
    pending, _, _, workspace, _ = _run(tmp_path, "G31-R02-PENDING", ["/satisfied"])
    pending_runtime = pending["runtime_result"]
    assert pending["exit_reason"] == "EOF_AWAITING_DISPOSABLE_PATCH_VALIDATION_DECISION"
    assert pending["pending_disposable_patch_validation_decision"] is True
    assert pending_runtime["disposable_patch_validation_review_pending"] is True
    assert pending_runtime["disposable_patch_validation_decision_recorded"] is False

    before = sha256((workspace / "aigol/runtime/human_interface.py").read_bytes()).hexdigest()
    rejected, _, _, rejected_workspace, _ = _run(tmp_path, "G31-R02-REJECT", ["/satisfied", "/cancel"])
    runtime = rejected["runtime_result"]
    assert rejected["exit_reason"] == "DISPOSABLE_PATCH_VALIDATION_HUMAN_DECISION_RECORDED"
    assert runtime["disposable_patch_validation_human_decision_capture"]["decision"] == human_decision.REJECT
    assert runtime["disposable_patch_validation_executed"] is False
    assert runtime["ready_for_acceptance"] is False
    assert runtime["result_accepted"] is False
    assert runtime["mutation_authorized"] is False
    assert sha256((rejected_workspace / "aigol/runtime/human_interface.py").read_bytes()).hexdigest() == before
    assert calls == {"execute": 0, "binder": 0, "accept": 0}


@pytest.mark.parametrize("tail", (["/approve"], ["/satisfied", "/unexpected"]))
def test_out_of_context_or_ambiguous_commands_do_not_create_disposable_evidence(
    tmp_path: Path, tail: list[str],
) -> None:
    result, _, _, _, _ = _run(tmp_path, f"G31-R02-COMMAND-{len(tail)}", tail)
    runtime = result["runtime_result"]
    assert "disposable_patch_validation_human_decision_capture" not in runtime
    assert runtime.get("disposable_patch_validation_executed") is not True


def test_changed_patch_fails_closed_before_disposable_review(tmp_path: Path) -> None:
    changed = VALID_PATCH.replace("Status: {value}", "State: {value}")
    with pytest.raises(FailClosedRuntimeError, match="task-outcome satisfaction failed closed"):
        _run(tmp_path, "G31-R02-CHANGED", ["/satisfied"], patch=changed)


def test_reconstructed_review_rejects_cross_session_and_replay_substitution(
    tmp_path: Path,
) -> None:
    result, _, root, workspace, _ = _run(tmp_path, "G31-R02-TAMPER", ["/satisfied"])
    runtime = result["runtime_result"]
    review = runtime["disposable_patch_validation_review_capture"]
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        disposable.reconstruct_disposable_patch_validation_review(
            review_binding_capture=review,
            task_outcome_decision_capture=runtime["codex_task_outcome_human_decision_capture"],
            review_capture=runtime["codex_task_outcome_review_capture"],
            result_capture_binding_capture=runtime["codex_worker_result_capture_binding_capture"],
            validation_binding_capture=runtime["codex_worker_semantic_validation_binding_capture"],
            activation_capture=runtime["codex_worker_activation_capture"],
            governed_execution_capture=runtime["governed_worker_execution_capture"],
            execution_candidate_capture=runtime["worker_execution_candidate_capture"],
            session_root=root.parent / "other", source_workspace=workspace,
        )
