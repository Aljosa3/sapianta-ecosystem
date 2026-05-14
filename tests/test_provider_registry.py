from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.providers.provider_registry import ProviderRegistry


def test_provider_registry_registers_and_exposes_metadata() -> None:
    registry = ProviderRegistry()

    assert registry.register(CodexAdapter()) == {"registered": True, "errors": []}
    assert registry.register(DeterministicMockAdapter()) == {"registered": True, "errors": []}

    metadata = registry.metadata()
    assert [item["provider_id"] for item in metadata] == ["codex", "deterministic_mock"]
    assert registry.validate()["routing_present"] is False
    assert registry.validate()["dynamic_selection_present"] is False


def test_provider_registry_rejects_duplicate_provider() -> None:
    registry = ProviderRegistry()
    registry.register(CodexAdapter())
    result = registry.register(CodexAdapter())

    assert result["registered"] is False
    assert result["errors"] == [{"field": "provider_id", "reason": "duplicate provider registration"}]


def test_provider_registry_does_not_select_or_route() -> None:
    registry = ProviderRegistry()
    registry.register(CodexAdapter())
    result = registry.validate()

    assert result["scheduling_present"] is False
    assert result["routing_present"] is False
    assert result["optimization_present"] is False
