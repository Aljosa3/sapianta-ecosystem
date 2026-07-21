from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime.governed_worker_execution_runtime import (
    EXECUTION_APPROVAL_SCOPE,
    FAILED_CLOSED,
    project_g31_candidate_to_governed_execution,
    reconstruct_governed_worker_execution_replay,
    run_governed_worker_execution,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding import _run_aicli


def test_exact_candidate_creates_one_governed_execution_evidence_replay(tmp_path: Path) -> None:
    runtime, output, session_root = _run_aicli(tmp_path, "G31-16B-SUCCESS")
    capture = runtime["governed_worker_execution_capture"]
    result = capture["worker_execution_result_artifact"]
    approval = capture["execution_scoped_human_approval_artifact"]
    candidate = runtime["worker_execution_candidate_capture"]["worker_execution_candidate_artifact"]
    selection = runtime["authorized_worker_selection_capture"]["resource_selection_artifact"]
    reconstructed = reconstruct_governed_worker_execution_replay(
        capture["worker_execution_replay_reference"]
    )

    assert runtime["governed_execution_evidence_created"] is True
    assert len(list(Path(capture["worker_execution_replay_reference"]).glob("*.json"))) == 3
    assert reconstructed["execution_status"] == "WORKER_EXECUTION_COMPLETED"
    assert reconstructed["source_execution_candidate"] == candidate["execution_candidate_id"]
    assert result["source_execution_candidate_hash"] == candidate["artifact_hash"]
    assert result["implementation_result_created"] is False
    assert result["provider_invoked"] is False
    assert result["worker_evidence"]["subprocess_invoked"] is False
    assert approval["approval_scope"] == EXECUTION_APPROVAL_SCOPE
    assert approval["source_human_execution_decision"] == runtime["execution_human_decision_hash"]
    assert approval["source_execution_authorization_hash"] == runtime[
        "execution_authorization_capture"
    ]["execution_authorization_artifact"]["artifact_hash"]
    assert approval["third_human_decision_recorded"] is False
    assert capture["source_human_decision_count"] == 2
    assert selection["selected_resource_id"] == "CODEX"
    assert selection["selected_resource_category"] == "HYBRID_PROVIDER_WORKER"
    assert selection["selected_role_type"] == "WORKER_ROLE"
    assert selection["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY"
    assert "CODEX did not start" in "\n".join(output)
    assert Path(capture["worker_execution_replay_reference"]).parent == session_root


def test_candidate_only_approval_remains_invalid_for_execution(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-16B-CANDIDATE-APPROVAL")
    candidate_capture = runtime["worker_execution_candidate_capture"]
    replay_path = session_root / "INVALID-CANDIDATE-APPROVAL"
    rejected = run_governed_worker_execution(
        execution_id="INVALID-CANDIDATE-APPROVAL",
        execution_candidate_artifact=candidate_capture["worker_execution_candidate_artifact"],
        human_approval_artifact=candidate_capture["candidate_only_human_approval_artifact"],
        executed_by="TEST",
        executed_at="2026-07-17T00:00:00Z",
        replay_dir=replay_path,
    )
    assert rejected["execution_status"] == FAILED_CLOSED
    assert rejected["worker_execution_completed"] is False
    assert not (replay_path / "000_worker_execution_validation_inputs_recorded.json").exists()


def test_changed_candidate_and_duplicate_destination_fail_closed(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-16B-TAMPER")
    candidate_capture = deepcopy(runtime["worker_execution_candidate_capture"])
    candidate_capture["worker_execution_candidate_artifact"]["source_ppp_candidate"] = "OTHER-PPP"
    candidate_capture["worker_execution_candidate_artifact"].pop("artifact_hash")
    candidate_capture["worker_execution_candidate_artifact"]["artifact_hash"] = replay_hash(
        candidate_capture["worker_execution_candidate_artifact"]
    )
    with pytest.raises(FailClosedRuntimeError):
        project_g31_candidate_to_governed_execution(
            execution_candidate_capture=candidate_capture,
            session_root=session_root,
            executed_by="TEST",
            executed_at="2026-07-17T00:00:00Z",
            replay_dir=session_root / "TAMPERED-EXECUTION",
        )

    original = runtime["governed_worker_execution_capture"]
    duplicate = project_g31_candidate_to_governed_execution(
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=session_root,
        executed_by="TEST",
        executed_at="2026-07-17T00:00:00Z",
        replay_dir=original["worker_execution_replay_reference"],
    )
    assert duplicate["execution_status"] == FAILED_CLOSED
    assert reconstruct_governed_worker_execution_replay(
        original["worker_execution_replay_reference"]
    )["execution_status"] == "WORKER_EXECUTION_COMPLETED"


def test_projection_has_no_process_provider_result_or_mutation_path() -> None:
    implementation = inspect.getsource(project_g31_candidate_to_governed_execution)
    common_source = Path("aigol/runtime/human_interface_runtime_entry_service.py").read_text(encoding="utf-8")
    assert common_source.count("governed_execution.project_g31_candidate_to_governed_execution(") == 1
    for forbidden in (
        "start_execution(", "external_worker_adapter_runtime", "openai_external",
        "subprocess.run", "capture_worker_result(", "repository_mutation_worker",
        ".write_text(",
    ):
        assert forbidden not in implementation.lower()
