"""Isolated Objective Commitment Runtime for Conversation Layer V2.

The runtime binds one explicit local human commit action to one exact G59-06
readiness report and immutable candidate snapshot.  It persists a local
commitment record and reconciles CWM cleanup.  It does not admit the record to
Platform Core or invoke Development Governance, capability selection,
Approval, Authorization, Worker, Completion, Replay, AiCLI, HIR, or providers.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as state_machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2


PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2 = (
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2"
)
PLATFORM_CORE_CANDIDATE_OBJECTIVE_SNAPSHOT_SCHEMA_V1 = (
    "PLATFORM_CORE_CANDIDATE_OBJECTIVE_SNAPSHOT_SCHEMA_V1"
)
PLATFORM_CORE_OBJECTIVE_COMMITMENT_REQUEST_SCHEMA_V1 = (
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_REQUEST_SCHEMA_V1"
)
PLATFORM_CORE_OBJECTIVE_COMMITMENT_RECORD_SCHEMA_V1 = (
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_RECORD_SCHEMA_V1"
)
PLATFORM_CORE_OBJECTIVE_COMMITMENT_INTENT_SCHEMA_V1 = (
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_INTENT_SCHEMA_V1"
)
OBJECTIVE_COMMITMENT_RULESET_V1 = "OBJECTIVE_COMMITMENT_RULESET_V1"
OBJECTIVE_SNAPSHOT_RULESET_V1 = "OBJECTIVE_SNAPSHOT_RULESET_V1"

COMMIT_EXACT_CANDIDATE = "COMMIT_EXACT_CANDIDATE"
IMMUTABLY_COMMITTED = "IMMUTABLY_COMMITTED"
COMMITMENT_REQUESTED = "COMMITMENT_REQUESTED"

COMMITTED = "COMMITTED"
ALREADY_COMMITTED = "ALREADY_COMMITTED"
CLEANUP_PENDING = "CLEANUP_PENDING"
RECOVERED_COMMITTED = "RECOVERED_COMMITTED"
RECOVERED_CLEANUP_PENDING = "RECOVERED_CLEANUP_PENDING"

_STORE_DIRECTORY = "_objective_commitments_v2"
_EPISODE_DIRECTORY = "episodes"
_RECORD_DIRECTORY = "records"
_MAX_IMMUTABLE_BYTES = 524_288

_SNAPSHOT_FIELDS = frozenset(
    {
        "snapshot_type",
        "snapshot_ruleset_version",
        "canonical_objective",
        "subject",
        "requested_action",
        "expected_outcome",
        "secondary_outcomes",
        "work_type",
        "mutation_boundary",
        "governing_qualifiers",
        "semantic_references",
        "output_constraints",
        "acceptance_criteria",
        "explicit_non_goals",
        "resolved_ambiguity_state",
        "source_semantic_slots",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "global_revision",
        "envelope_revision",
        "semantic_revision",
        "state_machine_state",
        "readiness_evidence",
        "exploratory_transcript_included",
        "hidden_reasoning_included",
        "confidence_history_included",
        "rejected_draft_history_included",
        "interpreter_authority",
        "external_llm_authority",
        "execution_authority",
    }
)

_CANONICAL_OBJECTIVE_FIELDS = frozenset(
    {"requested_action", "subject", "expected_outcome", "work_type"}
)
_MUTATION_BOUNDARY_FIELDS = frozenset(
    {"preservation_constraints", "scope_references"}
)
_AMBIGUITY_FIELDS = frozenset(
    {
        "material_ambiguity_resolved",
        "pending_clarification",
        "material_conflict_slot_ids",
        "material_stale_slot_ids",
        "incomplete_dependency_slot_ids",
    }
)
_READINESS_EVIDENCE_FIELDS = frozenset(
    {
        "readiness_report_identity",
        "readiness_report_digest",
        "readiness_report_checksum",
        "readiness_ruleset_version",
        "evaluated_at",
    }
)
_SOURCE_SLOT_FIELDS = frozenset(
    {
        "slot_id",
        "slot_revision",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "value_digest",
    }
)
_SEMANTIC_VALUE_FIELDS = frozenset(
    {
        "slot_id",
        "slot_revision",
        "slot_role",
        "cardinality_key",
        "canonical_value",
        "value_digest",
    }
)

_REQUEST_FIELDS = frozenset(
    {
        "request_type",
        "request_runtime_version",
        "request_ruleset_version",
        "request_id",
        "commitment_identity",
        "commitment_idempotency_key",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "global_revision",
        "envelope_revision",
        "semantic_revision",
        "state_machine_state",
        "normalization_ruleset_version",
        "candidate_objective_snapshot",
        "candidate_objective_digest",
        "readiness_report",
        "readiness_report_identity",
        "readiness_report_digest",
        "readiness_report_checksum",
        "source_semantic_slot_revisions",
        "human_commitment_action",
        "requested_at",
        "constitutional_authority",
        "execution_requested",
        "platform_core_admission_requested",
        "authorization_requested",
        "worker_requested",
        "replay_requested",
        "integrity_checksum",
    }
)
_HUMAN_ACTION_FIELDS = frozenset(
    {
        "control_act",
        "explicit_command",
        "candidate_objective_digest",
        "human_participant_digest",
        "participant_binding_digest",
    }
)
_SLOT_REVISION_FIELDS = frozenset({"slot_id", "slot_revision"})

_RECORD_FIELDS = frozenset(
    {
        "record_type",
        "record_runtime_version",
        "record_ruleset_version",
        "record_status",
        "commitment_identity",
        "commitment_idempotency_key",
        "source_request_id",
        "source_request_digest",
        "candidate_objective_snapshot",
        "candidate_objective_digest",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "global_revision",
        "envelope_revision",
        "semantic_revision",
        "state_machine_state",
        "readiness_report_identity",
        "readiness_report_digest",
        "readiness_report_checksum",
        "source_semantic_slot_revisions",
        "human_commitment_evidence",
        "committed_at",
        "constitutional_artifact",
        "constitutional_authority",
        "pipeline_objective_created",
        "execution_authority",
        "platform_core_admitted",
        "development_governance_admitted",
        "capability_selected",
        "approval_granted",
        "authorization_granted",
        "worker_dispatched",
        "completion_recorded",
        "replay_written",
        "aicli_invoked",
        "hir_invoked",
        "integrity_checksum",
    }
)

_INTENT_FIELDS = frozenset(
    {
        "intent_type",
        "intent_runtime_version",
        "intent_status",
        "intent_identity",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "commitment_identity",
        "request_digest",
        "record_digest",
        "commitment_request",
        "commitment_record",
        "created_at",
        "integrity_checksum",
    }
)

_RESULT_FIELDS_FALSE = (
    "constitutional_authority",
    "execution_authority",
    "platform_core_admitted",
    "development_governance_admitted",
    "capability_selected",
    "approval_granted",
    "authorization_granted",
    "worker_dispatched",
    "completion_recorded",
    "replay_written",
)


class ObjectiveCommitmentError(FailClosedRuntimeError):
    """Fail-closed Objective Commitment failure with a stable reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def build_candidate_objective_snapshot_v2(
    state: dict[str, Any],
    *,
    readiness_report: dict[str, Any],
) -> dict[str, Any]:
    """Build the exact bounded Objective candidate from one ready revision."""

    current, readiness = _validated_ready_state(state, readiness_report)
    slots = current["semantic_memory"]["semantic_slots"]
    action = _single_slot(slots, cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY)
    subject = _single_slot(slots, cwm_v2.OPERATIVE_SUBJECT, cwm_v2.PRIMARY)
    primary_outcome = _single_slot(slots, cwm_v2.DESIRED_OUTCOME, cwm_v2.PRIMARY)
    work_type = _single_slot(slots, cwm_v2.WORK_TYPE, None)
    qualifiers = sorted(
        [
            _semantic_value(slot)
            for slot in slots
            if slot["slot_class"] == cwm_v2.GOVERNING_QUALIFIER
        ],
        key=lambda item: item["slot_id"],
    )
    references = sorted(
        [
            _semantic_value(slot)
            for slot in slots
            if slot["slot_class"] == cwm_v2.SEMANTIC_REFERENCE
        ],
        key=lambda item: item["slot_id"],
    )
    secondary_outcomes = [
        slot["canonical_value"]
        for slot in slots
        if slot["slot_class"] == cwm_v2.DESIRED_OUTCOME
        and slot["slot_role"] == cwm_v2.SECONDARY
    ]
    preservation = [
        item["canonical_value"]
        for item in qualifiers
        if item["slot_role"] == cwm_v2.PRESERVATION
    ]
    scope_references = [
        item["canonical_value"]
        for item in references
        if item["slot_role"] == cwm_v2.SCOPE
    ]
    output_constraints = [
        item["canonical_value"]
        for item in qualifiers
        if item["slot_role"] == cwm_v2.OUTPUT
    ]
    acceptance_criteria = [
        item["canonical_value"]
        for item in qualifiers
        if item["slot_role"] == cwm_v2.ACCEPTANCE
    ]
    explicit_non_goals = [
        item["canonical_value"]
        for item in qualifiers
        if item["slot_role"] == cwm_v2.PRESERVATION
        and item["cardinality_key"].startswith("non-goal:")
    ]
    blockers = readiness["blocking_evidence"]
    snapshot = {
        "snapshot_type": PLATFORM_CORE_CANDIDATE_OBJECTIVE_SNAPSHOT_SCHEMA_V1,
        "snapshot_ruleset_version": OBJECTIVE_SNAPSHOT_RULESET_V1,
        "canonical_objective": {
            "requested_action": action["canonical_value"],
            "subject": subject["canonical_value"],
            "expected_outcome": primary_outcome["canonical_value"],
            "work_type": work_type["canonical_value"],
        },
        "subject": subject["canonical_value"],
        "requested_action": action["canonical_value"],
        "expected_outcome": primary_outcome["canonical_value"],
        "secondary_outcomes": secondary_outcomes,
        "work_type": work_type["canonical_value"],
        "mutation_boundary": {
            "preservation_constraints": preservation,
            "scope_references": scope_references,
        },
        "governing_qualifiers": qualifiers,
        "semantic_references": references,
        "output_constraints": output_constraints,
        "acceptance_criteria": acceptance_criteria,
        "explicit_non_goals": explicit_non_goals,
        "resolved_ambiguity_state": {
            "material_ambiguity_resolved": True,
            "pending_clarification": False,
            "material_conflict_slot_ids": deepcopy(blockers["material_conflicted"]),
            "material_stale_slot_ids": deepcopy(blockers["material_stale"]),
            "incomplete_dependency_slot_ids": deepcopy(blockers["unresolved_dependencies"]),
        },
        "source_semantic_slots": sorted(
            [_source_slot(slot) for slot in slots],
            key=lambda item: item["slot_id"],
        ),
        "conversation_identity": current["envelope"]["conversation_identity"],
        "workspace_identity_hash": current["envelope"]["workspace_identity_hash"],
        "session_identity_hash": current["envelope"]["session_identity_hash"],
        "global_revision": current["revision"],
        "envelope_revision": current["envelope_revision"],
        "semantic_revision": current["semantic_revision"],
        "state_machine_state": state_machine_v2.OBJECTIVE_READY,
        "readiness_evidence": {
            "readiness_report_identity": readiness["readiness_report_id"],
            "readiness_report_digest": cwm_v2._checksum(readiness),
            "readiness_report_checksum": readiness["report_checksum"],
            "readiness_ruleset_version": readiness["readiness_ruleset_version"],
            "evaluated_at": readiness["evaluated_at"],
        },
        "exploratory_transcript_included": False,
        "hidden_reasoning_included": False,
        "confidence_history_included": False,
        "rejected_draft_history_included": False,
        "interpreter_authority": False,
        "external_llm_authority": False,
        "execution_authority": False,
    }
    return validate_candidate_objective_snapshot_v2(snapshot)


def compute_candidate_objective_digest_v2(
    candidate_objective_snapshot: dict[str, Any],
) -> str:
    """Return the canonical digest of one validated candidate snapshot."""

    snapshot = validate_candidate_objective_snapshot_v2(
        candidate_objective_snapshot
    )
    return cwm_v2._checksum(snapshot)


def create_objective_commitment_request_v2(
    state: dict[str, Any],
    *,
    readiness_report: dict[str, Any],
    explicit_commit_action: str,
    human_participant_digest: str,
    requested_at: str,
) -> dict[str, Any]:
    """Create one exact explicit human commitment request; prose is invalid."""

    current, readiness = _validated_ready_state(state, readiness_report)
    requested = cwm_v2._canonical_timestamp(requested_at, "requested_at")
    if requested != readiness["evaluated_at"]:
        _fail("STALE_READINESS", "commitment time is not the readiness time")
    snapshot = build_candidate_objective_snapshot_v2(
        current, readiness_report=readiness
    )
    candidate_digest = compute_candidate_objective_digest_v2(snapshot)
    _validate_explicit_commit_action(explicit_commit_action, candidate_digest)
    participant, participant_digest = _bound_human_participant(
        current, human_participant_digest
    )
    del participant
    slot_revisions = [
        {"slot_id": item["slot_id"], "slot_revision": item["slot_revision"]}
        for item in snapshot["source_semantic_slots"]
    ]
    action = {
        "control_act": COMMIT_EXACT_CANDIDATE,
        "explicit_command": explicit_commit_action,
        "candidate_objective_digest": candidate_digest,
        "human_participant_digest": participant_digest,
        "participant_binding_digest": readiness["participant_binding_digest"],
    }
    identity_body = _commitment_identity_body(
        conversation_identity=snapshot["conversation_identity"],
        workspace_identity_hash=snapshot["workspace_identity_hash"],
        session_identity_hash=snapshot["session_identity_hash"],
        global_revision=snapshot["global_revision"],
        envelope_revision=snapshot["envelope_revision"],
        semantic_revision=snapshot["semantic_revision"],
        candidate_objective_digest=candidate_digest,
        readiness_report_identity=readiness["readiness_report_id"],
        readiness_report_digest=cwm_v2._checksum(readiness),
        source_semantic_slot_revisions=slot_revisions,
        human_commitment_action=action,
        requested_at=requested,
    )
    commitment_key = "objective-commitment-key-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(identity_body)
    ).hexdigest()
    commitment_identity = "objective-commitment-local-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(
            {
                "identity_body": identity_body,
                "commitment_idempotency_key": commitment_key,
            }
        )
    ).hexdigest()
    request = {
        "request_type": PLATFORM_CORE_OBJECTIVE_COMMITMENT_REQUEST_SCHEMA_V1,
        "request_runtime_version": PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2,
        "request_ruleset_version": OBJECTIVE_COMMITMENT_RULESET_V1,
        "request_id": None,
        "commitment_identity": commitment_identity,
        "commitment_idempotency_key": commitment_key,
        "conversation_identity": snapshot["conversation_identity"],
        "workspace_identity_hash": snapshot["workspace_identity_hash"],
        "session_identity_hash": snapshot["session_identity_hash"],
        "global_revision": snapshot["global_revision"],
        "envelope_revision": snapshot["envelope_revision"],
        "semantic_revision": snapshot["semantic_revision"],
        "state_machine_state": state_machine_v2.OBJECTIVE_READY,
        "normalization_ruleset_version": current["semantic_memory"]["normalization_ruleset_version"],
        "candidate_objective_snapshot": snapshot,
        "candidate_objective_digest": candidate_digest,
        "readiness_report": readiness,
        "readiness_report_identity": readiness["readiness_report_id"],
        "readiness_report_digest": cwm_v2._checksum(readiness),
        "readiness_report_checksum": readiness["report_checksum"],
        "source_semantic_slot_revisions": slot_revisions,
        "human_commitment_action": action,
        "requested_at": requested,
        "constitutional_authority": False,
        "execution_requested": False,
        "platform_core_admission_requested": False,
        "authorization_requested": False,
        "worker_requested": False,
        "replay_requested": False,
        "integrity_checksum": None,
    }
    request_identity_body = deepcopy(request)
    request_identity_body["request_id"] = None
    request_identity_body["integrity_checksum"] = None
    request["request_id"] = "objective-commitment-request-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(request_identity_body)
    ).hexdigest()
    request["integrity_checksum"] = _integrity(request)
    return validate_objective_commitment_request_v2(request)


def validate_candidate_objective_snapshot_v2(
    candidate_objective_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Validate the closed candidate snapshot without granting authority."""

    snapshot = _closed(candidate_objective_snapshot, _SNAPSHOT_FIELDS, "candidate snapshot")
    if snapshot["snapshot_type"] != PLATFORM_CORE_CANDIDATE_OBJECTIVE_SNAPSHOT_SCHEMA_V1 or snapshot["snapshot_ruleset_version"] != OBJECTIVE_SNAPSHOT_RULESET_V1:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "candidate snapshot version is invalid")
    canonical = _closed(snapshot["canonical_objective"], _CANONICAL_OBJECTIVE_FIELDS, "canonical objective")
    for field in ("requested_action", "subject", "expected_outcome", "work_type"):
        _text(canonical[field], field)
    if canonical != {
        "requested_action": snapshot["requested_action"],
        "subject": snapshot["subject"],
        "expected_outcome": snapshot["expected_outcome"],
        "work_type": snapshot["work_type"],
    }:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "canonical objective is inconsistent")
    if snapshot["work_type"] not in cwm_v2.CANONICAL_GOVERNED_WORK_TYPES:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "work type is invalid")
    for field in ("secondary_outcomes", "output_constraints", "acceptance_criteria", "explicit_non_goals"):
        _canonical_text_list(snapshot[field], field)
    qualifiers = _semantic_values(snapshot["governing_qualifiers"], cwm_v2.GOVERNING_QUALIFIER)
    references = _semantic_values(snapshot["semantic_references"], cwm_v2.SEMANTIC_REFERENCE)
    boundary = _closed(snapshot["mutation_boundary"], _MUTATION_BOUNDARY_FIELDS, "mutation boundary")
    _canonical_text_list(boundary["preservation_constraints"], "preservation constraints")
    _canonical_text_list(boundary["scope_references"], "scope references")
    if boundary["preservation_constraints"] != [item["canonical_value"] for item in qualifiers if item["slot_role"] == cwm_v2.PRESERVATION]:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "preservation boundary is invalid")
    if boundary["scope_references"] != [item["canonical_value"] for item in references if item["slot_role"] == cwm_v2.SCOPE]:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "scope boundary is invalid")
    if snapshot["output_constraints"] != [item["canonical_value"] for item in qualifiers if item["slot_role"] == cwm_v2.OUTPUT]:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "output constraints are invalid")
    if snapshot["acceptance_criteria"] != [item["canonical_value"] for item in qualifiers if item["slot_role"] == cwm_v2.ACCEPTANCE]:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "acceptance criteria are invalid")
    expected_non_goals = [item["canonical_value"] for item in qualifiers if item["slot_role"] == cwm_v2.PRESERVATION and item["cardinality_key"].startswith("non-goal:")]
    if snapshot["explicit_non_goals"] != expected_non_goals:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "explicit non-goals are invalid")
    ambiguity = _closed(snapshot["resolved_ambiguity_state"], _AMBIGUITY_FIELDS, "ambiguity state")
    if ambiguity["material_ambiguity_resolved"] is not True or ambiguity["pending_clarification"] is not False:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "material ambiguity is unresolved")
    for field in ("material_conflict_slot_ids", "material_stale_slot_ids", "incomplete_dependency_slot_ids"):
        if _slot_ids(ambiguity[field], field):
            _fail("CANDIDATE_SNAPSHOT_INVALID", "candidate contains unresolved blockers")
    source_slots = _source_slots(snapshot["source_semantic_slots"], snapshot["conversation_identity"])
    if not source_slots:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "candidate source slots are absent")
    _identity(snapshot["conversation_identity"], "conversation identity", "conversation-local-sha256:")
    _digest(snapshot["workspace_identity_hash"], "workspace identity hash", "sha256:")
    _digest(snapshot["session_identity_hash"], "session identity hash", "sha256:")
    for field in ("global_revision", "envelope_revision", "semantic_revision"):
        _nonnegative(snapshot[field], field)
    if any(
        item["slot_revision"] > snapshot["semantic_revision"]
        for item in source_slots
    ):
        _fail("CANDIDATE_SNAPSHOT_INVALID", "source slot revision is stale")
    _validate_snapshot_source_bindings(
        snapshot,
        source_slots=source_slots,
        qualifiers=qualifiers,
        references=references,
    )
    if snapshot["state_machine_state"] != state_machine_v2.OBJECTIVE_READY:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "candidate state is not Objective ready")
    evidence = _closed(snapshot["readiness_evidence"], _READINESS_EVIDENCE_FIELDS, "readiness evidence")
    _identity(evidence["readiness_report_identity"], "readiness identity", "objective-readiness-local-sha256:")
    _digest(evidence["readiness_report_digest"], "readiness digest", "sha256:")
    _digest(evidence["readiness_report_checksum"], "readiness checksum", "sha256:")
    if evidence["readiness_ruleset_version"] != readiness_v2.OBJECTIVE_READINESS_RULESET_V1:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "readiness ruleset is invalid")
    canonical_time = cwm_v2._canonical_timestamp(evidence["evaluated_at"], "evaluated_at")
    if evidence["evaluated_at"] != canonical_time:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "readiness time is not canonical")
    for field in ("exploratory_transcript_included", "hidden_reasoning_included", "confidence_history_included", "rejected_draft_history_included", "interpreter_authority", "external_llm_authority", "execution_authority"):
        if snapshot[field] is not False:
            _fail("CANDIDATE_SNAPSHOT_INVALID", "candidate grants forbidden authority")
    return snapshot


def validate_objective_commitment_request_v2(
    commitment_request: dict[str, Any],
) -> dict[str, Any]:
    """Validate one closed explicit commitment request and all bindings."""

    request = _closed(commitment_request, _REQUEST_FIELDS, "commitment request")
    if request["request_type"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_REQUEST_SCHEMA_V1 or request["request_runtime_version"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2 or request["request_ruleset_version"] != OBJECTIVE_COMMITMENT_RULESET_V1:
        _fail("COMMITMENT_REQUEST_INVALID", "commitment request version is invalid")
    for field in ("constitutional_authority", "execution_requested", "platform_core_admission_requested", "authorization_requested", "worker_requested", "replay_requested"):
        if request[field] is not False:
            _fail("FORBIDDEN_AUTHORITY_FIELD", "commitment request grants authority")
    snapshot = validate_candidate_objective_snapshot_v2(request["candidate_objective_snapshot"])
    readiness = readiness_v2.validate_objective_readiness_report_v2(request["readiness_report"])
    if readiness["readiness_disposition"] != readiness_v2.READY:
        _fail("READINESS_NOT_READY", "commitment requires a ready report")
    candidate_digest = compute_candidate_objective_digest_v2(snapshot)
    if request["candidate_objective_digest"] != candidate_digest:
        _fail("CANDIDATE_DIGEST_MISMATCH", "candidate digest is invalid")
    action = _closed(request["human_commitment_action"], _HUMAN_ACTION_FIELDS, "human commitment action")
    _validate_explicit_commit_action(action["explicit_command"], candidate_digest)
    if action["control_act"] != COMMIT_EXACT_CANDIDATE or action["candidate_objective_digest"] != candidate_digest:
        _fail("HUMAN_COMMITMENT_INVALID", "human commitment action is invalid")
    _digest(action["human_participant_digest"], "human participant digest", "sha256:")
    _digest(action["participant_binding_digest"], "participant binding digest", "sha256:")
    if action["participant_binding_digest"] != readiness["participant_binding_digest"]:
        _fail("HUMAN_COMMITMENT_INVALID", "participant binding is stale")
    _request_bindings(request, snapshot, readiness)
    slot_revisions = _slot_revisions(request["source_semantic_slot_revisions"])
    expected_revisions = [{"slot_id": item["slot_id"], "slot_revision": item["slot_revision"]} for item in snapshot["source_semantic_slots"]]
    if slot_revisions != expected_revisions:
        _fail("SLOT_REVISION_MISMATCH", "source slot revisions are invalid")
    identity_body = _commitment_identity_body(
        conversation_identity=request["conversation_identity"],
        workspace_identity_hash=request["workspace_identity_hash"],
        session_identity_hash=request["session_identity_hash"],
        global_revision=request["global_revision"],
        envelope_revision=request["envelope_revision"],
        semantic_revision=request["semantic_revision"],
        candidate_objective_digest=candidate_digest,
        readiness_report_identity=request["readiness_report_identity"],
        readiness_report_digest=request["readiness_report_digest"],
        source_semantic_slot_revisions=slot_revisions,
        human_commitment_action=action,
        requested_at=request["requested_at"],
    )
    expected_key = "objective-commitment-key-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes(identity_body)).hexdigest()
    expected_identity = "objective-commitment-local-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes({"identity_body": identity_body, "commitment_idempotency_key": expected_key})).hexdigest()
    if request["commitment_idempotency_key"] != expected_key or request["commitment_identity"] != expected_identity:
        _fail("COMMITMENT_IDENTITY_INVALID", "commitment identity is invalid")
    _identity(request["request_id"], "request identity", "objective-commitment-request-sha256:")
    request_identity_body = deepcopy(request)
    request_identity_body["request_id"] = None
    request_identity_body["integrity_checksum"] = None
    expected_request_id = "objective-commitment-request-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes(request_identity_body)).hexdigest()
    if request["request_id"] != expected_request_id:
        _fail("COMMITMENT_REQUEST_INVALID", "request identity is invalid")
    _validate_integrity(request, "commitment request")
    return request


def commit_objective_snapshot_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    commitment_request: dict[str, Any],
) -> dict[str, Any]:
    """Persist one immutable commitment and reconcile CWM cleanup."""

    request = validate_objective_commitment_request_v2(commitment_request)
    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    _validate_call_identity(request, workspace, session)
    cwm_root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(cwm_root):
        state_path = cwm_v2._state_path(cwm_root, workspace, session)
        store_root = _commitment_root(cwm_root)
        intent_path = _intent_path(store_root, request["conversation_identity"])
        record = _record_from_request(request)
        if intent_path.exists():
            intent = _read_and_validate_intent(intent_path)
            if intent["commitment_request"] != request or intent["commitment_record"] != record:
                _fail("CONFLICTING_COMMITMENT", "conversation episode already has another commitment")
        else:
            current = _load_exact_ready_state(state_path, workspace, session, request)
            del current
            intent = _intent_from_request(request, record)
            _write_immutable_json(intent_path, intent)
            written_intent = _read_and_validate_intent(intent_path)
            if written_intent != intent:
                _fail("COMMITMENT_INTENT_INVALID", "commitment intent read-back differs")
            intent = written_intent
        return _finish_commitment_locked(
            state_path=state_path,
            cwm_root=cwm_root,
            store_root=store_root,
            workspace=workspace,
            session=session,
            intent=intent,
            recovery=False,
        )


def validate_objective_commitment_record_v2(
    commitment_record: dict[str, Any],
) -> dict[str, Any]:
    """Validate one immutable local commitment record and authority boundary."""

    record = _closed(commitment_record, _RECORD_FIELDS, "commitment record")
    if record["record_type"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_RECORD_SCHEMA_V1 or record["record_runtime_version"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2 or record["record_ruleset_version"] != OBJECTIVE_COMMITMENT_RULESET_V1 or record["record_status"] != IMMUTABLY_COMMITTED:
        _fail("COMMITMENT_RECORD_INVALID", "commitment record version is invalid")
    for field in ("constitutional_artifact", "constitutional_authority", "pipeline_objective_created", "execution_authority", "platform_core_admitted", "development_governance_admitted", "capability_selected", "approval_granted", "authorization_granted", "worker_dispatched", "completion_recorded", "replay_written", "aicli_invoked", "hir_invoked"):
        if record[field] is not False:
            _fail("FORBIDDEN_AUTHORITY_FIELD", "commitment record grants execution authority")
    snapshot = validate_candidate_objective_snapshot_v2(record["candidate_objective_snapshot"])
    digest = compute_candidate_objective_digest_v2(snapshot)
    if record["candidate_objective_digest"] != digest:
        _fail("COMMITMENT_RECORD_INVALID", "record candidate digest is invalid")
    for field, expected in (
        ("conversation_identity", snapshot["conversation_identity"]),
        ("workspace_identity_hash", snapshot["workspace_identity_hash"]),
        ("session_identity_hash", snapshot["session_identity_hash"]),
        ("global_revision", snapshot["global_revision"]),
        ("envelope_revision", snapshot["envelope_revision"]),
        ("semantic_revision", snapshot["semantic_revision"]),
        ("state_machine_state", snapshot["state_machine_state"]),
    ):
        if record[field] != expected:
            _fail("COMMITMENT_RECORD_INVALID", "record state binding is invalid")
    evidence = snapshot["readiness_evidence"]
    if record["readiness_report_identity"] != evidence["readiness_report_identity"] or record["readiness_report_digest"] != evidence["readiness_report_digest"] or record["readiness_report_checksum"] != evidence["readiness_report_checksum"]:
        _fail("COMMITMENT_RECORD_INVALID", "record readiness binding is invalid")
    revisions = _slot_revisions(record["source_semantic_slot_revisions"])
    expected_revisions = [{"slot_id": item["slot_id"], "slot_revision": item["slot_revision"]} for item in snapshot["source_semantic_slots"]]
    if revisions != expected_revisions:
        _fail("COMMITMENT_RECORD_INVALID", "record slot revisions are invalid")
    action = _closed(record["human_commitment_evidence"], _HUMAN_ACTION_FIELDS, "human commitment evidence")
    _validate_explicit_commit_action(action["explicit_command"], digest)
    identity_body = _commitment_identity_body(
        conversation_identity=record["conversation_identity"],
        workspace_identity_hash=record["workspace_identity_hash"],
        session_identity_hash=record["session_identity_hash"],
        global_revision=record["global_revision"],
        envelope_revision=record["envelope_revision"],
        semantic_revision=record["semantic_revision"],
        candidate_objective_digest=digest,
        readiness_report_identity=record["readiness_report_identity"],
        readiness_report_digest=record["readiness_report_digest"],
        source_semantic_slot_revisions=revisions,
        human_commitment_action=action,
        requested_at=record["committed_at"],
    )
    expected_key = "objective-commitment-key-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes(identity_body)).hexdigest()
    expected_identity = "objective-commitment-local-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes({"identity_body": identity_body, "commitment_idempotency_key": expected_key})).hexdigest()
    if record["commitment_idempotency_key"] != expected_key or record["commitment_identity"] != expected_identity:
        _fail("COMMITMENT_RECORD_INVALID", "record commitment identity is invalid")
    _identity(record["source_request_id"], "source request identity", "objective-commitment-request-sha256:")
    _digest(record["source_request_digest"], "source request digest", "sha256:")
    committed = cwm_v2._canonical_timestamp(record["committed_at"], "committed_at")
    if record["committed_at"] != committed:
        _fail("COMMITMENT_RECORD_INVALID", "commitment time is not canonical")
    _validate_integrity(record, "commitment record")
    return record


def restore_or_reconcile_objective_commitment_v2(
    *,
    runtime_root: str | Path,
    workspace_identity: str | Path,
    session_identity: str,
    conversation_identity: str,
) -> dict[str, Any]:
    """Resume an immutable intent and reconcile record creation/CWM cleanup."""

    workspace = cwm_v2._normalize_workspace_identity(workspace_identity)
    session = cwm_v2._require_identity(session_identity, "session_identity")
    conversation = _identity(conversation_identity, "conversation identity", "conversation-local-sha256:")
    cwm_root = cwm_v2._conversation_root(runtime_root)
    with cwm_v2._store_lock(cwm_root):
        store_root = _commitment_root(cwm_root)
        intent_path = _intent_path(store_root, conversation)
        if not intent_path.exists():
            _fail("COMMITMENT_INTENT_ABSENT", "no commitment intent exists")
        intent = _read_and_validate_intent(intent_path)
        request = intent["commitment_request"]
        _validate_call_identity(request, workspace, session)
        state_path = cwm_v2._state_path(cwm_root, workspace, session)
        return _finish_commitment_locked(
            state_path=state_path,
            cwm_root=cwm_root,
            store_root=store_root,
            workspace=workspace,
            session=session,
            intent=intent,
            recovery=True,
        )


def _validated_ready_state(
    state: dict[str, Any], readiness_report: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        current = state_machine_v2.validate_conversation_state_machine_state_v2(state)
        readiness = readiness_v2.validate_objective_readiness_report_v2(readiness_report)
    except FailClosedRuntimeError as exc:
        _fail("READINESS_EVIDENCE_INVALID", str(exc))
    if readiness["readiness_disposition"] != readiness_v2.READY or readiness["objective_commitment_eligible"] is not True:
        _fail("READINESS_NOT_READY", "Objective readiness is not established")
    expected = readiness_v2.evaluate_objective_readiness_v2(
        current,
        expected_revision=current["revision"],
        expected_semantic_revision=current["semantic_revision"],
        observed_at=readiness["evaluated_at"],
    )
    if expected != readiness:
        _fail("STALE_READINESS", "readiness evidence does not match current state")
    if readiness["protocol_state"] != state_machine_v2.OBJECTIVE_READY:
        _fail("WRONG_STATE_MACHINE_STATE", "conversation is not Objective ready")
    return current, readiness


def _record_from_request(request: dict[str, Any]) -> dict[str, Any]:
    record = {
        "record_type": PLATFORM_CORE_OBJECTIVE_COMMITMENT_RECORD_SCHEMA_V1,
        "record_runtime_version": PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2,
        "record_ruleset_version": OBJECTIVE_COMMITMENT_RULESET_V1,
        "record_status": IMMUTABLY_COMMITTED,
        "commitment_identity": request["commitment_identity"],
        "commitment_idempotency_key": request["commitment_idempotency_key"],
        "source_request_id": request["request_id"],
        "source_request_digest": cwm_v2._checksum(request),
        "candidate_objective_snapshot": deepcopy(request["candidate_objective_snapshot"]),
        "candidate_objective_digest": request["candidate_objective_digest"],
        "conversation_identity": request["conversation_identity"],
        "workspace_identity_hash": request["workspace_identity_hash"],
        "session_identity_hash": request["session_identity_hash"],
        "global_revision": request["global_revision"],
        "envelope_revision": request["envelope_revision"],
        "semantic_revision": request["semantic_revision"],
        "state_machine_state": request["state_machine_state"],
        "readiness_report_identity": request["readiness_report_identity"],
        "readiness_report_digest": request["readiness_report_digest"],
        "readiness_report_checksum": request["readiness_report_checksum"],
        "source_semantic_slot_revisions": deepcopy(request["source_semantic_slot_revisions"]),
        "human_commitment_evidence": deepcopy(request["human_commitment_action"]),
        "committed_at": request["requested_at"],
        "constitutional_artifact": False,
        "constitutional_authority": False,
        "pipeline_objective_created": False,
        "execution_authority": False,
        "platform_core_admitted": False,
        "development_governance_admitted": False,
        "capability_selected": False,
        "approval_granted": False,
        "authorization_granted": False,
        "worker_dispatched": False,
        "completion_recorded": False,
        "replay_written": False,
        "aicli_invoked": False,
        "hir_invoked": False,
        "integrity_checksum": None,
    }
    record["integrity_checksum"] = _integrity(record)
    return validate_objective_commitment_record_v2(record)


def _intent_from_request(
    request: dict[str, Any], record: dict[str, Any]
) -> dict[str, Any]:
    body = {
        "conversation_identity": request["conversation_identity"],
        "commitment_identity": request["commitment_identity"],
        "request_digest": cwm_v2._checksum(request),
        "record_digest": cwm_v2._checksum(record),
    }
    intent = {
        "intent_type": PLATFORM_CORE_OBJECTIVE_COMMITMENT_INTENT_SCHEMA_V1,
        "intent_runtime_version": PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2,
        "intent_status": COMMITMENT_REQUESTED,
        "intent_identity": "objective-commitment-intent-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes(body)).hexdigest(),
        "conversation_identity": request["conversation_identity"],
        "workspace_identity_hash": request["workspace_identity_hash"],
        "session_identity_hash": request["session_identity_hash"],
        "commitment_identity": request["commitment_identity"],
        "request_digest": cwm_v2._checksum(request),
        "record_digest": cwm_v2._checksum(record),
        "commitment_request": deepcopy(request),
        "commitment_record": deepcopy(record),
        "created_at": request["requested_at"],
        "integrity_checksum": None,
    }
    intent["integrity_checksum"] = _integrity(intent)
    return _validate_intent(intent)


def _validate_intent(value: dict[str, Any]) -> dict[str, Any]:
    intent = _closed(value, _INTENT_FIELDS, "commitment intent")
    if intent["intent_type"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_INTENT_SCHEMA_V1 or intent["intent_runtime_version"] != PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2 or intent["intent_status"] != COMMITMENT_REQUESTED:
        _fail("COMMITMENT_INTENT_INVALID", "commitment intent version is invalid")
    request = validate_objective_commitment_request_v2(intent["commitment_request"])
    record = validate_objective_commitment_record_v2(intent["commitment_record"])
    if intent["conversation_identity"] != request["conversation_identity"] or intent["workspace_identity_hash"] != request["workspace_identity_hash"] or intent["session_identity_hash"] != request["session_identity_hash"] or intent["commitment_identity"] != request["commitment_identity"] or record["commitment_identity"] != request["commitment_identity"]:
        _fail("COMMITMENT_INTENT_INVALID", "commitment intent binding is invalid")
    if intent["request_digest"] != cwm_v2._checksum(request) or intent["record_digest"] != cwm_v2._checksum(record):
        _fail("COMMITMENT_INTENT_INVALID", "commitment intent digest is invalid")
    body = {
        "conversation_identity": request["conversation_identity"],
        "commitment_identity": request["commitment_identity"],
        "request_digest": intent["request_digest"],
        "record_digest": intent["record_digest"],
    }
    expected = "objective-commitment-intent-sha256:" + hashlib.sha256(cwm_v2._canonical_bytes(body)).hexdigest()
    if intent["intent_identity"] != expected or intent["created_at"] != request["requested_at"]:
        _fail("COMMITMENT_INTENT_INVALID", "commitment intent identity is invalid")
    _validate_integrity(intent, "commitment intent")
    return intent


def _finish_commitment_locked(
    *,
    state_path: Path,
    cwm_root: Path,
    store_root: Path,
    workspace: str,
    session: str,
    intent: dict[str, Any],
    recovery: bool,
) -> dict[str, Any]:
    request = intent["commitment_request"]
    expected_record = intent["commitment_record"]
    record_path = _record_path(store_root, request["commitment_identity"])
    existed = record_path.exists()
    if existed:
        record = _read_immutable_json(record_path, "commitment record")
        validated = validate_objective_commitment_record_v2(record)
        if validated != expected_record:
            _fail("CONFLICTING_COMMITMENT", "immutable commitment bytes conflict")
    else:
        if not state_path.exists():
            _fail("RECOVERY_INDETERMINATE", "intent exists without CWM or record")
        _load_exact_ready_state(state_path, workspace, session, request)
        try:
            _write_immutable_json(record_path, expected_record)
        except ObjectiveCommitmentError:
            raise
        except Exception as exc:  # pragma: no cover - defensive adapter boundary.
            raise ObjectiveCommitmentError("COMMITMENT_WRITE_FAILED", "immutable commitment write failed") from exc
        record = _read_immutable_json(record_path, "commitment record")
        if validate_objective_commitment_record_v2(record) != expected_record:
            _fail("COMMITMENT_RECORD_INVALID", "commitment read-back differs")
    cleanup_complete = True
    if state_path.exists():
        try:
            _load_exact_ready_state(state_path, workspace, session, request)
            cleanup_complete = _cleanup_cwm_episode(state_path, cwm_root)
        except (FailClosedRuntimeError, ObjectiveCommitmentError):
            cleanup_complete = False
    if cleanup_complete is False:
        disposition = RECOVERED_CLEANUP_PENDING if recovery else CLEANUP_PENDING
    elif recovery:
        disposition = RECOVERED_COMMITTED
    elif existed:
        disposition = ALREADY_COMMITTED
    else:
        disposition = COMMITTED
    return _commitment_result(disposition, record, cleanup_complete)


def _load_exact_ready_state(
    state_path: Path,
    workspace: str,
    session: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    if not state_path.exists():
        _fail("CWM_STATE_ABSENT", "conversation state is absent")
    try:
        current = state_machine_v2.validate_conversation_state_machine_state_v2(
            cwm_v2._read_json_state(state_path),
            expected_workspace_identity=workspace,
            expected_session_identity=session,
        )
    except FailClosedRuntimeError as exc:
        _fail("CWM_STATE_INVALID", str(exc))
    if current["revision"] != request["global_revision"] or current["envelope_revision"] != request["envelope_revision"] or current["semantic_revision"] != request["semantic_revision"]:
        _fail("STALE_CWM_REVISION", "CWM revision is stale")
    if current["envelope"]["conversation_identity"] != request["conversation_identity"] or current["envelope"]["workspace_identity_hash"] != request["workspace_identity_hash"] or current["envelope"]["session_identity_hash"] != request["session_identity_hash"]:
        _fail("IDENTITY_BINDING_MISMATCH", "CWM identity binding is invalid")
    rebuilt, readiness = _validated_ready_state(current, request["readiness_report"])
    if readiness["readiness_report_id"] != request["readiness_report_identity"] or cwm_v2._checksum(readiness) != request["readiness_report_digest"] or readiness["report_checksum"] != request["readiness_report_checksum"]:
        _fail("STALE_READINESS", "readiness report binding is stale")
    snapshot = build_candidate_objective_snapshot_v2(rebuilt, readiness_report=readiness)
    if snapshot != request["candidate_objective_snapshot"] or compute_candidate_objective_digest_v2(snapshot) != request["candidate_objective_digest"]:
        _fail("CANDIDATE_DIGEST_MISMATCH", "candidate snapshot changed")
    _, participant_digest = _bound_human_participant(
        rebuilt, request["human_commitment_action"]["human_participant_digest"]
    )
    if participant_digest != request["human_commitment_action"]["human_participant_digest"]:
        _fail("HUMAN_COMMITMENT_INVALID", "human participant binding changed")
    return rebuilt


def _cleanup_cwm_episode(state_path: Path, cwm_root: Path) -> bool:
    try:
        cwm_v2._remove_state(state_path, cwm_root)
    except FailClosedRuntimeError:
        return False
    return not state_path.exists()


def _commitment_result(
    disposition: str, record: dict[str, Any], cleanup_complete: bool
) -> dict[str, Any]:
    result = {
        "objective_commitment_runtime_version": PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2,
        "disposition": disposition,
        "commitment_identity": record["commitment_identity"],
        "candidate_objective_digest": record["candidate_objective_digest"],
        "commitment_record": deepcopy(record),
        "commitment_record_created": disposition == COMMITTED,
        "immutable_commitment_present": True,
        "cwm_cleanup_complete": cleanup_complete,
        "cwm_episode_state": "ABSENT" if cleanup_complete else CLEANUP_PENDING,
        "constitutional_authority": False,
        "execution_authority": False,
        "platform_core_admitted": False,
        "development_governance_admitted": False,
        "capability_selected": False,
        "approval_granted": False,
        "authorization_granted": False,
        "worker_dispatched": False,
        "completion_recorded": False,
        "replay_written": False,
    }
    for field in _RESULT_FIELDS_FALSE:
        if result[field] is not False:
            _fail("FORBIDDEN_AUTHORITY_FIELD", "commitment result grants authority")
    return result


def _request_bindings(
    request: dict[str, Any],
    snapshot: dict[str, Any],
    readiness: dict[str, Any],
) -> None:
    expected = {
        "conversation_identity": snapshot["conversation_identity"],
        "workspace_identity_hash": snapshot["workspace_identity_hash"],
        "session_identity_hash": snapshot["session_identity_hash"],
        "global_revision": snapshot["global_revision"],
        "envelope_revision": snapshot["envelope_revision"],
        "semantic_revision": snapshot["semantic_revision"],
        "state_machine_state": snapshot["state_machine_state"],
        "readiness_report_identity": readiness["readiness_report_id"],
        "readiness_report_digest": cwm_v2._checksum(readiness),
        "readiness_report_checksum": readiness["report_checksum"],
    }
    for field, value in expected.items():
        if request[field] != value:
            _fail("COMMITMENT_REQUEST_INVALID", f"{field} binding is invalid")
    if request["normalization_ruleset_version"] != cwm_v2.PLATFORM_CORE_SEMANTIC_NORMALIZATION_RULESET_V1:
        _fail("COMMITMENT_REQUEST_INVALID", "normalization ruleset is invalid")
    requested = cwm_v2._canonical_timestamp(request["requested_at"], "requested_at")
    if requested != request["requested_at"] or requested != readiness["evaluated_at"]:
        _fail("STALE_READINESS", "commitment time is stale")


def _commitment_identity_body(**values: Any) -> dict[str, Any]:
    return {
        "identity_ruleset_version": OBJECTIVE_COMMITMENT_RULESET_V1,
        **deepcopy(values),
    }


def _validate_explicit_commit_action(command: Any, candidate_digest: str) -> None:
    expected = f"/commit {candidate_digest}"
    if not isinstance(command, str) or command != expected:
        _fail("EXPLICIT_COMMIT_REQUIRED", "exact /commit candidate digest is required")


def _bound_human_participant(
    state: dict[str, Any], supplied_digest: str
) -> tuple[dict[str, Any], str]:
    humans = [
        participant
        for participant in state["envelope"]["participants"]
        if participant["participant_role"] == cwm_v2.HUMAN_ORIGINATOR
    ]
    if len(humans) != 1:
        _fail("HUMAN_COMMITMENT_INVALID", "exactly one human originator is required")
    digest = cwm_v2._checksum(humans[0])
    if supplied_digest != digest:
        _fail("HUMAN_COMMITMENT_INVALID", "human participant digest is invalid")
    return deepcopy(humans[0]), digest


def _single_slot(
    slots: list[dict[str, Any]], slot_class: str, slot_role: str | None
) -> dict[str, Any]:
    matches = [
        slot
        for slot in slots
        if slot["slot_class"] == slot_class
        and (slot_role is None or slot["slot_role"] == slot_role)
    ]
    if len(matches) != 1:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "required slot cardinality is invalid")
    return matches[0]


def _source_slot(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "slot_id": slot["slot_id"],
        "slot_revision": slot["slot_revision"],
        "slot_class": slot["slot_class"],
        "slot_role": slot["slot_role"],
        "cardinality_key": slot["cardinality_key"],
        "value_digest": cwm_v2._checksum(slot["canonical_value"]),
    }


def _semantic_value(slot: dict[str, Any]) -> dict[str, Any]:
    return {
        "slot_id": slot["slot_id"],
        "slot_revision": slot["slot_revision"],
        "slot_role": slot["slot_role"],
        "cardinality_key": slot["cardinality_key"],
        "canonical_value": slot["canonical_value"],
        "value_digest": cwm_v2._checksum(slot["canonical_value"]),
    }


def _source_slots(value: Any, conversation_identity: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > cwm_v2.MAX_SEMANTIC_SLOTS:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "source slots are invalid")
    result: list[dict[str, Any]] = []
    for raw in value:
        item = _closed(raw, _SOURCE_SLOT_FIELDS, "source slot")
        _identity(item["slot_id"], "slot identity", "conversation-slot-sha256:")
        _nonnegative(item["slot_revision"], "slot revision")
        if item["slot_class"] not in cwm_v2.SEMANTIC_SLOT_CLASSES or item["slot_role"] not in cwm_v2.SLOT_ROLES[item["slot_class"]]:
            _fail("CANDIDATE_SNAPSHOT_INVALID", "source slot taxonomy is invalid")
        _text(item["cardinality_key"], "cardinality key")
        expected_id = cwm_v2._slot_identity(conversation_identity, item["slot_class"], item["cardinality_key"])
        if item["slot_id"] != expected_id:
            _fail("CANDIDATE_SNAPSHOT_INVALID", "source slot identity is invalid")
        _digest(item["value_digest"], "source value digest", "sha256:")
        result.append(item)
    if [item["slot_id"] for item in result] != sorted({item["slot_id"] for item in result}):
        _fail("CANDIDATE_SNAPSHOT_INVALID", "source slots are not canonical")
    return result


def _semantic_values(value: Any, slot_class: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > cwm_v2.MAX_SEMANTIC_SLOTS:
        _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic values are invalid")
    result: list[dict[str, Any]] = []
    for raw in value:
        item = _closed(raw, _SEMANTIC_VALUE_FIELDS, "semantic value")
        _identity(item["slot_id"], "semantic slot identity", "conversation-slot-sha256:")
        _nonnegative(item["slot_revision"], "semantic slot revision")
        if item["slot_role"] not in cwm_v2.SLOT_ROLES[slot_class]:
            _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic value role is invalid")
        _text(item["cardinality_key"], "cardinality key")
        _text(item["canonical_value"], "canonical value")
        if item["value_digest"] != cwm_v2._checksum(item["canonical_value"]):
            _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic value digest is invalid")
        result.append(item)
    if [item["slot_id"] for item in result] != sorted({item["slot_id"] for item in result}):
        _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic values are not canonical")
    return result


def _validate_snapshot_source_bindings(
    snapshot: dict[str, Any],
    *,
    source_slots: list[dict[str, Any]],
    qualifiers: list[dict[str, Any]],
    references: list[dict[str, Any]],
) -> None:
    by_id = {item["slot_id"]: item for item in source_slots}
    conversation = snapshot["conversation_identity"]
    core = (
        (cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY, snapshot["requested_action"]),
        (cwm_v2.OPERATIVE_SUBJECT, cwm_v2.PRIMARY, snapshot["subject"]),
        (cwm_v2.DESIRED_OUTCOME, cwm_v2.PRIMARY, snapshot["expected_outcome"]),
        (cwm_v2.WORK_TYPE, snapshot["work_type"], snapshot["work_type"]),
    )
    for slot_class, slot_role, canonical_value in core:
        slot_id = cwm_v2._slot_identity(conversation, slot_class, cwm_v2.PRIMARY)
        source = by_id.get(slot_id)
        if (
            source is None
            or source["slot_class"] != slot_class
            or source["slot_role"] != slot_role
            or source["value_digest"] != cwm_v2._checksum(canonical_value)
        ):
            _fail("CANDIDATE_SNAPSHOT_INVALID", "core source binding is invalid")
    for values, slot_class in (
        (qualifiers, cwm_v2.GOVERNING_QUALIFIER),
        (references, cwm_v2.SEMANTIC_REFERENCE),
    ):
        source_ids = {
            item["slot_id"]
            for item in source_slots
            if item["slot_class"] == slot_class
        }
        if source_ids != {item["slot_id"] for item in values}:
            _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic source set is invalid")
        for value in values:
            source = by_id[value["slot_id"]]
            if (
                source["slot_revision"] != value["slot_revision"]
                or source["slot_role"] != value["slot_role"]
                or source["cardinality_key"] != value["cardinality_key"]
                or source["value_digest"] != value["value_digest"]
            ):
                _fail("CANDIDATE_SNAPSHOT_INVALID", "semantic source binding is invalid")
    secondary_sources = [
        item
        for item in source_slots
        if item["slot_class"] == cwm_v2.DESIRED_OUTCOME
        and item["slot_role"] == cwm_v2.SECONDARY
    ]
    if len(secondary_sources) != len(snapshot["secondary_outcomes"]):
        _fail("CANDIDATE_SNAPSHOT_INVALID", "secondary outcome binding is invalid")


def _slot_revisions(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > cwm_v2.MAX_SEMANTIC_SLOTS:
        _fail("SLOT_REVISION_MISMATCH", "slot revisions are invalid")
    result: list[dict[str, Any]] = []
    for raw in value:
        item = _closed(raw, _SLOT_REVISION_FIELDS, "slot revision binding")
        _identity(item["slot_id"], "slot revision identity", "conversation-slot-sha256:")
        _nonnegative(item["slot_revision"], "slot revision")
        result.append(item)
    if [item["slot_id"] for item in result] != sorted({item["slot_id"] for item in result}):
        _fail("SLOT_REVISION_MISMATCH", "slot revisions are not canonical")
    return result


def _validate_call_identity(request: dict[str, Any], workspace: str, session: str) -> None:
    if request["workspace_identity_hash"] != cwm_v2._identity_hash(workspace) or request["session_identity_hash"] != cwm_v2._identity_hash(session):
        _fail("IDENTITY_BINDING_MISMATCH", "call identity differs from commitment request")


def _commitment_root(cwm_root: Path) -> Path:
    root = cwm_root / _STORE_DIRECTORY
    _secure_directory(root)
    _secure_directory(root / _EPISODE_DIRECTORY)
    _secure_directory(root / _RECORD_DIRECTORY)
    return root


def _intent_path(store_root: Path, conversation_identity: str) -> Path:
    digest = _identity(conversation_identity, "conversation identity", "conversation-local-sha256:").removeprefix("conversation-local-sha256:")
    return store_root / _EPISODE_DIRECTORY / f"{digest}.json"


def _record_path(store_root: Path, commitment_identity: str) -> Path:
    digest = _identity(commitment_identity, "commitment identity", "objective-commitment-local-sha256:").removeprefix("objective-commitment-local-sha256:")
    return store_root / _RECORD_DIRECTORY / f"{digest}.json"


def _write_immutable_json(path: Path, value: dict[str, Any]) -> None:
    data = cwm_v2._canonical_bytes(value)
    if len(data) > _MAX_IMMUTABLE_BYTES:
        _fail("COMMITMENT_WRITE_FAILED", "immutable commitment exceeds storage bound")
    _secure_directory(path.parent)
    descriptor = -1
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(prefix=".commitment.", suffix=".tmp", dir=path.parent)
        os.fchmod(descriptor, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_name, path)
        os.chmod(path, stat.S_IRUSR)
        _fsync_directory(path.parent)
    except FileExistsError as exc:
        _fail("IMMUTABLE_PATH_EXISTS", "immutable commitment path already exists")
    except OSError as exc:
        raise ObjectiveCommitmentError("COMMITMENT_WRITE_FAILED", "immutable commitment write failed") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def _read_immutable_json(path: Path, name: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        _fail("COMMITMENT_RECORD_INVALID", f"{name} path is unsafe")
    mode = path.stat().st_mode
    if mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        _fail("COMMITMENT_RECORD_INVALID", f"{name} is writable")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ObjectiveCommitmentError("COMMITMENT_RECORD_INVALID", f"{name} is unreadable") from exc
    if len(raw) > _MAX_IMMUTABLE_BYTES:
        _fail("COMMITMENT_RECORD_INVALID", f"{name} exceeds storage bound")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ObjectiveCommitmentError("COMMITMENT_RECORD_INVALID", f"{name} is corrupt") from exc
    if not isinstance(value, dict) or cwm_v2._canonical_bytes(value) != raw:
        _fail("COMMITMENT_RECORD_INVALID", f"{name} is not canonical")
    return value


def _read_and_validate_intent(path: Path) -> dict[str, Any]:
    try:
        return _validate_intent(_read_immutable_json(path, "commitment intent"))
    except ObjectiveCommitmentError as exc:
        if exc.reason_code == "COMMITMENT_RECORD_INVALID":
            _fail("COMMITMENT_INTENT_INVALID", str(exc))
        raise


def _secure_directory(path: Path) -> None:
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if path.is_symlink() or not path.is_dir():
            _fail("COMMITMENT_STORE_UNSAFE", "commitment directory is unsafe")
        os.chmod(path, stat.S_IRWXU)
    except OSError as exc:
        raise ObjectiveCommitmentError("COMMITMENT_STORE_UNSAFE", "commitment directory is unavailable") from exc


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _integrity(value: dict[str, Any]) -> str:
    body = deepcopy(value)
    body["integrity_checksum"] = None
    return cwm_v2._checksum(body)


def _validate_integrity(value: dict[str, Any], name: str) -> None:
    _digest(value["integrity_checksum"], f"{name} integrity", "sha256:")
    if value["integrity_checksum"] != _integrity(value):
        _fail("INVALID_INTEGRITY", f"{name} integrity is invalid")


def _closed(value: Any, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail("UNSUPPORTED_SCHEMA", f"{name} schema fields are invalid")
    return deepcopy(value)


def _canonical_text_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or len(value) > cwm_v2.MAX_COLLECTION_ITEMS:
        _fail("CANDIDATE_SNAPSHOT_INVALID", f"{name} is invalid")
    result = [_text(item, name) for item in value]
    if result != list(value):
        _fail("CANDIDATE_SNAPSHOT_INVALID", f"{name} is not canonical")
    return result


def _slot_ids(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        _fail("CANDIDATE_SNAPSHOT_INVALID", f"{name} is invalid")
    result = [_identity(item, name, "conversation-slot-sha256:") for item in value]
    if result != sorted(set(result)):
        _fail("CANDIDATE_SNAPSHOT_INVALID", f"{name} is not canonical")
    return result


def _identity(value: Any, name: str, prefix: str) -> str:
    return _digest(value, name, prefix)


def _digest(value: Any, name: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        _fail("INVALID_IDENTITY", f"{name} is invalid")
    suffix = value.removeprefix(prefix)
    if len(suffix) != 64 or any(character not in "0123456789abcdef" for character in suffix):
        _fail("INVALID_IDENTITY", f"{name} is invalid")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > cwm_v2.MAX_TEXT_CHARACTERS:
        _fail("INVALID_TEXT", f"{name} is invalid")
    return value


def _nonnegative(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("INVALID_REVISION", f"{name} is invalid")
    return value


def _fail(reason_code: str, message: str) -> None:
    raise ObjectiveCommitmentError(reason_code, message)


__all__ = [
    "ALREADY_COMMITTED",
    "CLEANUP_PENDING",
    "COMMITTED",
    "OBJECTIVE_COMMITMENT_RULESET_V1",
    "PLATFORM_CORE_CANDIDATE_OBJECTIVE_SNAPSHOT_SCHEMA_V1",
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_RECORD_SCHEMA_V1",
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_REQUEST_SCHEMA_V1",
    "PLATFORM_CORE_OBJECTIVE_COMMITMENT_RUNTIME_V2",
    "RECOVERED_CLEANUP_PENDING",
    "RECOVERED_COMMITTED",
    "ObjectiveCommitmentError",
    "build_candidate_objective_snapshot_v2",
    "commit_objective_snapshot_v2",
    "compute_candidate_objective_digest_v2",
    "create_objective_commitment_request_v2",
    "restore_or_reconcile_objective_commitment_v2",
    "validate_candidate_objective_snapshot_v2",
    "validate_objective_commitment_record_v2",
    "validate_objective_commitment_request_v2",
]
