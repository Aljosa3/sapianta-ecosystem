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
            "runtime_replay_reference": "/tmp/g15-hir-10-runtime/TURN-000001",
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


def _workspace_states(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "workspace_state").glob("*.json"))
    ]


def _continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (runtime_root / session_id / "uhi_clarification_continuity").glob("*.json")
        )
    ]


def _conversation(context: dict) -> dict:
    conversation = context["human_conversation_experience"]
    assert isinstance(conversation, dict)
    return conversation


def _plan(context: dict) -> dict:
    plan = _conversation(context)["deterministic_clarification_plan"]
    assert isinstance(plan, dict)
    return plan


def test_direct_answer_satisfies_open_architecture_outcome_slot(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    session_id = "G15-HIR-10-SATISFIED"
    answer = "The outcome is a reusable Platform Core behavior shared by all Human Interfaces."

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader([answer, "/send", "/approve"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _contexts(tmp_path, session_id)
    first_conversation = _conversation(contexts[0])
    resolved_conversation = _conversation(contexts[1])
    resolution = contexts[1]["development_intent_resolution"]
    satisfaction = resolution["clarification_satisfaction_verification"]
    continuity = _continuity(tmp_path, session_id)[0]
    workspace_states = _workspace_states(tmp_path, session_id)

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["clarification_question_count"] == 1
    assert "\n".join(output).count("Clarification required before governed execution.") == 1
    assert first_conversation["clarification_questions"] == [
        "What outcome should the human interface architecture decision enable?"
    ]
    assert resolved_conversation["clarification_questions"] == []
    assert satisfaction["open_semantic_slot"] == "architecture_outcome"
    assert satisfaction["clarification_satisfied"] is True
    assert satisfaction["satisfied_semantic_slots"] == ["architecture_outcome"]
    assert satisfaction["pending_semantic_slots"] == []
    assert resolution["clarification_resolved"] is True
    assert resolution["answered_clarification_question_ids"] == satisfaction[
        "satisfied_question_ids"
    ]
    assert continuity["clarification_satisfaction_verification"] == satisfaction
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert calls
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


def test_insufficient_answer_records_missing_slot_without_repeating_identical_question(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    session_id = "G15-HIR-10-INSUFFICIENT"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader(["Yes, that one.", "/send", "/cancel"]),
        output_writer=output.append,
    )

    contexts = _contexts(tmp_path, session_id)
    first_question = _conversation(contexts[0])["clarification_questions"][0]
    second_conversation = _conversation(contexts[1])
    second_question = second_conversation["clarification_questions"][0]
    second_plan = _plan(contexts[1])
    resolution = contexts[1]["development_intent_resolution"]
    satisfaction = resolution["clarification_satisfaction_verification"]
    continuity = _continuity(tmp_path, session_id)[0]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert result["clarification_question_count"] == 2
    assert "\n".join(output).count("Clarification required before governed execution.") == 2
    assert first_question == "What outcome should the human interface architecture decision enable?"
    assert second_question != first_question
    assert second_question.startswith("I still need the architecture outcome")
    assert "State the reusable behavior or interface outcome it should enable." in second_question
    assert satisfaction["open_semantic_slot"] == "architecture_outcome"
    assert satisfaction["clarification_satisfied"] is False
    assert satisfaction["pending_semantic_slots"] == ["architecture_outcome"]
    assert satisfaction["missing_information"] == "architecture outcome"
    assert satisfaction["identical_question_repeated"] is False
    assert resolution["clarification_resolved"] is False
    assert resolution["answered_clarification_question_ids"] == []
    assert second_plan["selected_missing_slot"] == "architecture_outcome"
    assert second_plan["missing_semantic_slots"][0]["followup_after_insufficient_answer"] is True
    assert continuity["pending_semantic_slots"] == ["architecture_outcome"]
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
