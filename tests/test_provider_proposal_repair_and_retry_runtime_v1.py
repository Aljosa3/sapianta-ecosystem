"""Tests for AIGOL_PROVIDER_PROPOSAL_REPAIR_AND_RETRY_RUNTIME_V1."""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.development_context_assembly_runtime import assemble_development_context
from aigol.runtime.development_proposal_contract_runtime import (
    DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    validate_development_proposal_contract,
)
from aigol.runtime.domain_and_worker_resolution_registry import resolve_domain_worker_milestone
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake
from aigol.runtime.provider_necessity_policy_runtime import classify_provider_necessity
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_RESPONSE_ARTIFACT_V1
from aigol.runtime.provider_proposal_repair_and_retry_runtime import (
    HUMAN_APPROVAL_REQUIRED,
    HUMAN_CLARIFICATION_REQUIRED,
    HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1,
    HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1,
    MAX_PROVIDER_RETRIES,
    repair_and_retry_provider_development_proposal,
    reconstruct_provider_proposal_repair_and_retry_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-03T11:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"


@dataclass
class SequenceProviderAdapter:
    responses: list[dict[str, Any]]
    provider_id: str = PROVIDER_ID
    provider_version: str = PROVIDER_VERSION
    calls: int = field(default=0, init=False)

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        index = min(self.calls, len(self.responses) - 1)
        self.calls += 1
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.responses[index],
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


def _evidence_chain(tmp_path) -> tuple[dict, dict, dict, dict, dict, dict]:
    intake_capture = run_native_development_task_intake(
        intake_id="INTAKE-REPAIR-000001",
        human_prompt_reference="PROMPT-REPAIR-000001",
        human_prompt=(
            f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
            "No exchange integration. No order placement. No live trading."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
    )
    context_capture = assemble_development_context(
        context_assembly_id="CONTEXT-REPAIR-000001",
        development_task_intake_artifact=intake_capture["native_development_task_intake_artifact"],
        governance_root=GOVERNANCE_ROOT,
        replay_dir=tmp_path / "context",
        created_at=CREATED_AT,
    )
    registry_capture = resolve_domain_worker_milestone(
        resolution_id="REGISTRY-REPAIR-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "registry",
    )
    policy_capture = classify_provider_necessity(
        policy_decision_id="POLICY-REPAIR-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        task_kind="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "policy",
    )
    context = context_capture["development_context_assembly_artifact"]
    resolution = registry_capture["domain_worker_resolution_artifact"]
    rejected = _rejected_proposal(context, resolution)
    failure = validate_development_proposal_contract(
        contract_validation_id="CONTRACT-FAILURE-REPAIR-000001",
        proposal_artifact=rejected,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failure_contract",
    )["development_proposal_contract_validation_artifact"]
    return rejected, failure, _provider_response_artifact(), context, resolution, policy_capture[
        "provider_necessity_policy_artifact"
    ]


def _rejected_proposal(context: dict, resolution: dict) -> dict:
    proposal = {
        "artifact_type": DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
        "proposal_id": "PROPOSAL-REJECTED-REPAIR-000001",
        "task_reference": context["development_task_intake_reference"],
        "context_reference": context["context_assembly_id"],
        "context_hash": context["context_hash"],
        "domain_reference": resolution["domain_id"],
        "worker_reference": resolution["worker_family_id"],
        "milestone_reference": resolution["milestone_type"],
        "proposal_summary": "Rejected proposal missing proposed outputs.",
        "constraints_acknowledged": ["NO_BROKER_INTEGRATION"],
        "assumptions": ["Repair required."],
        "known_gaps": ["Missing outputs."],
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


def _provider_response_artifact() -> dict:
    artifact = {
        "artifact_type": PROVIDER_RESPONSE_ARTIFACT_V1,
        "production_id": "PROVIDER-PRODUCTION-REPAIR-000001",
        "provider_id": PROVIDER_ID,
        "provider_version": PROVIDER_VERSION,
        "provider_request_packet_reference": "PROVIDER-PRODUCTION-REPAIR-000001",
        "provider_request_packet_hash": "sha256:request",
        "provider_attachment_proposal_hash": "sha256:provider-proposal",
        "provider_attachment_created_hash": "sha256:provider-created",
        "provider_attachment_returned_hash": "sha256:provider-returned",
        "provider_response_payload": {"proposal_summary": "Rejected payload"},
        "provider_response_payload_hash": replay_hash({"proposal_summary": "Rejected payload"}),
        "provider_invocation_status": "PROVIDER_INVOKED",
        "created_at": CREATED_AT,
        "proposal_only": True,
        "provider_authority": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _valid_response() -> dict:
    return {
        "proposal_summary": "Corrected foundation-only Market Evidence Normalization Worker proposal.",
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
        "assumptions": ["Trading worker foundation remains non-executing."],
        "known_gaps": ["Runtime worker implementation remains future work."],
    }


def _invalid_response() -> dict:
    return {"proposal_summary": "Still missing required proposal fields."}


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    return artifact


def test_repair_retry_corrects_proposal_and_requires_human_approval_for_trading(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)

    capture = repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=SequenceProviderAdapter([_valid_response()]),
        replay_dir=tmp_path / "repair",
    )
    reconstructed = reconstruct_provider_proposal_repair_and_retry_replay(tmp_path / "repair")

    assert capture["retry_status"] == HUMAN_APPROVAL_REQUIRED
    assert capture["retry_count"] == 1
    assert capture["approval_required"] is True
    assert capture["clarification_required"] is False
    assert capture["retry_status_artifact"]["approval_request_hash"]
    assert capture["provider_retry_response"]["corrected_proposal_hash"]
    assert reconstructed["retry_status"] == HUMAN_APPROVAL_REQUIRED
    assert reconstructed["replay_artifact_count"] == 4
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False


def test_repair_retry_ambiguity_creates_human_clarification_without_provider_invocation(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)
    failure["failure_reason"] = "domain resolution is ambiguous: workstation could be domain, worker, artifact, or infrastructure"
    _rehash(failure)
    adapter = SequenceProviderAdapter([_valid_response()])

    capture = repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-CLARIFICATION-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=adapter,
        replay_dir=tmp_path / "clarification",
    )

    assert capture["retry_status"] == HUMAN_CLARIFICATION_REQUIRED
    assert capture["clarification_required"] is True
    assert capture["retry_count"] == 0
    assert adapter.calls == 0
    assert capture["provider_retry_response"]["escalation_reference"] == HUMAN_CLARIFICATION_REQUIRED_ARTIFACT_V1


def test_repair_retry_fails_closed_when_retry_limit_exceeded(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)

    capture = repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-LIMIT-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=SequenceProviderAdapter([_invalid_response()]),
        replay_dir=tmp_path / "limit",
        max_provider_retries=2,
    )

    assert capture["fail_closed"] is True
    assert capture["retry_count"] == 2
    assert "invalid proposal repeatedly returned" in capture["failure_reason"]


def test_repair_retry_fails_closed_when_provider_unavailable(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)

    capture = repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-UNAVAILABLE-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(status=UNAVAILABLE),
        adapter=SequenceProviderAdapter([_valid_response()]),
        replay_dir=tmp_path / "unavailable",
    )

    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_repair_retry_fails_closed_on_authority_violation(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)
    authority_response = _valid_response()
    authority_response["execution_authority"] = True

    capture = repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-AUTHORITY-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=SequenceProviderAdapter([authority_response]),
        replay_dir=tmp_path / "authority",
    )

    assert capture["fail_closed"] is True
    assert "authority violation" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_repair_retry_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    rejected, failure, response, context, resolution, policy = _evidence_chain(tmp_path)
    repair_and_retry_provider_development_proposal(
        repair_id="REPAIR-CORRUPT-000001",
        rejected_proposal_artifact=rejected,
        validation_failure_evidence=failure,
        provider_response_artifact=response,
        context_assembly_artifact=context,
        registry_resolution_artifact=resolution,
        provider_necessity_policy_artifact=policy,
        canonical_chain_id="CHAIN-REPAIR-000001",
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        registry=_registry(),
        adapter=SequenceProviderAdapter([_valid_response()]),
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_retry_status_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["corrected_proposal_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_proposal_repair_and_retry_replay(tmp_path / "corrupt")


def test_repair_retry_runtime_has_no_execution_or_worker_creation_imports() -> None:
    import aigol.runtime.provider_proposal_repair_and_retry_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
    assert "create_worker(" not in source
    assert "create_domain(" not in source
    assert str(MAX_PROVIDER_RETRIES) in source
