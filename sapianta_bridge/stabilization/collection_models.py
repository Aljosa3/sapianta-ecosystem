"""Models for deterministic pytest collection audit evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BLOCKER_CLASSES = {
    "OPTIONAL_DEPENDENCY",
    "STALE_GENERATED_ARTIFACT",
    "NESTED_PROJECT_SURFACE",
    "IMPORT_TOPOLOGY",
    "REAL_TEST_FAILURE",
    "UNKNOWN",
}


@dataclass(frozen=True)
class CollectionBlocker:
    path: str
    error_type: str
    classification: str
    recommended_action: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "error_type": self.error_type,
            "classification": self.classification,
            "recommended_action": self.recommended_action,
        }


def audit_report(collection_status: str, blockers: list[CollectionBlocker]) -> dict[str, Any]:
    ordered = sorted(blockers, key=lambda item: (item.classification, item.path, item.error_type))
    return {
        "collection_status": collection_status,
        "total_blockers": len(ordered),
        "blockers": [blocker.to_dict() for blocker in ordered],
    }
