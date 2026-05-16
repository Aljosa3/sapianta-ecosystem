from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_session import create_direct_runtime_interaction_session,validate_direct_runtime_interaction_session
def test_session_deterministic():
    s={"runtime_surface_session":{"runtime_surface_session_id":"SURF-1"}}
    a=create_direct_runtime_interaction_session(surface_output=s,interaction_admission_id="ADM-1").to_dict(); b=create_direct_runtime_interaction_session(surface_output=s,interaction_admission_id="ADM-1").to_dict()
    assert a["direct_runtime_interaction_session_id"]==b["direct_runtime_interaction_session_id"]; assert validate_direct_runtime_interaction_session(a)["valid"]
