"""Deterministic Codex CLI contract model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DISCOVERY_STATUSES = ("DISCOVERED", "DISCOVERED_PARTIAL", "BLOCKED", "FAILED")


@dataclass(frozen=True)
class CodexCliContract:
    discovery_name: str
    status: str
    codex_cli_detected: bool
    version_detected: str
    help_available: bool
    run_help_available: bool
    supported_subcommands: tuple[str, ...]
    non_interactive_supported: bool
    file_input_supported: bool
    stdin_input_supported: bool
    recommended_invocation_vector: tuple[str, ...]
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_name": self.discovery_name,
            "status": self.status,
            "codex_cli_detected": self.codex_cli_detected,
            "version_detected": self.version_detected,
            "help_available": self.help_available,
            "run_help_available": self.run_help_available,
            "supported_subcommands": list(self.supported_subcommands),
            "non_interactive_supported": self.non_interactive_supported,
            "file_input_supported": self.file_input_supported,
            "stdin_input_supported": self.stdin_input_supported,
            "recommended_invocation_vector": list(self.recommended_invocation_vector),
            "blocked_reason": self.blocked_reason,
            "shell_used": False,
            "task_executed": False,
            "repo_mutated": False,
            "orchestration_introduced": False,
            "routing_introduced": False,
            "autonomous_execution_introduced": False,
            "replay_safe": True,
        }


def validate_codex_cli_contract(contract: Any) -> dict[str, Any]:
    value = contract.to_dict() if hasattr(contract, "to_dict") else contract
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "codex_contract", "reason": "must be an object"}]}
    for field in (
        "discovery_name",
        "status",
        "codex_cli_detected",
        "help_available",
        "run_help_available",
        "non_interactive_supported",
        "file_input_supported",
        "stdin_input_supported",
        "recommended_invocation_vector",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing contract field"})
    if value.get("discovery_name") != "CODEX_CLI_CONTRACT_DISCOVERY_V1":
        errors.append({"field": "discovery_name", "reason": "discovery name mismatch"})
    if value.get("status") not in DISCOVERY_STATUSES:
        errors.append({"field": "status", "reason": "unsupported discovery status"})
    if not isinstance(value.get("supported_subcommands"), list):
        errors.append({"field": "supported_subcommands", "reason": "supported subcommands must be a list"})
    if not isinstance(value.get("recommended_invocation_vector"), list):
        errors.append({"field": "recommended_invocation_vector", "reason": "recommended vector must be a list"})
    for field in ("shell_used", "task_executed", "repo_mutated", "orchestration_introduced", "routing_introduced", "autonomous_execution_introduced"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "discovery reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
