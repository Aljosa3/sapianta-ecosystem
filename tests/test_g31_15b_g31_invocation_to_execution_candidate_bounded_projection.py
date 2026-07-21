from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import (
    APPROVAL_SCOPE,
    project_g31_invocation_to_execution_candidate,
    reconstruct_worker_invocation_to_execution_candidate_bridge_replay,
)
from test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding import _run_aicli


def test_exact_g31_invocation_creates_one_candidate_with_authentic_lineage(tmp_path: Path) -> None:
    runtime, output, session_root = _run_aicli(tmp_path, "G31-15B-SUCCESS")
    capture = runtime["worker_execution_candidate_capture"]
    candidate = capture["worker_execution_candidate_artifact"]
    approval = capture["candidate_only_human_approval_artifact"]
    invocation = runtime["worker_invocation_capture"]["worker_invocation_artifact"]
    selection = runtime["authorized_worker_selection_capture"]["resource_selection_artifact"]
    grounding = runtime["execution_human_decision_result"][
        "source_authorization_review_artifact"
    ]["source_repository_scope_grounding_artifact"]
    ppp = grounding["source_worker_payload_binding_artifact"]["ppp_task_package_artifact"]

    reconstructed = reconstruct_worker_invocation_to_execution_candidate_bridge_replay(
        capture["worker_execution_candidate_replay_reference"]
    )
    assert runtime["execution_candidate_created"] is True
    assert len(list(Path(capture["worker_execution_candidate_replay_reference"]).glob("*.json"))) == 3
    assert reconstructed["candidate_status"] == "WORKER_EXECUTION_CANDIDATE_CREATED"
    assert candidate["source_worker_invocation_hash"] == invocation["artifact_hash"]
    assert candidate["source_ppp_candidate"] == ppp["ppp_candidate_id"]
    assert candidate["source_ppp_candidate_hash"] == ppp["artifact_hash"]
    assert candidate["execution_candidate_scope"]["allowed_outputs"] == invocation["allowed_outputs"]
    assert selection["selected_resource_id"] == "CODEX"
    assert selection["selected_resource_category"] == "HYBRID_PROVIDER_WORKER"
    assert selection["selected_role_type"] == "WORKER_ROLE"
    assert selection["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY"
    assert approval["approval_scope"] == APPROVAL_SCOPE
    assert approval["source_human_execution_decision"] == runtime["execution_human_decision_hash"]
    assert approval["source_execution_authorization_hash"] == runtime[
        "execution_authorization_capture"
    ]["execution_authorization_artifact"]["artifact_hash"]
    assert approval["derived_compatibility_projection"] is True
    assert approval["third_human_decision_recorded"] is False
    assert capture["source_human_decision_count"] == 2
    assert "execution candidate was created as governance evidence only" in "\n".join(output)
    assert session_root == Path(capture["worker_execution_candidate_replay_reference"]).parent


def test_candidate_stops_before_every_execution_and_authority_boundary(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-15B-BOUNDARY")
    approval = runtime["worker_execution_candidate_capture"][
        "candidate_only_human_approval_artifact"
    ]
    assert runtime["worker_selected"] is True
    assert runtime["worker_assigned"] is True
    assert runtime["worker_dispatched"] is True
    assert runtime["worker_invoked"] is True
    assert runtime["execution_candidate_created"] is True
    for field in (
        "provider_invoked", "worker_process_started", "execution_started",
        "command_executed", "result_created", "repository_mutated",
    ):
        assert runtime[field] is False
    for field in (
        "worker_execution_allowed", "provider_invocation_allowed", "execution_started",
        "command_executed", "implementation_result_creation_allowed", "repository_mutation_allowed",
    ):
        assert approval[field] is False
    assert runtime["worker_dispatch_capture"]["worker_invoked"] is False
    assert not list(session_root.rglob("000_execution_started.json"))
    assert not list(session_root.glob("WORKER-RESULT-*"))


def test_changed_invocation_or_duplicate_candidate_fails_closed(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-15B-TAMPER")
    invocation_capture = runtime["worker_invocation_capture"]
    invocation = deepcopy(invocation_capture["worker_invocation_artifact"])
    invocation["worker_id"] = "OTHER-WORKER"
    invocation.pop("artifact_hash")
    invocation["artifact_hash"] = replay_hash(invocation)
    with pytest.raises(FailClosedRuntimeError):
        project_g31_invocation_to_execution_candidate(
            worker_invocation_artifact=invocation,
            worker_invocation_replay_reference=invocation_capture[
                "worker_invocation_replay_reference"
            ],
            session_root=session_root,
            requested_by="TEST",
            created_at="2026-07-17T00:00:00Z",
            replay_dir=session_root / "TAMPERED-CANDIDATE",
        )
    original = runtime["worker_execution_candidate_capture"]
    duplicate = project_g31_invocation_to_execution_candidate(
        worker_invocation_artifact=invocation_capture["worker_invocation_artifact"],
        worker_invocation_replay_reference=invocation_capture[
            "worker_invocation_replay_reference"
        ],
        session_root=session_root,
        requested_by="TEST",
        created_at="2026-07-17T00:00:00Z",
        replay_dir=original["worker_execution_candidate_replay_reference"],
    )
    assert duplicate["worker_execution_candidate_generated"] is False
    assert reconstruct_worker_invocation_to_execution_candidate_bridge_replay(
        original["worker_execution_candidate_replay_reference"]
    )["candidate_status"] == "WORKER_EXECUTION_CANDIDATE_CREATED"


def test_common_entry_has_one_candidate_edge_and_no_forbidden_execution_imports() -> None:
    source = Path("aigol/runtime/human_interface_runtime_entry_service.py").read_text(encoding="utf-8")
    implementation = inspect.getsource(project_g31_invocation_to_execution_candidate)
    assert source.count("worker_candidate.project_g31_invocation_to_execution_candidate(") == 1
    for forbidden in (
        "start_execution", "run_governed_worker_execution", "capture_worker_result",
        "subprocess", "repository_mutation_worker", "external_worker_adapter",
    ):
        assert forbidden not in implementation
