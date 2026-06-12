"""Checks for EXTERNAL_WORKER_READINESS_AUDIT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/EXTERNAL_WORKER_READINESS_AUDIT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_external_worker_audit_maps_complete_lifecycle() -> None:
    report = _load()
    completeness = report["lifecycle_completeness"]

    assert report["artifact_type"] == "EXTERNAL_WORKER_READINESS_AUDIT_V1"
    assert completeness["total_stages"] == 8
    assert completeness["implemented_stages"] == 8
    assert completeness["certified_stages"] == 7
    assert completeness["production_ready_stages"] == 6
    assert completeness["implemented_percent"] == 100.0
    assert completeness["certified_percent"] == 87.5
    assert completeness["production_ready_percent"] == 75.0


def test_external_worker_audit_classifies_assignment_and_execution_gaps() -> None:
    report = _load()
    stages = {stage["stage"]: stage for stage in report["lifecycle_stage_map"]}

    assert stages["WORKER_ASSIGNMENT"]["classification"] == "IMPLEMENTED"
    assert stages["WORKER_ASSIGNMENT"]["certified"] is False
    assert stages["WORKER_ASSIGNMENT"]["production_ready"] is False
    assert stages["WORKER_EXECUTION"]["classification"] == "CERTIFIED"
    assert stages["WORKER_EXECUTION"]["certified"] is True
    assert stages["WORKER_EXECUTION"]["production_ready"] is False
    assert "external LLM worker adapter" in stages["WORKER_EXECUTION"]["notes"]


def test_external_worker_audit_identifies_minimal_missing_components() -> None:
    report = _load()
    missing = report["missing_components"]
    gap = report["minimal_integration_gap"]

    assert "EXTERNAL_WORKER_ADAPTER_ARTIFACT_V1" in missing["missing_artifacts"]
    assert "external_worker_adapter_runtime.py" in missing["missing_runtimes"]
    assert "EXTERNAL_WORKER_ADAPTER_CERTIFICATION_V1" in missing["missing_certifications"]
    assert len(missing["missing_adapters"]) == 4
    assert gap["minimal_next_runtime"] == "aigol/runtime/external_worker_adapter_runtime.py"
    assert gap["minimal_next_artifact"] == "EXTERNAL_WORKER_ADAPTER_ARTIFACT_V1"
    assert "WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1" in gap["description"]


def test_external_worker_audit_scores_worker_options() -> None:
    report = _load()
    readiness = {item["worker_type"]: item for item in report["external_worker_readiness"]}

    assert readiness["Codex Worker"]["readiness_score"] == 80
    assert readiness["Claude Code Worker"]["readiness_score"] == 70
    assert readiness["Mistral Worker"]["readiness_score"] == 55
    assert readiness["Generic Local Worker"]["readiness_score"] == 75
    assert readiness["Codex Worker"]["readiness"] == "HIGH_WITH_ADAPTER_BINDING_GAP"
    assert readiness["Generic Local Worker"]["readiness"] == (
        "HIGH_FOR_COMMAND_AND_FILESYSTEM_WORKER_AFTER_CERTIFICATION"
    )


def test_external_worker_audit_final_outputs() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert outputs["WORKER_LIFECYCLE_COMPLETENESS"] == (
        "8_OF_8_IMPLEMENTED_7_OF_8_CERTIFIED_6_OF_8_PRODUCTION_READY"
    )
    assert outputs["CERTIFIED_COMPONENTS"] == "7_LIFECYCLE_STAGES_PLUS_5_CERTIFICATION_ARTIFACT_GROUPS"
    assert outputs["MISSING_COMPONENTS"] == "3_ARTIFACTS_2_RUNTIMES_3_CERTIFICATIONS_4_ADAPTER_BINDINGS"
    assert outputs["MINIMAL_INTEGRATION_GAP"].startswith("CERTIFIED_PROVIDER_NEUTRAL_EXTERNAL_WORKER_ADAPTER")
    assert outputs["EXTERNAL_WORKER_READINESS_SCORE"] == "75.0"
    assert outputs["RECOMMENDED_NEXT_IMPLEMENTATION"] == "AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_V1"
