import json

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.real_provider_transport.provider_transport_connector import local_file_transport_roundtrip


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-TRANSPORT-CONNECTOR",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT-CONNECTOR",
        validation_requirements=["pytest"],
    ).to_dict()


def test_local_file_transport_roundtrip_writes_and_reads_artifacts(tmp_path) -> None:
    output = local_file_transport_roundtrip(envelope=_envelope(), transport_dir=tmp_path)

    assert output["transport_status"] == "SUCCESS"
    assert output["provider_transport_evidence"]["local_file_transport_used"] is True
    task = json.loads((tmp_path / f"{output['provider_transport_request']['transport_id']}.task.json").read_text())
    result = json.loads((tmp_path / f"{output['provider_transport_request']['transport_id']}.result.json").read_text())
    assert task["transport_id"] == result["transport_id"]
    assert result["provider_id"] == "deterministic_mock"


def test_local_file_transport_blocks_invalid_envelope(tmp_path) -> None:
    envelope = _envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS"]
    output = local_file_transport_roundtrip(envelope=envelope, transport_dir=tmp_path)

    assert output["transport_status"] == "BLOCKED"
    assert output["provider_transport_request"] == {}


def test_local_file_transport_exposes_no_routing_retry_or_fallback(tmp_path) -> None:
    output = local_file_transport_roundtrip(envelope=_envelope(), transport_dir=tmp_path)

    assert output["routing_present"] is False
    assert output["retry_present"] is False
    assert output["fallback_present"] is False
    assert output["orchestration_present"] is False
