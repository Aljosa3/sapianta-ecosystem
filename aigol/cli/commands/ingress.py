"""Ingress command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from agol_bridge.chatgpt_ingress import generate_valid_chatgpt_ingress_artifact


def generate_ingress_artifact(*, human_request: str, semantic_intent: str) -> dict:
    return generate_valid_chatgpt_ingress_artifact(
        human_request=human_request,
        semantic_intent=semantic_intent,
    )


__all__ = ["generate_ingress_artifact"]

