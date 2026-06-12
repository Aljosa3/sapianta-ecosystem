"""Checks for AIGOL_FIRST_EXTERNAL_LLM_WORKER_CERTIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = ROOT / ".github/governance/finalize/AIGOL_FIRST_EXTERNAL_LLM_WORKER_CERTIFICATION_V1.json"


def _load() -> dict:
    return json.loads(CERTIFICATION.read_text(encoding="utf-8"))


def test_first_external_worker_certification_records_scope() -> None:
    certification = _load()
    scope = certification["certification_scope"]

    assert certification["artifact_type"] == "FIRST_EXTERNAL_LLM_WORKER_CERTIFICATION_V1"
    assert certification["certified_runtime"] == "AIGOL_FIRST_EXTERNAL_LLM_WORKER_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert scope["input_artifact"] == "EXTERNAL_WORKER_TASK_PACKAGE_V1"
    assert scope["output_artifact"] == "EXTERNAL_WORKER_RESULT_PACKAGE_V1"
    assert scope["proposal_authority"] == "PROPOSAL_ONLY"
    assert scope["repository_mutation_allowed"] is False
    assert scope["command_execution_allowed"] is False
    assert scope["provider_specific_logic_allowed"] is False


def test_first_external_worker_certification_preserves_boundaries() -> None:
    certification = _load()
    guarantees = certification["governance_guarantees"]

    assert guarantees["task_package_consumed"] is True
    assert guarantees["result_package_generated"] is True
    assert guarantees["adapter_compatibility_confirmed"] is True
    assert guarantees["result_validation_compatibility_confirmed"] is True
    assert guarantees["replay_compatibility_confirmed"] is True
    assert guarantees["provider_neutrality_confirmed"] is True
    assert guarantees["repository_mutation_performed"] is False
    assert guarantees["command_execution_performed"] is False
    assert guarantees["proposal_only_authority_preserved"] is True


def test_first_external_worker_certification_final_outputs() -> None:
    certification = _load()
    outputs = certification["final_outputs"]

    assert outputs["FIRST_EXTERNAL_WORKER_IMPLEMENTED"] == "YES"
    assert outputs["TASK_PACKAGE_CONSUMED"] == "YES"
    assert outputs["RESULT_PACKAGE_GENERATED"] == "YES"
    assert outputs["REPLAY_COMPATIBILITY_CONFIRMED"] == "YES"
    assert outputs["PROVIDER_NEUTRALITY_CONFIRMED"] == "YES"
    assert outputs["READY_FOR_REAL_WORKER_EVALUATION"] == "YES"
