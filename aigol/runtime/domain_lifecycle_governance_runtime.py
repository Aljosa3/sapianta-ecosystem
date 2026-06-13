"""Approval-gated governance for domain lifecycle candidates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED,
    DOMAIN_CANDIDATE_ARTIFACT_V1,
    DOMAIN_CANDIDATE_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION = "AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME_V1"
HUMAN_APPROVAL_ARTIFACT_V1 = "HUMAN_APPROVAL_ARTIFACT_V1"
DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1 = "DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1"
DOMAIN_ACTIVE_ARTIFACT_V1 = "DOMAIN_ACTIVE_ARTIFACT_V1"
DOMAIN_OPERATION_ARTIFACT_V1 = "DOMAIN_OPERATION_ARTIFACT_V1"
DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1 = "DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1"
DOMAIN_RETIRED_ARTIFACT_V1 = "DOMAIN_RETIRED_ARTIFACT_V1"

DOMAIN_ACTIVATION_CANDIDATE_CREATED = "DOMAIN_ACTIVATION_CANDIDATE_CREATED"
DOMAIN_ACTIVE = "DOMAIN_ACTIVE"
DOMAIN_OPERATION_AVAILABLE = "DOMAIN_OPERATION_AVAILABLE"
DOMAIN_RETIREMENT_CANDIDATE_CREATED = "DOMAIN_RETIREMENT_CANDIDATE_CREATED"
DOMAIN_RETIRED = "DOMAIN_RETIRED"
FAILED_CLOSED = "FAILED_CLOSED"

ACTIVATION_CANDIDATE_REPLAY_STEPS = (
    "domain_activation_candidate_recorded",
    "domain_activation_candidate_returned",
)
ACTIVATION_REPLAY_STEPS = (
    "domain_active_recorded",
    "domain_operation_recorded",
    "domain_activation_returned",
)
RETIREMENT_CANDIDATE_REPLAY_STEPS = (
    "domain_retirement_candidate_recorded",
    "domain_retirement_candidate_returned",
)
RETIREMENT_REPLAY_STEPS = (
    "domain_retired_recorded",
    "domain_retirement_returned",
)

AUTHORITY_FLAGS = {
    "candidate_authoritative": False,
    "activation_approval_required": True,
    "retirement_approval_required": True,
    "live_registry_mutated": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "worker_dispatched": False,
    "execution_started": False,
    "authorization_created": False,
    "governance_mutated": False,
    "replay_mutated": False,
    "self_authorized": False,
}


def create_domain_activation_candidate(
    *,
    activation_candidate_id: str,
    domain_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a domain activation candidate without activating a live domain."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, ACTIVATION_CANDIDATE_REPLAY_STEPS)
        candidate = deepcopy(domain_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_domain_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["domain_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_domain_candidate",
            source_hash_field="source_domain_candidate_hash",
            scope="CREATE_DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            allowed_flag="domain_activation_allowed",
            allowed_value=False,
        )
        activation_candidate = _activation_candidate_artifact(
            activation_candidate_id=activation_candidate_id,
            candidate=candidate,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            status=DOMAIN_ACTIVATION_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="DOMAIN_ACTIVATION_CANDIDATE_RETURNED",
            ref_key="activation_candidate_reference",
            hash_key="activation_candidate_hash",
            artifact_id=activation_candidate["activation_candidate_id"],
            artifact=activation_candidate,
        )
        _persist_step(replay_path, 0, ACTIVATION_CANDIDATE_REPLAY_STEPS[0], activation_candidate)
        _persist_step(replay_path, 1, ACTIVATION_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("activation_candidate_status", activation_candidate["activation_candidate_status"], activation_candidate, returned, replay_path)
    except Exception as exc:
        activation_candidate = _failed_activation_candidate_artifact(
            activation_candidate_id=activation_candidate_id,
            domain_candidate_artifact=domain_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="DOMAIN_ACTIVATION_CANDIDATE_RETURNED",
            ref_key="activation_candidate_reference",
            hash_key="activation_candidate_hash",
            artifact_id=activation_candidate["activation_candidate_id"],
            artifact=activation_candidate,
        )
        _persist_failure_if_possible(replay_path, 0, ACTIVATION_CANDIDATE_REPLAY_STEPS[0], activation_candidate)
        _persist_failure_if_possible(replay_path, 1, ACTIVATION_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("activation_candidate_status", activation_candidate["activation_candidate_status"], activation_candidate, returned, replay_path)


def activate_domain_candidate(
    *,
    active_domain_id: str,
    activation_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    activated_by: str,
    activated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Mark a candidate as lifecycle-active without mutating a live domain registry."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, ACTIVATION_REPLAY_STEPS)
        candidate = deepcopy(activation_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_activation_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["activation_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_activation_candidate",
            source_hash_field="source_activation_candidate_hash",
            scope="ACTIVATE_DOMAIN_ONLY",
            allowed_flag="domain_activation_allowed",
            allowed_value=True,
        )
        active = _active_artifact(
            active_domain_id=active_domain_id,
            candidate=candidate,
            approval=approval,
            activated_by=activated_by,
            activated_at=activated_at,
            status=DOMAIN_ACTIVE,
            failure_reason=None,
        )
        operation = _operation_artifact(active=active, activated_at=activated_at)
        returned = _returned_artifact(
            event_type="DOMAIN_ACTIVATION_RETURNED",
            ref_key="active_domain_reference",
            hash_key="active_domain_hash",
            artifact_id=active["active_domain_id"],
            artifact=active,
            extra={
                "domain_operation_reference": operation["domain_operation_id"],
                "domain_operation_hash": operation["artifact_hash"],
            },
        )
        _persist_step(replay_path, 0, ACTIVATION_REPLAY_STEPS[0], active)
        _persist_step(replay_path, 1, ACTIVATION_REPLAY_STEPS[1], operation)
        _persist_step(replay_path, 2, ACTIVATION_REPLAY_STEPS[2], returned)
        capture = _capture("active_domain_status", active["active_domain_status"], active, returned, replay_path)
        capture["domain_operation_artifact"] = deepcopy(operation)
        capture["domain_operation_status"] = operation["operation_status"]
        capture["domain_active"] = True
        return capture
    except Exception as exc:
        active = _failed_active_artifact(
            active_domain_id=active_domain_id,
            activation_candidate_artifact=activation_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            activated_by=activated_by,
            activated_at=activated_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="DOMAIN_ACTIVATION_RETURNED",
            ref_key="active_domain_reference",
            hash_key="active_domain_hash",
            artifact_id=active["active_domain_id"],
            artifact=active,
        )
        _persist_failure_if_possible(replay_path, 0, ACTIVATION_REPLAY_STEPS[0], active)
        _persist_failure_if_possible(replay_path, 2, ACTIVATION_REPLAY_STEPS[2], returned)
        capture = _capture("active_domain_status", active["active_domain_status"], active, returned, replay_path)
        capture["domain_operation_artifact"] = None
        capture["domain_operation_status"] = FAILED_CLOSED
        capture["domain_active"] = False
        return capture


def request_domain_retirement(
    *,
    retirement_candidate_id: str,
    active_domain_artifact: dict[str, Any],
    requested_by: str,
    requested_at: str,
    retirement_reason: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a retirement candidate for an active lifecycle domain."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, RETIREMENT_CANDIDATE_REPLAY_STEPS)
        active = deepcopy(active_domain_artifact)
        _validate_active_domain(active)
        candidate = _retirement_candidate_artifact(
            retirement_candidate_id=retirement_candidate_id,
            active=active,
            requested_by=requested_by,
            requested_at=requested_at,
            retirement_reason=retirement_reason,
            status=DOMAIN_RETIREMENT_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="DOMAIN_RETIREMENT_CANDIDATE_RETURNED",
            ref_key="retirement_candidate_reference",
            hash_key="retirement_candidate_hash",
            artifact_id=candidate["retirement_candidate_id"],
            artifact=candidate,
        )
        _persist_step(replay_path, 0, RETIREMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, RETIREMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("retirement_candidate_status", candidate["retirement_candidate_status"], candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_retirement_candidate_artifact(
            retirement_candidate_id=retirement_candidate_id,
            active_domain_artifact=active_domain_artifact,
            requested_by=requested_by,
            requested_at=requested_at,
            retirement_reason=retirement_reason,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="DOMAIN_RETIREMENT_CANDIDATE_RETURNED",
            ref_key="retirement_candidate_reference",
            hash_key="retirement_candidate_hash",
            artifact_id=candidate["retirement_candidate_id"],
            artifact=candidate,
        )
        _persist_failure_if_possible(replay_path, 0, RETIREMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, RETIREMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("retirement_candidate_status", candidate["retirement_candidate_status"], candidate, returned, replay_path)


def retire_domain_candidate(
    *,
    retired_domain_id: str,
    retirement_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    retired_by: str,
    retired_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Retire a lifecycle-active domain after explicit human approval."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, RETIREMENT_REPLAY_STEPS)
        candidate = deepcopy(retirement_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_retirement_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["retirement_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_retirement_candidate",
            source_hash_field="source_retirement_candidate_hash",
            scope="RETIRE_DOMAIN_ONLY",
            allowed_flag="domain_retirement_allowed",
            allowed_value=True,
        )
        retired = _retired_artifact(
            retired_domain_id=retired_domain_id,
            candidate=candidate,
            approval=approval,
            retired_by=retired_by,
            retired_at=retired_at,
            status=DOMAIN_RETIRED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="DOMAIN_RETIREMENT_RETURNED",
            ref_key="retired_domain_reference",
            hash_key="retired_domain_hash",
            artifact_id=retired["retired_domain_id"],
            artifact=retired,
        )
        _persist_step(replay_path, 0, RETIREMENT_REPLAY_STEPS[0], retired)
        _persist_step(replay_path, 1, RETIREMENT_REPLAY_STEPS[1], returned)
        capture = _capture("retired_domain_status", retired["retired_domain_status"], retired, returned, replay_path)
        capture["domain_retired"] = True
        return capture
    except Exception as exc:
        retired = _failed_retired_artifact(
            retired_domain_id=retired_domain_id,
            retirement_candidate_artifact=retirement_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            retired_by=retired_by,
            retired_at=retired_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="DOMAIN_RETIREMENT_RETURNED",
            ref_key="retired_domain_reference",
            hash_key="retired_domain_hash",
            artifact_id=retired["retired_domain_id"],
            artifact=retired,
        )
        _persist_failure_if_possible(replay_path, 0, RETIREMENT_REPLAY_STEPS[0], retired)
        _persist_failure_if_possible(replay_path, 1, RETIREMENT_REPLAY_STEPS[1], returned)
        capture = _capture("retired_domain_status", retired["retired_domain_status"], retired, returned, replay_path)
        capture["domain_retired"] = False
        return capture


def reconstruct_domain_lifecycle_governance_replay(replay_dir: str | Path, steps: tuple[str, ...]) -> dict[str, Any]:
    """Reconstruct one domain lifecycle governance transition replay."""

    wrappers = _load_wrappers(Path(replay_dir), steps)
    final_artifact = wrappers[-2]["artifact"] if len(wrappers) > 2 else wrappers[0]["artifact"]
    returned = wrappers[-1]["artifact"]
    return {
        "artifact_type": final_artifact["artifact_type"],
        "status": _status_value(final_artifact),
        "proposed_domain": final_artifact.get("proposed_domain"),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "fail_closed_preserved": final_artifact.get("fail_closed_preserved") is True,
        "returned_event_type": returned.get("event_type"),
        "replay_hash": replay_hash(wrappers),
    }


def _activation_candidate_artifact(
    *,
    activation_candidate_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    requested_by: str,
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1,
        proposed_domain=candidate["proposed_domain"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="activation_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "activation_candidate_id": _require_string(activation_candidate_id, "activation_candidate_id"),
            "source_domain_candidate": candidate["domain_candidate_id"],
            "source_domain_candidate_hash": candidate["artifact_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "requested_by": _require_string(requested_by, "requested_by"),
            "created_at": _require_string(created_at, "created_at"),
            "activation_scope": "DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            "domain_active": False,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _active_artifact(
    *,
    active_domain_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    activated_by: str,
    activated_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DOMAIN_ACTIVE_ARTIFACT_V1,
        proposed_domain=candidate["proposed_domain"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="active_domain_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "active_domain_id": _require_string(active_domain_id, "active_domain_id"),
            "source_activation_candidate": candidate["activation_candidate_id"],
            "source_activation_candidate_hash": candidate["artifact_hash"],
            "source_domain_candidate": candidate["source_domain_candidate"],
            "source_domain_candidate_hash": candidate["source_domain_candidate_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "activated_by": _require_string(activated_by, "activated_by"),
            "activated_at": _require_string(activated_at, "activated_at"),
            "domain_active": True,
            "domain_operation_available": True,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _operation_artifact(*, active: dict[str, Any], activated_at: str) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DOMAIN_OPERATION_ARTIFACT_V1,
        proposed_domain=active["proposed_domain"],
        canonical_chain_id=active["canonical_chain_id"],
        status_key="operation_status",
        status=DOMAIN_OPERATION_AVAILABLE,
        failure_reason=None,
    )
    artifact.update(
        {
            "domain_operation_id": f"{active['active_domain_id']}:DOMAIN-OPERATION",
            "source_active_domain": active["active_domain_id"],
            "source_active_domain_hash": active["artifact_hash"],
            "operation_scope": "GOVERNED_DOMAIN_OPERATION_ONLY",
            "operation_available_at": _require_string(activated_at, "activated_at"),
            "domain_active": True,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _retirement_candidate_artifact(
    *,
    retirement_candidate_id: str,
    active: dict[str, Any],
    requested_by: str,
    requested_at: str,
    retirement_reason: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1,
        proposed_domain=active["proposed_domain"],
        canonical_chain_id=active["canonical_chain_id"],
        status_key="retirement_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "retirement_candidate_id": _require_string(retirement_candidate_id, "retirement_candidate_id"),
            "source_active_domain": active["active_domain_id"],
            "source_active_domain_hash": active["artifact_hash"],
            "retirement_reason": _require_string(retirement_reason, "retirement_reason"),
            "requested_by": _require_string(requested_by, "requested_by"),
            "requested_at": _require_string(requested_at, "requested_at"),
            "required_next_step": "HUMAN_RETIREMENT_APPROVAL",
            "domain_active": True,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _retired_artifact(
    *,
    retired_domain_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    retired_by: str,
    retired_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=DOMAIN_RETIRED_ARTIFACT_V1,
        proposed_domain=candidate["proposed_domain"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="retired_domain_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "retired_domain_id": _require_string(retired_domain_id, "retired_domain_id"),
            "source_retirement_candidate": candidate["retirement_candidate_id"],
            "source_retirement_candidate_hash": candidate["artifact_hash"],
            "source_active_domain": candidate["source_active_domain"],
            "source_active_domain_hash": candidate["source_active_domain_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "retired_by": _require_string(retired_by, "retired_by"),
            "retired_at": _require_string(retired_at, "retired_at"),
            "domain_active": False,
            "domain_retired": True,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_activation_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("domain_candidate_artifact") if isinstance(kwargs.get("domain_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1,
        proposed_domain=source.get("proposed_domain"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="activation_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "activation_candidate_id": kwargs.get("activation_candidate_id") if isinstance(kwargs.get("activation_candidate_id"), str) else "INVALID",
            "source_domain_candidate": source.get("domain_candidate_id"),
            "source_domain_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "created_at": kwargs.get("created_at") if isinstance(kwargs.get("created_at"), str) else None,
            "activation_scope": "DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            "domain_active": False,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_active_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("activation_candidate_artifact") if isinstance(kwargs.get("activation_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=DOMAIN_ACTIVE_ARTIFACT_V1,
        proposed_domain=source.get("proposed_domain"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="active_domain_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "active_domain_id": kwargs.get("active_domain_id") if isinstance(kwargs.get("active_domain_id"), str) else "INVALID",
            "source_activation_candidate": source.get("activation_candidate_id"),
            "source_activation_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "activated_by": kwargs.get("activated_by") if isinstance(kwargs.get("activated_by"), str) else None,
            "activated_at": kwargs.get("activated_at") if isinstance(kwargs.get("activated_at"), str) else None,
            "domain_active": False,
            "domain_operation_available": False,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_retirement_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("active_domain_artifact") if isinstance(kwargs.get("active_domain_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1,
        proposed_domain=source.get("proposed_domain"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="retirement_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "retirement_candidate_id": kwargs.get("retirement_candidate_id") if isinstance(kwargs.get("retirement_candidate_id"), str) else "INVALID",
            "source_active_domain": source.get("active_domain_id"),
            "source_active_domain_hash": source.get("artifact_hash"),
            "retirement_reason": kwargs.get("retirement_reason") if isinstance(kwargs.get("retirement_reason"), str) else None,
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "requested_at": kwargs.get("requested_at") if isinstance(kwargs.get("requested_at"), str) else None,
            "required_next_step": "HUMAN_RETIREMENT_APPROVAL",
            "domain_active": False,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_retired_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("retirement_candidate_artifact") if isinstance(kwargs.get("retirement_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=DOMAIN_RETIRED_ARTIFACT_V1,
        proposed_domain=source.get("proposed_domain"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="retired_domain_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "retired_domain_id": kwargs.get("retired_domain_id") if isinstance(kwargs.get("retired_domain_id"), str) else "INVALID",
            "source_retirement_candidate": source.get("retirement_candidate_id"),
            "source_retirement_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "retired_by": kwargs.get("retired_by") if isinstance(kwargs.get("retired_by"), str) else None,
            "retired_at": kwargs.get("retired_at") if isinstance(kwargs.get("retired_at"), str) else None,
            "domain_active": False,
            "domain_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _base_lineage(
    *,
    artifact_type: str,
    proposed_domain: Any,
    canonical_chain_id: Any,
    status_key: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "runtime_version": AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION,
        "proposed_domain": proposed_domain if isinstance(proposed_domain, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
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
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "domain lifecycle governance artifact")
    returned = {
        "event_type": event_type,
        ref_key: artifact_id,
        hash_key: artifact["artifact_hash"],
        "status": _status_value(artifact),
        "proposed_domain": artifact.get("proposed_domain"),
        "replay_visible": True,
        "fail_closed_preserved": True,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    returned.update(extra or {})
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    status_key: str,
    status: str,
    artifact: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    name = artifact["artifact_type"].lower().replace("_artifact_v1", "")
    capture = {
        "runtime_version": AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION,
        status_key: status,
        f"{name}_artifact": deepcopy(artifact),
        f"{name}_returned_artifact": deepcopy(returned),
        f"{name}_replay_reference": str(replay_path),
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "live_registry_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    capture["domain_lifecycle_governance_capture_hash"] = replay_hash(capture)
    return capture


def _validate_domain_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "domain candidate artifact")
    if candidate.get("artifact_type") != DOMAIN_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: invalid domain candidate")
    if candidate.get("outcome_status") != DOMAIN_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: created domain candidate required")
    if candidate.get("candidate_authoritative", candidate.get("proposal_authoritative")) is not False:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: candidate authority invalid")
    if candidate.get("domain_created") is not False or candidate.get("live_registry_mutated") is not False:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: candidate already mutated domain")


def _validate_activation_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "domain activation candidate artifact")
    if candidate.get("artifact_type") != DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain activation failed closed: invalid activation candidate")
    if candidate.get("activation_candidate_status") != DOMAIN_ACTIVATION_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("domain activation failed closed: created activation candidate required")
    if candidate.get("domain_active") is not False:
        raise FailClosedRuntimeError("domain activation failed closed: candidate already active")


def _validate_active_domain(active: dict[str, Any]) -> None:
    _validate_artifact(active, "domain active artifact")
    if active.get("artifact_type") != DOMAIN_ACTIVE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain retirement request failed closed: active domain artifact required")
    if active.get("active_domain_status") != DOMAIN_ACTIVE or active.get("domain_active") is not True:
        raise FailClosedRuntimeError("domain retirement request failed closed: domain is not active")
    if active.get("domain_retired") is not False:
        raise FailClosedRuntimeError("domain retirement request failed closed: domain already retired")


def _validate_retirement_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "domain retirement candidate artifact")
    if candidate.get("artifact_type") != DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("domain retirement failed closed: invalid retirement candidate")
    if candidate.get("retirement_candidate_status") != DOMAIN_RETIREMENT_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("domain retirement failed closed: created retirement candidate required")
    if candidate.get("retirement_approval_required") is not True:
        raise FailClosedRuntimeError("domain retirement failed closed: approval requirement missing")


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
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: explicit human approval required")
    if approval.get(source_id_field) != source_id or approval.get(source_hash_field) != source_hash:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: approval source mismatch")
    if approval.get("approval_scope") != scope:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: approval scope invalid")
    if approval.get(allowed_flag) is not allowed_value:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: approval scope invalid")
    if approval.get("live_registry_mutation_allowed") is not False:
        raise FailClosedRuntimeError("domain lifecycle governance failed closed: live registry mutation not allowed")
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _load_wrappers(replay_path: Path, steps: tuple[str, ...]) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("domain lifecycle governance replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("domain lifecycle governance replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "domain lifecycle governance artifact")
        wrappers.append(wrapper)
    return wrappers


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "domain lifecycle governance artifact")
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
            raise FailClosedRuntimeError("domain lifecycle governance failed closed: replay already exists")


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
        raise FailClosedRuntimeError("domain lifecycle governance replay hash is required")
    candidate = deepcopy(wrapper)
    candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("domain lifecycle governance replay hash mismatch")


def _status_value(artifact: dict[str, Any]) -> str:
    for key in (
        "activation_candidate_status",
        "active_domain_status",
        "operation_status",
        "retirement_candidate_status",
        "retired_domain_status",
    ):
        value = artifact.get(key)
        if isinstance(value, str):
            return value
    return FAILED_CLOSED


def _field(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, dict) else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"domain lifecycle governance failed closed: {field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or "domain lifecycle governance failed closed"
