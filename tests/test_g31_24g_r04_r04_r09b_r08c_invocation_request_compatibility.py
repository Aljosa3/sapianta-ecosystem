from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime import worker_invocation_request_runtime as invocation_request
from aigol.runtime.human_decision_runtime import MUTATION_APPROVED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)
from test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection import (
    CAPABILITY,
    WORKER_ID,
    _select,
)


CREATED = "2026-07-22T00:00:00+00:00"


def _request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str = "R09B"):
    selection, request, _, consumption, _, target, _ = _select(
        tmp_path, monkeypatch, name
    )
    replay_dir = Path(request["session_root"]) / f"{name}-WORKER-REQUEST"
    capture = invocation_request.create_authenticated_replacement_worker_invocation_request(
        invocation_request_id=f"{name}:INVOCATION-REQUEST",
        authenticated_request=request,
        consumption_reconstruction=consumption,
        resource_selection_capture=selection,
        worker_selection_certification_reference=str(
            entry.existing_file_governance.R08B_CERTIFICATION_PATH
        ),
        requested_by="G31_R09B_TEST",
        requested_at=CREATED,
        replay_dir=replay_dir,
    )
    return capture, selection, request, consumption, target, replay_dir


def test_exact_r08c_lineage_creates_existing_invocation_request_and_reconstructs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    capture, selection, request, consumption, target, replay_dir = _request(
        tmp_path, monkeypatch
    )
    artifact = capture["worker_invocation_request_artifact"]
    compatibility = artifact["compatibility_lineage"]
    reconstructed = invocation_request.reconstruct_worker_invocation_request_replay(
        replay_dir
    )

    assert capture["request_status"] == invocation_request.WORKER_INVOCATION_REQUEST_CREATED
    assert artifact["artifact_type"] == invocation_request.WORKER_INVOCATION_REQUEST_ARTIFACT_V1
    assert artifact["authorization_reference"] == request["authorization_id"]
    assert artifact["authorization_hash"] == request["authorization_hash"]
    assert artifact["execution_packet_reference"] == request["request_id"]
    assert artifact["execution_packet_hash"] == request["request_hash"]
    assert artifact["target_worker_family"] == WORKER_ID
    assert artifact["worker_role"] == "WORKER_ROLE"
    assert artifact["allowed_outputs"] == [request["target_path"]]
    assert compatibility["lineage_type"] == (
        invocation_request.AUTHENTICATED_REPLACEMENT_SELECTION_LINEAGE_V1
    )
    assert compatibility["authenticated_request"] == request
    assert compatibility["consumption_reconstruction"] == consumption
    assert compatibility["resource_selection_capture"][
        "resource_selection_artifact"
    ] == selection["resource_selection_artifact"]
    assert compatibility["worker_selection_certification_hash"] == (
        entry.existing_file_governance.R08B_CERTIFICATION_HASH
    )
    assert reconstructed["complete_authenticated_replacement_lineage_reconstructed"] is True
    assert reconstructed["request_hash"] == artifact["request_hash"]
    assert reconstructed["target_worker_family"] == WORKER_ID
    for field in (
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "execution_started",
        "governance_mutated",
    ):
        assert capture[field] is False
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


def test_common_entry_preserves_request_through_invocation_and_stops_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R09B-COMMON")
    calls: dict[str, int] = {}
    forbidden = (
        (entry.existing_file_governance, "execute_g31_authenticated_replace"),
        (entry.filesystem_replace_worker, "execute_filesystem_replace_request"),
        (entry.filesystem_replace_worker, "_open_v2_target"),
    )
    for owner, symbol in forbidden:
        calls[symbol] = 0

        def reject(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden R09B downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, reject)

    result = InMemoryAdapter(root).transport(state, MUTATION_APPROVED)
    request = result["worker_invocation_request_capture"]
    artifact = request["worker_invocation_request_artifact"]

    assert result["g31_application_sequenced_by_common_entry"] is True
    assert result["worker_selected"] is True
    assert result["worker_invocation_request_created"] is True
    assert result["worker_invocation_request_status"] == (
        invocation_request.WORKER_INVOCATION_REQUEST_CREATED
    )
    assert artifact["target_worker_family"] == result["selected_resource_id"] == WORKER_ID
    assert artifact["execution_packet_hash"] == result[
        "authenticated_replacement_request_hash"
    ]
    assert result["authorization_consumption_identity"] == artifact[
        "compatibility_lineage"
    ]["consumption_reconstruction"]["consumption_identity"]
    assert result["worker_assigned"] is True
    assert result["worker_dispatched"] is True
    assert result["worker_invoked"] is True
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert result["repository_mutated"] is False
    assert all(count == 0 for count in calls.values())
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Invocation Request Created: True" in rendered
    assert "Worker Assignment Reached: True" in rendered
    assert "Worker Dispatch Reached: True" in rendered
    assert "Worker Invocation Reached: True" in rendered
    assert "No Worker has been assigned, dispatched, invoked, or executed." in rendered
    assert f"Dispatched Worker: {WORKER_ID}" in rendered
    assert "No Worker has been invoked, executed, or produced results." in rendered
    assert f"Invoked Worker: {WORKER_ID}" in rendered
    assert "No Worker process or execution has started." in rendered


@pytest.mark.parametrize(
    "mode",
    (
        "request",
        "consumption",
        "selection",
        "context",
        "certification",
        "cross_session",
    ),
)
def test_changed_lineage_fails_before_request_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    selection, request, _, consumption, _, _, _ = _select(
        tmp_path, monkeypatch, f"R09B-{mode}"
    )
    certification = str(entry.existing_file_governance.R08B_CERTIFICATION_PATH)
    if mode == "request":
        request = deepcopy(request)
        request["worker_operation"] = "BROADER_OPERATION"
        request["request_hash"] = replay_hash(
            {key: value for key, value in request.items() if key != "request_hash"}
        )
    elif mode == "consumption":
        consumption = {**deepcopy(consumption), "consumption_identity": "SUBSTITUTED"}
    elif mode == "selection":
        selection = deepcopy(selection)
        selection["resource_selection_artifact"]["selected_resource_id"] = "OTHER"
    elif mode == "context":
        selection = deepcopy(selection)
        selection["consumed_replacement_selection_context"]["terminal_prompt"] = "assign"
        selection["consumed_replacement_selection_context_hash"] = replay_hash(
            selection["consumed_replacement_selection_context"]
        )
    elif mode == "certification":
        certification = str(tmp_path / "missing-certification.json")
    else:
        selection = deepcopy(selection)
        selection["resource_selection_replay_reference"] = str(
            tmp_path / "different-session" / "selection"
        )
    replay_dir = Path(request["session_root"]) / f"FAILED-{mode}"
    capture = invocation_request.create_authenticated_replacement_worker_invocation_request(
        invocation_request_id=f"FAILED-{mode}",
        authenticated_request=request,
        consumption_reconstruction=consumption,
        resource_selection_capture=selection,
        worker_selection_certification_reference=certification,
        requested_by="G31_R09B_TEST",
        requested_at=CREATED,
        replay_dir=replay_dir,
    )
    assert capture["request_status"] == invocation_request.FAILED_CLOSED
    assert capture["worker_invocation_request_artifact"] is None
    assert not (replay_dir / "002_invocation_request_artifact_recorded.json").exists()


@pytest.mark.parametrize("mode", ("removed", "duplicated", "reordered", "substituted"))
def test_invocation_request_replay_tamper_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    _, _, _, _, _, replay_dir = _request(tmp_path, monkeypatch, f"R09B-{mode}")
    evidence = replay_dir / "000_invocation_request_evidence_recorded.json"
    classification = replay_dir / "001_invocation_request_classification_recorded.json"
    if mode == "removed":
        classification.unlink()
    elif mode == "duplicated":
        (replay_dir / "004_duplicate.json").write_bytes(evidence.read_bytes())
    elif mode == "reordered":
        wrapper = load_json(classification)
        wrapper["replay_index"] = 2
        classification.write_text(
            json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")),
            encoding="utf-8",
        )
    else:
        wrapper = load_json(evidence)
        wrapper["artifact"]["authorization_hash"] = "sha256:" + "0" * 64
        evidence.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        invocation_request.reconstruct_worker_invocation_request_replay(replay_dir)


def test_compatibility_owner_has_no_worker_identity_branch_or_assignment_call() -> None:
    source = "\n".join(
        inspect.getsource(symbol)
        for symbol in (
            invocation_request.create_authenticated_replacement_worker_invocation_request,
            invocation_request._load_authenticated_replacement_selection_lineage,
            invocation_request._project_authenticated_replacement_lineage,
        )
    )
    assert WORKER_ID not in source
    assert CAPABILITY not in source
    assert "assign_worker_from_invocation_request" not in source
    assert "dispatch_assigned_worker" not in source
    assert "invoke_dispatched_worker" not in source
    cli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    assert "create_authenticated_replacement_worker_invocation_request(" not in cli_source
    assert "run_human_interface_runtime_entry(" in cli_source
