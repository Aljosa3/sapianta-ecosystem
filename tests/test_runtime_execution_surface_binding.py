from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import (
    LINEAGE_FIELDS,
    create_runtime_execution_surface_binding,
)


def test_binding_preserves_lineage():
    binding = create_runtime_execution_surface_binding(
        runtime_execution_surface_id="SURFACE-1",
        realization_lineage={field: field for field in LINEAGE_FIELDS},
    )
    assert binding["runtime_execution_commit_id"] == "runtime_execution_commit_id"
