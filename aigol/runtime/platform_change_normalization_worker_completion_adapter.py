"""Complete one authenticated PLATFORM_CHANGE_NORMALIZATION Worker result.

This is a deliberately narrow additive adapter.  It does not select a
capability, authorize execution, dispatch a Worker, or alter a Worker lifecycle
owner.  It produces and binds completion evidence only for the already-bound
PLATFORM_CHANGE_NORMALIZATION capability.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_runtime import EXECUTING, reconstruct_execution_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_change_normalization_execution_binding_runtime import (
    CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION,
    PLATFORM_CHANGE_NORMALIZATION,
    reconstruct_platform_change_normalization_execution_binding_replay,
    validate_platform_change_normalization_execution_binding,
)
from aigol.runtime.project_context_semantic_capability_route import (
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_result_capture_runtime import (
    WORKER_RESULT_CAPTURED,
    default_worker_output_for_invocation,
    reconstruct_worker_result_capture_replay,
)
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    reconstruct_worker_result_validation_replay,
)


PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION = (
    "G54_05_PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_V1"
)
PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_EVIDENCE_ARTIFACT_V1 = (
    "PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_EVIDENCE_ARTIFACT_V1"
)
PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ARTIFACT_V1 = (
    "PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ARTIFACT_V1"
)
PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_RESULT_ARTIFACT_V1 = (
    "PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_RESULT_ARTIFACT_V1"
)
WORKER_CAPABILITY_COMPLETED = "WORKER_CAPABILITY_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "worker_capability_completion_evidence_recorded",
    "worker_capability_completion_recorded",
    "worker_capability_completion_result_recorded",
)

AUTHORITY_FLAGS = {
    "capability_selection_is_execution_authorization": False,
    "authorization_created": False,
    "execution_authorized": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "worker_lifecycle_modified": False,
    "provider_invoked": False,
    "repository_mutated": False,
    "governance_mutated": False,
    "replay_mutated": False,
}


def create_platform_change_normalization_worker_completion_evidence(
    *,
    capability_execution_binding_artifact: dict[str, Any],
    capability_execution_binding_replay_reference: str | Path,
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str | Path,
    execution_artifact: dict[str, Any],
    execution_replay_reference: str | Path,
    completed_at: str,
) -> dict[str, Any]:
    """Build exact Worker output evidence after an authenticated execution start.

    The returned object is passed unchanged to the existing Worker-result
    capture owner.  This function neither captures a result nor marks a Worker
    complete.
    """

    binding = _authenticated_binding(
        capability_execution_binding_artifact,
        capability_execution_binding_replay_reference,
    )
    invocation = _authenticated_invocation(
        worker_invocation_artifact,
        worker_invocation_replay_reference,
    )
    execution = _authenticated_execution(
        execution_artifact,
        execution_replay_reference,
        invocation,
    )
    normalized = _normalized_change_from_binding(binding)
    output = default_worker_output_for_invocation(invocation, captured_at=completed_at)
    output["payload"] = {
        "completion_evidence_type": (
            PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_EVIDENCE_ARTIFACT_V1
        ),
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "capability_execution_binding_id": binding["binding_id"],
        "capability_execution_binding_hash": binding["artifact_hash"],
        "normalized_change_artifact": deepcopy(normalized),
        "normalized_change_artifact_hash": normalized["artifact_hash"],
        "execution_reference": execution["execution_id"],
        "execution_hash": execution["artifact_hash"],
        "worker_completion_status": WORKER_CAPABILITY_COMPLETED,
        "completed_at": _require_string(completed_at, "completed_at"),
    }
    output["artifact_hash"] = replay_hash(
        {key: value for key, value in output.items() if key != "artifact_hash"}
    )
    return output


def complete_platform_change_normalization_worker_capability(
    *,
    completion_id: str,
    capability_execution_binding_artifact: dict[str, Any],
    capability_execution_binding_replay_reference: str | Path,
    execution_authorization_replay_reference: str | Path,
    worker_completion_evidence: dict[str, Any],
    worker_result_capture_artifact: dict[str, Any],
    worker_result_capture_replay_reference: str | Path,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str | Path,
    completed_by: str,
    completed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind authenticated Worker completion evidence into a human-returnable result."""

    replay_path = Path(replay_dir)
    identifier = _safe_string(completion_id)
    try:
        _ensure_replay_available(replay_path)
        authenticated = _authenticate_completion_inputs(
            capability_execution_binding_artifact=capability_execution_binding_artifact,
            capability_execution_binding_replay_reference=capability_execution_binding_replay_reference,
            execution_authorization_replay_reference=execution_authorization_replay_reference,
            worker_completion_evidence=worker_completion_evidence,
            worker_result_capture_artifact=worker_result_capture_artifact,
            worker_result_capture_replay_reference=worker_result_capture_replay_reference,
            worker_result_validation_artifact=worker_result_validation_artifact,
            worker_result_validation_replay_reference=worker_result_validation_replay_reference,
        )
        evidence = _completion_evidence_artifact(
            completion_id=_require_string(completion_id, "completion_id"),
            authenticated=authenticated,
            completed_at=_require_string(completed_at, "completed_at"),
        )
        completion = _completion_artifact(
            completion_id=_require_string(completion_id, "completion_id"),
            evidence=evidence,
            completed_by=_require_string(completed_by, "completed_by"),
            completed_at=_require_string(completed_at, "completed_at"),
        )
        result = _result_artifact(completion)
        for index, artifact in enumerate((evidence, completion, result)):
            _persist_step(replay_path, index, REPLAY_STEPS[index], artifact)
        return _capture(evidence, completion, result, replay_path)
    except Exception as exc:
        result = _failed_result(identifier, _failure_reason(exc))
        _persist_failure_if_possible(replay_path, result)
        return _capture(None, None, result, replay_path)


def reconstruct_platform_change_normalization_worker_completion_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the successful completion binding and all upstream evidence."""

    replay_path = Path(replay_dir)
    wrappers = _load_success_wrappers(replay_path)
    evidence, completion, result = (wrapper["artifact"] for wrapper in wrappers)
    _verify_artifact_hash(evidence, "completion evidence")
    completion = validate_platform_change_normalization_worker_completion(completion)
    _verify_artifact_hash(result, "completion result")
    if completion["completion_evidence_hash"] != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion replay evidence mismatch")
    if result.get("worker_capability_completion_hash") != completion["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion replay result mismatch")
    authenticated = _authenticate_completion_inputs(
        capability_execution_binding_artifact=_artifact_from_replay(
            evidence["capability_execution_binding_replay_reference"],
            "001_capability_execution_binding_recorded.json",
            "capability execution binding",
        ),
        capability_execution_binding_replay_reference=evidence[
            "capability_execution_binding_replay_reference"
        ],
        execution_authorization_replay_reference=evidence[
            "execution_authorization_replay_reference"
        ],
        worker_completion_evidence=evidence["worker_completion_evidence"],
        worker_result_capture_artifact=_artifact_from_replay(
            evidence["worker_result_capture_replay_reference"],
            "002_result_capture_artifact_recorded.json",
            "worker result capture",
        ),
        worker_result_capture_replay_reference=evidence[
            "worker_result_capture_replay_reference"
        ],
        worker_result_validation_artifact=_artifact_from_replay(
            evidence["worker_result_validation_replay_reference"],
            "002_validation_artifact_recorded.json",
            "worker result validation",
        ),
        worker_result_validation_replay_reference=evidence[
            "worker_result_validation_replay_reference"
        ],
    )
    if evidence["normalized_change_artifact_hash"] != authenticated["normalized"]["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion replay normalization mismatch")
    return {
        "completion_id": completion["completion_id"],
        "completion_status": completion["completion_status"],
        "selected_capability_identifier": completion["selected_capability_identifier"],
        "normalized_change_artifact_hash": completion["normalized_change_artifact_hash"],
        "human_visible_result": deepcopy(completion["human_visible_result"]),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def validate_platform_change_normalization_worker_completion(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a public completed-capability artifact without granting authority."""

    candidate = _validated_hashed_object(artifact, "worker capability completion")
    if candidate.get("artifact_type") != PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker capability completion artifact type mismatch")
    if candidate.get("runtime_version") != PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION:
        raise FailClosedRuntimeError("worker capability completion version mismatch")
    if candidate.get("completion_status") != WORKER_CAPABILITY_COMPLETED:
        raise FailClosedRuntimeError("worker capability completion status mismatch")
    if candidate.get("selected_capability_identifier") != PLATFORM_CHANGE_NORMALIZATION:
        raise FailClosedRuntimeError("worker capability completion capability identity mismatch")
    for field in (
        "completion_id",
        "completion_evidence_hash",
        "capability_execution_binding_id",
        "capability_execution_binding_hash",
        "normalized_change_artifact_hash",
        "execution_authorization_reference",
        "worker_result_capture_reference",
        "worker_result_capture_hash",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
    ):
        _require_string(candidate.get(field), field)
    if candidate.get("worker_completion_authenticated") is not True:
        raise FailClosedRuntimeError("worker capability completion authentication missing")
    if candidate.get("replay_continuity_preserved") is not True:
        raise FailClosedRuntimeError("worker capability completion replay continuity missing")
    if candidate.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("worker capability completion authority boundary mismatch")
    if not isinstance(candidate.get("human_visible_result"), dict):
        raise FailClosedRuntimeError("worker capability completion human result invalid")
    return candidate


def present_platform_change_normalization_worker_completion(
    completion_capture: dict[str, Any],
) -> dict[str, Any]:
    """Return a replay-authenticated completion presentation for Human Interfaces."""

    if not isinstance(completion_capture, dict):
        raise FailClosedRuntimeError("worker capability completion capture is invalid")
    replay_reference = _require_string(
        completion_capture.get("worker_capability_completion_replay_reference"),
        "worker_capability_completion_replay_reference",
    )
    reconstructed = reconstruct_platform_change_normalization_worker_completion_replay(
        replay_reference
    )
    artifact = completion_capture.get("worker_capability_completion_artifact")
    validated = validate_platform_change_normalization_worker_completion(artifact)
    if reconstructed["completion_id"] != validated["completion_id"]:
        raise FailClosedRuntimeError("worker capability completion presentation mismatch")
    return {
        "presentation_status": "HUMAN_VISIBLE_WORKER_CAPABILITY_COMPLETION",
        "completion_id": validated["completion_id"],
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "human_visible_result": deepcopy(validated["human_visible_result"]),
        "worker_capability_completion_replay_reference": replay_reference,
        "worker_capability_completion_replay_hash": reconstructed["replay_hash"],
        "authorization_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "replay_visible": True,
    }


def _authenticate_completion_inputs(**inputs: Any) -> dict[str, Any]:
    binding = _authenticated_binding(
        inputs["capability_execution_binding_artifact"],
        inputs["capability_execution_binding_replay_reference"],
    )
    authorization = _authenticated_authorization(
        inputs["execution_authorization_replay_reference"], binding
    )
    capture = _authenticated_result_capture(
        inputs["worker_result_capture_artifact"],
        inputs["worker_result_capture_replay_reference"],
    )
    validation = _authenticated_result_validation(
        inputs["worker_result_validation_artifact"],
        inputs["worker_result_validation_replay_reference"],
        capture,
    )
    completion_evidence = _validated_completion_evidence(
        inputs["worker_completion_evidence"], binding, capture
    )
    if capture["authorization_reference"] != authorization["authorization_id"]:
        raise FailClosedRuntimeError("worker capability completion authorization mismatch")
    if capture["execution_packet_reference"] != authorization["execution_packet_reference"]:
        raise FailClosedRuntimeError("worker capability completion packet mismatch")
    if completion_evidence["execution_reference"] != capture["execution_reference"]:
        raise FailClosedRuntimeError("worker capability completion execution mismatch")
    return {
        "binding": binding,
        "authorization": authorization,
        "capture": capture,
        "validation": validation,
        "completion_evidence": completion_evidence,
        "normalized": _normalized_change_from_binding(binding),
    }


def _authenticated_binding(artifact: dict[str, Any], replay_reference: str | Path) -> dict[str, Any]:
    binding = validate_platform_change_normalization_execution_binding(artifact)
    replay_path = Path(_require_string(str(replay_reference), "capability_execution_binding_replay_reference"))
    reconstructed = reconstruct_platform_change_normalization_execution_binding_replay(replay_path)
    persisted = _binding_artifact_from_reference(replay_path)
    evidence = _artifact_from_replay(
        replay_path,
        "000_capability_evidence_bound.json",
        "capability execution binding evidence",
    )
    if binding["artifact_hash"] != persisted["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion binding replay mismatch")
    if evidence.get("binding_id") != persisted["binding_id"]:
        raise FailClosedRuntimeError("worker capability completion binding evidence mismatch")
    if reconstructed["binding_status"] != CAPABILITY_EXECUTION_BINDING_READY_FOR_AUTHORIZATION:
        raise FailClosedRuntimeError("worker capability completion binding status invalid")
    persisted["_execution_ready_replay_reference"] = _require_string(
        evidence.get("execution_ready_replay_reference"),
        "binding_execution_ready_replay_reference",
    )
    return persisted


def _authenticated_authorization(replay_reference: str | Path, binding: dict[str, Any]) -> dict[str, Any]:
    replay_path = Path(_require_string(str(replay_reference), "execution_authorization_replay_reference"))
    reconstructed = reconstruct_execution_authorization_replay(replay_path)
    if reconstructed["authorization_status"] != EXECUTION_AUTHORIZED:
        raise FailClosedRuntimeError("worker capability completion authorization invalid")
    request = _artifact_from_replay(replay_path, "000_authorization_request_recorded.json", "authorization request")
    if not _same_path(
        request.get("execution_ready_replay_reference"),
        binding["_execution_ready_replay_reference"],
    ):
        raise FailClosedRuntimeError("worker capability completion authorization readiness mismatch")
    reconstructed["_replay_reference"] = str(replay_path)
    return reconstructed


def _authenticated_result_capture(artifact: dict[str, Any], replay_reference: str | Path) -> dict[str, Any]:
    replay_path = Path(_require_string(str(replay_reference), "worker_result_capture_replay_reference"))
    reconstructed = reconstruct_worker_result_capture_replay(replay_path)
    persisted = _artifact_from_replay(replay_path, "002_result_capture_artifact_recorded.json", "worker result capture")
    supplied = _validated_hashed_object(artifact, "provided worker result capture")
    if reconstructed["result_capture_status"] != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("worker capability completion result capture invalid")
    if supplied["artifact_hash"] != persisted["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion result capture mismatch")
    if not persisted.get("execution_reference") or not persisted.get("execution_hash"):
        raise FailClosedRuntimeError("worker capability completion execution evidence missing")
    persisted["_replay_reference"] = str(replay_path)
    return persisted


def _authenticated_result_validation(
    artifact: dict[str, Any], replay_reference: str | Path, capture: dict[str, Any]
) -> dict[str, Any]:
    replay_path = Path(_require_string(str(replay_reference), "worker_result_validation_replay_reference"))
    reconstructed = reconstruct_worker_result_validation_replay(replay_path)
    persisted = _artifact_from_replay(replay_path, "002_validation_artifact_recorded.json", "worker result validation")
    supplied = _validated_hashed_object(artifact, "provided worker result validation")
    if reconstructed["validation_status"] != RESULT_VALIDATED:
        raise FailClosedRuntimeError("worker capability completion result validation invalid")
    if supplied["artifact_hash"] != persisted["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion result validation mismatch")
    if persisted.get("worker_result_capture_hash") != capture["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion validation capture mismatch")
    persisted["_replay_reference"] = str(replay_path)
    return persisted


def _validated_completion_evidence(
    evidence: dict[str, Any], binding: dict[str, Any], capture: dict[str, Any]
) -> dict[str, Any]:
    output = _validated_hashed_object(evidence, "worker completion evidence")
    if output.get("artifact_hash") != capture.get("worker_output_hash"):
        raise FailClosedRuntimeError("worker capability completion output mismatch")
    payload = output.get("payload")
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("worker capability completion payload invalid")
    checks = (
        payload.get("completion_evidence_type") == PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_EVIDENCE_ARTIFACT_V1,
        payload.get("selected_capability_identifier") == PLATFORM_CHANGE_NORMALIZATION,
        payload.get("capability_execution_binding_id") == binding["binding_id"],
        payload.get("capability_execution_binding_hash") == binding["artifact_hash"],
        payload.get("normalized_change_artifact_hash") == binding["normalized_change_artifact_hash"],
        payload.get("worker_completion_status") == WORKER_CAPABILITY_COMPLETED,
        output.get("worker_invocation_reference") == capture["worker_invocation_reference"],
        output.get("authorization_reference") == capture["authorization_reference"],
        output.get("execution_packet_reference") == capture["execution_packet_reference"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker capability completion evidence mismatch")
    _require_string(payload.get("execution_reference"), "completion_execution_reference")
    _require_string(payload.get("execution_hash"), "completion_execution_hash")
    return {
        "worker_output": output,
        "artifact_hash": output["artifact_hash"],
        "execution_reference": payload["execution_reference"],
        "execution_hash": payload["execution_hash"],
        "normalized_change_artifact_hash": payload["normalized_change_artifact_hash"],
    }


def _normalized_change_from_binding(binding: dict[str, Any]) -> dict[str, Any]:
    route = reconstruct_project_context_semantic_capability_route(
        binding["semantic_capability_route_reference"]
    )
    lifecycle = Path(route["lifecycle_replay_reference"])
    result = _artifact_from_replay(
        lifecycle, "002_g28_invocation_result_recorded.json", "normalization invocation result"
    )
    normalized = result.get("g28_invocation_result", {}).get("output_artifact")
    normalized = _validated_hashed_object(normalized, "normalized change artifact")
    if normalized["artifact_hash"] != binding["normalized_change_artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion normalized change mismatch")
    return normalized


def _authenticated_invocation(artifact: dict[str, Any], replay_reference: str | Path) -> dict[str, Any]:
    replay_path = Path(_require_string(str(replay_reference), "worker_invocation_replay_reference"))
    reconstructed = reconstruct_worker_invocation_replay(replay_path)
    persisted = _artifact_from_replay(replay_path, "002_invocation_artifact_recorded.json", "worker invocation")
    supplied = _validated_hashed_object(artifact, "provided worker invocation")
    if reconstructed["invocation_status"] != WORKER_INVOKED or supplied["artifact_hash"] != persisted["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion invocation mismatch")
    return persisted


def _authenticated_execution(
    artifact: dict[str, Any], replay_reference: str | Path, invocation: dict[str, Any]
) -> dict[str, Any]:
    replay_path = Path(_require_string(str(replay_reference), "execution_replay_reference"))
    reconstructed = reconstruct_execution_replay(replay_path)
    persisted = _artifact_from_replay(replay_path, "000_execution_started.json", "execution")
    supplied = _validated_hashed_object(artifact, "provided execution")
    if reconstructed["execution_status"] != EXECUTING or supplied["artifact_hash"] != persisted["artifact_hash"]:
        raise FailClosedRuntimeError("worker capability completion execution state invalid")
    if persisted.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker capability completion execution invocation mismatch")
    return persisted


def _completion_evidence_artifact(*, completion_id: str, authenticated: dict[str, Any], completed_at: str) -> dict[str, Any]:
    binding = authenticated["binding"]
    authorization = authenticated["authorization"]
    capture = authenticated["capture"]
    validation = authenticated["validation"]
    artifact = {
        "artifact_type": "WORKER_CAPABILITY_COMPLETION_EVIDENCE_ARTIFACT_V1",
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION,
        "completion_evidence_id": f"{completion_id}:EVIDENCE",
        "completion_id": completion_id,
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "capability_execution_binding_id": binding["binding_id"],
        "capability_execution_binding_hash": binding["artifact_hash"],
        "capability_execution_binding_replay_reference": binding["_replay_reference"],
        "execution_ready_reference": binding["execution_ready_reference"],
        "execution_authorization_reference": authorization["authorization_id"],
        "execution_authorization_replay_reference": authorization["_replay_reference"],
        "worker_result_capture_reference": capture["worker_result_capture_id"],
        "worker_result_capture_hash": capture["artifact_hash"],
        "worker_result_capture_replay_reference": capture["_replay_reference"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_validation_replay_reference": validation["_replay_reference"],
        "normalized_change_artifact_hash": authenticated["normalized"]["artifact_hash"],
        "worker_completion_evidence": deepcopy(
            authenticated["completion_evidence"]["worker_output"]
        ),
        "worker_completion_evidence_hash": authenticated["completion_evidence"]["artifact_hash"],
        "completed_at": completed_at,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _completion_artifact(*, completion_id: str, evidence: dict[str, Any], completed_by: str, completed_at: str) -> dict[str, Any]:
    human_result = {
        "status": WORKER_CAPABILITY_COMPLETED,
        "message": "Platform change normalization completed through the authenticated Worker path.",
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "normalized_change_artifact_hash": evidence["normalized_change_artifact_hash"],
        "worker_result_capture_reference": evidence["worker_result_capture_reference"],
    }
    artifact = {
        "artifact_type": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION,
        "completion_id": completion_id,
        "completion_status": WORKER_CAPABILITY_COMPLETED,
        "selected_capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
        "completion_evidence_hash": evidence["artifact_hash"],
        "capability_execution_binding_id": evidence["capability_execution_binding_id"],
        "capability_execution_binding_hash": evidence["capability_execution_binding_hash"],
        "normalized_change_artifact_hash": evidence["normalized_change_artifact_hash"],
        "execution_authorization_reference": evidence["execution_authorization_reference"],
        "worker_result_capture_reference": evidence["worker_result_capture_reference"],
        "worker_result_capture_hash": evidence["worker_result_capture_hash"],
        "worker_result_validation_reference": evidence["worker_result_validation_reference"],
        "worker_result_validation_hash": evidence["worker_result_validation_hash"],
        "worker_completion_authenticated": True,
        "replay_continuity_preserved": True,
        "completed_by": completed_by,
        "completed_at": completed_at,
        "human_visible_result": human_result,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result_artifact(completion: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_RESULT_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION,
        "completion_id": completion["completion_id"],
        "completion_status": completion["completion_status"],
        "worker_capability_completion_hash": completion["artifact_hash"],
        "human_visible_result": deepcopy(completion["human_visible_result"]),
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(completion_id: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_RESULT_ARTIFACT_V1,
        "runtime_version": PLATFORM_CHANGE_NORMALIZATION_WORKER_COMPLETION_ADAPTER_VERSION,
        "completion_id": completion_id,
        "completion_status": FAILED_CLOSED,
        "worker_capability_completion_hash": None,
        "human_visible_result": None,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(evidence: dict[str, Any] | None, completion: dict[str, Any] | None, result: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "completion_status": result["completion_status"],
        "worker_capability_completion_evidence_artifact": deepcopy(evidence),
        "worker_capability_completion_artifact": deepcopy(completion),
        "worker_capability_completion_result_artifact": deepcopy(result),
        "worker_capability_completion_replay_reference": str(replay_path),
        "worker_capability_completion_replay_hash": replay_hash(_load_success_wrappers(replay_path)) if completion is not None else None,
        "human_visible_result": deepcopy(result.get("human_visible_result")),
        "fail_closed": result["completion_status"] == FAILED_CLOSED,
        "failure_reason": result.get("failure_reason"),
        "authorization_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "replay_mutated": False,
    }


def _binding_artifact_from_reference(reference: str | Path) -> dict[str, Any]:
    binding = _artifact_from_replay(reference, "001_capability_execution_binding_recorded.json", "capability execution binding")
    binding = validate_platform_change_normalization_execution_binding(binding)
    binding["_replay_reference"] = str(Path(reference))
    return binding


def _artifact_from_replay(reference: str | Path, filename: str, label: str) -> dict[str, Any]:
    wrapper = load_json(Path(reference) / filename)
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    return _validated_hashed_object(artifact, label)


def _load_success_wrappers(replay_path: Path) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker capability completion replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        if not isinstance(wrapper.get("artifact"), dict):
            raise FailClosedRuntimeError("worker capability completion replay artifact invalid")
        wrappers.append(wrapper)
    return wrappers


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    replay_path.mkdir(parents=True, exist_ok=True)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_path: Path, result: dict[str, Any]) -> None:
    try:
        if replay_path.exists() and any(replay_path.iterdir()):
            return
        _persist_step(replay_path, 2, REPLAY_STEPS[2], result)
    except Exception:
        return


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("worker capability completion replay destination is not empty")


def _validated_hashed_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} must be an object")
    candidate = deepcopy(value)
    supplied_hash = candidate.pop("artifact_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")
    candidate["artifact_hash"] = supplied_hash
    return candidate


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    _validated_hashed_object(artifact, label)


def _verify_wrapper_hash(wrapper: Any) -> None:
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("worker capability completion replay wrapper invalid")
    candidate = deepcopy(wrapper)
    supplied_hash = candidate.pop("replay_hash", None)
    if supplied_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("worker capability completion replay hash mismatch")


def _same_path(left: Any, right: Any) -> bool:
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    return Path(left).resolve() == Path(right).resolve()


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker capability completion {field} is required")
    return value


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "INVALID"


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__
