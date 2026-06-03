"""Tests for AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import (
    AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
    FAILED_CLOSED,
    IMPROVEMENT_INTENT_ARTIFACT_V1,
    IMPROVEMENT_INTENT_CLASSIFICATION_V1,
    IMPROVEMENT_INTENT_CREATED,
    IMPROVEMENT_INTENT_EVIDENCE_V1,
    create_improvement_intent_from_replay_gap,
    reconstruct_replay_to_improvement_intent_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T17:30:00+00:00"
CHAIN_ID = "CHAIN-REPLAY-IMPROVEMENT-000001"


def _evidence(evidence_id: str, evidence_type: str, payload: dict, *, confidence: str = "DETERMINISTIC", **extra) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "source_replay_reference": f"replay/{evidence_id}.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "observed replay condition",
        "expected_condition": "expected replay condition",
        "confidence": confidence,
        **extra,
    }


def _gap_capture(tmp_path, *, confidence: str = "DETERMINISTIC", domain_id: str = "TRADING", no_gap: bool = False):
    if no_gap:
        artifacts = [
            _evidence("VALIDATION-PASS", "VALIDATION_RESULT", {"status": "PASSED"}, confidence=confidence, status="PASSED")
        ]
    else:
        artifacts = [
            _evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, confidence=confidence, status="FAILED")
        ]
    return detect_replay_gaps(
        detection_id=f"GAP-{domain_id}-{confidence}-{no_gap}",
        domain_id=domain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"gap-{domain_id}-{confidence}-{no_gap}",
        replay_artifacts=artifacts,
    )


def test_confirmed_gap_becomes_bounded_improvement_intent(tmp_path) -> None:
    gap = _gap_capture(tmp_path, domain_id="TRADING")
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        affected_worker_family="MARKET_EVIDENCE_NORMALIZATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
    )
    reconstructed = reconstruct_replay_to_improvement_intent_replay(tmp_path / "intent")
    intent = capture["improvement_intent_artifact"]

    assert capture["intent_status"] == IMPROVEMENT_INTENT_CREATED
    assert intent["artifact_type"] == IMPROVEMENT_INTENT_ARTIFACT_V1
    assert capture["improvement_intent_evidence_artifact"]["artifact_type"] == IMPROVEMENT_INTENT_EVIDENCE_V1
    assert capture["improvement_intent_classification_artifact"]["artifact_type"] == IMPROVEMENT_INTENT_CLASSIFICATION_V1
    assert intent["improvement_intent_version"] == AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION
    assert intent["intent_source"] == "REPLAY_GAP_DETECTION"
    assert intent["canonical_chain_id"] == CHAIN_ID
    assert intent["intent_summary"] == "Validation improvement required."
    assert intent["improvement_class"] == "RUNTIME_HARDENING"
    assert intent["high_risk_domain"] is True
    assert intent["human_review_required"] is True
    assert intent["ppp_eligible"] is True
    assert intent["proposal_created"] is False
    assert intent["ppp_invoked"] is False
    assert intent["provider_invoked"] is False
    assert intent["worker_invoked"] is False
    assert intent["execution_requested"] is False
    assert intent["dispatch_requested"] is False
    assert reconstructed["intent_status"] == IMPROVEMENT_INTENT_CREATED
    assert reconstructed["replay_artifact_count"] == 4


def test_domain_effectiveness_gap_maps_to_domain_model_intent(tmp_path) -> None:
    gap = detect_replay_gaps(
        detection_id="GAP-MARKETING-DOMAIN-EFFECTIVENESS",
        domain_id="MARKETING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap-marketing",
        replay_artifacts=[
            _evidence(
                "DOMAIN-EFFECTIVENESS",
                "DOMAIN_EFFECTIVENESS",
                {"score": 0.7},
                observed_value=0.7,
                expected_value=1.0,
            )
        ],
    )
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-MARKETING-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="DOMAIN",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "marketing-intent",
    )

    assert capture["intent_status"] == IMPROVEMENT_INTENT_CREATED
    assert capture["improvement_class"] == "DOMAIN_MODEL"
    assert capture["intent_summary"] == "Domain effectiveness improvement required."
    assert capture["human_review_required"] is False


def test_no_gap_detection_fails_closed(tmp_path) -> None:
    gap = _gap_capture(tmp_path, no_gap=True)
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-NONE-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "none-intent",
    )

    assert capture["intent_status"] == FAILED_CLOSED
    assert "confirmed gap required" in capture["failure_reason"]
    assert capture["proposal_created"] is False


def test_insufficient_confidence_fails_closed(tmp_path) -> None:
    gap = _gap_capture(tmp_path, confidence="MEDIUM")
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-CONFIDENCE-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "confidence-intent",
    )

    assert capture["intent_status"] == FAILED_CLOSED
    assert "confidence insufficient" in capture["failure_reason"]


def test_chain_continuity_failure_fails_closed(tmp_path) -> None:
    gap = _gap_capture(tmp_path)
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-CHAIN-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id="DIFFERENT-CHAIN",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain-intent",
    )

    assert capture["intent_status"] == FAILED_CLOSED
    assert "chain continuity failed" in capture["failure_reason"]


def test_replay_hash_mismatch_fails_closed(tmp_path) -> None:
    gap = _gap_capture(tmp_path)
    detection = dict(gap["gap_detection_artifact"])
    detection["gap_count"] = 99
    capture = create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-HASH-000001",
        gap_detection_artifact=detection,
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hash-intent",
    )

    assert capture["intent_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_improvement_intent_replay(tmp_path) -> None:
    gap = _gap_capture(tmp_path)
    create_improvement_intent_from_replay_gap(
        improvement_intent_id="IMPROVEMENT-INTENT-CORRUPT-000001",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt-intent",
    )
    path = tmp_path / "corrupt-intent" / "002_improvement_intent_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["intent_summary"] = "Add MACD."
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_to_improvement_intent_replay(tmp_path / "corrupt-intent")


def test_replay_to_improvement_intent_runtime_has_no_ppp_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.replay_to_improvement_intent_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
