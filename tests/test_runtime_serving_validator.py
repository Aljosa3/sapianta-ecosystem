from sapianta_bridge.live_governed_runtime_serving.runtime_serving_validator import validate_runtime_serving


def test_runtime_serving_validator_blocks_missing_lineage():
    assert validate_runtime_serving(serving_session={}, binding={}, prior_output=None, session_runtime_output={})["valid"] is False
