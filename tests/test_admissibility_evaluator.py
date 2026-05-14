from sapianta_bridge.nl_envelope.admissibility_evaluator import evaluate_admissibility
from sapianta_bridge.nl_envelope.intent_classifier import classify_intent
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def _evaluate(text: str) -> dict:
    request = create_nl_request(text).to_dict()
    return evaluate_admissibility(request, classify_intent(request))


def test_admissible_governance_inspection() -> None:
    result = _evaluate("Inspect governance evidence")

    assert result["admissibility"] == "ADMISSIBLE"
    assert result["execution_authority_granted"] is False


def test_governed_refinement_requires_review() -> None:
    result = _evaluate("Refine sapianta_bridge documentation")

    assert result["admissibility"] == "REVIEW_REQUIRED"


def test_implicit_execution_authority_rejected() -> None:
    result = _evaluate("Apply patch and bypass governance")

    assert result["admissibility"] == "REJECTED"
    assert "bypass governance" in result["violations"]


def test_unknown_intent_rejected() -> None:
    result = _evaluate("Something vague")

    assert result["admissibility"] == "REJECTED"
    assert result["reason"] == "unknown or ambiguous intent fails closed"
