"""Tests for AIGOL_CONTEXT_ASSEMBLED_TO_PPP_ROUTING_CONTINUATION_V1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.context_assembled_to_ppp_routing_continuation import (
    POST_CONTEXT_CONTINUATION_ARTIFACT_V1,
    POST_CONTEXT_CONTINUATION_REACHED_PPP,
    continue_context_assembled_to_ppp_routing,
    reconstruct_context_assembled_to_ppp_routing_continuation_replay,
)
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.domain_and_worker_resolution_registry import (
    RESOLUTION_SUCCEEDED,
    resolve_domain_worker_milestone,
)


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-12T00:00:00Z"
PROVIDER_ID = "TEST_PROVIDER"
PROVIDER_VERSION = "v1"
CLAUDE_MILESTONE = "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"


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
        f"Implement {CLAUDE_MILESTONE}. Create the missing provider adapter proposal request only. "
        "No dispatch. No invocation. No execution."
    )


def _valid_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create a proposal-only Claude external worker provider adapter.",
        "proposed_outputs": [
            "aigol/runtime/claude_external_worker_provider_adapter.py",
            "tests/test_claude_external_worker_provider_adapter_v1.py",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": [
            "Adapter remains provider-neutral above the adapter layer.",
        ],
        "known_gaps": [
            "Real Claude endpoint invocation remains separately certified.",
        ],
    }


def test_aigol_claude_external_registry_entries_resolve(tmp_path) -> None:
    capture = resolve_domain_worker_milestone(
        resolution_id="REGISTRY-AIGOL-CLAUDE-EXTERNAL-000001",
        domain_id="AIGOL",
        worker_family_id="CLAUDE_EXTERNAL",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "registry",
    )

    assert capture["resolution_status"] == RESOLUTION_SUCCEEDED
    assert capture["domain_id"] == "AIGOL"
    assert capture["worker_family_id"] == "CLAUDE_EXTERNAL"
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False


def test_claude_context_assembled_continues_to_existing_ppp_routing(tmp_path) -> None:
    adapter = FakeProviderAdapter(_valid_response())

    capture = continue_context_assembled_to_ppp_routing(
        continuation_id="POST-CONTEXT-CONTINUATION-000001",
        prompt_id="PROMPT-CLAUDE-POST-CONTEXT-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuation",
        registry=_registry(),
        adapter=adapter,
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-CLAUDE-POST-CONTEXT-000001",
        turn_id="TURN-000001",
        current_chain_id="CHAIN-CLAUDE-POST-CONTEXT-000001",
        latest_chain_id="CHAIN-CLAUDE-POST-CONTEXT-000001",
    )
    reconstructed = reconstruct_context_assembled_to_ppp_routing_continuation_replay(tmp_path / "continuation")
    artifact = capture["post_context_continuation_artifact"]

    assert artifact["artifact_type"] == POST_CONTEXT_CONTINUATION_ARTIFACT_V1
    assert capture["continuation_status"] == POST_CONTEXT_CONTINUATION_REACHED_PPP
    assert capture["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert capture["domain_reference"] == "AIGOL"
    assert capture["worker_reference"] == "CLAUDE_EXTERNAL"
    assert capture["implementation_handoff_reference"]
    assert capture["provider_invoked"] is True
    assert adapter.calls == 1
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["continuation_status"] == POST_CONTEXT_CONTINUATION_REACHED_PPP
    assert reconstructed["domain_reference"] == "AIGOL"
    assert reconstructed["worker_reference"] == "CLAUDE_EXTERNAL"


def test_post_context_continuation_preserves_fail_closed_provider_unavailable(tmp_path) -> None:
    capture = continue_context_assembled_to_ppp_routing(
        continuation_id="POST-CONTEXT-CONTINUATION-UNAVAILABLE-000001",
        prompt_id="PROMPT-CLAUDE-POST-CONTEXT-UNAVAILABLE-000001",
        human_prompt=_prompt(),
        provider_id=PROVIDER_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuation",
        registry=_registry(status=UNAVAILABLE),
        adapter=FakeProviderAdapter(_valid_response()),
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-CLAUDE-POST-CONTEXT-UNAVAILABLE-000001",
        turn_id="TURN-000001",
    )
    reconstructed = reconstruct_context_assembled_to_ppp_routing_continuation_replay(tmp_path / "continuation")

    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["continuation_status"] == "FAILED_CLOSED"
