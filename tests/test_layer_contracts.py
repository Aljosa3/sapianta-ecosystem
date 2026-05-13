from sapianta_bridge.architecture.layer_contracts import (
    validate_all_layer_contracts,
    validate_layer_contract,
    validate_provider_contract,
)
from sapianta_bridge.architecture.layer_model import get_layer_definition


def test_all_layer_contracts_are_valid() -> None:
    result = validate_all_layer_contracts()

    assert result["valid"] is True
    assert all(layer["valid"] for layer in result["layers"].values())


def test_layer_contract_rejects_missing_authority() -> None:
    contract = get_layer_definition("INTERACTION_LAYER")
    contract.pop("authority")

    result = validate_layer_contract("INTERACTION_LAYER", contract)

    assert result["valid"] is False
    assert {"field": "authority", "reason": "missing layer contract field"} in result["errors"]


def test_provider_contract_is_non_authoritative() -> None:
    result = validate_provider_contract("codex")

    assert result["valid"] is True
    assert result["errors"] == []


def test_provider_contract_rejects_empty_provider() -> None:
    result = validate_provider_contract("")

    assert result["valid"] is False
    assert result["errors"] == [
        {"field": "provider", "reason": "provider identity must be non-empty"}
    ]
