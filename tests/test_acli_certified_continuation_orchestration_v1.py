"""Regression tests for AIGOL_ACLI_CERTIFIED_CONTINUATION_ORCHESTRATION_V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter, openai_provider_metadata
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.execution_authorization_runtime import EXECUTION_AUTHORIZED
from aigol.runtime.governed_implementation_dry_run import EXECUTION_READY
from aigol.runtime.implementation_handoff_visibility import IMPLEMENTATION_HANDOFF_SUMMARY_CREATED
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import OCS_TO_PPP_CONTINUATION_REACHED_PPP
from aigol.runtime.worker_invocation_request_runtime import WORKER_INVOCATION_REQUEST_CREATED


CREATED_AT = "2026-06-13T00:00:00Z"
NATIVE_PROMPT = (
    "Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1. Goal: Extend the certified "
    "provider-neutral external worker architecture with Claude support while reusing existing governance, "
    "replay, validation, mutation, and worker lifecycle infrastructure."
)
OCS_EXECUTION_PROMPT = (
    "What should Sapianta do with the replay-derived TRADING MARKET_EVIDENCE_NORMALIZATION "
    "worker improvement to enter governed execution next?"
)
OCS_PROPOSAL_ONLY_PROMPT = "I want to create the first real commercial Sapianta product."


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = "openai"
    provider_version: str = openai_provider_metadata().provider_version
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


def _args(tmp_path, *, session_id: str, auto_continue: bool = False):
    parser = build_parser()
    raw = [
        "conversation",
        "--session-id",
        session_id,
        "--created-at",
        CREATED_AT,
        "--runtime-root",
        str(tmp_path / "interactive_runtime"),
        "--workspace",
        str(tmp_path),
    ]
    if auto_continue:
        raw.append("--auto-continue")
    return parser.parse_args(raw)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _valid_provider_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create the governed worker/provider foundation.",
        "proposed_outputs": [
            "governance/WORKER_PROVIDER_FOUNDATION_V1.md",
            "governance/WORKER_PROVIDER_FOUNDATION_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": ["The worker lifecycle remains governed by existing runtimes."],
        "known_gaps": ["Provider execution remains behind authorization."],
    }


def _install_fake_proposal_adapter(monkeypatch) -> FakeProviderAdapter:
    adapter = FakeProviderAdapter(_valid_provider_response())
    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: adapter)
    return adapter


def _install_fake_ocs_provider(monkeypatch) -> None:
    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-acli-certified-continuation-ocs-001",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["Governed execution may be required."],
                                    "assumptions": ["Replay-derived evidence remains non-authoritative."],
                                    "alternatives": ["Proposal only", "PPP continuation"],
                                    "risks": ["Execution remains gated."],
                                    "uncertainties": ["Operator approval can still halt continuation."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(
        aigol_cli,
        "_conversation_openai_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client),
    )


def test_development_acli_auto_continue_reaches_domain_worker_request(tmp_path, monkeypatch) -> None:
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-CERTIFIED-CONTINUATION-DEV", auto_continue=True),
        input_func=_input_sequence([NATIVE_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert turn["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert turn["implementation_handoff_visibility_status"] == IMPLEMENTATION_HANDOFF_SUMMARY_CREATED
    assert turn["execution_preparation_status"] == EXECUTION_READY
    assert turn["execution_authorization_status"] == EXECUTION_AUTHORIZED
    assert turn["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert turn["worker_request_reached"] is True
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert proposal_adapter.calls == 1


def test_ocs_acli_reaches_ppp_only_when_execution_explicitly_required(tmp_path, monkeypatch) -> None:
    _install_fake_ocs_provider(monkeypatch)
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-CERTIFIED-CONTINUATION-OCS-EXECUTION"),
        input_func=_input_sequence([OCS_EXECUTION_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert turn["ocs_to_ppp_continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert turn["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert turn["ppp_invoked"] is True
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert proposal_adapter.calls == 1


def test_ocs_acli_proposal_only_prompt_stops_before_ppp(tmp_path, monkeypatch) -> None:
    _install_fake_ocs_provider(monkeypatch)
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-CERTIFIED-CONTINUATION-OCS-PROPOSAL"),
        input_func=_input_sequence([OCS_PROPOSAL_ONLY_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert turn["ocs_proposal_only_preserved"] is True
    assert turn["ocs_to_ppp_continuation_status"] is None
    assert turn["ppp_route_status"] is None
    assert turn["ppp_invoked"] is False
    assert turn["worker_invoked"] is False
    assert proposal_adapter.calls == 0
