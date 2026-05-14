"""Replay-safe result return binding."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


BINDING_FIELDS = (
    "result_return_id",
    "invocation_id",
    "provider_id",
    "envelope_id",
    "replay_identity",
    "normalized_result_hash",
    "evidence_hash",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deterministic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def result_return_identity(*, invocation_id: str, provider_id: str, envelope_id: str, replay_identity: str) -> str:
    digest = deterministic_hash(
        {
            "invocation_id": invocation_id,
            "provider_id": provider_id,
            "envelope_id": envelope_id,
            "replay_identity": replay_identity,
        }
    )
    return f"RESULT-{digest[:24]}"


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return deterministic_hash(payload)


@dataclass(frozen=True)
class ResultBinding:
    result_return_id: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    replay_identity: str
    normalized_result_hash: str
    evidence_hash: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "result_return_id": self.result_return_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "replay_identity": self.replay_identity,
            "normalized_result_hash": self.normalized_result_hash,
            "evidence_hash": self.evidence_hash,
        }
        value["binding_sha256"] = binding_hash(value)
        value["replay_safe"] = True
        value["immutable"] = True
        return value


def create_result_binding(invocation_result: dict[str, Any], invocation_evidence: dict[str, Any]) -> ResultBinding:
    invocation_id = invocation_result["invocation_id"]
    provider_id = invocation_result["provider_id"]
    envelope_id = invocation_result["envelope_id"]
    replay_identity = invocation_result["replay_identity"]
    return ResultBinding(
        result_return_id=result_return_identity(
            invocation_id=invocation_id,
            provider_id=provider_id,
            envelope_id=envelope_id,
            replay_identity=replay_identity,
        ),
        invocation_id=invocation_id,
        provider_id=provider_id,
        envelope_id=envelope_id,
        replay_identity=replay_identity,
        normalized_result_hash=deterministic_hash(invocation_result.get("normalized_result", {})),
        evidence_hash=deterministic_hash(invocation_evidence),
    )


def validate_result_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, ResultBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "result_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing result binding field"})
    for field in BINDING_FIELDS:
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "result binding field must be non-empty"})
    expected_id = None
    if not errors:
        expected_id = result_return_identity(
            invocation_id=value["invocation_id"],
            provider_id=value["provider_id"],
            envelope_id=value["envelope_id"],
            replay_identity=value["replay_identity"],
        )
        if value["result_return_id"] != expected_id:
            errors.append({"field": "result_return_id", "reason": "result return identity mismatch"})
    expected_hash = binding_hash(value) if not errors else None
    if "binding_sha256" in value and value["binding_sha256"] != expected_hash:
        errors.append({"field": "binding_sha256", "reason": "result binding hash mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "result binding must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "result_return_id": expected_id,
        "binding_sha256": expected_hash,
        "replay_safe": not errors,
    }
