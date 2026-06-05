"""Tests for AIGOL_OCS_REPLAY_DERIVED_INTENT_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_replay_derived_intent_runtime import (
    OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1,
    OCS_REPLAY_DERIVED_INTENT_CREATED,
    generate_ocs_replay_derived_intent,
    reconstruct_ocs_replay_derived_intent_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T09:00:00+00:00"


def _artifact(artifact_type: str, artifact_id: str, **extra: object) -> dict:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "replay_visible": True,
        "authority": False,
        **extra,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _cognition(tmp_path) -> dict:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-INTENT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_context={
            "conversation_context": [_artifact("CONVERSATION_RESPONSE_ARTIFACT_V1", "CONVERSATION-000001")],
            "clarification_context": [],
            "ppp_context": [
                _artifact(
                    "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                    "PPP-TRADING-000001",
                    ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
                    provider_necessity_classification="PROVIDER_REQUIRED",
                )
            ],
            "approval_context": [],
            "replay_visible_operation_context": [
                _artifact("UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1", "REPLAY-000001", status="READY")
            ],
            "domain_context": [_artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", "TRADING-DOMAIN", domain_id="TRADING")],
            "registry_context": [
                _artifact(
                    "DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1",
                    "REGISTRY-TRADING",
                    domain_id="TRADING",
                    resolution_status="DOMAIN_BUNDLE_RESOLVED",
                )
            ],
        },
    )["ocs_context_assembly_artifact"]
    return run_ocs_cognition(
        cognition_id="OCS-COGNITION-INTENT-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]


def _history() -> dict[str, list[dict]]:
    return {
        "execution_history": [
            _artifact("EXECUTION_ARTIFACT_V1", "EXEC-1", status="FAILED", failure_reason="worker timeout"),
            _artifact("EXECUTION_ARTIFACT_V1", "EXEC-2", status="FAILED", failure_reason="worker timeout"),
        ],
        "validation_history": [
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-1", validation_status="FAILED", error_code="MISSING_HASH"),
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-2", validation_status="FAILED", error_code="MISSING_HASH"),
        ],
        "failure_history": [
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-1", failure_reason="missing replay artifact"),
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-2", failure_reason="missing replay artifact"),
        ],
        "operator_decision_history": [
            _artifact("HUMAN_DECISION_ARTIFACT_V1", "DECISION-1", decision_status="REQUEST_MODIFICATION"),
            _artifact("HUMAN_DECISION_ARTIFACT_V1", "DECISION-2", decision_status="REQUEST_MODIFICATION"),
        ],
    }


def test_ocs_replay_derived_intent_generates_reconstructable_candidates(tmp_path) -> None:
    history = _history()
    capture = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-000001",
        ocs_cognition_artifact=_cognition(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
        **history,
    )
    reconstructed = reconstruct_ocs_replay_derived_intent_replay(tmp_path / "intent")
    artifact = capture["ocs_replay_derived_intent_artifact"]

    assert artifact["artifact_type"] == OCS_REPLAY_DERIVED_INTENT_ARTIFACT_V1
    assert capture["intent_status"] == OCS_REPLAY_DERIVED_INTENT_CREATED
    assert capture["recurring_failure_count"] == 1
    assert capture["recurring_operator_intervention_count"] == 1
    assert capture["capability_gap_count"] == 1
    assert capture["candidate_count"] >= 3
    assert artifact["authority_flags"]["authorizes_self_modification"] is False
    assert capture["self_modification_requested"] is False
    assert capture["automatic_implementation_requested"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["governance_modified"] is False
    assert reconstructed["intent_status"] == OCS_REPLAY_DERIVED_INTENT_CREATED
    assert reconstructed["intent_hash"] == capture["intent_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_replay_derived_intent_is_deterministic_for_identical_history(tmp_path) -> None:
    cognition = _cognition(tmp_path)
    first = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-DETERMINISTIC-000001",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
        **_history(),
    )
    shuffled = _history()
    shuffled["failure_history"] = list(reversed(shuffled["failure_history"]))
    shuffled["operator_decision_history"] = list(reversed(shuffled["operator_decision_history"]))
    second = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-DETERMINISTIC-000002",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
        **shuffled,
    )

    assert first["intent_hash"] == second["intent_hash"]
    assert reconstruct_ocs_replay_derived_intent_replay(tmp_path / "first")["intent_hash"] == first["intent_hash"]
    assert reconstruct_ocs_replay_derived_intent_replay(tmp_path / "second")["intent_hash"] == second["intent_hash"]


def test_ocs_replay_derived_intent_fails_closed_on_non_replay_visible_history(tmp_path) -> None:
    history = _history()
    history["failure_history"][0]["replay_visible"] = False
    history["failure_history"][0]["artifact_hash"] = replay_hash(
        {key: value for key, value in history["failure_history"][0].items() if key != "artifact_hash"}
    )

    capture = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-NON-REPLAY-000001",
        ocs_cognition_artifact=_cognition(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "non_replay",
        **history,
    )

    assert capture["fail_closed"] is True
    assert capture["intent_status"] == "FAILED_CLOSED"
    assert "history item is not replay-visible" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_ocs_replay_derived_intent_fails_closed_on_authority_bearing_history(tmp_path) -> None:
    history = _history()
    history["validation_history"][0]["execution_requested"] = True
    history["validation_history"][0]["artifact_hash"] = replay_hash(
        {key: value for key, value in history["validation_history"][0].items() if key != "artifact_hash"}
    )

    capture = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-AUTHORITY-000001",
        ocs_cognition_artifact=_cognition(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
        **history,
    )

    assert capture["fail_closed"] is True
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_replay_derived_intent_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-CORRUPT-000001",
        ocs_cognition_artifact=_cognition(tmp_path),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        **_history(),
    )
    path = tmp_path / "corrupt" / "000_ocs_replay_derived_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["intent_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_replay_derived_intent_replay(tmp_path / "corrupt")


def test_ocs_replay_derived_intent_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_replay_derived_intent_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
