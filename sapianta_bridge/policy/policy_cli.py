"""Classification-only policy CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from sapianta_bridge.transport.transport_config import TransportConfig

from .policy_engine import evaluate_policy_input, fail_closed_evaluation
from .policy_models import PolicyError
from .policy_reader import evaluations_by_source, latest_policy_evaluation, policy_history


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
    parser = argparse.ArgumentParser(prog="policy_cli")
    parser.add_argument("--runtime-root", default=None)
    parser.add_argument("--quarantine-root", default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("path")
    evaluate_parser.add_argument("--timestamp", default=None)
    subparsers.add_parser("latest")
    subparsers.add_parser("history")
    source_parser = subparsers.add_parser("source")
    source_parser.add_argument("--source-id", required=True)

    args = parser.parse_args(list(argv if argv is not None else sys.argv[1:]))
    config = _config_from_args(args)

    try:
        if args.command == "evaluate":
            try:
                policy_input = json.loads(Path(args.path).read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                _print(fail_closed_evaluation(field=str(args.path), reason=f"malformed JSON: {exc.msg}"))
                return 1
            result = evaluate_policy_input(policy_input, config, timestamp=args.timestamp)
            _print(result)
        elif args.command == "latest":
            _print(latest_policy_evaluation(config) or {})
        elif args.command == "history":
            _print(policy_history(config))
        elif args.command == "source":
            _print(evaluations_by_source(args.source_id, config))
        return 0
    except PolicyError as exc:
        _print(
            {
                "valid": False,
                "errors": [exc.to_dict()],
                "recommended_admissibility": "BLOCKED",
                "allowed_to_execute_automatically": False,
                "execution_authority_granted": False,
            }
        )
        return 1
    except Exception as exc:  # pragma: no cover - defensive fail-closed guard.
        _print(
            {
                "valid": False,
                "errors": [
                    {
                        "field": "policy",
                        "reason": f"internal policy failure: {exc.__class__.__name__}",
                    }
                ],
                "recommended_admissibility": "BLOCKED",
                "allowed_to_execute_automatically": False,
                "execution_authority_granted": False,
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
