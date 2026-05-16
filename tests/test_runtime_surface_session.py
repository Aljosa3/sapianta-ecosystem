from sapianta_bridge.governed_runtime_surface.runtime_surface_session import create_runtime_surface_session, validate_runtime_surface_session
def test_runtime_surface_session_deterministic():
    final={"runtime_delivery_finalization_session":{"runtime_delivery_finalization_id":"FIN-1"}}
    a=create_runtime_surface_session(finalization_output=final,surface_ingress_id="IN-1",surface_egress_id="OUT-1").to_dict()
    b=create_runtime_surface_session(finalization_output=final,surface_ingress_id="IN-1",surface_egress_id="OUT-1").to_dict()
    assert a["runtime_surface_session_id"]==b["runtime_surface_session_id"]
    assert validate_runtime_surface_session(a)["valid"]
