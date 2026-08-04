"""Minimal passive Constitutional Runtime Observatory core (G67-02)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash

from .catalog import ADAPTER_CATALOG_VERSION, CATALOG_BY_ID, catalog_projection
from .topology import CURRENT_STAGES, TOPOLOGY_OVERLAY_VERSION, load_topology_overlay


OBSERVATORY_CORE_VERSION = "G67_02_CONSTITUTIONAL_RUNTIME_OBSERVATORY_CORE_V1"
JOURNEY_ARCHITECTURE_VERSION = (
    "G67_01_CONSTITUTIONAL_RUNTIME_OBSERVATORY_ARCHITECTURE_V1"
)
GAP_PRECEDENCE = (
    "CORRUPTED",
    "AMBIGUOUS",
    "UNSUPPORTED_EVIDENCE",
    "STALE_TOPOLOGY",
    "FAILED",
    "INTENTIONALLY_EXCLUDED",
    "UNCOMPOSED",
    "NOT_APPLICABLE",
    "NOT_REACHED",
    "NOT_RECORDED",
    "NOT_OBSERVED",
    "UNKNOWN",
)
_GAP_FACTS = {
    "CORRUPTED": "corrupted",
    "AMBIGUOUS": "ambiguous",
    "UNSUPPORTED_EVIDENCE": "unsupported_evidence",
    "STALE_TOPOLOGY": "stale_topology",
    "FAILED": "failed",
    "INTENTIONALLY_EXCLUDED": "intentionally_excluded",
    "UNCOMPOSED": "uncomposed",
    "NOT_APPLICABLE": "not_applicable",
    "NOT_REACHED": "not_reached",
    "NOT_RECORDED": "not_recorded",
    "NOT_OBSERVED": "not_observed",
    "UNKNOWN": "unknown",
}


class FrozenDict(dict):
    """JSON-compatible recursively immutable mapping."""

    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("Constitutional Runtime Observatory projections are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return FrozenDict({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def evidence_adapter_catalog_v1() -> FrozenDict:
    """Expose the closed adapter metadata as an immutable passive view."""

    return _freeze(catalog_projection())


def classify_constitutional_runtime_gap_v1(
    *,
    subject: str,
    evidence_references: Iterable[str] = (),
    detail: str | None = None,
    **facts: bool,
) -> FrozenDict:
    """Classify one gap using the exact G67-01 precedence."""

    active = [name for name in GAP_PRECEDENCE if facts.get(_GAP_FACTS[name]) is True]
    classification = active[0] if active else "UNKNOWN"
    result = {
        "gap_type": "CONSTITUTIONAL_RUNTIME_OBSERVATION_GAP_V1",
        "subject": str(subject),
        "classification": classification,
        "matched_classifications": active or ["UNKNOWN"],
        "precedence": list(GAP_PRECEDENCE),
        "detail": detail,
        "evidence_references": sorted(str(item) for item in evidence_references),
        "descriptive_only": True,
        "runtime_event": False,
        "creates_task": False,
        "authorizes_repair": False,
        "authorizes_execution": False,
        "authorizes_mutation": False,
        "grants_authority": False,
    }
    return _freeze(result)


def _inside_scope(path: str | Path, scope: Path) -> Path:
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(scope)
    except ValueError as exc:
        raise FailClosedRuntimeError("observatory evidence path escapes bounded scope") from exc
    if not candidate.exists():
        raise FailClosedRuntimeError("observatory evidence path is absent")
    return candidate


def _artifact(path: Path, principal_file: str | None) -> dict[str, Any]:
    selected = path / principal_file if principal_file else path
    value = load_json(selected)
    if isinstance(value.get("artifact"), dict):
        return value["artifact"]
    return value


def _validate_nested_evidence_references(value: Any, scope: Path) -> None:
    """Reject absolute evidence references that leave the caller's scope."""

    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(item, str) and Path(item).is_absolute() and (
                str(key).endswith(
                    (
                        "_replay_reference",
                        "_record_reference",
                        "_context_reference",
                        "_summary_reference",
                    )
                )
                or key in {"replay_reference", "integration_root"}
            ):
                _inside_scope(item, scope)
            else:
                _validate_nested_evidence_references(item, scope)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _validate_nested_evidence_references(item, scope)


def _event(
    *,
    stage: str,
    owner: str,
    source_type: str,
    source_version: str,
    reference: str,
    artifact_hash: str | None,
    occurrence: int,
    classification: str,
    time_value: str | None = None,
    source_replay_hash: str | None = None,
    source_status_code: str | None = None,
    source_explanation: str | None = None,
    rule_identifier: str | None = None,
    source_confidence: str | None = None,
    source_authority_fields: Mapping[str, Any] | None = None,
    visibility: str = "OWNER_REPLAY_VISIBLE_METADATA_ONLY",
) -> dict[str, Any]:
    seed = {
        "stage": stage,
        "owner": owner,
        "source_type": source_type,
        "source_version": source_version,
        "source_reference": reference,
        "source_artifact_hash": artifact_hash,
        "source_replay_reference": reference,
        "source_replay_hash": source_replay_hash,
        "occurrence": occurrence,
    }
    return {
        "runtime_event_type": "CONSTITUTIONAL_RUNTIME_EVENT_PROJECTION_V1",
        "event_identity": "runtime-event-" + replay_hash(seed),
        **seed,
        "event_classification": classification,
        "time_field": "created_at" if time_value else None,
        "time_value": time_value,
        "validation_result": "OWNER_RECONSTRUCTION_VERIFIED",
        "source_status_code": source_status_code,
        "source_explanation": source_explanation,
        "rule_identifier": rule_identifier,
        "source_confidence": source_confidence or "NOT_APPLICABLE",
        "source_authority_fields": dict(source_authority_fields or {}),
        "authority": "SOURCE_OWNER_RETAINED",
        "visibility_classification": visibility,
        "observation_only": True,
    }


_FLOW_OWNERS = {
    "HUMAN_INTENT_PRECEDENCE": "CONVERSATION_LAYER",
    "INTERPRETER_PROPOSAL": "CONVERSATION_INTERPRETER",
    "PROPOSAL_VALIDATION": "G59_PROPOSAL_VALIDATION",
    "PROPOSAL_COMMIT": "G59_CONVERSATION",
    "REQUEST_CLASSIFICATION": "PLATFORM_QUERY_ROUTER",
    "OWNER_BOUND_CLARIFICATION_CONTINUATION": "G66_CONTINUATION",
    "HUMAN_CONFIRMATION": "HUMAN_AUTHORITY",
    "OBJECTIVE_READINESS": "G59_OBJECTIVE_READINESS",
    "OBJECTIVE_COMMITMENT": "HUMAN_AUTHORITY_PLUS_G59_CONVERSATION",
}


def _flow_events(path: Path, reconstructed: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    flow = reconstructed["production_conversation_flow_binding"]
    events: list[dict[str, Any]] = []
    events.extend(
        (
            _event(
                stage="CONVERSATION",
                owner="G59_CONVERSATION",
                source_type=flow["artifact_type"],
                source_version=flow["flow_architecture_version"],
                reference=reconstructed["replay_reference"],
                artifact_hash=replay_hash(
                    {
                        "conversation_identity": flow["conversation_identity"],
                        "workspace_identity_hash": flow["workspace_identity_hash"],
                    }
                ),
                occurrence=0,
                classification="CONVERSATION_STATE",
                time_value=flow.get("created_at"),
                rule_identifier=flow.get("flow_architecture_version"),
                source_authority_fields=_authority_fields(flow),
            ),
            _event(
                stage="SEMANTIC_SLOTS_CWM",
                owner="G59_CONVERSATION",
                source_type="CONVERSATION_WORKING_MEMORY_STATE_V2",
                source_version="V2",
                reference=reconstructed["replay_reference"],
                artifact_hash=flow["cwm_state_hash"],
                occurrence=flow["cwm_revision"],
                classification="CONVERSATION_STATE",
                time_value=flow.get("created_at"),
                rule_identifier="G59_CWM_V2",
                source_authority_fields=_authority_fields(flow),
            ),
        )
    )
    for occurrence, predecessor in enumerate(flow["ordered_predecessor_references"]):
        reference = Path(predecessor["replay_reference"]).resolve()
        raw = load_json(reference)
        if predecessor["stage"] == "HUMAN_CONFIRMATION":
            candidate = raw.get("state", {}).get("envelope", {}).get(
                "active_objective_candidate_binding"
            )
            if not isinstance(candidate, dict) or candidate.get("review_status") not in {
                "AWAITING_HUMAN_REVIEW",
                "AWAITING_CONFIRMATION",
                "CONFIRMED",
            }:
                raise FailClosedRuntimeError("Candidate Review source state differs")
            events.append(
                _event(
                    stage="CANDIDATE_REVIEW",
                    owner="G59_CONVERSATION",
                    source_type="ACTIVE_OBJECTIVE_CANDIDATE_BINDING_V2",
                    source_version="V2",
                    reference=str(reference),
                    artifact_hash=replay_hash(candidate),
                    occurrence=int(candidate.get("semantic_revision") or 0),
                    classification="DECISION",
                    time_value=raw.get("state", {}).get("envelope", {}).get("updated_at"),
                    source_status_code=candidate.get("review_status"),
                    rule_identifier=candidate.get("candidate_projection_ruleset_version"),
                    source_authority_fields=_authority_fields(raw),
                )
            )
        events.append(
            _event(
                stage=predecessor["stage"],
                owner=_FLOW_OWNERS[predecessor["stage"]],
                source_type=f"PRODUCTION_FLOW_PREDECESSOR:{predecessor['stage']}",
                source_version="G66_FLOW_BINDING_PREDECESSOR_V1",
                reference=str(reference),
                artifact_hash=predecessor["artifact_hash"],
                occurrence=occurrence,
                classification="CONVERSATION",
                time_value=raw.get("created_at") or raw.get("evaluated_at") or raw.get("committed_at"),
                source_status_code=_source_status(raw),
                source_explanation=raw.get("decision_reason_code") or raw.get("failure_reason"),
                rule_identifier=raw.get("readiness_ruleset_version") or raw.get("record_ruleset_version") or raw.get("proposal_ruleset_version"),
                source_confidence=raw.get("confidence"),
                source_authority_fields=_authority_fields(raw),
            )
        )
    events.append(
        _event(
            stage="FLOW_BINDING",
            owner="G66_CONVERSATION_FLOW_BINDING",
            source_type=flow["artifact_type"],
            source_version=flow["flow_architecture_version"],
            reference=reconstructed["replay_reference"],
            artifact_hash=flow["artifact_hash"],
            occurrence=0,
            classification="CORRELATION_BOUNDARY",
            time_value=flow.get("created_at"),
            source_replay_hash=reconstructed.get("reconstruction_hash"),
            source_status_code=flow.get("selection_disposition"),
            source_explanation=flow.get("route_sufficiency_status"),
            rule_identifier=flow.get("flow_architecture_version"),
            source_authority_fields=_authority_fields(flow),
        )
    )
    commitment_raw = load_json(Path(flow["ordered_predecessor_references"][-1]["replay_reference"]))
    return events, {
        "session_id": reconstructed["human_intent_precedence_decision"]["session_identity"],
        "request_identity": flow["request_identity"],
        "request_hash": flow["request_hash"],
        "conversation_identity": flow["conversation_identity"],
        "workspace_identity_hash": flow["workspace_identity_hash"],
        "commitment_identity": commitment_raw.get("commitment_identity"),
        "commitment_record_digest": replay_hash(commitment_raw.get("commitment_record")),
    }


def _preparation_events(path: Path, adapter: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prepared = _artifact(path, adapter.principal_file)
    context = load_json(Path(prepared["platform_core_project_context_reference"]))
    values = {
        "COMMITMENT_HANDOFF": (prepared["commitment_record_digest"], prepared["commitment_record_reference"]),
        "PLATFORM_OBJECTIVE": (prepared["platform_core_objective_hash"], prepared["platform_core_project_context_reference"]),
        "PLATFORM_ADMISSION": (prepared["platform_core_admission_hash"], prepared["platform_core_project_context_reference"]),
        "PRODUCTION_REUSE_PROOF": (context.get("reuse_proof_production_admission_hash"), prepared["platform_core_project_context_reference"]),
        "DEVELOPMENT_GOVERNANCE": (context.get("constitutional_development_governance_hash"), prepared["platform_core_project_context_reference"]),
        "CAPABILITY_ROUTE": (prepared["semantic_capability_route_hash"], prepared["semantic_capability_route_replay_reference"]),
        "EXECUTION_PREPARATION": (prepared["artifact_hash"], str(path)),
        "EXECUTION_SUMMARY": (prepared["execution_summary_hash"], prepared["execution_summary_reference"]),
        "HUMAN_EXECUTION_DECISION": (None, prepared["expected_authorization_action"]),
    }
    owners = {
        "COMMITMENT_HANDOFF": "G60_02_ORCHESTRATION",
        "PLATFORM_OBJECTIVE": "PLATFORM_CORE",
        "PLATFORM_ADMISSION": "PLATFORM_CORE",
        "PRODUCTION_REUSE_PROOF": "G64_REUSE_PROOF",
        "DEVELOPMENT_GOVERNANCE": "G47_DEVELOPMENT_GOVERNANCE",
        "CAPABILITY_ROUTE": "PLATFORM_CAPABILITY_ROUTING",
        "EXECUTION_PREPARATION": "G60_02_ORCHESTRATION",
        "EXECUTION_SUMMARY": "EXECUTION_SUMMARY",
        "HUMAN_EXECUTION_DECISION": "HUMAN_AUTHORITY",
    }
    events = [
        _event(
            stage=stage,
            owner=owners[stage],
            source_type=adapter.source_artifact_type,
            source_version=adapter.source_version,
            reference=str(values[stage][1]),
            artifact_hash=values[stage][0],
            occurrence=0,
            classification=adapter.event_classification,
            time_value=prepared.get("created_at"),
            source_status_code=(
                prepared.get("preparation_status")
                if stage in {"EXECUTION_PREPARATION", "EXECUTION_SUMMARY", "HUMAN_EXECUTION_DECISION"}
                else _source_status(context.get("project_objective_inference", {}) if stage == "PLATFORM_OBJECTIVE" else context.get("admission_precedence", {}) if stage == "PLATFORM_ADMISSION" else context)
            ),
            rule_identifier=adapter.source_version,
            source_authority_fields=_authority_fields(prepared),
        )
        for stage in adapter.stages
    ]
    return events, {
        "session_id": prepared["session_id"],
        "commitment_identity": prepared["commitment_identity"],
        "commitment_record_digest": prepared["commitment_record_digest"],
        "human_actor": prepared["human_actor"],
        "integration_root": prepared["integration_root"],
    }


def _source_status(record: Mapping[str, Any]) -> str | None:
    for key in (
        "certification_status",
        "termination_status",
        "review_status",
        "completion_status",
        "validation_status",
        "result_capture_status",
        "execution_status",
        "invocation_status",
        "dispatch_status",
        "assignment_status",
        "request_status",
        "authorization_status",
        "record_status",
        "readiness_disposition",
        "proposal_validation_disposition",
        "decision_disposition",
        "preparation_status",
    ):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _authority_fields(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in sorted(record)
        if key.endswith(("_authority", "_authorized", "_granted"))
        or key.startswith("authorizes_")
        or key in {"constitutional_authority", "provider_authority"}
        if isinstance(record[key], (bool, str)) or record[key] is None
    }


def _generic_events(path: Path, adapter: Any, capture: Mapping[str, Any]) -> list[dict[str, Any]]:
    artifact = _artifact(path, adapter.principal_file)
    if artifact.get("artifact_type") != adapter.source_artifact_type:
        raise FailClosedRuntimeError("catalog adapter artifact type differs")
    recorded_version = artifact.get("runtime_version")
    if recorded_version is not None and recorded_version != adapter.source_version:
        raise FailClosedRuntimeError("catalog adapter runtime version differs")
    return [
        _event(
            stage=stage,
            owner=adapter.source_owner,
            source_type=str(artifact.get("artifact_type") or adapter.source_artifact_type),
            source_version=str(artifact.get("runtime_version") or adapter.source_version),
            reference=str(path),
            artifact_hash=artifact.get("artifact_hash"),
            occurrence=index,
            classification=adapter.event_classification,
            time_value=artifact.get("created_at") or artifact.get("authorized_at"),
            source_replay_hash=capture.get("replay_hash"),
            source_status_code=_source_status(artifact) or _source_status(capture),
            source_explanation=artifact.get("failure_reason") or artifact.get("decision_reason"),
            rule_identifier=artifact.get("ruleset_version") or artifact.get("runtime_version") or adapter.source_version,
            source_confidence=artifact.get("confidence"),
            source_authority_fields=_authority_fields(artifact),
        )
        for index, stage in enumerate(adapter.stages)
    ]


def _decision_projection(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_type": "CONSTITUTIONAL_RUNTIME_DECISION_PROJECTION_V1",
        "decision_identity": "decision-" + replay_hash(event),
        "stage": event["stage"],
        "owner": event["owner"],
        "subject_reference": event["source_reference"],
        "subject_hash": event["source_artifact_hash"],
        "reason_status_code": event["source_status_code"] or "OWNER_RECORD_VALIDATED",
        "source_explanation": event["source_explanation"],
        "input_state_references": [event["source_reference"]],
        "output_state_references": [event["source_reference"]],
        "evidence_references": [event["source_reference"]],
        "evidence_hashes": [event["source_artifact_hash"]] if event["source_artifact_hash"] else [],
        "rule_identifier": event["rule_identifier"] or event["source_version"],
        "source_confidence": event["source_confidence"],
        "replay_reference": event["source_replay_reference"],
        "replay_absence_classification": None if event["source_replay_reference"] else "NOT_RECORDED",
        "decision_status": "OBSERVED_AND_OWNER_VALIDATED",
        "authority": "SOURCE_OWNER_ONLY",
        "observatory_authority": "NONE",
    }


def _failed_projection(topology: dict[str, Any], gap: FrozenDict) -> FrozenDict:
    body = {
        "journey_type": "CONSTITUTIONAL_HUMAN_INTENT_JOURNEY_PROJECTION_V1",
        "architecture_version": JOURNEY_ARCHITECTURE_VERSION,
        "observatory_core_version": OBSERVATORY_CORE_VERSION,
        "adapter_catalog_version": ADAPTER_CATALOG_VERSION,
        "topology": topology,
        "journey_status": "OBSERVATION_FAILED_CLOSED",
        "runtime_events": [],
        "decisions": [],
        "journey_states": [],
        "correlation_edges": [],
        "gaps": [dict(gap)],
        "terminal_classification": None,
        "read_only": True,
        "persisted": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "grants_authority": False,
        "authorizes_execution": False,
        "authorizes_mutation": False,
        "is_replay_hash": False,
        "is_certification_hash": False,
    }
    body["projection_hash"] = replay_hash(body)
    return _freeze(body)


def build_constitutional_human_intent_journey_v1(
    *,
    evidence_scope_root: str | Path,
    evidence_roots: Iterable[Mapping[str, Any]],
    selector: Mapping[str, str],
    adapter_catalog_version: str = ADAPTER_CATALOG_VERSION,
    topology_version: str = TOPOLOGY_OVERLAY_VERSION,
) -> FrozenDict:
    """Build one immutable, non-authoritative journey from bounded Replay roots."""

    scope = Path(evidence_scope_root).resolve()
    if not scope.is_dir():
        raise FailClosedRuntimeError("observatory evidence scope is not a directory")
    topology = load_topology_overlay(topology_version)
    if adapter_catalog_version != ADAPTER_CATALOG_VERSION:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="adapter_catalog", unsupported_evidence=True, detail="adapter catalog version is unsupported"))
    if not topology["supported"]:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="topology", stale_topology=True, detail="topology overlay version is stale or unsupported"))

    descriptors = []
    for raw in evidence_roots:
        adapter_id = str(raw.get("adapter_id") or "")
        path = _inside_scope(str(raw.get("path") or ""), scope)
        descriptors.append((adapter_id, path))
    if not descriptors:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="journey", not_observed=True, detail="no bounded evidence roots supplied"))
    unknown = [(adapter_id, path) for adapter_id, path in descriptors if adapter_id not in CATALOG_BY_ID]
    if unknown:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject=unknown[0][0], unsupported_evidence=True, evidence_references=[str(unknown[0][1])]))
    for index, (_left_id, left) in enumerate(descriptors):
        for _right_id, right in descriptors[index + 1 :]:
            if left == right or left in right.parents or right in left.parents:
                return _failed_projection(
                    topology,
                    classify_constitutional_runtime_gap_v1(
                        subject="evidence_root_scope",
                        ambiguous=True,
                        evidence_references=[str(left), str(right)],
                        detail="explicit evidence roots overlap",
                    ),
                )
    counts: dict[str, int] = {}
    for adapter_id, _path in descriptors:
        counts[adapter_id] = counts.get(adapter_id, 0) + 1
    duplicates = sorted(key for key, value in counts.items() if value > 1)
    if duplicates:
        refs = [str(path) for key, path in descriptors if key == duplicates[0]]
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject=duplicates[0], ambiguous=True, evidence_references=refs, detail="multiple evidence roots claim one owner occurrence"))

    reconstructed: list[tuple[Any, Path, dict[str, Any]]] = []
    try:
        for adapter_id, path in descriptors:
            adapter = CATALOG_BY_ID[adapter_id]
            if adapter.root_kind == "FILE" and not path.is_file():
                raise FailClosedRuntimeError("adapter requires one exact evidence file")
            if adapter.root_kind == "DIRECTORY" and not path.is_dir():
                raise FailClosedRuntimeError("adapter requires one exact Replay directory")
            if adapter.principal_file is not None or adapter.root_kind == "FILE":
                source = _artifact(path, adapter.principal_file)
                recorded_version = source.get("runtime_version")
                if source.get("artifact_type") != adapter.source_artifact_type or (
                    recorded_version is not None
                    and recorded_version != adapter.source_version
                ):
                    return _failed_projection(
                        topology,
                        classify_constitutional_runtime_gap_v1(
                            subject=adapter.adapter_id,
                            unsupported_evidence=True,
                            evidence_references=[str(path)],
                            detail="source artifact type or version is outside the closed catalog",
                        ),
                    )
            capture = adapter.reconstructor(path)
            _validate_nested_evidence_references(capture, scope)
            if adapter.adapter_id == "G66_FLOW_BINDING":
                flow = capture.get("production_conversation_flow_binding", {})
                if flow.get("artifact_type") != adapter.source_artifact_type or flow.get(
                    "flow_architecture_version"
                ) != adapter.source_version:
                    return _failed_projection(
                        topology,
                        classify_constitutional_runtime_gap_v1(
                            subject=adapter.adapter_id,
                            unsupported_evidence=True,
                            evidence_references=[str(path)],
                        ),
                    )
            reconstructed.append((adapter, path, capture))
    except (FailClosedRuntimeError, KeyError, TypeError, ValueError) as exc:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="owner_reconstruction", corrupted=True, evidence_references=[str(path)], detail=str(exc)))

    events: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    try:
        for adapter, path, capture in reconstructed:
            if adapter.adapter_id == "G66_FLOW_BINDING":
                selected, anchor = _flow_events(path, capture)
                events.extend(selected)
                anchors.append(anchor)
            elif adapter.adapter_id == "G60_EXECUTION_PREPARATION":
                selected, anchor = _preparation_events(path, adapter)
                events.extend(selected)
                anchors.append(anchor)
            else:
                events.extend(_generic_events(path, adapter, capture))
    except (FailClosedRuntimeError, KeyError, TypeError, ValueError) as exc:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="adapter_projection", corrupted=True, detail=str(exc)))

    mapped_stages = set(topology["current_stages"])
    stale_stages = sorted(
        {event["stage"] for event in events if event["stage"] not in mapped_stages}
    )
    if stale_stages:
        return _failed_projection(
            topology,
            classify_constitutional_runtime_gap_v1(
                subject=stale_stages[0],
                stale_topology=True,
                detail="owner-validated stage is absent from the selected topology overlay",
            ),
        )

    if len(anchors) != 2:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="journey_anchor", not_observed=True, detail="flow and execution-preparation anchors are both required"))
    flow_anchor, preparation_anchor = anchors
    if (
        flow_anchor.get("commitment_identity") != preparation_anchor.get("commitment_identity")
        or flow_anchor.get("commitment_record_digest") != preparation_anchor.get("commitment_record_digest")
        or flow_anchor.get("session_id") != preparation_anchor.get("session_id")
    ):
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="cross_owner_commitment_bridge", ambiguous=True, detail="exact commitment/session anchors do not converge"))
    captures = {adapter.adapter_id: capture for adapter, _path, capture in reconstructed}
    try:
        chain = captures["EXECUTION_AUTHORIZATION"]["chain_id"]
        for adapter_id in (
            "WORKER_INVOCATION_REQUEST",
            "WORKER_DISPATCH",
            "WORKER_INVOCATION",
            "RESULT_CAPTURE",
            "RESULT_VALIDATION",
            "POST_EXECUTION_REPLAY_REVIEW",
            "GOVERNED_TERMINATION",
        ):
            if captures[adapter_id]["chain_id"] != chain:
                raise ValueError("cross-owner canonical chain identity differs")
        if captures["WORKER_ASSIGNMENT"]["canonical_chain_id"] != chain:
            raise ValueError("Worker assignment canonical chain identity differs")
        if captures["EXECUTION"]["canonical_chain_id"] != chain:
            raise ValueError("execution canonical chain identity differs")
        exact_links = (
            (captures["EXECUTION_AUTHORIZATION"]["authorization_id"], captures["WORKER_INVOCATION_REQUEST"]["authorization_reference"]),
            (captures["WORKER_INVOCATION_REQUEST"]["worker_invocation_request_id"], captures["WORKER_ASSIGNMENT"]["worker_invocation_request_reference"]),
            (captures["WORKER_ASSIGNMENT"]["worker_assignment_id"], captures["WORKER_DISPATCH"]["worker_assignment_reference"]),
            (captures["WORKER_DISPATCH"]["worker_dispatch_id"], captures["WORKER_INVOCATION"]["worker_dispatch_reference"]),
            (captures["WORKER_INVOCATION"]["worker_invocation_id"], captures["EXECUTION"]["worker_invocation_reference"]),
            (captures["EXECUTION"]["execution_id"], captures["RESULT_CAPTURE"]["execution_reference"]),
            (captures["RESULT_CAPTURE"]["worker_result_capture_id"], captures["RESULT_VALIDATION"]["worker_result_capture_reference"]),
            (captures["RESULT_VALIDATION"]["worker_result_validation_id"], captures["POST_EXECUTION_REPLAY_REVIEW"]["worker_result_validation_reference"]),
            (captures["POST_EXECUTION_REPLAY_REVIEW"]["post_execution_replay_review_id"], captures["GOVERNED_TERMINATION"]["post_execution_replay_review_reference"]),
            (captures["EXECUTION"]["execution_id"], captures["FINAL_EXECUTION_CERTIFICATION"]["source_worker_execution"]),
        )
        if not all(left == right for left, right in exact_links):
            raise ValueError("cross-owner explicit predecessor identity differs")
        prepared_summary = captures["G60_EXECUTION_PREPARATION"]["execution_summary"]["artifact_hash"]
        if prepared_summary != captures["EXECUTION_AUTHORIZATION"]["execution_summary_hash"]:
            raise ValueError("preparation/Authorization summary hash differs")
    except (KeyError, TypeError, ValueError) as exc:
        return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject="cross_owner_correlation", ambiguous=True, detail=str(exc)))
    for key, expected in selector.items():
        actual = {**flow_anchor, **preparation_anchor}.get(key)
        if actual != expected:
            return _failed_projection(topology, classify_constitutional_runtime_gap_v1(subject=f"selector:{key}", not_reached=True, detail="selector does not identify reconstructed journey"))

    order = {stage: index for index, stage in enumerate(CURRENT_STAGES)}
    events.sort(key=lambda item: (order.get(item["stage"], 10_000), item["occurrence"], item["event_identity"]))
    stages = {event["stage"] for event in events}
    gaps = [
        dict(classify_constitutional_runtime_gap_v1(subject="CANONICAL_HUMAN_ENTRY", not_recorded=True, detail="no distinct Canonical Human Entry artifact exists; the first authenticated event is Human Intent precedence")),
        dict(classify_constitutional_runtime_gap_v1(subject="RAW_PROVIDER_CONTENT", intentionally_excluded=True, detail="provider content is excluded by the certified evidence boundary")),
        dict(classify_constitutional_runtime_gap_v1(subject="G64_CONSTITUTIONAL_COMPLETION", uncomposed=True, detail="G31 final execution Certification has no authenticated default bridge to G64 completion")),
        dict(classify_constitutional_runtime_gap_v1(subject="MUTATION_BRANCH", not_applicable=True, detail="the first supported journey is non-mutating")),
    ]
    states = []
    for stage in CURRENT_STAGES:
        observed = stage in stages
        states.append(
            {
                "journey_state_type": "CONSTITUTIONAL_RUNTIME_JOURNEY_STATE_V1",
                "stage": stage,
                "stage_state": "REACHED" if observed else ("NOT_RECORDED" if stage == "CANONICAL_HUMAN_ENTRY" else "NOT_OBSERVED"),
                "outcome_state": "SUCCEEDED" if observed else "UNKNOWN",
                "observation_state": "OWNER_RECONSTRUCTED" if observed else "GAP_CLASSIFIED",
                "dimensions_independent": True,
            }
        )
    decisions = [
        _decision_projection(event)
        for event in events
        if event["stage"] in {"HUMAN_INTENT_PRECEDENCE", "PROPOSAL_VALIDATION", "CANDIDATE_REVIEW", "HUMAN_CONFIRMATION", "OBJECTIVE_READINESS", "OBJECTIVE_COMMITMENT", "PLATFORM_ADMISSION", "DEVELOPMENT_GOVERNANCE", "HUMAN_EXECUTION_DECISION", "EXECUTION_AUTHORIZATION", "RESULT_VALIDATION", "POST_EXECUTION_REPLAY_REVIEW", "GOVERNED_TERMINATION", "FINAL_EXECUTION_CERTIFICATION"}
    ]
    edges = [
        {
            "correlation_type": (
                "EXPLICIT_PREDECESSOR_HASH"
                if left["event_classification"] == "CONVERSATION"
                else "AUTHENTICATED_HANDOFF"
                if left["stage"] == "FLOW_BINDING"
                else "OWNER_VALIDATED_IDENTITY"
            ),
            "from_event_identity": left["event_identity"],
            "to_event_identity": right["event_identity"],
            "cross_owner": left["owner"] != right["owner"],
            "authority": "NONE",
        }
        for left, right in zip(events, events[1:])
    ]
    terminal = next((event for event in reversed(events) if event["stage"] == "FINAL_EXECUTION_CERTIFICATION"), None)
    body = {
        "journey_type": "CONSTITUTIONAL_HUMAN_INTENT_JOURNEY_PROJECTION_V1",
        "architecture_version": JOURNEY_ARCHITECTURE_VERSION,
        "observatory_core_version": OBSERVATORY_CORE_VERSION,
        "adapter_catalog_version": ADAPTER_CATALOG_VERSION,
        "topology": topology,
        "journey_identity": "human-intent-journey-" + replay_hash({"topology": topology_version, "anchor": flow_anchor}),
        "anchor": {**flow_anchor, **preparation_anchor},
        "correlated_identity_aliases": {
            "commitment_identity": flow_anchor["commitment_identity"],
            "canonical_chain_identity": captures["EXECUTION_AUTHORIZATION"]["chain_id"],
            "conversation_identity": flow_anchor["conversation_identity"],
        },
        "evidence_root_scope": str(scope),
        "journey_status": "OBSERVED_THROUGH_FINAL_EXECUTION_CERTIFICATION" if terminal else "OBSERVED_INCOMPLETE",
        "runtime_events": events,
        "decisions": decisions,
        "journey_states": states,
        "correlation_edges": edges,
        "branches": [{"branch": "NON_MUTATING_CAPABILITY", "selected": True}, {"branch": "MUTATION", "selected": False}],
        "gaps": gaps,
        "terminal_classification": "FINAL_EXECUTION_CERTIFIED" if terminal else None,
        "source_references": sorted(str(path) for _adapter_id, path in descriptors),
        "validation_summary": {
            "owner_reconstructors_passed": len(reconstructed),
            "runtime_events_projected": len(events),
            "decisions_projected": len(decisions),
            "correlation_edges_admitted": len(edges),
            "cycles_detected": 0,
            "ambiguous_successors": 0,
            "static_topology_proved_traversal": False,
        },
        "read_only": True,
        "persisted": False,
        "provider_invoked": False,
        "observatory_worker_invoked": False,
        "grants_authority": False,
        "authorizes_execution": False,
        "authorizes_mutation": False,
        "admissible_as_predecessor": False,
        "is_replay_hash": False,
        "is_certification_hash": False,
    }
    body["projection_hash"] = replay_hash(body)
    return _freeze(body)
