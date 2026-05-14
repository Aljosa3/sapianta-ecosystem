"""Bounded governed execution transport bridge."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime

from .transport_evidence import transport_evidence
from .transport_guard import guard_transport
from .transport_request import create_transport_request, validate_transport_request
from .transport_response import create_transport_response


def build_transport_request(envelope: dict[str, Any]) -> dict[str, Any]:
    return create_transport_request(envelope).to_dict()


def execute_transport_bridge(
    *,
    envelope: dict[str, Any],
    provider: ExecutionProvider,
) -> dict[str, Any]:
    envelope_validation = validate_execution_envelope(envelope)
    if not envelope_validation["valid"]:
        request = build_transport_request(envelope) if "envelope_id" in envelope else {}
        return {
            "transport_response": {
                "transport_status": "BLOCKED",
                "envelope_id": envelope.get("envelope_id", ""),
                "provider_id": envelope.get("provider_id", ""),
                "replay_identity": envelope.get("replay_identity", ""),
                "runtime_result": {},
                "normalized_result": {},
                "runtime_evidence": {},
                "transport_evidence": {
                    "transport_executed": False,
                    "transport_id": request.get("transport_binding", {}).get("transport_id", ""),
                    "provider_id": envelope.get("provider_id", ""),
                    "envelope_id": envelope.get("envelope_id", ""),
                    "runtime_status": "BLOCKED",
                    "transport_binding_valid": False,
                    "runtime_binding_valid": False,
                    "authority_preserved": False,
                    "workspace_preserved": False,
                    "replay_safe": False,
                    "routing_present": False,
                    "orchestration_present": False,
                    "fallback_present": False,
                    "retry_present": False,
                },
                "replay_safe": False,
            },
            "transport_request": request,
            "transport_guard": {
                "transport_allowed": False,
                "errors": [{"field": "envelope", "reason": "envelope validation failed"}],
                "routing_present": False,
                "fallback_present": False,
                "retry_present": False,
            },
            "envelope_validation": envelope_validation,
            "routing_present": False,
            "orchestration_present": False,
        }
    request = build_transport_request(envelope)
    request_validation = validate_transport_request(request)
    guard_status = guard_transport(request=request, provider=provider)
    if not request_validation["valid"] or not guard_status["transport_allowed"]:
        runtime_output = execute_adapter_runtime(envelope=envelope, provider=provider)
    else:
        runtime_output = execute_adapter_runtime(envelope=envelope, provider=provider)
    evidence = transport_evidence(
        request=request,
        runtime_output=runtime_output,
        guard_status=guard_status,
    )
    response = create_transport_response(
        request=request,
        runtime_output=runtime_output,
        evidence=evidence,
    )
    return {
        "transport_request": request,
        "transport_response": response.to_dict(),
        "transport_guard": guard_status,
        "transport_evidence": evidence,
        "envelope_validation": envelope_validation,
        "request_validation": request_validation,
        "runtime_output": runtime_output,
        "routing_present": False,
        "orchestration_present": False,
    }
