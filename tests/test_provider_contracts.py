from sapianta_bridge.providers.provider_contracts import (
    ProviderContract,
    provider_contract_evidence,
    validate_provider_contract,
)


def test_valid_provider_contract_passes() -> None:
    contract = ProviderContract(provider_id="codex", provider_type="REMOTE_LLM")
    result = validate_provider_contract(contract)

    assert result["valid"] is True
    assert result["provider_contract_valid"] is True
    assert result["governance_independent"] is True
    assert result["authority_escalation_detected"] is False


def test_provider_contract_rejects_governance_authority() -> None:
    contract = ProviderContract(
        provider_id="codex",
        provider_type="REMOTE_LLM",
        governance_authority=True,
    )
    result = validate_provider_contract(contract)

    assert result["valid"] is False
    assert {"field": "governance_authority", "reason": "provider contract requires False"} in result["errors"]


def test_provider_contract_rejects_replay_mutation() -> None:
    contract = ProviderContract(
        provider_id="local_executor",
        provider_type="LOCAL_EXECUTOR",
        replay_mutation_allowed=True,
    )
    result = validate_provider_contract(contract)

    assert result["valid"] is False
    assert {"field": "replay_mutation_allowed", "reason": "provider contract requires False"} in result["errors"]


def test_provider_contract_evidence_is_deterministic() -> None:
    contract = ProviderContract(provider_id="deterministic_mock", provider_type="DETERMINISTIC_MOCK")

    assert provider_contract_evidence(contract) == provider_contract_evidence(contract)
    assert provider_contract_evidence(contract)["replay_safe"] is True
