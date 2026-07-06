"""Legacy OpenAI proposal-source adapter.

G14.46 classifies this module as compatibility-only replay support for
historical OPENAI_PROVIDER_ADAPTER_V1 evidence. Production provider invocation
must use aigol.provider.certified_provider_attachment with a ProviderAdapter.
"""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.minimal_cognition_to_execution_bridge import READ_ONLY_RUNTIME_INSPECTION
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_attachment import attach_real_provider_response, reconstruct_provider_attachment_replay
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


OPENAI_PROVIDER_IDENTITY = "OPENAI"
NORMALIZED_OPENAI_PROVIDER_IDENTITY = "openai"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_OPENAI_MODEL = "gpt-5.5"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_OPENAI_RESPONSE_CHARS = 4096

REQUEST_METADATA_CAPTURED = "OPENAI_REQUEST_METADATA_CAPTURED"
RAW_RESPONSE_CAPTURED = "OPENAI_RAW_RESPONSE_CAPTURED"
ATTACHMENT_CAPTURED = "OPENAI_ATTACHMENT_CAPTURED"
GOVERNED_RESULT_RETURNED = "OPENAI_GOVERNED_RESULT_RETURNED"
OPENAI_FAILED = "FAILED"
LEGACY_PROVIDER_ATTACHMENT_CLASSIFICATION = "LEGACY_COMPATIBILITY"
PRODUCTION_PROVIDER_ROUTING_ALLOWED = False
CERTIFIED_RUNTIME_REACHABLE = False
LEGACY_COMPATIBILITY_REASON = (
    "Retained only to reconstruct and validate historical OPENAI_PROVIDER_ADAPTER_V1 replay."
)

REPLAY_STEPS = (
    "provider_request_metadata",
    "raw_provider_response",
    "provider_attachment_capture",
    "governed_result",
)

OpenAIClient = Callable[[dict[str, Any]], Any]


def invoke_openai_provider_adapter(
    *,
    adapter_id: str,
    human_request: str,
    created_at: str,
    replay_dir: str | Path,
    openai_client: OpenAIClient | None = None,
    api_key: str | None = None,
    model: str = DEFAULT_OPENAI_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    target_capability: str = READ_ONLY_RUNTIME_INSPECTION,
    authorize: bool = True,
) -> dict[str, Any]:
    """Invoke OpenAI once as an untrusted proposal source."""

    replay_path = Path(replay_dir)
    try:
        metadata = create_openai_request_metadata(
            adapter_id=adapter_id,
            human_request=human_request,
            created_at=created_at,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
        _persist_step(replay_path, 0, "provider_request_metadata", metadata)
        raw = capture_openai_raw_response(metadata, openai_client=openai_client)
        _persist_step(replay_path, 1, "raw_provider_response", raw)
        attachment = attach_real_provider_response(
            provider_attachment_id=f"{metadata['adapter_id']}:REAL-PROVIDER",
            provider_identity=NORMALIZED_OPENAI_PROVIDER_IDENTITY,
            provider_response=raw["raw_provider_response"],
            created_at=metadata["created_at"],
            replay_dir=replay_path / "real_provider_attachment",
            target_capability=target_capability,
            authorize=authorize,
        )
        attachment_record = create_openai_attachment_capture(metadata, raw, attachment)
        _persist_step(replay_path, 2, "provider_attachment_capture", attachment_record)
        governed_result = create_openai_governed_result(metadata, raw, attachment_record)
        _persist_step(replay_path, 3, "governed_result", governed_result)
        return _capture(metadata, raw, attachment_record, governed_result)
    except Exception as exc:
        failure = _failure_artifact(
            adapter_id=adapter_id if isinstance(adapter_id, str) and adapter_id.strip() else "OPENAI-ADAPTER-INVALID",
            created_at=created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00+00:00",
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(None, None, None, failure)


def create_openai_request_metadata(
    *,
    adapter_id: str,
    human_request: str,
    created_at: str,
    api_key: str | None,
    model: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Create replay-visible OpenAI request metadata without storing credentials."""

    normalized_key_source = _validate_api_key_source(api_key)
    request_text = _normalize_string(human_request, "human_request")
    timeout = _normalize_timeout(timeout_seconds)
    model_name = _normalize_string(model, "model")
    artifact = {
        "adapter_id": _normalize_string(adapter_id, "adapter_id"),
        "state": REQUEST_METADATA_CAPTURED,
        "provider_identity": OPENAI_PROVIDER_IDENTITY,
        "normalized_provider_identity": NORMALIZED_OPENAI_PROVIDER_IDENTITY,
        "model": model_name,
        "created_at": _normalize_string(created_at, "created_at"),
        "provider_request_metadata": {
            "request_text": request_text,
            "request_text_hash": replay_hash(request_text),
            "request_text_present": True,
            "api_key_source": normalized_key_source,
            "api_key_captured": False,
            "timeout_seconds": timeout,
            "single_request": True,
            "streaming": False,
            "automatic_retries": False,
            "tool_use": False,
            "function_calling": False,
            "memory": False,
        },
        "untrusted_proposal_source": True,
        "openai_execution_authority": False,
        "openai_authorization_authority": False,
        "openai_governance_authority": False,
        "openai_replay_authority": False,
        "openai_worker_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def capture_openai_raw_response(metadata: dict[str, Any], *, openai_client: OpenAIClient | None) -> dict[str, Any]:
    """Call OpenAI once and capture full raw text before provider attachment."""

    _verify_artifact_hash(metadata)
    if metadata.get("state") != REQUEST_METADATA_CAPTURED:
        raise FailClosedRuntimeError("OpenAI request metadata is required")
    if openai_client is None:
        openai_client = _default_openai_client
    if not callable(openai_client):
        raise FailClosedRuntimeError("openai_client must be callable")
    raw_response = openai_client(_client_request(metadata))
    response_text = _extract_openai_response_text(raw_response)
    artifact = {
        "adapter_id": metadata["adapter_id"],
        "state": RAW_RESPONSE_CAPTURED,
        "provider_identity": OPENAI_PROVIDER_IDENTITY,
        "normalized_provider_identity": metadata["normalized_provider_identity"],
        "model": metadata["model"],
        "created_at": metadata["created_at"],
        "provider_request_metadata_hash": metadata["artifact_hash"],
        "raw_provider_response": response_text,
        "raw_provider_response_hash": replay_hash(response_text),
        "raw_response_shape": _response_shape(raw_response),
        "untrusted_proposal": True,
        "single_response": True,
        "streaming": False,
        "partial_response_execution": False,
        "openai_execution_authority": False,
        "openai_authorization_authority": False,
        "openai_governance_authority": False,
        "openai_replay_authority": False,
        "openai_worker_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_openai_attachment_capture(
    metadata: dict[str, Any],
    raw: dict[str, Any],
    attachment_capture: dict[str, Any],
) -> dict[str, Any]:
    """Create evidence that OpenAI output entered REAL_PROVIDER_ATTACHMENT_V1."""

    _verify_artifact_hash(metadata)
    _verify_artifact_hash(raw)
    if not isinstance(attachment_capture, dict) or "governed_result" not in attachment_capture:
        raise FailClosedRuntimeError("provider attachment capture is malformed")
    governed_result = attachment_capture["governed_result"]
    if not isinstance(governed_result, dict):
        raise FailClosedRuntimeError("provider attachment governed result is malformed")
    artifact = {
        "adapter_id": metadata["adapter_id"],
        "state": ATTACHMENT_CAPTURED,
        "provider_identity": OPENAI_PROVIDER_IDENTITY,
        "normalized_provider_identity": metadata["normalized_provider_identity"],
        "created_at": metadata["created_at"],
        "provider_request_metadata_hash": metadata["artifact_hash"],
        "raw_provider_response_hash": raw["artifact_hash"],
        "real_provider_attachment_hash": attachment_capture.get("provider_attachment_hash"),
        "real_provider_attachment_final_status": governed_result.get("final_status"),
        "real_provider_attachment_capture": deepcopy(attachment_capture),
        "routed_through_real_provider_attachment_v1": True,
        "routed_through_external_llm_response_attachment_v1": True,
        "proposal_source_only": True,
        "openai_authority": False,
        "aigol_governance_preserved": True,
        "authorization_model_preserved": True,
        "replay_model_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_openai_governed_result(metadata: dict[str, Any], raw: dict[str, Any], attachment: dict[str, Any]) -> dict[str, Any]:
    """Create final governed OpenAI adapter result."""

    _verify_artifact_hash(metadata)
    _verify_artifact_hash(raw)
    _verify_artifact_hash(attachment)
    completed = attachment.get("real_provider_attachment_final_status") == "COMPLETED"
    artifact = {
        "adapter_id": metadata["adapter_id"],
        "state": GOVERNED_RESULT_RETURNED if completed else OPENAI_FAILED,
        "final_status": "COMPLETED" if completed else OPENAI_FAILED,
        "provider_identity": OPENAI_PROVIDER_IDENTITY,
        "normalized_provider_identity": metadata["normalized_provider_identity"],
        "created_at": metadata["created_at"],
        "provider_request_metadata_hash": metadata["artifact_hash"],
        "raw_provider_response_hash": raw["artifact_hash"],
        "provider_attachment_capture_hash": attachment["artifact_hash"],
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": completed,
        "replay_records": True,
        "openai_execution_authority": False,
        "openai_authorization_authority": False,
        "openai_governance_authority": False,
        "openai_replay_authority": False,
        "openai_worker_authority": False,
        "tool_use": False,
        "function_calling": False,
        "streaming": False,
        "automatic_retries": False,
        "memory": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_openai_provider_adapter_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OpenAI adapter replay and nested provider attachment replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OpenAI provider adapter replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OpenAI provider adapter artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    final_artifact = wrappers[-1]["artifact"]
    nested_replay = None
    if (replay_path / "real_provider_attachment").exists():
        nested_replay = reconstruct_provider_attachment_replay(replay_path / "real_provider_attachment")
    return {
        "adapter_id": final_artifact["adapter_id"],
        "provider_identity": final_artifact["provider_identity"],
        "normalized_provider_identity": final_artifact.get("normalized_provider_identity"),
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": [wrapper["artifact"]["state"] for wrapper in wrappers],
        "replay_artifact_count": len(wrappers),
        "provider_attachment_replay": nested_replay,
        "append_only_valid": True,
        "replay_visible": True,
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": final_artifact.get("worker_executes_after_authorization") is True,
        "replay_records": True,
        "openai_authority": False,
        "replay_hash": replay_hash(wrappers),
    }


def _client_request(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_identity": metadata["provider_identity"],
        "model": metadata["model"],
        "input": metadata["provider_request_metadata"]["request_text"],
        "input_hash": metadata["provider_request_metadata"]["request_text_hash"],
        "timeout_seconds": metadata["provider_request_metadata"]["timeout_seconds"],
        "tool_use": False,
        "function_calling": False,
        "streaming": False,
        "automatic_retries": False,
    }


def _default_openai_client(request_metadata: dict[str, Any]) -> Any:
    from openai import OpenAI

    api_key = _load_api_key()
    client = OpenAI(api_key=api_key, timeout=request_metadata["timeout_seconds"], max_retries=0)
    return client.responses.create(model=request_metadata["model"], input=request_metadata["input"])


def _extract_openai_response_text(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return _normalize_response_text(raw_response)
    if not isinstance(raw_response, dict):
        to_dict = getattr(raw_response, "to_dict", None)
        if callable(to_dict):
            raw_response = to_dict()
        else:
            model_dump = getattr(raw_response, "model_dump", None)
            if callable(model_dump):
                raw_response = model_dump()
    if not isinstance(raw_response, dict):
        raise FailClosedRuntimeError("OpenAI response is malformed")
    for key in ("output_text", "text", "response_text"):
        if isinstance(raw_response.get(key), str):
            return _normalize_response_text(raw_response[key])
    output = raw_response.get("output")
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
        if chunks:
            return _normalize_response_text("".join(chunks))
    raise FailClosedRuntimeError("OpenAI response did not include bounded response text")


def _response_shape(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return "text"
    if isinstance(raw_response, dict):
        return "json_object"
    return type(raw_response).__name__


def _normalize_response_text(value: str) -> str:
    normalized = " ".join(_normalize_string(value, "openai_response").split())
    if len(normalized) > MAX_OPENAI_RESPONSE_CHARS:
        raise FailClosedRuntimeError("OpenAI response exceeds bounded size")
    return normalized


def _normalize_timeout(timeout_seconds: int) -> int:
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1 or timeout_seconds > 30:
        raise FailClosedRuntimeError("OpenAI timeout is outside the bounded range")
    return timeout_seconds


def _validate_api_key_source(api_key: str | None) -> str:
    value = api_key if api_key is not None else os.environ.get(OPENAI_API_KEY_ENV)
    _normalize_string(value, OPENAI_API_KEY_ENV)
    return "explicit_api_key" if api_key is not None else OPENAI_API_KEY_ENV


def _load_api_key() -> str:
    return _normalize_string(os.environ.get(OPENAI_API_KEY_ENV), OPENAI_API_KEY_ENV)


def _normalize_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OpenAI provider adapter replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _failure_artifact(*, adapter_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "adapter_id": adapter_id,
        "state": OPENAI_FAILED,
        "final_status": OPENAI_FAILED,
        "provider_identity": OPENAI_PROVIDER_IDENTITY,
        "normalized_provider_identity": NORMALIZED_OPENAI_PROVIDER_IDENTITY,
        "created_at": created_at,
        "failure_reason": failure_reason,
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": False,
        "replay_records": True,
        "openai_execution_authority": False,
        "openai_authorization_authority": False,
        "openai_governance_authority": False,
        "openai_replay_authority": False,
        "openai_worker_authority": False,
        "tool_use": False,
        "function_calling": False,
        "streaming": False,
        "automatic_retries": False,
        "memory": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_step(failure: dict[str, Any], step: str) -> dict[str, Any]:
    artifact = deepcopy(failure)
    artifact["failed_step"] = step
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    metadata: dict[str, Any] | None,
    raw: dict[str, Any] | None,
    attachment: dict[str, Any] | None,
    governed_result: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "provider_request_metadata": deepcopy(metadata),
        "raw_provider_response": deepcopy(raw),
        "provider_attachment_capture": deepcopy(attachment),
        "governed_result": deepcopy(governed_result),
    }
    capture["openai_provider_adapter_hash"] = replay_hash(capture)
    return capture


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OpenAI provider adapter artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("OpenAI provider adapter artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OpenAI provider adapter artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OpenAI provider adapter replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OpenAI provider adapter replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OpenAI provider adapter failed closed"
