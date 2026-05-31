"""Fail-closed validation for governed worker authorization inputs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


FORBIDDEN_EVIDENCE_FIELDS = frozenset(
    {
        "provider_authority",
        "proposal_authority",
        "cognition_authority",
        "replay_authority",
        "worker_self_authorized",
        "dispatch_request",
        "worker_invocation",
        "execution_request",
        "execution_started",
        "orchestration_request",
        "memory_mutation",
        "replay_mutation",
    }
)


def validate_authorization_inputs(
    *,
    proposal: dict[str, Any],
    worker_target: dict[str, Any],
    authorization_scope: str,
) -> dict[str, Any]:
    validated_proposal = validate_proposal_lineage(proposal)
    validated_worker = validate_worker_identity(worker_target)
    normalized_scope = validate_scope_integrity(authorization_scope)
    return {
        "proposal": validated_proposal,
        "worker_target": validated_worker,
        "authorization_scope": normalized_scope,
        "evidence_hash": replay_hash(
            {
                "proposal": validated_proposal,
                "worker_target": validated_worker,
                "authorization_scope": normalized_scope,
            }
        ),
    }


def validate_proposal_lineage(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise FailClosedRuntimeError("proposal is required")
    _reject_forbidden_fields(proposal, "proposal")
    proposal_id = _require_string(proposal.get("proposal_id"), "proposal_id")
    lineage = proposal.get("proposal_lineage") or proposal.get("lineage")
    if not isinstance(lineage, dict):
        raise FailClosedRuntimeError("proposal lineage is required")
    _reject_forbidden_fields(lineage, "proposal_lineage")
    reviewer = proposal.get("governance_review") or proposal.get("reviewed_by")
    _require_string(reviewer, "governance_review")
    return {
        "proposal_id": proposal_id,
        "proposal_lineage": deepcopy(lineage),
        "governance_review": reviewer,
        "proposal_hash": proposal.get("proposal_hash") or replay_hash(proposal),
    }


def validate_worker_identity(worker_target: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(worker_target, dict):
        raise FailClosedRuntimeError("worker target is required")
    _reject_forbidden_fields(worker_target, "worker_target")
    worker_id = _require_string(worker_target.get("worker_id"), "worker_id")
    worker_domain = _require_string(worker_target.get("domain", "unspecified"), "worker domain")
    capability = _require_string(worker_target.get("capability"), "worker capability")
    return {
        "worker_id": worker_id,
        "domain": worker_domain,
        "capability": capability,
        "worker_target_hash": worker_target.get("worker_target_hash") or replay_hash(worker_target),
    }


def validate_scope_integrity(scope: str) -> str:
    normalized_scope = _require_string(scope, "authorization_scope").strip().upper().replace("-", "_").replace(" ", "_")
    if normalized_scope in {"UNBOUNDED", "ALL", "ROOT", "ADMIN", "PRIVILEGED"}:
        raise FailClosedRuntimeError("authorization scope must be bounded")
    return normalized_scope


def _reject_forbidden_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_EVIDENCE_FIELDS.intersection(value):
            raise FailClosedRuntimeError(f"{label} contains forbidden authority field")
        for nested in value.values():
            _reject_forbidden_fields(nested, label)
    elif isinstance(value, list):
        for nested in value:
            _reject_forbidden_fields(nested, label)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value

