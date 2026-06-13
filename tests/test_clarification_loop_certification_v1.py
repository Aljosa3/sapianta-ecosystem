"""Certification tests for AIGOL_CLARIFICATION_LOOP_CERTIFICATION_V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.cognition_comparison_runtime import run_cognition_comparison_runtime
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.intent_clarification_cognition_integration import (
    CLARIFIED_COGNITION_INPUT_CREATED,
    FAILED_CLOSED as CLARIFICATION_COGNITION_FAILED_CLOSED,
    integrate_clarification_resolution_with_cognition,
    reconstruct_intent_clarification_cognition_integration_replay,
)
from aigol.runtime.intent_clarification_dialog_runtime import (
    CLARIFICATION_RESOLVED,
    FAILED_CLOSED as CLARIFICATION_DIALOG_FAILED_CLOSED,
    reconstruct_intent_clarification_dialog_replay,
    run_intent_clarification_dialog,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_cognition_runtime import run_ocs_cognition
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_llm_cognition_continuity_and_clarification_runtime import (
    CLARIFICATION_REQUIRED,
    reconstruct_ocs_llm_cognition_continuity_and_clarification_replay,
    run_ocs_llm_cognition_continuity_and_clarification,
)
from aigol.runtime.ocs_memory_and_continuity_runtime import build_ocs_memory_and_continuity
from aigol.runtime.ocs_replay_derived_intent_runtime import generate_ocs_replay_derived_intent
from aigol.runtime.ocs_semantic_resolution_runtime import resolve_ocs_semantics
from aigol.runtime.ocs_to_ppp_binding_runtime import create_ocs_to_ppp_handoff
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import (
    OCS_TO_PPP_CONTINUATION_REACHED_PPP,
    continue_ocs_to_ppp_routing,
)
from aigol.runtime.transport.serialization import replay_hash


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-13T00:00:00Z"
PROVIDERS = ("provider-a", "provider-b", "provider-c")
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"
CHAIN_ID = "CHAIN-CLARIFICATION-LOOP-CERTIFICATION"
HUMAN_PROMPT = "Human asks OCS which governed implementation should proceed."


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


def _contracts() -> list[dict[str, Any]]:
    return [
        create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
        for provider_id in PROVIDERS
    ]


def _provider_registry() -> ProviderRegistry:
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


def _provider_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create the governed Claude external worker provider adapter foundation.",
        "proposed_outputs": [
            "governance/CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1.md",
            "governance/CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_CERTIFICATION.json",
        ],
        "constraints_acknowledged": ["NO_DISPATCH", "NO_INVOCATION", "NO_EXECUTION", "PROPOSAL_ONLY"],
        "assumptions": ["Execution remains behind authorization."],
        "known_gaps": ["Final implementation execution remains separately governed."],
    }


def _context(tmp_path: Path, *, suffix: str, extra_context: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    source_context = {
        "conversation_context": [
            _artifact(
                "HUMAN_REQUEST_ARTIFACT_V1",
                f"HUMAN-REQUEST-{suffix}",
                summary=HUMAN_PROMPT,
            )
        ],
        "clarification_context": extra_context or [],
    }
    if extra_context:
        source_context.update(
            {
                "ppp_context": [
                    _artifact(
                        "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                        "PPP-AIGOL-CLAUDE_EXTERNAL",
                        ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
                        provider_necessity_classification="PROVIDER_REQUIRED",
                        domain_id="AIGOL",
                        worker_family_id="CLAUDE_EXTERNAL",
                    )
                ],
                "domain_context": [
                    _artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", "AIGOL-DOMAIN", domain_id="AIGOL")
                ],
                "registry_context": [
                    _artifact(
                        "DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1",
                        "REGISTRY-AIGOL-CLAUDE_EXTERNAL",
                        domain_id="AIGOL",
                        worker_family_id="CLAUDE_EXTERNAL",
                    )
                ],
                "replay_visible_operation_context": [
                    _artifact(
                        "CLARIFIED_COGNITION_INPUT_ARTIFACT_V1",
                        "CLARIFIED-AIGOL-CLAUDE_EXTERNAL",
                        domain_id="AIGOL",
                        worker_family_id="CLAUDE_EXTERNAL",
                    )
                ],
            }
        )
    capture = assemble_ocs_context(
        context_assembly_id=f"OCS-CONTEXT-{suffix}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_context",
        source_context=source_context,
        source_chain_id=CHAIN_ID,
        source_request_reference=f"HUMAN-REQUEST-{suffix}",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _response_text(provider_id: str, payloads: dict[str, dict[str, Any]]) -> str:
    payload = payloads[provider_id]
    return json.dumps(
        {
            "findings": payload.get("findings", []),
            "assumptions": payload.get("assumptions", []),
            "alternatives": payload.get("alternatives", []),
            "risks": payload.get("risks", []),
            "uncertainties": payload.get("uncertainties", []),
            "confidence": payload.get("confidence", "MEDIUM"),
        },
        sort_keys=True,
    )


def _transports(payloads: dict[str, dict[str, Any]], *, failing_provider: str | None = None):
    transports = {}
    for provider_id in PROVIDERS:

        def call(_payload: dict[str, Any], metadata: dict[str, Any], provider_id: str = provider_id) -> dict[str, Any]:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            if failing_provider == provider_id:
                raise FailClosedRuntimeError(f"{provider_id} missing evidence")
            return {"output_text": _response_text(provider_id, payloads)}

        transports[provider_id] = call
    return transports


def _comparison(
    tmp_path: Path,
    *,
    payloads: dict[str, dict[str, Any]],
    suffix: str,
    failing_provider: str | None = None,
) -> dict[str, Any]:
    multi = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id=f"MULTI-PROVIDER-CLARIFICATION-{suffix}",
        human_request=HUMAN_PROMPT,
        ocs_context_artifact=_context(tmp_path, suffix=suffix),
        provider_contracts=_contracts(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_multi_provider",
        transport_registry=_transports(payloads, failing_provider=failing_provider),
    )
    assert multi["fail_closed"] is False
    comparison = run_cognition_comparison_runtime(
        cognition_comparison_id=f"COGNITION-COMPARISON-CLARIFICATION-{suffix}",
        multi_provider_result_bundle=multi["result_bundle"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_comparison",
    )
    assert comparison["fail_closed"] is False
    return comparison


def _conflict_payloads() -> dict[str, dict[str, Any]]:
    return {
        "provider-a": {
            "findings": ["Provider A conclusion: ask human to choose implementation target."],
            "assumptions": ["A assumes target is ambiguous."],
            "alternatives": ["Ask a bounded question."],
            "risks": ["Ambiguity risk."],
            "uncertainties": ["Target unknown."],
        },
        "provider-b": {
            "findings": ["Provider B conclusion: stage PPP for AIGOL Claude external worker."],
            "assumptions": ["B assumes target is AIGOL."],
            "alternatives": ["Proceed to candidate staging."],
            "risks": ["Approval risk."],
            "uncertainties": ["Worker family unknown."],
        },
        "provider-c": {
            "findings": ["Provider C conclusion: stop pending more evidence."],
            "assumptions": ["C assumes evidence is incomplete."],
            "alternatives": ["Gather evidence."],
            "risks": ["Evidence risk."],
            "uncertainties": ["Evidence missing."],
        },
    }


def _insufficient_payloads() -> dict[str, dict[str, Any]]:
    return {
        "provider-a": {"findings": ["Available conclusion: evidence is incomplete."], "confidence": "LOW"},
        "provider-b": {"findings": ["Available conclusion: evidence is incomplete."], "confidence": "LOW"},
        "provider-c": {"findings": ["Unavailable."], "confidence": "UNKNOWN"},
    }


def _continuity_clarification(tmp_path: Path, comparison: dict[str, Any], *, suffix: str) -> dict[str, Any]:
    capture = run_ocs_llm_cognition_continuity_and_clarification(
        continuity_id=f"COGNITION-CONTINUITY-{suffix}",
        clarification_id=f"COGNITION-CLARIFICATION-{suffix}",
        current_comparison_artifact=comparison["cognition_comparison_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_continuity_clarification",
    )
    assert capture["final_status"] == "COMPLETED"
    return capture


def _clarification_candidates() -> list[dict[str, Any]]:
    return [
        {
            "interpretation_id": "AIGOL_CLAUDE_EXTERNAL",
            "label": "Implement the AIGOL Claude external worker provider adapter foundation.",
            "domain_id": "AIGOL",
            "worker_family_id": "CLAUDE_EXTERNAL",
            "milestone_type": "WORKER_PROVIDER_ADAPTER",
            "capability_id": "PROPOSAL_GENERATION",
            "resource_category": "WORKER",
            "output_scope": "GOVERNANCE_FOUNDATION",
            "resume_stage": "COGNITION",
        },
        {
            "interpretation_id": "TRADING_MARKET_EVIDENCE",
            "label": "Implement Trading market evidence normalization worker foundation.",
            "domain_id": "TRADING",
            "worker_family_id": "MARKET_EVIDENCE_NORMALIZATION",
            "milestone_type": "WORKER_FOUNDATION",
            "capability_id": "EVIDENCE_NORMALIZATION",
            "resource_category": "WORKER",
            "output_scope": "GOVERNANCE_FOUNDATION",
            "resume_stage": "COGNITION",
        },
    ]


def _clarification_response(**overrides: Any) -> dict[str, Any]:
    response = {
        "selected_interpretation": "AIGOL_CLAUDE_EXTERNAL",
        "selected_domain_id": "AIGOL",
        "selected_worker_family_id": "CLAUDE_EXTERNAL",
        "selected_milestone_type": "WORKER_PROVIDER_ADAPTER",
        "selected_output_scope": "GOVERNANCE_FOUNDATION",
        "human_response_text": "Use the AIGOL Claude external worker provider adapter foundation.",
        "resume_stage": "COGNITION",
    }
    response.update(overrides)
    return response


def _human_clarification(tmp_path: Path, *, suffix: str, response: dict[str, Any]) -> dict[str, Any]:
    capture = run_intent_clarification_dialog(
        clarification_id=f"HUMAN-CLARIFICATION-{suffix}",
        canonical_chain_id=CHAIN_ID,
        human_prompt_reference=f"HUMAN-REQUEST-{suffix}",
        human_prompt=HUMAN_PROMPT,
        ambiguity_categories=["INTENT_AMBIGUITY", "WORKER_AMBIGUITY"],
        candidate_interpretations=_clarification_candidates(),
        human_response=response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_human_clarification",
    )
    assert Path(capture["human_clarification_dialog_replay_reference"]).exists()
    return capture


def _clarified_to_ppp(tmp_path: Path, clarified_input: dict[str, Any], *, suffix: str) -> dict[str, Any]:
    context = _context(tmp_path, suffix=f"{suffix}_UPDATED", extra_context=[clarified_input])
    cognition = run_ocs_cognition(
        cognition_id=f"OCS-COGNITION-{suffix}",
        ocs_context_assembly_artifact=context,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_cognition",
    )["ocs_cognition_artifact"]
    intent = generate_ocs_replay_derived_intent(
        intent_generation_id=f"OCS-INTENT-{suffix}",
        ocs_cognition_artifact=cognition,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_intent",
        failure_history=[
            _artifact("FAILURE_ARTIFACT_V1", f"FAIL-{suffix}-1", failure_reason="prior ambiguity"),
            _artifact("FAILURE_ARTIFACT_V1", f"FAIL-{suffix}-2", failure_reason="prior ambiguity"),
        ],
        validation_history=[
            _artifact("VALIDATION_ARTIFACT_V1", f"VAL-{suffix}-1", validation_status="FAILED"),
            _artifact("VALIDATION_ARTIFACT_V1", f"VAL-{suffix}-2", validation_status="FAILED"),
        ],
    )["ocs_replay_derived_intent_artifact"]
    registry = [_artifact("DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1", "REGISTRY-AIGOL", domain_id="AIGOL")]
    memory_capture = build_ocs_memory_and_continuity(
        memory_continuity_id=f"OCS-MEMORY-{suffix}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_memory",
        ocs_context_artifacts=[context],
        ocs_cognition_artifacts=[cognition],
        replay_derived_intent_artifacts=[intent],
        domain_registry_context=registry,
        replay_visible_operation_history=[
            _artifact(
                "CLARIFIED_COGNITION_INPUT_ARTIFACT_V1",
                clarified_input["clarified_cognition_input_id"],
                domain_id="AIGOL",
                worker_family_id="CLAUDE_EXTERNAL",
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
        replay_dir=tmp_path / f"{suffix}_ocs_semantic",
    )["ocs_semantic_resolution_artifact"]
    handoff = create_ocs_to_ppp_handoff(
        handoff_id=f"OCS-PPP-HANDOFF-{suffix}",
        ocs_context_assembly_artifact=context,
        ocs_cognition_artifact=cognition,
        ocs_replay_derived_intent_artifact=intent,
        ocs_memory_artifact=memory_capture["ocs_memory_artifact"],
        ocs_continuity_artifact=memory_capture["ocs_continuity_artifact"],
        ocs_semantic_resolution_artifact=semantic,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_handoff",
    )["ocs_to_ppp_handoff_artifact"]
    return continue_ocs_to_ppp_routing(
        continuation_id=f"OCS-PPP-CONTINUATION-{suffix}",
        ocs_to_ppp_handoff_artifact=handoff,
        execution_required=True,
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"{suffix}_ocs_to_ppp",
        registry=_provider_registry(),
        adapter=FakeProviderAdapter(_provider_response()),
        governance_root=GOVERNANCE_ROOT,
        prompt_id=f"SESSION-CLARIFICATION-{suffix}:TURN-000001",
        session_id=f"SESSION-CLARIFICATION-{suffix}",
        turn_id="TURN-000001",
        current_chain_id=CHAIN_ID,
        latest_chain_id=CHAIN_ID,
    )


def _assert_no_execution(capture: dict[str, Any]) -> None:
    assert capture.get("worker_invoked") is False
    assert capture.get("execution_requested") is False
    assert capture.get("dispatch_requested") is False
    assert capture.get("approval_created", False) is False
    assert capture.get("authorization_created", False) is False


def test_conflict_between_cognition_artifacts_requires_clarification_without_execution(tmp_path) -> None:
    comparison = _comparison(tmp_path, payloads=_conflict_payloads(), suffix="CONFLICT")
    clarification = _continuity_clarification(tmp_path, comparison, suffix="CONFLICT")
    replay = reconstruct_ocs_llm_cognition_continuity_and_clarification_replay(
        tmp_path / "CONFLICT_continuity_clarification"
    )

    assert clarification["clarification_required"] is True
    assert clarification["cognition_clarification_artifact"]["clarification_status"] == CLARIFICATION_REQUIRED
    assert clarification["cognition_clarification_artifact"]["clarification_required"] is True
    assert any(
        candidate["trigger"] == "DISAGREEMENT_THRESHOLD_EXCEEDED"
        for candidate in clarification["cognition_clarification_artifact"]["clarification_candidates"]
    )
    assert replay["clarification_required"] is True
    _assert_no_execution(clarification)


def test_insufficient_information_requires_clarification_without_execution(tmp_path) -> None:
    comparison = _comparison(
        tmp_path,
        payloads=_insufficient_payloads(),
        suffix="INSUFFICIENT",
        failing_provider="provider-c",
    )
    clarification = _continuity_clarification(tmp_path, comparison, suffix="INSUFFICIENT")

    assert clarification["clarification_required"] is True
    assert clarification["cognition_clarification_artifact"]["clarification_status"] == CLARIFICATION_REQUIRED
    assert any(
        candidate["trigger"] in {"UNCERTAINTY_THRESHOLD_EXCEEDED", "MISSING_INFORMATION_DETECTED"}
        for candidate in clarification["cognition_clarification_artifact"]["clarification_candidates"]
    )
    _assert_no_execution(clarification)


def test_human_clarification_resolves_ambiguity_and_proceeds_to_ppp(tmp_path) -> None:
    comparison = _comparison(tmp_path, payloads=_conflict_payloads(), suffix="RESOLVED")
    clarification = _continuity_clarification(tmp_path, comparison, suffix="RESOLVED")
    human = _human_clarification(tmp_path, suffix="RESOLVED", response=_clarification_response())
    cognition_input = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-LOOP-RESOLVED-COGNITION",
        clarification_request_artifact=human["human_clarification_request_artifact"],
        clarification_response_artifact=human["human_clarification_response_artifact"],
        clarification_resolution_artifact=human["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "RESOLVED_clarification_cognition",
    )
    ppp = _clarified_to_ppp(tmp_path, cognition_input["clarified_cognition_input_artifact"], suffix="RESOLVED")

    assert clarification["clarification_required"] is True
    assert clarification["cognition_clarification_artifact"]["clarification_status"] == CLARIFICATION_REQUIRED
    assert human["resolution_status"] == CLARIFICATION_RESOLVED
    assert cognition_input["integration_status"] == CLARIFIED_COGNITION_INPUT_CREATED
    assert ppp["continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert ppp["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert ppp["worker_invoked"] is False
    assert ppp["execution_requested"] is False
    assert ppp["dispatch_requested"] is False
    assert reconstruct_intent_clarification_dialog_replay(tmp_path / "RESOLVED_human_clarification")[
        "resolution_status"
    ] == CLARIFICATION_RESOLVED
    assert reconstruct_intent_clarification_cognition_integration_replay(
        tmp_path / "RESOLVED_clarification_cognition"
    )["integration_status"] == CLARIFIED_COGNITION_INPUT_CREATED


def test_unresolved_human_clarification_fails_closed_before_ppp(tmp_path) -> None:
    comparison = _comparison(tmp_path, payloads=_conflict_payloads(), suffix="UNRESOLVED")
    clarification = _continuity_clarification(tmp_path, comparison, suffix="UNRESOLVED")
    human = _human_clarification(
        tmp_path,
        suffix="UNRESOLVED",
        response=_clarification_response(selected_interpretation="UNKNOWN_CHOICE"),
    )
    cognition_input = integrate_clarification_resolution_with_cognition(
        integration_id="CLARIFICATION-LOOP-UNRESOLVED-COGNITION",
        clarification_request_artifact=human["human_clarification_request_artifact"],
        clarification_response_artifact=human["human_clarification_response_artifact"],
        clarification_resolution_artifact=human["human_clarification_resolution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "UNRESOLVED_clarification_cognition",
    )

    assert clarification["clarification_required"] is True
    assert clarification["cognition_clarification_artifact"]["clarification_status"] == CLARIFICATION_REQUIRED
    assert human["resolution_status"] == CLARIFICATION_DIALOG_FAILED_CLOSED
    assert "ambiguity remains unresolved" in human["failure_reason"]
    assert cognition_input["integration_status"] == CLARIFICATION_COGNITION_FAILED_CLOSED
    assert "clarification unresolved" in cognition_input["failure_reason"]
    _assert_no_execution(human)
    _assert_no_execution(cognition_input)
    assert not (tmp_path / "UNRESOLVED_ocs_to_ppp").exists()
