from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import codex_transport_to_worker_result_capture_binding_runtime as bridge
from aigol.runtime.codex_transport_to_worker_result_capture_binding_runtime import (
    FAILED_CLOSED,
    SUCCESS,
    capture_successful_codex_worker_result,
    reconstruct_codex_worker_result_capture_binding,
)
from aigol.runtime.transport.serialization import load_json, replay_hash
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
    _run,
    _two_decisions,
)
from test_g31_09_distinct_human_execution_decision_binding import REQUEST


def _activated(tmp_path: Path, session: str, *, runner=None):
    runtime, root, workspace = _two_decisions(tmp_path, session)
    activation = _activate_direct(
        runtime, root, workspace, root / "activation",
        runner or RecordingRunner(stdout="Authentic bounded CODEX semantic output."),
    )
    return runtime, activation, root, workspace


def _capture(runtime: dict, activation: dict, root: Path, workspace: Path, name: str = "capture"):
    return capture_successful_codex_worker_result(
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        captured_at="2026-07-17T00:00:00Z",
        replay_dir=root / name,
    )


def test_successful_receipt_captures_authentic_output_exactly_once(tmp_path: Path, monkeypatch) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-SUCCESS")
    calls = 0
    canonical = bridge.result_capture.capture_worker_result

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return canonical(**kwargs)

    monkeypatch.setattr(bridge.result_capture, "capture_worker_result", counted)
    capture = _capture(runtime, activation, root, workspace)
    assert capture["g31_result_capture_status"] == SUCCESS, capture.get("failure_reason")
    output = capture["semantic_worker_output_artifact"]

    assert calls == 1
    assert capture["transport_receipt_successful"] is True
    assert capture["authentic_worker_output_present"] is True
    assert capture["semantic_worker_result_captured"] is True
    assert output["payload"]["semantic_output"] == activation["bounded_dispatch"]["stdout"]
    assert output["payload"]["semantic_output_sha256"] == activation["codex_transport_receipt"]["stdout_hash"]
    for field in (
        "provider_invoked", "additional_worker_process_started", "result_validated",
        "result_accepted", "repository_mutated", "commit_created", "deployed", "released",
    ):
        assert capture[field] is False
    reconstructed = reconstruct_codex_worker_result_capture_binding(
        binding_capture=capture,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
    )
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["worker_output_hash"] == output["artifact_hash"]


@pytest.mark.parametrize(("runner", "reason"), (
    (RecordingRunner(returncode=9, stderr="failed"), "not an authentic successful"),
    (RecordingRunner(stdout=""), "output is empty"),
    (RecordingRunner(stdout="x" * 5000), "truncated"),
))
def test_failure_nonzero_empty_and_truncated_output_never_call_capture(
    tmp_path: Path, monkeypatch, runner, reason: str
) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, f"G31-18-{reason[:6]}", runner=runner)
    monkeypatch.setattr(
        bridge.result_capture, "capture_worker_result",
        lambda **_kwargs: pytest.fail("canonical capture must not run"),
    )
    capture = _capture(runtime, activation, root, workspace)
    assert capture["g31_result_capture_status"] == FAILED_CLOSED
    assert reason in capture["failure_reason"]
    assert capture["semantic_worker_result_captured"] is False
    assert capture["result_validated"] is False
    assert capture["result_accepted"] is False
    assert capture["repository_mutated"] is False


def test_timeout_receipt_never_calls_capture(tmp_path: Path, monkeypatch) -> None:
    def timeout_runner(args, **kwargs):
        raise subprocess.TimeoutExpired(args, kwargs["timeout"], output="partial", stderr="timeout")

    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-TIMEOUT", runner=timeout_runner)
    monkeypatch.setattr(
        bridge.result_capture, "capture_worker_result",
        lambda **_kwargs: pytest.fail("canonical capture must not run"),
    )
    capture = _capture(runtime, activation, root, workspace)
    assert capture["g31_result_capture_status"] == FAILED_CLOSED
    assert capture["semantic_worker_result_captured"] is False


@pytest.mark.parametrize("tamper", ("stdout", "receipt", "approval", "candidate"))
def test_output_receipt_approval_candidate_and_identity_tampering_fail_closed(
    tmp_path: Path, monkeypatch, tamper: str
) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, f"G31-18-TAMPER-{tamper}")
    activation = deepcopy(activation)
    runtime = deepcopy(runtime)
    if tamper == "stdout":
        activation["bounded_dispatch"]["stdout"] = "substituted output"
    elif tamper == "receipt":
        activation["codex_transport_receipt"]["stdout_hash"] = "0" * 64
    elif tamper == "approval":
        activation["activation_approval_artifact"]["registered_worker_id"] = "codex-cognition"
    else:
        runtime["worker_execution_candidate_capture"]["worker_execution_candidate_artifact"]["worker_identity"]["worker_id"] = "OPENAI"
    monkeypatch.setattr(
        bridge.result_capture, "capture_worker_result",
        lambda **_kwargs: pytest.fail("canonical capture must not run"),
    )
    capture = _capture(runtime, activation, root, workspace)
    assert capture["g31_result_capture_status"] == FAILED_CLOSED
    assert capture["semantic_worker_result_captured"] is False


def test_activation_replay_tamper_and_cross_session_fail_closed(tmp_path: Path) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-REPLAY")
    wrapper_path = Path(activation["activation_replay_reference"]) / "002_worker_activation_transport_receipt_recorded.json"
    wrapper_path.write_text("{}\n", encoding="utf-8")
    assert _capture(runtime, activation, root, workspace)["g31_result_capture_status"] == FAILED_CLOSED

    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-CROSS-SESSION")
    capture = capture_successful_codex_worker_result(
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        captured_at="2026-07-17T00:00:00Z",
        replay_dir=tmp_path / "other-session" / "capture",
    )
    assert capture["g31_result_capture_status"] == FAILED_CLOSED


def test_duplicate_destination_receipt_reuse_and_repeated_capture_fail_closed(tmp_path: Path) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-ONE-TIME")
    first = _capture(runtime, activation, root, workspace, "capture-one")
    assert first["g31_result_capture_status"] == SUCCESS
    assert _capture(runtime, activation, root, workspace, "capture-one")["g31_result_capture_status"] == FAILED_CLOSED
    second = _capture(runtime, activation, root, workspace, "capture-two")
    assert second["g31_result_capture_status"] == FAILED_CLOSED
    assert "already captured" in second["failure_reason"]


def test_repository_drift_after_transport_blocks_semantic_capture(tmp_path: Path, monkeypatch) -> None:
    runtime, activation, root, workspace = _activated(tmp_path, "G31-18-DRIFT")
    (workspace / "UNAPPROVED-DRIFT.txt").write_text("changed\n", encoding="utf-8")
    monkeypatch.setattr(
        bridge.result_capture, "capture_worker_result",
        lambda **_kwargs: pytest.fail("canonical capture must not run"),
    )
    capture = _capture(runtime, activation, root, workspace)
    assert capture["g31_result_capture_status"] == FAILED_CLOSED
    assert capture["semantic_worker_result_captured"] is False


def test_aicli_orchestrates_capture_without_fourth_decision(tmp_path: Path) -> None:
    result, output, _, _ = _run(
        tmp_path, "G31-18-AICLI",
        [REQUEST, "/send", "/approve", "/approve", "/approve", "/exit"],
        RecordingRunner(stdout="AiCLI authentic bounded result."),
    )
    runtime = result["runtime_result"]
    assert result["approval_count"] == 3
    assert runtime["semantic_worker_result_captured"] is True
    assert runtime["result_validated"] is False
    assert runtime["result_accepted"] is False
    assert result["aicli_accepts_result"] is False
    assert "CODEX Semantic Worker Result Capture" in "\n".join(output)
