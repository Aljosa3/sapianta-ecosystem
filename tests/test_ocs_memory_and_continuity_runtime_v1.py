"""Tests for AIGOL_OCS_MEMORY_AND_CONTINUITY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import (
    OCS_CONTINUITY_ARTIFACT_V1,
    OCS_MEMORY_AND_CONTINUITY_RECORDED,
    OCS_MEMORY_ARTIFACT_V1,
    build_ocs_memory_and_continuity,
    reconstruct_ocs_memory_and_continuity_replay,
)
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T10:00:00+00:00"


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


def _ocs_stack(tmp_path) -> tuple[dict, dict, dict]:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-MEMORY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-MEMORY-000001",
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
                _artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-TRADING", domain_id="TRADING")
            ],
        },
    )["ocs_context_assembly_artifact"]
    cognition = run_ocs_cognition(
        cognition_id="OCS-COGNITION-MEMORY-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-MEMORY-000001",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
        failure_history=[
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-1", failure_reason="missing replay artifact"),
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-2", failure_reason="missing replay artifact"),
        ],
        validation_history=[
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-1", validation_status="FAILED", error_code="MISSING_HASH"),
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-2", validation_status="FAILED", error_code="MISSING_HASH"),
        ],
        operator_decision_history=[
            _artifact("HUMAN_DECISION_ARTIFACT_V1", "DECISION-1", decision_status="REQUEST_MODIFICATION"),
            _artifact("HUMAN_DECISION_ARTIFACT_V1", "DECISION-2", decision_status="REQUEST_MODIFICATION"),
        ],
    )["ocs_replay_derived_intent_artifact"]
    return context, cognition, intent


def _registry() -> list[dict]:
    return [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-TRADING", domain_id="TRADING")]


def _operation_history() -> list[dict]:
    return [
        _artifact("EXECUTION_ARTIFACT_V1", "OP-1", operation_id="OPERATION-TRADING-1", domain_id="TRADING", status="FAILED"),
        _artifact("EXECUTION_ARTIFACT_V1", "OP-2", operation_id="OPERATION-TRADING-2", domain_id="TRADING", status="FAILED"),
    ]


def test_ocs_memory_and_continuity_builds_reconstructable_artifacts(tmp_path) -> None:
    context, cognition, intent = _ocs_stack(tmp_path)
    capture = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-CONTINUITY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "memory",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=_registry(),
        replay_visible_operation_history=_operation_history(),
    )
    reconstructed = reconstruct_ocs_memory_and_continuity_replay(tmp_path / "memory")

    assert capture["ocs_memory_artifact"]["artifact_type"] == OCS_MEMORY_ARTIFACT_V1
    assert capture["ocs_continuity_artifact"]["artifact_type"] == OCS_CONTINUITY_ARTIFACT_V1
    assert capture["memory_status"] == OCS_MEMORY_AND_CONTINUITY_RECORDED
    assert capture["continuity_status"] == OCS_MEMORY_AND_CONTINUITY_RECORDED
    assert capture["memory_summary"]["domain_count"] == 1
    assert capture["memory_summary"]["domains"] == ["TRADING"]
    assert capture["memory_summary"]["source_count"] == 6
    assert capture["operation_groups"]
    assert capture["domain_continuity"][0]["domain_id"] == "TRADING"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["governance_modified"] is False
    assert capture["replay_modified"] is False
    assert reconstructed["memory_hash"] == capture["memory_hash"]
    assert reconstructed["continuity_hash"] == capture["continuity_hash"]
    assert reconstructed["replay_artifact_count"] == 3


def test_ocs_memory_and_continuity_is_deterministic_for_identical_history(tmp_path) -> None:
    context, cognition, intent = _ocs_stack(tmp_path)
    first = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-DETERMINISTIC-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=_registry(),
        replay_visible_operation_history=_operation_history(),
    )
    second = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-DETERMINISTIC-000002",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=list(reversed(_registry())),
        replay_visible_operation_history=list(reversed(_operation_history())),
    )

    assert first["memory_hash"] == second["memory_hash"]
    assert first["continuity_hash"] == second["continuity_hash"]
    assert reconstruct_ocs_memory_and_continuity_replay(tmp_path / "first")["memory_hash"] == first["memory_hash"]
    assert reconstruct_ocs_memory_and_continuity_replay(tmp_path / "second")["continuity_hash"] == second["continuity_hash"]


def test_ocs_memory_and_continuity_fails_closed_on_non_replay_visible_source(tmp_path) -> None:
    context, cognition, intent = _ocs_stack(tmp_path)
    operation_history = _operation_history()
    operation_history[0]["replay_visible"] = False
    operation_history[0]["artifact_hash"] = replay_hash(
        {key: value for key, value in operation_history[0].items() if key != "artifact_hash"}
    )

    capture = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-NON-REPLAY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "non_replay",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        replay_visible_operation_history=operation_history,
    )

    assert capture["fail_closed"] is True
    assert capture["memory_status"] == "FAILED_CLOSED"
    assert "not replay-visible" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_ocs_memory_and_continuity_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    context, cognition, intent = _ocs_stack(tmp_path)
    registry = _registry()
    registry[0]["execution_requested"] = True
    registry[0]["artifact_hash"] = replay_hash({key: value for key, value in registry[0].items() if key != "artifact_hash"})

    capture = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-AUTHORITY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=registry,
    )

    assert capture["fail_closed"] is True
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_memory_and_continuity_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    context, cognition, intent = _ocs_stack(tmp_path)
    build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-CORRUPT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=_registry(),
    )
    path = tmp_path / "corrupt" / "001_ocs_continuity_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["continuity_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_memory_and_continuity_replay(tmp_path / "corrupt")


def test_ocs_memory_and_continuity_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_memory_and_continuity_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
