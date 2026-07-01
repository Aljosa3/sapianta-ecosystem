"""Read-only Worker handoff for ACLI Next interactive sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.acli_next.interactive import ACLI_NEXT_INTERACTIVE_COMPLETED, run_acli_next_interactive_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_NEXT_READONLY_WORKER_VERSION = "G8_05_ACLI_NEXT_READONLY_WORKER_HANDOFF_V1"
READONLY_WORKER_COMMAND_NAME = "aigol next readonly-worker"

ACLI_NEXT_READONLY_WORKER_REQUESTED = "ACLI_NEXT_READONLY_WORKER_REQUESTED"
ACLI_NEXT_READONLY_WORKER_COMPLETED = "ACLI_NEXT_READONLY_WORKER_COMPLETED"
ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED = "ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED"

AUTHORIZED_READONLY_WORKER = "AUTHORIZED_READONLY_WORKER"

SUPPORTED_READONLY_CAPABILITIES: dict[str, dict[str, str]] = {
    "replay_inspection": {
        "worker_id": "ACLI_NEXT_REPLAY_INSPECTION_WORKER",
        "worker_type": "READONLY_REPLAY_INSPECTION_SUMMARY",
        "description": "Summarize ACLI Next replay references without mutation.",
    },
    "validation_summary": {
        "worker_id": "ACLI_NEXT_VALIDATION_SUMMARY_WORKER",
        "worker_type": "READONLY_VALIDATION_SUMMARY",
        "description": "Summarize validation evidence already present in ACLI Next replay.",
    },
    "canonical_mapping_lookup": {
        "worker_id": "ACLI_NEXT_CANONICAL_MAPPING_LOOKUP_WORKER",
        "worker_type": "READONLY_CANONICAL_MAPPING_LOOKUP",
        "description": "Summarize canonical mapping evidence already present in ACLI Next replay.",
    },
}


def run_acli_next_readonly_worker_handoff(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    worker_capability: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Run a certified read-only Worker handoff after interactive confirmation."""

    replay_path = Path(replay_dir)
    normalized_capability = _normalize_capability(worker_capability)
    capability = _lookup_readonly_capability(normalized_capability)
    authorization = _governance_authorization_check(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        created_at=created_at,
    )
    request = _worker_request_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        capability=capability,
        authorization=authorization,
        created_at=created_at,
    )
    _persist(replay_path, "000_acli_next_readonly_worker_request.json", request)

    result = _worker_result_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        capability=capability,
        request=request,
        created_at=created_at,
    )
    _persist(replay_path, "001_acli_next_readonly_worker_result.json", result)

    completion = _completion_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        result=result,
        replay_path=replay_path,
        created_at=created_at,
    )
    _persist(replay_path, "002_acli_next_readonly_worker_completion.json", completion)
    return _result(completion)


def run_acli_next_interactive_with_readonly_worker(
    *,
    session_id: str,
    turns: list[dict[str, str]],
    worker_capability: str,
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run an interactive ACLI Next session and then a read-only Worker handoff."""

    replay_path = Path(replay_dir)
    interactive_result = run_acli_next_interactive_session(
        session_id=session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=replay_path / "interactive_session",
        workspace=workspace,
    )
    return run_acli_next_readonly_worker_handoff(
        session_id=session_id,
        interactive_result=interactive_result,
        worker_capability=worker_capability,
        created_at=created_at,
        replay_dir=replay_path / "readonly_worker_handoff",
    )


def render_acli_next_readonly_worker_summary(result: dict[str, Any]) -> str:
    """Render ACLI Next read-only Worker handoff evidence."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"session_id: {result.get('session_id')}",
            f"handoff_status: {result.get('handoff_status')}",
            f"worker_capability: {result.get('worker_capability')}",
            f"worker_id: {result.get('worker_id')}",
            f"governance_authorization_status: {result.get('governance_authorization_status')}",
            f"worker_result_status: {result.get('worker_result_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"interactive_replay_reference: {result.get('interactive_replay_reference')}",
            f"read_only: {result.get('read_only')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
        ]
    )


def _governance_authorization_check(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    created_at: str,
) -> dict[str, Any]:
    _require_confirmed_interactive_session(interactive_result)
    authorization = {
        "artifact_type": "ACLI_NEXT_READONLY_WORKER_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": ACLI_NEXT_READONLY_WORKER_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "authorization_status": AUTHORIZED_READONLY_WORKER,
        "authorization_scope": "READ_ONLY_CONFIRMED_INTERACTIVE_SESSION",
        "authorization_basis": {
            "interactive_session_status": interactive_result.get("session_status"),
            "final_response_class": interactive_result.get("final_response_class"),
            "interactive_replay_reference": interactive_result.get("replay_reference"),
            "interactive_replay_hash": interactive_result.get("replay_hash"),
        },
        "human_confirmation_required": True,
        "human_confirmation_observed": True,
        "execution_authorized": False,
        "mutation_authorized": False,
        "provider_authorized": False,
        "worker_write_authorized": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def _worker_request_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    capability: dict[str, str],
    authorization: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    request = {
        "artifact_type": "ACLI_NEXT_READONLY_WORKER_REQUEST_V1",
        "runtime_version": ACLI_NEXT_READONLY_WORKER_VERSION,
        "command": READONLY_WORKER_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "worker_id": capability["worker_id"],
        "worker_type": capability["worker_type"],
        "capability_description": capability["description"],
        "governance_authorization_hash": authorization["artifact_hash"],
        "governance_authorization_status": authorization["authorization_status"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "created_at": _require_string(created_at, "created_at"),
        "handoff_status": ACLI_NEXT_READONLY_WORKER_REQUESTED,
        "read_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _worker_result_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    capability: dict[str, str],
    request: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    summary = _readonly_worker_summary(capability_id, interactive_result)
    result = {
        "artifact_type": "ACLI_NEXT_READONLY_WORKER_RESULT_V1",
        "runtime_version": ACLI_NEXT_READONLY_WORKER_VERSION,
        "command": READONLY_WORKER_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "worker_id": capability["worker_id"],
        "worker_type": capability["worker_type"],
        "worker_request_hash": request["artifact_hash"],
        "worker_result_status": ACLI_NEXT_READONLY_WORKER_COMPLETED,
        "result_summary": summary,
        "created_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "provider_invoked": False,
        "worker_invoked": True,
        "worker_write_performed": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def _completion_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    result: dict[str, Any],
    replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    _require_readonly_worker_result(result)
    completion = {
        "artifact_type": "ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETION_V1",
        "runtime_version": ACLI_NEXT_READONLY_WORKER_VERSION,
        "command": READONLY_WORKER_COMMAND_NAME,
        "session_id": _require_string(session_id, "session_id"),
        "handoff_status": ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED,
        "worker_capability": result["worker_capability"],
        "worker_id": result["worker_id"],
        "worker_type": result["worker_type"],
        "worker_request_hash": request["artifact_hash"],
        "worker_result_hash": result["artifact_hash"],
        "worker_result_status": result["worker_result_status"],
        "governance_authorization_status": request["governance_authorization_status"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "replay_reference": str(replay_path),
        "result_summary": deepcopy(result["result_summary"]),
        "created_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "provider_invoked": False,
        "worker_invoked": True,
        "worker_write_performed": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "fail_closed": False,
        "replay_visible": True,
    }
    completion["artifact_hash"] = replay_hash(completion)
    return completion


def _readonly_worker_summary(capability_id: str, interactive_result: dict[str, Any]) -> dict[str, Any]:
    turns = interactive_result.get("turns")
    if not isinstance(turns, list) or not turns:
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: turn history missing")
    if capability_id == "replay_inspection":
        return {
            "summary_type": "READONLY_REPLAY_INSPECTION_SUMMARY",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "turn_count": interactive_result["turn_count"],
            "final_response_class": interactive_result["final_response_class"],
            "turn_response_classes": [turn.get("canonical_response_class") for turn in turns],
            "all_turns_replay_visible": all(bool(turn.get("turn_replay_reference")) for turn in turns),
            "mutation_detected": False,
        }
    if capability_id == "validation_summary":
        return {
            "summary_type": "READONLY_VALIDATION_SUMMARY",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "validation_basis": "interactive session replay metadata",
            "turn_count": interactive_result["turn_count"],
            "completion_non_mutating": interactive_result.get("repository_mutated") is False,
            "mutation_detected": False,
        }
    if capability_id == "canonical_mapping_lookup":
        return {
            "summary_type": "READONLY_CANONICAL_MAPPING_LOOKUP",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "mapping_basis": "ACLI Next canonical response classes",
            "final_response_class": interactive_result["final_response_class"],
            "continuation_profile": [
                {
                    "turn_id": turn.get("turn_id"),
                    "canonical_response_class": turn.get("canonical_response_class"),
                    "continuation_allowed": turn.get("continuation_allowed"),
                    "terminal_turn": turn.get("terminal_turn"),
                }
                for turn in turns
            ],
            "mutation_detected": False,
        }
    raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: unsupported capability")


def _lookup_readonly_capability(capability_id: str) -> dict[str, str]:
    capability = SUPPORTED_READONLY_CAPABILITIES.get(capability_id)
    if capability is None:
        raise FailClosedRuntimeError(
            f"ACLI Next read-only Worker failed closed: unsupported capability {capability_id}"
        )
    return capability


def _require_confirmed_interactive_session(interactive_result: dict[str, Any]) -> None:
    if interactive_result.get("session_status") != ACLI_NEXT_INTERACTIVE_COMPLETED:
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: interactive session incomplete")
    if interactive_result.get("final_response_class") != "CONFIRMATION":
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: human confirmation missing")
    if not interactive_result.get("replay_reference") or not interactive_result.get("replay_hash"):
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: interactive replay evidence missing")
    for key in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if interactive_result.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next read-only Worker failed closed: {key} was not false")


def _require_readonly_worker_result(result: dict[str, Any]) -> None:
    for key in (
        "provider_invoked",
        "worker_write_performed",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if result.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI Next read-only Worker failed closed: {key} was not false")
    if result.get("worker_invoked") is not True:
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: Worker result missing")
    if result.get("read_only") is not True or result.get("replay_visible") is not True:
        raise FailClosedRuntimeError("ACLI Next read-only Worker failed closed: read-only replay evidence missing")


def _normalize_capability(value: str) -> str:
    return _require_string(value, "worker_capability").strip().lower().replace("-", "_")


def _result(completion: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(completion)
    result["replay_hash"] = completion["artifact_hash"]
    return result


def _persist(replay_path: Path, name: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / name, artifact)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI Next read-only Worker requires {field}")
    return value
