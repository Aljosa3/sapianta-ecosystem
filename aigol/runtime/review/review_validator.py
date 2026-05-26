"""Provider harness review validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


class ReviewValidator:
    """Fail-closed validation for provider harness review contracts."""

    def validate(self, contract) -> dict[str, object]:
        data = contract.to_dict()
        replay_input = deepcopy(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("review contract replay_hash mismatch")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("review requires AUTHORIZED governance_state")
        if not contract.review_id or not contract.runtime_id or not contract.provider_name:
            raise FailClosedRuntimeError("review identifiers are required")
        if not isinstance(contract.review_scope, dict):
            raise FailClosedRuntimeError("review_scope must be explicit")
        validation = {
            "status": "REVIEW_CONTRACT_VALIDATED",
            "review_id": contract.review_id,
            "runtime_id": contract.runtime_id,
            "provider_name": contract.provider_name,
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation
