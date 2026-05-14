from sapianta_bridge.capabilities.modality_model import classify_modality, validate_modality_class


def test_modality_model_classifies_known_modalities() -> None:
    assert classify_modality("TEXT") == "TEXT"
    assert classify_modality("CAD") == "CAD"
    assert classify_modality("INDUSTRIAL") == "INDUSTRIAL"


def test_modality_model_fails_closed_on_unknown_modality() -> None:
    validation = validate_modality_class("HOLOGRAM")

    assert validation["valid"] is False
    assert validation["modality_class"] == "UNKNOWN"
    assert validation["execution_permission_granted"] is False


def test_modality_model_does_not_enable_provider_invocation() -> None:
    validation = validate_modality_class("BROWSER")

    assert validation["valid"] is True
    assert validation["provider_invocation_enabled"] is False
