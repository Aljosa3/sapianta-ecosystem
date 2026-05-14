"""Deterministic governed execution session identity."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


IDENTITY_FIELDS = (
    "ingress_id",
    "semantic_request_id",
    "envelope_id",
    "provider_id",
    "invocation_id",
    "result_return_id",
    "replay_identity",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deterministic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def session_identity_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in IDENTITY_FIELDS}
    return deterministic_hash(payload)


def session_id_for(value: dict[str, Any]) -> str:
    return f"SESSION-{session_identity_hash(value)[:24]}"


@dataclass(frozen=True)
class SessionIdentity:
    ingress_id: str
    semantic_request_id: str
    envelope_id: str
    provider_id: str
    invocation_id: str
    result_return_id: str
    replay_identity: str

    def to_dict(self) -> dict[str, Any]:
        value = {
            "ingress_id": self.ingress_id,
            "semantic_request_id": self.semantic_request_id,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "invocation_id": self.invocation_id,
            "result_return_id": self.result_return_id,
            "replay_identity": self.replay_identity,
        }
        value["session_id"] = session_id_for(value)
        value["identity_sha256"] = session_identity_hash(value)
        value["replay_safe"] = True
        value["immutable"] = True
        return value


def create_session_identity(
    *,
    ingress_output: dict[str, Any],
    invocation_output: dict[str, Any],
    result_output: dict[str, Any],
) -> SessionIdentity:
    proposal = ingress_output["envelope_proposal"]
    semantic_request = proposal["semantic_request"]
    envelope = proposal["execution_envelope"]
    invocation_result = invocation_output["invocation_result"]
    result_payload = result_output["result_payload"]
    return SessionIdentity(
        ingress_id=ingress_output["session"]["session_id"],
        semantic_request_id=semantic_request["semantic_request_id"],
        envelope_id=envelope["envelope_id"],
        provider_id=envelope["provider_id"],
        invocation_id=invocation_result["invocation_id"],
        result_return_id=result_payload["result_return_id"],
        replay_identity=envelope["replay_identity"],
    )


def validate_session_identity(identity: Any) -> dict[str, Any]:
    value = identity.to_dict() if isinstance(identity, SessionIdentity) else identity
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "session_identity", "reason": "must be an object"}]}
    for field in (*IDENTITY_FIELDS, "session_id", "identity_sha256"):
        if field not in value:
            errors.append({"field": field, "reason": "missing session identity field"})
    for field in IDENTITY_FIELDS:
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "session identity field must be non-empty"})
    expected_session_id = session_id_for(value) if not errors else None
    expected_hash = session_identity_hash(value) if not errors else None
    if "session_id" in value and value["session_id"] != expected_session_id:
        errors.append({"field": "session_id", "reason": "session identity mismatch"})
    if "identity_sha256" in value and value["identity_sha256"] != expected_hash:
        errors.append({"field": "identity_sha256", "reason": "session identity hash mismatch"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "session identity must be replay-safe"})
    return {"valid": not errors, "errors": errors, "session_id": expected_session_id, "identity_sha256": expected_hash}
