from sapianta_bridge.live_runtime_interaction_attachment.runtime_attachment_state import SUCCESS_PATH


def test_runtime_attachment_state_path_emits():
    assert SUCCESS_PATH[-1] == "ATTACHMENT_RUNTIME_EMITTED"
