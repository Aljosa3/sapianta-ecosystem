"""Regression tests for G14-06 AiGOL Next project guidance assistant."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata


CREATED_AT = "2026-07-03T00:00:00Z"
SESSION_ID = "G14-06-PROJECT-GUIDANCE-ASSISTANT"


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


def _install_fake_proposal_adapter(monkeypatch) -> FakeProviderAdapter:
    adapter = FakeProviderAdapter(
        {
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
    )
    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: adapter)
    return adapter


def _install_fake_external_worker_openai_client(monkeypatch) -> None:
    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-g14-06-guidance-assistant-worker-001",
            "output_text": "Inspect runtime metadata and return bounded findings.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def _run_aigol_next(monkeypatch, tmp_path, inputs: list[str]) -> int:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    iterator = iter(inputs)
    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
    return aigol_cli.main(
        [
            "next",
            "--session-id",
            SESSION_ID,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )


def test_project_guidance_uses_workspace_state_and_continues_after_approval(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    first_result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1.",
            (
                "Goal: Extend the certified provider-neutral external worker architecture "
                "with Claude support while reusing existing governance, replay, validation, "
                "mutation, and worker lifecycle infrastructure."
            ),
            "/send",
            "exit",
        ],
    )
    first_output = capsys.readouterr().out

    assert first_result == 0
    assert "Governed implementation summary" in first_output
    assert "pending_execution_summary: True" in first_output

    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    second_result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "/approve",
            "exit",
        ],
    )
    second_output = capsys.readouterr().out
    state_path = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "workspace_state"
        / "001_acli_next_workspace_state_recorded.json"
    )
    workspace_state = json.loads(state_path.read_text(encoding="utf-8"))
    guidance = workspace_state["project_guidance"]

    assert second_result == 0
    assert "Persistent development workspace restored." in second_output
    assert "Project guidance" in second_output
    assert "guidance_source: deterministic_workspace_state" in second_output
    assert "active_generation: Generation 14" in second_output
    assert "active_milestone: CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1" in second_output
    assert "pending_approvals: IMPLEMENTATION_SUMMARY_APPROVAL" in second_output
    assert "recommended_next_governed_action: Review the pending implementation summary, then type /approve or /cancel." in second_output
    assert "acli_next_executes_recommendation: False" in second_output
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in second_output
    assert guidance["guidance_source"] == "deterministic_workspace_state"
    assert guidance["active_generation"] == "Generation 14"
    assert guidance["active_milestone"] == "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"
    assert guidance["pending_approvals"] == ["IMPLEMENTATION_SUMMARY_APPROVAL"]
    assert guidance["acli_next_executes_recommendation"] is False
    assert proposal_adapter.calls == 1
