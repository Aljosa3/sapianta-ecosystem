"""Tests for AIGOL_FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_INSTANTIATION_V1."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    DISPATCH_AUTHORIZED,
    FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_AUTHORIZATION_INSTANTIATED,
    STATUS_FAILED_CLOSED,
    instantiate_first_live_provider_dispatch_authorization,
    reconstruct_first_live_provider_dispatch_authorization,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-17T00:00:00+00:00"
EXPIRES_AT = "2026-06-17T01:00:00+00:00"


def _activation_package(tmp_path: Path, **overrides) -> dict:
    args = {
        "package_id": "FIRST-LIVE-ACTIVATION-PACKAGE-000001",
        "human_request": "Prepare a single governed OpenAI activation package.",
        "required_capability": "reasoning",
        "approved_by": "human.operator",
        "created_at": CREATED_AT,
        "expires_at": EXPIRES_AT,
        "replay_dir": tmp_path / "activation_package",
    }
    args.update(overrides)
    return instantiate_first_live_provider_activation_package(**args)


def _authorize(tmp_path: Path, **overrides) -> dict:
    _activation_package(tmp_path, **overrides.pop("activation_overrides", {}))
    args = {
        "dispatch_authorization_id": "FIRST-LIVE-DISPATCH-AUTHORIZATION-000001",
        "activation_package_replay_dir": tmp_path / "activation_package",
        "replay_dir": tmp_path / "dispatch_authorization",
        "created_at": CREATED_AT,
        "expires_at": EXPIRES_AT,
    }
    args.update(overrides)
    return instantiate_first_live_provider_dispatch_authorization(**args)


def test_dispatch_authorization_instantiates_single_attempt_authorization_without_dispatch(tmp_path):
    result = _authorize(tmp_path)
    replay = reconstruct_first_live_provider_dispatch_authorization(tmp_path / "dispatch_authorization")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_AUTHORIZATION_INSTANTIATED
    assert result["authorization_status"] == DISPATCH_AUTHORIZED
    assert result["live_dispatch_attempted"] is False
    assert result["live_dispatch_performed"] is False
    assert result["credential_secret_replayed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert (
        result["approval_freshness_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_APPROVAL_FRESHNESS_VALIDATION_ARTIFACT_V1
    )
    assert (
        result["credential_freshness_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_CREDENTIAL_FRESHNESS_VALIDATION_ARTIFACT_V1
    )
    assert (
        result["dispatch_execution_authorization_evidence_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_AUTHORIZATION_EVIDENCE_ARTIFACT_V1
    )
    assert result["dispatch_authorization_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_DISPATCH_AUTHORIZATION_ARTIFACT_V1
    assert result["dispatch_authorization_artifact"]["provider_id"] == "openai"
    assert result["dispatch_authorization_artifact"]["dispatch_count"] == 1
    assert result["dispatch_authorization_artifact"]["cognition_only"] is True
    assert result["dispatch_authorization_artifact"]["live_dispatch_performed"] is False
    assert replay["final_status"] == STATUS_AUTHORIZATION_INSTANTIATED
    assert replay["dispatch_count"] == 1
    assert replay["cognition_only"] is True
    assert replay["replay_artifact_count"] == 4


def test_dispatch_authorization_persists_ordered_replay_evidence(tmp_path):
    _authorize(tmp_path)
    replay_root = tmp_path / "dispatch_authorization"
    expected = [
        "first_live_provider_approval_freshness_validation",
        "first_live_provider_credential_freshness_validation",
        "first_live_provider_dispatch_execution_authorization_evidence",
        "first_live_provider_dispatch_authorization",
    ]

    for index, step in enumerate(expected):
        wrapper = load_json(replay_root / f"{index:03d}_{step}.json")
        assert wrapper["replay_index"] == index
        assert wrapper["replay_step"] == step
        assert wrapper["artifact"]["replay_visible"] is True
        assert wrapper["artifact"]["provider_invoked"] is False
        assert wrapper["artifact"]["worker_invoked"] is False
        assert wrapper["artifact"]["governance_modified"] is False
        assert wrapper["artifact"]["replay_modified"] is False


def test_dispatch_authorization_replay_artifacts_do_not_contain_secret_material(tmp_path):
    _authorize(tmp_path)
    serialized = "".join(
        canonical_serialize(load_json(path))
        for path in sorted((tmp_path / "dispatch_authorization").glob("*.json"))
    )

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "AIGOL_OPENAI_API_KEY" not in serialized
    assert "api_key" not in serialized.lower()
    assert "authorization_header_replayed" in serialized


def test_dispatch_authorization_lineage_links_are_reconstructable(tmp_path):
    result = _authorize(tmp_path)
    replay = reconstruct_first_live_provider_dispatch_authorization(tmp_path / "dispatch_authorization")

    approval_freshness = result["approval_freshness_artifact"]
    credential_freshness = result["credential_freshness_artifact"]
    dispatch_evidence = result["dispatch_execution_authorization_evidence_artifact"]
    authorization = result["dispatch_authorization_artifact"]

    assert dispatch_evidence["approval_freshness_validation_hash"] == approval_freshness["artifact_hash"]
    assert dispatch_evidence["credential_freshness_validation_hash"] == credential_freshness["artifact_hash"]
    assert authorization["approval_freshness_validation_hash"] == approval_freshness["artifact_hash"]
    assert authorization["credential_freshness_validation_hash"] == credential_freshness["artifact_hash"]
    assert authorization["dispatch_execution_authorization_evidence_hash"] == dispatch_evidence["artifact_hash"]
    assert replay["authorization_status"] == DISPATCH_AUTHORIZED


def test_dispatch_authorization_fails_closed_when_approval_expired(tmp_path):
    result = _authorize(
        tmp_path,
        created_at="2026-06-17T02:00:00+00:00",
    )
    replay = reconstruct_first_live_provider_dispatch_authorization(tmp_path / "dispatch_authorization")

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["authorization_status"] != DISPATCH_AUTHORIZED
    assert result["live_dispatch_performed"] is False
    assert "approval expired" in result["failure_reason"]
    assert replay["final_status"] == STATUS_FAILED_CLOSED


def test_dispatch_authorization_fails_closed_when_activation_package_was_tampered(tmp_path):
    _activation_package(tmp_path)
    path = tmp_path / "activation_package" / "004_first_live_provider_dispatch_attempt_prepared.json"
    wrapper = load_json(path)
    wrapper["artifact"]["live_dispatch_attempted"] = True
    path.write_text(str(wrapper), encoding="utf-8")

    result = instantiate_first_live_provider_dispatch_authorization(
        dispatch_authorization_id="FIRST-LIVE-DISPATCH-AUTHORIZATION-TAMPERED",
        activation_package_replay_dir=tmp_path / "activation_package",
        replay_dir=tmp_path / "dispatch_authorization",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_dispatch_performed"] is False
    assert "not valid JSON" in result["failure_reason"] or "hash mismatch" in result["failure_reason"]


def test_dispatch_authorization_detects_replay_tampering(tmp_path):
    _authorize(tmp_path)
    replay_root = tmp_path / "dispatch_authorization"
    path = replay_root / "003_first_live_provider_dispatch_authorization.json"
    wrapper = load_json(path)
    wrapper["artifact"]["dispatch_count"] = 2
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="not valid JSON|replay hash mismatch"):
        reconstruct_first_live_provider_dispatch_authorization(replay_root)


def test_dispatch_authorization_module_has_no_network_or_secret_dispatch_implementation():
    import aigol.runtime.first_live_provider_dispatch_authorization_instantiation as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "Bearer " not in source
    assert "sk-" not in source
