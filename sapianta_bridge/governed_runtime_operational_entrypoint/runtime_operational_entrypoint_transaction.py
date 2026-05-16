"""Governed runtime operational entrypoint transaction."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operational_entrypoint_transaction(
    *,
    runtime_operational_entrypoint_id: str,
    runtime_execution_realization_id: str,
    result_capture_id: str,
    response_return_id: str,
) -> dict:
    value = {
        "runtime_operational_entrypoint_id": runtime_operational_entrypoint_id,
        "runtime_execution_realization_id": runtime_execution_realization_id,
        "result_capture_id": result_capture_id,
        "response_return_id": response_return_id,
    }
    return {
        "runtime_operational_entrypoint_transaction_id": f"RUNTIME-OPERATIONAL-ENTRYPOINT-TRANSACTION-{stable_hash(value)[:24]}",
        **value,
    }
