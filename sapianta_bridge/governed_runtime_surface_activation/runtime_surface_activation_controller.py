"""Governed runtime surface activation controller."""

from .runtime_surface_activation import create_runtime_surface_activation_record
from .runtime_surface_activation_binding import create_runtime_surface_activation_binding
from .runtime_surface_activation_contract import create_runtime_surface_activation_contract
from .runtime_surface_activation_evidence import runtime_surface_activation_evidence
from .runtime_surface_activation_gate import OPERATIONAL_PATH
from .runtime_surface_activation_policy import create_runtime_surface_activation_policy
from .runtime_surface_activation_validator import validate_runtime_surface_activation


def create_runtime_surface_activation(*, surface_output: dict, prior_output: dict | None = None) -> dict:
    try:
        activation = create_runtime_surface_activation_record(
            execution_surface=surface_output["runtime_execution_surface"]
        )
        contract = create_runtime_surface_activation_contract(
            runtime_surface_activation_id=activation["runtime_surface_activation_id"]
        )
        binding = create_runtime_surface_activation_binding(
            activation_id=activation["runtime_surface_activation_id"],
            surface_output=surface_output,
        )
        policy = create_runtime_surface_activation_policy(
            runtime_surface_activation_id=activation["runtime_surface_activation_id"]
        )
    except KeyError:
        return {
            "validation": {"valid": False, "errors": [{"field": "runtime_surface_activation", "reason": "surface linkage incomplete"}]},
            "states": ["BLOCKED"],
        }
    states = OPERATIONAL_PATH
    validation = validate_runtime_surface_activation(
        activation=activation,
        contract=contract,
        binding=binding,
        policy=policy,
        surface_output=surface_output,
        states=states,
        prior_output=prior_output,
    )
    final_states = states if validation["valid"] else ("BLOCKED",)
    evidence = runtime_surface_activation_evidence(
        activation=activation,
        contract=contract,
        binding=binding,
        policy=policy,
        valid=validation["valid"],
        states=final_states,
    )
    return {
        "runtime_surface_activation": activation,
        "runtime_surface_activation_contract": contract,
        "runtime_surface_activation_binding": binding,
        "runtime_surface_activation_policy": policy,
        "runtime_surface_activation_evidence": evidence,
        "validation": validation,
        "states": list(final_states),
    }
