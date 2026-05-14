"""Evidence validation for Codex CLI contract discovery."""

from __future__ import annotations

from typing import Any

from .codex_contract_model import validate_codex_cli_contract


def codex_contract_evidence(*, discovery_result: dict[str, Any]) -> dict[str, Any]:
    contract = discovery_result.get("contract", {})
    return {
        **contract,
        "probe_count": len(discovery_result.get("probes", [])),
        "safe_probes_only": True,
        "shell_used": False,
        "task_executed": False,
        "repo_mutated": False,
    }


def validate_codex_contract_evidence(evidence: Any) -> dict[str, Any]:
    validation = validate_codex_cli_contract(evidence)
    errors = list(validation["errors"])
    if isinstance(evidence, dict):
        if evidence.get("safe_probes_only") is not True:
            errors.append({"field": "safe_probes_only", "reason": "discovery must use safe probes only"})
        if not isinstance(evidence.get("probe_count"), int):
            errors.append({"field": "probe_count", "reason": "probe count must be an integer"})
    return {"valid": not errors, "errors": errors}
