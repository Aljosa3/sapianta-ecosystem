from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import human_interface_conversation_execution_integration_v2 as execution_v2
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2
from aigol.runtime.execution_authorization_runtime import (
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


WORKSPACE = "/workspace/sapianta"
SESSION = "G60-03-REAL-WORLD"
CREATED = "2026-08-01T14:00:00Z"
RULESET = "G60_03_REAL_WORLD_VALIDATION_RULESET_V1"

TURNS = (
    "action: Review and normalize",
    "subject: a repository implementation change",
    "outcome: canonical change evidence",
    "work-type: ANALYSIS",
)


def _time(second: int) -> str:
    return f"2026-08-01T14:00:{second:02d}Z"


def _hash(label: str) -> str:
    return replay_hash({"label": label})


def _manifest(tmp_path: Path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G60-03-000001",
        canonical_chain_id="CHAIN-G60-03-000001",
        implementation_bundle_id="G60_03_REAL_WORLD_NORMALIZATION",
        source_candidate_reference="CANDIDATE-G60-03-000001",
        source_candidate_hash=_hash("candidate"),
        implementation_handoff_reference="HANDOFF-G60-03-000001",
        implementation_handoff_hash=_hash("handoff"),
        provider_generation_authorization_reference="AUTH-G60-03-000001",
        provider_generation_authorization_hash=_hash("authorization"),
        provider_response_reference="RESPONSE-G60-03-000001",
        provider_response_hash=_hash("response"),
        target_domain="PLATFORM_CORE",
        target_resource="G60_03_REAL_WORLD_VALIDATION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G60-03-000001",
                "target_path": "bounded/g60_03_validation_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED,
        replay_dir=tmp_path / "manifest",
    )["implementation_manifest_artifact"]


def _start(tmp_path: Path, *, session: str = SESSION) -> dict:
    return hir_v2.create_hir_conversation_session_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        human_identity="local-human",
        created_at=CREATED,
    )["state"]


def _admit_turns(
    tmp_path: Path,
    turns: tuple[str, ...] = TURNS,
    *,
    session: str = SESSION,
    start_second: int = 1,
) -> list[dict]:
    results = []
    for offset, text in enumerate(turns):
        results.append(
            hir_v2.admit_hir_semantic_turn_v2(
                runtime_root=tmp_path,
                workspace_identity=WORKSPACE,
                session_identity=session,
                source_turn_text=text,
                observed_at=_time(start_second + offset),
            )
        )
    return results


def _complete_review(tmp_path: Path, *, session: str = SESSION) -> dict:
    _start(tmp_path, session=session)
    return _admit_turns(tmp_path, session=session)[-1]["state"]


def _active_slot(state: dict, slot_class: str) -> dict:
    return next(
        slot
        for slot in state["semantic_memory"]["semantic_slots"]
        if slot["slot_class"] == slot_class
    )


def _incoming_slot(
    state: dict,
    slot_class: str,
    value: str,
    *,
    observed_at: str,
    disposition: str = "ASSERTED",
) -> dict:
    active = _active_slot(state, slot_class)
    canonical_value = value.upper() if slot_class == cwm_v2.WORK_TYPE else value
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        slot_class=active["slot_class"],
        slot_role=active["slot_role"],
        cardinality_key=active["cardinality_key"],
        surface_value=value,
        canonical_value=canonical_value,
        status=cwm_v2.ASSERTED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.HUMAN_ASSERTED,
        materiality=active["materiality"],
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": state["revision"] + 1,
                "source_revision": state["revision"],
                "source_span": value,
                "content_digest": cwm_v2._checksum(value),
                "normalization_rule_ids": [RULESET],
                "human_disposition": disposition,
            }
        ],
        depends_on=active["depends_on"],
        created_at=observed_at,
    )


def _persist_prepared(
    tmp_path: Path,
    state: dict,
    prepared: dict,
    *,
    observed_at: str,
    session: str = SESSION,
) -> dict:
    replacement = prepared["replacement_state"]
    assert replacement is not None
    return machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(tmp_path),
        workspace_identity=WORKSPACE,
        session_identity=session,
        expected_revision=state["revision"],
        replacement_state=replacement,
        observed_at=observed_at,
    )


def _correct(
    tmp_path: Path,
    state: dict,
    slot_class: str,
    value: str,
    *,
    observed_at: str,
    session: str = SESSION,
) -> dict:
    prepared = machine_v2.prepare_conversation_correction_v2(
        state,
        expected_revision=state["revision"],
        incoming_slot=_incoming_slot(
            state, slot_class, value, observed_at=observed_at
        ),
        observed_at=observed_at,
    )
    return _persist_prepared(
        tmp_path, state, prepared, observed_at=observed_at, session=session
    )


def _confirm_and_commit(
    tmp_path: Path,
    state: dict,
    *,
    confirm_at: str,
    commit_at: str,
    session: str = SESSION,
) -> dict:
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    confirmed = hir_v2.confirm_hir_candidate_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_confirmation_action=f"/confirm {request['candidate_digest']}",
        observed_at=confirm_at,
    )
    return hir_v2.create_hir_objective_commitment_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_commit_action=confirmed["expected_commit_action"],
        observed_at=commit_at,
    )


def _execute_commitment(tmp_path: Path, commitment: dict, *, session: str = SESSION) -> dict:
    prepared = execution_v2.prepare_committed_objective_execution_v2(
        commitment_record=commitment["commitment_record"],
        explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
        runtime_root=tmp_path / "execution",
        workspace=WORKSPACE,
        session_id=session,
        human_actor="local-human",
        created_at=CREATED,
    )
    completed = execution_v2.authorize_and_execute_prepared_objective_v2(
        prepared,
        explicit_authorization_action=prepared["expected_authorization_action"],
    )
    completed["_validation_prepared"] = prepared
    return completed


def _execution_projection(completed: dict) -> dict:
    replay = completed["replay_evidence"]
    return {
        "completion_status": completed["completion_status"],
        "capability": replay["capability_route"]["selected_capability_identifier"],
        "authorization": replay["authorization"]["authorization_status"],
        "request": replay["worker_request"]["request_status"],
        "assignment": replay["worker_assignment"]["assignment_status"],
        "dispatch": replay["worker_dispatch"]["dispatch_status"],
        "invocation": replay["worker_invocation"]["invocation_status"],
        "execution": replay["execution"]["execution_status"],
        "capture": replay["worker_result_capture"]["result_capture_status"],
        "validation": replay["worker_result_validation"]["validation_status"],
        "completion": replay["completion"]["completion_status"],
        "human_message": completed["human_visible_completion_result"]["message"],
    }


def test_realistic_multiturn_clarification_reaches_complete_pipeline(
    tmp_path: Path,
) -> None:
    _start(tmp_path / "conversation")
    turns = _admit_turns(tmp_path / "conversation")

    clarification_targets = [
        result["state"]["semantic_memory"]["protocol_control"][
            "clarification_control"
        ]["trigger_slot_id"]
        for result in turns[:3]
    ]
    assert clarification_targets == [
        "required-slot:OPERATIVE_SUBJECT:PRIMARY",
        "required-slot:DESIRED_OUTCOME:PRIMARY",
        "required-slot:WORK_TYPE:PRIMARY",
    ]
    assert turns[-1]["protocol_state"] == machine_v2.CANDIDATE_REVIEW

    commitment = _confirm_and_commit(
        tmp_path / "conversation",
        turns[-1]["state"],
        confirm_at=_time(5),
        commit_at=_time(6),
    )
    completed = _execute_commitment(tmp_path, commitment)
    assert completed["completion_status"] == (
        execution_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_explicit_correction_replaces_earlier_statement_before_execution(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _complete_review(conversation)
    state = _correct(
        conversation,
        state,
        cwm_v2.OPERATIVE_SUBJECT,
        "a bounded repository implementation change",
        observed_at=_time(5),
    )
    assert machine_v2.derive_conversation_protocol_state_v2(
        state, observed_at=_time(5)
    ) == machine_v2.CLARIFYING
    state = _correct(
        conversation,
        state,
        cwm_v2.DESIRED_OUTCOME,
        "verified canonical change evidence",
        observed_at=_time(6),
    )
    assert machine_v2.derive_conversation_protocol_state_v2(
        state, observed_at=_time(6)
    ) == machine_v2.CANDIDATE_REVIEW

    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(7), commit_at=_time(8)
    )
    completed = _execute_commitment(tmp_path, commitment)
    request = completed["_validation_prepared"]["platform_core_objective"][
        "source_request"
    ]
    assert "bounded repository implementation change" in request
    assert "verified canonical change evidence" in request


def test_interruption_persisted_suspension_and_exact_session_resume(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _start(conversation)
    state = _admit_turns(conversation, TURNS[:2])[-1]["state"]
    suspended_at = _time(3)
    prepared = machine_v2.prepare_conversation_suspension_v2(
        state, expected_revision=state["revision"], observed_at=suspended_at
    )
    suspended = _persist_prepared(
        conversation, state, prepared, observed_at=suspended_at
    )

    reloaded = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=conversation,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(4),
    )
    assert reloaded is not None
    assert reloaded["envelope"]["availability_state"] == cwm_v2.SUSPENDED
    with pytest.raises(FailClosedRuntimeError, match="requires active"):
        machine_v2.prepare_conversation_correction_v2(
            reloaded,
            expected_revision=reloaded["revision"],
            incoming_slot=_incoming_slot(
                reloaded,
                cwm_v2.OPERATIVE_SUBJECT,
                "a different change",
                observed_at=_time(4),
            ),
            observed_at=_time(4),
        )

    resume = machine_v2.prepare_conversation_resume_v2(
        suspended,
        expected_revision=suspended["revision"],
        current_interface_identity=cwm_v2.LOCAL_CONVERSATION_V2,
        participant_binding_digest=cwm_v2._checksum(
            suspended["envelope"]["participants"]
        ),
        observed_at=_time(4),
    )
    resumed = _persist_prepared(
        conversation, suspended, resume, observed_at=_time(4)
    )
    assert resumed["semantic_revision"] == suspended["semantic_revision"]

    state = _admit_turns(
        conversation, TURNS[2:], start_second=5
    )[-1]["state"]
    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(7), commit_at=_time(8)
    )
    assert _execute_commitment(tmp_path, commitment)["completion_status"] == (
        execution_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_conflicting_requirements_block_then_explicit_resolution_recovers(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _complete_review(conversation)
    conflict_at = _time(5)
    conflict = machine_v2.prepare_conversation_semantic_update_v2(
        state,
        expected_revision=state["revision"],
        operation=slots_v2.MERGE,
        incoming_slot=_incoming_slot(
            state,
            cwm_v2.OPERATIVE_ACTION,
            "Delete repository history",
            observed_at=conflict_at,
            disposition="ASSERTED",
        ),
        observed_at=conflict_at,
    )
    state = _persist_prepared(
        conversation, state, conflict, observed_at=conflict_at
    )
    clarification = state["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    assert clarification["trigger_reason"] == "CONFLICTED"
    assert clarification["candidate_values"] == [
        "Delete repository history",
        "Review and normalize",
    ]
    refused = readiness_v2.evaluate_objective_readiness_v2(
        state,
        expected_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        observed_at=conflict_at,
    )
    assert refused["readiness_disposition"] == readiness_v2.NOT_READY
    assert refused["unresolved_conflict_slot_ids"]

    repairs = (
        (cwm_v2.OPERATIVE_ACTION, "Review and normalize"),
        (cwm_v2.OPERATIVE_SUBJECT, "a repository implementation change"),
        (cwm_v2.DESIRED_OUTCOME, "canonical change evidence"),
        (cwm_v2.WORK_TYPE, "ANALYSIS"),
    )
    for second, (slot_class, value) in enumerate(repairs, start=6):
        state = _correct(
            conversation,
            state,
            slot_class,
            value,
            observed_at=_time(second),
        )
    assert machine_v2.derive_conversation_protocol_state_v2(
        state, observed_at=_time(9)
    ) == machine_v2.CANDIDATE_REVIEW

    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(10), commit_at=_time(11)
    )
    assert _execute_commitment(tmp_path, commitment)["completion_status"] == (
        execution_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_objective_revision_invalidates_old_confirmation_before_commitment(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _complete_review(conversation)
    original_request = machine_v2.create_candidate_confirmation_request_v2(state)
    confirmed = hir_v2.confirm_hir_candidate_v2(
        runtime_root=conversation,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        explicit_confirmation_action=(
            f"/confirm {original_request['candidate_digest']}"
        ),
        observed_at=_time(5),
    )
    old_commit_action = confirmed["expected_commit_action"]
    state = _correct(
        conversation,
        confirmed["state"],
        cwm_v2.DESIRED_OUTCOME,
        "revised canonical change evidence",
        observed_at=_time(6),
    )
    assert state["semantic_memory"]["protocol_control"][
        "confirmation_binding"
    ] is None
    with pytest.raises(FailClosedRuntimeError):
        hir_v2.create_hir_objective_commitment_v2(
            runtime_root=conversation,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            explicit_commit_action=old_commit_action,
            observed_at=_time(7),
        )

    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(8), commit_at=_time(9)
    )
    assert commitment["candidate_objective_digest"] != confirmed[
        "objective_candidate_digest"
    ]
    completed = _execute_commitment(tmp_path, commitment)
    objective = completed["_validation_prepared"]["platform_core_objective"]
    assert "revised canonical change evidence" in objective["source_request"]


def test_repeated_identical_requests_and_executions_are_deterministic(
    tmp_path: Path,
) -> None:
    completed_runs = []
    commitments = []
    objectives = []
    selections = []
    for label in ("left", "right"):
        root = tmp_path / label
        conversation = root / "conversation"
        state = _complete_review(conversation)
        commitment = _confirm_and_commit(
            conversation, state, confirm_at=_time(5), commit_at=_time(6)
        )
        completed = _execute_commitment(root, commitment)
        commitments.append(commitment["commitment_identity"])
        prepared = completed["_validation_prepared"]
        objectives.append(prepared["platform_core_objective"]["artifact_hash"])
        selections.append(
            prepared["semantic_capability_route"]["selection_hash"]
        )
        completed_runs.append(_execution_projection(completed))

    assert commitments[0] == commitments[1]
    assert objectives[0] == objectives[1]
    assert selections[0] == selections[1]
    assert completed_runs[0] == completed_runs[1]


def test_replay_verification_reconstructs_and_rejects_tampering(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _complete_review(conversation)
    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(5), commit_at=_time(6)
    )
    completed = _execute_commitment(tmp_path, commitment)
    assert len(completed["replay_evidence"]) == 14
    replay_dir = Path(
        completed["authorization"]["execution_authorization_replay_reference"]
    )
    reconstructed = reconstruct_execution_authorization_replay(replay_dir)
    assert reconstructed["authorization_status"] == "EXECUTION_AUTHORIZED"

    wrapper_path = replay_dir / "002_authorization_artifact_recorded.json"
    wrapper = load_json(wrapper_path)
    wrapper["artifact"]["authorization_status"] = "TAMPERED"
    wrapper_path.write_text(
        json.dumps(wrapper, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_execution_authorization_replay(replay_dir)


def test_authorization_failure_recovers_before_any_worker_side_effect(
    tmp_path: Path,
) -> None:
    conversation = tmp_path / "conversation"
    state = _complete_review(conversation)
    commitment = _confirm_and_commit(
        conversation, state, confirm_at=_time(5), commit_at=_time(6)
    )
    prepared = execution_v2.prepare_committed_objective_execution_v2(
        commitment_record=commitment["commitment_record"],
        explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
        runtime_root=tmp_path / "execution",
        workspace=WORKSPACE,
        session_id=SESSION,
        human_actor="local-human",
        created_at=CREATED,
    )
    with pytest.raises(FailClosedRuntimeError, match="exact /authorize"):
        execution_v2.authorize_and_execute_prepared_objective_v2(
            prepared,
            explicit_authorization_action="/authorize sha256:" + "0" * 64,
        )
    integration_root = Path(prepared["integration_root"])
    assert not (integration_root / "authorization").exists()
    assert not (integration_root / "worker_dispatch").exists()

    recovered = execution_v2.authorize_and_execute_prepared_objective_v2(
        prepared,
        explicit_authorization_action=prepared["expected_authorization_action"],
    )
    assert recovered["completion_status"] == (
        execution_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_terminal_authorization_typo_is_refused_then_corrected_in_session(
    tmp_path: Path,
) -> None:
    fixed = iter(TURNS)
    outputs: list[str] = []
    authorization_attempts = 0
    turn = 0

    def reader(prompt: str) -> str:
        nonlocal authorization_attempts, turn
        if turn < 4:
            value = next(fixed)
        elif prompt == "aicli-v2-authorization> ":
            authorization_attempts += 1
            if authorization_attempts == 1:
                value = "/authorize sha256:" + "0" * 64
            else:
                value = next(
                    item.removeprefix("next: ")
                    for item in reversed(outputs)
                    if item.startswith("next: /authorize ")
                )
        else:
            value = next(
                item.removeprefix("next: ")
                for item in reversed(outputs)
                if item.startswith("next: ")
            )
        turn += 1
        outputs.append(prompt + value)
        return value

    completed = execution_v2.run_complete_conversation_execution_terminal_v2(
        runtime_root=tmp_path / "runtime",
        workspace=WORKSPACE,
        session_id=SESSION,
        human_identity="local-human",
        created_at=CREATED,
        explicit_canonical_artifacts=[_manifest(tmp_path / "artifact")],
        input_reader=reader,
        output_writer=outputs.append,
    )
    transcript = "\n".join(outputs)

    assert "authorization_refused: EXACT_EXECUTION_SUMMARY_HASH_REQUIRED" in transcript
    assert "worker_dispatched: false" in transcript
    assert transcript.index("worker_dispatched: false") < transcript.index(
        "authorization: EXECUTION_AUTHORIZED"
    )
    assert completed["completion_status"] == (
        execution_v2.COMPLETE_PIPELINE_RETURNED_TO_AICLI
    )


def test_validation_suite_does_not_define_or_redesign_execution_owners() -> None:
    source = Path(execution_v2.__file__).read_text(encoding="utf-8")
    definitions = {
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert definitions.isdisjoint(
        {
            "authorize_execution_ready",
            "dispatch_assigned_worker",
            "invoke_dispatched_worker",
            "start_execution",
            "capture_worker_result",
            "validate_worker_result",
        }
    )
