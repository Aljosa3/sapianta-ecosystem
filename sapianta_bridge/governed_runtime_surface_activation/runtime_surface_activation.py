"""Governed runtime surface activation record."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_surface_activation_record(*, execution_surface: dict) -> dict:
    value = {
        "runtime_execution_surface_id": execution_surface["runtime_execution_surface_id"],
        "runtime_surface": execution_surface["runtime_surface"],
    }
    return {
        "runtime_surface_activation_id": f"RUNTIME-SURFACE-ACTIVATION-{stable_hash(value)[:24]}",
        **value,
    }
