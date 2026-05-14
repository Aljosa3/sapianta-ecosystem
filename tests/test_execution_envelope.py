from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope


def test_execution_envelope_is_serializable_and_replay_safe() -> None:
    envelope = create_execution_envelope(
        envelope_id="ENV-1",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-1",
        validation_requirements=["pytest"],
    )
    value = envelope.to_dict()

    assert value["envelope_id"] == "ENV-1"
    assert value["provider_id"] == "codex"
    assert value["replay_safe"] is True
    assert isinstance(value["replay_binding_sha256"], str)
    assert value["allowed_actions"] == ["inspect"]


def test_execution_envelope_sorts_actions_and_validation_requirements() -> None:
    envelope = create_execution_envelope(
        envelope_id="ENV-2",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["RUN_TESTS", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["z", "a"],
        forbidden_actions=["y", "b"],
        replay_identity="REPLAY-2",
        validation_requirements=["py_compile", "pytest"],
    ).to_dict()

    assert envelope["allowed_actions"] == ["a", "z"]
    assert envelope["forbidden_actions"] == ["b", "y"]
    assert envelope["validation_requirements"] == ["py_compile", "pytest"]
