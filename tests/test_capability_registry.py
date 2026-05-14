from sapianta_bridge.capabilities.capability_declaration import create_capability_declaration
from sapianta_bridge.capabilities.capability_registry import CapabilityRegistry


def test_capability_registry_registers_and_exposes_metadata() -> None:
    registry = CapabilityRegistry()
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="DOCUMENT_ANALYSIS",
    )

    assert registry.register(declaration) == {"registered": True, "errors": []}
    assert registry.metadata()[0]["capability_class"] == "DOCUMENT_ANALYSIS"
    assert registry.validate()["valid"] is True


def test_capability_registry_rejects_duplicate_capability() -> None:
    registry = CapabilityRegistry()
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="DOCUMENT_ANALYSIS",
    )
    registry.register(declaration)
    result = registry.register(declaration)

    assert result["registered"] is False
    assert result["errors"] == [{"field": "capability_class", "reason": "duplicate capability"}]


def test_capability_registry_is_passive_only() -> None:
    registry = CapabilityRegistry()
    registry.register(
        create_capability_declaration(provider_id="deterministic_mock", capability_class="CODE_GENERATION")
    )
    validation = registry.validate()

    assert validation["routing_present"] is False
    assert validation["orchestration_present"] is False
    assert validation["dynamic_selection_present"] is False
    assert validation["execution_authority_granted"] is False
