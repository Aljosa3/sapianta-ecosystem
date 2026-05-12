"""Human-governed approval queue CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from sapianta_bridge.transport.transport_config import TransportConfig

from .approval_models import ApprovalError
from .approval_queue import approve_approval, reject_approval
from .approval_reader import (
    approved_approvals,
    approvals_for_task,
    pending_approvals,
    rejected_approvals,
)


def _config_from_args(args: argparse.Namespace) -> TransportConfig:
    runtime_root = Path(args.runtime_root) if args.runtime_root else Path("sapianta_bridge/runtime")
    quarantine_root = (
        Path(args.quarantine_root)
        if args.quarantine_root
        else Path("sapianta_bridge/protocol/quarantine")
    )
    return TransportConfig(runtime_root=runtime_root, quarantine_root=quarantine_root)


def _print(value: dict[str, Any] | list[dict[str, Any]]) -> None:
    print(json.dumps(value, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="approval_cli")
    parser.add_argument("--runtime-root", default=None)
    parser.add_argument("--quarantine-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("pending")
    subparsers.add_parser("approved")
    subparsers.add_parser("rejected")
    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument("--approval-id", required=True)
    approve_parser.add_argument("--approved-by", default="human")
    approve_parser.add_argument("--reason", default="human governance approval recorded")
    approve_parser.add_argument("--timestamp", default=None)
    reject_parser = subparsers.add_parser("reject")
    reject_parser.add_argument("--approval-id", required=True)
    reject_parser.add_argument("--approved-by", default="human")
    reject_parser.add_argument("--reason", default="human governance rejection recorded")
    reject_parser.add_argument("--timestamp", default=None)
    task_parser = subparsers.add_parser("task")
    task_parser.add_argument("--task-id", required=True)

    args = parser.parse_args(list(argv if argv is not None else sys.argv[1:]))
    config = _config_from_args(args)

    try:
        if args.command == "pending":
            _print(pending_approvals(config))
        elif args.command == "approved":
            _print(approved_approvals(config))
        elif args.command == "rejected":
            _print(rejected_approvals(config))
        elif args.command == "approve":
            _print(
                approve_approval(
                    args.approval_id,
                    approved_by=args.approved_by,
                    reason=args.reason,
                    config=config,
                    timestamp=args.timestamp,
                )
            )
        elif args.command == "reject":
            _print(
                reject_approval(
                    args.approval_id,
                    approved_by=args.approved_by,
                    reason=args.reason,
                    config=config,
                    timestamp=args.timestamp,
                )
            )
        elif args.command == "task":
            _print(approvals_for_task(args.task_id, config))
        return 0
    except ApprovalError as exc:
        _print(
            {
                "valid": False,
                "errors": [exc.to_dict()],
                "recommended_state": "QUARANTINED",
            }
        )
        return 1
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard.
        _print(
            {
                "valid": False,
                "errors": [
                    {
                        "field": "approval",
                        "reason": f"internal approval failure: {exc.__class__.__name__}",
                    }
                ],
                "recommended_state": "QUARANTINED",
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
