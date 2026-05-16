"""Fail-closed governed runtime operational entrypoint validation."""

from .runtime_operational_entrypoint_binding import LINEAGE_FIELDS


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_operational_entrypoint(
    *,
    session: dict,
    request: dict,
    response: dict,
    binding: dict,
    realization_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if realization_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_execution_realization", "reason": "runtime realization continuity absent"})
    realization_evidence = realization_output.get("runtime_execution_realization_evidence", {})
    if session.get("runtime_execution_realization_id") != realization_evidence.get("runtime_execution_realization_id"):
        errors.append({"field": "runtime_execution_realization_id", "reason": "runtime activation linkage incomplete"})
    entry_id = session.get("runtime_operational_entrypoint_id")
    if _missing_text(request.get("runtime_operational_entrypoint_request_id")) or request.get("runtime_operational_entrypoint_id") != entry_id:
        errors.append({"field": "runtime_operational_entrypoint_request_id", "reason": "transaction linkage incomplete"})
    if (
        _missing_text(response.get("runtime_operational_entrypoint_response_id"))
        or response.get("runtime_operational_entrypoint_id") != entry_id
        or _missing_text(response.get("response_return_id"))
    ):
        errors.append({"field": "runtime_operational_entrypoint_response_id", "reason": "response return linkage incomplete"})
    for field in ("runtime_operational_entrypoint_id", *LINEAGE_FIELDS):
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "required lineage missing"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_operational_entrypoint_session", {}).get("runtime_operational_entrypoint_id")
        if prior_id != entry_id:
            errors.append({"field": "runtime_operational_entrypoint_id", "reason": "entrypoint identity drifts"})
    return {"valid": not errors, "errors": errors}
