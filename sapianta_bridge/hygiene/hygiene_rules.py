"""Governance worktree hygiene policy rules."""

from __future__ import annotations

from typing import Any

from .artifact_classifier import (
    CANONICAL_GOVERNANCE_ARTIFACT,
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
)


REQUIRED_GITIGNORE_PATTERNS = (
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    "*.pyo",
)

FORBIDDEN_ARTIFACT_CLASSES = (
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
)

ALLOWED_GOVERNANCE_ARTIFACT_CLASSES = (CANONICAL_GOVERNANCE_ARTIFACT,)


def hygiene_policy() -> dict[str, Any]:
    return {
        "policy_id": "GOVERNANCE_WORKTREE_HYGIENE_V1",
        "allowed_artifact_classes": list(ALLOWED_GOVERNANCE_ARTIFACT_CLASSES),
        "forbidden_artifact_classes": list(FORBIDDEN_ARTIFACT_CLASSES),
        "unknown_artifact_policy": "FAIL_CLOSED",
        "transient_artifact_policy": "BLOCK_FROM_GOVERNANCE_LINEAGE",
        "automatic_deletion_allowed": False,
        "history_rewrite_allowed": False,
        "required_gitignore_patterns": list(REQUIRED_GITIGNORE_PATTERNS),
    }


def validate_gitignore_text(text: str) -> dict[str, Any]:
    lines = {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}
    missing = [pattern for pattern in REQUIRED_GITIGNORE_PATTERNS if pattern not in lines]
    return {
        "valid": not missing,
        "missing_patterns": missing,
        "required_patterns": list(REQUIRED_GITIGNORE_PATTERNS),
    }


def class_allowed_in_governance_lineage(artifact_class: str) -> bool:
    return artifact_class in ALLOWED_GOVERNANCE_ARTIFACT_CLASSES
