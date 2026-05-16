from sapianta_bridge.governed_runtime_surface.runtime_surface_response import create_runtime_surface_response
def test_runtime_surface_response_preserves_egress():
    r=create_runtime_surface_response(binding={"runtime_surface_session_id":"S-1","surface_egress_id":"OUT-1","response_return_id":"RET-1"}).to_dict()
    assert r["surface_egress_id"]=="OUT-1"
    assert r["surface_status"]=="RUNTIME_SURFACE_COMPLETED"
