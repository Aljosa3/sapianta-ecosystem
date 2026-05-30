"""Minimal deterministic Conversation Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_memory_consultation_activation import (
    CONSULTED,
    activate_constitutional_memory_consultation,
)
from aigol.runtime.intent_classifier import CONVERSATION, CONSTITUTIONAL_MEMORY_CONSULTATION, classify_intent
from aigol.runtime.intent_routing_attachment import attach_intent_routing
from aigol.runtime.memory_based_response import CREATED as MEMORY_RESPONSE_CREATED
from aigol.runtime.memory_based_response import create_memory_based_response
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONVERSATION_RUNTIME_VERSION = "CONVERSATION_RUNTIME_V1"
CONVERSATION_RESPONSE_ARTIFACT_V1 = "CONVERSATION_RESPONSE_ARTIFACT_V1"
CONVERSATION_RESPONSE = "CONVERSATION_RESPONSE"
STARTED = "CONVERSATION_STARTED"
CREATED = "CONVERSATION_RESPONSE_CREATED"
RETURNED = "CONVERSATION_RESPONSE_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("conversation_started", "conversation_response_created", "conversation_response_returned")

FORBIDDEN_RESPONSE_FIELDS = frozenset(
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


def run_conversation(
    *,
    conversation_id: str,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    retrieval_scope: str = "CONSTITUTIONAL_INVARIANTS",
    artifact_query: str = "CONSTITUTIONAL_INVARIANTS",
) -> dict[str, Any]:
    """Run the first bounded conversation path over Constitutional Memory evidence."""

    replay_path = Path(replay_dir)
    started: dict[str, Any] | None = None
    try:
        _ensure_conversation_replay_available(replay_path)
        started = _conversation_started(
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], started)

        intent_capture = classify_intent(
            artifact_id=f"{conversation_id}:INTENT",
            human_request_reference=prompt_id,
            human_prompt=human_prompt,
            classification_timestamp=created_at,
            replay_reference=f"{conversation_id}:INTENT_REPLAY",
            replay_dir=replay_path / "intent_classification",
        )
        intent_artifact = intent_capture["intent_classification_artifact"]
        if intent_artifact.get("classification_destination") != CONVERSATION:
            raise FailClosedRuntimeError("conversation runtime failed closed: prompt is not conversation intent")
        if intent_artifact.get("classification_status") != "CLASSIFIED":
            raise FailClosedRuntimeError("conversation runtime failed closed: intent classification failed")

        memory_intent = classify_intent(
            artifact_id=f"{conversation_id}:MEMORY_INTENT",
            human_request_reference=prompt_id,
            human_prompt="Retrieve Constitutional Memory citation.",
            classification_timestamp=created_at,
            replay_reference=f"{conversation_id}:MEMORY_INTENT_REPLAY",
            replay_dir=replay_path / "memory_intent_classification",
        )
        memory_artifact = memory_intent["intent_classification_artifact"]
        if memory_artifact.get("classification_destination") != CONSTITUTIONAL_MEMORY_CONSULTATION:
            raise FailClosedRuntimeError("conversation runtime failed closed: memory path unavailable")
        memory_routing = attach_intent_routing(
            routing_record_id=f"{conversation_id}:MEMORY_ROUTING",
            intent_classification_artifact=memory_artifact,
            routing_timestamp=created_at,
            replay_reference=f"{conversation_id}:MEMORY_ROUTING_REPLAY",
            replay_dir=replay_path / "memory_routing",
        )
        consultation = activate_constitutional_memory_consultation(
            consultation_id=f"{conversation_id}:MEMORY_CONSULTATION",
            intent_routing_attachment_record=memory_routing["intent_routing_attachment_record"],
            retrieval_scope=retrieval_scope,
            query="Retrieve constitutional invariant references.",
            artifact_query=artifact_query,
            consultation_timestamp=created_at,
            replay_reference=f"{conversation_id}:MEMORY_CONSULTATION_REPLAY",
            replay_dir=replay_path / "memory_consultation",
        )
        consultation_record = consultation["constitutional_memory_consultation_record"]
        if consultation_record.get("consultation_status") != CONSULTED:
            raise FailClosedRuntimeError("conversation runtime failed closed: memory consultation failed")

        memory_response = create_memory_based_response(
            response_id=f"{conversation_id}:MEMORY_RESPONSE",
            prompt_id=prompt_id,
            constitutional_memory_consultation_record=consultation_record,
            created_at=created_at,
            replay_dir=replay_path / "memory_based_response",
        )
        memory_response_artifact = memory_response["memory_based_response"]
        if memory_response_artifact.get("response_status") != MEMORY_RESPONSE_CREATED:
            raise FailClosedRuntimeError("conversation runtime failed closed: memory based response failed")

        response = _conversation_response_artifact(
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            intent_id=intent_artifact["artifact_id"],
            response_id=memory_response_artifact["response_id"],
            response_text=memory_response_artifact["response_text"],
            created_at=created_at,
            response_status=CREATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response)
        returned = _conversation_returned(
            started=started,
            response=response,
            intent_artifact=intent_artifact,
            consultation_record=consultation_record,
            memory_response=memory_response_artifact,
            response_status=RETURNED,
            failure_reason=None,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(started, response, returned)
    except Exception as exc:
        if started is None:
            started = _failed_started(
                conversation_id=conversation_id,
                prompt_id=prompt_id,
                human_prompt=human_prompt,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
            _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], started)
        response = _failed_response_artifact(
            conversation_id=conversation_id,
            prompt_id=prompt_id,
            intent_id="UNAVAILABLE_INTENT",
            response_id="UNAVAILABLE_RESPONSE",
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], response)
        returned = _conversation_returned(
            started=started,
            response=response,
            intent_artifact=None,
            consultation_record=None,
            memory_response=None,
            response_status=FAILED_CLOSED,
            failure_reason=response["failure_reason"],
        )
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(started, response, returned)


def reconstruct_conversation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Conversation Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversation artifact")
        wrappers.append(wrapper)

    started = wrappers[0]["artifact"]
    response = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if response.get("conversation_id") != started["conversation_id"]:
        raise FailClosedRuntimeError("conversation replay response reference mismatch")
    if returned.get("conversation_id") != started["conversation_id"]:
        raise FailClosedRuntimeError("conversation replay returned reference mismatch")
    if returned.get("response_artifact_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("conversation replay response hash mismatch")
    _validate_conversation_response(response)
    return {
        "conversation_id": started["conversation_id"],
        "prompt_id": started["prompt_id"],
        "prompt": started["prompt_text"],
        "intent_id": response["intent_id"],
        "response_id": response["response_id"],
        "response_text": response["response_text"],
        "response_type": response["response_type"],
        "conversation_status": response["conversation_status"],
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "citation_bundle_id": returned["citation_bundle_id"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _ensure_conversation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _conversation_started(*, conversation_id: str, prompt_id: str, human_prompt: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "event_type": STARTED,
        "conversation_id": _require_string(conversation_id, "conversation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "prompt_text": _normalize_text(human_prompt, "human_prompt"),
        "prompt_hash": replay_hash({"human_prompt": _normalize_text(human_prompt, "human_prompt")}),
        "conversation_runtime_version": CONVERSATION_RUNTIME_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_started(
    *, conversation_id: Any, prompt_id: Any, human_prompt: Any, created_at: Any, failure_reason: str
) -> dict[str, Any]:
    prompt_text = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "event_type": STARTED,
        "conversation_id": conversation_id if isinstance(conversation_id, str) and conversation_id.strip() else "INVALID_CONVERSATION_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "prompt_text": prompt_text,
        "prompt_hash": replay_hash({"human_prompt": prompt_text}),
        "conversation_runtime_version": CONVERSATION_RUNTIME_VERSION,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "authority": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_response_artifact(
    *,
    conversation_id: str,
    prompt_id: str,
    intent_id: str,
    response_id: str,
    response_text: str,
    created_at: str,
    response_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "conversation_id": _require_string(conversation_id, "conversation_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "intent_id": _require_string(intent_id, "intent_id"),
        "response_id": _require_string(response_id, "response_id"),
        "artifact_type": CONVERSATION_RESPONSE_ARTIFACT_V1,
        "response_type": CONVERSATION_RESPONSE,
        "response_text": _require_string(response_text, "response_text"),
        "authority": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "conversation_status": response_status,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_conversation_response(artifact)
    return artifact


def _failed_response_artifact(
    *,
    conversation_id: Any,
    prompt_id: Any,
    intent_id: Any,
    response_id: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "conversation_id": conversation_id if isinstance(conversation_id, str) and conversation_id.strip() else "INVALID_CONVERSATION_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "intent_id": intent_id if isinstance(intent_id, str) and intent_id.strip() else "UNAVAILABLE_INTENT",
        "response_id": response_id if isinstance(response_id, str) and response_id.strip() else "UNAVAILABLE_RESPONSE",
        "artifact_type": CONVERSATION_RESPONSE_ARTIFACT_V1,
        "response_type": CONVERSATION_RESPONSE,
        "response_text": "",
        "authority": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "conversation_status": FAILED_CLOSED,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _conversation_returned(
    *,
    started: dict[str, Any],
    response: dict[str, Any],
    intent_artifact: dict[str, Any] | None,
    consultation_record: dict[str, Any] | None,
    memory_response: dict[str, Any] | None,
    response_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(started, "conversation started artifact")
    _verify_artifact_hash(response, "conversation response artifact")
    artifact = {
        "event_type": RETURNED if response_status != FAILED_CLOSED else FAILED_CLOSED,
        "conversation_id": started["conversation_id"],
        "prompt_id": started["prompt_id"],
        "intent_id": response["intent_id"],
        "response_id": response["response_id"],
        "response_artifact_hash": response["artifact_hash"],
        "intent_artifact_hash": intent_artifact.get("artifact_hash") if isinstance(intent_artifact, dict) else None,
        "consultation_record_reference": (
            consultation_record.get("consultation_id") if isinstance(consultation_record, dict) else None
        ),
        "consultation_record_hash": consultation_record.get("artifact_hash") if isinstance(consultation_record, dict) else None,
        "citation_bundle_id": (
            consultation_record.get("citation_bundle", {}).get("retrieval_id") if isinstance(consultation_record, dict) else None
        ),
        "memory_response_hash": memory_response.get("artifact_hash") if isinstance(memory_response, dict) else None,
        "conversation_status": response_status,
        "replay_visible": True,
        "authority": False,
        "reconstruction_metadata": {
            "prompt_reconstructable": True,
            "intent_reconstructable": intent_artifact is not None,
            "citation_bundle_reconstructable": consultation_record is not None,
            "response_reconstructable": True,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "authority_introduced": False,
        },
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(started: dict[str, Any], response: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "conversation_started": deepcopy(started),
        "conversation_response_artifact": deepcopy(response),
        "conversation_response_replay": deepcopy(returned),
    }
    capture["conversation_runtime_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "conversation artifact")
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


def _validate_conversation_response(response: dict[str, Any]) -> None:
    if response.get("artifact_type") != CONVERSATION_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversation runtime failed closed: invalid response artifact")
    if response.get("response_type") != CONVERSATION_RESPONSE:
        raise FailClosedRuntimeError("conversation runtime failed closed: invalid response type")
    if response.get("authority") is not False:
        raise FailClosedRuntimeError("conversation runtime failed closed: authority introduced")
    if response.get("replay_visible") is not True:
        raise FailClosedRuntimeError("conversation runtime failed closed: replay visibility missing")
    if FORBIDDEN_RESPONSE_FIELDS.intersection(response):
        raise FailClosedRuntimeError("conversation runtime failed closed: authority-bearing response")
    status = response.get("conversation_status")
    if status == CREATED and not response.get("response_text"):
        raise FailClosedRuntimeError("conversation runtime failed closed: response text missing")
    if status == FAILED_CLOSED and response.get("response_text"):
        raise FailClosedRuntimeError("conversation runtime failed closed: failed response cannot carry text")
    if status not in {CREATED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("conversation runtime failed closed: invalid response status")


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
        raise FailClosedRuntimeError("conversation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "conversation runtime failed closed"


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
