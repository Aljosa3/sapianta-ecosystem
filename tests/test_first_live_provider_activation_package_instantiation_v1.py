"""Tests for AIGOL_FIRST_LIVE_PROVIDER_ACTIVATION_PACKAGE_INSTANTIATION_V1."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1,
    FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_FAILED_CLOSED,
    STATUS_PACKAGE_INSTANTIATED,
    instantiate_first_live_provider_activation_package,
    reconstruct_first_live_provider_activation_package,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-16T00:00:00+00:00"
EXPIRES_AT = "2026-06-16T01:00:00+00:00"


def _instantiate(tmp_path: Path, **overrides) -> dict:
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


def test_activation_package_instantiation_creates_all_replay_visible_artifacts_without_live_dispatch(tmp_path):
    result = _instantiate(tmp_path)
    replay = reconstruct_first_live_provider_activation_package(tmp_path / "activation_package")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_PACKAGE_INSTANTIATED
    assert result["activation_package_instantiated"] is True
    assert result["live_dispatch_attempted"] is False
    assert result["live_dispatch_performed"] is False
    assert result["credential_secret_replayed"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert result["approval_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_APPROVAL_ARTIFACT_V1
    assert (
        result["activation_authorization_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_ACTIVATION_AUTHORIZATION_ARTIFACT_V1
    )
    assert result["credential_availability_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_CREDENTIAL_AVAILABILITY_ARTIFACT_V1
    assert result["dispatch_attempt_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_DISPATCH_ATTEMPT_ARTIFACT_V1
    assert (
        result["post_dispatch_audit_template_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_TEMPLATE_V1
    )
    assert (
        result["post_dispatch_recertification_template_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_TEMPLATE_V1
    )
    assert result["rollback_evidence_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_ROLLBACK_EVIDENCE_ARTIFACT_V1
    assert result["dispatch_attempt_artifact"]["dispatch_status"] == "ARMED_NOT_DISPATCHED"
    assert result["dispatch_attempt_artifact"]["dispatch_attempt_number"] == 0
    assert result["dispatch_attempt_artifact"]["dispatch_attempt_limit"] == 1
    assert result["post_dispatch_audit_template_artifact"]["template_status"] == "PENDING_LIVE_DISPATCH"
    assert result["rollback_evidence_artifact"]["further_live_calls_allowed"] is False
    assert replay["final_status"] == STATUS_PACKAGE_INSTANTIATED
    assert replay["replay_artifact_count"] == 8


def test_activation_package_persists_ordered_replay_evidence(tmp_path):
    _instantiate(tmp_path)
    replay_root = tmp_path / "activation_package"
    expected = [
        "first_live_provider_approval",
        "first_live_provider_activation_authorization",
        "first_live_provider_credential_policy",
        "first_live_provider_credential_availability",
        "first_live_provider_dispatch_attempt_prepared",
        "first_live_provider_post_dispatch_audit_template",
        "first_live_provider_post_dispatch_recertification_template",
        "first_live_provider_rollback_evidence",
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

    assert (replay_root / "err_openai_selection" / "000_err_resource_selection_evidence_recorded.json").exists()


def test_activation_package_replay_artifacts_do_not_contain_secret_material(tmp_path):
    _instantiate(tmp_path)
    serialized = "".join(
        canonical_serialize(load_json(path))
        for path in sorted((tmp_path / "activation_package").glob("*.json"))
    )

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "AIGOL_OPENAI_API_KEY" not in serialized
    assert "api_key" not in serialized.lower()
    assert "credential_reference_type" in serialized


def test_activation_package_lineage_links_are_reconstructable(tmp_path):
    result = _instantiate(tmp_path)
    replay = reconstruct_first_live_provider_activation_package(tmp_path / "activation_package")

    authorization = result["activation_authorization_artifact"]
    approval = result["approval_artifact"]
    credential = result["credential_availability_artifact"]
    dispatch = result["dispatch_attempt_artifact"]
    audit = result["post_dispatch_audit_template_artifact"]
    recertification = result["post_dispatch_recertification_template_artifact"]
    rollback = result["rollback_evidence_artifact"]

    assert authorization["approval_artifact_hash"] == approval["artifact_hash"]
    assert credential["activation_authorization_artifact_hash"] == authorization["artifact_hash"]
    assert dispatch["credential_availability_artifact_hash"] == credential["artifact_hash"]
    assert audit["dispatch_attempt_artifact_hash"] == dispatch["artifact_hash"]
    assert recertification["post_dispatch_audit_packet_hash"] == audit["artifact_hash"]
    assert rollback["post_dispatch_recertification_packet_hash"] == recertification["artifact_hash"]
    assert replay["rollback_evidence_present"] is True


def test_activation_package_fails_closed_when_credential_not_available(tmp_path):
    result = _instantiate(tmp_path, credential_available=False)
    replay = reconstruct_first_live_provider_activation_package(tmp_path / "activation_package")

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_dispatch_performed"] is False
    assert result["provider_invoked"] is False
    assert "credential unavailable" in result["failure_reason"]
    assert replay["final_status"] == STATUS_FAILED_CLOSED


def test_activation_package_fails_closed_for_missing_package_id(tmp_path):
    result = _instantiate(tmp_path, package_id="")

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["live_dispatch_performed"] is False
    assert "package_id is required" in result["failure_reason"]


def test_activation_package_detects_replay_tampering(tmp_path):
    _instantiate(tmp_path)
    replay_root = tmp_path / "activation_package"
    path = replay_root / "004_first_live_provider_dispatch_attempt_prepared.json"
    wrapper = load_json(path)
    wrapper["artifact"]["live_dispatch_attempted"] = True
    path.write_text(str(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="not valid JSON|replay hash mismatch"):
        reconstruct_first_live_provider_activation_package(replay_root)


def test_activation_package_module_has_no_network_or_secret_dispatch_implementation():
    import aigol.runtime.first_live_provider_activation_package_instantiation as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "Bearer " not in source
    assert "sk-" not in source
