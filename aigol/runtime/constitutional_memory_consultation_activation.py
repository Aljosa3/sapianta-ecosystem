"""Constitutional Memory consultation activation for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_memory_access import retrieve_constitutional_memory
from aigol.runtime.intent_classifier import CONSTITUTIONAL_MEMORY_CONSULTATION
from aigol.runtime.intent_routing_attachment import ROUTED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONSULTATION_VERSION = "CONSTITUTIONAL_MEMORY_CONSULTATION_ACTIVATION_V1"
CONSULTED = "CONSULTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("constitutional_memory_consultation_record", "constitutional_memory_consultation_replay")

FORBIDDEN_ROUTING_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "memory_retrieval_result",
        "conversation_response",
    }
)

FORBIDDEN_RECORD_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
        "conversation_response",
    }
)


def activate_constitutional_memory_consultation(
    *,
    consultation_id: str,
    intent_routing_attachment_record: dict[str, Any],
    retrieval_scope: str,
    query: str,
    consultation_timestamp: str,
    replay_reference: str,
    replay_dir: str | Path,
    artifact_query: str | None = None,
    repository_root: str | Path | None = None,
    artifact_catalog: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Activate reference-only Constitutional Memory consultation."""

    replay_path = Path(replay_dir)
    try:
        _ensure_activation_replay_available(replay_path)
        routing_record = _validate_routing_record(intent_routing_attachment_record)
        memory_replay_dir = replay_path / "constitutional_memory_access"
        memory_capture = retrieve_constitutional_memory(
            retrieval_id=f"{consultation_id}:MEMORY_RETRIEVAL",
            requested_by="AIGOL_GOVERNANCE",
            retrieval_scope=retrieval_scope,
            query=query,
            created_at=consultation_timestamp,
            replay_dir=memory_replay_dir,
            artifact_query=artifact_query,
            governance_context=True,
            repository_root=repository_root,
            artifact_catalog=artifact_catalog,
        )
        citation_bundle = memory_capture.get("citation_bundle")
        retrieval_result = memory_capture.get("retrieval_result")
        if not isinstance(citation_bundle, dict):
            raise FailClosedRuntimeError("constitutional memory consultation failed closed: citation bundle missing")
        if not isinstance(retrieval_result, dict) or retrieval_result.get("retrieval_status") != "SUCCESS":
            raise FailClosedRuntimeError("constitutional memory consultation failed closed: retrieval failed")
        _verify_artifact_hash(citation_bundle, "constitutional memory citation bundle")
        consultation_citation_bundle = _consultation_citation_bundle(citation_bundle)
        record = _consultation_record(
            consultation_id=consultation_id,
            routing_record_reference=routing_record["routing_record_id"],
            routing_record_hash=routing_record["artifact_hash"],
            retrieval_scope=retrieval_scope,
            citation_bundle=consultation_citation_bundle,
            consultation_timestamp=consultation_timestamp,
            replay_reference=replay_reference,
            memory_retrieval_id=retrieval_result["retrieval_id"],
            consultation_status=CONSULTED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], record)
        replay = _consultation_replay(record)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], replay)
        return _capture(record, replay, memory_capture)
    except Exception as exc:
        record = _failed_consultation_record(
            consultation_id=consultation_id,
            intent_routing_attachment_record=intent_routing_attachment_record,
            retrieval_scope=retrieval_scope,
            consultation_timestamp=consultation_timestamp,
            replay_reference=replay_reference,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, record)
        replay = _consultation_replay(record)
        _persist_failure_replay_if_possible(replay_path, replay)
        return _capture(record, replay, None)


def _ensure_activation_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def reconstruct_constitutional_memory_consultation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct consultation replay without performing retrieval again."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("constitutional memory consultation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("constitutional memory consultation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "constitutional memory consultation artifact")
        wrappers.append(wrapper)

    record = wrappers[0]["artifact"]
    replay = wrappers[1]["artifact"]
    if replay.get("consultation_record_reference") != record["consultation_id"]:
        raise FailClosedRuntimeError("constitutional memory consultation replay record reference mismatch")
    if replay.get("consultation_record_hash") != record["artifact_hash"]:
        raise FailClosedRuntimeError("constitutional memory consultation replay record hash mismatch")
    _validate_consultation_record(record)
    return {
        "consultation_id": record["consultation_id"],
        "routing_record_reference": record["routing_record_reference"],
        "retrieval_scope": record["retrieval_scope"],
        "consultation_status": record["consultation_status"],
        "citation_count": record["citation_bundle"].get("citation_count", 0) if isinstance(record.get("citation_bundle"), dict) else 0,
        "consultation_version": record["consultation_version"],
        "reference_only": True,
        "replay_visible": True,
        "retrieval_performed_during_reconstruction": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_routing_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: missing routing record")
    if record.get("record_type") != "INTENT_ROUTING_ATTACHMENT_RECORD":
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: invalid routing record")
    if FORBIDDEN_ROUTING_FIELDS.intersection(record):
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: authority-bearing routing record")
    _verify_artifact_hash(record, "intent routing record")
    if record.get("routing_status") != ROUTED:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: invalid routing record")
    if record.get("destination") != CONSTITUTIONAL_MEMORY_CONSULTATION:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: non-memory destination")
    metadata = record.get("reconstruction_metadata")
    if not isinstance(metadata, dict) or metadata.get("destination_invoked") is not False:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: corrupt routing record")
    return deepcopy(record)


def _consultation_citation_bundle(citation_bundle: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(citation_bundle, "constitutional memory citation bundle")
    citations = citation_bundle.get("citations")
    returned_artifacts = citation_bundle.get("returned_artifacts")
    if not isinstance(citations, list) or not citations:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: citation bundle missing")
    if not isinstance(returned_artifacts, list) or not returned_artifacts:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: returned artifacts missing")
    for citation in citations:
        if not isinstance(citation, dict):
            raise FailClosedRuntimeError("constitutional memory consultation failed closed: corrupt citation bundle")
        _require_string(citation.get("artifact_identity"), "artifact_identity")
        _require_string(citation.get("artifact_classification"), "artifact_classification")
        _require_string(citation.get("artifact_path"), "artifact_path")
        _require_string(citation.get("citation_reference"), "citation_reference")
        if citation.get("authority_status") != "REFERENCE_ONLY":
            raise FailClosedRuntimeError("constitutional memory consultation failed closed: citation is not reference-only")
    bundle = {
        "bundle_type": "CONSTITUTIONAL_MEMORY_CONSULTATION_CITATION_BUNDLE",
        "retrieval_id": _require_string(citation_bundle.get("retrieval_id"), "retrieval_id"),
        "citation_count": citation_bundle.get("citation_count"),
        "citations": deepcopy(citations),
        "returned_artifacts": deepcopy(returned_artifacts),
        "retrieval_status": _require_string(citation_bundle.get("retrieval_status"), "retrieval_status"),
        "reference_only": True,
        "citation_required": True,
        "replay_visible": True,
    }
    bundle["artifact_hash"] = replay_hash(bundle)
    return bundle


def _consultation_record(
    *,
    consultation_id: str,
    routing_record_reference: str,
    routing_record_hash: str,
    retrieval_scope: str,
    citation_bundle: dict[str, Any],
    consultation_timestamp: str,
    replay_reference: str,
    memory_retrieval_id: str,
    consultation_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(citation_bundle, "constitutional memory citation bundle")
    record = {
        "consultation_id": _require_string(consultation_id, "consultation_id"),
        "record_type": "CONSTITUTIONAL_MEMORY_CONSULTATION_RECORD",
        "routing_record_reference": _require_string(routing_record_reference, "routing_record_reference"),
        "routing_record_hash": _require_string(routing_record_hash, "routing_record_hash"),
        "retrieval_scope": _require_string(retrieval_scope, "retrieval_scope"),
        "citation_bundle": deepcopy(citation_bundle),
        "consultation_timestamp": _require_string(consultation_timestamp, "consultation_timestamp"),
        "consultation_version": CONSULTATION_VERSION,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "memory_retrieval_id": _require_string(memory_retrieval_id, "memory_retrieval_id"),
        "consultation_status": consultation_status,
        "reconstruction_metadata": {
            "routing_reference": routing_record_reference,
            "retrieval_scope": retrieval_scope,
            "citation_count": citation_bundle.get("citation_count", 0),
            "retrieval_performed_during_reconstruction": False,
        },
        "failure_reason": failure_reason,
    }
    record["artifact_hash"] = replay_hash(record)
    _validate_consultation_record(record)
    return record


def _failed_consultation_record(
    *,
    consultation_id: Any,
    intent_routing_attachment_record: Any,
    retrieval_scope: Any,
    consultation_timestamp: Any,
    replay_reference: Any,
    failure_reason: str,
) -> dict[str, Any]:
    routing_reference = "INVALID_ROUTING_RECORD_REFERENCE"
    routing_hash = "INVALID_ROUTING_RECORD_HASH"
    if isinstance(intent_routing_attachment_record, dict):
        routing_reference = str(intent_routing_attachment_record.get("routing_record_id") or routing_reference)
        routing_hash = str(intent_routing_attachment_record.get("artifact_hash") or routing_hash)
    record = {
        "consultation_id": (
            consultation_id if isinstance(consultation_id, str) and consultation_id.strip() else "INVALID_CONSULTATION_ID"
        ),
        "record_type": "CONSTITUTIONAL_MEMORY_CONSULTATION_RECORD",
        "routing_record_reference": routing_reference,
        "routing_record_hash": routing_hash,
        "retrieval_scope": retrieval_scope if isinstance(retrieval_scope, str) and retrieval_scope.strip() else "INVALID_RETRIEVAL_SCOPE",
        "citation_bundle": None,
        "consultation_timestamp": (
            consultation_timestamp if isinstance(consultation_timestamp, str) and consultation_timestamp.strip() else "INVALID_TIMESTAMP"
        ),
        "consultation_version": CONSULTATION_VERSION,
        "replay_reference": replay_reference if isinstance(replay_reference, str) and replay_reference.strip() else "INVALID_REPLAY_REFERENCE",
        "memory_retrieval_id": None,
        "consultation_status": FAILED_CLOSED,
        "reconstruction_metadata": {
            "routing_reference": routing_reference,
            "retrieval_scope": retrieval_scope,
            "citation_count": 0,
            "retrieval_performed_during_reconstruction": False,
        },
        "failure_reason": failure_reason,
    }
    record["artifact_hash"] = replay_hash(record)
    return record


def _consultation_replay(record: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(record, "constitutional memory consultation record")
    replay = {
        "replay_id": f"{record['consultation_id']}:REPLAY",
        "consultation_record_reference": record["consultation_id"],
        "routing_reference": record["routing_record_reference"],
        "retrieval_scope": record["retrieval_scope"],
        "citation_bundle": deepcopy(record["citation_bundle"]),
        "consultation_status": record["consultation_status"],
        "consultation_version": record["consultation_version"],
        "consultation_record_hash": record["artifact_hash"],
        "replay_reference": record["replay_reference"],
        "reconstruction_metadata": deepcopy(record["reconstruction_metadata"]),
        "replay_visibility": "MANDATORY",
        "reference_only": True,
    }
    replay["artifact_hash"] = replay_hash(replay)
    return replay


def _capture(
    record: dict[str, Any],
    replay: dict[str, Any],
    memory_capture: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = {
        "constitutional_memory_consultation_record": deepcopy(record),
        "constitutional_memory_consultation_replay": deepcopy(replay),
        "constitutional_memory_access_capture": deepcopy(memory_capture),
    }
    capture["constitutional_memory_consultation_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("constitutional memory consultation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "constitutional memory consultation artifact")
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


def _validate_consultation_record(record: dict[str, Any]) -> None:
    status = record.get("consultation_status")
    if status == CONSULTED and not isinstance(record.get("citation_bundle"), dict):
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: citation bundle missing")
    if status == FAILED_CLOSED and record.get("citation_bundle") is not None:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: failed record cannot carry citation bundle")
    if status not in {CONSULTED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: invalid status")
    if FORBIDDEN_RECORD_FIELDS.intersection(record):
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: authority-bearing consultation record")
    citation_bundle = record.get("citation_bundle")
    if isinstance(citation_bundle, dict) and FORBIDDEN_RECORD_FIELDS.intersection(citation_bundle):
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: authority-bearing citation bundle")
    metadata = record.get("reconstruction_metadata")
    if not isinstance(metadata, dict) or metadata.get("retrieval_performed_during_reconstruction") is not False:
        raise FailClosedRuntimeError("constitutional memory consultation failed closed: invalid reconstruction metadata")


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
        raise FailClosedRuntimeError("constitutional memory consultation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("constitutional memory consultation replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "constitutional memory consultation failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
