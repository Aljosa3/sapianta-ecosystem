"""Tests for G11-06 Codex Worker/Provider integration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.codex_worker_platform_integration import (
    CODEX_COGNITION_CREDENTIAL_REFERENCE,
    CODEX_COGNITION_PROVIDER_ID,
    CODEX_EXECUTION_CREDENTIAL_REFERENCE,
    CODEX_EXECUTION_WORKER_ID,
    MILESTONE_ID,
    reconstruct_codex_worker_provider_integration,
    register_codex_worker_provider_integration,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_governance_runtime import build_provider_credential_diagnostic
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-07-02T00:00:00Z"


def test_codex_registers_as_separate_provider_and_worker_identities(tmp_path):
    result = register_codex_worker_provider_integration(
        replay_dir=tmp_path / "codex",
        created_at=CREATED_AT,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "CODEX_REGISTERED_AS_GOVERNED_WORKER_AND_PROVIDER"
    assert result["codex_cognition_provider_id"] == CODEX_COGNITION_PROVIDER_ID
    assert result["codex_execution_worker_id"] == CODEX_EXECUTION_WORKER_ID
    assert result["provider_credential_reference"] == CODEX_COGNITION_CREDENTIAL_REFERENCE
    assert result["worker_credential_reference"] == CODEX_EXECUTION_CREDENTIAL_REFERENCE
    assert result["provider_credential_reference"] != result["worker_credential_reference"]
    assert all(result["assertions"].values())


def test_codex_integration_replay_reconstructs_independent_roles(tmp_path):
    register_codex_worker_provider_integration(replay_dir=tmp_path / "codex", created_at=CREATED_AT)

    reconstruction = reconstruct_codex_worker_provider_integration(tmp_path / "codex")

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["provider_identity"]["provider_id"] == CODEX_COGNITION_PROVIDER_ID
    assert reconstruction["provider_identity"]["provider_invoked"] is False
    assert reconstruction["provider_identity"]["worker_invoked"] is False
    assert reconstruction["worker_identity"]["worker_id"] == CODEX_EXECUTION_WORKER_ID
    assert reconstruction["worker_identity"]["provider_authority"] is False
    assert reconstruction["worker_identity"]["execution_performed"] is False
    assert all(reconstruction["assertions"].values())


def test_codex_authority_boundary_preserves_certified_owners(tmp_path):
    register_codex_worker_provider_integration(replay_dir=tmp_path / "codex", created_at=CREATED_AT)

    boundary = load_json(tmp_path / "codex" / "authority_boundary" / "000_codex_authority_boundary.json")
    health = load_json(
        tmp_path / "codex" / "architectural_health" / "000_codex_architectural_health_observation.json"
    )

    assert boundary["provider_execution_authority"] is False
    assert boundary["provider_worker_authority"] is False
    assert boundary["worker_governance_authority"] is False
    assert boundary["authority_transfer_detected"] is False
    assert boundary["platform_core_authority_preserved"] is True
    assert boundary["governance_authority_preserved"] is True
    assert boundary["replay_authority_preserved"] is True
    assert health["architectural_health_authority"] is False
    assert health["advisory_only"] is True
    assert health["findings"] == []


def test_codex_provider_governance_registration_is_secret_free(tmp_path):
    register_codex_worker_provider_integration(replay_dir=tmp_path / "codex", created_at=CREATED_AT)

    diagnostic = build_provider_credential_diagnostic(
        provider_id=CODEX_COGNITION_PROVIDER_ID,
        env={"AIGOL_CODEX_COGNITION_CREDENTIAL": "codex-secret-value"},
    )
    serialized = ""
    for path in sorted((tmp_path / "codex").rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert diagnostic["provider_id"] == CODEX_COGNITION_PROVIDER_ID
    assert diagnostic["credential_present"] is True
    assert "codex-secret-value" not in json.dumps(diagnostic)
    assert "codex-secret-value" not in serialized
    assert "Bearer " not in serialized
    assert "sk-" not in serialized


def test_codex_registration_is_append_only(tmp_path):
    register_codex_worker_provider_integration(replay_dir=tmp_path / "codex", created_at=CREATED_AT)

    with pytest.raises(FailClosedRuntimeError, match="replay already exists"):
        register_codex_worker_provider_integration(replay_dir=tmp_path / "codex", created_at=CREATED_AT)
