"""Replay-safe active ChatGPT bridge binding."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


BINDING_FIELDS = (
    "bridge_id",
    "bridge_request_id",
    "ingress_session_id",
    "semantic_request_id",
    "provider_id",
    "envelope_id",
    "session_id",
    "invocation_id",
    "result_return_id",
    "replay_identity",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def bridge_id_for(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS if field != "bridge_id"}
    return f"CHATGPT-BRIDGE-{stable_hash(payload)[:24]}"


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return stable_hash(payload)


@dataclass(frozen=True)
class BridgeBinding:
    bridge_id: str
    bridge_request_id: str
    ingress_session_id: str
    semantic_request_id: str
    provider_id: str
    envelope_id: str
    session_id: str
    invocation_id: str
    result_return_id: str
    replay_identity: str
    evidence_hashes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        value = {
            "bridge_id": self.bridge_id,
            "bridge_request_id": self.bridge_request_id,
            "ingress_session_id": self.ingress_session_id,
            "semantic_request_id": self.semantic_request_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "session_id": self.session_id,
            "invocation_id": self.invocation_id,
            "result_return_id": self.result_return_id,
            "replay_identity": self.replay_identity,
            "evidence_hashes": self.evidence_hashes,
        }
        value["binding_sha256"] = binding_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_bridge_binding(
    *,
    bridge_request: dict[str, Any],
    ingress_output: dict[str, Any],
    session_output: dict[str, Any],
    invocation_output: dict[str, Any],
    result_output: dict[str, Any],
) -> BridgeBinding:
    proposal = ingress_output["envelope_proposal"]
    session_identity = session_output["session_identity"]
    invocation_result = invocation_output["invocation_result"]
    result_payload = result_output["result_payload"]
    payload = {
        "bridge_request_id": bridge_request["bridge_request_id"],
        "ingress_session_id": ingress_output["session"]["session_id"],
        "semantic_request_id": proposal["semantic_request"]["semantic_request_id"],
        "provider_id": proposal["execution_envelope"]["provider_id"],
        "envelope_id": proposal["execution_envelope"]["envelope_id"],
        "session_id": session_identity["session_id"],
        "invocation_id": invocation_result["invocation_id"],
        "result_return_id": result_payload["result_return_id"],
        "replay_identity": proposal["execution_envelope"]["replay_identity"],
    }
    return BridgeBinding(
        bridge_id=bridge_id_for(payload),
        evidence_hashes={
            "ingress_evidence": stable_hash(ingress_output.get("ingress_evidence", {})),
            "session_evidence": stable_hash(session_output.get("session_evidence", {})),
            "invocation_evidence": stable_hash(invocation_output.get("invocation_evidence", {})),
            "result_evidence": stable_hash(result_output.get("result_evidence", {})),
        },
        **payload,
    )


def validate_bridge_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, BridgeBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "bridge_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing bridge binding field"})
    for field in BINDING_FIELDS:
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "bridge binding field must be non-empty"})
    expected_id = bridge_id_for(value) if not errors else None
    expected_hash = binding_hash(value) if not errors else None
    if "bridge_id" in value and value["bridge_id"] != expected_id:
        errors.append({"field": "bridge_id", "reason": "bridge identity mismatch"})
    if "binding_sha256" in value and value["binding_sha256"] != expected_hash:
        errors.append({"field": "binding_sha256", "reason": "bridge binding hash mismatch"})
    if not isinstance(value.get("evidence_hashes"), dict) or not value.get("evidence_hashes"):
        errors.append({"field": "evidence_hashes", "reason": "bridge evidence hashes required"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "bridge binding must be replay-safe"})
    return {"valid": not errors, "errors": errors, "bridge_id": expected_id, "binding_sha256": expected_hash}
