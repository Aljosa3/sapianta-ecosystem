"""Minimal Human Prompt Interface for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_classifier import classify_intent, reconstruct_intent_classification_replay
from aigol.runtime.intent_routing_attachment import attach_intent_routing, reconstruct_intent_routing_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


HUMAN_PROMPT_INTERFACE_VERSION = "MINIMAL_HUMAN_PROMPT_INTERFACE_V1"
PROMPT_ACCEPTED = "HUMAN_PROMPT_ACCEPTED"
PROMPT_FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("human_prompt_artifact", "human_prompt_lineage")
DEFAULT_CREATED_AT = "2026-06-01T00:00:00Z"
DEFAULT_PROMPT_ID = "AIGOL-HUMAN-PROMPT-000001"


def submit_human_prompt(
    *,
    human_prompt: str,
    prompt_id: str = DEFAULT_PROMPT_ID,
    created_at: str = DEFAULT_CREATED_AT,
    replay_dir: str | Path = ".aigol_prompt_runtime",
    operator_context: str = "operator_cli",
) -> dict[str, Any]:
    """Accept a human prompt and attach replay-visible intent and routing evidence."""

    replay_path = Path(replay_dir)
    try:
        prompt = _normalize_prompt(human_prompt)
        prompt_id = _resolve_prompt_id(
            prompt_id=prompt_id,
            human_prompt=prompt,
            replay_path=replay_path,
        )
        created_at = _require_string(created_at, "created_at")
        prompt_replay_path = replay_path / prompt_id
        _ensure_prompt_replay_available(prompt_replay_path)
        prompt_artifact = _prompt_artifact(
            prompt_id=prompt_id,
            human_prompt=prompt,
            created_at=created_at,
            operator_context=operator_context,
            replay_reference=str(prompt_replay_path),
            status=PROMPT_ACCEPTED,
            failure_reason=None,
        )
        _persist_step(prompt_replay_path, 0, REPLAY_STEPS[0], prompt_artifact)

        intent_capture = classify_intent(
            artifact_id=f"{prompt_id}:INTENT",
            human_request_reference=prompt_id,
            human_prompt=prompt,
            classification_timestamp=created_at,
            replay_reference=str(prompt_replay_path / "intent_classification"),
            replay_dir=prompt_replay_path / "intent_classification",
            normalized_request_reference=prompt_artifact["artifact_hash"],
        )
        intent_artifact = intent_capture["intent_classification_artifact"]

        routing_capture = attach_intent_routing(
            routing_record_id=f"{prompt_id}:ROUTING",
            intent_classification_artifact=intent_artifact,
            routing_timestamp=created_at,
            replay_reference=str(prompt_replay_path / "intent_routing"),
            replay_dir=prompt_replay_path / "intent_routing",
        )
        routing_record = routing_capture["intent_routing_attachment_record"]

        lineage = _prompt_lineage_artifact(
            prompt_artifact=prompt_artifact,
            intent_artifact=intent_artifact,
            routing_record=routing_record,
            created_at=created_at,
        )
        _persist_step(prompt_replay_path, 1, REPLAY_STEPS[1], lineage)
        return _capture(prompt_artifact, intent_artifact, routing_record, lineage)
    except Exception as exc:
        prompt_id = prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID"
        prompt_replay_path = Path(replay_dir) / prompt_id
        prompt_artifact = _failed_prompt_artifact(
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            created_at=created_at,
            operator_context=operator_context,
            replay_reference=str(prompt_replay_path),
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(prompt_replay_path, 0, REPLAY_STEPS[0], prompt_artifact)
        lineage = _failed_lineage_artifact(
            prompt_artifact=prompt_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(prompt_replay_path, 1, REPLAY_STEPS[1], lineage)
        return _capture(prompt_artifact, None, None, lineage)


def reconstruct_human_prompt_replay(replay_dir: str | Path, *, prompt_id: str) -> dict[str, Any]:
    """Reconstruct prompt, intent classification, and routing replay."""

    prompt_replay_path = Path(replay_dir) / _require_string(prompt_id, "prompt_id")
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(prompt_replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("human prompt replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("human prompt replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    prompt_artifact = wrappers[0]["artifact"]
    lineage = wrappers[1]["artifact"]
    if lineage.get("prompt_id") != prompt_artifact["prompt_id"]:
        raise FailClosedRuntimeError("human prompt lineage prompt mismatch")
    if lineage.get("prompt_artifact_hash") != prompt_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("human prompt lineage hash mismatch")

    intent_replay = reconstruct_intent_classification_replay(prompt_replay_path / "intent_classification")
    routing_replay = reconstruct_intent_routing_replay(prompt_replay_path / "intent_routing")
    return {
        "prompt_id": prompt_artifact["prompt_id"],
        "prompt_text": prompt_artifact["prompt_text"],
        "prompt_hash": prompt_artifact["prompt_hash"],
        "created_at": prompt_artifact["created_at"],
        "prompt_status": prompt_artifact["prompt_status"],
        "intent_classification": deepcopy(intent_replay),
        "routing_decision": deepcopy(routing_replay),
        "cognition_path_entered": lineage["cognition_path_entered"],
        "destination_invoked": lineage["destination_invoked"],
        "replay_visible": True,
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_artifact_count": len(wrappers) + intent_replay["replay_artifact_count"] + routing_replay["replay_artifact_count"],
        "replay_hash": replay_hash(
            {
                "human_prompt": wrappers,
                "intent": intent_replay,
                "routing": routing_replay,
            }
        ),
    }


def _prompt_artifact(
    *,
    prompt_id: str,
    human_prompt: str,
    created_at: str,
    operator_context: str,
    replay_reference: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    prompt = _normalize_prompt(human_prompt)
    artifact = {
        "artifact_type": "HUMAN_PROMPT_ARTIFACT",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": prompt}),
        "created_at": _require_string(created_at, "created_at"),
        "operator_context": _require_string(operator_context, "operator_context"),
        "prompt_interface_version": HUMAN_PROMPT_INTERFACE_VERSION,
        "prompt_status": status,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "authority": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_prompt_artifact(
    *,
    prompt_id: str,
    human_prompt: Any,
    created_at: Any,
    operator_context: Any,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    artifact = {
        "artifact_type": "HUMAN_PROMPT_ARTIFACT",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "prompt_text": prompt,
        "prompt_hash": replay_hash({"human_prompt": " ".join(str(prompt).split())}),
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "operator_context": operator_context if isinstance(operator_context, str) and operator_context.strip() else "INVALID_OPERATOR_CONTEXT",
        "prompt_interface_version": HUMAN_PROMPT_INTERFACE_VERSION,
        "prompt_status": PROMPT_FAILED_CLOSED,
        "replay_reference": replay_reference,
        "authority": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _prompt_lineage_artifact(
    *,
    prompt_artifact: dict[str, Any],
    intent_artifact: dict[str, Any],
    routing_record: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_PROMPT_LINEAGE",
        "prompt_id": prompt_artifact["prompt_id"],
        "prompt_artifact_hash": prompt_artifact["artifact_hash"],
        "intent_artifact_id": intent_artifact["artifact_id"],
        "intent_artifact_hash": intent_artifact["artifact_hash"],
        "intent_status": intent_artifact["classification_status"],
        "classification_destination": intent_artifact["classification_destination"],
        "routing_record_id": routing_record["routing_record_id"],
        "routing_record_hash": routing_record["artifact_hash"],
        "routing_status": routing_record["routing_status"],
        "routing_destination": routing_record["destination"],
        "cognition_path_entered": True,
        "destination_invoked": False,
        "created_at": _require_string(created_at, "created_at"),
        "authority": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_lineage_artifact(*, prompt_artifact: dict[str, Any], created_at: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": "HUMAN_PROMPT_LINEAGE",
        "prompt_id": prompt_artifact["prompt_id"],
        "prompt_artifact_hash": prompt_artifact["artifact_hash"],
        "intent_artifact_id": None,
        "intent_artifact_hash": None,
        "intent_status": PROMPT_FAILED_CLOSED,
        "classification_destination": None,
        "routing_record_id": None,
        "routing_record_hash": None,
        "routing_status": PROMPT_FAILED_CLOSED,
        "routing_destination": None,
        "cognition_path_entered": False,
        "destination_invoked": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "authority": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    prompt_artifact: dict[str, Any],
    intent_artifact: dict[str, Any] | None,
    routing_record: dict[str, Any] | None,
    lineage: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "command": "aigol prompt submit",
        "human_prompt_artifact": deepcopy(prompt_artifact),
        "intent_classification_artifact": deepcopy(intent_artifact),
        "intent_routing_attachment_record": deepcopy(routing_record),
        "human_prompt_lineage": deepcopy(lineage),
        "prompt_id": prompt_artifact["prompt_id"],
        "prompt_status": prompt_artifact["prompt_status"],
        "classification_destination": lineage["classification_destination"],
        "routing_destination": lineage["routing_destination"],
        "cognition_path_entered": lineage["cognition_path_entered"],
        "replay_reference": prompt_artifact["replay_reference"],
        "authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "fail_closed": prompt_artifact["prompt_status"] == PROMPT_FAILED_CLOSED,
        "failure_reason": prompt_artifact["failure_reason"],
    }
    capture["human_prompt_interface_capture_hash"] = replay_hash(capture)
    return capture


def _resolve_prompt_id(*, prompt_id: str, human_prompt: str, replay_path: Path) -> str:
    if prompt_id != DEFAULT_PROMPT_ID:
        return _require_string(prompt_id, "prompt_id")
    generated = generate_prompt_id(human_prompt=human_prompt)
    candidate = generated
    suffix = 1
    while (replay_path / candidate).exists():
        suffix += 1
        candidate = f"{generated}-{suffix:04d}"
    return candidate


def generate_prompt_id(*, human_prompt: str) -> str:
    prompt = _normalize_prompt(human_prompt)
    return f"AIGOL-HUMAN-PROMPT-{replay_hash({'human_prompt': prompt, 'version': HUMAN_PROMPT_INTERFACE_VERSION}).split(':', 1)[1][:12].upper()}"


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("human prompt replay step ordering mismatch")
    _verify_artifact_hash(artifact)
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


def _ensure_prompt_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("human prompt artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("human prompt artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("human prompt artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("human prompt replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("human prompt replay hash mismatch")


def _normalize_prompt(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("human prompt is required")
    return " ".join(value.split())


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "human prompt interface failed closed"
