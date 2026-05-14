from sapianta_bridge.capabilities.capability_declaration import create_capability_declaration
from sapianta_bridge.capabilities.capability_validator import validate_capability_declaration


def test_capability_validator_accepts_valid_declaration() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="TEST_EXECUTION",
    ).to_dict()
    validation = validate_capability_declaration(declaration)

    assert validation["valid"] is True
    assert validation["capability_authority_granted"] is False


def test_capability_validator_rejects_unknown_capability() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="UNKNOWN",
    ).to_dict()
    validation = validate_capability_declaration(declaration)

    assert validation["valid"] is False
    assert {"field": "capability_class", "reason": "unknown capability fails closed"} in validation["errors"]


def test_capability_validator_rejects_unknown_modality() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="CODE_GENERATION",
        modality_class="UNKNOWN",
    ).to_dict()
    validation = validate_capability_declaration(declaration)

    assert validation["valid"] is False
    assert {"field": "modality_class", "reason": "unknown modality fails closed"} in validation["errors"]


def test_capability_validator_rejects_authority_grants() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="DOCUMENT_ANALYSIS",
    ).to_dict()
    declaration["routing_enabled"] = True
    validation = validate_capability_declaration(declaration)

    assert validation["valid"] is False
    assert {"field": "routing_enabled", "reason": "capability declaration cannot grant authority"} in validation["errors"]
