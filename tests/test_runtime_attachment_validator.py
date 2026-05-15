from sapianta_bridge.live_runtime_interaction_attachment.runtime_attachment_validator import validate_runtime_attachment


def test_runtime_attachment_validator_blocks_missing_lineage():
    assert validate_runtime_attachment(session={}, live_runtime_output={}, binding={})["valid"] is False
