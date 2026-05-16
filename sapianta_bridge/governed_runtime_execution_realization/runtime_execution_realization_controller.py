"""Governed runtime execution realization controller."""

from .runtime_execution_realization import create_runtime_execution_realization_record
from .runtime_execution_realization_binding import create_runtime_execution_realization_binding
from .runtime_execution_realization_contract import create_runtime_execution_realization_contract
from .runtime_execution_realization_evidence import AUTHORIZED_PATH, runtime_execution_realization_evidence
from .runtime_execution_realization_policy import create_runtime_execution_realization_policy
from .runtime_execution_realization_transaction import create_runtime_execution_realization_transaction
from .runtime_execution_realization_validator import validate_runtime_execution_realization


def create_runtime_execution_realization(
    *,
    activation_output: dict,
    realization_lineage: dict,
    prior_output: dict | None = None,
) -> dict:
    try:
        activation_evidence = activation_output["runtime_surface_activation_evidence"]
        realization = create_runtime_execution_realization_record(activation_evidence=activation_evidence)
        contract = create_runtime_execution_realization_contract(
            runtime_execution_realization_id=realization["runtime_execution_realization_id"]
        )
        binding = create_runtime_execution_realization_binding(
            runtime_execution_realization_id=realization["runtime_execution_realization_id"],
            realization_lineage=realization_lineage,
        )
        transaction = create_runtime_execution_realization_transaction(
            runtime_execution_realization_id=realization["runtime_execution_realization_id"],
            result_capture_id=binding["result_capture_id"],
            response_return_id=binding["response_return_id"],
        )
        policy = create_runtime_execution_realization_policy(
            runtime_execution_realization_id=realization["runtime_execution_realization_id"]
        )
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_execution_realization", "reason": "realization linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_runtime_execution_realization(
        realization=realization,
        contract=contract,
        transaction=transaction,
        binding=binding,
        policy=policy,
        activation_output=activation_output,
        prior_output=prior_output,
    )
    if validation["valid"]:
        states = AUTHORIZED_PATH
    elif any(error["field"] == "realization_mode" for error in validation["errors"]):
        states = ("EXECUTION_REALIZATION_REJECTED",)
    else:
        states = ("BLOCKED",)
    evidence = runtime_execution_realization_evidence(
        realization=realization,
        contract=contract,
        transaction=transaction,
        binding=binding,
        policy=policy,
        valid=validation["valid"],
        states=states,
    )
    return {
        "runtime_execution_realization": realization,
        "runtime_execution_realization_contract": contract,
        "runtime_execution_realization_transaction": transaction,
        "runtime_execution_realization_binding": binding,
        "runtime_execution_realization_policy": policy,
        "runtime_execution_realization_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
