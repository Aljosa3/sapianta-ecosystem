"""Minimal provider attachment runtime for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import validate_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_ATTACHMENT_RUNTIME_VERSION = "MINIMAL_PROVIDER_ATTACHMENT_RUNTIME_V1"
PROVIDER_PROPOSAL_CREATED = "PROVIDER_PROPOSAL_CREATED"
PROVIDER_PROPOSAL_RETURNED = "PROVIDER_PROPOSAL_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("provider_proposal_created", "provider_proposal_returned")

FORBIDDEN_RUNTIME_FIELDS = frozenset(
    {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "dispatch_request",
        "worker_command",
        "provider_command",
        "memory_mutation",
        "replay_mutation",
    }
)


def run_provider_attachment(
    *,
    provider_id: str,
    request: Any,
    proposal_id: str,
    timestamp: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Attach a provider as proposal source and record replay-visible evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_provider_replay_available(replay_path)
        provider = registry.lookup_provider(provider_id)
        if provider["provider_status"] != AVAILABLE:
            raise FailClosedRuntimeError("provider is unavailable")
        _validate_adapter(provider=provider, adapter=adapter)
        _validate_request(request)
        envelope = adapter.generate_proposal(deepcopy(request), proposal_id=proposal_id, timestamp=timestamp)
        envelope_dict = validate_provider_proposal_envelope(envelope)
        if envelope_dict["provider_id"] != provider["provider_id"]:
            raise FailClosedRuntimeError("provider proposal envelope identity mismatch")
        if envelope_dict["provider_version"] != provider["provider_version"]:
            raise FailClosedRuntimeError("provider proposal envelope version mismatch")
        created = _created_replay(provider=provider, envelope=envelope_dict, timestamp=timestamp)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], created)
        returned = _returned_replay(provider=provider, envelope=envelope_dict, created=created, status=PROVIDER_PROPOSAL_RETURNED, failure_reason=None)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(envelope_dict, created, returned)
    except Exception as exc:
        envelope = _failed_envelope(
            provider_id=provider_id,
            request=request,
            proposal_id=proposal_id,
            timestamp=timestamp,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], envelope)
        returned = _failed_returned(envelope=envelope, failure_reason=envelope["failure_reason"])
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(envelope, envelope, returned)


def reconstruct_provider_attachment_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider attachment replay without granting authority."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider attachment replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider attachment replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "provider attachment artifact")
        wrappers.append(wrapper)
    created = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("proposal_hash") != created.get("proposal_hash"):
        raise FailClosedRuntimeError("provider attachment replay proposal hash mismatch")
    if returned.get("created_hash") != created.get("artifact_hash"):
        raise FailClosedRuntimeError("provider attachment replay created hash mismatch")
    return {
        "provider_id": created["provider_id"],
        "provider_version": created["provider_version"],
        "request": deepcopy(created["request"]),
        "response": deepcopy(created["response"]),
        "timestamp": created["timestamp"],
        "proposal_hash": created["proposal_hash"],
        "provider_status": created["provider_status"],
        "provider_invoked": created["provider_invoked"],
        "authority": False,
        "execution_capable": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _created_replay(*, provider: dict[str, Any], envelope: dict[str, Any], timestamp: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": PROVIDER_PROPOSAL_CREATED,
        "provider_id": provider["provider_id"],
        "provider_type": provider["provider_type"],
        "provider_version": provider["provider_version"],
        "provider_status": provider["provider_status"],
        "request": deepcopy(envelope["request"]),
        "response": deepcopy(envelope["response"]),
        "timestamp": timestamp,
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "provider_identity_hash": provider["provider_identity_hash"],
        "provider_invoked": True,
        "worker_invoked": False,
        "authority": False,
        "execution_capable": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_replay(
    *,
    provider: dict[str, Any],
    envelope: dict[str, Any],
    created: dict[str, Any],
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": status,
        "provider_id": provider["provider_id"],
        "provider_type": provider["provider_type"],
        "provider_version": provider["provider_version"],
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "created_hash": created["artifact_hash"],
        "provider_invoked": True,
        "worker_invoked": False,
        "authority": False,
        "execution_capable": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_envelope(*, provider_id: Any, request: Any, proposal_id: Any, timestamp: Any, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "provider_id": provider_id if isinstance(provider_id, str) and provider_id.strip() else "INVALID_PROVIDER_ID",
        "provider_type": "UNKNOWN",
        "provider_version": "UNKNOWN",
        "provider_status": "FAILED_CLOSED",
        "request": deepcopy(request) if _is_json_serializable(request) else "INVALID_REQUEST",
        "response": None,
        "timestamp": timestamp if isinstance(timestamp, str) and timestamp.strip() else "INVALID_TIMESTAMP",
        "proposal_id": proposal_id if isinstance(proposal_id, str) and proposal_id.strip() else "INVALID_PROPOSAL_ID",
        "proposal_hash": "FAILED_CLOSED",
        "provider_identity_hash": None,
        "provider_invoked": False,
        "worker_invoked": False,
        "authority": False,
        "execution_capable": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_returned(*, envelope: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "provider_id": envelope["provider_id"],
        "provider_type": envelope["provider_type"],
        "provider_version": envelope["provider_version"],
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "created_hash": envelope["artifact_hash"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authority": False,
        "execution_capable": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(envelope: dict[str, Any], created: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "provider_proposal_envelope": deepcopy(envelope),
        "provider_proposal_created": deepcopy(created),
        "provider_proposal_returned": deepcopy(returned),
    }
    capture["provider_attachment_runtime_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_provider_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _validate_adapter(*, provider: dict[str, Any], adapter: ProviderAdapter) -> None:
    if not hasattr(adapter, "generate_proposal"):
        raise FailClosedRuntimeError("provider adapter is invalid")
    if getattr(adapter, "provider_id", None) != provider["provider_id"]:
        raise FailClosedRuntimeError("provider adapter identity mismatch")
    if getattr(adapter, "provider_version", None) != provider["provider_version"]:
        raise FailClosedRuntimeError("provider adapter version mismatch")


def _validate_request(request: Any) -> None:
    if not _is_json_serializable(request):
        raise FailClosedRuntimeError("provider request must be JSON serializable")
    if isinstance(request, dict) and FORBIDDEN_RUNTIME_FIELDS.intersection(request):
        raise FailClosedRuntimeError("provider request contains forbidden field")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider attachment replay step ordering mismatch")
    _verify_artifact_hash(artifact, "provider attachment artifact")
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
        raise FailClosedRuntimeError("provider attachment replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider attachment replay hash mismatch")


def _is_json_serializable(value: Any) -> bool:
    try:
        replay_hash(value)
    except (TypeError, ValueError):
        return False
    return True


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider attachment failed closed"
