"""Replay pollution detection for candidate governance lineage artifacts."""

from __future__ import annotations

from typing import Any

from .artifact_classifier import (
    CANONICAL_GOVERNANCE_ARTIFACT,
    TRANSIENT_RUNTIME_ARTIFACT,
    UNKNOWN_ARTIFACT,
    classify_artifacts,
)


def detect_replay_pollution(paths: list[str]) -> dict[str, Any]:
    classifications = classify_artifacts(paths)
    polluting = [
        item
        for item in classifications
        if item["classification"] in {TRANSIENT_RUNTIME_ARTIFACT, UNKNOWN_ARTIFACT}
    ]
    canonical = [
        item for item in classifications if item["classification"] == CANONICAL_GOVERNANCE_ARTIFACT
    ]
    return {
        "replay_pollution_detected": bool(polluting),
        "polluting_artifacts": polluting,
        "canonical_artifacts": canonical,
        "requires_human_review": bool(polluting),
        "automatic_cleanup_performed": False,
    }
