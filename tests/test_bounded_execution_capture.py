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
    assert capture["process_state"] == "TERMINATED_COMPLETED"
    assert capture["process_terminated"] is True
    assert capture["bounded_result_captured"] is True
    assert capture["execution_started_at"] == "1970-01-01T00:00:00Z"
    assert capture["immutable"] is True
    assert validate_bounded_execution_capture(capture)["valid"] is True


def test_bounded_execution_capture_timeout_is_deterministic():
    capture = capture_timeout().to_dict()

    assert capture["timed_out"] is True
    assert capture["exit_code"] == 124
    assert capture["completion_state"] == "TIMEOUT"
    assert capture["process_state"] == "TIMEOUT_NO_COMPLETION"
    assert capture["process_terminated"] is False
    assert capture["bounded_result_captured"] is False
    assert validate_bounded_execution_capture(capture)["valid"] is True


def test_bounded_execution_capture_records_result_captured_with_termination():
    capture = capture_timeout(
        stdout="SAPIANTA_CODEX_VALIDATION_OK AIGOL_TASK_COMPLETE",
        stderr="",
        process_state="OUTPUT_COMPLETED_PROCESS_RUNNING",
        process_terminated=True,
        completion_marker_detected=True,
        bounded_result_captured=True,
        graceful_termination_attempted=True,
        graceful_termination_succeeded=True,
    ).to_dict()

    assert capture["timed_out"] is True
    assert capture["process_state"] == "OUTPUT_COMPLETED_PROCESS_RUNNING"
    assert capture["process_terminated"] is True
    assert capture["completion_marker_detected"] is True
    assert capture["bounded_result_captured"] is True
    assert capture["graceful_termination_succeeded"] is True
    assert validate_bounded_execution_capture(capture)["valid"] is True
