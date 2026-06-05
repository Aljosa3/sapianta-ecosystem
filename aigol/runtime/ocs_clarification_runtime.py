"""Bounded OCS clarification runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import OCS_COGNITION_ARTIFACT_V1, OCS_COGNITION_COMPLETED
from aigol.runtime.ocs_semantic_resolution_runtime import (
    OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1,
    OCS_SEMANTIC_RESOLUTION_COMPLETED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_CLARIFICATION_RUNTIME_VERSION = "AIGOL_OCS_CLARIFICATION_RUNTIME_V1"
OCS_CLARIFICATION_ARTIFACT_V1 = "OCS_CLARIFICATION_ARTIFACT_V1"
OCS_CLARIFICATION_REQUIRED = "OCS_CLARIFICATION_REQUIRED"
OCS_CLARIFICATION_NOT_REQUIRED = "OCS_CLARIFICATION_NOT_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "ocs_clarification_recorded",
    "ocs_clarification_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_domain_creation": False,
    "authorizes_human_approval": False,
    "authorizes_automatic_implementation": False,
    "invokes_ppp": False,
}

PROHIBITED_FLAGS = (
    "authority",
    "approval_created",
    "approval_inferred",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "worker_invoked",
    "provider_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
    "automatic_implementation_requested",
    "ppp_invoked",
)


def generate_ocs_clarification(
    *,
    clarification_id: str,
    ocs_cognition_artifact: dict[str, Any],
    ocs_semantic_resolution_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Generate replay-visible OCS clarification evidence without creating authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        cognition = deepcopy(ocs_cognition_artifact)
        semantic = deepcopy(ocs_semantic_resolution_artifact)
        _validate_inputs(cognition, semantic)
        payload = _clarification_payload(cognition, semantic)
        status = OCS_CLARIFICATION_REQUIRED if payload["clarification_requests"] else OCS_CLARIFICATION_NOT_REQUIRED
        artifact = _clarification_artifact(
            clarification_id=clarification_id,
            payload=payload,
            created_at=created_at,
            clarification_status=status,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        artifact = _failed_clarification_artifact(
            clarification_id=clarification_id,
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_ocs_clarification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS clarification evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS clarification replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS clarification replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("clarification_reference") != recorded["clarification_id"]:
        raise FailClosedRuntimeError("OCS clarification returned reference mismatch")
    if returned.get("clarification_artifact_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS clarification returned artifact hash mismatch")
    if returned.get("clarification_hash") != recorded["clarification_hash"]:
        raise FailClosedRuntimeError("OCS clarification returned clarification hash mismatch")
    if recorded.get("clarification_hash") != _compute_clarification_hash(recorded):
        raise FailClosedRuntimeError("OCS clarification hash mismatch")
    return {
        "clarification_id": recorded["clarification_id"],
        "clarification_status": recorded["clarification_status"],
        "clarification_hash": recorded["clarification_hash"],
        "clarification_required": recorded["clarification_required"],
        "clarification_requests": deepcopy(recorded["clarification_requests"]),
        "ambiguity_evidence": deepcopy(recorded["ambiguity_evidence"]),
        "continuity_references": deepcopy(recorded["continuity_references"]),
        "semantic_references": deepcopy(recorded["semantic_references"]),
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "approval_created": False,
        "ppp_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(cognition: dict[str, Any], semantic: dict[str, Any]) -> None:
    _validate_artifact(cognition, OCS_COGNITION_ARTIFACT_V1, "OCS cognition")
    _validate_artifact(semantic, OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1, "OCS semantic resolution")
    if cognition.get("cognition_status") != OCS_COGNITION_COMPLETED:
        raise FailClosedRuntimeError("OCS clarification failed closed: cognition is not completed")
    if semantic.get("resolution_status") != OCS_SEMANTIC_RESOLUTION_COMPLETED:
        raise FailClosedRuntimeError("OCS clarification failed closed: semantic resolution is not completed")
    if semantic.get("source_cognition_hash") != cognition.get("cognition_hash"):
        raise FailClosedRuntimeError("OCS clarification failed closed: semantic cognition hash mismatch")
    _reject_prohibited_flags(cognition)
    _reject_prohibited_flags(semantic)


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"OCS clarification failed closed: invalid {label} artifact")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError(f"OCS clarification failed closed: {label} artifact is not replay-visible")
    _verify_artifact_hash(artifact)


def _clarification_payload(cognition: dict[str, Any], semantic: dict[str, Any]) -> dict[str, Any]:
    requests = _clarification_requests(cognition, semantic)
    ambiguity = {
        "cognition_ambiguity": deepcopy(cognition.get("ambiguity", {})),
        "semantic_ambiguity": deepcopy(semantic.get("ambiguity_detection", {})),
        "authority": False,
    }
    return {
        "source_cognition_id": cognition["cognition_id"],
        "source_cognition_hash": cognition["cognition_hash"],
        "source_semantic_resolution_id": semantic["semantic_resolution_id"],
        "source_semantic_hash": semantic["semantic_hash"],
        "clarification_required": bool(requests),
        "clarification_requests": requests,
        "ambiguity_evidence": ambiguity,
        "continuity_references": deepcopy(semantic.get("continuity_reference_linking", [])),
        "semantic_references": deepcopy(semantic.get("semantic_reference_resolution", [])),
    }


def _clarification_requests(cognition: dict[str, Any], semantic: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for item in cognition.get("clarification_requirements", []):
        if item.get("required") is True:
            payload = {
                "source": "OCS_COGNITION",
                "source_requirement_id": item.get("requirement_id"),
                "reason": item.get("reason"),
            }
            requests.append(
                {
                    "clarification_request_id": replay_hash(payload),
                    **payload,
                    "required": True,
                    "operator_response_required": True,
                    "authority": False,
                }
            )
    for item in semantic.get("clarification_candidates", []):
        if item.get("required") is True:
            payload = {
                "source": "OCS_SEMANTIC_RESOLUTION",
                "source_requirement_id": item.get("clarification_id"),
                "reason": item.get("reason"),
            }
            requests.append(
                {
                    "clarification_request_id": replay_hash(payload),
                    **payload,
                    "required": True,
                    "operator_response_required": True,
                    "authority": False,
                }
            )
    deduped = {item["clarification_request_id"]: item for item in requests}
    return sorted(deduped.values(), key=lambda item: (item["source"], str(item["source_requirement_id"]), item["clarification_request_id"]))


def _clarification_artifact(
    *,
    clarification_id: str,
    payload: dict[str, Any],
    created_at: str,
    clarification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_CLARIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_CLARIFICATION_RUNTIME_VERSION,
        "clarification_id": _require_string(clarification_id, "clarification_id"),
        **deepcopy(payload),
        "clarification_status": clarification_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "ppp_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["clarification_hash"] = _compute_clarification_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_clarification_artifact(*, clarification_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    payload = {
        "source_cognition_id": None,
        "source_cognition_hash": None,
        "source_semantic_resolution_id": None,
        "source_semantic_hash": None,
        "clarification_required": True,
        "clarification_requests": [
            {
                "clarification_request_id": replay_hash({"source": "OCS_CLARIFICATION", "reason": failure_reason}),
                "source": "OCS_CLARIFICATION",
                "source_requirement_id": "OCS_CLARIFICATION_FAILED_CLOSED",
                "reason": failure_reason,
                "required": True,
                "operator_response_required": True,
                "authority": False,
            }
        ],
        "ambiguity_evidence": {
            "cognition_ambiguity": {},
            "semantic_ambiguity": {
                "is_ambiguous": True,
                "ambiguity_reasons": ["OCS clarification failed closed"],
                "authority": False,
            },
            "authority": False,
        },
        "continuity_references": [],
        "semantic_references": [],
    }
    return _clarification_artifact(
        clarification_id=clarification_id,
        payload=payload,
        created_at=created_at,
        clarification_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact)
    returned = {
        "event_type": "OCS_CLARIFICATION_RETURNED",
        "clarification_reference": artifact["clarification_id"],
        "clarification_artifact_hash": artifact["artifact_hash"],
        "clarification_hash": artifact["clarification_hash"],
        "clarification_status": artifact["clarification_status"],
        "clarification_required": artifact["clarification_required"],
        "clarification_request_count": len(artifact["clarification_requests"]),
        "replay_visible": True,
        "authority": False,
        "ppp_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
        "failure_reason": artifact["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_clarification_artifact": deepcopy(artifact),
        "ocs_clarification_returned": deepcopy(returned),
        "ocs_clarification_replay_reference": str(replay_path),
        "clarification_status": artifact["clarification_status"],
        "clarification_hash": artifact["clarification_hash"],
        "clarification_required": artifact["clarification_required"],
        "clarification_requests": deepcopy(artifact["clarification_requests"]),
        "ambiguity_evidence": deepcopy(artifact["ambiguity_evidence"]),
        "continuity_references": deepcopy(artifact["continuity_references"]),
        "semantic_references": deepcopy(artifact["semantic_references"]),
        "fail_closed": artifact["clarification_status"] == FAILED_CLOSED,
        "failure_reason": artifact["failure_reason"],
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "approval_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "automatic_implementation_requested": False,
    }
    capture["ocs_clarification_capture_hash"] = replay_hash(capture)
    return capture


def _compute_clarification_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "source_cognition_hash": artifact["source_cognition_hash"],
            "source_semantic_hash": artifact["source_semantic_hash"],
            "clarification_required": artifact["clarification_required"],
            "clarification_requests": artifact["clarification_requests"],
            "ambiguity_evidence": artifact["ambiguity_evidence"],
            "continuity_references": artifact["continuity_references"],
            "semantic_references": artifact["semantic_references"],
            "clarification_status": artifact["clarification_status"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _reject_prohibited_flags(artifact: dict[str, Any]) -> None:
    for flag in PROHIBITED_FLAGS:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS clarification failed closed: source carries prohibited flag {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag in AUTHORITY_FLAGS:
            if flags.get(flag) is True:
                raise FailClosedRuntimeError(f"OCS clarification failed closed: source carries prohibited authority flag {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS clarification replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("OCS clarification artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS clarification artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS clarification replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS clarification replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS clarification failed closed"
