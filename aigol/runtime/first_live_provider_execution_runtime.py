"""First governed live provider execution runtime for AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.cognition_artifact_runtime import LLM_COGNITION_ARTIFACT_V1
from aigol.runtime.external_resource_registry_runtime import COGNITION_PROVIDER, OPENAI_PROVIDER_ID
from aigol.runtime.first_live_provider_activation_package_instantiation import (
    FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    AUTHORIZATION_SCOPE,
    DISPATCH_AUTHORIZED,
    FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1,
    _load_activation_package,
)
from aigol.runtime.live_provider_invocation_prerequisites import (
    create_live_provider_credential_policy,
    create_live_provider_invocation_approval,
)
from aigol.runtime.live_provider_runtime_boundary import (
    STATUS_COMPLETED as BOUNDARY_STATUS_COMPLETED,
    run_live_provider_runtime_boundary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_RUNTIME_V1"

FIRST_LIVE_PROVIDER_EXECUTION_APPROVAL_REVALIDATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_EXECUTION_APPROVAL_REVALIDATION_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_EXECUTION_CREDENTIAL_REVALIDATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_EXECUTION_CREDENTIAL_REVALIDATION_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1 = "FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1"
FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1 = "FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1"

STATUS_COMPLETED = "DISPATCH_EXECUTION_COMPLETED"
STATUS_FAILED_CLOSED = "DISPATCH_EXECUTION_FAILED_CLOSED"
STATUS_ABORTED_PRE_REQUEST = "DISPATCH_EXECUTION_ABORTED_PRE_REQUEST"

ROLLBACK_NOT_REQUIRED = "ROLLBACK_NOT_REQUIRED"
ROLLBACK_EXECUTED = "ROLLBACK_EXECUTED"

REPLAY_STEPS = (
    "first_live_provider_execution_approval_revalidation",
    "first_live_provider_execution_credential_revalidation",
    "first_live_provider_live_transport_execution_evidence",
    "first_live_provider_llm_cognition_artifact",
    "first_live_provider_post_dispatch_audit_packet",
    "first_live_provider_post_dispatch_recertification_packet",
    "first_live_provider_rollback_execution",
    "first_live_provider_dispatch_execution_packet",
)

BoundaryTransport = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def run_first_live_provider_execution_runtime(
    *,
    execution_id: str,
    human_request: str,
    created_at: str,
    replay_dir: str | Path,
    activation_package_replay_dir: str | Path,
    dispatch_authorization_artifact: dict[str, Any],
    transport: BoundaryTransport | None,
    model: str = "gpt-5.1",
    timeout_seconds: int = 20,
    live_transport_enabled: bool = False,
) -> dict[str, Any]:
    """Execute one authorized OpenAI dispatch attempt through the governed boundary."""

    replay_path = Path(replay_dir)
    execution = execution_id if isinstance(execution_id, str) and execution_id.strip() else "INVALID_EXECUTION_ID"
    approval_revalidation: dict[str, Any] | None = None
    credential_revalidation: dict[str, Any] | None = None
    transport_evidence: dict[str, Any] | None = None
    cognition_artifact: dict[str, Any] | None = None
    post_dispatch_audit: dict[str, Any] | None = None
    recertification: dict[str, Any] | None = None
    rollback: dict[str, Any] | None = None
    execution_packet: dict[str, Any] | None = None
    try:
        execution = _require_string(execution_id, "execution_id")
        _ensure_replay_available(replay_path)
        dispatch_authorization = _validate_dispatch_authorization(dispatch_authorization_artifact, created_at)
        activation_package = _load_activation_package(Path(activation_package_replay_dir))
        _validate_authorization_lineage(dispatch_authorization, activation_package)

        approval_revalidation = create_execution_approval_revalidation(
            revalidation_id=f"{execution}:APPROVAL_REVALIDATION",
            dispatch_authorization_artifact=dispatch_authorization,
            approval_artifact=activation_package["approval"],
            created_at=created_at,
        )
        credential_revalidation = create_execution_credential_revalidation(
            revalidation_id=f"{execution}:CREDENTIAL_REVALIDATION",
            dispatch_authorization_artifact=dispatch_authorization,
            credential_policy_artifact=activation_package["credential_policy"],
            credential_availability_artifact=activation_package["credential_availability"],
            created_at=created_at,
        )
        approval_view = create_live_provider_invocation_approval(
            approval_id=f"{execution}:LIVE_PROVIDER_APPROVAL_VIEW",
            provider_id=OPENAI_PROVIDER_ID,
            required_capability=dispatch_authorization["required_capability"],
            runtime_path=MILESTONE_ID,
            replay_dir_reference=str(replay_path / "live_provider_boundary"),
            approved_by=activation_package["approval"]["approved_by"],
            created_at=created_at,
            expires_at=dispatch_authorization["expires_at"],
        )
        credential_policy_view = create_live_provider_credential_policy(
            policy_id=f"{execution}:LIVE_PROVIDER_CREDENTIAL_POLICY_VIEW",
            provider_id=OPENAI_PROVIDER_ID,
            credential_reference="env:AIGOL_OPENAI_API_KEY",
            created_at=created_at,
        )
        boundary = run_live_provider_runtime_boundary(
            invocation_id=f"{execution}:OPENAI_DISPATCH_ATTEMPT_1",
            human_request=human_request,
            created_at=created_at,
            replay_dir=replay_path / "live_provider_boundary",
            approval_artifact=approval_view,
            credential_policy_artifact=credential_policy_view,
            model=model,
            timeout_seconds=timeout_seconds,
            transport=transport,
            live_transport_enabled=live_transport_enabled,
        )
        transport_evidence = create_live_transport_execution_evidence(
            evidence_id=f"{execution}:LIVE_TRANSPORT_EVIDENCE",
            boundary_capture=boundary,
            created_at=created_at,
        )
        if boundary["final_status"] != BOUNDARY_STATUS_COMPLETED:
            raise FailClosedRuntimeError(boundary["failure_reason"] or "first live provider execution failed closed")
        cognition_artifact = create_execution_llm_cognition_artifact(
            cognition_artifact_id=f"{execution}:LLM_COGNITION_ARTIFACT",
            canonical_output_artifact=boundary["canonical_provider_output"],
            transport_evidence_artifact=transport_evidence,
            created_at=created_at,
        )
        post_dispatch_audit = create_post_dispatch_audit_packet(
            audit_packet_id=f"{execution}:POST_DISPATCH_AUDIT",
            final_status=STATUS_COMPLETED,
            failure_reason="",
            dispatch_authorization_artifact=dispatch_authorization,
            approval_revalidation_artifact=approval_revalidation,
            credential_revalidation_artifact=credential_revalidation,
            transport_evidence_artifact=transport_evidence,
            cognition_artifact=cognition_artifact,
            audit_template_artifact=activation_package["audit_template"],
            created_at=created_at,
        )
        recertification = create_post_dispatch_recertification_packet(
            recertification_id=f"{execution}:POST_DISPATCH_RECERTIFICATION",
            final_status=STATUS_COMPLETED,
            post_dispatch_audit_artifact=post_dispatch_audit,
            recertification_template_artifact=activation_package["recertification_template"],
            created_at=created_at,
        )
        rollback = create_rollback_execution_artifact(
            rollback_id=f"{execution}:ROLLBACK",
            final_status=STATUS_COMPLETED,
            rollback_reason="",
            rollback_required=False,
            rollback_template_artifact=activation_package["rollback"],
            post_dispatch_audit_artifact=post_dispatch_audit,
            recertification_artifact=recertification,
            created_at=created_at,
        )
        execution_packet = create_dispatch_execution_packet(
            execution_packet_id=f"{execution}:DISPATCH_EXECUTION_PACKET",
            final_status=STATUS_COMPLETED,
            failure_reason="",
            dispatch_authorization_artifact=dispatch_authorization,
            approval_revalidation_artifact=approval_revalidation,
            credential_revalidation_artifact=credential_revalidation,
            transport_evidence_artifact=transport_evidence,
            cognition_artifact=cognition_artifact,
            post_dispatch_audit_artifact=post_dispatch_audit,
            recertification_artifact=recertification,
            rollback_execution_artifact=rollback,
            created_at=created_at,
        )
        _persist_sequence(
            replay_path,
            (
                approval_revalidation,
                credential_revalidation,
                transport_evidence,
                cognition_artifact,
                post_dispatch_audit,
                recertification,
                rollback,
                execution_packet,
            ),
        )
        return _capture(
            execution_id=execution,
            final_status=STATUS_COMPLETED,
            failure_reason="",
            replay_path=replay_path,
            approval_revalidation=approval_revalidation,
            credential_revalidation=credential_revalidation,
            transport_evidence=transport_evidence,
            cognition_artifact=cognition_artifact,
            post_dispatch_audit=post_dispatch_audit,
            recertification=recertification,
            rollback=rollback,
            execution_packet=execution_packet,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "first live provider execution failed closed"
        if transport_evidence is None:
            transport_evidence = create_failed_live_transport_execution_evidence(
                evidence_id=f"{execution}:LIVE_TRANSPORT_EVIDENCE",
                failure_reason=reason,
                created_at=created_at,
            )
        if cognition_artifact is None:
            cognition_artifact = create_failed_execution_llm_cognition_artifact(
                cognition_artifact_id=f"{execution}:LLM_COGNITION_ARTIFACT",
                failure_reason=reason,
                transport_evidence_artifact=transport_evidence,
                created_at=created_at,
            )
        if post_dispatch_audit is None:
            post_dispatch_audit = create_failed_post_dispatch_audit_packet(
                audit_packet_id=f"{execution}:POST_DISPATCH_AUDIT",
                failure_reason=reason,
                transport_evidence_artifact=transport_evidence,
                cognition_artifact=cognition_artifact,
                created_at=created_at,
            )
        if recertification is None:
            recertification = create_post_dispatch_recertification_packet(
                recertification_id=f"{execution}:POST_DISPATCH_RECERTIFICATION",
                final_status=STATUS_FAILED_CLOSED,
                post_dispatch_audit_artifact=post_dispatch_audit,
                recertification_template_artifact=None,
                created_at=created_at,
            )
        if rollback is None:
            rollback = create_rollback_execution_artifact(
                rollback_id=f"{execution}:ROLLBACK",
                final_status=STATUS_FAILED_CLOSED,
                rollback_reason=reason,
                rollback_required=True,
                rollback_template_artifact=None,
                post_dispatch_audit_artifact=post_dispatch_audit,
                recertification_artifact=recertification,
                created_at=created_at,
            )
        if execution_packet is None:
            safe_authorization = (
                deepcopy(dispatch_authorization_artifact) if isinstance(dispatch_authorization_artifact, dict) else None
            )
            execution_packet = create_dispatch_execution_packet(
                execution_packet_id=f"{execution}:DISPATCH_EXECUTION_PACKET",
                final_status=STATUS_FAILED_CLOSED,
                failure_reason=reason,
                dispatch_authorization_artifact=safe_authorization,
                approval_revalidation_artifact=approval_revalidation,
                credential_revalidation_artifact=credential_revalidation,
                transport_evidence_artifact=transport_evidence,
                cognition_artifact=cognition_artifact,
                post_dispatch_audit_artifact=post_dispatch_audit,
                recertification_artifact=recertification,
                rollback_execution_artifact=rollback,
                created_at=created_at,
            )
        failure_artifacts = (
            approval_revalidation or _placeholder_artifact(
                artifact_type=FIRST_LIVE_PROVIDER_EXECUTION_APPROVAL_REVALIDATION_ARTIFACT_V1,
                artifact_id=f"{execution}:APPROVAL_REVALIDATION",
                failure_reason=reason,
                created_at=created_at,
            ),
            credential_revalidation or _placeholder_artifact(
                artifact_type=FIRST_LIVE_PROVIDER_EXECUTION_CREDENTIAL_REVALIDATION_ARTIFACT_V1,
                artifact_id=f"{execution}:CREDENTIAL_REVALIDATION",
                failure_reason=reason,
                created_at=created_at,
            ),
            transport_evidence,
            cognition_artifact,
            post_dispatch_audit,
            recertification,
            rollback,
            execution_packet,
        )
        if not _replay_exists(replay_path):
            _persist_sequence(replay_path, failure_artifacts)
        return _capture(
            execution_id=execution,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            approval_revalidation=approval_revalidation,
            credential_revalidation=credential_revalidation,
            transport_evidence=transport_evidence,
            cognition_artifact=cognition_artifact,
            post_dispatch_audit=post_dispatch_audit,
            recertification=recertification,
            rollback=rollback,
            execution_packet=execution_packet,
        )


def create_execution_approval_revalidation(
    *,
    revalidation_id: str,
    dispatch_authorization_artifact: dict[str, Any],
    approval_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    dispatch_authorization = _validate_dispatch_authorization(dispatch_authorization_artifact, created_at)
    _verify_artifact_hash(approval_artifact, "activation approval")
    if approval_artifact.get("artifact_hash") != dispatch_authorization["approval_artifact_hash"]:
        raise FailClosedRuntimeError("first live provider execution failed closed: approval lineage mismatch")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_EXECUTION_APPROVAL_REVALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "revalidation_id": _require_string(revalidation_id, "revalidation_id"),
        "dispatch_authorization_artifact_hash": dispatch_authorization["artifact_hash"],
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "approval_freshness_revalidation": "PASS",
        "approval_one_time_use": True,
        "approval_used_before_dispatch": False,
        "approval_revoked": False,
        "approval_expired": False,
        "dispatch_attempt_limit": 1,
        "replay_visible": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_execution_credential_revalidation(
    *,
    revalidation_id: str,
    dispatch_authorization_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    credential_availability_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    dispatch_authorization = _validate_dispatch_authorization(dispatch_authorization_artifact, created_at)
    _verify_artifact_hash(credential_policy_artifact, "credential policy")
    _verify_artifact_hash(credential_availability_artifact, "credential availability")
    if credential_availability_artifact.get("credential_available") is not True:
        raise FailClosedRuntimeError("first live provider execution failed closed: credential unavailable")
    reference = _require_string(credential_policy_artifact.get("credential_reference"), "credential_reference")
    if not reference.startswith("env:"):
        raise FailClosedRuntimeError("first live provider execution failed closed: unsupported credential reference")
    env_name = "AIGOL_OPENAI_API_KEY" if reference == "env:OPENAI_PROVIDER_CREDENTIAL" else reference.removeprefix("env:")
    credential_present = isinstance(os.environ.get(env_name), str) and bool(os.environ.get(env_name, "").strip())
    if not credential_present:
        raise FailClosedRuntimeError("first live provider execution failed closed: credential unavailable")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_EXECUTION_CREDENTIAL_REVALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "revalidation_id": _require_string(revalidation_id, "revalidation_id"),
        "dispatch_authorization_artifact_hash": dispatch_authorization["artifact_hash"],
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "credential_availability_artifact_hash": credential_availability_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_freshness_revalidation": "PASS",
        "credential_available": True,
        "credential_reference_type": "env",
        "credential_value_omitted": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "credential_hash_recorded": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_live_transport_execution_evidence(
    *,
    evidence_id: str,
    boundary_capture: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    boundary = deepcopy(boundary_capture)
    audit = boundary.get("live_boundary_audit_artifact")
    if not isinstance(audit, dict):
        raise FailClosedRuntimeError("first live provider execution failed closed: missing live boundary audit")
    _verify_artifact_hash(audit, "live boundary audit")
    request = boundary.get("live_request_envelope_artifact")
    response = boundary.get("live_response_envelope_artifact")
    error = boundary.get("live_error_envelope_artifact")
    live_provider_call_performed = boundary.get("live_provider_call_performed") is True
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "evidence_id": _require_string(evidence_id, "evidence_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "boundary_runtime": boundary.get("milestone_id"),
        "boundary_final_status": boundary.get("final_status"),
        "boundary_failure_reason": _redact_failure_reason(boundary.get("failure_reason", "")),
        "credential_retrieval_artifact_hash": _artifact_hash_or_none(boundary.get("credential_retrieval_artifact")),
        "credential_use_boundary_artifact_hash": _artifact_hash_or_none(boundary.get("credential_use_boundary_artifact")),
        "request_artifact_hash": _artifact_hash_or_none(request),
        "response_artifact_hash": _artifact_hash_or_none(response),
        "error_artifact_hash": _artifact_hash_or_none(error),
        "canonical_provider_output_hash": _artifact_hash_or_none(boundary.get("canonical_provider_output")),
        "live_provider_boundary_audit_hash": audit["artifact_hash"],
        "live_provider_call_performed": live_provider_call_performed,
        "deterministic_or_injected_transport_used": live_provider_call_performed is not True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "provider_invoked": boundary.get("provider_invoked") is True,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": boundary.get("final_status") != BOUNDARY_STATUS_COMPLETED,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_live_transport_execution_evidence(
    *, evidence_id: str, failure_reason: str, created_at: str
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "evidence_id": _require_string(evidence_id, "evidence_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "boundary_final_status": STATUS_FAILED_CLOSED,
        "boundary_failure_reason": _redact_failure_reason(failure_reason),
        "request_artifact_hash": None,
        "response_artifact_hash": None,
        "error_artifact_hash": None,
        "canonical_provider_output_hash": None,
        "live_provider_call_performed": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": True,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_execution_llm_cognition_artifact(
    *,
    cognition_artifact_id: str,
    canonical_output_artifact: dict[str, Any],
    transport_evidence_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(canonical_output_artifact, "canonical provider output")
    _verify_artifact_hash(transport_evidence_artifact, "transport evidence")
    response_text = _require_string(canonical_output_artifact.get("response_text"), "response_text")
    provider_invoked = transport_evidence_artifact.get("live_provider_call_performed") is True
    artifact = {
        "artifact_type": LLM_COGNITION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "cognition_artifact_id": _require_string(cognition_artifact_id, "cognition_artifact_id"),
        "cognition_artifact_status": "COMPLETED",
        "provider_id": OPENAI_PROVIDER_ID,
        "source_canonical_output_artifact_hash": canonical_output_artifact["artifact_hash"],
        "transport_evidence_artifact_hash": transport_evidence_artifact["artifact_hash"],
        "response_text": response_text,
        "response_text_hash": replay_hash(response_text),
        "untrusted_provider_output_normalized": True,
        "non_authoritative": True,
        "human_review_required": True,
        "authority_flags": {
            "provider_authority": False,
            "approval_authority": False,
            "execution_authority": False,
            "worker_authority": False,
            "governance_authority": False,
            "replay_authority": False,
        },
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "replay_visible": True,
        "provider_invoked": provider_invoked,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_execution_llm_cognition_artifact(
    *,
    cognition_artifact_id: str,
    failure_reason: str,
    transport_evidence_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(transport_evidence_artifact, "transport evidence")
    artifact = {
        "artifact_type": LLM_COGNITION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "cognition_artifact_id": _require_string(cognition_artifact_id, "cognition_artifact_id"),
        "cognition_artifact_status": "FAILED_CLOSED",
        "provider_id": OPENAI_PROVIDER_ID,
        "failure_reason": _redact_failure_reason(failure_reason),
        "transport_evidence_artifact_hash": transport_evidence_artifact["artifact_hash"],
        "untrusted_provider_output_normalized": False,
        "non_authoritative": True,
        "human_review_required": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_post_dispatch_audit_packet(
    *,
    audit_packet_id: str,
    final_status: str,
    failure_reason: str,
    dispatch_authorization_artifact: dict[str, Any],
    approval_revalidation_artifact: dict[str, Any],
    credential_revalidation_artifact: dict[str, Any],
    transport_evidence_artifact: dict[str, Any],
    cognition_artifact: dict[str, Any],
    audit_template_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(audit_template_artifact, "post-dispatch audit template")
    if audit_template_artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1:
        raise FailClosedRuntimeError("first live provider execution failed closed: invalid audit template")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "audit_packet_id": _require_string(audit_packet_id, "audit_packet_id"),
        "final_status": _require_string(final_status, "final_status"),
        "failure_reason": _redact_failure_reason(failure_reason),
        "dispatch_authorization_artifact_hash": dispatch_authorization_artifact["artifact_hash"],
        "approval_revalidation_artifact_hash": approval_revalidation_artifact["artifact_hash"],
        "credential_revalidation_artifact_hash": credential_revalidation_artifact["artifact_hash"],
        "transport_evidence_artifact_hash": transport_evidence_artifact["artifact_hash"],
        "cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "audit_template_artifact_hash": audit_template_artifact["artifact_hash"],
        "audit_verdict": "PASS" if final_status == STATUS_COMPLETED else "FAILED_CLOSED",
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_failed_post_dispatch_audit_packet(
    *,
    audit_packet_id: str,
    failure_reason: str,
    transport_evidence_artifact: dict[str, Any],
    cognition_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "audit_packet_id": _require_string(audit_packet_id, "audit_packet_id"),
        "final_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "transport_evidence_artifact_hash": transport_evidence_artifact["artifact_hash"],
        "cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "audit_verdict": "FAILED_CLOSED",
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_post_dispatch_recertification_packet(
    *,
    recertification_id: str,
    final_status: str,
    post_dispatch_audit_artifact: dict[str, Any],
    recertification_template_artifact: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(post_dispatch_audit_artifact, "post-dispatch audit")
    if recertification_template_artifact is not None:
        _verify_artifact_hash(recertification_template_artifact, "post-dispatch recertification template")
        if (
            recertification_template_artifact.get("artifact_type")
            != FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1
        ):
            raise FailClosedRuntimeError("first live provider execution failed closed: invalid recertification template")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "recertification_id": _require_string(recertification_id, "recertification_id"),
        "final_status": _require_string(final_status, "final_status"),
        "post_dispatch_audit_artifact_hash": post_dispatch_audit_artifact["artifact_hash"],
        "recertification_template_artifact_hash": (
            recertification_template_artifact["artifact_hash"] if recertification_template_artifact else None
        ),
        "recertification_verdict": "PASS" if final_status == STATUS_COMPLETED else "FAILED_CLOSED",
        "further_live_dispatch_blocked_without_new_authorization": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_rollback_execution_artifact(
    *,
    rollback_id: str,
    final_status: str,
    rollback_reason: str,
    rollback_required: bool,
    rollback_template_artifact: dict[str, Any] | None,
    post_dispatch_audit_artifact: dict[str, Any],
    recertification_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _verify_artifact_hash(post_dispatch_audit_artifact, "post-dispatch audit")
    _verify_artifact_hash(recertification_artifact, "post-dispatch recertification")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "rollback_id": _require_string(rollback_id, "rollback_id"),
        "rollback_status": ROLLBACK_EXECUTED if rollback_required else ROLLBACK_NOT_REQUIRED,
        "final_status": _require_string(final_status, "final_status"),
        "rollback_reason": _redact_failure_reason(rollback_reason),
        "rollback_template_artifact_hash": _artifact_hash_or_none(rollback_template_artifact),
        "post_dispatch_audit_artifact_hash": post_dispatch_audit_artifact["artifact_hash"],
        "post_dispatch_recertification_artifact_hash": recertification_artifact["artifact_hash"],
        "activation_reuse_allowed": False,
        "dispatch_reuse_allowed": False,
        "credential_reuse_allowed": False,
        "additional_live_dispatch_allowed": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_dispatch_execution_packet(
    *,
    execution_packet_id: str,
    final_status: str,
    failure_reason: str,
    dispatch_authorization_artifact: dict[str, Any] | None,
    approval_revalidation_artifact: dict[str, Any] | None,
    credential_revalidation_artifact: dict[str, Any] | None,
    transport_evidence_artifact: dict[str, Any],
    cognition_artifact: dict[str, Any],
    post_dispatch_audit_artifact: dict[str, Any],
    recertification_artifact: dict[str, Any],
    rollback_execution_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    status = _require_string(final_status, "final_status")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1,
        "runtime_version": MILESTONE_ID,
        "execution_packet_id": _require_string(execution_packet_id, "execution_packet_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_resource_type": COGNITION_PROVIDER,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number": 1,
        "execution_status": status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "dispatch_authorization_artifact_hash": _artifact_hash_or_none(dispatch_authorization_artifact),
        "approval_revalidation_artifact_hash": _artifact_hash_or_none(approval_revalidation_artifact),
        "credential_revalidation_artifact_hash": _artifact_hash_or_none(credential_revalidation_artifact),
        "transport_evidence_artifact_hash": transport_evidence_artifact["artifact_hash"],
        "cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "post_dispatch_audit_packet_hash": post_dispatch_audit_artifact["artifact_hash"],
        "post_dispatch_recertification_packet_hash": recertification_artifact["artifact_hash"],
        "rollback_execution_artifact_hash": rollback_execution_artifact["artifact_hash"],
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def reconstruct_first_live_provider_execution_runtime_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("first live provider execution replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("first live provider execution replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"first live provider execution {step}")
        wrappers.append(wrapper)
    packet = wrappers[-1]["artifact"]
    return {
        "milestone_id": MILESTONE_ID,
        "execution_packet_id": packet["execution_packet_id"],
        "final_status": packet["execution_status"],
        "provider_id": packet["provider_id"],
        "dispatch_attempt_limit": packet["dispatch_attempt_limit"],
        "dispatch_attempt_number": packet["dispatch_attempt_number"],
        "credential_secret_replayed": packet["credential_secret_replayed"],
        "authorization_header_replayed": packet["authorization_header_replayed"],
        "worker_invoked": packet["worker_invoked"],
        "governance_modified": packet["governance_modified"],
        "replay_modified": packet["replay_modified"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_dispatch_authorization(artifact: dict[str, Any], created_at: str) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first live provider execution failed closed: missing dispatch authorization")
    _verify_artifact_hash(artifact, "dispatch authorization")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("first live provider execution failed closed: invalid dispatch authorization")
    if artifact.get("authorization_status") != DISPATCH_AUTHORIZED:
        raise FailClosedRuntimeError("first live provider execution failed closed: dispatch not authorized")
    if artifact.get("authorization_scope") != AUTHORIZATION_SCOPE:
        raise FailClosedRuntimeError("first live provider execution failed closed: invalid dispatch scope")
    if artifact.get("provider_id") != OPENAI_PROVIDER_ID or artifact.get("provider_resource_type") != COGNITION_PROVIDER:
        raise FailClosedRuntimeError("first live provider execution failed closed: unauthorized provider")
    if artifact.get("dispatch_count") != 1 or artifact.get("dispatch_attempt_limit") != 1:
        raise FailClosedRuntimeError("first live provider execution failed closed: invalid dispatch count")
    if artifact.get("cognition_only") is not True or artifact.get("cognition_only_response_required") is not True:
        raise FailClosedRuntimeError("first live provider execution failed closed: cognition-only authorization required")
    if artifact.get("live_dispatch_attempted") is not False or artifact.get("live_dispatch_performed") is not False:
        raise FailClosedRuntimeError("first live provider execution failed closed: authorization already used")
    if _require_string(created_at, "created_at") > _require_string(artifact.get("expires_at"), "expires_at"):
        raise FailClosedRuntimeError("first live provider execution failed closed: dispatch authorization expired")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def _validate_authorization_lineage(dispatch_authorization: dict[str, Any], activation_package: dict[str, Any]) -> None:
    if dispatch_authorization["approval_artifact_hash"] != activation_package["approval"]["artifact_hash"]:
        raise FailClosedRuntimeError("first live provider execution failed closed: approval lineage mismatch")
    if dispatch_authorization["credential_availability_artifact_hash"] != activation_package["credential_availability"][
        "artifact_hash"
    ]:
        raise FailClosedRuntimeError("first live provider execution failed closed: credential lineage mismatch")
    if dispatch_authorization["post_dispatch_audit_template_hash"] != activation_package["audit_template"]["artifact_hash"]:
        raise FailClosedRuntimeError("first live provider execution failed closed: audit template lineage mismatch")
    if (
        dispatch_authorization["post_dispatch_recertification_template_hash"]
        != activation_package["recertification_template"]["artifact_hash"]
    ):
        raise FailClosedRuntimeError("first live provider execution failed closed: recertification template lineage mismatch")
    if dispatch_authorization["rollback_evidence_artifact_hash"] != activation_package["rollback"]["artifact_hash"]:
        raise FailClosedRuntimeError("first live provider execution failed closed: rollback lineage mismatch")


def _persist_sequence(replay_path: Path, artifacts: tuple[dict[str, Any], ...]) -> None:
    for index, (step, artifact) in enumerate(zip(REPLAY_STEPS, artifacts, strict=True)):
        _verify_artifact_hash(artifact, step)
        wrapper = {
            "replay_index": index,
            "replay_step": step,
            "artifact": deepcopy(artifact),
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _capture(
    *,
    execution_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    approval_revalidation: dict[str, Any] | None,
    credential_revalidation: dict[str, Any] | None,
    transport_evidence: dict[str, Any],
    cognition_artifact: dict[str, Any],
    post_dispatch_audit: dict[str, Any],
    recertification: dict[str, Any],
    rollback: dict[str, Any],
    execution_packet: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "execution_id": execution_id,
        "final_status": final_status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "approval_revalidation_artifact": deepcopy(approval_revalidation),
        "credential_revalidation_artifact": deepcopy(credential_revalidation),
        "live_transport_execution_evidence_artifact": deepcopy(transport_evidence),
        "llm_cognition_artifact": deepcopy(cognition_artifact),
        "post_dispatch_audit_packet_artifact": deepcopy(post_dispatch_audit),
        "post_dispatch_recertification_packet_artifact": deepcopy(recertification),
        "rollback_execution_artifact": deepcopy(rollback),
        "dispatch_execution_packet": deepcopy(execution_packet),
        "provider_id": OPENAI_PROVIDER_ID,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number": 1,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "replay_visible": True,
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _placeholder_artifact(*, artifact_type: str, artifact_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": _require_string(artifact_type, "artifact_type"),
        "runtime_version": MILESTONE_ID,
        "artifact_id": _require_string(artifact_id, "artifact_id"),
        "final_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("first live provider execution failed closed: replay artifact already exists")


def _replay_exists(replay_path: Path) -> bool:
    return any((replay_path / f"{index:03d}_{step}.json").exists() for index, step in enumerate(REPLAY_STEPS))


def _artifact_hash_or_none(artifact: Any) -> str | None:
    if artifact is None:
        return None
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("first live provider execution failed closed: artifact reference must be object")
    _verify_artifact_hash(artifact, "referenced artifact")
    return artifact["artifact_hash"]


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("first live provider execution replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("first live provider execution replay hash mismatch")


def _reject_mutation_flags(artifact: dict[str, Any]) -> None:
    for key in (
        "credential_secret_replayed",
        "authorization_header_replayed",
        "worker_invoked",
        "governance_modified",
        "replay_modified",
        "worker_invocation_allowed",
        "provider_routing_allowed",
        "fallback_allowed",
        "automatic_retry_allowed",
        "tool_use_allowed",
        "governance_mutation_allowed",
        "replay_mutation_allowed",
    ):
        if artifact.get(key) is True:
            raise FailClosedRuntimeError(f"first live provider execution failed closed: forbidden flag {key}")


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if "sk-" in serialized or "bearer " in serialized or "api_key" in serialized:
        raise FailClosedRuntimeError("first live provider execution failed closed: credential secret replay detected")


def _redact_failure_reason(value: Any) -> str:
    reason = value if isinstance(value, str) else ""
    if not reason:
        return ""
    if "sk-" in reason.lower() or "bearer " in reason.lower() or "api_key" in reason.lower():
        return "redacted credential-bearing failure"
    return reason


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"first live provider execution failed closed: {field_name} is required")
    return value
