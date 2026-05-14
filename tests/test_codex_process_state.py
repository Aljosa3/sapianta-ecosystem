from sapianta_bridge.provider_connectors.codex_process_state import (
    CODEX_PROCESS_STATES,
    validate_codex_process_state,
)


def test_codex_process_states_include_required_values():
    assert "OUTPUT_COMPLETED_PROCESS_RUNNING" in CODEX_PROCESS_STATES
    assert "TIMEOUT_NO_COMPLETION" in CODEX_PROCESS_STATES
    assert "UNKNOWN" in CODEX_PROCESS_STATES


def test_unknown_process_state_fails_closed():
    validation = validate_codex_process_state("UNKNOWN")

    assert validation["valid"] is False
    assert validation["bounded_result_available"] is False
    assert validation["fail_closed"] is True


def test_output_completed_process_running_has_bounded_result():
    validation = validate_codex_process_state("OUTPUT_COMPLETED_PROCESS_RUNNING")

    assert validation["valid"] is True
    assert validation["bounded_result_available"] is True
