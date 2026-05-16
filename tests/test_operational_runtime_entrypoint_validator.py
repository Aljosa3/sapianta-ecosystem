from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_activation import (
    create_entrypoint_activation,
)
from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_admission import (
    create_entry_admission,
)
from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_boundary import (
    create_activation_boundary,
)
from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_contract import (
    create_entry_contract,
)
from sapianta_bridge.governed_operational_runtime_entrypoint.operational_runtime_entrypoint_validator import (
    validate_operational_runtime_entrypoint,
)


def _artifacts():
    binding = {
        "runtime_persistent_channel_id": "CHANNEL-1",
        "runtime_surface_session_id": "SURFACE-1",
        "direct_runtime_interaction_session_id": "INTERACTION-1",
        "execution_exchange_session_id": "EXCHANGE-1",
        "execution_relay_session_id": "RELAY-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "runtime_delivery_finalization_id": "FINALIZATION-1",
        "response_return_id": "RESPONSE-1",
    }
    boundary = create_activation_boundary(channel_binding=binding)
    contract = create_entry_contract(boundary=boundary, operational_intent="bounded_runtime_entry")
    admission = create_entry_admission(contract=contract, admitted=True, approved_by="human")
    activation = create_entrypoint_activation(boundary=boundary, contract=contract, admission=admission)
    channel_output = {"runtime_persistent_channel_binding": binding, "validation": {"valid": True}}
    return activation, boundary, contract, admission, channel_output


def test_validator_accepts_explicit_operational_admission():
    activation, boundary, contract, admission, channel_output = _artifacts()
    result = validate_operational_runtime_entrypoint(
        activation=activation,
        boundary=boundary,
        contract=contract,
        admission=admission,
        channel_output=channel_output,
    )
    assert result["valid"] is True


def test_validator_blocks_missing_response_linkage():
    activation, boundary, contract, admission, channel_output = _artifacts()
    channel_output["runtime_persistent_channel_binding"]["response_return_id"] = ""
    result = validate_operational_runtime_entrypoint(
        activation=activation,
        boundary=boundary,
        contract=contract,
        admission=admission,
        channel_output=channel_output,
    )
    assert result["valid"] is False


def test_validator_blocks_non_human_admission():
    activation, boundary, contract, admission, channel_output = _artifacts()
    admission["approved_by"] = "system"
    result = validate_operational_runtime_entrypoint(
        activation=activation,
        boundary=boundary,
        contract=contract,
        admission=admission,
        channel_output=channel_output,
    )
    assert result["valid"] is False
