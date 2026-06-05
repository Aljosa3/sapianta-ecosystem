"""Tests for AIGOL_CAPABILITY_AUDIT_NORMALIZATION_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.runtime.capability_normalization_runtime import (
    normalize_capability_identity,
    normalize_capability_matrix,
    run_capability_normalization,
)


RULES = {
    "artifact_id": "TEST_RULES",
    "capability_id_prefix": "CAPABILITY",
    "normalization_rules": {"strip_aigol_prefix": True},
    "version_patterns": [r"_v[0-9]+$"],
    "terminal_suffixes": ["_runtime", "_certification", "_review"],
    "aliases": {
        "old_name": "canonical_name",
        "new_name": "canonical_name",
        "sample_capability": "sample",
    },
}


def _matrix() -> dict:
    return {
        "artifact_id": "SOURCE",
        "capabilities": [
            {
                "capability": "Old Name",
                "capability_key": "old_name",
                "layer": "L1 Governance",
                "status": "PARTIAL",
                "implementation": ["aigol/runtime/old_name.py"],
                "tests": [],
                "governance": [],
                "certification": [],
                "replay_evidence": [],
            },
            {
                "capability": "New Name",
                "capability_key": "new_name",
                "layer": "L1 Governance",
                "status": "CERTIFIED",
                "implementation": [],
                "tests": [],
                "governance": [],
                "certification": ["governance/NEW_NAME_CERTIFICATION.json"],
                "replay_evidence": [],
            },
            {
                "capability": "Duplicate Runtime",
                "capability_key": "duplicate_runtime",
                "layer": "L2 Cognition (OCS)",
                "status": "IMPLEMENTED",
                "implementation": ["aigol/runtime/duplicate.py"],
                "tests": ["tests/test_duplicate.py"],
                "governance": [],
                "certification": [],
                "replay_evidence": [],
            },
            {
                "capability": "Duplicate Certification",
                "capability_key": "duplicate_certification",
                "layer": "L2 Cognition (OCS)",
                "status": "CERTIFIED",
                "implementation": [],
                "tests": [],
                "governance": [],
                "certification": ["governance/DUPLICATE_CERTIFICATION.json"],
                "replay_evidence": [],
            },
            {
                "capability": "Versioned Capability V1",
                "capability_key": "versioned_capability_v1",
                "layer": "L3 Provider/Worker",
                "status": "PARTIAL",
                "implementation": [],
                "tests": [],
                "governance": ["governance/VERSIONED_CAPABILITY_V1.md"],
                "certification": [],
                "replay_evidence": [],
            },
            {
                "capability": "Versioned Capability V2",
                "capability_key": "versioned_capability_v2",
                "layer": "L3 Provider/Worker",
                "status": "PARTIAL",
                "implementation": [],
                "tests": [],
                "governance": ["governance/VERSIONED_CAPABILITY_V2.md"],
                "certification": [],
                "replay_evidence": [],
            },
        ],
    }


def test_alias_detection_and_capability_id_are_stable() -> None:
    first = normalize_capability_identity("Old Name", RULES)
    second = normalize_capability_identity("new-name", RULES)

    assert first["capability_id"] == "CAPABILITY::CANONICAL_NAME"
    assert first["capability_id"] == second["capability_id"]


def test_normalized_matrix_detects_renames_duplicates_and_versions() -> None:
    normalized = normalize_capability_matrix(_matrix(), rules=RULES)

    assert normalized["artifact_id"] == "AIGOL_CAPABILITY_NORMALIZED_MATRIX_V1"
    assert normalized["normalization_summary"]["source_capability_count"] == 6
    assert normalized["normalization_summary"]["normalized_capability_count"] == 3
    assert normalized["normalization_summary"]["duplicate_groups"] == 3
    assert normalized["normalization_summary"]["renamed_capabilities"] >= 2
    assert normalized["normalization_summary"]["version_only_changes"] == 1
    ids = {item["capability_id"]: item for item in normalized["capabilities"]}
    assert ids["CAPABILITY::CANONICAL_NAME"]["status"] == "CERTIFIED"
    assert ids["CAPABILITY::DUPLICATE"]["status"] == "CERTIFIED"
    assert ids["CAPABILITY::VERSIONED_CAPABILITY"]["source_count"] == 2
    assert normalized["normalized_matrix_hash"].startswith("sha256:")


def test_run_capability_normalization_writes_artifact(tmp_path: Path) -> None:
    governance = tmp_path / "governance"
    governance.mkdir()
    (governance / "AIGOL_CAPABILITY_MATRIX_V2.json").write_text(json.dumps(_matrix()), encoding="utf-8")
    (governance / "AIGOL_CAPABILITY_NORMALIZATION_RULES_V1.json").write_text(json.dumps(RULES), encoding="utf-8")

    capture = run_capability_normalization(repository_root=tmp_path)
    output = governance / "AIGOL_CAPABILITY_NORMALIZED_MATRIX_V1.json"
    normalized = json.loads(output.read_text(encoding="utf-8"))

    assert output.exists()
    assert capture["normalization_summary"]["normalized_capability_count"] == 3
    assert normalized["capability_counts"]["CERTIFIED"] == 2
