"""Governed runtime capability mapping controller."""

from .runtime_capability_contract import create_runtime_capability_contract
from .runtime_capability_evidence import AUTHORIZED_PATH, runtime_capability_evidence
from .runtime_capability_executor import create_runtime_capability_executor
from .runtime_capability_mapping import create_runtime_capability_mapping_record
from .runtime_capability_policy import create_runtime_capability_policy
from .runtime_capability_surface import create_runtime_capability_surface
from .runtime_capability_validator import validate_runtime_capability_mapping


def create_runtime_capability_mapping(*, operation_output: dict, prior_output: dict | None = None) -> dict:
    try:
        operation_evidence = operation_output["runtime_operation_evidence"]
        mapping = create_runtime_capability_mapping_record(operation_evidence=operation_evidence)
        contract = create_runtime_capability_contract(runtime_capability_mapping_id=mapping["runtime_capability_mapping_id"])
        executor = create_runtime_capability_executor(
            runtime_capability_mapping_id=mapping["runtime_capability_mapping_id"],
            executor_primitive=mapping["executor_primitive"],
        )
        surface = create_runtime_capability_surface(runtime_capability_mapping_id=mapping["runtime_capability_mapping_id"])
        policy = create_runtime_capability_policy(runtime_capability_mapping_id=mapping["runtime_capability_mapping_id"])
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_capability_mapping", "reason": "operation linkage incomplete"}]},
            "states": ["BLOCKED"],
        }

    validation = validate_runtime_capability_mapping(
        mapping=mapping,
        contract=contract,
        executor=executor,
        surface=surface,
        policy=policy,
        operation_output=operation_output,
        prior_output=prior_output,
    )
    if validation["valid"]:
        states = AUTHORIZED_PATH
    elif any(error["field"] in {"operation_type", "executor_primitive"} for error in validation["errors"]):
        states = ("CAPABILITY_REJECTED",)
    else:
        states = ("BLOCKED",)
    evidence = runtime_capability_evidence(
        mapping=mapping,
        contract=contract,
        executor=executor,
        surface=surface,
        policy=policy,
        operation_evidence=operation_evidence,
        valid=validation["valid"],
        states=states,
    )
    return {
        "runtime_capability_mapping": mapping,
        "runtime_capability_contract": contract,
        "runtime_capability_executor": executor,
        "runtime_capability_surface": surface,
        "runtime_capability_policy": policy,
        "runtime_capability_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
