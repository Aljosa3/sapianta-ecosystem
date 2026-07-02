"""Governed Deployment Worker.

This Worker executes only exact authorized deployment operations. It does not
orchestrate workflows, authorize execution, validate suites, or own Replay.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import shutil
from typing import Any

from aigol.authorization.authorization_record import validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


DEPLOYMENT_WORKER_VERSION = "G11_12_GOVERNED_DEPLOYMENT_WORKFLOW_IMPLEMENTATION_V1"
DEPLOYMENT_WORKER_ID = "GOVERNED_DEPLOYMENT_WORKER"
AUTHORIZED_DEPLOYMENT_REQUEST_TYPE = "AUTHORIZED_DEPLOYMENT_REQUEST_V1"
AUTHORIZED_DEPLOYMENT_SCOPE = "BOUNDED_DEPLOYMENT_OPERATION"

OPERATION_DEPLOYMENT_PLANNING = "DEPLOYMENT_PLANNING"
OPERATION_DEPLOYMENT_EXECUTION = "DEPLOYMENT_EXECUTION"
OPERATION_DEPLOYMENT_VERIFICATION = "DEPLOYMENT_VERIFICATION"
OPERATION_DEPLOYMENT_STATUS_REPORTING = "DEPLOYMENT_STATUS_REPORTING"
OPERATION_DEPLOYMENT_ROLLBACK_PREPARATION = "DEPLOYMENT_ROLLBACK_PREPARATION"
OPERATION_DEPLOYMENT_TARGET_VERIFICATION = "DEPLOYMENT_TARGET_VERIFICATION"
OPERATION_DEPLOYMENT_POLICY_VERIFICATION = "DEPLOYMENT_POLICY_VERIFICATION"

AUTHORIZED_OPERATIONS = {
    OPERATION_DEPLOYMENT_PLANNING,
    OPERATION_DEPLOYMENT_EXECUTION,
    OPERATION_DEPLOYMENT_VERIFICATION,
    OPERATION_DEPLOYMENT_STATUS_REPORTING,
    OPERATION_DEPLOYMENT_ROLLBACK_PREPARATION,
    OPERATION_DEPLOYMENT_TARGET_VERIFICATION,
    OPERATION_DEPLOYMENT_POLICY_VERIFICATION,
}

ADAPTER_LOCAL_STATIC_COPY = "LOCAL_STATIC_COPY"
ADAPTER_SSH = "SSH"
ADAPTER_DOCKER = "DOCKER"
ADAPTER_DOCKER_COMPOSE = "DOCKER_COMPOSE"
ADAPTER_KUBERNETES = "KUBERNETES"
SUPPORTED_ADAPTERS = {
    ADAPTER_LOCAL_STATIC_COPY,
    ADAPTER_SSH,
    ADAPTER_DOCKER,
    ADAPTER_DOCKER_COMPOSE,
    ADAPTER_KUBERNETES,
}
MUTATING_OPERATIONS = {OPERATION_DEPLOYMENT_EXECUTION}

DEPLOYMENT_REQUEST_CREATED = "DEPLOYMENT_REQUEST_CREATED"
DEPLOYMENT_PRE_STATE_RECORDED = "DEPLOYMENT_PRE_STATE_RECORDED"
DEPLOYMENT_WORKER_EXECUTED = "DEPLOYMENT_WORKER_EXECUTED"
DEPLOYMENT_WORKER_FAILED = "DEPLOYMENT_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "authorized_deployment_request",
    "deployment_worker_pre_state",
    "deployment_worker_execution",
)

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_command",
        "shell_command",
        "shell",
        "provider_invocation_request",
        "dispatch_request",
        "orchestration_request",
        "governance_mutation",
        "memory_mutation",
        "replay_mutation",
        "git_remote_request",
        "dependency_management_request",
        "validation_execution_request",
    }
)


def create_authorized_deployment_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    operation: str,
    deployment_id: str,
    target_adapter: str,
    target_id: str,
    target_environment: str,
    protected_environment: bool,
    protected_environment_authorized: bool,
    production_approval_reference: str | None,
    release_artifact_path: str,
    release_artifact_fingerprint: str,
    target_path: str,
    expected_active_release_fingerprint: str | None,
    deployment_strategy: str,
    credential_reference: str,
    git_remote_evidence_reference: str,
    dependency_evidence_reference: str,
    validation_artifact_hash: str,
    validation_suite_reference: str,
    rollback_reference: str,
    platform_digital_twin_projection: dict[str, Any],
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the Worker-facing request for one governed deployment operation."""

    record = _validate_deployment_authorization(authorization_record)
    normalized_operation = _operation(operation)
    adapter = _adapter(target_adapter)
    protected = bool(protected_environment)
    protected_authorized = bool(protected_environment_authorized)
    if protected and not protected_authorized:
        raise FailClosedRuntimeError("governed deployment failed closed: protected environment authorization required")
    if protected and _optional_string(production_approval_reference) is None:
        raise FailClosedRuntimeError("governed deployment failed closed: production approval reference required")
    projection = _require_json_object(platform_digital_twin_projection, "platform_digital_twin_projection")
    release_path = _normalize_relative_path(release_artifact_path, "release_artifact_path")
    target_relative = _normalize_relative_path(target_path, "target_path")
    request = {
        "request_type": AUTHORIZED_DEPLOYMENT_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": normalized_operation,
        "deployment_id": _require_string(deployment_id, "deployment_id"),
        "target_adapter": adapter,
        "target_id": _require_string(target_id, "target_id"),
        "target_environment": _normalize_token(target_environment, "target_environment"),
        "protected_environment": protected,
        "protected_environment_authorized": protected_authorized,
        "production_approval_reference": _optional_string(production_approval_reference),
        "release_artifact_path": release_path,
        "release_artifact_fingerprint": _require_string(release_artifact_fingerprint, "release_artifact_fingerprint"),
        "target_path": target_relative,
        "target_fingerprint": replay_hash(target_relative),
        "expected_active_release_fingerprint": _optional_string(expected_active_release_fingerprint),
        "deployment_strategy": _normalize_token(deployment_strategy, "deployment_strategy"),
        "credential_reference": _require_string(credential_reference, "credential_reference"),
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "git_remote_evidence_reference": _require_string(git_remote_evidence_reference, "git_remote_evidence_reference"),
        "dependency_evidence_reference": _require_string(dependency_evidence_reference, "dependency_evidence_reference"),
        "validation_artifact_hash": _require_string(validation_artifact_hash, "validation_artifact_hash"),
        "validation_suite_reference": _require_string(validation_suite_reference, "validation_suite_reference"),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "platform_digital_twin_projection": projection,
        "platform_digital_twin_projection_hash": replay_hash(projection),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "shell_allowed": False,
        "raw_command_allowed": False,
        "provider_invocation_allowed": False,
        "git_operation_allowed": False,
        "dependency_operation_allowed": False,
        "validation_execution_allowed": False,
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_deployment_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a governed deployment request without executing deployment."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized deployment request is required")
    _reject_forbidden_fields(request, "authorized deployment request")
    if request.get("request_type") != AUTHORIZED_DEPLOYMENT_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized deployment request type is invalid")
    if request.get("worker_id") != DEPLOYMENT_WORKER_ID:
        raise FailClosedRuntimeError("authorized deployment request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_DEPLOYMENT_SCOPE:
        raise FailClosedRuntimeError("authorized deployment request scope mismatch")
    _operation(request.get("operation"))
    _adapter(request.get("target_adapter"))
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    _require_string(request.get("deployment_id"), "deployment_id")
    _require_string(request.get("target_id"), "target_id")
    _normalize_token(request.get("target_environment"), "target_environment")
    if request.get("protected_environment") is True and request.get("protected_environment_authorized") is not True:
        raise FailClosedRuntimeError("authorized deployment request protected environment authorization missing")
    if request.get("protected_environment") is True and _optional_string(request.get("production_approval_reference")) is None:
        raise FailClosedRuntimeError("authorized deployment request production approval reference missing")
    _normalize_relative_path(request.get("release_artifact_path"), "release_artifact_path")
    _require_string(request.get("release_artifact_fingerprint"), "release_artifact_fingerprint")
    target_path = _normalize_relative_path(request.get("target_path"), "target_path")
    if request.get("target_fingerprint") != replay_hash(target_path):
        raise FailClosedRuntimeError("authorized deployment request target fingerprint mismatch")
    _optional_string(request.get("expected_active_release_fingerprint"))
    _normalize_token(request.get("deployment_strategy"), "deployment_strategy")
    projection = _require_json_object(request.get("platform_digital_twin_projection"), "platform_digital_twin_projection")
    if request.get("platform_digital_twin_projection_hash") != replay_hash(projection):
        raise FailClosedRuntimeError("authorized deployment request Platform Digital Twin projection hash mismatch")
    for field in (
        "credential_value_recorded",
        "credential_hash_recorded",
        "shell_allowed",
        "raw_command_allowed",
        "provider_invocation_allowed",
        "git_operation_allowed",
        "dependency_operation_allowed",
        "validation_execution_allowed",
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError(f"authorized deployment request {field} must be false")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized deployment request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected = deepcopy(request)
    expected.pop("request_hash")
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("authorized deployment request hash mismatch")
    if authorization_record is not None:
        record = _validate_deployment_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized deployment request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized deployment request authorization hash mismatch")
    return deepcopy(request)


def execute_deployment_request(
    *,
    authorized_request: dict[str, Any],
    repository_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute exactly one authorized deployment operation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_deployment_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        root = Path(repository_root).resolve()
        pre_state = _pre_state_artifact(request=request, root=root)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], pre_state)
        result = _execute_operation(request=request, root=root, pre_state=pre_state)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], result)
        return _capture(failure, result)


def reconstruct_deployment_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker-side governed deployment replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("Deployment Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("Deployment Worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "Deployment Worker replay artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    result = wrappers[2]["artifact"]
    if result.get("request_hash") != request.get("request_hash"):
        raise FailClosedRuntimeError("Deployment Worker replay request hash mismatch")
    return {
        "request_id": request["request_id"],
        "authorization_id": request["authorization_id"],
        "operation": request["operation"],
        "deployment_id": request["deployment_id"],
        "target_adapter": request["target_adapter"],
        "target_id": request["target_id"],
        "execution_status": result["execution_status"],
        "exit_code": result["exit_code"],
        "deployment_operation_performed": result["deployment_operation_performed"],
        "target_state_changed": result["target_state_changed"],
        "worker_invoked": result["worker_invoked"],
        "platform_digital_twin_projection_consumed": result["platform_digital_twin_projection_consumed"],
        "validation_executed_by_worker": result["validation_executed_by_worker"],
        "rollback_executed_by_worker": result["rollback_executed_by_worker"],
        "architectural_health_advisory_only": result["architectural_health_advisory_input"]["advisory_only"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _pre_state_artifact(*, request: dict[str, Any], root: Path) -> dict[str, Any]:
    _ensure_root(root)
    release_path = _resolve_relative(root, request["release_artifact_path"], "release_artifact_path")
    target_path = _resolve_relative(root, request["target_path"], "target_path")
    release_state = _path_state(release_path)
    if release_state["sha256"] != request["release_artifact_fingerprint"]:
        raise FailClosedRuntimeError("governed deployment failed closed: release artifact fingerprint mismatch")
    target_state = _path_state(target_path)
    expected = request.get("expected_active_release_fingerprint")
    if expected is not None and target_state["sha256"] != expected:
        raise FailClosedRuntimeError("governed deployment failed closed: active release fingerprint mismatch")
    artifact = {
        "runtime_version": DEPLOYMENT_WORKER_VERSION,
        "event_type": DEPLOYMENT_PRE_STATE_RECORDED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": request["operation"],
        "deployment_id": request["deployment_id"],
        "target_adapter": request["target_adapter"],
        "target_id": request["target_id"],
        "target_environment": request["target_environment"],
        "protected_environment": request["protected_environment"],
        "protected_environment_authorized": request["protected_environment_authorized"],
        "production_approval_reference": request.get("production_approval_reference"),
        "release_artifact_state": release_state,
        "target_state": target_state,
        "target_fingerprint": request["target_fingerprint"],
        "deployment_strategy": request["deployment_strategy"],
        "credential_reference": request["credential_reference"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "git_remote_evidence_reference": request["git_remote_evidence_reference"],
        "dependency_evidence_reference": request["dependency_evidence_reference"],
        "validation_artifact_hash": request["validation_artifact_hash"],
        "validation_suite_reference": request["validation_suite_reference"],
        "rollback_reference": request["rollback_reference"],
        "platform_digital_twin_projection_hash": request["platform_digital_twin_projection_hash"],
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_operation(*, request: dict[str, Any], root: Path, pre_state: dict[str, Any]) -> dict[str, Any]:
    operation = request["operation"]
    adapter = request["target_adapter"]
    target_state_changed = False
    exit_code = 0
    stdout = f"{operation} completed"
    stderr = ""
    if operation in MUTATING_OPERATIONS:
        if adapter != ADAPTER_LOCAL_STATIC_COPY:
            raise FailClosedRuntimeError("governed deployment failed closed: adapter execution not certified")
        _execute_local_static_copy(root=root, request=request)
        target_state_changed = True
        worker_invoked = True
    else:
        worker_invoked = operation in {
            OPERATION_DEPLOYMENT_VERIFICATION,
            OPERATION_DEPLOYMENT_STATUS_REPORTING,
            OPERATION_DEPLOYMENT_TARGET_VERIFICATION,
            OPERATION_DEPLOYMENT_POLICY_VERIFICATION,
        }
    post_target_state = _path_state(_resolve_relative(root, request["target_path"], "target_path"))
    release_state = _path_state(_resolve_relative(root, request["release_artifact_path"], "release_artifact_path"))
    if operation in {OPERATION_DEPLOYMENT_EXECUTION, OPERATION_DEPLOYMENT_VERIFICATION}:
        if post_target_state["sha256"] != release_state["sha256"]:
            exit_code = 1
            stdout = ""
            stderr = "deployed target fingerprint does not match release artifact"
    status = "DEPLOYMENT_OPERATION_COMPLETED" if exit_code == 0 else FAILED_CLOSED
    artifact = {
        "runtime_version": DEPLOYMENT_WORKER_VERSION,
        "event_type": DEPLOYMENT_WORKER_EXECUTED if exit_code == 0 else DEPLOYMENT_WORKER_FAILED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": operation,
        "deployment_id": request["deployment_id"],
        "target_adapter": adapter,
        "target_id": request["target_id"],
        "target_environment": request["target_environment"],
        "deployment_strategy": request["deployment_strategy"],
        "execution_sequence": _execution_sequence(request),
        "exit_code": exit_code,
        "stdout": _bounded_output(stdout),
        "stderr": _bounded_output(stderr),
        "execution_status": status,
        "deployment_operation_performed": exit_code == 0,
        "target_state_changed": target_state_changed,
        "pre_target_state_hash": replay_hash(pre_state["target_state"]),
        "post_target_state": post_target_state,
        "release_artifact_fingerprint": request["release_artifact_fingerprint"],
        "health_check_status": "HEALTH_CHECK_NOT_EXECUTED_BY_WORKER",
        "validation_suite_reference": request["validation_suite_reference"],
        "validation_artifact_hash": request["validation_artifact_hash"],
        "validation_outcome": "VALIDATION_SEQUENCING_REQUIRED_BY_PLATFORM_CORE",
        "rollback_reference": request["rollback_reference"],
        "rollback_prepared": True,
        "worker_invoked": worker_invoked,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "platform_digital_twin_projection_consumed": True,
        "platform_digital_twin_projection_owner": "Platform Digital Twin",
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "git_operation_performed": False,
        "dependency_operation_performed": False,
        "provider_invoked": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "architectural_health_advisory_input": _architectural_health_advisory_input(request, target_state_changed),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_local_static_copy(*, root: Path, request: dict[str, Any]) -> None:
    source = _resolve_relative(root, request["release_artifact_path"], "release_artifact_path")
    target = _resolve_relative(root, request["target_path"], "target_path")
    if not source.is_file():
        raise FailClosedRuntimeError("governed deployment failed closed: release artifact is not a file")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _execution_sequence(request: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "step": "consume_platform_digital_twin_projection",
            "projection_hash": request["platform_digital_twin_projection_hash"],
            "owner": "Platform Digital Twin",
        },
        {
            "step": "verify_release_artifact",
            "release_artifact_fingerprint": request["release_artifact_fingerprint"],
        },
        {
            "step": "execute_authorized_deployment_adapter",
            "target_adapter": request["target_adapter"],
            "operation": request["operation"],
        },
        {
            "step": "record_replay_evidence",
            "owner": "Replay",
        },
    ]


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(request)
    artifact["runtime_version"] = DEPLOYMENT_WORKER_VERSION
    artifact["event_type"] = DEPLOYMENT_REQUEST_CREATED
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": DEPLOYMENT_WORKER_VERSION,
        "event_type": DEPLOYMENT_WORKER_FAILED,
        "request_id": _safe_field(authorized_request, "request_id"),
        "request_hash": _safe_field(authorized_request, "request_hash"),
        "execution_status": FAILED_CLOSED,
        "failure_reason": _bounded_output(failure_reason),
        "exit_code": 1,
        "deployment_operation_performed": False,
        "target_state_changed": False,
        "worker_invoked": False,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "platform_digital_twin_projection_consumed": False,
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "git_operation_performed": False,
        "dependency_operation_performed": False,
        "provider_invoked": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "architectural_health_advisory_input": {
            "advisory_only": True,
            "architectural_health_authority": False,
            "findings_input_available": False,
        },
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(failure)


def _capture(request_artifact: dict[str, Any], result_artifact: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "worker_id": DEPLOYMENT_WORKER_ID,
        "request_id": request_artifact.get("request_id"),
        "request_hash": request_artifact.get("request_hash"),
        "operation": request_artifact.get("operation"),
        "target_adapter": request_artifact.get("target_adapter"),
        "target_id": request_artifact.get("target_id"),
        "execution_status": result_artifact["execution_status"],
        "deployment_operation_performed": result_artifact["deployment_operation_performed"],
        "target_state_changed": result_artifact["target_state_changed"],
        "worker_invoked": result_artifact["worker_invoked"],
        "failure_reason": result_artifact.get("failure_reason"),
        "result_hash": result_artifact["artifact_hash"],
        "replay_visible": True,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _validate_deployment_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record.get("worker_id") != DEPLOYMENT_WORKER_ID:
        raise FailClosedRuntimeError("Deployment authorization Worker mismatch")
    if record.get("authorization_scope") != AUTHORIZED_DEPLOYMENT_SCOPE:
        raise FailClosedRuntimeError("Deployment authorization scope mismatch")
    return record


def _architectural_health_advisory_input(request: dict[str, Any], target_state_changed: bool) -> dict[str, Any]:
    advisory = {
        "artifact_type": "DEPLOYMENT_ARCHITECTURAL_HEALTH_ADVISORY_INPUT_V1",
        "advisory_only": True,
        "architectural_health_authority": False,
        "deployment_consistency_observable": True,
        "deployment_failure_observable": True,
        "target_health_observable": True,
        "policy_violation_observable": True,
        "responsibility_preservation_observable": True,
        "operation": request["operation"],
        "target_adapter": request["target_adapter"],
        "target_state_changed": target_state_changed,
        "findings": [],
    }
    advisory["artifact_hash"] = replay_hash(advisory)
    return advisory


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only deployment replay artifact already exists: {path.name}")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "Deployment artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if path.exists():
        return
    _persist_step(replay_path, index, step, artifact)


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("Deployment Worker replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _path_state(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "is_file": path.is_file() if exists else False,
        "sha256": _file_sha256(path) if path.is_file() else None,
        "size_bytes": path.stat().st_size if path.is_file() else None,
    }


def _resolve_relative(root: Path, value: str, field: str) -> Path:
    relative = _normalize_relative_path(value, field)
    path = (root / relative).resolve()
    if not _is_relative_to(path, root):
        raise FailClosedRuntimeError(f"governed deployment failed closed: {field} escapes repository")
    return path


def _ensure_root(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("governed deployment failed closed: repository root is unavailable")


def _reject_forbidden_fields(request: dict[str, Any], label: str) -> None:
    present = FORBIDDEN_REQUEST_FIELDS.intersection(request)
    if present:
        raise FailClosedRuntimeError(f"{label} contains forbidden field {sorted(present)[0]}")


def _operation(value: Any) -> str:
    operation = _require_string(value, "operation").strip().upper().replace("-", "_").replace(" ", "_")
    if operation not in AUTHORIZED_OPERATIONS:
        raise FailClosedRuntimeError("governed deployment failed closed: unsupported operation")
    return operation


def _adapter(value: Any) -> str:
    adapter = _require_string(value, "target_adapter").strip().upper().replace("-", "_").replace(" ", "_")
    if adapter not in SUPPORTED_ADAPTERS:
        raise FailClosedRuntimeError("governed deployment failed closed: unsupported adapter")
    return adapter


def _normalize_relative_path(value: Any, field: str) -> str:
    relative = _require_string(value, field).strip()
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise FailClosedRuntimeError(f"governed deployment failed closed: invalid {field}")
    return relative


def _normalize_token(value: Any, field: str) -> str:
    return _require_string(value, field).strip().upper().replace("-", "_").replace(" ", "_")


def _require_json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"governed deployment requires {field}")
    return deepcopy(value)


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FailClosedRuntimeError("governed deployment optional string is invalid")
    return value.strip() or None


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed deployment requires {field}")
    return value.strip()


def _safe_field(value: Any, field: str) -> Any:
    return value.get(field) if isinstance(value, dict) else None


def _bounded_output(value: Any, limit: int = 4000) -> str:
    text = "" if value is None else str(value)
    return text[:limit]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed deployment failed closed"


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
