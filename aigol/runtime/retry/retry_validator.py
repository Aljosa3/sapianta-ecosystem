"""Retry execution validation."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


class RetryValidator:
    """Fail-closed validation for retry artifacts."""

    def validate(self, contract, request=None) -> dict[str, object]:
        self._verify_hash(contract.to_dict(), "retry contract")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("retry requires AUTHORIZED governance_state")
        if not contract.runtime_id or not contract.parent_runtime_id:
            raise FailClosedRuntimeError("retry runtime and parent runtime are required")
        if not isinstance(contract.retry_reason, str) or not contract.retry_reason:
            raise FailClosedRuntimeError("retry_reason is required")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("retry lineage_refs are required")
        if not isinstance(contract.retry_count, int) or not isinstance(contract.max_retry_limit, int):
            raise FailClosedRuntimeError("retry values must be integers")
        if contract.retry_count > contract.max_retry_limit:
            raise FailClosedRuntimeError("retry limit exceeded")
        if request is not None:
            self._verify_hash(request.to_dict(), "retry request")
            if request.runtime_id != contract.runtime_id:
                raise FailClosedRuntimeError("retry request runtime mismatch")
            if request.retry_reason != contract.retry_reason:
                raise FailClosedRuntimeError("retry request reason mismatch")
        validation = {
            "status": "RETRY_VALIDATED",
            "retry_contract_id": contract.retry_contract_id,
            "runtime_id": contract.runtime_id,
            "parent_runtime_id": contract.parent_runtime_id,
            "retry_count": contract.retry_count,
            "max_retry_limit": contract.max_retry_limit,
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation

    def _verify_hash(self, artifact: dict, label: str) -> None:
        replay_input = deepcopy(artifact)
        actual = replay_input.pop("replay_hash", None)
        if actual != replay_hash(replay_input):
            raise FailClosedRuntimeError(f"{label} replay_hash mismatch")
