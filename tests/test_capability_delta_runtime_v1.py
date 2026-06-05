"""Tests for AIGOL_CAPABILITY_DELTA_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.runtime.capability_delta_runtime import compute_capability_delta, run_capability_delta


def _matrix(capabilities: list[dict], scores: dict[str, int]) -> dict:
    counts = {"CERTIFIED": 0, "IMPLEMENTED": 0, "PARTIAL": 0, "NOT_STARTED": 0, "total": len(capabilities)}
    for capability in capabilities:
        counts[capability["status"]] += 1
    return {
        "artifact_id": "MATRIX",
        "capability_counts": counts,
        "layer_maturity_scores": scores,
        "capabilities": capabilities,
    }


def test_capability_delta_computes_added_removed_status_and_layer_changes() -> None:
    previous = _matrix(
        [
            {"capability": "Alpha", "layer": "L1 Governance", "status": "PARTIAL"},
            {"capability": "Beta", "layer": "L2 Cognition (OCS)", "status": "CERTIFIED"},
            {"capability": "Removed", "layer": "L7 Marketplace / Ecosystem", "status": "IMPLEMENTED"},
        ],
        {"L1 Governance": 50, "L2 Cognition (OCS)": 80, "L7 Marketplace / Ecosystem": 40},
    )
    current = _matrix(
        [
            {"capability_key": "alpha", "capability": "Alpha", "layer": "L1 Governance", "status": "CERTIFIED"},
            {"capability_key": "beta", "capability": "Beta", "layer": "L2 Cognition", "status": "PARTIAL"},
            {"capability_key": "added", "capability": "Added", "layer": "L5 Implementation Generation", "status": "IMPLEMENTED"},
        ],
        {"L1 Governance": 70, "L2 Cognition": 60, "L5 Implementation Generation": 55},
    )

    delta = compute_capability_delta(previous, current)

    assert delta["status_deltas"]["CERTIFIED"] == 0
    assert delta["status_deltas"]["IMPLEMENTED"] == 0
    assert delta["status_deltas"]["PARTIAL"] == 0
    assert delta["added_capabilities"][0]["capability"] == "Added"
    assert delta["removed_capabilities"][0]["capability"] == "Removed"
    assert any(change["capability"] == "Alpha" and change["direction"] == "IMPROVED" for change in delta["status_changes"])
    assert any(change["capability"] == "Beta" and change["direction"] == "REGRESSED" for change in delta["status_changes"])
    assert delta["layer_score_deltas"]["L1 Governance"]["delta"] == 20
    assert delta["layer_score_deltas"]["L2 Cognition"]["delta"] == -20
    assert delta["layer_score_deltas"]["L5 Implementation"]["current_score"] == 55
    assert delta["delta_hash"].startswith("sha256:")


def test_run_capability_delta_writes_report_and_json(tmp_path: Path) -> None:
    previous = _matrix(
        [{"capability": "Alpha", "layer": "L1 Governance", "status": "PARTIAL"}],
        {"L1 Governance": 50},
    )
    current = _matrix(
        [{"capability_key": "alpha", "capability": "Alpha", "layer": "L1 Governance", "status": "CERTIFIED"}],
        {"L1 Governance": 80},
    )
    previous_path = tmp_path / "AIGOL_CAPABILITY_MATRIX_V1.json"
    current_path = tmp_path / "AIGOL_CAPABILITY_MATRIX_V2.json"
    previous_path.write_text(json.dumps(previous), encoding="utf-8")
    current_path.write_text(json.dumps(current), encoding="utf-8")

    capture = run_capability_delta(
        previous_matrix_path=previous_path,
        current_matrix_path=current_path,
        output_governance_dir=tmp_path,
    )
    delta_path = tmp_path / "AIGOL_CAPABILITY_DELTA_V1.json"
    report_path = tmp_path / "AIGOL_CAPABILITY_DELTA_REPORT_V1.md"
    delta = json.loads(delta_path.read_text(encoding="utf-8"))

    assert delta_path.exists()
    assert report_path.exists()
    assert delta["artifact_id"] == "AIGOL_CAPABILITY_DELTA_V1"
    assert delta["status_deltas"]["CERTIFIED"] == 1
    assert "Top Improvements" in report_path.read_text(encoding="utf-8")
    assert capture["status_change_count"] == 1
