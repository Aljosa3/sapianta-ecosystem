"""Governed runtime execution surface controller."""

from .runtime_execution_surface import create_runtime_execution_surface_record
from .runtime_execution_surface_binding import create_runtime_execution_surface_binding
from .runtime_execution_surface_contract import create_runtime_execution_surface_contract
from .runtime_execution_surface_evidence import AUTHORIZED_PATH, runtime_execution_surface_evidence
from .runtime_execution_surface_executor import create_runtime_execution_surface_executor
from .runtime_execution_surface_policy import create_runtime_execution_surface_policy
from .runtime_execution_surface_validator import validate_runtime_execution_surface


def create_runtime_execution_surface(
    *,
    capability_output: dict,
    realization_lineage: dict,
    prior_output: dict | None = None,
) -> dict:
    try:
        capability_evidence = capability_output["runtime_capability_evidence"]
        surface_record = create_runtime_execution_surface_record(capability_evidence=capability_evidence)
        contract = create_runtime_execution_surface_contract(runtime_execution_surface_id=surface_record["runtime_execution_surface_id"])
        binding = create_runtime_execution_surface_binding(
            runtime_execution_surface_id=surface_record["runtime_execution_surface_id"],
            realization_lineage=realization_lineage,
        )
        executor = create_runtime_execution_surface_executor(
            runtime_execution_surface_id=surface_record["runtime_execution_surface_id"],
            executor_primitive=surface_record["executor_primitive"],
            runtime_surface=surface_record["runtime_surface"],
        )
        policy = create_runtime_execution_surface_policy(runtime_execution_surface_id=surface_record["runtime_execution_surface_id"])
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_execution_surface", "reason": "surface linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_runtime_execution_surface(
        surface_record=surface_record,
        contract=contract,
        binding=binding,
        executor=executor,
        policy=policy,
        capability_output=capability_output,
        prior_output=prior_output,
    )
    if validation["valid"]:
        states = AUTHORIZED_PATH
    elif any(error["field"] in {"runtime_surface", "executor_primitive"} for error in validation["errors"]):
        states = ("EXECUTION_SURFACE_REJECTED",)
    else:
        states = ("BLOCKED",)
    evidence = runtime_execution_surface_evidence(
        surface_record=surface_record,
        contract=contract,
        binding=binding,
        executor=executor,
        policy=policy,
        valid=validation["valid"],
        states=states,
    )
    return {
        "runtime_execution_surface": surface_record,
        "runtime_execution_surface_contract": contract,
        "runtime_execution_surface_binding": binding,
        "runtime_execution_surface_executor": executor,
        "runtime_execution_surface_policy": policy,
        "runtime_execution_surface_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
