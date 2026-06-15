"""Repair certification tests for AIGOL_EXECUTION_SUMMARY_ENFORCEMENT_REPAIR_V1."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from aigol.runtime.execution_authorization_runtime import EXECUTION_AUTHORIZED, authorize_execution_ready
from aigol.runtime.execution_summary_runtime import (
    EXECUTION_SUMMARY_ARTIFACT_V1,
    EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1,
    create_execution_summary,
)
from aigol.runtime.governed_worker_execution_runtime import (
    WORKER_EXECUTION_COMPLETED,
    run_governed_worker_execution,
)
from aigol.runtime.native_provider_execution_runtime import STATUS_COMPLETED, run_native_provider_execution
from aigol.runtime.transport.serialization import replay_hash


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "AIGOL_EXECUTION_SUMMARY_ENFORCEMENT_REPAIR_V1.json"
CREATED_AT = "2026-06-15T00:00:00Z"


def _load_helper(module_name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(module_name, Path(__file__).with_name(file_name))
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


AUTH_HELPERS = _load_helper("execution_authorization_helpers", "test_execution_authorization_runtime_v1.py")
WORKER_HELPERS = _load_helper("governed_worker_execution_helpers", "test_governed_worker_execution_runtime_v1.py")


def _bad_summary() -> dict:
    return {
        "artifact_type": EXECUTION_SUMMARY_ARTIFACT_V1,
        "schema_version": "1.0",
        "summary_id": "BAD-SUMMARY",
        "created_at": CREATED_AT,
        "created_by": "HUMAN_OPERATOR",
        "original_request": "bad",
        "interpreted_intent": {"intent": "bad"},
        "selected_route": {"route": "bad"},
        "planned_actions": ["bad"],
        "expected_outputs": ["bad"],
        "assumptions": ["bad"],
        "constraints": ["bad"],
        "risk_classification": {"risk": "bad"},
        "authorization_required": False,
        "human_review_required": True,
        "human_response_options": ["APPROVE"],
        "execution_scope": {"scope": "bad"},
        "replay_references": ["bad"],
        "authority_flags": {},
        "summary_status": "PENDING_HUMAN_CONFIRMATION",
        "artifact_hash": replay_hash({"bad": True}),
    }


def test_execution_authorization_generates_summary_and_confirmation_before_authorization(tmp_path) -> None:
    ready = AUTH_HELPERS._execution_ready(tmp_path, prompt="Create a filesystem worker.", suffix="repair")

    capture = authorize_execution_ready(
        authorization_id="AUTHORIZATION-REPAIR",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=AUTH_HELPERS.CREATED_AT,
        replay_dir=tmp_path / "authorization_repair",
    )
    authorization = capture["execution_authorization_artifact"]

    assert capture["authorization_status"] == EXECUTION_AUTHORIZED
    assert authorization["execution_summary_reference"].endswith(":EXECUTION-SUMMARY")
    assert authorization["execution_summary_hash"].startswith("sha256:")
    assert authorization["human_confirmation_reference"].endswith(":EXECUTION-SUMMARY-CONFIRMATION")
    assert authorization["human_confirmation_hash"].startswith("sha256:")


def test_execution_authorization_fails_closed_on_invalid_summary(tmp_path) -> None:
    ready = AUTH_HELPERS._execution_ready(tmp_path, prompt="Create a filesystem worker.", suffix="bad-summary")

    capture = authorize_execution_ready(
        authorization_id="AUTHORIZATION-BAD-SUMMARY",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=AUTH_HELPERS.CREATED_AT,
        replay_dir=tmp_path / "authorization_bad_summary",
        execution_summary_artifact=_bad_summary(),
    )

    assert capture["authorization_status"] == "FAILED_CLOSED"
    assert "execution summary failed closed" in capture["failure_reason"]


def test_governed_worker_execution_generates_summary_before_execution(tmp_path) -> None:
    candidate = WORKER_HELPERS._execution_candidate(tmp_path)
    approval = WORKER_HELPERS._execution_approval(candidate)

    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-REPAIR",
        execution_candidate_artifact=candidate,
        human_approval_artifact=approval,
        executed_by="HUMAN_OPERATOR",
        executed_at=WORKER_HELPERS.CREATED_AT,
        replay_dir=tmp_path / "governed_worker_execution_repair",
    )
    result = capture["worker_execution_result_artifact"]

    assert capture["execution_status"] == WORKER_EXECUTION_COMPLETED
    assert result["execution_summary_hash"].startswith("sha256:")
    assert result["human_confirmation_hash"].startswith("sha256:")


def test_native_provider_execution_generates_summary_before_provider_invocation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")

    result = run_native_provider_execution(
        execution_id="NATIVE-PROVIDER-EXECUTION-REPAIR",
        human_request="Summarize governed execution summary enforcement.",
        provider_id="openai",
        model="gpt-5.1",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "native_provider_execution_repair",
        human_approved=True,
        approved_by="human.operator",
        transport=lambda _payload, _metadata: {"id": "resp-repair", "output_text": "ok"},
    )

    assert result["final_status"] == STATUS_COMPLETED
    assert result["provider_request"]["execution_summary_hash"].startswith("sha256:")
    assert result["provider_request"]["human_confirmation_hash"].startswith("sha256:")


def test_lifecycle_approval_without_summary_lineage_fails_closed(tmp_path) -> None:
    candidate = WORKER_HELPERS._execution_candidate(tmp_path)
    approval = WORKER_HELPERS._execution_approval(candidate)
    approval.pop("artifact_hash")
    approval.pop("source_execution_candidate")
    approval.pop("source_execution_candidate_hash")
    approval["source_execution_candidate"] = candidate["execution_candidate_id"]
    approval["source_execution_candidate_hash"] = candidate["artifact_hash"]
    approval["artifact_type"] = EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1
    approval["artifact_hash"] = replay_hash(approval)

    capture = run_governed_worker_execution(
        execution_id="GOVERNED-WORKER-EXECUTION-BAD-APPROVAL",
        execution_candidate_artifact=candidate,
        human_approval_artifact=approval,
        executed_by="HUMAN_OPERATOR",
        executed_at=WORKER_HELPERS.CREATED_AT,
        replay_dir=tmp_path / "bad_approval",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert "explicit human approval required" in capture["failure_reason"]


def test_repair_report_final_fields_are_certified() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert report["repair_status"] == "CERTIFIED"
    assert report["final_fields"] == {
        "SUMMARY_ENFORCEMENT_COMPLETE": "YES",
        "EXECUTION_WITHOUT_SUMMARY_POSSIBLE": "NO",
        "EXECUTION_WITHOUT_CONFIRMATION_POSSIBLE": "NO",
        "EXECUTION_WITHOUT_AUTHORIZATION_POSSIBLE": "NO",
        "ALL_EXECUTION_PATHS_PROTECTED": "YES",
        "AUTHORIZATION_BOUNDARY_PRESERVED": "YES",
        "FAIL_CLOSED_PRESERVED": "YES",
    }
