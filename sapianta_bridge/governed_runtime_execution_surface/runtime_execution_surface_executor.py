"""Governed runtime execution surface executor realization."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_execution_surface_executor(
    *,
    runtime_execution_surface_id: str,
    executor_primitive: str,
    runtime_surface: str,
) -> dict:
    value = {
        "runtime_execution_surface_id": runtime_execution_surface_id,
        "executor_primitive": executor_primitive,
        "runtime_surface": runtime_surface,
    }
    return {
        "runtime_execution_surface_executor_id": f"RUNTIME-EXECUTION-SURFACE-EXECUTOR-{stable_hash(value)[:24]}",
        **value,
    }
