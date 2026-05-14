from sapianta_bridge.provider_connectors.bounded_execution_capture import (
    capture_completed_execution,
    capture_timeout,
    validate_bounded_execution_capture,
)


def test_bounded_execution_capture_is_deterministic():
    capture = capture_completed_execution(stdout="ok", stderr="", exit_code=0).to_dict()

    assert capture["stdout"] == "ok"
    assert capture["stderr"] == ""
    assert capture["exit_code"] == 0
    assert capture["completion_state"] == "COMPLETED"
    assert capture["process_terminated"] is True
    assert capture["execution_started_at"] == "1970-01-01T00:00:00Z"
    assert capture["immutable"] is True
    assert validate_bounded_execution_capture(capture)["valid"] is True


def test_bounded_execution_capture_timeout_is_deterministic():
    capture = capture_timeout().to_dict()

    assert capture["timed_out"] is True
    assert capture["exit_code"] == 124
    assert capture["completion_state"] == "TIMEOUT"
    assert capture["process_terminated"] is False
    assert validate_bounded_execution_capture(capture)["valid"] is True
