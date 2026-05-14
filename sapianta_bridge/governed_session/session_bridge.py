"""Canonical governed execution session bridge."""

from __future__ import annotations

from typing import Any

from .session_context import create_session_context
from .session_evidence import session_evidence
from .session_identity import create_session_identity
from .session_lifecycle import blocked_session_lifecycle, complete_session_lifecycle
from .session_validator import validate_session_artifacts


def _blocked_session(reason: str) -> dict[str, Any]:
    identity = {
        "session_id": "",
        "ingress_id": "",
        "semantic_request_id": "",
        "envelope_id": "",
        "provider_id": "",
        "invocation_id": "",
        "result_return_id": "",
        "replay_identity": "",
        "identity_sha256": "",
        "replay_safe": False,
        "immutable": True,
    }
    context = {
        "ingress_reference": {},
        "envelope_reference": {},
        "provider_invocation_reference": {},
        "result_loop_reference": {},
        "evidence_references": {},
        "mutable_hidden_memory_present": False,
        "autonomous_plan_present": False,
        "retry_queue_present": False,
        "routing_decision_present": False,
        "future_task_instructions_present": False,
        "replay_safe": False,
    }
    lifecycle = blocked_session_lifecycle()
    validation = {
        "valid": False,
        "errors": [{"field": "session", "reason": reason}],
        "identity_valid": False,
        "context_valid": False,
        "lifecycle_valid": True,
        "provider_identity_consistent": False,
        "envelope_identity_consistent": False,
        "replay_safe": False,
        "routing_present": False,
        "retry_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
    }
    evidence = session_evidence(identity=identity, context=context, lifecycle=lifecycle, validation=validation)
    return {
        "session_identity": identity,
        "session_context": context,
        "session_lifecycle": lifecycle,
        "session_validation": validation,
        "session_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }


def create_governed_execution_session(
    *,
    ingress_output: dict[str, Any],
    invocation_output: dict[str, Any],
    result_output: dict[str, Any],
) -> dict[str, Any]:
    try:
        identity = create_session_identity(
            ingress_output=ingress_output,
            invocation_output=invocation_output,
            result_output=result_output,
        ).to_dict()
        context = create_session_context(
            ingress_output=ingress_output,
            invocation_output=invocation_output,
            result_output=result_output,
        ).to_dict()
    except (KeyError, TypeError):
        return _blocked_session("missing required session artifact")
    lifecycle = complete_session_lifecycle()
    validation = validate_session_artifacts(identity=identity, context=context, lifecycle=lifecycle)
    evidence = session_evidence(identity=identity, context=context, lifecycle=lifecycle, validation=validation)
    return {
        "session_identity": identity,
        "session_context": context,
        "session_lifecycle": lifecycle if validation["valid"] else blocked_session_lifecycle(),
        "session_validation": validation,
        "session_evidence": evidence,
        "orchestration_present": False,
        "retry_present": False,
        "provider_routing_present": False,
        "autonomous_execution_present": False,
        "hidden_memory_mutation_present": False,
    }
