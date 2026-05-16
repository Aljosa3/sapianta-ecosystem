from .operational_runtime_entrypoint_activation import create_entrypoint_activation
from .operational_runtime_entrypoint_admission import create_entry_admission
from .operational_runtime_entrypoint_boundary import CLOSED_PATH, READY_PATH, create_activation_boundary
from .operational_runtime_entrypoint_contract import create_entry_contract
from .operational_runtime_entrypoint_evidence import operational_entrypoint_evidence
from .operational_runtime_entrypoint_validator import validate_operational_runtime_entrypoint


def create_operational_runtime_entrypoint(
    *,
    channel_output: dict,
    operational_intent: str,
    admitted: bool,
    approved_by: str,
    close_requested: bool = False,
    prior_output: dict | None = None,
) -> dict:
    try:
        binding = channel_output["runtime_persistent_channel_binding"]
        boundary = create_activation_boundary(channel_binding=binding)
        contract = create_entry_contract(boundary=boundary, operational_intent=operational_intent)
        admission = create_entry_admission(contract=contract, admitted=admitted, approved_by=approved_by)
        activation = create_entrypoint_activation(boundary=boundary, contract=contract, admission=admission)
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "operational_entrypoint", "reason": "channel linkage incomplete"}]},
            "states": ["BLOCKED"],
        }

    validation = validate_operational_runtime_entrypoint(
        activation=activation,
        boundary=boundary,
        contract=contract,
        admission=admission,
        channel_output=channel_output,
        prior_output=prior_output,
    )
    states = (CLOSED_PATH if close_requested else READY_PATH) if validation["valid"] else ("BLOCKED",)
    closed = validation["valid"] and close_requested
    evidence = operational_entrypoint_evidence(
        activation=activation,
        boundary=boundary,
        contract=contract,
        admission=admission,
        binding=binding,
        valid=validation["valid"],
        states=states,
        closed=closed,
    )
    return {
        "activation": activation,
        "boundary": boundary,
        "contract": contract,
        "admission": admission,
        "evidence": evidence,
        "validation": validation,
        "states": list(states),
        "closed": closed,
    }
