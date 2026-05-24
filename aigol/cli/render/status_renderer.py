"""Status rendering for deterministic AiGOL CLI output."""

from __future__ import annotations

from aigol.cli.render.terminal_cards import render_card


def render_status(summary: dict) -> str:
    return render_card(
        "AIGOL STATUS",
        [
            f"Ingress: {summary.get('ingress_status', 'UNKNOWN')}",
            f"Governance: {summary.get('governance_status', 'UNKNOWN')}",
            f"Continuity: {summary.get('continuity_status', 'UNKNOWN')}",
            f"Dispatch: {summary.get('dispatch_status', 'UNKNOWN')}",
            f"Execution: {summary.get('execution_status', 'UNKNOWN')}",
            f"Return: {summary.get('return_status', 'UNKNOWN')}",
            f"Provider: {summary.get('provider_status', 'UNKNOWN')}",
            f"Replay: {summary.get('replay_identity', 'UNKNOWN')}",
        ],
    )


__all__ = ["render_status"]
