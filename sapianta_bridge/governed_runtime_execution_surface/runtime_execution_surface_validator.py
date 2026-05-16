"""Fail-closed governed runtime execution surface validation."""

from .runtime_execution_surface import ALLOWED_EXECUTION_SURFACES, FORBIDDEN_EXECUTION_SURFACES
from .runtime_execution_surface_binding import LINEAGE_FIELDS


def _missing_text(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def validate_runtime_execution_surface(
    *,
    surface_record: dict,
    contract: dict,
    binding: dict,
    executor: dict,
    policy: dict,
    capability_output: dict,
    prior_output: dict | None = None,
) -> dict:
    errors = []
    if capability_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_capability_mapping", "reason": "capability continuity incomplete"})
    capability_evidence = capability_output.get("runtime_capability_evidence", {})
    primitive = surface_record.get("executor_primitive")
    expected_surface = ALLOWED_EXECUTION_SURFACES.get(primitive)
    if expected_surface is None:
        errors.append({"field": "executor_primitive", "reason": "unknown executor primitive"})
    if _missing_text(surface_record.get("runtime_surface")):
        errors.append({"field": "runtime_surface", "reason": "invalid runtime surface"})
    elif surface_record.get("runtime_surface") in FORBIDDEN_EXECUTION_SURFACES:
        errors.append({"field": "runtime_surface", "reason": "forbidden runtime surface"})
    elif surface_record.get("runtime_surface") != expected_surface:
        errors.append({"field": "runtime_surface", "reason": "executor surface mismatch"})
    if capability_evidence.get("executor_primitive") != primitive:
        errors.append({"field": "executor_primitive", "reason": "capability continuity incomplete"})

    surface_id = surface_record.get("runtime_execution_surface_id")
    for artifact, id_field, reason in (
        (contract, "runtime_execution_surface_contract_id", "surface contract incomplete"),
        (executor, "runtime_execution_surface_executor_id", "surface executor incomplete"),
        (policy, "runtime_execution_surface_policy_id", "surface policy incomplete"),
    ):
        if _missing_text(artifact.get(id_field)) or artifact.get("runtime_execution_surface_id") != surface_id:
            errors.append({"field": id_field, "reason": reason})
    if contract.get("static_surface_required") is not True:
        errors.append({"field": "runtime_execution_surface_contract_id", "reason": "surface contract incomplete"})
    if (
        policy.get("dynamic_surface_inference_allowed") is not False
        or policy.get("shell_true_allowed") is not False
        or policy.get("raw_shell_execution_allowed") is not False
        or policy.get("unrestricted_subprocess_allowed") is not False
        or policy.get("unrestricted_network_execution_allowed") is not False
    ):
        errors.append({"field": "runtime_execution_surface_policy_id", "reason": "surface policy incomplete"})
    if executor.get("runtime_surface") != surface_record.get("runtime_surface"):
        errors.append({"field": "runtime_execution_surface_executor_id", "reason": "executor surface mismatch"})
    for field in ("runtime_execution_surface_id", *LINEAGE_FIELDS):
        if _missing_text(binding.get(field)):
            errors.append({"field": field, "reason": "required surface lineage missing"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_execution_surface", {}).get("runtime_execution_surface_id")
        if prior_id != surface_id:
            errors.append({"field": "runtime_execution_surface_id", "reason": "surface drift"})
    return {"valid": not errors, "errors": errors}
