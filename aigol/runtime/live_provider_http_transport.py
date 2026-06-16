"""Governed HTTP transport boundary for AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.external_resource_registry_runtime import (
    COGNITION_PROVIDER,
    OPENAI_PROVIDER_ID,
    real_provider_err_v1_registry,
    select_resource_for_capability,
)
from aigol.runtime.first_real_provider_runtime import (
    OPENAI_CAPABILITIES,
    adapt_openai_contract_to_canonical,
)
from aigol.runtime.live_provider_runtime_boundary import (
    ERROR_AUTHENTICATION_UNAVAILABLE,
    ERROR_AUTHORITY_BOUNDARY_VIOLATION,
    ERROR_CREDENTIAL_POLICY_INVALID,
    ERROR_MALFORMED_RESPONSE,
    ERROR_RATE_LIMIT,
    ERROR_TIMEOUT,
    ERROR_TRANSPORT_UNAVAILABLE,
    PROHIBITED_RESPONSE_PHRASES,
    validate_live_provider_approval,
    validate_live_provider_credential_policy,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    OPENAI_RESPONSES_ENDPOINT,
    OPENAI_RESPONSES_SCHEMA,
    create_default_openai_cognition_provider_contract,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1"

LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1 = "LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1"
LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1 = "LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1"
LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1 = "LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1"
LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1 = "LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS_SUCCESS = (
    "live_provider_http_request",
    "live_provider_http_response",
    "live_provider_http_transport_audit",
)

REPLAY_STEPS_ERROR = (
    "live_provider_http_request",
    "live_provider_http_error",
    "live_provider_http_transport_audit",
)

HttpTransport = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def run_live_provider_http_transport(
    *,
    transport_id: str,
    human_request: str,
    created_at: str,
    replay_dir: str | Path,
    approval_artifact: dict[str, Any] | None,
    credential_policy_artifact: dict[str, Any] | None,
    err_registry: dict[str, Any] | None = None,
    model: str = "gpt-5.1",
    timeout_seconds: int = 20,
    transport: HttpTransport | None = None,
    live_http_enabled: bool = False,
) -> dict[str, Any]:
    """Run the governed OpenAI HTTP transport boundary through injected transport only."""

    replay_path = Path(replay_dir)
    transport_run_id = _require_string(transport_id, "transport_id")
    request_artifact: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        if live_http_enabled is True:
            raise FailClosedRuntimeError("live provider HTTP transport failed closed: live HTTP dispatch is not enabled")
        approval = validate_live_provider_approval(approval_artifact)
        credential_policy = validate_live_provider_credential_policy(credential_policy_artifact)
        err_selection = select_resource_for_capability(
            selection_id=f"{transport_run_id}:ERR_OPENAI_SELECTION",
            required_capability=approval["required_capability"],
            replay_dir=replay_path / "err_openai_selection",
            created_at=created_at,
            registry=deepcopy(err_registry) if err_registry is not None else real_provider_err_v1_registry(),
            resource_type=COGNITION_PROVIDER,
            human_intent=human_request,
            hirr_output={
                "runtime": MILESTONE_ID,
                "required_capability": approval["required_capability"],
                "resource_type": COGNITION_PROVIDER,
            },
        )
        if err_selection["selected_resource_id"] != OPENAI_PROVIDER_ID:
            raise FailClosedRuntimeError("live provider HTTP transport failed closed: ERR did not select openai")
        source_contract = create_default_openai_cognition_provider_contract(created_at=created_at)
        canonical_contract = adapt_openai_contract_to_canonical(
            source_contract=source_contract,
            capabilities=OPENAI_CAPABILITIES,
            created_at=created_at,
        )
        request_artifact = create_live_http_request_artifact(
            transport_id=transport_run_id,
            human_request=human_request,
            approval_artifact=approval,
            credential_policy_artifact=credential_policy,
            err_selection_capture=err_selection,
            canonical_contract=canonical_contract,
            model=model,
            timeout_seconds=timeout_seconds,
            created_at=created_at,
        )
        if transport is None:
            raise FailClosedRuntimeError("live provider HTTP transport failed closed: injected transport is required")
        raw_response = _invoke_injected_http_transport(transport=transport, request_artifact=request_artifact)
        response_artifact = create_live_http_response_artifact(
            transport_id=transport_run_id,
            request_artifact=request_artifact,
            raw_response=raw_response,
            created_at=created_at,
        )
        audit_artifact = create_live_http_transport_audit(
            transport_id=transport_run_id,
            final_status=STATUS_COMPLETED,
            failure_reason="",
            request_artifact=request_artifact,
            response_artifact=response_artifact,
            error_artifact=None,
            created_at=created_at,
        )
        _persist_sequence(replay_path, REPLAY_STEPS_SUCCESS, (request_artifact, response_artifact, audit_artifact))
        return _capture(
            transport_id=transport_run_id,
            final_status=STATUS_COMPLETED,
            failure_reason="",
            replay_path=replay_path,
            request_artifact=request_artifact,
            response_artifact=response_artifact,
            error_artifact=None,
            audit_artifact=audit_artifact,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "live provider HTTP transport failed closed"
        classification = _classify_error(reason)
        if request_artifact is None:
            request_artifact = create_failed_live_http_request_artifact(
                transport_id=transport_run_id,
                failure_reason=reason,
                created_at=created_at,
            )
        error_artifact = create_live_http_error_artifact(
            transport_id=transport_run_id,
            request_artifact=request_artifact,
            error_classification=classification,
            failure_reason=reason,
            created_at=created_at,
        )
        audit_artifact = create_live_http_transport_audit(
            transport_id=transport_run_id,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            request_artifact=request_artifact,
            response_artifact=None,
            error_artifact=error_artifact,
            created_at=created_at,
        )
        _persist_sequence(replay_path, REPLAY_STEPS_ERROR, (request_artifact, error_artifact, audit_artifact))
        return _capture(
            transport_id=transport_run_id,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            request_artifact=request_artifact,
            response_artifact=None,
            error_artifact=error_artifact,
            audit_artifact=audit_artifact,
        )


def create_live_http_request_artifact(
    *,
    transport_id: str,
    human_request: str,
    approval_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    err_selection_capture: dict[str, Any],
    canonical_contract: dict[str, Any],
    model: str,
    timeout_seconds: int,
    created_at: str,
) -> dict[str, Any]:
    """Create a replay-safe HTTP request artifact with secret-free headers."""

    if err_selection_capture.get("selected_resource_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: ERR did not select openai")
    _verify_artifact_hash(canonical_contract, "canonical contract")
    timeout = _normalize_timeout(timeout_seconds)
    body = {
        "model": _require_string(model, "model"),
        "input": _require_string(human_request, "human_request"),
        "stream": False,
    }
    request = {
        "method": "POST",
        "url": OPENAI_RESPONSES_ENDPOINT,
        "headers": {
            "Authorization": "<redacted>",
            "Content-Type": "application/json",
        },
        "body": body,
        "timeout_seconds": timeout,
    }
    artifact = {
        "artifact_type": LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "transport_id": _require_string(transport_id, "transport_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "endpoint": OPENAI_RESPONSES_ENDPOINT,
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "err_selection_artifact_hash": err_selection_capture["err_selection_evidence_artifact"]["artifact_hash"],
        "canonical_contract_artifact_hash": canonical_contract["artifact_hash"],
        "http_request": request,
        "http_request_hash": replay_hash(request),
        "credential_reference_replayed": False,
        "credential_secret_replayed": False,
        "authorization_header_redacted": True,
        "live_http_dispatch_enabled": False,
        "injected_transport_required": True,
        "timeout_seconds": timeout,
        "streaming": False,
        "tool_use": False,
        "automatic_retries": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["request_hash"] = replay_hash(_request_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_live_http_request_artifact(
    *,
    transport_id: str,
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_PROVIDER_HTTP_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "transport_id": _require_string(transport_id, "transport_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "endpoint": OPENAI_RESPONSES_ENDPOINT,
        "http_request": {},
        "http_request_hash": replay_hash({}),
        "failure_reason": _redact_failure_reason(failure_reason),
        "credential_secret_replayed": False,
        "authorization_header_redacted": True,
        "live_http_dispatch_enabled": False,
        "injected_transport_required": True,
        "timeout_seconds": 0,
        "streaming": False,
        "tool_use": False,
        "automatic_retries": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["request_hash"] = replay_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_http_response_artifact(
    *,
    transport_id: str,
    request_artifact: dict[str, Any],
    raw_response: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_artifact, "live HTTP request")
    safe_response = _json_safe(raw_response)
    status_code = _extract_status_code(safe_response)
    if status_code == 429:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: rate limit")
    response_text = _extract_response_text(safe_response)
    _reject_authority_bearing_response(response_text)
    artifact = {
        "artifact_type": LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "transport_id": _require_string(transport_id, "transport_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "request_artifact_hash": request_artifact["artifact_hash"],
        "http_status_code": status_code,
        "response_status": "CAPTURED",
        "raw_response": safe_response,
        "raw_response_hash": replay_hash(safe_response),
        "response_text": response_text,
        "response_text_hash": replay_hash(response_text),
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "live_http_dispatch_performed": False,
        "injected_transport_executed": True,
        "real_openai_called": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["response_hash"] = replay_hash(_response_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_http_error_artifact(
    *,
    transport_id: str,
    request_artifact: dict[str, Any],
    error_classification: str,
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_artifact, "live HTTP request")
    artifact = {
        "artifact_type": LIVE_PROVIDER_HTTP_ERROR_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "transport_id": _require_string(transport_id, "transport_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "request_artifact_hash": request_artifact["artifact_hash"],
        "error_classification": _require_string(error_classification, "error_classification"),
        "failure_reason": _redact_failure_reason(failure_reason),
        "retry_attempted": False,
        "fallback_attempted": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "live_http_dispatch_performed": False,
        "final_status": STATUS_FAILED_CLOSED,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["error_hash"] = replay_hash(_error_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_http_transport_audit(
    *,
    transport_id: str,
    final_status: str,
    failure_reason: str,
    request_artifact: dict[str, Any],
    response_artifact: dict[str, Any] | None,
    error_artifact: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_artifact, "live HTTP request")
    if response_artifact is not None:
        _verify_artifact_hash(response_artifact, "live HTTP response")
    if error_artifact is not None:
        _verify_artifact_hash(error_artifact, "live HTTP error")
    status = _require_string(final_status, "final_status")
    if status not in {STATUS_COMPLETED, STATUS_FAILED_CLOSED}:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: invalid audit status")
    artifact = {
        "artifact_type": LIVE_PROVIDER_HTTP_TRANSPORT_AUDIT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "transport_id": _require_string(transport_id, "transport_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "final_status": status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "request_artifact_hash": request_artifact["artifact_hash"],
        "response_artifact_hash": response_artifact["artifact_hash"] if response_artifact is not None else None,
        "error_artifact_hash": error_artifact["artifact_hash"] if error_artifact is not None else None,
        "err_passive": True,
        "ocs_architecture_modified": False,
        "credential_boundary_preserved": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "live_http_dispatch_performed": False,
        "injected_transport_supported": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": status == STATUS_FAILED_CLOSED,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["audit_hash"] = replay_hash(_audit_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def reconstruct_live_provider_http_transport_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify HTTP transport replay evidence."""

    replay_path = Path(replay_dir)
    wrappers = _load_replay_sequence(replay_path, REPLAY_STEPS_SUCCESS)
    if not wrappers:
        wrappers = _load_replay_sequence(replay_path, REPLAY_STEPS_ERROR)
    if not wrappers:
        raise FailClosedRuntimeError("live provider HTTP transport replay is incomplete")
    request = wrappers[0]["artifact"]
    terminal = wrappers[1]["artifact"]
    audit = wrappers[2]["artifact"]
    if audit["request_artifact_hash"] != request["artifact_hash"]:
        raise FailClosedRuntimeError("live provider HTTP transport replay request reference mismatch")
    if terminal["artifact_type"] == LIVE_PROVIDER_HTTP_RESPONSE_ARTIFACT_V1:
        if audit["response_artifact_hash"] != terminal["artifact_hash"]:
            raise FailClosedRuntimeError("live provider HTTP transport replay response reference mismatch")
    elif audit["error_artifact_hash"] != terminal["artifact_hash"]:
        raise FailClosedRuntimeError("live provider HTTP transport replay error reference mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "transport_id": audit["transport_id"],
        "final_status": audit["final_status"],
        "failure_reason": audit["failure_reason"],
        "provider_id": audit["provider_id"],
        "live_http_dispatch_performed": audit["live_http_dispatch_performed"],
        "credential_secret_replayed": audit["credential_secret_replayed"],
        "provider_invoked": audit["provider_invoked"],
        "worker_invoked": audit["worker_invoked"],
        "governance_modified": audit["governance_modified"],
        "replay_modified": audit["replay_modified"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _invoke_injected_http_transport(*, transport: HttpTransport, request_artifact: dict[str, Any]) -> dict[str, Any]:
    request = deepcopy(request_artifact["http_request"])
    metadata = {
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "endpoint": request_artifact["endpoint"],
        "timeout_seconds": request_artifact["timeout_seconds"],
        "credential_secret_replayed": False,
        "authorization_header_redacted": True,
        "live_http_dispatch_performed": False,
    }
    try:
        response = transport(request, metadata)
    except TimeoutError as exc:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: timeout") from exc
    except Exception as exc:
        message = str(exc).lower()
        if "rate" in message and "limit" in message:
            raise FailClosedRuntimeError("live provider HTTP transport failed closed: rate limit") from exc
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: transport unavailable") from exc
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: malformed response")
    if response.get("real_openai_called") is True:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: live OpenAI call is prohibited")
    return deepcopy(response)


def _persist_sequence(replay_path: Path, steps: tuple[str, ...], artifacts: tuple[dict[str, Any], ...]) -> None:
    _ensure_replay_available(replay_path)
    for index, (step, artifact) in enumerate(zip(steps, artifacts, strict=True)):
        _verify_artifact_hash(artifact, step)
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": deepcopy(artifact),
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _load_replay_sequence(replay_path: Path, steps: tuple[str, ...]) -> list[dict[str, Any]]:
    wrappers = []
    for index, step in enumerate(steps):
        path = replay_path / f"{index:03d}_{step}.json"
        if not path.exists():
            return []
        wrapper = load_json(path)
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("live provider HTTP transport replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("live provider HTTP transport replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"live provider HTTP transport {step}")
        wrappers.append(wrapper)
    return wrappers


def _capture(
    *,
    transport_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    request_artifact: dict[str, Any],
    response_artifact: dict[str, Any] | None,
    error_artifact: dict[str, Any] | None,
    audit_artifact: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "transport_id": transport_id,
        "final_status": final_status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "http_request_artifact": deepcopy(request_artifact),
        "http_response_artifact": deepcopy(response_artifact),
        "http_error_artifact": deepcopy(error_artifact),
        "http_transport_audit_artifact": deepcopy(audit_artifact),
        "live_http_dispatch_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "fail_closed": final_status == STATUS_FAILED_CLOSED,
        "replay_visible": True,
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    for steps in (REPLAY_STEPS_SUCCESS, REPLAY_STEPS_ERROR):
        for index, step in enumerate(steps):
            if (replay_path / f"{index:03d}_{step}.json").exists():
                raise FailClosedRuntimeError("live provider HTTP transport failed closed: replay artifact already exists")


def _json_safe(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: malformed response")
    replay_hash(value)
    return deepcopy(value)


def _extract_status_code(raw_response: dict[str, Any]) -> int:
    value = raw_response.get("status_code", 200)
    if not isinstance(value, int) or value < 100 or value > 599:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: malformed response")
    return value


def _extract_response_text(raw_response: dict[str, Any]) -> str:
    for key in ("output_text", "text", "response_text"):
        if isinstance(raw_response.get(key), str) and raw_response[key].strip():
            return _bounded_text(raw_response[key])
    output = raw_response.get("output")
    if isinstance(output, list):
        parts = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if isinstance(content_item, dict) and isinstance(content_item.get("text"), str):
                    parts.append(content_item["text"])
        if parts:
            return _bounded_text("".join(parts))
    raise FailClosedRuntimeError("live provider HTTP transport failed closed: malformed response")


def _bounded_text(value: str) -> str:
    text = _require_string(value, "response_text")
    if len(text) > 8192:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: malformed response")
    return text


def _reject_authority_bearing_response(response_text: str) -> None:
    lowered = _require_string(response_text, "response_text").lower()
    if any(phrase in lowered for phrase in PROHIBITED_RESPONSE_PHRASES):
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: authority-bearing provider output")


def _classify_error(reason: str) -> str:
    lowered = reason.lower()
    if "timeout" in lowered:
        return ERROR_TIMEOUT
    if "rate limit" in lowered:
        return ERROR_RATE_LIMIT
    if "malformed response" in lowered:
        return ERROR_MALFORMED_RESPONSE
    if "authority-bearing" in lowered:
        return ERROR_AUTHORITY_BOUNDARY_VIOLATION
    if "credential" in lowered:
        return ERROR_CREDENTIAL_POLICY_INVALID if "policy" in lowered else ERROR_AUTHENTICATION_UNAVAILABLE
    return ERROR_TRANSPORT_UNAVAILABLE


def _normalize_timeout(value: int) -> int:
    if not isinstance(value, int) or value <= 0 or value > 60:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: invalid timeout")
    return value


def _redact_failure_reason(reason: str) -> str:
    text = reason if isinstance(reason, str) else ""
    if "sk-" in text.lower() or "bearer " in text.lower():
        return "live provider HTTP transport failed closed: secret material redacted"
    return text


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if "sk-" in serialized or "bearer " in serialized or "api_key" in serialized:
        raise FailClosedRuntimeError("live provider HTTP transport failed closed: credential secret replay detected")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact_hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("live provider HTTP transport replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("live provider HTTP transport replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"live provider HTTP transport failed closed: {field_name} is required")
    return value


def _request_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "transport_id": artifact["transport_id"],
        "provider_id": artifact["provider_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "err_selection_artifact_hash": artifact["err_selection_artifact_hash"],
        "canonical_contract_artifact_hash": artifact["canonical_contract_artifact_hash"],
        "http_request_hash": artifact["http_request_hash"],
        "timeout_seconds": artifact["timeout_seconds"],
    }


def _response_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "transport_id": artifact["transport_id"],
        "provider_id": artifact["provider_id"],
        "request_artifact_hash": artifact["request_artifact_hash"],
        "http_status_code": artifact["http_status_code"],
        "raw_response_hash": artifact["raw_response_hash"],
        "response_text_hash": artifact["response_text_hash"],
    }


def _error_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "transport_id": artifact["transport_id"],
        "provider_id": artifact["provider_id"],
        "request_artifact_hash": artifact["request_artifact_hash"],
        "error_classification": artifact["error_classification"],
        "failure_reason": artifact["failure_reason"],
    }


def _audit_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "transport_id": artifact["transport_id"],
        "provider_id": artifact["provider_id"],
        "final_status": artifact["final_status"],
        "request_artifact_hash": artifact["request_artifact_hash"],
        "response_artifact_hash": artifact["response_artifact_hash"],
        "error_artifact_hash": artifact["error_artifact_hash"],
        "live_http_dispatch_performed": artifact["live_http_dispatch_performed"],
    }
