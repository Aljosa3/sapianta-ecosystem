"""Tests for AIGOL_FIRST_LIVE_COGNITION_PROVIDER_ENTRYPOINT_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.first_live_cognition_provider_certification import (
    MILESTONE_ID,
    main,
    run_first_live_cognition_provider_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def _transport(response_text: str = "Findings: live cognition certification captured. Confidence: HIGH"):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["provider_id"] == "openai"
        assert metadata["credential_secret_replayed"] is False
        return {
            "id": "first-live-cognition-provider-entrypoint-response",
            "status_code": 200,
            "output_text": response_text,
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
        }

    call.aigol_governed_live_openai_executor_v1 = True
    return call


def test_first_live_cognition_provider_entrypoint_certifies_success_path(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-live-openai-secret")

    result = run_first_live_cognition_provider_certification(
        replay_base=tmp_path / "first_live_cognition_provider",
        transport=_transport(),
    )

    observed = result["observed"]
    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"
    assert observed["provider_selected"] == "openai"
    assert observed["provider_invoked"] is True
    assert observed["provider_response_received"] is True
    assert observed["human_confirmation_recorded"] is True
    assert observed["replay_reconstructed"] is True
    assert observed["worker_invoked"] is False

    root = Path(result["cert_root"])
    assert root.name == "CERT-000001"
    assert (root / "evidence_package" / "000_first_live_cognition_provider_evidence_package.json").exists()
    assert (root / "replay_package" / "000_first_live_cognition_provider_replay_package.json").exists()
    assert (root / "certification_report" / "000_first_live_cognition_provider_certification_report.json").exists()
    assert (root / "human_confirmation" / "000_first_live_cognition_provider_human_confirmation.json").exists()
    assert (root / "provider_governance" / "credential_lifecycle" / "000_provider_governance_event.json").exists()
    assert (root / "provider_governance" / "usage" / "000_provider_usage_metric.json").exists()
    assert (
        root / "provider_governance" / "cognition_participation" / "000_cognition_participation.json"
    ).exists()

    report = load_json(root / "certification_report" / "000_first_live_cognition_provider_certification_report.json")
    governance_replay = report["provider_governance_replay"]
    assert governance_replay["provider_governance_event_count"] == 1
    assert governance_replay["provider_usage_metric_count"] == 1
    assert governance_replay["cognition_participation_count"] == 1


def test_first_live_cognition_provider_entrypoint_aborts_before_certification_without_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = run_first_live_cognition_provider_certification(
        replay_base=tmp_path / "first_live_cognition_provider",
        transport=_transport(),
    )

    assert result["aborted_before_certification"] is True
    assert result["aborted_reason"] == "AIGOL_OPENAI_API_KEY_MISSING"
    assert result["final_verdict"] == "COGNITION_PROVIDER_CERTIFICATION_FAILED"
    assert not (tmp_path / "first_live_cognition_provider").exists()


def test_first_live_cognition_provider_entrypoint_cli_prints_expected_markers(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-live-openai-secret")
    monkeypatch.chdir(tmp_path)

    import aigol.runtime.first_live_cognition_provider_certification as entrypoint

    monkeypatch.setattr(entrypoint, "DEFAULT_REPLAY_BASE", tmp_path / "first_live_cognition_provider")
    monkeypatch.setattr(entrypoint, "create_governed_live_openai_executor", lambda: _transport())

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AIGOL_OPENAI_API_KEY_PRESENT=True" in output
    assert "OPENAI_API_KEY_PRESENT=True" in output
    assert "provider_selected=openai" in output
    assert "provider_invoked=True" in output
    assert "provider_response_received=True" in output
    assert "human_confirmation_recorded=True" in output
    assert "replay_reconstructed=True" in output
    assert "FINAL_VERDICT=FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED" in output


def test_first_live_cognition_provider_entrypoint_does_not_replay_secret_material(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test-live-openai-secret")

    result = run_first_live_cognition_provider_certification(
        replay_base=tmp_path / "first_live_cognition_provider",
        transport=_transport(),
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "test-live-openai-secret" not in serialized
    assert "Bearer " not in serialized
