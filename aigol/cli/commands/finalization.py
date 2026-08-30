"""Human-facing adapter for one governed repository finalization invocation."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.governed_repository_finalization_runtime import (
    execute_governed_repository_finalization,
)
from aigol.runtime.transport.serialization import load_json


def finalize_repository_from_contract_file(contract_path: str | Path) -> dict:
    """Load one explicit Human contract and invoke the governed coordinator once."""

    path = Path(contract_path).resolve()
    contract = load_json(path)
    result = execute_governed_repository_finalization(contract_artifact=contract)
    result["command"] = "aigol finalize"
    result["contract_path"] = str(path)
    return result


def render_finalization_result(result: dict) -> list[str]:
    return [
        f"status: {result.get('finalization_status')}",
        f"contract_id: {result.get('contract_id')}",
        f"committed_head: {result.get('committed_head') or ''}",
        f"committed_tree: {result.get('committed_tree') or ''}",
        f"commit_subject: {result.get('commit_subject') or ''}",
        f"committed_path_set: {result.get('committed_path_set', [])}",
        f"post_commit_status: {result.get('post_commit_status')}",
        f"commit_effect_count: {result.get('commit_effect_count')}",
        f"replay_reference: {result.get('replay_reference') or ''}",
        f"fail_closed: {result.get('fail_closed')}",
        f"failure_reason: {result.get('failure_reason') or ''}",
    ]
