"""Governance validation command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from agol_bridge.chatgpt_ingress.chatgpt_ingress_validator import validate_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview


def validate_governance_continuity(*, ingress_artifact: dict) -> dict:
    validation = validate_chatgpt_ingress_artifact(ingress_artifact)
    preview = create_governed_task_package_preview(ingress_artifact) if validation.get("valid") is True else {}
    return {
        "command": "aigol governance validate",
        "validation": validation,
        "task_package_preview": preview,
        "governance_status": "PASS" if validation.get("valid") is True and preview.get("governance_status") == "READY_FOR_HUMAN_APPROVAL" else "FAIL_CLOSED",
        "replay_identity": validation.get("replay_identity", ingress_artifact.get("replay_identity", "UNKNOWN") if isinstance(ingress_artifact, dict) else "UNKNOWN"),
        "hash_continuity": {
            "artifact_hash": validation.get("artifact_hash", ""),
            "preview_hash": preview.get("preview_hash", ""),
        },
    }


__all__ = ["validate_governance_continuity"]

