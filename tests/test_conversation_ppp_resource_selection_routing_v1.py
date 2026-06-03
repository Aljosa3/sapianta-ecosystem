"""Tests for CONVERSATION_PPP_RESOURCE_SELECTION_ROUTING_V1."""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.conversation_ppp_resource_selection_routing import (
    CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED,
    CONVERSATION_RESOURCE_PPP_WORKER_HANDOFF_REFERENCE_READY,
    reconstruct_conversation_ppp_resource_selection_routing_replay,
    run_conversation_ppp_resource_selection_routing,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unified_resource_selection_runtime import HYBRID_PROVIDER_WORKER, PROVIDER, PROVIDER_ROLE, WORKER_ROLE


CREATED_AT = "2026-06-03T16:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"
PROVIDER_VERSION = "v1"
ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"


@dataclass
class SequenceProviderAdapter:
    responses: list[dict[str, Any]]
    provider_id: str
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


def _registry(provider_id: str, *, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=provider_id,
            provider_type="llm",
            provider_version=PROVIDER_VERSION,
            provider_status=status,
            domain="native_development",
            capability="proposal_generation",
        )
    )
    return registry


def _prompt(milestone_id: str = MILESTONE_ID) -> str:
    return (
        f"Implement {milestone_id}. Foundation only. No broker integration. "
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


def test_conversation_routes_openai_provider_resource_through_ppp_to_handoff(tmp_path) -> None:
    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-000001",
        human_prompt=_prompt(),
        provider_id="OPENAI",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "openai",
        registry=_registry("OPENAI"),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="OPENAI"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="OPENAI_PROVIDER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000001",
        latest_chain_id="CHAIN-RESOURCE-PPP-000001",
    )
    reconstructed = reconstruct_conversation_ppp_resource_selection_routing_replay(tmp_path / "openai")

    assert capture["route_status"] == CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED
    assert capture["selected_resource_id"] == "OPENAI"
    assert capture["selected_resource_category"] == PROVIDER
    assert capture["selected_role_type"] == PROVIDER_ROLE
    assert capture["provider_invoked"] is True
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["authorization_created"] is False
    assert reconstructed["route_status"] == CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED
    assert reconstructed["replay_artifact_count"] == 2


def test_conversation_routes_hybrid_codex_provider_role_with_explicit_role(tmp_path) -> None:
    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-CODEX-PROVIDER-000001",
        human_prompt=_prompt(),
        provider_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "codex-provider",
        registry=_registry("CODEX"),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="CODEX"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="CODEX_PROVIDER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000002",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000002",
        latest_chain_id="CHAIN-RESOURCE-PPP-000002",
    )

    assert capture["route_status"] == CONVERSATION_RESOURCE_PPP_HANDOFF_CREATED
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == PROVIDER_ROLE
    assert capture["provider_invoked"] is True
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_conversation_routes_hybrid_codex_worker_role_without_invoking_worker_or_provider(tmp_path) -> None:
    adapter = SequenceProviderAdapter([_valid_response()], provider_id="CODEX")

    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-CODEX-WORKER-000001",
        human_prompt=_prompt(),
        provider_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "codex-worker",
        registry=_registry("CODEX"),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="CODEX_WORKER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000003",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000003",
        latest_chain_id="CHAIN-RESOURCE-PPP-000003",
    )

    assert capture["route_status"] == CONVERSATION_RESOURCE_PPP_WORKER_HANDOFF_REFERENCE_READY
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == WORKER_ROLE
    assert capture["provider_invoked"] is False
    assert adapter.calls == 0
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False


def test_conversation_fails_closed_on_implicit_hybrid_role(tmp_path) -> None:
    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-AMBIGUOUS-000001",
        human_prompt=_prompt(),
        provider_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
        registry=_registry("CODEX"),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="CODEX"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="CODEX",
        session_id="SESSION-RESOURCE-PPP-000004",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000004",
        latest_chain_id="CHAIN-RESOURCE-PPP-000004",
    )

    assert capture["fail_closed"] is True
    assert "resource role ambiguous" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_conversation_fails_closed_on_selected_provider_mismatch(tmp_path) -> None:
    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-MISMATCH-000001",
        human_prompt=_prompt(),
        provider_id="ANTHROPIC",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "mismatch",
        registry=_registry("ANTHROPIC"),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="ANTHROPIC"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="OPENAI_PROVIDER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000005",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000005",
        latest_chain_id="CHAIN-RESOURCE-PPP-000005",
    )

    assert capture["fail_closed"] is True
    assert "selected provider resource mismatch" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_conversation_fails_closed_when_selected_provider_is_unavailable(tmp_path) -> None:
    capture = run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-UNAVAILABLE-000001",
        human_prompt=_prompt(),
        provider_id="OPENAI",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unavailable",
        registry=_registry("OPENAI", status=UNAVAILABLE),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="OPENAI"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="OPENAI_PROVIDER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000006",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000006",
        latest_chain_id="CHAIN-RESOURCE-PPP-000006",
    )

    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_conversation_resource_ppp_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_conversation_ppp_resource_selection_routing(
        prompt_id="PROMPT-RESOURCE-PPP-CORRUPT-000001",
        human_prompt=_prompt(),
        provider_id="OPENAI",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        registry=_registry("OPENAI"),
        adapter=SequenceProviderAdapter([_valid_response()], provider_id="OPENAI"),
        governance_root=GOVERNANCE_ROOT,
        explicit_resource_role="OPENAI_PROVIDER_ROLE",
        session_id="SESSION-RESOURCE-PPP-000007",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-RESOURCE-PPP-000007",
        latest_chain_id="CHAIN-RESOURCE-PPP-000007",
    )
    path = tmp_path / "corrupt" / "conversation_resource_ppp_route" / "000_conversation_resource_ppp_route_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_resource_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_ppp_resource_selection_routing_replay(tmp_path / "corrupt")


def test_conversation_resource_ppp_runtime_preserves_layer_authority_boundaries() -> None:
    import aigol.runtime.conversation_ppp_resource_selection_routing as runtime

    source = inspect.getsource(runtime)

    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "authorize_execution(" not in source
    assert "create_worker(" not in source
    assert "create_domain(" not in source
