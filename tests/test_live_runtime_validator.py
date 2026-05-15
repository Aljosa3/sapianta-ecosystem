from sapianta_bridge.live_governed_interaction_runtime.live_runtime_validator import validate_live_runtime


def test_live_runtime_validator_blocks_missing_binding_lineage():
    result = validate_live_runtime(session={}, loop_output={}, binding={})
    assert result["valid"] is False
