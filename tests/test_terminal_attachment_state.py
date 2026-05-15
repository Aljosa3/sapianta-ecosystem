from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_state import SUCCESS_PATH, TERMINAL_ATTACHMENT_STATES


def test_terminal_attachment_states_are_bounded():
    assert SUCCESS_PATH == TERMINAL_ATTACHMENT_STATES[:7]
    assert TERMINAL_ATTACHMENT_STATES[-2:] == ("BLOCKED", "FAILED")
