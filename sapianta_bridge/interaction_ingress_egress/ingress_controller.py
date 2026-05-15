"""Deterministic local file ingress/egress controller."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge

from .egress_exporter import export_egress_artifact
from .ingress_binding import create_ingress_binding, validate_ingress_binding
from .ingress_evidence import ingress_evidence
from .ingress_request import load_ingress_artifact
from .ingress_response import create_ingress_response, validate_ingress_response
from .ingress_session import create_ingress_session, validate_ingress_session
from .ingress_state import SUCCESS_PATH, validate_ingress_state_chain
from .ingress_validator import validate_ingress_artifact


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "ingress_validation": {"valid": False, "errors": [{"field": "ingress", "reason": reason}]},
        "ingress_response": {"state": "BLOCKED"},
        "states": ["BLOCKED"],
        "orchestration_present": False,
        "retry_present": False,
        "routing_present": False,
        "background_daemon_present": False,
        "async_execution_present": False,
    }


def run_local_ingress_egress(*, ingress_path: str | Path, egress_path: str | Path) -> dict[str, Any]:
    try:
        artifact = load_ingress_artifact(ingress_path)
    except (OSError, ValueError):
        return _blocked("malformed ingress artifact")
    artifact_validation = validate_ingress_artifact(artifact)
    if not artifact_validation["valid"]:
        return _blocked("ingress artifact invalid")
    transport = run_interaction_transport_bridge(
        artifact["human_input"],
        execution_gate_id=artifact["execution_gate_id"],
        bounded_runtime_id=artifact["bounded_runtime_id"],
        result_capture_id=artifact["result_capture_id"],
        requested_provider_id=artifact["requested_provider_id"],
        conversation_id=artifact["conversation_id"],
    )
    if transport.get("transport_validation", {}).get("valid") is not True:
        return _blocked("transport continuity invalid")
    session = create_ingress_session(ingress_artifact=artifact, transport_session_id=transport["transport_session"]["transport_session_id"]).to_dict()
    binding = create_ingress_binding(ingress_session=session, transport_binding=transport["transport_binding"]).to_dict()
    response = create_ingress_response(ingress_session=session, transport_output=transport, binding=binding).to_dict()
    states = list(SUCCESS_PATH)
    validations = (
        validate_ingress_session(session),
        validate_ingress_binding(binding),
        validate_ingress_response(response),
        validate_ingress_state_chain(states),
    )
    valid = all(item["valid"] for item in validations)
    if not valid:
        return _blocked("egress continuity invalid")
    target = export_egress_artifact(response, egress_path)
    evidence = ingress_evidence(binding=binding, states=states, valid=True, egress_path=str(target))
    return {
        "ingress_artifact": artifact,
        "ingress_session": session,
        "ingress_binding": binding,
        "ingress_response": response,
        "ingress_evidence": evidence,
        "states": states,
        "transport_output": transport,
        "ingress_validation": {"valid": True, "errors": []},
        "egress_path": str(target),
        "orchestration_present": False,
        "retry_present": False,
        "routing_present": False,
        "background_daemon_present": False,
        "async_execution_present": False,
    }
