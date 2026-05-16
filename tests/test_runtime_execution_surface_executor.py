from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_executor import (
    create_runtime_execution_surface_executor,
)


def test_executor_preserves_realization_pair():
    executor = create_runtime_execution_surface_executor(
        runtime_execution_surface_id="SURFACE-1",
        executor_primitive="GOVERNED_STATE_READER",
        runtime_surface="GOVERNED_STATE_READ_SURFACE",
    )
    assert executor["runtime_surface"] == "GOVERNED_STATE_READ_SURFACE"
