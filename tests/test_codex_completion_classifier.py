from sapianta_bridge.provider_connectors.codex_completion_classifier import (
    classify_codex_completion,
    validate_codex_completion_classification,
)


def test_classifier_marks_completed_only_on_zero_exit():
    classification = classify_codex_completion(
        stdout="done",
        stderr="",
        exit_code=0,
        timed_out=False,
        duration_seconds=1,
    )

    assert classification["completion_state"] == "COMPLETED"
    assert classification["completion_success"] is True
    assert validate_codex_completion_classification(classification)["valid"] is True


def test_classifier_marks_cli_error_on_nonzero_exit():
    classification = classify_codex_completion(
        stdout="",
        stderr="error",
        exit_code=2,
        timed_out=False,
        duration_seconds=1,
    )

    assert classification["completion_state"] == "CLI_ERROR"
    assert classification["completion_success"] is False


def test_classifier_detects_app_server_wait_on_timeout():
    classification = classify_codex_completion(
        stdout="",
        stderr="failed to initialize in-process app-server client",
        exit_code=124,
        timed_out=True,
        duration_seconds=30,
    )

    assert classification["completion_state"] == "APP_SERVER_WAIT"
    assert classification["suspected_blocker"] == "app_server_state_initialization"


def test_classifier_detects_auth_wait():
    classification = classify_codex_completion(
        stdout="",
        stderr="login required",
        exit_code=1,
        timed_out=False,
        duration_seconds=1,
    )

    assert classification["completion_state"] == "AUTH_WAIT"


def test_classifier_does_not_allow_behavior_mutation():
    classification = classify_codex_completion(
        stdout="done",
        stderr="",
        exit_code=0,
        timed_out=False,
        duration_seconds=1,
    )
    classification["retry_present"] = True

    validation = validate_codex_completion_classification(classification)

    assert validation["valid"] is False
    assert any(error["field"] == "retry_present" for error in validation["errors"])
