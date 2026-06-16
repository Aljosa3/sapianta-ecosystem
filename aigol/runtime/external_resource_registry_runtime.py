"""Minimal External Resource Registry runtime for AIGOL_ERR_V0."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_ERR_V0_RUNTIME_VERSION = "AIGOL_ERR_V0"
ERR_RESOURCE_SELECTION_EVIDENCE_V0 = "ERR_RESOURCE_SELECTION_EVIDENCE_V0"
ERR_RESOURCE_SELECTION_RETURNED_V0 = "ERR_RESOURCE_SELECTION_RETURNED_V0"

COGNITION_PROVIDER = "COGNITION_PROVIDER"
EXECUTION_WORKER = "EXECUTION_WORKER"
RESOURCE_TYPES = {COGNITION_PROVIDER, EXECUTION_WORKER}

ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"
RESOURCE_STATUSES = {ACTIVE, INACTIVE}

MOCK_PROVIDER_ID = "mock_provider"
MOCK_FILESYSTEM_WORKER_ID = "mock_filesystem_worker"

REPLAY_STEPS = (
    "err_resource_selection_evidence_recorded",
    "err_resource_selection_returned",
)


def default_err_v0_registry() -> dict[str, Any]:
    """Return test-only ERR_V0 resources."""

    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": MOCK_PROVIDER_ID,
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )
    register_resource(
        registry,
        {
            "resource_id": MOCK_FILESYSTEM_WORKER_ID,
            "resource_type": EXECUTION_WORKER,
            "capabilities": ["file_write"],
            "status": ACTIVE,
        },
    )
    return registry


def create_err_v0_registry() -> dict[str, Any]:
    return {
        "registry_version": AIGOL_ERR_V0_RUNTIME_VERSION,
        "resources": [],
        "provider_invoked": False,
        "worker_invoked": False,
        "orchestration_performed": False,
        "governance_modified": False,
        "replay_modified": False,
    }


def register_resource(registry: dict[str, Any], resource: dict[str, Any]) -> dict[str, Any]:
    """Register resource metadata in a passive ERR_V0 registry."""

    _validate_registry_shape(registry)
    normalized = _normalize_resource(resource)
    if any(item["resource_id"] == normalized["resource_id"] for item in registry["resources"]):
        raise FailClosedRuntimeError("ERR_V0 failed closed: duplicate resource_id")
    registry["resources"].append(normalized)
    return deepcopy(normalized)


def get_resource_by_id(registry: dict[str, Any], resource_id: str) -> dict[str, Any]:
    """Lookup resource metadata by resource_id."""

    _validate_registry(registry)
    normalized_id = _require_string(resource_id, "resource_id")
    for resource in registry["resources"]:
        if resource["resource_id"] == normalized_id:
            return deepcopy(resource)
    raise FailClosedRuntimeError("ERR_V0 failed closed: resource_id not registered")


def find_resources_by_capability(
    registry: dict[str, Any],
    required_capability: str,
    *,
    resource_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return active resources that declare the required capability."""

    _validate_registry(registry)
    capability = _require_string(required_capability, "required_capability")
    expected_type = _normalize_resource_type(resource_type) if resource_type is not None else None
    matches = []
    for resource in registry["resources"]:
        if resource["status"] != ACTIVE:
            continue
        if expected_type is not None and resource["resource_type"] != expected_type:
            continue
        if capability in resource["capabilities"]:
            matches.append(deepcopy(resource))
    return matches


def select_resource_for_capability(
    *,
    selection_id: str,
    required_capability: str,
    replay_dir: str | Path,
    created_at: str,
    registry: dict[str, Any] | None = None,
    resource_type: str | None = None,
    human_intent: str | None = None,
    hirr_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select the first active matching resource and record replay-visible evidence."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    active_registry = deepcopy(registry) if registry is not None else default_err_v0_registry()
    matches = find_resources_by_capability(
        active_registry,
        required_capability,
        resource_type=resource_type,
    )
    if not matches:
        raise FailClosedRuntimeError("ERR_V0 failed closed: no active resource for capability")
    selected = matches[0]
    evidence = _selection_evidence(
        selection_id=selection_id,
        required_capability=required_capability,
        selected=selected,
        matches=matches,
        registry=active_registry,
        created_at=created_at,
        human_intent=human_intent,
        hirr_output=hirr_output,
    )
    returned = _returned_artifact(evidence)
    _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(evidence, returned, replay_path)


def demonstrate_err_v0_hirr_to_resource_selection(
    *,
    selection_id: str,
    human_intent: str,
    hirr_output: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Demonstrate Human Intent -> HIRR output -> ERR capability lookup."""

    if not isinstance(hirr_output, dict):
        raise FailClosedRuntimeError("ERR_V0 failed closed: hirr_output must be a JSON object")
    required_capability = _require_string(hirr_output.get("required_capability"), "required_capability")
    return select_resource_for_capability(
        selection_id=selection_id,
        required_capability=required_capability,
        replay_dir=replay_dir,
        created_at=created_at,
        registry=registry,
        resource_type=hirr_output.get("resource_type"),
        human_intent=human_intent,
        hirr_output=hirr_output,
    )


def reconstruct_err_v0_selection_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct ERR_V0 selection replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("ERR_V0 replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("ERR_V0 replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("selection_reference") != evidence["selection_id"]:
        raise FailClosedRuntimeError("ERR_V0 replay reference mismatch")
    if returned.get("selection_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("ERR_V0 replay hash mismatch")
    return {
        "selection_id": evidence["selection_id"],
        "selection_status": evidence["selection_status"],
        "required_capability": evidence["required_capability"],
        "selected_resource_id": evidence["selected_resource_id"],
        "selected_resource_type": evidence["selected_resource_type"],
        "active_match_count": evidence["active_match_count"],
        "human_intent": evidence["human_intent"],
        "hirr_output": deepcopy(evidence["hirr_output"]),
        "provider_invoked": False,
        "worker_invoked": False,
        "orchestration_performed": False,
        "governance_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _selection_evidence(
    *,
    selection_id: str,
    required_capability: str,
    selected: dict[str, Any],
    matches: list[dict[str, Any]],
    registry: dict[str, Any],
    created_at: str,
    human_intent: str | None,
    hirr_output: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ERR_RESOURCE_SELECTION_EVIDENCE_V0,
        "runtime_version": AIGOL_ERR_V0_RUNTIME_VERSION,
        "selection_id": _require_string(selection_id, "selection_id"),
        "selection_status": "RESOURCE_SELECTED",
        "required_capability": _require_string(required_capability, "required_capability"),
        "selected_resource_id": selected["resource_id"],
        "selected_resource_type": selected["resource_type"],
        "active_match_count": len(matches),
        "active_resource_ids": [resource["resource_id"] for resource in matches],
        "registry_hash": replay_hash(_registry_hash_input(registry)),
        "human_intent": human_intent,
        "hirr_output": deepcopy(hirr_output),
        "provider_invoked": False,
        "worker_invoked": False,
        "provider_invoked_worker": False,
        "worker_invoked_provider": False,
        "orchestration_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(evidence: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": ERR_RESOURCE_SELECTION_RETURNED_V0,
        "runtime_version": AIGOL_ERR_V0_RUNTIME_VERSION,
        "selection_reference": evidence["selection_id"],
        "selection_hash": evidence["artifact_hash"],
        "selected_resource_id": evidence["selected_resource_id"],
        "selected_resource_type": evidence["selected_resource_type"],
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(evidence: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "selection_id": evidence["selection_id"],
        "selection_status": evidence["selection_status"],
        "required_capability": evidence["required_capability"],
        "selected_resource_id": evidence["selected_resource_id"],
        "selected_resource_type": evidence["selected_resource_type"],
        "active_match_count": evidence["active_match_count"],
        "err_selection_evidence_artifact": deepcopy(evidence),
        "err_selection_returned_artifact": deepcopy(returned),
        "provider_invoked": False,
        "worker_invoked": False,
        "orchestration_performed": False,
        "governance_modified": False,
        "replay_visible": True,
        "replay_reference": str(replay_path),
        "replay_hash": replay_hash([evidence, returned]),
    }


def _normalize_resource(resource: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(resource, dict):
        raise FailClosedRuntimeError("ERR_V0 failed closed: resource must be a JSON object")
    normalized = {
        "resource_id": _require_string(resource.get("resource_id"), "resource_id"),
        "resource_type": _normalize_resource_type(resource.get("resource_type")),
        "capabilities": _normalize_capabilities(resource.get("capabilities")),
        "status": _normalize_status(resource.get("status")),
    }
    return normalized


def _validate_registry(registry: dict[str, Any]) -> None:
    _validate_registry_shape(registry)
    seen: set[str] = set()
    for resource in registry["resources"]:
        normalized = _normalize_resource(resource)
        if normalized != resource:
            raise FailClosedRuntimeError("ERR_V0 failed closed: non-normalized resource metadata")
        if normalized["resource_id"] in seen:
            raise FailClosedRuntimeError("ERR_V0 failed closed: duplicate resource_id")
        seen.add(normalized["resource_id"])


def _validate_registry_shape(registry: dict[str, Any]) -> None:
    if not isinstance(registry, dict):
        raise FailClosedRuntimeError("ERR_V0 failed closed: registry must be a JSON object")
    if registry.get("registry_version") != AIGOL_ERR_V0_RUNTIME_VERSION:
        raise FailClosedRuntimeError("ERR_V0 failed closed: invalid registry_version")
    if not isinstance(registry.get("resources"), list):
        raise FailClosedRuntimeError("ERR_V0 failed closed: resources must be a list")


def _normalize_resource_type(value: Any) -> str:
    resource_type = _require_string(value, "resource_type")
    if resource_type not in RESOURCE_TYPES:
        raise FailClosedRuntimeError("ERR_V0 failed closed: invalid resource_type")
    return resource_type


def _normalize_status(value: Any) -> str:
    status = _require_string(value, "status")
    if status not in RESOURCE_STATUSES:
        raise FailClosedRuntimeError("ERR_V0 failed closed: invalid status")
    return status


def _normalize_capabilities(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("ERR_V0 failed closed: capabilities are required")
    capabilities = [_require_string(item, "capability") for item in value]
    if len(set(capabilities)) != len(capabilities):
        raise FailClosedRuntimeError("ERR_V0 failed closed: duplicate capability")
    return capabilities


def _registry_hash_input(registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "registry_version": registry["registry_version"],
        "resources": deepcopy(registry["resources"]),
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("ERR_V0 replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("ERR_V0 failed closed: replay artifact already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("ERR_V0 artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("ERR_V0 artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("ERR_V0 replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("ERR_V0 replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ERR_V0 failed closed: {field_name} is required")
    return value
