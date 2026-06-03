"""Tests for AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.improvement_intent_cognition_routing_runtime import route_improvement_intent_to_cognition
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_derived_intent_resource_selection_routing_runtime import (
    FAILED_CLOSED,
    RESOURCE_SELECTION_INTENT_ROUTED,
    RESOURCE_SELECTION_ROUTED_INTENT_V1,
    RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
    RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
    reconstruct_replay_derived_intent_resource_selection_routing_replay,
    route_replay_derived_intent_to_resource_selection,
)
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


CREATED_AT = "2026-06-03T18:30:00+00:00"
CHAIN_ID = "CHAIN-RESOURCE-SELECTION-ROUTING-000001"


def _evidence(evidence_id: str, evidence_type: str, payload: dict, **extra) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "source_replay_reference": f"replay/{evidence_id}.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "observed replay condition",
        "expected_condition": "expected replay condition",
        "confidence": "DETERMINISTIC",
        **extra,
    }


def _cognition_routing_capture(tmp_path, *, domain_id: str = "TRADING"):
    gap = detect_replay_gaps(
        detection_id=f"GAP-RS-{domain_id}",
        domain_id=domain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"gap-{domain_id}",
        replay_artifacts=[
            _evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED")
        ],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id=f"IMPROVEMENT-INTENT-RS-{domain_id}",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"intent-{domain_id}",
    )
    return route_improvement_intent_to_cognition(
        routing_id=f"COGNITION-ROUTING-RS-{domain_id}",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"cognition-{domain_id}",
    )


def test_routes_cognition_routed_replay_intent_to_resource_selection_input(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path)
    capture = route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-000001",
        cognition_routed_intent_artifact=cognition["cognition_routed_intent_artifact"],
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resource-routing",
    )
    reconstructed = reconstruct_replay_derived_intent_resource_selection_routing_replay(
        tmp_path / "resource-routing"
    )
    routed = capture["resource_selection_routed_intent_artifact"]
    contract = routed["resource_selection_input_contract"]

    assert capture["routing_status"] == RESOURCE_SELECTION_INTENT_ROUTED
    assert capture["resource_selection_routing_evidence_artifact"]["artifact_type"] == RESOURCE_SELECTION_ROUTING_EVIDENCE_V1
    assert (
        capture["resource_selection_routing_classification_artifact"]["artifact_type"]
        == RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1
    )
    assert routed["artifact_type"] == RESOURCE_SELECTION_ROUTED_INTENT_V1
    assert routed["resource_selection_input_type"] == "STRUCTURED_RESOURCE_SELECTION_REQUIREMENTS"
    assert contract["workflow_type"] == "NATIVE_DEVELOPMENT"
    assert contract["required_capability"] == "PROPOSAL_GENERATION"
    assert contract["requested_role_type"] == PROVIDER_ROLE
    assert contract["domain_id"] == "TRADING"
    assert contract["provider_necessity_classification"] == "PROVIDER_REQUIRED"
    assert routed["source_lineage_preserved"] is True
    assert routed["intent_source_visible_to_resource_selection"] is False
    assert contract["intent_source_visible_to_resource_selection"] is False
    assert routed["resource_selection_invoked"] is False
    assert routed["ppp_invoked"] is False
    assert routed["provider_invoked"] is False
    assert routed["worker_invoked"] is False
    assert routed["execution_requested"] is False
    assert reconstructed["routing_status"] == RESOURCE_SELECTION_INTENT_ROUTED
    assert reconstructed["replay_artifact_count"] == 4


def test_human_and_replay_intent_are_resource_selection_equivalent_after_routing(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path, domain_id="MARKETING")
    capture = route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-EQUIVALENCE-000001",
        cognition_routed_intent_artifact=cognition["cognition_routed_intent_artifact"],
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "equivalence",
    )
    contract = capture["resource_selection_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "workflow_type",
        "required_capability",
        "requested_role_type",
        "domain_id",
        "provider_necessity_classification",
        "confidence",
        "intent_source_visible_to_resource_selection",
    }
    assert contract["intent_source_visible_to_resource_selection"] is False
    assert "REPLAY_GAP_DETECTION" not in contract.values()


def test_resource_selection_routing_fails_closed_when_source_visibility_leaks(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path)
    artifact = dict(cognition["cognition_routed_intent_artifact"])
    artifact["intent_source_visible_to_ppp"] = True
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-LEAK-000001",
        cognition_routed_intent_artifact=artifact,
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "leak",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "source visibility leak" in capture["failure_reason"]


def test_resource_selection_routing_fails_closed_when_lineage_hash_mismatches(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path)
    artifact = dict(cognition["cognition_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = "sha256:not-real"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-LINEAGE-000001",
        cognition_routed_intent_artifact=artifact,
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "replay lineage broken" in capture["failure_reason"]


def test_resource_selection_routing_fails_closed_when_chain_continuity_fails(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path)
    evidence = dict(cognition["cognition_routing_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(cognition["cognition_routing_classification_artifact"])
    classification["routing_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    artifact = dict(cognition["cognition_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = evidence["artifact_hash"]
    artifact["routing_classification_hash"] = classification["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-CHAIN-000001",
        cognition_routed_intent_artifact=artifact,
        cognition_routing_evidence_artifact=evidence,
        cognition_routing_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "chain continuity failed" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_resource_selection_routing_replay(tmp_path) -> None:
    cognition = _cognition_routing_capture(tmp_path)
    route_replay_derived_intent_to_resource_selection(
        routing_id="RESOURCE-SELECTION-ROUTING-CORRUPT-000001",
        cognition_routed_intent_artifact=cognition["cognition_routed_intent_artifact"],
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_resource_selection_routed_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_derived_intent_resource_selection_routing_replay(tmp_path / "corrupt")


def test_replay_derived_intent_resource_selection_routing_has_no_selection_ppp_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.replay_derived_intent_resource_selection_routing_runtime as runtime

    source = inspect.getsource(runtime)

    assert "select_unified_resource(" not in source
    assert "integrate_resource_selection_with_ppp(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
