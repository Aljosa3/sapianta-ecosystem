from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_request import create_direct_runtime_interaction_request
def test_request_preserves_admission():
    assert create_direct_runtime_interaction_request(interaction_session={"direct_runtime_interaction_session_id":"D-1","runtime_surface_session_id":"S-1","interaction_admission_id":"ADM-1"}).to_dict()["interaction_admission_id"]=="ADM-1"
