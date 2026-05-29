"""Minimal operator entrypoint for the frozen governed read-only flow."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.human_prompt_to_governed_readonly_result import (
    OPERATOR_COMPLETED,
    OPERATOR_FAILED,
    READ_ONLY_RUNTIME_INSPECTION,
    reconstruct_human_prompt_governed_result_replay,
    run_human_prompt_to_governed_readonly_result,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.governed_result_summary import (
    create_governed_failure_summary,
    create_governed_result_summary,
)
from aigol.runtime.transport.serialization import replay_hash


SUPPORTED_ENTRYPOINT_CAPABILITIES = frozenset({READ_ONLY_RUNTIME_INSPECTION, FILESYSTEM_READ_ONLY_INSPECTION})
ENTRYPOINT_MODE = "MINIMAL_OPERATOR_ENTRYPOINT"


def run_minimal_operator_entrypoint(
    *,
    operator_flow_id: str,
    human_request: str,
    target_capability: str,
    created_at: str,
    replay_dir: str | Path,
    root_path: str | Path | None = None,
    requested_path: str | Path | None = None,
    allowed_paths: list[str | Path] | None = None,
    authorize: bool = True,
) -> dict[str, Any]:
    """Run one human request through the frozen governed read-only runtime."""

    try:
        normalized_request = _normalize_text(human_request, "human_request")
        capability = _normalize_capability(target_capability)
        replay_path = Path(replay_dir)
        flow = run_human_prompt_to_governed_readonly_result(
            operator_flow_id=_require_string(operator_flow_id, "operator_flow_id"),
            human_prompt=normalized_request,
            target_capability=capability,
            created_at=_require_string(created_at, "created_at"),
            replay_dir=replay_path,
            root_path=root_path,
            requested_path=requested_path,
            allowed_paths=allowed_paths,
            authorize=authorize,
        )
        governed_result = flow["governed_result"]
        replay_summary = reconstruct_human_prompt_governed_result_replay(replay_path)
        summary = create_operator_result_summary(
            operator_flow_id=operator_flow_id,
            human_request=normalized_request,
            target_capability=capability,
            replay_dir=replay_path,
            governed_result=governed_result,
            replay_summary=replay_summary,
        )
        return {
            "entrypoint_mode": ENTRYPOINT_MODE,
            "operator_result_summary": summary,
            "flow": deepcopy(flow),
            "replay_summary": deepcopy(replay_summary),
            "llm_proposes_only": True,
            "aigol_governs": True,
            "worker_executes_only_after_authorization": True,
            "replay_records": True,
        }
    except Exception as exc:
        summary = create_operator_failure_summary(
            operator_flow_id=operator_flow_id if isinstance(operator_flow_id, str) and operator_flow_id else "OPERATOR-FLOW-INVALID",
            human_request=human_request if isinstance(human_request, str) and human_request.strip() else "REQUEST-INVALID",
            target_capability=target_capability if isinstance(target_capability, str) and target_capability else "CAPABILITY-INVALID",
            replay_dir=Path(replay_dir),
            failure_reason=_failure_reason(exc),
        )
        return {
            "entrypoint_mode": ENTRYPOINT_MODE,
            "operator_result_summary": summary,
            "flow": None,
            "replay_summary": None,
            "llm_proposes_only": True,
            "aigol_governs": True,
            "worker_executes_only_after_authorization": False,
            "replay_records": True,
        }


def create_operator_result_summary(
    *,
    operator_flow_id: str,
    human_request: str,
    target_capability: str,
    replay_dir: str | Path,
    governed_result: dict[str, Any],
    replay_summary: dict[str, Any],
) -> dict[str, Any]:
    """Create concise operator-facing summary from existing replay evidence."""

    if not isinstance(governed_result, dict):
        raise FailClosedRuntimeError("governed result is required")
    if not isinstance(replay_summary, dict):
        raise FailClosedRuntimeError("replay summary is required")
    final_status = governed_result.get("final_status")
    if final_status not in {OPERATOR_COMPLETED, OPERATOR_FAILED}:
        raise FailClosedRuntimeError("operator result final status is invalid")
    accepted = final_status == OPERATOR_COMPLETED
    return create_governed_result_summary(
        operator_flow_id=_require_string(operator_flow_id, "operator_flow_id"),
        human_request=_normalize_text(human_request, "human_request"),
        capability_used=_normalize_capability(target_capability),
        replay_reference=replay_dir,
        governed_result=governed_result,
        replay_summary=replay_summary,
    )


def create_operator_failure_summary(
    *,
    operator_flow_id: str,
    human_request: str,
    target_capability: str,
    replay_dir: str | Path,
    failure_reason: str,
) -> dict[str, Any]:
    """Create operator-facing rejection summary when entrypoint validation fails."""

    return create_governed_failure_summary(
        operator_flow_id=_require_string(operator_flow_id, "operator_flow_id"),
        human_request=_require_string(human_request, "human_request"),
        capability_used=_require_string(target_capability, "target_capability"),
        replay_reference=replay_dir,
        failure_reason=_require_string(failure_reason, "failure_reason"),
    )


def _normalize_capability(value: Any) -> str:
    capability = _require_string(value, "target_capability").strip().upper().replace("-", "_")
    if capability not in SUPPORTED_ENTRYPOINT_CAPABILITIES:
        raise FailClosedRuntimeError("unsupported operator capability")
    return capability


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "minimal operator entrypoint failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
