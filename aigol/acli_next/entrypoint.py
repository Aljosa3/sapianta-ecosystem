"""Minimal ACLI Next bootstrap entrypoint over the certified PGSP lineage."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.g4_live_acli_governed_development_session_entrypoint import (
    run_g4_live_acli_governed_development_session_entrypoint,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_BOOTSTRAP_VERSION = "G8_03_ACLI_NEXT_BOOTSTRAP_IMPLEMENTATION_V1"
COMMAND_NAME = "aigol next session"

ACLI_NEXT_SESSION_CREATED = "ACLI_NEXT_SESSION_CREATED"
ACLI_NEXT_PGSP_INVOKED = "ACLI_NEXT_PGSP_INVOKED"
ACLI_NEXT_BOOTSTRAP_COMPLETED = "ACLI_NEXT_BOOTSTRAP_COMPLETED"


def run_acli_next_session(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Start a non-mutating ACLI Next session and delegate to existing PGSP runtime."""

    replay_path = Path(replay_dir)
    session = _session_bootstrap_artifact(
        session_id=session_id,
        operator_request=operator_request,
        operator_response=operator_response,
        created_at=created_at,
        workspace=workspace,
    )
    _persist(replay_path, "000_acli_next_session_created.json", session)

    pgsp_result = run_g4_live_acli_governed_development_session_entrypoint(
        session_id=f"{session['session_id']}:PGSP",
        operator_request=session["operator_request"],
        operator_response=session["operator_response"],
        created_at=session["created_at"],
        replay_dir=replay_path / "pgsp_session",
    )
    _require_pgsp_non_mutating(pgsp_result)

    pgsp_invocation = _pgsp_invocation_artifact(
        session=session,
        pgsp_result=pgsp_result,
        created_at=created_at,
    )
    _persist(replay_path, "001_pgsp_invocation_recorded.json", pgsp_invocation)

    completion = _completion_artifact(
        session=session,
        pgsp_invocation=pgsp_invocation,
        pgsp_result=pgsp_result,
        replay_path=replay_path,
        created_at=created_at,
    )
    _persist(replay_path, "002_acli_next_completion_recorded.json", completion)

    return _result(completion)


def render_acli_next_session_summary(result: dict[str, Any]) -> str:
    """Render ACLI Next bootstrap evidence without generating reusable communication."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"session_status: {result.get('session_status')}",
            f"pgsp_session_status: {result.get('pgsp_session_status')}",
            f"canonical_response_class: {result.get('canonical_response_class')}",
            f"governance_checkpoint_status: {result.get('governance_checkpoint_status')}",
            f"execution_intent_status: {result.get('execution_intent_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"pgsp_replay_reference: {result.get('pgsp_replay_reference')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"approval_created: {result.get('approval_created')}",
            f"authorization_created: {result.get('authorization_created')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
            f"copy_paste_workflow_used: {result.get('copy_paste_workflow_used')}",
        ]
    )


def _session_bootstrap_artifact(
    *,
    session_id: str,
    operator_request: str,
    operator_response: str,
    created_at: str,
    workspace: str | Path,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_SESSION_BOOTSTRAP_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_BOOTSTRAP_VERSION,
        "command": COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "turn_id": f"{_require_string(session_id, 'session_id')}:TURN-000001",
        "operator_request": _require_string(operator_request, "operator_request"),
        "operator_request_hash": replay_hash(operator_request),
        "operator_response": _require_string(operator_response, "operator_response"),
        "operator_response_hash": replay_hash(operator_response),
        "adapter_id": "ACLI_NEXT",
        "adapter_version": ACLI_NEXT_BOOTSTRAP_VERSION,
        "workspace": str(Path(workspace)),
        "created_at": _require_string(created_at, "created_at"),
        "semantic_translation_performed": False,
        "orchestration_performed": False,
        "governance_performed": False,
        "replay_logic_owned": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
        "session_status": ACLI_NEXT_SESSION_CREATED,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _pgsp_invocation_artifact(
    *,
    session: dict[str, Any],
    pgsp_result: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_PGSP_INVOCATION_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_BOOTSTRAP_VERSION,
        "command": COMMAND_NAME,
        "session_id": session["session_id"],
        "session_bootstrap_hash": session["artifact_hash"],
        "pgsp_entrypoint": "run_g4_live_acli_governed_development_session_entrypoint",
        "pgsp_session_id": pgsp_result.get("session_id"),
        "pgsp_session_status": pgsp_result.get("session_status"),
        "pgsp_replay_reference": pgsp_result.get("replay_reference"),
        "pgsp_replay_hash": pgsp_result.get("replay_hash"),
        "canonical_response_class": pgsp_result.get("canonical_response_class"),
        "governance_checkpoint_status": pgsp_result.get("governance_checkpoint_status"),
        "execution_intent_status": pgsp_result.get("execution_intent_status"),
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "copy_paste_workflow_used": False,
        "replay_visible": True,
        "session_status": ACLI_NEXT_PGSP_INVOKED,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _completion_artifact(
    *,
    session: dict[str, Any],
    pgsp_invocation: dict[str, Any],
    pgsp_result: dict[str, Any],
    replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "ACLI_NEXT_COMPLETION_SUMMARY_ARTIFACT_V1",
        "runtime_version": ACLI_NEXT_BOOTSTRAP_VERSION,
        "command": COMMAND_NAME,
        "session_id": session["session_id"],
        "turn_id": session["turn_id"],
        "session_bootstrap_hash": session["artifact_hash"],
        "pgsp_invocation_hash": pgsp_invocation["artifact_hash"],
        "session_status": ACLI_NEXT_BOOTSTRAP_COMPLETED,
        "pgsp_session_status": pgsp_invocation["pgsp_session_status"],
        "canonical_response_class": pgsp_invocation["canonical_response_class"],
        "governance_checkpoint_status": pgsp_invocation["governance_checkpoint_status"],
        "execution_intent_status": pgsp_invocation["execution_intent_status"],
        "replay_reference": str(replay_path),
        "pgsp_replay_reference": pgsp_invocation["pgsp_replay_reference"],
        "pgsp_replay_hash": pgsp_invocation["pgsp_replay_hash"],
        "summary_artifact": deepcopy(pgsp_result.get("summary_artifact", {})),
        "created_at": _require_string(created_at, "created_at"),
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


def _require_pgsp_non_mutating(pgsp_result: dict[str, Any]) -> None:
    for key in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if pgsp_result.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next bootstrap failed closed: PGSP {key} was not false")
    if not pgsp_result.get("replay_reference"):
        raise FailClosedRuntimeError("ACLI Next bootstrap failed closed: PGSP replay reference missing")


def _require_string(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next bootstrap requires {field}")
    return value
