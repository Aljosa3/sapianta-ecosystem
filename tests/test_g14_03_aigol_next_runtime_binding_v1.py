"""Regression tests for G14-03 ACLI Next runtime binding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata


CREATED_AT = "2026-07-03T00:00:00Z"
NATIVE_PROMPT = "Add GitHub Actions support."


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


def _install_fake_external_worker_openai_client(monkeypatch) -> None:
    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-g14-03-runtime-binding-worker-001",
            "output_text": "Inspect runtime metadata and return bounded findings.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def test_acli_next_development_prompt_enters_certified_runtime(tmp_path, monkeypatch) -> None:
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "--session-id",
            "G14-03-AIGOL-NEXT-RUNTIME-BINDING",
            "--prompt",
            NATIVE_PROMPT,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol next"
    assert result["runtime_binding_status"] == "AIGOL_NEXT_RUNTIME_BOUND"
    assert result["runtime_entered"] is True
    assert result["auto_continue_enabled"] is True
    assert result["execution_summary_presented"] is True
    assert result["human_confirmation_presented"] is True
    assert result["governance_authorization_reached"] is True
    assert result["provider_invocation_reached"] is True
    assert result["worker_execution_reached"] is True
    assert result["replay_certification_reached"] is True
    assert result["manual_chatgpt_codex_transfer_required"] is False
    assert result["acli_next_authorizes"] is False
    assert result["acli_next_executes"] is False
    assert result["acli_next_records_replay_evidence"] is False
    assert result["acli_next_runtime_orchestrates"] is False
    assert result["acli_next_runtime_authorizes"] is False
    assert result["acli_next_runtime_executes"] is False
    assert result["platform_core_runtime_delegated"] is True
    assert proposal_adapter.calls == 1
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in rendered
    assert "manual_chatgpt_codex_transfer_required: False" in rendered


def test_acli_next_status_prompt_remains_presentation_only(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "--session-id",
            "G14-03-AIGOL-NEXT-PRESENTATION-ONLY",
            "--prompt",
            "Show governed development status.",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )

    result = run_command(args)

    assert result["runtime_binding_status"] == "AIGOL_NEXT_RUNTIME_BINDING_NOT_REQUIRED"
    assert result["runtime_entered"] is False
    assert result["acli_next_executes"] is False
