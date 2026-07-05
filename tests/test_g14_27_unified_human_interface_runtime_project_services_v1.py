from __future__ import annotations

from pathlib import Path

from aigol.cli import aigol_cli


def test_aigol_next_runtime_binding_uses_platform_core_project_services(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def presentation(**kwargs):
        return {
            "artifact_hash": "sha256:presentation",
            "command": "aigol next",
            "replay_reference": str(tmp_path / "presentation"),
            "session_id": kwargs["session_id"],
        }

    def runtime(_args, input_func, output_func):
        prompt = input_func("")
        output_func("runtime accepted")
        assert "GitHub Actions" in prompt
        return {
            "command": "aigol conversation",
            "runtime_root": str(tmp_path),
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
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
                    "replay_reference": str(tmp_path / "runtime" / "TURN-000001"),
                    "execution_summary_reference": "summary",
                    "human_confirmation_reference": "approval",
                }
            ],
        }

    monkeypatch.setattr(aigol_cli, "run_acli_next_conversational_session", presentation)
    monkeypatch.setattr(aigol_cli, "run_interactive_conversation", runtime)

    result = aigol_cli._run_acli_next_runtime_bound_session(
        session_id="AIGOL-NEXT-UHI-CONTEXT",
        prompts=["I want AiGOL Next to support GitHub Actions."],
        created_at="2026-07-04T00:00:00Z",
        replay_dir=tmp_path,
        workspace=".",
    )

    context = result["platform_core_project_services_context"]
    assert result["runtime_binding_status"] == aigol_cli.ACLI_NEXT_RUNTIME_BOUND
    assert context["artifact_type"] == "UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1"
    assert context["project_workspace_authority"] == "PLATFORM_CORE"
    assert context["project_guidance_authority"] == "PLATFORM_CORE"
    assert context["project_knowledge_reuse_authority"] == "PLATFORM_CORE"
    assert context["development_intent_resolution_authority"] == "PLATFORM_CORE"
    assert context["knowledge_reuse"]["mapping_source"] == "deterministic_workspace_state"
    assert result["project_workspace_replay_reference"].endswith("workspace_state")
    assert (
        tmp_path
        / "AIGOL-NEXT-UHI-CONTEXT"
        / "uhi_project_services"
        / "001_uhi_project_context_recorded.json"
    ).exists()
    assert (
        tmp_path
        / "AIGOL-NEXT-UHI-CONTEXT"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()
