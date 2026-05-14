from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.envelopes.replay_binding import (
    compute_replay_binding,
    validate_replay_binding,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-1",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-1",
        validation_requirements=["pytest"],
    ).to_dict()


def test_replay_binding_is_deterministic() -> None:
    envelope = _envelope()

    assert compute_replay_binding(envelope) == compute_replay_binding(envelope)


def test_replay_binding_validation_passes() -> None:
    envelope = _envelope()
    result = validate_replay_binding(envelope)

    assert result["valid"] is True
    assert result["same_envelope_same_authority_semantics"] is True


def test_replay_binding_mismatch_fails_closed() -> None:
    envelope = _envelope()
    envelope["replay_binding_sha256"] = "bad"
    result = validate_replay_binding(envelope)

    assert result["valid"] is False
    assert {"field": "replay_binding_sha256", "reason": "replay binding mismatch"} in result["errors"]


def test_missing_replay_identity_fails_closed() -> None:
    envelope = _envelope()
    envelope["replay_identity"] = ""
    result = validate_replay_binding(envelope)

    assert result["valid"] is False
    assert {"field": "replay_identity", "reason": "replay identity must be non-empty"} in result["errors"]
