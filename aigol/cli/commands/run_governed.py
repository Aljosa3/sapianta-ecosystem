"""Operator-facing governed operation extension for the existing AiGOL CLI."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_runtime import (
    authorize_worker_request,
    reconstruct_authorization_replay,
)
from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import (
    ProviderProposalEnvelope,
    create_provider_proposal_envelope,
)
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.certified_provider_attachment import run_certified_provider_attachment
from aigol.provider.provider_runtime import reconstruct_provider_attachment_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE,
    FILESYSTEM_WORKER_ID,
    create_authorized_worker_request,
    execute_filesystem_create_request,
    reconstruct_filesystem_worker_replay,
)


COMMAND_NAME = "aigol run-governed"
SUPPORTED_WORKER = "filesystem"
SUPPORTED_OPERATION = "create-file"
PROVIDER_ID = "operator_cli_provider"
PROVIDER_VERSION = "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1"
DEFAULT_OPERATION_ID = "AIGOL-RUN-GOVERNED-000001"
DEFAULT_CREATED_AT = "2026-05-31T00:00:00Z"
FAILED_CLOSED = "FAILED_CLOSED"
SUCCEEDED = "SUCCEEDED"
OPERATOR_HARDENING_VERSION = "OPERATOR_EXPERIENCE_HARDENING_V1"


class OperatorCLIProviderAdapter(ProviderAdapter):
    """Deterministic local proposal source for the operator CLI extension."""

    provider_id = PROVIDER_ID
    provider_version = PROVIDER_VERSION

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        if not isinstance(request, dict):
            raise FailClosedRuntimeError("operator governed request must be a JSON object")
        response = {
            "proposal_kind": "FILESYSTEM_CREATE_FILE",
            "reason": "Create one governed file through existing AiGOL authorization and worker boundaries.",
            "target_worker": FILESYSTEM_WORKER_ID,
            "file_path": _require_string(request.get("target"), "target"),
            "content": _require_string(request.get("content"), "content"),
        }
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=deepcopy(request),
            response=response,
            timestamp=timestamp,
        )


def run_governed_operation_command(
    *,
    worker: str,
    operation: str,
    target: str,
    content: str,
    operation_id: str = DEFAULT_OPERATION_ID,
    created_at: str = DEFAULT_CREATED_AT,
    runtime_root: str | Path = ".aigol_operator_runtime",
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run one governed operation through existing provider, authorization, worker, and replay paths."""

    try:
        normalized_worker = _normalize_token(worker, "worker")
        normalized_operation = _normalize_token(operation, "operation")
        if normalized_worker != SUPPORTED_WORKER:
            raise FailClosedRuntimeError("unknown worker")
        if normalized_operation != SUPPORTED_OPERATION:
            raise FailClosedRuntimeError("unknown operation")
        created_at = _require_string(created_at, "created_at")
        target = _require_string(target, "target")
        content = _require_string(content, "content")
        root = Path(runtime_root)
        operation_id = _resolve_operation_id(
            operation_id=operation_id,
            worker=normalized_worker,
            operation=normalized_operation,
            target=target,
            content=content,
            runtime_root=root,
        )
        workspace_path = Path(workspace)
        if not workspace_path.exists() or not workspace_path.is_dir():
            raise FailClosedRuntimeError("workspace is invalid")
        replay_root = root / operation_id
        human_request = {
            "operation_id": operation_id,
            "human_request": f"Create {target} through governed filesystem operation.",
            "worker": normalized_worker,
            "operation": normalized_operation,
            "target": target,
            "content": content,
        }
        registry = ProviderRegistry()
        registry.register_provider(
            ProviderMetadata(
                provider_id=PROVIDER_ID,
                provider_type="local_operator_cli",
                provider_version=PROVIDER_VERSION,
                provider_status=AVAILABLE,
                domain="operator_interface",
                capability="proposal_generation",
                resource_type="text",
            )
        )
        provider_capture = run_certified_provider_attachment(
            provider_id=PROVIDER_ID,
            request=human_request,
            proposal_id=f"{operation_id}:PROPOSAL",
            timestamp=created_at,
            registry=registry,
            adapter=OperatorCLIProviderAdapter(),
            replay_dir=replay_root / "provider",
        )
        envelope = provider_capture["provider_proposal_envelope"]
        proposal = _proposal_for_authorization(envelope)
        authorization_capture = authorize_worker_request(
            authorization_id=f"{operation_id}:AUTHORIZATION",
            proposal=proposal,
            worker_target={
                "worker_id": FILESYSTEM_WORKER_ID,
                "domain": "filesystem",
                "capability": "filesystem_create_file",
            },
            authorization_scope=AUTHORIZED_SCOPE,
            authorization_timestamp=created_at,
            replay_dir=replay_root / "authorization",
        )
        authorization = authorization_capture["authorization_record"]
        authorized_request = create_authorized_worker_request(
            authorization_record=authorization,
            request_id=f"{operation_id}:AUTHORIZED_WORKER_REQUEST",
            file_path=envelope["response"]["file_path"],
            content=envelope["response"]["content"],
            request_timestamp=created_at,
            proposal_reference={
                "proposal_id": envelope["proposal_id"],
                "proposal_hash": envelope["proposal_hash"],
            },
            replay_reference=(
                authorization.get("authorization_hash", "MISSING_AUTHORIZATION_HASH")
                if isinstance(authorization, dict)
                else "MISSING_AUTHORIZATION_HASH"
            ),
        )
        worker_capture = execute_filesystem_create_request(
            authorized_request=authorized_request,
            base_dir=workspace_path,
            replay_dir=replay_root / "worker",
        )
        worker_result = worker_capture["filesystem_worker_execution"]
        if worker_result.get("execution_status") != SUCCEEDED:
            raise FailClosedRuntimeError(worker_result.get("failure_reason") or "worker execution failed closed")
        provider_replay = reconstruct_provider_attachment_replay(replay_root / "provider")
        authorization_replay = reconstruct_authorization_replay(replay_root / "authorization")
        worker_replay = reconstruct_filesystem_worker_replay(replay_root / "worker")
        return _success_result(
            operation_id=operation_id,
            target=target,
            provider_capture=provider_capture,
            authorization_capture=authorization_capture,
            worker_capture=worker_capture,
            provider_replay=provider_replay,
            authorization_replay=authorization_replay,
            worker_replay=worker_replay,
            replay_root=replay_root,
        )
    except Exception as exc:
        return _failure_result(
            operation_id=operation_id if isinstance(operation_id, str) and operation_id.strip() else "INVALID_OPERATION_ID",
            worker=worker,
            operation=operation,
            target=target,
            runtime_root=runtime_root,
            failure_reason=_failure_reason(exc),
        )


def _success_result(
    *,
    operation_id: str,
    target: str,
    provider_capture: dict[str, Any],
    authorization_capture: dict[str, Any],
    worker_capture: dict[str, Any],
    provider_replay: dict[str, Any],
    authorization_replay: dict[str, Any],
    worker_replay: dict[str, Any],
    replay_root: Path,
) -> dict[str, Any]:
    proposal = provider_capture["provider_proposal_envelope"]
    authorization = authorization_capture["authorization_record"]
    worker_result = worker_capture["filesystem_worker_execution"]
    result = {
        "command": COMMAND_NAME,
        "operation_id": operation_id,
        "status": SUCCEEDED,
        "operator_status": "READY",
        "execution_status": worker_result["execution_status"],
        "proposal_id": proposal["proposal_id"],
        "authorization_id": authorization["authorization_id"],
        "worker_id": worker_result["worker_id"],
        "worker_result": deepcopy(worker_result["execution_result"]),
        "replay_id": operation_id,
        "replay_reference": str(replay_root),
        "target": target,
        "provider_replay_hash": provider_replay["replay_hash"],
        "authorization_replay_hash": authorization_replay["replay_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "replay_summary": _replay_summary(
            provider_replay=provider_replay,
            authorization_replay=authorization_replay,
            worker_replay=worker_replay,
        ),
        "fail_closed": False,
        "authority": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
    }
    result["result_hash"] = replay_hash(result)
    return result


def _failure_result(
    *,
    operation_id: str,
    worker: Any,
    operation: Any,
    target: Any,
    runtime_root: Any,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": COMMAND_NAME,
        "operation_id": operation_id,
        "status": FAILED_CLOSED,
        "operator_status": FAILED_CLOSED,
        "execution_status": FAILED_CLOSED,
        "proposal_id": "UNAVAILABLE",
        "authorization_id": "UNAVAILABLE",
        "worker_id": worker if isinstance(worker, str) and worker.strip() else "INVALID_WORKER",
        "worker_result": {"created": False, "path": None, "content_hash": FAILED_CLOSED},
        "replay_id": operation_id,
        "replay_reference": str(Path(runtime_root) / operation_id) if isinstance(runtime_root, str | Path) else "UNAVAILABLE",
        "target": target if isinstance(target, str) and target.strip() else "INVALID_TARGET",
        "provider_replay_hash": FAILED_CLOSED,
        "authorization_replay_hash": FAILED_CLOSED,
        "worker_replay_hash": FAILED_CLOSED,
        "fail_closed": True,
        "failure_reason": failure_reason,
        "authority": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
    }
    result["result_hash"] = replay_hash(result)
    return result


def summarize_governed_operation_replay(
    *,
    operation_id: str,
    runtime_root: str | Path = ".aigol_operator_runtime",
) -> dict[str, Any]:
    """Return a replay-only summary for a governed operation id."""

    try:
        operation_id = _require_string(operation_id, "operation_id")
        replay_root = Path(runtime_root) / operation_id
        provider_replay = reconstruct_provider_attachment_replay(replay_root / "provider")
        authorization_replay = reconstruct_authorization_replay(replay_root / "authorization")
        worker_replay = reconstruct_filesystem_worker_replay(replay_root / "worker")
        worker_result = worker_replay.get("execution_result", {})
        proposal_reference = worker_replay.get("proposal_reference", {})
        result = {
            "command": "aigol replay operation",
            "operation_id": operation_id,
            "status": SUCCEEDED,
            "operator_status": "READY",
            "execution_status": worker_replay.get("execution_status"),
            "proposal_id": proposal_reference.get("proposal_id", authorization_replay.get("who_proposed")),
            "authorization_id": worker_replay.get("authorization_id"),
            "worker_id": worker_replay.get("worker_id"),
            "target": worker_result.get("path"),
            "worker_result": deepcopy(worker_result),
            "replay_id": operation_id,
            "replay_reference": str(replay_root),
            "provider_replay_hash": provider_replay["replay_hash"],
            "authorization_replay_hash": authorization_replay["replay_hash"],
            "worker_replay_hash": worker_replay["replay_hash"],
            "replay_summary": _replay_summary(
                provider_replay=provider_replay,
                authorization_replay=authorization_replay,
                worker_replay=worker_replay,
            ),
            "fail_closed": False,
            "authority": False,
            "orchestration_performed": False,
            "planning_performed": False,
            "multi_step_execution": False,
        }
        result["result_hash"] = replay_hash(result)
        return result
    except Exception as exc:
        result = {
            "command": "aigol replay operation",
            "operation_id": operation_id if isinstance(operation_id, str) and operation_id.strip() else "INVALID_OPERATION_ID",
            "status": FAILED_CLOSED,
            "operator_status": FAILED_CLOSED,
            "execution_status": FAILED_CLOSED,
            "proposal_id": "UNAVAILABLE",
            "authorization_id": "UNAVAILABLE",
            "worker_id": "UNAVAILABLE",
            "target": "UNAVAILABLE",
            "worker_result": {"created": False, "path": None, "content_hash": FAILED_CLOSED},
            "replay_id": operation_id if isinstance(operation_id, str) and operation_id.strip() else "INVALID_OPERATION_ID",
            "replay_reference": str(Path(runtime_root) / operation_id) if isinstance(runtime_root, str | Path) else "UNAVAILABLE",
            "provider_replay_hash": FAILED_CLOSED,
            "authorization_replay_hash": FAILED_CLOSED,
            "worker_replay_hash": FAILED_CLOSED,
            "replay_summary": {"events": [], "event_count": 0},
            "fail_closed": True,
            "failure_reason": _failure_reason(exc),
            "authority": False,
            "orchestration_performed": False,
            "planning_performed": False,
            "multi_step_execution": False,
        }
        result["result_hash"] = replay_hash(result)
        return result


def _proposal_for_authorization(envelope: dict[str, Any]) -> dict[str, Any]:
    if envelope.get("event_type") == FAILED_CLOSED:
        raise FailClosedRuntimeError(envelope.get("failure_reason") or "invalid proposal")
    response = envelope.get("response")
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("invalid proposal")
    if response.get("target_worker") != FILESYSTEM_WORKER_ID:
        raise FailClosedRuntimeError("invalid proposal target worker")
    if response.get("proposal_kind") != "FILESYSTEM_CREATE_FILE":
        raise FailClosedRuntimeError("invalid proposal kind")
    return {
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "proposal_lineage": {
            "provider_id": envelope["provider_id"],
            "provider_version": envelope["provider_version"],
            "proposal_hash": envelope["proposal_hash"],
        },
        "governance_review": "AIGOL_OPERATOR_INTERFACE_EXTENSION_V1",
    }


def _resolve_operation_id(
    *,
    operation_id: str,
    worker: str,
    operation: str,
    target: str,
    content: str,
    runtime_root: Path,
) -> str:
    if operation_id != DEFAULT_OPERATION_ID:
        return _require_string(operation_id, "operation_id")
    generated = generate_default_operation_id(
        worker=worker,
        operation=operation,
        target=target,
        content=content,
    )
    candidate = generated
    suffix = 1
    while (runtime_root / candidate).exists():
        suffix += 1
        candidate = f"{generated}-{suffix:04d}"
    return candidate


def generate_default_operation_id(*, worker: str, operation: str, target: str, content: str) -> str:
    seed = {
        "content": content,
        "operation": operation,
        "target": target,
        "version": OPERATOR_HARDENING_VERSION,
        "worker": worker,
    }
    return f"AIGOL-RUN-GOVERNED-{replay_hash(seed).split(':', 1)[1][:12].upper()}"


def _replay_summary(
    *,
    provider_replay: dict[str, Any],
    authorization_replay: dict[str, Any],
    worker_replay: dict[str, Any],
) -> dict[str, Any]:
    events: list[str] = []
    if provider_replay.get("replay_artifact_count"):
        events.extend(["PROVIDER_PROPOSAL_CREATED", "PROVIDER_PROPOSAL_RETURNED"])
    if authorization_replay.get("replay_visible"):
        events.extend(["AUTHORIZATION_CREATED", "AUTHORIZATION_RETURNED"])
    if worker_replay.get("replay_artifact_count"):
        events.extend(["AUTHORIZED_WORKER_REQUEST_CREATED", "FILESYSTEM_WORKER_EXECUTED"])
    return {
        "event_count": len(events),
        "events": events,
    }


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().lower().replace("_", "-")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "operator governed operation failed closed"
