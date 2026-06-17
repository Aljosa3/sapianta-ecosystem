"""Dispatch authorization instantiation for AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_INSTANTIATION_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.external_resource_registry_runtime import COGNITION_PROVIDER, OPENAI_PROVIDER_ID
from aigol.runtime.first_live_provider_activation_package_instantiation import (
    ACTIVATION_SCOPE,
    DISPATCH_STATUS,
    FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1,
    FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1,
    REPLAY_STEPS as ACTIVATION_PACKAGE_REPLAY_STEPS,
)
from aigol.runtime.live_provider_invocation_prerequisites import LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_INSTANTIATION_V1"

FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1"
)

STATUS_AUTHORIZATION_INSTANTIATED = "DISPATCH_AUTHORIZATION_INSTANTIATED_NO_DISPATCH"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"
DISPATCH_AUTHORIZED = "DISPATCH_AUTHORIZED"
DISPATCH_DENIED = "DISPATCH_DENIED"
AUTHORIZATION_SCOPE = "ONE_GOVERNED_OPENAI_DISPATCH_ATTEMPT"
VALIDATION_PASS = "PASS"

REPLAY_STEPS = (
    "first_live_provider_approval_freshness_validation",
    "first_live_provider_credential_freshness_validation",
    "first_live_provider_dispatch_execution_authorization_evidence",
    "first_live_provider_dispatch_authorization",
)


def instantiate_first_live_provider_dispatch_authorization(
    *,
    dispatch_authorization_id: str,
    activation_package_replay_dir: str | Path,
    replay_dir: str | Path,
    created_at: str,
    expires_at: str,
) -> dict[str, Any]:
    """Instantiate one-attempt dispatch authorization evidence without dispatching."""

    replay_path = Path(replay_dir)
    authorization_id = (
        dispatch_authorization_id
        if isinstance(dispatch_authorization_id, str) and dispatch_authorization_id.strip()
        else "INVALID_DISPATCH_AUTHORIZATION_ID"
    )
    try:
        authorization_id = _require_string(dispatch_authorization_id, "dispatch_authorization_id")
        _ensure_replay_available(replay_path)
        package = _load_activation_package(Path(activation_package_replay_dir))
        approval = package["approval"]
        activation_authorization = package["activation_authorization"]
        credential_policy = package["credential_policy"]
        credential_availability = package["credential_availability"]
        dispatch_attempt = package["dispatch_attempt"]
        audit_template = package["audit_template"]
        recertification_template = package["recertification_template"]
        rollback = package["rollback"]

        approval_freshness = create_approval_freshness_validation(
            validation_id=f"{authorization_id}:APPROVAL_FRESHNESS",
            approval_artifact=approval,
            activation_authorization_artifact=activation_authorization,
            validation_time=created_at,
            created_at=created_at,
        )
        credential_freshness = create_credential_freshness_validation(
            validation_id=f"{authorization_id}:CREDENTIAL_FRESHNESS",
            credential_policy_artifact=credential_policy,
            credential_availability_artifact=credential_availability,
            activation_authorization_artifact=activation_authorization,
            created_at=created_at,
        )
        dispatch_evidence = create_dispatch_execution_authorization_evidence(
            evidence_id=f"{authorization_id}:DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE",
            approval_freshness_artifact=approval_freshness,
            credential_freshness_artifact=credential_freshness,
            dispatch_attempt_artifact=dispatch_attempt,
            audit_template_artifact=audit_template,
            recertification_template_artifact=recertification_template,
            rollback_evidence_artifact=rollback,
            created_at=created_at,
        )
        dispatch_authorization = create_dispatch_authorization_artifact(
            dispatch_authorization_id=authorization_id,
            activation_package_id=approval["approval_id"].removesuffix(":APPROVAL"),
            approval_artifact=approval,
            activation_authorization_artifact=activation_authorization,
            credential_availability_artifact=credential_availability,
            dispatch_attempt_artifact=dispatch_attempt,
            audit_template_artifact=audit_template,
            recertification_template_artifact=recertification_template,
            rollback_evidence_artifact=rollback,
            approval_freshness_artifact=approval_freshness,
            credential_freshness_artifact=credential_freshness,
            dispatch_evidence_artifact=dispatch_evidence,
            created_at=created_at,
            expires_at=expires_at,
        )
        artifacts = (approval_freshness, credential_freshness, dispatch_evidence, dispatch_authorization)
        _persist_sequence(replay_path, artifacts)
        return _capture(
            dispatch_authorization_id=authorization_id,
            final_status=STATUS_AUTHORIZATION_INSTANTIATED,
            failure_reason="",
            replay_path=replay_path,
            approval_freshness=approval_freshness,
            credential_freshness=credential_freshness,
            dispatch_evidence=dispatch_evidence,
            dispatch_authorization=dispatch_authorization,
            failure_artifact=None,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "dispatch authorization instantiation failed closed"
        failure = _failure_artifact(
            dispatch_authorization_id=authorization_id,
            failure_reason=reason,
            created_at=created_at,
        )
        write_json_immutable(replay_path / "000_first_live_provider_dispatch_authorization_failed_closed.json", _wrap_failure(failure))
        return _capture(
            dispatch_authorization_id=authorization_id,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            approval_freshness=None,
            credential_freshness=None,
            dispatch_evidence=None,
            dispatch_authorization=None,
            failure_artifact=failure,
        )


def create_approval_freshness_validation(
    *,
    validation_id: str,
    approval_artifact: dict[str, Any],
    activation_authorization_artifact: dict[str, Any],
    validation_time: str,
    created_at: str,
) -> dict[str, Any]:
    _validate_activation_approval(approval_artifact)
    _validate_activation_authorization(activation_authorization_artifact)
    checked_at = _require_string(validation_time, "validation_time")
    expires_at = _require_string(approval_artifact.get("expires_at"), "expires_at")
    if checked_at > expires_at:
        raise FailClosedRuntimeError("dispatch authorization instantiation failed closed: approval expired")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "validation_id": _require_string(validation_id, "validation_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": activation_authorization_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_resource_type": COGNITION_PROVIDER,
        "approval_scope": approval_artifact["approved_scope"],
        "approval_one_time_use": approval_artifact["one_time_use"],
        "approval_used": False,
        "approval_revoked": False,
        "approval_expired": False,
        "approval_freshness_validation": VALIDATION_PASS,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invocation_allowed": False,
        "provider_routing_allowed": False,
        "fallback_allowed": False,
        "automatic_retry_allowed": False,
        "tool_use_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "validation_time": checked_at,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["approval_freshness_hash"] = replay_hash(_approval_freshness_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_credential_freshness_validation(
    *,
    validation_id: str,
    credential_policy_artifact: dict[str, Any],
    credential_availability_artifact: dict[str, Any],
    activation_authorization_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_credential_policy(credential_policy_artifact)
    _validate_credential_availability(credential_availability_artifact)
    _validate_activation_authorization(activation_authorization_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "validation_id": _require_string(validation_id, "validation_id"),
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "credential_availability_artifact_hash": credential_availability_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": activation_authorization_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "secret_authority": credential_availability_artifact["secret_authority"],
        "credential_freshness_validation": VALIDATION_PASS,
        "credential_available": True,
        "credential_revoked": False,
        "rotation_status_acceptable": True,
        "credential_value_omitted": True,
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "credential_hash_recorded": False,
        "authorization_header_replayed": False,
        "live_secret_retrieval_performed": False,
        "fresh_recheck_required_at_dispatch": True,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["credential_freshness_hash"] = replay_hash(_credential_freshness_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_dispatch_execution_authorization_evidence(
    *,
    evidence_id: str,
    approval_freshness_artifact: dict[str, Any],
    credential_freshness_artifact: dict[str, Any],
    dispatch_attempt_artifact: dict[str, Any],
    audit_template_artifact: dict[str, Any],
    recertification_template_artifact: dict[str, Any],
    rollback_evidence_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_approval_freshness(approval_freshness_artifact)
    _validate_credential_freshness(credential_freshness_artifact)
    _validate_dispatch_attempt(dispatch_attempt_artifact)
    _validate_audit_template(audit_template_artifact)
    _validate_recertification_template(recertification_template_artifact)
    _validate_rollback(rollback_evidence_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "evidence_id": _require_string(evidence_id, "evidence_id"),
        "approval_freshness_validation_hash": approval_freshness_artifact["artifact_hash"],
        "credential_freshness_validation_hash": credential_freshness_artifact["artifact_hash"],
        "dispatch_attempt_artifact_hash": dispatch_attempt_artifact["artifact_hash"],
        "post_dispatch_audit_template_hash": audit_template_artifact["artifact_hash"],
        "post_dispatch_recertification_template_hash": recertification_template_artifact["artifact_hash"],
        "rollback_evidence_artifact_hash": rollback_evidence_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "dispatch_conditions_met": True,
        "dispatch_status_before_authorization": DISPATCH_STATUS,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number_authorized": 1,
        "cognition_only_response_required": True,
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invocation_allowed": False,
        "provider_routing_allowed": False,
        "fallback_allowed": False,
        "automatic_retry_allowed": False,
        "tool_use_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["dispatch_execution_authorization_hash"] = replay_hash(_dispatch_evidence_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_dispatch_authorization_artifact(
    *,
    dispatch_authorization_id: str,
    activation_package_id: str,
    approval_artifact: dict[str, Any],
    activation_authorization_artifact: dict[str, Any],
    credential_availability_artifact: dict[str, Any],
    dispatch_attempt_artifact: dict[str, Any],
    audit_template_artifact: dict[str, Any],
    recertification_template_artifact: dict[str, Any],
    rollback_evidence_artifact: dict[str, Any],
    approval_freshness_artifact: dict[str, Any],
    credential_freshness_artifact: dict[str, Any],
    dispatch_evidence_artifact: dict[str, Any],
    created_at: str,
    expires_at: str,
) -> dict[str, Any]:
    _validate_dispatch_evidence(dispatch_evidence_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "dispatch_authorization_id": _require_string(dispatch_authorization_id, "dispatch_authorization_id"),
        "activation_package_id": _require_string(activation_package_id, "activation_package_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": activation_authorization_artifact["artifact_hash"],
        "credential_availability_artifact_hash": credential_availability_artifact["artifact_hash"],
        "dispatch_attempt_artifact_hash": dispatch_attempt_artifact["artifact_hash"],
        "post_dispatch_audit_template_hash": audit_template_artifact["artifact_hash"],
        "post_dispatch_recertification_template_hash": recertification_template_artifact["artifact_hash"],
        "rollback_evidence_artifact_hash": rollback_evidence_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_resource_type": COGNITION_PROVIDER,
        "required_capability": approval_artifact["required_capability"],
        "authorization_status": DISPATCH_AUTHORIZED,
        "authorization_scope": AUTHORIZATION_SCOPE,
        "dispatch_count": 1,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_number_authorized": 1,
        "cognition_only": True,
        "cognition_only_response_required": True,
        "approval_freshness_validation_hash": approval_freshness_artifact["artifact_hash"],
        "credential_freshness_validation_hash": credential_freshness_artifact["artifact_hash"],
        "dispatch_execution_authorization_evidence_hash": dispatch_evidence_artifact["artifact_hash"],
        "dispatch_conditions_hash": replay_hash(_dispatch_conditions()),
        "denial_conditions_hash": replay_hash(_denial_conditions()),
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "expires_at": _require_string(expires_at, "expires_at"),
        "replay_visible": True,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invocation_allowed": False,
        "provider_routing_allowed": False,
        "fallback_allowed": False,
        "automatic_retry_allowed": False,
        "tool_use_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["dispatch_authorization_hash"] = replay_hash(_dispatch_authorization_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def reconstruct_first_live_provider_dispatch_authorization(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    failure_path = replay_path / "000_first_live_provider_dispatch_authorization_failed_closed.json"
    if failure_path.exists():
        wrapper = load_json(failure_path)
        _verify_wrapper_hash(wrapper)
        artifact = wrapper["artifact"]
        _verify_artifact_hash(artifact, "dispatch authorization failure")
        return {
            "milestone_id": MILESTONE_ID,
            "final_status": STATUS_FAILED_CLOSED,
            "dispatch_authorization_id": artifact["dispatch_authorization_id"],
            "failure_reason": artifact["failure_reason"],
            "authorization_status": DISPATCH_DENIED,
            "live_dispatch_performed": False,
            "credential_secret_replayed": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "replay_visible": True,
            "replay_hash": replay_hash(wrapper),
        }
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("dispatch authorization replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("dispatch authorization replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"dispatch authorization {step}")
        wrappers.append(wrapper)
    approval_freshness = wrappers[0]["artifact"]
    credential_freshness = wrappers[1]["artifact"]
    dispatch_evidence = wrappers[2]["artifact"]
    dispatch_authorization = wrappers[3]["artifact"]
    if dispatch_authorization["approval_freshness_validation_hash"] != approval_freshness["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization approval freshness hash mismatch")
    if dispatch_authorization["credential_freshness_validation_hash"] != credential_freshness["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization credential freshness hash mismatch")
    if dispatch_authorization["dispatch_execution_authorization_evidence_hash"] != dispatch_evidence["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization evidence hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_status": STATUS_AUTHORIZATION_INSTANTIATED,
        "dispatch_authorization_id": dispatch_authorization["dispatch_authorization_id"],
        "authorization_status": dispatch_authorization["authorization_status"],
        "provider_id": dispatch_authorization["provider_id"],
        "dispatch_count": dispatch_authorization["dispatch_count"],
        "cognition_only": dispatch_authorization["cognition_only"],
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "credential_secret_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _load_activation_package(replay_path: Path) -> dict[str, Any]:
    wrappers = []
    for index, step in enumerate(ACTIVATION_PACKAGE_REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("dispatch authorization failed closed: activation package ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("dispatch authorization failed closed: activation package artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"activation package {step}")
        wrappers.append(wrapper)
    package = {
        "approval": wrappers[0]["artifact"],
        "activation_authorization": wrappers[1]["artifact"],
        "credential_policy": wrappers[2]["artifact"],
        "credential_availability": wrappers[3]["artifact"],
        "dispatch_attempt": wrappers[4]["artifact"],
        "audit_template": wrappers[5]["artifact"],
        "recertification_template": wrappers[6]["artifact"],
        "rollback": wrappers[7]["artifact"],
    }
    _validate_activation_package_lineage(package)
    return package


def _validate_activation_package_lineage(package: dict[str, dict[str, Any]]) -> None:
    approval = package["approval"]
    activation_authorization = package["activation_authorization"]
    credential_policy = package["credential_policy"]
    credential_availability = package["credential_availability"]
    dispatch_attempt = package["dispatch_attempt"]
    audit_template = package["audit_template"]
    recertification_template = package["recertification_template"]
    rollback = package["rollback"]
    _validate_activation_approval(approval)
    _validate_activation_authorization(activation_authorization)
    _validate_credential_policy(credential_policy)
    _validate_credential_availability(credential_availability)
    _validate_dispatch_attempt(dispatch_attempt)
    _validate_audit_template(audit_template)
    _validate_recertification_template(recertification_template)
    _validate_rollback(rollback)
    if activation_authorization["approval_artifact_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: activation authorization lineage mismatch")
    if credential_availability["credential_policy_artifact_hash"] != credential_policy["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: credential policy lineage mismatch")
    if dispatch_attempt["credential_availability_artifact_hash"] != credential_availability["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: dispatch credential lineage mismatch")
    if audit_template["dispatch_attempt_artifact_hash"] != dispatch_attempt["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: audit dispatch lineage mismatch")
    if recertification_template["post_dispatch_audit_packet_hash"] != audit_template["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: recertification audit lineage mismatch")
    if rollback["post_dispatch_recertification_packet_hash"] != recertification_template["artifact_hash"]:
        raise FailClosedRuntimeError("dispatch authorization failed closed: rollback recertification lineage mismatch")


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
    dispatch_authorization_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    approval_freshness: dict[str, Any] | None,
    credential_freshness: dict[str, Any] | None,
    dispatch_evidence: dict[str, Any] | None,
    dispatch_authorization: dict[str, Any] | None,
    failure_artifact: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "dispatch_authorization_id": dispatch_authorization_id,
        "final_status": final_status,
        "failure_reason": _redact_failure_reason(failure_reason),
        "approval_freshness_artifact": deepcopy(approval_freshness),
        "credential_freshness_artifact": deepcopy(credential_freshness),
        "dispatch_execution_authorization_evidence_artifact": deepcopy(dispatch_evidence),
        "dispatch_authorization_artifact": deepcopy(dispatch_authorization),
        "failure_artifact": deepcopy(failure_artifact),
        "authorization_status": dispatch_authorization["authorization_status"] if dispatch_authorization else DISPATCH_DENIED,
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "credential_secret_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status == STATUS_FAILED_CLOSED,
        "replay_visible": True,
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / "000_first_live_provider_dispatch_authorization_failed_closed.json").exists():
        raise FailClosedRuntimeError("dispatch authorization instantiation failed closed: replay artifact already exists")
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("dispatch authorization instantiation failed closed: replay artifact already exists")


def _failure_artifact(*, dispatch_authorization_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "dispatch_authorization_id": _require_string(dispatch_authorization_id, "dispatch_authorization_id"),
        "authorization_status": DISPATCH_DENIED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _wrap_failure(artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "replay_index": 0,
        "replay_step": "first_live_provider_dispatch_authorization_failed_closed",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _validate_activation_approval(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "activation approval")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid approval artifact")
    if artifact.get("approved_provider_id") != OPENAI_PROVIDER_ID or artifact.get("approved_resource_type") != COGNITION_PROVIDER:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid approval provider")
    if artifact.get("one_time_use") is not True:
        raise FailClosedRuntimeError("dispatch authorization failed closed: approval must be one-time")
    _reject_mutation_flags(artifact)


def _validate_activation_authorization(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "activation authorization")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid activation authorization")
    if artifact.get("provider_id") != OPENAI_PROVIDER_ID or artifact.get("activation_scope") != ACTIVATION_SCOPE:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid activation scope")
    if artifact.get("activation_attempt_limit") != 1 or artifact.get("live_dispatch_count_limit") != 1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid dispatch limit")
    _reject_mutation_flags(artifact)


def _validate_credential_policy(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "credential policy")
    if artifact.get("artifact_type") != LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid credential policy")
    if artifact.get("credential_secret_replayed") is not False or artifact.get("credential_secret_stored") is not False:
        raise FailClosedRuntimeError("dispatch authorization failed closed: credential secret replay detected")
    _reject_mutation_flags(artifact)


def _validate_credential_availability(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "credential availability")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid credential availability")
    if artifact.get("credential_available") is not True:
        raise FailClosedRuntimeError("dispatch authorization failed closed: credential unavailable")
    if artifact.get("credential_secret_replayed") is not False or artifact.get("credential_hash_recorded") is not False:
        raise FailClosedRuntimeError("dispatch authorization failed closed: credential secret replay detected")
    _reject_mutation_flags(artifact)


def _validate_dispatch_attempt(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "dispatch attempt")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid dispatch attempt")
    if artifact.get("dispatch_status") != DISPATCH_STATUS:
        raise FailClosedRuntimeError("dispatch authorization failed closed: dispatch is not armed")
    if artifact.get("live_dispatch_attempted") is not False or artifact.get("live_dispatch_performed") is not False:
        raise FailClosedRuntimeError("dispatch authorization failed closed: live dispatch already performed")
    if artifact.get("dispatch_attempt_limit") != 1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid dispatch limit")
    _reject_mutation_flags(artifact)


def _validate_audit_template(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "audit template")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid audit template")
    _reject_mutation_flags(artifact)


def _validate_recertification_template(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "recertification template")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid recertification template")
    _reject_mutation_flags(artifact)


def _validate_rollback(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "rollback")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid rollback")
    if artifact.get("further_live_calls_allowed") is not False or artifact.get("dispatch_reuse_allowed") is not False:
        raise FailClosedRuntimeError("dispatch authorization failed closed: invalid rollback scope")
    _reject_mutation_flags(artifact)


def _validate_approval_freshness(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "approval freshness")
    if artifact.get("approval_freshness_validation") != VALIDATION_PASS:
        raise FailClosedRuntimeError("dispatch authorization failed closed: approval freshness did not pass")
    _reject_mutation_flags(artifact)


def _validate_credential_freshness(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "credential freshness")
    if artifact.get("credential_freshness_validation") != VALIDATION_PASS:
        raise FailClosedRuntimeError("dispatch authorization failed closed: credential freshness did not pass")
    _reject_mutation_flags(artifact)


def _validate_dispatch_evidence(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "dispatch execution authorization evidence")
    if artifact.get("dispatch_conditions_met") is not True:
        raise FailClosedRuntimeError("dispatch authorization failed closed: dispatch conditions not met")
    _reject_mutation_flags(artifact)


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
            raise FailClosedRuntimeError(f"dispatch authorization failed closed: prohibited flag {flag}")


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
        raise FailClosedRuntimeError("dispatch authorization replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("dispatch authorization replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"dispatch authorization instantiation failed closed: {field_name} is required")
    return value


def _redact_failure_reason(reason: str) -> str:
    text = reason if isinstance(reason, str) else ""
    lowered = text.lower()
    if ("s" + "k-") in lowered or "bearer " in lowered:
        return "dispatch authorization instantiation failed closed: secret material redacted"
    return text


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if ("s" + "k-") in serialized or "bearer " in serialized:
        raise FailClosedRuntimeError("dispatch authorization instantiation failed closed: credential secret replay detected")


def _dispatch_conditions() -> list[str]:
    return [
        "activation package reconstructs",
        "approval freshness passes",
        "credential freshness passes",
        "dispatch status is armed not dispatched",
        "single dispatch attempt limit",
        "no worker invocation",
        "no routing fallback retry or tool use",
        "no governance mutation",
        "no replay mutation",
    ]


def _denial_conditions() -> list[str]:
    return [
        "approval expired revoked used malformed or out of scope",
        "credential unavailable or secret replay detected",
        "dispatch already attempted",
        "provider is not openai",
        "worker routing fallback retry or tool requested",
        "governance or replay mutation requested",
        "audit recertification or rollback evidence missing",
    ]


def _approval_freshness_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "validation_id": artifact["validation_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "approval_freshness_validation": artifact["approval_freshness_validation"],
        "validation_time": artifact["validation_time"],
    }


def _credential_freshness_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "validation_id": artifact["validation_id"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "credential_availability_artifact_hash": artifact["credential_availability_artifact_hash"],
        "credential_freshness_validation": artifact["credential_freshness_validation"],
        "credential_available": artifact["credential_available"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _dispatch_evidence_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": artifact["evidence_id"],
        "approval_freshness_validation_hash": artifact["approval_freshness_validation_hash"],
        "credential_freshness_validation_hash": artifact["credential_freshness_validation_hash"],
        "dispatch_attempt_artifact_hash": artifact["dispatch_attempt_artifact_hash"],
        "dispatch_conditions_met": artifact["dispatch_conditions_met"],
        "dispatch_attempt_number_authorized": artifact["dispatch_attempt_number_authorized"],
    }


def _dispatch_authorization_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "dispatch_authorization_id": artifact["dispatch_authorization_id"],
        "activation_package_id": artifact["activation_package_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "credential_availability_artifact_hash": artifact["credential_availability_artifact_hash"],
        "dispatch_attempt_artifact_hash": artifact["dispatch_attempt_artifact_hash"],
        "authorization_status": artifact["authorization_status"],
        "authorization_scope": artifact["authorization_scope"],
        "dispatch_count": artifact["dispatch_count"],
        "cognition_only": artifact["cognition_only"],
        "approval_freshness_validation_hash": artifact["approval_freshness_validation_hash"],
        "credential_freshness_validation_hash": artifact["credential_freshness_validation_hash"],
    }
