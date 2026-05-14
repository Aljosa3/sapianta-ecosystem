"""Generate bounded execution envelope proposals from semantic ingress."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.execution_envelope import ExecutionEnvelope
from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope

from .admissibility_evaluator import evaluate_admissibility
from .authority_mapper import map_authority_scope
from .intent_classifier import classify_intent
from .nl_request import NaturalLanguageRequest, validate_nl_request
from .workspace_mapper import map_workspace_scope


def _actions_for_intent(intent_type: str) -> tuple[list[str], list[str]]:
    allowed = {
        "GOVERNANCE_INSPECTION": ["inspect"],
        "CREATIVE_GENERATION": ["create_artifact_proposal"],
        "GOVERNED_REFINEMENT": ["propose_patch"],
        "GOVERNED_EXECUTION_PROPOSAL": ["propose_test_execution"],
    }.get(intent_type, [])
    forbidden = ["direct_execution", "provider_api_call", "bypass_governance", "self_authorize"]
    return allowed, forbidden


def generate_envelope_proposal(
    request: NaturalLanguageRequest | dict[str, Any],
    *,
    provider_id: str = "deterministic_mock",
) -> dict[str, Any]:
    request_value = request.to_dict() if isinstance(request, NaturalLanguageRequest) else request
    request_validation = validate_nl_request(request_value)
    if not request_validation["valid"]:
        return {
            "envelope_generated": False,
            "errors": request_validation["errors"],
            "execution_authority_granted": False,
        }
    classification = classify_intent(request_value)
    admissibility = evaluate_admissibility(request_value, classification)
    authority = map_authority_scope(classification, admissibility)
    workspace = map_workspace_scope(request_value, classification, admissibility)
    if not authority["authority_mapping_valid"] or not workspace["workspace_mapping_valid"]:
        return {
            "envelope_generated": False,
            "semantic_request": request_value,
            "intent_classification": classification,
            "admissibility": admissibility,
            "authority_mapping": authority,
            "workspace_mapping": workspace,
            "execution_authority_granted": False,
        }
    allowed_actions, forbidden_actions = _actions_for_intent(classification["intent_type"])
    envelope = ExecutionEnvelope(
        envelope_id=f"ENV-{request_value['semantic_request_id']}",
        provider_id=provider_id,
        workspace_scope=workspace["workspace_scope"],
        authority_scope=tuple(authority["authority_scope"]),
        allowed_actions=tuple(allowed_actions),
        forbidden_actions=tuple(sorted(forbidden_actions)),
        timeout_seconds=300,
        replay_identity=request_value["replay_identity"],
        validation_requirements=("pytest", "py_compile", "git_diff_check"),
        human_approval_required=admissibility["admissibility"] == "REVIEW_REQUIRED",
    ).to_dict()
    envelope_validation = validate_execution_envelope(envelope)
    return {
        "envelope_generated": envelope_validation["valid"],
        "semantic_request": request_value,
        "intent_classification": classification,
        "admissibility": admissibility,
        "authority_mapping": authority,
        "workspace_mapping": workspace,
        "execution_envelope": envelope if envelope_validation["valid"] else None,
        "envelope_validation": envelope_validation,
        "execution_authority_granted": False,
        "downstream_validation_required": True,
    }
