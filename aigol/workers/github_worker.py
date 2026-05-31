"""Minimal governed GitHub-domain worker for issue draft creation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


GITHUB_WORKER_VERSION = "FIRST_REAL_DOMAIN_WORKER_V1"
GITHUB_WORKER_ID = "GITHUB_ISSUE_DRAFT_WORKER"
AUTHORIZED_WORKER_REQUEST_TYPE = "AUTHORIZED_WORKER_REQUEST_V1"
AUTHORIZED_SCOPE = "GITHUB_CREATE_ISSUE_DRAFT"
OPERATION_CREATE_ISSUE_DRAFT = "CREATE_ISSUE_DRAFT"
GITHUB_WORKER_REQUEST_CREATED = "GITHUB_WORKER_REQUEST_CREATED"
GITHUB_ISSUE_DRAFT_CREATED = "GITHUB_ISSUE_DRAFT_CREATED"
GITHUB_WORKER_FAILED = "GITHUB_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("github_worker_request", "github_worker_result")

_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9_. -]+$")

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_provider_output",
        "raw_proposal",
        "raw_authorization_artifact",
        "github_api_token",
        "github_api_request",
        "api_invocation",
        "network_request",
        "dispatch_request",
        "orchestration_request",
        "planning_request",
        "reflection_request",
        "memory_mutation",
        "replay_mutation",
    }
)


def create_github_issue_draft_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    repository: str,
    issue_title: str,
    issue_body: str,
    labels: list[str],
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the governed request object accepted by the GitHub-domain worker."""

    record = _validate_github_authorization(authorization_record)
    request = {
        "request_type": AUTHORIZED_WORKER_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_CREATE_ISSUE_DRAFT,
        "repository": _validate_repository(repository),
        "issue_title": _require_string(issue_title, "issue_title"),
        "issue_body": _require_string(issue_body, "issue_body"),
        "labels": _validate_labels(labels),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "authorization_hash": record["authorization_hash"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "authority": False,
        "provider_authority": False,
        "proposal_authority": False,
        "governance_authority": False,
        "authorization_authority": False,
        "worker_self_authorized": False,
        "github_api_invoked": False,
        "repository_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_github_issue_draft_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a GitHub-domain authorized request without invoking GitHub."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("github worker request is required")
    _reject_forbidden_fields(request, "github worker request")
    if request.get("request_type") != AUTHORIZED_WORKER_REQUEST_TYPE:
        raise FailClosedRuntimeError("github worker request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    if request.get("worker_id") != GITHUB_WORKER_ID:
        raise FailClosedRuntimeError("github worker request worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_SCOPE:
        raise FailClosedRuntimeError("github worker request scope mismatch")
    if request.get("operation") != OPERATION_CREATE_ISSUE_DRAFT:
        raise FailClosedRuntimeError("github worker request operation is invalid")
    _validate_repository(request.get("repository"))
    _require_string(request.get("issue_title"), "issue_title")
    _require_string(request.get("issue_body"), "issue_body")
    _validate_labels(request.get("labels"))
    _require_string(request.get("request_timestamp"), "request_timestamp")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _require_string(request.get("replay_reference"), "replay_reference")
    for field_name in (
        "authority",
        "provider_authority",
        "proposal_authority",
        "governance_authority",
        "authorization_authority",
        "worker_self_authorized",
        "github_api_invoked",
        "repository_mutated",
        "dispatch_performed",
        "orchestration_performed",
        "planning_performed",
        "multi_step_execution",
    ):
        _require_false(request.get(field_name), field_name)
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("github worker request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("github worker request hash mismatch")
    if authorization_record is not None:
        record = _validate_github_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("github worker request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("github worker request authorization hash mismatch")
    return deepcopy(request)


def execute_github_issue_draft_request(
    *,
    authorized_request: dict[str, Any],
    known_repositories: list[str] | tuple[str, ...] | set[str],
    output_dir: str | Path,
    replay_dir: str | Path,
    worker_available: bool = True,
) -> dict[str, Any]:
    """Create a GitHub issue draft artifact and replay evidence; never calls GitHub."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        if worker_available is not True:
            raise FailClosedRuntimeError("github worker unavailable")
        request = validate_github_issue_draft_request(authorized_request)
        repositories = {_validate_repository(repository) for repository in known_repositories}
        if request["repository"] not in repositories:
            raise FailClosedRuntimeError("unknown repository")
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        target = _issue_draft_path(output_dir=Path(output_dir), request=request)
        issue_draft = _issue_draft_artifact(request=request)
        write_json_immutable(target, issue_draft)
        result = _result_artifact(request=request, request_artifact=request_artifact, target=target, issue_draft=issue_draft)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(failure, result)


def reconstruct_github_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the GitHub-domain worker replay without invoking GitHub."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("github worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("github worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "github worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("github worker replay request hash mismatch")
    if result_artifact.get("request_artifact_hash") != request_artifact.get("artifact_hash"):
        raise FailClosedRuntimeError("github worker replay request artifact mismatch")
    return {
        "proposal_reference": deepcopy(request_artifact["proposal_reference"]),
        "authorization_id": request_artifact["authorization_id"],
        "request_id": request_artifact["request_id"],
        "worker_id": request_artifact["worker_id"],
        "authorized_scope": request_artifact["authorized_scope"],
        "operation": request_artifact["operation"],
        "repository": request_artifact["repository"],
        "worker_action": result_artifact["worker_action"],
        "worker_result": deepcopy(result_artifact["worker_result"]),
        "github_api_invoked": result_artifact["github_api_invoked"],
        "repository_mutated": result_artifact["repository_mutated"],
        "execution_status": result_artifact["execution_status"],
        "replay_visible": True,
        "authority": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_github_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("authorization record must be authorized")
    if record["worker_id"] != GITHUB_WORKER_ID:
        raise FailClosedRuntimeError("authorization record worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_SCOPE:
        raise FailClosedRuntimeError("authorization record scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": GITHUB_WORKER_VERSION,
        "event_type": GITHUB_WORKER_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "repository": request["repository"],
        "issue_title": request["issue_title"],
        "issue_body_hash": replay_hash(request["issue_body"]),
        "labels": deepcopy(request["labels"]),
        "request_timestamp": request["request_timestamp"],
        "github_api_invoked": False,
        "repository_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _issue_draft_artifact(*, request: dict[str, Any]) -> dict[str, Any]:
    issue_draft = {
        "artifact_type": "GITHUB_ISSUE_DRAFT_V1",
        "repository": request["repository"],
        "title": request["issue_title"],
        "body": request["issue_body"],
        "labels": deepcopy(request["labels"]),
        "source_request_id": request["request_id"],
        "source_authorization_id": request["authorization_id"],
        "github_api_invoked": False,
        "repository_mutated": False,
        "replay_visible": True,
    }
    issue_draft["issue_draft_hash"] = replay_hash(issue_draft)
    return issue_draft


def _result_artifact(
    *,
    request: dict[str, Any],
    request_artifact: dict[str, Any],
    target: Path,
    issue_draft: dict[str, Any],
) -> dict[str, Any]:
    artifact = {
        "runtime_version": GITHUB_WORKER_VERSION,
        "event_type": GITHUB_ISSUE_DRAFT_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_artifact_hash": request_artifact["artifact_hash"],
        "authorization_id": request["authorization_id"],
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "repository": request["repository"],
        "worker_action": "created_github_issue_draft_artifact",
        "worker_result": {
            "issue_draft_created": True,
            "issue_draft_path": str(target),
            "issue_draft_hash": issue_draft["issue_draft_hash"],
        },
        "execution_status": "SUCCEEDED",
        "github_api_invoked": False,
        "repository_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, authorized_request: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": GITHUB_WORKER_VERSION,
        "event_type": FAILED_CLOSED,
        "request_id": _safe_field(authorized_request, "request_id", "INVALID_REQUEST"),
        "request_hash": _safe_field(authorized_request, "request_hash", FAILED_CLOSED),
        "authorization_id": _safe_field(authorized_request, "authorization_id", "INVALID_AUTHORIZATION"),
        "authorization_hash": _safe_field(authorized_request, "authorization_hash", FAILED_CLOSED),
        "proposal_reference": _safe_object_field(authorized_request, "proposal_reference"),
        "worker_id": _safe_field(authorized_request, "worker_id", "INVALID_WORKER"),
        "authorized_scope": _safe_field(authorized_request, "authorized_scope", "INVALID_SCOPE"),
        "operation": _safe_field(authorized_request, "operation", "INVALID_OPERATION"),
        "repository": _safe_field(authorized_request, "repository", "INVALID_REPOSITORY"),
        "issue_title": _safe_field(authorized_request, "issue_title", "INVALID_ISSUE_TITLE"),
        "issue_body_hash": FAILED_CLOSED,
        "labels": [],
        "request_timestamp": _safe_field(authorized_request, "request_timestamp", "INVALID_TIMESTAMP"),
        "github_api_invoked": False,
        "repository_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_result(*, failure: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": GITHUB_WORKER_VERSION,
        "event_type": GITHUB_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "request_artifact_hash": failure["artifact_hash"],
        "authorization_id": failure["authorization_id"],
        "worker_id": failure["worker_id"],
        "authorized_scope": failure["authorized_scope"],
        "operation": failure["operation"],
        "repository": failure["repository"],
        "worker_action": "failed_closed",
        "worker_result": {
            "issue_draft_created": False,
            "issue_draft_path": None,
            "issue_draft_hash": FAILED_CLOSED,
        },
        "execution_status": FAILED_CLOSED,
        "github_api_invoked": False,
        "repository_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "authority": False,
        "replay_visible": True,
        "failure_reason": failure["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(request_artifact: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "github_worker_request": deepcopy(request_artifact),
        "github_worker_result": deepcopy(result),
    }
    capture["github_worker_capture_hash"] = replay_hash(capture)
    return capture


def _issue_draft_path(*, output_dir: Path, request: dict[str, Any]) -> Path:
    if not output_dir.exists() or not output_dir.is_dir():
        raise FailClosedRuntimeError("github worker output directory is invalid")
    repository_token = request["repository"].replace("/", "__")
    request_token = request["request_id"].replace("/", "_")
    return output_dir / f"{repository_token}__{request_token}.issue.json"


def _validate_repository(value: Any) -> str:
    repository = _require_string(value, "repository")
    if not _REPOSITORY_PATTERN.match(repository):
        raise FailClosedRuntimeError("repository must be owner/name")
    return repository


def _validate_labels(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError("labels must be a list")
    labels: list[str] = []
    for label in value:
        normalized = _require_string(label, "label")
        if not _LABEL_PATTERN.match(normalized):
            raise FailClosedRuntimeError("label contains invalid characters")
        labels.append(normalized)
    return labels


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only github worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("github worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "github worker artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = _require_string(wrapper.get("replay_hash"), "replay_hash")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("github worker replay hash mismatch")


def _reject_forbidden_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_REQUEST_FIELDS.intersection(value):
            raise FailClosedRuntimeError(f"{label} contains forbidden authority field")
        for nested in value.values():
            _reject_forbidden_fields(nested, label)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_fields(nested, label)


def _require_json_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    replay_hash(value)
    return deepcopy(value)


def _require_false(value: Any, field_name: str) -> None:
    if value is not False:
        raise FailClosedRuntimeError(f"{field_name} must be false")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _safe_field(value: Any, field_name: str, default: str) -> str:
    if isinstance(value, dict):
        field = value.get(field_name)
        if isinstance(field, str) and field.strip():
            return field
    return default


def _safe_object_field(value: Any, field_name: str) -> dict[str, Any]:
    if isinstance(value, dict) and isinstance(value.get(field_name), dict):
        return deepcopy(value[field_name])
    return {}


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "github worker failed closed"

