"""Operational no-copy/paste validation controller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.human_interaction_continuity.interaction_session import stable_hash
from sapianta_bridge.interaction_ingress_egress.ingress_validator import validate_ingress_artifact
from sapianta_bridge.provider_connectors.bounded_execution_runtime import execute_bounded_codex
from sapianta_bridge.provider_connectors.bounded_runtime_state import runtime_state_session_id
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import EXECUTION_GATE_OPERATION_CODEX_CLI_RUN, create_execution_gate_request

from .no_copy_paste_validation_binding import ValidationBinding, capture_id_for
from .no_copy_paste_validation_evidence import validation_evidence
from .no_copy_paste_validation_request import NoCopyPasteValidationRequest
from .no_copy_paste_validation_response import NoCopyPasteValidationResponse
from .no_copy_paste_validation_state import SUCCESS_STATE
from .no_copy_paste_validation_validator import validate_flow


def _write(path: str | Path, value: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n", encoding="utf-8")


def run_no_copy_paste_validation(request: NoCopyPasteValidationRequest | dict[str, Any]) -> dict[str, Any]:
    value = request.to_dict() if isinstance(request, NoCopyPasteValidationRequest) else request
    ingress_path = Path(value["ingress_path"])
    try:
        ingress = json.loads(ingress_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"validation": {"valid": False, "errors": [{"field": "ingress", "reason": "invalid ingress artifact"}]}, "status": "BLOCKED"}
    ingress_validation = validate_ingress_artifact(ingress)
    if not ingress_validation["valid"]:
        return {"validation": ingress_validation, "status": "BLOCKED"}
    replay_identity = f"REPLAY-NO-COPY-{stable_hash(ingress)[:16]}"
    envelope = create_execution_envelope(
        envelope_id=f"ENV-NO-COPY-{stable_hash(ingress)[:16]}",
        provider_id="codex_cli",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity=replay_identity,
        validation_requirements=["bounded_no_copy_validation"],
    ).to_dict()
    prepared = prepare_codex_cli_task(envelope=envelope, connector_dir=value["workspace_path"])
    gate = create_execution_gate_request(
        connector_request=prepared["connector_request"],
        execution_authorized=True,
        approved_by="human",
        workspace_path=value["workspace_path"],
        timeout_seconds=30,
        operation=EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    ).to_dict()
    execution = execute_bounded_codex(gate_request=gate, codex_executable=value["codex_executable"])
    runtime_id = runtime_state_session_id(provider_id="codex_cli", invocation_id=gate["invocation_id"], replay_identity=replay_identity)
    capture_id = capture_id_for(gate["execution_gate_id"])
    response_return_id = f"RETURN-{stable_hash({'capture_id': capture_id, 'replay_identity': replay_identity})[:24]}"
    binding = ValidationBinding(
        ingress_artifact_id=ingress.get("ingress_artifact_id", ""),
        execution_gate_id=gate["execution_gate_id"],
        provider_invocation_id=gate["invocation_id"],
        bounded_runtime_id=runtime_id,
        result_capture_id=capture_id,
        response_return_id=response_return_id,
        replay_identity=replay_identity,
    ).to_dict()
    normalized = {
        "execution_status": execution.get("bounded_execution_status", "BLOCKED"),
        "provider_id": "codex_cli",
        "capture": execution.get("capture", {}),
        "provider_output_rewritten": False,
        "provider_success_fabricated": False,
        "replay_identity": replay_identity,
    }
    response = NoCopyPasteValidationResponse(SUCCESS_STATE, binding, normalized).to_dict()
    validation = validate_flow(binding=binding, execution=execution, response=response)
    if not validation["valid"]:
        response["status"] = "BLOCKED"
    _write(value["egress_path"], response)
    evidence = validation_evidence(response=response, execution=execution, egress_path=value["egress_path"], valid=validation["valid"])
    return {
        "request": value,
        "ingress_artifact": ingress,
        "execution_gate": gate,
        "execution": execution,
        "response": response,
        "validation": validation,
        "evidence": evidence,
        "egress_path": value["egress_path"],
        "manual_prompt_relay_present": False,
        "orchestration_present": False,
        "retry_present": False,
        "routing_present": False,
    }
