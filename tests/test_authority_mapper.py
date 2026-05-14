from sapianta_bridge.nl_envelope.admissibility_evaluator import evaluate_admissibility
from sapianta_bridge.nl_envelope.authority_mapper import map_authority_scope
from sapianta_bridge.nl_envelope.intent_classifier import classify_intent
from sapianta_bridge.nl_envelope.nl_request import create_nl_request


def _map(text: str) -> dict:
    request = create_nl_request(text).to_dict()
    classification = classify_intent(request)
    admissibility = evaluate_admissibility(request, classification)
    return map_authority_scope(classification, admissibility)


def test_inspection_maps_to_read_only() -> None:
    result = _map("Inspect governance evidence")

    assert result["authority_mapping_valid"] is True
    assert result["authority_scope"] == [
        "READ_ONLY",
        "NO_NETWORK",
        "NO_RUNTIME_EXECUTION",
        "NO_PRIVILEGE_ESCALATION",
    ]


def test_refinement_maps_to_bounded_patch_proposal() -> None:
    result = _map("Refine sapianta_bridge documentation")

    assert result["authority_mapping_valid"] is True
    assert "PATCH_EXISTING_FILES" in result["authority_scope"]
    assert result["execution_authority_granted"] is False


def test_rejected_intent_blocks_authority_mapping() -> None:
    result = _map("Run unrestricted shell")

    assert result["authority_mapping_valid"] is False
    assert result["authority_scope"] == []
