from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_payload import create_result_payload
from sapianta_bridge.result_loop.result_validator import validate_result_inputs, validate_result_payload


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-VAL",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-VAL",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_validator_accepts_valid_payload() -> None:
    output = _invocation_output()
    payload = create_result_payload(output["invocation_result"], output["invocation_evidence"]).to_dict()
    validation = validate_result_payload(payload)

    assert validation["valid"] is True
    assert validation["result_binding_valid"] is True


def test_result_validator_fails_closed_on_malformed_payload() -> None:
    validation = validate_result_payload({"invocation_id": "INV"})

    assert validation["valid"] is False


def test_result_validator_rejects_provider_mismatch() -> None:
    output = _invocation_output()
    evidence = dict(output["invocation_evidence"])
    evidence["provider_id"] = "codex"
    validation = validate_result_inputs(output["invocation_result"], evidence)

    assert validation["valid"] is False
    assert {"field": "provider_id", "reason": "invocation result/evidence mismatch"} in validation["errors"]


def test_result_validator_rejects_invalid_lifecycle() -> None:
    output = _invocation_output()
    payload = create_result_payload(output["invocation_result"], output["invocation_evidence"]).to_dict()
    payload["evidence_references"]["lifecycle"] = ["PROPOSED", "RETRYING"]
    validation = validate_result_payload(payload)

    assert validation["valid"] is False
    assert {"field": "lifecycle", "reason": "invalid result lifecycle"} in validation["errors"]
