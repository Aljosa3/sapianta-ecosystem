from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_binding import create_direct_runtime_interaction_binding
from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import LINEAGE_SOURCE_FIELDS
def test_binding_preserves_surface():
    surf={"runtime_surface_binding":{"runtime_surface_session_id":"S-1","surface_ingress_id":"IN","surface_egress_id":"OUT",**{f:f for f in LINEAGE_SOURCE_FIELDS}}}
    b=create_direct_runtime_interaction_binding(interaction_session={"direct_runtime_interaction_session_id":"D-1","interaction_admission_id":"ADM"},surface_output=surf).to_dict()
    assert b["runtime_surface_session_id"]=="S-1"; assert b["surface_egress_id"]=="OUT"
