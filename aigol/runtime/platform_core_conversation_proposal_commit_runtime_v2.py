"""Atomic, isolated commit boundary for validated interpreter candidates.

This runtime revalidates a G59-04 candidate operation set, reduces it through
the G59-02 semantic slot owner, refreshes G59-03 protocol controls, and writes
one G59-01 atomic state revision.  It creates no Objective, Replay artifact,
authorization, capability selection, Worker request, or external execution.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_interpreter_proposal_runtime_v2 as proposal_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as state_machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


PLATFORM_CORE_CONVERSATION_PROPOSAL_COMMIT_RUNTIME_V2 = (
    "PLATFORM_CORE_CONVERSATION_PROPOSAL_COMMIT_RUNTIME_V2"
)
PLATFORM_CORE_PROPOSAL_COMMIT_RECEIPT_SCHEMA_V1 = (
    "PLATFORM_CORE_PROPOSAL_COMMIT_RECEIPT_SCHEMA_V1"
)
PROPOSAL_COMMIT_RULESET_V1 = "PROPOSAL_COMMIT_RULESET_V1"

COMMITTED = "COMMITTED"
ALREADY_COMMITTED = "ALREADY_COMMITTED"
PREPARED = "PREPARED"

CREATE_CANDIDATE = "CREATE_CANDIDATE"
REVISE_CANDIDATE = "REVISE_CANDIDATE"
EQUIVALENCE_CANDIDATE = "EQUIVALENCE_CANDIDATE"
CONFLICT_CANDIDATE = "CONFLICT_CANDIDATE"
CLARIFICATION_CANDIDATE = "CLARIFICATION_CANDIDATE"
REFERENCE_ATTACHMENT_CANDIDATE = "REFERENCE_ATTACHMENT_CANDIDATE"

_COMMITTABLE_OPERATION_TYPES = frozenset(
    {
        CREATE_CANDIDATE,
        REVISE_CANDIDATE,
        EQUIVALENCE_CANDIDATE,
        REFERENCE_ATTACHMENT_CANDIDATE,
    }
)


class ProposalCommitError(FailClosedRuntimeError):
    """Fail-closed proposal commit error with a stable reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def prepare_proposal_commit_v2(
    state: dict[str, Any],
    *,
    candidate_operation_set: dict[str, Any],
    expected_revision: int,
    committed_at: str,
) -> dict[str, Any]:
    """Prepare one all-or-nothing semantic mutation without persistence."""

    candidate_set = _validated_candidate_set(candidate_operation_set)
    current = _validated_current_state(state, committed_at=committed_at)
    _validate_identity_bindings(current, candidate_set, expected_revision)
    if _already_committed(current, candidate_set):
        return _commit_result(
            disposition=ALREADY_COMMITTED,
            candidate_set=candidate_set,
            state=current,
            replacement_state=None,
            application_order=_application_order(candidate_set),
            invalidated_dependency_ids=[],
            durably_committed=False,
        )
    _require_current_revisions(current, candidate_set, expected_revision)
    replacement, application_order, invalidated = _prepare_replacement(
        current,
        candidate_set,
        committed_at=committed_at,
    )
    return _commit_result(
        disposition=PREPARED,
        candidate_set=candidate_set,
        state=replacement,
        replacement_state=replacement,
        application_order=application_order,
        invalidated_dependency_ids=invalidated,
        durably_committed=False,
    )


def commit_proposal_candidate_operations_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    candidate_operation_set: dict[str, Any],
    expected_revision: int,
    committed_at: str,
) -> dict[str, Any]:
    """Validate and atomically commit one candidate set under the G59-01 lock."""

    candidate_set = _validated_candidate_set(candidate_operation_set)
    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    timestamp = cwm_v2._canonical_timestamp(committed_at, "committed_at")
    root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(root):
        path = cwm_v2._state_path(root, workspace, session)
        if not path.exists():
            _fail("STATE_ABSENT", "conversation working memory state is absent")
        current = state_machine_v2.validate_conversation_state_machine_state_v2(
            cwm_v2._read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        current = _validated_current_state(current, committed_at=timestamp)
        _validate_identity_bindings(current, candidate_set, expected_revision)
        if _already_committed(current, candidate_set):
            return _commit_result(
                disposition=ALREADY_COMMITTED,
                candidate_set=candidate_set,
                state=current,
                replacement_state=None,
                application_order=_application_order(candidate_set),
                invalidated_dependency_ids=[],
                durably_committed=False,
            )
        _require_current_revisions(current, candidate_set, expected_revision)
        replacement, application_order, invalidated = _prepare_replacement(
            current,
            candidate_set,
            committed_at=timestamp,
        )
        state_machine_v2._validate_transition_replacement(
            current, replacement, timestamp
        )
        cwm_v2._write_state_atomically(path, replacement)
        persisted = state_machine_v2.validate_conversation_state_machine_state_v2(
            cwm_v2._read_json_state(path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
        if persisted != replacement:
            _fail("ATOMIC_WRITE_VERIFICATION_FAILED", "persisted state differs")
        return _commit_result(
            disposition=COMMITTED,
            candidate_set=candidate_set,
            state=persisted,
            replacement_state=persisted,
            application_order=application_order,
            invalidated_dependency_ids=invalidated,
            durably_committed=True,
        )


def _validated_candidate_set(value: Any) -> dict[str, Any]:
    try:
        candidate_set = proposal_v2.validate_candidate_operation_set_v2(value)
    except (proposal_v2.ProposalValidationError, FailClosedRuntimeError) as exc:
        _fail("CANDIDATE_SET_INVALID", str(exc))
    if (
        candidate_set["validation_disposition"] != proposal_v2.ADMISSIBLE
        or candidate_set["clarification_required"] is not False
        or candidate_set["reduction_allowed"] is not True
    ):
        _fail("CANDIDATE_SET_NOT_ADMISSIBLE", "candidate set requires clarification")
    operation_types = {
        operation["candidate_operation_type"]
        for operation in candidate_set["candidate_operations"]
    }
    unsupported = operation_types.difference(_COMMITTABLE_OPERATION_TYPES)
    if unsupported:
        _fail(
            "CANDIDATE_OPERATION_NOT_COMMITTABLE",
            f"candidate operation is not committable: {sorted(unsupported)[0]}",
        )
    proposed_slot_ids = [
        operation["proposed_slot_id"]
        for operation in candidate_set["candidate_operations"]
    ]
    if len(set(proposed_slot_ids)) != len(proposed_slot_ids):
        _fail(
            "CANDIDATE_OPERATION_COLLISION",
            "candidate set addresses one slot more than once",
        )
    return candidate_set


def _validated_current_state(
    state: Any,
    *,
    committed_at: str,
) -> dict[str, Any]:
    try:
        current = state_machine_v2.validate_conversation_state_machine_state_v2(
            state
        )
        timestamp = cwm_v2._canonical_timestamp(committed_at, "committed_at")
    except FailClosedRuntimeError as exc:
        _fail("STATE_INVALID", str(exc))
    if cwm_v2._is_v2_expired(current, timestamp):
        _fail("STATE_EXPIRED", "conversation working memory state is expired")
    if current["migration_metadata"]["migration_status"] != cwm_v2.NATIVE_V2:
        _fail("STATE_NOT_NATIVE_V2", "legacy semantic review is not implemented")
    if current["envelope"]["availability_state"] != cwm_v2.ACTIVE:
        _fail("STATE_NOT_ACTIVE", "proposal commit requires an active conversation")
    if current["envelope"]["conversation_phase"] in {
        cwm_v2.COMMITMENT_PENDING,
        cwm_v2.HANDED_OFF,
    }:
        _fail("STATE_PHASE_FORBIDDEN", "proposal commit phase is forbidden")
    if cwm_v2._parse_timestamp(
        timestamp, "committed_at"
    ) < cwm_v2._parse_timestamp(
        current["envelope"]["updated_at"], "updated_at"
    ):
        _fail("COMMIT_TIME_INVALID", "proposal commit precedes current state")
    return current


def _validate_identity_bindings(
    current: dict[str, Any],
    candidate_set: dict[str, Any],
    expected_revision: int,
) -> None:
    if not isinstance(expected_revision, int) or isinstance(expected_revision, bool):
        _fail("EXPECTED_REVISION_INVALID", "expected revision is invalid")
    if candidate_set["expected_cwm_revision"] != expected_revision:
        _fail("COMMIT_BINDING_MISMATCH", "candidate expected revision differs")
    envelope = current["envelope"]
    bindings = {
        "conversation_identity": envelope["conversation_identity"],
        "workspace_identity_hash": envelope["workspace_identity_hash"],
        "session_identity_hash": envelope["session_identity_hash"],
    }
    for field, expected in bindings.items():
        if candidate_set[field] != expected:
            _fail("COMMIT_BINDING_MISMATCH", f"candidate {field} differs")


def _require_current_revisions(
    current: dict[str, Any],
    candidate_set: dict[str, Any],
    expected_revision: int,
) -> None:
    if current["revision"] != expected_revision or current[
        "semantic_revision"
    ] != candidate_set["expected_semantic_revision"]:
        _fail("STALE_COMMIT_REVISION", "candidate revision binding is stale")


def _application_order(candidate_set: dict[str, Any]) -> list[str]:
    return sorted(
        operation["operation_id"]
        for operation in candidate_set["candidate_operations"]
    )


def _prepare_replacement(
    current: dict[str, Any],
    candidate_set: dict[str, Any],
    *,
    committed_at: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    conversation = current["envelope"]["conversation_identity"]
    by_id = {
        slot["slot_id"]: deepcopy(slot)
        for slot in slots_v2.validate_semantic_slot_collection_v2(
            current["semantic_memory"]["semantic_slots"],
            conversation_identity=conversation,
        )
    }
    explicit_slot_ids: set[str] = set()
    new_slot_ids: set[str] = set()
    invalidation_roots: set[str] = set()
    operations = sorted(
        candidate_set["candidate_operations"],
        key=lambda operation: operation["operation_id"],
    )
    application_order: list[str] = []
    for operation in operations:
        operation_id = operation["operation_id"]
        slot_id = operation["proposed_slot_id"]
        incoming = _incoming_slot(
            operation,
            candidate_set=candidate_set,
            committed_at=committed_at,
        )
        active = by_id.get(slot_id)
        operation_type = operation["candidate_operation_type"]
        if operation_type in {CREATE_CANDIDATE, REFERENCE_ATTACHMENT_CANDIDATE}:
            if active is not None:
                _fail("SEMANTIC_CONFLICT", "candidate creation slot already exists")
            changed = incoming
            new_slot_ids.add(slot_id)
        elif operation_type == REVISE_CANDIDATE:
            if active is None:
                _fail("SEMANTIC_CONFLICT", "candidate revision slot is absent")
            result = slots_v2.revise_semantic_slot_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=committed_at,
            )
            changed = _required_changed_slot(result)
        elif operation_type == EQUIVALENCE_CANDIDATE:
            if active is None:
                _fail("SEMANTIC_CONFLICT", "candidate equivalence slot is absent")
            result = slots_v2.merge_semantic_slots_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=committed_at,
            )
            changed = _required_changed_slot(result)
        else:
            _fail("CANDIDATE_OPERATION_NOT_COMMITTABLE", "operation is unsupported")
        by_id[slot_id] = changed
        explicit_slot_ids.add(slot_id)
        if active is not None and (
            active["equivalence_key"] != changed["equivalence_key"]
            or (
                active["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}
                and changed["status"] in {cwm_v2.CONFLICTED, cwm_v2.STALE}
            )
        ):
            invalidation_roots.add(slot_id)
        application_order.append(operation_id)

    canonical_before_invalidation = slots_v2.validate_semantic_slot_collection_v2(
        list(by_id.values()), conversation_identity=conversation
    )
    by_id = {slot["slot_id"]: slot for slot in canonical_before_invalidation}
    invalidated: set[str] = set()
    for root_slot_id in sorted(invalidation_roots):
        by_id, root_invalidated = slots_v2._invalidate_dependents(
            by_id,
            root_slot_id,
            observed_at=committed_at,
            conversation_identity=conversation,
        )
        invalidated.update(root_invalidated)
    if invalidated.intersection(explicit_slot_ids) or invalidated.intersection(
        new_slot_ids
    ):
        _fail(
            "ATOMIC_DEPENDENCY_CONFLICT",
            "one candidate operation invalidates another candidate operation",
        )
    semantic_slots = slots_v2.validate_semantic_slot_collection_v2(
        list(by_id.values()), conversation_identity=conversation
    )
    replacement = _state_replacement(
        current,
        semantic_slots=semantic_slots,
        committed_at=committed_at,
    )
    return replacement, application_order, sorted(invalidated)


def _required_changed_slot(result: dict[str, Any]) -> dict[str, Any]:
    if result["disposition"] in {
        slots_v2.CONFLICT_DETECTED,
        slots_v2.REJECT_LOWER_EVIDENCE,
        slots_v2.NO_CHANGE,
    }:
        _fail(
            "SEMANTIC_CONFLICT",
            f"candidate reduction did not produce one change: {result['disposition']}",
        )
    return deepcopy(result["slot"])


def _incoming_slot(
    operation: dict[str, Any],
    *,
    candidate_set: dict[str, Any],
    committed_at: str,
) -> dict[str, Any]:
    dependencies = set(operation["depends_on_slot_ids"])
    if operation["candidate_operation_type"] == REFERENCE_ATTACHMENT_CANDIDATE:
        target = operation["target_slot_id"]
        if target is None:
            _fail("SEMANTIC_CONFLICT", "reference attachment target is absent")
        dependencies.add(target)
    return slots_v2.create_semantic_slot_v2(
        conversation_identity=candidate_set["conversation_identity"],
        slot_class=operation["slot_class"],
        slot_role=operation["slot_role"],
        cardinality_key=operation["cardinality_key"],
        surface_value=operation["surface_value"],
        canonical_value=operation["canonical_value"],
        status=cwm_v2.PROPOSED,
        completeness=cwm_v2.COMPLETE,
        confidence_class=cwm_v2.CONTEXT_DERIVED,
        materiality=_materiality(operation["slot_class"]),
        provenance=[_proposal_origin_provenance(operation, candidate_set)],
        depends_on=sorted(dependencies),
        created_at=committed_at,
    )


def _materiality(slot_class: str) -> str:
    if slot_class in {
        cwm_v2.OPERATIVE_ACTION,
        cwm_v2.OPERATIVE_SUBJECT,
        cwm_v2.DESIRED_OUTCOME,
        cwm_v2.WORK_TYPE,
    }:
        return cwm_v2.REQUIRED
    return cwm_v2.CONDITIONAL


def _proposal_origin_provenance(
    operation: dict[str, Any], candidate_set: dict[str, Any]
) -> dict[str, Any]:
    surface = operation["surface_value"]
    markers = sorted(
        {
            PROPOSAL_COMMIT_RULESET_V1,
            "candidate-set:" + candidate_set["candidate_operation_set_id"],
            "proposal:" + candidate_set["proposal_id"],
            "operation:" + operation["operation_id"],
            "source-turn:" + candidate_set["source_turn_identity"],
            "interpreter-class:" + candidate_set["interpreter_class"],
            "interpreter-sha256:"
            + hashlib.sha256(
                candidate_set["interpreter_identity"].encode("utf-8")
            ).hexdigest(),
        }
    )
    return {
        "source_kind": cwm_v2.HUMAN_TURN,
        "turn_number": candidate_set["expected_cwm_revision"] + 1,
        "source_revision": candidate_set["expected_cwm_revision"],
        "source_span": surface,
        "content_digest": cwm_v2._checksum(surface),
        "normalization_rule_ids": markers,
        "human_disposition": "NOT_APPLICABLE",
    }


def _already_committed(
    current: dict[str, Any], candidate_set: dict[str, Any]
) -> bool:
    by_id = {
        slot["slot_id"]: slot
        for slot in current["semantic_memory"]["semantic_slots"]
    }
    matches: list[bool] = []
    for operation in candidate_set["candidate_operations"]:
        slot = by_id.get(operation["proposed_slot_id"])
        provenance = _proposal_origin_provenance(operation, candidate_set)
        matches.append(
            slot is not None
            and slot["canonical_value"] == operation["canonical_value"]
            and slot["equivalence_key"]
            == operation["validator_derived_equivalence_key"]
            and provenance in slot["provenance"]
        )
    if any(matches) and not all(matches):
        _fail(
            "PARTIAL_COMMIT_DETECTED",
            "candidate set has only partial durable commit evidence",
        )
    return bool(matches) and all(matches)


def _state_replacement(
    current: dict[str, Any],
    *,
    semantic_slots: list[dict[str, Any]],
    committed_at: str,
) -> dict[str, Any]:
    candidate = deepcopy(current)
    candidate["revision"] += 1
    candidate["envelope_revision"] += 1
    candidate["semantic_revision"] += 1
    candidate["envelope"]["updated_at"] = committed_at
    candidate["envelope"]["conversation_phase"] = cwm_v2.COLLECTING
    candidate["envelope"]["active_objective_candidate_binding"] = None
    candidate["semantic_memory"]["semantic_slots"] = semantic_slots
    candidate["semantic_memory"]["protocol_control"] = cwm_v2._empty_protocol_control()
    candidate["envelope"]["semantic_memory_binding"] = {
        "semantic_memory_type": cwm_v2.PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "global_revision": candidate["revision"],
        "semantic_revision": candidate["semantic_revision"],
        "semantic_memory_digest": cwm_v2._checksum(candidate["semantic_memory"]),
    }
    candidate = cwm_v2._with_integrity(candidate)
    candidate = state_machine_v2._reduce_protocol_controls(
        candidate, previous=current
    )
    validated = state_machine_v2.validate_conversation_state_machine_state_v2(
        candidate
    )
    state_machine_v2._validate_transition_replacement(
        current, validated, committed_at
    )
    return validated


def _commit_result(
    *,
    disposition: str,
    candidate_set: dict[str, Any],
    state: dict[str, Any],
    replacement_state: dict[str, Any] | None,
    application_order: list[str],
    invalidated_dependency_ids: list[str],
    durably_committed: bool,
) -> dict[str, Any]:
    commit_identity_body = {
        "commit_ruleset": PROPOSAL_COMMIT_RULESET_V1,
        "conversation_identity": candidate_set["conversation_identity"],
        "candidate_operation_set_id": candidate_set["candidate_operation_set_id"],
        "semantic_reduction_digest": candidate_set["semantic_reduction_digest"],
    }
    commit_identity = "proposal-commit-local-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(commit_identity_body)
    ).hexdigest()
    result = {
        "proposal_commit_runtime_version": (
            PLATFORM_CORE_CONVERSATION_PROPOSAL_COMMIT_RUNTIME_V2
        ),
        "receipt_type": PLATFORM_CORE_PROPOSAL_COMMIT_RECEIPT_SCHEMA_V1,
        "commit_identity": commit_identity,
        "disposition": disposition,
        "candidate_operation_set_id": candidate_set["candidate_operation_set_id"],
        "proposal_id": candidate_set["proposal_id"],
        "interpreter_identity": candidate_set["interpreter_identity"],
        "interpreter_class": candidate_set["interpreter_class"],
        "source_turn_identity": candidate_set["source_turn_identity"],
        "source_turn_digest": candidate_set["source_turn_digest"],
        "source_global_revision": candidate_set["expected_cwm_revision"],
        "source_semantic_revision": candidate_set["expected_semantic_revision"],
        "target_global_revision": candidate_set["expected_cwm_revision"] + 1,
        "target_semantic_revision": candidate_set["expected_semantic_revision"] + 1,
        "committed_global_revision": (
            candidate_set["expected_cwm_revision"] + 1
            if disposition in {COMMITTED, ALREADY_COMMITTED}
            else None
        ),
        "committed_semantic_revision": (
            candidate_set["expected_semantic_revision"] + 1
            if disposition in {COMMITTED, ALREADY_COMMITTED}
            else None
        ),
        "current_global_revision": state["revision"],
        "current_semantic_revision": state["semantic_revision"],
        "application_order": list(application_order),
        "invalidated_dependency_ids": sorted(invalidated_dependency_ids),
        "replacement_prepared": replacement_state is not None,
        "state_changed": durably_committed,
        "semantic_cwm_mutated": durably_committed,
        "conversation_protocol_reduced": replacement_state is not None,
        "state_integrity_checksum": state["integrity_checksum"],
        "replacement_state": deepcopy(replacement_state),
        "state": deepcopy(state),
        "replay_written": False,
        "objective_created": False,
        "objective_commitment_invoked": False,
        "platform_core_invoked": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "execution_invoked": False,
        "receipt_checksum": None,
    }
    checksum_body = deepcopy(result)
    checksum_body.pop("receipt_checksum")
    result["receipt_checksum"] = cwm_v2._checksum(checksum_body)
    return result


def _fail(reason_code: str, message: str) -> None:
    raise ProposalCommitError(reason_code, message)


__all__ = [
    "ALREADY_COMMITTED",
    "COMMITTED",
    "PLATFORM_CORE_CONVERSATION_PROPOSAL_COMMIT_RUNTIME_V2",
    "PLATFORM_CORE_PROPOSAL_COMMIT_RECEIPT_SCHEMA_V1",
    "PREPARED",
    "PROPOSAL_COMMIT_RULESET_V1",
    "ProposalCommitError",
    "commit_proposal_candidate_operations_v2",
    "prepare_proposal_commit_v2",
]
