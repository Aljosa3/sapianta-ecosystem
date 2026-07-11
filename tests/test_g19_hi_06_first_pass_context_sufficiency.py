from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


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


def test_original_request_satisfies_architecture_outcome_before_clarification(
    tmp_path: Path,
) -> None:
    prompt = (
        "Perform an AUDIT_ONLY analysis. The preferred conclusion is that Human "
        "Interfaces require only minimal bindings to Generation 19 Platform Core "
        "services and can become nearly stateless presentation adapters while "
        "Platform Core owns all Platform semantics."
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id="G19-HI-06-SUFFICIENT-ARCHITECTURE-OUTCOME",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: prompt,
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
    )

    context = _contexts(tmp_path, "G19-HI-06-SUFFICIENT-ARCHITECTURE-OUTCOME")[0]
    resolution = context["development_intent_resolution"]
    conversation = _conversation(context)
    plan = _plan(context)
    sufficiency = plan["clarification_context_sufficiency_evaluation"]

    assert result["clarification_question_count"] == 0
    assert result["pending_approval"] is False
    assert resolution["work_type"] == "AUDIT_ONLY"
    assert resolution["mutation_allowed"] is False
    assert resolution["clarification_required_before_context_sufficiency"] is True
    assert resolution["clarification_required"] is False
    assert resolution["clarification_suppressed_by_context_sufficiency"] is True
    assert conversation["response_mode"] == "INFORMATIONAL"
    assert conversation["clarification_questions"] == []
    assert plan["clarification_required_after_sufficiency"] is False
    assert plan["selected_missing_slot"] is None
    assert plan["clarification_questions"] == []
    assert "architecture_outcome" in [
        slot["slot_id"] for slot in plan["candidate_missing_semantic_slots"]
    ]
    assert sufficiency["satisfied_semantic_slots"] == ["architecture_outcome"]
    assert sufficiency["remaining_missing_slots"] == []
    assert sufficiency["platform_core_owns_sufficiency"] is True
    assert sufficiency["human_interface_authority"] is False
    assert sufficiency["llm_reasoning_used"] is False
    assert sufficiency["probabilistic_matching_used"] is False


def test_architecture_outcome_is_still_requested_when_context_is_insufficient(
    tmp_path: Path,
) -> None:
    result = aicli.run_reference_uhi_submit_session(
        session_id="G19-HI-06-INSUFFICIENT-ARCHITECTURE-OUTCOME",
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
    )

    context = _contexts(tmp_path, "G19-HI-06-INSUFFICIENT-ARCHITECTURE-OUTCOME")[0]
    resolution = context["development_intent_resolution"]
    conversation = _conversation(context)
    plan = _plan(context)
    sufficiency = plan["clarification_context_sufficiency_evaluation"]

    assert result["clarification_question_count"] == 1
    assert resolution["clarification_required"] is True
    assert resolution["clarification_required_after_context_sufficiency"] is True
    assert conversation["response_mode"] == "CLARIFICATION"
    assert conversation["clarification_questions"] == [
        "What outcome should the human interface architecture decision enable?"
    ]
    assert plan["selected_missing_slot"] == "architecture_outcome"
    assert sufficiency["satisfied_semantic_slots"] == []
    assert sufficiency["remaining_missing_slots"][0]["slot_id"] == "architecture_outcome"
    assert sufficiency["clarification_required_after_sufficiency"] is True
