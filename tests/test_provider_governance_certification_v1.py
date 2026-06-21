from pathlib import Path

from aigol.runtime.provider_governance_certification_v1 import (
    MILESTONE_ID,
    main,
    run_provider_governance_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_provider_governance_certification_certifies_campaign(tmp_path):
    result = run_provider_governance_certification(replay_base=tmp_path / "provider_governance")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_GOVERNANCE_CERTIFIED"
    assert all(result["success_criteria"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_provider_governance_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_provider_governance_evidence_package.json").exists()
    assert (root / "replay_package" / "000_provider_governance_replay_package.json").exists()
    assert (root / "certification_report" / "000_provider_governance_certification_report.json").exists()

    report = load_json(root / "certification_report" / "000_provider_governance_certification_report.json")
    assert report["questions"]["can_provider_lifecycle_actions_be_governed_safely"] is True
    assert report["questions"]["can_replay_reconstruct_all_provider_governance_actions"] is True
    assert report["questions"]["are_approval_boundaries_preserved"] is True


def test_provider_governance_certification_does_not_replay_secret_material(tmp_path):
    result = run_provider_governance_certification(replay_base=tmp_path / "provider_governance")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "operator-safe-present-marker" not in serialized
    assert "Bearer " not in serialized
    assert "sk-" not in serialized


def test_provider_governance_certification_cli_prints_markers(tmp_path, monkeypatch, capsys):
    import aigol.runtime.provider_governance_certification_v1 as certification

    monkeypatch.setattr(certification, "DEFAULT_REPLAY_BASE", tmp_path / "provider_governance")

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "CERT_ROOT=" in output
    assert "coverage_report_path=" in output
    assert "evidence_package_path=" in output
    assert "replay_package_path=" in output
    assert "certification_report_path=" in output
    assert "FINAL_VERDICT=PROVIDER_GOVERNANCE_CERTIFIED" in output
