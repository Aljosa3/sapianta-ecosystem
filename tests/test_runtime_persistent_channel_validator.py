from sapianta_bridge.governed_runtime_persistent_channel.runtime_persistent_channel_validator import validate_runtime_persistent_channel,LINEAGE_FIELDS
def test_validator_blocks_closed_reopen():
    b={f:"X" for f in LINEAGE_FIELDS}
    r=validate_runtime_persistent_channel(channel_session={"runtime_persistent_channel_id":"C","direct_runtime_interaction_session_id":"D","close_requested":False},binding=b,interaction_output={"validation":{"valid":True},"direct_runtime_interaction_binding":{"direct_runtime_interaction_session_id":"D"}},prior_output={"runtime_persistent_channel_session":{"runtime_persistent_channel_id":"C","close_requested":True}})
    assert not r["valid"]; assert any(e["field"]=="close_requested" for e in r["errors"])
