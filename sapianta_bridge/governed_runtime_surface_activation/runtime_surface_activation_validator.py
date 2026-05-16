"""Fail-closed governed runtime surface activation validation."""

from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface import FORBIDDEN_EXECUTION_SURFACES
from sapianta_bridge.governed_runtime_execution_surface.runtime_execution_surface_binding import LINEAGE_FIELDS

from .runtime_surface_activation_gate import OPERATIONAL_PATH, validate_activation_transitions


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_surface_activation(
    *,
    activation: dict,
    contract: dict,
    binding: dict,
    policy: dict,
    surface_output: dict,
    states: tuple[str, ...],
    prior_output: dict | None = None,
) -> dict:
    errors = list(validate_activation_transitions(states)["errors"])
    if surface_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_execution_surface", "reason": "surface validation missing"})
    surface_record = surface_output.get("runtime_execution_surface", {})
    if activation.get("runtime_execution_surface_id") != surface_record.get("runtime_execution_surface_id"):
        errors.append({"field": "runtime_execution_surface_id", "reason": "surface identity mutation"})
    if activation.get("runtime_surface") in FORBIDDEN_EXECUTION_SURFACES:
        errors.append({"field": "runtime_surface", "reason": "forbidden runtime surface"})
    if states != OPERATIONAL_PATH:
        errors.append({"field": "states", "reason": "activation not operational"})

    activation_id = activation.get("runtime_surface_activation_id")
    if _missing_text(contract.get("runtime_surface_activation_contract_id")) or contract.get("runtime_surface_activation_id") != activation_id:
        errors.append({"field": "runtime_surface_activation_contract_id", "reason": "activation contract incomplete"})
    if contract.get("surface_validation_required") is not True:
        errors.append({"field": "runtime_surface_activation_contract_id", "reason": "activation contract incomplete"})
    if (
        _missing_text(policy.get("runtime_surface_activation_policy_id"))
        or policy.get("runtime_surface_activation_id") != activation_id
        or policy.get("adaptive_activation_allowed") is not False
        or policy.get("shell_true_allowed") is not False
        or policy.get("raw_shell_execution_allowed") is not False
        or policy.get("unrestricted_subprocess_allowed") is not False
        or policy.get("unrestricted_network_execution_allowed") is not False
    ):
        errors.append({"field": "runtime_surface_activation_policy_id", "reason": "activation policy incomplete"})
    for field in ("runtime_surface_activation_id", "runtime_execution_surface_id", *LINEAGE_FIELDS):
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "activation lineage incomplete"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_surface_activation", {}).get("runtime_surface_activation_id")
        if prior_id != activation_id:
            errors.append({"field": "runtime_surface_activation_id", "reason": "activation drift"})
    return {"valid": not errors, "errors": errors}
