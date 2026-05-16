"""Governed runtime surface activation contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_surface_activation_contract(*, runtime_surface_activation_id: str) -> dict:
    value = {"runtime_surface_activation_id": runtime_surface_activation_id}
    return {
        "runtime_surface_activation_contract_id": f"RUNTIME-SURFACE-ACTIVATION-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "surface_validation_required": True,
    }
