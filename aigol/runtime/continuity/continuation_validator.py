"""Continuation contract validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


class ContinuationValidator:
    """Fail-closed validation for bounded continuation contracts."""

    def validate(self, contract, sandbox_id: str | None = None) -> dict[str, object]:
        data = contract.to_dict()
        replay_input = deepcopy(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("continuation contract replay_hash mismatch")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("continuation requires AUTHORIZED governance_state")
        if not contract.runtime_id or not contract.parent_runtime_id:
            raise FailClosedRuntimeError("continuation runtime and parent runtime are required")
        if not contract.sandbox_id:
            raise FailClosedRuntimeError("continuation sandbox_id is required")
        if sandbox_id is not None and contract.sandbox_id != sandbox_id:
            raise FailClosedRuntimeError("continuation sandbox compatibility mismatch")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("continuation lineage_refs are required")
        if not isinstance(contract.continuation_reason, str) or not contract.continuation_reason:
            raise FailClosedRuntimeError("continuation_reason is required")
        if not isinstance(contract.retry_count, int) or not isinstance(contract.max_retry_limit, int):
            raise FailClosedRuntimeError("continuation retry values must be integers")
        if contract.retry_count > contract.max_retry_limit:
            raise FailClosedRuntimeError("retry limit exceeded")
        validation = {
            "status": "CONTINUATION_VALIDATED",
            "continuation_id": contract.continuation_id,
            "runtime_id": contract.runtime_id,
            "parent_runtime_id": contract.parent_runtime_id,
            "retry_count": contract.retry_count,
            "max_retry_limit": contract.max_retry_limit,
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation
