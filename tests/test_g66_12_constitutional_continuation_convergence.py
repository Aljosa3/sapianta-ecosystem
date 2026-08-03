"""Focused G66-12 constitutional continuation convergence tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

import aigol.runtime.platform_core_project_services as project_services
import aigol.runtime.production_conversation_flow_binding as flow_binding
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    latest_platform_core_workspace_state,
    replay_backed_uhi_clarification_state,
)
from aigol.runtime.production_conversation_flow_binding import (
    CFA_CLARIFICATION,
    CFA_DEVELOPMENT_GOVERNANCE,
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-08-03T18:00:00Z"
ACTIONABLE_REQUEST = "Implement a validator."
PROJECT_CLARIFICATION_REQUEST = (
    "Analyze Platform Capability Composition Coverage.\nAudit only."
)


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("continuation must stop before the governed runner")


def _entry(tmp_path: Path, session: str, request: str) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="G66-12-TEST-INTERFACE",
        session_id=session,
        human_requests=[request],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
        operator_context="AICLI_NEW_TURN_PRE_APPROVAL",
    )


def _flow_replay_root(result: dict) -> Path:
    reference = result["production_conversation_binding"][
        "production_conversation_flow_binding_reference"
    ]
    return Path(reference).parent


def test_workspace_restoration_recognizes_existing_owner_bound_envelope(
    tmp_path: Path,
) -> None:
    session = "G66-12-WORKSPACE-RESTORE"
    first = _entry(tmp_path, session, ACTIONABLE_REQUEST)
    workspace = latest_platform_core_workspace_state(tmp_path / session)
    restored = replay_backed_uhi_clarification_state(workspace)

    assert restored is not None
    assert restored["owner_bound_clarification_envelope"] == first[
        "owner_bound_clarification_envelope"
    ]
    assert restored["operational_clarification_envelope"] is None
    assert restored["replay_backed"] is True


def test_g59_continuation_reuses_owner_conversation_cwm_revision_and_flow(
    tmp_path: Path,
) -> None:
    session = "G66-12-G59-CONTINUATION"
    first = _entry(tmp_path, session, ACTIONABLE_REQUEST)
    second = _entry(tmp_path, session, "/reply action: implement")
    first_capture = first["production_conversation_binding"]
    second_capture = second["production_conversation_binding"]
    first_context = first["platform_core_project_services_context"]
    second_context = second["platform_core_project_services_context"]

    assert second_capture["clarification_continuation_restored"] is True
    assert second_capture["originating_owner_restored"] == (
        "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    )
    assert second_capture["conversation_identity"] == first_capture[
        "conversation_identity"
    ]
    assert second_capture["conversation_state"] == first_capture[
        "conversation_state"
    ]
    assert second_capture["conversation_state"]["revision"] == 1
    assert second_capture["production_conversation_flow_binding"] == first_capture[
        "production_conversation_flow_binding"
    ]
    assert second_capture["human_intent_precedence_decision"] == first_capture[
        "human_intent_precedence_decision"
    ]
    assert second_capture["human_intent_reclassified"] is False
    assert second_capture["platform_query_router_reinvoked"] is False
    assert second_context["clarification_continuity"][
        "owner_bound_clarification_envelope"
    ] == first_context["owner_bound_clarification_envelope"]
    assert second_context["human_intent_precedence_before_restored_context"] is False
    assert second_context["production_conversation_flow_binding"] == first_context[
        "production_conversation_flow_binding"
    ]
    assert second_context["project_objective_inference"] is None
    assert second_context["constitutional_development_governance"] is None
    assert second_context["admission_precedence"] is None


def test_continuation_does_not_reclassify_or_reinvoke_query_router(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = "G66-12-NO-RECLASSIFY-OR-ROUTE"
    first = _entry(tmp_path, session, ACTIONABLE_REQUEST)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("continuation invoked a forbidden classifier or router")

    monkeypatch.setattr(flow_binding, "classify_self_knowledge_request", forbidden)
    monkeypatch.setattr(flow_binding, "select_platform_query_route", forbidden)
    monkeypatch.setattr(project_services, "classify_self_knowledge_request", forbidden)
    second = _entry(tmp_path, session, "/reply subject: validator")

    assert second["production_conversation_flow_binding"] == first[
        "production_conversation_flow_binding"
    ]
    assert second["production_conversation_binding"][
        "human_intent_reclassified"
    ] is False
    assert second["production_conversation_binding"][
        "platform_query_router_reinvoked"
    ] is False


def test_g29_continuation_returns_to_exact_existing_owner(
    tmp_path: Path,
) -> None:
    session = "G66-12-G29-CONTINUATION"
    first = _entry(tmp_path, session, PROJECT_CLARIFICATION_REQUEST)
    second = _entry(tmp_path, session, "capability coverage")
    first_context = first["platform_core_project_services_context"]
    second_context = second["platform_core_project_services_context"]
    continuation = second_context["clarification_continuity"]

    assert first_context["production_conversation_flow_binding"][
        "requested_target_flow_id"
    ] == CFA_CLARIFICATION
    assert continuation["clarification_owner"] == (
        "G29_SEMANTIC_CAPABILITY_SELECTION"
    )
    assert continuation["reply_bound_to_active_clarification"] is True
    assert continuation["owner_specific_continuation"] is True
    assert second["production_conversation_binding"][
        "originating_owner_restored"
    ] == "G29_SEMANTIC_CAPABILITY_SELECTION"
    assert second["production_conversation_flow_binding"] == first[
        "production_conversation_flow_binding"
    ]
    assert second["production_conversation_binding"]["conversation_state"] == first[
        "production_conversation_binding"
    ]["conversation_state"]
    assert second_context["constitutional_development_governance"] is None


def test_continuation_preserves_replay_lineage_without_new_flow_turn(
    tmp_path: Path,
) -> None:
    session = "G66-12-REPLAY"
    first = _entry(tmp_path, session, ACTIONABLE_REQUEST)
    replay_root = _flow_replay_root(first)
    before = sorted((replay_root.parent).glob("*/*_flow_binding.json"))
    first_reconstruction = reconstruct_production_conversation_flow_binding_v1(
        replay_root
    )
    second = _entry(tmp_path, session, "/reply outcome: validated requests")
    after = sorted((replay_root.parent).glob("*/*_flow_binding.json"))
    second_reconstruction = reconstruct_production_conversation_flow_binding_v1(
        replay_root
    )

    assert before == after
    assert first_reconstruction == second_reconstruction
    assert second["production_conversation_binding"][
        "production_conversation_replay_reference"
    ] == str(replay_root)
    assert second["production_conversation_flow_binding"] == first[
        "production_conversation_flow_binding"
    ]


def test_cross_session_owner_bound_restoration_fails_closed(tmp_path: Path) -> None:
    source_session = "G66-12-SOURCE-SESSION"
    target_session = "G66-12-TARGET-SESSION"
    _entry(tmp_path, source_session, ACTIONABLE_REQUEST)
    source_state = latest_platform_core_workspace_state(tmp_path / source_session)
    assert source_state is not None
    target_path = (
        tmp_path
        / target_session
        / "workspace_state"
        / "000_platform_core_workspace_state_recorded.json"
    )
    write_json_immutable(target_path, source_state)

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        _entry(tmp_path, target_session, "/reply action: implement")


def test_tampered_owner_bound_envelope_fails_closed(tmp_path: Path) -> None:
    session = "G66-12-TAMPER"
    _entry(tmp_path, session, ACTIONABLE_REQUEST)
    state = deepcopy(latest_platform_core_workspace_state(tmp_path / session))
    assert state is not None
    envelope = state["pending_clarification_request"][
        "owner_bound_clarification_envelope"
    ]
    envelope["originating_owner"] = "PLATFORM_CORE_PROJECT_SERVICES"
    envelope_body = dict(envelope)
    envelope_body.pop("artifact_hash", None)
    envelope["artifact_hash"] = replay_hash(envelope_body)
    body = dict(state)
    body.pop("artifact_hash", None)
    state["artifact_hash"] = replay_hash(body)
    tampered_path = (
        tmp_path
        / session
        / "workspace_state"
        / "999_platform_core_workspace_state_recorded.json"
    )
    write_json_immutable(tampered_path, state)

    with pytest.raises(FailClosedRuntimeError, match="Project Services Replay"):
        _entry(tmp_path, session, "/reply action: implement")


def test_historical_g15_operational_projection_remains_compatible() -> None:
    legacy_envelope = {"artifact_type": "PLATFORM_CORE_OPERATIONAL_CLARIFICATION_ENVELOPE_V1"}
    workspace = {
        "session_id": "G15-HISTORICAL",
        "replay_reference": "legacy-workspace",
        "artifact_hash": "sha256:" + "0" * 64,
        "pending_clarification_request": {
            "original_message": "historical request",
            "clarification_questions": ["Which capability?"],
            "operational_clarification_envelope": legacy_envelope,
        },
    }

    restored = replay_backed_uhi_clarification_state(workspace)

    assert restored is not None
    assert restored["operational_clarification_envelope"] == legacy_envelope
    assert restored["owner_bound_clarification_envelope"] is None
    assert restored["original_message"] == "historical request"
