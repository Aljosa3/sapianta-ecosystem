"""Deterministic Memory-Based Response runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_memory_consultation_activation import CONSULTED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MEMORY_BASED_RESPONSE_MODEL_V1 = "MEMORY_BASED_RESPONSE_MODEL_V1"
RESPONSE_TYPE = "MEMORY_BASED_RESPONSE"
CREATED = "MEMORY_BASED_RESPONSE_CREATED"
RETURNED = "MEMORY_BASED_RESPONSE_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = ("memory_based_response_created", "memory_based_response_returned")

FORBIDDEN_CONSULTATION_FIELDS = frozenset(
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
        "conversation_response",
    }
)


def create_memory_based_response(
    *,
    response_id: str,
    prompt_id: str,
    constitutional_memory_consultation_record: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a governed explanation from citation bundle evidence only."""

    replay_path = Path(replay_dir)
    try:
        _ensure_response_replay_available(replay_path)
        consultation_record = _validate_consultation_record(constitutional_memory_consultation_record)
        citation_bundle = _validate_citation_bundle(consultation_record["citation_bundle"])
        response = _response_artifact(
            response_id=response_id,
            prompt_id=prompt_id,
            citation_bundle=citation_bundle,
            created_at=created_at,
            response_status=CREATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], response)
        returned = _returned_replay_artifact(
            response=response,
            prompt_id=prompt_id,
            consultation_record=consultation_record,
            citation_bundle=citation_bundle,
            response_status=RETURNED,
            failure_reason=None,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(response, returned)
    except Exception as exc:
        response = _failed_response_artifact(
            response_id=response_id,
            prompt_id=prompt_id,
            constitutional_memory_consultation_record=constitutional_memory_consultation_record,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, response)
        returned = _returned_replay_artifact(
            response=response,
            prompt_id=prompt_id,
            consultation_record=None,
            citation_bundle=None,
            response_status=FAILED_CLOSED,
            failure_reason=response["failure_reason"],
        )
        _persist_failure_returned_if_possible(replay_path, returned)
        return _capture(response, returned)


def reconstruct_memory_based_response_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Memory-Based Response replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("memory based response replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("memory based response replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "memory based response artifact")
        wrappers.append(wrapper)

    response = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("response_reference") != response["response_id"]:
        raise FailClosedRuntimeError("memory based response replay response reference mismatch")
    if returned.get("response_hash") != response["artifact_hash"]:
        raise FailClosedRuntimeError("memory based response replay response hash mismatch")
    _validate_response_artifact(response)
    return {
        "response_id": response["response_id"],
        "prompt_id": response["prompt_id"],
        "citation_bundle_id": response["citation_bundle_id"],
        "response_text": response["response_text"],
        "citations": deepcopy(response["citations"]),
        "response_status": response["response_status"],
        "response_type": response["response_type"],
        "citation_count": len(response["citations"]),
        "replay_visible": True,
        "authority": False,
        "execution_capable": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _ensure_response_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _validate_consultation_record(record: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise FailClosedRuntimeError("memory based response failed closed: consultation record missing")
    if record.get("record_type") != "CONSTITUTIONAL_MEMORY_CONSULTATION_RECORD":
        raise FailClosedRuntimeError("memory based response failed closed: invalid consultation record")
    if FORBIDDEN_CONSULTATION_FIELDS.intersection(record):
        raise FailClosedRuntimeError("memory based response failed closed: authority-bearing consultation record")
    _verify_artifact_hash(record, "constitutional memory consultation record")
    if record.get("consultation_status") != CONSULTED:
        raise FailClosedRuntimeError("memory based response failed closed: evidence unavailable")
    return deepcopy(record)


def _validate_citation_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise FailClosedRuntimeError("memory based response failed closed: citation bundle missing")
    _verify_artifact_hash(bundle, "memory based response citation bundle")
    if bundle.get("bundle_type") != "CONSTITUTIONAL_MEMORY_CONSULTATION_CITATION_BUNDLE":
        raise FailClosedRuntimeError("memory based response failed closed: invalid citation bundle")
    if bundle.get("reference_only") is not True or bundle.get("replay_visible") is not True:
        raise FailClosedRuntimeError("memory based response failed closed: invalid citation bundle")
    if FORBIDDEN_CONSULTATION_FIELDS.intersection(bundle):
        raise FailClosedRuntimeError("memory based response failed closed: authority-bearing citation bundle")
    citations = bundle.get("citations")
    if not isinstance(citations, list) or not citations:
        raise FailClosedRuntimeError("memory based response failed closed: citation bundle empty")
    for citation in citations:
        _validate_citation(citation)
    return deepcopy(bundle)


def _validate_citation(citation: Any) -> None:
    if not isinstance(citation, dict):
        raise FailClosedRuntimeError("memory based response failed closed: corrupt citation bundle")
    _require_string(citation.get("artifact_identity"), "artifact_identity")
    _require_string(citation.get("artifact_classification"), "artifact_classification")
    _require_string(citation.get("artifact_path"), "artifact_path")
    _require_string(citation.get("citation_reference"), "citation_reference")
    if citation.get("authority_status") != "REFERENCE_ONLY":
        raise FailClosedRuntimeError("memory based response failed closed: citation is not reference-only")


def _response_artifact(
    *,
    response_id: str,
    prompt_id: str,
    citation_bundle: dict[str, Any],
    created_at: str,
    response_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    citations = [_response_citation(citation) for citation in citation_bundle["citations"]]
    response = {
        "response_id": _require_string(response_id, "response_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "citation_bundle_id": _require_string(citation_bundle.get("retrieval_id"), "citation_bundle_id"),
        "response_text": _response_text(citations),
        "citations": citations,
        "response_type": RESPONSE_TYPE,
        "authority": False,
        "execution_capable": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "response_model": MEMORY_BASED_RESPONSE_MODEL_V1,
        "response_status": response_status,
        "failure_reason": failure_reason,
    }
    response["artifact_hash"] = replay_hash(response)
    _validate_response_artifact(response)
    return response


def _failed_response_artifact(
    *,
    response_id: Any,
    prompt_id: Any,
    constitutional_memory_consultation_record: Any,
    created_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    citation_bundle_id = "INVALID_CITATION_BUNDLE"
    if isinstance(constitutional_memory_consultation_record, dict):
        bundle = constitutional_memory_consultation_record.get("citation_bundle")
        if isinstance(bundle, dict) and isinstance(bundle.get("retrieval_id"), str):
            citation_bundle_id = bundle["retrieval_id"]
    response = {
        "response_id": response_id if isinstance(response_id, str) and response_id.strip() else "INVALID_RESPONSE_ID",
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "citation_bundle_id": citation_bundle_id,
        "response_text": "",
        "citations": [],
        "response_type": RESPONSE_TYPE,
        "authority": False,
        "execution_capable": False,
        "created_at": created_at if isinstance(created_at, str) and created_at.strip() else "INVALID_TIMESTAMP",
        "replay_visible": True,
        "response_model": MEMORY_BASED_RESPONSE_MODEL_V1,
        "response_status": FAILED_CLOSED,
        "failure_reason": failure_reason,
    }
    response["artifact_hash"] = replay_hash(response)
    return response


def _response_citation(citation: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_identity": _require_string(citation.get("artifact_identity"), "artifact_identity"),
        "artifact_classification": _require_string(citation.get("artifact_classification"), "artifact_classification"),
        "artifact_path": _require_string(citation.get("artifact_path"), "artifact_path"),
        "citation_reference": _require_string(citation.get("citation_reference"), "citation_reference"),
        "authority_status": "REFERENCE_ONLY",
    }


def _response_text(citations: list[dict[str, Any]]) -> str:
    references = [
        f"{citation['artifact_identity']} ({citation['artifact_classification']}) at {citation['artifact_path']}"
        for citation in citations
    ]
    joined = "; ".join(references)
    return (
        "Constitutional Memory evidence references "
        f"{len(citations)} cited artifact(s): {joined}. "
        "This is a governed explanation only; it is not authorization, a governance decision, or an execution request."
    )


def _returned_replay_artifact(
    *,
    response: dict[str, Any],
    prompt_id: str,
    consultation_record: dict[str, Any] | None,
    citation_bundle: dict[str, Any] | None,
    response_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(response, "memory based response artifact")
    returned = {
        "replay_event": RETURNED if response_status != FAILED_CLOSED else FAILED_CLOSED,
        "response_reference": response["response_id"],
        "response_hash": response["artifact_hash"],
        "prompt_id": prompt_id if isinstance(prompt_id, str) and prompt_id.strip() else "INVALID_PROMPT_ID",
        "citation_bundle_id": response["citation_bundle_id"],
        "consultation_record_reference": (
            consultation_record.get("consultation_id") if isinstance(consultation_record, dict) else None
        ),
        "consultation_record_hash": (
            consultation_record.get("artifact_hash") if isinstance(consultation_record, dict) else None
        ),
        "citation_bundle_hash": citation_bundle.get("artifact_hash") if isinstance(citation_bundle, dict) else None,
        "response_status": response_status,
        "response_type": RESPONSE_TYPE,
        "reconstruction_metadata": {
            "prompt_reconstructable": True,
            "citation_bundle_reconstructable": citation_bundle is not None,
            "response_reconstructable": True,
            "provider_invoked": False,
            "worker_invoked": False,
            "authority_introduced": False,
        },
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(response: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "memory_based_response": deepcopy(response),
        "memory_based_response_replay": deepcopy(returned),
    }
    capture["memory_based_response_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("memory based response replay step ordering mismatch")
    _verify_artifact_hash(artifact, "memory based response artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": CREATED if index == 0 else RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, response: dict[str, Any]) -> None:
    path = replay_dir / f"000_{REPLAY_STEPS[0]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 0, REPLAY_STEPS[0], response)
        except FailClosedRuntimeError:
            return


def _persist_failure_returned_if_possible(replay_dir: Path, returned: dict[str, Any]) -> None:
    path = replay_dir / f"001_{REPLAY_STEPS[1]}.json"
    if not path.exists():
        try:
            _persist_step(replay_dir, 1, REPLAY_STEPS[1], returned)
        except FailClosedRuntimeError:
            return


def _validate_response_artifact(response: dict[str, Any]) -> None:
    if response.get("response_type") != RESPONSE_TYPE:
        raise FailClosedRuntimeError("memory based response failed closed: invalid response type")
    if response.get("authority") is not False:
        raise FailClosedRuntimeError("memory based response failed closed: authority introduced")
    if response.get("execution_capable") is not False:
        raise FailClosedRuntimeError("memory based response failed closed: execution capability introduced")
    if response.get("replay_visible") is not True:
        raise FailClosedRuntimeError("memory based response failed closed: replay visibility missing")
    if FORBIDDEN_RESPONSE_FIELDS.intersection(response):
        raise FailClosedRuntimeError("memory based response failed closed: authority-bearing response")
    status = response.get("response_status")
    if status == CREATED:
        if not response.get("response_text") or not response.get("citations"):
            raise FailClosedRuntimeError("memory based response failed closed: response evidence missing")
    elif status == FAILED_CLOSED:
        if response.get("response_text") or response.get("citations"):
            raise FailClosedRuntimeError("memory based response failed closed: failed response cannot carry evidence")
    else:
        raise FailClosedRuntimeError("memory based response failed closed: invalid response status")


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
        raise FailClosedRuntimeError("memory based response replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("memory based response replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "memory based response failed closed"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
