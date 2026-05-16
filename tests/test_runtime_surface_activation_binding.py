from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS
from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_binding import (
    create_runtime_surface_activation_binding,
)


def test_binding_preserves_activation_lineage():
    binding = create_runtime_surface_activation_binding(
        activation_id="ACT-1",
        surface_output={
            "runtime_execution_surface_binding": {
                "runtime_execution_surface_id": "SURFACE-1",
                **{field: field for field in LINEAGE_FIELDS},
            }
        },
    )
    assert binding["runtime_execution_surface_id"] == "SURFACE-1"
