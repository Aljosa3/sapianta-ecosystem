"""Bounded active provider invocation bridge."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime

from .invocation_evidence import invocation_evidence
from .invocation_lifecycle import complete_invocation_lifecycle
from .invocation_request import create_invocation_request
from .invocation_result import blocked_invocation_result, create_invocation_result
from .invocation_validator import validate_invocation_request


def invoke_provider(
    *,
    envelope: dict[str, Any],
    provider: ExecutionProvider,
    provider_id: str | None = None,
) -> dict[str, Any]:
    try:
        request = create_invocation_request(envelope, provider_id or provider.contract.provider_id).to_dict()
    except (KeyError, TypeError):
        request = {
            "invocation_id": "",
            "envelope": envelope if isinstance(envelope, dict) else {},
            "envelope_id": envelope.get("envelope_id", "") if isinstance(envelope, dict) else "",
            "provider_id": provider_id or getattr(provider.contract, "provider_id", ""),
            "replay_identity": envelope.get("replay_identity", "") if isinstance(envelope, dict) else "",
            "runtime_binding": {},
            "invocation_binding": {},
            "provider_auto_selection": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "concurrent_execution_present": False,
            "replay_safe": False,
        }
        validation = {
            "valid": False,
            "errors": [{"field": "envelope", "reason": "malformed invocation envelope"}],
            "envelope_valid": False,
            "provider_identity_valid": False,
            "runtime_binding_valid": False,
            "invocation_binding_valid": False,
            "lifecycle_valid": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
        }
        blocked = blocked_invocation_result(request, ["PROPOSED"]).to_dict()
        evidence = invocation_evidence(request=request, result=blocked, validation=validation)
        return {
            "invocation_request": request,
            "invocation_result": blocked,
            "invocation_evidence": evidence,
            "invocation_validation": validation,
            "runtime_output": {},
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
        }
    proposed_lifecycle = ["PROPOSED"]
    proposed_validation = validate_invocation_request(
        request=request,
        provider=provider,
        lifecycle=proposed_lifecycle,
    )
    if not proposed_validation["valid"]:
        blocked = blocked_invocation_result(request, proposed_lifecycle).to_dict()
        evidence = invocation_evidence(request=request, result=blocked, validation=proposed_validation)
        return {
            "invocation_request": request,
            "invocation_result": blocked,
            "invocation_evidence": evidence,
            "invocation_validation": proposed_validation,
            "runtime_output": {},
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
        }

    lifecycle = complete_invocation_lifecycle()
    validation = validate_invocation_request(request=request, provider=provider, lifecycle=lifecycle)
    if not validation["valid"]:
        blocked = blocked_invocation_result(request, ["PROPOSED", "VALIDATED"]).to_dict()
        evidence = invocation_evidence(request=request, result=blocked, validation=validation)
        return {
            "invocation_request": request,
            "invocation_result": blocked,
            "invocation_evidence": evidence,
            "invocation_validation": validation,
            "runtime_output": {},
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
        }

    runtime_output = execute_adapter_runtime(envelope=envelope, provider=provider)
    result = create_invocation_result(
        request=request,
        runtime_output=runtime_output,
        lifecycle=lifecycle,
    ).to_dict()
    evidence = invocation_evidence(request=request, result=result, validation=validation)
    return {
        "invocation_request": request,
        "invocation_result": result,
        "invocation_evidence": evidence,
        "invocation_validation": validation,
        "runtime_output": runtime_output,
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
    }
