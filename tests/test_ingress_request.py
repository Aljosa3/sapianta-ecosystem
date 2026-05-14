from sapianta_bridge.chatgpt_ingress.ingress_request import (
    create_ingress_request,
    validate_ingress_request,
)
from sapianta_bridge.chatgpt_ingress.ingress_session import create_ingress_session


def test_ingress_request_preserves_original_and_normalized_text() -> None:
    session = create_ingress_session(raw_text="Inspect   governance").to_dict()
    request = create_ingress_request(session=session, raw_text="Inspect   governance").to_dict()

    assert request["original_natural_language"] == "Inspect   governance"
    assert request["normalized_request"] == "Inspect governance"
    assert request["hidden_prompt_rewrite"] is False
    assert request["execution_authority_granted"] is False
    assert validate_ingress_request(request)["valid"] is True


def test_ingress_request_rejects_hidden_prompt_rewrite() -> None:
    session = create_ingress_session(raw_text="Inspect governance").to_dict()
    request = create_ingress_request(session=session, raw_text="Inspect governance").to_dict()
    request["hidden_prompt_rewrite"] = True

    result = validate_ingress_request(request)

    assert result["valid"] is False
    assert {"field": "hidden_prompt_rewrite", "reason": "hidden prompt rewriting is forbidden"} in result["errors"]


def test_ingress_request_rejects_execution_authority() -> None:
    session = create_ingress_session(raw_text="Inspect governance").to_dict()
    request = create_ingress_request(session=session, raw_text="Inspect governance").to_dict()
    request["execution_authority_granted"] = True

    result = validate_ingress_request(request)

    assert result["valid"] is False
    assert {"field": "execution_authority_granted", "reason": "ingress cannot grant execution authority"} in result["errors"]
