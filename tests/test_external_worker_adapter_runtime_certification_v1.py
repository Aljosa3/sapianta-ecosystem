"""Checks for AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_CERTIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = ROOT / ".github/governance/finalize/AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_CERTIFICATION_V1.json"


def _load() -> dict:
    return json.loads(CERTIFICATION.read_text(encoding="utf-8"))


def test_external_worker_adapter_certification_records_runtime_scope() -> None:
    certification = _load()
    scope = certification["certification_scope"]

    assert certification["artifact_type"] == "EXTERNAL_WORKER_ADAPTER_RUNTIME_CERTIFICATION_V1"
    assert certification["certified_runtime"] == "AIGOL_EXTERNAL_WORKER_ADAPTER_RUNTIME_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert scope["input_artifact"] == "WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1"
    assert scope["task_package_artifact"] == "EXTERNAL_WORKER_TASK_PACKAGE_V1"
    assert scope["result_package_artifact"] == "EXTERNAL_WORKER_RESULT_PACKAGE_V1"
    assert scope["output_artifact"] == "WORKER_EXECUTION_RESULT_ARTIFACT_V1"
    assert scope["provider_specific_logic_allowed"] is False


def test_external_worker_adapter_certification_preserves_governance_guarantees() -> None:
    certification = _load()
    guarantees = certification["governance_guarantees"]

    assert guarantees["accepts_only_worker_execution_candidate"] is True
    assert guarantees["task_package_generated"] is True
    assert guarantees["result_package_accepted"] is True
    assert guarantees["worker_execution_result_generated"] is True
    assert guarantees["replay_lineage_preserved"] is True
    assert guarantees["fail_closed_preserved"] is True
    assert guarantees["provider_neutrality_preserved"] is True
    assert guarantees["human_authority_preserved"] is True
    assert guarantees["provider_specific_logic_used"] is False


def test_external_worker_adapter_certification_final_outputs() -> None:
    certification = _load()
    outputs = certification["final_outputs"]

    assert outputs["EXTERNAL_WORKER_ADAPTER_IMPLEMENTED"] == "YES"
    assert outputs["TASK_PACKAGE_GENERATED"] == "YES"
    assert outputs["RESULT_PACKAGE_ACCEPTED"] == "YES"
    assert outputs["REPLAY_LINEAGE_PRESERVED"] == "YES"
    assert outputs["PROVIDER_NEUTRALITY_PRESERVED"] == "YES"
    assert outputs["READY_FOR_FIRST_EXTERNAL_WORKER"] == "YES"
