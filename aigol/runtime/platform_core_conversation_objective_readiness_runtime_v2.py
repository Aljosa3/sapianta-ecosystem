"""Read-only Objective readiness evaluation for Conversation Layer V2.

The runtime validates the atomic Conversation Envelope and Semantic CWM,
delegates semantic completeness to G59-02, and delegates protocol readiness to
G59-03.  It reports or refuses readiness only.  It cannot create or commit an
Objective and cannot invoke any certified execution-pipeline owner.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import platform_core_conversation_state_machine_runtime_v2 as state_machine_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_semantic_slot_runtime_v2 as slots_v2


PLATFORM_CORE_CONVERSATION_OBJECTIVE_READINESS_RUNTIME_V2 = (
    "PLATFORM_CORE_CONVERSATION_OBJECTIVE_READINESS_RUNTIME_V2"
)
PLATFORM_CORE_OBJECTIVE_READINESS_REPORT_SCHEMA_V1 = (
    "PLATFORM_CORE_OBJECTIVE_READINESS_REPORT_SCHEMA_V1"
)
OBJECTIVE_READINESS_RULESET_V1 = "OBJECTIVE_READINESS_RULESET_V1"

READY = "READY"
NOT_READY = "NOT_READY"

REQUIRED_SLOT_MISSING = "REQUIRED_SLOT_MISSING"
REQUIRED_SLOT_INCOMPLETE = "REQUIRED_SLOT_INCOMPLETE"
MATERIAL_SLOT_INCOMPLETE = "MATERIAL_SLOT_INCOMPLETE"
UNRESOLVED_CLARIFICATION = "UNRESOLVED_CLARIFICATION"
UNRESOLVED_SEMANTIC_CONFLICT = "UNRESOLVED_SEMANTIC_CONFLICT"
STALE_SEMANTIC_VALUE = "STALE_SEMANTIC_VALUE"
DEPENDENCY_INCOMPLETE = "DEPENDENCY_INCOMPLETE"
UNCONFIRMED_ASSUMPTION = "UNCONFIRMED_ASSUMPTION"
EXTERNAL_DISPOSITION_INVALID = "EXTERNAL_DISPOSITION_INVALID"
STATE_NOT_ACTIVE = "STATE_NOT_ACTIVE"
STATE_EXPIRED = "STATE_EXPIRED"
CANDIDATE_NOT_BOUND = "CANDIDATE_NOT_BOUND"
HUMAN_CONFIRMATION_MISSING = "HUMAN_CONFIRMATION_MISSING"
STATE_MACHINE_NOT_READY = "STATE_MACHINE_NOT_READY"

_REFUSAL_REASON_VALUES = frozenset(
    {
        REQUIRED_SLOT_MISSING,
        REQUIRED_SLOT_INCOMPLETE,
        MATERIAL_SLOT_INCOMPLETE,
        UNRESOLVED_CLARIFICATION,
        UNRESOLVED_SEMANTIC_CONFLICT,
        STALE_SEMANTIC_VALUE,
        DEPENDENCY_INCOMPLETE,
        UNCONFIRMED_ASSUMPTION,
        EXTERNAL_DISPOSITION_INVALID,
        STATE_NOT_ACTIVE,
        STATE_EXPIRED,
        CANDIDATE_NOT_BOUND,
        HUMAN_CONFIRMATION_MISSING,
        STATE_MACHINE_NOT_READY,
    }
)

_REQUIRED_SPECS = (
    (cwm_v2.OPERATIVE_ACTION, cwm_v2.PRIMARY),
    (cwm_v2.OPERATIVE_SUBJECT, cwm_v2.PRIMARY),
    (cwm_v2.DESIRED_OUTCOME, cwm_v2.PRIMARY),
    (cwm_v2.WORK_TYPE, None),
)

_REPORT_FIELDS = frozenset(
    {
        "readiness_report_type",
        "readiness_report_id",
        "readiness_runtime_version",
        "readiness_ruleset_version",
        "readiness_disposition",
        "conversation_identity",
        "workspace_identity_hash",
        "session_identity_hash",
        "global_revision",
        "envelope_revision",
        "semantic_revision",
        "evaluated_at",
        "state_integrity_checksum",
        "state_digest",
        "participant_binding_digest",
        "interface_binding_digest",
        "protocol_state",
        "required_slot_assessments",
        "semantic_slot_assessments",
        "unresolved_clarification",
        "unresolved_conflict_slot_ids",
        "stale_slot_ids",
        "incomplete_dependency_slot_ids",
        "blocking_evidence",
        "state_machine_assessment",
        "refusal_reasons",
        "objective_commitment_eligible",
        "constitutional_authority",
        "objective_created",
        "objective_commitment_invoked",
        "platform_core_invoked",
        "replay_written",
        "authorization_invoked",
        "worker_invoked",
        "execution_invoked",
        "report_checksum",
    }
)

_REQUIRED_ASSESSMENT_FIELDS = frozenset(
    {
        "required_slot_key",
        "slot_class",
        "required_slot_role",
        "slot_id",
        "present",
        "status",
        "completeness",
        "semantic_classification",
        "dependencies_complete",
        "active_complete",
    }
)

_SEMANTIC_ASSESSMENT_FIELDS = frozenset(
    {
        "slot_id",
        "slot_class",
        "slot_role",
        "cardinality_key",
        "status",
        "completeness",
        "materiality",
        "semantic_classification",
        "dependency_closure",
        "conflicted_dependency_ids",
        "stale_dependency_ids",
        "incomplete_dependency_ids",
    }
)

_CLARIFICATION_FIELDS = frozenset(
    {
        "clarification_id",
        "trigger_slot_id",
        "trigger_reason",
        "source_global_revision",
        "source_semantic_revision",
    }
)

_STATE_MACHINE_ASSESSMENT_FIELDS = frozenset(
    {
        "availability_valid",
        "candidate_ready",
        "candidate_bound",
        "confirmation_bound",
        "objective_commitment_eligible",
        "candidate_digest",
        "presentation_digest",
    }
)

_BLOCKER_FIELDS = frozenset(
    {
        "required_missing",
        "required_incomplete",
        "material_partial",
        "material_conflicted",
        "material_stale",
        "unconfirmed_assumptions",
        "unresolved_dependencies",
        "invalid_external_dispositions",
    }
)


class ObjectiveReadinessError(FailClosedRuntimeError):
    """Fail-closed readiness error with a stable reason and optional report."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        readiness_report: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.readiness_report = deepcopy(readiness_report)


def evaluate_objective_readiness_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    expected_semantic_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Return one deterministic readiness report without mutating state."""

    current, observed = _validated_evaluation_input(
        state,
        expected_revision=expected_revision,
        expected_semantic_revision=expected_semantic_revision,
        observed_at=observed_at,
    )
    try:
        machine = state_machine_v2.evaluate_conversation_readiness_v2(
            current, observed_at=observed
        )
    except FailClosedRuntimeError as exc:
        _fail("STATE_INVALID", str(exc))
    protocol_state = machine["protocol_state"]
    semantic_assessments = _semantic_slot_assessments(current)
    required_assessments = _required_slot_assessments(
        current, semantic_assessments=semantic_assessments
    )
    blockers = deepcopy(machine["blockers"])
    clarification = _clarification_summary(current)
    conflicts = sorted(
        assessment["slot_id"]
        for assessment in semantic_assessments
        if assessment["status"] == cwm_v2.CONFLICTED
        or assessment["completeness"] == cwm_v2.CONFLICTED
    )
    stale = sorted(
        assessment["slot_id"]
        for assessment in semantic_assessments
        if assessment["status"] == cwm_v2.STALE
        or assessment["completeness"] == cwm_v2.STALE
    )
    dependency_incomplete = sorted(
        assessment["slot_id"]
        for assessment in semantic_assessments
        if assessment["conflicted_dependency_ids"]
        or assessment["stale_dependency_ids"]
        or assessment["incomplete_dependency_ids"]
    )
    refusal_reasons = _refusal_reasons(
        current,
        observed_at=observed,
        protocol_state=protocol_state,
        machine=machine,
        blockers=blockers,
        clarification=clarification,
    )
    ready = not refusal_reasons and (
        protocol_state == state_machine_v2.OBJECTIVE_READY
        and machine["objective_commitment_eligible"] is True
    )
    if ready is False and not refusal_reasons:
        refusal_reasons = [STATE_MACHINE_NOT_READY]
    envelope = current["envelope"]
    control = current["semantic_memory"]["protocol_control"]
    candidate_binding = envelope["active_objective_candidate_binding"]
    confirmation = control["confirmation_binding"]
    report = {
        "readiness_report_type": PLATFORM_CORE_OBJECTIVE_READINESS_REPORT_SCHEMA_V1,
        "readiness_report_id": None,
        "readiness_runtime_version": (
            PLATFORM_CORE_CONVERSATION_OBJECTIVE_READINESS_RUNTIME_V2
        ),
        "readiness_ruleset_version": OBJECTIVE_READINESS_RULESET_V1,
        "readiness_disposition": READY if ready else NOT_READY,
        "conversation_identity": envelope["conversation_identity"],
        "workspace_identity_hash": envelope["workspace_identity_hash"],
        "session_identity_hash": envelope["session_identity_hash"],
        "global_revision": current["revision"],
        "envelope_revision": current["envelope_revision"],
        "semantic_revision": current["semantic_revision"],
        "evaluated_at": observed,
        "state_integrity_checksum": current["integrity_checksum"],
        "state_digest": cwm_v2._checksum(current),
        "participant_binding_digest": cwm_v2._checksum(envelope["participants"]),
        "interface_binding_digest": cwm_v2._checksum(
            {
                "current_interface_identity": envelope[
                    "current_interface_identity"
                ],
                "context_scope": envelope["context_scope"],
            }
        ),
        "protocol_state": protocol_state,
        "required_slot_assessments": required_assessments,
        "semantic_slot_assessments": semantic_assessments,
        "unresolved_clarification": clarification,
        "unresolved_conflict_slot_ids": conflicts,
        "stale_slot_ids": stale,
        "incomplete_dependency_slot_ids": dependency_incomplete,
        "blocking_evidence": blockers,
        "state_machine_assessment": {
            "availability_valid": machine["availability_valid"],
            "candidate_ready": machine["candidate_ready"],
            "candidate_bound": machine["candidate_bound"],
            "confirmation_bound": machine["confirmation_bound"],
            "objective_commitment_eligible": machine[
                "objective_commitment_eligible"
            ],
            "candidate_digest": (
                candidate_binding["candidate_digest"]
                if candidate_binding is not None
                else None
            ),
            "presentation_digest": (
                confirmation["presentation_digest"]
                if confirmation is not None
                else None
            ),
        },
        "refusal_reasons": sorted(set(refusal_reasons)),
        "objective_commitment_eligible": ready,
        "constitutional_authority": False,
        "objective_created": False,
        "objective_commitment_invoked": False,
        "platform_core_invoked": False,
        "replay_written": False,
        "authorization_invoked": False,
        "worker_invoked": False,
        "execution_invoked": False,
        "report_checksum": None,
    }
    return validate_objective_readiness_report_v2(
        _with_report_identity_and_integrity(report)
    )


def require_objective_readiness_v2(
    state: dict[str, Any],
    *,
    expected_revision: int,
    expected_semantic_revision: int,
    observed_at: str,
) -> dict[str, Any]:
    """Return an exact ready report or refuse without changing state."""

    report = evaluate_objective_readiness_v2(
        state,
        expected_revision=expected_revision,
        expected_semantic_revision=expected_semantic_revision,
        observed_at=observed_at,
    )
    if report["readiness_disposition"] != READY:
        raise ObjectiveReadinessError(
            "OBJECTIVE_READINESS_REFUSED",
            "conversation state is not ready for Objective Commitment",
            readiness_report=report,
        )
    return report


def validate_objective_readiness_report_v2(
    readiness_report: dict[str, Any],
) -> dict[str, Any]:
    """Validate the closed local readiness-report schema and integrity."""

    report = _closed_object(readiness_report, _REPORT_FIELDS, "readiness report")
    if report["readiness_report_type"] != (
        PLATFORM_CORE_OBJECTIVE_READINESS_REPORT_SCHEMA_V1
    ) or report["readiness_runtime_version"] != (
        PLATFORM_CORE_CONVERSATION_OBJECTIVE_READINESS_RUNTIME_V2
    ):
        _fail("READINESS_REPORT_INVALID", "readiness report type is invalid")
    if report["readiness_ruleset_version"] != OBJECTIVE_READINESS_RULESET_V1:
        _fail("READINESS_REPORT_INVALID", "readiness ruleset is invalid")
    _digest(
        report["readiness_report_id"],
        "readiness report identity",
        "objective-readiness-local-sha256:",
    )
    for field, prefix in (
        ("conversation_identity", "conversation-local-sha256:"),
        ("workspace_identity_hash", "sha256:"),
        ("session_identity_hash", "sha256:"),
        ("state_integrity_checksum", "sha256:"),
        ("state_digest", "sha256:"),
        ("participant_binding_digest", "sha256:"),
        ("interface_binding_digest", "sha256:"),
    ):
        _digest(report[field], field, prefix)
    for field in ("global_revision", "envelope_revision", "semantic_revision"):
        _nonnegative_integer(report[field], field)
    canonical_time = cwm_v2._canonical_timestamp(
        report["evaluated_at"], "evaluated_at"
    )
    if report["evaluated_at"] != canonical_time:
        _fail("READINESS_REPORT_INVALID", "evaluation time is not canonical")
    if report["protocol_state"] not in {
        state_machine_v2.COLLECTING,
        state_machine_v2.CLARIFYING,
        state_machine_v2.CANDIDATE_REVIEW,
        state_machine_v2.OBJECTIVE_READY,
        state_machine_v2.SUSPENDED,
        state_machine_v2.ABANDONED,
        state_machine_v2.EXPIRED,
    }:
        _fail("READINESS_REPORT_INVALID", "protocol state is invalid")
    _validate_required_assessments(report["required_slot_assessments"])
    _validate_semantic_assessments(report["semantic_slot_assessments"])
    _validate_clarification(report["unresolved_clarification"])
    for field in (
        "unresolved_conflict_slot_ids",
        "stale_slot_ids",
        "incomplete_dependency_slot_ids",
    ):
        _canonical_slot_ids(report[field], field)
    blockers = _closed_object(
        report["blocking_evidence"], _BLOCKER_FIELDS, "blocking evidence"
    )
    for field, values in blockers.items():
        if not isinstance(values, list) or values != sorted(set(values)):
            _fail("READINESS_REPORT_INVALID", f"{field} blockers are invalid")
        if field == "required_missing":
            if any(
                value
                not in {
                    f"required-slot:{slot_class}:PRIMARY"
                    for slot_class, _ in _REQUIRED_SPECS
                }
                for value in values
            ):
                _fail("READINESS_REPORT_INVALID", "required blockers are invalid")
        else:
            for value in values:
                _digest(value, field, "conversation-slot-sha256:")
    machine = _closed_object(
        report["state_machine_assessment"],
        _STATE_MACHINE_ASSESSMENT_FIELDS,
        "state machine assessment",
    )
    for field in (
        "availability_valid",
        "candidate_ready",
        "candidate_bound",
        "confirmation_bound",
        "objective_commitment_eligible",
    ):
        if not isinstance(machine[field], bool):
            _fail("READINESS_REPORT_INVALID", "state machine flag is invalid")
    for field in ("candidate_digest", "presentation_digest"):
        if machine[field] is not None:
            _digest(machine[field], field, "sha256:")
    reasons = report["refusal_reasons"]
    if (
        not isinstance(reasons, list)
        or reasons != sorted(set(reasons))
        or any(reason not in _REFUSAL_REASON_VALUES for reason in reasons)
    ):
        _fail("READINESS_REPORT_INVALID", "refusal reasons are not canonical")
    ready = report["readiness_disposition"] == READY
    if report["readiness_disposition"] not in {READY, NOT_READY} or (
        ready != report["objective_commitment_eligible"]
    ):
        _fail("READINESS_REPORT_INVALID", "readiness disposition is invalid")
    if ready != (not reasons) or ready != (
        report["protocol_state"] == state_machine_v2.OBJECTIVE_READY
    ):
        _fail("READINESS_REPORT_INVALID", "readiness evidence is inconsistent")
    if machine["objective_commitment_eligible"] != ready:
        _fail("READINESS_REPORT_INVALID", "state machine readiness is inconsistent")
    if ready and (
        report["unresolved_clarification"] is not None
        or any(blockers.values())
        or not all(
            item["active_complete"]
            for item in report["required_slot_assessments"]
        )
        or machine["availability_valid"] is not True
        or machine["candidate_ready"] is not True
        or machine["candidate_bound"] is not True
        or machine["confirmation_bound"] is not True
        or machine["candidate_digest"] is None
        or machine["presentation_digest"] is None
    ):
        _fail("READINESS_REPORT_INVALID", "ready evidence is incomplete")
    for field in (
        "constitutional_authority",
        "objective_created",
        "objective_commitment_invoked",
        "platform_core_invoked",
        "replay_written",
        "authorization_invoked",
        "worker_invoked",
        "execution_invoked",
    ):
        if report[field] is not False:
            _fail("READINESS_REPORT_INVALID", "readiness report grants authority")
    supplied_checksum = report["report_checksum"]
    checksum_body = deepcopy(report)
    checksum_body.pop("report_checksum")
    if supplied_checksum != cwm_v2._checksum(checksum_body):
        _fail("READINESS_REPORT_INVALID", "readiness report integrity is invalid")
    identity_body = deepcopy(report)
    identity_body["readiness_report_id"] = None
    identity_body["report_checksum"] = None
    expected_identity = "objective-readiness-local-sha256:" + hashlib.sha256(
        cwm_v2._canonical_bytes(identity_body)
    ).hexdigest()
    if report["readiness_report_id"] != expected_identity:
        _fail("READINESS_REPORT_INVALID", "readiness report identity is invalid")
    return report


def _validated_evaluation_input(
    state: Any,
    *,
    expected_revision: int,
    expected_semantic_revision: int,
    observed_at: str,
) -> tuple[dict[str, Any], str]:
    try:
        current = state_machine_v2.validate_conversation_state_machine_state_v2(
            state
        )
        observed = cwm_v2._canonical_timestamp(observed_at, "observed_at")
    except FailClosedRuntimeError as exc:
        _fail("STATE_INVALID", str(exc))
    for value, name in (
        (expected_revision, "expected revision"),
        (expected_semantic_revision, "expected semantic revision"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _fail("EXPECTED_REVISION_INVALID", f"{name} is invalid")
    if current["revision"] != expected_revision or current[
        "semantic_revision"
    ] != expected_semantic_revision:
        _fail("STALE_READINESS_REVISION", "readiness revision binding is stale")
    if current["migration_metadata"]["migration_status"] != cwm_v2.NATIVE_V2:
        _fail("STATE_NOT_NATIVE_V2", "legacy readiness evaluation is not implemented")
    return current, observed


def _semantic_slot_assessments(state: dict[str, Any]) -> list[dict[str, Any]]:
    conversation = state["envelope"]["conversation_identity"]
    slots = slots_v2.validate_semantic_slot_collection_v2(
        state["semantic_memory"]["semantic_slots"],
        conversation_identity=conversation,
    )
    assessments: list[dict[str, Any]] = []
    for slot in slots:
        completeness = slots_v2.evaluate_semantic_slot_completeness_v2(
            slot["slot_id"], slots, conversation_identity=conversation
        )
        assessments.append(
            {
                "slot_id": slot["slot_id"],
                "slot_class": slot["slot_class"],
                "slot_role": slot["slot_role"],
                "cardinality_key": slot["cardinality_key"],
                "status": slot["status"],
                "completeness": slot["completeness"],
                "materiality": slot["materiality"],
                "semantic_classification": completeness["classification"],
                "dependency_closure": completeness["dependency_closure"],
                "conflicted_dependency_ids": completeness[
                    "conflicted_dependency_ids"
                ],
                "stale_dependency_ids": completeness["stale_dependency_ids"],
                "incomplete_dependency_ids": completeness[
                    "incomplete_dependency_ids"
                ],
            }
        )
    return sorted(assessments, key=lambda item: item["slot_id"])


def _required_slot_assessments(
    state: dict[str, Any],
    *,
    semantic_assessments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    slots = state["semantic_memory"]["semantic_slots"]
    assessments_by_id = {
        assessment["slot_id"]: assessment for assessment in semantic_assessments
    }
    required: list[dict[str, Any]] = []
    for slot_class, required_role in _REQUIRED_SPECS:
        matches = [
            slot
            for slot in slots
            if slot["slot_class"] == slot_class
            and (required_role is None or slot["slot_role"] == required_role)
        ]
        slot = matches[0] if len(matches) == 1 else None
        semantic = assessments_by_id.get(slot["slot_id"]) if slot is not None else None
        dependencies_complete = bool(
            semantic is not None
            and not semantic["conflicted_dependency_ids"]
            and not semantic["stale_dependency_ids"]
            and not semantic["incomplete_dependency_ids"]
        )
        active_complete = bool(
            slot is not None
            and slot["status"] in {cwm_v2.ASSERTED, cwm_v2.CONFIRMED}
            and slot["completeness"] == cwm_v2.COMPLETE
            and dependencies_complete
        )
        required.append(
            {
                "required_slot_key": f"required-slot:{slot_class}:PRIMARY",
                "slot_class": slot_class,
                "required_slot_role": required_role,
                "slot_id": slot["slot_id"] if slot is not None else None,
                "present": slot is not None,
                "status": slot["status"] if slot is not None else None,
                "completeness": slot["completeness"] if slot is not None else None,
                "semantic_classification": (
                    semantic["semantic_classification"]
                    if semantic is not None
                    else cwm_v2.EMPTY
                ),
                "dependencies_complete": dependencies_complete,
                "active_complete": active_complete,
            }
        )
    return required


def _clarification_summary(state: dict[str, Any]) -> dict[str, Any] | None:
    clarification = state["semantic_memory"]["protocol_control"][
        "clarification_control"
    ]
    if clarification is None:
        return None
    return {
        field: deepcopy(clarification[field])
        for field in _CLARIFICATION_FIELDS
    }


def _refusal_reasons(
    state: dict[str, Any],
    *,
    observed_at: str,
    protocol_state: str,
    machine: dict[str, Any],
    blockers: dict[str, list[str]],
    clarification: dict[str, Any] | None,
) -> list[str]:
    reasons: set[str] = set()
    envelope = state["envelope"]
    if envelope["availability_state"] != cwm_v2.ACTIVE:
        reasons.add(STATE_NOT_ACTIVE)
    if cwm_v2._is_v2_expired(state, observed_at):
        reasons.add(STATE_EXPIRED)
    mapping = {
        "required_missing": REQUIRED_SLOT_MISSING,
        "required_incomplete": REQUIRED_SLOT_INCOMPLETE,
        "material_partial": MATERIAL_SLOT_INCOMPLETE,
        "material_conflicted": UNRESOLVED_SEMANTIC_CONFLICT,
        "material_stale": STALE_SEMANTIC_VALUE,
        "unconfirmed_assumptions": UNCONFIRMED_ASSUMPTION,
        "unresolved_dependencies": DEPENDENCY_INCOMPLETE,
        "invalid_external_dispositions": EXTERNAL_DISPOSITION_INVALID,
    }
    for blocker, reason in mapping.items():
        if blockers[blocker]:
            reasons.add(reason)
    if clarification is not None:
        reasons.add(UNRESOLVED_CLARIFICATION)
    if machine["candidate_bound"] is not True:
        reasons.add(CANDIDATE_NOT_BOUND)
    if machine["confirmation_bound"] is not True:
        reasons.add(HUMAN_CONFIRMATION_MISSING)
    if protocol_state != state_machine_v2.OBJECTIVE_READY or machine[
        "objective_commitment_eligible"
    ] is not True:
        reasons.add(STATE_MACHINE_NOT_READY)
    return sorted(reasons)


def _with_report_identity_and_integrity(report: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(report)
    identity_body = deepcopy(candidate)
    identity_body["readiness_report_id"] = None
    identity_body["report_checksum"] = None
    candidate["readiness_report_id"] = (
        "objective-readiness-local-sha256:"
        + hashlib.sha256(cwm_v2._canonical_bytes(identity_body)).hexdigest()
    )
    checksum_body = deepcopy(candidate)
    checksum_body.pop("report_checksum")
    candidate["report_checksum"] = cwm_v2._checksum(checksum_body)
    return candidate


def _validate_required_assessments(value: Any) -> None:
    if not isinstance(value, list) or len(value) != len(_REQUIRED_SPECS):
        _fail("READINESS_REPORT_INVALID", "required assessments are invalid")
    classes: list[str] = []
    for index, raw in enumerate(value):
        item = _closed_object(
            raw, _REQUIRED_ASSESSMENT_FIELDS, "required slot assessment"
        )
        slot_class, required_role = _REQUIRED_SPECS[index]
        if item["slot_class"] != slot_class or item["required_slot_role"] != (
            required_role
        ):
            _fail("READINESS_REPORT_INVALID", "required slot class is invalid")
        if item["required_slot_key"] != f"required-slot:{slot_class}:PRIMARY":
            _fail("READINESS_REPORT_INVALID", "required slot key is invalid")
        for field in ("present", "dependencies_complete", "active_complete"):
            if not isinstance(item[field], bool):
                _fail("READINESS_REPORT_INVALID", "required flag is invalid")
        if item["slot_id"] is not None:
            _digest(item["slot_id"], "required slot identity", "conversation-slot-sha256:")
        if item["present"] != (item["slot_id"] is not None):
            _fail("READINESS_REPORT_INVALID", "required presence is invalid")
        if item["present"] != (
            item["status"] is not None and item["completeness"] is not None
        ):
            _fail("READINESS_REPORT_INVALID", "required evidence is invalid")
        if item["present"] is False and (
            item["semantic_classification"] != cwm_v2.EMPTY
            or item["dependencies_complete"] is not False
            or item["active_complete"] is not False
        ):
            _fail("READINESS_REPORT_INVALID", "missing slot evidence is invalid")
        if item["status"] is not None and item["status"] not in cwm_v2.SLOT_STATUSES:
            _fail("READINESS_REPORT_INVALID", "required status is invalid")
        if item["completeness"] is not None and item[
            "completeness"
        ] not in cwm_v2.SLOT_COMPLETENESS:
            _fail("READINESS_REPORT_INVALID", "required completeness is invalid")
        if item["semantic_classification"] not in cwm_v2.SLOT_COMPLETENESS:
            _fail("READINESS_REPORT_INVALID", "required classification is invalid")
        classes.append(item["slot_class"])
    if classes != [slot_class for slot_class, _ in _REQUIRED_SPECS]:
        _fail("READINESS_REPORT_INVALID", "required assessment order is invalid")


def _validate_semantic_assessments(value: Any) -> None:
    if not isinstance(value, list) or len(value) > cwm_v2.MAX_SEMANTIC_SLOTS:
        _fail("READINESS_REPORT_INVALID", "semantic assessments are invalid")
    slot_ids: list[str] = []
    for raw in value:
        item = _closed_object(
            raw, _SEMANTIC_ASSESSMENT_FIELDS, "semantic slot assessment"
        )
        _digest(item["slot_id"], "semantic slot identity", "conversation-slot-sha256:")
        if item["slot_class"] not in cwm_v2.SEMANTIC_SLOT_CLASSES or item[
            "slot_role"
        ] not in cwm_v2.SLOT_ROLES[item["slot_class"]]:
            _fail("READINESS_REPORT_INVALID", "semantic slot taxonomy is invalid")
        if not isinstance(item["cardinality_key"], str) or not item[
            "cardinality_key"
        ]:
            _fail("READINESS_REPORT_INVALID", "cardinality key is invalid")
        if item["status"] not in cwm_v2.SLOT_STATUSES:
            _fail("READINESS_REPORT_INVALID", "semantic status is invalid")
        if item["completeness"] not in cwm_v2.SLOT_COMPLETENESS or item[
            "semantic_classification"
        ] not in cwm_v2.SLOT_COMPLETENESS:
            _fail("READINESS_REPORT_INVALID", "semantic completeness is invalid")
        if item["materiality"] not in cwm_v2.MATERIALITY_VALUES:
            _fail("READINESS_REPORT_INVALID", "semantic materiality is invalid")
        for field in (
            "dependency_closure",
            "conflicted_dependency_ids",
            "stale_dependency_ids",
            "incomplete_dependency_ids",
        ):
            _canonical_slot_ids(item[field], field)
        slot_ids.append(item["slot_id"])
    if slot_ids != sorted(set(slot_ids)):
        _fail("READINESS_REPORT_INVALID", "semantic assessment order is invalid")


def _validate_clarification(value: Any) -> None:
    if value is None:
        return
    item = _closed_object(value, _CLARIFICATION_FIELDS, "clarification summary")
    _digest(item["clarification_id"], "clarification identity", "clarification-local-sha256:")
    if not isinstance(item["trigger_slot_id"], str) or not item[
        "trigger_slot_id"
    ]:
        _fail("READINESS_REPORT_INVALID", "clarification trigger is invalid")
    if not isinstance(item["trigger_reason"], str) or not item["trigger_reason"]:
        _fail("READINESS_REPORT_INVALID", "clarification reason is invalid")
    _nonnegative_integer(item["source_global_revision"], "source global revision")
    _nonnegative_integer(item["source_semantic_revision"], "source semantic revision")


def _canonical_slot_ids(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        _fail("READINESS_REPORT_INVALID", f"{name} is invalid")
    normalized = [
        _digest(item, name, "conversation-slot-sha256:") for item in value
    ]
    if normalized != sorted(set(normalized)):
        _fail("READINESS_REPORT_INVALID", f"{name} is not canonical")
    return normalized


def _closed_object(value: Any, fields: frozenset[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        _fail("READINESS_REPORT_INVALID", f"{name} schema fields are invalid")
    return deepcopy(value)


def _nonnegative_integer(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("READINESS_REPORT_INVALID", f"{name} is invalid")
    return value


def _digest(value: Any, name: str, prefix: str) -> str:
    if not isinstance(value, str) or not value.startswith(prefix):
        _fail("READINESS_REPORT_INVALID", f"{name} is invalid")
    suffix = value.removeprefix(prefix)
    if len(suffix) != 64 or any(
        character not in "0123456789abcdef" for character in suffix
    ):
        _fail("READINESS_REPORT_INVALID", f"{name} is invalid")
    return value


def _fail(reason_code: str, message: str) -> None:
    raise ObjectiveReadinessError(reason_code, message)


__all__ = [
    "NOT_READY",
    "OBJECTIVE_READINESS_RULESET_V1",
    "PLATFORM_CORE_CONVERSATION_OBJECTIVE_READINESS_RUNTIME_V2",
    "PLATFORM_CORE_OBJECTIVE_READINESS_REPORT_SCHEMA_V1",
    "READY",
    "ObjectiveReadinessError",
    "evaluate_objective_readiness_v2",
    "require_objective_readiness_v2",
    "validate_objective_readiness_report_v2",
]
