from sapianta_bridge.real_e2e_codex_loop.e2e_loop_identity import (
    create_e2e_loop_identity,
    validate_e2e_loop_identity,
)


def test_real_e2e_loop_identity_is_deterministic():
    first = create_e2e_loop_identity(
        chatgpt_request="execute governed validation",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()
    second = create_e2e_loop_identity(
        chatgpt_request="execute governed validation",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()

    assert first == second
    assert first["immutable"] is True
    assert validate_e2e_loop_identity(first, chatgpt_request="execute governed validation")["valid"] is True


def test_real_e2e_loop_identity_rejects_lineage_mutation():
    identity = create_e2e_loop_identity(
        chatgpt_request="execute governed validation",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()
    identity["request_sha256"] = "mutated"

    validation = validate_e2e_loop_identity(identity, chatgpt_request="execute governed validation")

    assert validation["valid"] is False
    assert any(error["field"] == "request_sha256" for error in validation["errors"])
