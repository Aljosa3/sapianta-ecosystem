"""Deterministic Semantic Slot Runtime for isolated Conversation Layer V2.

The runtime is a pure reducer over a validated G59-01 Conversation Working
Memory V2 document.  It creates caller-visible replacement documents but does
not persist them.  Persistence remains owned by the G59-01 atomic store.

This module does not interpret natural language, advance a conversation state
machine, create or commit an Objective, or invoke Platform Core, Replay,
Authorization, Development Governance, capability selection, or Workers.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2


PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2 = (
    "PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2"
)

CREATE = "CREATE"
MERGE = "MERGE"
REFINE = "REFINE"
REPLACE = "REPLACE"
CONFIRM = "CONFIRM"

CREATED = "CREATED"
MERGED_EQUIVALENT = "MERGED_EQUIVALENT"
REFINED = "REFINED"
REPLACED = "REPLACED"
CONFIRMED = "CONFIRMED"
CONFLICT_DETECTED = "CONFLICT_DETECTED"
REJECT_LOWER_EVIDENCE = "REJECT_LOWER_EVIDENCE"
NO_CHANGE = "NO_CHANGE"

_OPERATIONS = frozenset({CREATE, MERGE, REFINE, REPLACE, CONFIRM})
_ACTIVE_INPUT_STATUSES = frozenset(
    {cwm_v2.PROPOSED, cwm_v2.ASSERTED, cwm_v2.CONFIRMED}
)
_CONFIDENCE_RANK = {
    cwm_v2.CONTEXT_DERIVED: 1,
    cwm_v2.DETERMINISTIC_NORMALIZATION: 2,
    cwm_v2.HUMAN_ASSERTED: 3,
    cwm_v2.HUMAN_CONFIRMED: 4,
    cwm_v2.CONFLICTED: 0,
}
_STATUS_RANK = {
    cwm_v2.PROPOSED: 1,
    cwm_v2.ASSERTED: 2,
    cwm_v2.CONFIRMED: 3,
    cwm_v2.STALE: 0,
    cwm_v2.CONFLICTED: 0,
}


def create_semantic_slot_v2(**slot_fields: Any) -> dict[str, Any]:
    """Create and validate one revision-zero canonical semantic slot."""

    return cwm_v2.create_semantic_cwm_slot_v2(**slot_fields)


def validate_semantic_slot_collection_v2(
    semantic_slots: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    conversation_identity: str,
) -> list[dict[str, Any]]:
    """Validate identities, dependencies, cardinality, and acyclic ordering."""

    if not isinstance(semantic_slots, (list, tuple)):
        raise FailClosedRuntimeError("semantic slots must be a collection")
    if len(semantic_slots) > cwm_v2.MAX_SEMANTIC_SLOTS:
        raise FailClosedRuntimeError("semantic slots exceed item bound")
    slots = [
        cwm_v2.validate_semantic_cwm_slot_v2(
            item, conversation_identity=conversation_identity
        )
        for item in semantic_slots
    ]
    slots = sorted(slots, key=cwm_v2._slot_sort_key)
    by_id = {item["slot_id"]: item for item in slots}
    if len(by_id) != len(slots):
        raise FailClosedRuntimeError("semantic slots contain duplicate identity")
    cwm_v2._validate_semantic_cardinality(slots)
    for slot in slots:
        if not set(slot["depends_on"]).issubset(by_id):
            raise FailClosedRuntimeError("semantic slot dependency is absent")
    _require_acyclic_dependencies(by_id)
    return deepcopy(slots)


def semantic_slots_equivalent_v2(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    conversation_identity: str,
) -> bool:
    """Return canonical equivalence; never infer equivalence from prose."""

    left_slot = cwm_v2.validate_semantic_cwm_slot_v2(
        left, conversation_identity=conversation_identity
    )
    right_slot = cwm_v2.validate_semantic_cwm_slot_v2(
        right, conversation_identity=conversation_identity
    )
    _require_same_slot_identity(left_slot, right_slot)
    return left_slot["equivalence_key"] == right_slot["equivalence_key"]


def detect_semantic_slot_conflict_v2(
    active_slot: dict[str, Any],
    incoming_slot: dict[str, Any],
    *,
    conversation_identity: str,
) -> dict[str, Any]:
    """Return a deterministic, bounded comparison without mutating either slot."""

    active, incoming = _validated_pair(
        active_slot, incoming_slot, conversation_identity=conversation_identity
    )
    equivalent = active["equivalence_key"] == incoming["equivalence_key"]
    lower_evidence = (
        _confidence_rank(incoming["confidence_class"])
        < _confidence_rank(active["confidence_class"])
    )
    return {
        "semantic_slot_runtime_version": PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2,
        "slot_id": active["slot_id"],
        "equivalent": equivalent,
        "conflict": not equivalent,
        "incoming_is_lower_evidence": lower_evidence,
        "active_equivalence_key": active["equivalence_key"],
        "incoming_equivalence_key": incoming["equivalence_key"],
        "candidate_value_digests": sorted(
            {
                cwm_v2._checksum(active["canonical_value"]),
                cwm_v2._checksum(incoming["canonical_value"]),
            }
        ),
    }


def evaluate_semantic_slot_completeness_v2(
    slot_id: str,
    semantic_slots: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    conversation_identity: str,
) -> dict[str, Any]:
    """Evaluate one slot against its transitive dependency closure."""

    slots = validate_semantic_slot_collection_v2(
        semantic_slots, conversation_identity=conversation_identity
    )
    by_id = {item["slot_id"]: item for item in slots}
    if slot_id not in by_id:
        raise FailClosedRuntimeError("semantic slot is absent")
    closure = _dependency_closure(slot_id, by_id)
    conflicted = sorted(
        dependency_id
        for dependency_id in closure
        if by_id[dependency_id]["status"] == cwm_v2.CONFLICTED
        or by_id[dependency_id]["completeness"] == cwm_v2.CONFLICTED
    )
    stale = sorted(
        dependency_id
        for dependency_id in closure
        if by_id[dependency_id]["status"] == cwm_v2.STALE
        or by_id[dependency_id]["completeness"] == cwm_v2.STALE
    )
    incomplete = sorted(
        dependency_id
        for dependency_id in closure
        if by_id[dependency_id]["completeness"]
        not in {cwm_v2.COMPLETE, cwm_v2.CONFLICTED, cwm_v2.STALE}
    )
    slot = by_id[slot_id]
    if slot["status"] == cwm_v2.CONFLICTED or conflicted:
        classification = cwm_v2.CONFLICTED
    elif slot["status"] == cwm_v2.STALE or stale:
        classification = cwm_v2.STALE
    elif slot["completeness"] != cwm_v2.COMPLETE or incomplete:
        classification = cwm_v2.PARTIAL
    else:
        classification = cwm_v2.COMPLETE
    return {
        "semantic_slot_runtime_version": PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2,
        "slot_id": slot_id,
        "classification": classification,
        "dependency_closure": sorted(closure),
        "conflicted_dependency_ids": conflicted,
        "stale_dependency_ids": stale,
        "incomplete_dependency_ids": incomplete,
    }


def merge_semantic_slots_v2(
    active_slot: dict[str, Any],
    incoming_slot: dict[str, Any],
    *,
    conversation_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    """Merge equivalent evidence or fail closed into an explicit conflict."""

    active, incoming = _validated_pair(
        active_slot, incoming_slot, conversation_identity=conversation_identity
    )
    _require_active_incoming(incoming)
    if active["equivalence_key"] == incoming["equivalence_key"]:
        merged = _equivalent_merge(
            active,
            incoming,
            observed_at=observed_at,
            allow_blocking_resolution=False,
        )
        if merged == active:
            return _slot_result(NO_CHANGE, active, None)
        merged = cwm_v2.validate_semantic_cwm_slot_v2(
            merged, conversation_identity=conversation_identity
        )
        return _slot_result(MERGED_EQUIVALENT, merged, None)
    if _confidence_rank(incoming["confidence_class"]) < _confidence_rank(
        active["confidence_class"]
    ):
        return _slot_result(
            REJECT_LOWER_EVIDENCE,
            active,
            _conflict_candidates(active, incoming),
        )
    conflicted = _conflicted_revision(active, incoming, observed_at=observed_at)
    conflicted = cwm_v2.validate_semantic_cwm_slot_v2(
        conflicted, conversation_identity=conversation_identity
    )
    return _slot_result(
        CONFLICT_DETECTED,
        conflicted,
        _conflict_candidates(active, incoming),
    )


def revise_semantic_slot_v2(
    active_slot: dict[str, Any],
    incoming_slot: dict[str, Any],
    *,
    conversation_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    """Apply an explicitly classified compatible refinement."""

    active, incoming = _validated_pair(
        active_slot, incoming_slot, conversation_identity=conversation_identity
    )
    _require_active_incoming(incoming)
    if active["equivalence_key"] == incoming["equivalence_key"]:
        return merge_semantic_slots_v2(
            active,
            incoming,
            conversation_identity=conversation_identity,
            observed_at=observed_at,
        )
    if _confidence_rank(incoming["confidence_class"]) < _confidence_rank(
        active["confidence_class"]
    ):
        return _slot_result(
            REJECT_LOWER_EVIDENCE,
            active,
            _conflict_candidates(active, incoming),
        )
    revised = _value_revision(
        active, incoming, observed_at=observed_at, change_kind="REFINED"
    )
    revised = cwm_v2.validate_semantic_cwm_slot_v2(
        revised, conversation_identity=conversation_identity
    )
    return _slot_result(REFINED, revised, None)


def replace_semantic_slot_v2(
    active_slot: dict[str, Any],
    incoming_slot: dict[str, Any],
    *,
    conversation_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    """Apply an explicit human correction while preserving forward history."""

    active, incoming = _validated_pair(
        active_slot, incoming_slot, conversation_identity=conversation_identity
    )
    _require_active_incoming(incoming)
    if incoming["confidence_class"] not in {
        cwm_v2.HUMAN_ASSERTED,
        cwm_v2.HUMAN_CONFIRMED,
    }:
        raise FailClosedRuntimeError(
            "explicit replacement requires human-asserted evidence"
        )
    if active["equivalence_key"] == incoming["equivalence_key"]:
        if active["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}:
            return merge_semantic_slots_v2(
                active,
                incoming,
                conversation_identity=conversation_identity,
                observed_at=observed_at,
            )
        replaced = _value_revision(
            active, incoming, observed_at=observed_at, change_kind="REFINED"
        )
        replaced = cwm_v2.validate_semantic_cwm_slot_v2(
            replaced, conversation_identity=conversation_identity
        )
        return _slot_result(REPLACED, replaced, None)
    replaced = _value_revision(
        active, incoming, observed_at=observed_at, change_kind="REFINED"
    )
    replaced = cwm_v2.validate_semantic_cwm_slot_v2(
        replaced, conversation_identity=conversation_identity
    )
    return _slot_result(REPLACED, replaced, None)


def confirm_semantic_slot_v2(
    active_slot: dict[str, Any],
    confirmation_slot: dict[str, Any],
    *,
    conversation_identity: str,
    observed_at: str,
) -> dict[str, Any]:
    """Confirm only the exact current canonical value."""

    active, confirmation = _validated_pair(
        active_slot,
        confirmation_slot,
        conversation_identity=conversation_identity,
    )
    _require_active_incoming(confirmation)
    if confirmation["confidence_class"] != cwm_v2.HUMAN_CONFIRMED:
        raise FailClosedRuntimeError("confirmation requires human-confirmed evidence")
    if active["equivalence_key"] != confirmation["equivalence_key"]:
        raise FailClosedRuntimeError("confirmation does not bind the active value")
    merged = _equivalent_merge(
        active,
        confirmation,
        observed_at=observed_at,
        allow_blocking_resolution=True,
    )
    merged["status"] = cwm_v2.CONFIRMED
    merged["confidence_class"] = cwm_v2.HUMAN_CONFIRMED
    merged["completeness"] = cwm_v2.COMPLETE
    if merged == active:
        return _slot_result(NO_CHANGE, active, None)
    if merged["slot_revision"] == active["slot_revision"]:
        merged = _append_revision(
            active,
            merged,
            observed_at=observed_at,
            change_kind="CONFIRMED",
        )
    else:
        merged["history"][-1]["change_kind"] = "CONFIRMED"
    validated = cwm_v2.validate_semantic_cwm_slot_v2(
        merged, conversation_identity=conversation_identity
    )
    return _slot_result(CONFIRMED, validated, None)


def prepare_semantic_slot_state_update_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    operation: str,
    incoming_slot: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    """Prepare one G59-01-compatible semantic replacement without persistence."""

    current = cwm_v2.validate_conversation_working_memory_state_v2(state)
    if current["revision"] != expected_revision:
        raise FailClosedRuntimeError("semantic update revision does not match")
    if current["migration_metadata"]["migration_status"] != cwm_v2.NATIVE_V2:
        raise FailClosedRuntimeError("legacy semantic review is not implemented")
    if operation not in _OPERATIONS:
        raise FailClosedRuntimeError("semantic slot operation is invalid")
    observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    if cwm_v2._parse_timestamp(observed, "observed_at") < cwm_v2._parse_timestamp(
        current["envelope"]["updated_at"], "updated_at"
    ):
        raise FailClosedRuntimeError("semantic update time precedes current state")
    conversation = current["envelope"]["conversation_identity"]
    incoming = cwm_v2.validate_semantic_cwm_slot_v2(
        incoming_slot, conversation_identity=conversation
    )
    slots = validate_semantic_slot_collection_v2(
        current["semantic_memory"]["semantic_slots"],
        conversation_identity=conversation,
    )
    by_id = {item["slot_id"]: item for item in slots}
    active = by_id.get(incoming["slot_id"])

    if operation == CREATE:
        if active is not None:
            raise FailClosedRuntimeError("semantic slot already exists")
        _require_active_incoming(incoming)
        changed_slot = incoming
        disposition = CREATED
        conflict_candidates = None
    else:
        if active is None:
            raise FailClosedRuntimeError("semantic slot is absent")
        if operation == MERGE:
            slot_result = merge_semantic_slots_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=observed,
            )
        elif operation == REFINE:
            slot_result = revise_semantic_slot_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=observed,
            )
        elif operation == REPLACE:
            slot_result = replace_semantic_slot_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=observed,
            )
        else:
            slot_result = confirm_semantic_slot_v2(
                active,
                incoming,
                conversation_identity=conversation,
                observed_at=observed,
            )
        disposition = slot_result["disposition"]
        changed_slot = slot_result["slot"]
        conflict_candidates = slot_result["conflict_candidates"]

    if disposition in {NO_CHANGE, REJECT_LOWER_EVIDENCE}:
        return _state_result(
            disposition=disposition,
            active_slot=active,
            replacement_state=None,
            invalidated_dependency_ids=(),
            conflict_candidates=conflict_candidates,
        )

    by_id[incoming["slot_id"]] = changed_slot
    validated_before_invalidation = validate_semantic_slot_collection_v2(
        list(by_id.values()), conversation_identity=conversation
    )
    by_id = {item["slot_id"]: item for item in validated_before_invalidation}
    equivalence_changed = active is not None and (
        active["equivalence_key"] != changed_slot["equivalence_key"]
    )
    status_became_blocking = active is not None and (
        active["status"] not in {cwm_v2.CONFLICTED, cwm_v2.STALE}
        and changed_slot["status"] in {cwm_v2.CONFLICTED, cwm_v2.STALE}
    )
    invalidated: list[str] = []
    if equivalence_changed or status_became_blocking:
        by_id, invalidated = _invalidate_dependents(
            by_id,
            changed_slot["slot_id"],
            observed_at=observed,
            conversation_identity=conversation,
        )
    canonical_slots = validate_semantic_slot_collection_v2(
        list(by_id.values()), conversation_identity=conversation
    )
    replacement = _prepare_state_replacement(
        current, semantic_slots=canonical_slots, observed_at=observed
    )
    return _state_result(
        disposition=disposition,
        active_slot=changed_slot,
        replacement_state=replacement,
        invalidated_dependency_ids=invalidated,
        conflict_candidates=conflict_candidates,
    )


def _validated_pair(
    active_slot: dict[str, Any],
    incoming_slot: dict[str, Any],
    *,
    conversation_identity: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    active = cwm_v2.validate_semantic_cwm_slot_v2(
        active_slot, conversation_identity=conversation_identity
    )
    incoming = cwm_v2.validate_semantic_cwm_slot_v2(
        incoming_slot, conversation_identity=conversation_identity
    )
    _require_same_slot_identity(active, incoming)
    return active, incoming


def _require_same_slot_identity(
    active: dict[str, Any], incoming: dict[str, Any]
) -> None:
    if active["slot_id"] != incoming["slot_id"]:
        raise FailClosedRuntimeError("semantic slot identities differ")
    for field in ("slot_class", "cardinality_key", "value_kind", "materiality"):
        if active[field] != incoming[field]:
            raise FailClosedRuntimeError("semantic slot immutable metadata differs")


def _require_active_incoming(incoming: dict[str, Any]) -> None:
    if incoming["status"] not in _ACTIVE_INPUT_STATUSES:
        raise FailClosedRuntimeError("incoming semantic slot status is not active")
    if incoming["slot_revision"] != 0:
        raise FailClosedRuntimeError("incoming semantic proposal must be revision zero")


def _confidence_rank(value: str) -> int:
    try:
        return _CONFIDENCE_RANK[value]
    except KeyError as exc:
        raise FailClosedRuntimeError("semantic confidence is invalid") from exc


def _equivalent_merge(
    active: dict[str, Any],
    incoming: dict[str, Any],
    *,
    observed_at: str,
    allow_blocking_resolution: bool,
) -> dict[str, Any]:
    candidate = deepcopy(active)
    candidate["provenance"] = _merge_provenance(
        active["provenance"], incoming["provenance"]
    )
    candidate["depends_on"] = sorted(
        set(active["depends_on"]).union(incoming["depends_on"])
    )
    incoming_priority = (
        _confidence_rank(incoming["confidence_class"]),
        _STATUS_RANK[incoming["status"]],
    )
    active_priority = (
        _confidence_rank(active["confidence_class"]),
        _STATUS_RANK[active["status"]],
    )
    blocking = active["status"] in {cwm_v2.CONFLICTED, cwm_v2.STALE}
    if incoming_priority > active_priority and (
        allow_blocking_resolution or not blocking
    ):
        candidate["surface_value"] = incoming["surface_value"]
        candidate["status"] = incoming["status"]
        candidate["completeness"] = incoming["completeness"]
        candidate["confidence_class"] = incoming["confidence_class"]
    if candidate == active:
        return active
    if candidate["status"] == cwm_v2.CONFLICTED:
        change_kind = "CONFLICTED"
    elif candidate["status"] == cwm_v2.STALE:
        change_kind = "STALE"
    elif candidate["status"] == cwm_v2.CONFIRMED:
        change_kind = "CONFIRMED"
    else:
        change_kind = "REFINED"
    return _append_revision(
        active, candidate, observed_at=observed_at, change_kind=change_kind
    )


def _value_revision(
    active: dict[str, Any],
    incoming: dict[str, Any],
    *,
    observed_at: str,
    change_kind: str,
) -> dict[str, Any]:
    candidate = deepcopy(active)
    for field in (
        "slot_role",
        "surface_value",
        "canonical_value",
        "equivalence_key",
        "status",
        "completeness",
        "confidence_class",
    ):
        candidate[field] = deepcopy(incoming[field])
    candidate["provenance"] = _merge_provenance(
        active["provenance"], incoming["provenance"]
    )
    candidate["depends_on"] = sorted(incoming["depends_on"])
    return _append_revision(
        active, candidate, observed_at=observed_at, change_kind=change_kind
    )


def _conflicted_revision(
    active: dict[str, Any], incoming: dict[str, Any], *, observed_at: str
) -> dict[str, Any]:
    candidate = deepcopy(active)
    candidate["status"] = cwm_v2.CONFLICTED
    candidate["completeness"] = cwm_v2.CONFLICTED
    candidate["confidence_class"] = cwm_v2.CONFLICTED
    candidate["provenance"] = _merge_provenance(
        active["provenance"], incoming["provenance"]
    )
    return _append_revision(
        active, candidate, observed_at=observed_at, change_kind="CONFLICTED"
    )


def _append_revision(
    active: dict[str, Any],
    candidate: dict[str, Any],
    *,
    observed_at: str,
    change_kind: str,
) -> dict[str, Any]:
    updated = deepcopy(candidate)
    updated["slot_revision"] = active["slot_revision"] + 1
    updated["history"] = deepcopy(active["history"])
    updated["history"].append(
        {
            "slot_revision": updated["slot_revision"],
            "changed_at": cwm_v2._canonical_timestamp(
                observed_at, "observed_at"
            ),
            "change_kind": change_kind,
            "prior_value_digest": cwm_v2._checksum(
                active["canonical_value"]
            ),
            "resulting_value_digest": cwm_v2._checksum(
                updated["canonical_value"]
            ),
        }
    )
    return updated


def _merge_provenance(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    unique: dict[bytes, dict[str, Any]] = {}
    for item in [*left, *right]:
        unique[cwm_v2._canonical_bytes(item)] = deepcopy(item)
    merged = [unique[key] for key in sorted(unique)]
    if len(merged) > cwm_v2.MAX_SLOT_PROVENANCE_ENTRIES:
        raise FailClosedRuntimeError("semantic slot provenance exceeds item bound")
    return merged


def _conflict_candidates(
    active: dict[str, Any], incoming: dict[str, Any]
) -> list[dict[str, Any]]:
    candidates = [
        {
            "candidate_kind": "ACTIVE",
            "equivalence_key": active["equivalence_key"],
            "surface_value": active["surface_value"],
            "canonical_value": active["canonical_value"],
            "confidence_class": active["confidence_class"],
        },
        {
            "candidate_kind": "INCOMING",
            "equivalence_key": incoming["equivalence_key"],
            "surface_value": incoming["surface_value"],
            "canonical_value": incoming["canonical_value"],
            "confidence_class": incoming["confidence_class"],
        },
    ]
    return sorted(candidates, key=lambda item: item["candidate_kind"])


def _invalidate_dependents(
    by_id: dict[str, dict[str, Any]],
    changed_slot_id: str,
    *,
    observed_at: str,
    conversation_identity: str,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    updated = deepcopy(by_id)
    pending = [changed_slot_id]
    invalidated: list[str] = []
    processed: set[str] = set()
    while pending:
        dependency_id = pending.pop(0)
        if dependency_id in processed:
            continue
        processed.add(dependency_id)
        direct = sorted(
            slot_id
            for slot_id, slot in updated.items()
            if dependency_id in slot["depends_on"]
            and slot_id not in invalidated
        )
        for slot_id in direct:
            slot = updated[slot_id]
            if slot["status"] != cwm_v2.STALE:
                candidate = deepcopy(slot)
                candidate["status"] = cwm_v2.STALE
                candidate["completeness"] = cwm_v2.STALE
                candidate = _append_revision(
                    slot,
                    candidate,
                    observed_at=observed_at,
                    change_kind="STALE",
                )
                updated[slot_id] = cwm_v2.validate_semantic_cwm_slot_v2(
                    candidate, conversation_identity=conversation_identity
                )
                invalidated.append(slot_id)
            pending.append(slot_id)
    return updated, invalidated


def _dependency_closure(
    slot_id: str, by_id: dict[str, dict[str, Any]]
) -> set[str]:
    closure: set[str] = set()
    pending = list(by_id[slot_id]["depends_on"])
    while pending:
        dependency_id = pending.pop(0)
        if dependency_id in closure:
            continue
        closure.add(dependency_id)
        pending.extend(by_id[dependency_id]["depends_on"])
    return closure


def _require_acyclic_dependencies(
    by_id: dict[str, dict[str, Any]]
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(slot_id: str) -> None:
        if slot_id in visiting:
            raise FailClosedRuntimeError("semantic slot dependency cycle detected")
        if slot_id in visited:
            return
        visiting.add(slot_id)
        for dependency_id in by_id[slot_id]["depends_on"]:
            visit(dependency_id)
        visiting.remove(slot_id)
        visited.add(slot_id)

    for slot_id in sorted(by_id):
        visit(slot_id)


def _prepare_state_replacement(
    current: dict[str, Any],
    *,
    semantic_slots: list[dict[str, Any]],
    observed_at: str,
) -> dict[str, Any]:
    candidate = deepcopy(current)
    candidate["revision"] += 1
    candidate["envelope_revision"] += 1
    candidate["semantic_revision"] += 1
    candidate["envelope"]["updated_at"] = observed_at
    candidate["semantic_memory"]["semantic_slots"] = semantic_slots
    candidate["envelope"]["semantic_memory_binding"] = {
        "semantic_memory_type": cwm_v2.PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "global_revision": candidate["revision"],
        "semantic_revision": candidate["semantic_revision"],
        "semantic_memory_digest": cwm_v2._checksum(candidate["semantic_memory"]),
    }
    candidate = cwm_v2._with_integrity(candidate)
    return cwm_v2.validate_conversation_working_memory_state_v2(candidate)


def _slot_result(
    disposition: str,
    slot: dict[str, Any],
    conflict_candidates: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "semantic_slot_runtime_version": PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2,
        "disposition": disposition,
        "slot": deepcopy(slot),
        "conflict_candidates": deepcopy(conflict_candidates),
    }


def _state_result(
    *,
    disposition: str,
    active_slot: dict[str, Any] | None,
    replacement_state: dict[str, Any] | None,
    invalidated_dependency_ids: list[str] | tuple[str, ...],
    conflict_candidates: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "semantic_slot_runtime_version": PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2,
        "disposition": disposition,
        "state_changed": replacement_state is not None,
        "active_slot": deepcopy(active_slot),
        "invalidated_dependency_ids": sorted(invalidated_dependency_ids),
        "conflict_candidates": deepcopy(conflict_candidates),
        "replacement_state": deepcopy(replacement_state),
        "objective_created": False,
        "execution_invoked": False,
    }


__all__ = [
    "CONFIRM",
    "CONFIRMED",
    "CONFLICT_DETECTED",
    "CREATE",
    "CREATED",
    "MERGE",
    "MERGED_EQUIVALENT",
    "NO_CHANGE",
    "PLATFORM_CORE_SEMANTIC_SLOT_RUNTIME_V2",
    "REFINE",
    "REFINED",
    "REJECT_LOWER_EVIDENCE",
    "REPLACE",
    "REPLACED",
    "confirm_semantic_slot_v2",
    "create_semantic_slot_v2",
    "detect_semantic_slot_conflict_v2",
    "evaluate_semantic_slot_completeness_v2",
    "merge_semantic_slots_v2",
    "prepare_semantic_slot_state_update_v2",
    "replace_semantic_slot_v2",
    "revise_semantic_slot_v2",
    "semantic_slots_equivalent_v2",
    "validate_semantic_slot_collection_v2",
]
