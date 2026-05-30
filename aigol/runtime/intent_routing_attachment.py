"""Minimal non-authoritative intent routing attachment for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_classifier import CLASSIFIED, VALID_DESTINATIONS
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ROUTING_VERSION = "INTENT_ROUTING_ATTACHMENT_V1"
ROUTED = "ROUTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("intent_routing_attachment_record", "intent_routing_attachment_replay")

FORBIDDEN_ARTIFACT_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "proposal_artifact",
        "correction_instruction",
    }
)


def attach_intent_routing(
    *,
    routing_record_id: str,
    intent_classification_artifact: dict[str, Any],
    routing_timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Attach routing evidence to an intent classification artifact."""

    replay_path = Path(replay_dir)
    try:
        artifact = _validate_intent_classification_artifact(intent_classification_artifact)
        record = _routing_record(
            routing_record_id=routing_record_id,
            artifact_reference=artifact["artifact_id"],
            classification_artifact_hash=artifact["artifact_hash"],
            destination=artifact["classification_destination"],
            routing_status=ROUTED,
            routing_timestamp=routing_timestamp,
            replay_reference=replay_reference,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], record)
        replay = _routing_replay(record)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], replay)
        return _capture(record, replay)
    except Exception as exc:
        record = _failed_routing_record(
            routing_record_id=routing_record_id,
            intent_classification_artifact=intent_classification_artifact,
            routing_timestamp=routing_timestamp,
            replay_reference=replay_reference,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, record)
        replay = _routing_replay(record)
        _persist_failure_replay_if_possible(replay_path, replay)
        return _capture(record, replay)


def reconstruct_intent_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate intent routing attachment replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("intent routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("intent routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    record = wrappers[0]["artifact"]
    replay = wrappers[1]["artifact"]
    if replay.get("routing_record_reference") != record["routing_record_id"]:
        raise FailClosedRuntimeError("intent routing replay record reference mismatch")
    if replay.get("routing_record_hash") != record["artifact_hash"]:
        raise FailClosedRuntimeError("intent routing replay record hash mismatch")
    _validate_routing_record(record)
    return {
        "routing_record_id": record["routing_record_id"],
        "artifact_reference": record["artifact_reference"],
        "destination": record["destination"],
        "routing_status": record["routing_status"],
        "routing_version": record["routing_version"],
        "replay_visible": True,
        "destination_invoked": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_intent_classification_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("intent routing failed closed: missing artifact")
    if artifact.get("artifact_type") != "INTENT_CLASSIFICATION_ARTIFACT":
        raise FailClosedRuntimeError("intent routing failed closed: invalid artifact")
    if FORBIDDEN_ARTIFACT_FIELDS.intersection(artifact):
        raise FailClosedRuntimeError("intent routing failed closed: authority-bearing artifact")
    _verify_artifact_hash(artifact)
    if artifact.get("classification_status") != CLASSIFIED:
        raise FailClosedRuntimeError("intent routing failed closed: ambiguous artifact")
    destination = artifact.get("classification_destination")
    if isinstance(destination, list):
        raise FailClosedRuntimeError("intent routing failed closed: multiple destinations")
    if not destination:
        raise FailClosedRuntimeError("intent routing failed closed: missing destination")
    if destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("intent routing failed closed: invalid destination")
    return deepcopy(artifact)


def _routing_record(
    *,
    routing_record_id: str,
    artifact_reference: str,
    classification_artifact_hash: str,
    destination: str | None,
    routing_status: str,
    routing_timestamp: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    record = {
        "routing_record_id": _require_string(routing_record_id, "routing_record_id"),
        "record_type": "INTENT_ROUTING_ATTACHMENT_RECORD",
        "artifact_reference": _require_string(artifact_reference, "artifact_reference"),
        "classification_artifact_hash": _require_string(classification_artifact_hash, "classification_artifact_hash"),
        "destination": destination,
        "routing_status": routing_status,
        "routing_version": ROUTING_VERSION,
        "routing_timestamp": _require_string(routing_timestamp, "routing_timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "reconstruction_metadata": {
            "source_artifact_reference": artifact_reference,
            "destination_evidence": destination,
            "destination_invoked": False,
        },
        "failure_reason": failure_reason,
    }
    record["artifact_hash"] = replay_hash(record)
    _validate_routing_record(record)
    return record


def _failed_routing_record(
    *,
    routing_record_id: Any,
    intent_classification_artifact: Any,
    routing_timestamp: Any,
    replay_reference: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact_reference = "INVALID_ARTIFACT_REFERENCE"
    artifact_hash = "INVALID_ARTIFACT_HASH"
    if isinstance(intent_classification_artifact, dict):
        artifact_reference = str(intent_classification_artifact.get("artifact_id") or artifact_reference)
        artifact_hash = str(intent_classification_artifact.get("artifact_hash") or artifact_hash)
    record = {
        "routing_record_id": (
            routing_record_id if isinstance(routing_record_id, str) and routing_record_id.strip() else "INVALID_ROUTING_RECORD_ID"
        ),
        "record_type": "INTENT_ROUTING_ATTACHMENT_RECORD",
        "artifact_reference": artifact_reference,
        "classification_artifact_hash": artifact_hash,
        "destination": None,
        "routing_status": FAILED_CLOSED,
        "routing_version": ROUTING_VERSION,
        "routing_timestamp": routing_timestamp if isinstance(routing_timestamp, str) and routing_timestamp.strip() else "INVALID_TIMESTAMP",
        "replay_reference": replay_reference if isinstance(replay_reference, str) and replay_reference.strip() else "INVALID_REPLAY_REFERENCE",
        "reconstruction_metadata": {
            "source_artifact_reference": artifact_reference,
            "destination_evidence": None,
            "destination_invoked": False,
        },
        "failure_reason": failure_reason,
    }
    record["artifact_hash"] = replay_hash(record)
    return record


def _routing_replay(record: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(record)
    replay = {
        "replay_id": f"{record['routing_record_id']}:REPLAY",
        "routing_record_reference": record["routing_record_id"],
        "artifact_reference": record["artifact_reference"],
        "destination": record["destination"],
        "routing_status": record["routing_status"],
        "routing_version": record["routing_version"],
        "routing_record_hash": record["artifact_hash"],
        "replay_reference": record["replay_reference"],
        "replay_visibility": "MANDATORY",
        "destination_invoked": False,
    }
    replay["artifact_hash"] = replay_hash(replay)
    return replay


def _capture(record: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "intent_routing_attachment_record": deepcopy(record),
        "intent_routing_attachment_replay": deepcopy(replay),
    }
    capture["intent_routing_attachment_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("intent routing replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, record: dict[str, Any]) -> None:
    path = replay_dir / f"000_{REPLAY_STEPS[0]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 0, REPLAY_STEPS[0], record)
        except FailClosedRuntimeError:
            return


def _persist_failure_replay_if_possible(replay_dir: Path, replay: dict[str, Any]) -> None:
    path = replay_dir / f"001_{REPLAY_STEPS[1]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 1, REPLAY_STEPS[1], replay)
        except FailClosedRuntimeError:
            return


def _validate_routing_record(record: dict[str, Any]) -> None:
    status = record.get("routing_status")
    destination = record.get("destination")
    if status == ROUTED and destination not in VALID_DESTINATIONS:
        raise FailClosedRuntimeError("intent routing failed closed: invalid destination")
    if status == FAILED_CLOSED and destination is not None:
        raise FailClosedRuntimeError("intent routing failed closed: failed record cannot carry destination")
    if status not in {ROUTED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("intent routing failed closed: invalid status")
    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "conversation_response",
    }
    if forbidden.intersection(record):
        raise FailClosedRuntimeError("intent routing failed closed: authority-bearing record")
    metadata = record.get("reconstruction_metadata")
    if not isinstance(metadata, dict) or metadata.get("destination_invoked") is not False:
        raise FailClosedRuntimeError("intent routing failed closed: destination invocation is forbidden")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("intent routing artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("intent routing artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("intent routing artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("intent routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("intent routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "intent routing failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value

