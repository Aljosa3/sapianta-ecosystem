"""Tests for AIGOL_MULTI_PROVIDER_OPERATIONAL_READINESS_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.multi_provider_operational_readiness_certification_v1 import (
    MILESTONE_ID,
    reconstruct_multi_provider_operational_readiness_replay,
    run_multi_provider_operational_readiness_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


def _report(path: Path, verdict: str) -> Path:
    payload = {"artifact_type": "TEST_REPORT", "final_verdict": verdict}
    payload["artifact_hash"] = replay_hash(payload)
    write_json_immutable(path, payload)
    return path


def test_multi_provider_operational_readiness_certifies_openai_and_claude(tmp_path):
    result = run_multi_provider_operational_readiness_certification_v1(
        runtime_root=tmp_path / "multi_provider_operational",
        openai_report_path=_report(tmp_path / "openai.json", "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"),
        claude_report_path=_report(tmp_path / "claude.json", "CLAUDE_LIVE_COGNITION_CERTIFIED"),
        role_identity_report_path=_report(tmp_path / "role.json", "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"),
        product1_report_path=_report(tmp_path / "product1.json", "AIGOL_PRODUCT1_END_TO_END_CERTIFIED"),
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "MULTI_PROVIDER_OPERATIONALLY_READY"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_multi_provider_operational_readiness_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_multi_provider_operational_readiness_evidence_package.json").exists()
    assert (root / "replay_package" / "000_multi_provider_operational_readiness_replay_package.json").exists()
    assert (root / "operational_readiness_report" / "000_multi_provider_operational_readiness_report.json").exists()
    assert (root / "certification_report" / "000_multi_provider_operational_readiness_certification_report.json").exists()


def test_multi_provider_operational_readiness_records_failover_and_isolation(tmp_path):
    result = run_multi_provider_operational_readiness_certification_v1(
        runtime_root=tmp_path / "multi_provider_operational",
        openai_report_path=_report(tmp_path / "openai.json", "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"),
        claude_report_path=_report(tmp_path / "claude.json", "CLAUDE_LIVE_COGNITION_CERTIFIED"),
        role_identity_report_path=_report(tmp_path / "role.json", "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"),
        product1_report_path=_report(tmp_path / "product1.json", "AIGOL_PRODUCT1_END_TO_END_CERTIFIED"),
    )
    evidence = load_json(
        Path(result["cert_root"])
        / "evidence_package"
        / "000_multi_provider_operational_readiness_evidence_package.json"
    )

    assert set(evidence["dual_success_probe"]["runtime_result"]["successful_providers"]) == {"openai", "claude"}
    assert evidence["failover_probe"]["runtime_result"]["successful_providers"] == ["claude"]
    assert evidence["failover_probe"]["runtime_result"]["failed_providers"] == ["openai"]
    assert evidence["failover_probe"]["runtime_result"]["failure_isolated"] is True


def test_multi_provider_operational_readiness_records_metrics_and_participation(tmp_path):
    result = run_multi_provider_operational_readiness_certification_v1(
        runtime_root=tmp_path / "multi_provider_operational",
        openai_report_path=_report(tmp_path / "openai.json", "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"),
        claude_report_path=_report(tmp_path / "claude.json", "CLAUDE_LIVE_COGNITION_CERTIFIED"),
        role_identity_report_path=_report(tmp_path / "role.json", "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"),
        product1_report_path=_report(tmp_path / "product1.json", "AIGOL_PRODUCT1_END_TO_END_CERTIFIED"),
    )
    root = Path(result["cert_root"])

    usage = list((root / "provider_governance_replay").rglob("000_provider_usage_metric.json"))
    participation = list((root / "provider_governance_replay").rglob("000_cognition_participation.json"))
    assert len(usage) == 2
    assert len(participation) == 2
    assert all(load_json(path)["provider_authority"] is False for path in participation)


def test_multi_provider_operational_readiness_replay_reconstructs(tmp_path):
    result = run_multi_provider_operational_readiness_certification_v1(
        runtime_root=tmp_path / "multi_provider_operational",
        openai_report_path=_report(tmp_path / "openai.json", "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"),
        claude_report_path=_report(tmp_path / "claude.json", "CLAUDE_LIVE_COGNITION_CERTIFIED"),
        role_identity_report_path=_report(tmp_path / "role.json", "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"),
        product1_report_path=_report(tmp_path / "product1.json", "AIGOL_PRODUCT1_END_TO_END_CERTIFIED"),
    )
    replay = reconstruct_multi_provider_operational_readiness_replay(result["cert_root"])

    assert replay["replay_reconstructed"] is True
    assert replay["dual_successful_provider_count"] == 2
    assert replay["failover_successful_provider_count"] == 1


def test_multi_provider_operational_readiness_evidence_is_secret_free(tmp_path):
    result = run_multi_provider_operational_readiness_certification_v1(
        runtime_root=tmp_path / "multi_provider_operational",
        openai_report_path=_report(tmp_path / "openai.json", "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED"),
        claude_report_path=_report(tmp_path / "claude.json", "CLAUDE_LIVE_COGNITION_CERTIFIED"),
        role_identity_report_path=_report(tmp_path / "role.json", "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"),
        product1_report_path=_report(tmp_path / "product1.json", "AIGOL_PRODUCT1_END_TO_END_CERTIFIED"),
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
