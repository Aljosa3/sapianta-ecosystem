"""Tests for G3 ACLI development session lifecycle phase 1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.acli_development_session_lifecycle import (
    ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1,
    CONFIRMATION_RECORDED,
    CONFIRMATION_REQUIRED,
    RECOVERY_REQUIRED,
    SESSION_CREATED,
    create_acli_development_session,
    record_acli_session_recovery_state,
    record_human_confirmation_checkpoint,
    reconstruct_acli_development_session_lifecycle_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-28T00:00:00Z"
RECORDED_AT = "2026-06-28T00:01:00Z"


def _governance_checkpoints() -> dict:
    return {
        "semantic_authority_preserved": True,
        "governance_authority_preserved": True,
        "approval_boundary_preserved": True,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "replay_boundary_preserved": True,
        "execution_boundary_preserved": True,
    }


def _replay_lineage() -> list[dict]:
    return [
        {
            "replay_reference": "runtime/g3/session/source/000_csa_recorded.json",
            "replay_hash": replay_hash({"source": "csa"}),
        }
    ]


def _session(tmp_path):
    return create_acli_development_session(
        session_id="ACLI-G3-SESSION-000001",
        parent_session_id="ACLI-G2-PARENT-000001",
        canonical_semantic_artifact_reference="CSA-G3-000001",
        canonical_semantic_artifact_hash=replay_hash({"csa": "G3-000001"}),
        replay_lineage=_replay_lineage(),
        governance_checkpoints=_governance_checkpoints(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "session",
    )


def test_creates_acli_development_session_with_csa_and_replay_lineage(tmp_path) -> None:
    capture = _session(tmp_path)
    artifact = capture["session_artifact"]
    reconstructed = reconstruct_acli_development_session_lifecycle_replay(tmp_path / "session")

    assert artifact["artifact_type"] == ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1
    assert artifact["session_id"] == "ACLI-G3-SESSION-000001"
    assert artifact["parent_session_id"] == "ACLI-G2-PARENT-000001"
    assert artifact["canonical_semantic_artifact_reference"] == "CSA-G3-000001"
    assert artifact["canonical_semantic_artifact_hash"].startswith("sha256:")
    assert artifact["replay_lineage"] == _replay_lineage()
    assert artifact["lifecycle_status"] == SESSION_CREATED
    assert artifact["confirmation_state"] == "NO_CONFIRMATION_REQUIRED"
    assert artifact["recovery_status"] == "NO_RECOVERY_REQUIRED"
    assert artifact["session_identity_preserved"] is True
    assert artifact["replay_lineage_preserved"] is True
    assert artifact["governance_checkpoints_preserved"] is True
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False
    assert artifact["repository_mutated"] is False
    assert reconstructed["session_id"] == artifact["session_id"]
    assert reconstructed["event_count"] == 1
    assert reconstructed["replay_visible"] is True


def test_records_human_confirmation_checkpoint_without_approval_authority(tmp_path) -> None:
    created = _session(tmp_path)
    capture = record_human_confirmation_checkpoint(
        session_artifact=created["session_artifact"],
        checkpoint_id="CONFIRMATION-000001",
        confirmation_class="PROPOSAL_APPROVAL",
        confirmation_status=CONFIRMATION_REQUIRED,
        active_context_reference="PROPOSAL-000001",
        proposal_reference="PROPOSAL-000001",
        approval_scope="docs/governance/example.md",
        confirmation_text_hash=replay_hash({"confirmation": "approve proposal"}),
        recorded_at=RECORDED_AT,
        replay_dir=tmp_path / "session",
    )
    artifact = capture["session_artifact"]
    checkpoint = artifact["confirmation_checkpoints"][0]
    reconstructed = reconstruct_acli_development_session_lifecycle_replay(tmp_path / "session")

    assert artifact["lifecycle_status"] == CONFIRMATION_REQUIRED
    assert artifact["confirmation_state"] == CONFIRMATION_REQUIRED
    assert artifact["confirmation_checkpoint_visible"] is True
    assert checkpoint["confirmation_class"] == "PROPOSAL_APPROVAL"
    assert checkpoint["approval_created"] is False
    assert checkpoint["authorization_created"] is False
    assert checkpoint["execution_requested"] is False
    assert reconstructed["event_count"] == 2
    assert reconstructed["confirmation_state"] == CONFIRMATION_REQUIRED


def test_records_recovery_state_without_provider_worker_or_execution(tmp_path) -> None:
    created = _session(tmp_path)
    capture = record_acli_session_recovery_state(
        session_artifact=created["session_artifact"],
        recovery_id="RECOVERY-000001",
        recovery_status=RECOVERY_REQUIRED,
        recovery_reason="missing repository context",
        safe_next_action="ask user for target repository path",
        recorded_at=RECORDED_AT,
        replay_dir=tmp_path / "session",
    )
    artifact = capture["session_artifact"]
    recovery = artifact["recovery_states"][0]

    assert artifact["lifecycle_status"] == RECOVERY_REQUIRED
    assert artifact["recovery_status"] == RECOVERY_REQUIRED
    assert artifact["recovery_state_visible"] is True
    assert recovery["recovery_reason"] == "missing repository context"
    assert recovery["safe_next_action"] == "ask user for target repository path"
    assert recovery["provider_invoked"] is False
    assert recovery["worker_invoked"] is False
    assert recovery["execution_requested"] is False


def test_records_confirmation_recorded_as_non_authoritative_checkpoint(tmp_path) -> None:
    created = _session(tmp_path)
    capture = record_human_confirmation_checkpoint(
        session_artifact=created["session_artifact"],
        checkpoint_id="CONFIRMATION-RECORDED-000001",
        confirmation_class="ADVISORY_CONFIRMATION",
        confirmation_status=CONFIRMATION_RECORDED,
        active_context_reference="ADVISORY-000001",
        confirmation_text_hash=replay_hash({"confirmation": "sounds good"}),
        recorded_at=RECORDED_AT,
        replay_dir=tmp_path / "session",
    )

    assert capture["session_artifact"]["lifecycle_status"] == CONFIRMATION_RECORDED
    assert capture["session_artifact"]["approval_created"] is False
    assert capture["session_artifact"]["authorization_created"] is False


def test_missing_governance_checkpoint_fails_closed(tmp_path) -> None:
    checkpoints = _governance_checkpoints()
    checkpoints["worker_boundary_preserved"] = False

    with pytest.raises(FailClosedRuntimeError, match="worker_boundary_preserved"):
        create_acli_development_session(
            session_id="ACLI-G3-SESSION-BROKEN",
            canonical_semantic_artifact_reference="CSA-G3-BROKEN",
            canonical_semantic_artifact_hash=replay_hash({"csa": "broken"}),
            replay_lineage=_replay_lineage(),
            governance_checkpoints=checkpoints,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "broken",
        )


def test_tampered_session_replay_fails_closed(tmp_path) -> None:
    _session(tmp_path)
    path = tmp_path / "session" / "000_acli_development_session_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_acli_development_session_lifecycle_replay(tmp_path / "session")


def test_runtime_has_no_provider_worker_execution_or_deployment_surfaces() -> None:
    import aigol.runtime.acli_development_session_lifecycle as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
    assert "deploy(" not in source
    assert "write_text(" not in source
