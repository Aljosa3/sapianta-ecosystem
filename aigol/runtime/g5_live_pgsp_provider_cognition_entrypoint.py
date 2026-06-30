"""Live PGSP entrypoint for bounded read-only provider cognition review."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.g5_pgsp_bound_read_only_provider_cognition_runtime import (
    G5_02_RUNTIME_VERSION,
    ProviderExecutor,
    READ_ONLY_PROVIDER_COGNITION_COMPLETED,
    reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay,
    run_g5_pgsp_bound_read_only_provider_cognition_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


G5_03_RUNTIME_VERSION = "G5_03_PROVIDER_COGNITION_PGSP_LIVE_ENTRYPOINT_AND_UHCL_REVIEW_V1"

LIVE_PGSP_CONTEXT_ARTIFACT_V1 = "G5_03_LIVE_PGSP_CONTEXT_ARTIFACT_V1"
LIVE_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1 = "G5_03_LIVE_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1"
LIVE_PROVIDER_COGNITION_GOVERNANCE_ARTIFACT_V1 = "G5_03_PROVIDER_COGNITION_GOVERNANCE_ARTIFACT_V1"
LIVE_G5_02_ROUTING_ARTIFACT_V1 = "G5_03_LIVE_G5_02_ROUTING_ARTIFACT_V1"
LIVE_G5_02_CAPTURE_ARTIFACT_V1 = "G5_03_LIVE_G5_02_CAPTURE_ARTIFACT_V1"
LIVE_UHCL_PROVIDER_COGNITION_REVIEW_ARTIFACT_V1 = "G5_03_UHCL_PROVIDER_COGNITION_REVIEW_ARTIFACT_V1"
LIVE_PROVIDER_COGNITION_SESSION_EVIDENCE_ARTIFACT_V1 = "G5_03_PROVIDER_COGNITION_SESSION_EVIDENCE_ARTIFACT_V1"

LIVE_PGSP_PROVIDER_COGNITION_RECORDED = "G5_03_LIVE_PGSP_PROVIDER_COGNITION_RECORDED"
LIVE_PGSP_ROUTED_TO_G5_02 = "G5_03_LIVE_PGSP_ROUTED_TO_G5_02"
LIVE_PROVIDER_COGNITION_GOVERNANCE_PASSED = "G5_03_PROVIDER_COGNITION_GOVERNANCE_PASSED"

REPLAY_STEPS = (
    "live_pgsp_context_recorded",
    "live_provider_cognition_request_recorded",
    "live_provider_cognition_governance_recorded",
    "live_g5_02_routing_recorded",
    "live_g5_02_capture_recorded",
    "live_uhcl_provider_cognition_review_recorded",
    "live_provider_cognition_session_evidence_recorded",
)


def run_g5_live_pgsp_provider_cognition_entrypoint(
    *,
    session_id: str,
    operator_request: str,
    human_review_response: str,
    provider_identity_artifact: dict[str, Any],
    execution_authorization_artifact: dict[str, Any],
    provider_executor: ProviderExecutor,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture live PGSP context and route bounded cognition execution through G5-02."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)

    context = _live_pgsp_context_artifact(
        session_id=session_id,
        operator_request=operator_request,
        human_review_response=human_review_response,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], context)

    request = _live_provider_cognition_request_artifact(
        session_id=session_id,
        context=context,
        created_at=created_at,
    )
    _persist_step(replay_path, 1, REPLAY_STEPS[1], request)

    governance = _live_governance_artifact(
        session_id=session_id,
        context=context,
        request=request,
        created_at=created_at,
    )
    _persist_step(replay_path, 2, REPLAY_STEPS[2], governance)

    routing = _live_g5_02_routing_artifact(
        session_id=session_id,
        request=request,
        governance=governance,
        created_at=created_at,
    )
    _persist_step(replay_path, 3, REPLAY_STEPS[3], routing)

    g5_02_capture = run_g5_pgsp_bound_read_only_provider_cognition_runtime(
        session_id=f"{session_id}:G5-02",
        cognition_request=request["provider_cognition_request"],
        provider_identity_artifact=provider_identity_artifact,
        execution_authorization_artifact=execution_authorization_artifact,
        provider_executor=provider_executor,
        created_at=created_at,
        replay_dir=replay_path / "g5_02_provider_cognition",
    )
    g5_02_replay = reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(
        g5_02_capture["replay_reference"]
    )
    g5_02_projection = _live_g5_02_capture_artifact(
        session_id=session_id,
        routing=routing,
        g5_02_capture=g5_02_capture,
        g5_02_replay=g5_02_replay,
        created_at=created_at,
    )
    _persist_step(replay_path, 4, REPLAY_STEPS[4], g5_02_projection)

    uhcl_review = _live_uhcl_review_artifact(
        session_id=session_id,
        context=context,
        g5_02_capture=g5_02_capture,
        g5_02_replay=g5_02_replay,
        created_at=created_at,
    )
    _persist_step(replay_path, 5, REPLAY_STEPS[5], uhcl_review)

    evidence = _live_session_evidence_artifact(
        session_id=session_id,
        context=context,
        request=request,
        governance=governance,
        routing=routing,
        g5_02_projection=g5_02_projection,
        uhcl_review=uhcl_review,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    _persist_step(replay_path, 6, REPLAY_STEPS[6], evidence)
    return _capture(evidence, replay_path)


def reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct the G5-03 live PGSP provider cognition entrypoint replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G5-03 live provider cognition replay ordering mismatch")
        _verify_hash(wrapper, "replay_hash", "G5-03 live provider cognition replay hash mismatch")
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_hash(artifact, "artifact_hash", "G5-03 live provider cognition artifact hash mismatch")
        _validate_boundary_flags(artifact)
        wrappers.append(wrapper)

    context = wrappers[0]["artifact"]
    request = wrappers[1]["artifact"]
    governance = wrappers[2]["artifact"]
    routing = wrappers[3]["artifact"]
    g5_02_projection = wrappers[4]["artifact"]
    uhcl_review = wrappers[5]["artifact"]
    evidence = wrappers[6]["artifact"]

    expected = {
        "context_hash": context["artifact_hash"],
        "provider_cognition_request_hash": request["artifact_hash"],
        "governance_checkpoint_hash": governance["artifact_hash"],
        "routing_hash": routing["artifact_hash"],
        "g5_02_capture_hash": g5_02_projection["artifact_hash"],
        "uhcl_review_hash": uhcl_review["artifact_hash"],
    }
    for field, value in expected.items():
        if evidence[field] != value:
            raise FailClosedRuntimeError(f"G5-03 live provider cognition {field} mismatch")
    g5_02_replay = reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(
        g5_02_projection["g5_02_replay_reference"]
    )
    if g5_02_replay["replay_hash"] != g5_02_projection["g5_02_replay_hash"]:
        raise FailClosedRuntimeError("G5-03 nested G5-02 replay hash mismatch")

    return {
        "runtime_version": G5_03_RUNTIME_VERSION,
        "session_id": evidence["session_id"],
        "session_status": evidence["session_status"],
        "routing_status": routing["routing_status"],
        "target_runtime": routing["target_runtime"],
        "provider_execution_status": evidence["provider_execution_status"],
        "canonical_review_response_class": uhcl_review["canonical_review_response_class"],
        "governance_checkpoint_status": governance["governance_checkpoint_status"],
        "provider_invoked": evidence["provider_invoked"],
        "provider_dispatch_count": evidence["provider_dispatch_count"],
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "replay_artifact_count": len(wrappers),
        "g5_02_replay_artifact_count": g5_02_replay["replay_artifact_count"],
        "replay_reference": str(replay_path),
        "g5_02_replay_reference": g5_02_projection["g5_02_replay_reference"],
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _live_pgsp_context_artifact(
    *,
    session_id: str,
    operator_request: str,
    human_review_response: str,
    created_at: str,
) -> dict[str, Any]:
    response_class = _canonical_review_response(human_review_response)
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_PGSP_CONTEXT_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "session_status": LIVE_PGSP_PROVIDER_COGNITION_RECORDED,
            "pgsp_context_source": "LIVE_PGSP_DEVELOPMENT_FLOW",
            "operator_request": _require_string(operator_request, "operator_request"),
            "operator_request_hash": replay_hash(_require_string(operator_request, "operator_request")),
            "human_review_response": _require_string(human_review_response, "human_review_response"),
            "human_review_response_hash": replay_hash(_require_string(human_review_response, "human_review_response")),
            "canonical_review_response_class": response_class,
            "adapter_scope": ["input_capture", "rendering", "response_capture", "session_interaction"],
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": False,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _live_provider_cognition_request_artifact(
    *,
    session_id: str,
    context: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    provider_request = (
        "Review this PGSP governed development request as read-only cognition evidence. "
        "Identify risks, replay considerations, and governance review points. "
        f"Request: {context['operator_request']}"
    )
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "context_hash": context["artifact_hash"],
            "provider_cognition_request": provider_request,
            "provider_cognition_request_hash": replay_hash(provider_request),
            "request_source": "PGSP_CONTEXT",
            "read_only": True,
            "cognition_only": True,
            "worker_execution_requested": False,
            "repository_mutation_requested": False,
            "deployment_requested": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": True,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _live_governance_artifact(
    *,
    session_id: str,
    context: dict[str, Any],
    request: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_PROVIDER_COGNITION_GOVERNANCE_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "governance_checkpoint_status": LIVE_PROVIDER_COGNITION_GOVERNANCE_PASSED,
            "context_hash": context["artifact_hash"],
            "provider_cognition_request_hash": request["artifact_hash"],
            "pgsp_session_boundary_preserved": True,
            "provider_identity_boundary_required": True,
            "credential_boundary_required": True,
            "read_only_boundary_preserved": True,
            "cognition_only_boundary_preserved": True,
            "worker_boundary_preserved": True,
            "mutation_boundary_preserved": True,
            "deployment_boundary_preserved": True,
            "approval_activation_performed": False,
            "authorization_activation_performed": False,
            "retry_permitted": False,
            "fallback_permitted": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": True,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _live_g5_02_routing_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    governance: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_G5_02_ROUTING_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "routing_status": LIVE_PGSP_ROUTED_TO_G5_02,
            "target_runtime": G5_02_RUNTIME_VERSION,
            "provider_cognition_request_hash": request["artifact_hash"],
            "governance_checkpoint_hash": governance["artifact_hash"],
            "routing_mode": "LIVE_PGSP_TO_G5_02",
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": True,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _live_g5_02_capture_artifact(
    *,
    session_id: str,
    routing: dict[str, Any],
    g5_02_capture: dict[str, Any],
    g5_02_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_G5_02_CAPTURE_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "routing_hash": routing["artifact_hash"],
            "target_runtime": G5_02_RUNTIME_VERSION,
            "g5_02_session_id": g5_02_capture["session_id"],
            "g5_02_execution_status": g5_02_capture["execution_status"],
            "g5_02_summary_hash": g5_02_capture["summary_hash"],
            "g5_02_replay_reference": g5_02_capture["replay_reference"],
            "g5_02_replay_hash": g5_02_replay["replay_hash"],
            "g5_02_replay_artifact_count": g5_02_replay["replay_artifact_count"],
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": g5_02_capture["provider_invoked"],
            "provider_request_created": True,
            "provider_response_received": g5_02_capture["provider_response_received"],
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _live_uhcl_review_artifact(
    *,
    session_id: str,
    context: dict[str, Any],
    g5_02_capture: dict[str, Any],
    g5_02_replay: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    success = g5_02_capture["execution_status"] == READ_ONLY_PROVIDER_COGNITION_COMPLETED
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_UHCL_PROVIDER_COGNITION_REVIEW_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "communication_owner": "UHCL",
            "session_id": _require_string(session_id, "session_id"),
            "context_hash": context["artifact_hash"],
            "g5_02_summary_hash": g5_02_capture["summary_hash"],
            "g5_02_replay_hash": g5_02_replay["replay_hash"],
            "canonical_review_response_class": context["canonical_review_response_class"],
            "review_status": "PROVIDER_COGNITION_AVAILABLE_FOR_HUMAN_REVIEW" if success else "PROVIDER_COGNITION_FAILED_CLOSED_REVIEW",
            "review_summary": (
                "Read-only provider cognition evidence is available for human review."
                if success
                else "Read-only provider cognition failed closed; no retry, fallback, worker execution, or mutation occurred."
            ),
            "human_review_response_hash": context["human_review_response_hash"],
            "provider_output_authoritative": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": g5_02_capture["provider_invoked"],
            "provider_request_created": True,
            "provider_response_received": g5_02_capture["provider_response_received"],
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _live_session_evidence_artifact(
    *,
    session_id: str,
    context: dict[str, Any],
    request: dict[str, Any],
    governance: dict[str, Any],
    routing: dict[str, Any],
    g5_02_projection: dict[str, Any],
    uhcl_review: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = _base_artifact(
        {
            "artifact_type": LIVE_PROVIDER_COGNITION_SESSION_EVIDENCE_ARTIFACT_V1,
            "runtime_version": G5_03_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "session_status": LIVE_PGSP_PROVIDER_COGNITION_RECORDED,
            "context_hash": context["artifact_hash"],
            "provider_cognition_request_hash": request["artifact_hash"],
            "governance_checkpoint_hash": governance["artifact_hash"],
            "routing_hash": routing["artifact_hash"],
            "g5_02_capture_hash": g5_02_projection["artifact_hash"],
            "uhcl_review_hash": uhcl_review["artifact_hash"],
            "provider_execution_status": g5_02_projection["g5_02_execution_status"],
            "provider_dispatch_count": 1,
            "replay_reference": _require_string(replay_reference, "replay_reference"),
            "g5_02_replay_reference": g5_02_projection["g5_02_replay_reference"],
            "g5_02_replay_hash": g5_02_projection["g5_02_replay_hash"],
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": g5_02_projection["provider_invoked"],
            "provider_request_created": True,
            "provider_response_received": g5_02_projection["provider_response_received"],
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _capture(evidence: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": G5_03_RUNTIME_VERSION,
        "session_id": evidence["session_id"],
        "session_status": evidence["session_status"],
        "provider_execution_status": evidence["provider_execution_status"],
        "provider_invoked": evidence["provider_invoked"],
        "provider_dispatch_count": evidence["provider_dispatch_count"],
        "provider_response_received": evidence["provider_response_received"],
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": True,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "replay_reference": str(replay_path),
        "g5_02_replay_reference": evidence["g5_02_replay_reference"],
        "summary_artifact": deepcopy(evidence),
        "summary_hash": evidence["artifact_hash"],
        "replay_visible": True,
    }


def _canonical_review_response(response: str) -> str:
    lowered = _require_string(response, "human_review_response").lower()
    if any(token in lowered for token in ("confirm", "approved", "acknowledge", "accept")):
        return "CONFIRMATION"
    if any(token in lowered for token in ("continue", "proceed", "next")):
        return "CONTINUATION"
    if any(token in lowered for token in ("clarify", "question", "explain")):
        return "CLARIFICATION"
    if any(token in lowered for token in ("modify", "change", "adjust")):
        return "MODIFICATION"
    if any(token in lowered for token in ("reject", "stop", "deny")):
        return "REJECTION"
    raise FailClosedRuntimeError("G5-03 live provider cognition failed closed: human review response does not map")


def _base_artifact(values: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "retry_performed": False,
        "fallback_performed": False,
        "provider_authority": False,
        "governance_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "mutation_authority": False,
        "deployment_authority": False,
        "replay_visible": True,
    }
    artifact.update(values)
    return artifact


def _with_artifact_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(artifact)
    result["artifact_hash"] = replay_hash(result)
    return result


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
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


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("G5-03 live provider cognition failed closed: replay directory already contains artifacts")
    replay_path.mkdir(parents=True, exist_ok=True)


def _verify_hash(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _validate_boundary_flags(artifact: dict[str, Any]) -> None:
    for field in (
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "repository_mutated",
        "deployment_performed",
        "retry_performed",
        "fallback_performed",
        "provider_authority",
        "governance_authority",
        "approval_authority",
        "authorization_authority",
        "mutation_authority",
        "deployment_authority",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G5-03 live provider cognition replay failed closed: {field} must be false")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("G5-03 live provider cognition replay failed closed: replay must be visible")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"G5-03 live provider cognition failed closed: {field_name} must be object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G5-03 live provider cognition failed closed: {field_name} is required")
    return value.strip()
