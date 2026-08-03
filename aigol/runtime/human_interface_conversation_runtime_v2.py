"""Isolated Human Interface Runtime boundary for Conversation Layer V2.

This module owns transport orchestration only.  It admits explicit, closed-form
human semantic turns through the certified G59 proposal, commit, state-machine,
readiness, and Objective Commitment runtimes.  The terminal condition is the
immutable Objective Commitment record.  No execution-pipeline service is
imported or invoked here.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_proposal_commit_runtime_v2 as proposal_commit_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_objective_commitment_runtime_v2 as commitment_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2 = (
    "HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2"
)
HIR_CONVERSATION_LAYER_INTEGRATION_RULESET_V1 = (
    "HIR_CONVERSATION_LAYER_INTEGRATION_RULESET_V1"
)
DETERMINISTIC_HIR_PARSER_IDENTITY = "hir-deterministic-semantic-command-parser-v1"
DETERMINISTIC_HIR_PARSER_VERSION = "1.0.0"
OBJECTIVE_COMMITMENT_CREATED = "OBJECTIVE_COMMITMENT_CREATED"
SESSION_ACTIVE = "SESSION_ACTIVE"
SESSION_STOPPED_AT_COMMITMENT = "SESSION_STOPPED_AT_OBJECTIVE_COMMITMENT"
SEMANTIC_TURN = "SEMANTIC_TURN"
CANDIDATE_CONFIRMATION = "CANDIDATE_CONFIRMATION"
OBJECTIVE_COMMITMENT = "OBJECTIVE_COMMITMENT"
NON_PROTOCOL_TURN = "NON_PROTOCOL_TURN"

_SEMANTIC_COMMANDS = {
    "action": (cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY, cwm_v2.PRIMARY),
    "subject": (cwm_v2.OPERATIVE_SUBJECT, cwm_v2.PRIMARY, cwm_v2.PRIMARY),
    "outcome": (cwm_v2.DESIRED_OUTCOME, cwm_v2.PRIMARY, cwm_v2.PRIMARY),
    "work-type": (cwm_v2.WORK_TYPE, None, cwm_v2.PRIMARY),
}
_REQUIRED_ORDER = (
    cwm_v2.OPERATIVE_ACTION,
    cwm_v2.OPERATIVE_SUBJECT,
    cwm_v2.DESIRED_OUTCOME,
    cwm_v2.WORK_TYPE,
)


def create_hir_conversation_session_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    human_identity: str,
    created_at: str,
    ttl_seconds: int = 3600,
    interface_identity: str = "AiCLI",
) -> dict[str, Any]:
    """Create one native Conversation V2 episode for a declared HIR transport."""

    human = _text(human_identity, "human_identity")
    participants = sorted([
        _participant(cwm_v2.HUMAN_ORIGINATOR, human, cwm_v2.LOCAL_ASSERTION),
        _participant(
            cwm_v2.INTERFACE_TRANSPORT,
            _text(interface_identity, "interface_identity"),
            cwm_v2.RUNTIME_DECLARATION,
        ),
        _participant(
            cwm_v2.CONVERSATION_OWNER_RUNTIME,
            HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
            cwm_v2.RUNTIME_DECLARATION,
        ),
    ], key=lambda item: (item["participant_role"], item["asserted_identity"]))
    state = cwm_v2.create_conversation_working_memory_state_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace_identity,
        session_identity=session_identity,
        created_at=created_at,
        ttl_seconds=ttl_seconds,
        origin_interface_identity=cwm_v2.LOCAL_CONVERSATION_V2,
        participants=participants,
    )
    return {
        "integration_runtime_version": HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
        "integration_ruleset_version": HIR_CONVERSATION_LAYER_INTEGRATION_RULESET_V1,
        "session_status": SESSION_ACTIVE,
        "state": state,
        **_boundary_flags(),
    }


def admit_hir_semantic_turn_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    source_turn_text: str,
    observed_at: str,
) -> dict[str, Any]:
    """Parse, validate, commit, and bind one explicit human semantic turn."""

    state = _load_state(
        runtime_root, workspace_identity, session_identity, observed_at
    )
    key, value = _parse_semantic_turn(source_turn_text)
    slot_class, configured_role, configured_key = _SEMANTIC_COMMANDS[key]
    _require_next_slot_class(state, slot_class)
    slot_role = configured_role or value.upper()
    cardinality_key = configured_key or slot_role
    canonical_value = value.upper() if slot_class == cwm_v2.WORK_TYPE else value
    if slot_class == cwm_v2.WORK_TYPE and canonical_value not in (
        cwm_v2.CANONICAL_GOVERNED_WORK_TYPES
    ):
        raise FailClosedRuntimeError("work-type is not a canonical governed work type")
    dependencies = _dependencies(state, slot_class)
    operation = proposal_v2.create_proposed_semantic_operation_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        operation_type=proposal_v2.PROPOSE_SLOT_CREATION,
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=canonical_value,
        source_spans=[
            proposal_v2.create_source_span_v2(
                source_turn_text,
                start_offset=source_turn_text.index(value),
                end_offset=source_turn_text.index(value) + len(value),
            )
        ],
        depends_on_slot_ids=dependencies,
    )
    turn_binding = proposal_v2.create_source_turn_binding_v2(
        conversation_identity=state["envelope"]["conversation_identity"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        expected_cwm_revision=state["revision"],
        source_turn_text=source_turn_text,
    )
    proposal = proposal_v2.create_conversation_interpreter_proposal_v2(
        interpreter_identity=DETERMINISTIC_HIR_PARSER_IDENTITY,
        interpreter_class=proposal_v2.DETERMINISTIC_PARSER,
        interpreter_version=DETERMINISTIC_HIR_PARSER_VERSION,
        conversation_identity=state["envelope"]["conversation_identity"],
        workspace_identity_hash=state["envelope"]["workspace_identity_hash"],
        session_identity_hash=state["envelope"]["session_identity_hash"],
        source_turn_identity=turn_binding["source_turn_identity"],
        source_turn_digest=turn_binding["source_turn_digest"],
        expected_cwm_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        proposed_semantic_operations=[operation],
    )
    validation = proposal_v2.validate_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=source_turn_text,
        observed_at=observed_at,
        interpreter_registry=[
            {
                "interpreter_identity": DETERMINISTIC_HIR_PARSER_IDENTITY,
                "interpreter_class": proposal_v2.DETERMINISTIC_PARSER,
                "interpreter_version": DETERMINISTIC_HIR_PARSER_VERSION,
                "enabled": True,
            }
        ],
    )
    if validation["validation_disposition"] != proposal_v2.ADMISSIBLE:
        raise FailClosedRuntimeError("semantic proposal is not admissible")
    proposal_commit = proposal_commit_v2.commit_proposal_candidate_operations_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace_identity,
        session_identity=session_identity,
        candidate_operation_set=validation["candidate_operation_set"],
        expected_revision=state["revision"],
        committed_at=observed_at,
    )
    proposed_state = proposal_commit["state"]
    proposed_slot = next(
        slot
        for slot in proposed_state["semantic_memory"]["semantic_slots"]
        if slot["slot_id"] == operation["proposed_slot_id"]
    )
    asserted_slot = slots_v2.create_semantic_slot_v2(
        conversation_identity=proposed_state["envelope"]["conversation_identity"],
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=canonical_value,
        status=cwm_v2.ASSERTED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.HUMAN_ASSERTED,
        materiality=cwm_v2.REQUIRED,
        provenance=[
            {
                "source_kind": cwm_v2.HUMAN_TURN,
                "turn_number": proposed_state["revision"],
                "source_revision": state["revision"],
                "source_span": value,
                "content_digest": cwm_v2._checksum(value),
                "normalization_rule_ids": sorted([
                    HIR_CONVERSATION_LAYER_INTEGRATION_RULESET_V1,
                    "proposal:" + validation["proposal_id"],
                    "proposal-commit:" + proposal_commit["commit_identity"],
                ]),
                "human_disposition": "ASSERTED",
            }
        ],
        depends_on=dependencies,
        created_at=observed_at,
    )
    if proposed_slot["slot_id"] != asserted_slot["slot_id"]:
        raise FailClosedRuntimeError("asserted slot identity differs from proposal")
    prepared = machine_v2.prepare_conversation_correction_v2(
        proposed_state,
        expected_revision=proposed_state["revision"],
        incoming_slot=asserted_slot,
        observed_at=observed_at,
    )
    replacement = prepared["replacement_state"]
    if replacement is None:
        raise FailClosedRuntimeError("human semantic admission produced no state change")
    persisted = machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(runtime_root),
        workspace_identity=str(workspace_identity),
        session_identity=session_identity,
        expected_revision=proposed_state["revision"],
        replacement_state=replacement,
        observed_at=observed_at,
    )
    protocol_state = machine_v2.derive_conversation_protocol_state_v2(
        persisted, observed_at=observed_at
    )
    result = {
        "integration_runtime_version": HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
        "turn_disposition": "SEMANTIC_TURN_ADMITTED",
        "slot_class": slot_class,
        "slot_id": asserted_slot["slot_id"],
        "canonical_value": canonical_value,
        "proposal_validation_disposition": validation["validation_disposition"],
        "proposal_id": validation["proposal_id"],
        "proposal_commit_disposition": proposal_commit["disposition"],
        "proposal_commit_identity": proposal_commit["commit_identity"],
        "source_turn_binding": deepcopy(turn_binding),
        "interpreter_proposal": deepcopy(proposal),
        "proposal_validation": deepcopy(validation),
        "proposal_commit": deepcopy(proposal_commit),
        "protocol_state": protocol_state,
        "state": persisted,
        **_boundary_flags(),
    }
    if protocol_state == machine_v2.CANDIDATE_REVIEW:
        result["candidate_review"] = machine_v2.candidate_review_presentation_v2(
            persisted
        )
    return result


def classify_hir_conversation_turn_v2(source_turn_text: str) -> str:
    """Classify only the existing closed G60 control grammar."""

    text = _text(source_turn_text, "source_turn_text")
    if text.startswith("/confirm "):
        return CANDIDATE_CONFIRMATION
    if text.startswith("/commit "):
        return OBJECTIVE_COMMITMENT
    prefix = text.split(":", 1)[0].strip().lower() if ":" in text else None
    if prefix in _SEMANTIC_COMMANDS:
        return SEMANTIC_TURN
    return NON_PROTOCOL_TURN


def confirm_hir_candidate_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    explicit_confirmation_action: str,
    observed_at: str,
) -> dict[str, Any]:
    """Record exact candidate confirmation and evaluate Objective readiness."""

    state = _load_state(
        runtime_root, workspace_identity, session_identity, observed_at
    )
    request = machine_v2.create_candidate_confirmation_request_v2(state)
    expected_action = f"/confirm {request['candidate_digest']}"
    if explicit_confirmation_action.strip() != expected_action:
        raise FailClosedRuntimeError("exact /confirm candidate digest is required")
    prepared = machine_v2.prepare_candidate_confirmation_v2(
        state,
        expected_revision=state["revision"],
        confirmation_request=request,
        observed_at=observed_at,
    )
    replacement = prepared["replacement_state"]
    if replacement is None:
        raise FailClosedRuntimeError("candidate confirmation produced no state change")
    persisted = machine_v2.persist_conversation_state_machine_transition_v2(
        runtime_root=str(runtime_root),
        workspace_identity=str(workspace_identity),
        session_identity=session_identity,
        expected_revision=state["revision"],
        replacement_state=replacement,
        observed_at=observed_at,
    )
    report = readiness_v2.require_objective_readiness_v2(
        persisted,
        expected_revision=persisted["revision"],
        expected_semantic_revision=persisted["semantic_revision"],
        observed_at=persisted["envelope"]["updated_at"],
    )
    snapshot = commitment_v2.build_candidate_objective_snapshot_v2(
        persisted, readiness_report=report
    )
    objective_digest = commitment_v2.compute_candidate_objective_digest_v2(snapshot)
    return {
        "integration_runtime_version": HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
        "confirmation_disposition": machine_v2.CONFIRMATION_RECORDED,
        "protocol_state": machine_v2.OBJECTIVE_READY,
        "readiness_report": report,
        "objective_candidate_digest": objective_digest,
        "expected_commit_action": f"/commit {objective_digest}",
        "state": persisted,
        **_boundary_flags(),
    }


def create_hir_objective_commitment_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    explicit_commit_action: str,
    observed_at: str,
) -> dict[str, Any]:
    """Prepare the request, create its immutable record, and stop the session."""

    state = _load_state(
        runtime_root, workspace_identity, session_identity, observed_at
    )
    report = readiness_v2.require_objective_readiness_v2(
        state,
        expected_revision=state["revision"],
        expected_semantic_revision=state["semantic_revision"],
        observed_at=state["envelope"]["updated_at"],
    )
    human = next(
        participant
        for participant in state["envelope"]["participants"]
        if participant["participant_role"] == cwm_v2.HUMAN_ORIGINATOR
    )
    request = commitment_v2.create_objective_commitment_request_v2(
        state,
        readiness_report=report,
        explicit_commit_action=explicit_commit_action,
        human_participant_digest=cwm_v2._checksum(human),
        requested_at=report["evaluated_at"],
    )
    committed = commitment_v2.commit_objective_snapshot_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace_identity,
        session_identity=session_identity,
        commitment_request=request,
    )
    return {
        "integration_runtime_version": HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
        "session_status": SESSION_STOPPED_AT_COMMITMENT,
        "terminal_condition": OBJECTIVE_COMMITMENT_CREATED,
        "commitment_request_prepared": True,
        "commitment_record_created": committed["commitment_record_created"],
        "commitment_disposition": committed["disposition"],
        "commitment_identity": request["commitment_identity"],
        "candidate_objective_digest": request["candidate_objective_digest"],
        "commitment_request": request,
        "commitment_record": committed["commitment_record"],
        **_boundary_flags(),
    }


def run_hir_conversation_terminal_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    human_identity: str,
    created_at: str,
    ttl_seconds: int = 3600,
    input_reader: Callable[[str], str] = input,
    output_writer: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Run the explicit multi-turn AiCLI/HIR Conversation V2 protocol."""

    started = create_hir_conversation_session_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace_identity,
        session_identity=session_identity,
        human_identity=human_identity,
        created_at=created_at,
        ttl_seconds=ttl_seconds,
    )
    output_writer("AiCLI/HIR Conversation Layer V2 session started")
    output_writer("route: Human -> AiCLI -> HIR -> Conversation Layer V2")
    output_writer("execution_pipeline_entered: false")
    output_writer("Enter action:, subject:, outcome:, and work-type: turns in order.")
    turn_index = 0
    last_result: dict[str, Any] = started
    while True:
        try:
            line = input_reader("aicli-v2> ")
        except (EOFError, StopIteration):
            return {
                "integration_runtime_version": HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2,
                "session_status": SESSION_ACTIVE,
                "terminal_condition": "EOF_BEFORE_OBJECTIVE_COMMITMENT",
                "last_result": last_result,
                **_boundary_flags(),
            }
        text = str(line).strip()
        if not text:
            continue
        turn_index += 1
        observed_at = _turn_time(created_at, turn_index)
        if text.startswith("/confirm "):
            last_result = confirm_hir_candidate_v2(
                runtime_root=runtime_root,
                workspace_identity=workspace_identity,
                session_identity=session_identity,
                explicit_confirmation_action=text,
                observed_at=observed_at,
            )
            output_writer("candidate_confirmation: CONFIRMATION_RECORDED")
            output_writer("objective_readiness: READY")
            output_writer(
                "objective_candidate_digest: "
                + last_result["objective_candidate_digest"]
            )
            output_writer("next: " + last_result["expected_commit_action"])
            continue
        if text.startswith("/commit "):
            last_result = create_hir_objective_commitment_v2(
                runtime_root=runtime_root,
                workspace_identity=workspace_identity,
                session_identity=session_identity,
                explicit_commit_action=text,
                observed_at=observed_at,
            )
            output_writer("objective_commitment: " + last_result["commitment_disposition"])
            output_writer("commitment_identity: " + last_result["commitment_identity"])
            output_writer("commitment_record_created: true")
            output_writer("platform_core_admission_reached: false")
            output_writer("execution_pipeline_entered: false")
            output_writer("session_stopped: OBJECTIVE_COMMITMENT_CREATED")
            return last_result
        last_result = admit_hir_semantic_turn_v2(
            runtime_root=runtime_root,
            workspace_identity=workspace_identity,
            session_identity=session_identity,
            source_turn_text=text,
            observed_at=observed_at,
        )
        output_writer(
            f"semantic_turn: {last_result['slot_class']}={last_result['canonical_value']}"
        )
        output_writer(
            "proposal_validation: "
            + last_result["proposal_validation_disposition"]
        )
        output_writer("proposal_commit: " + last_result["proposal_commit_disposition"])
        output_writer(
            f"conversation_state: {last_result['protocol_state']} "
            f"revision={last_result['state']['revision']}"
        )
        review = last_result.get("candidate_review")
        if isinstance(review, dict):
            digest = review["presentation"]["candidate_digest"]
            output_writer("candidate_digest: " + digest)
            output_writer("next: /confirm " + digest)


def _load_state(
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    state = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=runtime_root,
        workspace_identity=workspace_identity,
        session_identity=session_identity,
        observed_at=observed_at,
    )
    if state is None:
        raise FailClosedRuntimeError("Conversation V2 session is absent")
    return machine_v2.validate_conversation_state_machine_state_v2(state)


def _parse_semantic_turn(source_turn_text: str) -> tuple[str, str]:
    text = _text(source_turn_text, "source_turn_text")
    if ":" not in text:
        raise FailClosedRuntimeError("semantic turn requires one named field")
    key, value = text.split(":", 1)
    key = key.strip().lower()
    value = " ".join(value.strip().split())
    if key not in _SEMANTIC_COMMANDS or not value:
        raise FailClosedRuntimeError("semantic turn field or value is invalid")
    return key, value


def hir_semantic_turn_matches_next_required_v2(
    state: dict[str, Any], source_turn_text: str
) -> bool:
    """Return whether one existing typed command addresses the next G59 slot."""

    current = machine_v2.validate_conversation_state_machine_state_v2(state)
    key, _value = _parse_semantic_turn(source_turn_text)
    slot_class = _SEMANTIC_COMMANDS[key][0]
    return slot_class == _next_required_slot_class(current)


def _require_next_slot_class(state: dict[str, Any], slot_class: str) -> None:
    expected = _next_required_slot_class(state)
    if expected is None:
        raise FailClosedRuntimeError("required semantic slots are already complete")
    if slot_class != expected:
        raise FailClosedRuntimeError(f"next required semantic field is {expected}")


def _next_required_slot_class(state: dict[str, Any]) -> str | None:
    present = {
        slot["slot_class"]
        for slot in state["semantic_memory"]["semantic_slots"]
        if slot["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}
    }
    return next((item for item in _REQUIRED_ORDER if item not in present), None)


def _dependencies(state: dict[str, Any], slot_class: str) -> list[str]:
    by_class = {
        slot["slot_class"]: slot["slot_id"]
        for slot in state["semantic_memory"]["semantic_slots"]
    }
    if slot_class == cwm_v2.OPERATIVE_ACTION:
        return []
    if slot_class in {cwm_v2.OPERATIVE_SUBJECT, cwm_v2.WORK_TYPE}:
        return [by_class[cwm_v2.OPERATIVE_ACTION]]
    if slot_class == cwm_v2.DESIRED_OUTCOME:
        return sorted(
            [
                by_class[cwm_v2.OPERATIVE_ACTION],
                by_class[cwm_v2.OPERATIVE_SUBJECT],
            ]
        )
    raise FailClosedRuntimeError("unsupported required slot dependency")


def _participant(role: str, identity: str, source: str) -> dict[str, Any]:
    return {
        "participant_role": role,
        "asserted_identity": identity,
        "identity_source": source,
        "binding_disposition": cwm_v2.ASSERTED_NOT_AUTHENTICATED,
        "first_bound_revision": 0,
        "last_confirmed_revision": 0,
    }


def _turn_time(created_at: str, turn_index: int) -> str:
    canonical = cwm_v2._canonical_timestamp(created_at, "created_at")
    parsed = datetime.fromisoformat(canonical.replace("Z", "+00:00"))
    value = parsed + timedelta(seconds=turn_index)
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _boundary_flags() -> dict[str, bool]:
    return {
        "constitutional_authority": False,
        "objective_created": False,
        "platform_core_admission_reached": False,
        "development_governance_reached": False,
        "capability_selection_reached": False,
        "authorization_reached": False,
        "worker_reached": False,
        "replay_execution_reached": False,
        "execution_pipeline_entered": False,
        "external_llm_invoked": False,
    }


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{name} is required")
    return value.strip()


__all__ = [
    "CANDIDATE_CONFIRMATION",
    "HIR_CONVERSATION_LAYER_INTEGRATION_RUNTIME_V2",
    "NON_PROTOCOL_TURN",
    "OBJECTIVE_COMMITMENT",
    "OBJECTIVE_COMMITMENT_CREATED",
    "SEMANTIC_TURN",
    "SESSION_STOPPED_AT_COMMITMENT",
    "admit_hir_semantic_turn_v2",
    "classify_hir_conversation_turn_v2",
    "confirm_hir_candidate_v2",
    "create_hir_conversation_session_v2",
    "create_hir_objective_commitment_v2",
    "hir_semantic_turn_matches_next_required_v2",
    "run_hir_conversation_terminal_v2",
]
