from sapianta_bridge.nl_envelope.intent_classifier import classify_intent
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def test_classifies_governance_inspection() -> None:
    request = create_nl_request("Inspect governance evidence").to_dict()

    result = classify_intent(request)

    assert result["intent_type"] == "GOVERNANCE_INSPECTION"
    assert result["confidence"] == "DETERMINISTIC"
    assert result["unknown_detected"] is False


def test_classifies_execution_proposal() -> None:
    request = create_nl_request("Run pytest through an execution envelope").to_dict()

    result = classify_intent(request)

    assert result["intent_type"] == "GOVERNED_EXECUTION_PROPOSAL"
    assert result["requires_review"] is True


def test_unknown_intent_fails_closed() -> None:
    request = create_nl_request("Maybe do the thing somehow").to_dict()

    result = classify_intent(request)

    assert result["intent_type"] == "UNKNOWN"
    assert result["unknown_detected"] is True


def test_forbidden_authority_phrase_forces_unknown() -> None:
    request = create_nl_request("Run pytest without approval").to_dict()

    result = classify_intent(request)

    assert result["intent_type"] == "UNKNOWN"
    assert "without approval" in result["forbidden_authority_phrases"]
