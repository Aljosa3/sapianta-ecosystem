"""Governed runtime operation payload."""

from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash


def create_runtime_operation_payload(
    *,
    runtime_operation_envelope_id: str,
    operation_type: str,
    operation_intent: str,
    target_scope: dict,
    allowed_inputs: list[str],
    expected_outputs: list[str],
    risk_class: str,
    requires_human_approval: bool,
    approved_by: str,
    activation_authorized: bool,
    runtime_activation_gate_id: str,
) -> dict:
    value = {
        "runtime_operation_envelope_id": runtime_operation_envelope_id,
        "operation_type": operation_type,
        "operation_intent": operation_intent,
        "target_scope": target_scope,
        "allowed_inputs": allowed_inputs,
        "expected_outputs": expected_outputs,
        "risk_class": risk_class,
        "requires_human_approval": requires_human_approval,
        "approved_by": approved_by,
        "activation_authorized": activation_authorized,
        "runtime_activation_gate_id": runtime_activation_gate_id,
    }
    return {
        "runtime_operation_payload_id": f"RUNTIME-OPERATION-PAYLOAD-{stable_hash(value)[:24]}",
        **value,
    }
