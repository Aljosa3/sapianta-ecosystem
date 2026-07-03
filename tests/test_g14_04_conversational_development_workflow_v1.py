"""Regression tests for G14-04 conversational development workflow."""

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
            "id": "resp-g14-04-conversational-workflow-worker-001",
            "output_text": "Inspect runtime metadata and return bounded findings.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def test_aigol_next_guides_imprecise_request_to_runtime_execution(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    inputs = iter(
        [
            "Add automation.",
            "/send",
            "Add GitHub Actions support for governed validation only.",
            "/send",
            "/approve",
            "exit",
        ]
    )

    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    result = aigol_cli.main(
        [
            "next",
            "--session-id",
            "G14-04-CONVERSATIONAL-DEVELOPMENT-WORKFLOW",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )

    output = capsys.readouterr().out
    runtime_root = tmp_path / "runtime" / "G14-04-CONVERSATIONAL-DEVELOPMENT-WORKFLOW"

    assert result == 0
    assert "Clarification required before governed execution." in output
    assert "Governed implementation summary" in output
    assert "Human confirmation recorded. Entering certified runtime." in output
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in output
    assert "guided_development_workflow_enabled: True" in output
    assert "clarification_question_count: 1" in output
    assert "clarification_response_count: 1" in output
    assert "execution_summary_count: 1" in output
    assert "approval_count: 1" in output
    assert "runtime_bound_count: 1" in output
    assert proposal_adapter.calls == 1
    assert (runtime_root / "TURN-000001").exists()
