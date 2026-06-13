"""Tests for AIGOL_OCS_TO_PPP_CONTINUATION_ADAPTER_V1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.conversational_routing_visibility_runtime import (
    HIGH,
    ROUTING_SELECTED,
    record_conversational_routing_visibility,
)
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import create_ocs_to_ppp_handoff
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import (
    OCS_TO_PPP_CONTINUATION_REACHED_PPP,
    OCS_TO_PPP_PROPOSAL_ONLY_PRESERVED,
    continue_ocs_to_ppp_routing,
    reconstruct_ocs_to_ppp_continuation_replay,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.universal_intake_layer_runtime import (
    OCS_COGNITION_INTAKE,
    reconstruct_universal_intake_replay,
    record_universal_intake,
)


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-13T00:00:00Z"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"
OCS_PROMPT = "Which replay-derived trading worker improvement should enter governed execution next?"


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = PROVIDER_ID
    provider_version: str = PROVIDER_VERSION
    calls: int = 0

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        self.calls += 1
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
            timestamp=timestamp,
        )


def _artifact(artifact_type: str, artifact_id: str, **extra: object) -> dict[str, Any]:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "replay_visible": True,
        "authority": False,
        **extra,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=PROVIDER_ID,
            provider_type="llm",
            provider_version=PROVIDER_VERSION,
            provider_status=AVAILABLE,
            domain="native_development",
            capability="proposal_generation",
        )
    )
    return registry


def _valid_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create the trading market evidence normalization worker foundation.",
        "proposed_outputs": [
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": [
            "The worker remains read-only and evidence-normalization scoped.",
        ],
        "known_gaps": [
            "Runtime execution remains behind a separate authorization boundary.",
        ],
    }


def _ocs_handoff(tmp_path) -> dict[str, Any]:
    context = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-CONTINUATION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_chain_id="CHAIN-OCS-CONTINUATION-000001",
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
        cognition_id="OCS-COGNITION-CONTINUATION-000001",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id="OCS-INTENT-CONTINUATION-000001",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_intent",
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
        memory_continuity_id="OCS-MEMORY-CONTINUATION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_memory",
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
    semantic = resolve_ocs_semantics(
        semantic_resolution_id="OCS-SEMANTIC-CONTINUATION-000001",
        ocs_memory_artifact=memory_capture["ocs_memory_artifact"],
        ocs_continuity_artifact=memory_capture["ocs_continuity_artifact"],
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_semantic",
    )["ocs_semantic_resolution_artifact"]
    return create_ocs_to_ppp_handoff(
        handoff_id="OCS-PPP-HANDOFF-CONTINUATION-000001",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory_capture["ocs_memory_artifact"],
        ocs_continuity_artifact=memory_capture["ocs_continuity_artifact"],
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_handoff",
    )["ocs_to_ppp_handoff_artifact"]


def _record_universal_ocs_intake(tmp_path) -> dict[str, Any]:
    visibility = record_conversational_routing_visibility(
        turn_id="TURN-000001",
        prompt_id="SESSION-OCS-CONTINUATION:TURN-000001",
        human_prompt=OCS_PROMPT,
        workflow_id="OCS_LLM_COGNITION",
        routing_status=ROUTING_SELECTED,
        routing_confidence=HIGH,
        matched_signals=["ocs", "cognition"],
        competing_signals=[],
        routing_reason="Prompt requires cognition before execution handoff.",
        routing_timestamp=CREATED_AT,
        replay_dir=tmp_path / "routing_visibility",
    )
    return record_universal_intake(
        intake_id="SESSION-OCS-CONTINUATION:TURN-000001:UNIVERSAL-INTAKE",
        turn_id="TURN-000001",
        prompt_id="SESSION-OCS-CONTINUATION:TURN-000001",
        human_prompt=OCS_PROMPT,
        chain_id="CHAIN-OCS-CONTINUATION-000001",
        workflow_id="OCS_LLM_COGNITION",
        routing_visibility_artifact=visibility["conversational_routing_visibility_artifact"],
        routing_visibility_replay_reference=visibility["conversational_routing_visibility_replay_reference"],
        source_router_replay_reference=str(tmp_path / "source_router"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "universal_intake",
    )


def test_ocs_to_ppp_continuation_preserves_proposal_only_behavior_without_execution(tmp_path) -> None:
    handoff = _ocs_handoff(tmp_path)
    adapter = FakeProviderAdapter(_valid_response())

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-PPP-CONTINUATION-PROPOSAL-ONLY-000001",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=False,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuation_proposal_only",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
    )
    reconstructed = reconstruct_ocs_to_ppp_continuation_replay(tmp_path / "continuation_proposal_only")

    assert capture["continuation_status"] == OCS_TO_PPP_PROPOSAL_ONLY_PRESERVED
    assert capture["ppp_invoked"] is False
    assert capture["ppp_route_status"] is None
    assert adapter.calls == 0
    assert capture["provider_invoked_directly"] is False
    assert capture["worker_invoked_directly"] is False
    assert capture["worker_invoked"] is False
    assert capture["approval_created"] is False
    assert reconstructed["execution_required"] is False
    assert reconstructed["source_ocs_handoff_hash"] == handoff["artifact_hash"]


def test_universal_ocs_intake_to_ocs_handoff_continues_to_existing_ppp_routing(tmp_path) -> None:
    universal = _record_universal_ocs_intake(tmp_path)
    handoff = _ocs_handoff(tmp_path)
    adapter = FakeProviderAdapter(_valid_response())

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-PPP-CONTINUATION-EXECUTION-000001",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuation_execution",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
        prompt_id="SESSION-OCS-CONTINUATION:TURN-000001",
        session_id="SESSION-OCS-CONTINUATION",
        turn_id="TURN-000001",
        current_chain_id=universal["universal_intake_artifact"]["chain_id"],
        latest_chain_id=universal["universal_intake_artifact"]["chain_id"],
    )
    reconstructed = reconstruct_ocs_to_ppp_continuation_replay(tmp_path / "continuation_execution")
    universal_replay = reconstruct_universal_intake_replay(tmp_path / "universal_intake")

    assert universal_replay["intake_classification"] == OCS_COGNITION_INTAKE
    assert capture["continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert capture["execution_required"] is True
    assert capture["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert capture["ppp_invoked"] is True
    assert capture["provider_invoked_directly"] is False
    assert capture["provider_invoked_via_ppp"] is True
    assert adapter.calls == 1
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["worker_backbone_reused"] is True
    assert reconstructed["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert reconstructed["source_ocs_handoff_hash"] == handoff["artifact_hash"]


def test_ocs_to_ppp_continuation_fails_closed_on_corrupt_handoff(tmp_path) -> None:
    handoff = _ocs_handoff(tmp_path)
    handoff["artifact_hash"] = "sha256:wrong"

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-PPP-CONTINUATION-CORRUPT-000001",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuation_corrupt",
        registry=_registry(),
        adapter=FakeProviderAdapter(_valid_response()),
        governance_root=GOVERNANCE_ROOT,
    )

    assert capture["fail_closed"] is True
    assert capture["ppp_invoked"] is False
    assert capture["worker_invoked"] is False
    assert "hash mismatch" in capture["failure_reason"]
