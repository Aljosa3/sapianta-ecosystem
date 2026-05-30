"""Deterministic provider proposal envelope for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


ENVELOPE_TYPE = "PROVIDER_PROPOSAL_ENVELOPE_V1"

FORBIDDEN_FIELDS = frozenset(
    {
        "authority",
        "execution_capable",
        "provider_invoked",
        "worker_invoked",
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_command",
        "worker_command",
        "worker_instruction",
        "dispatch_request",
        "memory_mutation",
        "replay_mutation",
    }
)


@dataclass(frozen=True)
class ProviderProposalEnvelope:
    proposal_id: str
    provider_id: str
    provider_version: str
    request: Any
    response: Any
    timestamp: str
    proposal_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        envelope = {
            "envelope_type": ENVELOPE_TYPE,
            "proposal_id": _require_string(self.proposal_id, "proposal_id"),
            "provider_id": _require_string(self.provider_id, "provider_id"),
            "provider_version": _require_string(self.provider_version, "provider_version"),
            "request": _require_json_value(self.request, "request"),
            "response": _require_non_empty_json_value(self.response, "response"),
            "timestamp": _require_string(self.timestamp, "timestamp"),
            "replay_visible": True,
        }
        _validate_no_forbidden_payload(envelope["request"], "request")
        _validate_no_forbidden_payload(envelope["response"], "response")
        envelope["proposal_hash"] = self.proposal_hash or replay_hash(envelope)
        return envelope


def create_provider_proposal_envelope(
    *,
    proposal_id: str,
    provider_id: str,
    provider_version: str,
    request: Any,
    response: Any,
    timestamp: str,
) -> ProviderProposalEnvelope:
    envelope = ProviderProposalEnvelope(
        proposal_id=proposal_id,
        provider_id=provider_id,
        provider_version=provider_version,
        request=deepcopy(request),
        response=deepcopy(response),
        timestamp=timestamp,
    )
    envelope_dict = envelope.to_dict()
    return ProviderProposalEnvelope(
        proposal_id=envelope.proposal_id,
        provider_id=envelope.provider_id,
        provider_version=envelope.provider_version,
        request=envelope.request,
        response=envelope.response,
        timestamp=envelope.timestamp,
        proposal_hash=envelope_dict["proposal_hash"],
    )


def validate_provider_proposal_envelope(envelope: ProviderProposalEnvelope | dict[str, Any]) -> dict[str, Any]:
    envelope_dict = envelope.to_dict() if isinstance(envelope, ProviderProposalEnvelope) else deepcopy(envelope)
    if not isinstance(envelope_dict, dict):
        raise FailClosedRuntimeError("provider proposal envelope must be a JSON object")
    if envelope_dict.get("envelope_type") != ENVELOPE_TYPE:
        raise FailClosedRuntimeError("provider proposal envelope type is invalid")
    if FORBIDDEN_FIELDS.intersection(envelope_dict):
        raise FailClosedRuntimeError("provider proposal envelope contains authority-bearing field")
    if envelope_dict.get("replay_visible") is not True:
        raise FailClosedRuntimeError("provider proposal envelope must be replay visible")
    _require_string(envelope_dict.get("proposal_id"), "proposal_id")
    _require_string(envelope_dict.get("provider_id"), "provider_id")
    _require_string(envelope_dict.get("provider_version"), "provider_version")
    _require_string(envelope_dict.get("timestamp"), "timestamp")
    _require_json_value(envelope_dict.get("request"), "request")
    _require_non_empty_json_value(envelope_dict.get("response"), "response")
    _validate_no_forbidden_payload(envelope_dict["request"], "request")
    _validate_no_forbidden_payload(envelope_dict["response"], "response")
    actual_hash = _require_string(envelope_dict.get("proposal_hash"), "proposal_hash")
    expected_input = deepcopy(envelope_dict)
    expected_input.pop("proposal_hash")
    if actual_hash != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider proposal envelope hash mismatch")
    return envelope_dict


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_json_value(value: Any, field_name: str) -> Any:
    try:
        replay_hash(value)
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError(f"{field_name} must be JSON serializable") from exc
    return deepcopy(value)


def _require_non_empty_json_value(value: Any, field_name: str) -> Any:
    normalized = _require_json_value(value, field_name)
    if normalized is None:
        raise FailClosedRuntimeError(f"{field_name} is required")
    if isinstance(normalized, str) and not normalized.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    if isinstance(normalized, (dict, list)) and not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _validate_no_forbidden_payload(value: Any, field_name: str) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_FIELDS.intersection(value):
            raise FailClosedRuntimeError(f"{field_name} contains authority-bearing field")
        for nested in value.values():
            _validate_no_forbidden_payload(nested, field_name)
    elif isinstance(value, list):
        for nested in value:
            _validate_no_forbidden_payload(nested, field_name)
