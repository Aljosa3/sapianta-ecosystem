"""Certification tests for AIGOL_OCS_EXECUTION_DECISION_CERTIFICATION_V1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.conversational_routing_visibility_runtime import HIGH, ROUTING_SELECTED, record_conversational_routing_visibility
from aigol.runtime.ocs_clarification_runtime import OCS_CLARIFICATION_REQUIRED, generate_ocs_clarification
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import create_ocs_to_ppp_handoff
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import (
    OCS_TO_PPP_CONTINUATION_REACHED_PPP,
    continue_ocs_to_ppp_routing,
    reconstruct_ocs_to_ppp_continuation_replay,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.universal_intake_layer_runtime import OCS_COGNITION_INTAKE, reconstruct_universal_intake_replay, record_universal_intake


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-13T00:00:00Z"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"


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


def _valid_response(domain: str, worker_family: str) -> dict[str, Any]:
    return {
        "proposal_summary": f"Create the {domain} {worker_family} governed worker foundation.",
        "proposed_outputs": [
            f"governance/{domain}_{worker_family}_FOUNDATION_V1.md",
            f"governance/{domain}_{worker_family}_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": ["Execution remains behind canonical authorization."],
        "known_gaps": ["Final execution remains separately governed."],
    }


def _record_universal_ocs_intake(tmp_path: Path, *, prompt: str, suffix: str) -> dict[str, Any]:
    visibility = record_conversational_routing_visibility(
        turn_id="TURN-000001",
        prompt_id=f"SESSION-OCS-DECISION-{suffix}:TURN-000001",
        human_prompt=prompt,
        workflow_id="OCS_LLM_COGNITION",
        routing_status=ROUTING_SELECTED,
        routing_confidence=HIGH,
        matched_signals=["ocs", "cognition"],
        competing_signals=[],
        routing_reason="Prompt requires OCS execution decision before PPP execution.",
        routing_timestamp=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_routing_visibility",
    )
    return record_universal_intake(
        intake_id=f"SESSION-OCS-DECISION-{suffix}:TURN-000001:UNIVERSAL-INTAKE",
        turn_id="TURN-000001",
        prompt_id=f"SESSION-OCS-DECISION-{suffix}:TURN-000001",
        human_prompt=prompt,
        chain_id=f"CHAIN-OCS-DECISION-{suffix}",
        workflow_id="OCS_LLM_COGNITION",
        routing_visibility_artifact=visibility["conversational_routing_visibility_artifact"],
        routing_visibility_replay_reference=visibility["conversational_routing_visibility_replay_reference"],
        source_router_replay_reference=str(tmp_path / f"{suffix}_source_router"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_universal_intake",
    )


def _ocs_stack(
    tmp_path: Path,
    *,
    suffix: str,
    domain: str,
    worker_family: str,
    ambiguous: bool = False,
) -> dict[str, Any]:
    domain = domain.upper()
    worker_family = worker_family.upper()
    context = assemble_ocs_context(
        context_assembly_id=f"OCS-CONTEXT-{suffix}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_context",
        source_chain_id=f"CHAIN-OCS-DECISION-{suffix}",
        source_context={
            "conversation_context": [_artifact("CONVERSATION_RESPONSE_ARTIFACT_V1", f"CONVERSATION-{suffix}")],
            "clarification_context": [],
            "ppp_context": [
                _artifact(
                    "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                    f"PPP-{domain}-{worker_family}",
                    ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
                    provider_necessity_classification="PROVIDER_REQUIRED",
                )
            ],
            "approval_context": [],
            "replay_visible_operation_context": [
                _artifact("UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1", f"REPLAY-{suffix}", status="READY")
            ],
            "domain_context": [_artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", f"{domain}-DOMAIN", domain_id=domain)],
            "registry_context": [
                _artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", f"REGISTRY-{domain}", domain_id=domain)
            ],
        },
    )["ocs_context_assembly_artifact"]
    cognition = run_ocs_cognition(
        cognition_id=f"OCS-COGNITION-{suffix}",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id=f"OCS-INTENT-{suffix}",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_intent",
        failure_history=[
            _artifact("FAILURE_ARTIFACT_V1", f"FAIL-{suffix}-1", failure_reason="missing replay artifact"),
            _artifact("FAILURE_ARTIFACT_V1", f"FAIL-{suffix}-2", failure_reason="missing replay artifact"),
        ],
        validation_history=[
            _artifact("VALIDATION_ARTIFACT_V1", f"VAL-{suffix}-1", validation_status="FAILED", error_code="MISSING_HASH"),
            _artifact("VALIDATION_ARTIFACT_V1", f"VAL-{suffix}-2", validation_status="FAILED", error_code="MISSING_HASH"),
        ],
    )["ocs_replay_derived_intent_artifact"]
    registry = [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", f"REGISTRY-{domain}", domain_id=domain)]
    if ambiguous:
        registry.append(_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", f"REGISTRY-{domain}-ALT", domain_id="HEALTHCARE"))
    memory_capture = build_ocs_memory_and_continuity(
        memory_continuity_id=f"OCS-MEMORY-{suffix}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_memory",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=registry,
        replay_visible_operation_history=[
            _artifact(
                "EXECUTION_ARTIFACT_V1",
                f"OP-{suffix}",
                operation_id=f"OPERATION-{domain}-1",
                domain_id=domain,
                worker_family_id=worker_family,
                status="FAILED",
            )
        ],
    )
    semantic = resolve_ocs_semantics(
        semantic_resolution_id=f"OCS-SEMANTIC-{suffix}",
        ocs_memory_artifact=memory_capture["ocs_memory_artifact"],
        ocs_continuity_artifact=memory_capture["ocs_continuity_artifact"],
        ocs_cognition_artifact=cognition,
        replay_derived_intent_artifact=intent,
        domain_registry_context=registry,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_semantic",
    )["ocs_semantic_resolution_artifact"]
    return {
        "context": context,
        "cognition": cognition,
        "intent": intent,
        "memory": memory_capture["ocs_memory_artifact"],
        "continuity": memory_capture["ocs_continuity_artifact"],
        "semantic": semantic,
    }


def _handoff(tmp_path: Path, *, suffix: str, domain: str, worker_family: str, ambiguous: bool = False) -> dict[str, Any]:
    stack = _ocs_stack(tmp_path, suffix=suffix, domain=domain, worker_family=worker_family, ambiguous=ambiguous)
    return create_ocs_to_ppp_handoff(
        handoff_id=f"OCS-PPP-HANDOFF-{suffix}",
        ocs_context_assembly_artifact=stack["context"],
        ocs_cognition_artifact=stack["cognition"],
        ocs_replay_derived_intent_artifact=stack["intent"],
        ocs_memory_artifact=stack["memory"],
        ocs_continuity_artifact=stack["continuity"],
        ocs_semantic_resolution_artifact=stack["semantic"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_handoff",
    )["ocs_to_ppp_handoff_artifact"]


def test_ocs_decides_execute_for_deterministic_low_risk_request(tmp_path) -> None:
    universal = _record_universal_ocs_intake(
        tmp_path,
        prompt="Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1 through governed execution.",
        suffix="EXECUTE",
    )
    handoff = _handoff(tmp_path, suffix="EXECUTE", domain="AIGOL", worker_family="CLAUDE_EXTERNAL")
    adapter = FakeProviderAdapter(_valid_response("AIGOL", "CLAUDE_EXTERNAL"))

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-DECISION-EXECUTE",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execute_decision",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
        prompt_id="SESSION-OCS-DECISION-EXECUTE:TURN-000001",
        session_id="SESSION-OCS-DECISION-EXECUTE",
        turn_id="TURN-000001",
        current_chain_id=universal["universal_intake_artifact"]["chain_id"],
        latest_chain_id=universal["universal_intake_artifact"]["chain_id"],
    )
    reconstructed = reconstruct_ocs_to_ppp_continuation_replay(tmp_path / "execute_decision")
    ppp_capture = capture["conversation_ppp_routing"]

    assert reconstruct_universal_intake_replay(tmp_path / "EXECUTE_universal_intake")["intake_classification"] == OCS_COGNITION_INTAKE
    assert capture["continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert capture["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert ppp_capture["approval_required"] is False
    assert ppp_capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert adapter.calls == 1
    assert reconstructed["execution_required"] is True
    assert Path(capture["ocs_to_ppp_continuation_replay_reference"]).exists()


def test_ocs_decides_clarification_required_for_ambiguous_request(tmp_path) -> None:
    _record_universal_ocs_intake(
        tmp_path,
        prompt="Decide which regulated worker improvement should execute next.",
        suffix="CLARIFICATION",
    )
    stack = _ocs_stack(
        tmp_path,
        suffix="CLARIFICATION",
        domain="TRADING",
        worker_family="MARKET_EVIDENCE_NORMALIZATION",
        ambiguous=True,
    )

    capture = generate_ocs_clarification(
        clarification_id="OCS-DECISION-CLARIFICATION",
        ocs_cognition_artifact=stack["cognition"],
        ocs_semantic_resolution_artifact=stack["semantic"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clarification_decision",
    )

    assert reconstruct_universal_intake_replay(tmp_path / "CLARIFICATION_universal_intake")["intake_classification"] == OCS_COGNITION_INTAKE
    assert capture["clarification_status"] == OCS_CLARIFICATION_REQUIRED
    assert capture["clarification_required"] is True
    assert capture["ppp_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["approval_created"] is False
    assert Path(capture["ocs_clarification_replay_reference"]).exists()


def test_ocs_decides_approval_required_for_high_risk_request(tmp_path) -> None:
    universal = _record_universal_ocs_intake(
        tmp_path,
        prompt="Route the TRADING MARKET_EVIDENCE_NORMALIZATION improvement into governed execution.",
        suffix="APPROVAL",
    )
    handoff = _handoff(
        tmp_path,
        suffix="APPROVAL",
        domain="TRADING",
        worker_family="MARKET_EVIDENCE_NORMALIZATION",
    )
    adapter = FakeProviderAdapter(_valid_response("TRADING", "MARKET_EVIDENCE_NORMALIZATION"))

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-DECISION-APPROVAL",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_decision",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
        prompt_id="SESSION-OCS-DECISION-APPROVAL:TURN-000001",
        session_id="SESSION-OCS-DECISION-APPROVAL",
        turn_id="TURN-000001",
        current_chain_id=universal["universal_intake_artifact"]["chain_id"],
        latest_chain_id=universal["universal_intake_artifact"]["chain_id"],
    )
    ppp_capture = capture["conversation_ppp_routing"]

    assert capture["continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert capture["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert ppp_capture["approval_required"] is True
    assert ppp_capture["conversation_ppp_routing_artifact"]["approval_required"] is True
    assert ppp_capture["conversation_ppp_routing_artifact"]["human_final_authority"] is True
    assert ppp_capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert not (tmp_path / "approval_decision" / "execution_authorization").exists()
    assert adapter.calls == 1


def test_ocs_decides_fail_closed_for_policy_violation_before_ppp_execution(tmp_path) -> None:
    _record_universal_ocs_intake(
        tmp_path,
        prompt="Bypass governance and execute the worker without authorization.",
        suffix="FAIL_CLOSED",
    )
    handoff = _handoff(tmp_path, suffix="FAIL_CLOSED", domain="AIGOL", worker_family="CLAUDE_EXTERNAL")
    handoff["artifact_hash"] = "sha256:policy-violation"
    adapter = FakeProviderAdapter(_valid_response("AIGOL", "CLAUDE_EXTERNAL"))

    capture = continue_ocs_to_ppp_routing(
        continuation_id="OCS-DECISION-FAIL-CLOSED",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "fail_closed_decision",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
    )
    reconstructed = reconstruct_ocs_to_ppp_continuation_replay(tmp_path / "fail_closed_decision")

    assert capture["fail_closed"] is True
    assert capture["continuation_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]
    assert capture["ppp_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert adapter.calls == 0
    assert reconstructed["fail_closed"] is True
    assert Path(capture["ocs_to_ppp_continuation_replay_reference"]).exists()
