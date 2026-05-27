"""Operational readonly runtime inspection over the existing governed path."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.cli.commands.return_continuity import (
    generate_governed_return_artifact,
    persist_governed_return_artifact,
    read_ledger_entries,
    verify_governed_return,
)
from aigol.runtime.governed_return_interpretation import (
    ACCEPTED,
    interpret_governed_execution_return,
)
from aigol.runtime.minimal_governed_execution_path import (
    ALLOWED_OPERATION,
    ALLOWED_PROVIDER,
    EXECUTED,
    execute_minimal_governed_path,
)
from aigol.runtime.production_isolation_foundation import (
    ISOLATED,
    validate_production_isolation,
)


DEFAULT_OPERATION_ID = "RUNTIME-INSPECTION-001"
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
OPERATION_TYPE = "inspect-runtime"


def _readonly_proposal(*, operation_id: str, created_at: str) -> dict[str, Any]:
    return {
        "proposal_id": f"{operation_id}:PROPOSAL",
        "natural_language_input": "Inspect readonly runtime metadata.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": [ALLOWED_PROVIDER],
        "proposed_contract_reference": f"contract:{operation_id}:CONTRACT",
        "created_at": created_at,
    }


def _operation(*, operation_id: str, created_at: str, status: str) -> dict[str, Any]:
    return {
        "operation_id": operation_id,
        "operation_type": OPERATION_TYPE,
        "timestamp": created_at,
        "provider": ALLOWED_PROVIDER,
        "readonly": True,
        "status": status,
        "replay_reference": operation_id,
    }


def run_runtime_inspection(
    *,
    operation_id: str = DEFAULT_OPERATION_ID,
    created_at: str = DEFAULT_TIMESTAMP,
    runtime_root: str | Path | None = None,
    proposal_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute and persist one readonly runtime inspection through existing gates."""

    operation = _operation(operation_id=operation_id, created_at=created_at, status="pending")
    proposal = deepcopy(proposal_input) if proposal_input is not None else _readonly_proposal(
        operation_id=operation_id,
        created_at=created_at,
    )
    execution = execute_minimal_governed_path(
        execution_id=f"{operation_id}:EXECUTION",
        llm_proposal_input=proposal,
        created_at=created_at,
    )
    execution_result = execution["execution_result"]
    isolation = validate_production_isolation(
        isolation_id=f"{operation_id}:ISOLATION",
        execution_result=execution_result,
        quota_policy={
            "max_provider_invocations": 1,
            "allowed_provider": ALLOWED_PROVIDER,
            "allowed_operation": ALLOWED_OPERATION,
        },
        isolation_metadata={
            "isolation_mode": "LOCAL_READONLY_SINGLE_PROVIDER",
            "provider_state_mutation_allowed": False,
            "runtime_state_mutation_allowed": False,
            "network_mutation_allowed": False,
            "replay_durability": "APPEND_ONLY_HASHED_EVIDENCE",
            "governance_authority_separated": True,
        },
        created_at=created_at,
    )
    governed_return = interpret_governed_execution_return(
        return_id=f"{operation_id}:RETURN",
        execution_result=execution_result,
        provider_evidence=execution["provider_evidence"],
        session_lineage=execution["session_lineage"],
        isolation_evidence=isolation,
        created_at=created_at,
    )
    accepted = (
        execution_result.execution_status == EXECUTED
        and isolation.isolation_status == ISOLATED
        and governed_return.return_status == ACCEPTED
    )
    operation = _operation(
        operation_id=operation_id,
        created_at=created_at,
        status="success" if accepted else "blocked",
    )
    provider_evidence = execution["provider_evidence"] if isinstance(execution["provider_evidence"], dict) else {}
    provider_result = {
        "status": provider_evidence.get("status", "NOT_INVOKED"),
        "stdout": governed_return.normalized_return_summary,
        "stderr": "" if accepted else governed_return.normalized_return_summary,
        "returncode": 0 if accepted else None,
    }
    cli_return = {
        "governed_return_hash": governed_return.evidence_hash,
        "provider_result": provider_result,
        "continuity_verified": accepted,
        "fail_closed": not accepted,
        "diagnostic_evidence": {
            "runtime_operation": operation,
            "provider_invoked": bool(provider_evidence),
            "provider_operation": ALLOWED_OPERATION,
            "execution_evidence_hash": execution_result.evidence_hash,
            "session_lineage_hash": execution_result.session_lineage_hash,
            "isolation_evidence_hash": isolation.evidence_hash,
            "governed_return_evidence_hash": governed_return.evidence_hash,
            "readonly_enforced": True,
        },
    }
    execution_artifact = {
        "execution_status": "EXECUTION_COMPLETED" if accepted else "EXECUTION_BLOCKED",
        "replay_identity": operation["replay_reference"],
        "provider_invoked": bool(provider_evidence),
        "execution_result_hash": execution_result.evidence_hash,
        "execution_governance_hash": execution_result.session_lineage_hash,
        "source_dispatch_authorization_hash": getattr(execution.get("authorization"), "evidence_hash", "UNKNOWN"),
    }
    artifact = generate_governed_return_artifact(
        execution_artifact=execution_artifact,
        cli_governed_return=cli_return,
        created_at=created_at,
    )
    persistence = persist_governed_return_artifact(
        artifact=artifact,
        provider_result=provider_result,
        runtime_root=runtime_root,
    )
    replay_entries = 0
    try:
        verification = (
            verify_governed_return(replay_identity=operation["replay_reference"], runtime_root=runtime_root)
            if persistence.get("status") == "PERSISTED"
            else {"status": "VERIFY_FAILED", "fail_closed": True}
        )
        persisted = persistence.get("status") == "PERSISTED" and verification.get("status") == "VERIFY_PASSED"
        if persisted:
            replay_entries = len(read_ledger_entries(runtime_root=runtime_root, limit=100000))
    except (OSError, TypeError, ValueError, KeyError):
        verification = {"status": "VERIFY_FAILED", "fail_closed": True}
        persisted = False
    final_status = operation["status"] if persisted else "failed_closed"
    final_operation = {**operation, "status": final_status}
    return {
        "operation": final_operation,
        "execution": execution,
        "isolation": isolation,
        "governed_return": governed_return,
        "governed_return_artifact": artifact,
        "persistence": persistence,
        "verification": verification,
        "runtime_summary": {
            "replay_entries": replay_entries,
            "latest_operation_id": operation_id if persisted else "NONE",
            "governance": "active" if accepted and persisted else "blocked",
            "replay_available": persisted,
        },
        "fail_closed": final_status != "success",
    }


def render_runtime_inspection(result: dict[str, Any]) -> str:
    operation = result["operation"]
    summary = result["runtime_summary"]
    return "\n".join(
        [
            "[OPERATION]",
            f"status: {operation['status']}",
            f"operation: {operation['operation_type']}",
            f"operation_id: {operation['operation_id']}",
            f"provider: {operation['provider']}",
            f"readonly: {str(operation['readonly']).lower()}",
            "",
            "[RUNTIME]",
            f"replay_entries: {summary['replay_entries']}",
            f"latest_operation_id: {summary['latest_operation_id']}",
            f"governance: {summary['governance']}",
            f"replay_available: {str(summary['replay_available']).lower()}",
            "",
            "[REPLAY]",
            f"replay_reference: {operation['replay_reference']}",
            f"persistence: {result['persistence']['status'].lower()}",
            f"verification: {result['verification']['status'].lower()}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Readonly governed operational execution")
    parser.add_argument("--runtime-root", default="", help="governed return persistence root")
    subcommands = parser.add_subparsers(dest="command", required=True)
    inspect = subcommands.add_parser(OPERATION_TYPE, help="inspect runtime through the readonly governed path")
    inspect.add_argument("--operation-id", default=DEFAULT_OPERATION_ID)
    inspect.add_argument("--timestamp", default=DEFAULT_TIMESTAMP)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_runtime_inspection(
        operation_id=args.operation_id,
        created_at=args.timestamp,
        runtime_root=args.runtime_root or None,
    )
    print(render_runtime_inspection(result))
    return 0 if result["fail_closed"] is False else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_OPERATION_ID",
    "DEFAULT_TIMESTAMP",
    "OPERATION_TYPE",
    "main",
    "render_runtime_inspection",
    "run_runtime_inspection",
]
