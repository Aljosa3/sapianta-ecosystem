from sapianta_bridge.no_copy_paste_loop.loop_request import create_loop_request, validate_loop_request


def test_loop_request_is_deterministic() -> None:
    first = create_loop_request("Inspect governance evidence").to_dict()
    second = create_loop_request("Inspect governance evidence").to_dict()

    assert first["loop_request_id"] == second["loop_request_id"]
    assert first["semantic_request_id"].startswith("SEM-")
    assert first["replay_identity"].startswith("REPLAY-")
    assert validate_loop_request(first)["valid"] is True


def test_loop_request_preserves_governance_boundaries() -> None:
    request = create_loop_request("Inspect governance evidence").to_dict()

    assert request["chatgpt_is_governance"] is False
    assert request["natural_language_is_execution_authority"] is False
    assert request["proposal_is_execution"] is False
    assert request["provider_is_governance"] is False
    assert request["loop_is_orchestration"] is False


def test_loop_request_rejects_hidden_execution_authority() -> None:
    request = create_loop_request("Inspect governance evidence").to_dict()
    request["retry_requested"] = True

    assert validate_loop_request(request)["valid"] is False
