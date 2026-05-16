from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation import (
    create_runtime_surface_activation_record,
)


def test_activation_identity_is_deterministic():
    first = create_runtime_surface_activation_record(
        execution_surface={"runtime_execution_surface_id": "SURFACE-1", "runtime_surface": "GOVERNED_STATE_READ_SURFACE"}
    )
    second = create_runtime_surface_activation_record(
        execution_surface={"runtime_execution_surface_id": "SURFACE-1", "runtime_surface": "GOVERNED_STATE_READ_SURFACE"}
    )
    assert first == second
