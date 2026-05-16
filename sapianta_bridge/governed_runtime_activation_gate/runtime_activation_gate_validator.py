"""Fail-closed governed runtime activation gate validation."""

from typing import Any

from .runtime_activation_gate_session import validate_runtime_activation_gate_session

AUTHORITY_FIELDS = (
    "runtime_activation_gate_id",
    "runtime_activation_boundary_id",
    "operational_entry_contract_id",
    "operational_entry_admission_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
)


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_activation_gate(
    *,
    gate_session: dict,
    binding: dict,
    entrypoint_output: dict | None = None,
    bridge_output: dict | None = None,
    prior_output: dict | None = None,
) -> dict[str, Any]:
    errors = list(validate_runtime_activation_gate_session(gate_session)["errors"])

    if prior_output is not None:
        prior_id = prior_output.get("runtime_activation_gate_session", {}).get("runtime_activation_gate_id")
        if prior_id != gate_session.get("runtime_activation_gate_id"):
            errors.append({"field": "runtime_activation_gate_id", "reason": "activation identity changed"})
        if prior_output.get("closed") is True:
            errors.append({"field": "closed", "reason": "closed activation gate cannot reopen implicitly"})

    if entrypoint_output is not None:
        if entrypoint_output.get("validation", {}).get("valid") is not True:
            errors.append({"field": "operational_runtime_entrypoint", "reason": "activation boundary invalid"})
        activation = entrypoint_output.get("activation", {})
        contract = entrypoint_output.get("contract", {})
        admission = entrypoint_output.get("admission", {})
        evidence = entrypoint_output.get("evidence", {})
        if activation.get("runtime_activation_boundary_id") != binding.get("runtime_activation_boundary_id"):
            errors.append({"field": "runtime_activation_boundary_id", "reason": "activation boundary is invalid"})
        if contract.get("operational_entry_contract_id") != binding.get("operational_entry_contract_id"):
            errors.append({"field": "operational_entry_contract_id", "reason": "contract linkage incomplete"})
        if admission.get("operational_entry_admission_id") != binding.get("operational_entry_admission_id"):
            errors.append({"field": "operational_entry_admission_id", "reason": "operational admission is incomplete"})
        if admission.get("admitted") is not True or admission.get("approved_by") != "human":
            errors.append({"field": "operational_entry_admission_id", "reason": "operational admission is incomplete"})
        for field in ("execution_exchange_session_id", "execution_relay_session_id", "runtime_execution_commit_id", "runtime_delivery_finalization_id"):
            if evidence.get(field) != binding.get(field):
                errors.append({"field": field, "reason": "activation continuity missing"})
    elif bridge_output is not None:
        if bridge_output.get("validation", {}).get("valid") is not True:
            errors.append({"field": "local_runtime_bridge", "reason": "runtime bridge continuity invalid"})
    else:
        errors.append({"field": "activation_source", "reason": "activation source missing"})

    if binding.get("activation_source_kind") == "operational_entrypoint":
        for field in AUTHORITY_FIELDS:
            if _missing_text(binding.get(field)):
                errors.append({"field": field, "reason": "activation lineage incomplete"})
    else:
        for field in ("runtime_activation_gate_id", "execution_exchange_session_id", "execution_relay_session_id"):
            if _missing_text(binding.get(field)):
                errors.append({"field": field, "reason": "activation lineage incomplete"})

    if binding.get("activation_authorized") is not True:
        errors.append({"field": "activation_authorized", "reason": "activation approval cannot be validated"})
    if binding.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "activation approval must remain human"})

    return {"valid": not errors, "errors": errors}
