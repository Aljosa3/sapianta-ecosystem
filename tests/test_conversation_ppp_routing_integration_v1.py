"""Tests for AIGOL_CONVERSATION_PPP_ROUTING_INTEGRATION_V1."""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.conversation_ppp_routing_integration import (
    CONVERSATION_PPP_HANDOFF_CREATED,
    reconstruct_conversation_ppp_routing_replay,
    run_conversation_ppp_routing_integration,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_repair_and_retry_runtime import HUMAN_CLARIFICATION_REQUIRED
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-03T13:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"
ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"


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


def _prompt() -> str:
    return (
        f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
        "No exchange integration. No order placement. No live trading."
    )


def _valid_response() -> dict[str, Any]:
    return {
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
        "assumptions": ["Trading worker foundation remains evidence-only."],
        "known_gaps": ["Runtime implementation remains future work."],
    }


def _ambiguous_response() -> dict[str, Any]:
    response = _valid_response()
    response["proposed_outputs"] = [
        "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
        "governance/TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1.md",
    ]
    return response


def test_conversation_ppp_routes_successful_provider_proposal_to_handoff(tmp_path) -> None:
    capture = run_conversation_ppp_routing_integration(
        prompt_id="PROMPT-PPP-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ppp",
        registry=_registry(),
        adapter=SequenceProviderAdapter([_valid_response()]),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-PPP-000001",
        latest_chain_id="CHAIN-PPP-000001",
    )
    reconstructed = reconstruct_conversation_ppp_routing_replay(tmp_path / "ppp")

    assert capture["route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert capture["implementation_handoff_reference"]
    assert capture["provider_invoked"] is True
    assert capture["approval_required"] is True
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["worker_created"] is False
    assert reconstructed["route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert reconstructed["replay_artifact_count"] == 2


def test_conversation_ppp_invokes_repair_retry_when_production_proposal_fails(tmp_path) -> None:
    capture = run_conversation_ppp_routing_integration(
        prompt_id="PROMPT-PPP-REPAIR-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "repair",
        registry=_registry(),
        adapter=SequenceProviderAdapter([_ambiguous_response(), _valid_response()]),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-PPP-000001",
        latest_chain_id="CHAIN-PPP-000001",
    )

    assert capture["route_status"] in {"HUMAN_APPROVAL_REQUIRED", "RETRY_SUCCEEDED"}
    assert capture["repair_retry_status"] == "HUMAN_APPROVAL_REQUIRED"
    assert capture["approval_required"] is True
    assert capture["provider_invoked"] is True
    assert capture["execution_requested"] is False


def test_conversation_ppp_surfaces_human_clarification_when_repair_requires_it(tmp_path, monkeypatch) -> None:
    import aigol.runtime.conversation_ppp_routing_integration as runtime

    def clarification_repair(**_kwargs):
        return {
            "retry_status": HUMAN_CLARIFICATION_REQUIRED,
            "clarification_required": True,
            "approval_required": False,
            "provider_proposal_repair_retry_capture_hash": "sha256:clarification",
        }

    monkeypatch.setattr(runtime, "repair_and_retry_provider_development_proposal", clarification_repair)

    capture = run_conversation_ppp_routing_integration(
        prompt_id="PROMPT-PPP-CLARIFICATION-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "clarification",
        registry=_registry(),
        adapter=SequenceProviderAdapter([_ambiguous_response()]),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-PPP-000001",
        latest_chain_id="CHAIN-PPP-000001",
    )

    assert capture["route_status"] == HUMAN_CLARIFICATION_REQUIRED
    assert capture["clarification_required"] is True
    assert capture["approval_required"] is False
    assert capture["execution_requested"] is False


def test_conversation_ppp_fails_closed_when_provider_unavailable(tmp_path) -> None:
    capture = run_conversation_ppp_routing_integration(
        prompt_id="PROMPT-PPP-UNAVAILABLE-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unavailable",
        registry=_registry(status=UNAVAILABLE),
        adapter=SequenceProviderAdapter([_valid_response()]),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-PPP-000001",
        latest_chain_id="CHAIN-PPP-000001",
    )

    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_conversation_ppp_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_conversation_ppp_routing_integration(
        prompt_id="PROMPT-PPP-CORRUPT-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        registry=_registry(),
        adapter=SequenceProviderAdapter([_valid_response()]),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-PPP-000001",
        latest_chain_id="CHAIN-PPP-000001",
    )
    path = tmp_path / "corrupt" / "conversation_ppp_route" / "000_conversation_ppp_route_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["context_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_ppp_routing_replay(tmp_path / "corrupt")


def test_conversation_ppp_runtime_has_no_execution_or_worker_creation_imports() -> None:
    import aigol.runtime.conversation_ppp_routing_integration as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
    assert "create_worker(" not in source
    assert "create_domain(" not in source
