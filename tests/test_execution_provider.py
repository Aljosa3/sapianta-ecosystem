from sapianta_bridge.providers.adapters.claude_adapter import ClaudeAdapter
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.providers.adapters.local_adapter import LocalAdapter


def test_structural_adapters_have_valid_contracts() -> None:
    for adapter in (CodexAdapter(), ClaudeAdapter(), LocalAdapter(), DeterministicMockAdapter()):
        assert adapter.validate_contract()["valid"] is True


def test_provider_requires_bounded_envelope() -> None:
    result = CodexAdapter().execute({"bounded": False})

    assert result.execution_status == "BLOCKED"
    assert result.provider_id == "codex"


def test_provider_rejects_governance_authority_in_envelope() -> None:
    validation = LocalAdapter().validate_envelope(
        {"bounded": True, "governance_authority_granted": True}
    )

    assert validation["valid"] is False
    assert validation["errors"] == [
        {"field": "governance_authority_granted", "reason": "provider cannot receive governance authority"}
    ]


def test_deterministic_mock_returns_normalized_result() -> None:
    adapter = DeterministicMockAdapter()
    first = adapter.execute({"bounded": True, "expected_artifacts": ["b.txt", "a.txt"]})
    second = adapter.execute({"bounded": True, "expected_artifacts": ["b.txt", "a.txt"]})

    assert first == second
    assert first.execution_status == "SUCCESS"
    assert first.artifacts_created == ("a.txt", "b.txt")
    assert adapter.validate_result(first)["valid"] is True


def test_placeholder_remote_adapters_do_not_execute_real_providers() -> None:
    result = ClaudeAdapter().execute({"bounded": True})

    assert result.execution_status == "NOT_EXECUTED"
    assert result.replay_safe is True
    assert result.governance_modified is False
