"""Fail-closed validation for ChatGPT ingress state."""

from __future__ import annotations

from typing import Any

from .ingress_binding import validate_ingress_binding
from .ingress_request import validate_ingress_request
from .ingress_session import validate_ingress_session


def validate_ingress_state(
    *,
    session: dict[str, Any],
    request: dict[str, Any],
    proposal: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    session_result = validate_ingress_session(session)
    request_result = validate_ingress_request(request)
    binding_result = validate_ingress_binding(binding)
    if not session_result["valid"]:
        errors.append({"field": "session", "reason": "invalid ingress session"})
    if not request_result["valid"]:
        errors.append({"field": "request", "reason": "invalid ingress request"})
    if not binding_result["valid"]:
        errors.append({"field": "binding", "reason": "invalid ingress binding"})
    admissibility = proposal.get("admissibility", {})
    authority = proposal.get("authority_mapping", {})
    workspace = proposal.get("workspace_mapping", {})
    if not admissibility.get("admissibility"):
        errors.append({"field": "admissibility", "reason": "admissibility missing"})
    if admissibility.get("admissibility") == "REJECTED" and proposal.get("envelope_generated") is True:
        errors.append({"field": "admissibility", "reason": "rejected ingress cannot generate envelope"})
    if proposal.get("envelope_generated") is True:
        if not authority.get("authority_scope"):
            errors.append({"field": "authority_scope", "reason": "authority scope missing"})
        if not workspace.get("workspace_scope"):
            errors.append({"field": "workspace_scope", "reason": "workspace scope missing"})
        envelope = proposal.get("execution_envelope", {})
        if envelope.get("envelope_id") != binding.get("envelope_id"):
            errors.append({"field": "envelope_id", "reason": "proposal/binding envelope mismatch"})
    if proposal.get("execution_authority_granted") is not False:
        errors.append({"field": "execution_authority_granted", "reason": "ingress cannot grant authority"})
    return {
        "valid": not errors,
        "errors": errors,
        "ingress_allowed": not errors,
        "chatgpt_is_governance": False,
        "ingress_is_execution_authority": False,
    }
