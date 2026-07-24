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


def _forbid_post_invocation_lifecycle(
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
            raise AssertionError(f"forbidden R14B downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, reject)
    return calls


def test_common_entry_invokes_exact_dispatch_once_and_reconstructs_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R14B-COMMON")
    forbidden = _forbid_post_invocation_lifecycle(monkeypatch)
    calls = {"invocation": 0, "reconstruction": 0}
    original_invocation = entry.worker_invocation.invoke_dispatched_worker
    original_reconstruction = (
        entry.worker_invocation.reconstruct_worker_invocation_replay
    )

    def invoke(*args, **kwargs):
        calls["invocation"] += 1
        return original_invocation(*args, **kwargs)

    def reconstruct(*args, **kwargs):
        calls["reconstruction"] += 1
        return original_reconstruction(*args, **kwargs)

    monkeypatch.setattr(entry.worker_invocation, "invoke_dispatched_worker", invoke)
    monkeypatch.setattr(
        entry.worker_invocation, "reconstruct_worker_invocation_replay", reconstruct
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["worker_invocation_request_capture"][
        "worker_invocation_request_artifact"
    ]
    assignment = result["worker_assignment_capture"]["worker_assignment_artifact"]
    dispatch = result["worker_dispatch_capture"]["worker_dispatch_artifact"]
    invocation = result["worker_invocation_capture"]
    artifact = invocation["worker_invocation_artifact"]
    reconstruction = result["worker_invocation_reconstruction"]

    assert calls == {"invocation": 1, "reconstruction": 1}
    assert all(count == 0 for count in forbidden.values())
    assert result["g31_application_sequenced_by_common_entry"] is True
    assert result["worker_invocation_status"] == entry.worker_invocation.WORKER_INVOKED
    assert result["worker_assigned"] is True
    assert result["worker_dispatched"] is True
    assert result["dispatch_requested"] is True
    assert result["worker_invoked"] is True
    assert result["provider_invoked"] is False
    assert result["execution_started"] is False
    assert result["execution_requested"] is False
    assert result["result_created"] is False
    assert result["command_executed"] is False
    assert result["repository_mutated"] is False
    assert result["governance_mutated"] is False
    assert result["replay_mutated"] is False
    assert artifact["worker_dispatch_reference"] == dispatch["worker_dispatch_id"]
    assert artifact["worker_dispatch_hash"] == dispatch["artifact_hash"]
    assert artifact["worker_assignment_reference"] == assignment[
        "worker_assignment_id"
    ]
    assert artifact["worker_assignment_hash"] == assignment["artifact_hash"]
    assert artifact["worker_invocation_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert artifact["worker_invocation_request_hash"] == request["artifact_hash"]
    assert artifact["authorization_reference"] == request[
        "authorization_reference"
    ]
    assert artifact["authorization_hash"] == request["authorization_hash"]
    assert artifact["execution_packet_reference"] == request[
        "execution_packet_reference"
    ]
    assert artifact["execution_packet_hash"] == request["execution_packet_hash"]
    assert artifact["worker_id"] == WORKER_ID
    assert artifact["chain_id"] == request["chain_id"]
    assert artifact["allowed_outputs"] == dispatch["allowed_outputs"]
    assert artifact["forbidden_operations"] == dispatch["forbidden_operations"]
    assert artifact["validation_requirements"] == dispatch[
        "validation_requirements"
    ]
    assert reconstruction["worker_invocation_id"] == artifact[
        "worker_invocation_id"
    ]
    assert reconstruction["worker_dispatch_reference"] == dispatch[
        "worker_dispatch_id"
    ]
    assert reconstruction["worker_assignment_reference"] == assignment[
        "worker_assignment_id"
    ]
    assert reconstruction["worker_invocation_request_reference"] == request[
        "worker_invocation_request_id"
    ]
    assert reconstruction["authorization_reference"] == request[
        "authorization_reference"
    ]
    assert reconstruction["execution_packet_reference"] == request[
        "execution_packet_reference"
    ]
    assert reconstruction["worker_id"] == WORKER_ID
    assert reconstruction["chain_id"] == request["chain_id"]
    assert reconstruction["worker_invoked"] is True
    assert reconstruction["execution_started"] is False
    assert reconstruction["result_created"] is False
    assert result["worker_invocation_replay_hash"] == reconstruction["replay_hash"]
    assert result["runtime_replay_reference"] == result[
        "worker_invocation_replay_reference"
    ]
    assert sorted(
        path.name
        for path in Path(result["worker_invocation_replay_reference"]).glob("*.json")
    ) == [
        "000_invocation_evidence_recorded.json",
        "001_invocation_classification_recorded.json",
        "002_invocation_artifact_recorded.json",
        "003_invocation_result_recorded.json",
    ]
    assert not list(root.rglob("000_execution_started.json"))
    assert not list(root.glob("WORKER-RESULT-*"))
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Worker Invocation Reached: True" in rendered
    assert "Invocation Status: WORKER_INVOKED" in rendered
    assert f"Invoked Worker: {WORKER_ID}" in rendered
    assert "No Worker process or execution has started." in rendered
    assert "No command has executed." in rendered
    assert "No repository has been modified." in rendered


@pytest.mark.parametrize("mode", ("invocation", "reconstruction"))
def test_invalid_invocation_or_reconstruction_fails_before_worker_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R14B-{mode}")
    forbidden = _forbid_post_invocation_lifecycle(monkeypatch)
    if mode == "invocation":
        monkeypatch.setattr(
            entry.worker_invocation,
            "invoke_dispatched_worker",
            lambda **_kwargs: {"invocation_status": "FAILED_CLOSED"},
        )
    else:
        original = entry.worker_invocation.reconstruct_worker_invocation_replay

        def changed(*args, **kwargs):
            reconstructed = original(*args, **kwargs)
            return {**reconstructed, "execution_started": True}

        monkeypatch.setattr(
            entry.worker_invocation, "reconstruct_worker_invocation_replay", changed
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Worker invocation failed|Worker invocation Replay mismatch",
    ):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    assert all(count == 0 for count in forbidden.values())
    assert not list(root.rglob("000_execution_started.json"))
    invocation_roots = list(root.glob("WORKER-INVOCATION-*"))
    if mode == "invocation":
        assert invocation_roots == []
    else:
        assert len(invocation_roots) == 1
        assert (
            invocation_roots[0] / "002_invocation_artifact_recorded.json"
        ).is_file()


def test_aicli_receives_common_entry_invocation_without_invocation_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    memory_root, memory_state = _pending_state(
        tmp_path, monkeypatch, "R14B-MEMORY"
    )
    memory = InMemoryAdapter(memory_root).transport(
        memory_state, decision.MUTATION_APPROVED
    )
    cli_root, cli_state = _pending_state(tmp_path, monkeypatch, "R14B-AICLI")
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
        artifact = result["worker_invocation_capture"]["worker_invocation_artifact"]
        assert result["worker_invocation_status"] == entry.worker_invocation.WORKER_INVOKED
        assert result["worker_assigned"] is True
        assert result["worker_dispatched"] is True
        assert result["worker_invoked"] is True
        assert result["provider_invoked"] is False
        assert result["execution_started"] is False
        assert result["repository_mutated"] is False
        assert artifact["worker_id"] == WORKER_ID
    assert memory["g31_application_interface_transport"] == "in_memory_test_adapter"
    assert cli["g31_application_interface_transport"] == "aicli"
    cli_source = Path("aigol/cli/aicli.py").read_text(encoding="utf-8")
    assert "invoke_dispatched_worker(" not in cli_source
    assert "reconstruct_worker_invocation_replay(" not in cli_source
    assert "run_human_interface_runtime_entry(" in cli_source


def test_common_entry_invocation_binding_is_worker_neutral_and_stops_before_execution() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)

    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "CODEX" not in source
    assert source.count("invoke_dispatched_worker(") == 1
    assert source.count("reconstruct_worker_invocation_replay(") == 1
    assert "run_governed_worker_execution(" not in source
    assert "execute_g31_authenticated_replace(" not in source
    assert "execute_filesystem_replace_request(" not in source
