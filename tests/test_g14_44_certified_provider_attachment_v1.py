"""Regression coverage for G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aigol.provider.certified_provider_attachment import (
    CERTIFIED_PROVIDER_ATTACHMENT_API,
    CERTIFIED_PROVIDER_ATTACHMENT_VERSION,
    run_certified_provider_attachment,
)
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry


PROVIDER_ID = "certified-test-provider"
PROVIDER_VERSION = "certified-provider-v1"
CREATED_AT = "2026-07-06T00:00:00Z"


class CertifiedTestProviderAdapter:
    provider_id = PROVIDER_ID
    provider_version = PROVIDER_VERSION

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "proposal_summary": "Certified attachment test proposal.",
                "proposed_outputs": ["docs/governance/G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1.md"],
                "constraints_acknowledged": ["PROPOSAL_ONLY"],
                "assumptions": ["Provider attachment remains non-authoritative."],
                "known_gaps": ["None."],
            },
            timestamp=timestamp,
        )


def test_certified_provider_attachment_wraps_provider_platform(tmp_path) -> None:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=PROVIDER_ID,
            provider_type="test",
            provider_version=PROVIDER_VERSION,
            provider_status=AVAILABLE,
        )
    )

    capture = run_certified_provider_attachment(
        provider_id=PROVIDER_ID,
        request={"prompt": "Create one proposal."},
        proposal_id="CERTIFIED-PROVIDER-ATTACHMENT-000001",
        timestamp=CREATED_AT,
        registry=registry,
        adapter=CertifiedTestProviderAdapter(),
        replay_dir=tmp_path / "provider",
    )

    certification = capture["certified_provider_attachment"]

    assert capture["provider_proposal_created"]["provider_invoked"] is True
    assert certification["runtime_version"] == CERTIFIED_PROVIDER_ATTACHMENT_VERSION
    assert certification["certified_provider_attachment_api"] == CERTIFIED_PROVIDER_ATTACHMENT_API
    assert certification["provider_id"] == PROVIDER_ID
    assert certification["provider_invoked"] is True
    assert certification["request_construction_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["response_normalization_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["provider_diagnostics_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["failure_normalization_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["retry_entry_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["provider_evidence_owner"] == "CERTIFIED_PROVIDER_ATTACHMENT"
    assert certification["transport_authority"] is False
    assert certification["governance_authority"] is False
    assert certification["worker_authority"] is False
    assert certification["replay_visible"] is True

    persisted = json.loads(
        (tmp_path / "provider" / "002_certified_provider_attachment_recorded.json").read_text(
            encoding="utf-8"
        )
    )
    persisted_artifact = persisted["artifact"]
    assert persisted["replay_step"] == "certified_provider_attachment_recorded"
    assert persisted_artifact["artifact_hash"] == certification["artifact_hash"]
    assert persisted_artifact["certified_provider_attachment_api"] == CERTIFIED_PROVIDER_ATTACHMENT_API


def test_production_provider_callers_use_certified_attachment() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    allowed = {
        repo_root / "aigol/provider/provider_runtime.py",
        repo_root / "aigol/provider/certified_provider_attachment.py",
    }
    offenders: list[str] = []
    for path in sorted((repo_root / "aigol").rglob("*.py")):
        if path in allowed:
            continue
        source = path.read_text(encoding="utf-8")
        if "run_provider_attachment(" in source:
            offenders.append(str(path.relative_to(repo_root)))

    assert offenders == []
