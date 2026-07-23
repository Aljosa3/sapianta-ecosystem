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
    ACTOR,
    CREATED,
    InMemoryAdapter,
    _pending_state,
)
from test_g31_24g_r04_r04_r08c_consumed_request_certified_worker_selection import (
    CAPABILITY,
    WORKER_ID,
    WORKER_VERSION,
)


def _forbid_later_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (entry.worker_dispatch, "dispatch_assigned_worker"),
        (entry.worker_invocation, "invoke_dispatched_worker"),
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
            raise AssertionError(f"forbidden R12B downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, reject)
    return calls


def test_common_entry_assigns_exact_certified_worker_and_reconstructs_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R12B-COMMON")
    forbidden = _forbid_later_lifecycle(monkeypatch)
    calls = {"projection": 0, "assignment": 0, "reconstruction": 0}
    projected: list[dict] = []
    original_projection = entry.worker_assignment.default_worker_registry_for_request
    original_assignment = entry.worker_assignment.assign_worker_from_invocation_request
    original_reconstruction = (
        entry.worker_assignment.reconstruct_worker_assignment_runtime_replay
    )

    def project(*args, **kwargs):
        calls["projection"] += 1
        workers = original_projection(*args, **kwargs)
        projected.extend(deepcopy(workers))
        return workers

    def assign(*args, **kwargs):
        calls["assignment"] += 1
        return original_assignment(*args, **kwargs)

    def reconstruct(*args, **kwargs):
        calls["reconstruction"] += 1
        return original_reconstruction(*args, **kwargs)

    monkeypatch.setattr(
        entry.worker_assignment, "default_worker_registry_for_request", project
    )
    monkeypatch.setattr(
        entry.worker_assignment, "assign_worker_from_invocation_request", assign
    )
    monkeypatch.setattr(
        entry.worker_assignment,
        "reconstruct_worker_assignment_runtime_replay",
        reconstruct,
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    selection = result["consumed_replacement_worker_selection_capture"]
    request = result["worker_invocation_request_capture"][
        "worker_invocation_request_artifact"
    ]
    assignment = result["worker_assignment_capture"]
    artifact = assignment["worker_assignment_artifact"]
    reconstruction = result["worker_assignment_reconstruction"]
    worker = projected[0]

    assert calls == {"projection": 1, "assignment": 1, "reconstruction": 1}
    assert all(count == 0 for count in forbidden.values())
    assert result["g31_application_sequenced_by_common_entry"] is True
    assert result["worker_assigned"] is True
    assert result["worker_assignment_status"] == entry.worker_assignment.WORKER_ASSIGNED
    assert result["assigned_worker_id"] == WORKER_ID
    assert assignment["worker_id"] == WORKER_ID
    assert artifact["worker_id"] == WORKER_ID
    assert artifact["worker_invocation_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert artifact["worker_invocation_request_hash"] == request["artifact_hash"]
    assert artifact["canonical_chain_id"] == request["chain_id"]
    assert artifact["worker_hash"] == worker["artifact_hash"]
    assert worker["worker_version"] == WORKER_VERSION
    assert worker["capability_id"] == CAPABILITY
    assert worker["selection_artifact_hash"] == selection[
        "resource_selection_artifact"
    ]["artifact_hash"]
    assert reconstruction["worker_assignment_id"] == artifact["worker_assignment_id"]
    assert reconstruction["worker_id"] == WORKER_ID
    assert reconstruction["worker_invocation_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert reconstruction["canonical_chain_id"] == request["chain_id"]
    assert result["worker_assignment_replay_hash"] == reconstruction["replay_hash"]
    assert result["runtime_replay_reference"] == result[
        "worker_assignment_replay_reference"
    ]
    assert sorted(
        path.name
        for path in Path(result["worker_assignment_replay_reference"]).glob("*.json")
    ) == [
        "000_assignment_evidence_recorded.json",
        "001_assignment_classification_recorded.json",
        "002_assignment_artifact_recorded.json",
        "003_assignment_result_recorded.json",
    ]
    for field in (
        "worker_dispatched",
        "provider_invoked",
        "worker_invoked",
        "execution_started",
        "execution_requested",
        "command_executed",
        "repository_mutated",
        "main_repository_mutated",
        "governance_mutated",
        "replay_mutated",
    ):
        assert result.get(field) is False
    assert selection["worker_assigned"] is False
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Assignment Reached: True" in rendered
    assert f"Assigned Worker: {WORKER_ID}" in rendered
    assert "No Worker has been dispatched, invoked, or executed." in rendered


@pytest.mark.parametrize("mode", ("registry", "reconstruction"))
def test_invalid_registry_or_assignment_reconstruction_fails_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R12B-{mode}")
    forbidden = _forbid_later_lifecycle(monkeypatch)
    if mode == "registry":
        monkeypatch.setattr(
            entry.worker_assignment,
            "default_worker_registry_for_request",
            lambda *_args, **_kwargs: [],
        )
    else:
        original = entry.worker_assignment.reconstruct_worker_assignment_runtime_replay

        def changed(*args, **kwargs):
            reconstructed = original(*args, **kwargs)
            return {**reconstructed, "worker_dispatched": True}

        monkeypatch.setattr(
            entry.worker_assignment,
            "reconstruct_worker_assignment_runtime_replay",
            changed,
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Worker assignment failed|Worker assignment Replay mismatch",
    ):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    assert all(count == 0 for count in forbidden.values())
    assignment_roots = list(root.glob("WORKER-ASSIGNMENT-*"))
    assert len(assignment_roots) == 1
    if mode == "registry":
        assert not (assignment_roots[0] / "002_assignment_artifact_recorded.json").exists()
    else:
        assert (assignment_roots[0] / "002_assignment_artifact_recorded.json").is_file()


def test_aicli_receives_common_entry_assignment_without_assignment_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    memory_root, memory_state = _pending_state(
        tmp_path, monkeypatch, "R12B-MEMORY"
    )
    memory = InMemoryAdapter(memory_root).transport(
        memory_state, decision.MUTATION_APPROVED
    )
    cli_root, cli_state = _pending_state(tmp_path, monkeypatch, "R12B-AICLI")
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
        assert result["worker_assignment_status"] == entry.worker_assignment.WORKER_ASSIGNED
        assert result["assigned_worker_id"] == WORKER_ID
        assert result["worker_assigned"] is True
        assert result["worker_dispatched"] is False
        assert result["worker_invoked"] is False
        assert result["provider_invoked"] is False
        assert result["repository_mutated"] is False
    assert memory["g31_application_interface_transport"] == "in_memory_test_adapter"
    assert cli["g31_application_interface_transport"] == "aicli"
    cli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    assert "assign_worker_from_invocation_request(" not in cli_source
    assert "default_worker_registry_for_request(" not in cli_source
    assert "run_human_interface_runtime_entry(" in cli_source


def test_common_entry_binding_is_worker_neutral_and_stops_before_dispatch() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)

    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "CODEX" not in source
    assert source.count("default_worker_registry_for_request(") == 1
    assert source.count("assign_worker_from_invocation_request(") == 1
    assert source.count("reconstruct_worker_assignment_runtime_replay(") == 1
    assert "dispatch_assigned_worker(" not in source
    assert "invoke_dispatched_worker(" not in source
    assert "execute_governed_worker(" not in source
    assert "execute_g31_authenticated_replace(" not in source
