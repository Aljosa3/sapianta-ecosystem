"""Read-only Worker Platform preview helpers for ACLI Next MVP handoff."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_WORKER_PREVIEW_VERSION = "G8_06D_PLATFORM_CORE_WORKER_PREVIEW_V1"

READONLY_WORKER_COMPLETED = "ACLI_NEXT_READONLY_WORKER_COMPLETED"


def readonly_worker_result(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    capability: dict[str, str],
    request: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
    platform_core_service_version: str,
) -> dict[str, Any]:
    """Create a replay-visible read-only Worker result preview."""

    summary = readonly_worker_summary(capability_id, interactive_result)
    result = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_RESULT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": platform_core_service_version,
        "worker_preview_version": PLATFORM_CORE_WORKER_PREVIEW_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "worker_id": capability["worker_id"],
        "worker_type": capability["worker_type"],
        "worker_request_hash": request["artifact_hash"],
        "worker_result_status": READONLY_WORKER_COMPLETED,
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


def readonly_worker_summary(capability_id: str, interactive_result: dict[str, Any]) -> dict[str, Any]:
    turns = interactive_result.get("turns")
    if not isinstance(turns, list) or not turns:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: turn history missing")
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
            "mapping_basis": "canonical response classes",
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
    raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: unsupported capability")


def require_readonly_worker_result(result: dict[str, Any]) -> None:
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
            raise FailClosedRuntimeError(f"Platform Core read-only Worker failed closed: {key} was not false")
    if result.get("worker_invoked") is not True:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: Worker result missing")
    if result.get("read_only") is not True or result.get("replay_visible") is not True:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: read-only replay evidence missing")


def result_summary(result: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(result["result_summary"])


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Platform Core Worker preview requires {field}")
    return value
