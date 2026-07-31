from __future__ import annotations

from copy import deepcopy
import ast
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-03-CONVERSATION-STATE-MACHINE"
CREATED = "2026-07-31T13:00:00Z"


def _time(minute: int) -> str:
    return f"2026-07-31T13:{minute:02d}:00Z"


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


def _provenance(value: str, *, source_revision: int) -> list[dict]:
    return [
        {
            "source_kind": cwm_v2.HUMAN_TURN,
            "turn_number": source_revision,
            "source_revision": source_revision,
            "source_span": value,
            "content_digest": cwm_v2._checksum(value),
            "normalization_rule_ids": [],
            "human_disposition": "ASSERTED",
        }
    ]


def _slot(
    value: str,
    *,
    source_revision: int,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    materiality: str = cwm_v2.REQUIRED,
    depends_on=(),
    status: str = cwm_v2.ASSERTED,
    completeness: str = cwm_v2.COMPLETE,
    confidence: str = cwm_v2.HUMAN_ASSERTED,
) -> dict:
    provenance = _provenance(value, source_revision=source_revision)
    if confidence == cwm_v2.HUMAN_CONFIRMED:
        provenance[0]["human_disposition"] = "CONFIRMED"
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=_conversation(),
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        status=status,
        completeness=completeness,
        confidence_class=confidence,
        materiality=materiality,
        provenance=provenance,
        depends_on=sorted(depends_on),
        created_at=_time(source_revision),
    )


def _create(tmp_path: Path, *, ttl_seconds: int = 3600) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=ttl_seconds,
        participants=_participants(),
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
        "Conversation State Machine Runtime",
        source_revision=2,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _apply(state, subject, 2)
    outcome = _slot(
        "deterministic isolated conversation progression",
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


def _objective_ready_state(tmp_path: Path) -> dict:
    state = _review_state(tmp_path)
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    return machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=state["revision"],
        confirmation_request=request,
        observed_at=_time(5),
    )["replacement_state"]


def test_absent_and_new_document_derive_canonical_states(tmp_path: Path) -> None:
    assert machine_v2.derive_conversation_protocol_state_v2(
        None, observed_at=CREATED
    ) == machine_v2.ABSENT

    state = _create(tmp_path)

    assert machine_v2.derive_conversation_protocol_state_v2(
        state, observed_at=CREATED
    ) == machine_v2.COLLECTING


def test_initial_reduction_selects_one_highest_precedence_clarification(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)

    result = machine_v2.prepare_conversation_protocol_reduction_v2(
        state,
        expected_revision=0,
        observed_at=_time(1),
    )
    clarification = result["replacement_state"]["semantic_memory"][
        "protocol_control"
    ]["clarification_control"]

    assert result["protocol_state"] == machine_v2.CLARIFYING
    assert clarification["trigger_slot_id"] == (
        "required-slot:OPERATIVE_ACTION:PRIMARY"
    )
    assert clarification["trigger_reason"] == "MISSING"
    assert clarification["no_progress_count"] == 0


def test_progressive_semantic_updates_advance_clarification_precedence(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    action = _slot("implement", source_revision=1)
    state = _apply(state, action, 1)
    first = state["semantic_memory"]["protocol_control"]["clarification_control"]
    subject = _slot(
        "Conversation State Machine Runtime",
        source_revision=2,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _apply(state, subject, 2)
    second = state["semantic_memory"]["protocol_control"]["clarification_control"]

    assert first["trigger_slot_id"] == "required-slot:OPERATIVE_SUBJECT:PRIMARY"
    assert second["trigger_slot_id"] == "required-slot:DESIRED_OUTCOME:PRIMARY"
    assert state["revision"] == 2
    assert state["semantic_revision"] == 2


def test_clarification_answer_requires_current_identity_and_target(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    action = _slot("implement", source_revision=1)
    state = _apply(state, action, 1)
    subject = _slot(
        "Conversation State Machine Runtime",
        source_revision=2,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )

    with pytest.raises(FailClosedRuntimeError, match="binding is stale"):
        machine_v2.prepare_clarification_answer_v2(
            state,
            expected_revision=1,
            clarification_id="clarification-local-sha256:" + "a" * 64,
            operation=slots_v2.CREATE,
            incoming_slot=subject,
            observed_at=_time(2),
        )
    with pytest.raises(FailClosedRuntimeError, match="bound clarification"):
        machine_v2.prepare_conversation_semantic_update_v2(
            state,
            expected_revision=1,
            operation=slots_v2.CREATE,
            incoming_slot=subject,
            observed_at=_time(2),
        )
    with pytest.raises(FailClosedRuntimeError, match="another slot"):
        machine_v2.prepare_clarification_answer_v2(
            state,
            expected_revision=1,
            clarification_id=state["semantic_memory"]["protocol_control"][
                "clarification_control"
            ]["clarification_id"],
            operation=slots_v2.CREATE,
            incoming_slot=_slot(
                "outcome",
                source_revision=2,
                slot_class=cwm_v2.DESIRED_OUTCOME,
            ),
            observed_at=_time(2),
        )


def test_complete_core_enters_candidate_review_with_exact_binding(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)
    control = state["semantic_memory"]["protocol_control"]
    binding = state["envelope"]["active_objective_candidate_binding"]

    assert machine_v2.derive_conversation_protocol_state_v2(
        state, observed_at=_time(4)
    ) == machine_v2.CANDIDATE_REVIEW
    assert control["clarification_control"] is None
    assert control["candidate_projection"] is not None
    assert control["confirmation_binding"] is None
    assert binding["candidate_digest"] == cwm_v2._checksum(
        control["candidate_projection"]
    )
    assert binding["semantic_revision"] == state["semantic_revision"]


def test_candidate_projection_and_presentation_are_deterministic(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)

    first = machine_v2.candidate_review_presentation_v2(state)
    second = machine_v2.candidate_review_presentation_v2(deepcopy(state))

    assert first == second
    assert first["presentation_digest"] == cwm_v2._checksum(
        first["presentation"]
    )
    assert first["presentation"]["capability_hints_are_advisory"] is True


def test_exact_confirmation_derives_objective_ready_without_creating_objective(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)
    request = machine_v2.create_candidate_confirmation_request_v2(state)

    result = machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=4,
        confirmation_request=request,
        observed_at=_time(5),
    )
    readiness = machine_v2.evaluate_conversation_readiness_v2(
        result["replacement_state"], observed_at=_time(5)
    )

    assert result["protocol_state"] == machine_v2.OBJECTIVE_READY
    assert result["objective_commitment_eligible"] is True
    assert result["objective_created"] is False
    assert result["execution_invoked"] is False
    assert readiness["objective_commitment_eligible"] is True
    assert result["replacement_state"]["semantic_revision"] == 4
    assert result["replacement_state"]["revision"] == 5


def test_confirmation_requires_bound_human_participant(tmp_path: Path) -> None:
    state = _review_state(tmp_path)
    state["envelope"]["participants"] = []
    state = cwm_v2._with_integrity(state)

    with pytest.raises(FailClosedRuntimeError, match="human participant"):
        machine_v2.create_candidate_confirmation_request_v2(state)


def test_stale_or_implicit_confirmation_fails_closed(tmp_path: Path) -> None:
    state = _review_state(tmp_path)
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    request["candidate_digest"] = "sha256:" + "a" * 64

    with pytest.raises(FailClosedRuntimeError, match="binding is stale"):
        machine_v2.prepare_candidate_confirmation_v2(
            state,
            expected_revision=4,
            confirmation_request=request,
            observed_at=_time(5),
        )
    with pytest.raises(FailClosedRuntimeError, match="schema is invalid"):
        machine_v2.prepare_candidate_confirmation_v2(
            state,
            expected_revision=4,
            confirmation_request={"control_act": "yes"},
            observed_at=_time(5),
        )


def test_correction_invalidates_confirmation_and_returns_to_review(
    tmp_path: Path,
) -> None:
    state = _objective_ready_state(tmp_path)
    correction = _slot("audit", source_revision=6)

    result = machine_v2.prepare_conversation_correction_v2(
        state,
        expected_revision=5,
        incoming_slot=correction,
        observed_at=_time(6),
    )
    control = result["replacement_state"]["semantic_memory"]["protocol_control"]

    assert result["protocol_state"] == machine_v2.CLARIFYING
    assert result["objective_commitment_eligible"] is False
    assert control["confirmation_binding"] is None
    assert result["replacement_state"]["envelope"][
        "active_objective_candidate_binding"
    ] is None


def test_unmarked_non_equivalent_update_enters_conflict_clarification(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)
    incoming = _slot("audit", source_revision=5)

    result = machine_v2.prepare_conversation_semantic_update_v2(
        state,
        expected_revision=4,
        operation=slots_v2.MERGE,
        incoming_slot=incoming,
        observed_at=_time(5),
    )
    clarification = result["replacement_state"]["semantic_memory"][
        "protocol_control"
    ]["clarification_control"]

    assert result["protocol_state"] == machine_v2.CLARIFYING
    assert clarification["trigger_reason"] == "CONFLICTED"
    assert clarification["candidate_values"] == ["audit", "implement"]


def test_no_progress_first_records_then_second_suspends_fail_closed(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    state = machine_v2.prepare_conversation_protocol_reduction_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]

    first = machine_v2.prepare_no_progress_transition_v2(
        state, expected_revision=1, observed_at=_time(2)
    )
    second = machine_v2.prepare_no_progress_transition_v2(
        first["replacement_state"],
        expected_revision=2,
        observed_at=_time(3),
    )

    assert first["disposition"] == machine_v2.NO_PROGRESS_RECORDED
    assert first["replacement_state"]["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]["no_progress_count"] == 1
    assert first["replacement_state"]["semantic_revision"] == 0
    assert second["disposition"] == machine_v2.SUSPENDED_FAIL_CLOSED
    assert second["protocol_state"] == machine_v2.SUSPENDED


def test_suspension_blocks_semantics_and_exact_resume_restores_state(
    tmp_path: Path,
) -> None:
    state = _objective_ready_state(tmp_path)
    suspended = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=5, observed_at=_time(6)
    )["replacement_state"]
    correction = _slot("audit", source_revision=7)

    with pytest.raises(FailClosedRuntimeError, match="requires active"):
        machine_v2.prepare_conversation_semantic_update_v2(
            suspended,
            expected_revision=6,
            operation=slots_v2.REPLACE,
            incoming_slot=correction,
            observed_at=_time(7),
        )
    resumed = machine_v2.prepare_conversation_resume_v2(
        suspended,
        expected_revision=6,
        current_interface_identity=cwm_v2.LOCAL_CONVERSATION_V2,
        participant_binding_digest=cwm_v2._checksum(_participants()),
        observed_at=_time(7),
    )["replacement_state"]

    assert machine_v2.derive_conversation_protocol_state_v2(
        resumed, observed_at=_time(7)
    ) == machine_v2.OBJECTIVE_READY
    assert resumed["semantic_revision"] == suspended["semantic_revision"]
    assert resumed["envelope"]["restored_at"] == _time(7)


def test_g59_02_reducer_cannot_bypass_suspended_state(tmp_path: Path) -> None:
    state = _review_state(tmp_path)
    suspended = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=4, observed_at=_time(5)
    )["replacement_state"]
    correction = _slot("audit", source_revision=6)

    with pytest.raises(FailClosedRuntimeError, match="requires an active"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            suspended,
            expected_revision=5,
            operation=slots_v2.REPLACE,
            incoming_slot=correction,
            observed_at=_time(6),
        )


def test_resume_rejects_cross_interface_and_participant_mismatch(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)
    suspended = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=4, observed_at=_time(5)
    )["replacement_state"]

    with pytest.raises(FailClosedRuntimeError, match="cross-interface"):
        machine_v2.prepare_conversation_resume_v2(
            suspended,
            expected_revision=5,
            current_interface_identity="UNBOUND_MIGRATION",
            participant_binding_digest=cwm_v2._checksum(_participants()),
            observed_at=_time(6),
        )
    with pytest.raises(FailClosedRuntimeError, match="participant"):
        machine_v2.prepare_conversation_resume_v2(
            suspended,
            expected_revision=5,
            current_interface_identity=cwm_v2.LOCAL_CONVERSATION_V2,
            participant_binding_digest="sha256:" + "b" * 64,
            observed_at=_time(6),
        )


def test_prepared_transition_persists_through_single_g59_store(tmp_path: Path) -> None:
    state = _create(tmp_path)
    prepared = machine_v2.prepare_conversation_protocol_reduction_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]

    stored = machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=prepared,
        observed_at=_time(1),
    )
    loaded = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(2),
    )

    assert stored == prepared
    assert loaded == prepared


def test_semantic_and_protocol_change_persist_as_one_atomic_revision(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    action = _slot("implement", source_revision=1)
    prepared = machine_v2.prepare_conversation_semantic_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=action,
        observed_at=_time(1),
    )["replacement_state"]

    stored = machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=prepared,
        observed_at=_time(1),
    )

    assert stored["revision"] == 1
    assert stored["envelope_revision"] == 1
    assert stored["semantic_revision"] == 1
    assert stored["envelope"]["conversation_phase"] == cwm_v2.CLARIFYING


def test_persistence_rejects_stale_revision(tmp_path: Path) -> None:
    state = _create(tmp_path)
    prepared = machine_v2.prepare_conversation_protocol_reduction_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]
    machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=prepared,
        observed_at=_time(1),
    )

    with pytest.raises(FailClosedRuntimeError, match="revision does not match"):
        machine_v2.persist_conversation_state_machine_transition_v2(
            runtime_root=str(tmp_path),
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=prepared,
            observed_at=_time(1),
        )


def test_persistence_rejects_unsupported_same_suspended_transition(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    suspended = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]
    machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=suspended,
        observed_at=_time(1),
    )
    unsupported = deepcopy(suspended)
    unsupported["revision"] = 2
    unsupported["envelope_revision"] = 2
    unsupported["envelope"]["updated_at"] = _time(2)
    unsupported["envelope"]["semantic_memory_binding"]["global_revision"] = 2
    unsupported = cwm_v2._with_integrity(unsupported)

    with pytest.raises(FailClosedRuntimeError, match="not supported"):
        machine_v2.persist_conversation_state_machine_transition_v2(
            runtime_root=str(tmp_path),
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=1,
            replacement_state=unsupported,
            observed_at=_time(2),
        )


def test_abandonment_transitions_through_closed_and_cleans_state(
    tmp_path: Path,
) -> None:
    _create(tmp_path)

    result = machine_v2.abandon_conversation_state_machine_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        observed_at=_time(1),
    )
    loaded = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(2),
    )

    assert result["disposition"] == machine_v2.USER_ABANDONED
    assert result["protocol_state"] == machine_v2.ABANDONED
    assert result["closed_state_digest"] is not None
    assert loaded is None


def test_recovery_completes_interrupted_closed_state_cleanup(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    closed = machine_v2.prepare_conversation_abandonment_v2(
        state, expected_revision=0, observed_at=_time(1)
    )["replacement_state"]
    machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=closed,
        observed_at=_time(1),
    )

    result = machine_v2.recover_conversation_state_machine_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-07-31T14:01:00Z",
    )
    loaded = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-07-31T14:01:00Z",
    )

    assert result["protocol_state"] == machine_v2.ABANDONED
    assert result["state"] is None
    assert loaded is None


def test_expiration_recovery_cleans_without_abandonment_meaning(
    tmp_path: Path,
) -> None:
    _create(tmp_path, ttl_seconds=60)

    result = machine_v2.recover_conversation_state_machine_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(1),
    )

    assert result["protocol_state"] == machine_v2.EXPIRED
    assert result["retained_for_recovery"] is False


def test_corrupt_recovery_retains_state_fail_closed(tmp_path: Path) -> None:
    _create(tmp_path)
    root = cwm_v2._conversation_root(tmp_path)
    path = cwm_v2._state_path(root, WORKSPACE, SESSION)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["revision"] = 99
    path.write_text(json.dumps(raw), encoding="utf-8")

    result = machine_v2.recover_conversation_state_machine_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(1),
    )

    assert result["protocol_state"] == machine_v2.FAIL_CLOSED_RECOVERY
    assert result["retained_for_recovery"] is True
    assert path.exists()


def test_invalid_composite_and_reserved_commitment_phase_fail_closed(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    invalid = deepcopy(state)
    invalid["envelope"]["conversation_phase"] = cwm_v2.CANDIDATE_REVIEW
    invalid = cwm_v2._with_integrity(invalid)

    with pytest.raises(FailClosedRuntimeError, match="candidate review controls"):
        machine_v2.validate_conversation_state_machine_state_v2(invalid)

    reserved = deepcopy(state)
    reserved["envelope"]["conversation_phase"] = cwm_v2.COMMITMENT_PENDING
    reserved = cwm_v2._with_integrity(reserved)
    with pytest.raises(FailClosedRuntimeError, match="not implemented"):
        machine_v2.validate_conversation_state_machine_state_v2(reserved)


def test_lifecycle_timestamp_order_fails_closed(tmp_path: Path) -> None:
    state = _review_state(tmp_path)
    suspended = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=4, observed_at=_time(5)
    )["replacement_state"]
    resumed = machine_v2.prepare_conversation_resume_v2(
        suspended,
        expected_revision=5,
        current_interface_identity=cwm_v2.LOCAL_CONVERSATION_V2,
        participant_binding_digest=cwm_v2._checksum(_participants()),
        observed_at=_time(6),
    )["replacement_state"]
    closed = machine_v2.prepare_conversation_abandonment_v2(
        resumed, expected_revision=6, observed_at=_time(7)
    )["replacement_state"]
    closed["envelope"]["closed_at"] = _time(5)
    closed = cwm_v2._with_integrity(closed)

    with pytest.raises(FailClosedRuntimeError, match="closure precedes"):
        machine_v2.validate_conversation_state_machine_state_v2(closed)


def test_unconfirmed_material_assumption_blocks_candidate_review(
    tmp_path: Path,
) -> None:
    state = _review_state(tmp_path)
    assumption = _slot(
        "filesystem is writable",
        source_revision=5,
        slot_class=cwm_v2.GOVERNING_QUALIFIER,
        slot_role=cwm_v2.ASSUMPTION,
        cardinality_key="filesystem-writable",
        materiality=cwm_v2.CONDITIONAL,
    )

    result = machine_v2.prepare_conversation_semantic_update_v2(
        state,
        expected_revision=4,
        operation=slots_v2.CREATE,
        incoming_slot=assumption,
        observed_at=_time(5),
    )

    assert result["protocol_state"] == machine_v2.CLARIFYING
    assert result["replacement_state"]["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]["trigger_reason"] == "UNCONFIRMED"


def test_state_machine_source_has_no_interpreter_or_execution_imports() -> None:
    source = inspect.getsource(machine_v2)
    imported_modules = {
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }

    assert not any(
        forbidden in module.lower()
        for module in imported_modules
        for forbidden in (
            "interpreter",
            "objective",
            "authorization",
            "worker",
            "replay",
            "development_governance",
            "aicli",
        )
    )
    assert "objective_created\": True" not in source
    assert "execution_invoked\": True" not in source
