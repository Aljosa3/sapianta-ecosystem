from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def _contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (runtime_root / session_id / "uhi_clarification_continuity").glob("*.json")
        )
    ]


def _workspace_states(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "workspace_state").glob("*.json"))
    ]


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
            "runtime_replay_reference": "/tmp/g19-hi-04-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def test_accepted_architecture_answer_creates_completion_transition(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    session_id = "G19-HI-04-ARCHITECTURE-COMPLETION"
    answer = "The outcome is a reusable Platform Core behavior shared by all Human Interfaces."

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader([answer, "/send", "/approve"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _contexts(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]
    continuity = _continuity(tmp_path, session_id)[0]
    workspace_states = _workspace_states(tmp_path, session_id)

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert resolution["clarification_completed"] is True
    assert resolution["clarification_completion_status"] == "CLARIFICATION_COMPLETED"
    assert resolution["clarification_resolved"] is True
    assert resolution["pending_semantic_slots"] == []
    assert resolution["remaining_clarification_questions"] == []
    assert continuity["clarification_completion_status"] == "CLARIFICATION_COMPLETED"
    assert continuity["clarification_completed"] is True
    assert continuity["completed_clarification_question_ids"]
    assert continuity["pending_semantic_slots"] == []
    assert continuity["remaining_clarification_questions"] == []
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert workspace_states[-1]["completed_clarification_count"] >= 1
    assert workspace_states[-1]["latest_clarification_completion_transition"][
        "clarification_completed"
    ] is True
    assert calls


def test_completion_is_independent_of_non_mutating_downstream_admissibility(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    output: list[str] = []
    session_id = "G19-HI-04-AUDIT-COMPLETION"
    original = (
        "I have an idea but need clarification.\n\n"
        "work_type: AUDIT_ONLY\n"
        "Do not implement or modify runtime behavior."
    )
    answer = (
        "The outcome should improve governance audit evidence and preserve replay "
        "boundaries for human interface work."
    )

    result = aicli.run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader([original, "/send", answer, "/send", "/approve", "/exit"]),
        output_writer=output.append,
        runtime_runner=lambda **kwargs: calls.append(kwargs) or {},
    )

    contexts = _contexts(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]
    continuity = _continuity(tmp_path, session_id)[0]
    workspace_states = _workspace_states(tmp_path, session_id)
    rendered = "\n".join(output)

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert resolution["summary_admissible"] is False
    assert resolution["runtime_binding_admissible"] is False
    assert resolution["clarification_completed"] is True
    assert resolution["clarification_completion_status"] == "CLARIFICATION_COMPLETED"
    assert resolution["clarification_required"] is False
    assert continuity["clarification_completed"] is True
    assert continuity["clarification_completion_transition"][
        "downstream_intent_admissibility_required"
    ] is False
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert rendered.count("Clarification required before governed execution.") == 1
    assert "I still need" not in rendered
    assert result["runtime_entered"] is False
    assert calls == []


def test_insufficient_answer_does_not_complete_pending_clarification(
    tmp_path: Path,
) -> None:
    session_id = "G19-HI-04-INSUFFICIENT"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface behavior belong in Platform Core architecture?",
        input_reader=_reader(["Yes, that one.", "/send", "/cancel"]),
        output_writer=lambda _line: None,
    )

    contexts = _contexts(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]
    continuity = _continuity(tmp_path, session_id)[0]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_CANCELED"
    assert resolution["clarification_completed"] is False
    assert resolution["clarification_completion_status"] == "CLARIFICATION_COMPLETION_STILL_REQUIRED"
    assert resolution["clarification_resolved"] is False
    assert continuity["clarification_completed"] is False
    assert continuity["pending_semantic_slots"] == ["architecture_outcome"]
