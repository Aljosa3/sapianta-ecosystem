"""Execution handoff command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from agol_bridge.chatgpt_ingress.controlled_execution_handoff import create_controlled_execution_handoff
from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cli.commands.continuity import build_governed_chain
from aigol.cli.commands.return_continuity import (
    generate_governed_return_artifact,
    persist_governed_return_artifact,
)

ALLOWED_EXECUTION_STATUSES = ("EXECUTION_COMPLETED", "EXECUTION_FAILED", "EXECUTION_BLOCKED")


def _provider_result_from_artifact(artifact: dict) -> dict:
    native_response = artifact.get("native_response", {}) if isinstance(artifact.get("native_response"), dict) else {}
    result_artifact = native_response.get("result_artifact", {}) if isinstance(native_response.get("result_artifact"), dict) else {}
    codex_result = result_artifact.get("codex_cli_result", {}) if isinstance(result_artifact.get("codex_cli_result"), dict) else {}
    provider_result = codex_result.get("provider_result", {}) if isinstance(codex_result.get("provider_result"), dict) else {}
    if provider_result:
        return provider_result
    return {
        "status": artifact.get("execution_result_summary", {}).get("provider_status", "NOT_INVOKED"),
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "diagnostic_evidence": {},
    }


def _governed_return_hash_input(return_artifact: dict) -> dict:
    copy = dict(return_artifact)
    copy.pop("governed_return_hash", None)
    return copy


def create_governed_return_artifact(*, execution_artifact: dict) -> dict:
    provider_result = _provider_result_from_artifact(execution_artifact)
    provider_diagnostics = provider_result.get("diagnostic_evidence", {}) if isinstance(provider_result.get("diagnostic_evidence"), dict) else {}
    execution_status = execution_artifact.get("execution_status", "EXECUTION_BLOCKED")
    if execution_status not in ALLOWED_EXECUTION_STATUSES:
        execution_status = "EXECUTION_BLOCKED"
    provider_invoked = execution_artifact.get("provider_invoked") is True
    continuity_verified = bool(
        execution_status in ("EXECUTION_COMPLETED", "EXECUTION_FAILED")
        and provider_invoked
        and execution_artifact.get("replay_identity")
        and execution_artifact.get("execution_governance_hash", "").startswith("sha256:")
    )
    return_artifact = {
        "artifact_type": "CLI_GOVERNED_RETURN_CONTINUITY_V1",
        "execution_status": execution_status,
        "provider_invoked": provider_invoked,
        "provider_result": provider_result,
        "provider_exit_code": provider_result.get("returncode"),
        "replay_identity": execution_artifact.get("replay_identity", "UNKNOWN"),
        "execution_governance_hash": execution_artifact.get("execution_governance_hash", ""),
        "continuity_verified": continuity_verified,
        "fail_closed": execution_status != "EXECUTION_COMPLETED",
        "diagnostic_evidence": {
            "provider_invoked": provider_invoked,
            "provider_executable_found": provider_diagnostics.get("codex_executable_found", False),
            "provider_executable_path": provider_diagnostics.get("codex_executable", ""),
            "provider_command": provider_diagnostics.get("provider_command", provider_result.get("command", [])),
            "provider_exit_code": provider_result.get("returncode"),
            "provider_stdout": provider_result.get("stdout", ""),
            "provider_stderr": provider_result.get("stderr", ""),
            "provider_timeout": provider_diagnostics.get("provider_timeout", False),
            "execution_runtime_seconds": provider_diagnostics.get("provider_runtime_seconds", 0),
            "governed_return_generated": True,
            "continuity_verified": continuity_verified,
            "failure_stage": provider_diagnostics.get("failing_layer", "") if execution_status != "EXECUTION_COMPLETED" else "",
            "fail_closed": execution_status != "EXECUTION_COMPLETED",
            "provider_success": provider_diagnostics.get("provider_success", execution_status == "EXECUTION_COMPLETED"),
            "provider_failure_reason": provider_diagnostics.get("provider_failure_reason", ""),
            "subprocess_invoked": provider_diagnostics.get("subprocess_invoked", False),
        },
    }
    return_artifact["governed_return_hash"] = canonical_hash(_governed_return_hash_input(return_artifact))
    return_artifact["diagnostic_evidence"]["governed_return_hash"] = return_artifact["governed_return_hash"]
    return return_artifact


def run_execution_handoff(
    *,
    ingress_artifact: dict,
    workspace_path: str | None = None,
    timeout_seconds: int = 600,
    native_message_handler: Callable[[dict], dict] | None = None,
    provider_success_proof: bool = True,
    persist_return: bool = True,
    runtime_root: str | Path | None = None,
) -> dict:
    chain = build_governed_chain(ingress_artifact=ingress_artifact)
    kwargs = {
        "continuity_preview": chain["continuity_preview"],
        "workspace_path": workspace_path or str(Path.cwd()),
        "timeout_seconds": timeout_seconds,
        "provider_success_proof": provider_success_proof,
    }
    if native_message_handler is not None:
        kwargs["native_message_handler"] = native_message_handler
    artifact = create_controlled_execution_handoff(**kwargs)
    governed_return = create_governed_return_artifact(execution_artifact=artifact)
    governed_return_artifact = generate_governed_return_artifact(
        execution_artifact=artifact,
        cli_governed_return=governed_return,
        chain=chain,
    )
    if governed_return_artifact.get("governed_return_hash", "").startswith("sha256:"):
        governed_return["governed_return_hash"] = governed_return_artifact["governed_return_hash"]
        governed_return.setdefault("diagnostic_evidence", {})["governed_return_hash"] = governed_return_artifact["governed_return_hash"]
    persistence = (
        persist_governed_return_artifact(
            artifact=governed_return_artifact,
            provider_result=governed_return["provider_result"],
            runtime_root=runtime_root,
        )
        if persist_return
        else {"status": "NOT_PERSISTED", "fail_closed": False}
    )
    return {
        "command": "aigol execution handoff",
        "execution_artifact": artifact,
        "governed_return": governed_return,
        "governed_return_artifact": governed_return_artifact,
        "persistence": persistence,
        "execution_status": artifact.get("execution_status", "UNKNOWN"),
        "provider_invoked": artifact.get("provider_invoked") is True,
        "provider_result": governed_return["provider_result"],
        "provider_exit_code": governed_return["provider_exit_code"],
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
        "execution_governance_hash": artifact.get("execution_governance_hash", ""),
        "execution_result_hash": artifact.get("execution_result_hash", ""),
        "governed_return_hash": governed_return_artifact.get("governed_return_hash", governed_return["governed_return_hash"]),
        "continuity_verified": governed_return["continuity_verified"],
        "fail_closed": governed_return["fail_closed"] or persistence.get("status") == "PERSISTENCE_FAILED",
        "diagnostic_evidence": governed_return["diagnostic_evidence"],
    }


__all__ = ["create_governed_return_artifact", "run_execution_handoff"]
