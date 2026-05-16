"""Fail-closed governed runtime operational entrypoint validation."""

from .runtime_operational_entrypoint import (
    ALLOWED_OPERATIONAL_ENTRY_MODES,
    FORBIDDEN_OPERATIONAL_ENTRY_MODES,
)
from .runtime_operational_entrypoint_binding import LINEAGE_FIELDS


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_operational_entrypoint(
    *,
    entrypoint: dict,
    contract: dict,
    transaction: dict,
    binding: dict,
    policy: dict,
    realization_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if realization_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_execution_realization", "reason": "runtime realization continuity absent"})
    realization_evidence = realization_output.get("runtime_execution_realization_evidence", {})
    if entrypoint.get("runtime_execution_realization_id") != realization_evidence.get("runtime_execution_realization_id"):
        errors.append({"field": "runtime_execution_realization_id", "reason": "runtime activation linkage incomplete"})
    mode = entrypoint.get("operational_entry_mode")
    if mode in FORBIDDEN_OPERATIONAL_ENTRY_MODES:
        errors.append({"field": "operational_entry_mode", "reason": "operational entry mode forbidden"})
    elif mode not in ALLOWED_OPERATIONAL_ENTRY_MODES:
        errors.append({"field": "operational_entry_mode", "reason": "operational entry mode unknown"})

    entry_id = entrypoint.get("runtime_operational_entrypoint_id")
    if _missing_text(contract.get("runtime_operational_entrypoint_contract_id")) or contract.get("runtime_operational_entrypoint_id") != entry_id:
        errors.append({"field": "runtime_operational_entrypoint_contract_id", "reason": "entrypoint contract incomplete"})
    if contract.get("realization_continuity_required") is not True:
        errors.append({"field": "runtime_operational_entrypoint_contract_id", "reason": "entrypoint contract incomplete"})
    if (
        _missing_text(transaction.get("runtime_operational_entrypoint_transaction_id"))
        or transaction.get("runtime_operational_entrypoint_id") != entry_id
        or _missing_text(transaction.get("runtime_execution_realization_id"))
        or _missing_text(transaction.get("result_capture_id"))
        or _missing_text(transaction.get("response_return_id"))
    ):
        errors.append({"field": "runtime_operational_entrypoint_transaction_id", "reason": "transaction linkage incomplete"})
    if (
        _missing_text(policy.get("runtime_operational_entrypoint_policy_id"))
        or policy.get("runtime_operational_entrypoint_id") != entry_id
        or policy.get("shell_true_allowed") is not False
        or policy.get("raw_shell_execution_allowed") is not False
        or policy.get("unrestricted_subprocess_allowed") is not False
        or policy.get("runtime_self_expansion_allowed") is not False
    ):
        errors.append({"field": "runtime_operational_entrypoint_policy_id", "reason": "entrypoint policy incomplete"})
    for field in ("runtime_operational_entrypoint_id", *LINEAGE_FIELDS):
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "required lineage missing"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_operational_entrypoint", {}).get("runtime_operational_entrypoint_id")
        if prior_id != entry_id:
            errors.append({"field": "runtime_operational_entrypoint_id", "reason": "entrypoint identity drifts"})
    return {"valid": not errors, "errors": errors}
