"""PGSP-bound read-only provider cognition runtime for G5-02."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import (
    record_cognition_participation,
    record_provider_usage_metric,
)
from aigol.runtime.provider_identity_boundaries import (
    COGNITION_PROVIDER,
    PROVIDER_IDENTITY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


G5_02_RUNTIME_VERSION = "G5_02_PGSP_BOUND_READ_ONLY_PROVIDER_COGNITION_RUNTIME_V1"

PGSP_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1 = "G5_02_PGSP_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1"
PGSP_PROVIDER_IDENTITY_VALIDATION_ARTIFACT_V1 = "G5_02_PROVIDER_IDENTITY_VALIDATION_ARTIFACT_V1"
PGSP_PROVIDER_GOVERNANCE_CHECKPOINT_ARTIFACT_V1 = "G5_02_PROVIDER_GOVERNANCE_CHECKPOINT_ARTIFACT_V1"
PGSP_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1 = "G5_02_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1"
PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1 = "G5_02_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1"
PGSP_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1 = "G5_02_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1"
PGSP_PROVIDER_PARTICIPATION_EVIDENCE_ARTIFACT_V1 = "G5_02_PROVIDER_PARTICIPATION_EVIDENCE_ARTIFACT_V1"
PGSP_POST_EXECUTION_REVIEW_ARTIFACT_V1 = "G5_02_POST_EXECUTION_REVIEW_ARTIFACT_V1"
PGSP_UHCL_EXECUTION_SUMMARY_ARTIFACT_V1 = "G5_02_UHCL_EXECUTION_SUMMARY_ARTIFACT_V1"
PGSP_PROVIDER_COGNITION_RUNTIME_SUMMARY_ARTIFACT_V1 = "G5_02_PROVIDER_COGNITION_RUNTIME_SUMMARY_ARTIFACT_V1"

READ_ONLY_PROVIDER_COGNITION_COMPLETED = "G5_02_READ_ONLY_PROVIDER_COGNITION_COMPLETED"
READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED = "G5_02_READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED"
READ_ONLY_PROVIDER_GOVERNANCE_PASSED = "G5_02_READ_ONLY_PROVIDER_GOVERNANCE_PASSED"
READ_ONLY_PROVIDER_GOVERNANCE_FAILED_CLOSED = "G5_02_READ_ONLY_PROVIDER_GOVERNANCE_FAILED_CLOSED"
AUTHORIZATION_SCOPE = "PGSP_BOUND_READ_ONLY_PROVIDER_COGNITION"

REPLAY_STEPS = (
    "pgsp_provider_cognition_request_recorded",
    "provider_identity_validation_recorded",
    "provider_governance_checkpoint_recorded",
    "provider_request_envelope_recorded",
    "provider_result_envelope_recorded",
    "provider_participation_evidence_recorded",
    "post_execution_review_recorded",
    "uhcl_execution_summary_recorded",
    "provider_cognition_runtime_summary_recorded",
)

ProviderExecutor = Callable[[dict[str, Any]], dict[str, Any]]


def run_g5_pgsp_bound_read_only_provider_cognition_runtime(
    *,
    session_id: str,
    cognition_request: str,
    provider_identity_artifact: dict[str, Any],
    execution_authorization_artifact: dict[str, Any],
    provider_executor: ProviderExecutor,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Execute one PGSP-bound read-only cognition request through a provider."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)

    request = _request_artifact(
        session_id=session_id,
        cognition_request=cognition_request,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], request)

    identity = _identity_validation_artifact(
        session_id=session_id,
        provider_identity_artifact=provider_identity_artifact,
        created_at=created_at,
    )
    _persist_step(replay_path, 1, REPLAY_STEPS[1], identity)

    governance = _governance_checkpoint_artifact(
        session_id=session_id,
        request=request,
        identity=identity,
        execution_authorization_artifact=execution_authorization_artifact,
        created_at=created_at,
    )
    _persist_step(replay_path, 2, REPLAY_STEPS[2], governance)

    request_envelope = _provider_request_envelope_artifact(
        session_id=session_id,
        request=request,
        identity=identity,
        governance=governance,
        created_at=created_at,
    )
    _persist_step(replay_path, 3, REPLAY_STEPS[3], request_envelope)

    result_envelope = _execute_provider_once(
        session_id=session_id,
        request_envelope=request_envelope,
        provider_executor=provider_executor,
        created_at=created_at,
    )
    _persist_step(replay_path, 4, REPLAY_STEPS[4], result_envelope)

    participation = _provider_participation_evidence_artifact(
        session_id=session_id,
        identity=identity,
        result_envelope=result_envelope,
        created_at=created_at,
    )
    _persist_step(replay_path, 5, REPLAY_STEPS[5], participation)

    review = _post_execution_review_artifact(
        session_id=session_id,
        request=request,
        identity=identity,
        governance=governance,
        result_envelope=result_envelope,
        participation=participation,
        created_at=created_at,
    )
    _persist_step(replay_path, 6, REPLAY_STEPS[6], review)

    uhcl_summary = _uhcl_execution_summary_artifact(
        session_id=session_id,
        request=request,
        result_envelope=result_envelope,
        review=review,
        created_at=created_at,
    )
    _persist_step(replay_path, 7, REPLAY_STEPS[7], uhcl_summary)

    summary = _runtime_summary_artifact(
        session_id=session_id,
        request=request,
        identity=identity,
        governance=governance,
        request_envelope=request_envelope,
        result_envelope=result_envelope,
        participation=participation,
        review=review,
        uhcl_summary=uhcl_summary,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    _persist_step(replay_path, 8, REPLAY_STEPS[8], summary)
    return _capture(summary, replay_path)


def reconstruct_g5_pgsp_bound_read_only_provider_cognition_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct a G5-02 read-only provider cognition replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G5-02 provider cognition replay ordering mismatch")
        _verify_hash(wrapper, "replay_hash", "G5-02 provider cognition replay hash mismatch")
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_hash(artifact, "artifact_hash", "G5-02 provider cognition artifact hash mismatch")
        _validate_boundary_flags(artifact)
        wrappers.append(wrapper)

    request = wrappers[0]["artifact"]
    identity = wrappers[1]["artifact"]
    governance = wrappers[2]["artifact"]
    request_envelope = wrappers[3]["artifact"]
    result_envelope = wrappers[4]["artifact"]
    participation = wrappers[5]["artifact"]
    review = wrappers[6]["artifact"]
    uhcl_summary = wrappers[7]["artifact"]
    summary = wrappers[8]["artifact"]

    expected = {
        "request_hash": request["artifact_hash"],
        "identity_validation_hash": identity["artifact_hash"],
        "governance_checkpoint_hash": governance["artifact_hash"],
        "request_envelope_hash": request_envelope["artifact_hash"],
        "result_envelope_hash": result_envelope["artifact_hash"],
        "participation_evidence_hash": participation["artifact_hash"],
        "post_execution_review_hash": review["artifact_hash"],
        "uhcl_summary_hash": uhcl_summary["artifact_hash"],
    }
    for field, value in expected.items():
        if summary[field] != value:
            raise FailClosedRuntimeError(f"G5-02 provider cognition {field} mismatch")
    if review["provider_result_hash"] != result_envelope["artifact_hash"]:
        raise FailClosedRuntimeError("G5-02 provider cognition review result hash mismatch")
    if uhcl_summary["post_execution_review_hash"] != review["artifact_hash"]:
        raise FailClosedRuntimeError("G5-02 provider cognition UHCL summary hash mismatch")

    return {
        "runtime_version": G5_02_RUNTIME_VERSION,
        "session_id": summary["session_id"],
        "execution_status": summary["execution_status"],
        "provider_id": summary["provider_id"],
        "provider_role": summary["provider_role"],
        "governance_checkpoint_status": governance["governance_checkpoint_status"],
        "post_execution_review_status": review["post_execution_review_status"],
        "provider_invoked": summary["provider_invoked"],
        "provider_dispatch_count": summary["provider_dispatch_count"],
        "provider_response_received": summary["provider_response_received"],
        "provider_error_recorded": summary["provider_error_recorded"],
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "provider_authority": False,
        "governance_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "mutation_authority": False,
        "deployment_authority": False,
        "replay_artifact_count": len(wrappers),
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _request_artifact(*, session_id: str, cognition_request: str, created_at: str) -> dict[str, Any]:
    request = _require_string(cognition_request, "cognition_request")
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_COGNITION_REQUEST_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "request_scope": AUTHORIZATION_SCOPE,
            "cognition_request": request,
            "cognition_request_hash": replay_hash(request),
            "read_only": True,
            "cognition_only": True,
            "provider_role_required": COGNITION_PROVIDER,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": False,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _identity_validation_artifact(
    *,
    session_id: str,
    provider_identity_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    provider = _validated_provider_identity(provider_identity_artifact)
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_IDENTITY_VALIDATION_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "provider_identity_hash": provider["artifact_hash"],
            "provider_id": provider["provider_id"],
            "external_provider_family": provider["external_provider_family"],
            "model_id": provider["model_id"],
            "provider_role": provider["provider_role"],
            "provider_role_validated": True,
            "credential_reference_id": provider["credential_reference_id"],
            "credential_reference": provider["credential_reference"],
            "credential_reference_hash": provider["credential_reference_hash"],
            "credential_lifecycle_state": provider["credential_lifecycle_state"],
            "activation_status": provider["activation_status"],
            "credential_secret_replayed": False,
            "credential_hash_recorded": False,
            "authorization_header_recorded": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": False,
            "provider_response_received": False,
            "execution_authorized": False,
        }
    )
    return _with_artifact_hash(artifact)


def _governance_checkpoint_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    identity: dict[str, Any],
    execution_authorization_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    authorization = _validate_authorization(
        execution_authorization_artifact,
        session_id=session_id,
        provider_id=identity["provider_id"],
        provider_role=identity["provider_role"],
    )
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_GOVERNANCE_CHECKPOINT_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "governance_checkpoint_status": READ_ONLY_PROVIDER_GOVERNANCE_PASSED,
            "request_hash": request["artifact_hash"],
            "provider_identity_validation_hash": identity["artifact_hash"],
            "execution_authorization_hash": authorization["artifact_hash"],
            "authorization_status": authorization["authorization_status"],
            "authorization_scope": authorization["authorization_scope"],
            "authorization_consumed_by_runtime": True,
            "read_only_boundary_preserved": True,
            "cognition_only_boundary_preserved": True,
            "provider_identity_boundary_preserved": True,
            "credential_boundary_preserved": True,
            "worker_boundary_preserved": True,
            "mutation_boundary_preserved": True,
            "deployment_boundary_preserved": True,
            "approval_activation_performed": False,
            "authorization_activation_performed": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": False,
            "provider_response_received": False,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _provider_request_envelope_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    identity: dict[str, Any],
    governance: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    envelope = {
        "session_id": _require_string(session_id, "session_id"),
        "provider_id": identity["provider_id"],
        "provider_role": identity["provider_role"],
        "model_id": identity["model_id"],
        "request_scope": AUTHORIZATION_SCOPE,
        "input_text": request["cognition_request"],
        "read_only": True,
        "cognition_only": True,
        "stream": False,
    }
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_REQUEST_ENVELOPE_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "request_envelope_id": f"{_require_string(session_id, 'session_id')}:G5-02:PROVIDER-REQUEST",
            "session_id": _require_string(session_id, "session_id"),
            "request_hash": request["artifact_hash"],
            "provider_identity_validation_hash": identity["artifact_hash"],
            "governance_checkpoint_hash": governance["artifact_hash"],
            "provider_id": identity["provider_id"],
            "provider_role": identity["provider_role"],
            "model_id": identity["model_id"],
            "request_envelope": envelope,
            "request_envelope_hash": replay_hash(envelope),
            "credential_secret_replayed": False,
            "authorization_header_recorded": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": False,
            "provider_request_created": True,
            "provider_response_received": False,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _execute_provider_once(
    *,
    session_id: str,
    request_envelope: dict[str, Any],
    provider_executor: ProviderExecutor,
    created_at: str,
) -> dict[str, Any]:
    if not callable(provider_executor):
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: provider_executor must be callable")
    try:
        response = provider_executor(deepcopy(request_envelope["request_envelope"]))
        if not isinstance(response, dict):
            raise FailClosedRuntimeError("provider response must be a JSON object")
        output_text = _require_string(response.get("output_text"), "output_text")
        if _contains_authority_claim(output_text) or _contains_authority_claim(response):
            raise FailClosedRuntimeError("provider output contains authority-bearing content")
        safe_metadata = _safe_mapping(response.get("metadata", {}), "metadata")
        artifact = _base_artifact(
            {
                "artifact_type": PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1,
                "runtime_version": G5_02_RUNTIME_VERSION,
                "response_envelope_id": f"{_require_string(session_id, 'session_id')}:G5-02:PROVIDER-RESPONSE",
                "session_id": _require_string(session_id, "session_id"),
                "request_envelope_hash": request_envelope["artifact_hash"],
                "provider_id": request_envelope["provider_id"],
                "provider_role": request_envelope["provider_role"],
                "model_id": request_envelope["model_id"],
                "provider_dispatch_count": 1,
                "provider_response_received": True,
                "provider_error_recorded": False,
                "output_text": output_text,
                "output_hash": replay_hash(output_text),
                "provider_metadata": safe_metadata,
                "provider_output_authority": False,
                "created_at": _require_string(created_at, "created_at"),
                "provider_invoked": True,
                "provider_request_created": True,
                "execution_authorized": True,
            }
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "provider execution failed closed"
        artifact = _base_artifact(
            {
                "artifact_type": PGSP_PROVIDER_ERROR_ENVELOPE_ARTIFACT_V1,
                "runtime_version": G5_02_RUNTIME_VERSION,
                "error_envelope_id": f"{_require_string(session_id, 'session_id')}:G5-02:PROVIDER-ERROR",
                "session_id": _require_string(session_id, "session_id"),
                "request_envelope_hash": request_envelope["artifact_hash"],
                "provider_id": request_envelope["provider_id"],
                "provider_role": request_envelope["provider_role"],
                "model_id": request_envelope["model_id"],
                "provider_dispatch_count": 1,
                "provider_response_received": False,
                "provider_error_recorded": True,
                "failure_reason": reason,
                "automatic_retry_performed": False,
                "fallback_performed": False,
                "created_at": _require_string(created_at, "created_at"),
                "provider_invoked": True,
                "provider_request_created": True,
                "execution_authorized": True,
            }
        )
    return _with_artifact_hash(artifact)


def _provider_participation_evidence_artifact(
    *,
    session_id: str,
    identity: dict[str, Any],
    result_envelope: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    success = result_envelope["artifact_type"] == PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    usage = record_provider_usage_metric(
        metric_id=f"{_require_string(session_id, 'session_id')}:G5-02:PROVIDER-USAGE",
        provider_id=identity["provider_id"],
        model=identity["model_id"],
        status="SUCCESS" if success else "FAILED_CLOSED",
        availability="AVAILABLE" if success else "FAILED_CLOSED",
        success_count=1 if success else 0,
        failure_count=0 if success else 1,
        last_used=created_at,
        last_failure=None if success else result_envelope.get("failure_reason", "provider failed closed"),
        token_usage={"input_tokens": 0, "output_tokens": 0},
        cost_tracking={"cost_tracking_status": "NOT_ESTIMATED_IN_G5_02"},
        created_at=created_at,
    )
    participation = record_cognition_participation(
        participation_id=f"{_require_string(session_id, 'session_id')}:G5-02:COGNITION-PARTICIPATION",
        provider_id=identity["provider_id"],
        participation_location="OCS_LLM_COGNITION",
        participation_role="pgsp_bound_read_only_cognition",
        workflow_id=AUTHORIZATION_SCOPE,
        invocation_reason="PGSP governed read-only cognition execution",
        purpose="cognition evidence",
        response_used=success,
        worker_invoked_after=False,
        human_confirmation_required=True,
        created_at=created_at,
    )
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_PARTICIPATION_EVIDENCE_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "participation_evidence_id": f"{_require_string(session_id, 'session_id')}:G5-02:PARTICIPATION-EVIDENCE",
            "session_id": _require_string(session_id, "session_id"),
            "provider_id": identity["provider_id"],
            "provider_role": identity["provider_role"],
            "provider_result_hash": result_envelope["artifact_hash"],
            "provider_usage_metric": usage,
            "provider_usage_metric_hash": usage["artifact_hash"],
            "cognition_participation": participation,
            "cognition_participation_hash": participation["artifact_hash"],
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": True,
            "provider_request_created": True,
            "provider_response_received": success,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _post_execution_review_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    identity: dict[str, Any],
    governance: dict[str, Any],
    result_envelope: dict[str, Any],
    participation: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    success = result_envelope["artifact_type"] == PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_POST_EXECUTION_REVIEW_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "post_execution_review_id": f"{_require_string(session_id, 'session_id')}:G5-02:POST-EXECUTION-REVIEW",
            "session_id": _require_string(session_id, "session_id"),
            "post_execution_review_status": (
                READ_ONLY_PROVIDER_COGNITION_COMPLETED if success else READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED
            ),
            "request_hash": request["artifact_hash"],
            "provider_identity_validation_hash": identity["artifact_hash"],
            "governance_checkpoint_hash": governance["artifact_hash"],
            "provider_result_hash": result_envelope["artifact_hash"],
            "participation_evidence_hash": participation["artifact_hash"],
            "provider_identity_preserved": True,
            "credential_boundary_preserved": True,
            "provider_output_non_authoritative": success,
            "read_only_boundary_preserved": True,
            "cognition_only_boundary_preserved": True,
            "worker_boundary_preserved": True,
            "mutation_boundary_preserved": True,
            "deployment_boundary_preserved": True,
            "approval_activation_performed": False,
            "authorization_activation_performed": False,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": True,
            "provider_request_created": True,
            "provider_response_received": success,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _uhcl_execution_summary_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    result_envelope: dict[str, Any],
    review: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    success = result_envelope["artifact_type"] == PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_UHCL_EXECUTION_SUMMARY_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "communication_owner": "UHCL",
            "summary_id": f"{_require_string(session_id, 'session_id')}:G5-02:UHCL-SUMMARY",
            "session_id": _require_string(session_id, "session_id"),
            "request_hash": request["artifact_hash"],
            "provider_result_hash": result_envelope["artifact_hash"],
            "post_execution_review_hash": review["artifact_hash"],
            "communication_level": "STANDARD",
            "summary_status": "READ_ONLY_PROVIDER_COGNITION_RECORDED" if success else "READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED",
            "summary_text": (
                "Read-only provider cognition evidence was recorded without mutation."
                if success
                else "Read-only provider cognition failed closed; no retry, worker execution, or mutation was performed."
            ),
            "provider_output_renderable": success,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": True,
            "provider_request_created": True,
            "provider_response_received": success,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _runtime_summary_artifact(
    *,
    session_id: str,
    request: dict[str, Any],
    identity: dict[str, Any],
    governance: dict[str, Any],
    request_envelope: dict[str, Any],
    result_envelope: dict[str, Any],
    participation: dict[str, Any],
    review: dict[str, Any],
    uhcl_summary: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    success = result_envelope["artifact_type"] == PGSP_PROVIDER_RESPONSE_ENVELOPE_ARTIFACT_V1
    artifact = _base_artifact(
        {
            "artifact_type": PGSP_PROVIDER_COGNITION_RUNTIME_SUMMARY_ARTIFACT_V1,
            "runtime_version": G5_02_RUNTIME_VERSION,
            "session_id": _require_string(session_id, "session_id"),
            "execution_status": READ_ONLY_PROVIDER_COGNITION_COMPLETED if success else READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED,
            "provider_id": identity["provider_id"],
            "provider_role": identity["provider_role"],
            "request_hash": request["artifact_hash"],
            "identity_validation_hash": identity["artifact_hash"],
            "governance_checkpoint_hash": governance["artifact_hash"],
            "request_envelope_hash": request_envelope["artifact_hash"],
            "result_envelope_hash": result_envelope["artifact_hash"],
            "participation_evidence_hash": participation["artifact_hash"],
            "post_execution_review_hash": review["artifact_hash"],
            "uhcl_summary_hash": uhcl_summary["artifact_hash"],
            "replay_reference": _require_string(replay_reference, "replay_reference"),
            "provider_dispatch_count": result_envelope["provider_dispatch_count"],
            "provider_error_recorded": not success,
            "read_only": True,
            "cognition_only": True,
            "created_at": _require_string(created_at, "created_at"),
            "provider_invoked": True,
            "provider_request_created": True,
            "provider_response_received": success,
            "execution_authorized": True,
        }
    )
    return _with_artifact_hash(artifact)


def _validated_provider_identity(artifact: dict[str, Any]) -> dict[str, Any]:
    provider = _require_mapping(artifact, "provider_identity_artifact")
    if provider.get("artifact_type") != PROVIDER_IDENTITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: invalid provider identity artifact")
    _verify_hash(provider, "artifact_hash", "G5-02 provider cognition provider identity hash mismatch")
    if provider.get("provider_role") != COGNITION_PROVIDER:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: provider role must be COGNITION_PROVIDER")
    if provider.get("credential_reference_only") is not True:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: credential must be reference only")
    for field in ("credential_secret_stored", "credential_secret_replayed", "secret_material_present"):
        if provider.get(field) is not False:
            raise FailClosedRuntimeError(f"G5-02 provider cognition failed closed: {field} must be false")
    for capability in provider.get("capability_declarations", []):
        if capability.get("execution_authority") is not False:
            raise FailClosedRuntimeError("G5-02 provider cognition failed closed: provider capability grants authority")
    _assert_secret_safe(provider)
    return deepcopy(provider)


def _validate_authorization(
    artifact: dict[str, Any],
    *,
    session_id: str,
    provider_id: str,
    provider_role: str,
) -> dict[str, Any]:
    authorization = _require_mapping(artifact, "execution_authorization_artifact")
    _verify_hash(authorization, "artifact_hash", "G5-02 provider cognition authorization hash mismatch")
    expected = {
        "authorization_status": "AUTHORIZED",
        "authorization_scope": AUTHORIZATION_SCOPE,
        "session_id": _require_string(session_id, "session_id"),
        "provider_id": _require_string(provider_id, "provider_id"),
        "provider_role": _require_string(provider_role, "provider_role"),
    }
    for field, value in expected.items():
        if authorization.get(field) != value:
            raise FailClosedRuntimeError(f"G5-02 provider cognition failed closed: invalid {field}")
    if authorization.get("read_only") is not True or authorization.get("cognition_only") is not True:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: authorization must be read-only cognition")
    if authorization.get("dispatch_attempt_limit") != 1 or authorization.get("dispatch_attempt_consumed") is not False:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: authorization must be fresh one-attempt")
    if authorization.get("approval_created") is not False or authorization.get("authorization_created") is not False:
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: runtime must not activate approval or authorization")
    _assert_secret_safe(authorization)
    return deepcopy(authorization)


def _base_artifact(values: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "provider_authority": False,
        "governance_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "mutation_authority": False,
        "deployment_authority": False,
        "replay_visible": True,
    }
    artifact.update(values)
    return artifact


def _with_artifact_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    _assert_secret_safe(artifact)
    result = deepcopy(artifact)
    result["artifact_hash"] = replay_hash(result)
    return result


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _capture(summary: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": G5_02_RUNTIME_VERSION,
        "session_id": summary["session_id"],
        "execution_status": summary["execution_status"],
        "provider_id": summary["provider_id"],
        "provider_role": summary["provider_role"],
        "provider_invoked": summary["provider_invoked"],
        "provider_dispatch_count": summary["provider_dispatch_count"],
        "provider_response_received": summary["provider_response_received"],
        "provider_error_recorded": summary["provider_error_recorded"],
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": True,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_reference": str(replay_path),
        "summary_artifact": deepcopy(summary),
        "summary_hash": summary["artifact_hash"],
        "replay_visible": True,
    }


def _ensure_replay_available(replay_path: Path) -> None:
    if replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("G5-02 provider cognition failed closed: replay directory already contains artifacts")
    replay_path.mkdir(parents=True, exist_ok=True)


def _verify_hash(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _validate_boundary_flags(artifact: dict[str, Any]) -> None:
    for field in (
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "repository_mutated",
        "deployment_performed",
        "provider_authority",
        "governance_authority",
        "approval_authority",
        "authorization_authority",
        "mutation_authority",
        "deployment_authority",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G5-02 provider cognition replay failed closed: {field} must be false")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("G5-02 provider cognition replay failed closed: replay must be visible")
    _assert_secret_safe(artifact)


def _contains_authority_claim(value: Any) -> bool:
    lowered = repr(value).lower()
    markers = (
        "i approve",
        "approved by provider",
        "execution authorized",
        "authorization granted",
        "mutation authorized",
        "deploy now",
        "invoke worker",
        "worker execution authorized",
    )
    return any(marker in lowered for marker in markers)


def _assert_secret_safe(value: Any) -> None:
    serialized = repr(value)
    lowered = serialized.lower()
    for marker in ("sk-", "bearer ", "api_key=", "api-key:", "aigol_openai_api_key="):
        if marker in lowered:
            raise FailClosedRuntimeError("G5-02 provider cognition failed closed: secret material detected")


def _safe_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"G5-02 provider cognition failed closed: {field_name} must be object")
    _assert_secret_safe(value)
    return deepcopy(value)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"G5-02 provider cognition failed closed: {field_name} must be object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"G5-02 provider cognition failed closed: {field_name} is required")
    return value.strip()
