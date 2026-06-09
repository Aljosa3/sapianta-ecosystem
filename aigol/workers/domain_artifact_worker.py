"""Governed domain artifact authoring worker."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.authorization.authorization_record import AUTHORIZED, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


DOMAIN_ARTIFACT_WORKER_VERSION = "AIGOL_GOVERNED_DOMAIN_ARTIFACT_WORKER_FOUNDATION_V1"
DOMAIN_ARTIFACT_WORKER_ID = "GOVERNED_DOMAIN_ARTIFACT_WORKER"
AUTHORIZED_WORKER_REQUEST_TYPE = "AUTHORIZED_WORKER_REQUEST_V1"
AUTHORIZED_SCOPE = "GOVERNED_DOMAIN_ARTIFACT_AUTHORING"
OPERATION_AUTHOR_DOMAIN_ARTIFACTS = "AUTHOR_DOMAIN_ARTIFACTS"
DOMAIN_ARTIFACT_WORKER_REQUEST_CREATED = "DOMAIN_ARTIFACT_WORKER_REQUEST_CREATED"
DOMAIN_ARTIFACTS_AUTHORED = "DOMAIN_ARTIFACTS_AUTHORED"
DOMAIN_ARTIFACT_WORKER_FAILED = "DOMAIN_ARTIFACT_WORKER_FAILED"
FAILED_CLOSED = "FAILED_CLOSED"

DOMAIN_DEFINITION_ARTIFACT_V1 = "DOMAIN_DEFINITION_ARTIFACT_V1"
DOMAIN_METADATA_ARTIFACT_V1 = "DOMAIN_METADATA_ARTIFACT_V1"
DOMAIN_REGISTRATION_ARTIFACT_V1 = "DOMAIN_REGISTRATION_ARTIFACT_V1"
DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1 = "DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1"

REPLAY_STEPS = ("domain_artifact_worker_request", "domain_artifact_worker_result")

_DOMAIN_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{2,63}$")
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")

FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "raw_provider_output",
        "raw_proposal",
        "raw_authorization_artifact",
        "registry_mutation",
        "live_domain_registry_write",
        "domain_approval",
        "approval_created",
        "authorization_created",
        "worker_invocation",
        "dispatch_request",
        "orchestration_request",
        "planning_request",
        "reflection_request",
        "memory_mutation",
        "replay_mutation",
        "provider_invocation",
        "autonomous_continuation",
    }
)


def create_domain_artifact_request(
    *,
    authorization_record: dict[str, Any],
    request_id: str,
    domain_name: str,
    primary_purpose: str,
    expected_capabilities: list[str],
    target_users: list[str],
    source_clarification_reference: dict[str, Any],
    request_timestamp: str,
    proposal_reference: dict[str, Any],
    replay_reference: str,
) -> dict[str, Any]:
    """Create the governed request object accepted by the domain artifact worker."""

    record = _validate_domain_artifact_authorization(authorization_record)
    request = {
        "request_type": AUTHORIZED_WORKER_REQUEST_TYPE,
        "request_id": _require_string(request_id, "request_id"),
        "authorization_id": record["authorization_id"],
        "proposal_reference": _require_json_object(proposal_reference, "proposal_reference"),
        "worker_id": record["worker_id"],
        "authorized_scope": record["authorization_scope"],
        "operation": OPERATION_AUTHOR_DOMAIN_ARTIFACTS,
        "domain_name": _validate_domain_name(domain_name),
        "primary_purpose": _require_string(primary_purpose, "primary_purpose"),
        "expected_capabilities": _validate_non_empty_string_list(expected_capabilities, "expected_capabilities"),
        "target_users": _validate_non_empty_string_list(target_users, "target_users"),
        "source_clarification_reference": _require_json_object(
            source_clarification_reference,
            "source_clarification_reference",
        ),
        "request_timestamp": _require_string(request_timestamp, "request_timestamp"),
        "authorization_hash": record["authorization_hash"],
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "authority": False,
        "provider_authority": False,
        "proposal_authority": False,
        "governance_authority": False,
        "authorization_authority": False,
        "worker_self_authorized": False,
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return request


def validate_domain_artifact_request(
    request: dict[str, Any],
    *,
    authorization_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a domain artifact request without authoring artifacts."""

    if not isinstance(request, dict):
        raise FailClosedRuntimeError("domain artifact worker request is required")
    _reject_forbidden_fields(request, "domain artifact worker request")
    if request.get("request_type") != AUTHORIZED_WORKER_REQUEST_TYPE:
        raise FailClosedRuntimeError("domain artifact worker request type is invalid")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_id"), "authorization_id")
    _require_json_object(request.get("proposal_reference"), "proposal_reference")
    if request.get("worker_id") != DOMAIN_ARTIFACT_WORKER_ID:
        raise FailClosedRuntimeError("domain artifact worker request worker mismatch")
    if request.get("authorized_scope") != AUTHORIZED_SCOPE:
        raise FailClosedRuntimeError("domain artifact worker request scope mismatch")
    if request.get("operation") != OPERATION_AUTHOR_DOMAIN_ARTIFACTS:
        raise FailClosedRuntimeError("domain artifact worker operation is invalid")
    _validate_domain_name(request.get("domain_name"))
    _require_string(request.get("primary_purpose"), "primary_purpose")
    _validate_non_empty_string_list(request.get("expected_capabilities"), "expected_capabilities")
    _validate_non_empty_string_list(request.get("target_users"), "target_users")
    _require_json_object(request.get("source_clarification_reference"), "source_clarification_reference")
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
        "domain_approved",
        "domain_activated",
        "live_registry_mutated",
        "dispatch_performed",
        "orchestration_performed",
        "planning_performed",
        "multi_step_execution",
    ):
        _require_false(request.get(field_name), field_name)
    if request.get("replay_visible") is not True:
        raise FailClosedRuntimeError("domain artifact worker request must be replay visible")
    actual_hash = _require_string(request.get("request_hash"), "request_hash")
    expected_input = deepcopy(request)
    expected_input.pop("request_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("domain artifact worker request hash mismatch")
    if authorization_record is not None:
        record = _validate_domain_artifact_authorization(authorization_record)
        if request["authorization_id"] != record["authorization_id"]:
            raise FailClosedRuntimeError("domain artifact worker request authorization mismatch")
        if request["authorization_hash"] != record["authorization_hash"]:
            raise FailClosedRuntimeError("domain artifact worker request authorization hash mismatch")
    return deepcopy(request)


def execute_domain_artifact_request(
    *,
    authorized_request: dict[str, Any],
    output_dir: str | Path,
    replay_dir: str | Path,
    worker_available: bool = True,
) -> dict[str, Any]:
    """Author deterministic domain artifacts and replay evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        if worker_available is not True:
            raise FailClosedRuntimeError("domain artifact worker unavailable")
        request = validate_domain_artifact_request(authorized_request)
        request_artifact = _request_replay_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        artifacts = _domain_artifacts(request=request)
        output_paths = _write_domain_artifacts(output_dir=Path(output_dir), request=request, artifacts=artifacts)
        result = _result_artifact(
            request=request,
            request_artifact=request_artifact,
            artifacts=artifacts,
            output_paths=output_paths,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(request_artifact, result)
    except Exception as exc:
        failure = _failure_artifact(authorized_request=authorized_request, failure_reason=_failure_reason(exc))
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        result = _failure_result(failure=failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], result)
        return _capture(failure, result)


def reconstruct_domain_artifact_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct domain artifact worker replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain artifact worker replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain artifact worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain artifact worker replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    result_artifact = wrappers[1]["artifact"]
    if result_artifact.get("request_hash") != request_artifact.get("request_hash"):
        raise FailClosedRuntimeError("domain artifact worker replay request hash mismatch")
    if result_artifact.get("request_artifact_hash") != request_artifact.get("artifact_hash"):
        raise FailClosedRuntimeError("domain artifact worker replay request artifact mismatch")
    return {
        "proposal_reference": deepcopy(request_artifact["proposal_reference"]),
        "authorization_id": request_artifact["authorization_id"],
        "request_id": request_artifact["request_id"],
        "worker_id": request_artifact["worker_id"],
        "authorized_scope": request_artifact["authorized_scope"],
        "operation": request_artifact["operation"],
        "domain_name": request_artifact["domain_name"],
        "worker_action": result_artifact["worker_action"],
        "worker_result": deepcopy(result_artifact["worker_result"]),
        "artifact_hashes": deepcopy(result_artifact["artifact_hashes"]),
        "execution_status": result_artifact["execution_status"],
        "domain_approved": result_artifact["domain_approved"],
        "domain_activated": result_artifact["domain_activated"],
        "live_registry_mutated": result_artifact["live_registry_mutated"],
        "provider_invoked": result_artifact["provider_invoked"],
        "worker_invoked": result_artifact["worker_invoked"],
        "replay_visible": True,
        "authority": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_domain_artifact_authorization(authorization_record: dict[str, Any]) -> dict[str, Any]:
    record = validate_authorization_record(authorization_record)
    if record["authorization_status"] != AUTHORIZED:
        raise FailClosedRuntimeError("authorization record must be authorized")
    if record["worker_id"] != DOMAIN_ARTIFACT_WORKER_ID:
        raise FailClosedRuntimeError("authorization record worker mismatch")
    if record["authorization_scope"] != AUTHORIZED_SCOPE:
        raise FailClosedRuntimeError("authorization record scope mismatch")
    return record


def _request_replay_artifact(request: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "runtime_version": DOMAIN_ARTIFACT_WORKER_VERSION,
        "event_type": DOMAIN_ARTIFACT_WORKER_REQUEST_CREATED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "domain_name": request["domain_name"],
        "primary_purpose_hash": replay_hash(request["primary_purpose"]),
        "expected_capabilities_hash": replay_hash(request["expected_capabilities"]),
        "target_users_hash": replay_hash(request["target_users"]),
        "source_clarification_reference": deepcopy(request["source_clarification_reference"]),
        "request_timestamp": request["request_timestamp"],
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "orchestration_performed": False,
        "planning_performed": False,
        "multi_step_execution": False,
        "authority": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _domain_artifacts(*, request: dict[str, Any]) -> dict[str, dict[str, Any]]:
    definition = {
        "artifact_type": DOMAIN_DEFINITION_ARTIFACT_V1,
        "domain_name": request["domain_name"],
        "primary_purpose": request["primary_purpose"],
        "expected_capabilities": deepcopy(request["expected_capabilities"]),
        "target_users": deepcopy(request["target_users"]),
        "source_request_id": request["request_id"],
        "source_authorization_id": request["authorization_id"],
        "source_clarification_reference": deepcopy(request["source_clarification_reference"]),
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "replay_visible": True,
    }
    definition["domain_definition_hash"] = replay_hash(definition)

    metadata = {
        "artifact_type": DOMAIN_METADATA_ARTIFACT_V1,
        "domain_name": request["domain_name"],
        "domain_slug": _domain_slug(request["domain_name"]),
        "domain_status": "DOMAIN_ARTIFACT_CANDIDATE",
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "created_at": request["request_timestamp"],
        "definition_hash": definition["domain_definition_hash"],
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "replay_visible": True,
    }
    metadata["domain_metadata_hash"] = replay_hash(metadata)

    registration = {
        "artifact_type": DOMAIN_REGISTRATION_ARTIFACT_V1,
        "domain_name": request["domain_name"],
        "registration_status": "REGISTRATION_CANDIDATE_CREATED",
        "registration_authority_granted": False,
        "domain_definition_hash": definition["domain_definition_hash"],
        "domain_metadata_hash": metadata["domain_metadata_hash"],
        "source_authorization_id": request["authorization_id"],
        "source_request_id": request["request_id"],
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "replay_visible": True,
    }
    registration["domain_registration_hash"] = replay_hash(registration)

    governance_evidence = {
        "artifact_type": DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1,
        "domain_name": request["domain_name"],
        "evidence_status": "DOMAIN_ARTIFACT_AUTHORING_RECORDED",
        "proposal_reference": deepcopy(request["proposal_reference"]),
        "authorization_id": request["authorization_id"],
        "authorization_hash": request["authorization_hash"],
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "source_clarification_reference": deepcopy(request["source_clarification_reference"]),
        "definition_hash": definition["domain_definition_hash"],
        "metadata_hash": metadata["domain_metadata_hash"],
        "registration_hash": registration["domain_registration_hash"],
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authority": False,
        "replay_visible": True,
    }
    governance_evidence["domain_governance_evidence_hash"] = replay_hash(governance_evidence)

    return {
        "domain_definition": definition,
        "domain_metadata": metadata,
        "domain_registration": registration,
        "governance_evidence": governance_evidence,
    }


def _write_domain_artifacts(
    *,
    output_dir: Path,
    request: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
) -> dict[str, str]:
    if not output_dir.exists() or not output_dir.is_dir():
        raise FailClosedRuntimeError("domain artifact worker output directory is invalid")
    slug = _domain_slug(request["domain_name"])
    request_token = request["request_id"].replace("/", "_")
    paths = {
        "domain_definition_path": output_dir / f"{slug}__{request_token}.definition.json",
        "domain_metadata_path": output_dir / f"{slug}__{request_token}.metadata.json",
        "domain_registration_path": output_dir / f"{slug}__{request_token}.registration.json",
        "governance_evidence_path": output_dir / f"{slug}__{request_token}.governance-evidence.json",
    }
    write_json_immutable(paths["domain_definition_path"], artifacts["domain_definition"])
    write_json_immutable(paths["domain_metadata_path"], artifacts["domain_metadata"])
    write_json_immutable(paths["domain_registration_path"], artifacts["domain_registration"])
    write_json_immutable(paths["governance_evidence_path"], artifacts["governance_evidence"])
    return {key: str(path) for key, path in paths.items()}


def _result_artifact(
    *,
    request: dict[str, Any],
    request_artifact: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    output_paths: dict[str, str],
) -> dict[str, Any]:
    artifact = {
        "runtime_version": DOMAIN_ARTIFACT_WORKER_VERSION,
        "event_type": DOMAIN_ARTIFACTS_AUTHORED,
        "request_id": request["request_id"],
        "request_hash": request["request_hash"],
        "request_artifact_hash": request_artifact["artifact_hash"],
        "authorization_id": request["authorization_id"],
        "worker_id": request["worker_id"],
        "authorized_scope": request["authorized_scope"],
        "operation": request["operation"],
        "domain_name": request["domain_name"],
        "worker_action": "authored_governed_domain_artifacts",
        "worker_result": {
            "domain_definition_created": True,
            "domain_metadata_created": True,
            "domain_registration_created": True,
            "governance_evidence_created": True,
            **deepcopy(output_paths),
        },
        "artifact_hashes": {
            "domain_definition_hash": artifacts["domain_definition"]["domain_definition_hash"],
            "domain_metadata_hash": artifacts["domain_metadata"]["domain_metadata_hash"],
            "domain_registration_hash": artifacts["domain_registration"]["domain_registration_hash"],
            "domain_governance_evidence_hash": artifacts["governance_evidence"]["domain_governance_evidence_hash"],
        },
        "execution_status": "SUCCEEDED",
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
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
        "runtime_version": DOMAIN_ARTIFACT_WORKER_VERSION,
        "event_type": FAILED_CLOSED,
        "request_id": _safe_field(authorized_request, "request_id", "INVALID_REQUEST"),
        "request_hash": _safe_field(authorized_request, "request_hash", FAILED_CLOSED),
        "authorization_id": _safe_field(authorized_request, "authorization_id", "INVALID_AUTHORIZATION"),
        "authorization_hash": _safe_field(authorized_request, "authorization_hash", FAILED_CLOSED),
        "proposal_reference": _safe_object_field(authorized_request, "proposal_reference"),
        "worker_id": _safe_field(authorized_request, "worker_id", "INVALID_WORKER"),
        "authorized_scope": _safe_field(authorized_request, "authorized_scope", "INVALID_SCOPE"),
        "operation": _safe_field(authorized_request, "operation", "INVALID_OPERATION"),
        "domain_name": _safe_field(authorized_request, "domain_name", "INVALID_DOMAIN"),
        "primary_purpose_hash": FAILED_CLOSED,
        "expected_capabilities_hash": FAILED_CLOSED,
        "target_users_hash": FAILED_CLOSED,
        "source_clarification_reference": _safe_object_field(authorized_request, "source_clarification_reference"),
        "request_timestamp": _safe_field(authorized_request, "request_timestamp", "INVALID_TIMESTAMP"),
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
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
        "runtime_version": DOMAIN_ARTIFACT_WORKER_VERSION,
        "event_type": DOMAIN_ARTIFACT_WORKER_FAILED,
        "request_id": failure["request_id"],
        "request_hash": failure["request_hash"],
        "request_artifact_hash": failure["artifact_hash"],
        "authorization_id": failure["authorization_id"],
        "worker_id": failure["worker_id"],
        "authorized_scope": failure["authorized_scope"],
        "operation": failure["operation"],
        "domain_name": failure["domain_name"],
        "worker_action": "failed_closed",
        "worker_result": {
            "domain_definition_created": False,
            "domain_metadata_created": False,
            "domain_registration_created": False,
            "governance_evidence_created": False,
            "domain_definition_path": None,
            "domain_metadata_path": None,
            "domain_registration_path": None,
            "governance_evidence_path": None,
        },
        "artifact_hashes": {
            "domain_definition_hash": FAILED_CLOSED,
            "domain_metadata_hash": FAILED_CLOSED,
            "domain_registration_hash": FAILED_CLOSED,
            "domain_governance_evidence_hash": FAILED_CLOSED,
        },
        "execution_status": FAILED_CLOSED,
        "domain_approved": False,
        "domain_activated": False,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
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
        "domain_artifact_worker_request": deepcopy(request_artifact),
        "domain_artifact_worker_result": deepcopy(result),
    }
    capture["domain_artifact_worker_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only domain artifact worker artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("domain artifact worker replay step ordering mismatch")
    _verify_artifact_hash(artifact, "domain artifact worker artifact")
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
        raise FailClosedRuntimeError("domain artifact worker replay hash mismatch")


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


def _validate_domain_name(value: Any) -> str:
    domain_name = _require_string(value, "domain_name")
    if not _DOMAIN_NAME_PATTERN.match(domain_name):
        raise FailClosedRuntimeError("domain_name contains invalid characters")
    return domain_name


def _validate_non_empty_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} must be a non-empty list")
    normalized: list[str] = []
    for item in value:
        normalized.append(_require_string(item, field_name))
    return normalized


def _domain_slug(domain_name: str) -> str:
    token = _validate_domain_name(domain_name).lower().replace("_", "-")
    if not _TOKEN_PATTERN.match(token):
        raise FailClosedRuntimeError("domain slug contains invalid characters")
    return token


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
    return "domain artifact worker failed closed"

