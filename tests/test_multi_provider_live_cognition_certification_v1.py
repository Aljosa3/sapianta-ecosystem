"""Tests for AIGOL_MULTI_PROVIDER_LIVE_COGNITION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.multi_provider_live_cognition_certification_v1 import (
    FINAL_VERDICT_GAPS,
    MILESTONE_ID,
    reconstruct_multi_provider_live_cognition_certification_v1,
    run_multi_provider_live_cognition_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, write_json_immutable


def _component_reports(root: Path) -> dict[str, Path]:
    openai = root / "openai_live_report.json"
    product1 = root / "product1_report.json"
    write_json_immutable(
        openai,
        {
            "artifact_type": "TEST_FIRST_LIVE_COGNITION_PROVIDER_REPORT",
            "final_verdict": "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
            "observed": {
                "provider_selected": "openai",
                "provider_invoked": True,
                "provider_response_received": True,
                "replay_reconstructed": True,
                "worker_invoked": False,
            },
        },
    )
    write_json_immutable(
        product1,
        {
            "artifact_type": "TEST_PRODUCT1_REPORT",
            "final_verdict": "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
        },
    )
    return {
        "live_openai_report_path": openai,
        "product1_report_path": product1,
    }


def test_multi_provider_live_cognition_certification_records_current_gaps(tmp_path):
    reports = _component_reports(tmp_path / "reports")
    result = run_multi_provider_live_cognition_certification_v1(
        runtime_root=tmp_path / "multi_provider_live",
        **reports,
    )
    replay = reconstruct_multi_provider_live_cognition_certification_v1(result["cert_root"])

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_GAPS
    assert replay["replay_reconstructed"] is True
    assert replay["final_verdict"] == FINAL_VERDICT_GAPS
    assert result["assertions"]["openai_live_cognition_certified"] is True
    assert result["assertions"]["non_openai_live_provider_certified"] is False


def test_multi_provider_live_cognition_probe_isolates_non_openai_failures(tmp_path):
    reports = _component_reports(tmp_path / "reports")
    result = run_multi_provider_live_cognition_certification_v1(
        runtime_root=tmp_path / "multi_provider_live",
        **reports,
    )
    evidence = load_json(Path(result["evidence_package_path"]))
    probe = evidence["multi_provider_cognition_probe"]["runtime_result"]

    assert probe["provider_count"] == 4
    assert probe["successful_provider_count"] == 1
    assert probe["failed_provider_count"] == 3
    assert probe["successful_providers"] == ["openai"]
    assert set(probe["failed_providers"]) == {"claude", "gemini", "mistral"}


def test_multi_provider_live_cognition_evidence_is_secret_free(tmp_path):
    reports = _component_reports(tmp_path / "reports")
    result = run_multi_provider_live_cognition_certification_v1(
        runtime_root=tmp_path / "multi_provider_live",
        **reports,
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "secret-value" not in serialized.lower()
    assert "_credential_secret" not in serialized
