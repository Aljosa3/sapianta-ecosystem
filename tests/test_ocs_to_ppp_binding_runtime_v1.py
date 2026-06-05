"""Tests for AIGOL_OCS_TO_PPP_BINDING_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import (
    OCS_TO_PPP_HANDOFF_ARTIFACT_V1,
    OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED,
    create_ocs_to_ppp_handoff,
    reconstruct_ocs_to_ppp_handoff_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T12:00:00+00:00"


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


def _stack(tmp_path) -> tuple[dict, dict, dict, dict, dict, dict]:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-PPP-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-PPP-000001",
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
        cognition_id="OCS-COGNITION-PPP-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-PPP-000001",
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
    )["ocs_replay_derived_intent_artifact"]
    registry = [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-TRADING", domain_id="TRADING")]
    memory_capture = build_ocs_memory_and_continuity(
        memory_continuity_id="OCS-MEMORY-PPP-000001",
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
    memory = memory_capture["ocs_memory_artifact"]
    continuity = memory_capture["ocs_continuity_artifact"]
    semantic = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-PPP-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )["ocs_semantic_resolution_artifact"]
    return context, cognition, intent, memory, continuity, semantic


def test_ocs_to_ppp_binding_creates_reconstructable_handoff_candidate(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    capture = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )
    reconstructed = reconstruct_ocs_to_ppp_handoff_replay(tmp_path / "handoff")
    artifact = capture["ocs_to_ppp_handoff_artifact"]

    assert artifact["artifact_type"] == OCS_TO_PPP_HANDOFF_ARTIFACT_V1
    assert capture["handoff_status"] == OCS_TO_PPP_HANDOFF_CANDIDATE_CREATED
    assert capture["candidate_count"] >= 1
    assert artifact["proposal_only"] is True
    assert artifact["semantic_continuity_evidence"]["semantic_hash"] == semantic["semantic_hash"]
    assert artifact["domain_resolution_evidence"][0]["domain_id"] == "TRADING"
    assert artifact["provider_necessity_findings"]["necessity_classification"] == "PROVIDER_REQUIRED"
    assert artifact["worker_candidate_findings"]
    assert artifact["authority_flags"]["invokes_ppp"] is False
    assert capture["ppp_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["governance_modified"] is False
    assert reconstructed["handoff_hash"] == capture["handoff_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_to_ppp_binding_is_deterministic_for_identical_ocs_artifacts(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    first = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-DETERMINISTIC-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-DETERMINISTIC-000002",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )

    assert first["handoff_hash"] == second["handoff_hash"]
    assert reconstruct_ocs_to_ppp_handoff_replay(tmp_path / "first")["handoff_hash"] == first["handoff_hash"]
    assert reconstruct_ocs_to_ppp_handoff_replay(tmp_path / "second")["handoff_hash"] == second["handoff_hash"]


def test_ocs_to_ppp_binding_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    semantic["execution_requested"] = True
    semantic["artifact_hash"] = replay_hash({key: value for key, value in semantic.items() if key != "artifact_hash"})

    capture = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-AUTHORITY-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert capture["handoff_status"] == "FAILED_CLOSED"
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_to_ppp_binding_fails_closed_on_lineage_mismatch(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    semantic["source_memory_hash"] = "sha256:wrong"
    semantic["semantic_hash"] = replay_hash({key: value for key, value in semantic.items() if key not in {"semantic_hash", "artifact_hash"}})
    semantic["artifact_hash"] = replay_hash({key: value for key, value in semantic.items() if key != "artifact_hash"})

    capture = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-LINEAGE-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["fail_closed"] is True
    assert "semantic memory hash mismatch" in capture["failure_reason"]


def test_ocs_to_ppp_binding_fails_closed_on_mixed_ocs_chain(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    intent["source_cognition_hash"] = "sha256:wrong"
    intent["intent_hash"] = replay_hash({key: value for key, value in intent.items() if key not in {"intent_hash", "artifact_hash"}})
    intent["artifact_hash"] = replay_hash({key: value for key, value in intent.items() if key != "artifact_hash"})

    capture = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-MIXED-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "mixed",
    )

    assert capture["fail_closed"] is True
    assert "intent cognition hash mismatch" in capture["failure_reason"]


def test_ocs_to_ppp_binding_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic = _stack(tmp_path)
    create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-CORRUPT-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_ocs_to_ppp_handoff_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["handoff_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_to_ppp_handoff_replay(tmp_path / "corrupt")


def test_ocs_to_ppp_binding_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_to_ppp_binding_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
