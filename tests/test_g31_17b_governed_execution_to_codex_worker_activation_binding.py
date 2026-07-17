from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from aigol.cli import aicli
from aigol.runtime.codex_worker_activation_binding_runtime import (
    ACTIVATION_APPROVAL_SCOPE,
    ACTIVATION_TIMEOUT_SECONDS,
    activate_bounded_codex_worker,
    reconstruct_codex_worker_activation_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT, REQUEST, _workspace


class RecordingRunner:
    def __init__(self, *, returncode: int = 0, stdout: str = "bounded output", stderr: str = "") -> None:
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, args: list[str], **kwargs: object) -> SimpleNamespace:
        self.calls.append((args, kwargs))
        return SimpleNamespace(returncode=self.returncode, stdout=self.stdout, stderr=self.stderr)


def _run(tmp_path: Path, session: str, inputs: list[str], runner=None) -> tuple[dict, list[str], Path, Path]:
    workspace = _workspace(tmp_path, name=f"{session}-workspace")
    root = tmp_path / "runtime"
    output: list[str] = []
    values = iter(inputs)
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session, created_at=CREATED_AT, runtime_root=root, workspace=workspace,
            input_reader=lambda _prompt: next(values), output_writer=output.append,
            worker_process_runner=runner,
        )
    finally:
        os.chdir(previous)
    return result, output, root / session, workspace


def _two_decisions(tmp_path: Path, session: str) -> tuple[dict, Path, Path]:
    result, _, root, workspace = _run(
        tmp_path, session, [REQUEST, "/send", "/approve", "/approve", "/exit"]
    )
    return result["runtime_result"], root, workspace


def _activate_direct(runtime: dict, root: Path, workspace: Path, destination: Path, runner) -> dict:
    review = runtime["codex_worker_activation_review_capture"]["activation_review_artifact"]
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        return activate_bounded_codex_worker(
            activation_review_artifact=review,
            governed_execution_capture=runtime["governed_worker_execution_capture"],
            execution_candidate_capture=runtime["worker_execution_candidate_capture"],
            human_decision="APPROVE", decided_by="HUMAN_OPERATOR_VIA_AICLI",
            decided_at=CREATED_AT, session_root=root, workspace=workspace,
            replay_dir=destination, runner=runner,
        )
    finally:
        os.chdir(previous)


def test_third_approval_activates_one_fixed_codex_worker_process(tmp_path: Path) -> None:
    runner = RecordingRunner()
    result, output, _, workspace = _run(
        tmp_path, "G31-17B-SUCCESS",
        [REQUEST, "/send", "/approve", "/approve", "/approve", "/exit"], runner,
    )
    runtime = result["runtime_result"]
    activation = runtime["codex_worker_activation_capture"]
    approval = activation["activation_approval_artifact"]

    assert result["approval_count"] == 3
    assert approval["approval_scope"] == ACTIVATION_APPROVAL_SCOPE
    assert approval["worker_process_activation_allowed"] is True
    assert approval["provider_invocation_allowed"] is False
    assert approval["worker_result_capture_allowed"] is False
    assert approval["repository_mutation_allowed"] is False
    assert activation["third_human_decision_recorded"] is True
    assert activation["worker_process_started"] is True
    assert activation["subprocess_invoked"] is True
    assert activation["fixed_codex_exec_command_used"] is True
    assert activation["transport_receipt_created"] is True
    assert activation["provider_invoked"] is False
    assert activation["semantic_worker_result_captured"] is False
    assert activation["result_accepted"] is False
    assert activation["repository_mutated"] is False
    assert len(runner.calls) == 1
    args, kwargs = runner.calls[0]
    assert args[:2] == ["codex", "exec"] and len(args) == 3
    assert kwargs == {
        "capture_output": True, "text": True, "shell": False,
        "timeout": ACTIVATION_TIMEOUT_SECONDS,
    }
    assert activation["approved_workspace"] == str(workspace.resolve())
    reconstructed = reconstruct_codex_worker_activation_replay(
        activation["activation_replay_reference"]
    )
    assert reconstructed["replay_artifact_count"] == 3
    assert "Bounded CODEX Worker Process Activation Review" in "\n".join(output)


def test_two_decisions_only_leave_activation_pending_without_process(tmp_path: Path) -> None:
    runner = RecordingRunner()
    result, output, _, _ = _run(
        tmp_path, "G31-17B-PENDING", [REQUEST, "/send", "/approve", "/approve", "/exit"], runner
    )
    assert result["pending_worker_activation_decision"] is True
    assert result["approval_count"] == 2
    assert not runner.calls
    assert result["runtime_result"]["worker_process_started"] is False
    assert "The next exact /approve permits one fixed codex exec process" in "\n".join(output)


def test_third_cancel_records_rejection_without_process(tmp_path: Path) -> None:
    runner = RecordingRunner()
    result, _, _, _ = _run(
        tmp_path, "G31-17B-REJECT",
        [REQUEST, "/send", "/approve", "/approve", "/cancel", "/exit"], runner,
    )
    runtime = result["runtime_result"]
    assert runtime["third_human_decision_recorded"] is True
    assert runtime["worker_process_activation_allowed"] is False
    assert runtime.get("subprocess_invoked", False) is False
    assert not runner.calls


@pytest.mark.parametrize(("returncode", "expected_status"), ((7, "EXECUTION_FAILURE"),))
def test_injected_runner_failure_still_creates_truthful_transport_receipt(
    tmp_path: Path, returncode: int, expected_status: str
) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-FAILURE")
    capture = _activate_direct(runtime, root, workspace, root / "activation", RecordingRunner(returncode=returncode))
    assert capture["activation_status"] == expected_status
    assert capture["worker_process_started"] is True
    assert capture["transport_receipt_created"] is True
    assert capture["semantic_worker_result_captured"] is False


def test_timeout_and_output_capture_remain_bounded(tmp_path: Path) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-TIMEOUT")

    def timeout_runner(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs["timeout"], output="o" * 5000, stderr="e" * 5000)

    capture = _activate_direct(runtime, root, workspace, root / "activation", timeout_runner)
    assert capture["activation_status"] == "EXECUTION_TIMEOUT"
    assert capture["bounded_dispatch"]["timed_out"] is True
    assert len(capture["bounded_dispatch"]["stdout"]) == 4096
    assert len(capture["bounded_dispatch"]["stderr"]) == 4096


def test_exact_scope_changed_candidate_and_cross_session_fail_before_runner(tmp_path: Path) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-FAIL-CLOSED")
    runner = RecordingRunner()
    changed_review = deepcopy(runtime["codex_worker_activation_review_capture"]["activation_review_artifact"])
    changed_review["execution_scope"]["provider_invocation_allowed"] = True
    changed_review["artifact_hash"] = replay_hash({k: v for k, v in changed_review.items() if k != "artifact_hash"})
    runtime["codex_worker_activation_review_capture"]["activation_review_artifact"] = changed_review
    with pytest.raises(FailClosedRuntimeError, match="review or lineage"):
        _activate_direct(runtime, root, workspace, root / "activation-scope", runner)

    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-CANDIDATE-TAMPER")
    runtime["worker_execution_candidate_capture"] = deepcopy(runtime["worker_execution_candidate_capture"])
    runtime["worker_execution_candidate_capture"]["worker_execution_candidate_artifact"]["worker_identity"]["worker_id"] = "OPENAI"
    with pytest.raises(FailClosedRuntimeError):
        _activate_direct(runtime, root, workspace, root / "activation-candidate", runner)
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        _activate_direct(runtime, root, workspace, tmp_path / "other-session" / "activation", runner)
    assert not runner.calls


def test_governed_replay_tamper_and_repository_drift_fail_before_runner(tmp_path: Path) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-GOVERNED-TAMPER")
    replay = Path(runtime["governed_worker_execution_capture"]["worker_execution_replay_reference"])
    wrapper = load_json(replay / "001_worker_execution_result_recorded.json")
    wrapper["artifact"]["worker_evidence"]["subprocess_invoked"] = True
    (replay / "001_worker_execution_result_recorded.json").write_text("{}", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        _activate_direct(runtime, root, workspace, root / "activation-tamper", RecordingRunner())

    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-DRIFT")
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text("changed\n", encoding="utf-8")
    runner = RecordingRunner()
    with pytest.raises(FailClosedRuntimeError):
        _activate_direct(runtime, root, workspace, root / "activation-drift", runner)
    assert not runner.calls


def test_duplicate_destination_and_approval_reuse_fail_closed(tmp_path: Path) -> None:
    runtime, root, workspace = _two_decisions(tmp_path, "G31-17B-ONE-TIME")
    runner = RecordingRunner()
    _activate_direct(runtime, root, workspace, root / "activation-one", runner)
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        _activate_direct(runtime, root, workspace, root / "activation-one", runner)
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        _activate_direct(runtime, root, workspace, root / "activation-two", runner)
    assert len(runner.calls) == 1
