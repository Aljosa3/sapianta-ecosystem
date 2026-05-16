from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import create_runtime_surface_binding,LINEAGE_SOURCE_FIELDS
def test_runtime_surface_binding_preserves_lineage():
    source={f:f.upper() for f in LINEAGE_SOURCE_FIELDS}
    b=create_runtime_surface_binding(surface_session={"runtime_surface_session_id":"S-1","surface_ingress_id":"IN-1","surface_egress_id":"OUT-1"},finalization_output={"runtime_delivery_finalization_binding":source}).to_dict()
    assert b["runtime_surface_session_id"]=="S-1"
    assert b["runtime_delivery_finalization_id"]=="RUNTIME_DELIVERY_FINALIZATION_ID"
