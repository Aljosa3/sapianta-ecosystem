"""Read-only observability CLI for bounded bridge transport."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from sapianta_bridge.transport.transport_config import TransportConfig

from .execution_summary import execution_summary
from .queue_inspector import inspect_queue
from .replay_reader import ReplayEvidenceError, find_by_task_id, latest_execution, replay_summary
from .runtime_status import runtime_status
from .state_transitions import transition_history


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


def _error(exc: ReplayEvidenceError) -> dict[str, Any]:
    return {
        "valid": False,
        "errors": [exc.to_dict()],
        "recommended_state": "QUARANTINED",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="observability_cli")
    parser.add_argument("--runtime-root", default=None)
    parser.add_argument("--quarantine-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("queue")
    replay_parser = subparsers.add_parser("replay")
    replay_group = replay_parser.add_mutually_exclusive_group(required=True)
    replay_group.add_argument("--latest", action="store_true")
    replay_group.add_argument("--task-id")
    subparsers.add_parser("summary")
    transitions_parser = subparsers.add_parser("transitions")
    transitions_parser.add_argument("--task-id", required=True)

    args = parser.parse_args(list(argv if argv is not None else sys.argv[1:]))
    config = _config_from_args(args)

    try:
        if args.command == "status":
            _print(runtime_status(config))
        elif args.command == "queue":
            _print(inspect_queue(config))
        elif args.command == "replay":
            if args.latest:
                latest = latest_execution(config)
                _print(replay_summary(latest) if latest else {})
            else:
                _print([replay_summary(entry) for entry in find_by_task_id(args.task_id, config)])
        elif args.command == "summary":
            _print(execution_summary(config))
        elif args.command == "transitions":
            result = transition_history(args.task_id, config)
            _print(result)
            return 1 if result["invalid_transition_detected"] else 0
        return 0
    except ReplayEvidenceError as exc:
        _print(_error(exc))
        return 1
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard.
        _print(
            {
                "valid": False,
                "errors": [
                    {
                        "field": "observability",
                        "reason": f"internal observability failure: {exc.__class__.__name__}",
                    }
                ],
                "recommended_state": "QUARANTINED",
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

