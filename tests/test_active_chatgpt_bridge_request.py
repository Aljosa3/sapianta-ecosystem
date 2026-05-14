from sapianta_bridge.active_chatgpt_bridge.bridge_request import create_bridge_request, validate_bridge_request


def test_active_chatgpt_bridge_request_is_deterministic() -> None:
    first = create_bridge_request("Inspect governance evidence", requested_provider_id="deterministic_mock").to_dict()
    second = create_bridge_request("Inspect governance evidence", requested_provider_id="deterministic_mock").to_dict()

    assert first["bridge_request_id"] == second["bridge_request_id"]
    assert first["ingress_session_identity"]
    assert first["semantic_request_identity"].startswith("SEM-")
    assert validate_bridge_request(first)["valid"] is True


def test_active_chatgpt_bridge_request_contains_no_execution_authority() -> None:
    request = create_bridge_request("Inspect governance evidence").to_dict()

    assert request["execution_authority_granted"] is False
    assert request["hidden_plan_present"] is False
    assert request["hidden_memory_present"] is False
    assert request["retry_instructions_present"] is False
    assert request["routing_instructions_present"] is False


def test_active_chatgpt_bridge_request_rejects_hidden_authority() -> None:
    request = create_bridge_request("Inspect governance evidence").to_dict()
    request["execution_authority_granted"] = True

    assert validate_bridge_request(request)["valid"] is False
