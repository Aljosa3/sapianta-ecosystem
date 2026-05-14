"""Minimal live Codex validation case."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import (
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    create_execution_gate_request,
)


VALIDATION_NAME = "LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1"
VALIDATION_NAME_V2 = "LIVE_REAL_CODEX_EXECUTION_VALIDATION_V2"


@dataclass(frozen=True)
class LiveCodexValidationCase:
    validation_name: str
    workspace_path: str
    codex_executable: str
    envelope: dict[str, Any]
    connector_request: dict[str, Any]
    execution_gate_request: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_name": self.validation_name,
            "workspace_path": self.workspace_path,
            "codex_executable": self.codex_executable,
            "envelope": self.envelope,
            "connector_request": self.connector_request,
            "execution_gate_request": self.execution_gate_request,
            "safe_task_description": "Read prepared task artifact and return deterministic text; do not modify repository files.",
            "provider_id": "codex_cli",
            "execution_authorized": True,
            "timeout_seconds": self.execution_gate_request["timeout_seconds"],
            "replay_safe": True,
        }


def detect_codex_cli() -> str:
    return shutil.which("codex") or ""


def create_live_codex_validation_case(
    *,
    workspace_path: str | Path,
    codex_executable: str | None = None,
    timeout_seconds: int = 30,
) -> LiveCodexValidationCase | dict[str, Any]:
    executable = codex_executable if codex_executable is not None else detect_codex_cli()
    workspace = Path(workspace_path)
    workspace.mkdir(parents=True, exist_ok=True)
    if not executable:
        return {
            "validation_name": VALIDATION_NAME,
            "status": "BLOCKED",
            "blocked_reason": "codex CLI not detected",
            "codex_cli_detected": False,
            "workspace_path": str(workspace),
            "replay_safe": True,
        }
    envelope = create_execution_envelope(
        envelope_id="ENV-LIVE-CODEX-VALIDATION",
        provider_id="codex_cli",
        allowed_roots=["sapianta_bridge/provider_connectors/live_validation"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate", "write_repo_files", "network_access"],
        replay_identity="REPLAY-LIVE-CODEX-VALIDATION",
        validation_requirements=["live_codex_validation"],
        timeout_seconds=timeout_seconds,
    ).to_dict()
    connector_preparation = prepare_codex_cli_task(envelope=envelope, connector_dir=workspace)
    connector_request = connector_preparation["connector_request"]
    gate_request = create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(workspace),
        timeout_seconds=timeout_seconds,
        operation=EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    ).to_dict()
    return LiveCodexValidationCase(
        validation_name=VALIDATION_NAME,
        workspace_path=str(workspace),
        codex_executable=executable,
        envelope=envelope,
        connector_request=connector_request,
        execution_gate_request=gate_request,
    )


def create_live_codex_validation_case_v2(
    *,
    workspace_path: str | Path,
    codex_executable: str | None = None,
    timeout_seconds: int = 30,
) -> LiveCodexValidationCase | dict[str, Any]:
    case = create_live_codex_validation_case(
        workspace_path=workspace_path,
        codex_executable=codex_executable,
        timeout_seconds=timeout_seconds,
    )
    if isinstance(case, dict):
        return {**case, "validation_name": VALIDATION_NAME_V2}
    return LiveCodexValidationCase(
        validation_name=VALIDATION_NAME_V2,
        workspace_path=case.workspace_path,
        codex_executable=case.codex_executable,
        envelope=case.envelope,
        connector_request=case.connector_request,
        execution_gate_request=case.execution_gate_request,
    )
