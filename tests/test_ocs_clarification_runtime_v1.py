"""Tests for AIGOL_OCS_CLARIFICATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_clarification_runtime import (
    OCS_CLARIFICATION_ARTIFACT_V1,
    OCS_CLARIFICATION_NOT_REQUIRED,
    OCS_CLARIFICATION_REQUIRED,
    generate_ocs_clarification,
    reconstruct_ocs_clarification_replay,
)
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-05T14:00:00+00:00"


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


def _stack(tmp_path, *, ambiguous: bool) -> tuple[dict, dict]:
    context = assemble_ocs_context(
        context_assembly_id=f"OCS-CONTEXT-CLARIFICATION-{'AMBIGUOUS' if ambiguous else 'CLEAR'}-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "context",
        source_chain_id="CHAIN-CLARIFICATION-000001",
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
        cognition_id=f"OCS-COGNITION-CLARIFICATION-{'AMBIGUOUS' if ambiguous else 'CLEAR'}-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id=f"OCS-INTENT-CLARIFICATION-{'AMBIGUOUS' if ambiguous else 'CLEAR'}-000001",
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
    if ambiguous:
        registry.append(_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-HEALTHCARE", domain_id="HEALTHCARE"))
    memory_capture = build_ocs_memory_and_continuity(
        memory_continuity_id=f"OCS-MEMORY-CLARIFICATION-{'AMBIGUOUS' if ambiguous else 'CLEAR'}-000001",
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
    return cognition, resolve_ocs_semantics(
        semantic_resolution_id=f"OCS-SEMANTIC-CLARIFICATION-{'AMBIGUOUS' if ambiguous else 'CLEAR'}-000001",
        ocs_memory_artifact=memory_capture["ocs_memory_artifact"],
        ocs_continuity_artifact=memory_capture["ocs_continuity_artifact"],
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "semantic",
    )["ocs_semantic_resolution_artifact"]


def test_ocs_clarification_generates_reconstructable_required_requests(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=True)
    capture = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clarification",
    )
    reconstructed = reconstruct_ocs_clarification_replay(tmp_path / "clarification")
    artifact = capture["ocs_clarification_artifact"]

    assert artifact["artifact_type"] == OCS_CLARIFICATION_ARTIFACT_V1
    assert capture["clarification_status"] == OCS_CLARIFICATION_REQUIRED
    assert capture["clarification_required"] is True
    assert any(item["source"] == "OCS_SEMANTIC_RESOLUTION" for item in capture["clarification_requests"])
    assert artifact["continuity_references"]
    assert artifact["semantic_references"]
    assert artifact["ambiguity_evidence"]["semantic_ambiguity"]["is_ambiguous"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["approval_created"] is False
    assert capture["ppp_invoked"] is False
    assert reconstructed["clarification_hash"] == capture["clarification_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_clarification_records_not_required_for_clear_inputs(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=False)
    capture = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-NOT-REQUIRED-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clear",
    )

    assert capture["clarification_status"] == OCS_CLARIFICATION_NOT_REQUIRED
    assert capture["clarification_required"] is False
    assert capture["clarification_requests"] == []


def test_ocs_clarification_is_deterministic_for_identical_ambiguity_inputs(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=True)
    first = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-DETERMINISTIC-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
    )
    second = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-DETERMINISTIC-000002",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
    )

    assert first["clarification_hash"] == second["clarification_hash"]
    assert reconstruct_ocs_clarification_replay(tmp_path / "first")["clarification_hash"] == first["clarification_hash"]
    assert reconstruct_ocs_clarification_replay(tmp_path / "second")["clarification_hash"] == second["clarification_hash"]


def test_ocs_clarification_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=True)
    semantic["provider_invoked"] = True
    semantic["artifact_hash"] = replay_hash({key: value for key, value in semantic.items() if key != "artifact_hash"})

    capture = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-AUTHORITY-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert capture["clarification_status"] == "FAILED_CLOSED"
    assert "prohibited flag" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_ocs_clarification_fails_closed_on_lineage_mismatch(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=True)
    semantic["source_cognition_hash"] = "sha256:wrong"
    semantic["semantic_hash"] = replay_hash({key: value for key, value in semantic.items() if key not in {"semantic_hash", "artifact_hash"}})
    semantic["artifact_hash"] = replay_hash({key: value for key, value in semantic.items() if key != "artifact_hash"})

    capture = generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-LINEAGE-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["fail_closed"] is True
    assert "semantic cognition hash mismatch" in capture["failure_reason"]


def test_ocs_clarification_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    cognition, semantic = _stack(tmp_path, ambiguous=True)
    generate_ocs_clarification(
        clarification_id="OCS-CLARIFICATION-CORRUPT-000001",
        ocs_cognition_artifact=cognition,
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_ocs_clarification_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["clarification_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_clarification_replay(tmp_path / "corrupt")


def test_ocs_clarification_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_clarification_runtime as runtime

    source = inspect.getsource(runtime)

    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "run_conversation_ppp" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
