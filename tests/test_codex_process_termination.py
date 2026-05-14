from sapianta_bridge.provider_connectors.codex_process_termination import (
    classify_codex_process_termination,
    validate_codex_process_termination,
)


def test_process_termination_classifies_completed_output_running():
    classification = classify_codex_process_termination(
        stdout="SAPIANTA_CODEX_VALIDATION_OK AIGOL_TASK_COMPLETE",
        stderr="",
        exit_code=124,
        timed_out=True,
        process_terminated=False,
        idle_window_seconds=1,
    )

    assert classification["process_state"] == "OUTPUT_COMPLETED_PROCESS_RUNNING"
    assert classification["bounded_result_available"] is True
    assert classification["termination_required"] is True
    assert validate_codex_process_termination(classification)["valid"] is True


def test_process_termination_classifies_timeout_without_marker():
    classification = classify_codex_process_termination(
        stdout="some output without marker",
        stderr="",
        exit_code=124,
        timed_out=True,
        process_terminated=False,
        idle_window_seconds=1,
    )

    assert classification["process_state"] == "TIMEOUT_NO_COMPLETION"
    assert classification["bounded_result_available"] is False


def test_process_termination_classifies_auth_wait_as_blocked():
    classification = classify_codex_process_termination(
        stdout="",
        stderr="login required",
        exit_code=124,
        timed_out=True,
        process_terminated=False,
        idle_window_seconds=1,
    )

    assert classification["process_state"] == "AUTH_WAIT"
    assert classification["bounded_result_available"] is False


def test_process_termination_validation_blocks_behavior_mutation():
    classification = classify_codex_process_termination(
        stdout="AIGOL_TASK_COMPLETE",
        stderr="",
        exit_code=124,
        timed_out=True,
        process_terminated=False,
        idle_window_seconds=1,
    )
    classification["retry_present"] = True

    validation = validate_codex_process_termination(classification)

    assert validation["valid"] is False
    assert any(error["field"] == "retry_present" for error in validation["errors"])
