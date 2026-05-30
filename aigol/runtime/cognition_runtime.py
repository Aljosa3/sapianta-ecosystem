"""Canonical deterministic Cognition Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_runtime import CREATED as CONVERSATION_CREATED
from aigol.runtime.conversation_runtime import run_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


COGNITION_RUNTIME_VERSION = "COGNITION_RUNTIME_V1"
STARTED = "COGNITION_SESSION_STARTED"
COMPLETED = "COGNITION_SESSION_COMPLETED"
FAILED = "COGNITION_SESSION_FAILED"
STATE = "COGNITION_RUNTIME_STATE"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("cognition_session_started", "cognition_runtime_state", "cognition_session_completed")

FORBIDDEN_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }
)


def run_cognition(
    *,
    cognition_session_id: str,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    retrieval_scope: str = "CONSTITUTIONAL_INVARIANTS",
    artifact_query: str = "CONSTITUTIONAL_INVARIANTS",
) -> dict[str, Any]:
    """Run the canonical cognition entrypoint over the bounded conversation path."""

    replay_path = Path(replay_dir)
    started: dict[str, Any] | None = None
    try:
        _ensure_cognition_replay_available(replay_path)
        started = _session_started(
            cognition_session_id=cognition_session_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], started)

        conversation = run_conversation(
            conversation_id=f"{cognition_session_id}:CONVERSATION",
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
            replay_dir=replay_path / "conversation_runtime",
            retrieval_scope=retrieval_scope,
            artifact_query=artifact_query,
        )
        conversation_response = conversation["conversation_response_artifact"]
        if conversation_response.get("conversation_status") != CONVERSATION_CREATED:
            raise FailClosedRuntimeError("cognition runtime failed closed: conversation dependency failed")

        state = _runtime_state(
            cognition_session_id=cognition_session_id,
            prompt_id=prompt_id,
            conversation_response=conversation_response,
            created_at=created_at,
            state_status=COMPLETED,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], state)
        completed = _session_terminal(
            event_type=COMPLETED,
            cognition_session_id=cognition_session_id,
            prompt_id=prompt_id,
            started=started,
            state=state,
            conversation_response=conversation_response,
            created_at=created_at,
            failure_reason=None,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], completed)
        return _capture(started, state, completed)
    except Exception as exc:
        if started is None:
            started = _failed_started(
                cognition_session_id=cognition_session_id,
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
            _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], started)
        state = _failed_runtime_state(
            cognition_session_id=cognition_session_id,
            prompt_id=prompt_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], state)
        failed = _session_terminal(
            event_type=FAILED,
            cognition_session_id=cognition_session_id,
            prompt_id=prompt_id,
            started=started,
            state=state,
            conversation_response=None,
            created_at=created_at,
            failure_reason=state["failure_reason"],
        )
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], failed)
        return _capture(started, state, failed)


def reconstruct_cognition_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Cognition Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("cognition replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "cognition artifact")
        wrappers.append(wrapper)

    started = wrappers[0]["artifact"]
    state = wrappers[1]["artifact"]
    terminal = wrappers[2]["artifact"]
    if state.get("cognition_session_id") != started["cognition_session_id"]:
        raise FailClosedRuntimeError("cognition replay state reference mismatch")
    if terminal.get("cognition_session_id") != started["cognition_session_id"]:
        raise FailClosedRuntimeError("cognition replay terminal reference mismatch")
    if terminal.get("state_hash") != state["artifact_hash"]:
        raise FailClosedRuntimeError("cognition replay state hash mismatch")
    _validate_state(state)
    return {
        "cognition_session_id": started["cognition_session_id"],
        "prompt_id": started["prompt_id"],
        "prompt": started["prompt_text"],
        "intent_id": state["intent_id"],
        "memory_consultation_id": state["memory_consultation_id"],
        "response_id": state["response_id"],
        "conversation_response_id": state["conversation_response_id"],
        "cognition_status": state["cognition_status"],
        "terminal_event": terminal["event_type"],
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _ensure_cognition_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _session_started(
    *, cognition_session_id: str, prompt_id: str, human_prompt: str, created_at: str
) -> dict[str, Any]:
    prompt = _normalize_text(human_prompt, "human_prompt")
    artifact = {
        "event_type": STARTED,
        "cognition_session_id": _require_string(cognition_session_id, "cognition_session_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "cognition_runtime_version": COGNITION_RUNTIME_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_started(
    *, cognition_session_id: Any, prompt_id: Any, human_prompt: Any, created_at: Any, failure_reason: str
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "event_type": STARTED,
        "cognition_session_id": (
            cognition_session_id
            if isinstance(cognition_session_id, str) and cognition_session_id.strip()
            else "INVALID_COGNITION_SESSION_ID"
        ),
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "cognition_runtime_version": COGNITION_RUNTIME_VERSION,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "authority": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _runtime_state(
    *,
    cognition_session_id: str,
    prompt_id: str,
    conversation_response: dict[str, Any],
    created_at: str,
    state_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(conversation_response, "conversation response artifact")
    artifact = {
        "event_type": STATE,
        "cognition_session_id": _require_string(cognition_session_id, "cognition_session_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "intent_id": _require_string(conversation_response.get("intent_id"), "intent_id"),
        "memory_consultation_id": f"{cognition_session_id}:CONVERSATION:MEMORY_CONSULTATION",
        "response_id": _require_string(conversation_response.get("response_id"), "response_id"),
        "conversation_response_id": _require_string(conversation_response.get("response_id"), "response_id"),
        "conversation_response_hash": conversation_response["artifact_hash"],
        "cognition_status": state_status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_state(artifact)
    return artifact


def _failed_runtime_state(
    *, cognition_session_id: Any, prompt_id: Any, created_at: Any, failure_reason: str
) -> dict[str, Any]:
    artifact = {
        "event_type": STATE,
        "cognition_session_id": (
            cognition_session_id
            if isinstance(cognition_session_id, str) and cognition_session_id.strip()
            else "INVALID_COGNITION_SESSION_ID"
        ),
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "intent_id": None,
        "memory_consultation_id": None,
        "response_id": None,
        "conversation_response_id": None,
        "conversation_response_hash": None,
        "cognition_status": FAILED_CLOSED,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _session_terminal(
    *,
    event_type: str,
    cognition_session_id: str,
    prompt_id: str,
    started: dict[str, Any],
    state: dict[str, Any],
    conversation_response: dict[str, Any] | None,
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(started, "cognition started artifact")
    _verify_artifact_hash(state, "cognition state artifact")
    artifact = {
        "event_type": event_type,
        "cognition_session_id": cognition_session_id,
        "prompt_id": prompt_id,
        "started_hash": started["artifact_hash"],
        "state_hash": state["artifact_hash"],
        "conversation_response_hash": (
            conversation_response.get("artifact_hash") if isinstance(conversation_response, dict) else None
        ),
        "cognition_status": COMPLETED if event_type == COMPLETED else FAILED_CLOSED,
        "created_at": created_at,
        "replay_visible": True,
        "authority": False,
        "reconstruction_metadata": {
            "prompt_reconstructable": True,
            "intent_reconstructable": conversation_response is not None,
            "memory_consultation_reconstructable": conversation_response is not None,
            "response_reconstructable": conversation_response is not None,
            "conversation_result_reconstructable": conversation_response is not None,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "authority_introduced": False,
        },
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(started: dict[str, Any], state: dict[str, Any], terminal: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "cognition_session_started": deepcopy(started),
        "cognition_runtime_state": deepcopy(state),
        "cognition_session_terminal": deepcopy(terminal),
    }
    capture["cognition_runtime_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("cognition replay step ordering mismatch")
    _verify_artifact_hash(artifact, "cognition artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"{index:03d}_{step}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, index, step, artifact)
        except FailClosedRuntimeError:
            return


def _validate_state(state: dict[str, Any]) -> None:
    if state.get("event_type") != STATE:
        raise FailClosedRuntimeError("cognition runtime failed closed: invalid state artifact")
    if state.get("authority") is not False:
        raise FailClosedRuntimeError("cognition runtime failed closed: authority introduced")
    if state.get("provider_invoked") is not False:
        raise FailClosedRuntimeError("cognition runtime failed closed: provider invocation detected")
    if state.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("cognition runtime failed closed: worker invocation detected")
    if state.get("execution_requested") is not False:
        raise FailClosedRuntimeError("cognition runtime failed closed: execution request detected")
    if state.get("replay_visible") is not True:
        raise FailClosedRuntimeError("cognition runtime failed closed: replay visibility missing")
    if FORBIDDEN_FIELDS.intersection(state):
        raise FailClosedRuntimeError("cognition runtime failed closed: authority-bearing state")
    status = state.get("cognition_status")
    if status == COMPLETED:
        for field in ("intent_id", "memory_consultation_id", "response_id", "conversation_response_id"):
            _require_string(state.get(field), field)
    elif status != FAILED_CLOSED:
        raise FailClosedRuntimeError("cognition runtime failed closed: invalid state status")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("cognition replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "cognition runtime failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
