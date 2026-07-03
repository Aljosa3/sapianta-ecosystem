"""Regression tests for G14-05 persistent AiGOL Next development workspace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata


CREATED_AT = "2026-07-03T00:00:00Z"
SESSION_ID = "G14-05-PERSISTENT-DEVELOPMENT-WORKSPACE"


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
            "id": "resp-g14-05-persistent-workspace-worker-001",
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


def test_aigol_next_restores_pending_development_context_and_executes(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    first_result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "Add automation.",
            "/send",
            "exit",
        ],
    )
    first_output = capsys.readouterr().out

    assert first_result == 0
    assert "Clarification required before governed execution." in first_output
    assert "pending_clarification: True" in first_output
    assert "session_resumed: False" in first_output

    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)

    second_result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "Add GitHub Actions support for governed validation only.",
            "/send",
            "/approve",
            "exit",
        ],
    )
    second_output = capsys.readouterr().out
    state_root = tmp_path / "runtime" / SESSION_ID / "workspace_state"

    assert second_result == 0
    assert "Persistent development workspace restored." in second_output
    assert "active_development_objective: Add automation." in second_output
    assert "pending_clarification: True" in second_output
    assert "Governed implementation summary" in second_output
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in second_output
    assert "session_resumed: True" in second_output
    assert "restored_implementation_history_count: 0" in second_output
    assert "runtime_bound_count: 1" in second_output
    assert proposal_adapter.calls == 1
    assert (state_root / "001_acli_next_workspace_state_recorded.json").exists()
    assert (state_root / "002_acli_next_workspace_state_recorded.json").exists()
