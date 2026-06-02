"""Tests for BRIDGE_AUTHORIZATION_COMMAND_GROUP_V1."""

from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands import bridge as bridge_commands
from aigol.cli.commands.bridge import (
    BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION,
    bridge_approved_command,
    bridge_chain_command,
    bridge_execution_request_command,
    bridge_list_command,
    bridge_pending_command,
    bridge_rejected_command,
    bridge_show_command,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-06-02T15:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-BRIDGE-000001"
BRIDGE_ID = "BRIDGE-000001"
EXECUTION_REQUEST_ID = "EXECUTION-REQUEST-000001"


def _artifact(**values) -> dict:
    artifact = dict(values)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist(tmp_path, dirname: str, step: str, event_type: str, artifact: dict, *, index: int = 0) -> Path:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": event_type,
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    path = tmp_path / dirname / f"{index:03d}_{step}.json"
    write_json_immutable(path, wrapper)
    return path


def _bridge_replay(tmp_path) -> dict[str, dict]:
    request = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id=EXECUTION_REQUEST_ID,
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_reference="PLAN-000001",
        implementation_plan_hash="sha256:plan",
        improvement_approval_reference="APPROVAL-000001",
        improvement_approval_hash="sha256:approval",
        improvement_review_reference="REVIEW-000001",
        improvement_review_hash="sha256:review",
        improvement_proposal_reference="IMPROVEMENT-PROPOSAL-000001",
        improvement_proposal_hash="sha256:proposal",
        evaluation_reference="EVALUATION-000001",
        evaluation_hash="sha256:evaluation",
        result_reference="RESULT-000001",
        result_hash="sha256:result",
        worker_reference="WORKER-000001",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        human_authorization_reference="HUMAN-BRIDGE-AUTH-000001",
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={"approved_action": "CREATE_GOVERNED_IMPLEMENTATION_REQUEST"},
        request_payload_hash=replay_hash({"approved_action": "CREATE_GOVERNED_IMPLEMENTATION_REQUEST"}),
        status="CREATED",
        replay_reference="REPLAY-BRIDGE-000001",
        replay_visible=True,
        provider_authority=False,
        provider_invoked=False,
        worker_authority=False,
        worker_dispatched=False,
        worker_invoked=False,
        execution_performed=False,
        completion_performed=False,
        approval_created=False,
        automatic_authorization=False,
        implementation_performed=False,
        code_mutated=False,
        governance_mutated=False,
        replay_mutated=False,
        self_approved=False,
        self_authorized=False,
        self_implemented=False,
        self_application_performed=False,
    )
    link = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        implementation_plan_execution_request_runtime_version="IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1",
        bridge_id=BRIDGE_ID,
        execution_request_reference=request["execution_request_id"],
        execution_request_hash=request["artifact_hash"],
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_reference="PLAN-000001",
        implementation_plan_hash="sha256:plan",
        improvement_approval_reference="APPROVAL-000001",
        improvement_approval_hash="sha256:approval",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        human_authorization_reference="HUMAN-BRIDGE-AUTH-000001",
        requested_by="AIGOL",
        created_at=CREATED_AT,
        status="CREATED",
        replay_reference="REPLAY-BRIDGE-000001",
        replay_visible=True,
        execution_request_created=True,
        automatic_execution_request=False,
        automatic_authorization=False,
        provider_authority=False,
        worker_authority=False,
        worker_dispatched=False,
        worker_invoked=False,
        execution_performed=False,
        completion_performed=False,
        implementation_performed=False,
        code_mutated=False,
        governance_mutated=False,
        replay_mutated=False,
        self_approved=False,
        self_authorized=False,
        self_implemented=False,
        self_application_performed=False,
    )
    rejected = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        bridge_id="BRIDGE-REJECTED-000001",
        execution_request_reference=None,
        execution_request_hash=None,
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_reference="PLAN-REJECTED-000001",
        implementation_plan_hash="sha256:plan-rejected",
        improvement_approval_reference="APPROVAL-REJECTED-000001",
        improvement_approval_hash="sha256:approval-rejected",
        canonical_chain_id="CHAIN-BRIDGE-REJECTED",
        human_authorization_reference="HUMAN-BRIDGE-AUTH-REJECTED",
        requested_by="AIGOL",
        created_at=CREATED_AT,
        authorization_status="REJECTED",
        replay_reference="REPLAY-BRIDGE-REJECTED-000001",
        replay_visible=True,
        execution_request_created=False,
        automatic_execution_request=False,
        automatic_authorization=False,
        worker_dispatched=False,
        worker_invoked=False,
        execution_performed=False,
        governance_mutated=False,
        replay_mutated=False,
    )
    _persist(
        tmp_path,
        "bridge_request",
        "implementation_plan_execution_request_created",
        "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED",
        request,
        index=0,
    )
    _persist(
        tmp_path,
        "bridge_link",
        "implementation_plan_execution_request_linked",
        "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED",
        link,
        index=1,
    )
    _persist(
        tmp_path,
        "bridge_rejected",
        "implementation_plan_execution_request_rejected",
        "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_REJECTED",
        rejected,
        index=0,
    )
    return {"request": request, "link": link, "rejected": rejected}


def test_bridge_list_shows_authorized_bridge_transitions(tmp_path) -> None:
    _bridge_replay(tmp_path)

    result = bridge_list_command(replay_root=tmp_path)
    rendered = render_command_result(result)

    assert result["command"] == "aigol bridge list"
    assert result["bridge_authorization_command_group_version"] == BRIDGE_AUTHORIZATION_COMMAND_GROUP_VERSION
    assert result["status"] == "READY"
    assert result["bridge_count"] == 2
    assert result["read_only"] is True
    assert result["execution_requests_created"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert result["execution_performed"] is False
    assert "AIGOL BRIDGE" in rendered
    assert BRIDGE_ID in rendered


def test_bridge_show_and_status_filters(tmp_path) -> None:
    _bridge_replay(tmp_path)

    shown = bridge_show_command(bridge_id=BRIDGE_ID, replay_root=tmp_path)
    approved = bridge_approved_command(replay_root=tmp_path)
    rejected = bridge_rejected_command(replay_root=tmp_path)
    pending = bridge_pending_command(replay_root=tmp_path)

    assert shown["bridge_count"] == 1
    assert shown["bridges"][0]["execution_request_id"] == EXECUTION_REQUEST_ID
    assert shown["bridges"][0]["authorization_status"] == "APPROVED"
    assert approved["bridge_count"] == 1
    assert rejected["bridge_count"] == 1
    assert rejected["bridges"][0]["authorization_status"] == "REJECTED"
    assert pending["bridge_count"] == 0


def test_bridge_chain_and_execution_request_filters(tmp_path) -> None:
    _bridge_replay(tmp_path)

    by_chain = bridge_chain_command(canonical_chain_id=CANONICAL_CHAIN_ID, replay_root=tmp_path)
    by_request = bridge_execution_request_command(execution_request_id=EXECUTION_REQUEST_ID, replay_root=tmp_path)

    assert by_chain["bridge_count"] == 1
    assert by_chain["bridges"][0]["bridge_id"] == BRIDGE_ID
    assert by_request["bridge_count"] == 1
    assert by_request["bridges"][0]["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert by_request["bridges"][0]["execution_request_artifact_hash"]


def test_parser_and_run_command_support_bridge_execution_request(tmp_path) -> None:
    _bridge_replay(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "bridge",
            "execution-request",
            EXECUTION_REQUEST_ID,
            "--replay-root",
            str(tmp_path),
        ]
    )

    result = run_command(args)

    assert result["command"] == "aigol bridge execution-request"
    assert result["bridge_count"] == 1


def test_cli_entrypoint_outputs_bridge_json(tmp_path) -> None:
    _bridge_replay(tmp_path)

    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "bridge",
            "show",
            BRIDGE_ID,
            "--replay-root",
            str(tmp_path),
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["command"] == "aigol bridge show"
    assert payload["bridge_count"] == 1
    assert payload["bridges"][0]["bridge_id"] == BRIDGE_ID


def test_bridge_show_missing_fails_closed_without_authority(tmp_path) -> None:
    _bridge_replay(tmp_path)

    result = bridge_show_command(bridge_id="MISSING-BRIDGE", replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["execution_requests_created"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert "bridge not found" in result["failure_reason"]


def test_bridge_command_detects_corrupt_bridge_replay(tmp_path) -> None:
    _bridge_replay(tmp_path)
    path = tmp_path / "bridge_link" / "001_implementation_plan_execution_request_linked.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = bridge_list_command(replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "hash mismatch" in result["failure_reason"]


def test_bridge_command_group_has_no_dispatch_invocation_or_execution_surface() -> None:
    source = inspect.getsource(bridge_commands)
    cli_source = inspect.getsource(aigol_cli)

    assert "create_implementation_plan_execution_request(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "dispatch_worker(" not in cli_source
    assert "invoke_worker(" not in cli_source
