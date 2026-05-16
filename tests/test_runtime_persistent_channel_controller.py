from sapianta_bridge.governed_direct_runtime_interaction import create_direct_runtime_interaction
from sapianta_bridge.governed_runtime_persistent_channel import create_runtime_persistent_channel
from sapianta_bridge.governed_runtime_surface.runtime_surface_binding import LINEAGE_SOURCE_FIELDS
def _interaction():
    surface={"runtime_surface_session":{"runtime_surface_session_id":"S-1"},"runtime_surface_binding":{"runtime_surface_session_id":"S-1","surface_ingress_id":"IN","surface_egress_id":"OUT",**{f:f for f in LINEAGE_SOURCE_FIELDS}},"validation":{"valid":True}}
    return create_direct_runtime_interaction(surface_output=surface,interaction_admission_id="ADM")
def test_ready():
    r=create_runtime_persistent_channel(interaction_output=_interaction())
    assert r["validation"]["valid"]; assert r["states"][-1]=="RUNTIME_PERSISTENT_CHANNEL_READY"
def test_blocks_incomplete():
    assert create_runtime_persistent_channel(interaction_output={})["states"]==["BLOCKED"]
def test_closed_cannot_reopen():
    i=_interaction(); closed=create_runtime_persistent_channel(interaction_output=i,close_requested=True); reopened=create_runtime_persistent_channel(interaction_output=i,prior_output=closed)
    assert reopened["states"]==["BLOCKED"]
