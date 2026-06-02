"""Tests for IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_V1."""

from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands import plan as plan_commands
from aigol.cli.commands.plan import (
    IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION,
    plan_approved_command,
    plan_bridge_command,
    plan_chain_command,
    plan_execution_request_command,
    plan_latest_command,
    plan_list_command,
    plan_show_command,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-06-02T17:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-PLAN-000001"
IMPLEMENTATION_PLAN_ID = "PLAN-000001"
BRIDGE_ID = "BRIDGE-PLAN-000001"
EXECUTION_REQUEST_ID = "EXECUTION-REQUEST-PLAN-000001"


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


def _plan_replay(tmp_path) -> dict[str, Path]:
    plan_scope = {"runtime_surface": "cli", "mutation": "read_only"}
    plan_constraints = {"dispatch": False, "execution": False, "replay_mutation": False}
    targets = ["aigol/cli/commands/plan.py"]
    validation = ["python -m pytest tests/test_implementation_plan_inspection_command_group_v1.py"]
    plan = _artifact(
        artifact_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        improvement_implementation_plan_version="IMPROVEMENT_IMPLEMENTATION_RUNTIME_V1",
        implementation_plan_id=IMPLEMENTATION_PLAN_ID,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        improvement_approval_reference="IMPROVEMENT-APPROVAL-000001",
        improvement_approval_hash="sha256:approval",
        improvement_review_reference="IMPROVEMENT-REVIEW-000001",
        improvement_review_hash="sha256:review",
        improvement_proposal_reference="IMPROVEMENT-PROPOSAL-000001",
        improvement_proposal_hash="sha256:proposal",
        evaluation_reference="EVALUATION-000001",
        evaluation_hash="sha256:evaluation",
        result_reference="RESULT-000001",
        result_hash="sha256:result",
        worker_reference="WORKER-000001",
        human_authorization_reference="HUMAN-PLAN-AUTH-000001",
        plan_source="HUMAN_APPROVED_IMPROVEMENT",
        plan_text="Inspect implementation plans without creating execution authority.",
        plan_text_hash=replay_hash("Inspect implementation plans without creating execution authority."),
        plan_scope=plan_scope,
        plan_scope_hash=replay_hash(plan_scope),
        plan_constraints=plan_constraints,
        plan_constraints_hash=replay_hash(plan_constraints),
        planned_artifact_targets=targets,
        planned_artifact_targets_hash=replay_hash(targets),
        planned_validation=validation,
        planned_validation_hash=replay_hash(validation),
        plan_status="IMPLEMENTATION_PLAN_CREATED",
        execution_request_created=False,
        execution_request_reference=None,
        implementation_authorized=True,
        implementation_performed=False,
        implementation_reference=None,
        created_by="AIGOL",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PLAN-000001",
        replay_visible=True,
        provider_authority=False,
        worker_authority=False,
        aigol_autonomous_implementation=False,
        self_improvement_authority=False,
        governance_mutation_authority=False,
        code_mutated=False,
        configuration_mutated=False,
        governance_mutated=False,
        replay_mutated=False,
        worker_dispatched=False,
        worker_invoked=False,
        self_modification_performed=False,
        self_improvement_performed=False,
        self_application_performed=False,
    )
    request = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id=EXECUTION_REQUEST_ID,
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_reference=IMPLEMENTATION_PLAN_ID,
        implementation_plan_hash=plan["artifact_hash"],
        improvement_approval_reference="IMPROVEMENT-APPROVAL-000001",
        improvement_approval_hash="sha256:approval",
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
    bridge = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        bridge_id=BRIDGE_ID,
        execution_request_reference=EXECUTION_REQUEST_ID,
        execution_request_hash=request["artifact_hash"],
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_reference=IMPLEMENTATION_PLAN_ID,
        implementation_plan_hash=plan["artifact_hash"],
        improvement_approval_reference="IMPROVEMENT-APPROVAL-000001",
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
    return {
        "plan": _persist(
            tmp_path,
            "plan",
            "improvement_implementation_plan_created",
            "IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED",
            plan,
        ),
        "request": _persist(
            tmp_path,
            "request",
            "implementation_plan_execution_request_created",
            "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED",
            request,
        ),
        "bridge": _persist(
            tmp_path,
            "bridge",
            "implementation_plan_execution_request_linked",
            "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED",
            bridge,
            index=1,
        ),
    }


def test_plan_list_shows_replay_visible_implementation_plans(tmp_path) -> None:
    _plan_replay(tmp_path)

    result = plan_list_command(replay_root=tmp_path)
    rendered = render_command_result(result)

    assert result["command"] == "aigol plan list"
    assert result["implementation_plan_inspection_command_group_version"] == (
        IMPLEMENTATION_PLAN_INSPECTION_COMMAND_GROUP_VERSION
    )
    assert result["status"] == "READY"
    assert result["plan_count"] == 1
    assert result["read_only"] is True
    assert result["execution_requests_created"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert result["execution_performed"] is False
    assert result["plans"][0]["bridge_id"] == BRIDGE_ID
    assert result["plans"][0]["execution_request_id"] == EXECUTION_REQUEST_ID
    assert "AIGOL PLAN" in rendered


def test_plan_show_approved_and_latest_filters(tmp_path) -> None:
    _plan_replay(tmp_path)

    shown = plan_show_command(implementation_plan_id=IMPLEMENTATION_PLAN_ID, replay_root=tmp_path)
    approved = plan_approved_command(replay_root=tmp_path)
    latest = plan_latest_command(replay_root=tmp_path)

    assert shown["plan_count"] == 1
    assert shown["plans"][0]["implementation_authorized"] is True
    assert approved["plan_count"] == 1
    assert latest["plan_count"] == 1
    assert latest["plans"][0]["implementation_plan_id"] == IMPLEMENTATION_PLAN_ID


def test_plan_chain_bridge_and_execution_request_filters(tmp_path) -> None:
    _plan_replay(tmp_path)

    by_chain = plan_chain_command(canonical_chain_id=CANONICAL_CHAIN_ID, replay_root=tmp_path)
    by_bridge = plan_bridge_command(bridge_id=BRIDGE_ID, replay_root=tmp_path)
    by_request = plan_execution_request_command(execution_request_id=EXECUTION_REQUEST_ID, replay_root=tmp_path)

    assert by_chain["plan_count"] == 1
    assert by_bridge["plan_count"] == 1
    assert by_bridge["plans"][0]["implementation_plan_id"] == IMPLEMENTATION_PLAN_ID
    assert by_request["plan_count"] == 1
    assert by_request["plans"][0]["canonical_chain_id"] == CANONICAL_CHAIN_ID


def test_parser_and_run_command_support_plan_bridge(tmp_path) -> None:
    _plan_replay(tmp_path)
    parser = build_parser()
    args = parser.parse_args(["plan", "bridge", BRIDGE_ID, "--replay-root", str(tmp_path)])

    result = run_command(args)

    assert result["command"] == "aigol plan bridge"
    assert result["plan_count"] == 1


def test_cli_entrypoint_outputs_plan_json(tmp_path) -> None:
    _plan_replay(tmp_path)

    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "plan",
            "show",
            IMPLEMENTATION_PLAN_ID,
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
    assert payload["command"] == "aigol plan show"
    assert payload["plan_count"] == 1
    assert payload["plans"][0]["implementation_plan_id"] == IMPLEMENTATION_PLAN_ID


def test_plan_show_missing_fails_closed_without_authority(tmp_path) -> None:
    _plan_replay(tmp_path)

    result = plan_show_command(implementation_plan_id="MISSING-PLAN", replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["execution_requests_created"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert "implementation plan not found" in result["failure_reason"]


def test_plan_command_detects_corrupt_replay_and_nested_hashes(tmp_path) -> None:
    paths = _plan_replay(tmp_path)
    wrapper = json.loads(paths["plan"].read_text(encoding="utf-8"))
    wrapper["artifact"]["plan_scope"]["mutation"] = "write_enabled"
    paths["plan"].write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = plan_list_command(replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "hash mismatch" in result["failure_reason"]
    assert result["worker_invoked"] is False
    assert result["execution_performed"] is False


def test_plan_command_group_has_no_dispatch_invocation_execution_or_bridge_creation_surface() -> None:
    source = inspect.getsource(plan_commands)
    cli_source = inspect.getsource(aigol_cli)

    assert "create_implementation_plan_execution_request(" not in source
    assert "create_execution_request(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "dispatch_worker(" not in cli_source
    assert "invoke_worker(" not in cli_source
