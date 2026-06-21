"""Provider governance runtime for AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import os
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1"

PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1 = "PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1"
PROVIDER_USAGE_METRIC_ARTIFACT_V1 = "PROVIDER_USAGE_METRIC_ARTIFACT_V1"
COGNITION_PARTICIPATION_ARTIFACT_V1 = "COGNITION_PARTICIPATION_ARTIFACT_V1"

ADD = "ADD"
ENABLE = "ENABLE"
DISABLE = "DISABLE"
ROTATE = "ROTATE"
REPLACE = "REPLACE"
DELETE = "DELETE"
VERIFY = "VERIFY"
LIFECYCLE_OPERATIONS = {ADD, ENABLE, DISABLE, ROTATE, REPLACE, DELETE, VERIFY}
APPROVAL_REQUIRED_OPERATIONS = {DISABLE, ROTATE, REPLACE, DELETE}
ACTIVE = "ACTIVE"
DISABLED = "DISABLED"
DELETED = "DELETED"

PARTICIPATION_LOCATIONS = {
    "HIRR",
    "OCS_LLM_COGNITION",
    "REPLAY_ANALYSIS",
    "IMPROVEMENT_PROPOSAL",
    "WORKER_GENERATION",
    "WORKER_REPAIR",
    "HUMAN_RESPONSE_ASSISTANCE",
}

PROVIDER_CREDENTIAL_REGISTRY_VERSION = "AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1"
PROVIDER_REGISTRY: dict[str, dict[str, Any]] = {
    "openai": {
        "provider_id": "openai",
        "provider_aliases": ["openai"],
        "provider_resource_type": "COGNITION_PROVIDER",
        "credential_class": "API_KEY",
        "credential_reference": "env:AIGOL_OPENAI_API_KEY",
        "credential_source_type": "ENVIRONMENT_VARIABLE",
        "status": "ACTIVE_FOR_FIRST_LIVE_CERTIFICATION",
    },
    "claude": {
        "provider_id": "claude",
        "provider_aliases": ["anthropic", "claude"],
        "provider_resource_type": "COGNITION_PROVIDER",
        "credential_class": "API_KEY",
        "credential_reference": "env:AIGOL_ANTHROPIC_API_KEY",
        "credential_source_type": "ENVIRONMENT_VARIABLE",
        "status": "REFERENCE_DEFINED_NOT_LIVE_CERTIFIED",
    },
    "gemini": {
        "provider_id": "gemini",
        "provider_aliases": ["google_gemini", "gemini"],
        "provider_resource_type": "COGNITION_PROVIDER",
        "credential_class": "API_KEY",
        "credential_reference": "env:AIGOL_GEMINI_API_KEY",
        "credential_source_type": "ENVIRONMENT_VARIABLE",
        "status": "REFERENCE_DEFINED_NOT_LIVE_CERTIFIED",
    },
    "mistral": {
        "provider_id": "mistral",
        "provider_aliases": ["mistral"],
        "provider_resource_type": "COGNITION_PROVIDER",
        "credential_class": "API_KEY",
        "credential_reference": "env:AIGOL_MISTRAL_API_KEY",
        "credential_source_type": "ENVIRONMENT_VARIABLE",
        "status": "REFERENCE_DEFINED_NOT_LIVE_CERTIFIED",
    },
}

SECRET_MARKERS = ("sk-", "Bearer ", "AIGOL_OPENAI_API_KEY=", "OPENAI_API_KEY=", "ANTHROPIC_API_KEY=")


def provider_credential_registry() -> dict[str, dict[str, Any]]:
    return deepcopy(PROVIDER_REGISTRY)


def execute_provider_lifecycle_operation(
    *,
    event_id: str,
    operation: str,
    provider_id: str,
    requested_by: str,
    created_at: str,
    replay_dir: str | Path | None = None,
    human_approval_artifact: dict[str, Any] | None = None,
    reason: str = "",
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Record one provider lifecycle governance event."""

    normalized_operation = _operation(operation)
    provider = _provider(provider_id)
    if normalized_operation in APPROVAL_REQUIRED_OPERATIONS:
        _require_human_approval(normalized_operation, human_approval_artifact)
    credential_diagnostic = build_provider_credential_diagnostic(provider_id=provider["provider_id"], env=env)
    lifecycle_status = _lifecycle_status(normalized_operation)
    event = {
        "artifact_type": PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "registry_version": PROVIDER_CREDENTIAL_REGISTRY_VERSION,
        "event_id": _require_string(event_id, "event_id"),
        "operation": normalized_operation,
        "provider_id": provider["provider_id"],
        "provider_aliases": provider["provider_aliases"],
        "provider_resource_type": provider["provider_resource_type"],
        "credential_reference": provider["credential_reference"],
        "credential_source_type": provider["credential_source_type"],
        "credential_display_identifier": credential_diagnostic["credential_display_identifier"],
        "credential_present": credential_diagnostic["credential_present"],
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "credential_contents_recorded": False,
        "authorization_header_recorded": False,
        "human_approval_required": normalized_operation in APPROVAL_REQUIRED_OPERATIONS,
        "human_approval_recorded": human_approval_artifact is not None,
        "human_approval_artifact_hash": human_approval_artifact.get("artifact_hash") if human_approval_artifact else None,
        "requested_by": _require_string(requested_by, "requested_by"),
        "reason": _optional_string(reason),
        "lifecycle_status": lifecycle_status,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    event["artifact_hash"] = replay_hash(event)
    _assert_secret_safe(event)
    if replay_dir is not None:
        write_json_immutable(Path(replay_dir) / "000_provider_governance_event.json", event)
    return event


def build_provider_credential_diagnostic(
    *,
    provider_id: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    provider = _provider(provider_id)
    reference = provider["credential_reference"]
    env_name = reference.removeprefix("env:")
    environment = os.environ if env is None else env
    present = bool(environment.get(env_name))
    diagnostic = {
        "registry_version": PROVIDER_CREDENTIAL_REGISTRY_VERSION,
        "provider_id": provider["provider_id"],
        "credential_reference": reference,
        "credential_source_type": provider["credential_source_type"],
        "credential_present": present,
        "credential_display_identifier": _credential_display_identifier(provider["provider_id"], reference),
        "operator_safe_message": (
            f"{provider['provider_id']} credential reference is present."
            if present
            else f"{provider['provider_id']} credential reference is unavailable."
        ),
        "remediation_hint": f"Provision {reference} in the governed process environment and verify presence without printing the value.",
        "credential_value_recorded": False,
        "credential_hash_recorded": False,
        "credential_contents_recorded": False,
        "authorization_header_recorded": False,
        "replay_safe": True,
    }
    _assert_secret_safe(diagnostic)
    return diagnostic


def record_provider_usage_metric(
    *,
    metric_id: str,
    provider_id: str,
    model: str,
    status: str,
    availability: str,
    created_at: str,
    replay_dir: str | Path | None = None,
    success_count: int = 0,
    failure_count: int = 0,
    last_used: str | None = None,
    last_failure: str | None = None,
    latency_ms: int | None = None,
    token_usage: dict[str, Any] | None = None,
    cost_tracking: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = _provider(provider_id)
    artifact = {
        "artifact_type": PROVIDER_USAGE_METRIC_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "metric_id": _require_string(metric_id, "metric_id"),
        "provider_id": provider["provider_id"],
        "model": _require_string(model, "model"),
        "status": _require_string(status, "status"),
        "availability": _require_string(availability, "availability"),
        "success_count": _nonnegative_int(success_count, "success_count"),
        "failure_count": _nonnegative_int(failure_count, "failure_count"),
        "last_used": _optional_string(last_used),
        "last_failure": _optional_string(last_failure),
        "latency_ms": _optional_nonnegative_int(latency_ms, "latency_ms"),
        "token_usage": _safe_optional_dict(token_usage),
        "cost_tracking": _safe_optional_dict(cost_tracking),
        "cost_tracking_hooks_present": cost_tracking is not None,
        "provider_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_secret_safe(artifact)
    if replay_dir is not None:
        write_json_immutable(Path(replay_dir) / "000_provider_usage_metric.json", artifact)
    return artifact


def record_cognition_participation(
    *,
    participation_id: str,
    provider_id: str,
    participation_location: str,
    participation_role: str,
    workflow_id: str,
    invocation_reason: str,
    purpose: str,
    response_used: bool,
    worker_invoked_after: bool,
    human_confirmation_required: bool,
    created_at: str,
    replay_dir: str | Path | None = None,
) -> dict[str, Any]:
    provider = _provider(provider_id)
    location = _participation_location(participation_location)
    artifact = {
        "artifact_type": COGNITION_PARTICIPATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "participation_id": _require_string(participation_id, "participation_id"),
        "provider_id": provider["provider_id"],
        "participation_location": location,
        "participation_role": _require_string(participation_role, "participation_role"),
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "invocation_reason": _require_string(invocation_reason, "invocation_reason"),
        "purpose": _require_string(purpose, "purpose"),
        "response_used": bool(response_used),
        "worker_invoked_after": bool(worker_invoked_after),
        "human_confirmation_required": bool(human_confirmation_required),
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "non_authoritative_provider_principle_preserved": True,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_secret_safe(artifact)
    if replay_dir is not None:
        write_json_immutable(Path(replay_dir) / "000_cognition_participation.json", artifact)
    return artifact


def reconstruct_provider_governance_replay(replay_dir: str | Path) -> dict[str, Any]:
    artifacts = _load_provider_governance_artifacts(Path(replay_dir))
    for artifact in artifacts:
        _verify_artifact_hash(artifact)
    events = [item for item in artifacts if item.get("artifact_type") == PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1]
    metrics = [item for item in artifacts if item.get("artifact_type") == PROVIDER_USAGE_METRIC_ARTIFACT_V1]
    participation = [item for item in artifacts if item.get("artifact_type") == COGNITION_PARTICIPATION_ARTIFACT_V1]
    return {
        "runtime_version": MILESTONE_ID,
        "provider_governance_event_count": len(events),
        "provider_usage_metric_count": len(metrics),
        "cognition_participation_count": len(participation),
        "provider_status": query_provider_status(replay_dir),
        "provider_credentials": query_provider_credentials(replay_dir),
        "provider_usage": query_provider_usage(replay_dir),
        "provider_failures": query_provider_failures(replay_dir),
        "provider_costs": query_provider_costs(replay_dir),
        "cognition_participation": query_cognition_participation(replay_dir),
        "append_only_valid": True,
        "replay_visible": True,
        "replay_hash": replay_hash([item["artifact_hash"] for item in artifacts]),
    }


def query_provider_status(replay_root: str | Path = ".") -> list[dict[str, Any]]:
    artifacts = _load_provider_governance_artifacts(Path(replay_root))
    events = [item for item in artifacts if item.get("artifact_type") == PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1]
    by_provider: dict[str, dict[str, Any]] = {}
    for provider_id, provider in PROVIDER_REGISTRY.items():
        by_provider[provider_id] = {
            "provider_id": provider_id,
            "status": ACTIVE,
            "availability": "UNKNOWN",
            "credential_reference": provider["credential_reference"],
            "credential_display_identifier": _credential_display_identifier(provider_id, provider["credential_reference"]),
            "last_event": None,
        }
    for event in sorted(events, key=lambda item: item.get("created_at", "")):
        provider_id = event["provider_id"]
        if provider_id not in by_provider:
            continue
        by_provider[provider_id]["status"] = event["lifecycle_status"]
        by_provider[provider_id]["availability"] = "AVAILABLE" if event.get("credential_present") else "CREDENTIAL_MISSING"
        by_provider[provider_id]["last_event"] = event["operation"]
    return list(by_provider.values())


def query_provider_credentials(replay_root: str | Path = ".", *, env: dict[str, str] | None = None) -> list[dict[str, Any]]:
    return [
        build_provider_credential_diagnostic(provider_id=provider_id, env=env)
        for provider_id in sorted(PROVIDER_REGISTRY)
    ]


def query_provider_usage(replay_root: str | Path = ".") -> list[dict[str, Any]]:
    metrics = [
        item
        for item in _load_provider_governance_artifacts(Path(replay_root))
        if item.get("artifact_type") == PROVIDER_USAGE_METRIC_ARTIFACT_V1
    ]
    return sorted(metrics, key=lambda item: (item.get("provider_id", ""), item.get("created_at", "")))


def query_provider_failures(replay_root: str | Path = ".") -> list[dict[str, Any]]:
    return [
        {
            "provider_id": item["provider_id"],
            "model": item["model"],
            "failure_count": item["failure_count"],
            "last_failure": item["last_failure"],
            "created_at": item["created_at"],
        }
        for item in query_provider_usage(replay_root)
        if item.get("failure_count", 0) > 0 or item.get("last_failure")
    ]


def query_provider_costs(replay_root: str | Path = ".") -> list[dict[str, Any]]:
    costs = []
    for item in query_provider_usage(replay_root):
        cost_tracking = item.get("cost_tracking")
        if isinstance(cost_tracking, dict):
            costs.append(
                {
                    "provider_id": item["provider_id"],
                    "model": item["model"],
                    "cost_tracking": deepcopy(cost_tracking),
                    "created_at": item["created_at"],
                }
            )
    return costs


def query_cognition_participation(replay_root: str | Path = ".") -> list[dict[str, Any]]:
    participation = [
        item
        for item in _load_provider_governance_artifacts(Path(replay_root))
        if item.get("artifact_type") == COGNITION_PARTICIPATION_ARTIFACT_V1
    ]
    return sorted(participation, key=lambda item: (item.get("created_at", ""), item.get("participation_id", "")))


def render_provider_governance_query(query_name: str, rows: list[dict[str, Any]]) -> str:
    title = f"AIGOL PROVIDER {query_name.upper()}"
    if not rows:
        return f"{title}\n(no replay-visible records)"
    lines = [title]
    for row in rows:
        provider_id = row.get("provider_id", "unknown")
        if query_name == "credentials":
            lines.append(
                f"{provider_id}: {row.get('credential_reference')} present={row.get('credential_present')} "
                f"display={row.get('credential_display_identifier')}"
            )
        elif query_name == "participation":
            lines.append(
                f"{provider_id}: {row.get('participation_location')} workflow={row.get('workflow_id')} "
                f"response_used={row.get('response_used')}"
            )
        elif query_name == "usage":
            lines.append(
                f"{provider_id}: model={row.get('model')} status={row.get('status')} "
                f"success={row.get('success_count')} failure={row.get('failure_count')}"
            )
        elif query_name == "failures":
            lines.append(f"{provider_id}: failures={row.get('failure_count')} last_failure={row.get('last_failure')}")
        elif query_name == "costs":
            lines.append(f"{provider_id}: model={row.get('model')} cost_tracking={row.get('cost_tracking')}")
        else:
            lines.append(
                f"{provider_id}: status={row.get('status')} availability={row.get('availability')} "
                f"credential={row.get('credential_display_identifier')}"
            )
    return "\n".join(lines)


def _load_provider_governance_artifacts(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    artifacts = []
    for path in sorted(root.rglob("*.json")):
        try:
            loaded = load_json(path)
        except FailClosedRuntimeError:
            continue
        artifact = loaded.get("artifact") if isinstance(loaded.get("artifact"), dict) else loaded
        if artifact.get("artifact_type") in {
            PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1,
            PROVIDER_USAGE_METRIC_ARTIFACT_V1,
            COGNITION_PARTICIPATION_ARTIFACT_V1,
        }:
            artifacts.append(deepcopy(artifact))
    return artifacts


def _provider(provider_id: str) -> dict[str, Any]:
    normalized = _require_string(provider_id, "provider_id").lower()
    if normalized not in PROVIDER_REGISTRY:
        raise FailClosedRuntimeError(f"provider governance failed closed: unknown provider_id {provider_id}")
    return deepcopy(PROVIDER_REGISTRY[normalized])


def _operation(value: str) -> str:
    normalized = _require_string(value, "operation").upper()
    if normalized not in LIFECYCLE_OPERATIONS:
        raise FailClosedRuntimeError("provider governance failed closed: unsupported lifecycle operation")
    return normalized


def _participation_location(value: str) -> str:
    normalized = _require_string(value, "participation_location").upper()
    if normalized not in PARTICIPATION_LOCATIONS:
        raise FailClosedRuntimeError("provider governance failed closed: unsupported participation location")
    return normalized


def _credential_display_identifier(provider_id: str, credential_reference: str) -> str:
    safe_reference_hash = replay_hash(
        {
            "registry_version": PROVIDER_CREDENTIAL_REGISTRY_VERSION,
            "provider_id": provider_id,
            "credential_reference": credential_reference,
        }
    )
    return "ref:..." + safe_reference_hash[-6:]


def _require_human_approval(operation: str, artifact: dict[str, Any] | None) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"provider governance failed closed: {operation} requires human approval")
    if artifact.get("decision") != "APPROVED" and artifact.get("approval_status") != "APPROVED":
        raise FailClosedRuntimeError(f"provider governance failed closed: {operation} approval was not approved")


def _lifecycle_status(operation: str) -> str:
    if operation == DELETE:
        return DELETED
    if operation == DISABLE:
        return DISABLED
    return ACTIVE


def _safe_optional_dict(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("provider governance optional metric must be a JSON object")
    candidate = deepcopy(value)
    _assert_secret_safe(candidate)
    return candidate


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise FailClosedRuntimeError("optional string value is invalid")
    return value.strip() or None


def _nonnegative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise FailClosedRuntimeError(f"{field_name} must be a non-negative integer")
    return value


def _optional_nonnegative_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, field_name)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = artifact.get("artifact_hash")
    if not isinstance(expected, str):
        raise FailClosedRuntimeError("provider governance artifact hash is required")
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    if replay_hash(candidate) != expected:
        raise FailClosedRuntimeError("provider governance artifact hash mismatch")


def _assert_secret_safe(value: Any) -> None:
    serialized = repr(value)
    for marker in SECRET_MARKERS:
        if marker in serialized:
            raise FailClosedRuntimeError("provider governance failed closed: secret-like material recorded")
