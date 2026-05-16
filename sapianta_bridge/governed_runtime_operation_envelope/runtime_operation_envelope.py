"""Replay-safe governed runtime operation envelope identity."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operation_envelope_record(
    *,
    activation_binding: dict,
    operation_type: str,
    operation_intent: str,
) -> dict:
    value = {
        "runtime_activation_gate_id": activation_binding["runtime_activation_gate_id"],
        "operation_type": operation_type,
        "operation_intent": operation_intent,
    }
    return {
        "runtime_operation_envelope_id": f"RUNTIME-OPERATION-ENVELOPE-{stable_hash(value)[:24]}",
        **value,
        "replay_safe": True,
    }
