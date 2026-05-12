"""Lineage validation for protocol artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class LineageValidation:
    valid: bool
    errors: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors)}


def _error(field: str, reason: str) -> dict[str, str]:
    return {"field": field, "reason": reason}


def validate_lineage(
    lineage: Any,
    *,
    required_fields: Iterable[str],
    nullable_fields: Iterable[str] = (),
) -> LineageValidation:
    errors: list[dict[str, str]] = []
    nullable = set(nullable_fields)

    if not isinstance(lineage, dict):
        return LineageValidation(False, (_error("lineage", "missing or malformed lineage"),))

    for field in required_fields:
        if field not in lineage:
            errors.append(_error(f"lineage.{field}", "missing required field"))
            continue

        value = lineage[field]
        if value is None and field in nullable:
            continue
        if not isinstance(value, str) or not value.strip():
            errors.append(_error(f"lineage.{field}", "lineage id must be non-empty"))

    return LineageValidation(not errors, tuple(errors))


def parent_child_lineage(parent_id: str, child_id: str) -> dict[str, str]:
    if not parent_id or not child_id:
        raise ValueError("parent_id and child_id must be non-empty")
    return {"parent_id": parent_id, "child_id": child_id}

