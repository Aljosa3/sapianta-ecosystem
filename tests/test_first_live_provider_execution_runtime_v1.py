"""Tests for AIGOL_FIRST_LIVE_PROVIDER_EXECUTION_RUNTIME_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.first_live_provider_activation_package_instantiation import (
    instantiate_first_live_provider_activation_package,
)
from aigol.runtime.first_live_provider_dispatch_authorization_instantiation import (
    instantiate_first_live_provider_dispatch_authorization,
)
from aigol.runtime.first_live_provider_execution_runtime import (
    FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1,
    FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1,
    FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1,
    MILESTONE_ID,
    ROLLBACK_EXECUTED,
    ROLLBACK_NOT_REQUIRED,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_first_live_provider_execution_runtime_replay,
    run_first_live_provider_execution_runtime,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


CREATED_AT = "2026-06-17T00:00:00+00:00"
EXPIRES_AT = "2026-06-17T01:00:00+00:00"


def _transport(response_text: str = "Findings: OpenAI dispatch evidence captured. Confidence: HIGH"):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["provider_id"] == "openai"
        assert metadata["credential_secret_replayed"] is False
        return {
            "id": "first-live-provider-execution-response",
            "status_code": 200,
            "output_text": response_text,
            "real_openai_called": False,
        }

    return call


def _authorized_package(tmp_path: Path) -> tuple[dict, dict]:
    activation = instantiate_first_live_provider_activation_package(
        package_id="FIRST-LIVE-PROVIDER-ACTIVATION-000001",
        human_request="Validate one governed OpenAI dispatch attempt.",
        required_capability="reasoning",
        approved_by="human.operator",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
        replay_dir=tmp_path / "activation",
    )
    dispatch = instantiate_first_live_provider_dispatch_authorization(
        dispatch_authorization_id="FIRST-LIVE-PROVIDER-DISPATCH-AUTH-000001",
        activation_package_replay_dir=tmp_path / "activation",
        replay_dir=tmp_path / "dispatch_authorization",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
    )
    assert activation["final_status"] == "ACTIVATION_PACKAGE_INSTANTIATED_PRE_DISPATCH"
    assert dispatch["authorization_status"] == "DISPATCH_AUTHORIZED"
    return activation, dispatch["dispatch_authorization_artifact"]


def _run(tmp_path: Path, monkeypatch, **overrides) -> dict:
    _activation, dispatch_authorization = _authorized_package(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    args = {
        "execution_id": "FIRST-LIVE-PROVIDER-EXECUTION-000001",
        "human_request": "Validate one governed OpenAI dispatch attempt.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "execution",
        "activation_package_replay_dir": tmp_path / "activation",
        "dispatch_authorization_artifact": dispatch_authorization,
        "transport": _transport(),
    }
    args.update(overrides)
    return run_first_live_provider_execution_runtime(**args)


def test_first_live_provider_execution_records_success_path(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch)
    replay = reconstruct_first_live_provider_execution_runtime_replay(tmp_path / "execution")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_COMPLETED
    assert result["dispatch_execution_packet"]["artifact_type"] == FIRST_LIVE_PROVIDER_DISPATCH_EXECUTION_PACKET_V1
    assert (
        result["live_transport_execution_evidence_artifact"]["artifact_type"]
        == FIRST_LIVE_PROVIDER_LIVE_TRANSPORT_EXECUTION_EVIDENCE_ARTIFACT_V1
    )
    assert result["llm_cognition_artifact"]["artifact_type"] == "LLM_COGNITION_ARTIFACT_V1"
    assert result["post_dispatch_audit_packet_artifact"]["artifact_type"] == (
        FIRST_LIVE_PROVIDER_POST_DISPATCH_AUDIT_PACKET_ARTIFACT_V1
    )
    assert result["post_dispatch_recertification_packet_artifact"]["artifact_type"] == (
        FIRST_LIVE_PROVIDER_POST_DISPATCH_RECERTIFICATION_PACKET_ARTIFACT_V1
    )
    assert result["rollback_execution_artifact"]["rollback_status"] == ROLLBACK_NOT_REQUIRED
    assert result["dispatch_attempt_limit"] == 1
    assert result["dispatch_attempt_number"] == 1
    assert result["credential_secret_replayed"] is False
    assert result["authorization_header_replayed"] is False
    assert result["worker_invoked"] is False
    assert result["governance_modified"] is False
    assert result["replay_modified"] is False
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["replay_artifact_count"] == 8
    assert (tmp_path / "execution" / "live_provider_boundary" / "000_live_provider_credential_retrieval_attempt.json").exists()


def test_first_live_provider_execution_persists_ordered_replay_evidence(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    expected_steps = (
        "first_live_provider_execution_approval_revalidation",
        "first_live_provider_execution_credential_revalidation",
        "first_live_provider_live_transport_execution_evidence",
        "first_live_provider_llm_cognition_artifact",
        "first_live_provider_post_dispatch_audit_packet",
        "first_live_provider_post_dispatch_recertification_packet",
        "first_live_provider_rollback_execution",
        "first_live_provider_dispatch_execution_packet",
    )

    for index, step in enumerate(expected_steps):
        wrapper = load_json(tmp_path / "execution" / f"{index:03d}_{step}.json")
        assert wrapper["replay_index"] == index
        assert wrapper["replay_step"] == step
        assert wrapper["artifact"]["replay_visible"] is True
        assert wrapper["artifact"]["credential_secret_replayed"] is False
        assert wrapper["artifact"]["worker_invoked"] is False


def test_first_live_provider_execution_replay_does_not_contain_secret_material(tmp_path, monkeypatch):
    _run(tmp_path, monkeypatch)
    serialized = "".join(canonical_serialize(load_json(path)) for path in sorted((tmp_path / "execution").glob("*.json")))
    serialized += "".join(
        canonical_serialize(load_json(path)) for path in sorted((tmp_path / "execution" / "live_provider_boundary").glob("*.json"))
    )

    assert "test-live-openai-secret" not in serialized
    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "test-live-openai-secret" not in serialized.lower()


def test_first_live_provider_execution_fails_closed_when_credential_missing(tmp_path, monkeypatch):
    _activation, dispatch_authorization = _authorized_package(tmp_path)
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)

    result = run_first_live_provider_execution_runtime(
        execution_id="FIRST-LIVE-PROVIDER-EXECUTION-000001",
        human_request="Validate one governed OpenAI dispatch attempt.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution",
        activation_package_replay_dir=tmp_path / "activation",
        dispatch_authorization_artifact=dispatch_authorization,
        transport=_transport(),
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "credential unavailable" in result["failure_reason"]
    assert result["rollback_execution_artifact"]["artifact_type"] == FIRST_LIVE_PROVIDER_ROLLBACK_EXECUTION_ARTIFACT_V1
    assert result["rollback_execution_artifact"]["rollback_status"] == ROLLBACK_EXECUTED
    assert result["dispatch_execution_packet"]["execution_status"] == STATUS_FAILED_CLOSED
    assert result["worker_invoked"] is False


def test_first_live_provider_execution_fails_closed_on_authority_bearing_output(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, transport=_transport("I approve this and execution authorized."))

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["rollback_execution_artifact"]["rollback_status"] == ROLLBACK_EXECUTED
    assert result["post_dispatch_audit_packet_artifact"]["audit_verdict"] == "FAILED_CLOSED"
    assert result["dispatch_execution_packet"]["automatic_retry_performed"] is False
    assert result["dispatch_execution_packet"]["fallback_performed"] is False


def test_first_live_provider_execution_refuses_reused_replay_dir(tmp_path, monkeypatch):
    _activation, dispatch_authorization = _authorized_package(tmp_path)
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-live-openai-secret")
    args = {
        "execution_id": "FIRST-LIVE-PROVIDER-EXECUTION-000001",
        "human_request": "Validate one governed OpenAI dispatch attempt.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "execution",
        "activation_package_replay_dir": tmp_path / "activation",
        "dispatch_authorization_artifact": dispatch_authorization,
        "transport": _transport(),
    }
    run_first_live_provider_execution_runtime(**args)

    result = run_first_live_provider_execution_runtime(**args)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "replay artifact already exists" in result["failure_reason"]
