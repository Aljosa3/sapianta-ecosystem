from sapianta_bridge.governed_session.session_state import (
    CANONICAL_SUCCESS_PATH,
    SESSION_STATES,
    validate_session_state,
)


def test_session_states_are_explicit() -> None:
    assert "CREATED" in SESSION_STATES
    assert "COMPLETED" in SESSION_STATES
    assert "BLOCKED" in SESSION_STATES
    assert list(CANONICAL_SUCCESS_PATH)[0] == "CREATED"


def test_session_state_rejects_hidden_state() -> None:
    validation = validate_session_state("RETRYING")

    assert validation["valid"] is False
    assert validation["hidden_state_detected"] is True
