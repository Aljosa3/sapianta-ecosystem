"""Tests for MINIMAL_EXECUTION_RUNTIME_PROTOTYPE_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.minimal_execution_runtime_prototype import (
    AUTHORIZED,
    EXECUTED,
    FAILED,
    REQUESTED,
    TERMINATED,
    VALIDATED,
    authorize_execution,
    create_execution_request,
    execute_minimal_execution_runtime,
    reconstruct_minimal_execution_runtime_replay,
    validate_execution_request,
    validate_execution_transition,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-29T00:00:00+00:00"


def _run(tmp_path, **overrides) -> dict:
    args = {
        "execution_id": "EXECUTION-000001",
        "request_id": "EXECUTION-REQUEST-000001",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path,
    }
    args.update(overrides)
    return execute_minimal_execution_runtime(**args)


def test_successful_lifecycle_is_replay_visible(tmp_path) -> None:
    capture = _run(tmp_path)
    replay = reconstruct_minimal_execution_runtime_replay(tmp_path)

    assert capture["termination"]["state"] == TERMINATED
    assert replay["final_status"] == TERMINATED
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]
    assert replay["append_only_valid"] is True
    assert replay["constitutional_freeze_preserved"] is True
    assert replay["authority_separation_preserved"] is True
    assert replay["execution_boundaries_preserved"] is True


def test_runtime_artifacts_are_deterministic(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(tmp_path / "second")

    assert first == second


def test_replay_artifacts_are_append_only(tmp_path) -> None:
    _run(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _run(tmp_path)


def test_missing_authorization_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, authorize=False)
    replay = reconstruct_minimal_execution_runtime_replay(tmp_path)

    assert capture["termination"]["state"] == FAILED
    assert "authorization missing" in capture["termination"]["failure_reason"]
    assert replay["final_status"] == FAILED
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, FAILED, FAILED, FAILED]


def test_boundary_violation_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, requested_surface="FILESYSTEM", requested_capability="WRITE")

    assert capture["termination"]["state"] == FAILED
    assert capture["termination"]["boundary_violation_detected"] is True
    assert "boundary violation" in capture["termination"]["failure_reason"]


def test_restricted_surface_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, requested_surface="NETWORK", requested_capability="OUTBOUND")

    assert capture["termination"]["state"] == FAILED
    assert "restricted" in capture["termination"]["failure_reason"]


def test_ambiguous_execution_classification_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, requested_surface="UNKNOWN", requested_capability="MAYBE")

    assert capture["termination"]["state"] == FAILED
    assert "classification ambiguity" in capture["termination"]["failure_reason"]


def test_authority_escalation_attempt_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, requested_authority="governance authority")

    assert capture["termination"]["state"] == FAILED
    assert capture["termination"]["authority_escalation_detected"] is True
    assert "authority escalation" in capture["termination"]["failure_reason"]


def test_invalid_transition_rejected() -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid"):
        validate_execution_transition(REQUESTED, EXECUTED)


def test_terminal_transition_rejected() -> None:
    with pytest.raises(FailClosedRuntimeError, match="terminal"):
        validate_execution_transition(TERMINATED, REQUESTED)


def test_replay_discontinuity_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "003_outcome.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["state"] = FAILED
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_minimal_execution_runtime_replay(tmp_path)


def test_replay_ordering_mismatch_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "002_authorization.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "outcome"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_minimal_execution_runtime_replay(tmp_path)


def test_manual_authorization_requires_validated_state() -> None:
    request = create_execution_request(
        execution_id="EXECUTION-000001",
        request_id="EXECUTION-REQUEST-000001",
        created_at=CREATED_AT,
    )

    with pytest.raises(FailClosedRuntimeError, match="VALIDATED"):
        authorize_execution(request)


def test_validation_preserves_boundary_contract() -> None:
    request = create_execution_request(
        execution_id="EXECUTION-000001",
        request_id="EXECUTION-REQUEST-000001",
        created_at=CREATED_AT,
    )
    validation = validate_execution_request(request)

    assert validation["state"] == VALIDATED
    assert validation["boundary_classification"] == "ALLOWED"
    assert validation["replay_centrality_preserved"] is True
    assert validation["constitutional_freeze_preserved"] is True


def test_no_real_execution_surface_imports() -> None:
    import aigol.runtime.minimal_execution_runtime_prototype as prototype

    source = inspect.getsource(prototype)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
