"""Governed live provider runtime boundary for AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.external_resource_registry_runtime import (
    COGNITION_PROVIDER,
    OPENAI_PROVIDER_ID,
    real_provider_err_v1_registry,
    select_resource_for_capability,
)
from aigol.runtime.first_real_provider_runtime import (
    AUTHORITY_FLAGS,
    CANONICAL_CONTRACT_REFERENCE,
    CANONICAL_COGNITION_PROVIDER_CONTRACT_V1,
    CANONICAL_COGNITION_PROVIDER_INPUT_V1,
    CANONICAL_COGNITION_PROVIDER_OUTPUT_V1,
    OPENAI_CAPABILITIES,
    adapt_openai_contract_to_canonical,
)
from aigol.runtime.live_provider_invocation_prerequisites import (
    LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1,
    LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1,
    create_live_provider_credential_policy,
    create_live_provider_invocation_approval,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    OPENAI_RESPONSES_ENDPOINT,
    OPENAI_RESPONSES_SCHEMA,
    create_default_openai_cognition_provider_contract,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_LIVE_PROVIDER_RUNTIME_BOUNDARY_V1"

LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1 = (
    "LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1"
)
LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1 = "LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1"
LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1 = "LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1"
LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1 = "LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1"
LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1 = "LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1"
LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1 = "LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"
APPROVED = "APPROVED"
APPROVED_SCOPE = "SINGLE_PROVIDER_SINGLE_RUNTIME_VALIDATION"

ERROR_AUTHENTICATION_UNAVAILABLE = "AUTHENTICATION_UNAVAILABLE"
ERROR_CREDENTIAL_POLICY_INVALID = "CREDENTIAL_POLICY_INVALID"
ERROR_MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
ERROR_RATE_LIMIT = "RATE_LIMIT"
ERROR_REPLAY_WRITE_FAILURE = "REPLAY_WRITE_FAILURE"
ERROR_TIMEOUT = "TIMEOUT"
ERROR_TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"
ERROR_AUTHORITY_BOUNDARY_VIOLATION = "AUTHORITY_BOUNDARY_VIOLATION"

REPLAY_STEPS_SUCCESS = (
    "live_provider_credential_retrieval_attempt",
    "live_provider_credential_use_boundary",
    "live_provider_request_envelope",
    "live_provider_response_envelope",
    "live_provider_runtime_boundary_audit",
)

REPLAY_STEPS_ERROR = (
    "live_provider_credential_retrieval_attempt",
    "live_provider_request_envelope",
    "live_provider_error_envelope",
    "live_provider_runtime_boundary_audit",
)

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
    "governance mutation",
    "mutate governance",
    "replay mutation",
    "mutate replay",
    "credential disclosure",
    "api key",
)

BoundaryTransport = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def run_live_provider_runtime_boundary(
    *,
    invocation_id: str,
    human_request: str,
    created_at: str,
    replay_dir: str | Path,
    approval_artifact: dict[str, Any] | None,
    credential_policy_artifact: dict[str, Any] | None,
    err_registry: dict[str, Any] | None = None,
    model: str = "gpt-5.1",
    timeout_seconds: int = 20,
    transport: BoundaryTransport | None = None,
    live_transport_enabled: bool = False,
) -> dict[str, Any]:
    """Prepare the live provider boundary and execute only injected deterministic transport."""

    replay_path = Path(replay_dir)
    invocation = _require_string(invocation_id, "invocation_id")
    retrieval: dict[str, Any] | None = None
    request_envelope: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        if live_transport_enabled is True:
            raise FailClosedRuntimeError("live provider boundary failed closed: live OpenAI transport is not implemented")
        approval = validate_live_provider_approval(approval_artifact)
        credential_policy = validate_live_provider_credential_policy(credential_policy_artifact)
        err_selection = select_resource_for_capability(
            selection_id=f"{invocation}:ERR_OPENAI_SELECTION",
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
            raise FailClosedRuntimeError("live provider boundary failed closed: ERR did not select openai")

        source_contract = create_default_openai_cognition_provider_contract(created_at=created_at)
        canonical_contract = adapt_openai_contract_to_canonical(
            source_contract=source_contract,
            capabilities=OPENAI_CAPABILITIES,
            created_at=created_at,
        )
        retrieval = retrieve_live_provider_credential(
            retrieval_id=f"{invocation}:CREDENTIAL_RETRIEVAL",
            approval_artifact=approval,
            credential_policy_artifact=credential_policy,
            created_at=created_at,
        )
        request_envelope = create_live_request_envelope(
            invocation_id=invocation,
            human_request=human_request,
            approval_artifact=approval,
            credential_policy_artifact=credential_policy,
            credential_retrieval_artifact=retrieval,
            err_selection_capture=err_selection,
            canonical_contract=canonical_contract,
            model=model,
            timeout_seconds=timeout_seconds,
            created_at=created_at,
        )
        if transport is None:
            raise FailClosedRuntimeError("live provider boundary failed closed: deterministic transport is required")
        use_boundary = create_live_credential_use_boundary(
            invocation_id=invocation,
            credential_retrieval_artifact=retrieval,
            request_envelope_artifact=request_envelope,
            created_at=created_at,
        )
        raw_response = _invoke_deterministic_transport(
            transport=transport,
            request_envelope=request_envelope,
        )
        response_envelope = create_live_response_envelope(
            invocation_id=invocation,
            request_envelope_artifact=request_envelope,
            raw_response=raw_response,
            created_at=created_at,
        )
        canonical_input = create_live_canonical_input_view(
            request_envelope_artifact=request_envelope,
            canonical_contract=canonical_contract,
            created_at=created_at,
        )
        canonical_output = create_live_canonical_output_view(
            response_envelope_artifact=response_envelope,
            canonical_input_artifact=canonical_input,
            canonical_contract=canonical_contract,
            created_at=created_at,
        )
        audit = create_live_boundary_audit(
            invocation_id=invocation,
            final_status=STATUS_COMPLETED,
            created_at=created_at,
            credential_retrieval_artifact=retrieval,
            request_envelope_artifact=request_envelope,
            credential_use_artifact=use_boundary,
            response_envelope_artifact=response_envelope,
            error_envelope_artifact=None,
            canonical_output_artifact=canonical_output,
            failure_reason="",
        )
        _persist_sequence(
            replay_path,
            REPLAY_STEPS_SUCCESS,
            (retrieval, use_boundary, request_envelope, response_envelope, audit),
        )
        return _capture(
            invocation_id=invocation,
            final_status=STATUS_COMPLETED,
            failure_reason="",
            replay_path=replay_path,
            retrieval=retrieval,
            request_envelope=request_envelope,
            use_boundary=use_boundary,
            response_envelope=response_envelope,
            error_envelope=None,
            canonical_contract=canonical_contract,
            canonical_input=canonical_input,
            canonical_output=canonical_output,
            audit=audit,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "live provider boundary failed closed"
        classification = _classify_error(reason)
        if retrieval is None:
            retrieval = _failed_retrieval_artifact(
                retrieval_id=f"{invocation}:CREDENTIAL_RETRIEVAL",
                provider_id=OPENAI_PROVIDER_ID,
                failure_reason=reason,
                created_at=created_at,
            )
        if request_envelope is None:
            request_envelope = _failed_request_envelope(
                invocation_id=invocation,
                failure_reason=reason,
                created_at=created_at,
            )
        error_envelope = create_live_error_envelope(
            invocation_id=invocation,
            request_envelope_artifact=request_envelope,
            error_classification=classification,
            failure_reason=reason,
            created_at=created_at,
        )
        audit = create_live_boundary_audit(
            invocation_id=invocation,
            final_status=STATUS_FAILED_CLOSED,
            created_at=created_at,
            credential_retrieval_artifact=retrieval,
            request_envelope_artifact=request_envelope,
            credential_use_artifact=None,
            response_envelope_artifact=None,
            error_envelope_artifact=error_envelope,
            canonical_output_artifact=None,
            failure_reason=reason,
        )
        _persist_sequence(replay_path, REPLAY_STEPS_ERROR, (retrieval, request_envelope, error_envelope, audit))
        return _capture(
            invocation_id=invocation,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            retrieval=retrieval,
            request_envelope=request_envelope,
            use_boundary=None,
            response_envelope=None,
            error_envelope=error_envelope,
            canonical_contract=None,
            canonical_input=None,
            canonical_output=None,
            audit=audit,
        )


def validate_live_provider_approval(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("live provider boundary failed closed: missing approval")
    _verify_artifact_hash(artifact, "live provider approval")
    if artifact.get("artifact_type") != LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("live provider boundary failed closed: invalid approval artifact")
    if artifact.get("approval_status") != APPROVED or artifact.get("approval_granted") is not True:
        raise FailClosedRuntimeError("live provider boundary failed closed: missing approval")
    if artifact.get("approved_provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider boundary failed closed: unauthorized provider")
    if artifact.get("approved_scope") != APPROVED_SCOPE:
        raise FailClosedRuntimeError("live provider boundary failed closed: invalid approval scope")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def validate_live_provider_credential_policy(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("live provider boundary failed closed: missing credential policy")
    _verify_artifact_hash(artifact, "live provider credential policy")
    if artifact.get("artifact_type") != LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("live provider boundary failed closed: invalid credential policy")
    if artifact.get("provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider boundary failed closed: unauthorized provider")
    if not _is_allowed_credential_reference(artifact.get("credential_reference")):
        raise FailClosedRuntimeError("live provider boundary failed closed: unsupported credential reference")
    if artifact.get("credential_secret_stored") is not False or artifact.get("credential_secret_replayed") is not False:
        raise FailClosedRuntimeError("live provider boundary failed closed: credential policy must not store secrets")
    if artifact.get("secret_material_present") is not False:
        raise FailClosedRuntimeError("live provider boundary failed closed: credential policy must not store secrets")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def retrieve_live_provider_credential(
    *,
    retrieval_id: str,
    approval_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    approval = validate_live_provider_approval(approval_artifact)
    policy = validate_live_provider_credential_policy(credential_policy_artifact)
    reference = policy["credential_reference"]
    env_name = reference.removeprefix("env:")
    secret = os.environ.get(env_name)
    if not isinstance(secret, str) or not secret.strip():
        raise FailClosedRuntimeError("live provider boundary failed closed: credential unavailable")
    artifact = {
        "artifact_type": LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "retrieval_id": _require_string(retrieval_id, "retrieval_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "approval_artifact_hash": approval["artifact_hash"],
        "credential_policy_artifact_hash": policy["artifact_hash"],
        "credential_reference": reference,
        "retrieval_boundary": policy["retrieval_boundary"],
        "retrieval_attempted": True,
        "credential_present": True,
        "credential_secret_replayed": False,
        "credential_value_omitted": True,
        "retrieval_status": "AVAILABLE",
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
    artifact["retrieval_hash"] = replay_hash(_retrieval_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_request_envelope(
    *,
    invocation_id: str,
    human_request: str,
    approval_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    credential_retrieval_artifact: dict[str, Any],
    err_selection_capture: dict[str, Any],
    canonical_contract: dict[str, Any],
    model: str,
    timeout_seconds: int,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(credential_retrieval_artifact, "credential retrieval")
    _verify_artifact_hash(canonical_contract, "canonical contract")
    if err_selection_capture.get("selected_resource_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider boundary failed closed: ERR did not select openai")
    timeout = _normalize_timeout(timeout_seconds)
    payload = {
        "model": _require_string(model, "model"),
        "input": _require_string(human_request, "human_request"),
        "stream": False,
    }
    artifact = {
        "artifact_type": LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "endpoint": OPENAI_RESPONSES_ENDPOINT,
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "err_selection_artifact_hash": err_selection_capture["err_selection_evidence_artifact"]["artifact_hash"],
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "credential_retrieval_artifact_hash": credential_retrieval_artifact["artifact_hash"],
        "canonical_contract_artifact_hash": canonical_contract["artifact_hash"],
        "request_payload": payload,
        "request_payload_hash": replay_hash(payload),
        "timeout_seconds": timeout,
        "streaming": False,
        "tool_use": False,
        "automatic_retries": False,
        "credential_secret_replayed": False,
        "live_provider_call_performed": False,
        "deterministic_transport_required": True,
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
    artifact["request_envelope_hash"] = replay_hash(_request_envelope_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_credential_use_boundary(
    *,
    invocation_id: str,
    credential_retrieval_artifact: dict[str, Any],
    request_envelope_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(credential_retrieval_artifact, "credential retrieval")
    _verify_artifact_hash(request_envelope_artifact, "request envelope")
    artifact = {
        "artifact_type": LIVE_PROVIDER_CREDENTIAL_USE_BOUNDARY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_retrieval_artifact_hash": credential_retrieval_artifact["artifact_hash"],
        "request_envelope_artifact_hash": request_envelope_artifact["artifact_hash"],
        "credential_used_for_exactly_one_request": True,
        "credential_secret_replayed": False,
        "credential_value_omitted": True,
        "credential_disposed_after_boundary": True,
        "live_provider_call_performed": False,
        "deterministic_transport_only": True,
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
    artifact["credential_use_hash"] = replay_hash(_credential_use_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_response_envelope(
    *,
    invocation_id: str,
    request_envelope_artifact: dict[str, Any],
    raw_response: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_envelope_artifact, "request envelope")
    safe_response = _json_safe(raw_response)
    response_text = _extract_response_text(safe_response)
    _reject_authority_bearing_response(response_text)
    artifact = {
        "artifact_type": LIVE_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "request_envelope_artifact_hash": request_envelope_artifact["artifact_hash"],
        "response_status": "CAPTURED",
        "raw_response": safe_response,
        "raw_response_hash": replay_hash(safe_response),
        "response_text": response_text,
        "response_text_hash": replay_hash(response_text),
        "canonical_output_required": True,
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "credential_secret_replayed": False,
        "live_provider_call_performed": False,
        "deterministic_transport_executed": True,
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
    artifact["response_envelope_hash"] = replay_hash(_response_envelope_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_error_envelope(
    *,
    invocation_id: str,
    request_envelope_artifact: dict[str, Any],
    error_classification: str,
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_envelope_artifact, "request envelope")
    artifact = {
        "artifact_type": LIVE_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "request_envelope_artifact_hash": request_envelope_artifact["artifact_hash"],
        "error_classification": _require_string(error_classification, "error_classification"),
        "failure_reason": _redact_failure_reason(failure_reason),
        "retry_attempted": False,
        "fallback_attempted": False,
        "credential_secret_replayed": False,
        "live_provider_call_performed": False,
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
    artifact["error_envelope_hash"] = replay_hash(_error_envelope_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_canonical_input_view(
    *,
    request_envelope_artifact: dict[str, Any],
    canonical_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request_envelope_artifact, "request envelope")
    _verify_artifact_hash(canonical_contract, "canonical contract")
    artifact = {
        "artifact_type": CANONICAL_COGNITION_PROVIDER_INPUT_V1,
        "contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_input_id": request_envelope_artifact["invocation_id"],
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "provider_identity": {
            "provider_id": OPENAI_PROVIDER_ID,
            "provider_kind": "external_llm",
            "model": request_envelope_artifact["request_payload"]["model"],
            "endpoint": OPENAI_RESPONSES_ENDPOINT,
        },
        "request": deepcopy(request_envelope_artifact["request_payload"]),
        "provider_contract_hash": canonical_contract["artifact_hash"],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "source_input_artifact_hash": request_envelope_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["input_hash"] = replay_hash(_canonical_input_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_canonical_output_view(
    *,
    response_envelope_artifact: dict[str, Any],
    canonical_input_artifact: dict[str, Any],
    canonical_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(response_envelope_artifact, "response envelope")
    _verify_artifact_hash(canonical_input_artifact, "canonical input")
    _verify_artifact_hash(canonical_contract, "canonical contract")
    artifact = {
        "artifact_type": CANONICAL_COGNITION_PROVIDER_OUTPUT_V1,
        "contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_output_id": f"{response_envelope_artifact['invocation_id']}:CANONICAL_OUTPUT",
        "provider_input_id": canonical_input_artifact["provider_input_id"],
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "provider_identity": deepcopy(canonical_input_artifact["provider_identity"]),
        "provider_metadata": {
            "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
            "model": canonical_input_artifact["provider_identity"]["model"],
            "endpoint": OPENAI_RESPONSES_ENDPOINT,
            "streaming": False,
            "tool_use": False,
            "automatic_retries": False,
            "single_provider_only": True,
        },
        "provider_contract_hash": canonical_contract["artifact_hash"],
        "provider_input_hash": canonical_input_artifact["artifact_hash"],
        "source_provider_input_hash": canonical_input_artifact["source_input_artifact_hash"],
        "raw_response": deepcopy(response_envelope_artifact["raw_response"]),
        "raw_response_hash": response_envelope_artifact["raw_response_hash"],
        "response_text": response_envelope_artifact["response_text"],
        "response_text_hash": response_envelope_artifact["response_text_hash"],
        "response_status": response_envelope_artifact["response_status"],
        "untrusted_provider_output": True,
        "non_authoritative": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "source_output_artifact_hash": response_envelope_artifact["artifact_hash"],
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["output_hash"] = replay_hash(_canonical_output_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_boundary_audit(
    *,
    invocation_id: str,
    final_status: str,
    created_at: str,
    credential_retrieval_artifact: dict[str, Any],
    request_envelope_artifact: dict[str, Any],
    credential_use_artifact: dict[str, Any] | None,
    response_envelope_artifact: dict[str, Any] | None,
    error_envelope_artifact: dict[str, Any] | None,
    canonical_output_artifact: dict[str, Any] | None,
    failure_reason: str,
) -> dict[str, Any]:
    _verify_artifact_hash(credential_retrieval_artifact, "credential retrieval")
    _verify_artifact_hash(request_envelope_artifact, "request envelope")
    if credential_use_artifact is not None:
        _verify_artifact_hash(credential_use_artifact, "credential use boundary")
    if response_envelope_artifact is not None:
        _verify_artifact_hash(response_envelope_artifact, "response envelope")
    if error_envelope_artifact is not None:
        _verify_artifact_hash(error_envelope_artifact, "error envelope")
    if canonical_output_artifact is not None:
        _verify_artifact_hash(canonical_output_artifact, "canonical output")
    status = _require_string(final_status, "final_status")
    artifact = {
        "artifact_type": LIVE_PROVIDER_RUNTIME_BOUNDARY_AUDIT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "final_status": status,
        "audit_verdict": "PASS" if status == STATUS_COMPLETED else "FAILED_CLOSED",
        "failure_reason": _redact_failure_reason(failure_reason),
        "credential_retrieval_artifact_hash": credential_retrieval_artifact["artifact_hash"],
        "credential_use_artifact_hash": credential_use_artifact["artifact_hash"] if credential_use_artifact else None,
        "request_envelope_artifact_hash": request_envelope_artifact["artifact_hash"],
        "response_envelope_artifact_hash": response_envelope_artifact["artifact_hash"] if response_envelope_artifact else None,
        "error_envelope_artifact_hash": error_envelope_artifact["artifact_hash"] if error_envelope_artifact else None,
        "canonical_output_artifact_hash": canonical_output_artifact["artifact_hash"] if canonical_output_artifact else None,
        "live_provider_call_performed": False,
        "deterministic_transport_only": True,
        "credential_secret_replayed": False,
        "err_remained_passive": True,
        "no_worker_invocation": True,
        "no_governance_mutation": True,
        "no_replay_mutation": True,
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
    artifact["audit_hash"] = replay_hash(_audit_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_live_provider_runtime_boundary_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = _load_replay_sequence(replay_path, REPLAY_STEPS_SUCCESS)
    if not wrappers:
        wrappers = _load_replay_sequence(replay_path, REPLAY_STEPS_ERROR)
    if not wrappers:
        raise FailClosedRuntimeError("live provider boundary replay missing")
    audit = wrappers[-1]["artifact"]
    _verify_artifact_hash(audit, "live boundary audit")
    status = audit["final_status"]
    return {
        "milestone_id": MILESTONE_ID,
        "final_status": status,
        "invocation_id": audit["invocation_id"],
        "provider_id": audit["provider_id"],
        "live_provider_call_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "credential_secret_replayed": False,
        "audit_verdict": audit["audit_verdict"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _invoke_deterministic_transport(*, transport: BoundaryTransport, request_envelope: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(request_envelope["request_payload"])
    metadata = {
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "endpoint": OPENAI_RESPONSES_ENDPOINT,
        "timeout_seconds": request_envelope["timeout_seconds"],
        "live_provider_call_performed": False,
        "credential_secret_replayed": False,
    }
    try:
        response = transport(payload, metadata)
    except TimeoutError as exc:
        raise FailClosedRuntimeError("live provider boundary failed closed: timeout") from exc
    except Exception as exc:
        message = str(exc).lower()
        if "rate" in message and "limit" in message:
            raise FailClosedRuntimeError("live provider boundary failed closed: rate limit") from exc
        raise FailClosedRuntimeError("live provider boundary failed closed: transport unavailable") from exc
    if not isinstance(response, dict):
        raise FailClosedRuntimeError("live provider boundary failed closed: malformed response")
    if response.get("real_openai_called") is True:
        raise FailClosedRuntimeError("live provider boundary failed closed: live OpenAI call is prohibited")
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
            raise FailClosedRuntimeError("live provider boundary replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("live provider boundary replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"live provider boundary {step}")
        wrappers.append(wrapper)
    return wrappers


def _capture(
    *,
    invocation_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    retrieval: dict[str, Any] | None,
    request_envelope: dict[str, Any] | None,
    use_boundary: dict[str, Any] | None,
    response_envelope: dict[str, Any] | None,
    error_envelope: dict[str, Any] | None,
    canonical_contract: dict[str, Any] | None,
    canonical_input: dict[str, Any] | None,
    canonical_output: dict[str, Any] | None,
    audit: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "invocation_id": invocation_id,
        "final_status": final_status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "credential_retrieval_artifact": deepcopy(retrieval),
        "credential_use_boundary_artifact": deepcopy(use_boundary),
        "live_request_envelope_artifact": deepcopy(request_envelope),
        "live_response_envelope_artifact": deepcopy(response_envelope),
        "live_error_envelope_artifact": deepcopy(error_envelope),
        "canonical_provider_contract": deepcopy(canonical_contract),
        "canonical_provider_input": deepcopy(canonical_input),
        "canonical_provider_output": deepcopy(canonical_output),
        "live_boundary_audit_artifact": deepcopy(audit),
        "live_provider_call_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "credential_secret_replayed": False,
        "fail_closed": final_status == STATUS_FAILED_CLOSED,
        "replay_visible": True,
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _failed_retrieval_artifact(*, retrieval_id: str, provider_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_PROVIDER_CREDENTIAL_RETRIEVAL_ATTEMPT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "retrieval_id": _require_string(retrieval_id, "retrieval_id"),
        "provider_id": provider_id if isinstance(provider_id, str) and provider_id.strip() else OPENAI_PROVIDER_ID,
        "retrieval_attempted": False,
        "credential_present": False,
        "credential_secret_replayed": False,
        "credential_value_omitted": True,
        "retrieval_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
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
    artifact["retrieval_hash"] = replay_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_request_envelope(*, invocation_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_role": COGNITION_PROVIDER,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "request_payload": {},
        "request_payload_hash": replay_hash({}),
        "timeout_seconds": 0,
        "streaming": False,
        "tool_use": False,
        "automatic_retries": False,
        "credential_secret_replayed": False,
        "live_provider_call_performed": False,
        "failure_reason": _redact_failure_reason(failure_reason),
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
    artifact["request_envelope_hash"] = replay_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ensure_replay_available(replay_path: Path) -> None:
    for steps in (REPLAY_STEPS_SUCCESS, REPLAY_STEPS_ERROR):
        for index, step in enumerate(steps):
            if (replay_path / f"{index:03d}_{step}.json").exists():
                raise FailClosedRuntimeError("live provider boundary failed closed: replay artifact already exists")


def _json_safe(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("live provider boundary failed closed: malformed response")
    replay_hash(value)
    return deepcopy(value)


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
    raise FailClosedRuntimeError("live provider boundary failed closed: malformed response")


def _bounded_text(value: str) -> str:
    text = _require_string(value, "response_text")
    if len(text) > 8192:
        raise FailClosedRuntimeError("live provider boundary failed closed: malformed response")
    return text


def _reject_authority_bearing_response(response_text: str) -> None:
    lowered = _require_string(response_text, "response_text").lower()
    if any(phrase in lowered for phrase in PROHIBITED_RESPONSE_PHRASES):
        raise FailClosedRuntimeError("live provider boundary failed closed: authority-bearing provider output")


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
    if "replay" in lowered:
        return ERROR_REPLAY_WRITE_FAILURE
    return ERROR_TRANSPORT_UNAVAILABLE


def _is_allowed_credential_reference(value: Any) -> bool:
    return isinstance(value, str) and value == "env:AIGOL_OPENAI_API_KEY"


def _normalize_timeout(value: int) -> int:
    if not isinstance(value, int) or value <= 0 or value > 60:
        raise FailClosedRuntimeError("live provider boundary failed closed: invalid timeout")
    return value


def _redact_failure_reason(reason: str) -> str:
    text = reason if isinstance(reason, str) else ""
    if "sk-" in text.lower() or "bearer " in text.lower():
        return "live provider boundary failed closed: secret material redacted"
    return text


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if "sk-" in serialized or "bearer " in serialized or "api_key" in serialized:
        raise FailClosedRuntimeError("live provider boundary failed closed: credential secret replay detected")


def _reject_mutation_flags(artifact: dict[str, Any]) -> None:
    for flag in (
        "provider_invoked",
        "worker_invoked",
        "execution_requested",
        "dispatch_requested",
        "governance_modified",
        "replay_modified",
    ):
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"live provider boundary failed closed: prohibited flag {flag}")


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
        raise FailClosedRuntimeError("live provider boundary replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("live provider boundary replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"live provider boundary failed closed: {field_name} is required")
    return value


def _retrieval_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "retrieval_id": artifact["retrieval_id"],
        "provider_id": artifact["provider_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "credential_reference": artifact["credential_reference"],
        "retrieval_status": artifact["retrieval_status"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _request_envelope_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "err_selection_artifact_hash": artifact["err_selection_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "credential_retrieval_artifact_hash": artifact["credential_retrieval_artifact_hash"],
        "canonical_contract_artifact_hash": artifact["canonical_contract_artifact_hash"],
        "request_payload_hash": artifact["request_payload_hash"],
        "timeout_seconds": artifact["timeout_seconds"],
    }


def _credential_use_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "credential_retrieval_artifact_hash": artifact["credential_retrieval_artifact_hash"],
        "request_envelope_artifact_hash": artifact["request_envelope_artifact_hash"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _response_envelope_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "request_envelope_artifact_hash": artifact["request_envelope_artifact_hash"],
        "raw_response_hash": artifact["raw_response_hash"],
        "response_text_hash": artifact["response_text_hash"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _error_envelope_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "request_envelope_artifact_hash": artifact["request_envelope_artifact_hash"],
        "error_classification": artifact["error_classification"],
        "final_status": artifact["final_status"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _canonical_input_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_input_id": artifact["provider_input_id"],
        "provider_id": artifact["provider_id"],
        "provider_schema_id": artifact["provider_schema_id"],
        "request": artifact["request"],
        "provider_contract_hash": artifact["provider_contract_hash"],
        "source_input_artifact_hash": artifact["source_input_artifact_hash"],
    }


def _canonical_output_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_output_id": artifact["provider_output_id"],
        "provider_input_id": artifact["provider_input_id"],
        "provider_id": artifact["provider_id"],
        "provider_schema_id": artifact["provider_schema_id"],
        "provider_contract_hash": artifact["provider_contract_hash"],
        "provider_input_hash": artifact["provider_input_hash"],
        "raw_response_hash": artifact["raw_response_hash"],
        "response_text_hash": artifact["response_text_hash"],
        "source_output_artifact_hash": artifact["source_output_artifact_hash"],
    }


def _audit_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "final_status": artifact["final_status"],
        "credential_retrieval_artifact_hash": artifact["credential_retrieval_artifact_hash"],
        "credential_use_artifact_hash": artifact["credential_use_artifact_hash"],
        "request_envelope_artifact_hash": artifact["request_envelope_artifact_hash"],
        "response_envelope_artifact_hash": artifact["response_envelope_artifact_hash"],
        "error_envelope_artifact_hash": artifact["error_envelope_artifact_hash"],
        "canonical_output_artifact_hash": artifact["canonical_output_artifact_hash"],
        "live_provider_call_performed": artifact["live_provider_call_performed"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }
