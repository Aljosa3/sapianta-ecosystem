"""Regression tests for G14-19 canonical development intent resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.cli import aigol_cli
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import openai_provider_metadata
from aigol.runtime.platform_core_project_services import resolve_development_intent


CREATED_AT = "2026-07-04T00:00:00Z"


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


def _install_fake_provider_and_worker(monkeypatch) -> FakeProviderAdapter:
    adapter = FakeProviderAdapter(
        {
            "proposal_summary": "Implement the governed native development request.",
            "proposed_outputs": ["docs/governance/G14_19_RUNTIME_EVIDENCE.md"],
            "constraints_acknowledged": ["GOVERNANCE_PRESERVED", "REPLAY_PRESERVED"],
            "assumptions": ["The request remains inside native development scope."],
            "known_gaps": [],
        }
    )

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-g14-19-worker-001",
            "output_text": "Bounded governed development result.",
        }

    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: adapter)
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)
    return adapter


def test_canonical_development_intent_resolution_matrix() -> None:
    scenarios = {
        "natural implementation": "Implement a native validation helper for replay evidence summaries.",
        "natural improvement": "Improve runtime validation reporting.",
        "natural extension": "Extend runtime binding coverage for native development.",
        "ambiguous clarification": "Improve the system.",
        "previously failing": "Implement governed policy.",
    }

    results = {
        name: resolve_development_intent(message=prompt)
        for name, prompt in scenarios.items()
    }

    for name in ("natural implementation", "natural improvement", "natural extension", "previously failing"):
        result = results[name]
        assert result["development_intent_resolution_authority"] == "PLATFORM_CORE"
        assert result["summary_admissible"] is True
        assert result["runtime_binding_admissible"] is True
        assert result["same_decision_for_send_and_approve"] is True
        assert result["clarification_required"] is False

    ambiguous = results["ambiguous clarification"]
    assert ambiguous["summary_admissible"] is False
    assert ambiguous["runtime_binding_admissible"] is False
    assert ambiguous["clarification_required"] is True


def test_previously_failing_prompt_uses_same_resolution_for_send_and_approve(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    adapter = _install_fake_provider_and_worker(monkeypatch)
    inputs = iter(["Implement governed policy.", "/send", "/approve", "exit"])
    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    result = aigol_cli.main(
        [
            "next",
            "--session-id",
            "G14-19-INTENT-UNIFICATION",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )

    output = capsys.readouterr().out

    assert result == 0
    assert "Governed implementation summary" in output
    assert "Human confirmation recorded. Entering certified runtime." in output
    assert "runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND" in output
    assert "runtime_entered: True" in output
    assert "governance_authorization_reached: True" in output
    assert "provider_invocation_reached: True" in output
    assert "worker_execution_reached: True" in output
    assert "replay_certification_reached: True" in output
    assert "runtime_bound_count: 1" in output
    assert adapter.calls == 1
