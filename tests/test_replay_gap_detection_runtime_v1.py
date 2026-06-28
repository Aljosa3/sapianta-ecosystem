"""Tests for AIGOL_REPLAY_GAP_DETECTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import (
    AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION,
    FAILED_CLOSED,
    GAP_CLASSIFICATION_ARTIFACT_V1,
    GAP_DETECTION_ARTIFACT_V1,
    GAP_EVIDENCE_ARTIFACT_V1,
    GAPS_DETECTED,
    NO_GAPS_DETECTED,
    detect_replay_gaps,
    reconstruct_replay_gap_detection_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-03T17:00:00+00:00"


def _evidence(
    evidence_id: str,
    evidence_type: str,
    payload: dict,
    *,
    observed_condition: str = "observed condition",
    expected_condition: str = "expected condition",
    confidence: str = "DETERMINISTIC",
    **extra,
) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "source_replay_reference": f"replay/{evidence_id}.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "observed_condition": observed_condition,
        "expected_condition": expected_condition,
        "confidence": confidence,
        **extra,
    }


def test_detects_validation_policy_replay_and_failure_pattern_gaps(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "mixed",
        replay_artifacts=[
            _evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED"),
            _evidence("POLICY-FAIL", "POLICY_RESULT", {"status": "VIOLATION"}, status="VIOLATION"),
            _evidence("REPLAY-BROKEN", "REPLAY_INTEGRITY", {"status": "HASH_MISMATCH"}, status="HASH_MISMATCH"),
            _evidence("FAILURE-LOOP", "FAILURE_PATTERN", {"failure_count": 4}, failure_count=4),
        ],
    )
    reconstructed = reconstruct_replay_gap_detection_replay(tmp_path / "mixed")

    assert capture["detection_status"] == GAPS_DETECTED
    assert capture["gap_detection_artifact"]["artifact_type"] == GAP_DETECTION_ARTIFACT_V1
    assert capture["gap_classification_artifact"]["artifact_type"] == GAP_CLASSIFICATION_ARTIFACT_V1
    assert capture["gap_evidence_artifact"]["artifact_type"] == GAP_EVIDENCE_ARTIFACT_V1
    assert capture["gap_count"] == 4
    assert "VALIDATION_GAP" in capture["gap_categories"]
    assert "POLICY_GAP" in capture["gap_categories"]
    assert "REPLAY_INTEGRITY_GAP" in capture["gap_categories"]
    assert "REPEATED_FAILURE_PATTERN" in capture["gap_categories"]
    assert capture["human_review_required"] is True
    assert capture["improvement_intent_allowed"] is True
    assert capture["proposal_created"] is False
    assert capture["ppp_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["detection_status"] == GAPS_DETECTED
    assert reconstructed["replay_artifact_count"] == 4


def test_detects_performance_and_domain_effectiveness_gaps_with_thresholds(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-PERFORMANCE-000001",
        domain_id="MARKETING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "performance",
        replay_artifacts=[
            _evidence(
                "PERFORMANCE-GAP",
                "PERFORMANCE_METRIC",
                {"latency_ms": 130},
                observed_value=130,
                expected_value=100,
                observed_condition="latency exceeded expected target",
                expected_condition="latency within target",
            ),
            _evidence(
                "EFFECTIVENESS-GAP",
                "DOMAIN_EFFECTIVENESS",
                {"acceptance_rate": 0.7},
                observed_value=0.7,
                expected_value=1.0,
                observed_condition="domain evidence acceptance below target",
                expected_condition="domain evidence accepted at target rate",
            ),
        ],
    )

    assert capture["detection_status"] == GAPS_DETECTED
    assert set(capture["gap_categories"]) == {"DOMAIN_EFFECTIVENESS_GAP", "PERFORMANCE_GAP"}
    assert capture["confidence"] == "DETERMINISTIC"


def test_no_gap_result_is_replay_visible_and_non_authorizing(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-NONE-000001",
        domain_id="AIGOL_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "none",
        replay_artifacts=[
            _evidence(
                "VALIDATION-PASS",
                "VALIDATION_RESULT",
                {"status": "PASSED"},
                status="PASSED",
                observed_condition="validation passed",
                expected_condition="validation passed",
            )
        ],
    )

    assert capture["detection_status"] == NO_GAPS_DETECTED
    assert capture["gap_count"] == 0
    assert capture["improvement_intent_allowed"] is False
    assert capture["proposal_created"] is False
    assert capture["ppp_invoked"] is False


def test_replay_gap_classifier_consumes_csa_lineage_when_available(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-CSA-000001",
        domain_id="AIGOL_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "csa",
        replay_artifacts=[
            _evidence(
                "VALIDATION-CSA-FAIL",
                "VALIDATION_RESULT",
                {"status": "FAILED"},
                status="FAILED",
                canonical_semantic_lineage={
                    "canonical_semantic_artifact_reference": "replay/csa/validation",
                    "canonical_semantic_artifact_hash": "sha256:" + "c" * 64,
                },
            )
        ],
    )
    reconstructed = reconstruct_replay_gap_detection_replay(tmp_path / "csa")
    classification = capture["gap_classification_artifact"]

    assert capture["replay_derived_classifier_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert capture["canonical_semantic_artifact_hashes"] == ["sha256:" + "c" * 64]
    assert capture["semantic_comparison_hash"].startswith("sha256:")
    assert classification["semantic_comparison_artifact"]["artifact_hash"] == capture["semantic_comparison_hash"]
    assert classification["semantic_comparison_parity_status"] == (
        "CSA_COMPATIBILITY_REPLAY_CLASSIFIER_PARITY_PROVEN"
    )
    assert classification["semantic_parity_evidence"]["historical_replay_reinterpreted"] is False
    assert classification["fallback_status"] == "COMPATIBILITY_FALLBACK_AVAILABLE_NOT_USED"
    assert reconstructed["replay_derived_classifier_source"] == "CANONICAL_SEMANTIC_ARTIFACT"
    assert reconstructed["canonical_semantic_artifact_hashes"] == ["sha256:" + "c" * 64]


def test_gap_detection_fails_closed_when_evidence_is_missing(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-MISSING-000001",
        domain_id="HEALTHCARE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "missing",
        replay_artifacts=[],
    )

    assert capture["detection_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "evidence missing" in capture["failure_reason"]
    assert capture["proposal_created"] is False
    assert capture["execution_requested"] is False


def test_gap_detection_fails_closed_when_replay_hash_mismatches(tmp_path) -> None:
    evidence = _evidence("REPLAY-CORRUPT", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED")
    evidence["source_replay_hash"] = "sha256:not-the-real-hash"

    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-HASH-000001",
        domain_id="HR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hash",
        replay_artifacts=[evidence],
    )

    assert capture["detection_status"] == FAILED_CLOSED
    assert "replay broken" in capture["failure_reason"]


def test_gap_detection_fails_closed_when_threshold_is_undefined(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-THRESHOLD-000001",
        domain_id="TRADING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "threshold",
        thresholds={"performance_gap_ratio": None},
        replay_artifacts=[
            _evidence("PERFORMANCE", "PERFORMANCE_METRIC", {"value": 150}, observed_value=150, expected_value=100)
        ],
    )

    assert capture["detection_status"] == FAILED_CLOSED
    assert "thresholds undefined" in capture["failure_reason"]


def test_gap_detection_fails_closed_when_classification_is_ambiguous(tmp_path) -> None:
    capture = detect_replay_gaps(
        detection_id="GAP-DETECTION-AMBIGUOUS-000001",
        domain_id="AIGOL_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
        replay_artifacts=[_evidence("UNKNOWN", "UNMAPPED_EVIDENCE", {"status": "FAILED"})],
    )

    assert capture["detection_status"] == FAILED_CLOSED
    assert "classification ambiguous" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_gap_detection_replay(tmp_path) -> None:
    detect_replay_gaps(
        detection_id="GAP-DETECTION-CORRUPT-000001",
        domain_id="AIGOL_CORE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        replay_artifacts=[_evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED")],
    )
    path = tmp_path / "corrupt" / "002_gap_detection_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["gap_count"] = 99
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_gap_detection_replay(tmp_path / "corrupt")


def test_replay_gap_detection_runtime_has_no_ppp_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.replay_gap_detection_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
