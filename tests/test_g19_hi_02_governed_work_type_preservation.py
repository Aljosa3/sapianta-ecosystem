from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
    run_human_interface_runtime_entry,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    resolve_development_intent,
)


CREATED_AT = "2026-07-11T00:00:00Z"


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


def test_audit_only_implementation_prompt_fails_closed_before_approval() -> None:
    result = resolve_development_intent(
        message=(
            "Implement governance validation utility.\n\n"
            "work_type: AUDIT_ONLY\n"
            "Do not implement or modify runtime behavior."
        )
    )

    assert result["requested_work_type"] == "AUDIT_ONLY"
    assert result["prepared_work_type"] == "IMPLEMENTATION"
    assert result["mutation_allowed"] is False
    assert result["runtime_implementation"] is False
    assert result["work_type_conflict_detected"] is True
    assert result["summary_admissible"] is False
    assert result["runtime_binding_admissible"] is False


def test_aicli_clarification_preserves_audit_only_work_type_without_runtime(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []
    session_id = "G19-HI-02-AUDIT-CLARIFICATION"
    original = (
        "I have an idea but need clarification.\n\n"
        "This is an AUDIT-ONLY governance task.\n"
        "Do not implement or modify runtime behavior."
    )
    reply = (
        "The outcome should improve governance audit evidence and preserve replay "
        "boundaries for human interface work."
    )

    result = aicli.run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader([original, "/send", reply, "/send", "/approve", "/exit"]),
        output_writer=lambda _line: None,
        runtime_runner=lambda **kwargs: calls.append(kwargs) or {},
    )

    contexts = _contexts(tmp_path, session_id)
    first_resolution = contexts[0]["development_intent_resolution"]
    resolved = contexts[1]["development_intent_resolution"]

    assert first_resolution["requested_work_type"] == "AUDIT_ONLY"
    assert contexts[0]["human_conversation_experience"]["requested_work_type"] == "AUDIT_ONLY"
    assert resolved["clarification_resolved"] is True
    assert resolved["requested_work_type"] == "AUDIT_ONLY"
    assert resolved["work_type"] == "AUDIT_ONLY"
    assert resolved["mutation_allowed"] is False
    assert resolved["runtime_implementation"] is False
    assert resolved["summary_admissible"] is False
    assert resolved["runtime_binding_admissible"] is False
    assert "Implement the clarification-resolved" not in resolved["canonical_runtime_prompt"]
    assert result["runtime_entered"] is False
    assert calls == []


def test_explicit_implementation_work_type_can_reach_approval() -> None:
    result = resolve_development_intent(
        message="Implement governance validation utility.\n\nwork_type: IMPLEMENTATION"
    )

    assert result["requested_work_type"] == "IMPLEMENTATION"
    assert result["prepared_work_type"] == "IMPLEMENTATION"
    assert result["summary_admissible"] is True
    assert result["runtime_binding_admissible"] is True


def test_non_implementation_work_types_are_preserved_without_runtime(tmp_path: Path) -> None:
    scenarios = ("REVIEW", "CERTIFICATION", "ANALYSIS", "DOCUMENTATION")

    for work_type in scenarios:
        context = prepare_unified_human_interface_project_context(
            interface_name="test",
            session_id=f"G19-HI-02-{work_type}",
            message=(
                "I have an idea to improve governance documentation.\n\n"
                f"work_type: {work_type}"
            ),
            runtime_root=tmp_path,
            workspace=".",
            created_at=CREATED_AT,
        )
        resolution = context["development_intent_resolution"]
        approval = context["human_conversation_experience"]["approval_summary"]

        assert resolution["requested_work_type"] == work_type
        assert resolution["work_type"] == work_type
        assert resolution["mutation_allowed"] is False
        assert resolution["runtime_implementation"] is False
        assert resolution["summary_admissible"] is False
        assert resolution["runtime_binding_admissible"] is False
        assert approval["requested_work_type"] == work_type
        assert approval["runtime_after_approval"] is None


def test_runtime_entry_refuses_non_mutating_work_type(tmp_path: Path) -> None:
    calls: list[dict] = []

    def runner(*_args, **_kwargs):
        calls.append({"called": True})
        return {}

    result = run_human_interface_runtime_entry(
        interface_name="test",
        session_id="G19-HI-02-RUNTIME-GUARD",
        human_requests=[
            "Implement governance validation utility.\n\n"
            "work_type: AUDIT_ONLY\n"
            "Do not implement or modify runtime behavior."
        ],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=runner,
    )

    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED
    assert result["runtime_entered"] is False
    assert result["development_intent_resolution"]["requested_work_type"] == "AUDIT_ONLY"
    assert result["development_intent_resolution"]["runtime_binding_admissible"] is False
    assert calls == []


def test_new_governed_work_classification_does_not_override_work_type(tmp_path: Path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G19-HI-02-NEW-GOVERNED-WORK",
        message=(
            "I have an idea to improve an unregistered widget capability.\n\n"
            "work_type: REVIEW"
        ),
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )

    resolution = context["development_intent_resolution"]
    knowledge = context["knowledge_reuse"]

    assert knowledge["classification"] == "NEW_GOVERNED_WORK"
    assert resolution["requested_work_type"] == "REVIEW"
    assert resolution["knowledge_reuse_classification_is_work_type"] is False
    assert resolution["runtime_binding_admissible"] is False
