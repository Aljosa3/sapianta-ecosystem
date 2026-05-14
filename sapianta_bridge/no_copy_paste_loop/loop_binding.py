"""Replay-safe no-copy/paste loop binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.active_chatgpt_bridge.bridge_binding import stable_hash


BINDING_FIELDS = (
    "loop_id",
    "loop_request_id",
    "bridge_id",
    "session_id",
    "envelope_id",
    "provider_id",
    "invocation_id",
    "result_return_id",
    "replay_identity",
)


def loop_id_for(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS if field != "loop_id"}
    return f"NO-COPY-LOOP-{stable_hash(payload)[:24]}"


def binding_hash(value: dict[str, Any]) -> str:
    payload = {field: value.get(field) for field in BINDING_FIELDS}
    return stable_hash(payload)


@dataclass(frozen=True)
class LoopBinding:
    loop_id: str
    loop_request_id: str
    bridge_id: str
    session_id: str
    envelope_id: str
    provider_id: str
    invocation_id: str
    result_return_id: str
    replay_identity: str
    evidence_hashes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        value = {
            "loop_id": self.loop_id,
            "loop_request_id": self.loop_request_id,
            "bridge_id": self.bridge_id,
            "session_id": self.session_id,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "invocation_id": self.invocation_id,
            "result_return_id": self.result_return_id,
            "replay_identity": self.replay_identity,
            "evidence_hashes": self.evidence_hashes,
        }
        value["binding_sha256"] = binding_hash(value)
        value["immutable"] = True
        value["replay_safe"] = True
        return value


def create_loop_binding(*, loop_request: dict[str, Any], bridge_output: dict[str, Any]) -> LoopBinding:
    bridge_binding = bridge_output["bridge_binding"]
    bridge_response = bridge_output["bridge_response"]
    payload = {
        "loop_request_id": loop_request["loop_request_id"],
        "bridge_id": bridge_binding["bridge_id"],
        "session_id": bridge_response["session_id"],
        "envelope_id": bridge_response["envelope_id"],
        "provider_id": bridge_response["provider_id"],
        "invocation_id": bridge_response["invocation_id"],
        "result_return_id": bridge_response["interpretation_ready_payload"]["result_return_id"],
        "replay_identity": bridge_response["replay_identity"],
    }
    return LoopBinding(
        loop_id=loop_id_for(payload),
        evidence_hashes={
            "bridge_evidence": stable_hash(bridge_output.get("bridge_evidence", {})),
            "session_evidence": stable_hash(bridge_output.get("session_output", {}).get("session_evidence", {})),
            "result_evidence": stable_hash(bridge_output.get("result_output", {}).get("result_evidence", {})),
        },
        **payload,
    )


def validate_loop_binding(binding: Any) -> dict[str, Any]:
    value = binding.to_dict() if isinstance(binding, LoopBinding) else binding
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "loop_binding", "reason": "must be an object"}]}
    for field in BINDING_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing loop binding field"})
    for field in BINDING_FIELDS:
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "loop binding field must be non-empty"})
    expected_id = loop_id_for(value) if not errors else None
    expected_hash = binding_hash(value) if not errors else None
    if "loop_id" in value and value["loop_id"] != expected_id:
        errors.append({"field": "loop_id", "reason": "loop identity mismatch"})
    if "binding_sha256" in value and value["binding_sha256"] != expected_hash:
        errors.append({"field": "binding_sha256", "reason": "loop binding hash mismatch"})
    if not isinstance(value.get("evidence_hashes"), dict) or not value.get("evidence_hashes"):
        errors.append({"field": "evidence_hashes", "reason": "loop evidence hashes required"})
    return {"valid": not errors, "errors": errors, "loop_id": expected_id, "binding_sha256": expected_hash}
