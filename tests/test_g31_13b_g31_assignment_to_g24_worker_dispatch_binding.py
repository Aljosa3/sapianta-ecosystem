from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    WORKER_DISPATCH_ARTIFACT_V1,
    WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1,
    WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1,
    WORKER_DISPATCH_RESULT_ARTIFACT_V1,
    dispatch_assigned_worker,
    reconstruct_worker_dispatch_replay,
)
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT, REQUEST, _workspace


def _run_aicli(tmp_path: Path, session: str) -> tuple[dict, list[str], Path]:
    workspace = _workspace(tmp_path, f"{session}-workspace")
    runtime_root = tmp_path / "runtime"
    output: list[str] = []
    values = iter([REQUEST, "/send", "/approve", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=runtime_root,
        workspace=workspace,
        input_reader=lambda _prompt: next(values),
        output_writer=output.append,
    )
    return result["runtime_result"], output, runtime_root / session


def test_aicli_directly_reaches_existing_g24_dispatch_and_reconstructs_lineage(
    tmp_path: Path,
) -> None:
    runtime, output, session_root = _run_aicli(tmp_path, "G31-13B-SUCCESS")
    assignment = runtime["worker_assignment_capture"]
    dispatch = runtime["worker_dispatch_capture"]
    dispatch_artifact = dispatch["worker_dispatch_artifact"]
    assignment_artifact = assignment["worker_assignment_artifact"]
    replay_path = Path(dispatch["worker_dispatch_replay_reference"])

    assert runtime["worker_selected"] is True
    assert runtime["worker_assigned"] is True
    assert runtime["worker_dispatched"] is True
    assert runtime["worker_invoked"] is True
    assert runtime["authorization_dispatch_blocked"] is False
    assert assignment["worker_dispatched"] is False
    assert dispatch["worker_invoked"] is False
    assert dispatch["dispatch_status"] == WORKER_DISPATCHED
    assert dispatch["dispatch_evidence_artifact"]["artifact_type"] == WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1
    assert dispatch["dispatch_classification_artifact"]["artifact_type"] == WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1
    assert dispatch_artifact["artifact_type"] == WORKER_DISPATCH_ARTIFACT_V1
    assert dispatch["dispatch_result_artifact"]["artifact_type"] == WORKER_DISPATCH_RESULT_ARTIFACT_V1
    assert dispatch_artifact["worker_assignment_hash"] == assignment_artifact["artifact_hash"]
    assert replay_path == session_root / f"WORKER-DISPATCH-{assignment_artifact['artifact_hash'][-16:]}"
    assert Path(assignment["worker_assignment_replay_reference"]).parent == replay_path.parent

    reconstructed = reconstruct_worker_dispatch_replay(replay_path)
    assert reconstructed["dispatch_status"] == WORKER_DISPATCHED
    assert reconstructed["worker_assignment_reference"] == assignment_artifact["worker_assignment_id"]
    assert reconstructed["worker_id"] == "CODEX"
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_started"] is False
    assert reconstructed["result_created"] is False

    rendered = "\n".join(output)
    assert rendered.index("Worker Invocation Request") < rendered.index("Worker Assignment")
    assert rendered.index("Worker Assignment") < rendered.index("Worker Dispatch")
    assert "Dispatch Status: WORKER_DISPATCHED" in rendered
    assert "Dispatched Worker: CODEX" in rendered
    assert "No Worker has been invoked, executed, or produced results." in rendered


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("worker_assignment_id", "OTHER-ASSIGNMENT"),
        ("worker_invocation_request_hash", "sha256:" + "1" * 64),
        ("authorization_hash", "sha256:" + "2" * 64),
        ("execution_packet_hash", "sha256:" + "3" * 64),
        ("worker_id", "OTHER-WORKER"),
        ("worker_family", "PROVIDER"),
        ("worker_role", "PROVIDER_ROLE"),
    ),
)
def test_substituted_assignment_request_authorization_scope_or_worker_fails_before_dispatch(
    tmp_path: Path, field: str, value: str
) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, f"G31-13B-{field}")
    assignment = runtime["worker_assignment_capture"]
    artifact = deepcopy(assignment["worker_assignment_artifact"])
    artifact[field] = value
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    replay_path = session_root / f"FAILED-{field}"

    capture = dispatch_assigned_worker(
        worker_dispatch_id=f"FAILED-{field}",
        worker_assignment_artifact=artifact,
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert capture["worker_dispatched"] is False
    assert capture["worker_dispatch_artifact"] is None
    assert not (replay_path / "000_dispatch_evidence_recorded.json").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("selected_resource_category", "PROVIDER"),
        ("selected_role_type", "PROVIDER_ROLE"),
        ("selected_authority_profile", "PROVIDER_PROPOSAL_ONLY"),
        ("registry_hash", "sha256:" + "4" * 64),
        ("worker_selection_certification_hash", "sha256:" + "5" * 64),
    ),
)
def test_nested_selection_registry_certification_role_or_profile_substitution_fails_closed(
    tmp_path: Path, field: str, value: str
) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, f"G31-13B-SELECTION-{field}")
    selection = runtime["authorized_worker_selection_capture"]
    assignment = runtime["worker_assignment_capture"]
    selection_replay = Path(selection["resource_selection_replay_reference"])
    wrapper_path = selection_replay / "000_resource_selection_recorded.json"
    wrapper = load_json(wrapper_path)
    wrapper["artifact"][field] = value
    wrapper["artifact"] = with_replay_hash(wrapper["artifact"], hash_field="artifact_hash")
    wrapper_path.write_text(
        json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")),
        encoding="utf-8",
    )
    replay_path = session_root / f"FAILED-SELECTION-{field}"

    capture = dispatch_assigned_worker(
        worker_dispatch_id=f"FAILED-SELECTION-{field}",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert capture["dispatch_status"] == "FAILED_CLOSED"
    assert capture["worker_dispatch_artifact"] is None
    assert not (replay_path / "000_dispatch_evidence_recorded.json").exists()


def test_duplicate_dispatch_fails_without_changing_original_replay(tmp_path: Path) -> None:
    runtime, _, _ = _run_aicli(tmp_path, "G31-13B-DUPLICATE")
    assignment = runtime["worker_assignment_capture"]
    dispatch = runtime["worker_dispatch_capture"]
    replay_path = Path(dispatch["worker_dispatch_replay_reference"])
    before = reconstruct_worker_dispatch_replay(replay_path)

    duplicate = dispatch_assigned_worker(
        worker_dispatch_id=dispatch["worker_dispatch_reference"],
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="AIGOL_GOVERNANCE",
        dispatched_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert duplicate["dispatch_status"] == "FAILED_CLOSED"
    assert duplicate["worker_dispatch_artifact"] is None
    assert reconstruct_worker_dispatch_replay(replay_path)["replay_hash"] == before["replay_hash"]


def test_dispatch_stage_remains_non_invoking_before_later_invocation(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-13B-BOUNDARY")
    assert runtime["worker_invoked"] is True
    assert runtime["worker_dispatch_capture"]["worker_invoked"] is False
    for field in ("provider_invoked", "command_executed", "repository_mutated"):
        assert runtime[field] is False
    assert len(list(session_root.glob("WORKER-INVOCATION-*"))) == 1
    source = Path("aigol/runtime/human_interface_runtime_entry_service.py").read_text(encoding="utf-8")
    assert source.count("worker_dispatch.dispatch_assigned_worker(") == 2
    assert source.count("worker_invocation.invoke_dispatched_worker(") == 1
    for duplicate in ("def _verify_hash", "def _relative_path", "def _unique_relative_paths"):
        assert duplicate not in source
