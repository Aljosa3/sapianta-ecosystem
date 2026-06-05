"""Tests for AIGOL_OCS_SEMANTIC_RESOLUTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import (
    OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1,
    OCS_SEMANTIC_RESOLUTION_COMPLETED,
    reconstruct_ocs_semantic_resolution_replay,
    resolve_ocs_semantics,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T11:00:00+00:00"


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


def _stack(tmp_path) -> tuple[dict, dict, dict, dict, dict]:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-SEMANTIC-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-SEMANTIC-000001",
        source_context={
            "conversation_context": [_artifact("CONVERSATION_RESPONSE_ARTIFACT_V1", "CONVERSATION-000001")],
            "clarification_context": [],
            "ppp_context": [
                _artifact(
                    "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                    "PPP-TRADING-MARKET_EVIDENCE_NORMALIZATION-000001",
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
        cognition_id="OCS-COGNITION-SEMANTIC-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-SEMANTIC-000001",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intent",
        validation_history=[
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-1", validation_status="FAILED", error_code="MISSING_HASH"),
            _artifact("VALIDATION_ARTIFACT_V1", "VAL-2", validation_status="FAILED", error_code="MISSING_HASH"),
        ],
        failure_history=[
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-1", failure_reason="missing replay artifact"),
            _artifact("FAILURE_ARTIFACT_V1", "FAIL-2", failure_reason="missing replay artifact"),
        ],
    )["ocs_replay_derived_intent_artifact"]
    registry = [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-TRADING", domain_id="TRADING")]
    memory_capture = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-SEMANTIC-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "memory",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=registry,
        replay_visible_operation_history=[
            _artifact(
                "EXECUTION_ARTIFACT_V1",
                "OP-1",
                operation_id="OPERATION-TRADING-1",
                domain_id="TRADING",
                worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
                status="FAILED",
            )
        ],
    )
    return memory_capture["ocs_memory_artifact"], memory_capture["ocs_continuity_artifact"], cognition, intent, registry


def test_ocs_semantic_resolution_builds_reconstructable_resolution(tmp_path) -> None:
    memory, continuity, cognition, intent, registry = _stack(tmp_path)
    capture = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )
    reconstructed = reconstruct_ocs_semantic_resolution_replay(tmp_path / "semantic")
    artifact = capture["ocs_semantic_resolution_artifact"]

    assert artifact["artifact_type"] == OCS_SEMANTIC_RESOLUTION_ARTIFACT_V1
    assert capture["resolution_status"] == OCS_SEMANTIC_RESOLUTION_COMPLETED
    assert capture["domain_identity_resolution"] == [
        {
            "domain_id": "TRADING",
            "resolution_status": "RESOLVED",
            "evidence": ["cognition", "domain_continuity", "memory_summary", "registry", "semantic_reference"],
            "authority": False,
        }
    ]
    assert any(item["worker_id"] == "MARKET_EVIDENCE_NORMALIZATION" for item in capture["worker_identity_resolution"])
    assert any(item["capability_id"] == "CAPABILITY_GAP" for item in capture["capability_identity_resolution"])
    assert capture["ambiguity_detection"]["is_ambiguous"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["governance_modified"] is False
    assert reconstructed["semantic_hash"] == capture["semantic_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_semantic_resolution_is_deterministic_for_identical_memory_and_continuity(tmp_path) -> None:
    memory, continuity, cognition, intent, registry = _stack(tmp_path)
    first = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-DETERMINISTIC-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-DETERMINISTIC-000002",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=list(reversed(registry)),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )

    assert first["semantic_hash"] == second["semantic_hash"]
    assert reconstruct_ocs_semantic_resolution_replay(tmp_path / "first")["semantic_hash"] == first["semantic_hash"]
    assert reconstruct_ocs_semantic_resolution_replay(tmp_path / "second")["semantic_hash"] == second["semantic_hash"]


def test_ocs_semantic_resolution_generates_clarification_for_ambiguous_domains(tmp_path) -> None:
    memory, continuity, cognition, intent, registry = _stack(tmp_path)
    registry.append(_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-HEALTHCARE", domain_id="HEALTHCARE"))

    capture = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-AMBIGUOUS-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
    )

    assert capture["ambiguity_detection"]["is_ambiguous"] is True
    assert "multiple domain identities resolved" in capture["ambiguity_detection"]["ambiguity_reasons"]
    assert capture["clarification_candidates"]


def test_ocs_semantic_resolution_fails_closed_on_authority_bearing_registry(tmp_path) -> None:
    memory, continuity, cognition, intent, registry = _stack(tmp_path)
    registry[0]["execution_requested"] = True
    registry[0]["artifact_hash"] = replay_hash({key: value for key, value in registry[0].items() if key != "artifact_hash"})

    capture = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-AUTHORITY-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert capture["resolution_status"] == "FAILED_CLOSED"
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_semantic_resolution_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    memory, continuity, cognition, intent, registry = _stack(tmp_path)
    resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-CORRUPT-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_ocs_semantic_resolution_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["semantic_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_semantic_resolution_replay(tmp_path / "corrupt")


def test_ocs_semantic_resolution_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_semantic_resolution_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
