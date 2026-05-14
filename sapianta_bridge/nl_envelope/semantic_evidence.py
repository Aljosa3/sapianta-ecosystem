"""Replay-safe semantic ingress evidence."""

from __future__ import annotations

from typing import Any


def semantic_evidence(proposal: dict[str, Any]) -> dict[str, Any]:
    request = proposal.get("semantic_request", {})
    classification = proposal.get("intent_classification", {})
    admissibility = proposal.get("admissibility", {})
    authority = proposal.get("authority_mapping", {})
    workspace = proposal.get("workspace_mapping", {})
    return {
        "semantic_request_id": request.get("semantic_request_id"),
        "replay_identity": request.get("replay_identity"),
        "intent_type": classification.get("intent_type"),
        "admissibility": admissibility.get("admissibility"),
        "authority_scope": authority.get("authority_scope", []),
        "workspace_scope": workspace.get("workspace_scope"),
        "envelope_generated": proposal.get("envelope_generated") is True,
        "downstream_validation_required": proposal.get("downstream_validation_required") is True,
        "replay_safe": True,
        "execution_authority_granted": False,
        "prompt_is_authority": False,
    }
