"""Fail-closed governed execution realization validation."""

from .runtime_execution_realization import ALLOWED_REALIZATION_MODES, FORBIDDEN_REALIZATION_MODES
from .runtime_execution_realization_binding import LINEAGE_FIELDS


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_execution_realization(
    *,
    realization: dict,
    contract: dict,
    transaction: dict,
    binding: dict,
    policy: dict,
    activation_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if activation_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_surface_activation", "reason": "surface activation missing"})
    activation_evidence = activation_output.get("runtime_surface_activation_evidence", {})
    if activation_evidence.get("surface_operational") is not True:
        errors.append({"field": "runtime_surface_activation", "reason": "surface is not operational"})
    if realization.get("runtime_surface_activation_id") != activation_evidence.get("runtime_surface_activation_id"):
        errors.append({"field": "runtime_surface_activation_id", "reason": "surface activation linkage missing"})
    expected_mode = ALLOWED_REALIZATION_MODES.get(realization.get("runtime_surface"))
    mode = realization.get("realization_mode")
    if mode in FORBIDDEN_REALIZATION_MODES:
        errors.append({"field": "realization_mode", "reason": "realization mode forbidden"})
    elif _missing_text(mode):
        errors.append({"field": "realization_mode", "reason": "realization mode unknown"})
    elif mode != expected_mode:
        errors.append({"field": "realization_mode", "reason": "surface realization mismatch"})

    realization_id = realization.get("runtime_execution_realization_id")
    if _missing_text(contract.get("runtime_execution_realization_contract_id")) or contract.get("runtime_execution_realization_id") != realization_id:
        errors.append({"field": "runtime_execution_realization_contract_id", "reason": "realization contract incomplete"})
    if contract.get("activated_surface_required") is not True:
        errors.append({"field": "runtime_execution_realization_contract_id", "reason": "realization contract incomplete"})
    if (
        _missing_text(transaction.get("runtime_execution_realization_transaction_id"))
        or transaction.get("runtime_execution_realization_id") != realization_id
        or _missing_text(transaction.get("result_capture_id"))
        or _missing_text(transaction.get("response_return_id"))
    ):
        errors.append({"field": "runtime_execution_realization_transaction_id", "reason": "realization transaction incomplete"})
    if (
        _missing_text(policy.get("runtime_execution_realization_policy_id"))
        or policy.get("runtime_execution_realization_id") != realization_id
        or policy.get("shell_true_allowed") is not False
        or policy.get("raw_shell_execution_allowed") is not False
        or policy.get("unrestricted_subprocess_allowed") is not False
        or policy.get("unrestricted_network_execution_allowed") is not False
        or policy.get("autonomous_execution_allowed") is not False
    ):
        errors.append({"field": "runtime_execution_realization_policy_id", "reason": "realization policy incomplete"})
    for field in ("runtime_execution_realization_id", *LINEAGE_FIELDS):
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "realization lineage incomplete"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_execution_realization", {}).get("runtime_execution_realization_id")
        if prior_id != realization_id:
            errors.append({"field": "runtime_execution_realization_id", "reason": "realization identity changed"})
    return {"valid": not errors, "errors": errors}
