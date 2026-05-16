"""Governed runtime execution surface contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_execution_surface_contract(*, runtime_execution_surface_id: str) -> dict:
    value = {"runtime_execution_surface_id": runtime_execution_surface_id}
    return {
        "runtime_execution_surface_contract_id": f"RUNTIME-EXECUTION-SURFACE-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "static_surface_required": True,
    }
