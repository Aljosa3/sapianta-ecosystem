"""Deterministic bounded semantic contract synthesis.

The semantic contract is input to governance, not execution authority. This
module performs no LLM calls, provider calls, IO, dispatch, approval, or
orchestration.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

SEMANTIC_CONTRACT_VERSION = "v1"
SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY = "SEMANTIC_ONLY_NON_EXECUTION_AUTHORITY"
SEMANTIC_CONTRACT_SOURCE = "LOCAL_DETERMINISTIC_SEMANTIC_SYNTHESIS"

REQUIRED_SEMANTIC_CONTRACT_FIELDS = (
    "human_request",
    "semantic_intent",
    "requested_operation",
    "allowed_scope",
    "expected_artifacts",
    "expected_tests",
    "forbidden_operations",
    "completion_requirements",
    "ambiguities",
    "authority_boundary",
    "semantic_source",
    "contract_version",
    "contract_id",
    "artifact_hash",
    "provenance",
)

FORBIDDEN_AUTHORITY_TERMS = (
    "AUTO_EXECUTE",
    "AUTONOMOUS",
    "ORCHESTRATION",
    "APPROVAL_GRANTED",
    "EXECUTION_APPROVED",
    "DISPATCH_NOW",
    "PROVIDER_ROUTING",
)


def _contract_hash_input(contract: dict) -> dict:
    contract_copy = deepcopy(contract)
    contract_copy.pop("artifact_hash", None)
    return contract_copy


def _contract_hash(contract: dict) -> str:
    return canonical_hash(_contract_hash_input(contract))


def _normalize_request(human_request: str) -> str:
    request_text = str(human_request or "").strip()
    if not request_text:
        raise ValueError("human_request is required")
    return request_text


def _requested_operation(request_text: str) -> str:
    lowered = request_text.lower()
    if lowered.startswith(("implement ", "add ", "create ", "build ")):
        return "IMPLEMENT_BOUNDED_CHANGE"
    if lowered.startswith(("review ", "inspect ", "audit ")):
        return "REVIEW_BOUNDED_CHANGE"
    if "test" in lowered or "validate" in lowered:
        return "VALIDATE_BOUNDED_CHANGE"
    return "REVIEW_AND_SYNTHESIZE_BOUNDED_CHANGE"


def _expected_artifacts(request_text: str) -> list[str]:
    lowered = request_text.lower()
    artifacts = ["governed implementation summary"]
    if any(token in lowered for token in ("implement", "add", "create", "build", "fix")):
        artifacts.append("bounded code changes if required by governed task")
    if "doc" in lowered or "adr" in lowered or "report" in lowered:
        artifacts.append("governance documentation artifact if required by governed task")
    return artifacts


def _expected_tests(request_text: str) -> list[str]:
    lowered = request_text.lower()
    tests = ["targeted validation for touched surface"]
    if "browser" in lowered or "sidepanel" in lowered:
        tests.append("browser companion sidepanel tests")
    if "codex" in lowered or "runtime" in lowered or "bridge" in lowered:
        tests.append("governed bridge/runtime tests")
    return tests


def _ambiguities(request_text: str) -> list[str]:
    lowered = request_text.lower()
    ambiguities: list[str] = []
    if any(token in lowered for token in ("maybe", "possibly", "if needed", "whatever")):
        ambiguities.append("REQUEST_CONTAINS_OPEN_ENDED_LANGUAGE")
    if any(token in lowered for token in ("execute", "deploy", "publish", "release")):
        ambiguities.append("REQUEST_CONTAINS_EXECUTION_LIKE_LANGUAGE_REQUIRING_GOVERNANCE_GATE")
    if not ambiguities:
        ambiguities.append("NO_BLOCKING_AMBIGUITY_DETECTED")
    return ambiguities


def synthesize_semantic_contract(*, human_request: str, proposal: dict | None = None) -> dict:
    """Create a deterministic semantic contract for governance mediation."""

    request_text = _normalize_request(human_request)
    proposal_copy = deepcopy(proposal or {})
    semantic_intent = str(proposal_copy.get("semantic_intent") or f"Govern bounded semantic direction for: {request_text}")
    seed = {
        "human_request": request_text,
        "semantic_intent": semantic_intent,
        "contract_version": SEMANTIC_CONTRACT_VERSION,
    }
    contract = {
        "human_request": request_text,
        "semantic_intent": semantic_intent,
        "requested_operation": _requested_operation(request_text),
        "allowed_scope": "CURRENT_OPERATOR_SELECTED_WORKSPACE_ONLY",
        "expected_artifacts": _expected_artifacts(request_text),
        "expected_tests": _expected_tests(request_text),
        "forbidden_operations": [
            "approval automation",
            "provider routing",
            "orchestration",
            "autonomous continuation",
            "hidden execution",
            "durable persistence expansion",
            "semantic auto-dispatch",
        ],
        "completion_requirements": [
            "preserve governance mediation",
            "preserve authority separation",
            "return concise result summary",
            "report files changed, commands run, tests, errors, and residual risk",
            "end provider output with AIGOL_CODEX_TASK_COMPLETE",
        ],
        "ambiguities": _ambiguities(request_text),
        "authority_boundary": SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY,
        "semantic_source": SEMANTIC_CONTRACT_SOURCE,
        "contract_version": SEMANTIC_CONTRACT_VERSION,
        "contract_id": f"SEMANTIC-CONTRACT-{canonical_hash(seed)[7:31]}",
        "provenance": {
            "semantic_cognition": "bounded deterministic synthesis",
            "chatgpt_api_invoked": False,
            "execution_authority": False,
            "governance_mediated": True,
            "replayable": True,
        },
    }
    contract["artifact_hash"] = _contract_hash(contract)
    return contract


def validate_semantic_contract(contract: Any) -> dict:
    """Validate semantic contract shape and authority boundaries fail-closed."""

    if not isinstance(contract, dict) or isinstance(contract, list):
        return {"valid": False, "errors": [{"field": "semantic_contract", "error": "contract must be a JSON object"}]}
    errors: list[dict[str, str]] = []
    for field in REQUIRED_SEMANTIC_CONTRACT_FIELDS:
        if field not in contract:
            errors.append({"field": field, "error": "required field missing"})
    if errors:
        return {"valid": False, "errors": errors}
    string_fields = (
        "human_request",
        "semantic_intent",
        "requested_operation",
        "allowed_scope",
        "authority_boundary",
        "semantic_source",
        "contract_version",
        "contract_id",
        "artifact_hash",
    )
    for field in string_fields:
        if not isinstance(contract.get(field), str) or not contract[field].strip():
            errors.append({"field": field, "error": "expected non-empty str"})
    list_fields = ("expected_artifacts", "expected_tests", "forbidden_operations", "completion_requirements", "ambiguities")
    for field in list_fields:
        if not isinstance(contract.get(field), list):
            errors.append({"field": field, "error": "expected list"})
    if not isinstance(contract.get("provenance"), dict):
        errors.append({"field": "provenance", "error": "expected dict"})
    if contract.get("authority_boundary") != SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY:
        errors.append({"field": "authority_boundary", "error": "semantic contract must remain non-execution authority"})
    if contract.get("contract_version") != SEMANTIC_CONTRACT_VERSION:
        errors.append({"field": "contract_version", "error": "unsupported semantic contract version"})
    if isinstance(contract.get("provenance"), dict):
        provenance = contract["provenance"]
        if provenance.get("execution_authority") is not False:
            errors.append({"field": "provenance.execution_authority", "error": "execution authority is forbidden"})
        if provenance.get("governance_mediated") is not True:
            errors.append({"field": "provenance.governance_mediated", "error": "governance mediation is required"})
    computed_hash = _contract_hash(contract)
    if contract.get("artifact_hash") != computed_hash:
        errors.append({"field": "artifact_hash", "error": "semantic contract hash mismatch"})
    canonical_text = " ".join(
        str(contract.get(field, ""))
        for field in ("requested_operation", "authority_boundary", "semantic_source")
    ).upper()
    for token in FORBIDDEN_AUTHORITY_TERMS:
        if token in canonical_text:
            errors.append({"field": "semantic_contract", "error": f"forbidden authority token: {token}"})
    return {"valid": not errors, "errors": errors, "computed_hash": computed_hash}


__all__ = [
    "SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY",
    "SEMANTIC_CONTRACT_VERSION",
    "synthesize_semantic_contract",
    "validate_semantic_contract",
]
