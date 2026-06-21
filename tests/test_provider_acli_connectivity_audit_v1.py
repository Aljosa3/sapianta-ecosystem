from pathlib import Path

from aigol.runtime.provider_acli_connectivity_audit_v1 import (
    MILESTONE_ID,
    main,
    run_provider_acli_connectivity_audit,
)
from aigol.runtime.transport.serialization import load_json


def test_provider_acli_connectivity_audit_finds_expected_gaps(tmp_path):
    result = run_provider_acli_connectivity_audit(replay_base=tmp_path / "provider_acli_connectivity")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_ACLI_CONNECTIVITY_GAPS_FOUND"
    assert "provider credential add openai" in result["missing_acli_registrations"]
    assert "provider credential verify openai" in result["missing_acli_registrations"]
    assert "show provider credentials" in result["missing_acli_registrations"]

    report = load_json(Path(result["audit_report_path"]))
    rows = {row["runtime_capability"]: row for row in report["reachability_matrix"]}
    assert rows["provider status"]["acli_reachable"] is True
    assert rows["provider credentials"]["acli_reachable"] is True
    assert rows["provider credential add"]["acli_reachable"] is False
    assert rows["provider credential verify"]["acli_reachable"] is False
    assert report["first_live_migration"]["vault_migration_ready"] is False


def test_provider_acli_connectivity_audit_replay_package_created(tmp_path):
    result = run_provider_acli_connectivity_audit(replay_base=tmp_path / "provider_acli_connectivity")

    replay = load_json(Path(result["replay_package_path"]))

    assert replay["artifact_type"] == "PROVIDER_ACLI_CONNECTIVITY_REPLAY_PACKAGE_V1"
    assert replay["replay_secret_free"] is True
    assert replay["final_verdict"] == "PROVIDER_ACLI_CONNECTIVITY_GAPS_FOUND"


def test_provider_acli_connectivity_audit_cli_prints_gap_verdict(tmp_path, monkeypatch, capsys):
    import aigol.runtime.provider_acli_connectivity_audit_v1 as audit

    monkeypatch.setattr(audit, "DEFAULT_REPLAY_BASE", tmp_path / "provider_acli_connectivity")

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "CERT_ROOT=" in output
    assert "missing_acli_registrations=" in output
    assert "FINAL_VERDICT=PROVIDER_ACLI_CONNECTIVITY_GAPS_FOUND" in output
