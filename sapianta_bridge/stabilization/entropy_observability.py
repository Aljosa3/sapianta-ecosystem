"""Passive execution entropy observability for future AGOL analysis."""

from __future__ import annotations

from collections import Counter
from typing import Any


TOKEN_HEAVY_MARKERS = {
    "repo_wide_scan": "repo-wide scan",
    "collect_only": "collect-only",
    "full_context_regeneration": "full-context regeneration",
    "oversized_patch": "oversized patch",
}


def entropy_baseline(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_names = [str(event.get("event", "")) for event in events]
    counts = Counter(event_names)
    token_heavy_patterns = [
        marker
        for marker, phrase in TOKEN_HEAVY_MARKERS.items()
        if any(phrase in str(event).lower() for event in events)
    ]
    repeated_regeneration = sum(
        count - 1 for name, count in counts.items() if count > 1 and "regeneration" in name
    )
    reasoning_repetition = sum(
        count - 1 for name, count in counts.items() if count > 1 and "failure_explanation" in name
    )
    repo_scans = sum(1 for event in events if "repo-wide" in str(event).lower())
    collect_only = sum(1 for event in events if "collect-only" in str(event).lower())
    return {
        "entropy_metrics": {
            "repo_scan_frequency": repo_scans,
            "repeated_collect_only_invocations": collect_only,
            "repeated_regeneration_cycles": repeated_regeneration,
            "reasoning_repetition_events": reasoning_repetition,
            "token_heavy_patterns": sorted(set(token_heavy_patterns)),
        },
        "observability_mode": "PASSIVE_ONLY",
        "influences_execution": False,
    }
