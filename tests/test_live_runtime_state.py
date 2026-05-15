from sapianta_bridge.live_governed_interaction_runtime.live_runtime_state import SUCCESS_PATH


def test_live_runtime_state_path_is_deterministic():
    assert SUCCESS_PATH[-1] == "LIVE_RESPONSE_EMITTED"
