"""Tests for AIGOL_CAPABILITY_AUDIT_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.runtime.capability_audit_runtime import (
    build_capability_matrix,
    detect_capabilities,
    run_capability_audit,
)


def _write(path: Path, text: str = "{}\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_repo(tmp_path: Path) -> Path:
    _write(tmp_path / "governance" / "SAMPLE_CAPABILITY_CERTIFICATION.json")
    _write(tmp_path / "governance" / "SAMPLE_CAPABILITY_ACCEPTANCE_EVIDENCE.json")
    _write(tmp_path / "aigol" / "runtime" / "sample_capability.py", "\"\"\"sample\"\"\"\n")
    _write(tmp_path / "tests" / "test_sample_capability.py", "def test_sample():\n    assert True\n")
    _write(tmp_path / "aigol" / "runtime" / "implemented_only.py", "\"\"\"implemented\"\"\"\n")
    _write(tmp_path / "tests" / "test_implemented_only.py", "def test_implemented():\n    assert True\n")
    _write(tmp_path / "governance" / "PARTIAL_ONLY_GAP_ANALYSIS_V1.md", "# gap\n")
    return tmp_path


def test_detect_capabilities_classifies_certified_implemented_partial_and_missing(tmp_path) -> None:
    root = _fixture_repo(tmp_path)

    entries = detect_capabilities(root)
    matrix = build_capability_matrix(entries)
    statuses = {item["capability_key"]: item["status"] for item in matrix["capabilities"]}

    assert statuses["sample_capability"] == "CERTIFIED"
    assert statuses["implemented_only"] == "IMPLEMENTED"
    assert statuses["partial_only"] == "PARTIAL"
    assert statuses["marketplace_discovery_packaging_and_commercial_listing"] == "NOT_STARTED"
    assert matrix["capability_counts"]["CERTIFIED"] >= 1
    assert matrix["capability_counts"]["IMPLEMENTED"] >= 1
    assert matrix["capability_counts"]["PARTIAL"] >= 1
    assert matrix["capability_counts"]["NOT_STARTED"] >= 1
    assert matrix["matrix_hash"].startswith("sha256:")


def test_run_capability_audit_writes_v2_artifacts(tmp_path) -> None:
    root = _fixture_repo(tmp_path)

    capture = run_capability_audit(repository_root=root)
    matrix_path = root / "governance" / "AIGOL_CAPABILITY_MATRIX_V2.json"
    audit_path = root / "governance" / "AIGOL_CAPABILITY_AUDIT_V2.md"
    roadmap_path = root / "governance" / "AIGOL_ROADMAP_POST_AUDIT_V2.md"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    assert matrix_path.exists()
    assert audit_path.exists()
    assert roadmap_path.exists()
    assert matrix["artifact_id"] == "AIGOL_CAPABILITY_MATRIX_V2"
    assert matrix["runtime_version"] == "AIGOL_CAPABILITY_AUDIT_RUNTIME_V1"
    assert "AIGOL_CAPABILITY_AUDIT_V2_STATUS = GENERATED" in audit_path.read_text(encoding="utf-8")
    assert "Recommended Execution Order" in roadmap_path.read_text(encoding="utf-8")
    assert capture["capability_counts"]["total"] == matrix["capability_counts"]["total"]
    assert capture["audit_hash"].startswith("sha256:")


def test_certified_capability_requires_certification_evidence(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    (root / "governance" / "SAMPLE_CAPABILITY_CERTIFICATION.json").unlink()

    entries = detect_capabilities(root)
    matrix = build_capability_matrix(entries)
    sample = next(item for item in matrix["capabilities"] if item["capability_key"] == "sample_capability")

    assert sample["status"] == "IMPLEMENTED"
    assert sample["certification"] == []
