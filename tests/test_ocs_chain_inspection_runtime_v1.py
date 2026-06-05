"""Tests for AIGOL_OCS_CHAIN_INSPECTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_chain_inspection_runtime import (
    OCS_CHAIN_INSPECTION_ARTIFACT_V1,
    OCS_CHAIN_INSPECTION_COMPLETED,
    inspect_ocs_chain,
    reconstruct_ocs_chain_inspection_replay,
)
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import create_ocs_to_ppp_handoff
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T13:00:00+00:00"


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


def _stack(tmp_path) -> tuple[dict, dict, dict, dict, dict, dict, dict]:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-INSPECTION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-INSPECTION-000001",
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
        cognition_id="OCS-COGNITION-INSPECTION-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-INSPECTION-000001",
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
        memory_continuity_id="OCS-MEMORY-INSPECTION-000001",
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
        semantic_resolution_id="OCS-SEMANTIC-INSPECTION-000001",
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )["ocs_semantic_resolution_artifact"]
    handoff = create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-INSPECTION-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff",
    )["ocs_to_ppp_handoff_artifact"]
    return context, cognition, intent, memory, continuity, semantic, handoff


def test_ocs_chain_inspection_builds_reconstructable_operator_summary(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic, handoff = _stack(tmp_path)
    capture = inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "inspection",
    )
    reconstructed = reconstruct_ocs_chain_inspection_replay(tmp_path / "inspection")
    artifact = capture["ocs_chain_inspection_artifact"]

    assert artifact["artifact_type"] == OCS_CHAIN_INSPECTION_ARTIFACT_V1
    assert capture["inspection_status"] == OCS_CHAIN_INSPECTION_COMPLETED
    assert artifact["operator_summary"]["stage_count"] == 7
    assert [stage["stage_name"] for stage in artifact["chain_stages"]] == [
        "CONTEXT_ASSEMBLY",
        "COGNITION",
        "REPLAY_DERIVED_INTENT",
        "MEMORY",
        "CONTINUITY",
        "SEMANTIC_RESOLUTION",
        "OCS_TO_PPP_BINDING",
    ]
    assert artifact["source_chain_hashes"]["context_hash"] == context["context_hash"]
    assert artifact["continuity_links"]["semantic_reference_linking"]
    assert artifact["semantic_resolution_results"]["domain_identity_resolution"][0]["domain_id"] == "TRADING"
    assert artifact["replay_derived_intent_candidates"]
    assert artifact["ppp_handoff_candidates"]
    assert artifact["read_only_inspection"] is True
    assert capture["ppp_invoked"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["approval_created"] is False
    assert reconstructed["inspection_hash"] == capture["inspection_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_chain_inspection_is_deterministic_for_identical_ocs_chains(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic, handoff = _stack(tmp_path)
    first = inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-DETERMINISTIC-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-DETERMINISTIC-000002",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )

    assert first["inspection_hash"] == second["inspection_hash"]
    assert reconstruct_ocs_chain_inspection_replay(tmp_path / "first")["inspection_hash"] == first["inspection_hash"]
    assert reconstruct_ocs_chain_inspection_replay(tmp_path / "second")["inspection_hash"] == second["inspection_hash"]


def test_ocs_chain_inspection_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic, handoff = _stack(tmp_path)
    handoff["provider_invoked"] = True
    handoff["artifact_hash"] = replay_hash({key: value for key, value in handoff.items() if key != "artifact_hash"})

    capture = inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-AUTHORITY-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert capture["inspection_status"] == "FAILED_CLOSED"
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_ocs_chain_inspection_fails_closed_on_mixed_lineage(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic, handoff = _stack(tmp_path)
    handoff["source_semantic_hash"] = "sha256:wrong"
    handoff["handoff_hash"] = replay_hash({key: value for key, value in handoff.items() if key not in {"handoff_hash", "artifact_hash"}})
    handoff["artifact_hash"] = replay_hash({key: value for key, value in handoff.items() if key != "artifact_hash"})

    capture = inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-LINEAGE-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["fail_closed"] is True
    assert "handoff semantic hash mismatch" in capture["failure_reason"]


def test_ocs_chain_inspection_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    context, cognition, intent, memory, continuity, semantic, handoff = _stack(tmp_path)
    inspect_ocs_chain(
        inspection_id="OCS-CHAIN-INSPECTION-CORRUPT-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory,
        ocs_continuity_artifact=continuity,
        ocs_semantic_resolution_artifact=semantic,
        ocs_to_ppp_handoff_artifact=handoff,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_ocs_chain_inspection_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["inspection_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_chain_inspection_replay(tmp_path / "corrupt")


def test_ocs_chain_inspection_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_chain_inspection_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
