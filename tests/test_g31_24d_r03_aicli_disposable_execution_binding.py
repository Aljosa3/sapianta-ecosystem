from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import (
    codex_replacement_acceptance_prerequisite_binding_runtime as prerequisites,
    codex_satisfied_outcome_disposable_validation_binding_runtime as disposable,
    filesystem_mutation_authorization_runtime as mutation_authorization,
    generated_content_acceptance_runtime as acceptance,
)
from aigol.runtime.models import FailClosedRuntimeError
import test_g31_24d_r02_aicli_task_outcome_to_disposable_review_binding as r02


@pytest.fixture(autouse=True)
def _git_source_workspace(monkeypatch: pytest.MonkeyPatch):
    original = r02._workspace

    def git_workspace(*args, **kwargs):
        workspace = original(*args, **kwargs)
        for command in (
            ["git", "init"],
            ["git", "config", "user.name", "G31 R03"],
            ["git", "config", "user.email", "g31-r03@example.invalid"],
            ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
            ["git", "commit", "-m", "fixture baseline"],
        ):
            subprocess.run(command, cwd=workspace, check=True, capture_output=True, text=True)
        return workspace

    monkeypatch.setattr(r02, "_workspace", git_workspace)


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"binder": 0, "accept": 0, "authorization": 0}

    def forbidden(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            calls[name] += 1
            raise AssertionError(f"R03 must not call {name}")
        return _raise

    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", forbidden("binder"))
    monkeypatch.setattr(acceptance, "accept_generated_content", forbidden("accept"))
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", forbidden("authorization"))
    return calls


def test_positive_r02_decision_executes_existing_owner_once_and_reconstructs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    downstream = _forbid_downstream(monkeypatch)
    real_execute = disposable.execute_disposable_patch_validation
    execute_calls: list[dict] = []

    def execute_once(**kwargs):
        execute_calls.append(kwargs)
        return real_execute(**kwargs)

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", execute_once)
    result, output, root, source, _ = r02._run(
        tmp_path, "G31-R03-SUCCESS", ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    outcome = runtime["disposable_patch_validation_outcome_capture"]
    artifact = outcome["outcome_artifact"]
    plan = runtime["disposable_patch_validation_review_capture"][
        "disposable_patch_validation_plan_artifact"
    ]
    target = Path(plan["disposable_workspace"])

    assert len(execute_calls) == 1
    assert result["exit_reason"] == "DISPOSABLE_PATCH_VALIDATION_OUTCOME_RECORDED"
    assert artifact["execution_status"] == disposable.COMPLETED
    assert runtime["disposable_patch_validation_approved"] is True
    assert runtime["disposable_patch_validation_executed"] is True
    assert runtime["disposable_patch_application_succeeded"] is True
    assert runtime["focused_validation_executed"] is True
    assert runtime["focused_validation_succeeded"] is True
    assert runtime["ready_for_acceptance"] is False
    assert runtime["result_accepted"] is False
    assert runtime["mutation_authorized"] is False
    assert runtime["main_repository_mutated"] is False
    assert artifact["source_repository_unchanged"] is True
    assert (source / "aigol/runtime/human_interface.py").read_text(encoding="utf-8").endswith("Status: {value}'\n")
    assert (target / "aigol/runtime/human_interface.py").read_text(encoding="utf-8").endswith("Summary: {value}'\n")
    command = outcome["grounded_test_validation_capture"]["validation_command_result_artifact"]
    assert command["command"] == ["python", "-m", "pytest", "tests/test_human_interface.py"]
    assert command["cwd"] == str(target)
    assert command["exit_code"] == 0
    assert command["shell_execution_used"] is False
    assert runtime["disposable_patch_validation_outcome_reconstruction"]["replay_artifact_count"] == 1
    assert "Captured Disposable Patch Validation Outcome" in "\n".join(output)
    assert downstream == {"binder": 0, "accept": 0, "authorization": 0}
    for field in (
        "disposable_patch_validation_review_capture",
        "disposable_patch_validation_human_decision_capture",
        "codex_task_outcome_human_decision_capture",
        "codex_task_outcome_review_capture",
        "codex_worker_result_capture_binding_capture",
        "codex_worker_semantic_validation_binding_capture",
        "codex_worker_activation_capture",
        "governed_worker_execution_capture",
        "worker_execution_candidate_capture",
    ):
        assert field in runtime


def test_reject_preserves_r02_no_execution_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def forbidden(*_args: object, **_kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise AssertionError("REJECT must not execute")

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", forbidden)
    result, _, _, source, _ = r02._run(
        tmp_path, "G31-R03-REJECT", ["/satisfied", "/cancel"]
    )
    runtime = result["runtime_result"]
    assert calls == 0
    assert "disposable_patch_validation_outcome_capture" not in runtime
    assert runtime["disposable_patch_validation_executed"] is False
    assert sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest() == (
        "bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709"
    )


def test_substituted_decision_fails_before_command_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_execute = disposable.execute_disposable_patch_validation
    command_calls = 0

    def substituted(**kwargs):
        changed = deepcopy(kwargs)
        changed["application_decision_capture"]["human_decision_artifact"]["decision"] = "REJECT"
        return real_execute(**changed)

    def forbidden_command(*_args: object, **_kwargs: object) -> None:
        nonlocal command_calls
        command_calls += 1
        raise AssertionError("invalid decision must fail before command execution")

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", substituted)
    monkeypatch.setattr(disposable, "execute_validation_command", forbidden_command)
    with pytest.raises(FailClosedRuntimeError, match="exact unused human approval"):
        r02._run(tmp_path, "G31-R03-SUBSTITUTED", ["/satisfied", "/approve"])
    assert command_calls == 0


def test_focused_test_failure_is_recorded_without_retry_or_downstream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    downstream = _forbid_downstream(monkeypatch)
    original_workspace = r02._workspace

    def failing_workspace(*args, **kwargs):
        workspace = original_workspace(*args, **kwargs)
        (workspace / "tests/test_human_interface.py").write_text(
            "from aigol.runtime.human_interface import render_summary\n\n"
            "def test_render_summary():\n"
            "    assert render_summary('ready') == 'Other: ready'\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "tests/test_human_interface.py"], cwd=workspace, check=True)
        subprocess.run(["git", "commit", "-m", "failing focused test"], cwd=workspace, check=True, capture_output=True, text=True)
        return workspace

    monkeypatch.setattr(r02, "_workspace", failing_workspace)
    result, output, _, source, _ = r02._run(
        tmp_path, "G31-R03-TEST-FAILURE", ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    artifact = runtime["disposable_patch_validation_outcome_capture"]["outcome_artifact"]
    assert artifact["execution_status"] == disposable.FAILED_CLOSED
    assert artifact["disposable_patch_applied"] is True
    assert artifact["grounded_test_execution_performed"] is True
    assert artifact["grounded_test_validation_passed"] is False
    assert artifact["automatic_retry_performed"] is False
    assert artifact["source_repository_unchanged"] is True
    assert artifact["ready_for_generated_content_acceptance"] is False
    assert "grounded focused test validation failed" in artifact["failure_reason"]
    assert "Execution Status: FAILED_CLOSED" in "\n".join(output)
    assert (source / "aigol/runtime/human_interface.py").read_text(encoding="utf-8").endswith("Status: {value}'\n")
    assert downstream == {"binder": 0, "accept": 0, "authorization": 0}
