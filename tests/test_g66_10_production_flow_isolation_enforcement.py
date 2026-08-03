"""Focused G66-10 production flow-isolation enforcement tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.cli.aicli import run_reference_uhi_submit_session
from aigol.runtime import platform_core_project_services as project_services
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_conversation_flow_binding import (
    CFA_DEVELOPMENT_GOVERNANCE,
    CFA_EXECUTION,
    CFA_OBJECTIVE_COMMITMENT,
    CFA_PLATFORM_KNOWLEDGE,
    CFA_SELF_KNOWLEDGE,
    compose_production_conversation_flow_binding_v1,
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.transport.serialization import load_json


CREATED_AT = "2026-08-03T16:00:00Z"


def _submit(tmp_path: Path, request: str, *, session: str) -> dict:
    return run_reference_uhi_submit_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: request,
        input_reader=lambda _prompt: (_ for _ in ()).throw(EOFError()),
        output_writer=lambda _line: None,
    )


def _compose(tmp_path: Path, request: str, *, session: str) -> dict:
    return compose_production_conversation_flow_binding_v1(
        interface_identity="G66-10-TEST-INTERFACE",
        session_identity=session,
        request_text=request,
        runtime_root=tmp_path,
        workspace_identity=".",
        created_at=CREATED_AT,
        prior_workspace_state=None,
    )


@pytest.mark.parametrize(
    ("human_text", "target"),
    [
        ("Show architecture.", CFA_SELF_KNOWLEDGE),
        ("What platform capabilities are available?", CFA_PLATFORM_KNOWLEDGE),
        ("I have an idea.", CFA_PLATFORM_KNOWLEDGE),
        ("florbulate the quux matrix", CFA_PLATFORM_KNOWLEDGE),
        ("\x00", CFA_PLATFORM_KNOWLEDGE),
    ],
)
def test_bound_read_only_target_cannot_become_project_objective_or_clarification(
    tmp_path: Path,
    human_text: str,
    target: str,
) -> None:
    result = _submit(tmp_path, human_text, session="G66-10-READ-ONLY")
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    isolation = context["production_flow_isolation_enforcement"]

    assert binding["requested_target_flow_id"] == target
    assert isolation["attempted_flow_id"] == target
    assert isolation["transition_disposition"] == (
        "PRODUCTION_FLOW_TRANSITION_ACCEPTED"
    )
    assert isolation["legacy_raw_classification_invoked_by_isolation"] is False
    assert isolation["project_objective_inference_invoked_by_isolation"] is False
    assert isolation["project_clarification_invoked_by_isolation"] is False
    assert context["project_objective_inference"] is None
    assert context["admission_precedence"] is None
    assert context["operational_clarification_envelope"] is None
    assert context.get("owner_bound_clarification_envelope") is None
    assert context["constitutional_development_governance"] is None
    assert context["human_conversation_experience"]["response_mode"] == (
        "READ_ONLY_RESULT"
    )


def test_bound_read_only_branch_never_calls_legacy_project_services_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args, **_kwargs):
        raise AssertionError("bound read-only branch invoked a forbidden legacy path")

    monkeypatch.setattr(project_services, "_classify_new_operational_turn", forbidden)
    monkeypatch.setattr(project_services, "infer_platform_project_objective", forbidden)
    monkeypatch.setattr(project_services, "_operational_clarification_envelope", forbidden)

    result = _submit(tmp_path, "I have an idea.", session="G66-10-NO-LEGACY")
    context = result["platform_core_project_services_context"]

    assert context["project_objective_inference"] is None
    assert context["operational_clarification_envelope"] is None
    assert context["governed_read_only_work_result"]["presentation_status"] == (
        "PRESENTATION_READY"
    )


@pytest.mark.parametrize(
    ("human_text", "target"),
    [
        ("Implement a validator.", CFA_DEVELOPMENT_GOVERNANCE),
        ("Run the governed execution workflow.", CFA_EXECUTION),
    ],
)
def test_validated_actionable_target_retains_objective_commitment_gate(
    tmp_path: Path,
    human_text: str,
    target: str,
) -> None:
    result = _submit(tmp_path, human_text, session=f"G66-10-{target}")
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    isolation = context["production_flow_isolation_enforcement"]

    assert binding["requested_target_flow_id"] == target
    assert binding["permitted_next_flow_id"] == CFA_OBJECTIVE_COMMITMENT
    assert isolation["attempted_flow_id"] == CFA_OBJECTIVE_COMMITMENT
    assert isolation["attempted_owner"] == binding["permitted_next_owner"]
    assert isolation["transition_permitted"] is True
    assert context["owner_bound_clarification_envelope"]["originating_owner"] == (
        "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    )
    assert context["project_objective_inference"] is None
    assert context["admission_precedence"] is None
    assert context["constitutional_development_governance"] is None


def test_flow_isolation_preserves_binding_predecessor_replay_chain(
    tmp_path: Path,
) -> None:
    result = _submit(tmp_path, "Show architecture.", session="G66-10-REPLAY")
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    isolation = context["production_flow_isolation_enforcement"]
    predecessor_references = binding["ordered_predecessor_references"]

    assert [item["stage"] for item in predecessor_references[:4]] == [
        "HUMAN_INTENT_PRECEDENCE",
        "INTERPRETER_PROPOSAL",
        "PROPOSAL_VALIDATION",
        "PROPOSAL_COMMIT",
    ]
    reconstruction = reconstruct_production_conversation_flow_binding_v1(
        Path(binding["owner_local_replay_references"][0]).parent
    )
    persisted_isolation = load_json(Path(isolation["replay_reference"]))

    assert reconstruction["reconstruction_verified"] is True
    assert persisted_isolation == isolation
    assert isolation["production_conversation_flow_binding_hash"] == binding[
        "artifact_hash"
    ]


def test_incompatible_transition_attempt_is_recorded_and_fails_closed(
    tmp_path: Path,
) -> None:
    capture = _compose(tmp_path, "Show architecture.", session="G66-10-REJECT")
    binding = capture["production_conversation_flow_binding"]
    session_root = tmp_path / "G66-10-REJECT"

    with pytest.raises(
        FailClosedRuntimeError,
        match="attempted Platform transition is not selected",
    ):
        project_services._enforce_production_flow_isolation(
            session_root=session_root,
            session_id="G66-10-REJECT",
            created_at=CREATED_AT,
            flow_binding=binding,
            attempted_flow_id=CFA_OBJECTIVE_COMMITMENT,
            attempted_owner="CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY",
        )

    rejected = load_json(
        next(
            (session_root / "production_flow_isolation").glob(
                "*_production_flow_isolation_decision.json"
            )
        )
    )
    assert rejected["transition_disposition"] == (
        "PRODUCTION_FLOW_TRANSITION_REJECTED"
    )
    assert rejected["transition_permitted"] is False
    assert rejected["project_objective_inference_invoked_by_isolation"] is False
    assert rejected["governance_invoked_by_isolation"] is False


def test_unbound_direct_project_services_compatibility_is_unchanged(
    tmp_path: Path,
) -> None:
    context = project_services.prepare_unified_human_interface_project_context(
        interface_name="G66-10-DIRECT-API",
        session_id="G66-10-UNBOUND",
        message="florbulate the quux matrix",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )

    assert context["production_conversation_flow_binding"] is None
    assert "production_flow_isolation_enforcement" not in context
    assert context["project_objective_inference"] is not None
    assert not (tmp_path / "G66-10-UNBOUND" / "production_flow_isolation").exists()


def test_flow_isolation_does_not_create_governance_or_effect_authority(
    tmp_path: Path,
) -> None:
    read_only = _submit(tmp_path, "Show architecture.", session="G66-10-GOV-RO")
    actionable = _submit(
        tmp_path,
        "Implement a validator.",
        session="G66-10-GOV-ACTION",
    )

    for result in (read_only, actionable):
        context = result["platform_core_project_services_context"]
        isolation = context["production_flow_isolation_enforcement"]
        assert isolation["governance_invoked_by_isolation"] is False
        assert isolation["authorization_created_by_isolation"] is False
        assert isolation["worker_selected_by_isolation"] is False
        assert isolation["execution_invoked_by_isolation"] is False
        assert context["constitutional_development_governance"] is None
        assert result["runtime_entered"] is False
