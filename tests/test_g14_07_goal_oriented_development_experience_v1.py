"""Regression tests for G14-07 goal-oriented AiGOL Next development experience."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata


CREATED_AT = "2026-07-03T00:00:00Z"


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
            "id": "resp-g14-07-goal-oriented-worker-001",
            "output_text": "Inspect runtime metadata and return bounded findings.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def _run_aigol_next(monkeypatch, tmp_path, *, session_id: str, inputs: list[str]) -> int:
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
            session_id,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )


def test_high_level_github_actions_goal_maps_and_executes_runtime(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)

    result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        session_id="G14-07-GITHUB-ACTIONS-GOAL",
        inputs=[
            "I want AiGOL Next to support GitHub Actions.",
            "/send",
            "/approve",
            "exit",
        ],
    )
    output = capsys.readouterr().out

    assert result == 0
    assert "Governed implementation summary" in output
    assert "goal_mapping:" in output
    assert "goal_type: EXTENDS_PROJECT" in output
    assert "goal_target: github_actions" in output
    assert "governed_request: Add GitHub Actions support." in output
    assert "mapping_source: deterministic_workspace_state" in output
    assert "Human confirmation recorded. Entering certified runtime." in output
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in output
    assert "goal_mapping_count: 1" in output
    assert proposal_adapter.calls == 1


def test_high_level_operational_goals_map_without_manual_workflow_prompts(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        session_id="G14-07-OPERATIONAL-GOALS",
        inputs=[
            "Let's improve deployment.",
            "/send",
            "/cancel",
            "Continue the mobile interface.",
            "/send",
            "exit",
        ],
    )
    output = capsys.readouterr().out

    assert result == 0
    assert "goal_target: deployment" in output
    assert "governed_request: Add governed deployment workflow support." in output
    assert "goal_target: mobile_interface" in output
    assert "governed_request: Continue the governed mobile interface." in output
    assert "goal_mapping_count: 2" in output
    assert "runtime_bound_count: 0" in output
