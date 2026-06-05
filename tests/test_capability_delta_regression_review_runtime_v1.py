"""Tests for AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.runtime.capability_delta_regression_review_runtime import (
    compute_corrected_delta,
    run_delta_regression_review,
)


def _previous() -> dict:
    return {
        "artifact_id": "V1",
        "capabilities": [
            {"capability": "Broad Runtime", "layer": "L1 Governance", "status": "CERTIFIED"},
            {"capability": "Stable Capability", "layer": "L2 Cognition", "status": "PARTIAL"},
            {"capability": "Removed Manual", "layer": "L4 Execution", "status": "CERTIFIED"},
            {"capability": "Duplicate", "layer": "L1 Governance", "status": "PARTIAL"},
        ],
    }


def _current() -> dict:
    return {
        "artifact_id": "V2",
        "capabilities": [
            {
                "capability_key": "broad_runtime",
                "capability": "Broad Runtime",
                "layer": "L1 Governance",
                "status": "CERTIFIED",
            },
            {
                "capability_key": "broad_runtime_validator",
                "capability": "Broad Runtime Validator",
                "layer": "L1 Governance",
                "status": "PARTIAL",
            },
            {
                "capability_key": "stable_capability",
                "capability": "Stable Capability",
                "layer": "L2 Cognition",
                "status": "CERTIFIED",
            },
            {
                "capability_key": "capability_audit_runtime",
                "capability": "Capability Audit Runtime",
                "layer": "L1 Governance",
                "status": "CERTIFIED",
                "implementation": ["aigol/runtime/capability_audit_runtime.py"],
                "certification": ["governance/AIGOL_CAPABILITY_AUDIT_RUNTIME_V1_CERTIFICATION.json"],
            },
            {
                "capability_key": "duplicate_runtime",
                "capability": "Duplicate Runtime",
                "layer": "L1 Governance",
                "status": "PARTIAL",
            },
            {
                "capability_key": "duplicate_certification",
                "capability": "Duplicate Certification",
                "layer": "L1 Governance",
                "status": "PARTIAL",
            },
        ],
    }


def _delta() -> dict:
    return {
        "artifact_id": "DELTA",
        "status_deltas": {"CERTIFIED": 2, "IMPLEMENTED": 0, "PARTIAL": 2, "NOT_STARTED": 0},
        "added_capabilities": [
            {"capability_key": "broad_runtime_validator", "capability": "Broad Runtime Validator", "layer": "L1 Governance", "status": "PARTIAL"},
            {"capability_key": "capability_audit_runtime", "capability": "Capability Audit Runtime", "layer": "L1 Governance", "status": "CERTIFIED"},
            {"capability_key": "duplicate_runtime", "capability": "Duplicate Runtime", "layer": "L1 Governance", "status": "PARTIAL"},
            {"capability_key": "duplicate_certification", "capability": "Duplicate Certification", "layer": "L1 Governance", "status": "PARTIAL"},
        ],
        "removed_capabilities": [
            {"capability": "Removed Manual", "layer": "L4 Execution", "status": "CERTIFIED"}
        ],
        "status_changes": [
            {
                "capability_key": "stable_capability",
                "capability": "Stable Capability",
                "layer": "L2 Cognition",
                "previous_status": "PARTIAL",
                "current_status": "CERTIFIED",
            }
        ],
    }


def test_regression_review_classifies_each_delta_and_adjusts_counts() -> None:
    corrected = compute_corrected_delta(_previous(), _current(), _delta())
    classifications = {item["capability_key"]: item["classification"] for item in corrected["classified_deltas"]}

    assert classifications["broad_runtime_validator"] == "PARSER_CHANGE"
    assert classifications["capability_audit_runtime"] == "REAL_CHANGE"
    assert classifications["duplicate_runtime"] == "DUPLICATE_DETECTION"
    assert classifications["stable_capability"] == "CLASSIFICATION_CHANGE"
    assert corrected["classification_counts"]["REAL_CHANGE"] == 1
    assert corrected["classification_counts"]["CLASSIFICATION_CHANGE"] == 2
    assert corrected["classification_counts"]["PARSER_CHANGE"] == 1
    assert corrected["classification_counts"]["DUPLICATE_DETECTION"] == 2
    assert corrected["adjusted_delta"]["status_deltas"]["CERTIFIED"] == 1
    assert corrected["adjusted_delta"]["total_capability_delta"] == 1
    assert corrected["drift_findings"]["capability_inflation_detected"] is True
    assert corrected["corrected_delta_hash"].startswith("sha256:")


def test_run_delta_regression_review_writes_artifacts(tmp_path: Path) -> None:
    previous_path = tmp_path / "AIGOL_CAPABILITY_MATRIX_V1.json"
    current_path = tmp_path / "AIGOL_CAPABILITY_MATRIX_V2.json"
    delta_path = tmp_path / "AIGOL_CAPABILITY_DELTA_V1.json"
    previous_path.write_text(json.dumps(_previous()), encoding="utf-8")
    current_path.write_text(json.dumps(_current()), encoding="utf-8")
    delta_path.write_text(json.dumps(_delta()), encoding="utf-8")

    capture = run_delta_regression_review(
        previous_matrix_path=previous_path,
        current_matrix_path=current_path,
        delta_path=delta_path,
        output_governance_dir=tmp_path,
    )

    corrected_path = tmp_path / "AIGOL_CAPABILITY_DELTA_CORRECTED_V1.json"
    review_path = tmp_path / "AIGOL_CAPABILITY_DELTA_REGRESSION_REVIEW_V1.md"
    corrected = json.loads(corrected_path.read_text(encoding="utf-8"))
    assert corrected_path.exists()
    assert review_path.exists()
    assert corrected["artifact_id"] == "AIGOL_CAPABILITY_DELTA_CORRECTED_V1"
    assert "Adjusted Delta" in review_path.read_text(encoding="utf-8")
    assert capture["adjusted_status_deltas"]["CERTIFIED"] == 1
