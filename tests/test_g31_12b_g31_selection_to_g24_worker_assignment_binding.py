from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    FAILED_CLOSED,
    WORKER_INVOCATION_REQUEST_CREATED,
    create_worker_invocation_request,
    reconstruct_worker_invocation_request_replay,
)
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT, REQUEST, _workspace
from test_g31_11b_authorized_existing_worker_selection_binding import _selected


def _request_and_assignment(
    tmp_path: Path, session: str = "G31-12B", *, assign: bool = True
) -> tuple[dict, dict, dict, Path]:
    selection, authorization, _, root = _selected(tmp_path, session)
    request = create_worker_invocation_request(
        invocation_request_id=f"{session}:REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        resource_selection_replay_reference=selection[
            "resource_selection_replay_reference"
        ],
        requested_by="G31_12B_TEST",
        requested_at=CREATED_AT,
        replay_dir=root / "worker-request",
    )
    request_artifact = request["worker_invocation_request_artifact"]
    assignment = {}
    if assign:
        assignment = assign_worker_from_invocation_request(
            worker_assignment_id=f"{session}:ASSIGNMENT",
            worker_invocation_request_artifact=request_artifact,
            worker_invocation_request_replay_reference=request[
                "worker_invocation_request_replay_reference"
            ],
            worker_registry_artifacts=default_worker_registry_for_request(
                request_artifact, created_at=CREATED_AT
            ),
            assigned_by="G31_12B_TEST",
            assigned_at=CREATED_AT,
            replay_dir=root / "worker-assignment",
        )
    return request, assignment, selection, root


def test_exact_g31_lineage_creates_existing_request_worker_and_assignment(tmp_path: Path) -> None:
    request, assignment, selection, root = _request_and_assignment(tmp_path)
    request_artifact = request["worker_invocation_request_artifact"]
    worker = default_worker_registry_for_request(request_artifact, created_at=CREATED_AT)[0]
    request_replay = reconstruct_worker_invocation_request_replay(root / "worker-request")
    assignment_replay = reconstruct_worker_assignment_runtime_replay(root / "worker-assignment")

    assert request["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    scope = request_artifact["g31_lineage"]["authorization_scope"]
    assert scope["scope_hash"] == request_artifact["chain_id"]
    assert scope["repository_targets"] == request_artifact["allowed_outputs"]
    assert scope["validation_requirements"] == request_artifact["validation_requirements"]
    assert selection["resource_selection_artifact"]["context_hash"] == request_artifact["authorization_hash"]
    assert request_artifact["g31_lineage"]["resource_selection_artifact"]["artifact_hash"] == selection[
        "resource_selection_artifact"
    ]["artifact_hash"]
    assert request_replay["complete_g31_lineage_reconstructed"] is True
    assert worker["worker_id"] == "CODEX"
    assert worker["selected_resource_category"] == "HYBRID_PROVIDER_WORKER"
    assert worker["selected_role_type"] == "WORKER_ROLE"
    assert worker["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY"
    assert worker["provider_authority"] is False
    assert assignment["assignment_status"] == WORKER_ASSIGNED
    assert assignment["worker_id"] == "CODEX"
    assert assignment_replay["worker_id"] == "CODEX"
    for field in ("worker_dispatched", "worker_invoked", "execution_started", "governance_mutated"):
        assert assignment[field] is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("selected_resource_id", "OTHER"),
        ("selected_resource_category", "PROVIDER"),
        ("selected_role_type", "PROVIDER_ROLE"),
        ("selected_authority_profile", "PROVIDER_PROPOSAL_ONLY"),
        ("registry_hash", "sha256:" + "1" * 64),
    ),
)
def test_selection_identity_role_registry_and_provider_substitution_fail_before_request(
    tmp_path: Path, field: str, value: str
) -> None:
    selection, authorization, _, root = _selected(tmp_path, f"TAMPER-{field}")
    replay = Path(selection["resource_selection_replay_reference"])
    recorded = load_json(replay / "000_resource_selection_recorded.json")
    recorded["artifact"][field] = value
    recorded["artifact"] = with_replay_hash(recorded["artifact"], hash_field="artifact_hash")
    (replay / "000_resource_selection_recorded.json").write_text(
        json.dumps(with_replay_hash(recorded, hash_field="replay_hash")), encoding="utf-8"
    )
    capture = create_worker_invocation_request(
        invocation_request_id=f"TAMPER-{field}:REQUEST",
        execution_authorization_replay_reference=authorization[
            "execution_authorization_replay_reference"
        ],
        resource_selection_replay_reference=str(replay),
        requested_by="G31_12B_TEST",
        requested_at=CREATED_AT,
        replay_dir=root / "failed-request",
    )
    assert capture["request_status"] == FAILED_CLOSED
    assert capture["worker_invocation_request_artifact"] is None
    assert not (root / "failed-request" / "002_invocation_request_artifact_recorded.json").exists()


@pytest.mark.parametrize("mode", ("UNAVAILABLE", "INCOMPATIBLE", "PROVIDER_AUTHORITY"))
def test_unavailable_incompatible_or_provider_authority_worker_fails_before_assignment(
    tmp_path: Path, mode: str
) -> None:
    request, _, _, root = _request_and_assignment(tmp_path, f"WORKER-{mode}", assign=False)
    artifact = request["worker_invocation_request_artifact"]
    worker = default_worker_registry_for_request(artifact, created_at=CREATED_AT)[0]
    if mode == "UNAVAILABLE":
        worker["state"] = "UNAVAILABLE"
    elif mode == "INCOMPATIBLE":
        worker["worker_roles"] = ["OTHER_ROLE"]
    else:
        worker["provider_authority"] = True
    worker.pop("artifact_hash")
    worker["artifact_hash"] = replay_hash(worker)
    capture = assign_worker_from_invocation_request(
        worker_assignment_id=f"FAILED-{mode}",
        worker_invocation_request_artifact=artifact,
        worker_invocation_request_replay_reference=request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=[worker],
        assigned_by="G31_12B_TEST",
        assigned_at=CREATED_AT,
        replay_dir=root / f"failed-{mode}",
    )
    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert capture["worker_assignment_artifact"] is None
    expected = {"UNAVAILABLE": "unavailable", "INCOMPATIBLE": "role mismatch", "PROVIDER_AUTHORITY": "authority violation"}
    assert expected[mode] in capture["failure_reason"]


@pytest.mark.parametrize("mode", ("SCOPE", "CERTIFICATION"))
def test_grounded_scope_or_certification_substitution_fails_against_request_replay(
    tmp_path: Path, mode: str
) -> None:
    request, _, _, root = _request_and_assignment(tmp_path, f"REQUEST-{mode}", assign=False)
    artifact = deepcopy(request["worker_invocation_request_artifact"])
    if mode == "SCOPE":
        artifact["g31_lineage"]["authorization_scope"]["source_paths"].append("broadened.py")
    else:
        artifact["g31_lineage"]["worker_selection_certification_hash"] = "sha256:" + "2" * 64
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = assign_worker_from_invocation_request(
        worker_assignment_id=f"FAILED-{mode}", worker_invocation_request_artifact=artifact,
        worker_invocation_request_replay_reference=request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=[], assigned_by="G31_12B_TEST", assigned_at=CREATED_AT,
        replay_dir=root / f"failed-{mode}",
    )
    assert capture["assignment_status"] == "FAILED_CLOSED"
    assert "request" in capture["failure_reason"] and "mismatch" in capture["failure_reason"]


def test_replayed_assignment_and_reordered_nested_replay_fail_closed(tmp_path: Path) -> None:
    request, _, _, root = _request_and_assignment(tmp_path, "REPLAY")
    artifact = request["worker_invocation_request_artifact"]
    repeated = assign_worker_from_invocation_request(
        worker_assignment_id="REPLAY:ASSIGNMENT",
        worker_invocation_request_artifact=artifact,
        worker_invocation_request_replay_reference=request[
            "worker_invocation_request_replay_reference"
        ],
        worker_registry_artifacts=default_worker_registry_for_request(artifact, created_at=CREATED_AT),
        assigned_by="G31_12B_TEST",
        assigned_at=CREATED_AT,
        replay_dir=root / "worker-assignment",
    )
    assert repeated["assignment_status"] == "FAILED_CLOSED"
    path = root / "worker-request" / "001_invocation_request_classification_recorded.json"
    wrapper = load_json(path)
    wrapper["replay_index"] = 2
    path.write_text(json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_worker_assignment_runtime_replay(root / "worker-assignment")


def test_real_aicli_preserves_assignment_stage_before_later_dispatch(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, "g31-12b-aicli")
    output: list[str] = []
    values = iter([REQUEST, "/send", "/approve", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-12B-AICLI", created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime", workspace=workspace,
        input_reader=lambda _prompt: next(values), output_writer=output.append,
    )
    runtime = result["runtime_result"]
    assert runtime["selected_resource_id"] == "CODEX"
    assert runtime["worker_assigned"] is True
    assert runtime["worker_dispatched"] is True
    assert runtime["worker_assignment_capture"]["worker_dispatched"] is False
    assert runtime["worker_invoked"] is True
    assert runtime["worker_assignment_capture"]["worker_invoked"] is False
    for field in ("provider_invoked", "command_executed", "repository_mutated"):
        assert runtime[field] is False
    rendered = "\n".join(output)
    assert "Worker Invocation Request" in rendered
    assert "No Worker has been assigned, dispatched, invoked, or executed." in rendered
    assert "Worker Assignment" in rendered
    assert "Assigned Worker: CODEX" in rendered
    assert "No Worker has been dispatched, invoked, or executed." in rendered


def test_production_change_has_no_new_module_or_duplicate_helpers() -> None:
    sources = [
        Path("aigol/runtime/worker_invocation_request_runtime.py").read_text(encoding="utf-8"),
        Path("aigol/runtime/worker_assignment_runtime.py").read_text(encoding="utf-8"),
        Path("aigol/runtime/human_interface_runtime_entry_service.py").read_text(encoding="utf-8"),
    ]
    assert "def _load_g31_selection_binding" in sources[0]
    for duplicate in ("def _verify_hash", "def _relative_path", "def _unique_relative_paths"):
        assert all(duplicate not in source for source in sources)
    assert "worker_dispatch.dispatch_assigned_worker" in sources[2]
