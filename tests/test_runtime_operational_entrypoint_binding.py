from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import LINEAGE_FIELDS, create_runtime_operational_entrypoint_binding


def test_binding_preserves_full_operational_lineage():
    binding = create_runtime_operational_entrypoint_binding(runtime_operational_entrypoint_id="ENTRY-1", lineage={field: field for field in LINEAGE_FIELDS})
    assert binding["stdin_relay_id"] == "stdin_relay_id"
    assert binding["runtime_operational_entrypoint_binding_id"].startswith("RUNTIME-OPERATIONAL-ENTRYPOINT-BINDING-")
