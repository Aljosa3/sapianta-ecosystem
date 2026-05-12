from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.protocol.validator import (
    validate_artifact,
    validate_json_text,
    validate_protocol_manifest,
)
from protocol_fixtures import valid_result, valid_task


def valid_analysis_context() -> dict:
    result = valid_result()
    context = {
        "protocol_version": "0.1",
        "task_id": "TASK-001",
        "analysis_context_id": "CTX-001",
        "interpretation_ready": True,
        "architectural_impact": {
            "level": "LOW",
            "summary": "Schema-only protocol substrate.",
        },
        "governance_impact": {
            "level": "LOW",
            "summary": "Replay-safe evidence envelope added.",
        },
        "risk_analysis": [],
        "opportunities": [],
        "recommended_next_milestone": {
            "milestone_id": "BRIDGE-TRANSPORT-V0.1",
            "reason": "Transport comes after protocol stabilization.",
        },
        "artifact_hashes": {
            "analysis_context_sha256": "0" * 64,
            "source_result_sha256": result["artifact_hashes"]["result_sha256"],
        },
        "lineage": {
            "source_task_id": "TASK-001",
            "source_result_id": "RESULT-001",
        },
    }
    context["artifact_hashes"]["analysis_context_sha256"] = compute_hash(
        context,
        omit_hash_fields={"analysis_context_sha256"},
    )
    return context


def valid_next_task_proposal() -> dict:
    return {
        "protocol_version": "0.1",
        "proposal_id": "NEXT-001",
        "proposal_type": "FOLLOW_UP",
        "recommended_action": "Prepare future bridge transport milestone.",
        "rationale": "Execution transport is intentionally excluded from v0.1.",
        "approval_required": True,
        "allowed_to_execute_automatically": False,
        "lineage": {
            "source_task_id": "TASK-001",
            "source_result_id": "RESULT-001",
            "source_analysis_context_id": "CTX-001",
        },
    }


def test_valid_task_schema_passes() -> None:
    result = validate_artifact(valid_task(), "task.json")
    assert result.valid, result.errors


def test_missing_task_id_rejected() -> None:
    task = valid_task()
    task.pop("task_id")
    result = validate_artifact(task, "task.json")
    assert not result.valid
    assert {"field": "task_id", "reason": "missing required field"} in result.to_dict()["errors"]


def test_invalid_protocol_version_rejected() -> None:
    task = valid_task()
    task["protocol_version"] = "9.9"
    result = validate_artifact(task, "task.json")
    assert not result.valid
    assert any(error["field"] == "protocol_version" for error in result.errors)


def test_invalid_enum_rejected() -> None:
    task = valid_task()
    task["task_type"] = "EXECUTE"
    result = validate_artifact(task, "task.json")
    assert not result.valid
    assert any(error["field"] == "task_type" for error in result.errors)


def test_malformed_artifact_rejected() -> None:
    result = validate_json_text("{", "task.json")
    assert not result.valid
    assert result.errors[0]["field"] == "json"


def test_next_task_proposal_always_disables_auto_execution() -> None:
    proposal = valid_next_task_proposal()
    assert validate_artifact(proposal, "next_task_proposal.json").valid

    proposal["allowed_to_execute_automatically"] = True
    result = validate_artifact(proposal, "next_task_proposal.json")
    assert not result.valid
    assert any(error["field"] == "allowed_to_execute_automatically" for error in result.errors)


def test_invalid_hash_rejected() -> None:
    result_artifact = valid_result()
    result_artifact["artifact_hashes"]["result_sha256"] = "f" * 64
    result = validate_artifact(result_artifact, "result.json")
    assert not result.valid
    assert any(error["reason"] == "hash mismatch" for error in result.errors)


def test_protocol_manifest_validation_passes() -> None:
    manifest_path = Path("sapianta_bridge/protocol/protocol_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = validate_protocol_manifest(manifest)
    assert result.valid, result.errors
