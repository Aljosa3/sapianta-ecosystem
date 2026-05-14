"""Controller for the first real bounded Codex E2E loop."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.active_invocation.invocation_evidence import invocation_evidence
from sapianta_bridge.active_invocation.invocation_lifecycle import complete_invocation_lifecycle
from sapianta_bridge.chatgpt_ingress.ingress_request import create_ingress_request
from sapianta_bridge.chatgpt_ingress.ingress_session import create_ingress_session
from sapianta_bridge.nl_envelope.envelope_generator import generate_envelope_proposal
from sapianta_bridge.nl_envelope.nl_request import create_nl_request
from sapianta_bridge.provider_connectors.bounded_execution_runtime import execute_bounded_codex
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import (
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    create_execution_gate_request,
)
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result

from .e2e_loop_binding import create_e2e_loop_binding
from .e2e_loop_evidence import e2e_loop_evidence
from .e2e_loop_request import REQUIRED_PROVIDER_ID
from .e2e_loop_response import create_e2e_loop_response
from .e2e_loop_validator import validate_e2e_loop_request, validate_e2e_loop_response


def _runtime_to_invocation_result(*, gate_request: dict[str, Any], bounded_result: dict[str, Any]) -> dict[str, Any]:
    status = bounded_result["bounded_execution_status"]
    capture = bounded_result["capture"]
    execution_status = "SUCCESS" if status == "SUCCESS" else "FAIL"
    normalized = NormalizedExecutionResult(
        provider_id=gate_request["provider_id"],
        execution_status=execution_status,
        artifacts_created=(),
        tests_executed=False,
        governance_modified=False,
        execution_time_ms=0,
        replay_safe=True,
        stdout_tail=capture.get("stdout", "")[-200:],
        stderr_tail=capture.get("stderr", "")[-200:],
    ).to_dict()
    runtime_status = "SUCCESS" if status == "SUCCESS" else "FAILED"
    runtime_result = {
        "runtime_status": runtime_status,
        "provider_id": gate_request["provider_id"],
        "envelope_id": gate_request["envelope_id"],
        "replay_identity": gate_request["replay_identity"],
        "artifacts": [],
        "runtime_guard_status": {
            "runtime_allowed": status in ("SUCCESS", "FAILED", "TIMEOUT"),
            "execution_gate_id": gate_request["execution_gate_id"],
        },
        "normalized_result": normalized,
        "replay_safe": True,
    }
    return {
        "invocation_status": runtime_status,
        "invocation_id": gate_request["invocation_id"],
        "provider_id": gate_request["provider_id"],
        "envelope_id": gate_request["envelope_id"],
        "replay_identity": gate_request["replay_identity"],
        "runtime_result": runtime_result,
        "normalized_result": normalized,
        "lifecycle": complete_invocation_lifecycle(),
        "adaptive_interpretation_present": False,
        "replay_safe": True,
    }


def _blocked_result(*, request: dict[str, Any], request_validation: dict[str, Any]) -> dict[str, Any]:
    evidence = e2e_loop_evidence(
        request=request,
        response=None,
        request_validation=request_validation,
        response_validation={"valid": False},
        runtime_result={},
    )
    return {
        "real_e2e_loop_status": "BLOCKED",
        "request_validation": request_validation,
        "response": {},
        "response_validation": {"valid": False, "errors": request_validation["errors"]},
        "evidence": evidence,
    }


def run_real_e2e_codex_loop(*, request: dict[str, Any]) -> dict[str, Any]:
    request_validation = validate_e2e_loop_request(request)
    if not request_validation["valid"]:
        return _blocked_result(request=request, request_validation=request_validation)

    ingress_session = create_ingress_session(raw_text=request["chatgpt_request"]).to_dict()
    ingress_request = create_ingress_request(session=ingress_session, raw_text=request["chatgpt_request"]).to_dict()
    semantic_request = create_nl_request(
        request["chatgpt_request"],
        semantic_request_id=f"SEM-{request['loop_id'][-12:]}",
    ).to_dict()
    semantic_request["replay_identity"] = request["replay_identity"]
    envelope_proposal = generate_envelope_proposal(semantic_request, provider_id=REQUIRED_PROVIDER_ID)
    envelope = envelope_proposal.get("execution_envelope")
    if not envelope:
        blocked_validation = {
            "valid": False,
            "errors": envelope_proposal.get("errors", envelope_proposal.get("envelope_validation", {}).get("errors", [])),
        }
        return _blocked_result(request=request, request_validation=blocked_validation)

    connector_preparation = prepare_codex_cli_task(envelope=envelope, connector_dir=request["workspace_path"])
    connector_request = connector_preparation["connector_request"]
    gate_request = create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=request["execution_authorized"],
        approved_by=request["approved_by"],
        workspace_path=request["workspace_path"],
        timeout_seconds=request["timeout_seconds"],
        operation=EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    ).to_dict()
    bounded_execution = execute_bounded_codex(
        gate_request=gate_request,
        codex_executable=request["codex_executable"],
    )
    if bounded_execution["bounded_execution_status"] == "BLOCKED":
        blocked_validation = bounded_execution["runtime_validation"]
        return _blocked_result(request=request, request_validation=blocked_validation)

    invocation_result = _runtime_to_invocation_result(gate_request=gate_request, bounded_result=bounded_execution)
    invocation_validation = {
        "provider_identity_valid": True,
        "envelope_valid": True,
        "runtime_binding_valid": True,
        "invocation_binding_valid": True,
    }
    invocation_record_evidence = invocation_evidence(
        request=gate_request,
        result=invocation_result,
        validation=invocation_validation,
    )
    result_return = return_invocation_result(
        invocation_result=invocation_result,
        invocation_evidence=invocation_record_evidence,
    )
    result_payload = result_return["result_payload"]
    binding = create_e2e_loop_binding(
        request=request,
        ingress_request=ingress_request,
        semantic_request=semantic_request,
        envelope=envelope,
        connector_request=connector_request,
        gate_request=gate_request,
        result_payload=result_payload,
    ).to_dict()
    runtime_bundle = {
        "ingress_request": ingress_request,
        "semantic_request": semantic_request,
        "envelope_proposal": envelope_proposal,
        "session_reference": {"session_id": f"SESSION-{request['loop_id'][-12:]}", "single_provider": True},
        "connector_preparation": connector_preparation,
        "execution_gate_request": gate_request,
        "bounded_execution": bounded_execution,
        "invocation_result": invocation_result,
        "invocation_evidence": invocation_record_evidence,
        "result_return": result_return,
    }
    response = create_e2e_loop_response(
        request=request,
        result_payload=result_payload,
        loop_binding=binding,
        evidence_references={
            "execution_gate_id": gate_request["execution_gate_id"],
            "invocation_id": invocation_result["invocation_id"],
            "result_return_id": result_payload["result_return_id"],
        },
    ).to_dict()
    response_validation = validate_e2e_loop_response(response, request=request)
    evidence = e2e_loop_evidence(
        request=request,
        response=response,
        request_validation=request_validation,
        response_validation=response_validation,
        runtime_result=runtime_bundle,
    )
    return {
        "real_e2e_loop_status": "SUCCESS" if response_validation["valid"] else "BLOCKED",
        "request_validation": request_validation,
        "response": response,
        "response_validation": response_validation,
        "runtime": runtime_bundle,
        "evidence": evidence,
    }
