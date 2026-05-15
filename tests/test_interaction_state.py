from sapianta_bridge.human_interaction_continuity.interaction_state import (
    SUCCESS_PATH,
    validate_interaction_state,
    validate_interaction_state_chain,
)


def test_interaction_state_success_path_is_valid():
    assert validate_interaction_state_chain(list(SUCCESS_PATH))["valid"] is True


def test_interaction_state_fails_closed_for_unknown():
    assert validate_interaction_state("UNKNOWN")["valid"] is False
