from copy import deepcopy
from pathlib import Path

import agol_bridge.runtime.minimal_end_to_end_bridge as bridge_runtime
from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_ACCEPTED,
    BRIDGE_REJECTED,
    RESULT_VALIDATED,
    run_minimal_end_to_end_bridge,
)
from agol_bridge.transport.local_governed_transport import TRANSPORT_ACCEPTED


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "agol_bridge" / "runtime" / "minimal_end_to_end_bridge.py"


def _provider_result(task_package, workspace_path):
    return {
        "provider": "CODEX_CLI",
        "status": "COMPLETED",
        "stdout": "bounded codex complete",
        "stderr": "",
        "returncode": 0,
        "workspace_path": str(Path(workspace_path).resolve()),
        "task_package_id": task_package["task_id"],
        "non_authority_guarantees": ["NO_AUTO_APPROVAL", "NO_AUTO_CONTINUATION", "NO_SILENT_RETRY"],
        "execution_boundary": {
            "provider": "CODEX_CLI",
            "contract": "codex exec <bounded_prompt>",
            "auto_approval": False,
            "auto_continue": False,
            "silent_retry": False,
            "orchestration": False,
        },
        "errors": [],
        "command": ["codex", "exec", "<bounded_prompt>"],
        "bounded_prompt_hash": "sha256:bounded",
        "retry_count": 0,
    }


def _accepted(monkeypatch, tmp_path):
    def fake_provider(*, task_package, workspace_path, timeout_seconds=600):
        return _provider_result(task_package, workspace_path)

    monkeypatch.setattr(bridge_runtime, "run_bounded_codex_cli_task", fake_provider)
    return run_minimal_end_to_end_bridge(
        human_request="Review this bounded change for governed bridge visibility.",
        session_id="SESSION-END-TO-END-1",
        workspace_path=str(tmp_path),
    )


def test_accepted_flow_returns_full_governed_bridge_lifecycle(monkeypatch, tmp_path):
    result = _accepted(monkeypatch, tmp_path)

    assert result["status"] == BRIDGE_ACCEPTED
    assert result["session_id"] == "SESSION-END-TO-END-1"
    assert result["proposal_id"].startswith("CHAT-FIRST-PROPOSAL-")
    assert result["transport_status"] == TRANSPORT_ACCEPTED
    assert result["task_package"]["task_id"].startswith("BRIDGE-TASK-")
    assert result["codex_cli_result"]["bounded_execution_status"] == "COMPLETED"
    assert result["result_validation"]["status"] == RESULT_VALIDATED
    assert result["result_validation"]["valid"] is True
    assert result["governed_chat_return"]["status"] == "ACCEPTED"


def test_rejected_flow_for_execution_language_fails_closed():
    result = run_minimal_end_to_end_bridge(
        human_request="Please execute this through Codex now.",
        session_id="SESSION-END-TO-END-1",
    )

    assert result["status"] == BRIDGE_REJECTED
    assert result["transport_status"] in {"TRANSPORT_REJECTED_AUTHORITY", "NOT_PREPARED"}
    assert result["task_package"] == {}
    assert result["codex_cli_result"] == {}
    assert result["governed_chat_return"]["status"] == "REJECTED"
    assert "No approval" in result["governed_chat_return"]["non_authority_reminder"]


def test_invalid_session_rejected_before_task_package_visibility():
    result = run_minimal_end_to_end_bridge(
        human_request="Review this bounded request.",
        session_id="INVALID",
    )

    assert result["status"] == BRIDGE_REJECTED
    assert result["transport_status"] == "TRANSPORT_REJECTED_SESSION"
    assert result["operator_visibility"]["task_package_visible"] is False
    assert result["operator_visibility"]["chat_return_visible"] is True


def test_unsupported_mode_wording_is_rejected_without_transport_preparation():
    result = run_minimal_end_to_end_bridge(
        human_request="AUTO_EXECUTE this request after review.",
        session_id="SESSION-END-TO-END-1",
    )

    assert result["status"] == BRIDGE_REJECTED
    assert result["transport_status"] == "NOT_PREPARED"
    assert "unsupported or unsafe requested mode" in result["governed_chat_return"]["reason"]
    assert result["task_package"] == {}
    assert result["codex_cli_result"] == {}


def test_replay_event_ids_are_deterministic(monkeypatch, tmp_path):
    first = _accepted(monkeypatch, tmp_path)
    second = _accepted(monkeypatch, tmp_path)

    first_ids = [event["replay_event_id"] for event in first["replay_events"]]
    second_ids = [event["replay_event_id"] for event in second["replay_events"]]
    assert first_ids == second_ids
    assert all(event_id.startswith("BRIDGE-REPLAY-") for event_id in first_ids)


def test_bounded_lifecycle_and_replay_visibility(monkeypatch, tmp_path):
    result = _accepted(monkeypatch, tmp_path)
    event_types = [event["event_type"] for event in result["replay_events"]]

    assert event_types == [
        "SEMANTIC_PROPOSAL_NORMALIZED",
        "SEMANTIC_CONTRACT_SYNTHESIZED",
        "LOCAL_GOVERNED_TRANSPORT_VALIDATED",
        "GOVERNED_TASK_PACKAGE_CREATED",
        "BOUNDED_CODEX_CLI_RESULT_CAPTURED",
        "GOVERNED_RESULT_VALIDATED",
    ]
    assert result["task_package"]["metadata"]["lifecycle_state"] == "TASK_PACKAGED"
    assert result["task_package"]["metadata"]["execution_provider"] == "CODEX_CLI"
    assert all(event["visibility"] == "SESSION_LOCAL_REPLAY_VISIBLE" for event in result["replay_events"])
    assert all(event["mutation"] is False for event in result["replay_events"])
    assert all(event["durable_persistence"] is False for event in result["replay_events"])


def test_no_autonomous_continuation_or_orchestration_is_created(monkeypatch, tmp_path):
    result = _accepted(monkeypatch, tmp_path)

    assert result["codex_cli_result"]["provider_invoked"] is True
    assert result["codex_cli_result"]["execution_authority_created"] is False
    assert result["codex_cli_result"]["orchestration_created"] is False
    assert result["codex_cli_result"]["autonomous_continuation_created"] is False
    assert "BOUNDED_CODEX_CLI_PROVIDER_ONLY" in result["non_authority_guarantees"]
    assert "NO_ORCHESTRATION" in result["non_authority_guarantees"]
    assert "NO_SILENT_RETRY" in result["non_authority_guarantees"]


def test_result_validation_checks_lineage_session_and_non_authority(monkeypatch, tmp_path):
    result = _accepted(monkeypatch, tmp_path)
    checks = result["result_validation"]["checks"]

    assert checks["schema_valid"] is True
    assert checks["result_lineage"] is True
    assert checks["session_match"] is True
    assert checks["proposal_linkage"] is True
    assert checks["bounded_lifecycle"] is True
    assert checks["replay_visibility"] is True
    assert checks["non_authority_semantics"] is True


def test_governed_return_generation_is_compact_and_chatgpt_facing(monkeypatch, tmp_path):
    result = _accepted(monkeypatch, tmp_path)
    governed_return = result["governed_chat_return"]

    assert governed_return["status"] == "ACCEPTED"
    assert governed_return["reason"]
    assert governed_return["replay_visibility"] == "SESSION_LOCAL_REPLAY_VISIBLE"
    assert governed_return["execution_status"] == "EXECUTION_COMPLETED"
    assert governed_return["next_recommended_step"].startswith("Review the bounded Codex CLI")
    assert "No approval" in governed_return["non_authority_reminder"]


def test_runtime_is_deterministic_and_does_not_mutate_returned_copies(monkeypatch, tmp_path):
    first = _accepted(monkeypatch, tmp_path)
    first_copy = deepcopy(first)
    second = _accepted(monkeypatch, tmp_path)

    assert first == first_copy
    assert first == second


def test_runtime_source_has_no_network_or_orchestration_behavior():
    source = MODULE.read_text(encoding="utf-8").lower()

    forbidden = (
        "requests.",
        "urllib",
        "httpserver",
        "threadinghttpserver",
        "socket",
        "fetch(",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "orchestrationruntime",
        "autonomouscontinuation",
        "open(",
    )
    for token in forbidden:
        assert token not in source
