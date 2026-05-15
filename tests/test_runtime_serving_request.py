from sapianta_bridge.live_governed_runtime_serving.runtime_serving_request import create_runtime_serving_request


def test_runtime_serving_request_preserves_session():
    assert create_runtime_serving_request(serving_session={"runtime_serving_session_id":"RS","session_runtime_id":"S"}).to_dict()["session_runtime_id"] == "S"
