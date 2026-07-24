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


CAPABILITY = "REPLACE_EXISTING_TEXT_FILE"


def _forbid_post_execution_handoff(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (entry.governed_execution, "run_governed_worker_execution"),
        (entry.codex_result, "capture_successful_codex_worker_result"),
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
            raise AssertionError(f"forbidden R15F downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, reject)
    return calls


def test_common_entry_starts_exact_execution_once_and_reconstructs_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R15F-COMMON")
    forbidden = _forbid_post_execution_handoff(monkeypatch)
    calls = {"execution": 0, "reconstruction": 0}
    supplied: dict[str, object] = {}
    original_execution = entry.execution_runtime.start_execution
    original_reconstruction = entry.execution_runtime.reconstruct_execution_replay

    def start(*args, **kwargs):
        calls["execution"] += 1
        supplied.update(deepcopy(kwargs))
        return original_execution(*args, **kwargs)

    def reconstruct(*args, **kwargs):
        calls["reconstruction"] += 1
        return original_reconstruction(*args, **kwargs)

    monkeypatch.setattr(entry.execution_runtime, "start_execution", start)
    monkeypatch.setattr(
        entry.execution_runtime, "reconstruct_execution_replay", reconstruct
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["worker_invocation_request_capture"][
        "worker_invocation_request_artifact"
    ]
    assignment = result["worker_assignment_capture"]["worker_assignment_artifact"]
    dispatch = result["worker_dispatch_capture"]["worker_dispatch_artifact"]
    invocation_capture = result["worker_invocation_capture"]
    invocation = invocation_capture["worker_invocation_artifact"]
    execution = result["worker_execution_capture"]["execution_artifact"]
    reconstruction = result["worker_execution_reconstruction"]

    assert calls == {"execution": 1, "reconstruction": 1}
    assert all(count == 0 for count in forbidden.values())
    assert supplied["invocation_artifact"] == invocation
    assert supplied["invocation_replay"] == invocation_capture[
        "invocation_result_artifact"
    ]
    assert supplied["dispatch_artifact"] == dispatch
    assert supplied["worker_assignment_artifact"] == assignment
    assert supplied["canonical_chain_id"] == request["chain_id"]
    assert supplied["started_by"] == "AIGOL"
    assert result["g31_application_sequenced_by_common_entry"] is True
    assert result["worker_execution_status"] == entry.execution_runtime.EXECUTING
    assert result["execution_started"] is True
    assert result["execution_requested"] is True
    assert result["worker_execution_performed"] is False
    assert result["provider_invoked"] is False
    assert result["result_created"] is False
    assert result["command_executed"] is False
    assert result["target_opened"] is False
    assert result["repository_mutated"] is False
    assert result["governance_mutated"] is False
    assert result["replay_mutated"] is False
    assert execution["worker_invocation_reference"] == invocation[
        "worker_invocation_id"
    ]
    assert execution["worker_invocation_hash"] == invocation["artifact_hash"]
    assert execution["worker_invocation_replay_hash"] == invocation_capture[
        "invocation_result_artifact"
    ]["artifact_hash"]
    assert execution["dispatch_reference"] == dispatch["worker_dispatch_id"]
    assert execution["dispatch_hash"] == dispatch["artifact_hash"]
    assert execution["worker_assignment_reference"] == assignment[
        "worker_assignment_id"
    ]
    assert execution["worker_assignment_hash"] == assignment["artifact_hash"]
    assert execution["execution_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert execution["readiness_reference"] == request[
        "execution_packet_reference"
    ]
    assert execution["worker_reference"] == WORKER_ID
    assert execution["canonical_chain_id"] == request["chain_id"]
    assert execution["capability_id"] == CAPABILITY
    assert execution["provider_authority"] is False
    assert execution["completion_recorded"] is False
    assert execution["result_certified"] is False
    assert reconstruction["execution_id"] == execution["execution_id"]
    assert reconstruction["worker_invocation_reference"] == invocation[
        "worker_invocation_id"
    ]
    assert reconstruction["dispatch_reference"] == dispatch[
        "worker_dispatch_id"
    ]
    assert reconstruction["worker_assignment_reference"] == assignment[
        "worker_assignment_id"
    ]
    assert reconstruction["replay_artifact_count"] == 2
    assert result["worker_execution_replay_hash"] == reconstruction["replay_hash"]
    assert result["runtime_replay_reference"] == result[
        "worker_execution_replay_reference"
    ]
    assert sorted(
        path.name
        for path in Path(result["worker_execution_replay_reference"]).glob("*.json")
    ) == [
        "000_execution_started.json",
        "001_execution_returned.json",
    ]
    assert not list(root.glob("WORKER-RESULT-*"))
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Execution Handoff Reached: True" in rendered
    assert "Execution Status: EXECUTING" in rendered
    assert "No Worker implementation has executed." in rendered
    assert "No Provider has been invoked." in rendered
    assert "No Worker result has been captured." in rendered
    assert "No repository has been modified." in rendered


@pytest.mark.parametrize("mode", ("execution", "reconstruction"))
def test_invalid_execution_or_reconstruction_fails_before_physical_worker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R15F-{mode}")
    forbidden = _forbid_post_execution_handoff(monkeypatch)
    if mode == "execution":
        monkeypatch.setattr(
            entry.execution_runtime,
            "start_execution",
            lambda **_kwargs: {
                "execution_artifact": {"execution_status": "FAILED_CLOSED"}
            },
        )
    else:
        original = entry.execution_runtime.reconstruct_execution_replay

        def changed(*args, **kwargs):
            reconstructed = original(*args, **kwargs)
            return {**reconstructed, "completion_recorded": True}

        monkeypatch.setattr(
            entry.execution_runtime, "reconstruct_execution_replay", changed
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Worker execution failed|Worker execution Replay mismatch",
    ):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    assert all(count == 0 for count in forbidden.values())
    assert not list(root.glob("WORKER-RESULT-*"))
    execution_roots = list(root.glob("WORKER-EXECUTION-*"))
    if mode == "execution":
        assert execution_roots == []
    else:
        assert len(execution_roots) == 1
        assert (execution_roots[0] / "000_execution_started.json").is_file()


def test_aicli_receives_execution_handoff_without_execution_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    memory_root, memory_state = _pending_state(
        tmp_path, monkeypatch, "R15F-MEMORY"
    )
    memory = InMemoryAdapter(memory_root).transport(
        memory_state, decision.MUTATION_APPROVED
    )
    cli_root, cli_state = _pending_state(tmp_path, monkeypatch, "R15F-AICLI")
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
        execution = result["worker_execution_capture"]["execution_artifact"]
        assert result["worker_execution_status"] == entry.execution_runtime.EXECUTING
        assert result["execution_started"] is True
        assert result["worker_execution_performed"] is False
        assert result["provider_invoked"] is False
        assert result["result_created"] is False
        assert result["repository_mutated"] is False
        assert execution["worker_reference"] == WORKER_ID
        assert execution["capability_id"] == CAPABILITY
    assert memory["g31_application_interface_transport"] == "in_memory_test_adapter"
    assert cli["g31_application_interface_transport"] == "aicli"
    cli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    assert "start_execution(" not in cli_source
    assert "reconstruct_execution_replay(" not in cli_source
    assert "run_human_interface_runtime_entry(" in cli_source


def test_common_entry_execution_binding_is_worker_neutral_and_stops_before_physical_execution() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)

    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "CODEX" not in source
    assert source.count("start_execution(") == 1
    assert source.count("reconstruct_execution_replay(") == 1
    assert "run_governed_worker_execution(" not in source
    assert "capture_successful_codex_worker_result(" not in source
    assert "execute_g31_authenticated_replace(" not in source
    assert "execute_filesystem_replace_request(" not in source
