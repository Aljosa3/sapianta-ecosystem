"""Governed runtime operational entrypoint controller."""

from .runtime_operational_entrypoint import create_runtime_operational_entrypoint_record
from .runtime_operational_entrypoint_binding import create_runtime_operational_entrypoint_binding
from .runtime_operational_entrypoint_contract import create_runtime_operational_entrypoint_contract
from .runtime_operational_entrypoint_evidence import runtime_operational_entrypoint_evidence
from .runtime_operational_entrypoint_policy import create_runtime_operational_entrypoint_policy
from .runtime_operational_entrypoint_transaction import create_runtime_operational_entrypoint_transaction
from .runtime_operational_entrypoint_validator import validate_runtime_operational_entrypoint


def create_runtime_operational_entrypoint(
    *,
    realization_output: dict,
    operational_entry_mode: str,
    supplemental_lineage: dict,
    prior_output: dict | None = None,
) -> dict:
    try:
        realization_evidence = realization_output["runtime_execution_realization_evidence"]
        entrypoint = create_runtime_operational_entrypoint_record(
            realization_evidence=realization_evidence,
            operational_entry_mode=operational_entry_mode,
        )
        lineage = {**realization_evidence, **supplemental_lineage}
        contract = create_runtime_operational_entrypoint_contract(
            runtime_operational_entrypoint_id=entrypoint["runtime_operational_entrypoint_id"]
        )
        binding = create_runtime_operational_entrypoint_binding(
            runtime_operational_entrypoint_id=entrypoint["runtime_operational_entrypoint_id"],
            lineage=lineage,
        )
        transaction = create_runtime_operational_entrypoint_transaction(
            runtime_operational_entrypoint_id=entrypoint["runtime_operational_entrypoint_id"],
            runtime_execution_realization_id=binding["runtime_execution_realization_id"],
            result_capture_id=binding["result_capture_id"],
            response_return_id=binding["response_return_id"],
        )
        policy = create_runtime_operational_entrypoint_policy(
            runtime_operational_entrypoint_id=entrypoint["runtime_operational_entrypoint_id"]
        )
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_operational_entrypoint", "reason": "entrypoint linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    validation = validate_runtime_operational_entrypoint(
        entrypoint=entrypoint,
        contract=contract,
        transaction=transaction,
        binding=binding,
        policy=policy,
        realization_output=realization_output,
        prior_output=prior_output,
    )
    states = ("OPERATIONAL_ENTRYPOINT_ADMITTED",) if validation["valid"] else (
        "OPERATIONAL_ENTRYPOINT_REJECTED" if any(error["field"] == "operational_entry_mode" for error in validation["errors"]) else "BLOCKED",
    )
    evidence = runtime_operational_entrypoint_evidence(
        entrypoint=entrypoint,
        contract=contract,
        transaction=transaction,
        binding=binding,
        policy=policy,
        valid=validation["valid"],
    )
    return {
        "runtime_operational_entrypoint": entrypoint,
        "runtime_operational_entrypoint_contract": contract,
        "runtime_operational_entrypoint_transaction": transaction,
        "runtime_operational_entrypoint_binding": binding,
        "runtime_operational_entrypoint_policy": policy,
        "runtime_operational_entrypoint_evidence": evidence,
        "validation": validation,
        "states": list(states),
    }
