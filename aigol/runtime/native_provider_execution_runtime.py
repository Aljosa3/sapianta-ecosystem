"""Governed native provider execution runtime.

This runtime performs one direct provider invocation after explicit human
approval evidence. Provider output is captured as untrusted response text and
normalized through a schema registry before replay binding.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib import error, request

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.execution_summary_runtime import (
    create_execution_summary,
    create_execution_summary_confirmation,
    verify_execution_summary_confirmation,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_NATIVE_PROVIDER_EXECUTION_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_NATIVE_PROVIDER_EXECUTION_RUNTIME_STATUS"

PROVIDER_OPENAI = "openai"
OPENAI_RESPONSES_SCHEMA = "openai.responses.v1"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.1"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_PROVIDER_RESPONSE_CHARS = 8192

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "credential_policy",
    "provider_request",
    "provider_response",
    "normalized_provider_response",
    "replay_binding",
)

ProviderTransport = Callable[[dict[str, Any], dict[str, Any]], Any]


def run_native_provider_execution(
    *,
    execution_id: str,
    human_request: str,
    provider_id: str = PROVIDER_OPENAI,
    model: str = DEFAULT_OPENAI_MODEL,
    created_at: str,
    replay_dir: str | Path,
    human_approved: bool,
    approved_by: str = "human.operator",
    credential_env: str = "AIGOL_OPENAI_API_KEY",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    transport: ProviderTransport | None = None,
    execution_summary_artifact: dict[str, Any] | None = None,
    human_confirmation_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Invoke a provider once and persist replay-visible evidence."""

    replay_path = Path(replay_dir)
    try:
        approval = _approval_evidence(
            execution_id=execution_id,
            human_approved=human_approved,
            approved_by=approved_by,
            created_at=created_at,
        )
        if approval["human_approved"] is not True:
            raise FailClosedRuntimeError("explicit human approval is required before provider invocation")
        summary = execution_summary_artifact or create_execution_summary(
            summary_id=f"{execution_id}:EXECUTION-SUMMARY",
            original_request=human_request,
            interpreted_intent={
                "intent_type": "NATIVE_PROVIDER_EXECUTION",
                "provider_id": provider_id,
                "model": model,
            },
            selected_route={"route_type": "NATIVE_PROVIDER_EXECUTION_RUNTIME"},
            planned_actions=[{"action": "INVOKE_PROVIDER_ONCE", "provider_id": provider_id}],
            expected_outputs=[{"artifact_type": "PROVIDER_RESPONSE_ARTIFACT", "status": "PROVIDER_RESPONSE_CAPTURED"}],
            assumptions=["The human request is approved for one bounded provider invocation."],
            constraints=[
                "Provider output is non-authoritative.",
                "Provider invocation does not grant governance, implementation, or replay authority.",
            ],
            risk_classification={
                "risk_level": "BOUNDED_PROVIDER_INVOCATION",
                "reason": "External provider invocation is execution-capable.",
            },
            execution_scope={
                "provider_id": provider_id,
                "model": model,
                "single_invocation": True,
                "automatic_retries": False,
            },
            replay_references=[execution_id],
            created_by=approved_by,
            created_at=created_at,
        )
        confirmation = human_confirmation_artifact or create_execution_summary_confirmation(
            confirmation_id=f"{execution_id}:EXECUTION-SUMMARY-CONFIRMATION",
            execution_summary_artifact=summary,
            decision="APPROVE",
            confirmed_by=approved_by,
            confirmed_at=created_at,
        )
        verify_execution_summary_confirmation(summary, confirmation)
        credential_policy = load_governed_provider_credentials(
            provider_id=provider_id,
            credential_env=credential_env,
        )
        _persist_step(replay_path, 0, "credential_policy", credential_policy)
        provider_request = create_provider_request(
            execution_id=execution_id,
            human_request=human_request,
            provider_id=provider_id,
            model=model,
            created_at=created_at,
            credential_policy=credential_policy,
            approval_evidence=approval,
            execution_summary_artifact=summary,
            human_confirmation_artifact=confirmation,
            timeout_seconds=timeout_seconds,
        )
        _persist_step(replay_path, 1, "provider_request", provider_request)
        provider_response = invoke_provider_once(
            provider_request=provider_request,
            credential_secret=credential_policy["_credential_secret"],
            transport=transport,
        )
        _persist_step(replay_path, 2, "provider_response", provider_response)
        normalized = normalize_provider_response(
            provider_response=provider_response,
            provider_request=provider_request,
        )
        _persist_step(replay_path, 3, "normalized_provider_response", normalized)
        replay_binding = create_replay_binding(
            credential_policy=credential_policy,
            provider_request=provider_request,
            provider_response=provider_response,
            normalized_response=normalized,
        )
        _persist_step(replay_path, 4, "replay_binding", replay_binding)
        return _capture(
            final_status=STATUS_COMPLETED,
            credential_policy=credential_policy,
            provider_request=provider_request,
            provider_response=provider_response,
            normalized_response=normalized,
            replay_binding=replay_binding,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "native provider execution failed closed"
        failure = _failure_artifact(
            execution_id=execution_id if _is_nonempty_string(execution_id) else "NATIVE-PROVIDER-EXECUTION-INVALID",
            provider_id=provider_id if _is_nonempty_string(provider_id) else "unknown",
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            credential_policy=None,
            provider_request=None,
            provider_response=None,
            normalized_response=None,
            replay_binding=failure,
            failure_reason=failure_reason,
        )


def load_governed_provider_credentials(*, provider_id: str, credential_env: str) -> dict[str, Any]:
    provider = _normalize_provider_id(provider_id)
    env_name = _require_string(credential_env, "credential_env")
    allowed = _credential_env_registry(provider)
    if env_name not in allowed:
        raise FailClosedRuntimeError("credential_env is not registered for provider")
    secret = os.environ.get(env_name)
    if not _is_nonempty_string(secret):
        raise FailClosedRuntimeError(f"{env_name} is required")
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": "CREDENTIAL_POLICY_LOADED",
        "provider_id": provider,
        "credential_env": env_name,
        "credential_loaded": True,
        "credential_captured": False,
        "credential_hash_captured": False,
        "credential_source_registered": True,
        "human_approval_required": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    artifact["_credential_secret"] = secret.strip()
    return artifact


def create_provider_request(
    *,
    execution_id: str,
    human_request: str,
    provider_id: str,
    model: str,
    created_at: str,
    credential_policy: dict[str, Any],
    approval_evidence: dict[str, Any],
    execution_summary_artifact: dict[str, Any],
    human_confirmation_artifact: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    _verify_artifact_hash(_public_artifact(credential_policy))
    provider = _normalize_provider_id(provider_id)
    schema_id = _schema_for_provider(provider)
    timeout = _normalize_timeout(timeout_seconds)
    request_text = _require_string(human_request, "human_request")
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": "PROVIDER_REQUEST_CREATED",
        "execution_id": _require_string(execution_id, "execution_id"),
        "provider_id": provider,
        "provider_schema_id": schema_id,
        "provider_identity": {
            "provider_id": provider,
            "provider_kind": "external_llm",
            "model": _require_string(model, "model"),
            "endpoint": OPENAI_RESPONSES_ENDPOINT if provider == PROVIDER_OPENAI else "",
        },
        "request": {
            "input": request_text,
            "input_hash": replay_hash(request_text),
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
            "timeout_seconds": timeout,
        },
        "credential_policy_hash": credential_policy["artifact_hash"],
        "approval_evidence": approval_evidence,
        "execution_summary_reference": execution_summary_artifact["summary_id"],
        "execution_summary_hash": execution_summary_artifact["artifact_hash"],
        "human_confirmation_reference": human_confirmation_artifact["confirmation_id"],
        "human_confirmation_hash": human_confirmation_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
        "lineage_refs": {
            "human_request_hash": replay_hash(request_text),
            "credential_policy_hash": credential_policy["artifact_hash"],
            "approval_evidence_hash": replay_hash(approval_evidence),
            "execution_summary_hash": execution_summary_artifact["artifact_hash"],
            "human_confirmation_hash": human_confirmation_artifact["artifact_hash"],
        },
        "provider_authority": False,
        "implementation_authority": False,
        "governance_authority": False,
        "replay_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def invoke_provider_once(
    *,
    provider_request: dict[str, Any],
    credential_secret: str,
    transport: ProviderTransport | None = None,
) -> dict[str, Any]:
    _verify_artifact_hash(provider_request)
    if not _is_nonempty_string(credential_secret):
        raise FailClosedRuntimeError("provider credential secret is unavailable")
    provider_id = provider_request["provider_id"]
    if provider_id != PROVIDER_OPENAI:
        raise FailClosedRuntimeError("provider is not supported by native provider execution runtime")
    payload = {
        "model": provider_request["provider_identity"]["model"],
        "input": provider_request["request"]["input"],
        "stream": False,
    }
    metadata = {
        "provider_id": provider_id,
        "endpoint": provider_request["provider_identity"]["endpoint"],
        "timeout_seconds": provider_request["request"]["timeout_seconds"],
        "api_key": credential_secret,
    }
    raw_response = transport(deepcopy(payload), deepcopy(metadata)) if transport else _openai_http_transport(payload, metadata)
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": "PROVIDER_RESPONSE_CAPTURED",
        "execution_id": provider_request["execution_id"],
        "provider_id": provider_id,
        "provider_schema_id": provider_request["provider_schema_id"],
        "provider_request_hash": provider_request["artifact_hash"],
        "raw_response": _json_safe(raw_response),
        "raw_response_hash": replay_hash(_json_safe(raw_response)),
        "provider_invoked": True,
        "single_invocation": True,
        "automatic_retries": False,
        "streaming": False,
        "tool_use": False,
        "function_calling": False,
        "provider_authority": False,
        "implementation_authority": False,
        "governance_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def normalize_provider_response(*, provider_response: dict[str, Any], provider_request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(provider_response)
    _verify_artifact_hash(provider_request)
    schema_id = provider_response.get("provider_schema_id")
    extractor = _schema_registry().get(schema_id)
    if extractor is None:
        raise FailClosedRuntimeError("provider response schema is not registered")
    response_text = extractor(provider_response["raw_response"])
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": "PROVIDER_RESPONSE_NORMALIZED",
        "execution_id": provider_response["execution_id"],
        "provider_id": provider_response["provider_id"],
        "provider_schema_id": schema_id,
        "provider_request_hash": provider_request["artifact_hash"],
        "provider_response_hash": provider_response["artifact_hash"],
        "normalized_response": {
            "response_text": response_text,
            "response_text_hash": replay_hash(response_text),
            "status": "NORMALIZED",
            "untrusted_provider_output": True,
        },
        "schema_registry": {
            "registry_id": "AIGOL_PROVIDER_RESPONSE_SCHEMA_REGISTRY_V1",
            "registered_schema_ids": sorted(_schema_registry()),
            "selected_schema_id": schema_id,
        },
        "provider_authority": False,
        "implementation_authority": False,
        "governance_authority": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_replay_binding(
    *,
    credential_policy: dict[str, Any],
    provider_request: dict[str, Any],
    provider_response: dict[str, Any],
    normalized_response: dict[str, Any],
) -> dict[str, Any]:
    public_credential_policy = _public_artifact(credential_policy)
    for artifact in (public_credential_policy, provider_request, provider_response, normalized_response):
        _verify_artifact_hash(artifact)
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": FINAL_CLASSIFICATION,
        "final_status": STATUS_COMPLETED,
        "execution_id": provider_request["execution_id"],
        "provider_invoked": True,
        "provider_id": provider_request["provider_id"],
        "provider_identity": provider_request["provider_identity"],
        "provider_metadata": {
            "provider_schema_id": provider_request["provider_schema_id"],
            "model": provider_request["provider_identity"]["model"],
            "endpoint": provider_request["provider_identity"]["endpoint"],
            "credential_env": public_credential_policy["credential_env"],
            "credential_captured": False,
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
        },
        "lineage_refs": {
            "credential_policy_hash": public_credential_policy["artifact_hash"],
            "provider_request_hash": provider_request["artifact_hash"],
            "provider_response_hash": provider_response["artifact_hash"],
            "normalized_provider_response_hash": normalized_response["artifact_hash"],
            "human_request_hash": provider_request["lineage_refs"]["human_request_hash"],
        },
        "governance_preservation": {
            "human_approval_boundary_preserved": True,
            "implementation_authority_chain_preserved": True,
            "fail_closed_behavior_preserved": True,
            "replay_reconstruction_preserved": True,
            "provider_output_authoritative": False,
            "automatic_implementation": False,
        },
        "human_request_to_provider_result_to_replay": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_native_provider_execution_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("native provider execution replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("native provider execution artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    final = wrappers[-1]["artifact"]
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "final_status": final.get("final_status"),
        "execution_id": final.get("execution_id"),
        "provider_invoked": final.get("provider_invoked") is True,
        "provider_id": final.get("provider_id"),
        "lineage_refs": final.get("lineage_refs", {}),
        "replay_artifact_count": len(wrappers),
        "replay_visible": True,
        "append_only_valid": True,
        "human_request_to_provider_result_to_replay": final.get("human_request_to_provider_result_to_replay") is True,
        "governance_preservation": final.get("governance_preservation", {}),
        "replay_hash": replay_hash(wrappers),
    }


def render_native_provider_execution_summary(result: dict[str, Any]) -> str:
    binding = result.get("replay_binding") or {}
    return "\n".join(
        [
            "AIGOL NATIVE PROVIDER EXECUTION",
            f"status: {result.get('final_status')}",
            f"classification: {FINAL_CLASSIFICATION}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"provider_id: {result.get('provider_id')}",
            f"execution_id: {result.get('execution_id')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"replay_binding_hash: {binding.get('artifact_hash')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def _openai_http_transport(payload: dict[str, Any], metadata: dict[str, Any]) -> Any:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    http_request = request.Request(
        metadata["endpoint"],
        data=body,
        headers={
            "Authorization": f"Bearer {metadata['api_key']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=metadata["timeout_seconds"]) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise FailClosedRuntimeError("provider HTTP failure") from exc
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("provider unavailable") from exc


def _extract_openai_response_text(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return _bounded_response_text(raw_response)
    if not isinstance(raw_response, dict):
        raise FailClosedRuntimeError("provider response is malformed")
    for key in ("output_text", "text", "response_text"):
        if isinstance(raw_response.get(key), str):
            return _bounded_response_text(raw_response[key])
    output = raw_response.get("output")
    if isinstance(output, list):
        parts: list[str] = []
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
            return _bounded_response_text("".join(parts))
    raise FailClosedRuntimeError("provider response did not include bounded response text")


def _schema_registry() -> dict[str, Callable[[Any], str]]:
    return {OPENAI_RESPONSES_SCHEMA: _extract_openai_response_text}


def _schema_for_provider(provider_id: str) -> str:
    if provider_id == PROVIDER_OPENAI:
        return OPENAI_RESPONSES_SCHEMA
    raise FailClosedRuntimeError("provider is not registered")


def _credential_env_registry(provider_id: str) -> tuple[str, ...]:
    if provider_id == PROVIDER_OPENAI:
        return ("AIGOL_OPENAI_API_KEY", "OPENAI_API_KEY")
    raise FailClosedRuntimeError("provider is not registered")


def _approval_evidence(*, execution_id: str, human_approved: bool, approved_by: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "execution_id": _require_string(execution_id, "execution_id"),
        "human_approved": human_approved is True,
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(created_at, "created_at"),
        "approval_boundary": "HUMAN_APPROVAL_REQUIRED_BEFORE_PROVIDER_INVOCATION",
    }
    artifact["approval_evidence_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(*, execution_id: str, provider_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "milestone_id": MILESTONE_ID,
        "state": FINAL_CLASSIFICATION,
        "final_status": STATUS_FAILED_CLOSED,
        "execution_id": execution_id,
        "provider_id": provider_id,
        "provider_invoked": False,
        "created_at": created_at,
        "failure_reason": failure_reason,
        "governance_preservation": {
            "human_approval_boundary_preserved": True,
            "implementation_authority_chain_preserved": True,
            "fail_closed_behavior_preserved": True,
            "replay_reconstruction_preserved": True,
            "provider_output_authoritative": False,
            "automatic_implementation": False,
        },
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    credential_policy: dict[str, Any] | None,
    provider_request: dict[str, Any] | None,
    provider_response: dict[str, Any] | None,
    normalized_response: dict[str, Any] | None,
    replay_binding: dict[str, Any],
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol provider invoke",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "final_status": final_status,
        "execution_id": replay_binding.get("execution_id"),
        "provider_id": replay_binding.get("provider_id"),
        "provider_invoked": replay_binding.get("provider_invoked") is True,
        "credential_policy": _public_artifact(credential_policy) if credential_policy else None,
        "provider_request": deepcopy(provider_request),
        "provider_response": deepcopy(provider_response),
        "normalized_provider_response": deepcopy(normalized_response),
        "replay_binding": deepcopy(replay_binding),
        "replay_reference": "",
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["native_provider_execution_hash"] = replay_hash(result)
    return result


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("native provider execution replay step ordering mismatch")
    public_artifact = _public_artifact(artifact)
    _verify_artifact_hash(public_artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": public_artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            artifact = deepcopy(failure)
            artifact["failed_step"] = step
            artifact.pop("artifact_hash", None)
            artifact["artifact_hash"] = replay_hash(artifact)
            _persist_step(replay_dir, index, step, artifact)


def _public_artifact(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if artifact is None:
        return {}
    public = deepcopy(artifact)
    public.pop("_credential_secret", None)
    return public


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("native provider execution artifact must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("native provider execution artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("native provider execution artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("native provider execution replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("native provider execution replay hash mismatch")


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("provider response must be JSON serializable") from exc
    return deepcopy(value)


def _bounded_response_text(value: str) -> str:
    text = " ".join(_require_string(value, "provider_response_text").split())
    if len(text) > MAX_PROVIDER_RESPONSE_CHARS:
        raise FailClosedRuntimeError("provider response exceeds bounded size")
    return text


def _normalize_timeout(value: int) -> int:
    if not isinstance(value, int) or value < 1 or value > 60:
        raise FailClosedRuntimeError("timeout_seconds is outside the bounded range")
    return value


def _normalize_provider_id(value: str) -> str:
    provider_id = _require_string(value, "provider_id").lower()
    if provider_id != PROVIDER_OPENAI:
        raise FailClosedRuntimeError("provider is not registered")
    return provider_id


def _require_string(value: Any, field_name: str) -> str:
    if not _is_nonempty_string(value):
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
