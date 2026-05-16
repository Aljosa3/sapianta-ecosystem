from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_response import create_runtime_persistent_channel_response
def test_response_status():
    assert create_runtime_persistent_channel_response(binding={"runtime_persistent_channel_id":"C","response_return_id":"R","close_requested":False}).to_dict()["channel_status"]=="RUNTIME_PERSISTENT_CHANNEL_READY"
