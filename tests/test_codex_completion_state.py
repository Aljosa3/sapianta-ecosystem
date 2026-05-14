from sapianta_bridge.provider_connectors.codex_completion_state import (
    completion_state_is_success,
    validate_codex_completion_state,
)


def test_completed_is_only_success_state():
    assert completion_state_is_success("COMPLETED") is True
    assert completion_state_is_success("TIMEOUT") is False
    assert validate_codex_completion_state("COMPLETED")["valid"] is True


def test_unknown_completion_state_fails_closed():
    validation = validate_codex_completion_state("UNKNOWN")

    assert validation["valid"] is False
    assert validation["fail_closed"] is True


def test_invalid_completion_state_rejected():
    validation = validate_codex_completion_state("SOMETHING_ELSE")

    assert validation["valid"] is False
