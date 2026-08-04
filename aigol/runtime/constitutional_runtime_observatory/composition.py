"""Executable passive composition of the certified CRO layers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

from aigol.runtime.models import FailClosedRuntimeError

from .cli_transport import run_cro_cli_transport
from .core import build_constitutional_human_intent_journey_v1
from .query import build_journey


CRO_PASSIVE_COMPOSITION_VERSION = (
    "G67_05_CONSTITUTIONAL_RUNTIME_OBSERVATORY_PASSIVE_COMPOSITION_V1"
)
REQUIRED_SELECTOR_KEYS = (
    "session_id",
    "commitment_identity",
    "human_actor",
)
_WILDCARD_MARKERS = frozenset("*?[]")


def _required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"CRO composition {label} is required")
    return value


def _explicit_absolute_path(value: Any, label: str) -> str:
    text = str(value) if isinstance(value, Path) else _required_text(value, label)
    if any(marker in text for marker in _WILDCARD_MARKERS):
        raise FailClosedRuntimeError(
            f"CRO composition {label} must not contain wildcard syntax"
        )
    if not Path(text).is_absolute():
        raise FailClosedRuntimeError(
            f"CRO composition {label} must be an explicit absolute path"
        )
    return text


def _validated_roots(
    evidence_roots: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, str], ...]:
    if isinstance(evidence_roots, (str, bytes)) or not evidence_roots:
        raise FailClosedRuntimeError(
            "CRO composition requires explicit evidence-root descriptors"
        )
    validated = []
    adapter_ids = set()
    for descriptor in evidence_roots:
        if not isinstance(descriptor, Mapping) or set(descriptor) != {
            "adapter_id",
            "path",
        }:
            raise FailClosedRuntimeError(
                "CRO evidence roots require only adapter_id and path"
            )
        adapter_id = _required_text(descriptor["adapter_id"], "adapter_id")
        if adapter_id in adapter_ids:
            raise FailClosedRuntimeError(
                "CRO composition evidence adapter identities must be unique"
            )
        adapter_ids.add(adapter_id)
        validated.append(
            {
                "adapter_id": adapter_id,
                "path": _explicit_absolute_path(
                    descriptor["path"],
                    f"evidence root {adapter_id}",
                ),
            }
        )
    return tuple(validated)


def _validated_selector(selector: Mapping[str, Any]) -> dict[str, str]:
    if not isinstance(selector, Mapping) or set(selector) != set(
        REQUIRED_SELECTOR_KEYS
    ):
        raise FailClosedRuntimeError(
            "CRO composition requires exact session, Commitment, and Human selectors"
        )
    result = {}
    for key in REQUIRED_SELECTOR_KEYS:
        value = _required_text(selector[key], f"selector {key}")
        if any(marker in value for marker in _WILDCARD_MARKERS):
            raise FailClosedRuntimeError(
                f"CRO composition selector {key} must not contain wildcard syntax"
            )
        result[key] = value
    return result


def compose_passive_cro_observation(
    *,
    evidence_scope_root: str | Path,
    evidence_roots: Sequence[Mapping[str, Any]],
    selector: Mapping[str, Any],
    command: str,
    output: TextIO | None = None,
) -> int:
    """Compose G67-02, G67-03, and G67-04 without adding CRO logic."""

    scope = _explicit_absolute_path(evidence_scope_root, "evidence scope root")
    roots = _validated_roots(evidence_roots)
    exact_selector = _validated_selector(selector)
    exact_command = _required_text(command, "command")

    journey_projection = build_constitutional_human_intent_journey_v1(
        evidence_scope_root=scope,
        evidence_roots=roots,
        selector=exact_selector,
    )
    journey = build_journey(journey_projection=journey_projection)
    return run_cro_cli_transport(
        journey=journey,
        argv=[exact_command],
        output=output,
    )


def _assignment(value: str, label: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"{label} must use NAME=VALUE syntax")
    name, content = value.split("=", 1)
    if not name or not content:
        raise argparse.ArgumentTypeError(f"{label} must use NAME=VALUE syntax")
    return name, content


def build_cro_composition_parser() -> argparse.ArgumentParser:
    """Return the explicit passive-composition terminal grammar."""

    parser = argparse.ArgumentParser(
        prog="cro",
        description="Passive Constitutional Runtime Observatory composition",
    )
    parser.add_argument(
        "--evidence-scope-root",
        required=True,
        help="explicit absolute boundary containing every evidence root",
    )
    parser.add_argument(
        "--evidence-root",
        action="append",
        required=True,
        metavar="ADAPTER_ID=ABSOLUTE_PATH",
        help="explicit versioned G67-02 evidence adapter root",
    )
    parser.add_argument(
        "--selector",
        action="append",
        required=True,
        metavar="NAME=VALUE",
        help="exact session_id, commitment_identity, or human_actor selector",
    )
    parser.add_argument("command", help="one G67-04 CLI transport command")
    return parser


def main(argv: Sequence[str] | None = None, *, output: TextIO | None = None) -> int:
    """Run one bounded passive CRO observation from explicit terminal input."""

    parser = build_cro_composition_parser()
    args = parser.parse_args(argv)
    try:
        roots = [
            {"adapter_id": name, "path": value}
            for name, value in (
                _assignment(item, "evidence root") for item in args.evidence_root
            )
        ]
        selector_items = [
            _assignment(item, "selector") for item in args.selector
        ]
        selector = dict(selector_items)
        if len(selector) != len(selector_items):
            raise FailClosedRuntimeError(
                "CRO composition selector identities must be unique"
            )
        return compose_passive_cro_observation(
            evidence_scope_root=args.evidence_scope_root,
            evidence_roots=roots,
            selector=selector,
            command=args.command,
            output=output,
        )
    except (FailClosedRuntimeError, argparse.ArgumentTypeError) as exc:
        parser.exit(2, f"FAIL_CLOSED: {exc}\n")


__all__ = [
    "CRO_PASSIVE_COMPOSITION_VERSION",
    "REQUIRED_SELECTOR_KEYS",
    "compose_passive_cro_observation",
    "build_cro_composition_parser",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
