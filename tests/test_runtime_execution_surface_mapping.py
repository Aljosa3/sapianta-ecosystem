from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface import (
    ALLOWED_EXECUTION_SURFACES,
    create_runtime_execution_surface_record,
)


def test_surface_mappings_are_static_and_deterministic():
    for primitive, surface in ALLOWED_EXECUTION_SURFACES.items():
        record = create_runtime_execution_surface_record(
            capability_evidence={"runtime_capability_mapping_id": "MAP-1", "executor_primitive": primitive}
        )
        assert record["runtime_surface"] == surface
