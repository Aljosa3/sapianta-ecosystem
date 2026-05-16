"""Governed execution realization transaction."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_execution_realization_transaction(
    *,
    runtime_execution_realization_id: str,
    result_capture_id: str,
    response_return_id: str,
) -> dict:
    value = {
        "runtime_execution_realization_id": runtime_execution_realization_id,
        "result_capture_id": result_capture_id,
        "response_return_id": response_return_id,
    }
    return {
        "runtime_execution_realization_transaction_id": f"RUNTIME-EXECUTION-REALIZATION-TRANSACTION-{stable_hash(value)[:24]}",
        **value,
    }
