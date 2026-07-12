from __future__ import annotations

import argparse
import json
from pathlib import Path

from aigol.cli import aicli, aigol_cli
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND,
    _runtime_status_projection,
    run_human_interface_runtime_entry,
)


def _runtime_runner(calls: list[dict]):
    def run(args, input_func, output_func):
        prompt = input_func("")
        calls.append(
            {
                "session_id": args.session_id,
                "operator_context": args.operator_context,
                "prompt": prompt,
            }
        )
        output_func("canonical runtime accepted")
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": True,
                    "replay_certification_reached": True,
                    "execution_authorization_status": "EXECUTION_AUTHORIZED",
                    "openai_provider_reached": True,
                    "execution_preparation_status": "EXECUTION_READY",
                    "worker_assignment_status": "WORKER_ASSIGNED",
                    "worker_dispatch_status": "WORKER_DISPATCHED",
                    "worker_invocation_status": "WORKER_INVOKED",
                    "result_validation_status": "RESULT_VALIDATION_COMPLETED",
                    "replay_certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                    "execution_summary_reference": "summary",
                    "human_confirmation_reference": "approval",
                    "replay_reference": str(Path(args.runtime_root) / "runtime" / "TURN-000001"),
                }
            ],
        }

    return run


def test_canonical_runtime_entry_service_owns_shared_runtime_binding(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = run_human_interface_runtime_entry(
        interface_name="reference test interface",
        session_id="UHI-CANONICAL",
        human_requests=["Implement governance validation utility."],
        created_at="2026-07-05T00:00:00Z",
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_runtime_runner(calls),
    )

    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["runtime_entered"] is True
    assert result["platform_core_project_services_delegated"] is True
    assert result["human_interface_runtime_entry_orchestrates"] is False
    assert result["development_intent_resolution"]["development_intent_resolution_authority"] == "PLATFORM_CORE"
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    assert calls[0]["prompt"] == "Implement governance validation utility."
    assert (
        tmp_path
        / "UHI-CANONICAL"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()


def _authorization_projection(
    tmp_path: Path,
    *,
    latest_turn_status: str | None = None,
    replay_status: str | None = None,
) -> dict:
    turn_root = tmp_path / "runtime" / "TURN-000026"
    replay_reference = turn_root / "acli_governed_development_execution_bridge"
    replay_reference.mkdir(parents=True)
    if replay_status is not None:
        _write_wrapped_artifact(
            turn_root
            / "governed_bridge_certified_development_continuation"
            / "execution_authorization"
            / "002_authorization_artifact_recorded.json",
            {
                "artifact_type": "EXECUTION_AUTHORIZATION_ARTIFACT_V1",
                "authorization_status": replay_status,
            },
        )
    latest_turn = {"replay_reference": str(replay_reference)}
    if latest_turn_status is not None:
        latest_turn["execution_authorization_status"] = latest_turn_status
    return _runtime_status_projection({"failed_turns": 0}, latest_turn)


def test_governance_authorization_projection_uses_latest_turn_field(tmp_path: Path) -> None:
    projection = _authorization_projection(
        tmp_path,
        latest_turn_status="EXECUTION_AUTHORIZED",
        replay_status="EXECUTION_NOT_AUTHORIZED",
    )

    assert projection["governance_authorization_reached"] is True
    assert projection["projection_evidence"]["execution_authorization_status_source"] == (
        "LATEST_TURN"
    )


def test_governance_authorization_projection_recovers_from_replay(tmp_path: Path) -> None:
    projection = _authorization_projection(tmp_path, replay_status="EXECUTION_AUTHORIZED")

    assert projection["governance_authorization_reached"] is True
    assert projection["projection_evidence"]["execution_authorization_replay_inspected"] is True
    assert projection["projection_evidence"]["execution_authorization_status_source"] == (
        "EXECUTION_AUTHORIZATION_REPLAY"
    )


def test_governance_authorization_projection_fails_closed_without_evidence(tmp_path: Path) -> None:
    projection = _authorization_projection(tmp_path)

    assert projection["governance_authorization_reached"] is False
    assert projection["projection_evidence"]["execution_authorization_status_source"] == (
        "NOT_AVAILABLE"
    )


def test_governance_authorization_projection_rejects_non_authorized_replay(
    tmp_path: Path,
) -> None:
    projection = _authorization_projection(
        tmp_path,
        replay_status="EXECUTION_AUTHORIZATION_DENIED",
    )

    assert projection["governance_authorization_reached"] is False
    assert projection["projection_evidence"]["execution_authorization_status"] == (
        "EXECUTION_AUTHORIZATION_DENIED"
    )


def test_recovered_authorization_does_not_override_partial_runtime_binding(
    tmp_path: Path,
) -> None:
    def partially_bound_runtime(args, input_func, output_func):
        input_func("")
        output_func("runtime stopped before replay certification")
        turn_root = Path(args.runtime_root) / "runtime" / "TURN-000026"
        replay_reference = turn_root / "acli_governed_development_execution_bridge"
        replay_reference.mkdir(parents=True)
        _write_wrapped_artifact(
            turn_root
            / "governed_bridge_certified_development_continuation"
            / "execution_authorization"
            / "002_authorization_artifact_recorded.json",
            {
                "artifact_type": "EXECUTION_AUTHORIZATION_ARTIFACT_V1",
                "authorization_status": "EXECUTION_AUTHORIZED",
            },
        )
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "turns": [
                {
                    "provider_invocation_reached": True,
                    "worker_invocation_status": "WORKER_INVOKED",
                    "replay_certification_reached": False,
                    "replay_reference": str(replay_reference),
                }
            ],
        }

    result = run_human_interface_runtime_entry(
        interface_name="reference authorization replay interface",
        session_id="UHI-G25-03-AUTHORIZATION-REPLAY",
        human_requests=["Implement authorization replay projection."],
        created_at="2026-07-12T00:00:00Z",
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=partially_bound_runtime,
    )

    assert result["governance_authorization_reached"] is True
    assert result["replay_certification_reached"] is False
    assert result["canonical_runtime_entry_status"] == (
        CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_PARTIALLY_BOUND
    )


def test_canonical_runtime_entry_projects_status_from_replay_evidence(tmp_path: Path) -> None:
    def replay_backed_runtime(args, input_func, output_func):
        input_func("")
        output_func("runtime completed with replay evidence")
        universal_replay = Path(args.runtime_root) / "runtime" / "universal_provider_worker"
        certification_replay = Path(args.runtime_root) / "runtime" / "replay_certification"
        universal_replay.mkdir(parents=True)
        certification_replay.mkdir(parents=True)
        _write_wrapped_artifact(
            universal_replay / "001_universal_provider_worker_result_recorded.json",
            {
                "universal_provider_worker_status": "UNIVERSAL_PROVIDER_WORKER_COMPLETED",
                "smart_selection_executed": True,
                "provider_invocation_delegated": True,
                "certified_provider_attachment_reused": True,
                "selected_resource_id": "OPENAI",
            },
        )
        _write_wrapped_artifact(
            certification_replay / "000_replay_certification_artifact_recorded.json",
            {
                "certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                "replay_lineage_preserved": True,
            },
        )
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": False,
                    "provider_invoked": False,
                    "openai_provider_reached": False,
                    "replay_certification_reached": False,
                    "execution_authorization_status": "EXECUTION_AUTHORIZED",
                    "universal_provider_worker_replay_reference": str(universal_replay),
                    "replay_certification_replay_reference": str(certification_replay),
                    "replay_reference": str(Path(args.runtime_root) / "runtime" / "TURN-000001"),
                }
            ],
        }

    result = run_human_interface_runtime_entry(
        interface_name="reference replay projection interface",
        session_id="UHI-G18-05-REPLAY-PROJECTION",
        human_requests=["Implement replay-backed runtime projection."],
        created_at="2026-07-10T00:00:00Z",
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=replay_backed_runtime,
    )

    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["runtime_binding_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["provider_invocation_reached"] is True
    assert result["worker_execution_reached"] is True
    assert result["replay_certification_reached"] is True
    assert result["runtime_status_projection_source"] == "LATEST_TURN_AND_REPLAY_EVIDENCE"
    assert result["runtime_status_projection_evidence"]["universal_provider_worker_replay_inspected"] is True
    assert result["runtime_status_projection_evidence"]["replay_certification_replay_inspected"] is True


def test_canonical_runtime_entry_discovers_status_from_current_turn_replay_tree(
    tmp_path: Path,
) -> None:
    def turn_replay_runtime(args, input_func, output_func):
        input_func("")
        output_func("runtime completed with discovered turn replay")
        turn_root = Path(args.runtime_root) / "runtime" / "TURN-000023"
        bridge_root = turn_root / "governed_bridge_certified_development_continuation"
        worker_lifecycle = bridge_root / "worker_lifecycle_continuation"
        (turn_root / "acli_governed_development_execution_bridge").mkdir(parents=True)
        _write_wrapped_artifact(
            worker_lifecycle / "worker_invocation" / "003_invocation_result_recorded.json",
            {
                "artifact_type": "WORKER_INVOCATION_RESULT_ARTIFACT_V1",
                "runtime_version": "AIGOL_WORKER_INVOCATION_RUNTIME_V1",
                "invocation_status": "WORKER_INVOKED",
                "worker_invoked": True,
                "failure_reason": None,
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "000_universal_provider_worker_binding_recorded.json",
            {
                "binding_status": "UNIVERSAL_PROVIDER_WORKER_COMPLETED",
                "universal_provider_runtime_reached": True,
                "smart_selection_executed": True,
                "selected_resource_id": "OPENAI",
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "001_universal_provider_worker_result_recorded.json",
            {
                "universal_provider_worker_status": "FAILED_CLOSED",
                "provider_invocation_delegated": True,
                "certified_provider_attachment_reused": True,
                "selected_resource_id": "OPENAI",
                "failure_reason": "OpenAI provider unavailable",
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "universal_resource_selection"
            / "001_resource_selection_returned.json",
            {
                "selection_status": "RESOURCE_SELECTION_SUCCEEDED",
                "selected_resource_id": "OPENAI",
                "selected_role_type": "PROVIDER_ROLE",
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "selected_provider_openai"
            / "001_openai_provider_adapter_recorded.json",
            {
                "artifact_type": "OPENAI_EXTERNAL_WORKER_PROVIDER_CAPTURE_ARTIFACT_V1",
                "provider_adapter_runtime": "OPENAI_PROVIDER_ADAPTER_V1",
                "provider_invoked_inside_adapter": True,
                "provider_status": "FAILED_CLOSED",
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "selected_provider_openai"
            / "002_openai_external_worker_result_recorded.json",
            {
                "worker_status": "FAILED_CLOSED",
                "provider_invoked_inside_adapter": True,
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle
            / "universal_provider_worker"
            / "selected_provider_openai"
            / "certified_provider_attachment"
            / "002_certified_provider_attachment_recorded.json",
            {
                "provider_status": "FAILED_CLOSED",
                "provider_invoked": False,
                "failure_reason": "OpenAI provider unavailable",
            },
        )
        _write_wrapped_artifact(
            worker_lifecycle / "replay_certification" / "000_replay_certification_artifact_recorded.json",
            {
                "certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                "replay_lineage_preserved": True,
            },
        )
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": False,
                    "provider_invoked": False,
                    "openai_provider_reached": False,
                    "replay_certification_reached": False,
                    "execution_authorization_status": "EXECUTION_AUTHORIZED",
                    "replay_reference": str(
                        turn_root / "acli_governed_development_execution_bridge"
                    ),
                }
            ],
        }

    result = run_human_interface_runtime_entry(
        interface_name="reference turn replay discovery interface",
        session_id="UHI-G18-07-REPLAY-DISCOVERY",
        human_requests=["Implement turn replay discovery projection."],
        created_at="2026-07-10T00:00:00Z",
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=turn_replay_runtime,
    )

    evidence = result["runtime_status_projection_evidence"]
    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["provider_invocation_reached"] is True
    assert result["worker_execution_reached"] is True
    assert result["replay_certification_reached"] is True
    assert evidence["turn_replay_discovery_used"] is True
    assert evidence["worker_invocation_replay_inspected"] is True
    assert evidence["universal_provider_worker_binding_replay_inspected"] is True
    assert evidence["universal_provider_worker_replay_inspected"] is True
    assert evidence["resource_selection_replay_inspected"] is True
    assert evidence["selected_provider_replay_inspected"] is True
    assert evidence["certified_provider_attachment_replay_inspected"] is True
    assert evidence["replay_certification_replay_inspected"] is True
    assert evidence["worker_invocation_status"] == "WORKER_INVOKED"
    assert evidence["selected_provider_resource_id"] == "OPENAI"


def test_aicli_default_approval_uses_canonical_runtime_entry(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(aicli, "run_interactive_conversation", _runtime_runner(calls))

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G14-30",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement replay evidence utility.", "/approve", "/exit"]),
        output_writer=lambda _line: None,
    )

    runtime_result = result["runtime_result"]
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert runtime_result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert runtime_result["human_interface_runtime_entry_service_used"] is True
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"


def test_aigol_next_uses_same_canonical_runtime_entry(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []

    def presentation(**kwargs):
        return {
            "artifact_hash": "sha256:presentation",
            "command": "aigol next",
            "replay_reference": str(tmp_path / "presentation"),
            "session_id": kwargs["session_id"],
        }

    monkeypatch.setattr(aigol_cli, "run_acli_next_conversational_session", presentation)
    monkeypatch.setattr(aigol_cli, "run_interactive_conversation", _runtime_runner(calls))

    result = aigol_cli._run_acli_next_runtime_bound_session(
        session_id="AIGOL-NEXT-G14-30",
        prompts=["Implement governance validation utility."],
        created_at="2026-07-05T00:00:00Z",
        replay_dir=tmp_path,
        workspace=".",
    )

    assert result["runtime_binding_status"] == aigol_cli.ACLI_NEXT_RUNTIME_BOUND
    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["human_interface_runtime_entry_service_used"] is True
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    assert (
        tmp_path
        / "AIGOL-NEXT-G14-30"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()


def test_canonical_runtime_entry_selects_governed_bridge_before_native_routing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[str] = []

    def forbidden_native_router(**_kwargs):
        raise AssertionError("native conversational routing must not be selected")

    def bridge_proposal(**kwargs):
        calls.append("bridge_proposal")
        return {
            "bridge_status": aigol_cli.ACLI_GOVERNED_DEVELOPMENT_APPROVAL_REQUIRED,
            "workflow_id": aigol_cli.CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW,
            "approval_required": True,
            "approval_bypassed": False,
            "approval_granted": False,
            "execution_authorized": False,
            "worker_invoked": False,
            "replay_certification_reached": False,
            "replay_reference": str(kwargs["replay_dir"]),
            "workflow_capture": {
                "governed_development_replay_reference": str(kwargs["replay_dir"]),
            },
        }

    def bridge_continuation(**_kwargs):
        calls.append("bridge_continuation")
        worker_lifecycle = {
            "worker_assignment_reached": True,
            "worker_dispatch_reached": True,
            "worker_invocation_reached": True,
            "worker_execution_candidate_reached": True,
            "external_task_package_reached": True,
            "openai_provider_reached": True,
            "result_validation_reached": True,
            "replay_certification_reached": True,
            "replay_lineage_preserved": True,
            "worker_assignment": {"assignment_status": "WORKER_ASSIGNED"},
            "worker_dispatch": {"dispatch_status": "WORKER_DISPATCHED"},
            "worker_invocation": {"invocation_status": "WORKER_INVOKED"},
            "worker_execution_candidate": {"candidate_status": "WORKER_EXECUTION_CANDIDATE_CREATED"},
            "external_worker_task_package": {"task_status": "EXTERNAL_WORKER_TASK_PACKAGE_CREATED"},
            "openai_external_worker_provider": {"worker_status": "OPENAI_EXTERNAL_WORKER_COMPLETED"},
            "result_validation": {"validation_status": "RESULT_VALIDATION_COMPLETED"},
            "replay_certification": {"certification_status": "REPLAY_CERTIFICATION_COMPLETED"},
        }
        return {
            "continuation_status": "GOVERNED_DEVELOPMENT_BRIDGE_CONTINUED_TO_CERTIFIED_RUNTIME",
            "upstream_human_approval_consumed": True,
            "approval_bypassed": False,
            "post_context_continuation": {
                "continuation_status": "POST_CONTEXT_CONTINUED",
                "ppp_route_status": "PPP_ROUTE_COMPLETED",
            },
            "certified_worker_continuation": {
                "worker_request_reached": True,
                "execution_requested": True,
                "dispatch_requested": True,
                "execution_authorization": {"authorization_status": "EXECUTION_AUTHORIZED"},
                "worker_invocation_request": {
                    "request_status": "WORKER_INVOCATION_REQUEST_CREATED",
                },
                "worker_lifecycle_continuation": worker_lifecycle,
            },
            "worker_request_reached": True,
            "worker_assignment_reached": True,
            "worker_dispatch_reached": True,
            "worker_invocation_reached": True,
            "worker_execution_candidate_reached": True,
            "external_task_package_reached": True,
            "openai_provider_reached": True,
            "result_validation_reached": True,
            "replay_certification_reached": True,
            "replay_lineage_preserved": True,
            "fail_closed": False,
            "failure_reason": None,
        }

    monkeypatch.setattr(aigol_cli, "route_conversational_cli_intent", forbidden_native_router)
    monkeypatch.setattr(aigol_cli, "propose_acli_governed_development_execution", bridge_proposal)
    monkeypatch.setattr(
        aigol_cli,
        "_continue_governed_development_bridge_to_certified_runtime",
        bridge_continuation,
    )
    monkeypatch.setattr(
        aigol_cli,
        "render_acli_governed_development_bridge_summary",
        lambda capture: f"bridge_status: {capture.get('bridge_status')}",
    )

    result = aigol_cli.run_interactive_conversation(
        argparse.Namespace(
            session_id="UHI-BRIDGE-SELECTION",
            created_at="2026-07-10T00:00:00Z",
            runtime_root=str(tmp_path),
            workspace=".",
            operator_context="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            auto_continue=True,
            enable_llm_assisted_explanation=False,
            llm_explanation_provider_id="UNSPECIFIED_EXPLANATION_PROVIDER",
        ),
        input_func=_reader(["Implement runtime worker utility.", "exit"]),
        output_func=lambda _line: None,
    )

    assert calls == ["bridge_proposal", "bridge_continuation"]
    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_source"] == "ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE"
    assert result["turns"][0]["conversational_workflow_id"] == (
        aigol_cli.CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW
    )
    assert result["turns"][0]["worker_invoked"] is True
    assert result["turns"][0]["replay_certification_reached"] is True


def test_governed_bridge_summary_binds_worker_continuation_envelope() -> None:
    summary = aigol_cli._interactive_acli_governed_development_bridge_turn_summary(
        turn_id="TURN-000001",
        prompt_id="PROMPT-000001",
        router_capture={
            "source_of_truth_router_artifact": {
                "selected_source": "GOVERNED_DEVELOPMENT",
                "selection_reason": "canonical Human Interface runtime entry",
            }
        },
        bridge_capture={
            "bridge_status": "GOVERNED_DEVELOPMENT_BRIDGE_CERTIFIED_RUNTIME_COMPLETED",
            "workflow_id": aigol_cli.CONVERSATIONAL_GOVERNED_DEVELOPMENT_WORKFLOW,
            "approval_granted": True,
            "execution_authorized": True,
            "worker_invoked": False,
            "replay_reference": "runtime/turn/acli_governed_development_execution_bridge",
            "certified_development_continuation": {
                "worker_request_reached": True,
                "worker_assignment_reached": True,
                "worker_dispatch_reached": True,
                "worker_invocation_reached": True,
                "worker_execution_candidate_reached": True,
                "external_task_package_reached": True,
                "openai_provider_reached": True,
                "result_validation_reached": True,
                "replay_certification_reached": True,
                "replay_lineage_preserved": True,
                "certified_worker_continuation": {
                    "execution_authorization": {"authorization_status": "EXECUTION_AUTHORIZED"},
                    "worker_invocation_request": {
                        "request_status": "WORKER_INVOCATION_REQUEST_CREATED",
                    },
                    "worker_lifecycle_continuation": {
                        "worker_invocation": {"invocation_status": "WORKER_INVOKED"},
                        "result_validation": {"validation_status": "RESULT_VALIDATION_COMPLETED"},
                        "replay_certification": {
                            "certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                        },
                    },
                },
            },
        },
        source_router_replay_reference="runtime/turn/source_router",
    )

    assert summary["worker_invoked"] is True
    assert summary["worker_invocation_reached"] is True
    assert summary["external_task_package_reached"] is True
    assert summary["result_validation_reached"] is True
    assert summary["replay_certification_reached"] is True
    assert summary["replay_lineage_preserved"] is True


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _write_wrapped_artifact(path: Path, artifact: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"artifact": artifact}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
