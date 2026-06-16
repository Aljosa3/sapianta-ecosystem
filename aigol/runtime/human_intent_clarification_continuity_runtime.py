"""Replay-visible continuity for human-intent clarification intake."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarification_lifecycle_resolution_runtime import active_clarification_state
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1 = (
    "AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1"
)
HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS = "HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS"

HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1 = (
    "HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1"
)
HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1 = "HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1"
HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1 = "HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1"
HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1 = (
    "HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1"
)

HUMAN_INTENT_CLARIFICATION_INTAKE = "HUMAN_INTENT_CLARIFICATION_INTAKE"
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
WORKFLOW_SELECTED = "WORKFLOW_SELECTED"
WORKFLOW_SELECTION_AFTER_CLARIFICATION = "WORKFLOW_SELECTION_AFTER_CLARIFICATION"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "human_intent_clarification_reply_binding_recorded",
    "human_intent_clarification_response_recorded",
    "human_intent_clarification_resolution_recorded",
    "human_intent_workflow_selection_after_clarification_recorded",
)


def continue_human_intent_clarification_to_workflow(
    *,
    continuity_id: str,
    session_root: str | Path,
    turn_id: str,
    prompt_id: str,
    clarification_response: str,
    current_chain_id: str | None,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Bind a human-intent clarification response and select the expected workflow."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        state = _require_human_intent_state(Path(session_root))
        _validate_state(state=state, current_chain_id=current_chain_id)
        binding = _binding_artifact(
            continuity_id=continuity_id,
            state=state,
            turn_id=turn_id,
            prompt_id=prompt_id,
            clarification_response=clarification_response,
            created_at=created_at,
            replay_reference=str(replay_path),
        )
        response = _response_artifact(
            continuity_id=continuity_id,
            state=state,
            binding=binding,
            clarification_response=clarification_response,
            created_at=created_at,
        )
        resolution = _resolution_artifact(
            continuity_id=continuity_id,
            state=state,
            response=response,
            clarification_response=clarification_response,
            created_at=created_at,
        )
        selection = _selection_artifact(
            continuity_id=continuity_id,
            state=state,
            resolution=resolution,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], binding)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], resolution)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], selection)
        return _capture(binding, response, resolution, selection, state, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "human intent clarification continuity failed closed"
        return _failed_capture(
            continuity_id=continuity_id,
            turn_id=turn_id,
            prompt_id=prompt_id,
            current_chain_id=current_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )


def reconstruct_human_intent_clarification_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human intent clarification continuity replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human intent clarification continuity artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    selection = wrappers[3]["artifact"]
    return {
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "workflow_id": selection["workflow_id"],
        "routing_status": selection["routing_status"],
        "clarification_response_bound": True,
        "intent_resolution_after_clarification": True,
        "workflow_selection_after_clarification": True,
        "canonical_chain_id": selection["canonical_chain_id"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_human_intent_clarification_continuity_summary(capture: dict[str, Any]) -> str:
    if capture.get("fail_closed") is True:
        return f"FAILED_CLOSED: {capture.get('failure_reason')}"
    return "\n".join(
        [
            "Human Intent Clarification Bound",
            f"Intent Family: {capture.get('intent_family')}",
            f"Selected Workflow: {capture.get('workflow_id')}",
            "Workflow Selection After Clarification: YES",
            "No provider invoked.",
            "No worker invoked.",
            "No execution requested.",
        ]
    )


def _require_human_intent_state(session_root: Path) -> dict[str, Any]:
    state = active_clarification_state(session_root=session_root)
    if not isinstance(state, dict):
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: missing active clarification")
    if state.get("originating_workflow_id") != HUMAN_INTENT_CLARIFICATION_INTAKE:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: workflow mismatch")
    return state


def _validate_state(*, state: dict[str, Any], current_chain_id: str | None) -> None:
    request = state["clarification_request_artifact"]
    chain_id = request.get("canonical_chain_id")
    if current_chain_id is not None and current_chain_id != chain_id:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: chain mismatch")
    targets = request.get("expected_workflow_targets")
    if not isinstance(targets, list) or CREATE_DOMAIN_COMPLIANCE_CLARIFICATION not in targets:
        raise FailClosedRuntimeError("human intent clarification continuity failed closed: target workflow missing")


def _binding_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    turn_id: str,
    prompt_id: str,
    clarification_response: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_REPLY_BINDING_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "binding_id": f"{_require_string(continuity_id, 'continuity_id')}:BINDING",
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_hash": replay_hash(_require_string(clarification_response, "clarification_response")),
        "canonical_chain_id": request["canonical_chain_id"],
        "binding_status": "CLARIFICATION_RESPONSE_BOUND",
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _response_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    binding: dict[str, Any],
    clarification_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_RESPONSE_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "response_id": f"{_require_string(continuity_id, 'continuity_id')}:RESPONSE",
        "binding_reference": binding["binding_id"],
        "binding_hash": binding["artifact_hash"],
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "original_prompt_hash": request.get("routing_decision_hash"),
        "clarification_response_hash": binding["clarification_response_hash"],
        "combined_intent_hash": replay_hash(
            {
                "original_prompt_reference": request.get("routing_decision_reference"),
                "clarification_response": clarification_response,
            }
        ),
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _resolution_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    response: dict[str, Any],
    clarification_response: str,
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "resolution_id": f"{_require_string(continuity_id, 'continuity_id')}:RESOLUTION",
        "response_reference": response["response_id"],
        "response_hash": response["artifact_hash"],
        "clarification_request_reference": request["workflow_selection_id"],
        "clarification_request_hash": request["artifact_hash"],
        "intent_family": request.get("intent_family"),
        "original_workflow_id": request.get("workflow_id"),
        "clarification_response_hash": replay_hash(_require_string(clarification_response, "clarification_response")),
        "resolution_status": "INTENT_RESOLVED_AFTER_CLARIFICATION",
        "selected_workflow_id": CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _selection_artifact(
    *,
    continuity_id: str,
    state: dict[str, Any],
    resolution: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    artifact = {
        "artifact_type": HUMAN_INTENT_WORKFLOW_SELECTION_AFTER_CLARIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "selection_id": f"{_require_string(continuity_id, 'continuity_id')}:WORKFLOW-SELECTION",
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "workflow_id": CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        "routing_status": WORKFLOW_SELECTED,
        "selection_status": WORKFLOW_SELECTION_AFTER_CLARIFICATION,
        "created_at": _require_string(created_at, "created_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    binding: dict[str, Any],
    response: dict[str, Any],
    resolution: dict[str, Any],
    selection: dict[str, Any],
    state: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    request = state["clarification_request_artifact"]
    capture = {
        "command": "aigol conversation",
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "response_status": WORKFLOW_SELECTED,
        "response_source": "HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME",
        "response_text": "",
        "human_intent_clarification_reply_binding_artifact": deepcopy(binding),
        "human_intent_clarification_response_artifact": deepcopy(response),
        "human_intent_clarification_resolution_artifact": deepcopy(resolution),
        "human_intent_workflow_selection_after_clarification_artifact": deepcopy(selection),
        "human_intent_clarification_continuity_replay_reference": str(replay_path),
        "conversation_replay_reference": str(replay_path),
        "canonical_chain_id": request["canonical_chain_id"],
        "current_chain_id": request["canonical_chain_id"],
        "latest_chain_id": request["canonical_chain_id"],
        "originating_workflow_id": HUMAN_INTENT_CLARIFICATION_INTAKE,
        "intent_family": request.get("intent_family"),
        "clarification_response_bound": True,
        "intent_resolution_after_clarification": True,
        "workflow_selection_after_clarification": True,
        "workflow_id": selection["workflow_id"],
        "routing_status": selection["routing_status"],
        "fail_closed": False,
        "failure_reason": None,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["response_text"] = render_human_intent_clarification_continuity_summary(capture)
    capture["human_intent_clarification_continuity_hash"] = replay_hash(capture)
    return capture


def _failed_capture(
    *,
    continuity_id: str,
    turn_id: str,
    prompt_id: str,
    current_chain_id: str | None,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return {
        "command": "aigol conversation",
        "runtime_version": AIGOL_HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME_V1,
        "final_classification": HUMAN_INTENT_CLARIFICATION_CONTINUITY_STATUS,
        "response_status": FAILED_CLOSED,
        "response_source": "HUMAN_INTENT_CLARIFICATION_CONTINUITY_RUNTIME",
        "continuity_id": continuity_id,
        "turn_id": turn_id,
        "prompt_id": prompt_id,
        "canonical_chain_id": current_chain_id,
        "created_at": created_at,
        "replay_reference": replay_reference,
        "fail_closed": True,
        "failure_reason": failure_reason,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human intent clarification continuity replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("human intent clarification continuity failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("human intent clarification continuity artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human intent clarification continuity replay mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("human intent clarification continuity wrapper hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("human intent clarification continuity replay mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
