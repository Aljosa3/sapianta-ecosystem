import json
from pathlib import Path

import pytest

from agol_bridge.bridge_listener import process_incoming_tasks
from agol_bridge.lifecycle import transition_lifecycle
from agol_bridge.replay_logger import replay_log_path
from agol_bridge.result_writer import write_result_package
from agol_bridge.schema_validator import validate_result_package, validate_task_package
from agol_bridge.task_dispatcher import approve_task, dispatch_task, submit_task


def _task(**overrides):
    package = {
        "task_id": "TASK-1",
        "governance_mode": "governed_execution_bridge",
        "risk_class": "bounded",
        "approval_required": True,
        "codex_prompt": "Run bounded validation.",
        "constraints": ["no hidden execution", "filesystem transport only"],
        "expected_outputs": ["summary"],
        "metadata": {"source": "chatgpt", "approved": False},
    }
    package.update(overrides)
    return package


def _result(**overrides):
    package = {
        "status": "EXECUTION_ACCEPTED",
        "tests": [{"command": "python -m pytest agol_bridge/tests", "status": "PASS"}],
        "files_changed": ["agol_bridge/task_dispatcher.py"],
        "artifacts": [],
        "summary": "Bounded transport runtime updated.",
        "requires_human_review": True,
    }
    package.update(overrides)
    return package


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_task_and_result_schema_validation():
    assert validate_task_package(_task())["valid"] is True
    assert validate_result_package(_result())["valid"] is True
    invalid_task = _task()
    invalid_task.pop("codex_prompt")
    assert validate_task_package(invalid_task)["valid"] is False
    invalid_result = _result(tests="not-a-list")
    assert validate_result_package(invalid_result)["valid"] is False


def test_approval_required_task_waits_and_logs_replay(tmp_path):
    outcome = submit_task(_task(), bridge_root=tmp_path)
    assert outcome["status"] == "WAITING_FOR_APPROVAL"
    stored = _read(outcome["path"])
    assert stored["metadata"]["lifecycle_state"] == "WAITING_FOR_APPROVAL"
    log_lines = replay_log_path(tmp_path).read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 1
    record = json.loads(log_lines[0])
    assert record["event_type"] == "WAITING_FOR_APPROVAL"
    assert record["package_hash"]


def test_explicit_approval_gates_dispatch(tmp_path):
    submit_task(_task(), bridge_root=tmp_path)
    blocked = dispatch_task("TASK-1", bridge_root=tmp_path)
    assert blocked["status"] == "WAITING_FOR_APPROVAL"
    approved = approve_task("TASK-1", bridge_root=tmp_path, approved_by="human")
    assert approved["status"] == "APPROVED"
    dispatched = dispatch_task("TASK-1", bridge_root=tmp_path)
    assert dispatched["status"] == "DISPATCHED"
    stored = _read(dispatched["path"])
    assert stored["metadata"]["lifecycle_state"] == "DISPATCHED"
    assert not (tmp_path / "approved" / "TASK-1.json").exists()


def test_dispatched_packages_are_immutable(tmp_path):
    package = _task(approval_required=False, metadata={"source": "chatgpt", "approved": True})
    submit_task(package, bridge_root=tmp_path)
    first = dispatch_task("TASK-1", bridge_root=tmp_path)
    assert first["status"] == "DISPATCHED"
    package = _task(approval_required=False, metadata={"source": "chatgpt", "approved": True})
    submit_task(package, bridge_root=tmp_path)
    second = dispatch_task("TASK-1", bridge_root=tmp_path)
    assert second["status"] == "BLOCKED"
    assert "immutable dispatched package already exists" in second["errors"][0]["error"]


def test_duplicate_submission_does_not_silently_overwrite(tmp_path):
    first = submit_task(_task(), bridge_root=tmp_path)
    assert first["status"] == "WAITING_FOR_APPROVAL"
    second = submit_task(_task(), bridge_root=tmp_path)
    assert second["status"] == "BLOCKED"
    assert "silent overwrite blocked" in second["errors"][0]["error"]


def test_invalid_schema_quarantines_fail_closed(tmp_path):
    invalid = _task()
    invalid.pop("metadata")
    outcome = submit_task(invalid, bridge_root=tmp_path)
    assert outcome["status"] == "QUARANTINED"
    assert Path(outcome["path"]).parent.name == "quarantine"
    stored = _read(outcome["path"])
    assert stored["metadata"]["lifecycle_state"] == "QUARANTINED"


def test_unknown_and_unexpected_lifecycle_states_fail_closed():
    unknown = _task(metadata={"lifecycle_state": "SURPRISE", "approved": True})
    assert transition_lifecycle(unknown, "APPROVED")["status"] == "BLOCKED"
    finalized = _task(metadata={"lifecycle_state": "FINALIZED", "approved": True})
    result = transition_lifecycle(finalized, "DISPATCHED")
    assert result["status"] == "QUARANTINE"
    assert result["package"]["metadata"]["lifecycle_state"] == "QUARANTINED"


def test_result_writer_returns_valid_results_and_quarantines_invalid_results(tmp_path):
    returned = write_result_package(_result(), bridge_root=tmp_path)
    assert returned["status"] == "RETURNED"
    assert Path(returned["path"]).parent.name == "results"
    with pytest.raises(FileExistsError):
        write_result_package(_result(), bridge_root=tmp_path)
    invalid = _result(summary="")
    quarantined = write_result_package(invalid, bridge_root=tmp_path)
    assert quarantined["status"] == "QUARANTINED"
    assert Path(quarantined["path"]).parent.name == "quarantine"


def test_replay_log_is_append_only_jsonl(tmp_path):
    submit_task(_task(), bridge_root=tmp_path)
    approve_task("TASK-1", bridge_root=tmp_path, approved_by="human")
    dispatch_task("TASK-1", bridge_root=tmp_path)
    records = [json.loads(line) for line in replay_log_path(tmp_path).read_text(encoding="utf-8").splitlines()]
    assert [record["event_type"] for record in records] == [
        "WAITING_FOR_APPROVAL",
        "APPROVED",
        "DISPATCHED",
    ]
    assert all(record["event_id"].startswith("AGOL-REPLAY-") for record in records)
    assert all(record["package_hash"] for record in records)


def test_listener_preserves_waiting_for_approval_file(tmp_path):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    package = _task()
    path = incoming / "TASK-1.json"
    path.write_text(json.dumps(package), encoding="utf-8")
    outcomes = process_incoming_tasks(bridge_root=tmp_path)
    assert outcomes[0]["status"] == "WAITING_FOR_APPROVAL"
    assert path.exists()
    stored = _read(path)
    assert stored["metadata"]["lifecycle_state"] == "WAITING_FOR_APPROVAL"
