from sapianta_bridge.chatgpt_ingress.ingress_session import (
    create_ingress_session,
    validate_ingress_session,
)


def test_ingress_session_identity_is_deterministic() -> None:
    first = create_ingress_session(raw_text="Inspect governance", timestamp="2026-05-14T00:00:00Z")
    second = create_ingress_session(raw_text="Inspect governance", timestamp="2026-05-14T00:00:00Z")

    assert first == second
    assert first.session_id.startswith("INGRESS-SESSION-")
    assert first.request_id.startswith("INGRESS-REQUEST-")
    assert validate_ingress_session(first)["valid"] is True


def test_ingress_session_has_no_mutable_memory_or_governance_authority() -> None:
    session = create_ingress_session(raw_text="Inspect governance").to_dict()

    assert session["mutable_memory"] is False
    assert session["chatgpt_governance_authority"] is False


def test_ingress_session_replay_binding_mismatch_fails_closed() -> None:
    session = create_ingress_session(raw_text="Inspect governance").to_dict()
    session["replay_binding"] = "bad"

    result = validate_ingress_session(session)

    assert result["valid"] is False
    assert {"field": "replay_binding", "reason": "session replay binding mismatch"} in result["errors"]
