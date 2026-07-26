from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime import (
    filesystem_replace_worker_selection_lineage_resolver_runtime
    as filesystem_lineage,
)
from aigol.runtime import worker_assignment_runtime as assignment
from aigol.runtime import worker_invocation_request_runtime as invocation_request
from aigol.runtime.transport.serialization import replay_hash
from test_g31_12b_g31_selection_to_g24_worker_assignment_binding import (
    _request_and_assignment,
)
from test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection import (
    _select,
)
from test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility import (
    CREATED,
)
from aigol.runtime import human_interface_runtime_entry_service as entry


def _projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[dict, Path]:
    selection, request, _, consumption, _, _, _ = _select(
        tmp_path,
        monkeypatch,
        name,
    )
    replay_dir = Path(request["session_root"]) / f"{name}-WORKER-REQUEST"
    projection = (
        filesystem_lineage
        .resolve_authenticated_replacement_worker_selection_lineage(
            authenticated_request=request,
            consumption_reconstruction=consumption,
            resource_selection_capture=selection,
            worker_selection_certification_reference=str(
                entry.existing_file_governance.R08B_CERTIFICATION_PATH
            ),
            anchor=replay_dir,
        )
    )
    return projection, replay_dir


def _rehash(projection: dict) -> dict:
    changed = deepcopy(projection)
    changed.pop("artifact_hash", None)
    changed["artifact_hash"] = replay_hash(changed)
    return changed


def test_filesystem_resolver_is_supplied_once_and_generic_replay_reconstructs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    projection, replay_dir = _projection(tmp_path, monkeypatch, "R21C-EXACT")
    calls = 0

    def resolve() -> dict:
        nonlocal calls
        calls += 1
        return deepcopy(projection)

    capture = invocation_request.create_worker_invocation_request_from_selection_lineage(
        invocation_request_id="R21C-EXACT:INVOCATION-REQUEST",
        worker_selection_lineage_resolver=resolve,
        requested_by="G31_R21C_TEST",
        requested_at=CREATED,
        replay_dir=replay_dir,
    )
    reconstructed = invocation_request.reconstruct_worker_invocation_request_replay(
        replay_dir
    )

    assert calls == 1
    assert capture["request_status"] == (
        invocation_request.WORKER_INVOCATION_REQUEST_CREATED
    )
    assert projection["artifact_type"] == (
        invocation_request.WORKER_SELECTION_LINEAGE_PROJECTION_V1
    )
    assert capture["worker_invocation_request_artifact"][
        "compatibility_lineage"
    ] == projection
    assert reconstructed["complete_worker_selection_lineage_reconstructed"] is True
    assert reconstructed["replay_artifact_count"] == 4


@pytest.mark.parametrize(
    "mode",
    ("unsupported", "substituted", "cross_session"),
)
def test_invalid_projection_fails_before_invocation_request_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    projection, replay_dir = _projection(
        tmp_path,
        monkeypatch,
        f"R21C-{mode}",
    )
    if mode == "unsupported":
        projection["artifact_type"] = "UNSUPPORTED_SELECTION_LINEAGE"
    elif mode == "substituted":
        projection["selection_artifact_hash"] = "sha256:" + "0" * 64
    else:
        projection["session_root"] = str(tmp_path / "OTHER-SESSION")
    projection = _rehash(projection)

    capture = invocation_request.create_worker_invocation_request_from_selection_lineage(
        invocation_request_id=f"R21C-{mode}:INVOCATION-REQUEST",
        worker_selection_lineage_resolver=lambda: projection,
        requested_by="G31_R21C_TEST",
        requested_at=CREATED,
        replay_dir=replay_dir,
    )

    assert capture["request_status"] == invocation_request.FAILED_CLOSED
    assert capture["worker_invocation_request_artifact"] is None
    assert not (replay_dir / "000_invocation_request_evidence_recorded.json").exists()
    assert not (
        replay_dir / "001_invocation_request_classification_recorded.json"
    ).exists()
    assert not (
        replay_dir / "002_invocation_request_artifact_recorded.json"
    ).exists()


def test_neutral_projection_preserves_assignment_replay_format(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    projection, request_replay = _projection(
        tmp_path,
        monkeypatch,
        "R21C-ASSIGNMENT",
    )
    request = invocation_request.create_worker_invocation_request_from_selection_lineage(
        invocation_request_id="R21C-ASSIGNMENT:INVOCATION-REQUEST",
        worker_selection_lineage_resolver=lambda: projection,
        requested_by="G31_R21C_TEST",
        requested_at=CREATED,
        replay_dir=request_replay,
    )
    artifact = request["worker_invocation_request_artifact"]
    assignment_replay = request_replay.parent / "R21C-ASSIGNMENT-REPLAY"
    capture = assignment.assign_worker_from_invocation_request(
        worker_assignment_id="R21C-ASSIGNMENT",
        worker_invocation_request_artifact=artifact,
        worker_invocation_request_replay_reference=str(request_replay),
        worker_registry_artifacts=assignment.default_worker_registry_for_request(
            artifact,
            created_at=CREATED,
        ),
        assigned_by="G31_R21C_TEST",
        assigned_at=CREATED,
        replay_dir=assignment_replay,
    )

    assert capture["assignment_status"] == assignment.WORKER_ASSIGNED
    assert sorted(path.name for path in assignment_replay.glob("*.json")) == [
        f"{index:03d}_{step}.json"
        for index, step in enumerate(assignment.REPLAY_STEPS)
    ]


def test_historical_generic_default_and_assignment_remain_unchanged(
    tmp_path: Path,
) -> None:
    request, capture, _, _ = _request_and_assignment(
        tmp_path,
        "R21C-GENERIC-DEFAULT",
    )

    assert request["request_status"] == (
        invocation_request.WORKER_INVOCATION_REQUEST_CREATED
    )
    assert request["worker_invocation_request_artifact"].get(
        "compatibility_lineage"
    ) is None
    assert capture["assignment_status"] == assignment.WORKER_ASSIGNED


def test_generic_owners_contain_no_filesystem_lineage_or_routing_state() -> None:
    invocation_source = Path(
        "aigol/runtime/worker_invocation_request_runtime.py"
    ).read_text(encoding="utf-8")
    assignment_source = Path(
        "aigol/runtime/worker_assignment_runtime.py"
    ).read_text(encoding="utf-8")
    combined = f"{invocation_source}\n{assignment_source}".lower()

    assert "filesystem_replace_worker" not in combined
    assert "authenticated_replacement_selection_lineage" not in combined
    assert "consumed_replacement_selection_context" not in combined
    assert "registry = {}" not in combined
    assert "contextvar" not in combined
    assert "contextmanager" not in combined
    assert "routing_state" not in combined
