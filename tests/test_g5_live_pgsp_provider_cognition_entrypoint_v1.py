"""Tests for G5-03 live PGSP provider cognition entrypoint."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.g5_live_pgsp_provider_cognition_entrypoint import (
    G5_03_RUNTIME_VERSION,
    LIVE_PGSP_PROVIDER_COGNITION_RECORDED,
    LIVE_PGSP_ROUTED_TO_G5_02,
    reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay,
    run_g5_live_pgsp_provider_cognition_entrypoint,
)
from aigol.runtime.g5_pgsp_bound_read_only_provider_cognition_runtime import (
    AUTHORIZATION_SCOPE,
    G5_02_RUNTIME_VERSION,
    READ_ONLY_PROVIDER_COGNITION_COMPLETED,
    READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_identity_boundaries import (
    COGNITION_PROVIDER,
    CREDENTIAL_CONFIGURED_INACTIVE,
    PROVIDER_REGISTERED_INACTIVE,
    create_provider_credential_reference,
    create_provider_identity,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-30T00:00:00Z"
SESSION_ID = "G5-03-LIVE-PGSP-SESSION-000001"
LIVE_REQUEST = "Review the G5 provider cognition entrypoint implementation plan."


def _capability() -> list[dict]:
    return [
        {
            "capability_id": "G5-03-CAPABILITY-COGNITION",
            "capability": "bounded live PGSP read-only cognition",
            "capability_scope": COGNITION_PROVIDER,
            "advisory_only": True,
            "execution_authority": False,
        }
    ]


def _provider_identity(tmp_path) -> dict:
    credential = create_provider_credential_reference(
        credential_reference_id="G5-03-CREDENTIAL-COGNITION",
        credential_reference="vault://provider/g5-03/openai-cognition",
        credential_role=COGNITION_PROVIDER,
        credential_lifecycle_state=CREDENTIAL_CONFIGURED_INACTIVE,
        secret_present=False,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "credential",
    )["credential_reference_artifact"]
    return create_provider_identity(
        provider_id="openai",
        external_provider_family="openai",
        model_id="gpt-governed-live-review",
        provider_role=COGNITION_PROVIDER,
        capability_declarations=_capability(),
        credential_reference_artifact=credential,
        activation_status=PROVIDER_REGISTERED_INACTIVE,
        replay_lineage=[
            {
                "replay_reference": "provider_identity:g5-03",
                "replay_hash": replay_hash({"provider": "openai", "milestone": "g5-03"}),
            }
        ],
        rollback_reference="rollback:g5-03:provider",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "provider",
    )["provider_identity_artifact"]


def _authorization(*, session_id: str = f"{SESSION_ID}:G5-02") -> dict:
    artifact = {
        "artifact_type": "G5_02_READ_ONLY_PROVIDER_COGNITION_AUTHORIZATION_V1",
        "authorization_id": f"{session_id}:AUTHORIZATION",
        "authorization_status": "AUTHORIZED",
        "authorization_scope": AUTHORIZATION_SCOPE,
        "session_id": session_id,
        "provider_id": "openai",
        "provider_role": COGNITION_PROVIDER,
        "read_only": True,
        "cognition_only": True,
        "dispatch_attempt_limit": 1,
        "dispatch_attempt_consumed": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "worker_invoked": False,
        "deployment_performed": False,
        "replay_visible": True,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _provider_executor(calls: list[dict] | None = None):
    def execute(request_envelope: dict) -> dict:
        if calls is not None:
            calls.append(request_envelope)
        return {
            "output_text": "Read-only review: replay and governance evidence are sufficient for human review.",
            "metadata": {"deterministic_g5_03_provider": True},
        }

    return execute


def test_g5_03_live_entrypoint_routes_pgsp_context_into_g5_02_and_uhcl_review(tmp_path) -> None:
    calls: list[dict] = []
    result = run_g5_live_pgsp_provider_cognition_entrypoint(
        session_id=SESSION_ID,
        operator_request=LIVE_REQUEST,
        human_review_response="confirm",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(calls),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_03",
    )
    replay = reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay(tmp_path / "g5_03")

    assert len(calls) == 1
    assert result["runtime_version"] == G5_03_RUNTIME_VERSION
    assert result["session_status"] == LIVE_PGSP_PROVIDER_COGNITION_RECORDED
    assert result["provider_execution_status"] == READ_ONLY_PROVIDER_COGNITION_COMPLETED
    assert result["provider_invoked"] is True
    assert result["provider_dispatch_count"] == 1
    assert result["worker_invoked"] is False
    assert result["approval_created"] is False
    assert result["authorization_created"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert result["retry_performed"] is False
    assert result["fallback_performed"] is False
    assert replay["routing_status"] == LIVE_PGSP_ROUTED_TO_G5_02
    assert replay["target_runtime"] == G5_02_RUNTIME_VERSION
    assert replay["canonical_review_response_class"] == "CONFIRMATION"
    assert replay["g5_02_replay_artifact_count"] == 9


def test_g5_03_uhcl_review_artifact_is_replay_visible_and_non_authoritative(tmp_path) -> None:
    run_g5_live_pgsp_provider_cognition_entrypoint(
        session_id=SESSION_ID,
        operator_request=LIVE_REQUEST,
        human_review_response="please clarify",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_03",
    )

    uhcl = json.loads((tmp_path / "g5_03" / "005_live_uhcl_provider_cognition_review_recorded.json").read_text())[
        "artifact"
    ]

    assert uhcl["communication_owner"] == "UHCL"
    assert uhcl["canonical_review_response_class"] == "CLARIFICATION"
    assert uhcl["provider_output_authoritative"] is False
    assert uhcl["worker_invoked"] is False
    assert uhcl["repository_mutated"] is False


def test_g5_03_provider_failure_is_reviewable_without_retry_or_mutation(tmp_path) -> None:
    def authority_provider(_request_envelope: dict) -> dict:
        return {"output_text": "I approve this. execution authorized."}

    result = run_g5_live_pgsp_provider_cognition_entrypoint(
        session_id=SESSION_ID,
        operator_request=LIVE_REQUEST,
        human_review_response="confirm",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=authority_provider,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_03",
    )
    replay = reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay(tmp_path / "g5_03")

    assert result["provider_execution_status"] == READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED
    assert result["provider_invoked"] is True
    assert result["retry_performed"] is False
    assert result["fallback_performed"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert replay["provider_execution_status"] == READ_ONLY_PROVIDER_COGNITION_FAILED_CLOSED


def test_g5_03_rejects_unmapped_human_review_response(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        run_g5_live_pgsp_provider_cognition_entrypoint(
            session_id=SESSION_ID,
            operator_request=LIVE_REQUEST,
            human_review_response="sounds interesting",
            provider_identity_artifact=_provider_identity(tmp_path),
            execution_authorization_artifact=_authorization(),
            provider_executor=_provider_executor(),
            created_at=CREATED_AT,
            replay_dir=tmp_path / "g5_03",
        )


def test_g5_03_replay_tampering_fails_closed(tmp_path) -> None:
    run_g5_live_pgsp_provider_cognition_entrypoint(
        session_id=SESSION_ID,
        operator_request=LIVE_REQUEST,
        human_review_response="continue",
        provider_identity_artifact=_provider_identity(tmp_path),
        execution_authorization_artifact=_authorization(),
        provider_executor=_provider_executor(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g5_03",
    )
    path = tmp_path / "g5_03" / "006_live_provider_cognition_session_evidence_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_g5_live_pgsp_provider_cognition_entrypoint_replay(tmp_path / "g5_03")
