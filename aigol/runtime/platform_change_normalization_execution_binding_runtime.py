"""Bind one completed change-normalization capability result to execution readiness.

This module is deliberately narrow.  It transfers exact, replay-verified
evidence to the existing execution-ready pipeline without authorizing,
dispatching, invoking, or executing anything.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    validate_certified_capability_invocation_result_artifact,
)
from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_READY,
    reconstruct_governed_implementation_dry_run_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_normalization_runtime import (
    CHANGE_NORMALIZED,
    CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS,
    validate_normalized_change_artifact,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
    reconstruct_project_context_semantic_capability_route,
    validate_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION = (
    "G54_03_PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_V1"
)
PLATFORM_CHANGE_NORMALIZATION = "PLATFORM_CHANGE_NORMALIZATION"
CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1 = "CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1"
CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION = (
    "CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION"
)
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "capability_evidence_bound",
    "capability_execution_binding_recorded",
)

AUTHORITY_FLAGS = {
    "capability_selection_is_execution_authorization": False,
    "execution_authorized": False,
    "authorization_created": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_started": False,
    "repository_mutated": False,
    "replay_mutated": False,
}


def bind_platform_change_normalization_to_execution_ready(
    *,
    binding_id: str,
    semantic_capability_route_artifact: dict[str, Any],
    semantic_capability_route_replay_reference: str | Path,
    execution_ready_status_artifact: dict[str, Any],
    execution_ready_replay_reference: str | Path,
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    execution_authorization_reference: str | None = None,
) -> dict[str, Any]:
    """Create a non-authorizing binding to existing execution-ready evidence."""

    replay_path = Path(replay_dir)
    identifier = _safe_string(binding_id)
    try:
        _ensure_replay_available(replay_path)
        if execution_authorization_reference is not None:
            raise FailClosedRuntimeError(
                "capability execution binding failed closed: authorization input is forbidden"
            )
        route_reference = _require_path(
            semantic_capability_route_replay_reference,
            "semantic_capability_route_replay_reference",
        )
        ready_reference = _require_path(
            execution_ready_replay_reference,
            "execution_ready_replay_reference",
        )
        route = _validated_route(
            semantic_capability_route_artifact,
            route_reference,
        )
        normalized = _validated_normalization_result(route)
        ready = _validated_execution_ready(
            execution_ready_status_artifact,
            ready_reference,
        )
        evidence = _evidence_artifact(
            binding_id=_require_string(binding_id, "binding_id"),
            route=route,
            route_reference=route_reference,
            normalized=normalized,
            ready=ready,
            ready_reference=ready_reference,
            requested_by=_require_string(requested_by, "requested_by"),
            created_at=_require_string(created_at, "created_at"),
        )
        binding = _binding_artifact(evidence)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], binding)
        return _capture(evidence, binding, replay_path)
    except Exception as exc:
        binding = _failed_binding_artifact(
            binding_id=identifier,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, binding)
        return _capture(None, binding, replay_path)


def reconstruct_platform_change_normalization_execution_binding_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct a successful binding and verify both upstream lineages."""

    replay_path = Path(replay_dir)
    evidence_wrapper = load_json(replay_path / f"000_{REPLAY_STEPS[0]}.json")
    binding_wrapper = load_json(replay_path / f"001_{REPLAY_STEPS[1]}.json")
    _verify_wrapper(evidence_wrapper, 0, REPLAY_STEPS[0])
    _verify_wrapper(binding_wrapper, 1, REPLAY_STEPS[1])
    evidence = _validate_evidence_artifact(evidence_wrapper.get("artifact"))
    binding = validate_platform_change_normalization_execution_binding(
        binding_wrapper.get("artifact")
    )
    if binding["evidence_hash"] != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("capability execution binding replay evidence mismatch")
    if binding["artifact_hash"] != _binding_hash(binding):
        raise FailClosedRuntimeError("capability execution binding replay binding hash mismatch")
    route = reconstruct_project_context_semantic_capability_route(
        evidence["semantic_capability_route_reference"]
    )
    if route["artifact_hash"] != evidence["semantic_capability_route_hash"]:
        raise FailClosedRuntimeError("capability execution binding replay route mismatch")
    normalized = _validated_normalization_result(route)
    if normalized["artifact_hash"] != evidence["normalized_change_artifact_hash"]:
        raise FailClosedRuntimeError("capability execution binding replay normalization mismatch")
    ready = reconstruct_governed_implementation_dry_run_replay(
        evidence["execution_ready_replay_reference"]
    )
    if ready["execution_status"] != EXECUTION_READY:
        raise FailClosedRuntimeError("capability execution binding replay execution readiness mismatch")
    if ready["replay_hash"] != evidence["execution_ready_replay_hash"]:
        raise FailClosedRuntimeError("capability execution binding replay readiness hash mismatch")
    return {
        "binding_id": binding["binding_id"],
        "binding_status": binding["binding_status"],
        "selected_capability_identifier": binding["selected_capability_identifier"],
        "normalized_change_artifact_hash": binding["normalized_change_artifact_hash"],
        "execution_ready_reference": binding["execution_ready_reference"],
        "execution_ready_replay_hash": binding["execution_ready_replay_hash"],
        "authorization_required": binding["authorization_required"],
        "replay_visible": True,
        "replay_artifact_count": 2,
        "replay_hash": replay_hash((evidence_wrapper, binding_wrapper)),
    }


def validate_platform_change_normalization_execution_binding(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate the public non-authorizing execution-binding artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("capability execution binding artifact must be an object")
    candidate = deepcopy(artifact)
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("capability execution binding artifact hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("artifact_type") != CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability execution binding artifact type mismatch")
    if candidate.get("runtime_version") != PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION:
        raise FailClosedRuntimeError("capability execution binding version mismatch")
    if candidate.get("binding_status") != CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION:
        raise FailClosedRuntimeError("capability execution binding status mismatch")
    if candidate.get("selected_capability_identifier") != PLATFORM_CHANGE_NORMALIZATION:
        raise FailClosedRuntimeError("capability execution binding capability identity mismatch")
    for field in (
        "binding_id",
        "semantic_capability_route_reference",
        "semantic_capability_route_hash",
        "normalized_change_artifact_hash",
        "execution_ready_reference",
        "execution_ready_replay_hash",
        "evidence_hash",
    ):
        _require_string(candidate.get(field), field)
    if candidate.get("authorization_required") is not True:
        raise FailClosedRuntimeError("capability execution binding must require authorization")
    if candidate.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("capability execution binding authority boundary mismatch")
    if candidate.get("replay_visible") is not True:
        raise FailClosedRuntimeError("capability execution binding must be replay-visible")
    return candidate


def _validated_route(artifact: dict[str, Any], replay_reference: str) -> dict[str, Any]:
    route = validate_project_context_semantic_capability_route(artifact)
    reconstructed = reconstruct_project_context_semantic_capability_route(replay_reference)
    if route["artifact_hash"] != reconstructed["artifact_hash"]:
        raise FailClosedRuntimeError("capability execution binding route replay mismatch")
    if route.get("route_status") != ROUTE_COMPLETED:
        raise FailClosedRuntimeError("capability execution binding requires completed semantic route")
    if route.get("selected_capability_identifier") != PLATFORM_CHANGE_NORMALIZATION:
        raise FailClosedRuntimeError("capability execution binding capability identity mismatch")
    return route


def _validated_normalization_result(route: dict[str, Any]) -> dict[str, Any]:
    lifecycle_reference = Path(_require_string(route.get("lifecycle_replay_reference"), "lifecycle_replay_reference"))
    result_wrapper = load_json(lifecycle_reference / "002_g28_invocation_result_recorded.json")
    _verify_wrapper(result_wrapper, 2, "g28_invocation_result_recorded")
    record = result_wrapper.get("artifact")
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("capability execution binding invocation result record is invalid")
    result = validate_certified_capability_invocation_result_artifact(
        record.get("g28_invocation_result")
    )
    if result.get("capability_identifier") != PLATFORM_CHANGE_NORMALIZATION:
        raise FailClosedRuntimeError("capability execution binding invocation identity mismatch")
    if result.get("capability_invoked") is not True:
        raise FailClosedRuntimeError("capability execution binding invocation is incomplete")
    normalized = validate_normalized_change_artifact(result.get("output_artifact"))
    if normalized.get("normalization_status") not in {
        CHANGE_NORMALIZED,
        CHANGE_NORMALIZED_WITH_UNRESOLVED_MAPPINGS,
    }:
        raise FailClosedRuntimeError("capability execution binding normalization is not complete")
    return normalized


def _validated_execution_ready(
    artifact: dict[str, Any], replay_reference: str
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("capability execution binding execution-ready artifact is invalid")
    candidate = deepcopy(artifact)
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("capability execution binding execution-ready artifact hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    reconstructed = reconstruct_governed_implementation_dry_run_replay(replay_reference)
    if reconstructed.get("execution_status") != EXECUTION_READY:
        raise FailClosedRuntimeError("capability execution binding requires execution-ready evidence")
    persisted = load_json(Path(replay_reference) / "003_execution_ready_status_recorded.json")
    _verify_wrapper(persisted, 3, "execution_ready_status_recorded")
    recorded = persisted.get("artifact")
    if not isinstance(recorded, dict):
        raise FailClosedRuntimeError("capability execution binding execution-ready replay is invalid")
    recorded_hash = recorded.get("artifact_hash")
    if not isinstance(recorded_hash, str) or recorded_hash != candidate["artifact_hash"]:
        raise FailClosedRuntimeError("capability execution binding execution-ready replay mismatch")
    for field in (
        "worker_invoked",
        "execution_requested",
        "dispatch_requested",
        "authorization_created",
    ):
        if candidate.get(field) is not False:
            raise FailClosedRuntimeError("capability execution binding execution-ready authority mismatch")
    return {
        "reference": _require_string(candidate.get("dry_run_id"), "execution_ready_reference"),
        "artifact_hash": candidate["artifact_hash"],
        "replay_hash": reconstructed["replay_hash"],
    }


def _evidence_artifact(
    *,
    binding_id: str,
    route: dict[str, Any],
    route_reference: str,
    normalized: dict[str, Any],
    ready: dict[str, Any],
    ready_reference: str,
    requested_by: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "CAPABILITY_EXECUTION_BINDING_EVIDENCE_ARTIFACT_V1",
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION,
        "binding_id": binding_id,
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "semantic_capability_route_reference": route_reference,
        "semantic_capability_route_hash": route["artifact_hash"],
        "normalized_change_reference": normalized["normalization_id"],
        "normalized_change_artifact_hash": normalized["artifact_hash"],
        "execution_ready_reference": ready["reference"],
        "execution_ready_artifact_hash": ready["artifact_hash"],
        "execution_ready_replay_reference": ready_reference,
        "execution_ready_replay_hash": ready["replay_hash"],
        "requested_by": requested_by,
        "created_at": created_at,
        "authorization_required": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return _validate_evidence_artifact(artifact)


def _binding_artifact(evidence: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION,
        "binding_id": evidence["binding_id"],
        "binding_status": CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "semantic_capability_route_reference": evidence["semantic_capability_route_reference"],
        "semantic_capability_route_hash": evidence["semantic_capability_route_hash"],
        "normalized_change_artifact_hash": evidence["normalized_change_artifact_hash"],
        "execution_ready_reference": evidence["execution_ready_reference"],
        "execution_ready_replay_hash": evidence["execution_ready_replay_hash"],
        "authorization_required": True,
        "evidence_hash": evidence["artifact_hash"],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_platform_change_normalization_execution_binding(artifact)


def _failed_binding_artifact(*, binding_id: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION,
        "binding_id": binding_id,
        "binding_status": FAILED_CLOSED,
        "selected_capability_identifier": None,
        "failure_reason": failure_reason,
        "authorization_required": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validate_evidence_artifact(artifact: Any) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("capability execution binding evidence must be an object")
    candidate = deepcopy(artifact)
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("capability execution binding evidence hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    if candidate.get("artifact_type") != "CAPABILITY_EXECUTION_BINDING_EVIDENCE_ARTIFACT_V1":
        raise FailClosedRuntimeError("capability execution binding evidence type mismatch")
    if candidate.get("selected_capability_identifier") != PLATFORM_CHANGE_NORMALIZATION:
        raise FailClosedRuntimeError("capability execution binding evidence capability mismatch")
    if candidate.get("authorization_required") is not True:
        raise FailClosedRuntimeError("capability execution binding evidence authorization boundary mismatch")
    if candidate.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("capability execution binding evidence authority boundary mismatch")
    return candidate


def _binding_hash(artifact: dict[str, Any]) -> str:
    return replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})


def _capture(
    evidence: dict[str, Any] | None, binding: dict[str, Any], replay_path: Path
) -> dict[str, Any]:
    return {
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION,
        "binding_id": binding["binding_id"],
        "binding_status": binding["binding_status"],
        "capability_execution_binding_evidence_artifact": deepcopy(evidence),
        "capability_execution_binding_artifact": deepcopy(binding),
        "capability_execution_binding_replay_reference": str(replay_path),
        "authorization_required": True,
        "execution_authorized": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "replay_visible": True,
        "fail_closed": binding["binding_status"] == FAILED_CLOSED,
        "failure_reason": binding.get("failure_reason"),
    }


def _verify_wrapper(wrapper: Any, index: int, step: str) -> None:
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("capability execution binding replay wrapper is invalid")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("capability execution binding replay ordering mismatch")
    expected_hash = wrapper.get("replay_hash")
    candidate = deepcopy(wrapper)
    candidate.pop("replay_hash", None)
    if expected_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("capability execution binding replay hash mismatch")


def _persist_step(path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(path: Path, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(path, 1, REPLAY_STEPS[1], artifact)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists():
        raise FailClosedRuntimeError("capability execution binding replay path already exists")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_path(value: str | Path, field_name: str) -> str:
    return _require_string(str(value), field_name)


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "UNAVAILABLE"


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__


__all__ = [
    "CAPABILITY_EXECUTION_BINDING_ARTIFACT_V1",
    "CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION",
    "FAILED_CLOSED",
    "PLATFORM_CHANGE_NORMALIZATION",
    "PLATFORM_CHANGE_NORMALIZATION_EXECUTION_BINDING_RUNTIME_VERSION",
    "bind_platform_change_normalization_to_execution_ready",
    "reconstruct_platform_change_normalization_execution_binding_replay",
    "validate_platform_change_normalization_execution_binding",
]
