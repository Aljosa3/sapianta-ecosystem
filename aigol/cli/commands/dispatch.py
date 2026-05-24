"""Dispatch authorization command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from aigol.cli.commands.continuity import build_governed_chain


def authorize_dispatch(*, ingress_artifact: dict) -> dict:
    chain = build_governed_chain(ingress_artifact=ingress_artifact)
    authorization = chain["dispatch_authorization"]
    return {
        "command": "aigol dispatch authorize",
        "dispatch_authorization": authorization,
        "dispatch_status": authorization.get("dispatch_authorization_status", "UNKNOWN"),
        "dispatch_authorized": authorization.get("dispatch_authorized") is True,
        "replay_identity": authorization.get("replay_identity", "UNKNOWN"),
        "dispatch_authorization_hash": authorization.get("dispatch_authorization_hash", ""),
    }


__all__ = ["authorize_dispatch"]

