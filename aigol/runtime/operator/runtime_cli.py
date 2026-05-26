"""Minimal local read-only runtime operator CLI."""

from __future__ import annotations

import argparse

from aigol.runtime.models import FailClosedRuntimeError

from .runtime_query import RuntimeQuery
from .runtime_report import render_goal_report, render_retry_report, render_runtime_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only AiGOL runtime operator CLI")
    parser.add_argument("--root", default=".", help="runtime artifact root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="render runtime summary")
    summary.add_argument("runtime_id")

    goal = subparsers.add_parser("goal", help="render goal summary")
    goal.add_argument("goal_id")

    retry = subparsers.add_parser("retry", help="render retry summary")
    retry.add_argument("runtime_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    query = RuntimeQuery(args.root)
    try:
        if args.command == "summary":
            print(render_runtime_report(query.get_runtime_summary(args.runtime_id)))
        elif args.command == "goal":
            print(render_goal_report(query.get_goal_summary(args.goal_id)))
        elif args.command == "retry":
            print(render_retry_report(query.get_retry_summary(args.runtime_id)))
        else:  # pragma: no cover - argparse prevents this.
            parser.error("unknown command")
    except FailClosedRuntimeError as exc:
        parser.exit(2, f"FAIL_CLOSED: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
