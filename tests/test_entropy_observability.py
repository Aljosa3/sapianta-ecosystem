from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.stabilization.entropy_observability import entropy_baseline


def test_entropy_observability_is_passive_and_deterministic() -> None:
    events = [
        {"event": "repo_scan", "detail": "repo-wide scan"},
        {"event": "collect_only", "detail": "collect-only"},
        {"event": "collect_only", "detail": "collect-only"},
        {"event": "failure_explanation", "detail": "same failure"},
        {"event": "failure_explanation", "detail": "same failure"},
    ]

    first = entropy_baseline(events)
    second = entropy_baseline(events)

    assert first == second
    assert first["observability_mode"] == "PASSIVE_ONLY"
    assert first["influences_execution"] is False
    assert first["entropy_metrics"]["repo_scan_frequency"] == 1
    assert first["entropy_metrics"]["reasoning_repetition_events"] == 1
