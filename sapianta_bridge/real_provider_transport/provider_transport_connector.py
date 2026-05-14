"""Deterministic local file provider transport connector."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .provider_transport_evidence import provider_transport_evidence
from .provider_transport_request import create_provider_transport_request
from .provider_transport_response import create_provider_transport_response
from .provider_transport_validator import (
    validate_envelope_for_transport,
    validate_provider_transport_request,
    validate_provider_transport_response,
)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_provider_task_artifact(*, request: dict[str, Any], transport_dir: Path) -> Path:
    transport_dir.mkdir(parents=True, exist_ok=True)
    path = transport_dir / f"{request['transport_id']}.task.json"
    _write_json(path, request)
    return path


def write_provider_result_artifact(*, response: dict[str, Any], transport_dir: Path) -> Path:
    transport_dir.mkdir(parents=True, exist_ok=True)
    path = transport_dir / f"{response['transport_id']}.result.json"
    _write_json(path, response)
    return path


def local_file_transport_roundtrip(*, envelope: dict[str, Any], transport_dir: str | Path) -> dict[str, Any]:
    envelope_validation = validate_envelope_for_transport(envelope)
    if not envelope_validation["valid"]:
        return {
            "transport_status": "BLOCKED",
            "envelope_validation": envelope_validation,
            "provider_transport_request": {},
            "provider_transport_response": {},
            "provider_transport_evidence": {
                "transport_id": "",
                "provider_id": envelope.get("provider_id", "") if isinstance(envelope, dict) else "",
                "envelope_id": envelope.get("envelope_id", "") if isinstance(envelope, dict) else "",
                "invocation_id": "",
                "replay_identity": envelope.get("replay_identity", "") if isinstance(envelope, dict) else "",
                "provider_transport_request_valid": False,
                "provider_transport_response_valid": False,
                "identity_continuity_valid": False,
                "local_file_transport_used": True,
                "real_external_api_call_present": False,
                "shell_execution_present": False,
                "routing_present": False,
                "retry_present": False,
                "fallback_present": False,
                "orchestration_present": False,
                "autonomous_execution_present": False,
                "replay_safe": False,
            },
        }
    directory = Path(transport_dir)
    request = create_provider_transport_request(envelope).to_dict()
    request_validation = validate_provider_transport_request(request)
    task_path = write_provider_task_artifact(request=request, transport_dir=directory)
    response = create_provider_transport_response(request=request).to_dict()
    result_path = write_provider_result_artifact(response=response, transport_dir=directory)
    inbound_response = _read_json(result_path)
    response_validation = validate_provider_transport_response(inbound_response, request=request)
    evidence = provider_transport_evidence(
        request=request,
        response=inbound_response,
        request_validation=request_validation,
        response_validation=response_validation,
        task_artifact_path=str(task_path),
        result_artifact_path=str(result_path),
    )
    return {
        "transport_status": "SUCCESS" if request_validation["valid"] and response_validation["valid"] else "BLOCKED",
        "envelope_validation": envelope_validation,
        "provider_transport_request": request,
        "provider_transport_response": inbound_response,
        "provider_transport_evidence": evidence,
        "task_artifact_path": str(task_path),
        "result_artifact_path": str(result_path),
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
    }
