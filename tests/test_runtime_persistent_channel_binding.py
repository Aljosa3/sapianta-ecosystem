from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_binding import create_runtime_persistent_channel_binding,SOURCE_FIELDS
def test_binding_lineage():
    b=create_runtime_persistent_channel_binding(channel_session={"runtime_persistent_channel_id":"C","close_requested":False},interaction_output={"direct_runtime_interaction_binding":{"direct_runtime_interaction_session_id":"D",**{f:f for f in SOURCE_FIELDS}}}).to_dict()
    assert b["runtime_surface_session_id"]=="runtime_surface_session_id"
