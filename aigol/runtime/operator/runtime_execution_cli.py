"""Operational readonly runtime inspection over the existing governed path."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.cli.commands.return_continuity import (
    ARTIFACT_TYPE,
    DEFAULT_RUNTIME_ROOT,
    SCHEMA_VERSION,
    generate_governed_return_artifact,
    inspect_governed_return,
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
INSPECT_REPLAY_COMMAND = "inspect-replay"
VERIFY_REPLAY_COMMAND = "verify-replay"


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


def _governed_return_path(*, replay_reference: str, runtime_root: str | Path | None) -> Path:
    root = Path(runtime_root) if runtime_root is not None else DEFAULT_RUNTIME_ROOT
    return root / "evidence" / replay_reference / "governed_return.json"


def _load_operational_replay_artifact(*, replay_reference: str, runtime_root: str | Path | None) -> dict[str, Any]:
    artifact_path = _governed_return_path(replay_reference=replay_reference, runtime_root=runtime_root)
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(artifact, dict):
        raise ValueError("governed return artifact must be an object")
    if artifact.get("artifact_type") != ARTIFACT_TYPE or artifact.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("governed return schema mismatch")
    if artifact.get("replay_identity") != replay_reference:
        raise ValueError("governed return replay identity mismatch")
    return artifact


def run_replay_verification(*, replay_reference: str, runtime_root: str | Path | None = None) -> dict[str, Any]:
    """Verify one persisted replay through the existing governed-return verifier."""

    try:
        verification = verify_governed_return(replay_identity=replay_reference, runtime_root=runtime_root)
        if verification.get("status") != "VERIFY_PASSED":
            raise ValueError("existing replay verification failed")
        artifact = _load_operational_replay_artifact(replay_reference=replay_reference, runtime_root=runtime_root)
        return {
            "replay_reference": replay_reference,
            "schema_version": artifact["schema_version"],
            "verification": "verify_passed",
            "continuity": "valid",
            "evidence": "present",
            "governed_return_present": True,
            "fail_closed": False,
        }
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return {
            "replay_reference": replay_reference,
            "schema_version": "unknown",
            "verification": "verify_failed",
            "continuity": "invalid",
            "evidence": "missing_or_invalid",
            "governed_return_present": False,
            "fail_closed": True,
        }


def run_replay_inspection(*, replay_reference: str, runtime_root: str | Path | None = None) -> dict[str, Any]:
    """Read one persisted runtime inspection replay without executing or writing."""

    verification = run_replay_verification(replay_reference=replay_reference, runtime_root=runtime_root)
    try:
        inspected = inspect_governed_return(replay_identity=replay_reference, runtime_root=runtime_root)
        if inspected.get("status") != "FOUND" or verification["fail_closed"]:
            raise ValueError("replay inspection cannot accept unverified evidence")
        artifact = _load_operational_replay_artifact(replay_reference=replay_reference, runtime_root=runtime_root)
        operation = artifact.get("diagnostic_evidence", {}).get("runtime_operation")
        if not isinstance(operation, dict):
            raise ValueError("runtime operation evidence is absent")
        if operation.get("replay_reference") != replay_reference:
            raise ValueError("runtime operation replay reference mismatch")
        if operation.get("operation_type") != OPERATION_TYPE or operation.get("provider") != ALLOWED_PROVIDER:
            raise ValueError("runtime operation boundary mismatch")
        if operation.get("readonly") is not True:
            raise ValueError("runtime operation is not readonly")
        return {
            "replay_reference": replay_reference,
            "schema_version": artifact["schema_version"],
            "status": "persisted",
            "operation": operation,
            "verification_available": True,
            "governed_return_present": True,
            "evidence_present": True,
            "fail_closed": False,
        }
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError):
        return {
            "replay_reference": replay_reference,
            "schema_version": "unknown",
            "status": "failed_closed",
            "operation": {},
            "verification_available": True,
            "governed_return_present": False,
            "evidence_present": False,
            "fail_closed": True,
        }


def render_replay_inspection(result: dict[str, Any]) -> str:
    operation = result["operation"]
    return "\n".join(
        [
            "[REPLAY]",
            f"replay_reference: {result['replay_reference']}",
            f"schema_version: {result['schema_version']}",
            f"status: {result['status']}",
            "",
            "[OPERATION]",
            f"operation: {operation.get('operation_type', 'unknown')}",
            f"provider: {operation.get('provider', 'unknown')}",
            f"readonly: {str(operation.get('readonly', False)).lower()}",
            "",
            "[VERIFICATION]",
            f"verification_available: {str(result['verification_available']).lower()}",
            f"governed_return_present: {str(result['governed_return_present']).lower()}",
            f"evidence_present: {str(result['evidence_present']).lower()}",
        ]
    )


def render_replay_verification(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "[VERIFY]",
            f"replay_reference: {result['replay_reference']}",
            f"verification: {result['verification']}",
            f"continuity: {result['continuity']}",
            f"evidence: {result['evidence']}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Readonly governed operational execution")
    parser.add_argument("--runtime-root", default="", help="governed return persistence root")
    subcommands = parser.add_subparsers(dest="command", required=True)
    inspect = subcommands.add_parser(OPERATION_TYPE, help="inspect runtime through the readonly governed path")
    inspect.add_argument("--operation-id", default=DEFAULT_OPERATION_ID)
    inspect.add_argument("--timestamp", default=DEFAULT_TIMESTAMP)
    inspect_replay = subcommands.add_parser(INSPECT_REPLAY_COMMAND, help="inspect existing runtime replay evidence")
    inspect_replay.add_argument("replay_reference")
    verify_replay = subcommands.add_parser(VERIFY_REPLAY_COMMAND, help="verify existing runtime replay evidence")
    verify_replay.add_argument("replay_reference")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == OPERATION_TYPE:
        result = run_runtime_inspection(
            operation_id=args.operation_id,
            created_at=args.timestamp,
            runtime_root=args.runtime_root or None,
        )
        print(render_runtime_inspection(result))
    elif args.command == INSPECT_REPLAY_COMMAND:
        result = run_replay_inspection(
            replay_reference=args.replay_reference,
            runtime_root=args.runtime_root or None,
        )
        print(render_replay_inspection(result))
    else:
        result = run_replay_verification(
            replay_reference=args.replay_reference,
            runtime_root=args.runtime_root or None,
        )
        print(render_replay_verification(result))
    return 0 if result["fail_closed"] is False else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_OPERATION_ID",
    "DEFAULT_TIMESTAMP",
    "INSPECT_REPLAY_COMMAND",
    "OPERATION_TYPE",
    "VERIFY_REPLAY_COMMAND",
    "main",
    "render_replay_inspection",
    "render_replay_verification",
    "render_runtime_inspection",
    "run_replay_inspection",
    "run_replay_verification",
    "run_runtime_inspection",
]
