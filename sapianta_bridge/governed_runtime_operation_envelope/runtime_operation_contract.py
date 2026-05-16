"""Governed runtime operation contract."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operation_contract(*, runtime_operation_envelope_id: str) -> dict:
    value = {"runtime_operation_envelope_id": runtime_operation_envelope_id}
    return {
        "runtime_operation_contract_id": f"RUNTIME-OPERATION-CONTRACT-{stable_hash(value)[:24]}",
        **value,
        "structured_operation_required": True,
    }
