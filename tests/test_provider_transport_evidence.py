from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.real_provider_transport.provider_transport_connector import local_file_transport_roundtrip
from sapianta_bridge.real_provider_transport.provider_transport_evidence import validate_provider_transport_evidence


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-TRANSPORT-EVIDENCE",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()


def test_provider_transport_evidence_is_valid_and_replay_safe(tmp_path) -> None:
    output = local_file_transport_roundtrip(envelope=_envelope(), transport_dir=tmp_path)
    evidence = output["provider_transport_evidence"]

    assert evidence["replay_safe"] is True
    assert evidence["identity_continuity_valid"] is True
    assert validate_provider_transport_evidence(evidence)["valid"] is True


def test_provider_transport_evidence_rejects_forbidden_behavior_flags(tmp_path) -> None:
    output = local_file_transport_roundtrip(envelope=_envelope(), transport_dir=tmp_path)
    evidence = output["provider_transport_evidence"]
    evidence["routing_present"] = True

    assert validate_provider_transport_evidence(evidence)["valid"] is False
