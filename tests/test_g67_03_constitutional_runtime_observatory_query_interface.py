from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest

from aigol.runtime.constitutional_runtime_observatory import (
    ADAPTER_CATALOG_VERSION,
    QUERY_CONTRACT_VERSION,
    QUERY_INTERFACE_VERSION,
    TOPOLOGY_OVERLAY_VERSION,
    Journey,
    JourneyDecision,
    JourneyEvent,
    JourneyEvidenceReferences,
    JourneyGap,
    JourneyMetadata,
    JourneyOwnerMap,
    JourneyState,
    JourneySummary,
    JourneyTerminalState,
    JourneyTimeline,
    JourneyTopology,
    JourneyValidationSummary,
    build_constitutional_human_intent_journey_v1,
    build_journey,
    evidence_adapter_catalog_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


def _event(
    identity: str,
    stage: str,
    owner: str,
    occurrence: int,
    timestamp: str,
) -> dict:
    return {
        "runtime_event_type": "CONSTITUTIONAL_RUNTIME_EVENT_PROJECTION_V1",
        "event_identity": identity,
        "stage": stage,
        "owner": owner,
        "source_type": f"{stage}_ARTIFACT_V1",
        "source_version": "V1",
        "source_reference": f"/bounded/{identity}.json",
        "source_artifact_hash": replay_hash({"event": identity}),
        "source_replay_reference": f"/bounded/{identity}",
        "source_replay_hash": replay_hash({"replay": identity}),
        "occurrence": occurrence,
        "event_classification": "DECISION" if occurrence == 0 else "CERTIFICATION",
        "time_field": "created_at",
        "time_value": timestamp,
        "validation_result": "OWNER_RECONSTRUCTION_VERIFIED",
        "source_status_code": "ADMITTED" if occurrence == 0 else "CERTIFIED",
        "source_explanation": None,
        "rule_identifier": "SOURCE_RULE_V1",
        "source_confidence": "NOT_APPLICABLE",
        "source_authority_fields": {"constitutional_authority": False},
        "authority": "SOURCE_OWNER_RETAINED",
        "visibility_classification": "OWNER_REPLAY_VISIBLE_METADATA_ONLY",
        "observation_only": True,
    }


def _projection() -> dict:
    events = [
        _event(
            "runtime-event-human-intent",
            "HUMAN_INTENT_PRECEDENCE",
            "CONVERSATION_LAYER",
            0,
            "2026-08-04T14:00:00Z",
        ),
        _event(
            "runtime-event-certification",
            "FINAL_EXECUTION_CERTIFICATION",
            "FINAL_EXECUTION_CERTIFICATION",
            1,
            "2026-08-04T14:00:01Z",
        ),
    ]
    decisions = [
        {
            "decision_type": "CONSTITUTIONAL_RUNTIME_DECISION_PROJECTION_V1",
            "decision_identity": "decision-human-intent",
            "stage": "HUMAN_INTENT_PRECEDENCE",
            "owner": "CONVERSATION_LAYER",
            "subject_reference": events[0]["source_reference"],
            "subject_hash": events[0]["source_artifact_hash"],
            "reason_status_code": "NEW_HUMAN_INTENT",
            "source_explanation": "NO_ACTIVE_CLARIFICATION_STATE",
            "input_state_references": [events[0]["source_reference"]],
            "output_state_references": [events[0]["source_reference"]],
            "evidence_references": [events[0]["source_reference"]],
            "evidence_hashes": [events[0]["source_artifact_hash"]],
            "rule_identifier": "HUMAN_INTENT_PRECEDENCE_V1",
            "source_confidence": "NOT_APPLICABLE",
            "replay_reference": events[0]["source_replay_reference"],
            "replay_absence_classification": None,
            "decision_status": "OBSERVED_AND_OWNER_VALIDATED",
            "authority": "SOURCE_OWNER_ONLY",
            "observatory_authority": "NONE",
        }
    ]
    states = [
        {
            "journey_state_type": "CONSTITUTIONAL_RUNTIME_JOURNEY_STATE_V1",
            "stage": "HUMAN_INTENT_PRECEDENCE",
            "stage_state": "REACHED",
            "outcome_state": "SUCCEEDED",
            "observation_state": "OWNER_RECONSTRUCTED",
            "dimensions_independent": True,
        },
        {
            "journey_state_type": "CONSTITUTIONAL_RUNTIME_JOURNEY_STATE_V1",
            "stage": "FINAL_EXECUTION_CERTIFICATION",
            "stage_state": "REACHED",
            "outcome_state": "SUCCEEDED",
            "observation_state": "OWNER_RECONSTRUCTED",
            "dimensions_independent": True,
        },
    ]
    gaps = [
        {
            "gap_type": "CONSTITUTIONAL_RUNTIME_OBSERVATION_GAP_V1",
            "subject": "G64_CONSTITUTIONAL_COMPLETION",
            "classification": "UNCOMPOSED",
            "matched_classifications": ["UNCOMPOSED"],
            "precedence": ["UNCOMPOSED", "UNKNOWN"],
            "detail": "No authenticated default bridge.",
            "evidence_references": [],
            "descriptive_only": True,
            "runtime_event": False,
            "creates_task": False,
            "authorizes_repair": False,
            "authorizes_execution": False,
            "authorizes_mutation": False,
            "grants_authority": False,
        }
    ]
    body = {
        "journey_type": "CONSTITUTIONAL_HUMAN_INTENT_JOURNEY_PROJECTION_V1",
        "architecture_version": (
            "G67_01_CONSTITUTIONAL_RUNTIME_OBSERVATORY_ARCHITECTURE_V1"
        ),
        "observatory_core_version": (
            "G67_02_CONSTITUTIONAL_RUNTIME_OBSERVATORY_CORE_V1"
        ),
        "adapter_catalog_version": ADAPTER_CATALOG_VERSION,
        "topology": {
            "topology_overlay_version": TOPOLOGY_OVERLAY_VERSION,
            "g65_map_version": (
                "G65_10_CONSTITUTIONAL_NERVOUS_SYSTEM_STATIC_MAP_V1"
            ),
            "g65_map_hash": replay_hash({"map": "G65"}),
            "map_semantics": {
                "descriptive_only": True,
                "runtime_registry": False,
                "grants_authority": False,
                "authorizes_execution": False,
                "authorizes_mutation": False,
                "static_reconstruction_only": True,
                "exhaustive_dynamic_reachability_claimed": False,
            },
            "current_stages": [
                "HUMAN_INTENT_PRECEDENCE",
                "FINAL_EXECUTION_CERTIFICATION",
            ],
            "known_uncomposed_edges": [
                {
                    "from": "FINAL_EXECUTION_CERTIFICATION",
                    "to": "G64_CONSTITUTIONAL_COMPLETION",
                    "gap_classification": "UNCOMPOSED",
                    "correlated": False,
                }
            ],
        },
        "journey_identity": "human-intent-journey-query-fixture",
        "anchor": {"request_identity": "human-intent-query-fixture"},
        "correlated_identity_aliases": {
            "canonical_chain_identity": "CHAIN-G67-03-000001"
        },
        "evidence_root_scope": "/bounded",
        "journey_status": "OBSERVED_THROUGH_FINAL_EXECUTION_CERTIFICATION",
        "runtime_events": events,
        "decisions": decisions,
        "journey_states": states,
        "correlation_edges": [
            {
                "correlation_type": "OWNER_VALIDATED_IDENTITY",
                "from_event_identity": events[0]["event_identity"],
                "to_event_identity": events[1]["event_identity"],
                "cross_owner": True,
                "authority": "NONE",
            }
        ],
        "branches": [
            {"branch": "NON_MUTATING_CAPABILITY", "selected": True}
        ],
        "gaps": gaps,
        "terminal_classification": "FINAL_EXECUTION_CERTIFIED",
        "source_references": ["/bounded/root-a", "/bounded/root-b"],
        "validation_summary": {
            "owner_reconstructors_passed": 2,
            "runtime_events_projected": 2,
            "decisions_projected": 1,
            "correlation_edges_admitted": 1,
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
    return body


def test_build_journey_exposes_one_stable_query_boundary() -> None:
    journey = build_journey(journey_projection=_projection())
    assert isinstance(journey, Journey)
    assert not hasattr(journey, "adapter_catalog")
    assert not hasattr(journey, "correlation_engine")
    assert not hasattr(journey, "projection")
    assert journey.get_metadata()["query_interface_version"] == QUERY_INTERFACE_VERSION
    assert journey.get_metadata()["query_contract_version"] == QUERY_CONTRACT_VERSION


def test_summary_events_and_decisions_are_stable_read_only_contracts() -> None:
    journey = build_journey(journey_projection=_projection())
    summary = journey.get_summary()
    events = journey.get_events()
    decisions = journey.get_decisions()
    assert isinstance(summary, JourneySummary)
    assert all(isinstance(event, JourneyEvent) for event in events)
    assert all(isinstance(decision, JourneyDecision) for decision in decisions)
    assert summary["event_count"] == 2
    assert summary["decision_count"] == 1
    assert events[0]["owner"] == "CONVERSATION_LAYER"
    assert decisions[0]["reason_status_code"] == "NEW_HUMAN_INTENT"
    with pytest.raises(TypeError):
        events[0]["owner"] = "OBSERVATORY"


def test_states_current_state_and_terminal_state_remain_distinct() -> None:
    journey = build_journey(journey_projection=_projection())
    states = journey.get_states()
    current = journey.get_current_state()
    terminal = journey.get_terminal_state()
    assert all(isinstance(state, JourneyState) for state in states)
    assert isinstance(terminal, JourneyTerminalState)
    assert current["stage"] == "FINAL_EXECUTION_CERTIFICATION"
    assert current["stage_state"] == "REACHED"
    assert current["outcome_state"] == "SUCCEEDED"
    assert current["observation_state"] == "OWNER_RECONSTRUCTED"
    assert terminal["terminal_reached"] is True
    assert terminal["terminal_owner"] == "FINAL_EXECUTION_CERTIFICATION"


def test_gaps_and_timeline_do_not_turn_gaps_into_runtime_traversal() -> None:
    journey = build_journey(journey_projection=_projection())
    gaps = journey.get_gaps()
    timeline = journey.get_timeline()
    assert all(isinstance(gap, JourneyGap) for gap in gaps)
    assert isinstance(timeline, JourneyTimeline)
    assert gaps[0]["classification"] == "UNCOMPOSED"
    assert timeline["entries"][-1]["entry_kind"] == "DESCRIPTIVE_GAP"
    assert timeline["entries"][-1]["proves_runtime_traversal"] is False


def test_owner_map_and_evidence_references_preserve_source_owners() -> None:
    journey = build_journey(journey_projection=_projection())
    owners = journey.get_owner_map()
    evidence = journey.get_evidence_references()
    assert isinstance(owners, JourneyOwnerMap)
    assert isinstance(evidence, JourneyEvidenceReferences)
    assert owners["observatory_owner_added"] is False
    assert {row["owner"] for row in owners["owners"]} == {
        "CONVERSATION_LAYER",
        "FINAL_EXECUTION_CERTIFICATION",
    }
    assert evidence["source_content_included"] is False
    assert evidence["source_references"] == ("/bounded/root-a", "/bounded/root-b")


def test_validation_metadata_and_topology_hide_internal_implementations() -> None:
    journey = build_journey(journey_projection=_projection())
    validation = journey.get_validation_summary()
    metadata = journey.get_metadata()
    topology = journey.get_topology()
    assert isinstance(validation, JourneyValidationSummary)
    assert isinstance(metadata, JourneyMetadata)
    assert isinstance(topology, JourneyTopology)
    assert validation["query_projection_hash_verified"] is True
    assert validation["query_reconstructed_owner_evidence"] is False
    assert "adapter_catalog_version" not in metadata
    assert "g65_map_hash" not in topology
    assert "current_stages" not in topology
    assert topology["runtime_registry"] is False


def test_repeated_queries_are_deterministic_and_json_serializable() -> None:
    journey = build_journey(journey_projection=_projection())
    first = {
        "summary": journey.get_summary().as_dict(),
        "events": [event.as_dict() for event in journey.get_events()],
        "timeline": journey.get_timeline().as_dict(),
        "metadata": journey.get_metadata().as_dict(),
    }
    second = {
        "summary": journey.get_summary().as_dict(),
        "events": [event.as_dict() for event in journey.get_events()],
        "timeline": journey.get_timeline().as_dict(),
        "metadata": journey.get_metadata().as_dict(),
    }
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_query_takes_private_snapshot_and_never_changes_source_journey() -> None:
    source = _projection()
    original = json.loads(json.dumps(source, sort_keys=True))
    journey = build_journey(journey_projection=source)
    source["runtime_events"][0]["owner"] = "TAMPERED_AFTER_BUILD"
    assert journey.get_events()[0]["owner"] == "CONVERSATION_LAYER"
    original["runtime_events"][0]["owner"] = "TAMPERED_AFTER_BUILD"
    assert source == original


def test_query_invokes_no_builder_reconstructor_loader_writer_or_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import aigol.runtime.constitutional_runtime_observatory.core as core
    import aigol.runtime.transport.serialization as serialization

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forbidden runtime/evidence API invoked")

    monkeypatch.setattr(core, "build_constitutional_human_intent_journey_v1", forbidden)
    monkeypatch.setattr(serialization, "load_json", forbidden)
    monkeypatch.setattr(serialization, "write_json_immutable", forbidden)
    journey = build_journey(journey_projection=_projection())
    journey.get_summary()
    journey.get_events()
    journey.get_decisions()
    journey.get_states()
    journey.get_gaps()
    journey.get_timeline()
    journey.get_current_state()
    journey.get_terminal_state()
    journey.get_owner_map()
    journey.get_validation_summary()
    journey.get_metadata()
    journey.get_topology()
    journey.get_evidence_references()


def test_tampered_or_authority_shaped_projection_fails_closed() -> None:
    tampered = _projection()
    tampered["journey_status"] = "TAMPERED"
    with pytest.raises(FailClosedRuntimeError, match="projection hash"):
        build_journey(journey_projection=tampered)
    authority = _projection()
    authority["authorizes_execution"] = True
    authority["projection_hash"] = replay_hash(
        {key: value for key, value in authority.items() if key != "projection_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="passive query boundary"):
        build_journey(journey_projection=authority)


def test_future_adapter_contract_is_channel_neutral_without_adapters() -> None:
    metadata = build_journey(journey_projection=_projection()).get_metadata()
    assert metadata["adapter_neutral"] is True
    assert set(metadata["future_adapter_classes"]) == {
        "CLI",
        "GUI",
        "REST",
        "BROWSER",
        "SPEECH",
        "NATURAL_CONVERSATION",
        "AGENT_TO_AGENT",
    }
    assert metadata["future_adapters_require_query_interface_change"] is False
    assert metadata["future_adapters_require_separate_implementation"] is True


def test_g67_02_api_and_catalog_remain_compatible() -> None:
    assert callable(build_constitutional_human_intent_journey_v1)
    assert evidence_adapter_catalog_v1()["catalog_version"] == ADAPTER_CATALOG_VERSION


def test_real_g67_02_journey_is_consumed_without_query_side_reconstruction(
    tmp_path: Path,
) -> None:
    helper = runpy.run_path(
        str(
            Path(__file__).resolve().parent
            / "test_g67_02_constitutional_runtime_observatory_core.py"
        )
    )
    evidence = helper["_build_source"](
        tmp_path / "runtime",
        tmp_path / "workspace",
        tmp_path / "artifact",
    )
    projection = helper["_build"](evidence)
    journey = build_journey(journey_projection=projection)
    summary = journey.get_summary()
    assert summary["event_count"] == 35
    assert summary["decision_count"] == 14
    assert summary["terminal_classification"] == "FINAL_EXECUTION_CERTIFIED"
    assert journey.get_terminal_state()["terminal_reached"] is True
