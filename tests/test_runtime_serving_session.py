from sapianta_bridge.live_governed_runtime_serving.runtime_serving_session import create_runtime_serving_session, validate_runtime_serving_session


def test_runtime_serving_session_is_valid():
    assert validate_runtime_serving_session(create_runtime_serving_session(session_runtime={"session_runtime_id":"S"}).to_dict())["valid"] is True
