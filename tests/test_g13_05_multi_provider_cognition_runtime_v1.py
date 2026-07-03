"""Tests for G13_05_MULTI_PROVIDER_COGNITION_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.runtime.g13_05_multi_provider_cognition_runtime_v1 import (
    FINAL_VERDICT_CERTIFIED,
    FINAL_VERDICT_PARTIALLY_READY,
    OPENAI_PROVIDER_ID,
    STANDARDS_ADAPTER_PROVIDER_ID,
    reconstruct_g13_05_multi_provider_cognition_runtime_v1,
    run_g13_05_multi_provider_cognition_runtime_v1,
)
from aigol.runtime.transport.serialization import load_json


class FakeOpenAIAdapter:
    provider_id = OPENAI_PROVIDER_ID
    provider_version = "openai-responses-v1"

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        if self.fail:
            raise RuntimeError("OpenAI unavailable in test")
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "model": "gpt-test",
                "response_text": json.dumps(
                    {
                        "findings": ["OpenAI returned governed cognition evidence."],
                        "assumptions": ["Provider output is non-authoritative."],
                        "alternatives": ["Compare against the standards adapter."],
                        "risks": ["Live providers can return variable response shapes."],
                        "uncertainties": ["Credential and network state are environment dependent."],
                        "confidence": "MEDIUM",
                    },
                    sort_keys=True,
                ),
                "raw_response": {
                    "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
                },
                "raw_response_hash": "sha256:test",
            },
            timestamp=timestamp,
        )


def test_g13_05_certifies_openai_plus_standards_adapter(tmp_path):
    result = run_g13_05_multi_provider_cognition_runtime_v1(
        runtime_root=tmp_path / "g13_05",
        openai_adapter=FakeOpenAIAdapter(),
    )
    replay = reconstruct_g13_05_multi_provider_cognition_runtime_v1(result["cert_root"])
    readiness = load_json(Path(result["readiness_assessment_path"]))
    evidence = load_json(Path(result["evidence_inventory_path"]))

    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert replay["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert replay["successful_provider_count"] == 2
    assert result["successful_providers"] == [OPENAI_PROVIDER_ID, STANDARDS_ADAPTER_PROVIDER_ID]
    assert readiness["provider_abstraction_validated"] is True
    assert evidence["provider_abstraction_validated"] is True
    assert evidence["worker_execution_evidence"]["worker_boundary_preserved"] is True


def test_g13_05_reports_partial_readiness_when_openai_fails(tmp_path):
    result = run_g13_05_multi_provider_cognition_runtime_v1(
        runtime_root=tmp_path / "g13_05",
        openai_adapter=FakeOpenAIAdapter(fail=True),
    )
    readiness = load_json(Path(result["readiness_assessment_path"]))

    assert result["final_verdict"] == FINAL_VERDICT_PARTIALLY_READY
    assert result["successful_providers"] == [STANDARDS_ADAPTER_PROVIDER_ID]
    assert result["failed_providers"] == [OPENAI_PROVIDER_ID]
    assert readiness["remaining_gaps"]
