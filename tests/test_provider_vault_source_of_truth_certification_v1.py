"""Tests for AIGOL_PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.provider_vault_source_of_truth_certification_v1 import (
    MILESTONE_ID,
    run_provider_vault_source_of_truth_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


SECRET = "sk-provider-vault-source-of-truth-test-7Klm"


def _transport():
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["provider_id"] == "openai"
        assert metadata["_credential_secret"] == SECRET
        assert metadata["credential_secret_replayed"] is False
        return {
            "id": "provider-vault-source-of-truth-response",
            "status_code": 200,
            "output_text": "Findings: provider vault source of truth certified. Confidence: HIGH",
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
        }

    call.aigol_governed_live_openai_executor_v1 = True
    return call


def test_provider_vault_source_of_truth_certifies_vault_only_execution(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", SECRET)
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)

    result = run_provider_vault_source_of_truth_certification(
        replay_base=tmp_path / "source_of_truth",
        vault_path=tmp_path / "operator" / "provider-credentials.json",
        transport=_transport(),
        require_real_transport=False,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_VAULT_SOURCE_OF_TRUTH_CERTIFIED"
    coverage = result["coverage"]
    assert coverage["vault_file_exists"] is True
    assert coverage["vault_resolution_successful"] is True
    assert coverage["provider_selected"] == "openai"
    assert coverage["provider_invoked"] is True
    assert coverage["provider_response_received"] is True
    assert coverage["credential_source"] == "vault://provider/openai"
    assert coverage["secret_free_evidence"] is True
    assert coverage["approval_boundaries_preserved"] is True

    root = Path(result["cert_root"])
    assert (root / "evidence_package" / "000_provider_vault_source_of_truth_evidence_package.json").exists()
    assert (root / "replay_package" / "000_provider_vault_source_of_truth_replay_package.json").exists()
    assert (root / "certification_report" / "000_provider_vault_source_of_truth_certification_report.json").exists()
    serialized = ""
    for path in sorted(root.rglob("*.json")):
        serialized += canonical_serialize(load_json(path))
    assert SECRET not in serialized
    assert "Bearer " not in serialized


def test_provider_vault_source_of_truth_reports_gap_without_operator_credential(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AIGOL_PROVIDER_CREDENTIAL_INPUT", raising=False)

    result = run_provider_vault_source_of_truth_certification(
        replay_base=tmp_path / "source_of_truth",
        vault_path=tmp_path / "operator" / "provider-credentials.json",
        transport=_transport(),
        require_real_transport=False,
    )

    assert result["final_verdict"] == "PROVIDER_VAULT_SOURCE_OF_TRUTH_GAPS_FOUND"
    assert "requires an OpenAI credential" in str(result["coverage"]["failure_reason"])
