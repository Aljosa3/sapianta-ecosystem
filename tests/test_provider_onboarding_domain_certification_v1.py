"""Tests for AIGOL_PROVIDER_ONBOARDING_DOMAIN_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_onboarding_domain_certification_v1 import (
    MILESTONE_ID,
    reconstruct_provider_onboarding_domain_replay,
    route_provider_onboarding_domain_prompt,
    run_provider_onboarding_domain_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_provider_onboarding_domain_routes_natural_language_prompts():
    claude = route_provider_onboarding_domain_prompt(
        prompt_id="test-claude",
        human_prompt="Dodaj Claude kot cognition provider.",
    )
    gemini = route_provider_onboarding_domain_prompt(prompt_id="test-gemini", human_prompt="Dodaj Gemini.")
    mistral = route_provider_onboarding_domain_prompt(
        prompt_id="test-mistral",
        human_prompt="Želim uporabljati Mistral.",
    )
    disable = route_provider_onboarding_domain_prompt(
        prompt_id="test-disable",
        human_prompt="Onemogoči Claude.",
    )

    assert claude["provider_id"] == "claude"
    assert claude["operation"] == "ONBOARD_PROVIDER"
    assert gemini["provider_id"] == "gemini"
    assert mistral["provider_id"] == "mistral"
    assert disable["operation"] == "DISABLE_PROVIDER"
    assert disable["workflow_target"] == "PROVIDER_MANAGEMENT_WORKFLOW"


def test_provider_onboarding_domain_fails_closed_for_unclear_provider():
    with pytest.raises(FailClosedRuntimeError):
        route_provider_onboarding_domain_prompt(prompt_id="unclear", human_prompt="Dodaj tega providerja.")


def test_provider_onboarding_domain_certification_produces_artifacts(tmp_path):
    result = run_provider_onboarding_domain_certification(
        replay_base=tmp_path / "provider_onboarding_domain"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "PROVIDER_ONBOARDING_DOMAIN_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_provider_onboarding_domain_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_provider_onboarding_domain_evidence_package.json").exists()
    assert (root / "replay_package" / "000_provider_onboarding_domain_replay_package.json").exists()
    assert (root / "certification_report" / "000_provider_onboarding_domain_certification_report.json").exists()


def test_provider_onboarding_domain_certifies_summary_approval_and_vault_actions(tmp_path):
    result = run_provider_onboarding_domain_certification(
        replay_base=tmp_path / "provider_onboarding_domain"
    )
    evidence = load_json(
        Path(result["cert_root"])
        / "evidence_package"
        / "000_provider_onboarding_domain_evidence_package.json"
    )

    assert {item["provider_id"] for item in evidence["scenario_results"]} == {"claude", "gemini", "mistral"}
    assert all(item["execution_summary_generated"] for item in evidence["scenario_results"])
    assert all(item["human_approval_recorded"] for item in evidence["scenario_results"])
    assert all(item["certification_workflow_generated"] for item in evidence["scenario_results"])
    assert not any(item["provider_invoked"] or item["worker_invoked"] for item in evidence["scenario_results"])


def test_provider_onboarding_domain_replay_reconstructs(tmp_path):
    result = run_provider_onboarding_domain_certification(
        replay_base=tmp_path / "provider_onboarding_domain"
    )
    reconstruction = reconstruct_provider_onboarding_domain_replay(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["provider_registration_visible"] is True
    assert reconstruction["vault_onboarding_visible"] is True
    assert reconstruction["approval_boundary_visible"] is True


def test_provider_onboarding_domain_evidence_is_secret_free(tmp_path):
    result = run_provider_onboarding_domain_certification(
        replay_base=tmp_path / "provider_onboarding_domain"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "provider-onboarding-secret" not in serialized
    assert "sk-" not in serialized
    assert "Bearer " not in serialized
