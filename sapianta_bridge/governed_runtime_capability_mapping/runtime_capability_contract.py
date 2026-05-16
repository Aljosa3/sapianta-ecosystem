"""Governed runtime capability contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_capability_contract(*, runtime_capability_mapping_id: str) -> dict:
    value = {"runtime_capability_mapping_id": runtime_capability_mapping_id}
    return {
        "runtime_capability_contract_id": f"RUNTIME-CAPABILITY-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "deterministic_mapping_required": True,
    }
