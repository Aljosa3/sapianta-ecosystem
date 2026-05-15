from sapianta_bridge.live_governed_runtime_serving.runtime_serving_response import create_runtime_serving_response


def test_runtime_serving_response_preserves_return():
    assert create_runtime_serving_response(binding={"runtime_serving_session_id":"RS","response_return_id":"R"}).to_dict()["response_return_id"] == "R"
