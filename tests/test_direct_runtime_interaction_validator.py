from sapianta_bridge.governed_direct_runtime_interaction.direct_runtime_interaction_validator import validate_direct_runtime_interaction,LINEAGE_FIELDS
def test_validator_blocks_missing_return():
    b={f:"X" for f in LINEAGE_FIELDS}; b["response_return_id"]=""
    r=validate_direct_runtime_interaction(interaction_session={"direct_runtime_interaction_session_id":"D","runtime_surface_session_id":"S","interaction_admission_id":"A"},binding=b,surface_output={"validation":{"valid":True},"runtime_surface_binding":{"runtime_surface_session_id":"S"}})
    assert not r["valid"]; assert any(e["field"]=="response_return_id" for e in r["errors"])
