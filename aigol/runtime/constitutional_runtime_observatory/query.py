"""Canonical passive query interface over an existing G67-02 Journey."""

from __future__ import annotations

from typing import Any, Mapping, TypeVar

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


QUERY_INTERFACE_VERSION = (
    "G67_03_CONSTITUTIONAL_RUNTIME_OBSERVATORY_QUERY_INTERFACE_V1"
)
QUERY_CONTRACT_VERSION = "CONSTITUTIONAL_RUNTIME_OBSERVATORY_QUERY_CONTRACT_V1"
SUPPORTED_JOURNEY_TYPE = "CONSTITUTIONAL_HUMAN_INTENT_JOURNEY_PROJECTION_V1"


class _FrozenQueryValue(dict):
    """Recursively immutable JSON-compatible query value."""

    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("Constitutional Runtime Observatory query values are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable

    def as_dict(self) -> dict[str, Any]:
        """Return a detached JSON-compatible copy for a presentation adapter."""

        return _plain(self)


class JourneySummary(_FrozenQueryValue):
    """Stable Journey summary query contract."""


class JourneyEvent(_FrozenQueryValue):
    """Stable source-owner Runtime Event query contract."""


class JourneyDecision(_FrozenQueryValue):
    """Stable source-owner Decision query contract."""


class JourneyState(_FrozenQueryValue):
    """Stable three-dimensional Journey State query contract."""


class JourneyGap(_FrozenQueryValue):
    """Stable descriptive Journey Gap query contract."""


class JourneyTimeline(_FrozenQueryValue):
    """Stable ordered event/gap timeline query contract."""


class JourneyOwnerMap(_FrozenQueryValue):
    """Stable source-owner occurrence query contract."""


class JourneyValidationSummary(_FrozenQueryValue):
    """Stable source/query validation summary contract."""


class JourneyMetadata(_FrozenQueryValue):
    """Stable non-authoritative Journey metadata contract."""


class JourneyTopology(_FrozenQueryValue):
    """Stable sanitized topology query contract."""


class JourneyEvidenceReferences(_FrozenQueryValue):
    """Stable source evidence-reference query contract."""


class JourneyTerminalState(_FrozenQueryValue):
    """Stable terminal-state query contract."""


_Record = TypeVar("_Record", bound=_FrozenQueryValue)


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _FrozenQueryValue(
            {str(key): _freeze(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _record(record_type: type[_Record], values: Mapping[str, Any]) -> _Record:
    return record_type({str(key): _freeze(value) for key, value in values.items()})


def _query_header(contract: str) -> dict[str, Any]:
    return {
        "query_contract": contract,
        "query_contract_version": QUERY_CONTRACT_VERSION,
        "query_interface_version": QUERY_INTERFACE_VERSION,
        "read_only": True,
        "grants_authority": False,
    }


def _sequence(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"Journey {label} must be an ordered sequence")
    result = []
    for item in value:
        if not isinstance(item, Mapping):
            raise FailClosedRuntimeError(f"Journey {label} entries must be objects")
        result.append(_plain(item))
    return result


def _validate_and_snapshot(journey_projection: Mapping[str, Any]) -> _FrozenQueryValue:
    if not isinstance(journey_projection, Mapping):
        raise FailClosedRuntimeError("Journey projection must be an object")
    snapshot = _plain(journey_projection)
    required = {
        "journey_type",
        "architecture_version",
        "observatory_core_version",
        "adapter_catalog_version",
        "topology",
        "journey_status",
        "runtime_events",
        "decisions",
        "journey_states",
        "gaps",
        "terminal_classification",
        "validation_summary",
        "projection_hash",
        "read_only",
        "persisted",
        "grants_authority",
        "authorizes_execution",
        "authorizes_mutation",
        "admissible_as_predecessor",
        "is_replay_hash",
        "is_certification_hash",
    }
    missing = sorted(required - set(snapshot))
    if missing:
        raise FailClosedRuntimeError(
            "Journey projection lacks required query fields: " + ", ".join(missing)
        )
    if snapshot["journey_type"] != SUPPORTED_JOURNEY_TYPE:
        raise FailClosedRuntimeError("Journey projection type is unsupported")
    if (
        snapshot["read_only"] is not True
        or snapshot["persisted"] is not False
        or snapshot["grants_authority"] is not False
        or snapshot["authorizes_execution"] is not False
        or snapshot["authorizes_mutation"] is not False
        or snapshot["admissible_as_predecessor"] is not False
        or snapshot["is_replay_hash"] is not False
        or snapshot["is_certification_hash"] is not False
    ):
        raise FailClosedRuntimeError("Journey projection violates passive query boundary")
    for field in ("runtime_events", "decisions", "journey_states", "gaps"):
        _sequence(snapshot[field], field)
    if not isinstance(snapshot["topology"], dict):
        raise FailClosedRuntimeError("Journey topology must be an object")
    if not isinstance(snapshot["validation_summary"], dict):
        raise FailClosedRuntimeError("Journey validation summary must be an object")
    actual_hash = snapshot.pop("projection_hash")
    if actual_hash != replay_hash(snapshot):
        raise FailClosedRuntimeError("Journey projection hash differs")
    snapshot["projection_hash"] = actual_hash
    return _freeze(snapshot)


def _event_view(event: Mapping[str, Any]) -> JourneyEvent:
    return _record(
        JourneyEvent,
        {
            **_query_header("JOURNEY_EVENT_V1"),
            "event_identity": event.get("event_identity"),
            "stage": event.get("stage"),
            "occurrence": event.get("occurrence"),
            "owner": event.get("owner"),
            "classification": event.get("event_classification"),
            "status_code": event.get("source_status_code"),
            "timestamp_field": event.get("time_field"),
            "timestamp_value": event.get("time_value"),
            "source_artifact_type": event.get("source_type"),
            "source_artifact_version": event.get("source_version"),
            "source_reference": event.get("source_reference"),
            "source_artifact_hash": event.get("source_artifact_hash"),
            "source_replay_reference": event.get("source_replay_reference"),
            "source_replay_hash": event.get("source_replay_hash"),
            "authority_classification": event.get("authority"),
            "source_authority_fields": event.get("source_authority_fields", {}),
            "visibility_classification": event.get("visibility_classification"),
            "validation_result": event.get("validation_result"),
        },
    )


def _decision_view(decision: Mapping[str, Any]) -> JourneyDecision:
    return _record(
        JourneyDecision,
        {
            **_query_header("JOURNEY_DECISION_V1"),
            "decision_identity": decision.get("decision_identity"),
            "stage": decision.get("stage"),
            "owner": decision.get("owner"),
            "reason_status_code": decision.get("reason_status_code"),
            "source_explanation": decision.get("source_explanation"),
            "input_state_references": decision.get("input_state_references", []),
            "output_state_references": decision.get("output_state_references", []),
            "evidence_references": decision.get("evidence_references", []),
            "evidence_hashes": decision.get("evidence_hashes", []),
            "rule_identifier": decision.get("rule_identifier"),
            "source_confidence": decision.get("source_confidence"),
            "replay_reference": decision.get("replay_reference"),
            "replay_absence_classification": decision.get(
                "replay_absence_classification"
            ),
            "decision_status": decision.get("decision_status"),
            "observatory_authority": decision.get("observatory_authority"),
        },
    )


def _state_view(state: Mapping[str, Any]) -> JourneyState:
    return _record(
        JourneyState,
        {
            **_query_header("JOURNEY_STATE_V1"),
            "stage": state.get("stage"),
            "stage_state": state.get("stage_state"),
            "outcome_state": state.get("outcome_state"),
            "observation_state": state.get("observation_state"),
            "dimensions_independent": state.get("dimensions_independent"),
        },
    )


def _gap_view(gap: Mapping[str, Any]) -> JourneyGap:
    return _record(
        JourneyGap,
        {
            **_query_header("JOURNEY_GAP_V1"),
            "subject": gap.get("subject"),
            "classification": gap.get("classification"),
            "matched_classifications": gap.get("matched_classifications", []),
            "detail": gap.get("detail"),
            "evidence_references": gap.get("evidence_references", []),
            "descriptive_only": gap.get("descriptive_only"),
            "runtime_event": gap.get("runtime_event"),
            "creates_task": gap.get("creates_task"),
            "authorizes_repair": gap.get("authorizes_repair"),
        },
    )


class Journey:
    """Single stable query mechanism over one immutable G67-02 Journey snapshot."""

    __slots__ = ("__snapshot",)

    def __init__(self, snapshot: _FrozenQueryValue) -> None:
        self.__snapshot = snapshot

    def get_summary(self) -> JourneySummary:
        events = self.get_events()
        decisions = self.get_decisions()
        states = self.get_states()
        gaps = self.get_gaps()
        terminal = self.get_terminal_state()
        current = self.get_current_state()
        return _record(
            JourneySummary,
            {
                **_query_header("JOURNEY_SUMMARY_V1"),
                "journey_identity": self.__snapshot.get("journey_identity"),
                "journey_status": self.__snapshot["journey_status"],
                "event_count": len(events),
                "decision_count": len(decisions),
                "state_count": len(states),
                "gap_count": len(gaps),
                "current_stage": current.get("stage"),
                "terminal_reached": terminal["terminal_reached"],
                "terminal_classification": terminal["terminal_classification"],
            },
        )

    def get_events(self) -> tuple[JourneyEvent, ...]:
        return tuple(
            _event_view(event)
            for event in _sequence(self.__snapshot["runtime_events"], "runtime_events")
        )

    def get_decisions(self) -> tuple[JourneyDecision, ...]:
        return tuple(
            _decision_view(decision)
            for decision in _sequence(self.__snapshot["decisions"], "decisions")
        )

    def get_states(self) -> tuple[JourneyState, ...]:
        return tuple(
            _state_view(state)
            for state in _sequence(self.__snapshot["journey_states"], "journey_states")
        )

    def get_gaps(self) -> tuple[JourneyGap, ...]:
        return tuple(
            _gap_view(gap)
            for gap in _sequence(self.__snapshot["gaps"], "gaps")
        )

    def get_timeline(self) -> JourneyTimeline:
        entries: list[dict[str, Any]] = []
        for position, event in enumerate(self.get_events()):
            entries.append(
                {
                    "position": position,
                    "entry_kind": "RUNTIME_EVENT",
                    "identity": event["event_identity"],
                    "stage_or_subject": event["stage"],
                    "owner": event["owner"],
                    "status_or_classification": event["status_code"],
                    "timestamp_value": event["timestamp_value"],
                    "proves_runtime_traversal": True,
                }
            )
        offset = len(entries)
        for index, gap in enumerate(self.get_gaps()):
            entries.append(
                {
                    "position": offset + index,
                    "entry_kind": "DESCRIPTIVE_GAP",
                    "identity": None,
                    "stage_or_subject": gap["subject"],
                    "owner": None,
                    "status_or_classification": gap["classification"],
                    "timestamp_value": None,
                    "proves_runtime_traversal": False,
                }
            )
        return _record(
            JourneyTimeline,
            {
                **_query_header("JOURNEY_TIMELINE_V1"),
                "journey_identity": self.__snapshot.get("journey_identity"),
                "entries": entries,
            },
        )

    def get_current_state(self) -> JourneyState:
        events = self.get_events()
        if not events:
            return _record(
                JourneyState,
                {
                    **_query_header("JOURNEY_STATE_V1"),
                    "stage": None,
                    "stage_state": "NOT_OBSERVED",
                    "outcome_state": "UNKNOWN",
                    "observation_state": "NO_OBSERVED_RUNTIME_EVENT",
                    "dimensions_independent": True,
                },
            )
        current_stage = events[-1]["stage"]
        matches = [state for state in self.get_states() if state["stage"] == current_stage]
        if len(matches) != 1:
            raise FailClosedRuntimeError(
                "Journey current stage lacks one exact state occurrence"
            )
        return matches[0]

    def get_terminal_state(self) -> JourneyTerminalState:
        terminal_events = [
            event
            for event in self.get_events()
            if event["stage"] == "FINAL_EXECUTION_CERTIFICATION"
        ]
        classification = self.__snapshot.get("terminal_classification")
        if len(terminal_events) > 1:
            raise FailClosedRuntimeError("Journey has ambiguous terminal occurrences")
        if bool(terminal_events) != (classification is not None):
            raise FailClosedRuntimeError("Journey terminal event/classification differs")
        event = terminal_events[0] if terminal_events else None
        return _record(
            JourneyTerminalState,
            {
                **_query_header("JOURNEY_TERMINAL_STATE_V1"),
                "terminal_reached": event is not None,
                "terminal_classification": classification,
                "terminal_event_identity": event.get("event_identity") if event else None,
                "terminal_stage": event.get("stage") if event else None,
                "terminal_owner": event.get("owner") if event else None,
            },
        )

    def get_owner_map(self) -> JourneyOwnerMap:
        owners: dict[str, dict[str, Any]] = {}
        for event in self.get_events():
            owner = str(event["owner"])
            entry = owners.setdefault(
                owner,
                {"owner": owner, "event_identities": [], "decision_identities": []},
            )
            entry["event_identities"].append(event["event_identity"])
        for decision in self.get_decisions():
            owner = str(decision["owner"])
            entry = owners.setdefault(
                owner,
                {"owner": owner, "event_identities": [], "decision_identities": []},
            )
            entry["decision_identities"].append(decision["decision_identity"])
        rows = []
        for owner in sorted(owners):
            row = owners[owner]
            row["event_identities"] = sorted(row["event_identities"])
            row["decision_identities"] = sorted(row["decision_identities"])
            rows.append(row)
        return _record(
            JourneyOwnerMap,
            {
                **_query_header("JOURNEY_OWNER_MAP_V1"),
                "owners": rows,
                "owner_count": len(rows),
                "observatory_owner_added": False,
            },
        )

    def get_validation_summary(self) -> JourneyValidationSummary:
        return _record(
            JourneyValidationSummary,
            {
                **_query_header("JOURNEY_VALIDATION_SUMMARY_V1"),
                "source_validation_summary": self.__snapshot["validation_summary"],
                "query_projection_hash_verified": True,
                "query_reconstructed_owner_evidence": False,
                "query_rebuilt_journey": False,
                "query_invoked_runtime": False,
            },
        )

    def get_metadata(self) -> JourneyMetadata:
        return _record(
            JourneyMetadata,
            {
                **_query_header("JOURNEY_METADATA_V1"),
                "journey_identity": self.__snapshot.get("journey_identity"),
                "journey_status": self.__snapshot["journey_status"],
                "architecture_version": self.__snapshot["architecture_version"],
                "observatory_core_version": self.__snapshot[
                    "observatory_core_version"
                ],
                "topology_version": self.__snapshot["topology"].get(
                    "topology_overlay_version"
                ),
                "source_projection_hash": self.__snapshot["projection_hash"],
                "source_projection_hash_kind": "RESPONSE_IDENTITY_ONLY",
                "adapter_neutral": True,
                "future_adapter_classes": [
                    "CLI",
                    "GUI",
                    "REST",
                    "BROWSER",
                    "SPEECH",
                    "NATURAL_CONVERSATION",
                    "AGENT_TO_AGENT",
                ],
                "future_adapters_require_query_interface_change": False,
                "future_adapters_require_separate_implementation": True,
                "persisted": False,
                "admissible_as_runtime_predecessor": False,
            },
        )

    def get_topology(self) -> JourneyTopology:
        source = self.__snapshot["topology"]
        observed_stages = [event["stage"] for event in self.get_events()]
        return _record(
            JourneyTopology,
            {
                **_query_header("JOURNEY_TOPOLOGY_V1"),
                "topology_version": source.get("topology_overlay_version"),
                "g65_map_version": source.get("g65_map_version"),
                "map_semantics": source.get("map_semantics", {}),
                "observed_stages": observed_stages,
                "known_uncomposed_edges": source.get("known_uncomposed_edges", []),
                "static_topology_proves_runtime_traversal": False,
                "runtime_registry": False,
            },
        )

    def get_evidence_references(self) -> JourneyEvidenceReferences:
        event_evidence = [
            {
                "event_identity": event["event_identity"],
                "source_reference": event["source_reference"],
                "source_artifact_hash": event["source_artifact_hash"],
                "source_replay_reference": event["source_replay_reference"],
                "source_replay_hash": event["source_replay_hash"],
            }
            for event in self.get_events()
        ]
        return _record(
            JourneyEvidenceReferences,
            {
                **_query_header("JOURNEY_EVIDENCE_REFERENCES_V1"),
                "evidence_root_scope": self.__snapshot.get("evidence_root_scope"),
                "source_references": self.__snapshot.get("source_references", []),
                "event_evidence": event_evidence,
                "source_content_included": False,
            },
        )


def build_journey(*, journey_projection: Mapping[str, Any]) -> Journey:
    """Validate and privately snapshot one existing G67-02 Journey projection."""

    return Journey(_validate_and_snapshot(journey_projection))


__all__ = [
    "QUERY_INTERFACE_VERSION",
    "QUERY_CONTRACT_VERSION",
    "Journey",
    "JourneySummary",
    "JourneyEvent",
    "JourneyDecision",
    "JourneyState",
    "JourneyGap",
    "JourneyTimeline",
    "JourneyOwnerMap",
    "JourneyValidationSummary",
    "JourneyMetadata",
    "JourneyTopology",
    "JourneyEvidenceReferences",
    "JourneyTerminalState",
    "build_journey",
]
