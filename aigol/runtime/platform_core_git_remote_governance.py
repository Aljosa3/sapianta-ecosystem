"""Governance-owned authorization helpers for governed Git remote operations."""

from __future__ import annotations

from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.workers.git_remote_worker import AUTHORIZED_GIT_REMOTE_SCOPE, GIT_REMOTE_WORKER_ID


GIT_REMOTE_GOVERNANCE_VERSION = "G11_08_GOVERNED_GIT_REMOTE_WORKFLOW_IMPLEMENTATION_V1"


def create_governed_git_remote_authorization_record(
    *,
    authorization_id: str,
    proposal_id: str,
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create a Governance authorization record for the Git Remote Worker."""

    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=_require_string(proposal_id, "proposal_id"),
        worker_id=GIT_REMOTE_WORKER_ID,
        authorization_scope=AUTHORIZED_GIT_REMOTE_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git remote requires {field}")
    return value
