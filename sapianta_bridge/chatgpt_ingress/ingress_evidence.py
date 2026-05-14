"""Replay-safe ChatGPT ingress evidence."""

from __future__ import annotations

from typing import Any


def ingress_evidence(
    *,
    session: dict[str, Any],
    request: dict[str, Any],
    proposal: dict[str, Any],
    binding: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "session_id": session.get("session_id"),
        "request_id": session.get("request_id"),
        "semantic_request_id": proposal.get("semantic_request", {}).get("semantic_request_id"),
        "replay_identity": proposal.get("semantic_request", {}).get("replay_identity"),
        "ingress_binding_sha256": binding.get("ingress_binding_sha256"),
        "intent_type": proposal.get("intent_classification", {}).get("intent_type"),
        "admissibility": proposal.get("admissibility", {}).get("admissibility"),
        "authority_scope": proposal.get("authority_mapping", {}).get("authority_scope", []),
        "workspace_scope": proposal.get("workspace_mapping", {}).get("workspace_scope"),
        "envelope_id": binding.get("envelope_id"),
        "proposal_generated": proposal.get("envelope_generated") is True,
        "ingress_valid": validation.get("valid") is True,
        "replay_safe": True,
        "chatgpt_governance_authority": False,
        "execution_authority_granted": False,
        "provider_invoked": False,
        "transport_executed": False,
        "runtime_executed": False,
    }
