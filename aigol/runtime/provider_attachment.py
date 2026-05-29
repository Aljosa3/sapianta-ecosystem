"""Provider attachment boundary for proposal-only provider responses."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.external_llm_response_attachment import (
    attach_external_llm_response,
    reconstruct_external_llm_response_attachment_replay,
)
from aigol.runtime.minimal_cognition_to_execution_bridge import READ_ONLY_RUNTIME_INSPECTION
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_CAPTURED = "PROVIDER_CAPTURED"
RAW_PROVIDER_RESPONSE_CAPTURED = "RAW_PROVIDER_RESPONSE_CAPTURED"
PROVIDER_ATTACHMENT_RECORDED = "PROVIDER_ATTACHMENT_RECORDED"
PROVIDER_GOVERNED_RESULT_RETURNED = "PROVIDER_GOVERNED_RESULT_RETURNED"
PROVIDER_FAILED = "FAILED"

REPLAY_STEPS = (
    "provider_identity",
    "raw_provider_response",
    "provider_attachment_record",
    "governed_result",
)
MAX_PROVIDER_RESPONSE_CHARS = 4096
FORBIDDEN_PROVIDER_IDENTITIES = frozenset({"", ".", ".."})


def attach_real_provider_response(
    *,
    provider_attachment_id: str,
    provider_identity: str,
    provider_response: Any,
    created_at: str,
    replay_dir: str | Path,
    target_capability: str = READ_ONLY_RUNTIME_INSPECTION,
    authorize: bool = True,
) -> dict[str, Any]:
    """Attach one provider response as proposal-only input."""

    replay_path = Path(replay_dir)
    try:
        identity = create_provider_identity_artifact(
            provider_attachment_id=provider_attachment_id,
            provider_identity=provider_identity,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, "provider_identity", identity)
        raw = capture_raw_provider_response(
            identity,
            provider_response=provider_response,
        )
        _persist_step(replay_path, 1, "raw_provider_response", raw)
        external_capture = attach_external_llm_response(
            attachment_id=f"{identity['provider_attachment_id']}:EXTERNAL-LLM",
            provider_identity=identity["provider_identity"],
            external_response=raw["raw_provider_response"],
            created_at=identity["created_at"],
            replay_dir=replay_path / "external_llm_attachment",
            target_capability=target_capability,
            authorize=authorize,
        )
        record = create_provider_attachment_record(identity, raw, external_capture)
        _persist_step(replay_path, 2, "provider_attachment_record", record)
        governed_result = create_provider_governed_result(identity, raw, record)
        _persist_step(replay_path, 3, "governed_result", governed_result)
        return _capture(identity, raw, record, governed_result)
    except Exception as exc:
        failure = _failure_artifact(
            provider_attachment_id=(
                provider_attachment_id
                if isinstance(provider_attachment_id, str) and provider_attachment_id.strip()
                else "PROVIDER-ATTACHMENT-INVALID"
            ),
            provider_identity=provider_identity if isinstance(provider_identity, str) and provider_identity.strip() else "PROVIDER-INVALID",
            created_at=created_at if isinstance(created_at, str) and created_at.strip() else "1970-01-01T00:00:00+00:00",
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(None, None, None, failure)


def create_provider_identity_artifact(
    *,
    provider_attachment_id: str,
    provider_identity: str,
    created_at: str,
) -> dict[str, Any]:
    """Create deterministic provider identity evidence."""

    identity = _normalize_provider_identity(provider_identity)
    artifact = {
        "provider_attachment_id": _require_string(provider_attachment_id, "provider_attachment_id"),
        "state": PROVIDER_CAPTURED,
        "provider_identity": identity,
        "created_at": _require_string(created_at, "created_at"),
        "provider_role": "PROPOSAL_SOURCE_ONLY",
        "provider_execution_authority": False,
        "provider_authorization_authority": False,
        "provider_governance_authority": False,
        "provider_replay_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def capture_raw_provider_response(identity_artifact: dict[str, Any], *, provider_response: Any) -> dict[str, Any]:
    """Capture raw provider response before external attachment handoff."""

    _verify_artifact_hash(identity_artifact)
    if identity_artifact.get("state") != PROVIDER_CAPTURED:
        raise FailClosedRuntimeError("provider identity artifact is required")
    response = _normalize_provider_response(provider_response)
    artifact = {
        "provider_attachment_id": identity_artifact["provider_attachment_id"],
        "state": RAW_PROVIDER_RESPONSE_CAPTURED,
        "provider_identity": identity_artifact["provider_identity"],
        "provider_identity_hash": identity_artifact["artifact_hash"],
        "created_at": identity_artifact["created_at"],
        "raw_provider_response": response,
        "raw_provider_response_hash": replay_hash(response),
        "untrusted_provider_output": True,
        "proposal_source_only": True,
        "execution_authority": False,
        "authorization_authority": False,
        "governance_authority": False,
        "replay_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_provider_attachment_record(
    identity_artifact: dict[str, Any],
    raw_artifact: dict[str, Any],
    external_capture: dict[str, Any],
) -> dict[str, Any]:
    """Record provider-to-external-attachment handoff evidence."""

    _verify_artifact_hash(identity_artifact)
    _verify_artifact_hash(raw_artifact)
    if not isinstance(external_capture, dict) or "governed_result" not in external_capture:
        raise FailClosedRuntimeError("external attachment capture is malformed")
    governed_result = external_capture["governed_result"]
    if not isinstance(governed_result, dict):
        raise FailClosedRuntimeError("external attachment governed result is malformed")
    artifact = {
        "provider_attachment_id": identity_artifact["provider_attachment_id"],
        "state": PROVIDER_ATTACHMENT_RECORDED,
        "provider_identity": identity_artifact["provider_identity"],
        "provider_identity_hash": identity_artifact["artifact_hash"],
        "raw_provider_response_hash": raw_artifact["artifact_hash"],
        "external_attachment_hash": external_capture.get("attachment_hash"),
        "external_attachment_final_status": governed_result.get("final_status"),
        "external_attachment_capture": deepcopy(external_capture),
        "provider_forwarded_to_external_attachment": True,
        "provider_authority": False,
        "aigol_governance_preserved": True,
        "authorization_model_preserved": True,
        "replay_model_preserved": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_provider_governed_result(
    identity_artifact: dict[str, Any],
    raw_artifact: dict[str, Any],
    record_artifact: dict[str, Any],
) -> dict[str, Any]:
    """Create governed provider attachment result."""

    _verify_artifact_hash(identity_artifact)
    _verify_artifact_hash(raw_artifact)
    _verify_artifact_hash(record_artifact)
    completed = record_artifact.get("external_attachment_final_status") == "COMPLETED"
    artifact = {
        "provider_attachment_id": identity_artifact["provider_attachment_id"],
        "state": PROVIDER_GOVERNED_RESULT_RETURNED if completed else PROVIDER_FAILED,
        "final_status": "COMPLETED" if completed else PROVIDER_FAILED,
        "provider_identity": identity_artifact["provider_identity"],
        "provider_identity_hash": identity_artifact["artifact_hash"],
        "raw_provider_response_hash": raw_artifact["artifact_hash"],
        "provider_attachment_record_hash": record_artifact["artifact_hash"],
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": completed,
        "replay_records": True,
        "provider_execution_authority": False,
        "provider_authorization_authority": False,
        "provider_governance_authority": False,
        "provider_replay_authority": False,
        "provider_specific_integration": False,
        "network_access": False,
        "provider_sdk": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_provider_attachment_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate provider attachment replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider attachment replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider attachment artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    final_artifact = wrappers[-1]["artifact"]
    external_replay = None
    if (replay_path / "external_llm_attachment").exists():
        external_replay = reconstruct_external_llm_response_attachment_replay(replay_path / "external_llm_attachment")
    return {
        "provider_attachment_id": final_artifact["provider_attachment_id"],
        "provider_identity": final_artifact["provider_identity"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": [wrapper["artifact"]["state"] for wrapper in wrappers],
        "replay_artifact_count": len(wrappers),
        "external_attachment_replay": external_replay,
        "append_only_valid": True,
        "replay_visible": True,
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": final_artifact.get("worker_executes_after_authorization") is True,
        "replay_records": True,
        "provider_authority": False,
        "replay_hash": replay_hash(wrappers),
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider attachment replay step ordering mismatch")
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


def _failure_artifact(*, provider_attachment_id: str, provider_identity: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "provider_attachment_id": provider_attachment_id,
        "state": PROVIDER_FAILED,
        "final_status": PROVIDER_FAILED,
        "provider_identity": provider_identity,
        "created_at": created_at,
        "failure_reason": failure_reason,
        "llm_proposes": True,
        "aigol_governs": True,
        "worker_executes_after_authorization": False,
        "replay_records": True,
        "provider_execution_authority": False,
        "provider_authorization_authority": False,
        "provider_governance_authority": False,
        "provider_replay_authority": False,
        "provider_specific_integration": False,
        "network_access": False,
        "provider_sdk": False,
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
    identity_artifact: dict[str, Any] | None,
    raw_artifact: dict[str, Any] | None,
    record_artifact: dict[str, Any] | None,
    governed_result: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "provider_identity": deepcopy(identity_artifact),
        "raw_provider_response": deepcopy(raw_artifact),
        "provider_attachment_record": deepcopy(record_artifact),
        "governed_result": deepcopy(governed_result),
    }
    capture["provider_attachment_hash"] = replay_hash(capture)
    return capture


def _normalize_provider_identity(value: Any) -> str:
    identity = _require_string(value, "provider_identity").strip().lower()
    if identity in FORBIDDEN_PROVIDER_IDENTITIES:
        raise FailClosedRuntimeError("provider_identity is invalid")
    if any(char.isspace() for char in identity):
        raise FailClosedRuntimeError("provider_identity must be deterministic")
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
    if any(char not in allowed_chars for char in identity):
        raise FailClosedRuntimeError("provider_identity must be deterministic")
    return identity


def _normalize_provider_response(value: Any) -> str:
    raw = _require_string(value, "provider_response")
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError("provider_response is required")
    if len(normalized) > MAX_PROVIDER_RESPONSE_CHARS:
        raise FailClosedRuntimeError("provider_response exceeds bounded size")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider attachment artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("provider attachment artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider attachment artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider attachment replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider attachment replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider attachment failed closed"
