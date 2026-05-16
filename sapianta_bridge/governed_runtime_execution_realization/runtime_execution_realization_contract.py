"""Governed execution realization contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_execution_realization_contract(*, runtime_execution_realization_id: str) -> dict:
    value = {"runtime_execution_realization_id": runtime_execution_realization_id}
    return {
        "runtime_execution_realization_contract_id": f"RUNTIME-EXECUTION-REALIZATION-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "activated_surface_required": True,
    }
