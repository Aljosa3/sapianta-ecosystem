from sapianta_bridge.capabilities.capability_declaration import create_capability_declaration


def test_capability_declaration_is_replay_safe_metadata() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="DOCUMENT_ANALYSIS",
        evidence_refs=["capability-evidence"],
    ).to_dict()

    assert declaration["provider_id"] == "deterministic_mock"
    assert declaration["modality_class"] == "TEXT"
    assert declaration["evidence_refs"] == ["capability-evidence"]
    assert declaration["execution_authority_granted"] is False
    assert declaration["routing_enabled"] is False


def test_capability_declaration_does_not_bypass_envelopes_or_provider_abstraction() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="CODE_GENERATION",
    ).to_dict()

    assert declaration["envelope_bypass_allowed"] is False
    assert declaration["provider_abstraction_bypass_allowed"] is False
    assert declaration["autonomous_provider_selection_enabled"] is False
