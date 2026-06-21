"""Tests for AIGOL_HIRR_REAL_WORLD_DOGFOOD_CERTIFICATION_V2."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.provider.providers.openai_provider import OpenAIProviderAdapter
from aigol.runtime.hirr_real_world_dogfood_certification_v2 import (
    execute_hirr_real_world_dogfood_certification_v2,
    reconstruct_hirr_real_world_dogfood_certification_v2,
)
from aigol.runtime.transport.serialization import canonical_serialize


def _fake_openai_adapter():
    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-hirr-v2-test",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["The safest next step is to clarify scope before action."],
                                    "assumptions": ["Provider output remains non-authoritative."],
                                    "alternatives": ["Ask for more context", "Prepare a proposal only"],
                                    "risks": ["Acting without context can produce the wrong result."],
                                    "uncertainties": ["The target object is not fully specified."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
        }

    return OpenAIProviderAdapter(api_key="sk-hirr-v2-test-secret", client=fake_client)


def test_hirr_real_world_dogfood_v2_runs_subset_and_reconstructs(tmp_path, monkeypatch):
    from aigol.cli import aigol_cli

    monkeypatch.setattr(aigol_cli, "_conversation_openai_provider_adapter", _fake_openai_adapter)

    result = execute_hirr_real_world_dogfood_certification_v2(
        runtime_root=tmp_path / "hirr_v2",
        workspace=tmp_path,
        scenario_ids=["HRD2-001", "HRD2-005"],
    )
    replay = reconstruct_hirr_real_world_dogfood_certification_v2(result["cert_root"])

    assert Path(result["coverage_report_path"]).exists()
    assert Path(result["evidence_package_path"]).exists()
    assert Path(result["replay_package_path"]).exists()
    assert Path(result["certification_report_path"]).exists()
    assert replay["replay_reconstructed"] is True
    assert replay["certification_report"]["case_count"] == 2
    assert any(
        item["case_id"] == "HRD2-005" and item["expected_behavior"] == "live_cognition"
        for item in replay["evidence_package"]["scenario_results"]
    )
    assert replay["certification_report"]["final_verdict"] in {
        "HIRR_REAL_WORLD_READY",
        "HIRR_REAL_WORLD_GAPS_FOUND",
    }


def test_hirr_real_world_dogfood_v2_summary_artifacts_do_not_record_secret(tmp_path, monkeypatch):
    from aigol.cli import aigol_cli

    monkeypatch.setattr(aigol_cli, "_conversation_openai_provider_adapter", _fake_openai_adapter)

    result = execute_hirr_real_world_dogfood_certification_v2(
        runtime_root=tmp_path / "hirr_v2",
        workspace=tmp_path,
        scenario_ids=["HRD2-005"],
    )
    combined = ""
    for relative in ("coverage_report_path", "evidence_package_path", "replay_package_path", "certification_report_path"):
        combined += canonical_serialize(json.loads(Path(result[relative]).read_text(encoding="utf-8")))

    assert "sk-hirr-v2-test-secret" not in combined
    assert "Authorization" not in combined
