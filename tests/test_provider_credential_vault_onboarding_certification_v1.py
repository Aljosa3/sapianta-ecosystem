from pathlib import Path

from aigol.runtime.provider_credential_vault_onboarding_certification_v1 import (
    MILESTONE_ID,
    main,
    run_provider_credential_vault_onboarding_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_provider_credential_vault_onboarding_certification_detects_fallback_dependency(tmp_path):
    result = run_provider_credential_vault_onboarding_certification(
        replay_base=tmp_path / "vault_onboarding_certification",
        local_vault_base=tmp_path / "local-vault",
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_CREDENTIAL_VAULT_FALLBACK_DEPENDENT"

    root = Path(result["cert_root"])
    report = load_json(root / "certification_report" / "000_provider_credential_vault_onboarding_certification_report.json")
    assert "ACLI provider credential onboarding command is not implemented." in report["gap_analysis"]
    assert "First live cognition certification still requires environment credential preflight." in report["gap_analysis"]
    assert report["questions"]["first_live_certification_vault_only"] is False
    assert report["questions"]["vault_functions_without_provider_env"] is True


def test_provider_credential_vault_onboarding_certification_replay_is_secret_free(tmp_path):
    result = run_provider_credential_vault_onboarding_certification(
        replay_base=tmp_path / "vault_onboarding_certification",
        local_vault_base=tmp_path / "local-vault",
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-onboarding-cert-secret" not in serialized
    assert "sk-should-not-record" not in serialized
    assert "Bearer " not in serialized


def test_provider_credential_vault_onboarding_certification_cli_prints_markers(tmp_path, monkeypatch, capsys):
    import aigol.runtime.provider_credential_vault_onboarding_certification_v1 as certification

    monkeypatch.setattr(certification, "DEFAULT_REPLAY_BASE", tmp_path / "certification")
    monkeypatch.setattr(certification, "DEFAULT_LOCAL_VAULT_BASE", tmp_path / "local-vault")

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "CERT_ROOT=" in output
    assert "coverage_report_path=" in output
    assert "evidence_package_path=" in output
    assert "replay_package_path=" in output
    assert "certification_report_path=" in output
    assert "FINAL_VERDICT=PROVIDER_CREDENTIAL_VAULT_FALLBACK_DEPENDENT" in output
