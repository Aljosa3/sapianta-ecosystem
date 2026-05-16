from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_response import create_direct_runtime_interaction_response
def test_response_returned():
    r=create_direct_runtime_interaction_response(binding={"direct_runtime_interaction_session_id":"D-1","response_return_id":"RET-1"}).to_dict()
    assert r["interaction_status"]=="DIRECT_RUNTIME_INTERACTION_RETURNED"
