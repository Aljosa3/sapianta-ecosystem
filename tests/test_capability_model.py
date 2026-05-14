from sapianta_bridge.capabilities.capability_model import (
    classify_capability,
    modality_for_capability,
    validate_capability_class,
)


def test_capability_model_classifies_known_capabilities() -> None:
    assert classify_capability("CODE_GENERATION") == "CODE_GENERATION"
    assert modality_for_capability("IMAGE_EDITING") == "IMAGE"
    assert modality_for_capability("ROBOTIC_ACTION") == "ROBOTIC"


def test_capability_model_fails_closed_on_unknown_capability() -> None:
    validation = validate_capability_class("NEW_POWER")

    assert validation["valid"] is False
    assert validation["capability_class"] == "UNKNOWN"
    assert validation["execution_authority_granted"] is False


def test_capability_model_never_enables_routing_or_orchestration() -> None:
    validation = validate_capability_class("DOCUMENT_ANALYSIS")

    assert validation["valid"] is True
    assert validation["routing_enabled"] is False
    assert validation["orchestration_enabled"] is False
