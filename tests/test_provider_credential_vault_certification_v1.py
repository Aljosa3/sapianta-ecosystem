from pathlib import Path

from aigol.runtime.provider_credential_vault_certification_v1 import (
    MILESTONE_ID,
    main,
    run_provider_credential_vault_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_provider_credential_vault_certification_succeeds(tmp_path):
    result = run_provider_credential_vault_certification(
        replay_base=tmp_path / "provider_credential_vault_certification",
        local_vault_base=tmp_path / "local-vault-storage",
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_CREDENTIAL_VAULT_IMPLEMENTED"
    assert all(result["success_criteria"].values())

    root = Path(result["cert_root"])
    assert (root / "evidence_package" / "000_provider_credential_vault_evidence_package.json").exists()
    assert (root / "replay_package" / "000_provider_credential_vault_replay_package.json").exists()
    assert (root / "certification_report" / "000_provider_credential_vault_certification_report.json").exists()


def test_provider_credential_vault_certification_replay_is_secret_free(tmp_path):
    result = run_provider_credential_vault_certification(
        replay_base=tmp_path / "provider_credential_vault_certification",
        local_vault_base=tmp_path / "local-vault-storage",
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-cert-vault-initial-secret" not in serialized
    assert "sk-cert-vault-rotated-secret" not in serialized
    assert "sk-cert-env-fallback-secret" not in serialized
    assert "Bearer " not in serialized


def test_provider_credential_vault_certification_cli_prints_markers(tmp_path, monkeypatch, capsys):
    import aigol.runtime.provider_credential_vault_certification_v1 as certification

    monkeypatch.setattr(certification, "DEFAULT_REPLAY_BASE", tmp_path / "certification")
    monkeypatch.setattr(certification, "DEFAULT_LOCAL_VAULT_BASE", tmp_path / "local-vault-storage")

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "CERT_ROOT=" in output
    assert "evidence_package_path=" in output
    assert "replay_package_path=" in output
    assert "certification_report_path=" in output
    assert "FINAL_VERDICT=PROVIDER_CREDENTIAL_VAULT_IMPLEMENTED" in output
