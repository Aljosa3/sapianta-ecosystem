"""Bounded execution gate controller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .execution_gate_evidence import execution_gate_evidence
from .execution_gate_request import EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK
from .execution_gate_response import create_execution_gate_response
from .execution_gate_validator import validate_execution_gate_request, validate_execution_gate_response


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def execute_through_execution_gate(*, request: dict[str, Any]) -> dict[str, Any]:
    """Run the single bounded execution gate operation after validation."""

    request_validation = validate_execution_gate_request(request)
    if not request_validation["valid"]:
        response = create_execution_gate_response(
            request=request,
            status="BLOCKED",
            stderr="execution gate validation failed",
            exit_code=1,
            result_metadata={"validation_errors": request_validation["errors"]},
        ).to_dict()
        response_validation = validate_execution_gate_response(response, request=request)
        return {
            "execution_gate_status": "BLOCKED",
            "execution_gate_request_validation": request_validation,
            "execution_gate_response": response,
            "execution_gate_response_validation": response_validation,
            "execution_gate_evidence": execution_gate_evidence(
                request=request,
                response=response,
                request_validation=request_validation,
                response_validation=response_validation,
            ),
        }
    if request["operation"] != EXECUTION_GATE_OPERATION_CAPTURE_CONNECTOR_TASK:
        response = create_execution_gate_response(
            request=request,
            status="BLOCKED",
            stderr="unsupported execution gate operation",
            exit_code=1,
        ).to_dict()
    else:
        task_path = Path(request["connector_request"]["bounded_task_artifact_path"])
        task_artifact = json.loads(task_path.read_text(encoding="utf-8"))
        stdout = _canonical_json(
            {
                "captured_connector_id": task_artifact["connector_id"],
                "captured_provider_id": task_artifact["provider_id"],
                "captured_envelope_id": task_artifact["envelope_id"],
                "captured_invocation_id": task_artifact["invocation_id"],
                "captured_transport_id": task_artifact["transport_id"],
                "captured_replay_identity": task_artifact["replay_identity"],
                "operation": request["operation"],
            }
        )
        response = create_execution_gate_response(
            request=request,
            status="SUCCESS",
            stdout=stdout,
            stderr="",
            exit_code=0,
            result_metadata={
                "operation": request["operation"],
                "task_artifact_path": str(task_path),
                "workspace_path": request["workspace_path"],
                "bounded_local_execution": True,
            },
        ).to_dict()
    response_validation = validate_execution_gate_response(response, request=request)
    evidence = execution_gate_evidence(
        request=request,
        response=response,
        request_validation=request_validation,
        response_validation=response_validation,
    )
    return {
        "execution_gate_status": "SUCCESS" if response_validation["valid"] and response["status"] == "SUCCESS" else "BLOCKED",
        "execution_gate_request_validation": request_validation,
        "execution_gate_response": response,
        "execution_gate_response_validation": response_validation,
        "execution_gate_evidence": evidence,
    }
