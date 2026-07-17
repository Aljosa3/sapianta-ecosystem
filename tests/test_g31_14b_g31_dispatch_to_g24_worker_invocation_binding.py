from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1,
    WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1,
    WORKER_INVOCATION_RESULT_ARTIFACT_V1,
    invoke_dispatched_worker,
    reconstruct_worker_invocation_replay,
)
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT
from test_g31_13b_g31_assignment_to_g24_worker_dispatch_binding import _run_aicli


def test_exact_g31_dispatch_reaches_existing_invocation_and_reconstructs_lineage(
    tmp_path: Path,
) -> None:
    runtime, output, session_root = _run_aicli(tmp_path, "G31-14B-SUCCESS")
    dispatch = runtime["worker_dispatch_capture"]
    invocation = runtime["worker_invocation_capture"]
    dispatch_artifact = dispatch["worker_dispatch_artifact"]
    invocation_artifact = invocation["worker_invocation_artifact"]
    replay_path = Path(invocation["worker_invocation_replay_reference"])

    assert runtime["worker_selected"] is True
    assert runtime["worker_assigned"] is True
    assert runtime["worker_dispatched"] is True
    assert runtime["worker_invoked"] is True
    assert dispatch["worker_invoked"] is False
    assert invocation["invocation_status"] == WORKER_INVOKED
    assert invocation["invocation_evidence_artifact"]["artifact_type"] == WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1
    assert invocation["invocation_classification_artifact"]["artifact_type"] == WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1
    assert invocation_artifact["artifact_type"] == WORKER_INVOCATION_ARTIFACT_V1
    assert invocation["invocation_result_artifact"]["artifact_type"] == WORKER_INVOCATION_RESULT_ARTIFACT_V1
    assert invocation_artifact["worker_dispatch_hash"] == dispatch_artifact["artifact_hash"]
    assert replay_path == session_root / f"WORKER-INVOCATION-{dispatch_artifact['artifact_hash'][-16:]}"
    assert Path(dispatch["worker_dispatch_replay_reference"]).parent == replay_path.parent

    reconstructed = reconstruct_worker_invocation_replay(replay_path)
    assert reconstructed["invocation_status"] == WORKER_INVOKED
    assert reconstructed["worker_dispatch_reference"] == dispatch_artifact["worker_dispatch_id"]
    assert reconstructed["worker_id"] == "CODEX"
    assert reconstructed["worker_invoked"] is True
    assert reconstructed["execution_started"] is False
    assert reconstructed["result_created"] is False
    assert reconstructed["result_validated"] is False

    rendered = "\n".join(output)
    assert rendered.index("Worker Assignment") < rendered.index("Worker Dispatch")
    assert rendered.index("Worker Dispatch") < rendered.index("Worker Invocation\n")
    assert "selected_role_type: WORKER_ROLE" in rendered
    assert "Invocation Status: WORKER_INVOKED" in rendered
    assert "Invoked Worker: CODEX" in rendered
    assert "Worker invocation lifecycle evidence has been recorded." in rendered
    assert "No Worker process or execution has started." in rendered
    assert "No command has executed." in rendered
    assert "No Worker result has been produced." in rendered
    assert "No repository has been modified." in rendered


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("worker_dispatch_id", "OTHER-DISPATCH"),
        ("worker_assignment_hash", "sha256:" + "1" * 64),
        ("worker_invocation_request_hash", "sha256:" + "2" * 64),
        ("authorization_hash", "sha256:" + "3" * 64),
        ("execution_packet_hash", "sha256:" + "4" * 64),
        ("worker_id", "OTHER-WORKER"),
        ("worker_role", "PROVIDER_ROLE"),
    ),
)
def test_dispatch_assignment_request_authorization_scope_or_worker_substitution_fails(
    tmp_path: Path, field: str, value: str
) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, f"G31-14B-{field}")
    dispatch = runtime["worker_dispatch_capture"]
    artifact = deepcopy(dispatch["worker_dispatch_artifact"])
    artifact[field] = value
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    replay_path = session_root / f"FAILED-{field}"

    capture = invoke_dispatched_worker(
        worker_invocation_id=f"FAILED-{field}",
        worker_dispatch_artifact=artifact,
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert capture["worker_invoked"] is False
    assert capture["worker_invocation_artifact"] is None
    assert not (replay_path / "000_invocation_evidence_recorded.json").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("selected_resource_category", "PROVIDER"),
        ("selected_role_type", "PROVIDER_ROLE"),
        ("selected_authority_profile", "PROVIDER_PROPOSAL_ONLY"),
        ("registry_hash", "sha256:" + "5" * 64),
        ("worker_selection_certification_hash", "sha256:" + "6" * 64),
    ),
)
def test_nested_selection_registry_certification_role_or_profile_substitution_fails(
    tmp_path: Path, field: str, value: str
) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, f"G31-14B-SELECTION-{field}")
    selection = runtime["authorized_worker_selection_capture"]
    dispatch = runtime["worker_dispatch_capture"]
    wrapper_path = Path(selection["resource_selection_replay_reference"]) / "000_resource_selection_recorded.json"
    wrapper = load_json(wrapper_path)
    wrapper["artifact"][field] = value
    wrapper["artifact"] = with_replay_hash(wrapper["artifact"], hash_field="artifact_hash")
    wrapper_path.write_text(
        json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")),
        encoding="utf-8",
    )
    replay_path = session_root / f"FAILED-SELECTION-{field}"

    capture = invoke_dispatched_worker(
        worker_invocation_id=f"FAILED-SELECTION-{field}",
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert capture["invocation_status"] == "FAILED_CLOSED"
    assert capture["worker_invocation_artifact"] is None
    assert not (replay_path / "000_invocation_evidence_recorded.json").exists()


def test_duplicate_invocation_fails_without_changing_original_replay(tmp_path: Path) -> None:
    runtime, _, _ = _run_aicli(tmp_path, "G31-14B-DUPLICATE")
    dispatch = runtime["worker_dispatch_capture"]
    invocation = runtime["worker_invocation_capture"]
    replay_path = Path(invocation["worker_invocation_replay_reference"])
    before = reconstruct_worker_invocation_replay(replay_path)

    duplicate = invoke_dispatched_worker(
        worker_invocation_id=invocation["worker_invocation_reference"],
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="AIGOL_GOVERNANCE",
        invoked_at=CREATED_AT,
        replay_dir=replay_path,
    )

    assert duplicate["invocation_status"] == "FAILED_CLOSED"
    assert duplicate["worker_invocation_artifact"] is None
    assert reconstruct_worker_invocation_replay(replay_path)["replay_hash"] == before["replay_hash"]


def test_invocation_evidence_stops_before_execution_and_external_activation(tmp_path: Path) -> None:
    runtime, _, session_root = _run_aicli(tmp_path, "G31-14B-BOUNDARY")
    assert runtime["worker_invoked"] is True
    for field in ("provider_invoked", "execution_started", "command_executed", "result_created", "repository_mutated"):
        assert runtime[field] is False
    assert not list(session_root.rglob("000_execution_started.json"))
    assert not list(session_root.glob("WORKER-RESULT-*"))

    aicli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    invocation_source = inspect.getsource(invoke_dispatched_worker)
    assert aicli_source.count("worker_invocation.invoke_dispatched_worker(") == 1
    for forbidden in (
        "bridge_worker_invocation_to_execution_candidate",
        "start_execution(",
        "capture_worker_result(",
        "subprocess",
    ):
        assert forbidden not in invocation_source
        assert forbidden not in aicli_source
    assert "import requests" not in invocation_source
    assert "import requests" not in aicli_source
    for duplicate in ("def _verify_hash", "def _relative_path", "def _unique_relative_paths"):
        assert duplicate not in aicli_source
