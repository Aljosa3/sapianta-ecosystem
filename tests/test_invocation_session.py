from sapianta_bridge.active_invocation.invocation_session import create_invocation_session
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-SESSION",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-SESSION",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_session_identity_is_deterministic() -> None:
    first = create_invocation_session(_envelope()).to_dict()
    second = create_invocation_session(_envelope()).to_dict()

    assert first["invocation_id"] == second["invocation_id"]
    assert first["invocation_id"].startswith("INVOCATION-")
    assert first["mutable_state_present"] is False


def test_invocation_session_preserves_replay_lineage() -> None:
    session = create_invocation_session(_envelope()).to_dict()

    assert session["envelope_id"] == "ENV-INV-SESSION"
    assert session["provider_id"] == "deterministic_mock"
    assert session["replay_identity"] == "REPLAY-INV-SESSION"
    assert session["replay_safe"] is True
