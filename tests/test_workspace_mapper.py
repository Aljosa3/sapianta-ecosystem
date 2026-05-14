from sapianta_bridge.nl_envelope.admissibility_evaluator import evaluate_admissibility
from sapianta_bridge.nl_envelope.intent_classifier import classify_intent
from sapianta_bridge.nl_envelope.nl_request import create_nl_request
from sapianta_bridge.nl_envelope.workspace_mapper import map_workspace_scope


def _map(text: str) -> dict:
    request = create_nl_request(text).to_dict()
    classification = classify_intent(request)
    admissibility = evaluate_admissibility(request, classification)
    return map_workspace_scope(request, classification, admissibility)


def test_workspace_mapping_uses_explicit_hint() -> None:
    result = _map("Inspect `.github/governance` evidence")

    assert result["workspace_mapping_valid"] is True
    assert result["workspace_scope"]["allowed_roots"] == [".github/governance"]


def test_workspace_mapping_uses_least_privilege_default() -> None:
    result = _map("Refine bridge documentation")

    assert result["workspace_mapping_valid"] is True
    assert result["workspace_scope"]["allowed_roots"] == ["sapianta_bridge"]


def test_rejected_request_blocks_workspace_mapping() -> None:
    result = _map("Run unrestricted shell")

    assert result["workspace_mapping_valid"] is False
    assert result["workspace_scope"] is None
