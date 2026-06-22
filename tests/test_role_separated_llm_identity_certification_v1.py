"""Tests for AIGOL_ROLE_SEPARATED_LLM_IDENTITY_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.role_separated_llm_identity_certification_v1 import (
    MILESTONE_ID,
    reconstruct_role_separated_llm_identity_replay,
    run_role_separated_llm_identity_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_role_separated_certification_produces_required_artifacts(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_role_separated_llm_identity_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_role_separated_llm_identity_evidence_package.json").exists()
    assert (root / "replay_package" / "000_role_separated_llm_identity_replay_package.json").exists()
    assert (root / "certification_report" / "000_role_separated_llm_identity_certification_report.json").exists()


def test_role_separated_identities_have_distinct_references_and_roles(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")
    report = load_json(
        Path(result["cert_root"])
        / "certification_report"
        / "000_role_separated_llm_identity_certification_report.json"
    )
    evidence = load_json(
        Path(result["cert_root"])
        / "evidence_package"
        / "000_role_separated_llm_identity_evidence_package.json"
    )

    assert report["assertions"]["role_separated_credential_identities_created"] is True
    assert report["assertions"]["credential_references_are_unique"] is True
    assert report["assertions"]["same_external_provider_shared_across_roles"] is True
    assert {item["credential_reference"] for item in evidence["role_results"]} == {
        "vault://provider/openai-cognition",
        "vault://worker/openai-translation",
        "vault://worker/openai-repair",
    }
    assert {item["architectural_role"] for item in evidence["role_results"]} == {
        "COGNITION_PROVIDER",
        "TRANSLATION_WORKER",
        "REPAIR_WORKER",
    }


def test_independent_disable_does_not_mutate_other_role_status(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")
    evidence = load_json(
        Path(result["cert_root"])
        / "evidence_package"
        / "000_role_separated_llm_identity_evidence_package.json"
    )
    statuses = {item["identity_id"]: item["final_lifecycle_status"] for item in evidence["role_results"]}

    assert statuses == {
        "openai-cognition": "ENABLED",
        "openai-translation": "DISABLED",
        "openai-repair": "ENABLED",
    }


def test_replay_reconstruction_distinguishes_all_roles(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")
    reconstruction = reconstruct_role_separated_llm_identity_replay(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["distinguished_cognition_provider"] is True
    assert reconstruction["distinguished_translation_worker"] is True
    assert reconstruction["distinguished_repair_worker"] is True


def test_authority_never_transfers_to_role_separated_llm_identity(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")

    for path in Path(result["cert_root"]).glob("role_identities/*/004_authority_boundary.json"):
        artifact = load_json(path)
        assert artifact["llm_may_propose"] is True
        assert artifact["llm_may_contribute"] is True
        assert artifact["llm_is_authority"] is False
        assert artifact["authority_transfer_detected"] is False
        assert artifact["human_authority_preserved"] is True
        assert artifact["governance_authority_preserved"] is True


def test_role_separated_certification_evidence_is_secret_free(tmp_path):
    result = run_role_separated_llm_identity_certification(replay_base=tmp_path / "role_separated")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
