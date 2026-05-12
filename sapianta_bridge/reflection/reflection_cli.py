"""Advisory-only reflection CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from sapianta_bridge.transport.transport_config import TransportConfig

from .reflection_engine import generate_reflection
from .reflection_models import ReflectionError
from .reflection_reader import latest_reflection, reflection_summary, reflections_for_task


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


def _error(exc: ReflectionError) -> dict[str, Any]:
    return {
        "valid": False,
        "errors": [exc.to_dict()],
        "recommended_state": "QUARANTINED",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reflection_cli")
    parser.add_argument("--runtime-root", default=None)
    parser.add_argument("--quarantine-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("latest")
    subparsers.add_parser("summary")
    task_parser = subparsers.add_parser("task")
    task_parser.add_argument("--task-id", required=True)
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--task-id", required=True)
    generate_parser.add_argument("--timestamp", default=None)

    args = parser.parse_args(list(argv if argv is not None else sys.argv[1:]))
    config = _config_from_args(args)

    try:
        if args.command == "latest":
            _print(latest_reflection(config) or {})
        elif args.command == "summary":
            _print(reflection_summary(config))
        elif args.command == "task":
            _print(reflections_for_task(args.task_id, config))
        elif args.command == "generate":
            result = generate_reflection(args.task_id, config, timestamp=args.timestamp)
            _print(result)
        return 0
    except ReflectionError as exc:
        _print(_error(exc))
        return 1
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard.
        _print(
            {
                "valid": False,
                "errors": [
                    {
                        "field": "reflection",
                        "reason": f"internal reflection failure: {exc.__class__.__name__}",
                    }
                ],
                "recommended_state": "QUARANTINED",
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
