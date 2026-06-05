"""Single-provider LLM cognition bridge for OCS.

This runtime creates a governed bridge from an OCS context assembly artifact to
one approved cognition provider. It captures request/response replay evidence
but does not create OCS cognition artifacts, comparisons, continuity, memory,
clarification, approvals, workers, execution, governance mutation, or replay
mutation.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable
from urllib import error, request

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_SINGLE_PROVIDER_COGNITION_RUNTIME"

LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1 = "LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1"
LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1 = "LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1"
LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1 = "LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1"

PROVIDER_OPENAI = "openai"
COGNITION_PROVIDER_ROLE = "COGNITION_PROVIDER"
OPENAI_RESPONSES_SCHEMA = "openai.responses.v1"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.1"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_PROVIDER_RESPONSE_CHARS = 8192

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "llm_cognition_provider_request",
    "llm_cognition_provider_response",
    "llm_cognition_provider_replay_binding",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

PROHIBITED_RESPONSE_PHRASES = (
    "i approve",
    "approved for execution",
    "approval granted",
    "i authorize",
    "authorized for execution",
    "execution authorized",
    "implementation authorized",
    "invoke worker",
    "worker invocation authorized",
    "create the domain",
    "domain creation authorized",
    "governance mutation",
    "mutate governance",
    "replay mutation",
    "mutate replay",
)

ProviderTransport = Callable[[dict[str, Any], dict[str, Any]], Any]


def run_llm_cognition_provider_runtime(
    *,
    cognition_provider_request_id: str,
    human_request: str,
    ocs_context_artifact: dict[str, Any],
    provider_contract: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    human_approved: bool,
    approved_by: str = "human.operator",
    provider_id: str = PROVIDER_OPENAI,
    model: str = DEFAULT_OPENAI_MODEL,
    credential_env: str = "AIGOL_OPENAI_API_KEY",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    transport: ProviderTransport | None = None,
) -> dict[str, Any]:
    """Invoke one approved cognition provider and persist replay evidence."""

    replay_path = Path(replay_dir)
    request_artifact: dict[str, Any] | None = None
    response_artifact: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        context = _validate_ocs_context_artifact(ocs_context_artifact)
        contract = _validate_provider_contract(provider_contract, provider_id=provider_id)
        approval_evidence = _approval_evidence(
            request_id=cognition_provider_request_id,
            human_approved=human_approved,
            approved_by=approved_by,
            created_at=created_at,
        )
        if approval_evidence["human_approved"] is not True:
            raise FailClosedRuntimeError("explicit human approval is required before cognition provider invocation")
        credential_policy = _load_governed_provider_credentials(provider_id=provider_id, credential_env=credential_env)
        request_artifact = create_llm_cognition_provider_request(
            cognition_provider_request_id=cognition_provider_request_id,
            human_request=human_request,
            ocs_context_artifact=context,
            provider_contract=contract,
            provider_id=provider_id,
            model=model,
            created_at=created_at,
            approval_evidence=approval_evidence,
            credential_policy=credential_policy,
            timeout_seconds=timeout_seconds,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], request_artifact)
        response_artifact = invoke_approved_cognition_provider(
            request_artifact=request_artifact,
            credential_secret=credential_policy["_credential_secret"],
            transport=transport,
        )
        _persist_step(replay_path, 1, REPLAY_STEPS[1], response_artifact)
        replay_binding = create_llm_cognition_provider_replay_binding(
            request_artifact=request_artifact,
            response_artifact=response_artifact,
        )
        _persist_step(replay_path, 2, REPLAY_STEPS[2], replay_binding)
        return _capture(
            final_status=STATUS_COMPLETED,
            request_artifact=request_artifact,
            response_artifact=response_artifact,
            replay_binding=replay_binding,
            replay_path=replay_path,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "LLM cognition provider runtime failed closed"
        failure = _failure_artifact(
            cognition_provider_request_id=(
                cognition_provider_request_id
                if _is_nonempty_string(cognition_provider_request_id)
                else "LLM-COGNITION-PROVIDER-INVALID"
            ),
            provider_id=provider_id if _is_nonempty_string(provider_id) else "unknown",
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
            request_artifact=request_artifact,
            response_artifact=response_artifact,
        )
        _persist_failure_sequence(replay_path, failure)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            request_artifact=request_artifact,
            response_artifact=response_artifact,
            replay_binding=failure,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )


def create_default_openai_cognition_provider_contract(*, created_at: str = "1970-01-01T00:00:00Z") -> dict[str, Any]:
    """Create a replay-hashable approved single-provider contract for tests and callers."""

    artifact = {
        "artifact_type": "LLM_COGNITION_PROVIDER_CONTRACT_REGISTRATION_V1",
        "contract_reference": "AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1",
        "provider_id": PROVIDER_OPENAI,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_approved": True,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "provider_identity": {
            "provider_id": PROVIDER_OPENAI,
            "provider_kind": "external_llm",
            "endpoint": OPENAI_RESPONSES_ENDPOINT,
        },
        "authority_model": deepcopy(AUTHORITY_FLAGS),
        "allowed_outputs": [
            "findings",
            "assumptions",
            "alternatives",
            "risks",
            "uncertainties",
            "confidence statements",
            "clarification candidates",
        ],
        "prohibited_outputs": [
            "approvals",
            "authorizations",
            "governance mutations",
            "replay mutations",
            "worker invocation",
            "execution authorization",
            "domain creation authorization",
            "implementation authorization",
        ],
        "single_provider_only": True,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_llm_cognition_provider_request(
    *,
    cognition_provider_request_id: str,
    human_request: str,
    ocs_context_artifact: dict[str, Any],
    provider_contract: dict[str, Any],
    provider_id: str,
    model: str,
    created_at: str,
    approval_evidence: dict[str, Any],
    credential_policy: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    context = _validate_ocs_context_artifact(ocs_context_artifact)
    contract = _validate_provider_contract(provider_contract, provider_id=provider_id)
    _verify_artifact_hash(_public_artifact(credential_policy), "credential policy")
    provider = _normalize_provider_id(provider_id)
    request_text = _require_string(human_request, "human_request")
    timeout = _normalize_timeout(timeout_seconds)
    prompt = _provider_prompt(human_request=request_text, context=context)
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "contract_reference": "AIGOL_LLM_COGNITION_PROVIDER_CONTRACT_V1",
        "authority_policy_reference": "AIGOL_LLM_COGNITION_PROVIDER_AUTHORITY_POLICY_V1",
        "necessity_policy_reference": "AIGOL_LLM_COGNITION_PROVIDER_NECESSITY_POLICY_V1",
        "cognition_provider_request_id": _require_string(
            cognition_provider_request_id, "cognition_provider_request_id"
        ),
        "provider_id": provider,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_schema_id": contract["provider_schema_id"],
        "provider_identity": {
            "provider_id": provider,
            "provider_kind": "external_llm",
            "model": _require_string(model, "model"),
            "endpoint": contract["provider_identity"]["endpoint"],
        },
        "request": {
            "human_request": request_text,
            "human_request_hash": replay_hash(request_text),
            "input": prompt,
            "input_hash": replay_hash(prompt),
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
            "timeout_seconds": timeout,
        },
        "ocs_context_reference": {
            "context_assembly_id": context["context_assembly_id"],
            "context_hash": context["context_hash"],
            "context_artifact_hash": context["artifact_hash"],
            "context_status": context["context_status"],
        },
        "provider_contract_hash": contract["artifact_hash"],
        "credential_policy_hash": credential_policy["artifact_hash"],
        "approval_evidence": approval_evidence,
        "lineage_refs": {
            "human_request_hash": replay_hash(request_text),
            "ocs_context_hash": context["context_hash"],
            "ocs_context_artifact_hash": context["artifact_hash"],
            "provider_contract_hash": contract["artifact_hash"],
            "credential_policy_hash": credential_policy["artifact_hash"],
            "approval_evidence_hash": approval_evidence["approval_evidence_hash"],
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["request_hash"] = _compute_request_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def invoke_approved_cognition_provider(
    *,
    request_artifact: dict[str, Any],
    credential_secret: str,
    transport: ProviderTransport | None = None,
) -> dict[str, Any]:
    _validate_request_artifact(request_artifact)
    if not _is_nonempty_string(credential_secret):
        raise FailClosedRuntimeError("provider credential secret is unavailable")
    provider_id = request_artifact["provider_id"]
    if provider_id != PROVIDER_OPENAI:
        raise FailClosedRuntimeError("provider is not registered for single-provider cognition runtime")
    payload = {
        "model": request_artifact["provider_identity"]["model"],
        "input": request_artifact["request"]["input"],
        "stream": False,
    }
    metadata = {
        "provider_id": provider_id,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "endpoint": request_artifact["provider_identity"]["endpoint"],
        "timeout_seconds": request_artifact["request"]["timeout_seconds"],
        "api_key": credential_secret,
    }
    raw_response = transport(deepcopy(payload), deepcopy(metadata)) if transport else _openai_http_transport(payload, metadata)
    safe_response = _json_safe(raw_response)
    response_text = _extract_openai_response_text(safe_response)
    _reject_authority_bearing_response(response_text)
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "cognition_provider_request_id": request_artifact["cognition_provider_request_id"],
        "provider_id": provider_id,
        "provider_role": COGNITION_PROVIDER_ROLE,
        "provider_schema_id": request_artifact["provider_schema_id"],
        "provider_identity": deepcopy(request_artifact["provider_identity"]),
        "provider_metadata": {
            "provider_schema_id": request_artifact["provider_schema_id"],
            "model": request_artifact["provider_identity"]["model"],
            "endpoint": request_artifact["provider_identity"]["endpoint"],
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "automatic_retries": False,
            "single_provider_only": True,
        },
        "provider_request_hash": request_artifact["artifact_hash"],
        "request_hash": request_artifact["request_hash"],
        "ocs_context_hash": request_artifact["ocs_context_reference"]["context_hash"],
        "raw_response": safe_response,
        "raw_response_hash": replay_hash(safe_response),
        "response_text": response_text,
        "response_text_hash": replay_hash(response_text),
        "response_status": "CAPTURED",
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "lineage_refs": {
            "llm_cognition_provider_request_hash": request_artifact["artifact_hash"],
            "request_hash": request_artifact["request_hash"],
            "ocs_context_hash": request_artifact["ocs_context_reference"]["context_hash"],
            "ocs_context_artifact_hash": request_artifact["ocs_context_reference"]["context_artifact_hash"],
            "provider_contract_hash": request_artifact["provider_contract_hash"],
            "approval_evidence_hash": request_artifact["approval_evidence"]["approval_evidence_hash"],
        },
        "replay_visible": True,
        "provider_invoked": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["response_hash"] = _compute_response_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_llm_cognition_provider_replay_binding(
    *, request_artifact: dict[str, Any], response_artifact: dict[str, Any]
) -> dict[str, Any]:
    _validate_request_artifact(request_artifact)
    _validate_response_artifact(response_artifact)
    if response_artifact["provider_request_hash"] != request_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("LLM cognition provider response request hash mismatch")
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": STATUS_COMPLETED,
        "cognition_provider_request_id": request_artifact["cognition_provider_request_id"],
        "provider_invoked": True,
        "single_provider_only": True,
        "provider_id": request_artifact["provider_id"],
        "provider_identity": deepcopy(request_artifact["provider_identity"]),
        "provider_metadata": deepcopy(response_artifact["provider_metadata"]),
        "lineage_refs": {
            "human_request_hash": request_artifact["lineage_refs"]["human_request_hash"],
            "ocs_context_hash": request_artifact["ocs_context_reference"]["context_hash"],
            "ocs_context_artifact_hash": request_artifact["ocs_context_reference"]["context_artifact_hash"],
            "request_hash": request_artifact["request_hash"],
            "response_hash": response_artifact["response_hash"],
            "llm_cognition_provider_request_artifact_hash": request_artifact["artifact_hash"],
            "llm_cognition_provider_response_artifact_hash": response_artifact["artifact_hash"],
            "provider_contract_hash": request_artifact["provider_contract_hash"],
            "approval_evidence_hash": request_artifact["approval_evidence"]["approval_evidence_hash"],
        },
        "governance_preservation": {
            "constitutional_invariant": [
                "LLM proposes.",
                "AiGOL governs.",
                "Worker executes.",
                "Replay records.",
            ],
            "provider_output_authoritative": False,
            "human_approval_boundary_preserved": True,
            "fail_closed_behavior_preserved": True,
            "replay_reconstruction_preserved": True,
            "no_execution": True,
            "no_worker_invocation": True,
            "no_approval_creation": True,
            "no_governance_mutation": True,
            "no_replay_mutation": True,
            "no_cognition_artifact_runtime": True,
            "no_multi_provider_cognition": True,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "human_request_to_ocs_context_to_cognition_provider_to_response_to_replay": True,
        "replay_visible": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_llm_cognition_provider_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("LLM cognition provider replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("LLM cognition provider replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay artifact")
        wrappers.append(wrapper)
    request_artifact = wrappers[0]["artifact"]
    response_artifact = wrappers[1]["artifact"]
    binding = wrappers[2]["artifact"]
    if response_artifact.get("provider_request_hash") != request_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("LLM cognition provider replay response request hash mismatch")
    if binding["lineage_refs"]["llm_cognition_provider_request_artifact_hash"] != request_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("LLM cognition provider replay request lineage mismatch")
    if binding["lineage_refs"]["llm_cognition_provider_response_artifact_hash"] != response_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("LLM cognition provider replay response lineage mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": binding.get("classification"),
        "final_status": binding.get("final_status"),
        "cognition_provider_request_id": binding.get("cognition_provider_request_id"),
        "provider_invoked": binding.get("provider_invoked") is True,
        "provider_id": binding.get("provider_id"),
        "provider_identity": deepcopy(binding.get("provider_identity")),
        "provider_metadata": deepcopy(binding.get("provider_metadata")),
        "lineage_refs": deepcopy(binding.get("lineage_refs", {})),
        "authority_flags": deepcopy(binding.get("authority_flags", {})),
        "replay_artifact_count": len(wrappers),
        "replay_visible": True,
        "append_only_valid": True,
        "human_request_to_ocs_context_to_cognition_provider_to_response_to_replay": (
            binding.get("human_request_to_ocs_context_to_cognition_provider_to_response_to_replay") is True
        ),
        "governance_preservation": deepcopy(binding.get("governance_preservation", {})),
        "replay_hash": replay_hash(wrappers),
    }


def render_llm_cognition_provider_summary(result: dict[str, Any]) -> str:
    binding = result.get("replay_binding") or {}
    return "\n".join(
        [
            "AIGOL LLM COGNITION PROVIDER RUNTIME",
            f"status: {result.get('final_status')}",
            f"classification: {result.get('classification')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"provider_id: {result.get('provider_id')}",
            f"cognition_provider_request_id: {result.get('cognition_provider_request_id')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"replay_binding_hash: {binding.get('artifact_hash')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def _provider_prompt(*, human_request: str, context: dict[str, Any]) -> str:
    prompt = {
        "instruction": (
            "You are a non-authoritative AiGOL COGNITION_PROVIDER. "
            "Analyze, infer, compare, explain, identify uncertainty, and identify missing information only. "
            "Do not approve, authorize, execute, invoke workers, create domains, mutate governance, or mutate replay."
        ),
        "allowed_outputs": [
            "findings",
            "assumptions",
            "alternatives",
            "risks",
            "uncertainties",
            "confidence statements",
            "clarification candidates",
        ],
        "human_request": human_request,
        "ocs_context_reference": {
            "context_assembly_id": context["context_assembly_id"],
            "context_hash": context["context_hash"],
            "context_sections": context["context_sections"],
            "known_gaps": context["known_gaps"],
        },
    }
    return json.dumps(prompt, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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
        raise FailClosedRuntimeError("cognition provider HTTP failure") from exc
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("cognition provider unavailable") from exc


def _extract_openai_response_text(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return _bounded_response_text(raw_response)
    if not isinstance(raw_response, dict):
        raise FailClosedRuntimeError("cognition provider response is malformed")
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
    raise FailClosedRuntimeError("cognition provider response did not include bounded response text")


def _validate_ocs_context_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS context artifact must be a JSON object")
    if artifact.get("artifact_type") != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid OCS context assembly artifact")
    if artifact.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS context must be assembled before cognition provider invocation")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS context artifact is not replay-visible")
    _verify_artifact_hash(artifact, "OCS context artifact")
    _reject_governance_mutating_flags(artifact)
    return deepcopy(artifact)


def _validate_provider_contract(contract: dict[str, Any], *, provider_id: str) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("provider contract is missing")
    _verify_artifact_hash(contract, "provider contract")
    provider = _normalize_provider_id(provider_id)
    if contract.get("provider_id") != provider:
        raise FailClosedRuntimeError("provider contract provider mismatch")
    if contract.get("provider_role") != COGNITION_PROVIDER_ROLE:
        raise FailClosedRuntimeError("provider role is not COGNITION_PROVIDER")
    if contract.get("provider_approved") is not True:
        raise FailClosedRuntimeError("provider is not approved")
    if contract.get("single_provider_only") is not True:
        raise FailClosedRuntimeError("provider contract must preserve single-provider scope")
    if contract.get("provider_schema_id") != OPENAI_RESPONSES_SCHEMA:
        raise FailClosedRuntimeError("provider response schema is not registered for cognition provider")
    identity = contract.get("provider_identity")
    if not isinstance(identity, dict) or identity.get("endpoint") != OPENAI_RESPONSES_ENDPOINT:
        raise FailClosedRuntimeError("provider identity is not registered")
    _validate_authority_flags(contract.get("authority_model"))
    if contract.get("replay_visible") is not True:
        raise FailClosedRuntimeError("provider contract is not replay-visible")
    return deepcopy(contract)


def _validate_request_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition provider request artifact")
    _verify_artifact_hash(artifact, "LLM cognition provider request")
    if artifact.get("request_hash") != _compute_request_hash(artifact):
        raise FailClosedRuntimeError("LLM cognition provider request hash mismatch")
    _validate_authority_flags(artifact.get("authority_flags"))


def _validate_response_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition provider response artifact")
    _verify_artifact_hash(artifact, "LLM cognition provider response")
    if artifact.get("response_hash") != _compute_response_hash(artifact):
        raise FailClosedRuntimeError("LLM cognition provider response hash mismatch")
    _validate_authority_flags(artifact.get("authority_flags"))
    _reject_authority_bearing_response(artifact.get("response_text"))


def _validate_authority_flags(flags: Any) -> None:
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("provider authority flags are missing")
    for name, expected in AUTHORITY_FLAGS.items():
        if flags.get(name) is not expected:
            raise FailClosedRuntimeError(f"provider authority flag must be false: {name}")


def _reject_governance_mutating_flags(artifact: dict[str, Any]) -> None:
    prohibited = (
        "approval_created",
        "execution_requested",
        "dispatch_requested",
        "worker_invoked",
        "domain_created",
        "governance_modified",
        "replay_modified",
    )
    for flag in prohibited:
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS context carries prohibited authority flag: {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        for flag, value in flags.items():
            if value is True:
                raise FailClosedRuntimeError(f"OCS context carries prohibited authority flag: {flag}")


def _reject_authority_bearing_response(response_text: Any) -> None:
    text = _require_string(response_text, "response_text").lower()
    for phrase in PROHIBITED_RESPONSE_PHRASES:
        if phrase in text:
            raise FailClosedRuntimeError("cognition provider response exceeds authority boundary")


def _load_governed_provider_credentials(*, provider_id: str, credential_env: str) -> dict[str, Any]:
    provider = _normalize_provider_id(provider_id)
    env_name = _require_string(credential_env, "credential_env")
    allowed = _credential_env_registry(provider)
    if env_name not in allowed:
        raise FailClosedRuntimeError("credential_env is not registered for cognition provider")
    import os

    secret = os.environ.get(env_name)
    if not _is_nonempty_string(secret):
        raise FailClosedRuntimeError(f"{env_name} is required")
    artifact = {
        "artifact_type": "LLM_COGNITION_PROVIDER_CREDENTIAL_POLICY_V1",
        "runtime_version": MILESTONE_ID,
        "provider_id": provider,
        "credential_env": env_name,
        "credential_loaded": True,
        "credential_captured": False,
        "credential_hash_captured": False,
        "credential_source_registered": True,
        "human_approval_required": True,
        "provider_role": COGNITION_PROVIDER_ROLE,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    artifact["_credential_secret"] = secret.strip()
    return artifact


def _credential_env_registry(provider_id: str) -> tuple[str, ...]:
    if provider_id == PROVIDER_OPENAI:
        return ("AIGOL_OPENAI_API_KEY", "OPENAI_API_KEY")
    raise FailClosedRuntimeError("provider is not registered")


def _approval_evidence(*, request_id: str, human_approved: bool, approved_by: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "cognition_provider_request_id": _require_string(request_id, "cognition_provider_request_id"),
        "human_approved": human_approved is True,
        "approved_by": _require_string(approved_by, "approved_by"),
        "approved_at": _require_string(created_at, "created_at"),
        "approval_boundary": "HUMAN_APPROVAL_REQUIRED_BEFORE_COGNITION_PROVIDER_INVOCATION",
    }
    artifact["approval_evidence_hash"] = replay_hash(artifact)
    return artifact


def _failure_artifact(
    *,
    cognition_provider_request_id: str,
    provider_id: str,
    created_at: str,
    failure_reason: str,
    request_artifact: dict[str, Any] | None,
    response_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": LLM_COGNITION_PROVIDER_REPLAY_BINDING_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": STATUS_FAILED_CLOSED,
        "cognition_provider_request_id": cognition_provider_request_id,
        "provider_id": provider_id,
        "provider_invoked": response_artifact is not None,
        "request_artifact_hash": request_artifact.get("artifact_hash") if request_artifact else None,
        "response_artifact_hash": response_artifact.get("artifact_hash") if response_artifact else None,
        "failure_reason": failure_reason,
        "created_at": created_at,
        "governance_preservation": {
            "provider_output_authoritative": False,
            "human_approval_boundary_preserved": True,
            "fail_closed_behavior_preserved": True,
            "replay_reconstruction_preserved": True,
            "no_execution": True,
            "no_worker_invocation": True,
            "no_approval_creation": True,
            "no_governance_mutation": True,
            "no_replay_mutation": True,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    request_artifact: dict[str, Any] | None,
    response_artifact: dict[str, Any] | None,
    replay_binding: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol llm-cognition-provider invoke",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "cognition_provider_request_id": replay_binding.get("cognition_provider_request_id"),
        "provider_id": replay_binding.get("provider_id"),
        "provider_invoked": replay_binding.get("provider_invoked") is True,
        "llm_cognition_provider_request_artifact": deepcopy(request_artifact),
        "llm_cognition_provider_response_artifact": deepcopy(response_artifact),
        "replay_binding": deepcopy(replay_binding),
        "replay_reference": str(replay_path),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["llm_cognition_provider_runtime_hash"] = replay_hash(result)
    return result


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("LLM cognition provider replay step ordering mismatch")
    _verify_artifact_hash(artifact, "LLM cognition provider replay artifact")
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
            artifact = deepcopy(failure)
            artifact["failed_step"] = step
            artifact.pop("artifact_hash", None)
            artifact["artifact_hash"] = replay_hash(artifact)
            _persist_step(replay_dir, index, step, artifact)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _public_artifact(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if artifact is None:
        return {}
    public = deepcopy(artifact)
    public.pop("_credential_secret", None)
    return public


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("cognition provider response must be JSON serializable") from exc
    return deepcopy(value)


def _bounded_response_text(value: str) -> str:
    text = " ".join(_require_string(value, "provider_response_text").split())
    if len(text) > MAX_PROVIDER_RESPONSE_CHARS:
        raise FailClosedRuntimeError("cognition provider response exceeds bounded size")
    return text


def _compute_request_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "contract_reference": artifact["contract_reference"],
            "authority_policy_reference": artifact["authority_policy_reference"],
            "necessity_policy_reference": artifact["necessity_policy_reference"],
            "cognition_provider_request_id": artifact["cognition_provider_request_id"],
            "provider_id": artifact["provider_id"],
            "provider_role": artifact["provider_role"],
            "provider_schema_id": artifact["provider_schema_id"],
            "provider_identity": artifact["provider_identity"],
            "request": artifact["request"],
            "ocs_context_reference": artifact["ocs_context_reference"],
            "provider_contract_hash": artifact["provider_contract_hash"],
            "credential_policy_hash": artifact["credential_policy_hash"],
            "approval_evidence": artifact["approval_evidence"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
        }
    )


def _compute_response_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "cognition_provider_request_id": artifact["cognition_provider_request_id"],
            "provider_id": artifact["provider_id"],
            "provider_role": artifact["provider_role"],
            "provider_schema_id": artifact["provider_schema_id"],
            "provider_identity": artifact["provider_identity"],
            "provider_metadata": artifact["provider_metadata"],
            "provider_request_hash": artifact["provider_request_hash"],
            "request_hash": artifact["request_hash"],
            "ocs_context_hash": artifact["ocs_context_hash"],
            "raw_response_hash": artifact["raw_response_hash"],
            "response_text_hash": artifact["response_text_hash"],
            "response_status": artifact["response_status"],
            "untrusted_provider_output": artifact["untrusted_provider_output"],
            "non_authoritative": artifact["non_authoritative"],
            "authority_flags": artifact["authority_flags"],
            "lineage_refs": artifact["lineage_refs"],
        }
    )


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("LLM cognition provider replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("LLM cognition provider replay hash mismatch")


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
