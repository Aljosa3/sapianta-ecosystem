"""Deterministic artifact classification for governance lineage hygiene."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


CANONICAL_GOVERNANCE_ARTIFACT = "CANONICAL_GOVERNANCE_ARTIFACT"
TRANSIENT_RUNTIME_ARTIFACT = "TRANSIENT_RUNTIME_ARTIFACT"
UNKNOWN_ARTIFACT = "UNKNOWN_ARTIFACT"

ARTIFACT_CLASSES = (
    CANONICAL_GOVERNANCE_ARTIFACT,
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
)

TRANSIENT_SUFFIXES = (".pyc", ".pyo", ".tmp", ".temp", ".log")
TRANSIENT_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
}
TRANSIENT_PREFIXES = (
    "runtime/tmp/",
    "runtime/logs/",
    "runtime/development/generated/",
    "runtime/development/quarantine/",
    "sapianta_bridge/runtime/logs/",
    "sapianta_bridge/runtime/processing/",
    "sapianta_bridge/runtime/failed/",
)

CANONICAL_GOVERNANCE_PREFIXES = (
    ".github/governance/adr/",
    ".github/governance/evidence/",
    ".github/governance/finalize/",
    ".github/governance/freeze/",
    ".github/governance/manifests/",
    "sapianta_bridge/architecture/evidence/",
    "sapianta_bridge/hygiene/evidence/",
    "sapianta_bridge/protocol/finalize/",
    "sapianta_bridge/transport/finalize/",
    "sapianta_bridge/approval/finalize/",
    "sapianta_bridge/policy/finalize/",
    "sapianta_bridge/stabilization/evidence/",
)

CANONICAL_GOVERNANCE_SUFFIXES = (".md", ".json", ".txt")


def normalize_path(path: str) -> str:
    normalized = PurePosixPath(path.replace("\\", "/")).as_posix()
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def classify_artifact(path: str) -> dict[str, Any]:
    normalized = normalize_path(path)
    parts = set(PurePosixPath(normalized).parts)
    if (
        any(part in TRANSIENT_PARTS for part in parts)
        or normalized.endswith(TRANSIENT_SUFFIXES)
        or any(normalized.startswith(prefix) for prefix in TRANSIENT_PREFIXES)
    ):
        return {
            "path": normalized,
            "classification": TRANSIENT_RUNTIME_ARTIFACT,
            "reason": "transient runtime/cache artifact",
            "allowed_in_governance_lineage": False,
        }
    if normalized.endswith(CANONICAL_GOVERNANCE_SUFFIXES) and any(
        normalized.startswith(prefix) for prefix in CANONICAL_GOVERNANCE_PREFIXES
    ):
        return {
            "path": normalized,
            "classification": CANONICAL_GOVERNANCE_ARTIFACT,
            "reason": "canonical governance evidence or manifest artifact",
            "allowed_in_governance_lineage": True,
        }
    return {
        "path": normalized,
        "classification": UNKNOWN_ARTIFACT,
        "reason": "artifact requires explicit governance classification",
        "allowed_in_governance_lineage": False,
    }


def classify_artifacts(paths: list[str]) -> list[dict[str, Any]]:
    return [classify_artifact(path) for path in sorted(paths)]
