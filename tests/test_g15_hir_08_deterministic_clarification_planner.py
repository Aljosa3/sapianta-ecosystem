from __future__ import annotations

import json
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
            "runtime_replay_reference": "/tmp/g15-hir-08-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def _contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _conversation(context: dict) -> dict:
    conversation = context["human_conversation_experience"]
    assert isinstance(conversation, dict)
    return conversation


def _plan(context: dict) -> dict:
    plan = _conversation(context)["deterministic_clarification_plan"]
    assert isinstance(plan, dict)
    return plan


def test_vague_opener_uses_planner_and_asks_exactly_one_high_value_question(tmp_path: Path) -> None:
    output: list[str] = []

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-HIR-08-VAGUE-OPENER",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["/cancel"]),
        output_writer=output.append,
    )

    context = _contexts(tmp_path, "G15-HIR-08-VAGUE-OPENER")[0]
    conversation = _conversation(context)
    plan = _plan(context)

    assert result["clarification_question_count"] == 1
    assert conversation["clarification_question_count"] == 1
    assert plan["asks_exactly_one_question"] is True
    assert plan["generic_template_used"] is False
    assert plan["selected_missing_slot"] == "capability_target"
    assert conversation["clarification_questions"] == [
        "What outcome should improve runtime, clarification quality, replay behavior, or another governed capability?"
    ]
    assert "\n".join(output).count("- ") == 1


def test_existing_workspace_context_suppresses_unnecessary_continuation_clarification(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    runner = _successful_runner(calls)

    first = aicli.run_reference_uhi_submit_session(
        session_id="G15-HIR-08-CONTEXT",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Implement replay validation support.",
        input_reader=_reader(["/approve"]),
        output_writer=lambda _line: None,
        runtime_runner=runner,
    )
    second = aicli.run_reference_uhi_submit_session(
        session_id="G15-HIR-08-CONTEXT",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Continue this governed workflow.",
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
        runtime_runner=runner,
    )

    second_context = _contexts(tmp_path, "G15-HIR-08-CONTEXT")[-1]
    conversation = _conversation(second_context)
    plan = _plan(second_context)

    assert first["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert second["clarification_question_count"] == 0
    assert conversation["response_mode"] == "APPROVAL_PREPARATION"
    assert conversation["clarification_questions"] == []
    assert plan["clarification_question_count"] == 0
    assert plan["selected_missing_slot"] is None
    assert second["aicli_authorizes"] is False
    assert second["aicli_executes"] is False
    assert second["aicli_owns_replay"] is False


def test_previously_answered_clarification_is_not_repeated(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    reply = (
        "Change clarification state management so answered questions are recorded "
        "as reusable Platform Core behavior."
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-HIR-08-NO-REPEAT",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface clarification behavior belong in Platform Core architecture?",
        input_reader=_reader([reply, "/send", "/approve"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _contexts(tmp_path, "G15-HIR-08-NO-REPEAT")
    first_conversation = _conversation(contexts[0])
    resolved_conversation = _conversation(contexts[1])
    resolved_plan = _plan(contexts[1])
    resolution = contexts[1]["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["clarification_question_count"] == 1
    assert "\n".join(output).count("Clarification required before governed execution.") == 1
    assert resolution["clarification_resolved"] is True
    assert resolution["answered_clarification_question_ids"]
    assert resolved_conversation["response_mode"] == "APPROVAL_PREPARATION"
    assert resolved_conversation["clarification_questions"] == []
    assert resolved_plan["clarification_questions"] == []
    assert resolved_plan["selected_clarification_question"] not in first_conversation["clarification_questions"]


def test_architecture_question_targets_smallest_remaining_semantic_gap(tmp_path: Path) -> None:
    result = aicli.run_reference_uhi_submit_session(
        session_id="G15-HIR-08-SMALLEST-GAP",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this behavior belong in Platform Core architecture?",
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
    )

    context = _contexts(tmp_path, "G15-HIR-08-SMALLEST-GAP")[0]
    conversation = _conversation(context)
    plan = _plan(context)

    assert result["clarification_question_count"] == 1
    assert plan["selected_missing_slot"] in {"architecture_subject", "architecture_outcome"}
    assert plan["clarification_question_count"] == 1
    assert conversation["clarification_questions"] == plan["clarification_questions"]
    assert "What should change next?" not in conversation["clarification_questions"]
    assert plan["platform_core_owns_clarification_semantics"] is True
    assert plan["human_interface_authority"] is False
