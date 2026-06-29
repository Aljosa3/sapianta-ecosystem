"""Deterministic provider identity and credential boundary runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_IDENTITY_BOUNDARY_RUNTIME_VERSION = (
    "G3_04_IMPLEMENTATION_PHASE_1_PROVIDER_IDENTITY_AND_CREDENTIAL_BOUNDARIES_RUNTIME_V1"
)
PROVIDER_CREDENTIAL_REFERENCE_ARTIFACT_V1 = "PROVIDER_CREDENTIAL_REFERENCE_ARTIFACT_V1"
PROVIDER_IDENTITY_ARTIFACT_V1 = "PROVIDER_IDENTITY_ARTIFACT_V1"

EVENT_PROVIDER_CREDENTIAL_REFERENCE_CREATED = "provider_credential_reference_created"
EVENT_PROVIDER_IDENTITY_CREATED = "provider_identity_created"

PROVIDER_IDENTITY_CREATED = "PROVIDER_IDENTITY_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

COGNITION_PROVIDER = "COGNITION_PROVIDER"
TRANSLATION_WORKER = "TRANSLATION_WORKER"
REPAIR_WORKER = "REPAIR_WORKER"

CREDENTIAL_NOT_CONFIGURED = "CREDENTIAL_NOT_CONFIGURED"
CREDENTIAL_CONFIGURED_INACTIVE = "CREDENTIAL_CONFIGURED_INACTIVE"
CREDENTIAL_ACTIVE_ADVISORY_ONLY = "CREDENTIAL_ACTIVE_ADVISORY_ONLY"
CREDENTIAL_SUSPENDED = "CREDENTIAL_SUSPENDED"
CREDENTIAL_RETIRED = "CREDENTIAL_RETIRED"

PROVIDER_REGISTERED_INACTIVE = "PROVIDER_REGISTERED_INACTIVE"
PROVIDER_ACTIVE_ADVISORY_ONLY = "PROVIDER_ACTIVE_ADVISORY_ONLY"
PROVIDER_SUSPENDED = "PROVIDER_SUSPENDED"
PROVIDER_RETIRED = "PROVIDER_RETIRED"

PROVIDER_ROLES = {
    COGNITION_PROVIDER,
    TRANSLATION_WORKER,
    REPAIR_WORKER,
    "ACLI_CONVERSATIONAL_ASSISTANT",
    "OCS_ADVISORY_COGNITION",
    "PRODUCT1_DECISION_SUPPORT",
    "REPLAY_EXPLANATION_ASSISTANT",
    "PROVIDER_COMPARISON_EVALUATOR",
}

CREDENTIAL_LIFECYCLE_STATES = {
    CREDENTIAL_NOT_CONFIGURED,
    CREDENTIAL_CONFIGURED_INACTIVE,
    CREDENTIAL_ACTIVE_ADVISORY_ONLY,
    CREDENTIAL_SUSPENDED,
    CREDENTIAL_RETIRED,
}

PROVIDER_ACTIVATION_STATUSES = {
    PROVIDER_REGISTERED_INACTIVE,
    PROVIDER_ACTIVE_ADVISORY_ONLY,
    PROVIDER_SUSPENDED,
    PROVIDER_RETIRED,
}

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "api_key",
    "apikey",
    "authorization:",
    "authorization_header:",
    "OPENAI_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
)

NON_AUTHORITY_FLAGS = (
    "provider_invoked",
    "provider_selection_performed",
    "provider_request_created",
    "provider_response_received",
    "worker_invoked",
    "approval_created",
    "authorization_created",
    "execution_requested",
    "repository_mutated",
    "deployment_requested",
    "external_integration_invoked",
)


def create_provider_credential_reference(
    *,
    credential_reference_id: str,
    credential_reference: str,
    credential_role: str,
    credential_lifecycle_state: str,
    secret_present: bool,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a secret-free provider credential reference artifact."""

    lifecycle_state = _require_one_of(
        credential_lifecycle_state,
        CREDENTIAL_LIFECYCLE_STATES,
        "credential_lifecycle_state",
    )
    role = _require_one_of(credential_role, PROVIDER_ROLES, "credential_role")
    reference = _require_string(credential_reference, "credential_reference")
    if secret_present is True or _looks_like_secret(reference):
        raise FailClosedRuntimeError("provider identity boundary failed closed: credential secret must not be replayed")
    event = _event(
        event_index=0,
        event_type=EVENT_PROVIDER_CREDENTIAL_REFERENCE_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "credential_reference_id": _require_string(credential_reference_id, "credential_reference_id"),
            "credential_role": role,
            "credential_lifecycle_state": lifecycle_state,
        },
    )
    artifact = {
        "artifact_type": PROVIDER_CREDENTIAL_REFERENCE_ARTIFACT_V1,
        "runtime_version": PROVIDER_IDENTITY_BOUNDARY_RUNTIME_VERSION,
        "migration_batch_id": "G3_04_IMPLEMENTATION_PHASE_1_PROVIDER_IDENTITY_AND_CREDENTIAL_BOUNDARIES_V1",
        "credential_reference_id": _require_string(credential_reference_id, "credential_reference_id"),
        "credential_reference": reference,
        "credential_role": role,
        "credential_lifecycle_state": lifecycle_state,
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "secret_material_present": False,
        "secret_present_input": False,
        "reference_only": True,
        "role_separated": True,
        "replay_lineage": [
            {
                "replay_reference": f"credential_reference:{_require_string(credential_reference_id, 'credential_reference_id')}",
                "replay_hash": replay_hash({"credential_reference_id": credential_reference_id, "role": role}),
            }
        ],
        "rollback_reference": f"rollback:credential_reference:{credential_reference_id}",
        "provider_invoked": False,
        "provider_selection_performed": False,
        "provider_request_created": False,
        "provider_response_received": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "event": event,
        "failure_reason": None,
    }
    _assert_secret_safe(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(Path(replay_dir), 0, EVENT_PROVIDER_CREDENTIAL_REFERENCE_CREATED, artifact)
    return _capture_credential(artifact, Path(replay_dir))


def create_provider_identity(
    *,
    provider_id: str,
    external_provider_family: str,
    model_id: str,
    provider_role: str,
    capability_declarations: list[dict[str, Any]],
    credential_reference_artifact: dict[str, Any],
    activation_status: str,
    replay_lineage: list[dict[str, Any]],
    rollback_reference: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a deterministic provider identity bound to a credential reference."""

    credential = _validated_credential_reference(credential_reference_artifact)
    role = _require_one_of(provider_role, PROVIDER_ROLES, "provider_role")
    if credential["credential_role"] != role:
        raise FailClosedRuntimeError("provider identity boundary failed closed: credential role does not match provider role")
    status = _require_one_of(activation_status, PROVIDER_ACTIVATION_STATUSES, "activation_status")
    capabilities = _normalize_capabilities(capability_declarations)
    lineage = _provider_replay_lineage(replay_lineage, credential, provider_id, capabilities)
    event = _event(
        event_index=0,
        event_type=EVENT_PROVIDER_IDENTITY_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "provider_id": _require_string(provider_id, "provider_id"),
            "external_provider_family": _require_string(external_provider_family, "external_provider_family"),
            "provider_role": role,
            "credential_reference_id": credential["credential_reference_id"],
            "activation_status": status,
            "capability_count": len(capabilities),
        },
    )
    artifact = {
        "artifact_type": PROVIDER_IDENTITY_ARTIFACT_V1,
        "runtime_version": PROVIDER_IDENTITY_BOUNDARY_RUNTIME_VERSION,
        "migration_batch_id": "G3_04_IMPLEMENTATION_PHASE_1_PROVIDER_IDENTITY_AND_CREDENTIAL_BOUNDARIES_V1",
        "provider_id": _require_string(provider_id, "provider_id"),
        "provider_status": PROVIDER_IDENTITY_CREATED,
        "external_provider_family": _require_string(external_provider_family, "external_provider_family"),
        "model_id": _require_string(model_id, "model_id"),
        "provider_role": role,
        "capability_declarations": capabilities,
        "capability_count": len(capabilities),
        "capability_declarations_hash": replay_hash(capabilities),
        "credential_reference_id": credential["credential_reference_id"],
        "credential_reference": credential["credential_reference"],
        "credential_reference_hash": credential["artifact_hash"],
        "credential_lifecycle_state": credential["credential_lifecycle_state"],
        "activation_status": status,
        "provider_identity_created": True,
        "provider_role_identity_created": True,
        "credential_boundary_recorded": True,
        "credential_reference_only": True,
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "secret_material_present": False,
        "replay_lineage": lineage,
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "source_credential_reference": deepcopy(credential),
        "provider_invoked": False,
        "provider_selection_performed": False,
        "provider_request_created": False,
        "provider_response_received": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "event": event,
        "failure_reason": None,
    }
    _assert_secret_safe(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(Path(replay_dir), 0, EVENT_PROVIDER_IDENTITY_CREATED, artifact)
    return _capture_provider(artifact, Path(replay_dir))


def reconstruct_provider_identity_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider identity or credential reference replay evidence."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("provider identity boundary failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("provider identity boundary replay ordering mismatch")
    artifact = wrappers[-1]["artifact"]
    if artifact.get("artifact_type") == PROVIDER_CREDENTIAL_REFERENCE_ARTIFACT_V1:
        credential = _validated_credential_reference(artifact)
        return {
            "artifact_type": credential["artifact_type"],
            "credential_reference_id": credential["credential_reference_id"],
            "credential_role": credential["credential_role"],
            "credential_lifecycle_state": credential["credential_lifecycle_state"],
            "credential_secret_stored": False,
            "credential_secret_replayed": False,
            "secret_material_present": False,
            "replay_lineage_count": len(credential["replay_lineage"]),
            "artifact_hash": credential["artifact_hash"],
            "replay_hash": replay_hash(wrappers),
        }
    provider = _validated_provider_identity(artifact)
    return {
        "artifact_type": provider["artifact_type"],
        "provider_id": provider["provider_id"],
        "provider_status": provider["provider_status"],
        "external_provider_family": provider["external_provider_family"],
        "model_id": provider["model_id"],
        "provider_role": provider["provider_role"],
        "capability_count": provider["capability_count"],
        "credential_reference_id": provider["credential_reference_id"],
        "credential_lifecycle_state": provider["credential_lifecycle_state"],
        "activation_status": provider["activation_status"],
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "secret_material_present": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "replay_lineage_count": len(provider["replay_lineage"]),
        "rollback_reference": provider["rollback_reference"],
        "artifact_hash": provider["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _validated_credential_reference(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider identity boundary failed closed: credential artifact must be object")
    if artifact.get("artifact_type") != PROVIDER_CREDENTIAL_REFERENCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider identity boundary failed closed: invalid credential artifact")
    _verify_hash_field(artifact, "artifact_hash", "provider identity boundary credential hash mismatch")
    _assert_secret_safe(artifact)
    if artifact.get("reference_only") is not True:
        raise FailClosedRuntimeError("provider identity boundary failed closed: credential must be reference only")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"provider identity boundary failed closed: {flag} must be false")
    for field in ("credential_secret_stored", "credential_secret_replayed", "credential_value_recorded", "credential_hash_recorded", "secret_material_present"):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"provider identity boundary failed closed: {field} must be false")
    _require_one_of(artifact.get("credential_role"), PROVIDER_ROLES, "credential_role")
    _require_one_of(artifact.get("credential_lifecycle_state"), CREDENTIAL_LIFECYCLE_STATES, "credential_lifecycle_state")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_provider_identity(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider identity boundary failed closed: provider artifact must be object")
    if artifact.get("artifact_type") != PROVIDER_IDENTITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("provider identity boundary failed closed: invalid provider artifact")
    _verify_hash_field(artifact, "artifact_hash", "provider identity boundary provider hash mismatch")
    _assert_secret_safe(artifact)
    if artifact.get("provider_status") != PROVIDER_IDENTITY_CREATED:
        raise FailClosedRuntimeError("provider identity boundary failed closed: provider identity is not created")
    if artifact.get("credential_reference_only") is not True:
        raise FailClosedRuntimeError("provider identity boundary failed closed: credential must be reference only")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"provider identity boundary failed closed: {flag} must be false")
    for field in ("credential_secret_stored", "credential_secret_replayed", "secret_material_present"):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"provider identity boundary failed closed: {field} must be false")
    _require_one_of(artifact.get("provider_role"), PROVIDER_ROLES, "provider_role")
    _require_one_of(artifact.get("credential_lifecycle_state"), CREDENTIAL_LIFECYCLE_STATES, "credential_lifecycle_state")
    _require_one_of(artifact.get("activation_status"), PROVIDER_ACTIVATION_STATUSES, "activation_status")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _normalize_capabilities(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("provider identity boundary failed closed: capability declarations are required")
    capabilities = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("provider identity boundary failed closed: capability item must be object")
        capability_id = _require_string(item.get("capability_id"), "capability_id")
        if capability_id in seen_ids:
            raise FailClosedRuntimeError("provider identity boundary failed closed: duplicate capability id")
        seen_ids.add(capability_id)
        record = {
            "capability_index": index,
            "capability_id": capability_id,
            "capability": _require_string(item.get("capability"), "capability"),
            "capability_scope": _require_string(item.get("capability_scope"), "capability_scope"),
            "advisory_only": item.get("advisory_only") is True,
            "execution_authority": item.get("execution_authority") is True,
        }
        if record["advisory_only"] is not True:
            raise FailClosedRuntimeError("provider identity boundary failed closed: capability must be advisory only")
        if record["execution_authority"] is not False:
            raise FailClosedRuntimeError("provider identity boundary failed closed: capability must not grant execution authority")
        record["capability_hash"] = replay_hash(record)
        capabilities.append(record)
    return capabilities


def _provider_replay_lineage(
    value: Any,
    credential: dict[str, Any],
    provider_id: str,
    capabilities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lineage = _normalize_replay_lineage(value)
    lineage.append(
        {
            "replay_reference": f"credential_reference:{credential['credential_reference_id']}",
            "replay_hash": credential["artifact_hash"],
        }
    )
    lineage.append(
        {
            "replay_reference": f"provider_identity:{_require_string(provider_id, 'provider_id')}",
            "replay_hash": replay_hash({"provider_id": provider_id, "capability_hash": replay_hash(capabilities)}),
        }
    )
    return _normalize_replay_lineage(lineage)


def _event(
    *,
    event_index: int,
    event_type: str,
    occurred_at: str,
    previous_event_hash: str,
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "previous_event_hash": previous_event_hash,
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "provider_selection_performed": False,
        "provider_request_created": False,
        "provider_response_received": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("provider identity boundary failed closed: replay already exists")
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _load_verified_wrapper(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    _verify_hash_field(wrapper, "replay_hash", "provider identity boundary replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider identity boundary replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "provider identity boundary artifact hash mismatch")
    return wrapper


def _verify_hash_field(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _capture_credential(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PROVIDER_IDENTITY_BOUNDARY_RUNTIME_VERSION,
        "credential_reference_artifact": deepcopy(artifact),
        "credential_reference_id": artifact["credential_reference_id"],
        "credential_role": artifact["credential_role"],
        "credential_lifecycle_state": artifact["credential_lifecycle_state"],
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "secret_material_present": False,
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _capture_provider(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PROVIDER_IDENTITY_BOUNDARY_RUNTIME_VERSION,
        "provider_identity_artifact": deepcopy(artifact),
        "provider_id": artifact["provider_id"],
        "provider_role": artifact["provider_role"],
        "external_provider_family": artifact["external_provider_family"],
        "model_id": artifact["model_id"],
        "credential_reference_id": artifact["credential_reference_id"],
        "credential_lifecycle_state": artifact["credential_lifecycle_state"],
        "activation_status": artifact["activation_status"],
        "capability_count": artifact["capability_count"],
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "secret_material_present": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _normalize_replay_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("provider identity boundary failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("provider identity boundary failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _assert_secret_safe(value: Any) -> None:
    serialized = repr(value)
    lowered = serialized.lower()
    for marker in SECRET_MARKERS:
        if marker in serialized or marker.lower() in lowered:
            raise FailClosedRuntimeError("provider identity boundary failed closed: secret material detected")


def _looks_like_secret(value: str) -> bool:
    lowered = value.lower()
    return any(marker in value or marker.lower() in lowered for marker in SECRET_MARKERS)


def _require_one_of(value: Any, allowed: set[str], field_name: str) -> str:
    text = _require_string(value, field_name)
    if text not in allowed:
        raise FailClosedRuntimeError(f"provider identity boundary failed closed: invalid {field_name}")
    return text


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"provider identity boundary failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"provider identity boundary failed closed: {field_name} must be replay hash")
    return text
