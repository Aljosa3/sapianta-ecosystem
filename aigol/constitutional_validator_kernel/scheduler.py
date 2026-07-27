"""Deterministic dependency scheduling for ECC V1 requirements."""

from __future__ import annotations

import heapq
from typing import Any

from .errors import ConstitutionalValidationInputError


def schedule_requirements(requirements: list[dict[str, Any]]) -> tuple[str, ...]:
    """Return a stable topological order using requirement identifiers."""

    requirement_ids = [requirement["requirement_id"] for requirement in requirements]
    if len(requirement_ids) != len(set(requirement_ids)):
        raise ConstitutionalValidationInputError(
            "DUPLICATE_REQUIREMENT_ID",
            "contract contains duplicate requirement identifiers",
        )
    known = set(requirement_ids)
    dependencies: dict[str, set[str]] = {}
    dependents: dict[str, set[str]] = {requirement_id: set() for requirement_id in requirement_ids}
    for requirement in requirements:
        requirement_id = requirement["requirement_id"]
        declared = requirement["dependencies"]
        dependency_set = set(declared)
        if len(dependency_set) != len(declared):
            raise ConstitutionalValidationInputError(
                "DUPLICATE_DEPENDENCY",
                f"{requirement_id} contains duplicate dependencies",
            )
        if requirement_id in dependency_set:
            raise ConstitutionalValidationInputError(
                "SELF_DEPENDENCY",
                f"{requirement_id} depends on itself",
            )
        unknown = dependency_set - known
        if unknown:
            raise ConstitutionalValidationInputError(
                "UNKNOWN_DEPENDENCY",
                f"{requirement_id} contains an unknown dependency",
            )
        dependencies[requirement_id] = dependency_set
        for dependency in dependency_set:
            dependents[dependency].add(requirement_id)

    ready = [requirement_id for requirement_id in requirement_ids if not dependencies[requirement_id]]
    heapq.heapify(ready)
    scheduled: list[str] = []
    while ready:
        requirement_id = heapq.heappop(ready)
        scheduled.append(requirement_id)
        for dependent in sorted(dependents[requirement_id]):
            dependencies[dependent].remove(requirement_id)
            if not dependencies[dependent]:
                heapq.heappush(ready, dependent)
    if len(scheduled) != len(requirement_ids):
        raise ConstitutionalValidationInputError(
            "DEPENDENCY_CYCLE",
            "contract requirement dependency graph contains a cycle",
        )
    return tuple(scheduled)


__all__ = ["schedule_requirements"]
