"""Regression coverage for the G47 Objective Inference intake repair."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_project_objective_inference import (
    OBJECTIVE_AMBIGUOUS,
    OBJECTIVE_INSUFFICIENT,
    OBJECTIVE_SUFFICIENT,
)


CREATED_AT = "2026-07-29T00:00:00Z"


def _context(tmp_path: Path, request: str, session_id: str) -> dict:
    workspace = tmp_path / f"{session_id}-workspace"
    workspace.mkdir()
    (workspace / ".git").mkdir()
    return prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=request,
        runtime_root=tmp_path / f"{session_id}-runtime",
        workspace=workspace,
        created_at=CREATED_AT,
    )


@pytest.mark.parametrize(
    ("prompt", "session_id"),
    (
        (
            "Extend runtime binding coverage for native development.",
            "G47-R01-EXTEND",
        ),
        (
            "Refactor message composer buffer handling.",
            "G47-R01-REFACTOR",
        ),
        (
            "I want AiGOL Next to support GitHub Actions.",
            "G47-R01-SUPPORT",
        ),
        (
            "Fix the failing addition test in calc.py and test_calc.py. "
            "Return a minimal unified diff only; do not edit files.",
            "G47-R01-FIX",
        ),
    ),
)
def test_historical_implementation_forms_produce_valid_governance_intake(
    tmp_path: Path,
    prompt: str,
    session_id: str,
) -> None:
    context = _context(tmp_path, prompt, session_id)
    objective = context["project_objective_inference"]
    governance = context["constitutional_development_governance"]

    assert objective["objective_status"] == OBJECTIVE_SUFFICIENT
    assert objective["objective_sufficient"] is True
    assert objective["canonical_project_objective"]
    assert governance["planning_eligible"] is True
    assert governance["governance_disposition"] == "BOUNDED_PLANNING_PERMITTED"
    assert context["canonical_implementation_turn_binding"] is not None


def test_insufficient_objective_uses_existing_clarification_without_task_intake(
    tmp_path: Path,
) -> None:
    context = _context(
        tmp_path,
        "Enhance message composer buffer handling.",
        "G47-R01-INSUFFICIENT",
    )
    objective = context["project_objective_inference"]
    intent = context["development_intent_resolution"]

    assert objective["objective_status"] == OBJECTIVE_INSUFFICIENT
    assert objective["objective_sufficient"] is False
    assert objective["canonical_project_objective"] == ""
    assert intent["clarification_required"] is True
    assert intent["summary_admissible"] is False
    assert context["human_conversation_experience"]["response_mode"] == "CLARIFICATION"
    assert context["constitutional_development_governance"] is None
    assert context["canonical_implementation_turn_binding"] is None


def test_generation_47_certification_record_is_metadata_only() -> None:
    record = lookup_platform_capability_certification(
        "CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE"
    )

    assert record["certification_status"] == "CERTIFIED"
    assert record["certification_scope"] == "END_TO_END"
    assert record["certification_milestone"] == "G47-FINAL"
    assert record["certification_evidence"] == (
        "docs/governance/G47_FINAL_CONSTITUTIONAL_CLOSURE_REPORT.md",
    )
    assert record["governance_metadata_only"] is True
    assert record["runtime_execution_authority"] is False
    assert record["human_interface_authority"] is False
    assert record["replay_modified"] is False
    assert record["governance_modified"] is False


def test_ambiguous_objective_uses_existing_clarification_without_task_intake(
    tmp_path: Path,
) -> None:
    context = _context(
        tmp_path,
        "Implement replay validation support.",
        "G47-R01-AMBIGUOUS",
    )
    objective = context["project_objective_inference"]
    intent = context["development_intent_resolution"]

    assert objective["objective_status"] == OBJECTIVE_AMBIGUOUS
    assert objective["objective_sufficient"] is False
    assert intent["clarification_required"] is True
    assert intent["summary_admissible"] is False
    assert context["human_conversation_experience"]["response_mode"] == "CLARIFICATION"
    assert context["constitutional_development_governance"] is None
    assert context["canonical_implementation_turn_binding"] is None
