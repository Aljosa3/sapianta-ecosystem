from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    CREATED,
    InMemoryAdapter,
    _pending_state,
)
from test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection import (
    WORKER_ID,
)


def _forbid_post_dispatch_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (entry.governed_execution, "run_governed_worker_execution"),
        (entry.existing_file_governance, "execute_g31_authenticated_replace"),
        (entry.existing_file_governance, "recover_g31_authenticated_replace"),
        (entry.filesystem_replace_worker, "execute_filesystem_replace_request"),
        (entry.filesystem_replace_worker, "_execute_authenticated_replace_v2"),
        (entry.filesystem_replace_worker, "_recover_authenticated_replace_v2"),
        (entry.filesystem_replace_worker, "_open_v2_target"),
        (entry.filesystem_replace_worker, "_atomic_restore_v2"),
    )
    for owner, symbol in targets:
        calls[symbol] = 0

        def reject(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden R13B downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, reject)
    return calls


def test_common_entry_dispatches_exact_assignment_and_reconstructs_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R13B-COMMON")
    forbidden = _forbid_post_dispatch_lifecycle(monkeypatch)
    calls = {"dispatch": 0, "reconstruction": 0}
    original_dispatch = entry.worker_dispatch.dispatch_assigned_worker
    original_reconstruction = entry.worker_dispatch.reconstruct_worker_dispatch_replay

    def dispatch(*args, **kwargs):
        calls["dispatch"] += 1
        return original_dispatch(*args, **kwargs)

    def reconstruct(*args, **kwargs):
        calls["reconstruction"] += 1
        return original_reconstruction(*args, **kwargs)

    monkeypatch.setattr(entry.worker_dispatch, "dispatch_assigned_worker", dispatch)
    monkeypatch.setattr(
        entry.worker_dispatch, "reconstruct_worker_dispatch_replay", reconstruct
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["worker_invocation_request_capture"][
        "worker_invocation_request_artifact"
    ]
    assignment = result["worker_assignment_capture"]
    assignment_artifact = assignment["worker_assignment_artifact"]
    dispatch_capture = result["worker_dispatch_capture"]
    dispatch_artifact = dispatch_capture["worker_dispatch_artifact"]
    reconstruction = result["worker_dispatch_reconstruction"]

    assert calls == {"dispatch": 1, "reconstruction": 1}
    assert all(count == 0 for count in forbidden.values())
    assert result["g31_application_sequenced_by_common_entry"] is True
    assert result["worker_assigned"] is True
    assert result["worker_dispatched"] is True
    assert result["dispatch_requested"] is True
    assert result["worker_dispatch_status"] == entry.worker_dispatch.WORKER_DISPATCHED
    assert result["worker_invoked"] is True
    assert result["provider_invoked"] is False
    assert result["execution_started"] is True
    assert result["execution_requested"] is True
    assert result["result_created"] is False
    assert result["repository_mutated"] is False
    assert dispatch_capture["worker_id"] == WORKER_ID
    assert dispatch_artifact["worker_assignment_reference"] == assignment_artifact[
        "worker_assignment_id"
    ]
    assert dispatch_artifact["worker_assignment_hash"] == assignment_artifact[
        "artifact_hash"
    ]
    assert dispatch_artifact["worker_invocation_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert dispatch_artifact["chain_id"] == request["chain_id"]
    assert dispatch_artifact["worker_invoked"] is False
    assert dispatch_artifact["execution_started"] is False
    assert reconstruction["worker_dispatch_id"] == dispatch_artifact[
        "worker_dispatch_id"
    ]
    assert reconstruction["worker_assignment_reference"] == assignment_artifact[
        "worker_assignment_id"
    ]
    assert reconstruction["worker_id"] == WORKER_ID
    assert reconstruction["worker_invoked"] is False
    assert reconstruction["execution_started"] is False
    assert result["worker_dispatch_replay_hash"] == reconstruction["replay_hash"]
    assert result["runtime_replay_reference"] == result[
        "worker_execution_replay_reference"
    ]
    assert sorted(
        path.name
        for path in Path(result["worker_dispatch_replay_reference"]).glob("*.json")
    ) == [
        "000_dispatch_evidence_recorded.json",
        "001_dispatch_classification_recorded.json",
        "002_dispatch_artifact_recorded.json",
        "003_dispatch_result_recorded.json",
    ]
    assert len(list(root.glob("WORKER-INVOCATION-*"))) == 1
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Dispatch Reached: True" in rendered
    assert "Worker Invocation Reached: True" in rendered
    assert "Dispatch Status: WORKER_DISPATCHED" in rendered
    assert f"Dispatched Worker: {WORKER_ID}" in rendered
    assert "No Worker has been invoked, executed, or produced results." in rendered


@pytest.mark.parametrize("mode", ("dispatch", "reconstruction"))
def test_invalid_dispatch_or_reconstruction_fails_before_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R13B-{mode}")
    forbidden = _forbid_post_dispatch_lifecycle(monkeypatch)
    if mode == "dispatch":
        monkeypatch.setattr(
            entry.worker_dispatch,
            "dispatch_assigned_worker",
            lambda **_kwargs: {"dispatch_status": "FAILED_CLOSED"},
        )
    else:
        original = entry.worker_dispatch.reconstruct_worker_dispatch_replay

        def changed(*args, **kwargs):
            reconstructed = original(*args, **kwargs)
            return {**reconstructed, "worker_invoked": True}

        monkeypatch.setattr(
            entry.worker_dispatch, "reconstruct_worker_dispatch_replay", changed
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Worker dispatch failed|Worker dispatch Replay mismatch",
    ):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    assert all(count == 0 for count in forbidden.values())
    assert list(root.glob("WORKER-INVOCATION-*")) == []
    dispatch_roots = list(root.glob("WORKER-DISPATCH-*"))
    if mode == "dispatch":
        assert dispatch_roots == []
    else:
        assert len(dispatch_roots) == 1
        assert (
            dispatch_roots[0] / "002_dispatch_artifact_recorded.json"
        ).is_file()


def test_aicli_receives_common_entry_dispatch_without_dispatch_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    memory_root, memory_state = _pending_state(
        tmp_path, monkeypatch, "R13B-MEMORY"
    )
    memory = InMemoryAdapter(memory_root).transport(
        memory_state, decision.MUTATION_APPROVED
    )
    cli_root, cli_state = _pending_state(tmp_path, monkeypatch, "R13B-AICLI")
    cli = aicli._continue_g31_application_action(
        runtime_result=cli_state,
        action=decision.MUTATION_APPROVED,
        session=cli_root.name,
        root=cli_root.parent,
        workspace_path="/isolated/repository",
        created=CREATED,
        worker_process_runner=None,
    )

    for result in (memory, cli):
        dispatch = result["worker_dispatch_capture"]
        assert result["worker_dispatch_status"] == entry.worker_dispatch.WORKER_DISPATCHED
        assert result["worker_assigned"] is True
        assert result["worker_dispatched"] is True
        assert result["worker_invoked"] is True
        assert result["provider_invoked"] is False
        assert result["repository_mutated"] is False
        assert dispatch["worker_id"] == WORKER_ID
    assert memory["g31_application_interface_transport"] == "in_memory_test_adapter"
    assert cli["g31_application_interface_transport"] == "aicli"
    cli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    assert "dispatch_assigned_worker(" not in cli_source
    assert "reconstruct_worker_dispatch_replay(" not in cli_source
    assert "run_human_interface_runtime_entry(" in cli_source


def test_common_entry_dispatch_binding_is_worker_neutral_and_stops_before_execution() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)

    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "CODEX" not in source
    assert source.count("dispatch_assigned_worker(") == 1
    assert source.count("reconstruct_worker_dispatch_replay(") == 1
    assert source.count("invoke_dispatched_worker(") == 1
    assert source.count("reconstruct_worker_invocation_replay(") == 1
    assert "run_governed_worker_execution(" not in source
    assert "execute_g31_authenticated_replace(" not in source
