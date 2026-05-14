from sapianta_bridge.capabilities.capability_declaration import create_capability_declaration
from sapianta_bridge.capabilities.capability_evidence import capability_evidence, validate_capability_evidence


def test_capability_evidence_is_replay_safe_for_valid_declaration() -> None:
    declaration = create_capability_declaration(
        provider_id="deterministic_mock",
        capability_class="IMAGE_GENERATION",
    )
    evidence = capability_evidence(declaration)

    assert evidence["capability_admissible"] is True
    assert evidence["modality_class"] == "IMAGE"
    assert evidence["replay_safe"] is True
    assert validate_capability_evidence(evidence)["valid"] is True


def test_capability_evidence_rejects_forbidden_authority_flags() -> None:
    evidence = capability_evidence(
        create_capability_declaration(provider_id="deterministic_mock", capability_class="CAD_MODELING")
    )
    evidence["provider_invocation_enabled"] = True

    assert validate_capability_evidence(evidence)["valid"] is False


def test_capability_evidence_records_fail_closed_unknowns() -> None:
    evidence = capability_evidence(
        create_capability_declaration(provider_id="deterministic_mock", capability_class="UNKNOWN")
    )

    assert evidence["capability_admissible"] is False
    assert evidence["replay_safe"] is False
