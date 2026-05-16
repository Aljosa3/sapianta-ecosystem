from sapianta_bridge.governed_runtime_surface.runtime_surface_request import create_runtime_surface_request
def test_runtime_surface_request_preserves_ingress():
    r=create_runtime_surface_request(surface_session={"runtime_surface_session_id":"S-1","surface_ingress_id":"IN-1","runtime_delivery_finalization_id":"FIN-1"}).to_dict()
    assert r["surface_ingress_id"]=="IN-1"
