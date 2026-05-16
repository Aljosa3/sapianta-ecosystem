from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_session import create_runtime_persistent_channel_session,validate_runtime_persistent_channel_session
def test_session_deterministic():
    o={"direct_runtime_interaction_session":{"direct_runtime_interaction_session_id":"D-1"}}
    a=create_runtime_persistent_channel_session(interaction_output=o).to_dict(); b=create_runtime_persistent_channel_session(interaction_output=o).to_dict()
    assert a["runtime_persistent_channel_id"]==b["runtime_persistent_channel_id"]; assert validate_runtime_persistent_channel_session(a)["valid"]
