"""Deterministic terminal card rendering."""

from __future__ import annotations

from typing import Iterable


def render_card(title: str, lines: Iterable[str]) -> str:
    body = [str(line) for line in lines]
    boundary = "=" * 50
    return "\n".join([boundary, str(title).upper(), boundary, *body, boundary])


__all__ = ["render_card"]

