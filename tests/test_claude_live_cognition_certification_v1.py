"""Tests for AIGOL_CLAUDE_LIVE_COGNITION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.claude_live_cognition_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    FINAL_VERDICT_GAPS,
    MILESTONE_ID,
    reconstruct_claude_live_cognition_certification_v1,
    run_claude_live_cognition_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


SECRET = "claude-certification-secret-value"


def _fake_claude_transport(payload: dict, metadata: dict) -> dict:
    assert payload["provider_id"] == "claude"
    assert metadata["provider_id"] == "claude"
    assert metadata["_credential_secret"] == SECRET
    return {
        "provider_id": "claude",
        "model": "claude-certification-test",
        "text": "Claude proposal-only cognition response captured.",
        "usage": {"input_tokens": 10, "output_tokens": 8, "total_tokens": 18},
    }


_fake_claude_transport.aigol_governed_live_claude_executor_v1 = True


def test_claude_live_cognition_reports_gap_without_executor(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET)
    monkeypatch.delenv("AIGOL_ANTHROPIC_API_KEY", raising=False)

    result = run_claude_live_cognition_certification_v1(
        runtime_root=tmp_path / "claude_live",
        vault_path=tmp_path / "vault" / "provider-credentials.json",
    )
    replay = reconstruct_claude_live_cognition_certification_v1(result["cert_root"])

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_GAPS
    assert replay["replay_reconstructed"] is True
    coverage = result["coverage"]
    assert coverage["provider_registered"] is True
    assert coverage["credential_reference"] == "vault://provider/claude"
    assert coverage["credential_onboarded"] is True
    assert coverage["credential_resolution_successful"] is True
    assert coverage["live_executor_exists"] is False
    assert coverage["provider_response_received"] is False


def test_claude_live_cognition_certifies_with_governed_executor(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET)
    monkeypatch.delenv("AIGOL_ANTHROPIC_API_KEY", raising=False)

    result = run_claude_live_cognition_certification_v1(
        runtime_root=tmp_path / "claude_live",
        vault_path=tmp_path / "vault" / "provider-credentials.json",
        transport=_fake_claude_transport,
    )

    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    coverage = result["coverage"]
    assert coverage["provider_selected"] == "claude"
    assert coverage["provider_invoked"] is True
    assert coverage["provider_response_received"] is True
    assert coverage["credential_source"] == "vault://provider/claude"
    assert coverage["participation_metrics_recorded"] is True
    assert coverage["usage_metrics_recorded"] is True
    assert coverage["cost_hooks_recorded"] is True


def test_claude_live_cognition_evidence_is_secret_free(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", SECRET)

    result = run_claude_live_cognition_certification_v1(
        runtime_root=tmp_path / "claude_live",
        vault_path=tmp_path / "vault" / "provider-credentials.json",
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert SECRET not in serialized
    assert "Bearer " not in serialized
    assert "_credential_secret" not in serialized
