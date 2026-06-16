"""Clarification continuity runtime for interactive ACLI conversations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarification_lifecycle_resolution_runtime import (
    active_clarification_state,
    resolve_clarification_lifecycle,
)
from aigol.runtime.human_execution_intent_detection import (
    NO_EXECUTION_INTENT,
    detect_human_execution_intent,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unknown_domain_clarification_runtime import (
    CLARIFICATION_REQUIRED,
    CREATE_DOMAIN,
    UNKNOWN_DOMAIN_ARTIFACT_V1,
)


AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION = "AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_V1"
CLARIFICATION_CONTINUITY_STATUS = "CLARIFICATION_CONTINUITY_STATUS"

CLARIFICATION_REPLY_BINDING_ARTIFACT_V1 = "CLARIFICATION_REPLY_BINDING_ARTIFACT_V1"
CLARIFICATION_RESPONSE_ARTIFACT_V1 = "CLARIFICATION_RESPONSE_ARTIFACT_V1"
CLARIFICATION_RESOLUTION_ARTIFACT_V1 = "CLARIFICATION_RESOLUTION_ARTIFACT_V1"
CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1 = "CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1"

CLARIFICATION_RESOLVED = "CLARIFICATION_RESOLVED"
WORKFLOW_RESUME_READY = "WORKFLOW_RESUME_READY"
FAILED_CLOSED = "FAILED_CLOSED"

CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
HUMAN_INTENT_CLARIFICATION_INTAKE = "HUMAN_INTENT_CLARIFICATION_INTAKE"

REPLAY_STEPS = (
    "clarification_reply_binding_recorded",
    "clarification_response_recorded",
    "clarification_resolution_recorded",
    "clarification_workflow_resume_recorded",
)


def detect_active_clarification(
    *,
    session_root: str | Path,
) -> dict[str, Any]:
    """Detect exactly one unresolved clarification in session replay."""

    lifecycle = resolve_clarification_lifecycle(session_root=session_root)
    state = lifecycle.get("active_clarification")
    return {
        "open_clarification_detected": state is not None,
        "active_clarification_count": lifecycle["active_clarification_count"],
        "active_clarification": deepcopy(state),
        "clarification_lifecycle": deepcopy(lifecycle),
        "fail_closed": False,
        "failure_reason": None,
    }


def should_bind_operator_reply_to_active_clarification(
    *,
    session_root: str | Path,
    human_prompt: str,
) -> dict[str, Any]:
    """Return whether a prompt is a reply to the active clarification."""

    lifecycle = resolve_clarification_lifecycle(session_root=session_root)
    state = lifecycle.get("active_clarification")
    if not isinstance(state, dict):
        return _reply_gate_capture(lifecycle, False, "NO_ACTIVE_CLARIFICATION")
    prompt = _require_string(human_prompt, "human_prompt")
    if state.get("originating_workflow_id") == HUMAN_INTENT_CLARIFICATION_INTAKE:
        return _reply_gate_capture(lifecycle, True, "HUMAN_INTENT_CLARIFICATION_REPLY_MATCH")
    if _matches_missing_information(prompt, state):
        return _reply_gate_capture(lifecycle, True, "MISSING_INFORMATION_REPLY_MATCH")
    if _looks_like_new_governed_request(prompt):
        return _reply_gate_capture(lifecycle, False, "NEW_REQUEST_DETECTED")
    return _reply_gate_capture(lifecycle, False, "REPLY_DOES_NOT_MATCH_ACTIVE_CLARIFICATION_SCOPE")


def run_clarification_continuity(
    *,
    continuity_id: str,
    session_root: str | Path,
    turn_id: str,
    prompt_id: str,
    operator_reply: str,
    current_chain_id: str | None,
    created_at: str,
    replay_dir: str | Path,
    expected_workflow_id: str = CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
) -> dict[str, Any]:
    """Bind an operator reply to an active clarification and record resume-ready evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        state = _require_active_clarification(Path(session_root))
        _validate_state(
            state=state,
            current_chain_id=current_chain_id,
            expected_workflow_id=expected_workflow_id,
            created_at=created_at,
        )
        binding = _binding_artifact(
            continuity_id=continuity_id,
            state=state,
            turn_id=turn_id,
            prompt_id=prompt_id,
            operator_reply=operator_reply,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        response = _response_artifact(
            continuity_id=continuity_id,
            state=state,
            binding=binding,
            operator_reply=operator_reply,
            created_at=created_at,
        )
        resolution = _resolution_artifact(
            continuity_id=continuity_id,
            state=state,
            response=response,
            created_at=created_at,
        )
        resume = _resume_artifact(
            continuity_id=continuity_id,
            state=state,
            resolution=resolution,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], binding)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], resolution)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], resume)
        return _capture(binding, response, resolution, resume, state, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        binding = _failed_binding_artifact(
            continuity_id=continuity_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            operator_reply=operator_reply,
            current_chain_id=current_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        _persist_failure_if_possible(replay_path, binding)
        return _failed_capture(binding, replay_path)


def reconstruct_clarification_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarification continuity replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarification continuity replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarification continuity replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarification continuity artifact")
        wrappers.append(wrapper)
    binding = wrappers[0]["artifact"]
    response = wrappers[1]["artifact"]
    resolution = wrappers[2]["artifact"]
    resume = wrappers[3]["artifact"]
    if response.get("clarification_reply_binding_reference") != binding["clarification_reply_binding_id"]:
        raise FailClosedRuntimeError("clarification continuity binding reference mismatch")
    if response.get("clarification_reply_binding_hash") != binding["artifact_hash"]:
        raise FailClosedRuntimeError("clarification continuity binding hash mismatch")
    if resolution.get("clarification_response_reference") != response["clarification_response_id"]:
        raise FailClosedRuntimeError("clarification continuity response reference mismatch")
    if resolution.get("clarification_response_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("clarification continuity response hash mismatch")
    if resume.get("clarification_resolution_reference") != resolution["clarification_resolution_id"]:
        raise FailClosedRuntimeError("clarification continuity resolution reference mismatch")
    if resume.get("clarification_resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("clarification continuity resolution hash mismatch")
    return {
        "milestone_id": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "final_classification": CLARIFICATION_CONTINUITY_STATUS,
        "continuity_status": resume["workflow_resume_status"],
        "clarification_resolved": resolution["resolution_status"] == CLARIFICATION_RESOLVED,
        "workflow_resumed": resume["workflow_resume_status"] == WORKFLOW_RESUME_READY,
        "originating_workflow_id": resume["originating_workflow_id"],
        "originating_intent": resume["originating_intent"],
        "proposed_domain": resume["proposed_domain"],
        "canonical_chain_id": resume["canonical_chain_id"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_clarification_continuity_summary(capture: dict[str, Any]) -> str:
    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Reply Bound",
            "",
            "Clarification Resolved",
            "",
            f"Originating Workflow: {capture.get('originating_workflow_id')}",
            f"Originating Intent: {capture.get('originating_intent')}",
            f"Proposed Domain: {capture.get('proposed_domain')}",
            "",
            "Workflow Resumed",
            "Next Governed Workflow Stage: OCS_OR_EXECUTION_HANDOFF_REVIEW",
        ]
    )


def _reply_gate_capture(lifecycle: dict[str, Any], should_bind: bool, reason: str) -> dict[str, Any]:
    return {
        "open_clarification_detected": lifecycle.get("active_clarification_count") == 1,
        "active_clarification_count": lifecycle.get("active_clarification_count"),
        "active_clarification": deepcopy(lifecycle.get("active_clarification")),
        "should_bind_reply": should_bind,
        "binding_decision_reason": reason,
        "clarification_lifecycle": deepcopy(lifecycle),
        "fail_closed": False,
        "failure_reason": None,
    }


def _looks_like_new_governed_request(human_prompt: str) -> bool:
    normalized = human_prompt.lower().strip()
    execution_intent = detect_human_execution_intent(human_prompt)
    if execution_intent.get("intent_class") != NO_EXECUTION_INTENT:
        return True
    return "domain" in normalized and any(term in normalized for term in ("create", "new", "add", "build", "make"))


def _matches_missing_information(human_prompt: str, state: dict[str, Any]) -> bool:
    request = state.get("clarification_request_artifact")
    if not isinstance(request, dict):
        return False
    missing_information = request.get("missing_information")
    if not isinstance(missing_information, list) or not missing_information:
        return False
    normalized = human_prompt.lower()
    required_markers = {
        "primary purpose": ("purpose",),
        "expected capabilities": ("capability", "capabilities"),
        "target users": ("user", "users"),
        "domain name": ("domain", "name", "called", "named"),
    }
    known_requirements = 0
    matched = 0
    for item in missing_information:
        markers = required_markers.get(str(item).lower())
        if markers is None:
            continue
        known_requirements += 1
        if any(marker in normalized for marker in markers):
            matched += 1
    return known_requirements > 0 and matched == known_requirements


def _active_clarification_state(session_root: Path) -> dict[str, Any] | None:
    return active_clarification_state(session_root=session_root)


def _require_active_clarification(session_root: Path) -> dict[str, Any]:
    state = _active_clarification_state(session_root)
    if state is None:
        raise FailClosedRuntimeError("clarification continuity failed closed: missing clarification state")
    return state


def _validate_state(
    *,
    state: dict[str, Any],
    current_chain_id: str | None,
    expected_workflow_id: str,
    created_at: str,
) -> None:
    request = state["clarification_request_artifact"]
    workflow_id = state.get("originating_workflow_id")
    if workflow_id != expected_workflow_id:
        raise FailClosedRuntimeError("clarification continuity failed closed: workflow mismatch")
    if request.get("originating_intent") != CREATE_DOMAIN:
        raise FailClosedRuntimeError("clarification continuity failed closed: workflow mismatch")
    chain_id = request.get("canonical_chain_id")
    if current_chain_id is not None and current_chain_id != chain_id:
        raise FailClosedRuntimeError("clarification continuity failed closed: clarification chain mismatch")
    expires_at = request.get("expires_at")
    if isinstance(expires_at, str) and _require_string(created_at, "created_at") > expires_at:
        raise FailClosedRuntimeError("clarification continuity failed closed: expired clarification")


def _binding_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    turn_id: str,
    prompt_id: str,
    operator_reply: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": CLARIFICATION_REPLY_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "clarification_reply_binding_id": f"{_require_string(continuity_id, 'continuity_id')}:BINDING",
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "operator_reply_hash": replay_hash(_require_string(operator_reply, "operator_reply")),
        "clarification_request_reference": request["clarification_id"],
        "clarification_request_hash": request["artifact_hash"],
        "originating_workflow_id": state["originating_workflow_id"],
        "originating_intent": request["originating_intent"],
        "originating_replay_reference": state["originating_replay_reference"],
        "canonical_chain_id": request["canonical_chain_id"],
        "binding_status": "OPERATOR_REPLY_BOUND",
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _response_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    binding: dict[str, Any],
    operator_reply: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": CLARIFICATION_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "clarification_response_id": f"{_require_string(continuity_id, 'continuity_id')}:RESPONSE",
        "clarification_reply_binding_reference": binding["clarification_reply_binding_id"],
        "clarification_reply_binding_hash": binding["artifact_hash"],
        "clarification_request_reference": request["clarification_id"],
        "clarification_request_hash": request["artifact_hash"],
        "operator_reply_hash": binding["operator_reply_hash"],
        "missing_information_requested": deepcopy(request.get("missing_information", [])),
        "response_completeness_status": "OPERATOR_RESPONSE_RECEIVED",
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resolution_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    response: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": CLARIFICATION_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "clarification_resolution_id": f"{_require_string(continuity_id, 'continuity_id')}:RESOLUTION",
        "clarification_response_reference": response["clarification_response_id"],
        "clarification_response_hash": response["artifact_hash"],
        "clarification_request_reference": request["clarification_id"],
        "clarification_request_hash": request["artifact_hash"],
        "resolution_status": CLARIFICATION_RESOLVED,
        "originating_intent": request["originating_intent"],
        "proposed_domain": request["proposed_domain"],
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resume_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    resolution: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": CLARIFICATION_WORKFLOW_RESUME_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "clarification_workflow_resume_id": f"{_require_string(continuity_id, 'continuity_id')}:WORKFLOW-RESUME",
        "clarification_resolution_reference": resolution["clarification_resolution_id"],
        "clarification_resolution_hash": resolution["artifact_hash"],
        "originating_workflow_id": state["originating_workflow_id"],
        "originating_intent": request["originating_intent"],
        "proposed_domain": request["proposed_domain"],
        "canonical_chain_id": request["canonical_chain_id"],
        "workflow_resume_status": WORKFLOW_RESUME_READY,
        "resume_stage": "CLARIFICATION_RESOLVED",
        "next_required_boundary": "OCS_OR_EXECUTION_HANDOFF_REVIEW",
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    binding: dict[str, Any],
    response: dict[str, Any],
    resolution: dict[str, Any],
    resume: dict[str, Any],
    state: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    capture = {
        "command": "aigol conversation",
        "milestone_id": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "final_classification": CLARIFICATION_CONTINUITY_STATUS,
        "response_status": WORKFLOW_RESUME_READY,
        "response_source": "CLARIFICATION_CONTINUITY_RUNTIME",
        "response_text": "",
        "clarification_reply_binding_artifact": deepcopy(binding),
        "clarification_response_artifact": deepcopy(response),
        "clarification_resolution_artifact": deepcopy(resolution),
        "clarification_workflow_resume_artifact": deepcopy(resume),
        "clarification_continuity_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": request["canonical_chain_id"],
        "current_chain_id": request["canonical_chain_id"],
        "latest_chain_id": request["canonical_chain_id"],
        "originating_workflow_id": state["originating_workflow_id"],
        "originating_intent": request["originating_intent"],
        "proposed_domain": request["proposed_domain"],
        "open_clarification_detected": True,
        "operator_reply_bound": True,
        "clarification_resolved": True,
        "workflow_resumed": True,
        "fail_closed": False,
        "failure_reason": None,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
    }
    capture["response_text"] = render_clarification_continuity_summary(capture)
    capture["clarification_continuity_hash"] = replay_hash(capture)
    return capture


def _failed_binding_artifact(
    *,
    continuity_id: str,
    turn_id: str,
    prompt_id: str,
    operator_reply: Any,
    current_chain_id: str | None,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFICATION_REPLY_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "clarification_reply_binding_id": f"{continuity_id}:BINDING",
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "operator_reply_hash": replay_hash(operator_reply) if isinstance(operator_reply, str) else None,
        "clarification_request_reference": None,
        "clarification_request_hash": None,
        "originating_workflow_id": None,
        "originating_intent": None,
        "originating_replay_reference": None,
        "canonical_chain_id": current_chain_id,
        "binding_status": FAILED_CLOSED,
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_capture(binding: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "command": "aigol conversation",
        "milestone_id": AIGOL_CLARIFICATION_CONTINUITY_RUNTIME_VERSION,
        "final_classification": CLARIFICATION_CONTINUITY_STATUS,
        "response_status": FAILED_CLOSED,
        "response_source": "CLARIFICATION_CONTINUITY_RUNTIME",
        "response_text": f"FAILED_CLOSED: {binding.get('failure_reason')}",
        "clarification_reply_binding_artifact": deepcopy(binding),
        "clarification_continuity_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "open_clarification_detected": False,
        "operator_reply_bound": False,
        "clarification_resolved": False,
        "workflow_resumed": False,
        "fail_closed": True,
        "failure_reason": binding.get("failure_reason"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
    }


def _load_verified_wrapper(path: Path, replay_index: int, replay_step: str) -> dict[str, Any]:
    wrapper = load_json(path)
    if wrapper.get("replay_index") != replay_index or wrapper.get("replay_step") != replay_step:
        raise FailClosedRuntimeError("clarification continuity failed closed: replay mismatch")
    _verify_wrapper_hash(wrapper)
    return wrapper


def _verified_artifact(wrapper: dict[str, Any], label: str) -> dict[str, Any]:
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"clarification continuity failed closed: {label} artifact missing")
    _verify_artifact_hash(artifact, label)
    return artifact


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarification continuity replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarification continuity artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"000_{REPLAY_STEPS[0]}.json"
        if not path.exists():
            _persist_step(replay_dir, 0, REPLAY_STEPS[0], artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("clarification continuity failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("clarification continuity failed closed: replay mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("clarification continuity replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("clarification continuity failed closed: replay mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarification continuity failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
