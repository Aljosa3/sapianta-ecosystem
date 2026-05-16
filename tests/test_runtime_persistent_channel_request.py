from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_request import create_runtime_persistent_channel_request
def test_request_close_flag():
    assert create_runtime_persistent_channel_request(channel_session={"runtime_persistent_channel_id":"C","direct_runtime_interaction_session_id":"D","close_requested":True}).to_dict()["close_requested"] is True
