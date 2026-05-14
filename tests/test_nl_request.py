from sapianta_bridge.nl_envelope.nl_request import create_nl_request, validate_nl_request


def test_nl_request_preserves_raw_text_and_replay_identity() -> None:
    request = create_nl_request("Inspect governance evidence in `.github/governance`")
    value = request.to_dict()

    assert value["raw_text"] == "Inspect governance evidence in `.github/governance`"
    assert value["semantic_request_id"].startswith("SEM-")
    assert value["replay_identity"].startswith("REPLAY-")
    assert value["execution_authority_granted"] is False
    assert value["prompt_is_authority"] is False
    assert validate_nl_request(value)["valid"] is True


def test_nl_request_rejects_authority_flag() -> None:
    request = create_nl_request("Run tests").to_dict()
    request["execution_authority_granted"] = True

    result = validate_nl_request(request)

    assert result["valid"] is False
    assert {"field": "execution_authority_granted", "reason": "natural language cannot grant authority"} in result["errors"]


def test_nl_request_hash_mismatch_fails_closed() -> None:
    request = create_nl_request("Run tests").to_dict()
    request["raw_text_sha256"] = "bad"

    result = validate_nl_request(request)

    assert result["valid"] is False
    assert {"field": "raw_text_sha256", "reason": "raw text hash mismatch"} in result["errors"]
