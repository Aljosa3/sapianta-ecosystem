"""Deterministic models for the AiGOL runtime engine foundation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any


APPROVED = "APPROVED"
AUTHORIZED = "AUTHORIZED"
VALID_GOVERNANCE_STATES = {APPROVED, AUTHORIZED}


class FailClosedRuntimeError(ValueError):
    """Raised when runtime evidence is invalid and execution must fail closed."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def replay_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_serializable(value: Any, field_name: str) -> Any:
    try:
        canonical_json(value)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(f"{field_name} must be JSON serializable") from exc
    return deepcopy(value)


@dataclass(frozen=True)
class RuntimePackage:
    runtime_id: str
    package_id: str
    provider: str
    worker_id: str
    task_type: str
    payload: Any
    lineage_refs: list[Any]
    governance_state: str
    created_at: str = "1970-01-01T00:00:00Z"

    def validate(self) -> None:
        _require_string(self.runtime_id, "runtime_id")
        _require_string(self.package_id, "package_id")
        _require_string(self.provider, "provider")
        _require_string(self.worker_id, "worker_id")
        _require_string(self.task_type, "task_type")
        _require_string(self.created_at, "created_at")
        if self.governance_state not in VALID_GOVERNANCE_STATES:
            raise FailClosedRuntimeError("governance_state must be APPROVED or AUTHORIZED")
        if not isinstance(self.lineage_refs, list) or not self.lineage_refs:
            raise FailClosedRuntimeError("lineage_refs must be explicit")
        _require_serializable(self.payload, "payload")
        _require_serializable(self.lineage_refs, "lineage_refs")

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_id": self.runtime_id,
            "package_id": self.package_id,
            "provider": self.provider,
            "worker_id": self.worker_id,
            "task_type": self.task_type,
            "payload": deepcopy(self.payload),
            "lineage_refs": deepcopy(self.lineage_refs),
            "governance_state": self.governance_state,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    status: str
    output: Any
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "output": deepcopy(self.output),
            "metadata": deepcopy(self.metadata),
        }


@dataclass(frozen=True)
class GovernedReturnArtifact:
    runtime_id: str
    package_id: str
    worker_id: str
    provider: str
    lifecycle_state: str
    status: str
    provider_response: ProviderResponse | None
    lineage_refs: list[Any]
    lifecycle_transitions: list[dict[str, str]]
    runtime_dispatch_artifact: dict[str, Any]
    boundary_guarantees: dict[str, bool]
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "runtime_id": self.runtime_id,
            "package_id": self.package_id,
            "worker_id": self.worker_id,
            "provider": self.provider,
            "lifecycle_state": self.lifecycle_state,
            "status": self.status,
            "provider_response": self.provider_response.to_dict() if self.provider_response else None,
            "lineage_refs": deepcopy(self.lineage_refs),
            "lifecycle_transitions": deepcopy(self.lifecycle_transitions),
            "runtime_dispatch_artifact": deepcopy(self.runtime_dispatch_artifact),
            "boundary_guarantees": deepcopy(self.boundary_guarantees),
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact


def boundary_guarantees() -> dict[str, bool]:
    return {
        "real_execution": False,
        "autonomous_execution": False,
        "provider_authority": False,
        "orchestration": False,
        "hidden_continuation": False,
        "governance_mutation": False,
    }
