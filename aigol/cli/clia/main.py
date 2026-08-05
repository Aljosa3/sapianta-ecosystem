"""Repository CLI entry for the canonical production CLIA transport."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

from .session import CliaTransportStatus, create_clia_transport_session_v1
from .transport import run_clia_interactive_session_v1


DEFAULT_CLIA_CREATED_AT = "2026-08-04T00:00:00Z"
DEFAULT_CLIA_RUNTIME_ROOT = ".runtime/clia-production"


def build_clia_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clia",
        description=(
            "Canonical thin CLI Human Interaction Channel transport.\n"
            "G69-13 evidence label: Development-only thin CLI Human Interaction Channel transport.\n"
            "Sole runtime successor: Canonical Human Entry."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--session-id", default="CLIA-PRODUCTION-SESSION")
    parser.add_argument("--human-actor", default="HUMAN_OPERATOR")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--runtime-root", default=DEFAULT_CLIA_RUNTIME_ROOT)
    parser.add_argument("--created-at", default=DEFAULT_CLIA_CREATED_AT)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> int:
    args = build_clia_parser().parse_args(argv)
    session = create_clia_transport_session_v1(
        transport_session_identity=args.session_id,
        human_actor_reference=args.human_actor,
        workspace_reference=args.workspace,
        runtime_root_reference=args.runtime_root,
        created_at=args.created_at,
        production=True,
    )
    result = run_clia_interactive_session_v1(
        session=session,
        input_reader=input_reader,
        output_writer=output_writer,
    )
    if result.status is CliaTransportStatus.TRANSPORT_FAILED_CLOSED:
        return 2
    if result.status is CliaTransportStatus.INTERRUPTED:
        return 130
    return 0
