"""Deterministic, isolated Conversation Layer V2 state machine.

Protocol state is derived from the atomic G59-01 Conversation Envelope and
Semantic CWM document.  Semantic corrections delegate only to the G59-02
Semantic Slot Runtime.  This module creates no Objective and cannot invoke
Platform Core, AiCLI, Replay, Authorization, Development Governance,
capability selection, Workers, completion, or Providers.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2 = (
    "PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2"
)

ABSENT = "ABSENT"
COLLECTING = cwm_v2.COLLECTING
CLARIFYING = cwm_v2.CLARIFYING
CANDIDATE_REVIEW = cwm_v2.CANDIDATE_REVIEW
OBJECTIVE_READY = "OBJECTIVE_READY"
COMMITMENT_PENDING = cwm_v2.COMMITMENT_PENDING
COMMITMENT_RECOVERY = "COMMITMENT_RECOVERY"
HANDED_OFF = cwm_v2.HANDED_OFF
SUSPENDED = cwm_v2.SUSPENDED
ABANDONED = "ABANDONED"
EXPIRED = "EXPIRED"
FAIL_CLOSED_RECOVERY = "FAIL_CLOSED_RECOVERY"

STATE_UPDATED = "STATE_UPDATED"
NO_CHANGE = "NO_CHANGE"
NO_PROGRESS_RECORDED = "NO_PROGRESS_RECORDED"
SUSPENDED_FAIL_CLOSED = "SUSPENDED_FAIL_CLOSED"
CONFIRMATION_RECORDED = "CONFIRMATION_RECORDED"
RESUMED = "RESUMED"
USER_ABANDONED = "USER_ABANDONED"

MAX_NO_PROGRESS_COUNT = 1

_CONFIRMATION_REQUEST_FIELDS = frozenset(
    {
        "protocol_version",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "global_revision",
        "semantic_revision",
        "normalization_ruleset_version",
        "candidate_digest",
        "presentation_digest",
        "participant_binding_digest",
        "control_act",
    }
)


def derive_conversation_protocol_state_v2(
    state: dict[str, Any] | None,
    *,
    observed_at: str,
) -> str:
    """Derive one canonical reportable state from validated atomic data."""

    if state is None:
        return ABSENT
    candidate = cwm_v2.validate_conversation_working_memory_state_v2(state)
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    if cwm_v2._is_v2_expired(candidate, observed):
        return EXPIRED
    envelope = candidate["envelope"]
    if envelope["availability_state"] == cwm_v2.SUSPENDED:
        return SUSPENDED
    if envelope["availability_state"] == cwm_v2.CLOSED:
        return ABANDONED
    phase = envelope["conversation_phase"]
    if phase == cwm_v2.COMMITMENT_PENDING:
        raise FailClosedRuntimeError("Objective Commitment is not implemented")
    if phase == cwm_v2.HANDED_OFF:
        raise FailClosedRuntimeError("Objective handoff is not implemented")
    if phase == cwm_v2.CANDIDATE_REVIEW:
        confirmation = candidate["semantic_memory"]["protocol_control"][
            "confirmation_binding"
        ]
        return OBJECTIVE_READY if confirmation is not None else CANDIDATE_REVIEW
    if phase == cwm_v2.CLARIFYING:
        return CLARIFYING
    if phase == cwm_v2.COLLECTING:
        return COLLECTING
    raise FailClosedRuntimeError("conversation protocol state is invalid")


def evaluate_conversation_readiness_v2(
    state: dict[str, Any],
    *,
    observed_at: str,
) -> dict[str, Any]:
    """Evaluate candidate and Objective Commitment eligibility without acting."""

    candidate = cwm_v2.validate_conversation_working_memory_state_v2(state)
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    expired = cwm_v2._is_v2_expired(candidate, observed)
    slots = candidate["semantic_memory"]["semantic_slots"]
    by_id = {slot["slot_id"]: slot for slot in slots}

    required_specs = (
        (cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY),
        (cwm_v2.OPERATIVE_SUBJECT, cwm_v2.PRIMARY),
        (cwm_v2.DESIRED_OUTCOME, cwm_v2.PRIMARY),
        (cwm_v2.WORK_TYPE, None),
    )
    required_missing: list[str] = []
    required_incomplete: list[str] = []
    for slot_class, slot_role in required_specs:
        matching = [
            slot
            for slot in slots
            if slot["slot_class"] == slot_class
            and (slot_role is None or slot["slot_role"] == slot_role)
        ]
        required_key = _required_slot_key(slot_class)
        if len(matching) != 1:
            required_missing.append(required_key)
            continue
        slot = matching[0]
        if not _slot_is_complete_active(slot):
            required_incomplete.append(slot["slot_id"])

    material_slots = [
        slot for slot in slots if slot["materiality"] != cwm_v2.OPTIONAL
    ]
    material_partial = sorted(
        slot["slot_id"]
        for slot in material_slots
        if slot["completeness"] == cwm_v2.PARTIAL
        or slot["status"] == cwm_v2.PROPOSED
    )
    material_conflicted = sorted(
        slot["slot_id"]
        for slot in material_slots
        if slot["status"] == cwm_v2.CONFLICTED
        or slot["completeness"] == cwm_v2.CONFLICTED
    )
    material_stale = sorted(
        slot["slot_id"]
        for slot in material_slots
        if slot["status"] == cwm_v2.STALE
        or slot["completeness"] == cwm_v2.STALE
    )
    unconfirmed_assumptions = sorted(
        slot["slot_id"]
        for slot in material_slots
        if slot["slot_class"] == cwm_v2.GOVERNING_QUALIFIER
        and slot["slot_role"] == cwm_v2.ASSUMPTION
        and (
            slot["status"] != cwm_v2.CONFIRMED
            or slot["confidence_class"] != cwm_v2.HUMAN_CONFIRMED
        )
    )
    unresolved_dependencies = sorted(
        slot["slot_id"]
        for slot in material_slots
        if any(
            dependency not in by_id
            or not _slot_is_complete_active(by_id[dependency])
            for dependency in slot["depends_on"]
        )
    )
    invalid_external_dispositions = sorted(
        slot["slot_id"]
        for slot in material_slots
        if slot["slot_class"] == cwm_v2.SEMANTIC_REFERENCE
        and slot["slot_role"] == cwm_v2.EVIDENCE
        and not any(
            entry["source_kind"] == cwm_v2.OWNER_DISPOSITION
            for entry in slot["provenance"]
        )
    )
    clarification = candidate["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    blockers = {
        "required_missing": sorted(required_missing),
        "required_incomplete": sorted(required_incomplete),
        "material_partial": material_partial,
        "material_conflicted": material_conflicted,
        "material_stale": material_stale,
        "unconfirmed_assumptions": unconfirmed_assumptions,
        "unresolved_dependencies": unresolved_dependencies,
        "invalid_external_dispositions": invalid_external_dispositions,
    }
    candidate_ready = (
        candidate["envelope"]["availability_state"] == cwm_v2.ACTIVE
        and not expired
        and not any(blockers.values())
        and clarification is None
    )
    control = candidate["semantic_memory"]["protocol_control"]
    candidate_bound = (
        control["candidate_projection"] is not None
        and candidate["envelope"]["active_objective_candidate_binding"] is not None
    )
    confirmation_bound = control["confirmation_binding"] is not None
    objective_eligible = (
        candidate_ready and candidate_bound and confirmation_bound
    )
    return {
        "conversation_state_machine_runtime_version": (
            PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2
        ),
        "protocol_state": derive_conversation_protocol_state_v2(
            candidate, observed_at=observed
        ),
        "availability_valid": (
            candidate["envelope"]["availability_state"] == cwm_v2.ACTIVE
            and not expired
        ),
        "required_core_complete_count": 4
        - len(required_missing)
        - len(required_incomplete),
        "required_core_missing_count": len(required_missing),
        "material_partial_count": len(material_partial),
        "material_conflict_count": len(material_conflicted),
        "material_stale_count": len(material_stale),
        "unconfirmed_material_assumption_count": len(unconfirmed_assumptions),
        "unresolved_dependency_count": len(unresolved_dependencies),
        "pending_clarification_count": 1 if clarification is not None else 0,
        "external_disposition_invalid_count": len(
            invalid_external_dispositions
        ),
        "candidate_ready": candidate_ready,
        "candidate_bound": candidate_bound,
        "confirmation_bound": confirmation_bound,
        "objective_commitment_eligible": objective_eligible,
        "blockers": blockers,
        "objective_created": False,
        "execution_invoked": False,
    }


def prepare_conversation_protocol_reduction_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Recompute clarification/review controls in one forward transaction."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    candidate = _next_control_revision(current, observed_at=observed_at)
    candidate = _reduce_protocol_controls(candidate, previous=current)
    if _protocol_projection(candidate) == _protocol_projection(current):
        return _transition_result(NO_CHANGE, current, None)
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(STATE_UPDATED, validated, validated)


def prepare_conversation_semantic_update_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    operation: str,
    incoming_slot: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Apply an unbound semantic update only outside clarification."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["conversation_phase"] == cwm_v2.CLARIFYING:
        raise FailClosedRuntimeError(
            "clarifying update requires a bound clarification answer"
        )
    return _prepare_semantic_update(
        current,
        expected_revision=expected_revision,
        operation=operation,
        incoming_slot=incoming_slot,
        observed_at=observed_at,
    )


def prepare_clarification_answer_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    clarification_id: str,
    operation: str,
    incoming_slot: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Apply one semantic answer bound to the exact current clarification."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["availability_state"] != cwm_v2.ACTIVE or current[
        "envelope"
    ]["conversation_phase"] != cwm_v2.CLARIFYING:
        raise FailClosedRuntimeError("conversation is not awaiting clarification")
    clarification = current["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    if clarification is None or clarification_id != clarification[
        "clarification_id"
    ]:
        raise FailClosedRuntimeError("clarification answer binding is stale")
    incoming = cwm_v2.validate_semantic_cwm_slot_v2(
        incoming_slot,
        conversation_identity=current["envelope"]["conversation_identity"],
    )
    if not _answer_addresses_clarification(clarification, incoming):
        raise FailClosedRuntimeError("clarification answer addresses another slot")
    return _prepare_semantic_update(
        current,
        expected_revision=expected_revision,
        operation=operation,
        incoming_slot=incoming,
        observed_at=observed_at,
    )


def prepare_conversation_correction_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    incoming_slot: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Apply one explicit human replacement, including during clarification."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    return _prepare_semantic_update(
        current,
        expected_revision=expected_revision,
        operation=slots_v2.REPLACE,
        incoming_slot=incoming_slot,
        observed_at=observed_at,
    )


def _prepare_semantic_update(
    current: dict[str, Any],
    *,
    expected_revision: int,
    operation: str,
    incoming_slot: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    if current["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        raise FailClosedRuntimeError("semantic update requires active conversation")
    semantic_result = slots_v2.prepare_semantic_slot_state_update_v2(
        current,
        expected_revision=expected_revision,
        operation=operation,
        incoming_slot=incoming_slot,
        observed_at=observed_at,
    )
    if semantic_result["replacement_state"] is None:
        if current["envelope"]["conversation_phase"] == cwm_v2.CLARIFYING:
            return prepare_no_progress_transition_v2(
                current,
                expected_revision=expected_revision,
                observed_at=observed_at,
            )
        return _transition_result(
            semantic_result["disposition"], current, None
        )
    candidate = _reduce_protocol_controls(
        semantic_result["replacement_state"], previous=current
    )
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(
        semantic_result["disposition"], validated, validated
    )


def prepare_no_progress_transition_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Record one no-progress event; a second suspends fail closed."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        raise FailClosedRuntimeError("no-progress transition requires active state")
    clarification = current["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    if clarification is None or clarification["status"] != "PENDING":
        raise FailClosedRuntimeError("no pending clarification exists")
    candidate = _next_control_revision(current, observed_at=observed_at)
    next_clarification = deepcopy(clarification)
    if clarification["no_progress_count"] < MAX_NO_PROGRESS_COUNT:
        next_clarification["no_progress_count"] += 1
        candidate["semantic_memory"]["protocol_control"][
            "clarification_control"
        ] = next_clarification
        disposition = NO_PROGRESS_RECORDED
    else:
        candidate["envelope"]["availability_state"] = cwm_v2.SUSPENDED
        candidate["envelope"]["suspended_at"] = candidate["envelope"][
            "updated_at"
        ]
        candidate["envelope"]["restored_at"] = None
        disposition = SUSPENDED_FAIL_CLOSED
    candidate = _refresh_bindings_and_integrity(candidate)
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(disposition, validated, validated)


def candidate_review_presentation_v2(state: dict[str, Any]) -> dict[str, Any]:
    """Return canonical review bytes and digest; transport framing is excluded."""

    candidate = validate_conversation_state_machine_state_v2(state)
    if candidate["envelope"]["conversation_phase"] != cwm_v2.CANDIDATE_REVIEW:
        raise FailClosedRuntimeError("candidate review is not active")
    control = candidate["semantic_memory"]["protocol_control"]
    projection = control["candidate_projection"]
    binding = candidate["envelope"]["active_objective_candidate_binding"]
    presentation = {
        "presentation_type": "CONVERSATION_CANDIDATE_PRESENTATION_V1",
        "conversation_identity": candidate["envelope"]["conversation_identity"],
        "candidate_source_global_revision": binding["bound_at_global_revision"],
        "semantic_revision": candidate["semantic_revision"],
        "normalization_ruleset_version": candidate["semantic_memory"][
            "normalization_ruleset_version"
        ],
        "candidate_projection_ruleset_version": projection[
            "projection_ruleset_version"
        ],
        "candidate_digest": binding["candidate_digest"],
        "semantic_values": deepcopy(projection["semantic_values"]),
        "capability_hints_are_advisory": True,
        "confirmation_is_not_commitment": True,
    }
    return {
        "presentation": presentation,
        "presentation_digest": cwm_v2._checksum(presentation),
    }


def create_candidate_confirmation_request_v2(
    state: dict[str, Any],
) -> dict[str, Any]:
    """Create the exact local control request a human interface must affirm."""

    candidate = validate_conversation_state_machine_state_v2(state)
    if not any(
        participant["participant_role"] == cwm_v2.HUMAN_ORIGINATOR
        for participant in candidate["envelope"]["participants"]
    ):
        raise FailClosedRuntimeError(
            "candidate confirmation requires a human participant binding"
        )
    presentation = candidate_review_presentation_v2(candidate)
    binding = candidate["envelope"]["active_objective_candidate_binding"]
    return {
        "protocol_version": PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2,
        "conversation_identity": candidate["envelope"]["conversation_identity"],
        "workspace_identity_hash": candidate["envelope"]["workspace_identity_hash"],
        "session_identity_hash": candidate["envelope"]["session_identity_hash"],
        "global_revision": candidate["revision"],
        "semantic_revision": candidate["semantic_revision"],
        "normalization_ruleset_version": candidate["semantic_memory"][
            "normalization_ruleset_version"
        ],
        "candidate_digest": binding["candidate_digest"],
        "presentation_digest": presentation["presentation_digest"],
        "participant_binding_digest": cwm_v2._checksum(
            candidate["envelope"]["participants"]
        ),
        "control_act": "CONFIRM_CANDIDATE",
    }


def prepare_candidate_confirmation_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    confirmation_request: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Bind exact semantic confirmation without preparing commitment."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if derive_conversation_protocol_state_v2(
        current, observed_at=observed_at
    ) != CANDIDATE_REVIEW:
        raise FailClosedRuntimeError("candidate is not awaiting confirmation")
    if not isinstance(confirmation_request, dict) or set(
        confirmation_request
    ) != _CONFIRMATION_REQUEST_FIELDS:
        raise FailClosedRuntimeError("confirmation request schema is invalid")
    expected = create_candidate_confirmation_request_v2(current)
    if confirmation_request != expected:
        raise FailClosedRuntimeError("confirmation request binding is stale")
    candidate = _next_control_revision(current, observed_at=observed_at)
    binding = candidate["envelope"]["active_objective_candidate_binding"]
    candidate["semantic_memory"]["protocol_control"]["confirmation_binding"] = {
        "confirmation_binding_type": (
            cwm_v2.PLATFORM_CORE_CONFIRMATION_BINDING_SCHEMA_V1
        ),
        "candidate_source_global_revision": binding["bound_at_global_revision"],
        "confirmation_global_revision": candidate["revision"],
        "semantic_revision": candidate["semantic_revision"],
        "candidate_digest": binding["candidate_digest"],
        "presentation_digest": confirmation_request["presentation_digest"],
        "participant_binding_digest": confirmation_request[
            "participant_binding_digest"
        ],
        "confirmed_at": candidate["envelope"]["updated_at"],
        "control_act": "CONFIRM_CANDIDATE",
    }
    candidate = _refresh_bindings_and_integrity(candidate)
    validated = validate_conversation_state_machine_state_v2(candidate)
    if derive_conversation_protocol_state_v2(
        validated, observed_at=observed_at
    ) != OBJECTIVE_READY:
        raise FailClosedRuntimeError("confirmation did not establish readiness")
    return _transition_result(CONFIRMATION_RECORDED, validated, validated)


def prepare_conversation_suspension_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Suspend one active pre-commit conversation without changing semantics."""

    current = _require_mutable_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        raise FailClosedRuntimeError("only an active conversation can suspend")
    candidate = _next_control_revision(current, observed_at=observed_at)
    candidate["envelope"]["availability_state"] = cwm_v2.SUSPENDED
    candidate["envelope"]["suspended_at"] = candidate["envelope"]["updated_at"]
    candidate["envelope"]["restored_at"] = None
    candidate = _refresh_bindings_and_integrity(candidate)
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(SUSPENDED, validated, validated)


def prepare_conversation_resume_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    current_interface_identity: str,
    participant_binding_digest: str,
    observed_at: str,
) -> dict[str, Any]:
    """Resume only the exact same-interface, same-participant conversation."""

    current = _require_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["availability_state"] != cwm_v2.SUSPENDED:
        raise FailClosedRuntimeError("conversation is not suspended")
    if current_interface_identity != current["envelope"]["current_interface_identity"]:
        raise FailClosedRuntimeError("cross-interface resume is not implemented")
    if participant_binding_digest != cwm_v2._checksum(
        current["envelope"]["participants"]
    ):
        raise FailClosedRuntimeError("resume participant binding is invalid")
    candidate = _next_control_revision(current, observed_at=observed_at)
    candidate["envelope"]["availability_state"] = cwm_v2.ACTIVE
    candidate["envelope"]["restored_at"] = candidate["envelope"]["updated_at"]
    candidate = _refresh_bindings_and_integrity(candidate)
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(RESUMED, validated, validated)


def prepare_conversation_abandonment_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Prepare the transient CLOSED revision used before deterministic cleanup."""

    current = _require_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["envelope"]["availability_state"] not in {
        cwm_v2.ACTIVE,
        cwm_v2.SUSPENDED,
    }:
        raise FailClosedRuntimeError("conversation cannot be abandoned")
    candidate = _next_control_revision(current, observed_at=observed_at)
    candidate["envelope"]["availability_state"] = cwm_v2.CLOSED
    candidate["envelope"]["closed_at"] = candidate["envelope"]["updated_at"]
    candidate = _refresh_bindings_and_integrity(candidate)
    validated = validate_conversation_state_machine_state_v2(candidate)
    return _transition_result(USER_ABANDONED, validated, validated)


def persist_conversation_state_machine_transition_v2(
    *,
    runtime_root: str,
    workspace_identity: str,
    session_identity: str,
    expected_revision: int,
    replacement_state: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Persist one prepared transition using the single G59-01 lock/path."""

    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(root):
        path = cwm_v2._state_path(root, workspace, session)
        if not path.exists():
            raise FailClosedRuntimeError("conversation working memory state is absent")
        current = validate_conversation_state_machine_state_v2(
            cwm_v2._read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _require_expected_revision(current, expected_revision)
        if cwm_v2._is_v2_expired(current, observed):
            raise FailClosedRuntimeError("conversation working memory state is expired")
        candidate = validate_conversation_state_machine_state_v2(
            replacement_state,
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _validate_transition_replacement(current, candidate, observed)
        cwm_v2._write_state_atomically(path, candidate)
        return deepcopy(candidate)


def abandon_conversation_state_machine_v2(
    *,
    runtime_root: str,
    workspace_identity: str,
    session_identity: str,
    expected_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Validate, transition through CLOSED, and atomically clean local state."""

    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(root):
        path = cwm_v2._state_path(root, workspace, session)
        if not path.exists():
            raise FailClosedRuntimeError("conversation working memory state is absent")
        current = validate_conversation_state_machine_state_v2(
            cwm_v2._read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        _require_expected_revision(current, expected_revision)
        if cwm_v2._is_v2_expired(current, observed):
            cwm_v2._remove_state(path, root)
            return _terminal_result(EXPIRED, current["revision"], None)
        prepared = prepare_conversation_abandonment_v2(
            current,
            expected_revision=expected_revision,
            observed_at=observed,
        )["replacement_state"]
        _validate_transition_replacement(current, prepared, observed)
        cwm_v2._write_state_atomically(path, prepared)
        cwm_v2._remove_state(path, root)
        return _terminal_result(USER_ABANDONED, prepared["revision"], prepared)


def recover_conversation_state_machine_v2(
    *,
    runtime_root: str,
    workspace_identity: str,
    session_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    """Recover valid state, clean ordinary expiry, or retain corrupt custody."""

    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(root):
        path = cwm_v2._state_path(root, workspace, session)
        if not path.exists():
            return _recovery_result(ABSENT, None, False)
        try:
            state = validate_conversation_state_machine_state_v2(
                cwm_v2._read_json_state(path),
                expected_workspace_identity=workspace,
                expected_session_identity=session,
            )
        except FailClosedRuntimeError:
            return _recovery_result(FAIL_CLOSED_RECOVERY, None, True)
        if state["envelope"]["availability_state"] == cwm_v2.CLOSED:
            cwm_v2._remove_state(path, root)
            return _recovery_result(ABANDONED, None, False)
        if cwm_v2._is_v2_expired(state, observed):
            cwm_v2._remove_state(path, root)
            return _recovery_result(EXPIRED, None, False)
        protocol_state = derive_conversation_protocol_state_v2(
            state, observed_at=observed
        )
        return _recovery_result(protocol_state, state, False)


def validate_conversation_state_machine_state_v2(
    state: dict[str, Any],
    *,
    expected_workspace_identity: str | None = None,
    expected_session_identity: str | None = None,
) -> dict[str, Any]:
    """Validate foundation state plus exact derived protocol invariants."""

    candidate = cwm_v2.validate_conversation_working_memory_state_v2(
        state,
        expected_workspace_identity=expected_workspace_identity,
        expected_session_identity=expected_session_identity,
    )
    control = candidate["semantic_memory"]["protocol_control"]
    clarification = control["clarification_control"]
    if clarification is not None:
        expected_clarification = _clarification_for_state(
            candidate,
            source_global_revision=clarification["source_global_revision"],
        )
        if expected_clarification is None:
            raise FailClosedRuntimeError("clarification no longer has a trigger")
        for field in (
            "clarification_id",
            "trigger_slot_id",
            "trigger_reason",
            "source_semantic_revision",
            "candidate_values",
            "question_template_id",
            "clarification_fingerprint",
        ):
            if clarification[field] != expected_clarification[field]:
                raise FailClosedRuntimeError("clarification binding is invalid")
        if clarification["status"] != "PENDING":
            raise FailClosedRuntimeError("only a pending clarification may be current")
    projection = control["candidate_projection"]
    if projection is not None:
        readiness = _readiness_without_protocol(candidate)
        if any(readiness["blockers"].values()):
            raise FailClosedRuntimeError("candidate projection is not ready")
        expected_projection = _candidate_projection(candidate)
        if projection != expected_projection:
            raise FailClosedRuntimeError("candidate projection is not canonical")
    confirmation = control["confirmation_binding"]
    if confirmation is not None:
        if not any(
            participant["participant_role"] == cwm_v2.HUMAN_ORIGINATOR
            for participant in candidate["envelope"]["participants"]
        ):
            raise FailClosedRuntimeError(
                "confirmation requires a human participant binding"
            )
        presentation = candidate_review_presentation_v2_unvalidated(candidate)
        if confirmation["presentation_digest"] != presentation[
            "presentation_digest"
        ]:
            raise FailClosedRuntimeError("confirmation presentation is invalid")
    return candidate


def _reduce_protocol_controls(
    candidate: dict[str, Any], *, previous: dict[str, Any]
) -> dict[str, Any]:
    if candidate["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        return _refresh_bindings_and_integrity(candidate)
    readiness = _readiness_without_protocol(candidate)
    control = candidate["semantic_memory"]["protocol_control"]
    if readiness["candidate_ready"]:
        projection = _candidate_projection(candidate)
        digest = cwm_v2._checksum(projection)
        previous_projection = previous["semantic_memory"]["protocol_control"][
            "candidate_projection"
        ]
        previous_binding = previous["envelope"][
            "active_objective_candidate_binding"
        ]
        unchanged_candidate = (
            previous_projection == projection
            and previous_binding is not None
            and previous_binding["candidate_digest"] == digest
            and previous_binding["semantic_revision"]
            == candidate["semantic_revision"]
        )
        control["clarification_control"] = None
        control["candidate_projection"] = projection
        if unchanged_candidate:
            bound_at = previous_binding["bound_at_global_revision"]
            control["confirmation_binding"] = deepcopy(
                previous["semantic_memory"]["protocol_control"][
                    "confirmation_binding"
                ]
            )
        else:
            bound_at = candidate["revision"]
            control["confirmation_binding"] = None
        candidate["envelope"]["active_objective_candidate_binding"] = {
            "semantic_revision": candidate["semantic_revision"],
            "candidate_projection_ruleset_version": (
                cwm_v2.PLATFORM_CORE_CANDIDATE_PROJECTION_RULESET_V1
            ),
            "candidate_digest": digest,
            "review_status": "AWAITING_HUMAN_REVIEW",
            "bound_at_global_revision": bound_at,
        }
        candidate["envelope"]["conversation_phase"] = cwm_v2.CANDIDATE_REVIEW
    else:
        clarification = _clarification_for_state(
            candidate, source_global_revision=candidate["revision"]
        )
        previous_clarification = previous["semantic_memory"]["protocol_control"][
            "clarification_control"
        ]
        if (
            clarification is not None
            and previous_clarification is not None
            and _clarification_semantic_projection(clarification)
            == _clarification_semantic_projection(previous_clarification)
        ):
            clarification = deepcopy(previous_clarification)
        control["candidate_projection"] = None
        control["confirmation_binding"] = None
        candidate["envelope"]["active_objective_candidate_binding"] = None
        if clarification is None:
            control["clarification_control"] = None
            candidate["envelope"]["conversation_phase"] = cwm_v2.COLLECTING
        else:
            control["clarification_control"] = clarification
            candidate["envelope"]["conversation_phase"] = cwm_v2.CLARIFYING
    return _refresh_bindings_and_integrity(candidate)


def _readiness_without_protocol(state: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(state)
    candidate["semantic_memory"]["protocol_control"] = cwm_v2._empty_protocol_control()
    candidate["envelope"]["conversation_phase"] = cwm_v2.COLLECTING
    candidate["envelope"]["active_objective_candidate_binding"] = None
    candidate = _refresh_bindings_and_integrity(candidate)
    return evaluate_conversation_readiness_v2(
        candidate, observed_at=candidate["envelope"]["updated_at"]
    )


def _clarification_for_state(
    state: dict[str, Any], *, source_global_revision: int
) -> dict[str, Any] | None:
    readiness = _readiness_without_protocol(state)
    slots = state["semantic_memory"]["semantic_slots"]
    by_id = {slot["slot_id"]: slot for slot in slots}
    trigger_slot_id: str | None = None
    reason: str | None = None
    template: str | None = None
    candidate_values: list[str] = []

    for slot_id in readiness["blockers"]["material_conflicted"]:
        slot = by_id[slot_id]
        trigger_slot_id = slot_id
        reason = "CONFLICTED"
        template = "CLARIFY_CONFLICT_V1"
        candidate_values = sorted(
            {
                slot["canonical_value"],
                *[entry["source_span"] for entry in slot["provenance"]],
            }
        )[: cwm_v2.MAX_CLARIFICATION_CANDIDATES]
        break
    ordered_required = (
        (cwm_v2.OPERATIVE_ACTION, "CLARIFY_REQUIRED_ACTION_V1"),
        (cwm_v2.OPERATIVE_SUBJECT, "CLARIFY_REQUIRED_SUBJECT_V1"),
        (cwm_v2.DESIRED_OUTCOME, "CLARIFY_REQUIRED_OUTCOME_V1"),
        (cwm_v2.WORK_TYPE, "CLARIFY_REQUIRED_WORK_TYPE_V1"),
    )
    if trigger_slot_id is None:
        missing = set(readiness["blockers"]["required_missing"])
        incomplete = set(readiness["blockers"]["required_incomplete"])
        for slot_class, question_template in ordered_required:
            key = _required_slot_key(slot_class)
            matching = [
                slot for slot in slots if slot["slot_class"] == slot_class
            ]
            primary = next(
                (
                    slot
                    for slot in matching
                    if slot_class == cwm_v2.WORK_TYPE
                    or slot["slot_role"] == cwm_v2.PRIMARY
                ),
                None,
            )
            if key in missing:
                trigger_slot_id = key
                reason = "MISSING"
                template = question_template
                break
            if primary is not None and primary["slot_id"] in incomplete:
                trigger_slot_id = primary["slot_id"]
                reason = _slot_block_reason(primary)
                template = question_template
                candidate_values = [primary["canonical_value"]]
                break
    precedence = (
        ("unconfirmed_assumptions", "UNCONFIRMED", "CLARIFY_ASSUMPTION_V1"),
        ("unresolved_dependencies", "STALE", "CLARIFY_DEPENDENCY_V1"),
        ("material_stale", "STALE", "CLARIFY_REFERENCE_V1"),
        ("invalid_external_dispositions", "STALE", "CLARIFY_REFERENCE_V1"),
        ("material_partial", "PARTIAL", "CLARIFY_QUALIFIER_V1"),
    )
    if trigger_slot_id is None:
        for blocker_name, blocker_reason, question_template in precedence:
            blocker_ids = readiness["blockers"][blocker_name]
            if blocker_ids:
                trigger_slot_id = blocker_ids[0]
                reason = blocker_reason
                template = question_template
                candidate_values = [by_id[trigger_slot_id]["canonical_value"]]
                break
    if trigger_slot_id is None:
        return None
    body = {
        "trigger_slot_id": trigger_slot_id,
        "trigger_reason": reason,
        "source_global_revision": source_global_revision,
        "source_semantic_revision": state["semantic_revision"],
        "candidate_values": sorted(set(candidate_values)),
        "question_template_id": template,
    }
    fingerprint = "clarification-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(body)
    ).hexdigest()
    identity_body = {
        "conversation_identity": state["envelope"]["conversation_identity"],
        "clarification_fingerprint": fingerprint,
    }
    clarification_id = "clarification-local-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(identity_body)
    ).hexdigest()
    return {
        "clarification_id": clarification_id,
        **body,
        "clarification_fingerprint": fingerprint,
        "no_progress_count": 0,
        "status": "PENDING",
    }


def _candidate_projection(state: dict[str, Any]) -> dict[str, Any]:
    values = [
        {
            "slot_id": slot["slot_id"],
            "slot_class": slot["slot_class"],
            "slot_role": slot["slot_role"],
            "cardinality_key": slot["cardinality_key"],
            "canonical_value": slot["canonical_value"],
            "equivalence_key": slot["equivalence_key"],
            "materiality": slot["materiality"],
        }
        for slot in state["semantic_memory"]["semantic_slots"]
    ]
    return {
        "projection_type": cwm_v2.PLATFORM_CORE_CANDIDATE_PROJECTION_SCHEMA_V1,
        "projection_ruleset_version": (
            cwm_v2.PLATFORM_CORE_CANDIDATE_PROJECTION_RULESET_V1
        ),
        "source_semantic_revision": state["semantic_revision"],
        "semantic_values": values,
    }


def candidate_review_presentation_v2_unvalidated(
    state: dict[str, Any],
) -> dict[str, Any]:
    control = state["semantic_memory"]["protocol_control"]
    projection = control["candidate_projection"]
    binding = state["envelope"]["active_objective_candidate_binding"]
    presentation = {
        "presentation_type": "CONVERSATION_CANDIDATE_PRESENTATION_V1",
        "conversation_identity": state["envelope"]["conversation_identity"],
        "candidate_source_global_revision": binding["bound_at_global_revision"],
        "semantic_revision": state["semantic_revision"],
        "normalization_ruleset_version": state["semantic_memory"][
            "normalization_ruleset_version"
        ],
        "candidate_projection_ruleset_version": projection[
            "projection_ruleset_version"
        ],
        "candidate_digest": binding["candidate_digest"],
        "semantic_values": deepcopy(projection["semantic_values"]),
        "capability_hints_are_advisory": True,
        "confirmation_is_not_commitment": True,
    }
    return {
        "presentation": presentation,
        "presentation_digest": cwm_v2._checksum(presentation),
    }


def _next_control_revision(
    current: dict[str, Any], *, observed_at: str
) -> dict[str, Any]:
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    if cwm_v2._parse_timestamp(observed, "observed_at") < cwm_v2._parse_timestamp(
        current["envelope"]["updated_at"], "updated_at"
    ):
        raise FailClosedRuntimeError("conversation update time precedes current state")
    candidate = deepcopy(current)
    candidate["revision"] += 1
    candidate["envelope_revision"] += 1
    candidate["envelope"]["updated_at"] = observed
    return candidate


def _refresh_bindings_and_integrity(state: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(state)
    candidate["envelope"]["semantic_memory_binding"] = {
        "semantic_memory_type": cwm_v2.PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "global_revision": candidate["revision"],
        "semantic_revision": candidate["semantic_revision"],
        "semantic_memory_digest": cwm_v2._checksum(candidate["semantic_memory"]),
    }
    return cwm_v2._with_integrity(candidate)


def _require_current(
    state: dict[str, Any], *, expected_revision: int, observed_at: str
) -> dict[str, Any]:
    current = validate_conversation_state_machine_state_v2(state)
    _require_expected_revision(current, expected_revision)
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    if cwm_v2._is_v2_expired(current, observed):
        raise FailClosedRuntimeError("conversation working memory state is expired")
    return current


def _require_mutable_current(
    state: dict[str, Any], *, expected_revision: int, observed_at: str
) -> dict[str, Any]:
    current = _require_current(
        state, expected_revision=expected_revision, observed_at=observed_at
    )
    if current["migration_metadata"]["migration_status"] != cwm_v2.NATIVE_V2:
        raise FailClosedRuntimeError("legacy semantic review is not implemented")
    if current["envelope"]["availability_state"] == cwm_v2.CLOSED:
        raise FailClosedRuntimeError("closed conversation is immutable")
    return current


def _require_expected_revision(state: dict[str, Any], expected_revision: int) -> None:
    if not isinstance(expected_revision, int) or isinstance(expected_revision, bool):
        raise FailClosedRuntimeError("expected revision is invalid")
    if state["revision"] != expected_revision:
        raise FailClosedRuntimeError("conversation state revision does not match")


def _validate_transition_replacement(
    current: dict[str, Any], candidate: dict[str, Any], observed_at: str
) -> None:
    if candidate["revision"] != current["revision"] + 1:
        raise FailClosedRuntimeError("state transition revision is invalid")
    if candidate["envelope_revision"] != current["envelope_revision"] + 1:
        raise FailClosedRuntimeError("Envelope transition revision is invalid")
    if candidate["semantic_revision"] not in {
        current["semantic_revision"],
        current["semantic_revision"] + 1,
    }:
        raise FailClosedRuntimeError("semantic transition revision is invalid")
    if candidate["envelope"]["updated_at"] != observed_at:
        raise FailClosedRuntimeError("state transition timestamp is invalid")
    if cwm_v2._parse_timestamp(
        observed_at, "observed_at"
    ) < cwm_v2._parse_timestamp(
        current["envelope"]["updated_at"], "updated_at"
    ):
        raise FailClosedRuntimeError("state transition time precedes current state")
    for field in (
        "working_memory_type",
        "runtime_version",
        "schema_version",
        "runtime_owner",
        "migration_metadata",
        "constitutional_artifact",
        "constitutional_authority",
        "replay_visible",
        "authorization_eligible",
        "worker_eligible",
        "objective_creation_supported",
        "capability_routing_supported",
    ):
        if candidate[field] != current[field]:
            raise FailClosedRuntimeError("state transition changes immutable field")
    for field in (
        "conversation_identity",
        "workspace_identity",
        "workspace_identity_hash",
        "session_identity",
        "session_identity_hash",
        "origin_interface_identity",
        "current_interface_identity",
        "participants",
        "context_scope",
        "created_at",
        "expires_at",
    ):
        if candidate["envelope"][field] != current["envelope"][field]:
            raise FailClosedRuntimeError("state transition changes Envelope identity")
    if candidate["semantic_memory"]["legacy_import"] != current[
        "semantic_memory"
    ]["legacy_import"]:
        raise FailClosedRuntimeError("state transition changes legacy import")
    slots_changed = candidate["semantic_memory"]["semantic_slots"] != current[
        "semantic_memory"
    ]["semantic_slots"]
    current_availability = current["envelope"]["availability_state"]
    candidate_availability = candidate["envelope"]["availability_state"]
    allowed_availability = {
        cwm_v2.ACTIVE: {cwm_v2.ACTIVE, cwm_v2.SUSPENDED, cwm_v2.CLOSED},
        cwm_v2.SUSPENDED: {cwm_v2.ACTIVE, cwm_v2.CLOSED},
        cwm_v2.CLOSED: set(),
    }
    if candidate_availability not in allowed_availability[current_availability]:
        raise FailClosedRuntimeError("availability transition is not supported")
    if current_availability != cwm_v2.ACTIVE and slots_changed:
        raise FailClosedRuntimeError(
            "semantic transition requires an active conversation"
        )
    if slots_changed != (
        candidate["semantic_revision"] == current["semantic_revision"] + 1
    ):
        raise FailClosedRuntimeError("semantic revision does not match slot change")
    cwm_v2._validate_slot_revision_transitions(current, candidate)


def _protocol_projection(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "conversation_phase": state["envelope"]["conversation_phase"],
        "candidate_binding": state["envelope"]["active_objective_candidate_binding"],
        "protocol_control": state["semantic_memory"]["protocol_control"],
    }


def _clarification_semantic_projection(
    clarification: dict[str, Any]
) -> dict[str, Any]:
    return {
        field: deepcopy(clarification[field])
        for field in (
            "trigger_slot_id",
            "trigger_reason",
            "source_semantic_revision",
            "candidate_values",
            "question_template_id",
        )
    }


def _answer_addresses_clarification(
    clarification: dict[str, Any], incoming_slot: dict[str, Any]
) -> bool:
    trigger = clarification["trigger_slot_id"]
    if trigger.startswith("conversation-slot-sha256:"):
        return incoming_slot["slot_id"] == trigger
    parts = trigger.split(":")
    if len(parts) != 3 or parts[0] != "required-slot":
        return False
    slot_class = parts[1]
    if incoming_slot["slot_class"] != slot_class:
        return False
    return slot_class == cwm_v2.WORK_TYPE or incoming_slot[
        "slot_role"
    ] == cwm_v2.PRIMARY


def _slot_is_complete_active(slot: dict[str, Any]) -> bool:
    return (
        slot["status"] in {cwm_v2.ASSERTED, cwm_v2.CONFIRMED}
        and slot["completeness"] == cwm_v2.COMPLETE
    )


def _slot_block_reason(slot: dict[str, Any]) -> str:
    if slot["status"] == cwm_v2.CONFLICTED:
        return "CONFLICTED"
    if slot["status"] == cwm_v2.STALE:
        return "STALE"
    return "PARTIAL"


def _required_slot_key(slot_class: str) -> str:
    return f"required-slot:{slot_class}:PRIMARY"


def _transition_result(
    disposition: str,
    state: dict[str, Any],
    replacement_state: dict[str, Any] | None,
) -> dict[str, Any]:
    protocol_state = derive_conversation_protocol_state_v2(
        state, observed_at=state["envelope"]["updated_at"]
    )
    return {
        "conversation_state_machine_runtime_version": (
            PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2
        ),
        "disposition": disposition,
        "protocol_state": protocol_state,
        "state_changed": replacement_state is not None,
        "replacement_state": deepcopy(replacement_state),
        "objective_commitment_eligible": protocol_state == OBJECTIVE_READY,
        "objective_created": False,
        "execution_invoked": False,
    }


def _terminal_result(
    disposition: str,
    final_revision: int,
    closed_state: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "conversation_state_machine_runtime_version": (
            PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2
        ),
        "disposition": disposition,
        "protocol_state": ABANDONED if disposition == USER_ABANDONED else EXPIRED,
        "final_revision": final_revision,
        "closed_state_digest": (
            cwm_v2._checksum(closed_state) if closed_state is not None else None
        ),
        "state_present": False,
        "objective_created": False,
        "execution_invoked": False,
    }


def _recovery_result(
    protocol_state: str,
    state: dict[str, Any] | None,
    retained_for_recovery: bool,
) -> dict[str, Any]:
    return {
        "conversation_state_machine_runtime_version": (
            PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2
        ),
        "protocol_state": protocol_state,
        "state": deepcopy(state),
        "retained_for_recovery": retained_for_recovery,
        "objective_created": False,
        "execution_invoked": False,
    }


__all__ = [
    "ABANDONED",
    "ABSENT",
    "CANDIDATE_REVIEW",
    "CLARIFYING",
    "COLLECTING",
    "EXPIRED",
    "FAIL_CLOSED_RECOVERY",
    "OBJECTIVE_READY",
    "PLATFORM_CORE_CONVERSATION_STATE_MACHINE_RUNTIME_V2",
    "SUSPENDED",
    "abandon_conversation_state_machine_v2",
    "candidate_review_presentation_v2",
    "create_candidate_confirmation_request_v2",
    "derive_conversation_protocol_state_v2",
    "evaluate_conversation_readiness_v2",
    "persist_conversation_state_machine_transition_v2",
    "prepare_candidate_confirmation_v2",
    "prepare_clarification_answer_v2",
    "prepare_conversation_abandonment_v2",
    "prepare_conversation_correction_v2",
    "prepare_conversation_protocol_reduction_v2",
    "prepare_conversation_resume_v2",
    "prepare_conversation_semantic_update_v2",
    "prepare_conversation_suspension_v2",
    "prepare_no_progress_transition_v2",
    "recover_conversation_state_machine_v2",
    "validate_conversation_state_machine_state_v2",
]
