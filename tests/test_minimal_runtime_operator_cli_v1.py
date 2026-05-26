"""Tests for MINIMAL_RUNTIME_OPERATOR_CLI_V1."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from aigol.runtime import FailClosedRuntimeError, MockProvider, RuntimeEngine, RuntimePackage
from aigol.runtime.operator import RuntimeQuery, RuntimeSummary, render_runtime_report
from aigol.runtime.operator.runtime_cli import main
from aigol.runtime.transport import RuntimeStore


def _payload():
    return {
        "capability_request": {
            "capability": "analyze_text",
            "target": "inline",
            "request_payload": {"text": "operator visibility", "policy_scope": "ANALYSIS_ONLY"},
        },
        "sandbox": {
            "execution_mode": "MOCK_EXECUTION",
            "allowed_capabilities": ["analyze_text"],
            "denied_capabilities": [
                "shell_execution",
                "subprocess_spawn",
                "filesystem_write",
                "unrestricted_network",
                "worker_spawn",
                "recursive_dispatch",
            ],
            "resource_limits": {"max_memory_mb": 64, "max_runtime_seconds": 1},
            "execution_ttl_seconds": 1,
        },
        "continuity": {
            "continuation_reason": "retry_requested",
            "retry_count": 0,
            "max_retry_limit": 3,
            "parent_runtime_id": "parent-operator-runtime",
        },
        "retry": {
            "retry_reason": "retry_requested",
            "retry_count": 0,
            "max_retry_limit": 3,
            "parent_runtime_id": "parent-operator-runtime",
            "requested_capability": "analyze_text",
            "approval_state": "APPROVED",
        },
    }


def _goal_payload():
    return {
        "goal_sequence": {
            "goal_id": "operator-goal",
            "requested_objective": "inspect bounded goal state",
            "max_step_limit": 2,
            "steps": [
                {
                    "step_id": "operator-step-1",
                    "capability_request": {"capability": "analyze_text", "target": "inline"},
                    "policy_scope": "ANALYSIS_ONLY",
                    "sandbox_profile": "MOCK_EXECUTION",
                    "execution_state": "PENDING",
                }
            ],
        }
    }


def _package(runtime_id: str = "operator-v1", payload=None) -> RuntimePackage:
    return RuntimePackage(
        runtime_id=runtime_id,
        package_id=f"package-{runtime_id}",
        provider="mock",
        worker_id=f"worker-{runtime_id}",
        task_type="capability",
        payload=payload or _payload(),
        lineage_refs=[{"ref_type": "minimal_operator_cli", "hash": "sha256:operator-v1"}],
        governance_state="AUTHORIZED",
        created_at="1970-01-01T00:00:00Z",
    )


def _store_with_runtime(tmp_path) -> RuntimeStore:
    store = RuntimeStore(tmp_path)
    engine = RuntimeEngine(runtime_store=store)
    engine.register_provider(MockProvider())
    engine.dispatch(_package())
    engine.dispatch(_package(runtime_id="operator-goal-runtime", payload=_goal_payload()))
    return store


def test_summary_rendering(tmp_path) -> None:
    _store_with_runtime(tmp_path)
    summary = RuntimeQuery(tmp_path).get_runtime_summary("operator-v1")
    report = render_runtime_report(summary)

    assert "runtime_id: operator-v1" in report
    assert "approval_state: APPROVED" in report
    assert "routing_state: ROUTE_ASSIGNED" in report
    assert "retry_state: RETRY_EXECUTED" in report
    assert "replay_integrity_state: VERIFIED" in report


def test_replay_backed_queries(tmp_path) -> None:
    _store_with_runtime(tmp_path)
    query = RuntimeQuery(tmp_path)

    runtime = query.get_runtime_summary("operator-v1")
    goal = query.get_goal_summary("operator-goal")
    retry = query.get_retry_summary("operator-v1")

    assert runtime["continuity_state"] == "CONTINUE"
    assert goal["goal_state"] == "CONTINUE"
    assert retry["retry_state"] == "RETRY_EXECUTED"


def test_deterministic_cli_output(tmp_path, capsys) -> None:
    _store_with_runtime(tmp_path)

    assert main(["--root", str(tmp_path), "summary", "operator-v1"]) == 0
    first = capsys.readouterr().out
    assert main(["--root", str(tmp_path), "summary", "operator-v1"]) == 0
    second = capsys.readouterr().out

    assert first == second
    assert "runtime_id: operator-v1" in first


def test_goal_cli_output(tmp_path, capsys) -> None:
    _store_with_runtime(tmp_path)

    assert main(["--root", str(tmp_path), "goal", "operator-goal"]) == 0
    output = capsys.readouterr().out

    assert "goal_id: operator-goal" in output
    assert "goal_state: CONTINUE" in output


def test_retry_cli_output(tmp_path, capsys) -> None:
    _store_with_runtime(tmp_path)

    assert main(["--root", str(tmp_path), "retry", "operator-v1"]) == 0
    output = capsys.readouterr().out

    assert "retry_state: RETRY_EXECUTED" in output
    assert "bounded_local_only: True" in output


def test_invalid_runtime_handling(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError):
        RuntimeQuery(tmp_path).get_runtime_summary("missing-runtime")


def test_cli_invalid_runtime_fails_closed(tmp_path, capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--root", str(tmp_path), "summary", "missing-runtime"])

    assert exc.value.code == 2
    assert "FAIL_CLOSED" in capsys.readouterr().err


def test_immutable_observability_guarantees(tmp_path) -> None:
    _store_with_runtime(tmp_path)
    before = RuntimeStore(tmp_path).ledger.read("operator-v1")
    summary = RuntimeQuery(tmp_path).get_runtime_summary("operator-v1")
    after = RuntimeStore(tmp_path).ledger.read("operator-v1")

    assert before == after
    model = RuntimeSummary(
        runtime_id=summary["runtime_id"],
        goal_state=summary["goal_state"],
        approval_state=summary["approval_state"],
        routing_state=summary["routing_state"],
        retry_state=summary["retry_state"],
        continuity_state=summary["continuity_state"],
        replay_integrity_state=summary["replay_integrity_state"],
        created_at=summary["created_at"],
        lineage_refs=summary["lineage_refs"],
        replay_hash=summary["replay_hash"],
    )
    with pytest.raises(FrozenInstanceError):
        model.retry_state = "MUTATED"  # type: ignore[misc]
