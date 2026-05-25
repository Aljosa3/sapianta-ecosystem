"""Governed memory validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .memory_retention_policy import MemoryRetentionPolicy
from .semantic_summary import MAX_SUMMARY_LENGTH, SemanticSummary


class MemoryValidator:
    """Fail-closed validation for semantic continuity memory."""

    def __init__(self, retention_policy: MemoryRetentionPolicy | None = None) -> None:
        self.retention_policy = retention_policy or MemoryRetentionPolicy()

    def validate(self, contract, record) -> dict[str, object]:
        self._verify_hash(contract.to_dict(), "memory contract")
        self._verify_hash(record.to_dict(), "memory record")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("memory requires AUTHORIZED governance_state")
        if not contract.runtime_id or not record.runtime_id:
            raise FailClosedRuntimeError("memory runtime_id is required")
        if not contract.continuity_scope or not record.continuity_scope:
            raise FailClosedRuntimeError("memory continuity_scope is required")
        if contract.runtime_id != record.runtime_id or contract.goal_id != record.goal_id:
            raise FailClosedRuntimeError("memory contract and record mismatch")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("memory lineage_refs are required")
        if not isinstance(record.lineage_refs, list) or not record.lineage_refs:
            raise FailClosedRuntimeError("memory record lineage_refs are required")
        retention = self.retention_policy.validate(contract.retention_policy)
        if record.retention_policy != contract.retention_policy:
            raise FailClosedRuntimeError("memory retention_policy mismatch")
        summary_text = SemanticSummary.as_text(record.semantic_summary)
        if len(summary_text) > MAX_SUMMARY_LENGTH:
            raise FailClosedRuntimeError("semantic summary exceeds bounded length")
        validation = {
            "status": "MEMORY_VALIDATED",
            "memory_contract_id": contract.memory_contract_id,
            "memory_id": record.memory_id,
            "runtime_id": contract.runtime_id,
            "retention_policy": contract.retention_policy,
            "retention_bounded": retention["bounded"],
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation

    def _verify_hash(self, artifact: dict, label: str) -> None:
        replay_input = deepcopy(artifact)
        actual = replay_input.pop("replay_hash", None)
        if actual != replay_hash(replay_input):
            raise FailClosedRuntimeError(f"{label} replay_hash mismatch")
