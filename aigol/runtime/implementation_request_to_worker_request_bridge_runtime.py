"""Governed bridge from implementation request to worker request generation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from aigol.runtime.governed_implementation_request_runtime import (
    IMPLEMENTATION_REQUEST_ARTIFACT_V1,
    IMPLEMENTATION_REQUEST_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_VERSION = (
    "AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_V1"
)
WORKER_REQUEST_ARTIFACT_V1 = "WORKER_REQUEST_ARTIFACT_V1"
WORKER_REQUEST_CREATED = "WORKER_REQUEST_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "worker_request_recorded",
    "worker_request_returned",
)

DEFAULT_WORKER_CONSTRAINTS = {
    "single_worker_request_only": True,
    "dispatch_allowed": False,
    "worker_invocation_allowed": False,
    "implementation_execution_allowed": False,
    "provider_invocation_allowed": False,
    "code_modification_allowed": False,
    "governance_modification_allowed": False,
    "human_approval_required": True,
}


def bridge_implementation_request_to_worker_request(
    *,
    bridge_id: str,
    implementation_request_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
    worker_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a governed worker request without dispatching, invoking, or executing a worker."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        implementation_request = deepcopy(implementation_request_artifact)
        _validate_implementation_request(implementation_request)
        request = _worker_request_artifact(
            bridge_id=bridge_id,
            implementation_request=implementation_request,
            requested_by=requested_by,
            created_at=created_at,
            worker_constraints=worker_constraints,
            request_status=WORKER_REQUEST_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(request, returned, replay_path)
    except Exception as exc:
        request = _failed_worker_request_artifact(
            bridge_id=bridge_id,
            implementation_request_artifact=implementation_request_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(request)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], request)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(request, returned, replay_path)


def reconstruct_implementation_request_to_worker_request_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate implementation request to worker request replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation request to worker request replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation request to worker request artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    worker_request = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("worker_request_reference") != worker_request["worker_request_id"]:
        raise FailClosedRuntimeError("implementation request to worker request returned reference mismatch")
    if returned.get("worker_request_hash") != worker_request["artifact_hash"]:
        raise FailClosedRuntimeError("implementation request to worker request returned hash mismatch")
    return {
        "worker_request_id": worker_request["worker_request_id"],
        "request_status": worker_request["request_status"],
        "source_implementation_request": worker_request["source_implementation_request"],
        "source_ppp_candidate": worker_request["source_ppp_candidate"],
        "source_improvement_intent": worker_request["source_improvement_intent"],
        "source_gap_artifact": worker_request["source_gap_artifact"],
        "replay_lineage_preserved": worker_request["replay_lineage_preserved"],
        "human_approval_required": worker_request["human_approval_required"],
        "execution_prevented": worker_request["execution_requested"] is False
        and worker_request["implementation_executed"] is False
        and worker_request["worker_dispatched"] is False
        and worker_request["worker_invoked"] is False,
        "ready_for_worker_dispatch_governance": worker_request["ready_for_worker_dispatch_governance"],
        "worker_dispatched": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "code_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def project_worker_request_repository_scope(
    *,
    worker_request_artifact: dict[str, Any],
    repository_targets: list[str],
    focused_test_targets: list[str],
    repository_scope_grounding_identity: str,
    repository_scope_grounding_hash: str,
) -> dict[str, Any]:
    """Project immutable Repository Cognition evidence into one Worker request.

    This projection changes no objective, approval, constraint, or execution
    flag.  It only replaces the explicitly unresolved repository-scope fields
    of an approved durable-work request.
    """

    source = validate_worker_request_artifact(worker_request_artifact)
    if source.get("candidate_source_type") != "APPROVED_DURABLE_GOVERNED_WORK":
        raise FailClosedRuntimeError(
            "Worker repository-scope projection requires approved durable work"
        )
    if source.get("dispatch_blocked_by_unresolved_repository_scope") is not True:
        raise FailClosedRuntimeError(
            "Worker repository-scope projection requires unresolved source scope"
        )
    targets = _unique_relative_paths(repository_targets, "repository_targets")
    focused_tests = _unique_relative_paths(
        focused_test_targets, "focused_test_targets"
    )
    if not targets or not focused_tests or not set(focused_tests).issubset(targets):
        raise FailClosedRuntimeError(
            "Worker repository-scope projection requires grounded source and test targets"
        )
    grounding_identity = _require_string(
        repository_scope_grounding_identity,
        "repository_scope_grounding_identity",
    )
    grounding_hash = _require_hash(
        repository_scope_grounding_hash,
        "repository_scope_grounding_hash",
    )
    projected = deepcopy(source)
    scope = projected["implementation_scope"]
    scope["repository_scope_status"] = "CANONICALLY_GROUNDED_BY_REPOSITORY_COGNITION"
    scope["repository_targets"] = targets
    scope["focused_test_requirements"] = focused_tests
    scope["repository_scope_grounding_identity"] = grounding_identity
    scope["repository_scope_grounding_hash"] = grounding_hash
    scope["field_lineage"] = deepcopy(scope["field_lineage"])
    scope["field_lineage"]["repository_scope"] = {
        "source_artifact_type": "CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1",
        "source_identity": grounding_identity,
        "source_hash": grounding_hash,
    }
    projected["repository_scope_status"] = scope["repository_scope_status"]
    projected["repository_targets"] = targets
    projected["repository_scope_grounding_identity"] = grounding_identity
    projected["repository_scope_grounding_hash"] = grounding_hash
    projected["ready_for_worker_dispatch_governance"] = True
    projected["dispatch_blocked_by_unresolved_repository_scope"] = False
    projected["artifact_hash"] = replay_hash(
        {key: value for key, value in projected.items() if key != "artifact_hash"}
    )
    return validate_worker_request_artifact(projected)


def validate_worker_request_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate an existing or repository-scope-projected Worker request."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Worker request artifact must be a JSON object")
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate)
    if candidate.get("artifact_type") != WORKER_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("Worker request artifact type mismatch")
    if candidate.get("request_status") != WORKER_REQUEST_CREATED:
        raise FailClosedRuntimeError("Worker request must be created")
    if candidate.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("Worker request Replay lineage is not preserved")
    scope = candidate.get("implementation_scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("field_lineage"), dict):
        raise FailClosedRuntimeError("Worker request implementation scope is invalid")
    targets = scope.get("repository_targets")
    if not isinstance(targets, list):
        raise FailClosedRuntimeError("Worker request repository targets are invalid")
    grounded = scope.get("repository_scope_status") == (
        "CANONICALLY_GROUNDED_BY_REPOSITORY_COGNITION"
    )
    if grounded:
        normalized = _unique_relative_paths(targets, "repository_targets")
        if normalized != candidate.get("repository_targets"):
            raise FailClosedRuntimeError("Worker request grounded targets mismatch")
        grounding_hash = _require_hash(
            scope.get("repository_scope_grounding_hash"),
            "repository_scope_grounding_hash",
        )
        if candidate.get("repository_scope_grounding_hash") != grounding_hash:
            raise FailClosedRuntimeError("Worker request grounding hash mismatch")
        if candidate.get("repository_scope_grounding_identity") != scope.get(
            "repository_scope_grounding_identity"
        ):
            raise FailClosedRuntimeError("Worker request grounding identity mismatch")
        if candidate.get("ready_for_worker_dispatch_governance") is not True:
            raise FailClosedRuntimeError("grounded Worker request readiness mismatch")
        if candidate.get("dispatch_blocked_by_unresolved_repository_scope") is not False:
            raise FailClosedRuntimeError("grounded Worker request dispatch boundary mismatch")
    for flag in (
        "implementation_executed",
        "worker_dispatched",
        "worker_invoked",
        "provider_invoked",
        "code_modified",
        "governance_modified",
        "authorization_created",
        "execution_requested",
        "dispatch_requested",
    ):
        if candidate.get(flag) is not False:
            raise FailClosedRuntimeError(f"Worker request {flag} must remain false")
    return candidate


def _validate_implementation_request(request: dict[str, Any]) -> None:
    _validate_artifact(request)
    if request.get("artifact_type") != IMPLEMENTATION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: invalid artifact type")
    if request.get("request_status") != IMPLEMENTATION_REQUEST_CREATED:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: certified request required")
    if request.get("replay_lineage_preserved") is not True:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: replay lineage broken")
    if request.get("human_approval_required") is not True or request.get("human_approval_granted") is not True:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: human approval chain required")
    if request.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: human authority missing")
    if request.get("ready_for_worker_request_generation") is not True:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: request is not worker-ready")
    _require_string(request.get("source_ppp_candidate"), "source_ppp_candidate")
    _require_hash(request.get("source_ppp_candidate_hash"), "source_ppp_candidate_hash")
    _require_string(request.get("source_improvement_intent"), "source_improvement_intent")
    _require_hash(request.get("source_improvement_intent_hash"), "source_improvement_intent_hash")
    _require_string(request.get("source_gap_artifact"), "source_gap_artifact")
    _require_hash(request.get("source_gap_hash"), "source_gap_hash")
    _require_string(request.get("human_approval_reference"), "human_approval_reference")
    _require_hash(request.get("human_approval_hash"), "human_approval_hash")
    if not _string_list(request.get("replay_references")):
        raise FailClosedRuntimeError("implementation request to worker request failed closed: replay references required")
    if not _hash_list(request.get("replay_hashes")):
        raise FailClosedRuntimeError("implementation request to worker request failed closed: replay hashes required")
    scope = request.get("implementation_scope")
    if not isinstance(scope, dict):
        raise FailClosedRuntimeError("implementation request to worker request failed closed: implementation scope invalid")
    if scope.get("allowed_next_step") != "WORKER_REQUEST_GENERATION":
        raise FailClosedRuntimeError("implementation request to worker request failed closed: implementation scope invalid")
    if request.get("candidate_source_type") == "APPROVED_DURABLE_GOVERNED_WORK":
        lineage = request.get("canonical_approved_work_lineage")
        if not isinstance(lineage, dict):
            raise FailClosedRuntimeError(
                "implementation request to worker request failed closed: approved-work lineage missing"
            )
        if not isinstance(scope.get("field_lineage"), dict):
            raise FailClosedRuntimeError(
                "implementation request to worker request failed closed: payload lineage missing"
            )
    constraints = request.get("governance_constraints")
    if not isinstance(constraints, dict) or constraints.get("worker_invocation_allowed") is not False:
        raise FailClosedRuntimeError("implementation request to worker request failed closed: governance constraints invalid")
    for flag in (
        "implementation_executed",
        "worker_invoked",
        "provider_invoked",
        "code_modified",
        "governance_modified",
        "authorization_created",
        "execution_requested",
        "dispatch_requested",
    ):
        if request.get(flag) is not False:
            raise FailClosedRuntimeError(
                f"implementation request to worker request failed closed: request {flag} must be false"
            )


def _worker_request_artifact(
    *,
    bridge_id: str,
    implementation_request: dict[str, Any],
    requested_by: str,
    created_at: str,
    worker_constraints: dict[str, Any] | None,
    request_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    constraints = _worker_constraints(worker_constraints)
    implementation_scope = deepcopy(implementation_request["implementation_scope"])
    repository_scope_status = implementation_scope.get("repository_scope_status")
    repository_targets = deepcopy(implementation_scope.get("repository_targets") or [])
    approved_durable_work_source = (
        implementation_request.get("candidate_source_type")
        == "APPROVED_DURABLE_GOVERNED_WORK"
    )
    unresolved_repository_scope = approved_durable_work_source and (
        str(repository_scope_status or "").startswith("UNRESOLVED")
        or not repository_targets
    )
    artifact = {
        "artifact_type": WORKER_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_VERSION,
        "worker_request_id": f"{_require_string(bridge_id, 'bridge_id')}:WORKER-REQUEST",
        "bridge_id": bridge_id,
        "request_status": request_status,
        "source_implementation_request": implementation_request["implementation_request_id"],
        "source_implementation_request_hash": implementation_request["artifact_hash"],
        "source_ppp_candidate": implementation_request["source_ppp_candidate"],
        "source_ppp_candidate_hash": implementation_request["source_ppp_candidate_hash"],
        "source_improvement_intent": implementation_request["source_improvement_intent"],
        "source_improvement_intent_hash": implementation_request["source_improvement_intent_hash"],
        "source_gap_artifact": implementation_request["source_gap_artifact"],
        "source_gap_hash": implementation_request["source_gap_hash"],
        "candidate_source_type": implementation_request.get("candidate_source_type"),
        "canonical_approved_work_lineage": deepcopy(
            implementation_request.get("canonical_approved_work_lineage")
        ),
        "replay_references": deepcopy(implementation_request["replay_references"]),
        "replay_hashes": deepcopy(implementation_request["replay_hashes"]),
        "human_approval_reference": implementation_request["human_approval_reference"],
        "human_approval_hash": implementation_request["human_approval_hash"],
        "human_approval_required": True,
        "human_authority_preserved": True,
        "worker_objective": implementation_request["implementation_objective"],
        "implementation_scope": implementation_scope,
        "worker_payload_field_lineage": deepcopy(
            implementation_scope.get("field_lineage")
        ),
        "repository_scope_status": repository_scope_status,
        "repository_targets": repository_targets,
        "worker_constraints": constraints,
        "governance_requirements": {
            "dispatch_requires_separate_governance": True,
            "worker_invocation_requires_separate_governance": True,
            "execution_requires_separate_authorization": True,
            "human_approval_remains_mandatory": True,
            "replay_lineage_required": True,
            "fail_closed_required": True,
        },
        "governance_classification": deepcopy(implementation_request["governance_classification"]),
        "affected_runtime": implementation_request["affected_runtime"],
        "affected_lifecycle_stage": implementation_request["affected_lifecycle_stage"],
        "requested_by": _require_string(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "certification_status": "CERTIFIED_IMPLEMENTATION_REQUEST_ACCEPTED",
        "replay_lineage_preserved": True,
        "ready_for_worker_dispatch_governance": not unresolved_repository_scope,
        "dispatch_blocked_by_unresolved_repository_scope": (
            unresolved_repository_scope
        ),
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_worker_request_artifact(
    *,
    bridge_id: str,
    implementation_request_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_VERSION,
        "worker_request_id": f"{bridge_id}:WORKER-REQUEST" if isinstance(bridge_id, str) else "INVALID",
        "bridge_id": bridge_id if isinstance(bridge_id, str) else "INVALID",
        "request_status": FAILED_CLOSED,
        "source_implementation_request": implementation_request_artifact.get("implementation_request_id")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_implementation_request_hash": implementation_request_artifact.get("artifact_hash")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_ppp_candidate": implementation_request_artifact.get("source_ppp_candidate")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_ppp_candidate_hash": implementation_request_artifact.get("source_ppp_candidate_hash")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_improvement_intent": implementation_request_artifact.get("source_improvement_intent")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_improvement_intent_hash": implementation_request_artifact.get("source_improvement_intent_hash")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_gap_artifact": implementation_request_artifact.get("source_gap_artifact")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "source_gap_hash": implementation_request_artifact.get("source_gap_hash")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "candidate_source_type": implementation_request_artifact.get("candidate_source_type")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "canonical_approved_work_lineage": deepcopy(
            implementation_request_artifact.get("canonical_approved_work_lineage")
        )
        if isinstance(implementation_request_artifact, dict)
        else None,
        "replay_references": [],
        "replay_hashes": [],
        "human_approval_reference": implementation_request_artifact.get("human_approval_reference")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "human_approval_hash": implementation_request_artifact.get("human_approval_hash")
        if isinstance(implementation_request_artifact, dict)
        else None,
        "human_approval_required": True,
        "human_authority_preserved": True,
        "worker_objective": None,
        "implementation_scope": {},
        "worker_payload_field_lineage": {},
        "repository_scope_status": None,
        "repository_targets": [],
        "worker_constraints": deepcopy(DEFAULT_WORKER_CONSTRAINTS),
        "governance_requirements": {},
        "governance_classification": {},
        "affected_runtime": None,
        "affected_lifecycle_stage": None,
        "requested_by": requested_by if isinstance(requested_by, str) else None,
        "created_at": created_at if isinstance(created_at, str) else None,
        "certification_status": FAILED_CLOSED,
        "replay_lineage_preserved": False,
        "ready_for_worker_dispatch_governance": False,
        "dispatch_blocked_by_unresolved_repository_scope": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "governance_modified": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(worker_request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(worker_request)
    artifact = {
        "event_type": "WORKER_REQUEST_RETURNED",
        "worker_request_reference": worker_request["worker_request_id"],
        "worker_request_hash": worker_request["artifact_hash"],
        "request_status": worker_request["request_status"],
        "source_implementation_request": worker_request["source_implementation_request"],
        "source_ppp_candidate": worker_request["source_ppp_candidate"],
        "source_improvement_intent": worker_request["source_improvement_intent"],
        "source_gap_artifact": worker_request["source_gap_artifact"],
        "replay_lineage_preserved": worker_request["replay_lineage_preserved"],
        "human_approval_required": worker_request["human_approval_required"],
        "ready_for_worker_dispatch_governance": worker_request["ready_for_worker_dispatch_governance"],
        "worker_dispatched": False,
        "worker_invoked": False,
        "implementation_executed": False,
        "provider_invoked": False,
        "code_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": worker_request["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(worker_request: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": AIGOL_IMPLEMENTATION_REQUEST_TO_WORKER_REQUEST_BRIDGE_VERSION,
        "request_status": worker_request["request_status"],
        "worker_request_artifact": deepcopy(worker_request),
        "worker_request_returned_artifact": deepcopy(returned),
        "worker_request_replay_reference": str(replay_path),
        "worker_request_artifact_generated": worker_request["request_status"] == WORKER_REQUEST_CREATED,
        "replay_lineage_preserved": worker_request["replay_lineage_preserved"],
        "human_approval_required": worker_request["human_approval_required"],
        "execution_prevented": worker_request["execution_requested"] is False
        and worker_request["implementation_executed"] is False
        and worker_request["worker_dispatched"] is False
        and worker_request["worker_invoked"] is False,
        "ready_for_worker_dispatch_governance": worker_request["ready_for_worker_dispatch_governance"],
        "failure_reason": worker_request["failure_reason"],
    }
    capture["implementation_request_to_worker_request_bridge_capture_hash"] = replay_hash(capture)
    return capture


def _worker_constraints(worker_constraints: dict[str, Any] | None) -> dict[str, Any]:
    constraints = deepcopy(DEFAULT_WORKER_CONSTRAINTS)
    if worker_constraints is None:
        return constraints
    if not isinstance(worker_constraints, dict):
        raise FailClosedRuntimeError("implementation request to worker request failed closed: worker constraints invalid")
    forbidden_true = {
        "dispatch_allowed",
        "worker_invocation_allowed",
        "implementation_execution_allowed",
        "provider_invocation_allowed",
        "code_modification_allowed",
        "governance_modification_allowed",
    }
    for key, value in worker_constraints.items():
        if key in forbidden_true and value is not False:
            raise FailClosedRuntimeError("implementation request to worker request failed closed: worker constraints exceed bridge")
        constraints[key] = deepcopy(value)
    return constraints


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("implementation request to worker request failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation request to worker request failed closed: artifact must be object")
    _verify_artifact_hash(artifact)


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("implementation request to worker request artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("implementation request to worker request artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("implementation request to worker request replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("implementation request to worker request replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation request to worker request failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"implementation request to worker request failed closed: {field_name} must be a replay hash"
        )
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _hash_list(value: Any) -> list[str]:
    return [item for item in _string_list(value) if item.startswith("sha256:")]


def _unique_relative_paths(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(
            f"implementation request to worker request failed closed: {field_name} are required"
        )
    normalized: list[str] = []
    for item in value:
        text = _require_string(item, field_name).replace("\\", "/")
        path = PurePosixPath(text)
        if path.is_absolute() or ".." in path.parts or text in {".", ""}:
            raise FailClosedRuntimeError(
                f"implementation request to worker request failed closed: {field_name} must be workspace-relative"
            )
        normalized.append(path.as_posix())
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(
            f"implementation request to worker request failed closed: {field_name} contain duplicates"
        )
    return sorted(normalized)


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "implementation request to worker request failed closed"
