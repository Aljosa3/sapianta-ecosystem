from __future__ import annotations

from copy import deepcopy
import ast
import inspect
from pathlib import Path

import pytest

from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as commit_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-06-OBJECTIVE-READINESS"
CREATED = "2026-08-01T10:00:00Z"
PARSER = "conversation-deterministic-parser-v1"


def _time(minute: int) -> str:
    return f"2026-08-01T10:{minute:02d}:00Z"


def _conversation() -> str:
    return cwm_v2.conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )


def _participants() -> list[dict]:
    return [
        {
            "participant_role": cwm_v2.HUMAN_ORIGINATOR,
            "asserted_identity": "local-human",
            "identity_source": cwm_v2.LOCAL_ASSERTION,
            "binding_disposition": cwm_v2.ASSERTED_NOT_AUTHENTICATED,
            "first_bound_revision": 0,
            "last_confirmed_revision": 0,
        }
    ]


def _slot(
    value: str,
    *,
    source_revision: int,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    depends_on=(),
    status: str = cwm_v2.ASSERTED,
    completeness: str = cwm_v2.COMPLETE,
) -> dict:
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=_conversation(),
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        status=status,
        completeness=completeness,
        confidence_class=(
            cwm_v2.CONTEXT_DERIVED
            if status == cwm_v2.PROPOSED
            else cwm_v2.HUMAN_ASSERTED
        ),
        materiality=cwm_v2.REQUIRED,
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": source_revision,
                "source_revision": source_revision,
                "source_span": value,
                "content_digest": cwm_v2._checksum(value),
                "normalization_rule_ids": [],
                "human_disposition": (
                    "NOT_APPLICABLE"
                    if status == cwm_v2.PROPOSED
                    else "ASSERTED"
                ),
            }
        ],
        depends_on=sorted(depends_on),
        created_at=_time(source_revision),
    )


def _create(tmp_path: Path, *, semantic_slots: list[dict] | None = None) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=3600,
        participants=_participants(),
        semantic_slots=semantic_slots or [],
    )


def _apply(state: dict, slot: dict, minute: int, operation: str = slots_v2.CREATE) -> dict:
    clarification = state["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    if clarification is None:
        result = machine_v2.prepare_conversation_semantic_update_v2(
            state,
            expected_revision=state["revision"],
            operation=operation,
            incoming_slot=slot,
            observed_at=_time(minute),
        )
    else:
        result = machine_v2.prepare_clarification_answer_v2(
            state,
            expected_revision=state["revision"],
            clarification_id=clarification["clarification_id"],
            operation=operation,
            incoming_slot=slot,
            observed_at=_time(minute),
        )
    return result["replacement_state"]


def _review_state(tmp_path: Path) -> dict:
    state = _create(tmp_path)
    action = _slot("implement", source_revision=1)
    state = _apply(state, action, 1)
    subject = _slot(
        "Objective Readiness Runtime",
        source_revision=2,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _apply(state, subject, 2)
    outcome = _slot(
        "deterministic fail-closed readiness reports",
        source_revision=3,
        slot_class=cwm_v2.DESIRED_OUTCOME,
        depends_on=[action["slot_id"], subject["slot_id"]],
    )
    state = _apply(state, outcome, 3)
    work_type = _slot(
        "IMPLEMENTATION",
        source_revision=4,
        slot_class=cwm_v2.WORK_TYPE,
        slot_role="IMPLEMENTATION",
        depends_on=[action["slot_id"]],
    )
    return _apply(state, work_type, 4)


def _ready_state(tmp_path: Path) -> dict:
    state = _review_state(tmp_path)
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    return machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=state["revision"],
        confirmation_request=request,
        observed_at=_time(5),
    )["replacement_state"]


def _evaluate(state: dict, *, observed_at: str | None = None) -> dict:
    return readiness_v2.evaluate_objective_readiness_v2(
        state,
        expected_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        observed_at=observed_at or state["envelope"]["updated_at"],
    )


def test_complete_confirmed_conversation_is_ready_without_objective_creation(
    tmp_path: Path,
) -> None:
    state = _ready_state(tmp_path)
    original = deepcopy(state)

    report = _evaluate(state)
    required = report["required_slot_assessments"]

    assert report["readiness_disposition"] == readiness_v2.READY
    assert report["protocol_state"] == machine_v2.OBJECTIVE_READY
    assert report["objective_commitment_eligible"] is True
    assert report["refusal_reasons"] == []
    assert all(item["active_complete"] for item in required)
    assert readiness_v2.require_objective_readiness_v2(
        state,
        expected_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        observed_at=state["envelope"]["updated_at"],
    ) == report
    assert state == original
    for field in (
        "constitutional_authority",
        "objective_created",
        "objective_commitment_invoked",
        "platform_core_invoked",
        "replay_written",
        "authorization_invoked",
        "worker_invoked",
        "execution_invoked",
    ):
        assert report[field] is False


def test_missing_mandatory_slots_refuse_and_preserve_report(tmp_path: Path) -> None:
    state = _create(tmp_path)

    report = _evaluate(state)

    assert report["readiness_disposition"] == readiness_v2.NOT_READY
    assert readiness_v2.REQUIRED_SLOT_MISSING in report["refusal_reasons"]
    assert len(report["blocking_evidence"]["required_missing"]) == 4
    with pytest.raises(readiness_v2.ObjectiveReadinessError) as raised:
        readiness_v2.require_objective_readiness_v2(
            state,
            expected_revision=0,
            expected_semantic_revision=0,
            observed_at=CREATED,
        )
    assert raised.value.reason_code == "OBJECTIVE_READINESS_REFUSED"
    assert raised.value.readiness_report == report


def test_pending_clarification_is_explicit_readiness_blocker(tmp_path: Path) -> None:
    state = _create(tmp_path)
    state = machine_v2.prepare_conversation_protocol_reduction_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]

    report = _evaluate(state)

    assert report["protocol_state"] == machine_v2.CLARIFYING
    assert readiness_v2.UNRESOLVED_CLARIFICATION in report["refusal_reasons"]
    assert report["unresolved_clarification"]["trigger_reason"] == "MISSING"


def test_semantic_conflict_is_detected_and_refused(tmp_path: Path) -> None:
    state = _review_state(tmp_path)
    incoming = _slot("audit", source_revision=5)
    conflicted = machine_v2.prepare_conversation_semantic_update_v2(
        state,
        expected_revision=state["revision"],
        operation=slots_v2.MERGE,
        incoming_slot=incoming,
        observed_at=_time(5),
    )["replacement_state"]

    report = _evaluate(conflicted)

    assert readiness_v2.UNRESOLVED_SEMANTIC_CONFLICT in report["refusal_reasons"]
    assert report["unresolved_conflict_slot_ids"]
    assert report["blocking_evidence"]["material_conflicted"]


def test_dependency_completeness_is_reported_fail_closed(tmp_path: Path) -> None:
    action = _slot(
        "implement",
        source_revision=0,
        status=cwm_v2.PROPOSED,
        completeness=cwm_v2.PARTIAL,
    )
    subject = _slot(
        "runtime",
        source_revision=0,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _create(tmp_path, semantic_slots=[action, subject])
    state = machine_v2.prepare_conversation_protocol_reduction_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]

    report = _evaluate(state)

    assert readiness_v2.DEPENDENCY_INCOMPLETE in report["refusal_reasons"]
    assert subject["slot_id"] in report["incomplete_dependency_slot_ids"]
    subject_evidence = next(
        item
        for item in report["semantic_slot_assessments"]
        if item["slot_id"] == subject["slot_id"]
    )
    assert subject_evidence["semantic_classification"] == cwm_v2.PARTIAL


@pytest.mark.parametrize("global_delta, semantic_delta", [(-1, 0), (0, -1)])
def test_stale_expected_revisions_are_rejected_before_evaluation(
    tmp_path: Path, global_delta: int, semantic_delta: int
) -> None:
    state = _review_state(tmp_path)

    with pytest.raises(readiness_v2.ObjectiveReadinessError) as raised:
        readiness_v2.evaluate_objective_readiness_v2(
            state,
            expected_revision=state["revision"] + global_delta,
            expected_semantic_revision=state["semantic_revision"] + semantic_delta,
            observed_at=_time(4),
        )

    assert raised.value.reason_code == "STALE_READINESS_REVISION"


@pytest.mark.parametrize("phase", [cwm_v2.COMMITMENT_PENDING, cwm_v2.HANDED_OFF])
def test_reserved_or_invalid_pipeline_transition_fails_closed(
    tmp_path: Path, phase: str
) -> None:
    state = _review_state(tmp_path)
    state["envelope"]["conversation_phase"] = phase
    state = machine_v2._refresh_bindings_and_integrity(state)

    with pytest.raises(readiness_v2.ObjectiveReadinessError) as raised:
        _evaluate(state)

    assert raised.value.reason_code == "STATE_INVALID"


def test_repeated_evaluation_and_report_identity_are_deterministic(
    tmp_path: Path,
) -> None:
    state = _ready_state(tmp_path)

    first = _evaluate(state)
    second = _evaluate(deepcopy(state))

    assert first == second
    assert first["readiness_report_id"].startswith(
        "objective-readiness-local-sha256:"
    )
    assert first["report_checksum"] == cwm_v2._checksum(
        {key: value for key, value in first.items() if key != "report_checksum"}
    )


def test_readiness_report_tampering_is_rejected(tmp_path: Path) -> None:
    report = _evaluate(_ready_state(tmp_path))
    report["objective_created"] = True

    with pytest.raises(readiness_v2.ObjectiveReadinessError) as raised:
        readiness_v2.validate_objective_readiness_report_v2(report)

    assert raised.value.reason_code == "READINESS_REPORT_INVALID"


def test_g59_05_committed_interpreter_proposal_remains_not_ready(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    text = "implement"
    span = proposal_v2.create_source_span_v2(
        text, start_offset=0, end_offset=len(text)
    )
    operation = proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=proposal_v2.PROPOSE_SLOT_CREATION,
        slot_class=cwm_v2.OPERATIVE_ACTION,
        slot_role=cwm_v2.PRIMARY,
        cardinality_key=cwm_v2.PRIMARY,
        surface_value=text,
        canonical_value=text,
        source_spans=[span],
    )
    source = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=0,
        source_turn_text=text,
    )
    proposal = proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=PARSER,
        interpreter_class=proposal_v2.DETERMINISTIC_PARSER,
        interpreter_version="1.0.0",
        conversation_identity=state["envelope"]["conversation_identity"],
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        source_turn_identity=source["source_turn_identity"],
        source_turn_digest=source["source_turn_digest"],
        expected_cwm_revision=0,
        expected_semantic_revision=0,
        proposed_semantic_operations=[operation],
    )
    validation = proposal_v2.validate_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=_time(1),
        interpreter_registry=[
            {
                "interpreter_identity": PARSER,
                "interpreter_class": proposal_v2.DETERMINISTIC_PARSER,
                "interpreter_version": "1.0.0",
                "enabled": True,
            }
        ],
    )
    committed = commit_v2.commit_proposal_candidate_operations_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        candidate_operation_set=validation["candidate_operation_set"],
        expected_revision=0,
        committed_at=_time(1),
    )["state"]

    report = _evaluate(committed)

    assert report["readiness_disposition"] == readiness_v2.NOT_READY
    assert readiness_v2.MATERIAL_SLOT_INCOMPLETE in report["refusal_reasons"]
    assert committed["semantic_memory"]["semantic_slots"][0]["status"] == (
        cwm_v2.PROPOSED
    )


def test_runtime_imports_only_isolated_conversation_owners() -> None:
    source = inspect.getsource(readiness_v2)
    imported = {
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }

    assert not any(
        forbidden in module.lower()
        for module in imported
        for forbidden in (
            "replay",
            "authorization",
            "worker",
            "development_governance",
            "capability",
            "aicli",
            "provider",
        )
    )
