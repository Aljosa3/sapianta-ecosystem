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
from aigol.runtime.implementation_manifest_runtime import (
    IMPLEMENTATION_MANIFEST_ARTIFACT_V2,
    REPLACE_CONTENT,
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
            ["git", "config", "user.name", "G31 R04"],
            ["git", "config", "user.email", "g31-r04@example.invalid"],
            ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
            ["git", "commit", "-m", "fixture baseline"],
        ):
            subprocess.run(command, cwd=workspace, check=True, capture_output=True, text=True)
        return workspace

    monkeypatch.setattr(r02, "_workspace", git_workspace)


def _forbid_acceptance_and_authorization(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"accept": 0, "authorization": 0}

    def forbidden(name: str):
        def _raise(*_args: object, **_kwargs: object) -> None:
            calls[name] += 1
            raise AssertionError(f"R04 must not call {name}")
        return _raise

    monkeypatch.setattr(acceptance, "accept_generated_content", forbidden("accept"))
    monkeypatch.setattr(mutation_authorization, "authorize_filesystem_mutation", forbidden("authorization"))
    return calls


def test_successful_r03_outcome_binds_exact_ten_captures_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    downstream = _forbid_acceptance_and_authorization(monkeypatch)
    real_bind = prerequisites.bind_codex_replacement_acceptance_prerequisites
    real_execute = disposable.execute_disposable_patch_validation
    real_command = disposable.execute_validation_command
    bind_calls: list[dict] = []
    execute_calls = 0
    command_calls = 0

    def bind_once(**kwargs):
        bind_calls.append(kwargs)
        return real_bind(**kwargs)

    def execute_once(**kwargs):
        nonlocal execute_calls
        execute_calls += 1
        return real_execute(**kwargs)

    def command_once(**kwargs):
        nonlocal command_calls
        command_calls += 1
        return real_command(**kwargs)

    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", bind_once)
    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", execute_once)
    monkeypatch.setattr(disposable, "execute_validation_command", command_once)
    result, output, root, source, runner = r02._run(
        tmp_path, "G31-R04-SUCCESS", ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    capture = runtime["codex_replacement_acceptance_prerequisite_binding_capture"]
    reconstructed = runtime["codex_replacement_acceptance_prerequisite_binding_reconstruction"]
    manifest = capture["implementation_manifest_capture"]["implementation_manifest_artifact"]

    assert result["exit_reason"] == "REPLACEMENT_ACCEPTANCE_PREREQUISITES_BOUND"
    assert len(bind_calls) == execute_calls == command_calls == 1
    expected = {
        "disposable_validation_outcome_capture": "disposable_patch_validation_outcome_capture",
        "disposable_validation_review_capture": "disposable_patch_validation_review_capture",
        "application_decision_capture": "disposable_patch_validation_human_decision_capture",
        "task_outcome_decision_capture": "codex_task_outcome_human_decision_capture",
        "task_outcome_review_capture": "codex_task_outcome_review_capture",
        "result_capture_binding_capture": "codex_worker_result_capture_binding_capture",
        "governance_validation_binding_capture": "codex_worker_semantic_validation_binding_capture",
        "activation_capture": "codex_worker_activation_capture",
        "governed_execution_capture": "governed_worker_execution_capture",
        "execution_candidate_capture": "worker_execution_candidate_capture",
    }
    assert all(bind_calls[0][parameter] == runtime[field] for parameter, field in expected.items())
    assert manifest["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V2
    assert manifest["manifest_contract_version"] == "V2"
    assert manifest["operation_mode"] == REPLACE_CONTENT
    assert capture["acceptance_prerequisites_satisfied"] is True
    assert runtime["ready_for_acceptance"] is True
    assert runtime["result_accepted"] is False
    assert runtime["mutation_authorized"] is False
    assert runtime["main_repository_mutated"] is False
    assert reconstructed["binding_hash"] == capture["binding_artifact"]["artifact_hash"]
    assert reconstructed["replay_artifact_count"] == 1
    presentation = "\n".join(output)
    assert "Captured Replacement Acceptance Prerequisites" in presentation
    assert "Operation: REPLACE_CONTENT" in presentation
    assert "Ready For Human Acceptance: True" in presentation
    assert "Result Accepted: False" in presentation
    assert "Mutation Authorized: False" in presentation
    assert downstream == {"accept": 0, "authorization": 0}
    assert runner.calls and len(runner.calls) == 1
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""
    assert sha256((source / "aigol/runtime/human_interface.py").read_bytes()).hexdigest() == (
        "bd12492ff3e10bcc46c6bd0ab7bcc007224a00151367b02110942400718b0709"
    )
    assert root == Path(capture["binding_replay_reference"]).parent
    assert "generated_content_acceptance_capture" not in runtime


def test_failed_focused_validation_stops_before_binder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
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
        subprocess.run(
            ["git", "commit", "-m", "failing focused test"], cwd=workspace,
            check=True, capture_output=True, text=True,
        )
        return workspace

    def forbidden(*_args: object, **_kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise AssertionError("failed R03 outcome must not reach G31-23B")

    monkeypatch.setattr(r02, "_workspace", failing_workspace)
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", forbidden)
    result, _, _, source, _ = r02._run(
        tmp_path, "G31-R04-FAILED-TEST", ["/satisfied", "/approve"]
    )
    runtime = result["runtime_result"]
    assert calls == 0
    assert result["exit_reason"] == "DISPOSABLE_PATCH_VALIDATION_OUTCOME_RECORDED"
    assert runtime["grounded_test_validation_passed"] is False
    assert runtime["ready_for_acceptance"] is False
    assert "codex_replacement_acceptance_prerequisite_binding_capture" not in runtime
    assert subprocess.run(
        ["git", "status", "--short"], cwd=source, check=True, capture_output=True, text=True
    ).stdout == ""


def test_source_drift_after_r03_fails_before_binder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_execute = disposable.execute_disposable_patch_validation
    binder_calls = 0

    def execute_then_drift(**kwargs):
        outcome = real_execute(**kwargs)
        Path(kwargs["source_workspace"], "README.md").write_text("drift\n", encoding="utf-8")
        return outcome

    def forbidden(*_args: object, **_kwargs: object) -> None:
        nonlocal binder_calls
        binder_calls += 1
        raise AssertionError("source drift must fail before binder")

    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", execute_then_drift)
    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", forbidden)
    with pytest.raises(FailClosedRuntimeError, match="workspace|identity|source repository drift"):
        r02._run(tmp_path, "G31-R04-SOURCE-DRIFT", ["/satisfied", "/approve"])
    assert binder_calls == 0


@pytest.mark.parametrize("substitution", ["postimage", "cross-session-replay"])
def test_changed_r03_evidence_fails_without_readiness_or_downstream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, substitution: str,
) -> None:
    downstream = _forbid_acceptance_and_authorization(monkeypatch)
    real_bind = prerequisites.bind_codex_replacement_acceptance_prerequisites

    def substituted(**kwargs):
        changed = dict(kwargs)
        if substitution == "postimage":
            plan = changed["disposable_validation_review_capture"][
                "disposable_patch_validation_plan_artifact"
            ]
            Path(plan["disposable_workspace"], plan["changed_paths"][0]).write_text(
                "SUBSTITUTED = True\n", encoding="utf-8"
            )
        else:
            changed["disposable_validation_outcome_capture"] = deepcopy(
                changed["disposable_validation_outcome_capture"]
            )
            changed["disposable_validation_outcome_capture"]["outcome_replay_reference"] = str(
                tmp_path / "OTHER-SESSION" / "outcome"
            )
        return real_bind(**changed)

    monkeypatch.setattr(prerequisites, "bind_codex_replacement_acceptance_prerequisites", substituted)
    with pytest.raises(FailClosedRuntimeError):
        r02._run(tmp_path, f"G31-R04-{substitution}", ["/satisfied", "/approve"])
    assert downstream == {"accept": 0, "authorization": 0}
