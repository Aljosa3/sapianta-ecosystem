from __future__ import annotations

from copy import deepcopy
import ast
import inspect
from pathlib import Path

import pytest

from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as commit_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-05-PROPOSAL-COMMIT"
CREATED = "2026-08-01T09:00:00Z"
COMMITTED = "2026-08-01T09:01:00Z"
PARSER = "conversation-deterministic-parser-v1"


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


def _human_slot(
    conversation: str,
    value: str,
    *,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
) -> dict:
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=conversation,
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        status=cwm_v2.ASSERTED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.HUMAN_ASSERTED,
        materiality=cwm_v2.REQUIRED,
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": 0,
                "source_revision": 0,
                "source_span": value,
                "content_digest": cwm_v2._checksum(value),
                "normalization_rule_ids": [],
                "human_disposition": "ASSERTED",
            }
        ],
        depends_on=[],
        created_at=CREATED,
    )


def _state(tmp_path: Path, *, semantic_slots: list[dict] | None = None) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=3600,
        participants=_participants(),
        semantic_slots=semantic_slots or [],
    )


def _operation(
    state: dict,
    text: str,
    *,
    value: str,
    operation_type: str = proposal_v2.PROPOSE_SLOT_CREATION,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    target_slot_id: str | None = None,
    evidence_reference_ids: list[str] | None = None,
    depends_on_slot_ids: list[str] | None = None,
) -> dict:
    start = text.index(value)
    return proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=operation_type,
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        source_spans=[
            proposal_v2.create_source_span_v2(
                text, start_offset=start, end_offset=start + len(value)
            )
        ],
        target_slot_id=target_slot_id,
        evidence_reference_ids=evidence_reference_ids,
        depends_on_slot_ids=depends_on_slot_ids,
    )


def _candidate_set(
    state: dict,
    text: str,
    operations: list[dict],
    *,
    evidence_references: list[dict] | None = None,
) -> dict:
    binding = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=text,
    )
    proposal = proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=PARSER,
        interpreter_class=proposal_v2.DETERMINISTIC_PARSER,
        interpreter_version="1.0.0",
        conversation_identity=state["envelope"]["conversation_identity"],
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        source_turn_identity=binding["source_turn_identity"],
        source_turn_digest=binding["source_turn_digest"],
        expected_cwm_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        proposed_semantic_operations=operations,
        evidence_references=evidence_references,
    )
    result = proposal_v2.validate_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=COMMITTED,
        interpreter_registry=[
            {
                "interpreter_identity": PARSER,
                "interpreter_class": proposal_v2.DETERMINISTIC_PARSER,
                "interpreter_version": "1.0.0",
                "enabled": True,
            }
        ],
    )
    assert result["validation_disposition"] == proposal_v2.ADMISSIBLE
    return result["candidate_operation_set"]


def _commit(tmp_path: Path, candidate_set: dict, expected_revision: int = 0) -> dict:
    return commit_v2.commit_proposal_candidate_operations_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        candidate_operation_set=candidate_set,
        expected_revision=expected_revision,
        committed_at=COMMITTED,
    )


def test_successful_proposal_commit_is_one_atomic_semantic_revision(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "implement proposal commit runtime"
    candidate_set = _candidate_set(
        state,
        text,
        [_operation(state, text, value="implement")],
    )

    result = _commit(tmp_path, candidate_set)
    persisted = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=COMMITTED,
    )

    assert result["disposition"] == commit_v2.COMMITTED
    assert result["state_changed"] is True
    assert result["semantic_cwm_mutated"] is True
    assert result["objective_created"] is False
    assert result["execution_invoked"] is False
    assert persisted == result["state"]
    assert persisted["revision"] == 1
    assert persisted["envelope_revision"] == 1
    assert persisted["semantic_revision"] == 1
    assert len(persisted["semantic_memory"]["semantic_slots"]) == 1
    assert cwm_v2.validate_conversation_working_memory_state_v2(persisted) == persisted


def test_repeated_commit_is_idempotent_without_revision_advance(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    candidate_set = _candidate_set(
        state, text, [_operation(state, text, value="implement")]
    )
    first = _commit(tmp_path, candidate_set)

    repeated = _commit(tmp_path, candidate_set)

    assert repeated["disposition"] == commit_v2.ALREADY_COMMITTED
    assert repeated["state_changed"] is False
    assert repeated["semantic_cwm_mutated"] is False
    assert repeated["commit_identity"] == first["commit_identity"]
    assert repeated["state"]["revision"] == 1
    assert repeated["replacement_state"] is None


def test_proposal_origin_is_durable_canonical_slot_provenance(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    candidate_set = _candidate_set(
        state, text, [_operation(state, text, value="implement")]
    )

    result = _commit(tmp_path, candidate_set)
    provenance = result["state"]["semantic_memory"]["semantic_slots"][0][
        "provenance"
    ][0]

    assert provenance["source_revision"] == 0
    assert provenance["source_span"] == "implement"
    assert commit_v2.PROPOSAL_COMMIT_RULESET_V1 in provenance[
        "normalization_rule_ids"
    ]
    assert (
        "candidate-set:" + candidate_set["candidate_operation_set_id"]
        in provenance["normalization_rule_ids"]
    )
    assert "proposal:" + candidate_set["proposal_id"] in provenance[
        "normalization_rule_ids"
    ]


def test_conflict_rolls_back_entire_batch(tmp_path: Path) -> None:
    conversation = cwm_v2.conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )
    active = _human_slot(conversation, "preserve")
    state = _state(tmp_path, semantic_slots=[active])
    original = deepcopy(state)
    text = "change runtime"
    operations = [
        _operation(
            state,
            text,
            value="change",
            operation_type=proposal_v2.PROPOSE_SLOT_REVISION,
            target_slot_id=active["slot_id"],
        ),
        _operation(
            state,
            text,
            value="runtime",
            slot_class=cwm_v2.OPERATIVE_SUBJECT,
        ),
    ]
    candidate_set = _candidate_set(state, text, operations)

    with pytest.raises(commit_v2.ProposalCommitError) as raised:
        _commit(tmp_path, candidate_set)

    persisted = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=COMMITTED,
    )
    assert raised.value.reason_code == "SEMANTIC_CONFLICT"
    assert persisted == original


def test_stale_revision_rejects_without_mutation(tmp_path: Path) -> None:
    state = _state(tmp_path)
    first_text = "implement"
    stale_text = "runtime"
    first = _candidate_set(
        state, first_text, [_operation(state, first_text, value="implement")]
    )
    stale = _candidate_set(
        state,
        stale_text,
        [
            _operation(
                state,
                stale_text,
                value="runtime",
                slot_class=cwm_v2.OPERATIVE_SUBJECT,
            )
        ],
    )
    committed = _commit(tmp_path, first)["state"]

    with pytest.raises(commit_v2.ProposalCommitError) as raised:
        _commit(tmp_path, stale)

    persisted = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=COMMITTED,
    )
    assert raised.value.reason_code == "STALE_COMMIT_REVISION"
    assert persisted == committed


def test_candidate_integrity_is_reverified_before_commit(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    candidate_set = _candidate_set(
        state, text, [_operation(state, text, value="implement")]
    )
    candidate_set["integrity_checksum"] = "sha256:" + "0" * 64

    with pytest.raises(commit_v2.ProposalCommitError) as raised:
        _commit(tmp_path, candidate_set)

    assert raised.value.reason_code == "CANDIDATE_SET_INVALID"
    assert cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=COMMITTED,
    )["revision"] == 0


def test_application_order_and_receipt_are_deterministic(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement runtime"
    operations = [
        _operation(
            state,
            text,
            value="runtime",
            slot_class=cwm_v2.OPERATIVE_SUBJECT,
        ),
        _operation(state, text, value="implement"),
    ]
    candidate_set = _candidate_set(state, text, operations)

    first = commit_v2.prepare_proposal_commit_v2(
        state,
        candidate_operation_set=candidate_set,
        expected_revision=0,
        committed_at=COMMITTED,
    )
    second = commit_v2.prepare_proposal_commit_v2(
        state,
        candidate_operation_set=candidate_set,
        expected_revision=0,
        committed_at=COMMITTED,
    )

    assert first == second
    assert first["disposition"] == commit_v2.PREPARED
    assert first["state_changed"] is False
    assert first["replacement_prepared"] is True
    assert first["application_order"] == sorted(first["application_order"])
    assert first["state"]["revision"] == 1
    assert first["state"]["semantic_revision"] == 1
    assert len(first["state"]["semantic_memory"]["semantic_slots"]) == 2


def test_reference_attachment_commits_as_dependent_reference(tmp_path: Path) -> None:
    conversation = cwm_v2.conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )
    active = _human_slot(conversation, "implement")
    state = _state(tmp_path, semantic_slots=[active])
    text = "spec.md"
    reference = proposal_v2.create_evidence_reference_v2(
        reference_kind="EXTERNAL_EVIDENCE",
        reference_digest=cwm_v2._checksum(text),
        verification_status="UNVERIFIED",
    )
    operation = _operation(
        state,
        text,
        value=text,
        operation_type=proposal_v2.PROPOSE_REFERENCE_ATTACHMENT,
        slot_class=cwm_v2.SEMANTIC_REFERENCE,
        slot_role=cwm_v2.EVIDENCE,
        cardinality_key="spec-primary",
        target_slot_id=active["slot_id"],
        evidence_reference_ids=[reference["reference_id"]],
    )
    candidate_set = _candidate_set(
        state, text, [operation], evidence_references=[reference]
    )

    result = _commit(tmp_path, candidate_set)
    reference_slot = next(
        slot
        for slot in result["state"]["semantic_memory"]["semantic_slots"]
        if slot["slot_class"] == cwm_v2.SEMANTIC_REFERENCE
    )

    assert reference_slot["depends_on"] == [active["slot_id"]]
    assert reference_slot["materiality"] == cwm_v2.CONDITIONAL
    assert result["state"]["semantic_revision"] == 1


def test_commit_refreshes_protocol_without_objective_commitment(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    candidate_set = _candidate_set(
        state, text, [_operation(state, text, value="implement")]
    )

    result = _commit(tmp_path, candidate_set)
    committed_state = result["state"]

    assert machine_v2.validate_conversation_state_machine_state_v2(
        committed_state
    ) == committed_state
    assert committed_state["envelope"]["conversation_phase"] == cwm_v2.CLARIFYING
    assert result["conversation_protocol_reduced"] is True
    assert result["objective_commitment_invoked"] is False
    assert result["platform_core_invoked"] is False


def test_public_candidate_validator_remains_non_authoritative(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    candidate_set = _candidate_set(
        state, text, [_operation(state, text, value="implement")]
    )
    original = deepcopy(candidate_set)

    validated = proposal_v2.validate_candidate_operation_set_v2(candidate_set)

    assert validated == original
    assert validated["semantic_cwm_mutated"] is False
    assert state["revision"] == 0


def test_commit_runtime_has_no_execution_pipeline_or_provider_imports() -> None:
    source = inspect.getsource(commit_v2)
    tree = ast.parse(source)
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert not any(
        forbidden in module.lower()
        for module in imported
        for forbidden in (
            "objective",
            "replay",
            "authorization",
            "worker",
            "development_governance",
            "pcbv31",
            "provider",
            "openai",
            "anthropic",
            "aicli",
        )
    )
    assert "requests" not in source
    assert "urllib" not in source
    assert '"objective_created": True' not in source
    assert '"execution_invoked": True' not in source
