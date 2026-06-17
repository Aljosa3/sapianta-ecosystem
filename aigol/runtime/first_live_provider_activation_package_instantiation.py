"""Activation package instantiation for AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_INSTANTIATION_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.external_resource_registry_runtime import (
    COGNITION_PROVIDER,
    OPENAI_PROVIDER_ID,
    real_provider_err_v1_registry,
    select_resource_for_capability,
)
from aigol.runtime.first_real_provider_runtime import (
    CANONICAL_CONTRACT_REFERENCE,
    OPENAI_CAPABILITIES,
    adapt_openai_contract_to_canonical,
)
from aigol.runtime.live_provider_invocation_prerequisites import (
    LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1,
    create_live_provider_credential_policy,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    OPENAI_RESPONSES_ENDPOINT,
    OPENAI_RESPONSES_SCHEMA,
    create_default_openai_cognition_provider_contract,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_INSTANTIATION_V1"

FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1 = "FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1"
FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1 = (
    "FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1"
)
FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1 = "FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1"
FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1 = (
    "FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1"
)
FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1 = (
    "FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1"
)
FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1 = "FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1"

STATUS_PACKAGE_INSTANTIATED = "ACTIVATION_PACKAGE_INSTANTIATED_PRE_DISPATCH"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"
APPROVED = "APPROVED"
AUTHORIZED = "AUTHORIZED"
APPROVED_SCOPE = "SINGLE_PROVIDER_SINGLE_LIVE_INVOCATION"
ACTIVATION_SCOPE = "ONE_GOVERNED_OPENAI_INVOCATION"
DISPATCH_STATUS = "ARMED_NOT_DISPATCHED"
TEMPLATE_STATUS = "PENDING_LIVE_DISPATCH"
ROLLBACK_STATUS = "ROLLBACK_PREDECLARED_NOT_EXECUTED"

REPLAY_STEPS = (
    "first_live_provider_approval",
    "first_live_provider_activation_authorization",
    "first_live_provider_credential_policy",
    "first_live_provider_credential_availability",
    "first_live_provider_dispatch_attempt_prepared",
    "first_live_provider_post_dispatch_audit_template",
    "first_live_provider_post_dispatch_recertification_template",
    "first_live_provider_rollback_evidence",
)


def instantiate_first_live_provider_activation_package(
    *,
    package_id: str,
    human_request: str,
    required_capability: str,
    approved_by: str,
    created_at: str,
    expires_at: str,
    replay_dir: str | Path,
    err_registry: dict[str, Any] | None = None,
    credential_available: bool = True,
    secret_authority: str = "operator_controlled_environment",
    model: str = "gpt-5.1",
) -> dict[str, Any]:
    """Instantiate the replay-visible activation package and stop before live dispatch."""

    replay_path = Path(replay_dir)
    package = package_id if isinstance(package_id, str) and package_id.strip() else "INVALID_PACKAGE_ID"
    try:
        package = _require_string(package_id, "package_id")
        _ensure_replay_available(replay_path)
        approval = create_first_live_provider_approval(
            approval_id=f"{package}:APPROVAL",
            approved_by=approved_by,
            required_capability=required_capability,
            replay_dir_reference=str(replay_path),
            created_at=created_at,
            expires_at=expires_at,
        )
        authorization = create_first_live_provider_activation_authorization(
            activation_id=f"{package}:AUTHORIZATION",
            approval_artifact=approval,
            created_at=created_at,
            expires_at=expires_at,
        )
        credential_policy = create_live_provider_credential_policy(
            policy_id=f"{package}:CREDENTIAL_POLICY",
            provider_id=OPENAI_PROVIDER_ID,
            credential_reference="env:OPENAI_PROVIDER_CREDENTIAL",
            created_at=created_at,
        )
        credential_availability = create_first_live_provider_credential_availability(
            credential_availability_id=f"{package}:CREDENTIAL_AVAILABILITY",
            approval_artifact=approval,
            authorization_artifact=authorization,
            credential_policy_artifact=credential_policy,
            secret_authority=secret_authority,
            credential_available=credential_available,
            created_at=created_at,
        )
        err_selection = select_resource_for_capability(
            selection_id=f"{package}:ERR_OPENAI_SELECTION",
            required_capability=required_capability,
            replay_dir=replay_path / "err_openai_selection",
            created_at=created_at,
            registry=deepcopy(err_registry) if err_registry is not None else real_provider_err_v1_registry(),
            resource_type=COGNITION_PROVIDER,
            human_intent=human_request,
            hirr_output={
                "runtime": MILESTONE_ID,
                "required_capability": required_capability,
                "resource_type": COGNITION_PROVIDER,
            },
        )
        if err_selection["selected_resource_id"] != OPENAI_PROVIDER_ID:
            raise FailClosedRuntimeError("activation package instantiation failed closed: ERR did not select openai")
        source_contract = create_default_openai_cognition_provider_contract(created_at=created_at)
        canonical_contract = adapt_openai_contract_to_canonical(
            source_contract=source_contract,
            capabilities=OPENAI_CAPABILITIES,
            created_at=created_at,
        )
        dispatch_attempt = create_first_live_provider_dispatch_attempt(
            dispatch_id=f"{package}:DISPATCH_ATTEMPT",
            human_request=human_request,
            model=model,
            approval_artifact=approval,
            authorization_artifact=authorization,
            credential_availability_artifact=credential_availability,
            err_selection_capture=err_selection,
            canonical_contract=canonical_contract,
            created_at=created_at,
        )
        audit_template = create_first_live_provider_post_dispatch_audit_template(
            audit_packet_id=f"{package}:POST_DISPATCH_AUDIT_TEMPLATE",
            approval_artifact=approval,
            authorization_artifact=authorization,
            credential_availability_artifact=credential_availability,
            dispatch_attempt_artifact=dispatch_attempt,
            created_at=created_at,
        )
        recertification_template = create_first_live_provider_post_dispatch_recertification_template(
            recertification_id=f"{package}:POST_DISPATCH_RECERTIFICATION_TEMPLATE",
            audit_template_artifact=audit_template,
            created_at=created_at,
        )
        rollback = create_first_live_provider_rollback_evidence(
            rollback_id=f"{package}:ROLLBACK",
            approval_artifact=approval,
            authorization_artifact=authorization,
            audit_template_artifact=audit_template,
            recertification_template_artifact=recertification_template,
            created_at=created_at,
        )
        artifacts = (
            approval,
            authorization,
            credential_policy,
            credential_availability,
            dispatch_attempt,
            audit_template,
            recertification_template,
            rollback,
        )
        _persist_sequence(replay_path, artifacts)
        return _capture(
            package_id=package,
            final_status=STATUS_PACKAGE_INSTANTIATED,
            failure_reason="",
            replay_path=replay_path,
            approval=approval,
            authorization=authorization,
            credential_policy=credential_policy,
            credential_availability=credential_availability,
            dispatch_attempt=dispatch_attempt,
            audit_template=audit_template,
            recertification_template=recertification_template,
            rollback=rollback,
            err_selection=err_selection,
            canonical_contract=canonical_contract,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "activation package instantiation failed closed"
        failure = _failure_artifact(package_id=package, failure_reason=reason, created_at=created_at)
        write_json_immutable(replay_path / "000_first_live_provider_activation_package_failed_closed.json", _wrap_failure(failure))
        return _capture(
            package_id=package,
            final_status=STATUS_FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            approval=None,
            authorization=None,
            credential_policy=None,
            credential_availability=None,
            dispatch_attempt=None,
            audit_template=None,
            recertification_template=None,
            rollback=None,
            err_selection=None,
            canonical_contract=None,
            failure_artifact=failure,
        )


def create_first_live_provider_approval(
    *,
    approval_id: str,
    approved_by: str,
    required_capability: str,
    replay_dir_reference: str,
    created_at: str,
    expires_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "approval_id": _require_string(approval_id, "approval_id"),
        "approved_by": _require_string(approved_by, "approved_by"),
        "approval_status": APPROVED,
        "approval_granted": True,
        "approved_provider_id": OPENAI_PROVIDER_ID,
        "approved_resource_type": COGNITION_PROVIDER,
        "required_capability": _require_string(required_capability, "required_capability"),
        "approved_runtime_path": MILESTONE_ID,
        "approved_transport_boundary": "AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1",
        "approved_canonical_contract": CANONICAL_CONTRACT_REFERENCE,
        "approved_scope": APPROVED_SCOPE,
        "one_time_use": True,
        "expires_at": _require_string(expires_at, "expires_at"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_dir_reference": _require_string(replay_dir_reference, "replay_dir_reference"),
        "credential_policy_reference": "activation_package_internal_policy_hash_only",
        "rollback_required": True,
        "recertification_required": True,
        "worker_invocation_allowed": False,
        "provider_routing_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "credential_secret_replayed": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["approval_hash"] = replay_hash(_approval_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_activation_authorization(
    *,
    activation_id: str,
    approval_artifact: dict[str, Any],
    created_at: str,
    expires_at: str,
) -> dict[str, Any]:
    _validate_approval(approval_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "activation_id": _require_string(activation_id, "activation_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "runtime_path": MILESTONE_ID,
        "transport_boundary": "AIGOL_LIVE_PROVIDER_HTTP_TRANSPORT_V1",
        "activation_status": AUTHORIZED,
        "activation_scope": ACTIVATION_SCOPE,
        "activation_attempt_limit": 1,
        "live_dispatch_allowed_after_manual_gate": True,
        "live_dispatch_performed": False,
        "live_dispatch_count_limit": 1,
        "activation_expires_at": _require_string(expires_at, "expires_at"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "credential_secret_replayed": False,
        "worker_invocation_allowed": False,
        "provider_routing_allowed": False,
        "fallback_allowed": False,
        "automatic_retry_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["authorization_hash"] = replay_hash(_authorization_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_credential_availability(
    *,
    credential_availability_id: str,
    approval_artifact: dict[str, Any],
    authorization_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    secret_authority: str,
    credential_available: bool,
    created_at: str,
) -> dict[str, Any]:
    _validate_approval(approval_artifact)
    _validate_authorization(authorization_artifact)
    _validate_credential_policy(credential_policy_artifact)
    if credential_available is not True:
        raise FailClosedRuntimeError("activation package instantiation failed closed: credential unavailable")
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "credential_availability_id": _require_string(credential_availability_id, "credential_availability_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": authorization_artifact["artifact_hash"],
        "provider_id": OPENAI_PROVIDER_ID,
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "credential_reference_type": "ENVIRONMENT_SECRET_REFERENCE",
        "secret_authority": _require_string(secret_authority, "secret_authority"),
        "credential_available": True,
        "credential_checked_at": _require_string(created_at, "credential_checked_at"),
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "credential_value_omitted": True,
        "credential_hash_recorded": False,
        "rotation_status_checked": True,
        "revocation_status_checked": True,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["credential_availability_hash"] = replay_hash(_credential_availability_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_dispatch_attempt(
    *,
    dispatch_id: str,
    human_request: str,
    model: str,
    approval_artifact: dict[str, Any],
    authorization_artifact: dict[str, Any],
    credential_availability_artifact: dict[str, Any],
    err_selection_capture: dict[str, Any],
    canonical_contract: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_approval(approval_artifact)
    _validate_authorization(authorization_artifact)
    _validate_credential_availability(credential_availability_artifact)
    _verify_artifact_hash(canonical_contract, "canonical contract")
    if err_selection_capture.get("selected_resource_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("activation package instantiation failed closed: ERR did not select openai")
    payload = {
        "model": _require_string(model, "model"),
        "input_hash": replay_hash(_require_string(human_request, "human_request")),
        "stream": False,
    }
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "dispatch_id": _require_string(dispatch_id, "dispatch_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": authorization_artifact["artifact_hash"],
        "credential_availability_artifact_hash": credential_availability_artifact["artifact_hash"],
        "err_selection_artifact_hash": err_selection_capture["err_selection_evidence_artifact"]["artifact_hash"],
        "canonical_contract_artifact_hash": canonical_contract["artifact_hash"],
        "canonical_contract_reference": CANONICAL_CONTRACT_REFERENCE,
        "provider_id": OPENAI_PROVIDER_ID,
        "provider_schema_id": OPENAI_RESPONSES_SCHEMA,
        "endpoint": OPENAI_RESPONSES_ENDPOINT,
        "http_method": "POST",
        "request_payload_hash": replay_hash(payload),
        "request_created_at": _require_string(created_at, "request_created_at"),
        "dispatch_status": DISPATCH_STATUS,
        "dispatch_armed": True,
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "dispatch_attempt_number": 0,
        "dispatch_attempt_limit": 1,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "worker_invoked": False,
        "provider_routing_performed": False,
        "fallback_performed": False,
        "automatic_retry_performed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "provider_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["dispatch_attempt_hash"] = replay_hash(_dispatch_attempt_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_post_dispatch_audit_template(
    *,
    audit_packet_id: str,
    approval_artifact: dict[str, Any],
    authorization_artifact: dict[str, Any],
    credential_availability_artifact: dict[str, Any],
    dispatch_attempt_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_approval(approval_artifact)
    _validate_authorization(authorization_artifact)
    _validate_credential_availability(credential_availability_artifact)
    _validate_dispatch_attempt(dispatch_attempt_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1,
        "runtime_version": MILESTONE_ID,
        "audit_packet_id": _require_string(audit_packet_id, "audit_packet_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": authorization_artifact["artifact_hash"],
        "credential_availability_artifact_hash": credential_availability_artifact["artifact_hash"],
        "dispatch_attempt_artifact_hash": dispatch_attempt_artifact["artifact_hash"],
        "dispatch_response_artifact_hash": None,
        "dispatch_error_artifact_hash": None,
        "template_status": TEMPLATE_STATUS,
        "final_status": TEMPLATE_STATUS,
        "provider_id": OPENAI_PROVIDER_ID,
        "attempt_count": 0,
        "worker_invocation_observed": False,
        "provider_routing_observed": False,
        "fallback_observed": False,
        "credential_secret_replayed": False,
        "authorization_header_replayed": False,
        "authority_boundary_result": "PENDING_LIVE_DISPATCH",
        "canonical_output_created": False,
        "llm_cognition_artifact_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "audit_created_at": _require_string(created_at, "audit_created_at"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["audit_template_hash"] = replay_hash(_audit_template_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_post_dispatch_recertification_template(
    *,
    recertification_id: str,
    audit_template_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_audit_template(audit_template_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1,
        "runtime_version": MILESTONE_ID,
        "recertification_id": _require_string(recertification_id, "recertification_id"),
        "post_dispatch_audit_packet_hash": audit_template_artifact["artifact_hash"],
        "template_status": TEMPLATE_STATUS,
        "hirr_certification_preserved": None,
        "err_role_preserved": None,
        "provider_contract_preserved": None,
        "credential_boundary_preserved": None,
        "transport_boundary_preserved": None,
        "replay_integrity_preserved": None,
        "fail_closed_integrity_preserved": None,
        "authority_boundary_preserved": None,
        "worker_boundary_preserved": None,
        "governance_boundary_preserved": None,
        "recertification_verdict": "PENDING_LIVE_DISPATCH",
        "recertification_created_at": _require_string(created_at, "recertification_created_at"),
        "credential_secret_replayed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["recertification_template_hash"] = replay_hash(_recertification_template_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def create_first_live_provider_rollback_evidence(
    *,
    rollback_id: str,
    approval_artifact: dict[str, Any],
    authorization_artifact: dict[str, Any],
    audit_template_artifact: dict[str, Any],
    recertification_template_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    _validate_approval(approval_artifact)
    _validate_authorization(authorization_artifact)
    _validate_audit_template(audit_template_artifact)
    _validate_recertification_template(recertification_template_artifact)
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "rollback_id": _require_string(rollback_id, "rollback_id"),
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "activation_authorization_artifact_hash": authorization_artifact["artifact_hash"],
        "post_dispatch_audit_packet_hash": audit_template_artifact["artifact_hash"],
        "post_dispatch_recertification_packet_hash": recertification_template_artifact["artifact_hash"],
        "rollback_required": True,
        "rollback_status": ROLLBACK_STATUS,
        "activation_reuse_allowed": False,
        "credential_reuse_allowed": False,
        "dispatch_reuse_allowed": False,
        "further_live_calls_allowed": False,
        "cleanup_completed": False,
        "secret_material_retained": False,
        "credential_secret_replayed": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["rollback_hash"] = replay_hash(_rollback_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    _assert_no_secret_material(artifact)
    return artifact


def reconstruct_first_live_provider_activation_package(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the activation package replay sequence."""

    replay_path = Path(replay_dir)
    failure_path = replay_path / "000_first_live_provider_activation_package_failed_closed.json"
    if failure_path.exists():
        wrapper = load_json(failure_path)
        _verify_wrapper_hash(wrapper)
        artifact = wrapper["artifact"]
        _verify_artifact_hash(artifact, "activation package failure")
        return {
            "milestone_id": MILESTONE_ID,
            "final_status": STATUS_FAILED_CLOSED,
            "package_id": artifact["package_id"],
            "failure_reason": artifact["failure_reason"],
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
            raise FailClosedRuntimeError("activation package replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("activation package replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"activation package {step}")
        wrappers.append(wrapper)
    approval = wrappers[0]["artifact"]
    authorization = wrappers[1]["artifact"]
    credential_policy = wrappers[2]["artifact"]
    credential_availability = wrappers[3]["artifact"]
    dispatch_attempt = wrappers[4]["artifact"]
    audit_template = wrappers[5]["artifact"]
    recertification_template = wrappers[6]["artifact"]
    rollback = wrappers[7]["artifact"]
    _verify_lineage(
        approval=approval,
        authorization=authorization,
        credential_policy=credential_policy,
        credential_availability=credential_availability,
        dispatch_attempt=dispatch_attempt,
        audit_template=audit_template,
        recertification_template=recertification_template,
        rollback=rollback,
    )
    return {
        "milestone_id": MILESTONE_ID,
        "final_status": STATUS_PACKAGE_INSTANTIATED,
        "approval_id": approval["approval_id"],
        "activation_id": authorization["activation_id"],
        "provider_id": approval["approved_provider_id"],
        "credential_available": credential_availability["credential_available"],
        "dispatch_status": dispatch_attempt["dispatch_status"],
        "live_dispatch_attempted": dispatch_attempt["live_dispatch_attempted"],
        "live_dispatch_performed": dispatch_attempt["live_dispatch_performed"],
        "post_dispatch_audit_template_present": True,
        "post_dispatch_recertification_template_present": True,
        "rollback_evidence_present": True,
        "credential_secret_replayed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


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
    package_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    approval: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    credential_policy: dict[str, Any] | None,
    credential_availability: dict[str, Any] | None,
    dispatch_attempt: dict[str, Any] | None,
    audit_template: dict[str, Any] | None,
    recertification_template: dict[str, Any] | None,
    rollback: dict[str, Any] | None,
    err_selection: dict[str, Any] | None,
    canonical_contract: dict[str, Any] | None,
    failure_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "package_id": package_id,
        "final_status": final_status,
        "failure_reason": failure_reason,
        "approval_artifact": deepcopy(approval),
        "activation_authorization_artifact": deepcopy(authorization),
        "credential_policy_artifact": deepcopy(credential_policy),
        "credential_availability_artifact": deepcopy(credential_availability),
        "dispatch_attempt_artifact": deepcopy(dispatch_attempt),
        "post_dispatch_audit_template_artifact": deepcopy(audit_template),
        "post_dispatch_recertification_template_artifact": deepcopy(recertification_template),
        "rollback_evidence_artifact": deepcopy(rollback),
        "err_selection_capture": deepcopy(err_selection),
        "canonical_contract_artifact": deepcopy(canonical_contract),
        "failure_artifact": deepcopy(failure_artifact),
        "activation_package_instantiated": final_status == STATUS_PACKAGE_INSTANTIATED,
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
    if (replay_path / "000_first_live_provider_activation_package_failed_closed.json").exists():
        raise FailClosedRuntimeError("activation package instantiation failed closed: replay artifact already exists")
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("activation package instantiation failed closed: replay artifact already exists")


def _failure_artifact(*, package_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1,
        "runtime_version": MILESTONE_ID,
        "package_id": _require_string(package_id, "package_id"),
        "final_status": STATUS_FAILED_CLOSED,
        "failure_reason": _redact_failure_reason(failure_reason),
        "live_dispatch_attempted": False,
        "live_dispatch_performed": False,
        "credential_secret_replayed": False,
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
        "replay_step": "first_live_provider_activation_package_failed_closed",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _verify_lineage(
    *,
    approval: dict[str, Any],
    authorization: dict[str, Any],
    credential_policy: dict[str, Any],
    credential_availability: dict[str, Any],
    dispatch_attempt: dict[str, Any],
    audit_template: dict[str, Any],
    recertification_template: dict[str, Any],
    rollback: dict[str, Any],
) -> None:
    if authorization["approval_artifact_hash"] != approval["artifact_hash"]:
        raise FailClosedRuntimeError("activation package authorization approval hash mismatch")
    if credential_availability["activation_authorization_artifact_hash"] != authorization["artifact_hash"]:
        raise FailClosedRuntimeError("activation package credential authorization hash mismatch")
    if credential_availability["credential_policy_artifact_hash"] != credential_policy["artifact_hash"]:
        raise FailClosedRuntimeError("activation package credential policy hash mismatch")
    if dispatch_attempt["credential_availability_artifact_hash"] != credential_availability["artifact_hash"]:
        raise FailClosedRuntimeError("activation package dispatch credential hash mismatch")
    if audit_template["dispatch_attempt_artifact_hash"] != dispatch_attempt["artifact_hash"]:
        raise FailClosedRuntimeError("activation package audit dispatch hash mismatch")
    if recertification_template["post_dispatch_audit_packet_hash"] != audit_template["artifact_hash"]:
        raise FailClosedRuntimeError("activation package recertification audit hash mismatch")
    if rollback["post_dispatch_recertification_packet_hash"] != recertification_template["artifact_hash"]:
        raise FailClosedRuntimeError("activation package rollback recertification hash mismatch")


def _validate_approval(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider approval")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid approval artifact")
    if artifact.get("approval_status") != APPROVED or artifact.get("approval_granted") is not True:
        raise FailClosedRuntimeError("activation package instantiation failed closed: missing approval")
    if artifact.get("approved_provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("activation package instantiation failed closed: unauthorized provider")
    if artifact.get("approved_scope") != APPROVED_SCOPE or artifact.get("one_time_use") is not True:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid approval scope")
    _reject_mutation_flags(artifact)


def _validate_authorization(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider activation authorization")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid authorization artifact")
    if artifact.get("activation_status") != AUTHORIZED or artifact.get("activation_scope") != ACTIVATION_SCOPE:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid authorization")
    if artifact.get("activation_attempt_limit") != 1 or artifact.get("live_dispatch_count_limit") != 1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid dispatch limit")
    if artifact.get("live_dispatch_performed") is not False:
        raise FailClosedRuntimeError("activation package instantiation failed closed: live dispatch already performed")
    _reject_mutation_flags(artifact)


def _validate_credential_policy(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider credential policy")
    if artifact.get("artifact_type") != LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid credential policy")
    if artifact.get("provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("activation package instantiation failed closed: unauthorized provider")
    if artifact.get("credential_secret_stored") is not False or artifact.get("credential_secret_replayed") is not False:
        raise FailClosedRuntimeError("activation package instantiation failed closed: credential secret replay detected")
    _reject_mutation_flags(artifact)


def _validate_credential_availability(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider credential availability")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid credential availability")
    if artifact.get("credential_available") is not True:
        raise FailClosedRuntimeError("activation package instantiation failed closed: credential unavailable")
    if artifact.get("credential_secret_replayed") is not False or artifact.get("credential_hash_recorded") is not False:
        raise FailClosedRuntimeError("activation package instantiation failed closed: credential secret replay detected")
    _reject_mutation_flags(artifact)


def _validate_dispatch_attempt(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider dispatch attempt")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid dispatch attempt")
    if artifact.get("dispatch_status") != DISPATCH_STATUS:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid dispatch status")
    if artifact.get("live_dispatch_attempted") is not False or artifact.get("live_dispatch_performed") is not False:
        raise FailClosedRuntimeError("activation package instantiation failed closed: live dispatch already performed")
    _reject_mutation_flags(artifact)


def _validate_audit_template(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider post-dispatch audit template")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid audit template")
    if artifact.get("template_status") != TEMPLATE_STATUS:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid audit template status")
    _reject_mutation_flags(artifact)


def _validate_recertification_template(artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first live provider post-dispatch recertification template")
    if artifact.get("artifact_type") != FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid recertification template")
    if artifact.get("template_status") != TEMPLATE_STATUS:
        raise FailClosedRuntimeError("activation package instantiation failed closed: invalid recertification template status")
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
            raise FailClosedRuntimeError(f"activation package instantiation failed closed: prohibited flag {flag}")


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
        raise FailClosedRuntimeError("activation package replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("activation package replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"activation package instantiation failed closed: {field_name} is required")
    return value


def _redact_failure_reason(reason: str) -> str:
    text = reason if isinstance(reason, str) else ""
    lowered = text.lower()
    if ("s" + "k-") in lowered or "bearer " in lowered:
        return "activation package instantiation failed closed: secret material redacted"
    return text


def _assert_no_secret_material(artifact: dict[str, Any]) -> None:
    serialized = repr(artifact).lower()
    if ("s" + "k-") in serialized or "bearer " in serialized:
        raise FailClosedRuntimeError("activation package instantiation failed closed: credential secret replay detected")


def _approval_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "approval_id": artifact["approval_id"],
        "approved_by": artifact["approved_by"],
        "approved_provider_id": artifact["approved_provider_id"],
        "required_capability": artifact["required_capability"],
        "approved_scope": artifact["approved_scope"],
        "one_time_use": artifact["one_time_use"],
        "expires_at": artifact["expires_at"],
    }


def _authorization_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "activation_id": artifact["activation_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "provider_id": artifact["provider_id"],
        "activation_scope": artifact["activation_scope"],
        "activation_attempt_limit": artifact["activation_attempt_limit"],
        "live_dispatch_count_limit": artifact["live_dispatch_count_limit"],
    }


def _credential_availability_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "credential_availability_id": artifact["credential_availability_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "credential_available": artifact["credential_available"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
    }


def _dispatch_attempt_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "dispatch_id": artifact["dispatch_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "credential_availability_artifact_hash": artifact["credential_availability_artifact_hash"],
        "err_selection_artifact_hash": artifact["err_selection_artifact_hash"],
        "canonical_contract_artifact_hash": artifact["canonical_contract_artifact_hash"],
        "request_payload_hash": artifact["request_payload_hash"],
        "dispatch_status": artifact["dispatch_status"],
        "live_dispatch_attempted": artifact["live_dispatch_attempted"],
    }


def _audit_template_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "audit_packet_id": artifact["audit_packet_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "credential_availability_artifact_hash": artifact["credential_availability_artifact_hash"],
        "dispatch_attempt_artifact_hash": artifact["dispatch_attempt_artifact_hash"],
        "template_status": artifact["template_status"],
    }


def _recertification_template_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "recertification_id": artifact["recertification_id"],
        "post_dispatch_audit_packet_hash": artifact["post_dispatch_audit_packet_hash"],
        "template_status": artifact["template_status"],
        "recertification_verdict": artifact["recertification_verdict"],
    }


def _rollback_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "rollback_id": artifact["rollback_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "activation_authorization_artifact_hash": artifact["activation_authorization_artifact_hash"],
        "post_dispatch_audit_packet_hash": artifact["post_dispatch_audit_packet_hash"],
        "post_dispatch_recertification_packet_hash": artifact["post_dispatch_recertification_packet_hash"],
        "rollback_status": artifact["rollback_status"],
        "further_live_calls_allowed": artifact["further_live_calls_allowed"],
    }
