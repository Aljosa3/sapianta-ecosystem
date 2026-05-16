"""Operational entrypoint activation artifact."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_entrypoint_activation(*, boundary: dict, contract: dict, admission: dict) -> dict:
    value = {
        "runtime_activation_boundary_id": boundary["runtime_activation_boundary_id"],
        "operational_entry_contract_id": contract["operational_entry_contract_id"],
        "operational_entry_admission_id": admission["operational_entry_admission_id"],
    }
    return {
        "operational_runtime_entrypoint_id": f"OPERATIONAL-RUNTIME-ENTRYPOINT-{stable_hash(value)[:24]}",
        **value,
    }
