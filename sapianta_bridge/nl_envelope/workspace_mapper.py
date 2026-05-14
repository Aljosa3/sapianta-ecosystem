"""Deterministic workspace scope mapping for semantic ingress."""

from __future__ import annotations

import re
from typing import Any

from sapianta_bridge.envelopes.workspace_scope import workspace_scope


_PATH_HINTS = (
    "sapianta_bridge",
    "tests",
    ".github/governance",
    "docs",
)


def _extract_path_hints(text: str) -> list[str]:
    hints = [hint for hint in _PATH_HINTS if hint in text]
    explicit = re.findall(r"`([^`]+)`", text)
    for item in explicit:
        if item.startswith(("/", "..")):
            continue
        if item.startswith(("sapianta_bridge", "tests", ".github/governance", "docs")):
            hints.append(item)
    return sorted(set(hints))


def map_workspace_scope(request: dict[str, Any], classification: dict[str, Any], admissibility: dict[str, Any]) -> dict[str, Any]:
    if admissibility.get("admissibility") == "REJECTED":
        return {
            "workspace_scope": None,
            "workspace_mapping_valid": False,
            "reason": "workspace mapping blocked by rejected request",
            "least_privilege_preserved": True,
        }
    text = str(request.get("raw_text", "")).lower()
    roots = _extract_path_hints(text)
    if not roots:
        if classification.get("intent_type") == "GOVERNANCE_INSPECTION":
            roots = [".github/governance"]
        elif classification.get("intent_type") == "CREATIVE_GENERATION":
            roots = ["docs"]
        else:
            roots = ["sapianta_bridge"]
    return {
        "workspace_scope": workspace_scope(
            roots,
            forbidden_roots=[".git", "sapianta_system/venv"],
            generated_artifact_roots=["sapianta_bridge/runtime/processing"],
        ),
        "workspace_mapping_valid": True,
        "reason": "least-privilege workspace scope mapped from deterministic request hints",
        "least_privilege_preserved": True,
    }
