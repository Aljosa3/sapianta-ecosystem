from sapianta_bridge.live_governed_session_runtime.session_runtime_validator import validate_session_runtime


def test_session_runtime_validator_blocks_missing_lineage():
    assert validate_session_runtime(session_runtime={}, turn={}, binding={}, prior_output=None, attachment_output={})["valid"] is False
