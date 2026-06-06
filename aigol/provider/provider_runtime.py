"""Minimal provider attachment runtime for AiGOL."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any
from urllib import error as url_error
from urllib.parse import urlparse

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import validate_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PROVIDER_ATTACHMENT_RUNTIME_VERSION = "MINIMAL_PROVIDER_ATTACHMENT_RUNTIME_V1"
PROVIDER_HEALTH_AND_READINESS_RUNTIME_VERSION = "AIGOL_PROVIDER_HEALTH_AND_READINESS_RUNTIME_V1"
PROVIDER_READINESS_ARTIFACT_TYPE = "PROVIDER_READINESS_ARTIFACT_V1"
PROVIDER_PROPOSAL_CREATED = "PROVIDER_PROPOSAL_CREATED"
PROVIDER_PROPOSAL_RETURNED = "PROVIDER_PROPOSAL_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"
READY = "READY"
NOT_READY = "NOT_READY"
REPLAY_STEPS = ("provider_proposal_created", "provider_proposal_returned")
PROVIDER_READINESS_STEP = "provider_readiness_recorded"

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


class ProviderNotReadyRuntimeError(FailClosedRuntimeError):
    def __init__(self, readiness_artifact: dict[str, Any]) -> None:
        super().__init__("provider readiness failed closed")
        self.readiness_artifact = deepcopy(readiness_artifact)


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
        readiness_artifact = None
        if _requires_provider_readiness(adapter):
            readiness_artifact = _provider_readiness_artifact(
                provider=provider,
                adapter=adapter,
                timestamp=timestamp,
            )
            _persist_provider_readiness_if_possible(replay_path, readiness_artifact)
            if readiness_artifact["readiness_status"] != READY:
                raise ProviderNotReadyRuntimeError(readiness_artifact)
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
        failure_diagnostics = _failure_diagnostics(exc)
        readiness_artifact = _readiness_artifact_from_exception(exc)
        envelope = _failed_envelope(
            provider_id=provider_id,
            request=request,
            proposal_id=proposal_id,
            timestamp=timestamp,
            failure_reason=_failure_reason(exc),
            failure_diagnostics=failure_diagnostics,
            readiness_artifact=readiness_artifact,
        )
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], envelope)
        returned = _failed_returned(
            envelope=envelope,
            failure_reason=envelope["failure_reason"],
            failure_diagnostics=failure_diagnostics,
            readiness_artifact=readiness_artifact,
        )
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
    replay = {
        "provider_id": created["provider_id"],
        "provider_version": created["provider_version"],
        "request": deepcopy(created["request"]),
        "response": deepcopy(created["response"]),
        "timestamp": created["timestamp"],
        "proposal_hash": created["proposal_hash"],
        "provider_status": created["provider_status"],
        "provider_metadata": deepcopy(created.get("provider_metadata", _default_provider_metadata())),
        "provider_invoked": created["provider_invoked"],
        "authority": False,
        "execution_capable": False,
        "worker_invoked": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }
    if "failure_diagnostics" in created:
        replay["failure_diagnostics"] = deepcopy(created["failure_diagnostics"])
    if "provider_readiness_artifact" in created:
        replay["provider_readiness_artifact"] = deepcopy(created["provider_readiness_artifact"])
    readiness_path = replay_path / f"000_{PROVIDER_READINESS_STEP}.json"
    if readiness_path.exists():
        readiness_wrapper = load_json(readiness_path)
        if readiness_wrapper.get("replay_step") != PROVIDER_READINESS_STEP:
            raise FailClosedRuntimeError("provider readiness replay step mismatch")
        _verify_wrapper_hash(readiness_wrapper)
        readiness_artifact = readiness_wrapper.get("artifact")
        if not isinstance(readiness_artifact, dict):
            raise FailClosedRuntimeError("provider readiness replay artifact must be a JSON object")
        _verify_artifact_hash(readiness_artifact, "provider readiness artifact")
        replay["provider_readiness_artifact"] = deepcopy(readiness_artifact)
    return replay


def _created_replay(*, provider: dict[str, Any], envelope: dict[str, Any], timestamp: str) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": PROVIDER_PROPOSAL_CREATED,
        "provider_id": provider["provider_id"],
        "provider_type": provider["provider_type"],
        "provider_version": provider["provider_version"],
        "provider_status": provider["provider_status"],
        "provider_metadata": _provider_metadata(provider),
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
        "provider_metadata": _provider_metadata(provider),
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


def _failed_envelope(
    *,
    provider_id: Any,
    request: Any,
    proposal_id: Any,
    timestamp: Any,
    failure_reason: str,
    failure_diagnostics: dict[str, Any],
    readiness_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "provider_id": provider_id if isinstance(provider_id, str) and provider_id.strip() else "INVALID_PROVIDER_ID",
        "provider_type": "UNKNOWN",
        "provider_version": "UNKNOWN",
        "provider_status": "FAILED_CLOSED",
        "provider_metadata": _default_provider_metadata(),
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
        "failure_diagnostics": deepcopy(failure_diagnostics),
    }
    if readiness_artifact is not None:
        artifact["provider_readiness_artifact"] = deepcopy(readiness_artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_returned(
    *,
    envelope: dict[str, Any],
    failure_reason: str,
    failure_diagnostics: dict[str, Any],
    readiness_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact = {
        "runtime_version": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "event_type": FAILED_CLOSED,
        "provider_id": envelope["provider_id"],
        "provider_type": envelope["provider_type"],
        "provider_version": envelope["provider_version"],
        "provider_metadata": deepcopy(envelope.get("provider_metadata", _default_provider_metadata())),
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "created_hash": envelope["artifact_hash"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authority": False,
        "execution_capable": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
        "failure_diagnostics": deepcopy(failure_diagnostics),
    }
    if readiness_artifact is not None:
        artifact["provider_readiness_artifact"] = deepcopy(readiness_artifact)
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


def _provider_metadata(provider: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain": provider.get("domain", "unspecified"),
        "capability": provider.get("capability", "proposal_generation"),
        "resource_type": provider.get("resource_type", "provider"),
        "metadata_authority": False,
        "metadata_routing_enabled": False,
        "metadata_selection_enabled": False,
        "metadata_execution_enabled": False,
    }


def _default_provider_metadata() -> dict[str, Any]:
    return {
        "domain": "unspecified",
        "capability": "proposal_generation",
        "resource_type": "provider",
        "metadata_authority": False,
        "metadata_routing_enabled": False,
        "metadata_selection_enabled": False,
        "metadata_execution_enabled": False,
    }


def _ensure_provider_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")
    readiness_path = replay_path / f"000_{PROVIDER_READINESS_STEP}.json"
    if readiness_path.exists():
        raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {readiness_path.name}")


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


def _persist_provider_readiness_if_possible(replay_dir: Path, artifact: dict[str, Any]) -> None:
    path = replay_dir / f"000_{PROVIDER_READINESS_STEP}.json"
    if path.exists():
        return
    _verify_artifact_hash(artifact, "provider readiness artifact")
    wrapper = {
        "replay_index": 0,
        "replay_step": PROVIDER_READINESS_STEP,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path, wrapper)


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
    if isinstance(exc, ProviderNotReadyRuntimeError):
        category = exc.readiness_artifact["sanitized_diagnostics"]["failure_category"]
        if category == "MISSING_API_KEY":
            return "OPENAI_API_KEY is required"
        return "provider readiness failed closed"
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider attachment failed closed"


def _failure_diagnostics(exc: Exception) -> dict[str, Any]:
    readiness_artifact = _readiness_artifact_from_exception(exc)
    if readiness_artifact is not None:
        return deepcopy(readiness_artifact["sanitized_diagnostics"])
    diagnostic_exc = _diagnostic_exception(exc)
    return {
        "failure_stage": _failure_stage(exc=exc, diagnostic_exc=diagnostic_exc),
        "exception_type": _exception_type(diagnostic_exc),
        "transport_failure_category": _transport_failure_category(diagnostic_exc),
        "http_status": _http_status(diagnostic_exc),
    }


def _diagnostic_exception(exc: Exception) -> Exception:
    cause = exc.__cause__
    if isinstance(cause, (url_error.HTTPError, url_error.URLError, TimeoutError, json.JSONDecodeError)):
        return cause
    return exc


def _failure_stage(*, exc: Exception, diagnostic_exc: Exception) -> str:
    if isinstance(diagnostic_exc, (url_error.HTTPError, url_error.URLError, TimeoutError, json.JSONDecodeError)):
        return "openai_http_request"
    if isinstance(exc, FailClosedRuntimeError) and str(exc).startswith("OpenAI provider"):
        return "openai_provider_adapter"
    return "provider_attachment_runtime"


def _exception_type(exc: Exception) -> str:
    name = type(exc).__name__
    if not name or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_" for character in name):
        return "UNKNOWN_EXCEPTION"
    return name


def _transport_failure_category(exc: Exception) -> str:
    if isinstance(exc, url_error.HTTPError):
        return "HTTP_ERROR"
    if isinstance(exc, url_error.URLError):
        return "URL_ERROR"
    if isinstance(exc, TimeoutError):
        return "TIMEOUT"
    if isinstance(exc, json.JSONDecodeError):
        return "JSON_DECODE"
    if isinstance(exc, FailClosedRuntimeError):
        return "FAIL_CLOSED"
    return "CLIENT_EXCEPTION"


def _http_status(exc: Exception) -> int | None:
    if isinstance(exc, url_error.HTTPError) and isinstance(exc.code, int):
        return exc.code
    return None


def _readiness_artifact_from_exception(exc: Exception) -> dict[str, Any] | None:
    if isinstance(exc, ProviderNotReadyRuntimeError):
        return deepcopy(exc.readiness_artifact)
    return None


def _provider_readiness_artifact(*, provider: dict[str, Any], adapter: ProviderAdapter, timestamp: str) -> dict[str, Any]:
    readiness_checks = _provider_readiness_checks(provider=provider, adapter=adapter)
    failed_check = next((check for check in readiness_checks if check["check_status"] != READY), None)
    readiness_status = READY if failed_check is None else NOT_READY
    diagnostics = _readiness_diagnostics(failed_check)
    artifact = {
        "artifact_type": PROVIDER_READINESS_ARTIFACT_TYPE,
        "runtime_version": PROVIDER_HEALTH_AND_READINESS_RUNTIME_VERSION,
        "provider_id": provider["provider_id"],
        "provider_type": provider["provider_type"],
        "provider_version": provider["provider_version"],
        "provider_status": provider["provider_status"],
        "provider_identity_hash": provider["provider_identity_hash"],
        "readiness_status": readiness_status,
        "readiness_checks": readiness_checks,
        "sanitized_diagnostics": diagnostics,
        "api_key_present": _check_status(readiness_checks, "api_key_presence") == READY,
        "provider_configuration_valid": _check_status(readiness_checks, "provider_configuration_validity") == READY,
        "model_configuration_valid": _check_status(readiness_checks, "model_configuration_validity") == READY,
        "transport_available": _check_status(readiness_checks, "transport_availability") == READY,
        "provider_activation_ready": readiness_status == READY,
        "provider_invocation_allowed": readiness_status == READY,
        "provider_invoked": False,
        "credential_exposed": False,
        "authorization_header_exposed": False,
        "request_body_exposed": False,
        "raw_response_body_exposed": False,
        "stack_trace_exposed": False,
        "authority": False,
        "execution_capable": False,
        "worker_invoked": False,
        "replay_visible": True,
        "timestamp": timestamp if isinstance(timestamp, str) and timestamp.strip() else "INVALID_TIMESTAMP",
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_readiness_checks(*, provider: dict[str, Any], adapter: ProviderAdapter) -> list[dict[str, Any]]:
    return [
        _readiness_check(
            check_id="api_key_presence",
            ready=_openai_api_key_present(adapter),
            failure_category="MISSING_API_KEY",
        ),
        _readiness_check(
            check_id="provider_configuration_validity",
            ready=_openai_provider_configuration_valid(provider=provider, adapter=adapter),
            failure_category="PROVIDER_CONFIGURATION_INVALID",
        ),
        _readiness_check(
            check_id="model_configuration_validity",
            ready=_openai_model_configuration_valid(adapter),
            failure_category="MODEL_CONFIGURATION_INVALID",
        ),
        _readiness_check(
            check_id="transport_availability",
            ready=_openai_transport_available(adapter),
            failure_category="TRANSPORT_UNAVAILABLE",
        ),
        _readiness_check(
            check_id="provider_activation_readiness",
            ready=provider.get("provider_status") == AVAILABLE,
            failure_category="PROVIDER_NOT_AVAILABLE",
        ),
    ]


def _readiness_check(*, check_id: str, ready: bool, failure_category: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "check_status": READY if ready else NOT_READY,
        "failure_category": None if ready else failure_category,
    }


def _readiness_diagnostics(failed_check: dict[str, Any] | None) -> dict[str, Any]:
    if failed_check is None:
        return {
            "readiness_stage": "provider_activation_readiness",
            "failure_category": None,
            "exception_type": None,
            "http_status": None,
        }
    return {
        "readiness_stage": failed_check["check_id"],
        "failure_category": failed_check["failure_category"],
        "exception_type": None,
        "http_status": None,
    }


def _check_status(readiness_checks: list[dict[str, Any]], check_id: str) -> str:
    for check in readiness_checks:
        if check["check_id"] == check_id:
            return check["check_status"]
    return NOT_READY


def _openai_api_key_present(adapter: ProviderAdapter) -> bool:
    candidate = getattr(adapter, "_api_key", None)
    if candidate is None:
        candidate = os.environ.get("OPENAI_API_KEY")
    return isinstance(candidate, str) and bool(candidate.strip())


def _requires_provider_readiness(adapter: ProviderAdapter) -> bool:
    return (
        getattr(adapter, "provider_id", None) == "openai"
        and hasattr(adapter, "_client")
        and hasattr(adapter, "endpoint")
        and hasattr(adapter, "model")
    )


def _openai_provider_configuration_valid(*, provider: dict[str, Any], adapter: ProviderAdapter) -> bool:
    return (
        provider.get("provider_id") == getattr(adapter, "provider_id", None)
        and provider.get("provider_version") == getattr(adapter, "provider_version", None)
    )


def _openai_model_configuration_valid(adapter: ProviderAdapter) -> bool:
    model = getattr(adapter, "model", None)
    endpoint = getattr(adapter, "endpoint", None)
    timeout_seconds = getattr(adapter, "timeout_seconds", None)
    return (
        isinstance(model, str)
        and bool(model.strip())
        and isinstance(endpoint, str)
        and _https_url(endpoint)
        and isinstance(timeout_seconds, int)
        and timeout_seconds > 0
    )


def _openai_transport_available(adapter: ProviderAdapter) -> bool:
    return callable(getattr(adapter, "_client", None))


def _https_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme == "https" and bool(parsed.netloc)
