"""Interactive ACLI Next session loop over the bootstrap runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.entrypoint import run_acli_next_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_INTERACTIVE_VERSION = "G8_04_ACLI_NEXT_INTERACTIVE_SESSION_IMPLEMENTATION_V1"
INTERACTIVE_COMMAND_NAME = "aigol next interactive"

ACLI_NEXT_INTERACTIVE_STARTED = "ACLI_NEXT_INTERACTIVE_STARTED"
ACLI_NEXT_INTERACTIVE_TURN_RECORDED = "ACLI_NEXT_INTERACTIVE_TURN_RECORDED"
ACLI_NEXT_INTERACTIVE_COMPLETED = "ACLI_NEXT_INTERACTIVE_COMPLETED"

CONTINUABLE_RESPONSE_CLASSES = {
    "CLARIFICATION",
    "MODIFICATION",
    "CONTINUATION",
}
TERMINAL_RESPONSE_CLASSES = {
    "CONFIRMATION",
    "REJECTION",
}


def run_acli_next_interactive_session(
    *,
    session_id: str,
    turns: list[dict[str, str]],
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run a replay-visible multi-turn ACLI Next session."""

    replay_path = Path(replay_dir)
    normalized_turns = _require_turns(turns)
    start = _interactive_start_artifact(
        session_id=session_id,
        turn_count=len(normalized_turns),
        created_at=created_at,
        workspace=workspace,
    )
    _persist(replay_path, "000_acli_next_interactive_started.json", start)

    recorded_turns: list[dict[str, Any]] = []
    prior_response_class: str | None = None
    for index, turn in enumerate(normalized_turns, start=1):
        if index > 1 and prior_response_class not in CONTINUABLE_RESPONSE_CLASSES:
            raise FailClosedRuntimeError(
                "ACLI Next interactive continuation failed closed: prior turn is terminal"
            )
        turn_id = f"TURN-{index:06d}"
        bootstrap = run_acli_next_session(
            session_id=f"{session_id}:{turn_id}",
            operator_request=turn["operator_request"],
            operator_response=turn["operator_response"],
            created_at=created_at,
            replay_dir=replay_path / "turns" / turn_id,
            workspace=workspace,
        )
        turn_record = _turn_record_artifact(
            session_id=session_id,
            turn_index=index,
            turn_id=turn_id,
            bootstrap_result=bootstrap,
            previous_response_class=prior_response_class,
            created_at=created_at,
        )
        _persist(replay_path, f"{index:03d}_acli_next_turn_recorded.json", turn_record)
        recorded_turns.append(turn_record)
        prior_response_class = turn_record["canonical_response_class"]

    completion = _completion_artifact(
        session_id=session_id,
        start=start,
        turns=recorded_turns,
        replay_path=replay_path,
        created_at=created_at,
    )
    _persist(
        replay_path,
        f"{len(recorded_turns) + 1:03d}_acli_next_interactive_completed.json",
        completion,
    )
    return _result(completion)


def render_acli_next_interactive_summary(result: dict[str, Any]) -> str:
    """Render an interactive ACLI Next session summary."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"session_status: {result.get('session_status')}",
            f"turn_count: {result.get('turn_count')}",
            f"final_response_class: {result.get('final_response_class')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"approval_created: {result.get('approval_created')}",
            f"authorization_created: {result.get('authorization_created')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
            f"copy_paste_workflow_used: {result.get('copy_paste_workflow_used')}",
        ]
    )


def _interactive_start_artifact(
    *,
    session_id: str,
    turn_count: int,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_INTERACTIVE_SESSION_STARTED_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_INTERACTIVE_VERSION,
        "command": INTERACTIVE_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "declared_turn_count": turn_count,
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "session_status": ACLI_NEXT_INTERACTIVE_STARTED,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _turn_record_artifact(
    *,
    session_id: str,
    turn_index: int,
    turn_id: str,
    bootstrap_result: dict[str, Any],
    previous_response_class: str | None,
    created_at: str,
) -> dict[str, Any]:
    _require_non_mutating(bootstrap_result)
    response_class = _require_string(
        bootstrap_result.get("canonical_response_class"), "canonical_response_class"
    )
    artifact = {
        "artifact_type": "ACLI_NEXT_INTERACTIVE_TURN_RECORDED_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_INTERACTIVE_VERSION,
        "command": INTERACTIVE_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "turn_id": turn_id,
        "turn_index": turn_index,
        "previous_response_class": previous_response_class,
        "canonical_response_class": response_class,
        "turn_replay_reference": bootstrap_result.get("replay_reference"),
        "pgsp_replay_reference": bootstrap_result.get("pgsp_replay_reference"),
        "turn_result_hash": bootstrap_result.get("replay_hash"),
        "created_at": _require_string(created_at, "created_at"),
        "session_status": ACLI_NEXT_INTERACTIVE_TURN_RECORDED,
        "continuation_allowed": response_class in CONTINUABLE_RESPONSE_CLASSES,
        "terminal_turn": response_class in TERMINAL_RESPONSE_CLASSES,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _completion_artifact(
    *,
    session_id: str,
    start: dict[str, Any],
    turns: list[dict[str, Any]],
    replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    if not turns:
        raise FailClosedRuntimeError("ACLI Next interactive session requires at least one turn")
    final_response_class = turns[-1]["canonical_response_class"]
    artifact = {
        "artifact_type": "ACLI_NEXT_INTERACTIVE_COMPLETION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_INTERACTIVE_VERSION,
        "command": INTERACTIVE_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "session_start_hash": start["artifact_hash"],
        "turn_hashes": [turn["artifact_hash"] for turn in turns],
        "turn_count": len(turns),
        "final_response_class": final_response_class,
        "session_status": ACLI_NEXT_INTERACTIVE_COMPLETED,
        "replay_reference": str(replay_path),
        "created_at": _require_string(created_at, "created_at"),
        "turns": deepcopy(turns),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "fail_closed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result(completion: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(completion)
    result["replay_hash"] = completion["artifact_hash"]
    return result


def _persist(replay_path: Path, name: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / name, artifact)


def _require_turns(turns: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(turns, list) or not turns:
        raise FailClosedRuntimeError("ACLI Next interactive session requires turns")
    normalized: list[dict[str, str]] = []
    for index, turn in enumerate(turns, start=1):
        if not isinstance(turn, dict):
            raise FailClosedRuntimeError(f"ACLI Next turn {index} must be a mapping")
        normalized.append(
            {
                "operator_request": _require_string(turn.get("operator_request"), "operator_request"),
                "operator_response": _require_string(turn.get("operator_response"), "operator_response"),
            }
        )
    return normalized


def _require_non_mutating(result: dict[str, Any]) -> None:
    for key in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if result.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next interactive failed closed: {key} was not false")
    if not result.get("replay_reference"):
        raise FailClosedRuntimeError("ACLI Next interactive failed closed: turn replay reference missing")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next interactive requires {field}")
    return value
