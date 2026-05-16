"""Operational entry contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_entry_contract(*, boundary: dict, operational_intent: str) -> dict:
    value = {
        "runtime_activation_boundary_id": boundary["runtime_activation_boundary_id"],
        "operational_intent": operational_intent,
    }
    return {
        "operational_entry_contract_id": f"OPERATIONAL-ENTRY-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "operational_ingress_governed": True,
        "replay_safe": True,
    }
