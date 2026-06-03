"""Tests for AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.domain_and_worker_resolution_registry import (
    AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION,
    DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1,
    RESOLUTION_SUCCEEDED,
    default_domain_worker_registry,
    reconstruct_domain_worker_resolution_replay,
    resolve_domain_worker_milestone,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-02T17:00:00+00:00"


def test_resolves_trading_market_evidence_worker_foundation(tmp_path) -> None:
    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-TRADING-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resolution",
    )
    reconstructed = reconstruct_domain_worker_resolution_replay(tmp_path / "resolution")
    artifact = capture["domain_worker_resolution_artifact"]

    assert artifact["artifact_type"] == DOMAIN_WORKER_RESOLUTION_ARTIFACT_V1
    assert capture["resolution_status"] == RESOLUTION_SUCCEEDED
    assert capture["domain_id"] == "TRADING"
    assert capture["worker_family_id"] == "MARKET_EVIDENCE_NORMALIZATION"
    assert capture["milestone_type"] == "WORKER_FOUNDATION"
    assert capture["registry_version"] == AIGOL_DOMAIN_AND_WORKER_RESOLUTION_REGISTRY_VERSION
    assert capture["registry_hash"].startswith("sha256:")
    assert capture["resolution_result"]["canonical_milestone_prefix"] == (
        "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION"
    )
    assert capture["semantic_interpretation_performed"] is False
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["resolution_status"] == RESOLUTION_SUCCEEDED
    assert reconstructed["registry_hash"] == capture["registry_hash"]
    assert reconstructed["replay_artifact_count"] == 2


def test_registry_supports_future_domains_without_worker_resolution(tmp_path) -> None:
    registry = default_domain_worker_registry()

    assert {domain["domain_id"] for domain in registry["domains"]} >= {
        "TRADING",
        "MARKETING",
        "HEALTHCARE",
        "PUBLIC_SERVICES",
    }

    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-MARKETING-000001",
        domain_id="MARKETING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "marketing",
    )

    assert capture["fail_closed"] is True
    assert "unknown worker family" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_resolves_trading_portfolio_context_by_intake_worker_family(tmp_path) -> None:
    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-TRADING-PORTFOLIO-CONTEXT-000001",
        domain_id="TRADING",
        worker_family_id="PORTFOLIO_CONTEXT",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "portfolio_context",
    )
    reconstructed = reconstruct_domain_worker_resolution_replay(tmp_path / "portfolio_context")

    assert capture["resolution_status"] == RESOLUTION_SUCCEEDED
    assert capture["domain_id"] == "TRADING"
    assert capture["worker_family_id"] == "PORTFOLIO_CONTEXT"
    assert capture["resolution_result"]["worker_family"]["worker_class"] == "PORTFOLIO_CONTEXT"
    assert capture["resolution_result"]["canonical_milestone_prefix"] == "TRADING_PORTFOLIO_CONTEXT_WORKER_FOUNDATION"
    assert capture["semantic_interpretation_performed"] is False
    assert capture["provider_invoked"] is False
    assert reconstructed["worker_family_id"] == "PORTFOLIO_CONTEXT"
    assert reconstructed["replay_artifact_count"] == 2


def test_unknown_domain_fails_closed(tmp_path) -> None:
    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-UNKNOWN-DOMAIN-000001",
        domain_id="LEGAL",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unknown_domain",
    )

    assert capture["fail_closed"] is True
    assert "unknown domain" in capture["failure_reason"]


def test_invalid_milestone_type_fails_closed(tmp_path) -> None:
    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-BAD-MILESTONE-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_DEPLOYMENT",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bad_milestone",
    )

    assert capture["fail_closed"] is True
    assert "invalid milestone type" in capture["failure_reason"]


def test_duplicate_worker_registration_fails_closed(tmp_path) -> None:
    registry = default_domain_worker_registry()
    registry["worker_families"].append(dict(registry["worker_families"][0]))
    registry.pop("registry_hash", None)

    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-DUPLICATE-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "duplicate",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "duplicate worker registration" in capture["failure_reason"]


def test_ambiguous_worker_alias_fails_closed(tmp_path) -> None:
    registry = default_domain_worker_registry()
    registry["worker_families"].append(
        {
            "domain_id": "TRADING",
            "worker_family_id": "MARKET_SIGNAL_REVIEW",
            "display_name": "Market Signal Review",
            "worker_class": "SIGNAL_REVIEW",
            "status": "FOUNDATION_CANDIDATE",
            "aliases": ("MARKET EVIDENCE NORMALIZATION",),
            "authority": "EVIDENCE_REVIEW_ONLY",
        }
    )
    registry.pop("registry_hash", None)

    capture = resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-AMBIGUOUS-000001",
        domain_id="TRADING",
        worker_family_id="MARKET EVIDENCE NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "ambiguous worker family" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_resolution_replay(tmp_path) -> None:
    resolve_domain_worker_milestone(
        resolution_id="RESOLUTION-CORRUPT-000001",
        domain_id="TRADING",
        worker_family_id="MARKET_EVIDENCE_NORMALIZATION",
        milestone_type="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_domain_worker_resolution_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_family_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_worker_resolution_replay(tmp_path / "corrupt")


def test_registry_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.domain_and_worker_resolution_registry as registry_runtime

    source = inspect.getsource(registry_runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
