"""Governed runtime operation envelope controller."""

from .runtime_operation_boundary import AUTHORIZED_PATH, create_runtime_operation_boundary
from .runtime_operation_contract import create_runtime_operation_contract
from .runtime_operation_envelope import create_runtime_operation_envelope_record
from .runtime_operation_evidence import runtime_operation_evidence
from .runtime_operation_payload import create_runtime_operation_payload
from .runtime_operation_policy import create_runtime_operation_policy
from .runtime_operation_validator import validate_runtime_operation_envelope


def create_runtime_operation_envelope(
    *,
    activation_output: dict,
    upstream_lineage: dict,
    operation_type: str,
    operation_intent: str,
    target_scope: dict,
    allowed_inputs: list[str],
    expected_outputs: list[str],
    risk_class: str,
    requires_human_approval: bool,
    approved_by: str,
    prior_output: dict | None = None,
) -> dict:
    try:
        activation_binding = activation_output["runtime_activation_gate_binding"]
        envelope = create_runtime_operation_envelope_record(
            activation_binding=activation_binding,
            operation_type=operation_type,
            operation_intent=operation_intent,
        )
        contract = create_runtime_operation_contract(runtime_operation_envelope_id=envelope["runtime_operation_envelope_id"])
        payload = create_runtime_operation_payload(
            runtime_operation_envelope_id=envelope["runtime_operation_envelope_id"],
            operation_type=operation_type,
            operation_intent=operation_intent,
            target_scope=target_scope,
            allowed_inputs=allowed_inputs,
            expected_outputs=expected_outputs,
            risk_class=risk_class,
            requires_human_approval=requires_human_approval,
            approved_by=approved_by,
            activation_authorized=activation_binding["activation_authorized"],
            runtime_activation_gate_id=activation_binding["runtime_activation_gate_id"],
        )
        policy = create_runtime_operation_policy(runtime_operation_envelope_id=envelope["runtime_operation_envelope_id"])
        boundary = create_runtime_operation_boundary(runtime_operation_envelope_id=envelope["runtime_operation_envelope_id"])
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_operation_envelope", "reason": "activation linkage incomplete"}]},
            "states": ["BLOCKED"],
        }

    validation = validate_runtime_operation_envelope(
        envelope=envelope,
        contract=contract,
        payload=payload,
        policy=policy,
        boundary=boundary,
        activation_output=activation_output,
        upstream_lineage=upstream_lineage,
        prior_output=prior_output,
    )
    if validation["valid"]:
        states = AUTHORIZED_PATH
    elif any(error["field"] == "operation_type" for error in validation["errors"]):
        states = ("OPERATION_REJECTED",)
    else:
        states = ("BLOCKED",)
    lineage = {**upstream_lineage, **activation_binding}
    evidence = runtime_operation_evidence(
        envelope=envelope,
        contract=contract,
        payload=payload,
        policy=policy,
        boundary=boundary,
        lineage=lineage,
        valid=validation["valid"],
        states=states,
    )
    return {
        "runtime_operation_envelope": envelope,
        "runtime_operation_contract": contract,
        "runtime_operation_payload": payload,
        "runtime_operation_policy": policy,
        "runtime_operation_boundary": boundary,
        "runtime_operation_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
