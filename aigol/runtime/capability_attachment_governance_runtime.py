"""Approval-gated governance for capability attachment and detachment."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.capability_lifecycle_governance_runtime import (
    CAPABILITY_ACTIVE,
    CAPABILITY_ACTIVE_ARTIFACT_V1,
)
from aigol.runtime.domain_lifecycle_governance_runtime import DOMAIN_ACTIVE, DOMAIN_ACTIVE_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CAPABILITY_ATTACHMENT_GOVERNANCE_RUNTIME_VERSION = "AIGOL_CAPABILITY_ATTACHMENT_GOVERNANCE_RUNTIME_V1"
HUMAN_APPROVAL_ARTIFACT_V1 = "HUMAN_APPROVAL_ARTIFACT_V1"
ATTACHMENT_CANDIDATE_ARTIFACT_V1 = "ATTACHMENT_CANDIDATE_ARTIFACT_V1"
CAPABILITY_ATTACHED_ARTIFACT_V1 = "CAPABILITY_ATTACHED_ARTIFACT_V1"
DETACHMENT_CANDIDATE_ARTIFACT_V1 = "DETACHMENT_CANDIDATE_ARTIFACT_V1"
CAPABILITY_DETACHED_ARTIFACT_V1 = "CAPABILITY_DETACHED_ARTIFACT_V1"

ATTACHMENT_CANDIDATE_CREATED = "ATTACHMENT_CANDIDATE_CREATED"
ATTACHED = "ATTACHED"
DETACHMENT_CANDIDATE_CREATED = "DETACHMENT_CANDIDATE_CREATED"
DETACHED = "DETACHED"
APPROVED = "APPROVED"
FAILED_CLOSED = "FAILED_CLOSED"

ATTACHMENT_CANDIDATE_REPLAY_STEPS = (
    "attachment_candidate_recorded",
    "attachment_candidate_returned",
)
ATTACHMENT_REPLAY_STEPS = ("capability_attached_recorded", "capability_attached_returned")
DETACHMENT_CANDIDATE_REPLAY_STEPS = (
    "detachment_candidate_recorded",
    "detachment_candidate_returned",
)
DETACHMENT_REPLAY_STEPS = ("capability_detached_recorded", "capability_detached_returned")

AUTHORITY_FLAGS = {
    "attachment_candidate_authoritative": False,
    "attachment_approval_required": True,
    "detachment_approval_required": True,
    "capability_executor_invoked": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_started": False,
    "authorization_created": False,
    "governance_mutated": False,
    "replay_mutated": False,
    "self_authorized": False,
}


def create_capability_attachment_candidate(
    *,
    attachment_candidate_id: str,
    active_capability_artifact: dict[str, Any],
    active_domain_artifact: dict[str, Any],
    attachment_scope: str,
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a non-authoritative candidate for attaching one capability to one domain."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, ATTACHMENT_CANDIDATE_REPLAY_STEPS)
        capability = deepcopy(active_capability_artifact)
        domain = deepcopy(active_domain_artifact)
        _validate_active_capability(capability)
        _validate_active_domain(domain)
        candidate = _attachment_candidate_artifact(
            attachment_candidate_id=attachment_candidate_id,
            capability=capability,
            domain=domain,
            attachment_scope=attachment_scope,
            requested_by=requested_by,
            created_at=created_at,
            status=ATTACHMENT_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="ATTACHMENT_CANDIDATE_RETURNED",
            ref_key="attachment_candidate_reference",
            hash_key="attachment_candidate_hash",
            artifact_id=candidate["attachment_candidate_id"],
            artifact=candidate,
        )
        _persist_step(replay_path, 0, ATTACHMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, ATTACHMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("attachment_candidate_status", candidate["attachment_candidate_status"], candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_attachment_candidate_artifact(
            attachment_candidate_id=attachment_candidate_id,
            active_capability_artifact=active_capability_artifact,
            active_domain_artifact=active_domain_artifact,
            attachment_scope=attachment_scope,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="ATTACHMENT_CANDIDATE_RETURNED",
            ref_key="attachment_candidate_reference",
            hash_key="attachment_candidate_hash",
            artifact_id=candidate["attachment_candidate_id"],
            artifact=candidate,
        )
        _persist_failure_if_possible(replay_path, 0, ATTACHMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, ATTACHMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("attachment_candidate_status", candidate["attachment_candidate_status"], candidate, returned, replay_path)


def attach_capability_to_domain(
    *,
    attached_id: str,
    attachment_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    attached_by: str,
    attached_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Attach a capability to a domain after explicit human approval."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, ATTACHMENT_REPLAY_STEPS)
        candidate = deepcopy(attachment_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_attachment_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["attachment_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_attachment_candidate",
            source_hash_field="source_attachment_candidate_hash",
            scope="ATTACH_CAPABILITY_TO_DOMAIN_ONLY",
            allowed_flag="capability_attachment_allowed",
            allowed_value=True,
        )
        attached = _attached_artifact(
            attached_id=attached_id,
            candidate=candidate,
            approval=approval,
            attached_by=attached_by,
            attached_at=attached_at,
            status=ATTACHED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_ATTACHED_RETURNED",
            ref_key="attached_reference",
            hash_key="attached_hash",
            artifact_id=attached["attached_id"],
            artifact=attached,
        )
        _persist_step(replay_path, 0, ATTACHMENT_REPLAY_STEPS[0], attached)
        _persist_step(replay_path, 1, ATTACHMENT_REPLAY_STEPS[1], returned)
        return _capture("attachment_status", attached["attachment_status"], attached, returned, replay_path)
    except Exception as exc:
        attached = _failed_attached_artifact(
            attached_id=attached_id,
            attachment_candidate_artifact=attachment_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            attached_by=attached_by,
            attached_at=attached_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_ATTACHED_RETURNED",
            ref_key="attached_reference",
            hash_key="attached_hash",
            artifact_id=attached["attached_id"],
            artifact=attached,
        )
        _persist_failure_if_possible(replay_path, 0, ATTACHMENT_REPLAY_STEPS[0], attached)
        _persist_failure_if_possible(replay_path, 1, ATTACHMENT_REPLAY_STEPS[1], returned)
        return _capture("attachment_status", attached["attachment_status"], attached, returned, replay_path)


def create_capability_detachment_candidate(
    *,
    detachment_candidate_id: str,
    attached_artifact: dict[str, Any],
    detachment_reason: str,
    requested_by: str,
    requested_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a non-authoritative detachment candidate for an attached capability."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, DETACHMENT_CANDIDATE_REPLAY_STEPS)
        attached = deepcopy(attached_artifact)
        _validate_attached(attached)
        candidate = _detachment_candidate_artifact(
            detachment_candidate_id=detachment_candidate_id,
            attached=attached,
            detachment_reason=detachment_reason,
            requested_by=requested_by,
            requested_at=requested_at,
            status=DETACHMENT_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="DETACHMENT_CANDIDATE_RETURNED",
            ref_key="detachment_candidate_reference",
            hash_key="detachment_candidate_hash",
            artifact_id=candidate["detachment_candidate_id"],
            artifact=candidate,
        )
        _persist_step(replay_path, 0, DETACHMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, DETACHMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("detachment_candidate_status", candidate["detachment_candidate_status"], candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_detachment_candidate_artifact(
            detachment_candidate_id=detachment_candidate_id,
            attached_artifact=attached_artifact,
            detachment_reason=detachment_reason,
            requested_by=requested_by,
            requested_at=requested_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="DETACHMENT_CANDIDATE_RETURNED",
            ref_key="detachment_candidate_reference",
            hash_key="detachment_candidate_hash",
            artifact_id=candidate["detachment_candidate_id"],
            artifact=candidate,
        )
        _persist_failure_if_possible(replay_path, 0, DETACHMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, DETACHMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("detachment_candidate_status", candidate["detachment_candidate_status"], candidate, returned, replay_path)


def detach_capability_from_domain(
    *,
    detached_id: str,
    detachment_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    detached_by: str,
    detached_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Detach a capability from a domain after explicit human approval."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, DETACHMENT_REPLAY_STEPS)
        candidate = deepcopy(detachment_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_detachment_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["detachment_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_detachment_candidate",
            source_hash_field="source_detachment_candidate_hash",
            scope="DETACH_CAPABILITY_FROM_DOMAIN_ONLY",
            allowed_flag="capability_detachment_allowed",
            allowed_value=True,
        )
        detached = _detached_artifact(
            detached_id=detached_id,
            candidate=candidate,
            approval=approval,
            detached_by=detached_by,
            detached_at=detached_at,
            status=DETACHED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_DETACHED_RETURNED",
            ref_key="detached_reference",
            hash_key="detached_hash",
            artifact_id=detached["detached_id"],
            artifact=detached,
        )
        _persist_step(replay_path, 0, DETACHMENT_REPLAY_STEPS[0], detached)
        _persist_step(replay_path, 1, DETACHMENT_REPLAY_STEPS[1], returned)
        return _capture("detachment_status", detached["detachment_status"], detached, returned, replay_path)
    except Exception as exc:
        detached = _failed_detached_artifact(
            detached_id=detached_id,
            detachment_candidate_artifact=detachment_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            detached_by=detached_by,
            detached_at=detached_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_DETACHED_RETURNED",
            ref_key="detached_reference",
            hash_key="detached_hash",
            artifact_id=detached["detached_id"],
            artifact=detached,
        )
        _persist_failure_if_possible(replay_path, 0, DETACHMENT_REPLAY_STEPS[0], detached)
        _persist_failure_if_possible(replay_path, 1, DETACHMENT_REPLAY_STEPS[1], returned)
        return _capture("detachment_status", detached["detachment_status"], detached, returned, replay_path)


def reconstruct_capability_attachment_governance_replay(replay_dir: str | Path, steps: tuple[str, ...]) -> dict[str, Any]:
    """Reconstruct one capability attachment governance transition replay."""

    wrappers = _load_wrappers(Path(replay_dir), steps)
    artifact = wrappers[0]["artifact"]
    returned = wrappers[-1]["artifact"]
    return {
        "artifact_type": artifact["artifact_type"],
        "status": _status_value(artifact),
        "capability_name": artifact.get("capability_name"),
        "domain_name": artifact.get("domain_name"),
        "attachment_scope": artifact.get("attachment_scope"),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "capability_executor_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "fail_closed_preserved": artifact.get("fail_closed_preserved") is True,
        "returned_event_type": returned.get("event_type"),
        "replay_hash": replay_hash(wrappers),
    }


def _attachment_candidate_artifact(
    *,
    attachment_candidate_id: str,
    capability: dict[str, Any],
    domain: dict[str, Any],
    attachment_scope: str,
    requested_by: str,
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=ATTACHMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=capability["capability_name"],
        domain_name=domain["proposed_domain"],
        attachment_scope=attachment_scope,
        status_key="attachment_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "attachment_candidate_id": _require_string(attachment_candidate_id, "attachment_candidate_id"),
            "source_active_capability": capability["active_capability_id"],
            "source_active_capability_hash": capability["artifact_hash"],
            "source_active_domain": domain["active_domain_id"],
            "source_active_domain_hash": domain["artifact_hash"],
            "requested_by": _require_string(requested_by, "requested_by"),
            "created_at": _require_string(created_at, "created_at"),
            "capability_attached": False,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _attached_artifact(
    *,
    attached_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    attached_by: str,
    attached_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_ATTACHED_ARTIFACT_V1,
        capability_name=candidate["capability_name"],
        domain_name=candidate["domain_name"],
        attachment_scope=candidate["attachment_scope"],
        status_key="attachment_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "attached_id": _require_string(attached_id, "attached_id"),
            "source_attachment_candidate": candidate["attachment_candidate_id"],
            "source_attachment_candidate_hash": candidate["artifact_hash"],
            "source_active_capability": candidate["source_active_capability"],
            "source_active_capability_hash": candidate["source_active_capability_hash"],
            "source_active_domain": candidate["source_active_domain"],
            "source_active_domain_hash": candidate["source_active_domain_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "attached_by": _require_string(attached_by, "attached_by"),
            "attached_at": _require_string(attached_at, "attached_at"),
            "capability_attached": True,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _detachment_candidate_artifact(
    *,
    detachment_candidate_id: str,
    attached: dict[str, Any],
    detachment_reason: str,
    requested_by: str,
    requested_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DETACHMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=attached["capability_name"],
        domain_name=attached["domain_name"],
        attachment_scope=attached["attachment_scope"],
        status_key="detachment_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "detachment_candidate_id": _require_string(detachment_candidate_id, "detachment_candidate_id"),
            "source_attached": attached["attached_id"],
            "source_attached_hash": attached["artifact_hash"],
            "source_active_capability": attached["source_active_capability"],
            "source_active_domain": attached["source_active_domain"],
            "detachment_reason": _require_string(detachment_reason, "detachment_reason"),
            "requested_by": _require_string(requested_by, "requested_by"),
            "requested_at": _require_string(requested_at, "requested_at"),
            "capability_attached": True,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _detached_artifact(
    *,
    detached_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    detached_by: str,
    detached_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_DETACHED_ARTIFACT_V1,
        capability_name=candidate["capability_name"],
        domain_name=candidate["domain_name"],
        attachment_scope=candidate["attachment_scope"],
        status_key="detachment_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "detached_id": _require_string(detached_id, "detached_id"),
            "source_detachment_candidate": candidate["detachment_candidate_id"],
            "source_detachment_candidate_hash": candidate["artifact_hash"],
            "source_attached": candidate["source_attached"],
            "source_attached_hash": candidate["source_attached_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "detached_by": _require_string(detached_by, "detached_by"),
            "detached_at": _require_string(detached_at, "detached_at"),
            "capability_attached": False,
            "capability_detached": True,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_attachment_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    capability = kwargs.get("active_capability_artifact") if isinstance(kwargs.get("active_capability_artifact"), dict) else {}
    domain = kwargs.get("active_domain_artifact") if isinstance(kwargs.get("active_domain_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=ATTACHMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=capability.get("capability_name"),
        domain_name=domain.get("proposed_domain"),
        attachment_scope=kwargs.get("attachment_scope"),
        status_key="attachment_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "attachment_candidate_id": kwargs.get("attachment_candidate_id") if isinstance(kwargs.get("attachment_candidate_id"), str) else "INVALID",
            "source_active_capability": capability.get("active_capability_id"),
            "source_active_capability_hash": capability.get("artifact_hash"),
            "source_active_domain": domain.get("active_domain_id"),
            "source_active_domain_hash": domain.get("artifact_hash"),
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "created_at": kwargs.get("created_at") if isinstance(kwargs.get("created_at"), str) else None,
            "capability_attached": False,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_attached_artifact(**kwargs: Any) -> dict[str, Any]:
    candidate = kwargs.get("attachment_candidate_artifact") if isinstance(kwargs.get("attachment_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_ATTACHED_ARTIFACT_V1,
        capability_name=candidate.get("capability_name"),
        domain_name=candidate.get("domain_name"),
        attachment_scope=candidate.get("attachment_scope"),
        status_key="attachment_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "attached_id": kwargs.get("attached_id") if isinstance(kwargs.get("attached_id"), str) else "INVALID",
            "source_attachment_candidate": candidate.get("attachment_candidate_id"),
            "source_attachment_candidate_hash": candidate.get("artifact_hash"),
            "source_active_capability": candidate.get("source_active_capability"),
            "source_active_capability_hash": candidate.get("source_active_capability_hash"),
            "source_active_domain": candidate.get("source_active_domain"),
            "source_active_domain_hash": candidate.get("source_active_domain_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "attached_by": kwargs.get("attached_by") if isinstance(kwargs.get("attached_by"), str) else None,
            "attached_at": kwargs.get("attached_at") if isinstance(kwargs.get("attached_at"), str) else None,
            "capability_attached": False,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_detachment_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    attached = kwargs.get("attached_artifact") if isinstance(kwargs.get("attached_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=DETACHMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=attached.get("capability_name"),
        domain_name=attached.get("domain_name"),
        attachment_scope=attached.get("attachment_scope"),
        status_key="detachment_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "detachment_candidate_id": kwargs.get("detachment_candidate_id") if isinstance(kwargs.get("detachment_candidate_id"), str) else "INVALID",
            "source_attached": attached.get("attached_id"),
            "source_attached_hash": attached.get("artifact_hash"),
            "source_active_capability": attached.get("source_active_capability"),
            "source_active_domain": attached.get("source_active_domain"),
            "detachment_reason": kwargs.get("detachment_reason") if isinstance(kwargs.get("detachment_reason"), str) else None,
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "requested_at": kwargs.get("requested_at") if isinstance(kwargs.get("requested_at"), str) else None,
            "capability_attached": False,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_detached_artifact(**kwargs: Any) -> dict[str, Any]:
    candidate = kwargs.get("detachment_candidate_artifact") if isinstance(kwargs.get("detachment_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_DETACHED_ARTIFACT_V1,
        capability_name=candidate.get("capability_name"),
        domain_name=candidate.get("domain_name"),
        attachment_scope=candidate.get("attachment_scope"),
        status_key="detachment_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "detached_id": kwargs.get("detached_id") if isinstance(kwargs.get("detached_id"), str) else "INVALID",
            "source_detachment_candidate": candidate.get("detachment_candidate_id"),
            "source_detachment_candidate_hash": candidate.get("artifact_hash"),
            "source_attached": candidate.get("source_attached"),
            "source_attached_hash": candidate.get("source_attached_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "detached_by": kwargs.get("detached_by") if isinstance(kwargs.get("detached_by"), str) else None,
            "detached_at": kwargs.get("detached_at") if isinstance(kwargs.get("detached_at"), str) else None,
            "capability_attached": True,
            "capability_detached": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _base_lineage(
    *,
    artifact_type: str,
    capability_name: Any,
    domain_name: Any,
    attachment_scope: Any,
    status_key: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "runtime_version": AIGOL_CAPABILITY_ATTACHMENT_GOVERNANCE_RUNTIME_VERSION,
        "capability_name": capability_name if isinstance(capability_name, str) else None,
        "domain_name": domain_name if isinstance(domain_name, str) else None,
        "attachment_scope": attachment_scope if isinstance(attachment_scope, str) else None,
        status_key: status,
        "replay_visible": True,
        "fail_closed_preserved": True,
        **deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }


def _returned_artifact(
    *,
    event_type: str,
    ref_key: str,
    hash_key: str,
    artifact_id: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "capability attachment governance artifact")
    returned = {
        "event_type": event_type,
        ref_key: artifact_id,
        hash_key: artifact["artifact_hash"],
        "status": _status_value(artifact),
        "capability_name": artifact.get("capability_name"),
        "domain_name": artifact.get("domain_name"),
        "attachment_scope": artifact.get("attachment_scope"),
        "replay_visible": True,
        "fail_closed_preserved": True,
        "capability_executor_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(status_key: str, status: str, artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    name = artifact["artifact_type"].lower().replace("_artifact_v1", "")
    capture = {
        "runtime_version": AIGOL_CAPABILITY_ATTACHMENT_GOVERNANCE_RUNTIME_VERSION,
        status_key: status,
        f"{name}_artifact": deepcopy(artifact),
        f"{name}_returned_artifact": deepcopy(returned),
        f"{name}_replay_reference": str(replay_path),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "capability_executor_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    capture["capability_attachment_governance_capture_hash"] = replay_hash(capture)
    return capture


def _validate_active_capability(capability: dict[str, Any]) -> None:
    _validate_artifact(capability, "active capability artifact")
    if capability.get("artifact_type") != CAPABILITY_ACTIVE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability attachment governance failed closed: active capability required")
    if capability.get("active_capability_status") != CAPABILITY_ACTIVE or capability.get("capability_active") is not True:
        raise FailClosedRuntimeError("capability attachment governance failed closed: capability is not active")


def _validate_active_domain(domain: dict[str, Any]) -> None:
    _validate_artifact(domain, "active domain artifact")
    if domain.get("artifact_type") != DOMAIN_ACTIVE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability attachment governance failed closed: active domain required")
    if domain.get("active_domain_status") != DOMAIN_ACTIVE or domain.get("domain_active") is not True:
        raise FailClosedRuntimeError("capability attachment governance failed closed: domain is not active")


def _validate_attachment_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "attachment candidate artifact")
    if candidate.get("artifact_type") != ATTACHMENT_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability attachment failed closed: invalid attachment candidate")
    if candidate.get("attachment_candidate_status") != ATTACHMENT_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("capability attachment failed closed: created attachment candidate required")
    if candidate.get("attachment_candidate_authoritative") is not False:
        raise FailClosedRuntimeError("capability attachment failed closed: candidate authority invalid")
    if candidate.get("capability_attached") is not False:
        raise FailClosedRuntimeError("capability attachment failed closed: candidate already attached")


def _validate_attached(attached: dict[str, Any]) -> None:
    _validate_artifact(attached, "attached capability artifact")
    if attached.get("artifact_type") != CAPABILITY_ATTACHED_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability detachment candidate failed closed: attached artifact required")
    if attached.get("attachment_status") != ATTACHED or attached.get("capability_attached") is not True:
        raise FailClosedRuntimeError("capability detachment candidate failed closed: capability is not attached")
    if attached.get("capability_detached") is not False:
        raise FailClosedRuntimeError("capability detachment candidate failed closed: capability already detached")


def _validate_detachment_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "detachment candidate artifact")
    if candidate.get("artifact_type") != DETACHMENT_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability detachment failed closed: invalid detachment candidate")
    if candidate.get("detachment_candidate_status") != DETACHMENT_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("capability detachment failed closed: created detachment candidate required")
    if candidate.get("detachment_approval_required") is not True:
        raise FailClosedRuntimeError("capability detachment failed closed: approval requirement missing")


def _validate_human_approval(
    approval: dict[str, Any],
    *,
    source_id: str,
    source_hash: str,
    source_id_field: str,
    source_hash_field: str,
    scope: str,
    allowed_flag: str,
    allowed_value: bool,
) -> None:
    _validate_artifact(approval, "human approval artifact")
    if approval.get("artifact_type") != HUMAN_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability attachment governance failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("capability attachment governance failed closed: explicit human approval required")
    if approval.get(source_id_field) != source_id or approval.get(source_hash_field) != source_hash:
        raise FailClosedRuntimeError("capability attachment governance failed closed: approval source mismatch")
    if approval.get("approval_scope") != scope or approval.get(allowed_flag) is not allowed_value:
        raise FailClosedRuntimeError("capability attachment governance failed closed: approval scope invalid")
    if approval.get("capability_executor_invocation_allowed") is not False:
        raise FailClosedRuntimeError("capability attachment governance failed closed: executor invocation not allowed")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _load_wrappers(replay_path: Path, steps: tuple[str, ...]) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("capability attachment governance replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("capability attachment governance replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "capability attachment governance artifact")
        wrappers.append(wrapper)
    return wrappers


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "capability attachment governance artifact")
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path, steps: tuple[str, ...]) -> None:
    for index, step in enumerate(steps):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("capability attachment governance failed closed: replay already exists")


def _validate_artifact(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} missing")
    _verify_artifact_hash(artifact, label)


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError("capability attachment governance replay hash is required")
    candidate = deepcopy(wrapper)
    candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("capability attachment governance replay hash mismatch")


def _status_value(artifact: dict[str, Any]) -> str:
    for key in (
        "attachment_candidate_status",
        "attachment_status",
        "detachment_candidate_status",
        "detachment_status",
    ):
        value = artifact.get(key)
        if isinstance(value, str):
            return value
    return FAILED_CLOSED


def _field(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, dict) else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"capability attachment governance failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or "capability attachment governance failed closed"
