"""Tests for AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.improvement_intent_cognition_routing_runtime import (
    COGNITION_INTENT_ROUTED,
    COGNITION_ROUTED_INTENT_ARTIFACT_V1,
    COGNITION_ROUTING_CLASSIFICATION_V1,
    COGNITION_ROUTING_EVIDENCE_V1,
    FAILED_CLOSED,
    reconstruct_improvement_intent_cognition_routing_replay,
    route_improvement_intent_to_cognition,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T18:00:00+00:00"
CHAIN_ID = "CHAIN-COGNITION-ROUTING-000001"


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


def _improvement_intent_capture(tmp_path, *, domain_id: str = "TRADING"):
    gap = detect_replay_gaps(
        detection_id=f"GAP-COGNITION-{domain_id}",
        domain_id=domain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"gap-{domain_id}",
        replay_artifacts=[
            _evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED")
        ],
    )
    return create_improvement_intent_from_replay_gap(
        improvement_intent_id=f"IMPROVEMENT-INTENT-COGNITION-{domain_id}",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"intent-{domain_id}",
    )


def test_routes_replay_derived_improvement_intent_to_cognition_input(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path)
    capture = route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )
    reconstructed = reconstruct_improvement_intent_cognition_routing_replay(tmp_path / "routing")
    routed = capture["cognition_routed_intent_artifact"]

    assert capture["routing_status"] == COGNITION_INTENT_ROUTED
    assert capture["cognition_routing_evidence_artifact"]["artifact_type"] == COGNITION_ROUTING_EVIDENCE_V1
    assert capture["cognition_routing_classification_artifact"]["artifact_type"] == COGNITION_ROUTING_CLASSIFICATION_V1
    assert routed["artifact_type"] == COGNITION_ROUTED_INTENT_ARTIFACT_V1
    assert routed["cognition_input_type"] == "STRUCTURED_INTENT"
    assert routed["normalized_intent"] == "Validation improvement required."
    assert routed["normalized_intent_class"] == "RUNTIME_HARDENING"
    assert routed["canonical_chain_id"] == CHAIN_ID
    assert routed["affected_domain"] == "TRADING"
    assert routed["source_lineage_preserved"] is True
    assert routed["intent_source"] == "REPLAY_GAP_DETECTION"
    assert routed["intent_source_visible_to_ppp"] is False
    assert routed["ppp_input_contract"]["intent_source_visible_to_ppp"] is False
    assert routed["ppp_input_contract"]["normalized_intent"] == "Validation improvement required."
    assert routed["proposal_created"] is False
    assert routed["ppp_invoked"] is False
    assert routed["provider_invoked"] is False
    assert routed["worker_invoked"] is False
    assert routed["execution_requested"] is False
    assert reconstructed["routing_status"] == COGNITION_INTENT_ROUTED
    assert reconstructed["replay_artifact_count"] == 4


def test_human_and_replay_intent_are_ppp_equivalent_after_cognition_routing(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path, domain_id="MARKETING")
    capture = route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-EQUIVALENCE-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "equivalence",
    )
    contract = capture["cognition_routed_intent_artifact"]["ppp_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "normalized_intent",
        "normalized_intent_class",
        "affected_domain",
        "confidence",
        "intent_source_visible_to_ppp",
    }
    assert contract["intent_source_visible_to_ppp"] is False
    assert "REPLAY_GAP_DETECTION" not in contract.values()


def test_routing_fails_closed_when_intent_is_not_ppp_eligible(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path)
    artifact = dict(intent["improvement_intent_artifact"])
    artifact["ppp_eligible"] = False
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-NOT-ELIGIBLE-000001",
        improvement_intent_artifact=artifact,
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "not-eligible",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "not ppp eligible" in capture["failure_reason"]
    assert capture["ppp_invoked"] is False


def test_routing_fails_closed_when_lineage_hash_mismatches(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path)
    artifact = dict(intent["improvement_intent_artifact"])
    artifact["intent_evidence_hash"] = "sha256:not-real"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-LINEAGE-000001",
        improvement_intent_artifact=artifact,
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "replay lineage broken" in capture["failure_reason"]


def test_routing_fails_closed_when_chain_continuity_fails(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path)
    evidence = dict(intent["improvement_intent_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    artifact = dict(intent["improvement_intent_artifact"])
    artifact["intent_evidence_hash"] = evidence["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    classification = dict(intent["improvement_intent_classification_artifact"])
    classification["intent_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    artifact["intent_classification_hash"] = classification["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-CHAIN-000001",
        improvement_intent_artifact=artifact,
        improvement_intent_evidence_artifact=evidence,
        improvement_intent_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "chain continuity failed" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_cognition_routing_replay(tmp_path) -> None:
    intent = _improvement_intent_capture(tmp_path)
    route_improvement_intent_to_cognition(
        routing_id="COGNITION-ROUTING-CORRUPT-000001",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_cognition_routed_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_intent_cognition_routing_replay(tmp_path / "corrupt")


def test_improvement_intent_cognition_routing_has_no_ppp_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.improvement_intent_cognition_routing_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
