"""Governance-owned helpers for governed dependency management operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record, validate_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.worker_runtime import AVAILABLE, register_worker
from aigol.workers.dependency_management_worker import (
    AUTHORIZED_DEPENDENCY_REQUEST_TYPE,
    AUTHORIZED_DEPENDENCY_SCOPE,
    DEPENDENCY_WORKER_ID,
    DEPENDENCY_WORKER_VERSION,
)


DEPENDENCY_GOVERNANCE_VERSION = "G11_10_GOVERNED_DEPENDENCY_MANAGEMENT_WORKFLOW_IMPLEMENTATION_V1"


def create_governed_dependency_management_authorization_record(
    *,
    authorization_id: str,
    proposal_id: str,
    authorization_timestamp: str,
) -> dict[str, Any]:
    """Create a Governance authorization record for the Dependency Worker."""

    authorization = create_authorization_record(
        authorization_id=_require_string(authorization_id, "authorization_id"),
        proposal_id=_require_string(proposal_id, "proposal_id"),
        worker_id=DEPENDENCY_WORKER_ID,
        authorization_scope=AUTHORIZED_DEPENDENCY_SCOPE,
        authorization_timestamp=_require_string(authorization_timestamp, "authorization_timestamp"),
    ).to_dict()
    return validate_authorization_record(authorization)


def register_governed_dependency_management_worker(
    *,
    replay_dir: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Register the Dependency Management Worker through the Worker Runtime."""

    return register_worker(
        worker_id=DEPENDENCY_WORKER_ID,
        worker_type="DEPENDENCY_MANAGEMENT_WORKER",
        worker_version=DEPENDENCY_WORKER_VERSION,
        declared_capabilities=[
            "BOUNDED_DEPENDENCY_OPERATION",
            "DEPENDENCY_INSPECTION",
            "DEPENDENCY_EXECUTION",
            "LOCKFILE_AWARE_EVIDENCE",
            "ENVIRONMENT_CONSISTENCY_VERIFICATION",
        ],
        supported_request_types=[AUTHORIZED_DEPENDENCY_REQUEST_TYPE],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=_require_string(created_at, "created_at"),
        replay_reference="replay:worker:governed-dependency-management:registration",
        replay_dir=replay_dir,
        state=AVAILABLE,
    )


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed dependency management requires {field}")
    return value
