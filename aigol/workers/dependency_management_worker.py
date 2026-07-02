"""Governed Dependency Management Worker.

This Worker executes only exact authorized dependency operations. It does not
orchestrate workflows, authorize execution, validate suites, or own Replay.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import sys
from typing import Any

from aigol.authorization.authorization_record import validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


DEPENDENCY_WORKER_VERSION = "G11_10_GOVERNED_DEPENDENCY_MANAGEMENT_WORKFLOW_IMPLEMENTATION_V1"
DEPENDENCY_WORKER_ID = "GOVERNED_DEPENDENCY_MANAGEMENT_WORKER"
AUTHORIZED_DEPENDENCY_REQUEST_TYPE = "AUTHORIZED_DEPENDENCY_MANAGEMENT_REQUEST_V1"
AUTHORIZED_DEPENDENCY_SCOPE = "BOUNDED_DEPENDENCY_OPERATION"

OPERATION_DEPENDENCY_INSPECTION = "DEPENDENCY_INSPECTION"
OPERATION_DEPENDENCY_INSTALL = "DEPENDENCY_INSTALL"
OPERATION_DEPENDENCY_UPDATE = "DEPENDENCY_UPDATE"
OPERATION_DEPENDENCY_REMOVAL = "DEPENDENCY_REMOVAL"
OPERATION_DEPENDENCY_VERIFICATION = "DEPENDENCY_VERIFICATION"
OPERATION_LOCK_SYNCHRONIZATION = "LOCK_SYNCHRONIZATION"
OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION = "ENVIRONMENT_CONSISTENCY_VERIFICATION"
AUTHORIZED_OPERATIONS = {
    OPERATION_DEPENDENCY_INSPECTION,
    OPERATION_DEPENDENCY_INSTALL,
    OPERATION_DEPENDENCY_UPDATE,
    OPERATION_DEPENDENCY_REMOVAL,
    OPERATION_DEPENDENCY_VERIFICATION,
    OPERATION_LOCK_SYNCHRONIZATION,
    OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION,
}
PACKAGE_OPERATIONS = {
    OPERATION_DEPENDENCY_INSTALL,
    OPERATION_DEPENDENCY_UPDATE,
    OPERATION_DEPENDENCY_REMOVAL,
}

PYTHON = "PYTHON"
NODE = "NODE"
SUPPORTED_PACKAGE_MANAGERS = {
    "pip": PYTHON,
    "uv": PYTHON,
    "poetry": PYTHON,
    "npm": NODE,
    "pnpm": NODE,
    "yarn": NODE,
}

DEPENDENCY_REQUEST_CREATED = "DEPENDENCY_REQUEST_CREATED"
DEPENDENCY_PRE_STATE_RECORDED = "DEPENDENCY_PRE_STATE_RECORDED"
DEPENDENCY_WORKER_EXECUTED = "DEPENDENCY_WORKER_EXECUTED"
DEPENDENCY_WORKER_FAILED = "DEPENDENCY_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "authorized_dependency_request",
    "dependency_worker_pre_state",
    "dependency_worker_execution",
)

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_command",
        "shell_command",
        "shell",
        "deployment_request",
        "provider_invocation_request",
        "dispatch_request",
        "orchestration_request",
        "governance_mutation",
        "memory_mutation",
        "replay_mutation",
        "git_commit_request",
        "git_remote_request",
    }
)


def create_authorized_dependency_management_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    operation: str,
    project_id: str,
    package_manager: str,
    project_root: str,
    manifest_paths: list[str],
    lockfile_paths: list[str],
    dependency_name: str | None,
    dependency_version: str | None,
    version_constraint: str | None,
    registry_url: str | None,
    registry_private: bool,
    private_registry_authorized: bool,
    credential_reference: str,
    protected_dependency: bool,
    protected_dependency_authorized: bool,
    package_policy_reference: str,
    validation_artifact_hash: str,
    validation_suite_reference: str,
    rollback_reference: str,
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the Worker-facing request for one governed dependency operation."""

    record = _validate_dependency_authorization(authorization_record)
    normalized_operation = _operation(operation)
    manager = _package_manager(package_manager)
    ecosystem = SUPPORTED_PACKAGE_MANAGERS[manager]
    protected = bool(protected_dependency)
    protected_authorized = bool(protected_dependency_authorized)
    private = bool(registry_private)
    private_authorized = bool(private_registry_authorized)
    if protected and not protected_authorized:
        raise FailClosedRuntimeError("governed dependency management failed closed: protected dependency authorization required")
    if private and not private_authorized:
        raise FailClosedRuntimeError("governed dependency management failed closed: private registry authorization required")
    dependency = _optional_dependency_name(dependency_name)
    if normalized_operation in PACKAGE_OPERATIONS and dependency is None:
        raise FailClosedRuntimeError("governed dependency management failed closed: dependency identity required")
    registry = _optional_string(registry_url)
    request = {
        "request_type": AUTHORIZED_DEPENDENCY_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": normalized_operation,
        "project_id": _require_string(project_id, "project_id"),
        "project_root": _normalize_project_root(project_root),
        "ecosystem": ecosystem,
        "package_manager": manager,
        "manifest_paths": _normalize_relative_paths(manifest_paths, "manifest_paths"),
        "lockfile_paths": _normalize_relative_paths(lockfile_paths, "lockfile_paths"),
        "dependency_name": dependency,
        "dependency_version": _optional_string(dependency_version),
        "version_constraint": _optional_string(version_constraint),
        "registry_url": registry,
        "registry_fingerprint": replay_hash(registry) if registry else None,
        "registry_private": private,
        "private_registry_authorized": private_authorized,
        "credential_reference": _require_string(credential_reference, "credential_reference"),
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "protected_dependency": protected,
        "protected_dependency_authorized": protected_authorized,
        "package_policy_reference": _require_string(package_policy_reference, "package_policy_reference"),
        "validation_artifact_hash": _require_string(validation_artifact_hash, "validation_artifact_hash"),
        "validation_suite_reference": _require_string(validation_suite_reference, "validation_suite_reference"),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "shell_allowed": False,
        "raw_command_allowed": False,
        "arbitrary_script_allowed": False,
        "global_install_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "git_operation_allowed": False,
        "worker_self_authorized": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_authorized_dependency_management_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a governed dependency request without executing package managers."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized dependency request is required")
    _reject_forbidden_fields(request, "authorized dependency request")
    if request.get("request_type") != AUTHORIZED_DEPENDENCY_REQUEST_TYPE:
        raise FailClosedRuntimeError("authorized dependency request type is invalid")
    if request.get("worker_id") != DEPENDENCY_WORKER_ID:
        raise FailClosedRuntimeError("authorized dependency request Worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_DEPENDENCY_SCOPE:
        raise FailClosedRuntimeError("authorized dependency request scope mismatch")
    operation = _operation(request.get("operation"))
    manager = _package_manager(request.get("package_manager"))
    if request.get("ecosystem") != SUPPORTED_PACKAGE_MANAGERS[manager]:
        raise FailClosedRuntimeError("authorized dependency request ecosystem mismatch")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    _require_string(request.get("project_id"), "project_id")
    _normalize_project_root(request.get("project_root"))
    _normalize_relative_paths(request.get("manifest_paths"), "manifest_paths")
    _normalize_relative_paths(request.get("lockfile_paths"), "lockfile_paths")
    dependency = _optional_dependency_name(request.get("dependency_name"))
    if operation in PACKAGE_OPERATIONS and dependency is None:
        raise FailClosedRuntimeError("authorized dependency request requires dependency identity")
    registry = _optional_string(request.get("registry_url"))
    if registry:
        if request.get("registry_fingerprint") != replay_hash(registry):
            raise FailClosedRuntimeError("authorized dependency request registry fingerprint mismatch")
    elif request.get("registry_fingerprint") is not None:
        raise FailClosedRuntimeError("authorized dependency request registry fingerprint must be absent")
    if request.get("registry_private") is True and request.get("private_registry_authorized") is not True:
        raise FailClosedRuntimeError("authorized dependency request private registry authorization missing")
    if request.get("protected_dependency") is True and request.get("protected_dependency_authorized") is not True:
        raise FailClosedRuntimeError("authorized dependency request protected dependency authorization missing")
    for field in (
        "credential_value_recorded",
        "credential_hash_recorded",
        "shell_allowed",
        "raw_command_allowed",
        "arbitrary_script_allowed",
        "global_install_allowed",
        "deployment_allowed",
        "provider_invocation_allowed",
        "git_operation_allowed",
        "worker_self_authorized",
        "dispatch_performed",
        "orchestration_performed",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError(f"authorized dependency request {field} must be false")
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("authorized dependency request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected = deepcopy(request)
    expected.pop("request_hash")
    if actual_hash != replay_hash(expected):
        raise FailClosedRuntimeError("authorized dependency request hash mismatch")
    if authorization_record is not None:
        record = _validate_dependency_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("authorized dependency request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("authorized dependency request authorization hash mismatch")
    return deepcopy(request)


def execute_dependency_management_request(
    *,
    authorized_request: dict[str, Any],
    repository_root: str | Path,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute exactly one authorized dependency operation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = validate_authorized_dependency_management_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        root = _resolve_project_root(repository_root, request["project_root"])
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


def reconstruct_dependency_management_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker-side governed dependency replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("Dependency Worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("Dependency Worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "Dependency Worker replay artifact")
        wrappers.append(wrapper)
    request = wrappers[0]["artifact"]
    result = wrappers[2]["artifact"]
    if result.get("request_hash") != request.get("request_hash"):
        raise FailClosedRuntimeError("Dependency Worker replay request hash mismatch")
    return {
        "request_id": request["request_id"],
        "authorization_id": request["authorization_id"],
        "operation": request["operation"],
        "project_id": request["project_id"],
        "package_manager": request["package_manager"],
        "dependency_name": request.get("dependency_name"),
        "execution_status": result["execution_status"],
        "exit_code": result["exit_code"],
        "dependency_operation_performed": result["dependency_operation_performed"],
        "repository_files_changed": result["repository_files_changed"],
        "worker_invoked": result["worker_invoked"],
        "validation_executed_by_worker": result["validation_executed_by_worker"],
        "rollback_executed_by_worker": result["rollback_executed_by_worker"],
        "architectural_health_advisory_only": result["architectural_health_advisory_input"]["advisory_only"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _pre_state_artifact(*, request: dict[str, Any], root: Path) -> dict[str, Any]:
    manifest_state = _path_state(root, request["manifest_paths"])
    lockfile_state = _path_state(root, request["lockfile_paths"])
    artifact = {
        "runtime_version": DEPENDENCY_WORKER_VERSION,
        "event_type": DEPENDENCY_PRE_STATE_RECORDED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": request["operation"],
        "project_id": request["project_id"],
        "project_root": str(root),
        "ecosystem": request["ecosystem"],
        "package_manager": request["package_manager"],
        "package_manager_version": _package_manager_version(request["package_manager"], root),
        "dependency_name": request.get("dependency_name"),
        "dependency_version": request.get("dependency_version"),
        "version_constraint": request.get("version_constraint"),
        "manifest_state": manifest_state,
        "lockfile_state": lockfile_state,
        "registry_fingerprint": request.get("registry_fingerprint"),
        "registry_private": request["registry_private"],
        "private_registry_authorized": request["private_registry_authorized"],
        "credential_reference": request["credential_reference"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "protected_dependency": request["protected_dependency"],
        "protected_dependency_authorized": request["protected_dependency_authorized"],
        "package_policy_reference": request["package_policy_reference"],
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_operation(*, request: dict[str, Any], root: Path, pre_state: dict[str, Any]) -> dict[str, Any]:
    operation = request["operation"]
    if operation == OPERATION_DEPENDENCY_INSPECTION:
        argv: list[str] = []
        completed = _synthetic_completed(returncode=0, stdout="dependency inspection completed", stderr="")
        operation_performed = True
    else:
        argv = _dependency_argv(request)
        completed = _run_dependency_command(root, argv)
        operation_performed = completed.returncode == 0
    post_manifest_state = _path_state(root, request["manifest_paths"])
    post_lockfile_state = _path_state(root, request["lockfile_paths"])
    changed_paths = _changed_paths(pre_state["manifest_state"], post_manifest_state)
    changed_paths.extend(_changed_paths(pre_state["lockfile_state"], post_lockfile_state))
    status = "DEPENDENCY_OPERATION_COMPLETED" if completed.returncode == 0 else FAILED_CLOSED
    artifact = {
        "runtime_version": DEPENDENCY_WORKER_VERSION,
        "event_type": DEPENDENCY_WORKER_EXECUTED if completed.returncode == 0 else DEPENDENCY_WORKER_FAILED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "operation": operation,
        "project_id": request["project_id"],
        "ecosystem": request["ecosystem"],
        "package_manager": request["package_manager"],
        "dependency_name": request.get("dependency_name"),
        "dependency_version": request.get("dependency_version"),
        "version_constraint": request.get("version_constraint"),
        "argv": argv,
        "argv_hash": replay_hash(argv),
        "exit_code": completed.returncode,
        "stdout": _bounded_output(completed.stdout),
        "stderr": _bounded_output(completed.stderr),
        "execution_status": status,
        "dependency_operation_performed": operation_performed,
        "repository_files_changed": bool(changed_paths),
        "changed_paths": sorted(set(changed_paths)),
        "pre_manifest_state_hash": replay_hash(pre_state["manifest_state"]),
        "post_manifest_state": post_manifest_state,
        "pre_lockfile_state_hash": replay_hash(pre_state["lockfile_state"]),
        "post_lockfile_state": post_lockfile_state,
        "validation_suite_reference": request["validation_suite_reference"],
        "validation_artifact_hash": request["validation_artifact_hash"],
        "validation_outcome": "VALIDATION_SEQUENCING_REQUIRED_BY_PLATFORM_CORE",
        "rollback_reference": request["rollback_reference"],
        "rollback_prepared": True,
        "worker_invoked": operation != OPERATION_DEPENDENCY_INSPECTION,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "git_operation_performed": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "architectural_health_advisory_input": _architectural_health_advisory_input(request, changed_paths),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _dependency_argv(request: dict[str, Any]) -> list[str]:
    manager = request["package_manager"]
    operation = request["operation"]
    name = request.get("dependency_name")
    if manager == "pip":
        base = [sys.executable, "-m", "pip"]
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return [*base, "install", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            spec = _dependency_spec(request)
            return [*base, "install", "--upgrade", spec]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return [*base, "uninstall", "-y", _require_string(name, "dependency_name")]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return [*base, "check" if operation == OPERATION_DEPENDENCY_VERIFICATION else "--version"]
    if manager == "uv":
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return ["uv", "pip", "install", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            spec = _dependency_spec(request)
            return ["uv", "pip", "install", "--upgrade", spec]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return ["uv", "pip", "uninstall", _require_string(name, "dependency_name")]
        if operation == OPERATION_LOCK_SYNCHRONIZATION:
            return ["uv", "lock"]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return ["uv", "--version"]
    if manager == "poetry":
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return ["poetry", "add", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            return ["poetry", "update", _require_string(name, "dependency_name")]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return ["poetry", "remove", _require_string(name, "dependency_name")]
        if operation == OPERATION_LOCK_SYNCHRONIZATION:
            return ["poetry", "lock"]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return ["poetry", "check" if operation == OPERATION_DEPENDENCY_VERIFICATION else "--version"]
    if manager == "npm":
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return ["npm", "install", "--ignore-scripts", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            return ["npm", "update", "--ignore-scripts", _require_string(name, "dependency_name")]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return ["npm", "uninstall", "--ignore-scripts", _require_string(name, "dependency_name")]
        if operation == OPERATION_LOCK_SYNCHRONIZATION:
            return ["npm", "install", "--package-lock-only", "--ignore-scripts"]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return ["npm", "ls", "--json", "--depth=0"] if operation == OPERATION_DEPENDENCY_VERIFICATION else ["npm", "--version"]
    if manager == "pnpm":
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return ["pnpm", "add", "--ignore-scripts", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            return ["pnpm", "update", "--ignore-scripts", _require_string(name, "dependency_name")]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return ["pnpm", "remove", "--ignore-scripts", _require_string(name, "dependency_name")]
        if operation == OPERATION_LOCK_SYNCHRONIZATION:
            return ["pnpm", "install", "--lockfile-only", "--ignore-scripts"]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return ["pnpm", "list", "--json", "--depth=0"] if operation == OPERATION_DEPENDENCY_VERIFICATION else ["pnpm", "--version"]
    if manager == "yarn":
        if operation == OPERATION_DEPENDENCY_INSTALL:
            spec = _dependency_spec(request)
            return ["yarn", "add", "--ignore-scripts", spec]
        if operation == OPERATION_DEPENDENCY_UPDATE:
            return ["yarn", "upgrade", _require_string(name, "dependency_name")]
        if operation == OPERATION_DEPENDENCY_REMOVAL:
            return ["yarn", "remove", _require_string(name, "dependency_name")]
        if operation == OPERATION_LOCK_SYNCHRONIZATION:
            return ["yarn", "install", "--mode=update-lockfile"]
        if operation in {OPERATION_DEPENDENCY_VERIFICATION, OPERATION_ENVIRONMENT_CONSISTENCY_VERIFICATION}:
            return ["yarn", "list", "--depth=0"] if operation == OPERATION_DEPENDENCY_VERIFICATION else ["yarn", "--version"]
    raise FailClosedRuntimeError("governed dependency management failed closed: unsupported package-manager operation")


def _dependency_spec(request: dict[str, Any]) -> str:
    name = _require_string(request.get("dependency_name"), "dependency_name")
    version = request.get("dependency_version")
    constraint = request.get("version_constraint")
    manager = request["package_manager"]
    if version:
        return f"{name}@{version}" if manager in {"npm", "pnpm", "yarn"} else f"{name}=={version}"
    if constraint:
        return f"{name}@{constraint}" if manager in {"npm", "pnpm", "yarn"} else f"{name}{constraint}"
    return name


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(request)
    artifact["runtime_version"] = DEPENDENCY_WORKER_VERSION
    artifact["event_type"] = DEPENDENCY_REQUEST_CREATED
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": DEPENDENCY_WORKER_VERSION,
        "event_type": DEPENDENCY_WORKER_FAILED,
        "request_id": _safe_field(authorized_request, "request_id"),
        "request_hash": _safe_field(authorized_request, "request_hash"),
        "execution_status": FAILED_CLOSED,
        "failure_reason": _bounded_output(failure_reason),
        "exit_code": 1,
        "dependency_operation_performed": False,
        "repository_files_changed": False,
        "worker_invoked": False,
        "worker_self_authorized": False,
        "orchestration_performed": False,
        "validation_executed_by_worker": False,
        "rollback_executed_by_worker": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "git_operation_performed": False,
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
        "worker_id": DEPENDENCY_WORKER_ID,
        "request_id": request_artifact.get("request_id"),
        "request_hash": request_artifact.get("request_hash"),
        "operation": request_artifact.get("operation"),
        "package_manager": request_artifact.get("package_manager"),
        "dependency_name": request_artifact.get("dependency_name"),
        "execution_status": result_artifact["execution_status"],
        "dependency_operation_performed": result_artifact["dependency_operation_performed"],
        "repository_files_changed": result_artifact["repository_files_changed"],
        "worker_invoked": result_artifact["worker_invoked"],
        "failure_reason": result_artifact.get("failure_reason"),
        "result_hash": result_artifact["artifact_hash"],
        "replay_visible": True,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _validate_dependency_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record.get("worker_id") != DEPENDENCY_WORKER_ID:
        raise FailClosedRuntimeError("Dependency authorization Worker mismatch")
    if record.get("authorization_scope") != AUTHORIZED_DEPENDENCY_SCOPE:
        raise FailClosedRuntimeError("Dependency authorization scope mismatch")
    return record


def _resolve_project_root(repository_root: str | Path, project_root: str) -> Path:
    base = Path(repository_root).resolve()
    root = (base / project_root).resolve()
    if not _is_relative_to(root, base):
        raise FailClosedRuntimeError("governed dependency management failed closed: project root escapes repository")
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("governed dependency management failed closed: project root is unavailable")
    return root


def _path_state(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    state = []
    for relative in paths:
        path = (root / relative).resolve()
        if not _is_relative_to(path, root):
            raise FailClosedRuntimeError("governed dependency management failed closed: path escapes project root")
        exists = path.exists()
        state.append(
            {
                "path": relative,
                "exists": exists,
                "is_file": path.is_file() if exists else False,
                "sha256": _file_sha256(path) if path.is_file() else None,
                "size_bytes": path.stat().st_size if path.is_file() else None,
            }
        )
    return state


def _changed_paths(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[str]:
    before_by_path = {item["path"]: item for item in before}
    changed = []
    for item in after:
        previous = before_by_path.get(item["path"])
        if previous is None or previous.get("sha256") != item.get("sha256") or previous.get("exists") != item.get("exists"):
            changed.append(item["path"])
    return changed


def _package_manager_version(manager: str, root: Path) -> str:
    try:
        if manager == "pip":
            argv = [sys.executable, "-m", "pip", "--version"]
        else:
            argv = [manager, "--version"]
        completed = _run_dependency_command(root, argv, timeout=10)
    except Exception:
        return "UNAVAILABLE"
    if completed.returncode != 0:
        return "UNAVAILABLE"
    return _bounded_output(completed.stdout or completed.stderr, limit=400)


def _run_dependency_command(root: Path, argv: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    if not argv:
        return _synthetic_completed(returncode=0, stdout="", stderr="")
    return subprocess.run(
        argv,
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
        timeout=timeout,
    )


def _synthetic_completed(*, returncode: int, stdout: str, stderr: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _architectural_health_advisory_input(request: dict[str, Any], changed_paths: list[str]) -> dict[str, Any]:
    advisory = {
        "artifact_type": "DEPENDENCY_MANAGEMENT_ARCHITECTURAL_HEALTH_ADVISORY_INPUT_V1",
        "advisory_only": True,
        "architectural_health_authority": False,
        "dependency_consistency_observable": True,
        "version_conflict_observable": True,
        "unsupported_state_observable": True,
        "policy_violation_observable": True,
        "responsibility_preservation_observable": True,
        "operation": request["operation"],
        "package_manager": request["package_manager"],
        "changed_paths": sorted(set(changed_paths)),
        "findings": [],
    }
    advisory["artifact_hash"] = replay_hash(advisory)
    return advisory


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only dependency replay artifact already exists: {path.name}")


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "Dependency artifact")
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
        raise FailClosedRuntimeError("Dependency Worker replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _reject_forbidden_fields(request: dict[str, Any], label: str) -> None:
    present = FORBIDDEN_REQUEST_FIELDS.intersection(request)
    if present:
        raise FailClosedRuntimeError(f"{label} contains forbidden field {sorted(present)[0]}")


def _operation(value: Any) -> str:
    operation = _require_string(value, "operation").strip().upper().replace("-", "_").replace(" ", "_")
    if operation not in AUTHORIZED_OPERATIONS:
        raise FailClosedRuntimeError("governed dependency management failed closed: unsupported operation")
    return operation


def _package_manager(value: Any) -> str:
    manager = _require_string(value, "package_manager").strip().lower()
    if manager not in SUPPORTED_PACKAGE_MANAGERS:
        raise FailClosedRuntimeError("governed dependency management failed closed: unsupported package manager")
    return manager


def _normalize_project_root(value: Any) -> str:
    root = _require_string(value, "project_root").strip()
    if Path(root).is_absolute() or ".." in Path(root).parts:
        raise FailClosedRuntimeError("governed dependency management failed closed: invalid project root")
    return "." if root in {"", "."} else root


def _normalize_relative_paths(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"governed dependency management requires {field}")
    normalized = []
    for item in value:
        relative = _require_string(item, field).strip()
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise FailClosedRuntimeError(f"governed dependency management failed closed: invalid {field}")
        normalized.append(relative)
    return normalized


def _require_json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"governed dependency management requires {field}")
    return deepcopy(value)


def _optional_dependency_name(value: Any) -> str | None:
    text = _optional_string(value)
    if text is None:
        return None
    if text.startswith("-") or any(char.isspace() for char in text):
        raise FailClosedRuntimeError("governed dependency management failed closed: invalid dependency identity")
    return text


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FailClosedRuntimeError("governed dependency management optional string is invalid")
    return value.strip() or None


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed dependency management requires {field}")
    return value.strip()


def _safe_field(value: Any, field: str) -> Any:
    return value.get(field) if isinstance(value, dict) else None


def _bounded_output(value: Any, limit: int = 4000) -> str:
    text = "" if value is None else str(value)
    return text[:limit]


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    if isinstance(exc, subprocess.TimeoutExpired):
        return "governed dependency management failed closed: package manager timeout"
    if isinstance(exc, FileNotFoundError):
        return "governed dependency management failed closed: package manager unavailable"
    return "governed dependency management failed closed"


def _file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
