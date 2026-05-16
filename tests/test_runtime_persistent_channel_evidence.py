from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_evidence import runtime_persistent_channel_evidence
def test_evidence():
    e=runtime_persistent_channel_evidence(binding={},valid=True,states=("RUNTIME_PERSISTENT_CHANNEL_CREATED",))
    assert e["persistent_channel_continuity"] is True
