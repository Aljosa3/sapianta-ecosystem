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


def test_aicli_renders_platform_core_clarification_without_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-CLARIFY",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Improve project.", "/exit"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    assert result["clarification_question_count"] == 1
    assert result["runtime_entered"] is False
    assert calls == []
    assert any("Clarification required before governed execution." in line for line in output)
    assert result["development_intent_resolution"]["development_intent_resolution_authority"] == "PLATFORM_CORE"


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
        input_reader=_reader(["Improve project.", "/exit"]),
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
    assert "resolve_development_intent(" in source
    assert "run_interactive_conversation(" in source
