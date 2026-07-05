from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _successful_runner(calls: list[dict]):
    def run(**kwargs):
        calls.append(kwargs)
        return {
            "runtime_binding_status": aicli.REFERENCE_UHI_BOUND,
            "runtime_entered": True,
            "governance_authorization_reached": True,
            "provider_invocation_reached": True,
            "worker_execution_reached": True,
            "replay_certification_reached": True,
            "runtime_replay_reference": "/tmp/aicli-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def test_aicli_approval_delegates_to_certified_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-TEST",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement governance validation utility.", "/approve", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert result["runtime_entered"] is True
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert calls[0]["prompt"] == "Implement governance validation utility."
    assert any("Governed implementation summary" in line for line in output)
    assert any("Certified runtime result" in line for line in output)
    assert result["platform_core_project_services_context"]["project_guidance_authority"] == "PLATFORM_CORE"
    assert result["project_workspace_replay_reference"].endswith("workspace_state")
    assert (
        tmp_path
        / "AICLI-TEST"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()


def test_aicli_restores_platform_core_workspace_state_across_sessions(tmp_path: Path) -> None:
    first_calls: list[dict] = []
    aicli.run_reference_uhi_session(
        session_id="AICLI-CONTINUITY",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["I want AiGOL Next to support GitHub Actions.", "/approve", "/exit"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(first_calls),
    )

    second_calls: list[dict] = []
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="AICLI-CONTINUITY",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Continue the mobile interface.", "/approve", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(second_calls),
    )

    context = result["platform_core_project_services_context"]
    assert context["project_workspace_restored"] is True
    assert context["project_workspace_authority"] == "PLATFORM_CORE"
    assert context["project_guidance_authority"] == "PLATFORM_CORE"
    assert context["project_knowledge_reuse_authority"] == "PLATFORM_CORE"
    assert context["knowledge_reuse"]["mapping_source"] == "deterministic_workspace_state"
    assert result["aicli_owns_workspace"] is False
    assert any("Platform Core project context" in line for line in output)


def test_aicli_renders_platform_core_clarification_without_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-CLARIFY",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Improve project.", "/send", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["clarification_question_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []
    assert any("Clarification required before governed execution." in line for line in output)
    assert result["development_intent_resolution"]["development_intent_resolution_authority"] == "PLATFORM_CORE"


def test_aicli_multiline_composer_submits_one_complete_request(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    request_lines = [
        "Implement governance validation utility.",
        "",
        "Requirements:",
        "- preserve replay evidence",
        "- add deterministic reporting",
    ]

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-MULTILINE",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader([*request_lines, "/send", "/approve", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 1
    assert result["multiline_request_count"] == 1
    assert result["submitted_message_count"] == 1
    assert calls[0]["prompt"] == "\n".join(request_lines)
    assert result["development_intent_resolution"]["raw_prompt"] == "\n".join(request_lines)
    assert any("Request submitted to Platform Core." in line for line in output)
    assert (
        tmp_path
        / "AICLI-MULTILINE"
        / "uhi_project_services"
        / "001_uhi_project_context_recorded.json"
    ).exists()


def test_aicli_dot_submits_composed_request(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-DOT",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement replay summary utility.", ".", "/approve", "/exit"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 1
    assert result["runtime_entered"] is True
    assert calls[0]["prompt"] == "Implement replay summary utility."


def test_aicli_cancel_clears_compose_buffer_without_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-CANCEL",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement discarded utility.", "/cancel", "/exit"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    assert result["submitted_request_count"] == 0
    assert result["canceled_compose_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []


def test_aicli_reference_scenarios_share_same_runtime_runner(tmp_path: Path) -> None:
    scenarios = {
        "A_new_implementation": "Implement governance validation utility.",
        "B_improve_existing_implementation": "Improve provider availability handling.",
        "C_extend_certified_capability": "Extend certified replay capability with a summary utility.",
        "E_resume_project": "Implement workspace resume support.",
        "F_knowledge_reuse": "I want AiGOL Next to support GitHub Actions.",
        "G_replay_generation": "Implement replay summary utility.",
    }
    calls: list[dict] = []

    for index, prompt in enumerate(scenarios.values(), start=1):
        aicli.run_reference_uhi_session(
            session_id=f"AICLI-SCENARIO-{index}",
            runtime_root=tmp_path / f"scenario-{index}",
            workspace=".",
            input_reader=_reader([prompt, "/approve", "/exit"]),
            output_writer=lambda _line: None,
            runtime_runner=_successful_runner(calls),
        )

    assert len(calls) == len(scenarios)
    assert {call["workspace"] for call in calls} == {"."}
    assert all(call["prompt"] for call in calls)


def test_aicli_clarification_scenario_does_not_enter_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-SCENARIO-D",
        runtime_root=tmp_path / "scenario-d",
        workspace=".",
        input_reader=_reader(["Improve project.", "/send", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["clarification_question_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []
    assert any("Clarification required before governed execution." in line for line in output)


def test_aicli_source_remains_thin_adapter() -> None:
    source = Path("aigol/cli/aicli.py").read_text()

    forbidden = [
        "openai_provider_metadata(",
        "OpenAIProviderAdapter(",
        "ProviderRegistry(",
        "run_provider_attachment(",
        "authorize_dispatch(",
        "run_governed_operation_command(",
        "build_persistent_workspace_state_artifact(",
        "project_knowledge_context_from_workspace(",
        "goal_mapping_from_workspace(",
    ]

    for token in forbidden:
        assert token not in source
    assert "prepare_unified_human_interface_project_context(" in source
    assert "record_unified_human_interface_workspace_state(" in source
    assert "run_interactive_conversation(" in source
