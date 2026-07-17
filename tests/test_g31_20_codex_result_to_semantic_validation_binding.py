from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import codex_worker_result_to_semantic_validation_binding_runtime as bridge
from aigol.runtime.codex_worker_result_to_semantic_validation_binding_runtime import (
    FAILED_CLOSED,
    INVALID,
    SUCCESS,
    reconstruct_codex_worker_semantic_validation_binding,
    validate_captured_codex_worker_result,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
    _run,
    _two_decisions,
)
from test_g31_18_codex_transport_to_worker_result_capture_binding import _capture
from test_g31_09_distinct_human_execution_decision_binding import REQUEST


def _captured(tmp_path: Path, session: str, *, runner=None):
    runtime, root, workspace = _two_decisions(tmp_path, session)
    process_runner = runner or RecordingRunner(stdout="Authentic bounded CODEX semantic output.")
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", process_runner
    )
    capture = _capture(runtime, activation, root, workspace)
    return runtime, activation, capture, root, workspace, process_runner


def _validate(runtime, activation, capture, root, workspace, name="validation"):
    return validate_captured_codex_worker_result(
        result_capture_binding_capture=capture,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        validated_at="2026-07-17T01:00:00Z",
        replay_dir=root / name,
    )


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    return artifact


def _call_canonical_with_semantically_invalid_capture(canonical, kwargs):
    changed = deepcopy(kwargs["worker_result_capture_artifact"])
    changed["operations"] = ["MUTATE_REPOSITORY"]
    changed = _rehash(changed)
    replay = Path(kwargs["worker_result_capture_replay_reference"])

    capture_path = replay / "002_result_capture_artifact_recorded.json"
    capture_wrapper = load_json(capture_path)
    capture_wrapper["artifact"] = changed
    capture_wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in capture_wrapper.items() if key != "replay_hash"}
    )
    capture_path.write_text(canonical_serialize(capture_wrapper) + "\n", encoding="utf-8")

    result_path = replay / "003_result_capture_result_recorded.json"
    result_wrapper = load_json(result_path)
    result_wrapper["artifact"]["worker_result_capture_hash"] = changed["artifact_hash"]
    _rehash(result_wrapper["artifact"])
    result_wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in result_wrapper.items() if key != "replay_hash"}
    )
    result_path.write_text(canonical_serialize(result_wrapper) + "\n", encoding="utf-8")

    kwargs["worker_result_capture_artifact"] = changed
    return canonical(**kwargs)


def test_valid_captured_codex_output_calls_canonical_validator_once(tmp_path: Path, monkeypatch) -> None:
    runtime, activation, capture, root, workspace, runner = _captured(
        tmp_path, "G31-20-VALID"
    )
    calls = 0
    canonical = bridge.result_validation.validate_worker_result

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return canonical(**kwargs)

    monkeypatch.setattr(bridge.result_validation, "validate_worker_result", counted)
    result = _validate(runtime, activation, capture, root, workspace)

    assert calls == 1
    assert len(runner.calls) == 1
    assert result["g31_semantic_validation_status"] == SUCCESS
    assert result["validation_status"] == "RESULT_VALIDATED"
    assert result["semantic_worker_result_captured"] is True
    assert result["semantic_validation_performed"] is True
    assert result["result_validated"] is True
    assert result["validation_replay_created"] is True
    assert result["validation_count"] == 1
    assert result["semantic_output_sha256"] == activation["codex_transport_receipt"]["stdout_hash"]
    for field in (
        "result_accepted", "repository_mutated", "commit_created", "deployed",
        "released", "provider_invoked", "additional_worker_process_started",
    ):
        assert result[field] is False

    reconstructed = reconstruct_codex_worker_semantic_validation_binding(
        validation_binding_capture=result,
        result_capture_binding_capture=capture,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
    )
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["result_validated"] is True


def test_canonical_invalid_outcome_is_not_misreported_as_valid(tmp_path: Path, monkeypatch) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20-INVALID"
    )
    canonical = bridge.result_validation.validate_worker_result
    calls = 0

    def invalid(**kwargs):
        nonlocal calls
        calls += 1
        return _call_canonical_with_semantically_invalid_capture(canonical, kwargs)

    monkeypatch.setattr(bridge.result_validation, "validate_worker_result", invalid)
    result = _validate(runtime, activation, capture, root, workspace)

    assert calls == 1
    assert result["g31_semantic_validation_status"] == INVALID
    assert result["validation_status"] == "FAILED_CLOSED"
    assert result["semantic_worker_result_captured"] is True
    assert result["semantic_validation_performed"] is True
    assert result["result_validated"] is False
    assert "forbidden operation" in result["failure_reason"]
    assert result["result_accepted"] is False
    assert result["repository_mutated"] is False


@pytest.mark.parametrize("tamper", ("missing-bytes", "stdout-hash", "worker-output-hash"))
def test_missing_bytes_and_output_hash_substitution_fail_before_validator(
    tmp_path: Path, monkeypatch, tamper: str
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, f"G31-20-{tamper}"
    )
    capture = deepcopy(capture)
    output = capture["semantic_worker_output_artifact"]
    if tamper == "missing-bytes":
        output["payload"].pop("semantic_output")
        _rehash(output)
    elif tamper == "stdout-hash":
        output["payload"]["semantic_output_sha256"] = "0" * 64
        _rehash(output)
    else:
        output["artifact_hash"] = "sha256:" + "0" * 64
    monkeypatch.setattr(
        bridge.result_validation, "validate_worker_result",
        lambda **_kwargs: pytest.fail("canonical validator must not run"),
    )

    result = _validate(runtime, activation, capture, root, workspace)
    assert result["g31_semantic_validation_status"] == FAILED_CLOSED
    assert result["semantic_validation_performed"] is False
    assert result["result_validated"] is False


@pytest.mark.parametrize("tamper", ("receipt", "capture-replay"))
def test_receipt_and_capture_replay_tampering_fail_before_validator(
    tmp_path: Path, monkeypatch, tamper: str
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, f"G31-20-{tamper}"
    )
    if tamper == "receipt":
        activation = deepcopy(activation)
        activation["codex_transport_receipt"]["stdout_hash"] = "0" * 64
    else:
        path = Path(capture["worker_result_capture_replay_reference"]) / "002_result_capture_artifact_recorded.json"
        wrapper = load_json(path)
        wrapper["artifact"]["worker_output_hash"] = "sha256:" + "0" * 64
        _rehash(wrapper["artifact"])
        wrapper["replay_hash"] = replay_hash({key: value for key, value in wrapper.items() if key != "replay_hash"})
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
    monkeypatch.setattr(
        bridge.result_validation, "validate_worker_result",
        lambda **_kwargs: pytest.fail("canonical validator must not run"),
    )
    result = _validate(runtime, activation, capture, root, workspace)
    assert result["semantic_validation_performed"] is False
    assert result["result_validated"] is False


def test_cross_session_provider_substitution_and_repository_drift_fail_closed(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        bridge.result_validation, "validate_worker_result",
        lambda **_kwargs: pytest.fail("canonical validator must not run"),
    )
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20-CROSS"
    )
    cross = validate_captured_codex_worker_result(
        result_capture_binding_capture=capture,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        validated_at="2026-07-17T01:00:00Z",
        replay_dir=tmp_path / "other-session" / "validation",
    )
    assert cross["semantic_validation_performed"] is False

    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20-PROVIDER"
    )
    changed = deepcopy(runtime)
    changed["worker_execution_candidate_capture"]["worker_execution_candidate_artifact"]["worker_identity"]["worker_id"] = "OPENAI"
    assert _validate(changed, activation, capture, root, workspace)["result_validated"] is False

    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20-DRIFT"
    )
    (workspace / "UNAPPROVED-DRIFT.txt").write_text("changed\n", encoding="utf-8")
    assert _validate(runtime, activation, capture, root, workspace)["result_validated"] is False


def test_duplicate_destination_and_repeated_capture_validation_call_once(
    tmp_path: Path, monkeypatch
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20-ONCE"
    )
    canonical = bridge.result_validation.validate_worker_result
    calls = 0

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return canonical(**kwargs)

    monkeypatch.setattr(bridge.result_validation, "validate_worker_result", counted)
    first = _validate(runtime, activation, capture, root, workspace, "validation-one")
    assert first["result_validated"] is True
    assert _validate(runtime, activation, capture, root, workspace, "validation-one")["result_validated"] is False
    repeated = _validate(runtime, activation, capture, root, workspace, "validation-two")
    assert repeated["result_validated"] is False
    assert "already" in repeated["failure_reason"]
    assert calls == 1


@pytest.mark.parametrize("runner", (
    RecordingRunner(returncode=9, stderr="failed"),
    RecordingRunner(stdout=""),
    RecordingRunner(stdout="x" * 5000),
))
def test_failed_empty_and_truncated_transport_never_reaches_validator(
    tmp_path: Path, monkeypatch, runner
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, f"G31-20-INELIGIBLE-{id(runner)}", runner=runner
    )
    monkeypatch.setattr(
        bridge.result_validation, "validate_worker_result",
        lambda **_kwargs: pytest.fail("canonical validator must not run"),
    )
    result = _validate(runtime, activation, capture, root, workspace)
    assert result["semantic_validation_performed"] is False
    assert result["result_validated"] is False


def test_aicli_renders_valid_validation_without_fourth_decision(tmp_path: Path) -> None:
    result, output, _, _ = _run(
        tmp_path, "G31-20-AICLI-VALID",
        [REQUEST, "/send", "/approve", "/approve", "/approve", "/exit"],
        RecordingRunner(stdout="AiCLI authentic bounded result."),
    )
    runtime = result["runtime_result"]
    assert result["approval_count"] == 3
    assert result["aicli_validates"] is False
    assert result["aicli_accepts_result"] is False
    assert runtime["semantic_validation_performed"] is True
    assert runtime["result_validated"] is True
    assert runtime["result_accepted"] is False
    assert "CODEX Semantic Worker Result Validation" in "\n".join(output)
    assert "Validation Status: RESULT_VALIDATED" in "\n".join(output)


def test_aicli_renders_canonical_invalid_outcome_truthfully(tmp_path: Path, monkeypatch) -> None:
    canonical = bridge.result_validation.validate_worker_result

    def invalid(**kwargs):
        return _call_canonical_with_semantically_invalid_capture(canonical, kwargs)

    monkeypatch.setattr(bridge.result_validation, "validate_worker_result", invalid)
    result, output, _, _ = _run(
        tmp_path, "G31-20-AICLI-INVALID",
        [REQUEST, "/send", "/approve", "/approve", "/approve", "/exit"],
        RecordingRunner(stdout="Structurally invalid bounded result."),
    )
    runtime = result["runtime_result"]
    assert result["approval_count"] == 3
    assert result["aicli_validates"] is False
    assert runtime["semantic_validation_performed"] is True
    assert runtime["result_validated"] is False
    assert runtime["result_accepted"] is False
    assert "Validation Status: FAILED_CLOSED" in "\n".join(output)
