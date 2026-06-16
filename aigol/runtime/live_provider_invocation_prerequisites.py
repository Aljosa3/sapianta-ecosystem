"""Pre-live governance prerequisites for AIGOL_LIVE_PROVIDER_INVOCATION_PREREQUISITES_V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.external_resource_registry_runtime import COGNITION_PROVIDER, OPENAI_PROVIDER_ID
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_LIVE_PROVIDER_INVOCATION_PREREQUISITES_V1"

LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1 = "LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1"
LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1 = "LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1"
LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1 = "LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1"
LIVE_PROVIDER_REPLAY_ENVELOPE_ARTIFACT_V1 = "LIVE_PROVIDER_REPLAY_ENVELOPE_ARTIFACT_V1"
LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1 = "LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1"
LIVE_PROVIDER_ABORT_MARKER_ARTIFACT_V1 = "LIVE_PROVIDER_ABORT_MARKER_ARTIFACT_V1"

APPROVED = "APPROVED"
FAILED_CLOSED = "FAILED_CLOSED"
ABORTED_PRE_INVOCATION = "ABORTED_PRE_INVOCATION"
PASS = "PASS"
FAIL = "FAIL"

APPROVED_SCOPE = "SINGLE_PROVIDER_SINGLE_RUNTIME_VALIDATION"

REPLAY_STEPS = (
    "live_provider_invocation_approval",
    "live_provider_credential_policy",
    "live_provider_transport_boundary",
    "live_provider_replay_envelope",
    "live_provider_audit_packet",
    "live_provider_abort_marker",
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
)


def create_live_provider_invocation_approval(
    *,
    approval_id: str,
    provider_id: str,
    required_capability: str,
    runtime_path: str,
    replay_dir_reference: str,
    approved_by: str,
    created_at: str,
    expires_at: str,
    approval_status: str = APPROVED,
    approval_granted: bool = True,
) -> dict[str, Any]:
    """Create a replay-visible approval artifact without authorizing workers or governance mutation."""

    provider = _require_string(provider_id, "provider_id")
    artifact = {
        "artifact_type": LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "approval_id": _require_string(approval_id, "approval_id"),
        "approval_status": _require_string(approval_status, "approval_status"),
        "approval_granted": approval_granted is True,
        "approved_provider_id": provider,
        "approved_scope": APPROVED_SCOPE,
        "required_capability": _require_string(required_capability, "required_capability"),
        "runtime_path": _require_string(runtime_path, "runtime_path"),
        "canonical_contract_version": "AIGOL_CANONICAL_PROVIDER_CONTRACT_V1",
        "replay_dir_reference": _require_string(replay_dir_reference, "replay_dir_reference"),
        "credential_policy_required": True,
        "allowed_prompt_boundary": "single governed cognition request",
        "allowed_provider_output_boundary": "non-authoritative cognition only",
        "time_bounded": True,
        "revocable": True,
        "non_transferable": True,
        "approved_by": _require_string(approved_by, "approved_by"),
        "created_at": _require_string(created_at, "created_at"),
        "expires_at": _require_string(expires_at, "expires_at"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["approval_hash"] = replay_hash(_approval_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_provider_credential_policy(
    *,
    policy_id: str,
    provider_id: str,
    credential_reference: str,
    created_at: str,
    secret_present: bool = False,
) -> dict[str, Any]:
    """Create a secret-free credential policy placeholder."""

    reference = _require_string(credential_reference, "credential_reference")
    if _looks_like_secret(reference) or secret_present is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: credential policy must not store secrets")
    artifact = {
        "artifact_type": LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "policy_id": _require_string(policy_id, "policy_id"),
        "provider_id": _require_openai_provider(provider_id),
        "credential_reference": reference,
        "credential_secret_stored": False,
        "credential_secret_replayed": False,
        "secret_material_present": False,
        "retrieval_boundary": "external_secret_reference_only",
        "redaction_required": True,
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
    artifact["policy_hash"] = replay_hash(_credential_policy_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_transport_boundary(
    *,
    boundary_id: str,
    provider_id: str,
    created_at: str,
    transport_enabled: bool = False,
) -> dict[str, Any]:
    """Create a live transport boundary artifact that does not invoke OpenAI."""

    if transport_enabled is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: transport invocation is not implemented")
    artifact = {
        "artifact_type": LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "boundary_id": _require_string(boundary_id, "boundary_id"),
        "provider_id": _require_openai_provider(provider_id),
        "provider_role": COGNITION_PROVIDER,
        "transport_boundary": "openai_live_transport_placeholder",
        "transport_enabled": False,
        "live_provider_call_performed": False,
        "authentication_implemented": False,
        "request_payload_created": False,
        "response_payload_captured": False,
        "timeout_handling_required": True,
        "transport_failure_fail_closed": True,
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
    artifact["boundary_hash"] = replay_hash(_transport_boundary_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_replay_envelope(
    *,
    invocation_id: str,
    approval_artifact: dict[str, Any],
    credential_policy_artifact: dict[str, Any],
    transport_boundary_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create the pre-live replay envelope for a governed live invocation attempt."""

    _validate_approval(approval_artifact)
    _validate_credential_policy(credential_policy_artifact)
    _validate_transport_boundary(transport_boundary_artifact)
    artifact = {
        "artifact_type": LIVE_PROVIDER_REPLAY_ENVELOPE_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": _require_string(invocation_id, "invocation_id"),
        "provider_id": OPENAI_PROVIDER_ID,
        "required_capability": approval_artifact["required_capability"],
        "approval_artifact_hash": approval_artifact["artifact_hash"],
        "credential_policy_artifact_hash": credential_policy_artifact["artifact_hash"],
        "transport_boundary_artifact_hash": transport_boundary_artifact["artifact_hash"],
        "pre_invocation_replay_ready": True,
        "invocation_attempt_recorded": True,
        "live_provider_call_performed": False,
        "live_response_captured": False,
        "abort_required_before_live_call": True,
        "credential_secret_replayed": False,
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
    artifact["envelope_hash"] = replay_hash(_replay_envelope_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def create_live_audit_packet(
    *,
    audit_id: str,
    replay_envelope_artifact: dict[str, Any],
    final_status: str,
    failure_reason: str,
    created_at: str,
) -> dict[str, Any]:
    """Create an audit packet for the pre-live invocation prerequisite run."""

    _verify_artifact_hash(replay_envelope_artifact, "live replay envelope")
    status = _require_string(final_status, "final_status")
    if status not in {ABORTED_PRE_INVOCATION, FAILED_CLOSED}:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: audit status must be pre-live terminal")
    artifact = {
        "artifact_type": LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "audit_id": _require_string(audit_id, "audit_id"),
        "invocation_id": replay_envelope_artifact["invocation_id"],
        "provider_id": replay_envelope_artifact["provider_id"],
        "audit_verdict": PASS if status == ABORTED_PRE_INVOCATION else FAIL,
        "final_status": status,
        "failure_reason": failure_reason,
        "approval_artifact_hash": replay_envelope_artifact["approval_artifact_hash"],
        "credential_policy_artifact_hash": replay_envelope_artifact["credential_policy_artifact_hash"],
        "transport_boundary_artifact_hash": replay_envelope_artifact["transport_boundary_artifact_hash"],
        "replay_envelope_artifact_hash": replay_envelope_artifact["artifact_hash"],
        "live_provider_call_performed": False,
        "credential_secret_replayed": False,
        "no_worker_invocation": True,
        "no_governance_mutation": True,
        "no_replay_mutation": True,
        "replay_reconstruction_required_before_live_call": True,
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


def create_live_abort_marker(
    *,
    abort_id: str,
    replay_envelope_artifact: dict[str, Any],
    audit_packet_artifact: dict[str, Any],
    abort_reason: str,
    created_at: str,
) -> dict[str, Any]:
    """Create an explicit rollback/abort marker preserving replay evidence."""

    _verify_artifact_hash(replay_envelope_artifact, "live replay envelope")
    _verify_artifact_hash(audit_packet_artifact, "live audit packet")
    artifact = {
        "artifact_type": LIVE_PROVIDER_ABORT_MARKER_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "abort_id": _require_string(abort_id, "abort_id"),
        "invocation_id": replay_envelope_artifact["invocation_id"],
        "provider_id": replay_envelope_artifact["provider_id"],
        "abort_status": ABORTED_PRE_INVOCATION,
        "abort_reason": _require_string(abort_reason, "abort_reason"),
        "replay_envelope_artifact_hash": replay_envelope_artifact["artifact_hash"],
        "audit_packet_artifact_hash": audit_packet_artifact["artifact_hash"],
        "live_provider_call_performed": False,
        "rollback_marker_created": True,
        "approval_revocation_required_before_retry": True,
        "deterministic_provider_path_preserved": True,
        "replay_evidence_preserved": True,
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
    artifact["abort_hash"] = replay_hash(_abort_hash_input(artifact))
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def prepare_live_provider_invocation_prerequisites(
    *,
    invocation_id: str,
    created_at: str,
    replay_dir: str | Path,
    approval_artifact: dict[str, Any] | None,
    credential_policy_artifact: dict[str, Any] | None,
    provider_id: str = OPENAI_PROVIDER_ID,
    transport_failure: bool = False,
    provider_output_preview: str | None = None,
) -> dict[str, Any]:
    """Prepare pre-live artifacts and abort before any real OpenAI call."""

    replay_path = Path(replay_dir)
    invocation = _require_string(invocation_id, "invocation_id")
    envelope: dict[str, Any] | None = None
    audit: dict[str, Any] | None = None
    abort: dict[str, Any] | None = None
    try:
        _ensure_replay_available(replay_path)
        approval = _validate_approval(approval_artifact)
        credential_policy = _validate_credential_policy(credential_policy_artifact)
        if approval["approved_provider_id"] != _require_openai_provider(provider_id):
            raise FailClosedRuntimeError("live provider prerequisite failed closed: unauthorized provider")
        if transport_failure is True:
            raise FailClosedRuntimeError("live provider prerequisite failed closed: transport failure")
        _reject_authority_bearing_provider_output(provider_output_preview)
        transport_boundary = create_live_transport_boundary(
            boundary_id=f"{invocation}:TRANSPORT_BOUNDARY",
            provider_id=provider_id,
            created_at=created_at,
        )
        envelope = create_live_replay_envelope(
            invocation_id=invocation,
            approval_artifact=approval,
            credential_policy_artifact=credential_policy,
            transport_boundary_artifact=transport_boundary,
            created_at=created_at,
        )
        audit = create_live_audit_packet(
            audit_id=f"{invocation}:AUDIT",
            replay_envelope_artifact=envelope,
            final_status=ABORTED_PRE_INVOCATION,
            failure_reason="pre-live prerequisites prepared; live provider invocation intentionally not performed",
            created_at=created_at,
        )
        abort = create_live_abort_marker(
            abort_id=f"{invocation}:ABORT",
            replay_envelope_artifact=envelope,
            audit_packet_artifact=audit,
            abort_reason="pre-live boundary requires separate live invocation implementation",
            created_at=created_at,
        )
        artifacts = (approval, credential_policy, transport_boundary, envelope, audit, abort)
        _persist_sequence(replay_path, artifacts)
        return _capture(
            invocation_id=invocation,
            final_status=ABORTED_PRE_INVOCATION,
            failure_reason="",
            replay_path=replay_path,
            approval=approval,
            credential_policy=credential_policy,
            transport_boundary=transport_boundary,
            envelope=envelope,
            audit=audit,
            abort=abort,
        )
    except Exception as exc:
        reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "live provider prerequisite failed closed"
        failure = _failure_artifact(invocation_id=invocation, failure_reason=reason, created_at=created_at)
        write_json_immutable(replay_path / "000_live_provider_prerequisite_failed_closed.json", _wrap_failure(failure))
        return _capture(
            invocation_id=invocation,
            final_status=FAILED_CLOSED,
            failure_reason=reason,
            replay_path=replay_path,
            approval=None,
            credential_policy=None,
            transport_boundary=None,
            envelope=envelope,
            audit=audit,
            abort=abort,
            failure_artifact=failure,
        )


def reconstruct_live_provider_invocation_prerequisites(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the pre-live replay envelope sequence."""

    replay_path = Path(replay_dir)
    first_failure = replay_path / "000_live_provider_prerequisite_failed_closed.json"
    if first_failure.exists():
        wrapper = load_json(first_failure)
        _verify_wrapper_hash(wrapper)
        artifact = wrapper["artifact"]
        _verify_artifact_hash(artifact, "live prerequisite failure")
        return {
            "milestone_id": MILESTONE_ID,
            "final_status": FAILED_CLOSED,
            "invocation_id": artifact["invocation_id"],
            "failure_reason": artifact["failure_reason"],
            "provider_invoked": False,
            "live_provider_call_performed": False,
            "replay_visible": True,
            "replay_hash": replay_hash(wrapper),
        }
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("live provider prerequisite replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("live provider prerequisite replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, f"live provider prerequisite {step}")
        wrappers.append(wrapper)
    envelope = wrappers[3]["artifact"]
    audit = wrappers[4]["artifact"]
    abort = wrappers[5]["artifact"]
    if audit["replay_envelope_artifact_hash"] != envelope["artifact_hash"]:
        raise FailClosedRuntimeError("live provider prerequisite audit envelope hash mismatch")
    if abort["audit_packet_artifact_hash"] != audit["artifact_hash"]:
        raise FailClosedRuntimeError("live provider prerequisite abort audit hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_status": ABORTED_PRE_INVOCATION,
        "invocation_id": envelope["invocation_id"],
        "provider_id": envelope["provider_id"],
        "live_provider_call_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "audit_verdict": audit["audit_verdict"],
        "rollback_marker_created": abort["rollback_marker_created"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_approval(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("live provider prerequisite failed closed: missing approval")
    _verify_artifact_hash(artifact, "live approval")
    if artifact.get("artifact_type") != LIVE_PROVIDER_INVOCATION_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: invalid approval artifact")
    if artifact.get("approval_status") != APPROVED or artifact.get("approval_granted") is not True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: missing approval")
    if artifact.get("approved_provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: unauthorized provider")
    if artifact.get("approved_scope") != APPROVED_SCOPE:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: invalid approval scope")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def _validate_credential_policy(artifact: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("live provider prerequisite failed closed: missing credential policy")
    _verify_artifact_hash(artifact, "live credential policy")
    if artifact.get("artifact_type") != LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: invalid credential policy")
    if artifact.get("provider_id") != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: unauthorized provider")
    if artifact.get("credential_secret_stored") is not False or artifact.get("credential_secret_replayed") is not False:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: credential policy must not store secrets")
    if artifact.get("secret_material_present") is not False:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: credential policy must not store secrets")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def _validate_transport_boundary(artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "live transport boundary")
    if artifact.get("artifact_type") != LIVE_PROVIDER_TRANSPORT_BOUNDARY_ARTIFACT_V1:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: invalid transport boundary")
    if artifact.get("transport_enabled") is not False or artifact.get("live_provider_call_performed") is not False:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: transport invocation is not implemented")
    _reject_mutation_flags(artifact)
    return deepcopy(artifact)


def _reject_authority_bearing_provider_output(output: str | None) -> None:
    if output is None:
        return
    text = _require_string(output, "provider_output_preview").lower()
    if any(phrase in text for phrase in PROHIBITED_RESPONSE_PHRASES):
        raise FailClosedRuntimeError("live provider prerequisite failed closed: authority-bearing provider output")


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
    invocation_id: str,
    final_status: str,
    failure_reason: str,
    replay_path: Path,
    approval: dict[str, Any] | None,
    credential_policy: dict[str, Any] | None,
    transport_boundary: dict[str, Any] | None,
    envelope: dict[str, Any] | None,
    audit: dict[str, Any] | None,
    abort: dict[str, Any] | None,
    failure_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capture = {
        "milestone_id": MILESTONE_ID,
        "invocation_id": invocation_id,
        "final_status": final_status,
        "failure_reason": failure_reason,
        "approval_artifact": deepcopy(approval),
        "credential_policy_artifact": deepcopy(credential_policy),
        "transport_boundary_artifact": deepcopy(transport_boundary),
        "replay_envelope_artifact": deepcopy(envelope),
        "audit_packet_artifact": deepcopy(audit),
        "abort_marker_artifact": deepcopy(abort),
        "failure_artifact": deepcopy(failure_artifact),
        "live_provider_call_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status == FAILED_CLOSED,
        "replay_visible": True,
        "replay_reference": str(replay_path),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _failure_artifact(*, invocation_id: str, failure_reason: str, created_at: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": LIVE_PROVIDER_AUDIT_PACKET_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "invocation_id": invocation_id,
        "final_status": FAILED_CLOSED,
        "audit_verdict": FAIL,
        "failure_reason": failure_reason,
        "live_provider_call_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
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
        "replay_step": "live_provider_prerequisite_failed_closed",
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    if (replay_path / "000_live_provider_prerequisite_failed_closed.json").exists():
        raise FailClosedRuntimeError("live provider prerequisite failed closed: replay artifact already exists")
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("live provider prerequisite failed closed: replay artifact already exists")


def _reject_mutation_flags(artifact: dict[str, Any]) -> None:
    if artifact.get("provider_invoked") is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: provider was invoked")
    if artifact.get("worker_invoked") is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: worker was invoked")
    if artifact.get("execution_requested") is True or artifact.get("dispatch_requested") is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: execution or dispatch requested")
    if artifact.get("governance_modified") is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: governance modified")
    if artifact.get("replay_modified") is True:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: replay modified")


def _require_openai_provider(provider_id: str) -> str:
    provider = _require_string(provider_id, "provider_id")
    if provider != OPENAI_PROVIDER_ID:
        raise FailClosedRuntimeError("live provider prerequisite failed closed: unauthorized provider")
    return provider


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
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("live provider prerequisite replay wrapper must be a JSON object")
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("live provider prerequisite replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("live provider prerequisite replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"live provider prerequisite failed closed: {field_name} is required")
    return value


def _looks_like_secret(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith("sk-") or "bearer " in lowered or "api_key=" in lowered or "secret=" in lowered


def _approval_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "approval_id": artifact["approval_id"],
        "approval_status": artifact["approval_status"],
        "approval_granted": artifact["approval_granted"],
        "approved_provider_id": artifact["approved_provider_id"],
        "approved_scope": artifact["approved_scope"],
        "required_capability": artifact["required_capability"],
        "runtime_path": artifact["runtime_path"],
        "approved_by": artifact["approved_by"],
        "created_at": artifact["created_at"],
        "expires_at": artifact["expires_at"],
    }


def _credential_policy_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_id": artifact["policy_id"],
        "provider_id": artifact["provider_id"],
        "credential_reference": artifact["credential_reference"],
        "credential_secret_stored": artifact["credential_secret_stored"],
        "credential_secret_replayed": artifact["credential_secret_replayed"],
        "retrieval_boundary": artifact["retrieval_boundary"],
    }


def _transport_boundary_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "boundary_id": artifact["boundary_id"],
        "provider_id": artifact["provider_id"],
        "transport_boundary": artifact["transport_boundary"],
        "transport_enabled": artifact["transport_enabled"],
        "live_provider_call_performed": artifact["live_provider_call_performed"],
        "authentication_implemented": artifact["authentication_implemented"],
    }


def _replay_envelope_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "transport_boundary_artifact_hash": artifact["transport_boundary_artifact_hash"],
        "live_provider_call_performed": artifact["live_provider_call_performed"],
        "abort_required_before_live_call": artifact["abort_required_before_live_call"],
    }


def _audit_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "audit_id": artifact["audit_id"],
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "audit_verdict": artifact["audit_verdict"],
        "final_status": artifact["final_status"],
        "approval_artifact_hash": artifact["approval_artifact_hash"],
        "credential_policy_artifact_hash": artifact["credential_policy_artifact_hash"],
        "transport_boundary_artifact_hash": artifact["transport_boundary_artifact_hash"],
        "replay_envelope_artifact_hash": artifact["replay_envelope_artifact_hash"],
        "live_provider_call_performed": artifact["live_provider_call_performed"],
    }


def _abort_hash_input(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "abort_id": artifact["abort_id"],
        "invocation_id": artifact["invocation_id"],
        "provider_id": artifact["provider_id"],
        "abort_status": artifact["abort_status"],
        "replay_envelope_artifact_hash": artifact["replay_envelope_artifact_hash"],
        "audit_packet_artifact_hash": artifact["audit_packet_artifact_hash"],
        "live_provider_call_performed": artifact["live_provider_call_performed"],
        "rollback_marker_created": artifact["rollback_marker_created"],
    }
