"""Tests for AIGOL_CAPABILITY_AUDIT_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.runtime.capability_audit_runtime import (
    build_audit_report_summary,
    build_capability_matrix,
    detect_capabilities,
    main,
    render_audit_report_summary,
    render_cli_summary,
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
    summary_path = root / "governance" / "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_V1.md"
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    assert matrix_path.exists()
    assert audit_path.exists()
    assert roadmap_path.exists()
    assert summary_path.exists()
    assert matrix["artifact_id"] == "AIGOL_CAPABILITY_MATRIX_V2"
    assert matrix["runtime_version"] == "AIGOL_CAPABILITY_AUDIT_RUNTIME_V1"
    assert "AIGOL_CAPABILITY_AUDIT_V2_STATUS = GENERATED" in audit_path.read_text(encoding="utf-8")
    assert "Recommended Execution Order" in roadmap_path.read_text(encoding="utf-8")
    assert "AIGOL_CAPABILITY_AUDIT_REPORT_SUMMARY_STATUS = CERTIFIED" in summary_path.read_text(encoding="utf-8")
    assert capture["capability_counts"]["total"] == matrix["capability_counts"]["total"]
    assert capture["summary_path"] == str(summary_path)
    assert capture["overall_maturity"] >= 0
    assert capture["audit_hash"].startswith("sha256:")


def test_certified_capability_requires_certification_evidence(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    (root / "governance" / "SAMPLE_CAPABILITY_CERTIFICATION.json").unlink()

    entries = detect_capabilities(root)
    matrix = build_capability_matrix(entries)
    sample = next(item for item in matrix["capabilities"] if item["capability_key"] == "sample_capability")

    assert sample["status"] == "IMPLEMENTED"
    assert sample["certification"] == []


def test_audit_matrix_includes_normalized_capability_id(tmp_path) -> None:
    root = _fixture_repo(tmp_path)

    entries = detect_capabilities(root)
    matrix = build_capability_matrix(entries)
    sample = next(item for item in matrix["capabilities"] if item["capability_key"] == "sample_capability")

    assert sample["capability_id"] == "CAPABILITY::SAMPLE_CAPABILITY"
    assert sample["canonical_capability_key"] == "sample_capability"
    assert sample["normalization"]["capability_id"] == sample["capability_id"]


def test_audit_summary_generation_includes_counts_layers_and_recommendation(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    matrix = build_capability_matrix(detect_capabilities(root))

    summary = build_audit_report_summary(matrix, repository_root=root, audit_timestamp="2026-06-05T00:00:00+00:00")
    rendered = render_audit_report_summary(summary)

    assert summary["repository"] == str(root.resolve())
    assert summary["audit_timestamp"] == "2026-06-05T00:00:00+00:00"
    assert summary["capability_counts"]["CERTIFIED"] >= 1
    assert summary["normalized_capability_counts"]["total"] <= summary["capability_counts"]["total"]
    assert "Governance" in rendered
    assert "OCS / Cognition" in rendered
    assert "Provider / Worker" in rendered
    assert "Recommended Next Milestone" in rendered
    assert summary["recommended_next_milestone"]["milestone"].startswith("AIGOL_")


def test_audit_summary_layer_ranking_generation(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    matrix = build_capability_matrix(detect_capabilities(root))

    summary = build_audit_report_summary(matrix, repository_root=root, audit_timestamp="2026-06-05T00:00:00+00:00")

    assert len(summary["top_strongest_layers"]) == 5
    assert len(summary["top_weakest_layers"]) == 5
    assert summary["top_strongest_layers"][0]["score"] >= summary["top_strongest_layers"][-1]["score"]
    assert summary["top_weakest_layers"][0]["score"] <= summary["top_weakest_layers"][-1]["score"]
    assert len(summary["top_capability_growth_areas"]) == 5
    assert len(summary["top_stagnating_areas"]) == 5


def test_audit_summary_recommendation_generation_for_weak_marketplace_layer(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    matrix = build_capability_matrix(detect_capabilities(root))

    summary = build_audit_report_summary(matrix, repository_root=root, audit_timestamp="2026-06-05T00:00:00+00:00")

    assert summary["recommended_next_milestone"]["milestone"] == "AIGOL_MARKETPLACE_ECOSYSTEM_FOUNDATION_V1"
    assert "Marketplace / Ecosystem" in summary["recommended_next_milestone"]["reasoning"]


def test_audit_cli_summary_output_generation(tmp_path, capsys) -> None:
    root = _fixture_repo(tmp_path)

    result = main([str(root)])
    output = capsys.readouterr().out

    assert result == 0
    assert "AIGOL CAPABILITY AUDIT SUMMARY" in output
    assert f"Repository: {root.resolve()}" in output
    assert "Overall Maturity:" in output
    assert "Top Strengths:" in output
    assert "Top Weaknesses:" in output
    assert "Recommended Next Milestone:" in output
    assert "Status: SUCCESS" in output


def test_render_cli_summary_contract(tmp_path) -> None:
    root = _fixture_repo(tmp_path)
    matrix = build_capability_matrix(detect_capabilities(root))
    summary = build_audit_report_summary(matrix, repository_root=root, audit_timestamp="2026-06-05T00:00:00+00:00")

    output = render_cli_summary(summary)

    assert output.startswith("AIGOL CAPABILITY AUDIT SUMMARY")
    assert "Repository:" in output
    assert "Overall Maturity:" in output
    assert "Status: SUCCESS" in output
