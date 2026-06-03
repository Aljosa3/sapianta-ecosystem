"""Tests for AIGOL_PROVIDER_PROPOSAL_PRODUCTION_RUNTIME_V1."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.conversation_to_implementation_handoff_runtime import create_conversation_to_implementation_handoff
from aigol.runtime.development_context_assembly_runtime import assemble_development_context
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import resolve_domain_worker_milestone
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_PROHIBITED, classify_provider_necessity
from aigol.runtime.provider_proposal_production_runtime import (
    PROVIDER_PROPOSAL_PRODUCED,
    PROVIDER_REQUEST_PACKET_V1,
    PROVIDER_RESPONSE_ARTIFACT_V1,
    produce_provider_development_proposal,
    reconstruct_provider_proposal_production_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-03T09:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = PROVIDER_ID
    provider_version: str = PROVIDER_VERSION

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
            timestamp=timestamp,
        )


def _registry(*, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=PROVIDER_ID,
            provider_type="llm",
            provider_version=PROVIDER_VERSION,
            provider_status=status,
            domain="native_development",
            capability="proposal_generation",
        )
    )
    return registry


def _evidence_chain(tmp_path) -> tuple[dict, dict, dict, dict]:
    intake_capture = run_native_development_task_intake(
        intake_id="INTAKE-PROVIDER-PRODUCTION-000001",
        human_prompt_reference="PROMPT-PROVIDER-PRODUCTION-000001",
        human_prompt=(
            f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
            "No exchange integration. No order placement. No live trading."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
    )
    context_capture = assemble_development_context(
        context_assembly_id="CONTEXT-PROVIDER-PRODUCTION-000001",
        development_task_intake_artifact=intake_capture["native_development_task_intake_artifact"],
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "context",
        created_at=CREATED_AT,
    )
    registry_capture = resolve_domain_worker_milestone(
        resolution_id="REGISTRY-PROVIDER-PRODUCTION-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "registry",
    )
    policy_capture = classify_provider_necessity(
        policy_decision_id="POLICY-PROVIDER-PRODUCTION-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        task_kind="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "policy",
    )
    context = context_capture["development_context_assembly_artifact"]
    resolution = registry_capture["domain_worker_resolution_artifact"]
    policy = policy_capture["provider_necessity_policy_artifact"]
    seed_proposal = _seed_proposal(context, resolution)
    validation = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-SEED-PROVIDER-PRODUCTION-000001",
        proposal_artifact=seed_proposal,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "seed_contract",
    )
    handoff = create_conversation_to_implementation_handoff(
        handoff_id="HANDOFF-PROVIDER-PRODUCTION-000001",
        proposal_artifact=seed_proposal,
        proposal_contract_validation_artifact=validation["development_proposal_contract_validation_artifact"],
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "seed_handoff",
    )
    return handoff["implementation_handoff_artifact"], context, resolution, policy


def _seed_proposal(context: dict, resolution: dict) -> dict:
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": "PROPOSAL-SEED-PROVIDER-PRODUCTION-000001",
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "proposal_summary": "Seed handoff for provider proposal production.",
        "proposed_outputs": [
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_CERTIFICATION.json",
        ],
        "constraints_acknowledged": ["NO_BROKER_INTEGRATION", "NO_EXCHANGE_INTEGRATION"],
        "assumptions": ["Provider proposal production remains proposal-only."],
        "known_gaps": ["Provider-generated proposal still needs validation."],
        "proposal_only": True,
        "execution_authority": False,
        "dispatch_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    proposal["artifact_hash"] = replay_hash(proposal)
    return proposal


def _provider_response(*, overrides: dict | None = None) -> dict:
    response = {
        "proposal_summary": "Create a foundation-only Market Evidence Normalization Worker.",
        "proposed_outputs": [
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
            "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_BROKER_INTEGRATION",
            "NO_EXCHANGE_INTEGRATION",
            "NO_ORDER_PLACEMENT",
            "NO_LIVE_TRADING",
            "PROPOSAL_ONLY",
        ],
        "assumptions": ["Trading Domain worker taxonomy is certified."],
        "known_gaps": ["Runtime implementation remains a future milestone."],
    }
    if overrides:
        response.update(overrides)
    return response


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_provider_proposal_production_generates_validated_proposal(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter(_provider_response()),
        replay_dir=tmp_path / "production",
    )
    reconstructed = reconstruct_provider_proposal_production_replay(tmp_path / "production")

    assert capture["production_status"] == PROVIDER_PROPOSAL_PRODUCED
    assert capture["provider_request_packet"]["artifact_type"] == PROVIDER_REQUEST_PACKET_V1
    assert capture["provider_response_artifact"]["artifact_type"] == PROVIDER_RESPONSE_ARTIFACT_V1
    assert capture["development_proposal_artifact"]["artifact_type"] == DEVELOPMENT_PROPOSAL_ARTIFACT_V1
    assert capture["development_proposal_artifact"]["proposal_only"] is True
    assert capture["provider_invocation_status"] == "PROVIDER_INVOKED"
    assert capture["context_hash"] == context["context_hash"]
    assert capture["canonical_chain_id"] == "CHAIN-PROVIDER-PRODUCTION-000001"
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["worker_created"] is False
    assert reconstructed["production_status"] == PROVIDER_PROPOSAL_PRODUCED
    assert reconstructed["replay_artifact_count"] == 4


def test_provider_proposal_production_fails_closed_when_provider_unavailable(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-UNAVAILABLE-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(status=UNAVAILABLE),
        adapter=FakeProviderAdapter(_provider_response()),
        replay_dir=tmp_path / "unavailable",
    )

    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_provider_proposal_production_fails_closed_when_policy_prohibits_provider(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)
    policy["necessity_classification"] = PROVIDER_PROHIBITED
    _rehash(policy)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-PROHIBITED-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter(_provider_response()),
        replay_dir=tmp_path / "prohibited",
    )

    assert capture["fail_closed"] is True
    assert "provider prohibited by policy" in capture["failure_reason"]
    assert capture["provider_invocation_status"] == "PROVIDER_NOT_INVOKED"


def test_provider_proposal_production_fails_closed_on_invalid_provider_response(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-INVALID-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter({"proposal_summary": "Incomplete"}),
        replay_dir=tmp_path / "invalid",
    )

    assert capture["fail_closed"] is True
    assert "provider response invalid" in capture["failure_reason"]


def test_provider_proposal_production_fails_closed_on_proposal_contract_failure(tmp_path, monkeypatch) -> None:
    import aigol.runtime.provider_proposal_production_runtime as runtime

    handoff, context, resolution, policy = _evidence_chain(tmp_path)

    def failed_contract(**_kwargs):
        return {"validation_status": "FAILED_CLOSED", "failure_reason": "proposal contract validation fails"}

    monkeypatch.setattr(runtime, "validate_development_proposal_contract", failed_contract)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-CONTRACT-FAILED-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter(_provider_response()),
        replay_dir=tmp_path / "contract_failed",
    )

    assert capture["fail_closed"] is True
    assert "proposal contract validation fails" in capture["failure_reason"]


def test_provider_proposal_production_fails_closed_on_authority_violation(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)

    capture = produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-AUTHORITY-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter(_provider_response(overrides={"execution_authority": True})),
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert "authority violation" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_provider_proposal_production_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    handoff, context, resolution, policy = _evidence_chain(tmp_path)
    produce_provider_development_proposal(
        production_id="PROVIDER-PRODUCTION-CORRUPT-000001",
        provider_id=PROVIDER_ID,
        handoff_artifact=handoff,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-PROVIDER-PRODUCTION-000001",
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=FakeProviderAdapter(_provider_response()),
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_development_proposal_artifact_produced.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_proposal_production_replay(tmp_path / "corrupt")


def test_provider_proposal_production_runtime_has_no_execution_or_worker_creation_imports() -> None:
    import aigol.runtime.provider_proposal_production_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
    assert "create_worker(" not in source
    assert "create_domain(" not in source
