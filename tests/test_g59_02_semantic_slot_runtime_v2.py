from __future__ import annotations

import ast
from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-02-SEMANTIC-SLOT-SESSION"
CREATED = "2026-07-31T12:00:00Z"
UPDATED = "2026-07-31T12:01:00Z"
LATER = "2026-07-31T12:02:00Z"


def _conversation() -> str:
    return cwm_v2.conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )


def _provenance(
    value: str,
    *,
    source_revision: int = 0,
    turn_number: int = 1,
    disposition: str = "ASSERTED",
) -> list[dict]:
    return [
        {
            "source_kind": cwm_v2.HUMAN_TURN,
            "turn_number": turn_number,
            "source_revision": source_revision,
            "source_span": value,
            "content_digest": cwm_v2._checksum(value),
            "normalization_rule_ids": [],
            "human_disposition": disposition,
        }
    ]


def _slot(
    value: str,
    *,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    status: str = cwm_v2.ASSERTED,
    completeness: str = cwm_v2.COMPLETE,
    confidence: str = cwm_v2.HUMAN_ASSERTED,
    materiality: str = cwm_v2.REQUIRED,
    depends_on=(),
    created_at: str = CREATED,
    source_revision: int = 0,
    turn_number: int = 1,
) -> dict:
    disposition = "CONFIRMED" if confidence == cwm_v2.HUMAN_CONFIRMED else "ASSERTED"
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
        provenance=_provenance(
            value,
            source_revision=source_revision,
            turn_number=turn_number,
            disposition=disposition,
        ),
        depends_on=sorted(depends_on),
        created_at=created_at,
    )


def _state(tmp_path: Path, semantic_slots=()) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        semantic_slots=list(semantic_slots),
    )


@pytest.mark.parametrize(
    ("slot_class", "slot_role", "cardinality_key", "value", "materiality"),
    [
        (cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY, cwm_v2.PRIMARY, "implement", cwm_v2.REQUIRED),
        (
            cwm_v2.OPERATIVE_SUBJECT,
            cwm_v2.PRIMARY,
            cwm_v2.PRIMARY,
            "semantic slots",
            cwm_v2.REQUIRED,
        ),
        (
            cwm_v2.DESIRED_OUTCOME,
            cwm_v2.PRIMARY,
            cwm_v2.PRIMARY,
            "deterministic state",
            cwm_v2.REQUIRED,
        ),
        (cwm_v2.WORK_TYPE, "IMPLEMENTATION", cwm_v2.PRIMARY, "IMPLEMENTATION", cwm_v2.REQUIRED),
        (
            cwm_v2.GOVERNING_QUALIFIER,
            cwm_v2.PRESERVATION,
            "isolation",
            "preserve isolation",
            cwm_v2.CONDITIONAL,
        ),
        (cwm_v2.SEMANTIC_REFERENCE, cwm_v2.SCOPE, "runtime", "aigol/runtime", cwm_v2.CONDITIONAL),
    ],
)
def test_runtime_creates_all_six_canonical_slot_classes(
    slot_class, slot_role, cardinality_key, value, materiality
) -> None:
    slot = _slot(
        value,
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        materiality=materiality,
    )

    assert slot["slot_class"] == slot_class
    assert slot["slot_revision"] == 0


def test_equivalence_uses_only_foundation_equivalence_key() -> None:
    left = _slot("implement")
    right = _slot("implement", turn_number=2)

    assert slots_v2.semantic_slots_equivalent_v2(
        left, right, conversation_identity=_conversation()
    )


def test_equivalent_merge_extends_provenance_and_revision() -> None:
    active = _slot("implement")
    incoming = _slot("implement", source_revision=1, turn_number=2, created_at=UPDATED)

    result = slots_v2.merge_semantic_slots_v2(
        active,
        incoming,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.MERGED_EQUIVALENT
    assert result["slot"]["slot_revision"] == 1
    assert len(result["slot"]["provenance"]) == 2
    assert result["slot"]["canonical_value"] == "implement"


def test_exact_duplicate_is_no_change() -> None:
    active = _slot("implement")

    result = slots_v2.merge_semantic_slots_v2(
        active,
        deepcopy(active),
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.NO_CHANGE
    assert result["slot"] == active


def test_non_equivalent_equal_evidence_creates_visible_conflict() -> None:
    active = _slot("implement")
    incoming = _slot("audit", source_revision=1, turn_number=2, created_at=UPDATED)

    result = slots_v2.merge_semantic_slots_v2(
        active,
        incoming,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.CONFLICT_DETECTED
    assert result["slot"]["status"] == cwm_v2.CONFLICTED
    assert result["slot"]["completeness"] == cwm_v2.CONFLICTED
    assert {item["candidate_kind"] for item in result["conflict_candidates"]} == {
        "ACTIVE",
        "INCOMING",
    }


def test_equivalent_merge_cannot_silently_resolve_existing_conflict() -> None:
    active = _slot("implement")
    conflicting = _slot(
        "audit", source_revision=1, turn_number=2, created_at=UPDATED
    )
    conflict = slots_v2.merge_semantic_slots_v2(
        active,
        conflicting,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )["slot"]
    repeated_active = _slot(
        "implement", source_revision=2, turn_number=3, created_at=LATER
    )

    result = slots_v2.merge_semantic_slots_v2(
        conflict,
        repeated_active,
        conversation_identity=_conversation(),
        observed_at=LATER,
    )

    assert result["disposition"] == slots_v2.MERGED_EQUIVALENT
    assert result["slot"]["status"] == cwm_v2.CONFLICTED
    assert result["slot"]["history"][-1]["change_kind"] == "CONFLICTED"


def test_lower_evidence_never_replaces_human_confirmed_value() -> None:
    active = _slot(
        "implement",
        status=cwm_v2.CONFIRMED,
        confidence=cwm_v2.HUMAN_CONFIRMED,
    )
    incoming = _slot(
        "audit",
        confidence=cwm_v2.DETERMINISTIC_NORMALIZATION,
        source_revision=1,
        turn_number=2,
        created_at=UPDATED,
    )

    result = slots_v2.merge_semantic_slots_v2(
        active,
        incoming,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.REJECT_LOWER_EVIDENCE
    assert result["slot"] == active


def test_explicit_human_replacement_preserves_forward_history() -> None:
    active = _slot(
        "implement",
        status=cwm_v2.CONFIRMED,
        confidence=cwm_v2.HUMAN_CONFIRMED,
    )
    correction = _slot(
        "audit",
        source_revision=1,
        turn_number=2,
        created_at=UPDATED,
    )

    result = slots_v2.replace_semantic_slot_v2(
        active,
        correction,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.REPLACED
    assert result["slot"]["canonical_value"] == "audit"
    assert result["slot"]["slot_id"] == active["slot_id"]
    assert result["slot"]["slot_revision"] == 1
    assert result["slot"]["history"][-1]["prior_value_digest"] == cwm_v2._checksum("implement")


def test_explicit_compatible_refinement_versions_the_same_slot() -> None:
    active = _slot("implement")
    refinement = _slot(
        "implement isolated semantic slots",
        source_revision=1,
        turn_number=2,
        created_at=UPDATED,
    )

    result = slots_v2.revise_semantic_slot_v2(
        active,
        refinement,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.REFINED
    assert result["slot"]["slot_id"] == active["slot_id"]
    assert result["slot"]["slot_revision"] == 1
    assert result["slot"]["history"][-1]["change_kind"] == "REFINED"


def test_non_human_explicit_replacement_fails_closed() -> None:
    active = _slot("implement")
    incoming = _slot(
        "audit",
        confidence=cwm_v2.DETERMINISTIC_NORMALIZATION,
        source_revision=1,
        created_at=UPDATED,
    )

    with pytest.raises(FailClosedRuntimeError, match="human-asserted"):
        slots_v2.replace_semantic_slot_v2(
            active,
            incoming,
            conversation_identity=_conversation(),
            observed_at=UPDATED,
        )


def test_confirmation_binds_exact_value() -> None:
    active = _slot("implement")
    confirmation = _slot(
        "implement",
        status=cwm_v2.CONFIRMED,
        confidence=cwm_v2.HUMAN_CONFIRMED,
        source_revision=1,
        turn_number=2,
        created_at=UPDATED,
    )

    result = slots_v2.confirm_semantic_slot_v2(
        active,
        confirmation,
        conversation_identity=_conversation(),
        observed_at=UPDATED,
    )

    assert result["disposition"] == slots_v2.CONFIRMED
    assert result["slot"]["status"] == cwm_v2.CONFIRMED
    assert result["slot"]["history"][-1]["change_kind"] == "CONFIRMED"


def test_confirmation_of_different_value_fails_closed() -> None:
    active = _slot("implement")
    confirmation = _slot(
        "audit",
        status=cwm_v2.CONFIRMED,
        confidence=cwm_v2.HUMAN_CONFIRMED,
        source_revision=1,
        created_at=UPDATED,
    )

    with pytest.raises(FailClosedRuntimeError, match="does not bind"):
        slots_v2.confirm_semantic_slot_v2(
            active,
            confirmation,
            conversation_identity=_conversation(),
            observed_at=UPDATED,
        )


def test_conflict_invalidates_transitive_dependents_in_prepared_state(
    tmp_path: Path,
) -> None:
    action = _slot("implement")
    subject = _slot(
        "semantic slots",
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    outcome = _slot(
        "deterministic state",
        slot_class=cwm_v2.DESIRED_OUTCOME,
        depends_on=[subject["slot_id"]],
    )
    state = _state(tmp_path, [action, subject, outcome])
    incoming = _slot(
        "audit",
        source_revision=1,
        turn_number=2,
        created_at=UPDATED,
    )

    result = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.MERGE,
        incoming_slot=incoming,
        observed_at=UPDATED,
    )
    revised = {
        item["slot_id"]: item
        for item in result["replacement_state"]["semantic_memory"]["semantic_slots"]
    }

    assert result["disposition"] == slots_v2.CONFLICT_DETECTED
    assert result["invalidated_dependency_ids"] == sorted(
        [subject["slot_id"], outcome["slot_id"]]
    )
    assert revised[action["slot_id"]]["status"] == cwm_v2.CONFLICTED
    assert revised[subject["slot_id"]]["status"] == cwm_v2.STALE
    assert revised[outcome["slot_id"]]["status"] == cwm_v2.STALE


def test_equivalent_update_does_not_stale_dependents(tmp_path: Path) -> None:
    action = _slot("implement")
    subject = _slot(
        "semantic slots",
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _state(tmp_path, [action, subject])
    incoming = _slot(
        "implement", source_revision=1, turn_number=2, created_at=UPDATED
    )

    result = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.MERGE,
        incoming_slot=incoming,
        observed_at=UPDATED,
    )

    assert result["invalidated_dependency_ids"] == []
    subject_after = next(
        item
        for item in result["replacement_state"]["semantic_memory"]["semantic_slots"]
        if item["slot_id"] == subject["slot_id"]
    )
    assert subject_after == subject


def test_dependency_cycle_fails_closed_before_reducer_can_loop(tmp_path: Path) -> None:
    action = _slot("implement")
    subject = _slot(
        "semantic slots",
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _state(tmp_path, [action, subject])
    cyclic_action = _slot(
        "build",
        depends_on=[subject["slot_id"]],
        source_revision=1,
        created_at=UPDATED,
    )

    with pytest.raises(FailClosedRuntimeError, match="cycle"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            state,
            expected_revision=0,
            operation=slots_v2.REPLACE,
            incoming_slot=cyclic_action,
            observed_at=UPDATED,
        )


def test_missing_dependency_fails_closed_on_creation(tmp_path: Path) -> None:
    state = _state(tmp_path)
    missing = "conversation-slot-sha256:" + "a" * 64
    subject = _slot(
        "semantic slots",
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[missing],
        source_revision=1,
        created_at=UPDATED,
    )

    with pytest.raises(FailClosedRuntimeError, match="dependency is absent"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            state,
            expected_revision=0,
            operation=slots_v2.CREATE,
            incoming_slot=subject,
            observed_at=UPDATED,
        )


def test_completeness_evaluation_includes_transitive_blockers() -> None:
    action = _slot(
        "implement",
        status=cwm_v2.CONFLICTED,
        completeness=cwm_v2.CONFLICTED,
        confidence=cwm_v2.CONFLICTED,
    )
    subject = _slot(
        "semantic slots",
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    outcome = _slot(
        "deterministic state",
        slot_class=cwm_v2.DESIRED_OUTCOME,
        depends_on=[subject["slot_id"]],
    )

    result = slots_v2.evaluate_semantic_slot_completeness_v2(
        outcome["slot_id"],
        [action, subject, outcome],
        conversation_identity=_conversation(),
    )

    assert result["classification"] == cwm_v2.CONFLICTED
    assert result["conflicted_dependency_ids"] == [action["slot_id"]]


def test_prepared_document_is_accepted_by_g59_01_atomic_store(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)
    prepared = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=action,
        observed_at=UPDATED,
    )

    stored = cwm_v2.replace_conversation_working_memory_state_v2_atomically(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=prepared["replacement_state"],
        observed_at=UPDATED,
    )

    assert stored == prepared["replacement_state"]
    assert stored["revision"] == 1
    assert stored["semantic_revision"] == 1


def test_reducer_is_deterministic_for_identical_inputs(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)

    first = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=action,
        observed_at=UPDATED,
    )
    second = slots_v2.prepare_semantic_slot_state_update_v2(
        deepcopy(state),
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=deepcopy(action),
        observed_at=UPDATED,
    )

    assert first == second


def test_stale_expected_revision_fails_closed(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)

    with pytest.raises(FailClosedRuntimeError, match="revision does not match"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            state,
            expected_revision=1,
            operation=slots_v2.CREATE,
            incoming_slot=action,
            observed_at=UPDATED,
        )


def test_unknown_operation_fails_closed(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)

    with pytest.raises(FailClosedRuntimeError, match="operation is invalid"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            state,
            expected_revision=0,
            operation="INTERPRET_AND_EXECUTE",
            incoming_slot=action,
            observed_at=UPDATED,
        )


def test_update_time_cannot_move_backwards(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)
    revision_one = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=action,
        observed_at=UPDATED,
    )["replacement_state"]
    incoming = _slot(
        "implement", source_revision=2, turn_number=2, created_at=LATER
    )

    with pytest.raises(FailClosedRuntimeError, match="precedes current state"):
        slots_v2.prepare_semantic_slot_state_update_v2(
            revision_one,
            expected_revision=1,
            operation=slots_v2.MERGE,
            incoming_slot=incoming,
            observed_at=CREATED,
        )


def test_runtime_has_no_persistence_or_execution_pipeline_imports() -> None:
    source = inspect.getsource(slots_v2)
    imported_modules = {
        node.module or ""
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }

    assert "_write_state_atomically" not in source
    assert "replace_conversation_working_memory_state_v2_atomically(" not in source
    assert not any(
        forbidden in module.lower()
        for module in imported_modules
        for forbidden in (
            "authorization",
            "worker",
            "replay",
            "development_governance",
        )
    )


def test_state_result_never_claims_objective_or_execution(tmp_path: Path) -> None:
    state = _state(tmp_path)
    action = _slot("implement", source_revision=1, created_at=UPDATED)

    result = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=action,
        observed_at=UPDATED,
    )

    assert result["objective_created"] is False
    assert result["execution_invoked"] is False
