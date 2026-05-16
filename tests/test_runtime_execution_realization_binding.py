from sapianta_bridge.governed_runtime_execution_realization.runtime_execution_realization_binding import (
    LINEAGE_FIELDS,
    create_runtime_execution_realization_binding,
)


def test_binding_preserves_lineage():
    binding = create_runtime_execution_realization_binding(
        runtime_execution_realization_id="REAL-1",
        realization_lineage={field: field for field in LINEAGE_FIELDS},
    )
    assert binding["runtime_surface_activation_id"] == "runtime_surface_activation_id"
