from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import LINEAGE_SOURCE_FIELDS
from sapianta_bridge.governed_runtime_surface.runtime_surface_validator import validate_runtime_surface
def test_runtime_surface_validator_blocks_missing_ingress():
    b={f:"X" for f in LINEAGE_SOURCE_FIELDS}; b.update({"runtime_surface_session_id":"S-1","surface_ingress_id":"","surface_egress_id":"OUT-1"})
    result=validate_runtime_surface(surface_session={"runtime_surface_session_id":"S-1","runtime_delivery_finalization_id":"FIN-1","surface_ingress_id":"","surface_egress_id":"OUT-1"},binding=b,finalization_output={"validation":{"valid":True},"runtime_delivery_finalization_binding":{"runtime_delivery_finalization_id":"FIN-1"}})
    assert not result["valid"]
    assert any(e["field"]=="surface_ingress_id" for e in result["errors"])
