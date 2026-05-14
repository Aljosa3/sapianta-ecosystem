"""Codex CLI connector in deterministic PREPARE_ONLY mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request
from sapianta_bridge.real_provider_transport.provider_transport_validator import validate_envelope_for_transport

from .connector_evidence import connector_evidence
from .connector_request import create_connector_request
from .connector_response import create_connector_response
from .connector_validator import validate_connector_request, validate_connector_response


CODEX_CONNECTOR_MODE = "PREPARE_ONLY"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_codex_cli_task(*, envelope: dict[str, Any], connector_dir: str | Path) -> dict[str, Any]:
    """Write a Codex-facing task artifact without invoking Codex."""

    envelope_validation = validate_envelope_for_transport(envelope)
    if not envelope_validation["valid"]:
        return {
            "connector_status": "BLOCKED",
            "connector_mode": CODEX_CONNECTOR_MODE,
            "envelope_validation": envelope_validation,
            "connector_request": {},
            "connector_evidence": {
                "connector_id": "",
                "connector_mode": CODEX_CONNECTOR_MODE,
                "provider_id": envelope.get("provider_id", "") if isinstance(envelope, dict) else "",
                "envelope_id": envelope.get("envelope_id", "") if isinstance(envelope, dict) else "",
                "invocation_id": "",
                "transport_id": "",
                "replay_identity": envelope.get("replay_identity", "") if isinstance(envelope, dict) else "",
                "connector_request_valid": False,
                "connector_response_valid": False,
                "task_artifact_written": False,
                "codex_cli_invoked": False,
                "real_external_api_call_present": False,
                "shell_execution_present": False,
                "network_execution_present": False,
                "routing_present": False,
                "retry_present": False,
                "fallback_present": False,
                "orchestration_present": False,
                "autonomous_execution_present": False,
                "provider_auto_selection_present": False,
                "connector_artifact_is_execution_authority": False,
                "provider_response_is_governance_decision": False,
                "replay_safe": False,
            },
        }
    directory = Path(connector_dir)
    directory.mkdir(parents=True, exist_ok=True)
    transport_request = create_provider_transport_request(envelope).to_dict()
    task_path = directory / f"{transport_request['transport_id']}.codex-task.json"
    result_path = directory / f"{transport_request['transport_id']}.codex-result.json"
    connector_request = create_connector_request(
        provider_transport_request=transport_request,
        bounded_task_artifact_path=str(task_path),
        expected_result_artifact_path=str(result_path),
    ).to_dict()
    request_validation = validate_connector_request(connector_request)
    if request_validation["valid"]:
        _write_json(task_path, connector_request)
        task_written = True
    else:
        task_written = False
    evidence = connector_evidence(
        connector_request=connector_request,
        request_validation=request_validation,
        task_artifact_written=task_written,
    )
    return {
        "connector_status": "PREPARED" if request_validation["valid"] else "BLOCKED",
        "connector_mode": CODEX_CONNECTOR_MODE,
        "envelope_validation": envelope_validation,
        "provider_transport_request": transport_request,
        "connector_request": connector_request,
        "connector_evidence": evidence,
        "task_artifact_path": str(task_path),
        "expected_result_artifact_path": str(result_path),
        "codex_cli_invoked": False,
        "shell_execution_present": False,
        "network_execution_present": False,
    }


def read_codex_cli_result(*, connector_request: dict[str, Any], result_artifact_path: str | Path) -> dict[str, Any]:
    """Read and validate a provider-side result artifact without invoking Codex."""

    path = Path(result_artifact_path)
    provider_transport_response = _read_json(path)
    connector_response = create_connector_response(
        connector_request=connector_request,
        provider_transport_response=provider_transport_response,
        result_artifact_path=str(path),
    ).to_dict()
    request_validation = validate_connector_request(connector_request)
    response_validation = validate_connector_response(connector_response, request=connector_request)
    evidence = connector_evidence(
        connector_request=connector_request,
        connector_response=connector_response,
        request_validation=request_validation,
        response_validation=response_validation,
        task_artifact_written=Path(connector_request["bounded_task_artifact_path"]).exists(),
    )
    return {
        "connector_status": "SUCCESS" if response_validation["valid"] else "BLOCKED",
        "connector_mode": CODEX_CONNECTOR_MODE,
        "provider_transport_response": provider_transport_response,
        "connector_response": connector_response,
        "connector_evidence": evidence,
        "codex_cli_invoked": False,
        "shell_execution_present": False,
        "network_execution_present": False,
    }
