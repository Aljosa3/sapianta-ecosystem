from sapianta_bridge.live_governed_runtime_serving.runtime_serving_state import SUCCESS_PATH


def test_runtime_serving_state_emits():
    assert SUCCESS_PATH[-1] == "RUNTIME_SERVING_RESPONSE_EMITTED"
