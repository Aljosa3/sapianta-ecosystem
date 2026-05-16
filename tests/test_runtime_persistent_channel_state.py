from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_state import READY_PATH,CLOSED_PATH
def test_states_paths():
    assert READY_PATH[-1]=="RUNTIME_PERSISTENT_CHANNEL_READY"; assert CLOSED_PATH[-1]=="RUNTIME_PERSISTENT_CHANNEL_CLOSED"
