from __future__ import annotations

from copy import deepcopy
import ast
import inspect
import os
from pathlib import Path
import stat

import pytest

from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_objective_commitment_runtime_v2 as commitment_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-07-OBJECTIVE-COMMITMENT"
CREATED = "2026-08-01T11:00:00Z"


def _time(minute: int) -> str:
    return f"2026-08-01T11:{minute:02d}:00Z"


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


def _conversation(
    *, workspace: str = WORKSPACE, session: str = SESSION, created: str = CREATED
) -> str:
    return cwm_v2.conversation_working_memory_conversation_identity_v2(
        workspace_identity=workspace,
        session_identity=session,
        created_at=created,
    )


def _slot(
    value: str,
    *,
    source_revision: int,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    materiality: str = cwm_v2.REQUIRED,
    depends_on=(),
    conversation: str | None = None,
) -> dict:
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=conversation or _conversation(),
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        status=cwm_v2.ASSERTED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.HUMAN_ASSERTED,
        materiality=materiality,
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": source_revision,
                "source_revision": source_revision,
                "source_span": value,
                "content_digest": cwm_v2._checksum(value),
                "normalization_rule_ids": [],
                "human_disposition": "ASSERTED",
            }
        ],
        depends_on=sorted(depends_on),
        created_at=_time(source_revision),
    )


def _create(
    tmp_path: Path,
    *,
    workspace: str = WORKSPACE,
    session: str = SESSION,
    created: str = CREATED,
) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=workspace,
        session_identity=session,
        created_at=created,
        ttl_seconds=3600,
        participants=_participants(),
    )


def _apply_and_persist(
    tmp_path: Path,
    state: dict,
    slot: dict,
    minute: int,
    operation: str = slots_v2.CREATE,
) -> dict:
    clarification = state["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    if clarification is None:
        prepared = machine_v2.prepare_conversation_semantic_update_v2(
            state,
            expected_revision=state["revision"],
            operation=operation,
            incoming_slot=slot,
            observed_at=_time(minute),
        )["replacement_state"]
    else:
        prepared = machine_v2.prepare_clarification_answer_v2(
            state,
            expected_revision=state["revision"],
            clarification_id=clarification["clarification_id"],
            operation=operation,
            incoming_slot=slot,
            observed_at=_time(minute),
        )["replacement_state"]
    return machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=state["revision"],
        replacement_state=prepared,
        observed_at=_time(minute),
    )


def _review_state(tmp_path: Path, *, action_value: str = "implement") -> dict:
    state = _create(tmp_path)
    action = _slot(action_value, source_revision=1)
    state = _apply_and_persist(tmp_path, state, action, 1)
    subject = _slot(
        "Objective Commitment Runtime",
        source_revision=2,
        slot_class=cwm_v2.OPERATIVE_SUBJECT,
        depends_on=[action["slot_id"]],
    )
    state = _apply_and_persist(tmp_path, state, subject, 2)
    outcome = _slot(
        "one immutable isolated commitment record",
        source_revision=3,
        slot_class=cwm_v2.DESIRED_OUTCOME,
        depends_on=[action["slot_id"], subject["slot_id"]],
    )
    state = _apply_and_persist(tmp_path, state, outcome, 3)
    work_type = _slot(
        "IMPLEMENTATION",
        source_revision=4,
        slot_class=cwm_v2.WORK_TYPE,
        slot_role="IMPLEMENTATION",
        depends_on=[action["slot_id"]],
    )
    return _apply_and_persist(tmp_path, state, work_type, 4)


def _ready_state(tmp_path: Path, *, action_value: str = "implement") -> dict:
    state = _review_state(tmp_path, action_value=action_value)
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    prepared = machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=state["revision"],
        confirmation_request=request,
        observed_at=_time(5),
    )["replacement_state"]
    return machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=state["revision"],
        replacement_state=prepared,
        observed_at=_time(5),
    )


def _rich_ready_state(tmp_path: Path) -> dict:
    state = _review_state(tmp_path)
    action_id = next(
        slot["slot_id"]
        for slot in state["semantic_memory"]["semantic_slots"]
        if slot["slot_class"] == cwm_v2.OPERATIVE_ACTION
    )
    additions = (
        _slot(
            "Do not integrate Platform Core",
            source_revision=5,
            slot_class=cwm_v2.GOVERNING_QUALIFIER,
            slot_role=cwm_v2.PRESERVATION,
            cardinality_key="non-goal:platform-core",
            materiality=cwm_v2.CONDITIONAL,
            depends_on=[action_id],
        ),
        _slot(
            "Return one immutable record",
            source_revision=6,
            slot_class=cwm_v2.GOVERNING_QUALIFIER,
            slot_role=cwm_v2.OUTPUT,
            cardinality_key="output:record",
            materiality=cwm_v2.CONDITIONAL,
            depends_on=[action_id],
        ),
        _slot(
            "Reject stale readiness",
            source_revision=7,
            slot_class=cwm_v2.GOVERNING_QUALIFIER,
            slot_role=cwm_v2.ACCEPTANCE,
            cardinality_key="acceptance:stale",
            materiality=cwm_v2.CONDITIONAL,
            depends_on=[action_id],
        ),
        _slot(
            "aigol/runtime",
            source_revision=8,
            slot_class=cwm_v2.SEMANTIC_REFERENCE,
            slot_role=cwm_v2.SCOPE,
            cardinality_key="scope:runtime",
            materiality=cwm_v2.CONDITIONAL,
            depends_on=[action_id],
        ),
    )
    for minute, slot in enumerate(additions, start=5):
        state = _apply_and_persist(tmp_path, state, slot, minute)
    confirmation = machine_v2.create_candidate_confirmation_request_v2(state)
    prepared = machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=state["revision"],
        confirmation_request=confirmation,
        observed_at=_time(9),
    )["replacement_state"]
    return machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=state["revision"],
        replacement_state=prepared,
        observed_at=_time(9),
    )


def _readiness(state: dict) -> dict:
    return readiness_v2.evaluate_objective_readiness_v2(
        state,
        expected_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        observed_at=state["envelope"]["updated_at"],
    )


def _request(state: dict) -> dict:
    report = _readiness(state)
    snapshot = commitment_v2.build_candidate_objective_snapshot_v2(
        state, readiness_report=report
    )
    digest = commitment_v2.compute_candidate_objective_digest_v2(snapshot)
    human = next(
        participant
        for participant in state["envelope"]["participants"]
        if participant["participant_role"] == cwm_v2.HUMAN_ORIGINATOR
    )
    return commitment_v2.create_objective_commitment_request_v2(
        state,
        readiness_report=report,
        explicit_commit_action=f"/commit {digest}",
        human_participant_digest=cwm_v2._checksum(human),
        requested_at=report["evaluated_at"],
    )


def _commit(tmp_path: Path, request: dict) -> dict:
    return commitment_v2.commit_objective_snapshot_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        commitment_request=request,
    )


def test_candidate_snapshot_and_digest_are_exact_and_deterministic(
    tmp_path: Path,
) -> None:
    state = _rich_ready_state(tmp_path)
    report = _readiness(state)

    first = commitment_v2.build_candidate_objective_snapshot_v2(
        state, readiness_report=report
    )
    second = commitment_v2.build_candidate_objective_snapshot_v2(
        deepcopy(state), readiness_report=deepcopy(report)
    )
    digest = commitment_v2.compute_candidate_objective_digest_v2(first)

    assert first == second
    assert digest == cwm_v2._checksum(first)
    assert first["canonical_objective"] == {
        "requested_action": "implement",
        "subject": "Objective Commitment Runtime",
        "expected_outcome": "one immutable isolated commitment record",
        "work_type": "IMPLEMENTATION",
    }
    assert first["mutation_boundary"]["preservation_constraints"] == [
        "Do not integrate Platform Core"
    ]
    assert first["mutation_boundary"]["scope_references"] == ["aigol/runtime"]
    assert first["output_constraints"] == ["Return one immutable record"]
    assert first["acceptance_criteria"] == ["Reject stale readiness"]
    assert first["explicit_non_goals"] == ["Do not integrate Platform Core"]
    assert first["resolved_ambiguity_state"]["material_ambiguity_resolved"] is True
    assert first["exploratory_transcript_included"] is False
    assert first["execution_authority"] is False


def test_request_and_commitment_identity_are_deterministic(tmp_path: Path) -> None:
    state = _ready_state(tmp_path)

    first = _request(state)
    second = _request(deepcopy(state))

    assert first == second
    assert first["commitment_identity"] == second["commitment_identity"]
    assert first["commitment_idempotency_key"] == second[
        "commitment_idempotency_key"
    ]


def test_valid_readiness_bound_commit_creates_immutable_record(
    tmp_path: Path,
) -> None:
    state = _ready_state(tmp_path)
    request = _request(state)

    result = _commit(tmp_path, request)
    record = commitment_v2.validate_objective_commitment_record_v2(
        result["commitment_record"]
    )
    cwm_state = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(5),
    )
    record_path = commitment_v2._record_path(
        commitment_v2._commitment_root(cwm_v2._conversation_root(tmp_path)),
        request["commitment_identity"],
    )

    assert result["disposition"] == commitment_v2.COMMITTED
    assert result["commitment_record_created"] is True
    assert result["cwm_cleanup_complete"] is True
    assert cwm_state is None
    assert record["commitment_identity"] == request["commitment_identity"]
    assert stat.S_IMODE(record_path.stat().st_mode) == stat.S_IRUSR
    assert record_path.read_bytes() == cwm_v2._canonical_bytes(record)
    assert record["pipeline_objective_created"] is False
    assert record["execution_authority"] is False


@pytest.mark.parametrize(
    "action",
    [
        "yes, commit it",
        "commit",
        "/commit",
        "/commit sha256:" + "0" * 64,
    ],
)
def test_explicit_human_commit_action_is_required(
    tmp_path: Path, action: str
) -> None:
    state = _ready_state(tmp_path)
    report = _readiness(state)
    snapshot = commitment_v2.build_candidate_objective_snapshot_v2(
        state, readiness_report=report
    )
    human = state["envelope"]["participants"][0]

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        commitment_v2.create_objective_commitment_request_v2(
            state,
            readiness_report=report,
            explicit_commit_action=action,
            human_participant_digest=cwm_v2._checksum(human),
            requested_at=report["evaluated_at"],
        )

    assert raised.value.reason_code == "EXPLICIT_COMMIT_REQUIRED"
    assert commitment_v2.compute_candidate_objective_digest_v2(snapshot)


def test_stale_cwm_revision_and_readiness_are_rejected(tmp_path: Path) -> None:
    state = _ready_state(tmp_path)
    request = _request(state)
    prepared = machine_v2.prepare_conversation_suspension_v2(
        state,
        expected_revision=state["revision"],
        observed_at=_time(6),
    )["replacement_state"]
    machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=state["revision"],
        replacement_state=prepared,
        observed_at=_time(6),
    )

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        _commit(tmp_path, request)
    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as stale_report:
        commitment_v2.build_candidate_objective_snapshot_v2(
            prepared, readiness_report=request["readiness_report"]
        )

    assert raised.value.reason_code == "STALE_CWM_REVISION"
    assert stale_report.value.reason_code == "STALE_READINESS"


@pytest.mark.parametrize(
    "workspace, session",
    [("/workspace/other", SESSION), (WORKSPACE, "OTHER-SESSION")],
)
def test_wrong_workspace_or_session_is_rejected(
    tmp_path: Path, workspace: str, session: str
) -> None:
    request = _request(_ready_state(tmp_path))

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        commitment_v2.commit_objective_snapshot_v2(
            runtime_root=tmp_path,
            workspace_identity=workspace,
            session_identity=session,
            commitment_request=request,
        )

    assert raised.value.reason_code == "IDENTITY_BINDING_MISMATCH"


def test_wrong_conversation_binding_is_rejected(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    source_root = tmp_path / "source"
    _ready_state(target_root)
    source_state = _create(
        source_root,
        created="2026-08-01T10:59:00Z",
    )
    # Build a valid source request with the normal helpers after replacing the
    # stored source state with the canonical fixture identity is intentionally
    # impossible; the exact target mismatch is exercised by the request field.
    request = _request(_ready_state(tmp_path / "request"))
    altered = deepcopy(request)
    altered["conversation_identity"] = source_state["envelope"][
        "conversation_identity"
    ]

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        commitment_v2.validate_objective_commitment_request_v2(altered)

    assert raised.value.reason_code in {
        "COMMITMENT_REQUEST_INVALID",
        "COMMITMENT_IDENTITY_INVALID",
    }


def test_semantic_slot_revision_mismatch_is_rejected(tmp_path: Path) -> None:
    request = _request(_ready_state(tmp_path))
    request["source_semantic_slot_revisions"][0]["slot_revision"] += 1

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        commitment_v2.validate_objective_commitment_request_v2(request)

    assert raised.value.reason_code == "SLOT_REVISION_MISMATCH"


def test_unresolved_ambiguity_and_conflict_are_rejected(tmp_path: Path) -> None:
    collecting = _create(tmp_path / "collecting")
    collecting_report = readiness_v2.evaluate_objective_readiness_v2(
        collecting,
        expected_revision=0,
        expected_semantic_revision=0,
        observed_at=CREATED,
    )
    review = _review_state(tmp_path / "conflict")
    incoming = _slot("audit", source_revision=5)
    conflicted = machine_v2.prepare_conversation_semantic_update_v2(
        review,
        expected_revision=review["revision"],
        operation=slots_v2.MERGE,
        incoming_slot=incoming,
        observed_at=_time(5),
    )["replacement_state"]
    conflict_report = readiness_v2.evaluate_objective_readiness_v2(
        conflicted,
        expected_revision=conflicted["revision"],
        expected_semantic_revision=conflicted["semantic_revision"],
        observed_at=_time(5),
    )

    for state, report in ((collecting, collecting_report), (conflicted, conflict_report)):
        with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
            commitment_v2.build_candidate_objective_snapshot_v2(
                state, readiness_report=report
            )
        assert raised.value.reason_code == "READINESS_NOT_READY"


def test_identical_repeat_is_idempotent_after_cwm_cleanup(tmp_path: Path) -> None:
    request = _request(_ready_state(tmp_path))
    first = _commit(tmp_path, request)

    repeated = _commit(tmp_path, request)

    assert first["disposition"] == commitment_v2.COMMITTED
    assert repeated["disposition"] == commitment_v2.ALREADY_COMMITTED
    assert repeated["commitment_record"] == first["commitment_record"]
    assert repeated["commitment_record_created"] is False


def test_conflicting_duplicate_episode_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    alternate = tmp_path / "alternate"
    request_one = _request(_ready_state(target, action_value="implement"))
    request_two = _request(_ready_state(alternate, action_value="audit"))
    original_write = commitment_v2._write_immutable_json

    def fail_record(path: Path, value: dict) -> None:
        if commitment_v2._RECORD_DIRECTORY in path.parts:
            raise commitment_v2.ObjectiveCommitmentError(
                "COMMITMENT_WRITE_FAILED", "simulated record failure"
            )
        original_write(path, value)

    monkeypatch.setattr(commitment_v2, "_write_immutable_json", fail_record)
    with pytest.raises(commitment_v2.ObjectiveCommitmentError):
        _commit(target, request_one)

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        _commit(target, request_two)

    assert raised.value.reason_code == "CONFLICTING_COMMITMENT"


def test_write_failure_leaves_recoverable_intent_and_restart_reconciles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = _ready_state(tmp_path)
    request = _request(state)
    original_write = commitment_v2._write_immutable_json

    def fail_record(path: Path, value: dict) -> None:
        if commitment_v2._RECORD_DIRECTORY in path.parts:
            raise commitment_v2.ObjectiveCommitmentError(
                "COMMITMENT_WRITE_FAILED", "simulated record failure"
            )
        original_write(path, value)

    monkeypatch.setattr(commitment_v2, "_write_immutable_json", fail_record)
    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        _commit(tmp_path, request)
    assert raised.value.reason_code == "COMMITMENT_WRITE_FAILED"
    assert cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(5),
    ) == state

    monkeypatch.setattr(commitment_v2, "_write_immutable_json", original_write)
    recovered = commitment_v2.restore_or_reconcile_objective_commitment_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        conversation_identity=request["conversation_identity"],
    )

    assert recovered["disposition"] == commitment_v2.RECOVERED_COMMITTED
    assert recovered["cwm_cleanup_complete"] is True


def test_cleanup_pending_recovery_preserves_immutable_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _request(_ready_state(tmp_path))
    original_cleanup = commitment_v2._cleanup_cwm_episode
    monkeypatch.setattr(
        commitment_v2, "_cleanup_cwm_episode", lambda state_path, root: False
    )

    pending = _commit(tmp_path, request)
    immutable = deepcopy(pending["commitment_record"])
    assert pending["disposition"] == commitment_v2.CLEANUP_PENDING
    assert pending["cwm_episode_state"] == commitment_v2.CLEANUP_PENDING

    monkeypatch.setattr(commitment_v2, "_cleanup_cwm_episode", original_cleanup)
    recovered = commitment_v2.restore_or_reconcile_objective_commitment_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        conversation_identity=request["conversation_identity"],
    )

    assert recovered["disposition"] == commitment_v2.RECOVERED_COMMITTED
    assert recovered["commitment_record"] == immutable


def test_tampered_persisted_record_fails_closed(tmp_path: Path) -> None:
    request = _request(_ready_state(tmp_path))
    result = _commit(tmp_path, request)
    store = commitment_v2._commitment_root(cwm_v2._conversation_root(tmp_path))
    path = commitment_v2._record_path(store, request["commitment_identity"])
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    tampered = deepcopy(result["commitment_record"])
    tampered["execution_authority"] = True
    path.write_bytes(cwm_v2._canonical_bytes(tampered))
    os.chmod(path, stat.S_IRUSR)

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        _commit(tmp_path, request)

    assert raised.value.reason_code in {
        "FORBIDDEN_AUTHORITY_FIELD",
        "INVALID_INTEGRITY",
    }


def test_different_valid_record_at_same_identity_is_a_conflicting_duplicate(
    tmp_path: Path,
) -> None:
    request = _request(_ready_state(tmp_path))
    result = _commit(tmp_path, request)
    store = commitment_v2._commitment_root(cwm_v2._conversation_root(tmp_path))
    path = commitment_v2._record_path(store, request["commitment_identity"])
    conflicting = deepcopy(result["commitment_record"])
    conflicting["source_request_digest"] = "sha256:" + "a" * 64
    conflicting["integrity_checksum"] = commitment_v2._integrity(conflicting)
    assert commitment_v2.validate_objective_commitment_record_v2(conflicting)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    path.write_bytes(cwm_v2._canonical_bytes(conflicting))
    os.chmod(path, stat.S_IRUSR)

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        _commit(tmp_path, request)

    assert raised.value.reason_code == "CONFLICTING_COMMITMENT"


def test_request_and_record_reject_execution_authority_fields(tmp_path: Path) -> None:
    request = _request(_ready_state(tmp_path))
    request["authorization_requested"] = True

    with pytest.raises(commitment_v2.ObjectiveCommitmentError) as raised:
        commitment_v2.validate_objective_commitment_request_v2(request)

    assert raised.value.reason_code == "FORBIDDEN_AUTHORITY_FIELD"


def test_runtime_has_no_execution_pipeline_or_transport_imports() -> None:
    source = inspect.getsource(commitment_v2)
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
            "approval",
            "aicli",
            "human_interface",
            "provider",
        )
    )
