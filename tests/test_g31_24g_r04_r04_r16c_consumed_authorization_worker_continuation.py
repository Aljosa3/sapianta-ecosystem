from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)


WORKER_ID = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
CAPABILITY = "REPLACE_EXISTING_TEXT_FILE"


def _capture_continuation(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[dict[str, object], object]:
    supplied: dict[str, object] = {}
    original = entry.filesystem_replace_worker.execute_consumed_authenticated_replace_v2

    def observed(**kwargs):
        supplied.update(deepcopy(kwargs))
        return original(**kwargs)

    monkeypatch.setattr(
        entry.filesystem_replace_worker,
        "execute_consumed_authenticated_replace_v2",
        observed,
    )
    return supplied, original


def _rehash_artifact(artifact: dict) -> dict:
    changed = deepcopy(artifact)
    changed["artifact_hash"] = replay_hash(
        {key: value for key, value in changed.items() if key != "artifact_hash"}
    )
    return changed


def test_common_entry_continues_consumed_authorization_once_through_existing_worker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R16C-COMMON")
    supplied, _ = _capture_continuation(monkeypatch)
    calls = {"consume": 0, "continuation": 0, "events": []}
    original_consume = (
        entry.filesystem_replace_worker.consume_authenticated_replace_authorization_v2
    )
    original_continue = (
        entry.filesystem_replace_worker.execute_consumed_authenticated_replace_v2
    )
    original_event = entry.filesystem_replace_worker._persist_v2_event

    def consume(request):
        calls["consume"] += 1
        return original_consume(request)

    def continuation(**kwargs):
        calls["continuation"] += 1
        return original_continue(**kwargs)

    def event(request, key, event_type, payload, previous):
        calls["events"].append(key)
        return original_event(request, key, event_type, payload, previous)

    monkeypatch.setattr(
        entry.filesystem_replace_worker,
        "consume_authenticated_replace_authorization_v2",
        consume,
    )
    monkeypatch.setattr(
        entry.filesystem_replace_worker,
        "execute_consumed_authenticated_replace_v2",
        continuation,
    )
    monkeypatch.setattr(entry.filesystem_replace_worker, "_persist_v2_event", event)

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    consumption = result["authorization_consumption_reconstruction"]
    worker_replay = result["filesystem_replace_worker_reconstruction"]
    execution = result["worker_execution_capture"]["execution_artifact"]
    target = (
        Path(state["repository_grounding_artifact"]["workspace_root"])
        / request["target_path"]
    )
    journal = load_json(Path(request["destinations"]["journal"]))

    assert supplied
    assert calls == {
        "consume": 1,
        "continuation": 1,
        "events": [
            "request",
            "consumption",
            "journal",
            "started",
            "atomic",
            "result",
            "completion",
        ],
    }
    assert journal["previous_replay_hash"] == consumption["last_wrapper_hash"]
    assert worker_replay["event_keys"] == [
        "request",
        "consumption",
        "journal",
        "started",
        "atomic",
        "result",
        "completion",
    ]
    assert worker_replay["latest_event"] == "MUTATION_COMPLETED"
    assert len(list(Path(request["destinations"]["request"]).parent.glob("*consumption.json"))) == 1
    assert target.read_text(encoding="utf-8") == "after\n"
    assert result["authorization_consumed"] is True
    assert result["worker_execution_performed"] is True
    assert result["filesystem_replace_worker_status"] == "COMPLETED"
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert result["worker_result_captured"] is True
    assert result["result_created"] is True
    assert result["result_validated"] is False
    assert result["repository_mutated"] is True
    assert result["main_repository_mutated"] is True
    assert execution["execution_status"] == entry.execution_runtime.EXECUTING
    assert execution["worker_reference"] == WORKER_ID
    assert execution["capability_id"] == CAPABILITY
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Filesystem Replace Worker Executed: True" in rendered
    assert "Filesystem Replace Worker Result Captured: True" in rendered
    assert "Authorization consumption was not repeated." in rendered


@pytest.mark.parametrize(
    "case",
    (
        "consumption",
        "invocation_request",
        "assignment_capability",
        "execution_authority",
        "execution_reconstruction",
    ),
)
def test_changed_continuation_lineage_fails_before_target_open_or_journal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R16C-{case}")
    supplied: dict[str, object] = {}
    original = entry.filesystem_replace_worker.execute_consumed_authenticated_replace_v2

    def stop_before_worker(**kwargs):
        supplied.update(deepcopy(kwargs))
        raise FailClosedRuntimeError("captured R16C boundary")

    monkeypatch.setattr(
        entry.filesystem_replace_worker,
        "execute_consumed_authenticated_replace_v2",
        stop_before_worker,
    )
    with pytest.raises(FailClosedRuntimeError, match="captured R16C boundary"):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    monkeypatch.setattr(
        entry.filesystem_replace_worker,
        "execute_consumed_authenticated_replace_v2",
        original,
    )

    changed = deepcopy(supplied)
    if case == "consumption":
        changed["consumption_reconstruction"]["replay_hash"] = "SUBSTITUTED"
    elif case == "invocation_request":
        artifact = changed["worker_invocation_request_artifact"]
        artifact["execution_packet_hash"] = "SUBSTITUTED"
        changed["worker_invocation_request_artifact"] = _rehash_artifact(artifact)
    elif case == "assignment_capability":
        artifact = changed["worker_assignment_artifact"]
        artifact["capability_id"] = "SUBSTITUTED"
        changed["worker_assignment_artifact"] = _rehash_artifact(artifact)
    elif case == "execution_authority":
        artifact = changed["execution_artifact"]
        artifact["provider_authority"] = True
        changed["execution_artifact"] = _rehash_artifact(artifact)
    else:
        changed["execution_reconstruction"]["completion_recorded"] = True

    request = changed["authenticated_request"]
    target = Path(request["repository_root"]) / request["target_path"]
    with pytest.raises(
        FailClosedRuntimeError,
        match="consumed filesystem replace continuation lineage mismatch",
    ):
        original(**changed)

    assert target.read_text(encoding="utf-8") == "before\n"
    assert not Path(request["destinations"]["journal"]).exists()
    assert (
        entry.filesystem_replace_worker.reconstruct_authenticated_replace_replay_v2(
            request
        )["event_keys"]
        == ["request", "consumption"]
    )


def test_second_worker_continuation_fails_without_duplicate_consumption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R16C-DUPLICATE")
    supplied, original = _capture_continuation(monkeypatch)
    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    request = result["authenticated_replacement_request"]
    lifecycle = Path(request["destinations"]["request"]).parent

    with pytest.raises(FailClosedRuntimeError):
        original(**supplied)

    assert len(list(lifecycle.glob("*consumption.json"))) == 1
    assert result["filesystem_replace_worker_reconstruction"]["event_keys"] == [
        "request",
        "consumption",
        "journal",
        "started",
        "atomic",
        "result",
        "completion",
    ]


def test_common_entry_uses_one_worker_owned_continuation_and_no_legacy_execution_path() -> None:
    entry_source = inspect.getsource(entry._authorize_g31_mutation_decision)
    fresh_source = inspect.getsource(
        entry.filesystem_replace_worker._execute_authenticated_replace_v2
    )
    continuation_source = inspect.getsource(
        entry.filesystem_replace_worker.execute_consumed_authenticated_replace_v2
    )

    assert entry_source.count("execute_consumed_authenticated_replace_v2(") == 1
    assert "execute_g31_authenticated_replace(" not in entry_source
    assert "execute_filesystem_replace_request(" not in entry_source
    assert "_execute_authenticated_replace_v2(" not in entry_source
    assert fresh_source.count("_execute_authenticated_replace_after_consumption_v2(") == 1
    assert (
        continuation_source.count(
            "_execute_authenticated_replace_after_consumption_v2("
        )
        == 1
    )
