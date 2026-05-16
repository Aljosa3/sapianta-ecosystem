"""Fail-closed governed runtime capability mapping validation."""

from .runtime_capability_mapping import ALLOWED_CAPABILITY_MAPPINGS, FORBIDDEN_CAPABILITY_REQUESTS

LINEAGE_FIELDS = (
    "runtime_operation_envelope_id",
    "runtime_operation_contract_id",
    "runtime_operation_payload_id",
    "runtime_operation_policy_id",
    "runtime_activation_gate_id",
    "execution_exchange_session_id",
    "execution_relay_session_id",
    "runtime_execution_commit_id",
    "runtime_delivery_finalization_id",
)


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_capability_mapping(
    *,
    mapping: dict,
    contract: dict,
    executor: dict,
    surface: dict,
    policy: dict,
    operation_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if operation_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_operation_envelope", "reason": "runtime operation envelope linkage missing"})
    evidence = operation_output.get("runtime_operation_evidence", {})
    operation_type = mapping.get("operation_type")
    expected_executor = ALLOWED_CAPABILITY_MAPPINGS.get(operation_type)
    if operation_type in FORBIDDEN_CAPABILITY_REQUESTS:
        errors.append({"field": "operation_type", "reason": "executor primitive forbidden"})
    elif expected_executor is None:
        errors.append({"field": "operation_type", "reason": "operation type has no deterministic mapping"})
    if _missing_text(mapping.get("executor_primitive")):
        errors.append({"field": "executor_primitive", "reason": "executable primitive undefined"})
    elif mapping.get("executor_primitive") != expected_executor:
        errors.append({"field": "executor_primitive", "reason": "executor primitive forbidden"})

    mapping_id = mapping.get("runtime_capability_mapping_id")
    for artifact, id_field, reason in (
        (contract, "runtime_capability_contract_id", "capability contract incomplete"),
        (executor, "runtime_capability_executor_id", "executable primitive undefined"),
        (surface, "runtime_capability_surface_id", "capability surface incomplete"),
        (policy, "runtime_capability_policy_id", "capability policy incomplete"),
    ):
        if _missing_text(artifact.get(id_field)) or artifact.get("runtime_capability_mapping_id") != mapping_id:
            errors.append({"field": id_field, "reason": reason})
    if contract.get("deterministic_mapping_required") is not True:
        errors.append({"field": "runtime_capability_contract_id", "reason": "capability contract incomplete"})
    if policy.get("bounded_executor_required") is not True or policy.get("dynamic_executor_generation_allowed") is not False:
        errors.append({"field": "runtime_capability_policy_id", "reason": "capability policy incomplete"})
    if (
        surface.get("raw_shell_execution_allowed") is not False
        or surface.get("unrestricted_subprocess_allowed") is not False
        or surface.get("unrestricted_network_execution_allowed") is not False
    ):
        errors.append({"field": "runtime_capability_surface_id", "reason": "capability surface incomplete"})

    for field in LINEAGE_FIELDS:
        if _missing_text(evidence.get(field)):
            errors.append({"field": field, "reason": "required capability lineage missing"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_capability_mapping", {}).get("runtime_capability_mapping_id")
        if prior_id != mapping_id:
            errors.append({"field": "runtime_capability_mapping_id", "reason": "capability identity changed"})
    return {"valid": not errors, "errors": errors}
