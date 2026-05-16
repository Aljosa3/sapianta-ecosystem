"""Fail-closed governed runtime operation envelope validation."""

from .runtime_operation_boundary import ALLOWED_OPERATION_TYPES, FORBIDDEN_OPERATION_TYPES

UPSTREAM_LINEAGE_FIELDS = (
    "runtime_activation_gate_id",
    "runtime_activation_boundary_id",
    "operational_entry_contract_id",
    "operational_entry_admission_id",
    "operational_runtime_entrypoint_id",
    "runtime_persistent_channel_id",
    "direct_runtime_interaction_session_id",
    "runtime_surface_session_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "local_runtime_bridge_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
    "governed_session_id",
    "execution_gate_id",
    "provider_invocation_id",
    "bounded_runtime_id",
    "result_capture_id",
    "response_return_id",
)


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _explicit_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _bounded_scope(value: object) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("kind"), str)
        and value["kind"].strip()
        and isinstance(value.get("value"), str)
        and value["value"].strip()
        and value["value"] not in {"*", "ALL", "UNBOUNDED"}
    )


def validate_runtime_operation_envelope(
    *,
    envelope: dict,
    contract: dict,
    payload: dict,
    policy: dict,
    boundary: dict,
    activation_output: dict,
    upstream_lineage: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if activation_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_activation_gate", "reason": "activation authorization missing"})
    activation_binding = activation_output.get("runtime_activation_gate_binding", {})
    if activation_binding.get("activation_authorized") is not True or payload.get("activation_authorized") is not True:
        errors.append({"field": "activation_authorized", "reason": "activation authorization missing"})
    if payload.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "operation approval must be human"})
    if _missing_text(payload.get("runtime_activation_gate_id")):
        errors.append({"field": "runtime_activation_gate_id", "reason": "runtime activation gate linkage missing"})
    if payload.get("runtime_activation_gate_id") != activation_binding.get("runtime_activation_gate_id"):
        errors.append({"field": "runtime_activation_gate_id", "reason": "runtime activation gate linkage missing"})

    operation_type = payload.get("operation_type")
    if operation_type in FORBIDDEN_OPERATION_TYPES:
        errors.append({"field": "operation_type", "reason": "operation type forbidden"})
    elif operation_type not in ALLOWED_OPERATION_TYPES:
        errors.append({"field": "operation_type", "reason": "operation type unknown"})
    if _missing_text(payload.get("operation_intent")):
        errors.append({"field": "operation_intent", "reason": "operation intent missing"})
    if not _bounded_scope(payload.get("target_scope")):
        errors.append({"field": "target_scope", "reason": "target scope unbounded"})
    if not _explicit_list(payload.get("allowed_inputs")):
        errors.append({"field": "allowed_inputs", "reason": "allowed inputs must be explicit"})
    if not _explicit_list(payload.get("expected_outputs")):
        errors.append({"field": "expected_outputs", "reason": "expected outputs must be explicit"})
    if _missing_text(payload.get("risk_class")):
        errors.append({"field": "risk_class", "reason": "risk class missing"})

    envelope_id = envelope.get("runtime_operation_envelope_id")
    for artifact, id_field, reason in (
        (payload, "runtime_operation_payload_id", "operation payload incomplete"),
        (contract, "runtime_operation_contract_id", "operation contract incomplete"),
        (policy, "runtime_operation_policy_id", "policy linkage incomplete"),
        (boundary, "runtime_operation_boundary_id", "boundary linkage incomplete"),
    ):
        if _missing_text(artifact.get(id_field)) or artifact.get("runtime_operation_envelope_id") != envelope_id:
            errors.append({"field": id_field, "reason": reason})
    if contract.get("structured_operation_required") is not True:
        errors.append({"field": "runtime_operation_contract_id", "reason": "operation contract incomplete"})
    if policy.get("bounded_operation_required") is not True or policy.get("raw_prompt_to_shell_forbidden") is not True:
        errors.append({"field": "runtime_operation_policy_id", "reason": "policy linkage incomplete"})
    if boundary.get("raw_shell_execution_allowed") is not False or boundary.get("unrestricted_subprocess_allowed") is not False:
        errors.append({"field": "runtime_operation_boundary_id", "reason": "boundary linkage incomplete"})

    lineage = {**upstream_lineage, **activation_binding}
    for field in UPSTREAM_LINEAGE_FIELDS:
        if _missing_text(lineage.get(field)):
            errors.append({"field": field, "reason": "required upstream lineage missing"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_operation_envelope", {}).get("runtime_operation_envelope_id")
        if prior_id != envelope_id:
            errors.append({"field": "runtime_operation_envelope_id", "reason": "operation envelope identity changed"})
    return {"valid": not errors, "errors": errors}
