from __future__ import annotations

from copy import deepcopy
import ast
import hashlib
import inspect
from pathlib import Path

import pytest

from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-04-INTERPRETER-PROPOSAL"
CREATED = "2026-07-31T15:00:00Z"
OBSERVED = "2026-07-31T15:01:00Z"
PARSER = "conversation-deterministic-parser-v1"
EXTERNAL = "conversation-external-language-model-v1"


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


def _state(tmp_path: Path) -> dict:
    return cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=3600,
        participants=_participants(),
    )


def _registry(*entries: tuple[str, str]) -> list[dict]:
    return [
        {
            "interpreter_identity": identity,
            "interpreter_class": interpreter_class,
            "interpreter_version": "1.0.0",
            "enabled": True,
        }
        for identity, interpreter_class in entries
    ]


def _source_binding(state: dict, text: str, *, revision: int | None = None) -> dict:
    return proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=(state["revision"] if revision is None else revision),
        source_turn_text=text,
    )


def _operation(
    state: dict,
    text: str,
    *,
    value: str = "implement",
    operation_type: str = proposal_v2.PROPOSE_SLOT_CREATION,
    slot_class: str = cwm_v2.OPERATIVE_ACTION,
    slot_role: str = cwm_v2.PRIMARY,
    cardinality_key: str = cwm_v2.PRIMARY,
    target_slot_id: str | None = None,
    evidence_reference_ids: list[str] | None = None,
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
    )


def _proposal(
    state: dict,
    text: str,
    operations: list[dict],
    *,
    interpreter_identity: str = PARSER,
    interpreter_class: str = proposal_v2.DETERMINISTIC_PARSER,
    expected_revision: int | None = None,
    workspace_identity_hash: str | None = None,
    session_identity_hash: str | None = None,
    conversation_identity: str | None = None,
    advisory_confidence: dict | None = None,
    ambiguity_declaration: dict | None = None,
    conflict_declaration: dict | None = None,
    evidence_references: list[dict] | None = None,
) -> dict:
    revision = state["revision"] if expected_revision is None else expected_revision
    binding = _source_binding(state, text, revision=revision)
    return proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=interpreter_identity,
        interpreter_class=interpreter_class,
        interpreter_version="1.0.0",
        conversation_identity=(
            state["envelope"]["conversation_identity"]
            if conversation_identity is None
            else conversation_identity
        ),
        workspace_identity_hash=(
            state["envelope"]["workspace_identity_hash"]
            if workspace_identity_hash is None
            else workspace_identity_hash
        ),
        session_identity_hash=(
            state["envelope"]["session_identity_hash"]
            if session_identity_hash is None
            else session_identity_hash
        ),
        source_turn_identity=binding["source_turn_identity"],
        source_turn_digest=binding["source_turn_digest"],
        expected_cwm_revision=revision,
        expected_semantic_revision=state["semantic_revision"],
        proposed_semantic_operations=operations,
        evidence_references=evidence_references,
        advisory_confidence=advisory_confidence,
        ambiguity_declaration=ambiguity_declaration,
        conflict_declaration=conflict_declaration,
    )


def _validate(
    proposal: dict,
    state: dict,
    text: str,
    registry: list[dict] | None = None,
) -> dict:
    return proposal_v2.validate_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=(
            registry
            if registry is not None
            else _registry((PARSER, proposal_v2.DETERMINISTIC_PARSER))
        ),
    )


def _state_with_action(tmp_path: Path) -> tuple[dict, dict]:
    state = _state(tmp_path)
    conversation = state["envelope"]["conversation_identity"]
    slot = slots_v2.create_semantic_slot_v2(
        conversation_identity=conversation,
        slot_class=cwm_v2.OPERATIVE_ACTION,
        slot_role=cwm_v2.PRIMARY,
        cardinality_key=cwm_v2.PRIMARY,
        surface_value="implement",
        canonical_value="implement",
        status=cwm_v2.ASSERTED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.HUMAN_ASSERTED,
        materiality=cwm_v2.REQUIRED,
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": 1,
                "source_revision": 1,
                "source_span": "implement",
                "content_digest": cwm_v2._checksum("implement"),
                "normalization_rule_ids": [],
                "human_disposition": "ASSERTED",
            }
        ],
        depends_on=[],
        created_at=OBSERVED,
    )
    replacement = slots_v2.prepare_semantic_slot_state_update_v2(
        state,
        expected_revision=0,
        operation=slots_v2.CREATE,
        incoming_slot=slot,
        observed_at=OBSERVED,
    )["replacement_state"]
    return replacement, slot


def _reason(result: dict) -> str:
    assert result["validation_disposition"] == proposal_v2.REJECTED
    assert result["candidate_operation_set"] is None
    assert result["semantic_cwm_mutated"] is False
    return result["rejection_reasons"][0]


def test_valid_deterministic_parser_proposal_is_candidate_only(tmp_path: Path) -> None:
    state = _state(tmp_path)
    original = deepcopy(state)
    text = "implement interpreter runtime"
    proposal = _proposal(state, text, [_operation(state, text)])

    result = _validate(proposal, state, text)
    candidate_set = result["candidate_operation_set"]

    assert result["validation_disposition"] == proposal_v2.ADMISSIBLE
    assert candidate_set["reduction_allowed"] is True
    assert candidate_set["semantic_cwm_mutated"] is False
    assert candidate_set["conversation_transition_applied"] is False
    assert candidate_set["objective_created"] is False
    assert candidate_set["execution_invoked"] is False
    assert candidate_set["candidate_operations"][0]["authority_effect"] is False
    assert state == original


def test_external_llm_class_uses_same_boundary_without_provider_execution(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "implement interpreter runtime"
    proposal = _proposal(
        state,
        text,
        [_operation(state, text)],
        interpreter_identity=EXTERNAL,
        interpreter_class=proposal_v2.EXTERNAL_LANGUAGE_MODEL,
    )

    result = _validate(
        proposal,
        state,
        text,
        _registry((EXTERNAL, proposal_v2.EXTERNAL_LANGUAGE_MODEL)),
    )

    assert result["validation_disposition"] == proposal_v2.ADMISSIBLE
    assert result["execution_invoked"] is False
    assert result["candidate_operation_set"]["interpreter_class"] == (
        proposal_v2.EXTERNAL_LANGUAGE_MODEL
    )


def test_identical_input_validation_is_byte_deterministic(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement interpreter runtime"
    proposal = _proposal(state, text, [_operation(state, text)])

    first = _validate(proposal, state, text)
    second = _validate(deepcopy(proposal), deepcopy(state), text)

    assert first == second
    assert cwm_v2._canonical_bytes(first) == cwm_v2._canonical_bytes(second)


def test_unknown_proposal_version_rejects_before_acceptance(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    proposal["proposal_version"] = "V99"

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "UNKNOWN_PROPOSAL_VERSION"


def test_unknown_interpreter_identity_rejects(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=[],
    )

    assert _reason(result) == "UNKNOWN_INTERPRETER_IDENTITY"


def test_stale_revision_rejects_without_rebase(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(
        state, text, [_operation(state, text)], expected_revision=1
    )

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "STALE_CWM_REVISION"


@pytest.mark.parametrize(
    "override",
    (
        {"conversation_identity": "conversation-local-sha256:" + "a" * 64},
        {"workspace_identity_hash": "sha256:" + "b" * 64},
        {"session_identity_hash": "sha256:" + "c" * 64},
    ),
)
def test_wrong_conversation_workspace_or_session_rejects(
    tmp_path: Path,
    override: dict,
) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)], **override)

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "CONVERSATION_BINDING_MISMATCH"


def test_unknown_slot_class_and_invalid_slot_identity_reject(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    span = proposal_v2.create_source_span_v2(text, start_offset=0, end_offset=9)
    unknown = proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=proposal_v2.PROPOSE_SLOT_CREATION,
        slot_class="SEVENTH_SLOT_CLASS",
        slot_role=cwm_v2.PRIMARY,
        cardinality_key=cwm_v2.PRIMARY,
        proposed_slot_id="conversation-slot-sha256:" + "d" * 64,
        surface_value="implement",
        canonical_value="implement",
        proposed_equivalence_key="semantic-equivalence-sha256:" + "e" * 64,
        source_spans=[span],
    )
    unknown_result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        _proposal(state, text, [unknown]),
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )
    invalid_identity = _operation(state, text)
    invalid_identity["proposed_slot_id"] = "conversation-slot-sha256:" + "f" * 64
    invalid_identity["operation_id"] = proposal_v2._operation_identity(invalid_identity)
    identity_result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        _proposal(state, text, [invalid_identity]),
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(unknown_result) == "UNKNOWN_SLOT_CLASS"
    assert _reason(identity_result) == "INVALID_SLOT_IDENTITY"


def test_invalid_operation_and_control_operations_reject_deterministically(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "implement"
    reasons = {}
    for operation_type in (
        "UNBOUNDED_OPERATION",
        "CONFIRM_CANDIDATE",
        "OBJECTIVE_COMMITMENT",
    ):
        operation = _operation(state, text, operation_type=operation_type)
        result = proposal_v2.assess_conversation_interpreter_proposal_v2(
            _proposal(state, text, [operation]),
            current_state=state,
            source_turn_text=text,
            observed_at=OBSERVED,
            interpreter_registry=_registry(
                (PARSER, proposal_v2.DETERMINISTIC_PARSER)
            ),
        )
        reasons[operation_type] = _reason(result)

    assert reasons["UNBOUNDED_OPERATION"] == "FORBIDDEN_OPERATION"
    assert reasons["CONFIRM_CANDIDATE"] == "FORBIDDEN_CONTROL_ACT"
    assert reasons["OBJECTIVE_COMMITMENT"] == "FORBIDDEN_CONTROL_ACT"


def test_material_conflict_requires_clarification_without_selection(
    tmp_path: Path,
) -> None:
    state, active = _state_with_action(tmp_path)
    text = "audit"
    operation = _operation(
        state,
        text,
        value="audit",
        operation_type=proposal_v2.PROPOSE_CONFLICT,
        target_slot_id=active["slot_id"],
    )
    proposal = _proposal(
        state,
        text,
        [operation],
        conflict_declaration={
            "declared": True,
            "operation_ids": [operation["operation_id"]],
        },
    )

    result = _validate(proposal, state, text)

    assert result["validation_disposition"] == proposal_v2.CLARIFICATION_REQUIRED
    assert result["candidate_operation_set"]["conflict_operation_ids"] == [
        operation["operation_id"]
    ]
    assert result["candidate_operation_set"]["reduction_allowed"] is False


def test_slot_revision_is_only_a_non_authoritative_candidate(tmp_path: Path) -> None:
    state, active = _state_with_action(tmp_path)
    original = deepcopy(state)
    text = "audit"
    operation = _operation(
        state,
        text,
        value="audit",
        operation_type=proposal_v2.PROPOSE_SLOT_REVISION,
        target_slot_id=active["slot_id"],
    )

    result = _validate(_proposal(state, text, [operation]), state, text)
    candidate = result["candidate_operation_set"]["candidate_operations"][0]

    assert candidate["candidate_operation_type"] == "REVISE_CANDIDATE"
    assert candidate["authority_effect"] is False
    assert result["semantic_cwm_mutated"] is False
    assert state == original


def test_declared_ambiguity_requires_clarification(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    operation = _operation(state, text)
    proposal = _proposal(
        state,
        text,
        [operation],
        ambiguity_declaration={
            "declared": True,
            "operation_ids": [operation["operation_id"]],
        },
    )

    result = _validate(proposal, state, text)

    assert result["validation_disposition"] == proposal_v2.CLARIFICATION_REQUIRED
    assert result["candidate_operation_set"]["reduction_allowed"] is False


def test_explicit_clarification_operation_has_no_semantic_payload(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "what should be changed?"
    operation = proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=proposal_v2.PROPOSE_CLARIFICATION_REQUIREMENT,
        slot_class=cwm_v2.OPERATIVE_ACTION,
        slot_role=cwm_v2.PRIMARY,
        cardinality_key=cwm_v2.PRIMARY,
        surface_value=None,
        canonical_value=None,
        source_spans=[],
        clarification_reason="MISSING",
    )

    result = _validate(_proposal(state, text, [operation]), state, text)
    candidate = result["candidate_operation_set"]["candidate_operations"][0]

    assert result["validation_disposition"] == proposal_v2.CLARIFICATION_REQUIRED
    assert candidate["canonical_value"] is None
    assert candidate["authority_effect"] is False


def test_contradictory_equivalence_and_conflict_operations_reject(
    tmp_path: Path,
) -> None:
    state, active = _state_with_action(tmp_path)
    text = "implement audit"
    equivalent = _operation(
        state,
        text,
        value="implement",
        operation_type=proposal_v2.PROPOSE_SEMANTIC_EQUIVALENCE,
        target_slot_id=active["slot_id"],
    )
    conflict = _operation(
        state,
        text,
        value="audit",
        operation_type=proposal_v2.PROPOSE_CONFLICT,
        target_slot_id=active["slot_id"],
    )
    proposal = _proposal(
        state,
        text,
        [equivalent, conflict],
        conflict_declaration={
            "declared": True,
            "operation_ids": [conflict["operation_id"]],
        },
    )

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "CONTRADICTORY_OPERATIONS"


def test_confidence_is_advisory_and_excluded_from_semantic_reduction(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "implement"
    operation = _operation(state, text)
    low = _proposal(
        state,
        text,
        [operation],
        advisory_confidence={
            "scale_id": "MODEL_SCORE_V1",
            "reported_value": "0.01",
            "limitations": ["NOT_CALIBRATED"],
            "authority_effect": False,
        },
    )
    high = _proposal(
        state,
        text,
        [operation],
        advisory_confidence={
            "scale_id": "MODEL_SCORE_V1",
            "reported_value": "0.99",
            "limitations": ["NOT_CALIBRATED"],
            "authority_effect": False,
        },
    )

    low_set = _validate(low, state, text)["candidate_operation_set"]
    high_set = _validate(high, state, text)["candidate_operation_set"]

    assert low_set["semantic_reduction_digest"] == high_set[
        "semantic_reduction_digest"
    ]
    assert low_set["confidence_authority_effect"] is False
    assert high_set["confidence_authority_effect"] is False


def test_interpreter_majority_cannot_resolve_material_conflict(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement audit"
    entries = [
        ("parser-a", proposal_v2.DETERMINISTIC_PARSER, "implement"),
        ("parser-b", proposal_v2.RULE_BASED_INTERPRETER, "implement"),
        ("model-c", proposal_v2.EXTERNAL_LANGUAGE_MODEL, "audit"),
    ]
    registry = _registry(*[(identity, kind) for identity, kind, _ in entries])
    sets = []
    for identity, kind, value in entries:
        proposal = _proposal(
            state,
            text,
            [_operation(state, text, value=value)],
            interpreter_identity=identity,
            interpreter_class=kind,
        )
        sets.append(_validate(proposal, state, text, registry)["candidate_operation_set"])

    comparison = proposal_v2.compare_validated_candidate_operation_sets_v2(sets)
    reversed_comparison = proposal_v2.compare_validated_candidate_operation_sets_v2(
        list(reversed(sets))
    )

    assert comparison == reversed_comparison
    assert comparison["comparison_disposition"] == proposal_v2.MATERIAL_CONFLICT
    assert comparison["interpreter_count"] == 3
    assert comparison["selected_by_majority"] is False
    assert comparison["majority_authority_effect"] is False
    assert comparison["reduction_allowed"] is False
    assert comparison["clarification_required"] is True


def test_comparison_recomputes_semantic_reduction_digest(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    forged = deepcopy(_validate(proposal, state, text)["candidate_operation_set"])
    forged["semantic_reduction_digest"] = "sha256:" + "0" * 64
    forged["candidate_operation_set_id"] = None
    forged["integrity_checksum"] = None
    identity_body = deepcopy(forged)
    forged["candidate_operation_set_id"] = (
        "candidate-operation-set-local-sha256:"
        + hashlib.sha256(proposal_v2._canonical_bytes(identity_body)).hexdigest()
    )
    integrity_body = deepcopy(forged)
    integrity_body.pop("integrity_checksum")
    forged["integrity_checksum"] = proposal_v2._checksum(integrity_body)

    with pytest.raises(proposal_v2.ProposalValidationError) as raised:
        proposal_v2.compare_validated_candidate_operation_sets_v2([forged])

    assert raised.value.reason_code == "COMPARISON_INPUT_INVALID"


def test_reference_attachment_is_candidate_only(tmp_path: Path) -> None:
    state, active = _state_with_action(tmp_path)
    text = "spec.md"
    reference = proposal_v2.create_evidence_reference_v2(
        reference_kind="EXTERNAL_EVIDENCE",
        reference_digest=cwm_v2._checksum("spec.md"),
        verification_status="UNVERIFIED",
    )
    operation = _operation(
        state,
        text,
        value="spec.md",
        operation_type=proposal_v2.PROPOSE_REFERENCE_ATTACHMENT,
        slot_class=cwm_v2.SEMANTIC_REFERENCE,
        slot_role=cwm_v2.EVIDENCE,
        cardinality_key="spec-primary",
        target_slot_id=active["slot_id"],
        evidence_reference_ids=[reference["reference_id"]],
    )

    result = _validate(
        _proposal(
            state,
            text,
            [operation],
            evidence_references=[reference],
        ),
        state,
        text,
    )

    candidate = result["candidate_operation_set"]["candidate_operations"][0]
    assert candidate["candidate_operation_type"] == "REFERENCE_ATTACHMENT_CANDIDATE"
    assert candidate["authority_effect"] is False


def test_direct_cwm_and_execution_fields_reject_before_schema_coercion(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    text = "implement"
    base = _proposal(state, text, [_operation(state, text)])
    direct_cwm = deepcopy(base)
    direct_cwm["semantic_cwm_mutation"] = {"replace": True}
    direct_cwm = proposal_v2._with_proposal_identity_and_integrity(direct_cwm)
    execution = deepcopy(base)
    execution["execution_request"] = {"run": True}
    execution = proposal_v2._with_proposal_identity_and_integrity(execution)

    for attempted in (direct_cwm, execution):
        result = proposal_v2.assess_conversation_interpreter_proposal_v2(
            attempted,
            current_state=state,
            source_turn_text=text,
            observed_at=OBSERVED,
            interpreter_registry=_registry(
                (PARSER, proposal_v2.DETERMINISTIC_PARSER)
            ),
        )
        assert _reason(result) == "FORBIDDEN_AUTHORITY_FIELD"


def test_authority_flag_tampering_rejects(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    proposal["boundary_flags"]["semantic_cwm_mutation_authority"] = True
    proposal = proposal_v2._with_proposal_identity_and_integrity(proposal)

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "FORBIDDEN_AUTHORITY_FIELD"


def test_tampering_and_missing_source_binding_reject(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    tampered = deepcopy(proposal)
    tampered["interpreter_version"] = "2.0.0"
    tampered_result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        tampered,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )
    missing_source = deepcopy(proposal)
    missing_source["source_turn_digest"] = "sha256:" + "a" * 64
    missing_source = proposal_v2._with_proposal_identity_and_integrity(missing_source)
    source_result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        missing_source,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(tampered_result) == "INVALID_INTEGRITY"
    assert _reason(source_result) == "MISSING_SOURCE_BINDING"


def test_proposal_byte_bound_fails_closed(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    proposal["advisory_confidence"]["reported_value"] = "x" * (
        proposal_v2.MAX_PROPOSAL_BYTES + 1
    )

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert _reason(result) == "PROPOSAL_TOO_LARGE"


def test_compatibility_preserves_g59_state_and_authority_boundaries(
    tmp_path: Path,
) -> None:
    state, _ = _state_with_action(tmp_path)
    original = deepcopy(state)
    text = "implement"
    target = state["semantic_memory"]["semantic_slots"][0]["slot_id"]
    operation = _operation(
        state,
        text,
        operation_type=proposal_v2.PROPOSE_SEMANTIC_EQUIVALENCE,
        target_slot_id=target,
    )

    result = _validate(_proposal(state, text, [operation]), state, text)

    assert result["candidate_operation_set"] is not None
    assert state == original
    for field in (
        "constitutional_authority",
        "replay_visible",
        "authorization_eligible",
        "worker_eligible",
        "objective_creation_supported",
        "capability_routing_supported",
    ):
        assert state[field] is False


def test_runtime_has_no_provider_or_execution_owner_imports() -> None:
    source = inspect.getsource(proposal_v2)
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
    assert "semantic_cwm_mutated\": True" not in source
    assert "execution_invoked\": True" not in source
