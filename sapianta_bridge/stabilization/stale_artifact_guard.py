"""Non-destructive stale generated artifact detection."""

from __future__ import annotations

from pathlib import Path
from typing import Any


GENERATED_ROOT_MARKERS = (
    "runtime/development/generated",
    "runtime/development/quarantine",
    "sapianta_system/runtime/development/generated",
    "sapianta_system/runtime/development/quarantine",
    "sapianta_system/sapianta_product/generated",
)


def inspect_stale_artifacts(root: Path) -> dict[str, Any]:
    artifacts: list[str] = []
    safe_to_remove: list[str] = []
    for marker in GENERATED_ROOT_MARKERS:
        directory = root / marker
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root))
            if "__pycache__" in relative or path.name.startswith("test_"):
                artifacts.append(relative)
                if "__pycache__" in relative:
                    safe_to_remove.append(relative)
    return {
        "stale_artifacts_detected": bool(artifacts),
        "artifacts": artifacts,
        "safe_to_remove": safe_to_remove,
        "requires_human_approval": True,
    }
