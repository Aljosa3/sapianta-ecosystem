"""Approval-gated governance for capability lifecycle candidates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_runtime import CREATED, PROPOSAL_RUNTIME_ARTIFACT_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION = "AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME_V1"
HUMAN_APPROVAL_ARTIFACT_V1 = "HUMAN_APPROVAL_ARTIFACT_V1"
CAPABILITY_CANDIDATE_ARTIFACT_V1 = "CAPABILITY_CANDIDATE_ARTIFACT_V1"
CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1 = "CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1"
CAPABILITY_ACTIVE_ARTIFACT_V1 = "CAPABILITY_ACTIVE_ARTIFACT_V1"
CAPABILITY_OPERATION_ARTIFACT_V1 = "CAPABILITY_OPERATION_ARTIFACT_V1"
CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1 = "CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1"
CAPABILITY_RETIRED_ARTIFACT_V1 = "CAPABILITY_RETIRED_ARTIFACT_V1"

CAPABILITY_CANDIDATE_CREATED = "CAPABILITY_CANDIDATE_CREATED"
CAPABILITY_ACTIVATION_CANDIDATE_CREATED = "CAPABILITY_ACTIVATION_CANDIDATE_CREATED"
CAPABILITY_ACTIVE = "CAPABILITY_ACTIVE"
CAPABILITY_OPERATION_AVAILABLE = "CAPABILITY_OPERATION_AVAILABLE"
CAPABILITY_RETIREMENT_CANDIDATE_CREATED = "CAPABILITY_RETIREMENT_CANDIDATE_CREATED"
CAPABILITY_RETIRED = "CAPABILITY_RETIRED"
APPROVED = "APPROVED"
FAILED_CLOSED = "FAILED_CLOSED"

CANDIDATE_REPLAY_STEPS = ("capability_candidate_recorded", "capability_candidate_returned")
ACTIVATION_CANDIDATE_REPLAY_STEPS = (
    "capability_activation_candidate_recorded",
    "capability_activation_candidate_returned",
)
ACTIVATION_REPLAY_STEPS = (
    "capability_active_recorded",
    "capability_operation_recorded",
    "capability_activation_returned",
)
RETIREMENT_CANDIDATE_REPLAY_STEPS = (
    "capability_retirement_candidate_recorded",
    "capability_retirement_candidate_returned",
)
RETIREMENT_REPLAY_STEPS = ("capability_retired_recorded", "capability_retirement_returned")

AUTHORITY_FLAGS = {
    "candidate_authoritative": False,
    "activation_approval_required": True,
    "retirement_approval_required": True,
    "capability_executor_invoked": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_started": False,
    "authorization_created": False,
    "governance_mutated": False,
    "replay_mutated": False,
    "self_authorized": False,
}


def create_capability_candidate(
    *,
    capability_candidate_id: str,
    capability_proposal_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a non-authoritative capability candidate from a capability proposal."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, CANDIDATE_REPLAY_STEPS)
        proposal = deepcopy(capability_proposal_artifact)
        _validate_capability_proposal(proposal)
        candidate = _candidate_artifact(
            capability_candidate_id=capability_candidate_id,
            proposal=proposal,
            requested_by=requested_by,
            created_at=created_at,
            status=CAPABILITY_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_CANDIDATE_RETURNED",
            ref_key="capability_candidate_reference",
            hash_key="capability_candidate_hash",
            artifact_id=candidate["capability_candidate_id"],
            artifact=candidate,
        )
        _persist_step(replay_path, 0, CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_step(replay_path, 1, CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("candidate_status", candidate["candidate_status"], candidate, returned, replay_path)
    except Exception as exc:
        candidate = _failed_candidate_artifact(
            capability_candidate_id=capability_candidate_id,
            capability_proposal_artifact=capability_proposal_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_CANDIDATE_RETURNED",
            ref_key="capability_candidate_reference",
            hash_key="capability_candidate_hash",
            artifact_id=candidate["capability_candidate_id"],
            artifact=candidate,
        )
        _persist_failure_if_possible(replay_path, 0, CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("candidate_status", candidate["candidate_status"], candidate, returned, replay_path)


def create_capability_activation_candidate(
    *,
    activation_candidate_id: str,
    capability_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    requested_by: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create an activation candidate without activating or executing the capability."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, ACTIVATION_CANDIDATE_REPLAY_STEPS)
        candidate = deepcopy(capability_candidate_artifact)
        approval = deepcopy(human_approval_artifact)
        _validate_capability_candidate(candidate)
        _validate_human_approval(
            approval,
            source_id=candidate["capability_candidate_id"],
            source_hash=candidate["artifact_hash"],
            source_id_field="source_capability_candidate",
            source_hash_field="source_capability_candidate_hash",
            scope="CREATE_CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            allowed_flag="capability_activation_allowed",
            allowed_value=False,
        )
        activation_candidate = _activation_candidate_artifact(
            activation_candidate_id=activation_candidate_id,
            candidate=candidate,
            approval=approval,
            requested_by=requested_by,
            created_at=created_at,
            status=CAPABILITY_ACTIVATION_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_ACTIVATION_CANDIDATE_RETURNED",
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
            capability_candidate_artifact=capability_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            requested_by=requested_by,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_ACTIVATION_CANDIDATE_RETURNED",
            ref_key="activation_candidate_reference",
            hash_key="activation_candidate_hash",
            artifact_id=activation_candidate["activation_candidate_id"],
            artifact=activation_candidate,
        )
        _persist_failure_if_possible(replay_path, 0, ACTIVATION_CANDIDATE_REPLAY_STEPS[0], activation_candidate)
        _persist_failure_if_possible(replay_path, 1, ACTIVATION_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("activation_candidate_status", activation_candidate["activation_candidate_status"], activation_candidate, returned, replay_path)


def activate_capability_candidate(
    *,
    active_capability_id: str,
    activation_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    activated_by: str,
    activated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create active capability evidence without invoking a capability executor."""

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
            scope="ACTIVATE_CAPABILITY_ONLY",
            allowed_flag="capability_activation_allowed",
            allowed_value=True,
        )
        active = _active_artifact(
            active_capability_id=active_capability_id,
            candidate=candidate,
            approval=approval,
            activated_by=activated_by,
            activated_at=activated_at,
            status=CAPABILITY_ACTIVE,
            failure_reason=None,
        )
        operation = _operation_artifact(active=active, activated_at=activated_at)
        returned = _returned_artifact(
            event_type="CAPABILITY_ACTIVATION_RETURNED",
            ref_key="active_capability_reference",
            hash_key="active_capability_hash",
            artifact_id=active["active_capability_id"],
            artifact=active,
            extra={
                "capability_operation_reference": operation["capability_operation_id"],
                "capability_operation_hash": operation["artifact_hash"],
            },
        )
        _persist_step(replay_path, 0, ACTIVATION_REPLAY_STEPS[0], active)
        _persist_step(replay_path, 1, ACTIVATION_REPLAY_STEPS[1], operation)
        _persist_step(replay_path, 2, ACTIVATION_REPLAY_STEPS[2], returned)
        capture = _capture("active_capability_status", active["active_capability_status"], active, returned, replay_path)
        capture["capability_operation_artifact"] = deepcopy(operation)
        capture["capability_operation_status"] = operation["operation_status"]
        return capture
    except Exception as exc:
        active = _failed_active_artifact(
            active_capability_id=active_capability_id,
            activation_candidate_artifact=activation_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            activated_by=activated_by,
            activated_at=activated_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_ACTIVATION_RETURNED",
            ref_key="active_capability_reference",
            hash_key="active_capability_hash",
            artifact_id=active["active_capability_id"],
            artifact=active,
        )
        _persist_failure_if_possible(replay_path, 0, ACTIVATION_REPLAY_STEPS[0], active)
        _persist_failure_if_possible(replay_path, 2, ACTIVATION_REPLAY_STEPS[2], returned)
        capture = _capture("active_capability_status", active["active_capability_status"], active, returned, replay_path)
        capture["capability_operation_artifact"] = None
        capture["capability_operation_status"] = FAILED_CLOSED
        return capture


def request_capability_retirement(
    *,
    retirement_candidate_id: str,
    active_capability_artifact: dict[str, Any],
    requested_by: str,
    requested_at: str,
    retirement_reason: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a retirement candidate for an active capability."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path, RETIREMENT_CANDIDATE_REPLAY_STEPS)
        active = deepcopy(active_capability_artifact)
        _validate_active_capability(active)
        candidate = _retirement_candidate_artifact(
            retirement_candidate_id=retirement_candidate_id,
            active=active,
            requested_by=requested_by,
            requested_at=requested_at,
            retirement_reason=retirement_reason,
            status=CAPABILITY_RETIREMENT_CANDIDATE_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_RETIREMENT_CANDIDATE_RETURNED",
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
            active_capability_artifact=active_capability_artifact,
            requested_by=requested_by,
            requested_at=requested_at,
            retirement_reason=retirement_reason,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_RETIREMENT_CANDIDATE_RETURNED",
            ref_key="retirement_candidate_reference",
            hash_key="retirement_candidate_hash",
            artifact_id=candidate["retirement_candidate_id"],
            artifact=candidate,
        )
        _persist_failure_if_possible(replay_path, 0, RETIREMENT_CANDIDATE_REPLAY_STEPS[0], candidate)
        _persist_failure_if_possible(replay_path, 1, RETIREMENT_CANDIDATE_REPLAY_STEPS[1], returned)
        return _capture("retirement_candidate_status", candidate["retirement_candidate_status"], candidate, returned, replay_path)


def retire_capability_candidate(
    *,
    retired_capability_id: str,
    retirement_candidate_artifact: dict[str, Any],
    human_approval_artifact: dict[str, Any],
    retired_by: str,
    retired_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Retire an active capability after explicit human approval."""

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
            scope="RETIRE_CAPABILITY_ONLY",
            allowed_flag="capability_retirement_allowed",
            allowed_value=True,
        )
        retired = _retired_artifact(
            retired_capability_id=retired_capability_id,
            candidate=candidate,
            approval=approval,
            retired_by=retired_by,
            retired_at=retired_at,
            status=CAPABILITY_RETIRED,
            failure_reason=None,
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_RETIREMENT_RETURNED",
            ref_key="retired_capability_reference",
            hash_key="retired_capability_hash",
            artifact_id=retired["retired_capability_id"],
            artifact=retired,
        )
        _persist_step(replay_path, 0, RETIREMENT_REPLAY_STEPS[0], retired)
        _persist_step(replay_path, 1, RETIREMENT_REPLAY_STEPS[1], returned)
        return _capture("retired_capability_status", retired["retired_capability_status"], retired, returned, replay_path)
    except Exception as exc:
        retired = _failed_retired_artifact(
            retired_capability_id=retired_capability_id,
            retirement_candidate_artifact=retirement_candidate_artifact,
            human_approval_artifact=human_approval_artifact,
            retired_by=retired_by,
            retired_at=retired_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(
            event_type="CAPABILITY_RETIREMENT_RETURNED",
            ref_key="retired_capability_reference",
            hash_key="retired_capability_hash",
            artifact_id=retired["retired_capability_id"],
            artifact=retired,
        )
        _persist_failure_if_possible(replay_path, 0, RETIREMENT_REPLAY_STEPS[0], retired)
        _persist_failure_if_possible(replay_path, 1, RETIREMENT_REPLAY_STEPS[1], returned)
        return _capture("retired_capability_status", retired["retired_capability_status"], retired, returned, replay_path)


def reconstruct_capability_lifecycle_governance_replay(replay_dir: str | Path, steps: tuple[str, ...]) -> dict[str, Any]:
    """Reconstruct one capability lifecycle governance transition replay."""

    wrappers = _load_wrappers(Path(replay_dir), steps)
    final_artifact = wrappers[-2]["artifact"] if len(wrappers) > 2 else wrappers[0]["artifact"]
    returned = wrappers[-1]["artifact"]
    return {
        "artifact_type": final_artifact["artifact_type"],
        "status": _status_value(final_artifact),
        "capability_name": final_artifact.get("capability_name"),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "capability_executor_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "fail_closed_preserved": final_artifact.get("fail_closed_preserved") is True,
        "returned_event_type": returned.get("event_type"),
        "replay_hash": replay_hash(wrappers),
    }


def _candidate_artifact(
    *,
    capability_candidate_id: str,
    proposal: dict[str, Any],
    requested_by: str,
    created_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_CANDIDATE_ARTIFACT_V1,
        capability_name=proposal["proposal_text"],
        canonical_chain_id=proposal["proposal_id"],
        status_key="candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "capability_candidate_id": _require_string(capability_candidate_id, "capability_candidate_id"),
            "source_capability_proposal": proposal["proposal_id"],
            "source_capability_proposal_hash": proposal["artifact_hash"],
            "requested_by": _require_string(requested_by, "requested_by"),
            "created_at": _require_string(created_at, "created_at"),
            "required_next_step": "HUMAN_ACTIVATION_CANDIDATE_APPROVAL",
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


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
        artifact_type=CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1,
        capability_name=candidate["capability_name"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="activation_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "activation_candidate_id": _require_string(activation_candidate_id, "activation_candidate_id"),
            "source_capability_candidate": candidate["capability_candidate_id"],
            "source_capability_candidate_hash": candidate["artifact_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "requested_by": _require_string(requested_by, "requested_by"),
            "created_at": _require_string(created_at, "created_at"),
            "activation_scope": "CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _active_artifact(
    *,
    active_capability_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    activated_by: str,
    activated_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_ACTIVE_ARTIFACT_V1,
        capability_name=candidate["capability_name"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="active_capability_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "active_capability_id": _require_string(active_capability_id, "active_capability_id"),
            "source_activation_candidate": candidate["activation_candidate_id"],
            "source_activation_candidate_hash": candidate["artifact_hash"],
            "source_capability_candidate": candidate["source_capability_candidate"],
            "source_capability_candidate_hash": candidate["source_capability_candidate_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "activated_by": _require_string(activated_by, "activated_by"),
            "activated_at": _require_string(activated_at, "activated_at"),
            "capability_active": True,
            "capability_operation_available": True,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _operation_artifact(*, active: dict[str, Any], activated_at: str) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_OPERATION_ARTIFACT_V1,
        capability_name=active["capability_name"],
        canonical_chain_id=active["canonical_chain_id"],
        status_key="operation_status",
        status=CAPABILITY_OPERATION_AVAILABLE,
        failure_reason=None,
    )
    artifact.update(
        {
            "capability_operation_id": f"{active['active_capability_id']}:CAPABILITY-OPERATION",
            "source_active_capability": active["active_capability_id"],
            "source_active_capability_hash": active["artifact_hash"],
            "operation_scope": "GOVERNED_CAPABILITY_OPERATION_ONLY",
            "operation_available_at": _require_string(activated_at, "activated_at"),
            "capability_active": True,
            "capability_retired": False,
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
        artifact_type=CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=active["capability_name"],
        canonical_chain_id=active["canonical_chain_id"],
        status_key="retirement_candidate_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "retirement_candidate_id": _require_string(retirement_candidate_id, "retirement_candidate_id"),
            "source_active_capability": active["active_capability_id"],
            "source_active_capability_hash": active["artifact_hash"],
            "retirement_reason": _require_string(retirement_reason, "retirement_reason"),
            "requested_by": _require_string(requested_by, "requested_by"),
            "requested_at": _require_string(requested_at, "requested_at"),
            "required_next_step": "HUMAN_RETIREMENT_APPROVAL",
            "capability_active": True,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _retired_artifact(
    *,
    retired_capability_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    retired_by: str,
    retired_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = _base_lineage(
        artifact_type=CAPABILITY_RETIRED_ARTIFACT_V1,
        capability_name=candidate["capability_name"],
        canonical_chain_id=candidate["canonical_chain_id"],
        status_key="retired_capability_status",
        status=status,
        failure_reason=failure_reason,
    )
    artifact.update(
        {
            "retired_capability_id": _require_string(retired_capability_id, "retired_capability_id"),
            "source_retirement_candidate": candidate["retirement_candidate_id"],
            "source_retirement_candidate_hash": candidate["artifact_hash"],
            "source_active_capability": candidate["source_active_capability"],
            "source_active_capability_hash": candidate["source_active_capability_hash"],
            "human_approval_reference": approval["approval_id"],
            "human_approval_hash": approval["artifact_hash"],
            "retired_by": _require_string(retired_by, "retired_by"),
            "retired_at": _require_string(retired_at, "retired_at"),
            "capability_active": False,
            "capability_retired": True,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("capability_proposal_artifact") if isinstance(kwargs.get("capability_proposal_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_CANDIDATE_ARTIFACT_V1,
        capability_name=source.get("proposal_text"),
        canonical_chain_id=source.get("proposal_id"),
        status_key="candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "capability_candidate_id": kwargs.get("capability_candidate_id") if isinstance(kwargs.get("capability_candidate_id"), str) else "INVALID",
            "source_capability_proposal": source.get("proposal_id"),
            "source_capability_proposal_hash": source.get("artifact_hash"),
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "created_at": kwargs.get("created_at") if isinstance(kwargs.get("created_at"), str) else None,
            "required_next_step": "HUMAN_ACTIVATION_CANDIDATE_APPROVAL",
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_activation_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("capability_candidate_artifact") if isinstance(kwargs.get("capability_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1,
        capability_name=source.get("capability_name"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="activation_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "activation_candidate_id": kwargs.get("activation_candidate_id") if isinstance(kwargs.get("activation_candidate_id"), str) else "INVALID",
            "source_capability_candidate": source.get("capability_candidate_id"),
            "source_capability_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "created_at": kwargs.get("created_at") if isinstance(kwargs.get("created_at"), str) else None,
            "activation_scope": "CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_active_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("activation_candidate_artifact") if isinstance(kwargs.get("activation_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_ACTIVE_ARTIFACT_V1,
        capability_name=source.get("capability_name"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="active_capability_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "active_capability_id": kwargs.get("active_capability_id") if isinstance(kwargs.get("active_capability_id"), str) else "INVALID",
            "source_activation_candidate": source.get("activation_candidate_id"),
            "source_activation_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "activated_by": kwargs.get("activated_by") if isinstance(kwargs.get("activated_by"), str) else None,
            "activated_at": kwargs.get("activated_at") if isinstance(kwargs.get("activated_at"), str) else None,
            "capability_active": False,
            "capability_operation_available": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_retirement_candidate_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("active_capability_artifact") if isinstance(kwargs.get("active_capability_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1,
        capability_name=source.get("capability_name"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="retirement_candidate_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "retirement_candidate_id": kwargs.get("retirement_candidate_id") if isinstance(kwargs.get("retirement_candidate_id"), str) else "INVALID",
            "source_active_capability": source.get("active_capability_id"),
            "source_active_capability_hash": source.get("artifact_hash"),
            "retirement_reason": kwargs.get("retirement_reason") if isinstance(kwargs.get("retirement_reason"), str) else None,
            "requested_by": kwargs.get("requested_by") if isinstance(kwargs.get("requested_by"), str) else None,
            "requested_at": kwargs.get("requested_at") if isinstance(kwargs.get("requested_at"), str) else None,
            "required_next_step": "HUMAN_RETIREMENT_APPROVAL",
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_retired_artifact(**kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("retirement_candidate_artifact") if isinstance(kwargs.get("retirement_candidate_artifact"), dict) else {}
    artifact = _base_lineage(
        artifact_type=CAPABILITY_RETIRED_ARTIFACT_V1,
        capability_name=source.get("capability_name"),
        canonical_chain_id=source.get("canonical_chain_id"),
        status_key="retired_capability_status",
        status=FAILED_CLOSED,
        failure_reason=kwargs["failure_reason"],
    )
    artifact.update(
        {
            "retired_capability_id": kwargs.get("retired_capability_id") if isinstance(kwargs.get("retired_capability_id"), str) else "INVALID",
            "source_retirement_candidate": source.get("retirement_candidate_id"),
            "source_retirement_candidate_hash": source.get("artifact_hash"),
            "human_approval_reference": _field(kwargs.get("human_approval_artifact"), "approval_id"),
            "human_approval_hash": _field(kwargs.get("human_approval_artifact"), "artifact_hash"),
            "retired_by": kwargs.get("retired_by") if isinstance(kwargs.get("retired_by"), str) else None,
            "retired_at": kwargs.get("retired_at") if isinstance(kwargs.get("retired_at"), str) else None,
            "capability_active": False,
            "capability_retired": False,
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _base_lineage(
    *,
    artifact_type: str,
    capability_name: Any,
    canonical_chain_id: Any,
    status_key: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "runtime_version": AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION,
        "capability_name": capability_name if isinstance(capability_name, str) else None,
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
    _verify_artifact_hash(artifact, "capability lifecycle governance artifact")
    returned = {
        "event_type": event_type,
        ref_key: artifact_id,
        hash_key: artifact["artifact_hash"],
        "status": _status_value(artifact),
        "capability_name": artifact.get("capability_name"),
        "replay_visible": True,
        "fail_closed_preserved": True,
        "capability_executor_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "failure_reason": artifact.get("failure_reason"),
    }
    returned.update(extra or {})
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(status_key: str, status: str, artifact: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    name = artifact["artifact_type"].lower().replace("_artifact_v1", "")
    capture = {
        "runtime_version": AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME_VERSION,
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
    capture["capability_lifecycle_governance_capture_hash"] = replay_hash(capture)
    return capture


def _validate_capability_proposal(proposal: dict[str, Any]) -> None:
    _validate_artifact(proposal, "capability proposal artifact")
    if proposal.get("artifact_type") != PROPOSAL_RUNTIME_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: invalid capability proposal")
    if proposal.get("proposal_type") != "CAPABILITY_PROPOSAL":
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: capability proposal required")
    if proposal.get("status") != CREATED:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: created proposal required")
    if proposal.get("authority") is not False or proposal.get("approval_created") is not False:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: proposal authority invalid")


def _validate_capability_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "capability candidate artifact")
    if candidate.get("artifact_type") != CAPABILITY_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: invalid capability candidate")
    if candidate.get("candidate_status") != CAPABILITY_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: created candidate required")
    if candidate.get("candidate_authoritative") is not False:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: candidate authority invalid")
    if candidate.get("capability_active") is not False or candidate.get("capability_executor_invoked") is not False:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: candidate already executed")


def _validate_activation_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "capability activation candidate artifact")
    if candidate.get("artifact_type") != CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability activation failed closed: invalid activation candidate")
    if candidate.get("activation_candidate_status") != CAPABILITY_ACTIVATION_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("capability activation failed closed: created activation candidate required")
    if candidate.get("capability_active") is not False:
        raise FailClosedRuntimeError("capability activation failed closed: candidate already active")


def _validate_active_capability(active: dict[str, Any]) -> None:
    _validate_artifact(active, "capability active artifact")
    if active.get("artifact_type") != CAPABILITY_ACTIVE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability retirement request failed closed: active capability artifact required")
    if active.get("active_capability_status") != CAPABILITY_ACTIVE or active.get("capability_active") is not True:
        raise FailClosedRuntimeError("capability retirement request failed closed: capability is not active")
    if active.get("capability_retired") is not False:
        raise FailClosedRuntimeError("capability retirement request failed closed: capability already retired")


def _validate_retirement_candidate(candidate: dict[str, Any]) -> None:
    _validate_artifact(candidate, "capability retirement candidate artifact")
    if candidate.get("artifact_type") != CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1:
        raise FailClosedRuntimeError("capability retirement failed closed: invalid retirement candidate")
    if candidate.get("retirement_candidate_status") != CAPABILITY_RETIREMENT_CANDIDATE_CREATED:
        raise FailClosedRuntimeError("capability retirement failed closed: created retirement candidate required")
    if candidate.get("retirement_approval_required") is not True:
        raise FailClosedRuntimeError("capability retirement failed closed: approval requirement missing")


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
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: explicit human approval required")
    if approval.get("approval_status") != APPROVED or approval.get("approval_granted") is not True:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: explicit human approval required")
    if approval.get(source_id_field) != source_id or approval.get(source_hash_field) != source_hash:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: approval source mismatch")
    if approval.get("approval_scope") != scope:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: approval scope invalid")
    if approval.get(allowed_flag) is not allowed_value:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: approval scope invalid")
    if approval.get("capability_executor_invocation_allowed") is not False:
        raise FailClosedRuntimeError("capability lifecycle governance failed closed: executor invocation not allowed")
    _require_summary_bound_confirmation(approval)
    _require_string(approval.get("approved_by"), "approved_by")
    _require_string(approval.get("approved_at"), "approved_at")


def _require_summary_bound_confirmation(approval: dict[str, Any]) -> None:
    _require_string(approval.get("execution_summary_reference"), "execution_summary_reference")
    _require_replay_hash(approval.get("execution_summary_hash"), "execution_summary_hash")
    _require_string(approval.get("human_confirmation_reference"), "human_confirmation_reference")
    _require_replay_hash(approval.get("human_confirmation_hash"), "human_confirmation_hash")


def _load_wrappers(replay_path: Path, steps: tuple[str, ...]) -> list[dict[str, Any]]:
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("capability lifecycle governance replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("capability lifecycle governance replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "capability lifecycle governance artifact")
        wrappers.append(wrapper)
    return wrappers


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _persist_failure_if_possible(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if not path.exists():
        write_json_immutable(path, _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(artifact, "capability lifecycle governance artifact")
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
            raise FailClosedRuntimeError("capability lifecycle governance failed closed: replay already exists")


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
        raise FailClosedRuntimeError("capability lifecycle governance replay hash is required")
    candidate = deepcopy(wrapper)
    candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("capability lifecycle governance replay hash mismatch")


def _status_value(artifact: dict[str, Any]) -> str:
    for key in (
        "candidate_status",
        "activation_candidate_status",
        "active_capability_status",
        "operation_status",
        "retirement_candidate_status",
        "retired_capability_status",
    ):
        value = artifact.get(key)
        if isinstance(value, str):
            return value
    return FAILED_CLOSED


def _field(value: Any, key: str) -> Any:
    return value.get(key) if isinstance(value, dict) else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"capability lifecycle governance failed closed: {field_name} is required")
    return value.strip()


def _require_replay_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"capability lifecycle governance failed closed: {field_name} must be a replay hash")
    return text


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or "capability lifecycle governance failed closed"
