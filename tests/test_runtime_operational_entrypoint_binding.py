from sapianta_bridge.governed_runtime_operational_entrypoint.runtime_operational_entrypoint_binding import (
    LINEAGE_FIELDS,
    create_runtime_operational_entrypoint_binding,
)


def test_binding_preserves_lineage():
    binding = create_runtime_operational_entrypoint_binding(
        runtime_operational_entrypoint_id="ENTRY-1",
        lineage={field: field for field in LINEAGE_FIELDS},
    )
    assert binding["runtime_execution_commit_id"] == "runtime_execution_commit_id"
