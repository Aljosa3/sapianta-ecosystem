"""Text-only deterministic runtime reports."""

from __future__ import annotations


def render_runtime_report(summary: dict) -> str:
    return "\n".join(
        [
            f"runtime_id: {summary['runtime_id']}",
            f"goal_state: {summary['goal_state']}",
            f"approval_state: {summary['approval_state']}",
            f"routing_state: {summary['routing_state']}",
            f"retry_state: {summary['retry_state']}",
            f"continuity_state: {summary['continuity_state']}",
            f"replay_integrity_state: {summary['replay_integrity_state']}",
            f"replay_hash: {summary['replay_hash']}",
        ]
    )


def render_goal_report(summary: dict) -> str:
    return "\n".join(
        [
            f"goal_id: {summary['goal_id']}",
            f"runtime_id: {summary['runtime_id']}",
            f"goal_state: {summary['goal_state']}",
            f"step_count: {summary['step_count']}",
            f"max_step_limit: {summary['max_step_limit']}",
            f"replay_integrity_state: {summary['replay_integrity_state']}",
            f"replay_hash: {summary['replay_hash']}",
        ]
    )


def render_retry_report(summary: dict) -> str:
    return "\n".join(
        [
            f"runtime_id: {summary['runtime_id']}",
            f"retry_state: {summary['retry_state']}",
            f"retry_count: {summary['retry_count']}",
            f"retry_scope: {summary['retry_scope']}",
            f"bounded_local_only: {summary['bounded_local_only']}",
            f"replay_integrity_state: {summary['replay_integrity_state']}",
            f"replay_hash: {summary['replay_hash']}",
        ]
    )
