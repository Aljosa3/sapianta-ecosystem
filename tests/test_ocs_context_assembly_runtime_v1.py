"""Tests for AIGOL_OCS_CONTEXT_ASSEMBLY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
    assemble_ocs_context,
    reconstruct_ocs_context_assembly_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-04T12:00:00+00:00"


def _artifact(artifact_type: str, artifact_id: str, **extra: object) -> dict:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "replay_visible": True,
        "authority": False,
        **extra,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _source_context() -> dict:
    conversation = _artifact(
        "CONVERSATION_RESPONSE_ARTIFACT_V1",
        "CONVERSATION-000001",
        context_status="CONVERSATION_READY",
    )
    return {
        "conversation_context": [
            conversation,
            dict(conversation),
        ],
        "clarification_context": [
            _artifact("HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1", "CLARIFICATION-000001")
        ],
        "ppp_context": [
            _artifact(
                "RESOURCE_PPP_INTEGRATION_ARTIFACT_V1",
                "PPP-000001",
                ppp_resource_status="PPP_PROVIDER_PROPOSAL_READY",
            )
        ],
        "approval_context": [
            _artifact("HUMAN_DECISION_ARTIFACT_V1", "HUMAN-DECISION-000001", decision_status="APPROVED")
        ],
        "replay_visible_operation_context": [
            _artifact("UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1", "REPLAY-000001", status="READY")
        ],
        "domain_context": [
            _artifact("DOMAIN_FOUNDATION_ARTIFACT_V1", "TRADING-DOMAIN-000001", domain_id="TRADING")
        ],
        "registry_context": [
            _artifact(
                "DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1",
                "REGISTRY-000001",
                domain_id="TRADING",
                resolution_status="DOMAIN_BUNDLE_RESOLVED",
            )
        ],
    }


def test_ocs_context_assembly_builds_reconstructable_context(tmp_path) -> None:
    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs",
        source_context=_source_context(),
        source_chain_id="CHAIN-000001",
        source_request_reference="PROMPT-000001",
    )
    reconstructed = reconstruct_ocs_context_assembly_replay(tmp_path / "ocs")
    artifact = capture["ocs_context_assembly_artifact"]

    assert artifact["artifact_type"] == OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1
    assert capture["context_status"] == OCS_CONTEXT_ASSEMBLED
    assert capture["accepted_input_count"] == 7
    assert capture["deduplicated_input_count"] == 1
    assert capture["rejected_input_count"] == 1
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert capture["governance_modified"] is False
    assert capture["replay_modified"] is False
    assert artifact["authority_flags"]["authorizes_execution"] is False
    assert reconstructed["context_status"] == OCS_CONTEXT_ASSEMBLED
    assert reconstructed["context_hash"] == capture["context_hash"]
    assert reconstructed["accepted_input_count"] == 7
    assert reconstructed["deduplicated_input_count"] == 1
    assert reconstructed["replay_artifact_count"] == 2


def test_ocs_context_assembly_is_deterministic_for_same_sources(tmp_path) -> None:
    first = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-DETERMINISTIC-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "first",
        source_context=_source_context(),
        source_chain_id="CHAIN-000001",
        source_request_reference="PROMPT-000001",
    )
    shuffled = _source_context()
    shuffled["conversation_context"] = list(reversed(shuffled["conversation_context"]))
    second = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-DETERMINISTIC-000002",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "second",
        source_context=shuffled,
        source_chain_id="CHAIN-000001",
        source_request_reference="PROMPT-000001",
    )

    assert first["context_hash"] == second["context_hash"]
    assert reconstruct_ocs_context_assembly_replay(tmp_path / "first")["context_hash"] == first["context_hash"]
    assert reconstruct_ocs_context_assembly_replay(tmp_path / "second")["context_hash"] == second["context_hash"]


def test_ocs_context_assembly_fails_closed_on_non_replay_visible_source(tmp_path) -> None:
    source_context = _source_context()
    source_context["conversation_context"][0]["replay_visible"] = False
    source_context["conversation_context"][0]["artifact_hash"] = replay_hash(
        {key: value for key, value in source_context["conversation_context"][0].items() if key != "artifact_hash"}
    )

    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-NON-REPLAY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "non_replay",
        source_context=source_context,
    )

    assert capture["fail_closed"] is True
    assert capture["context_status"] == "FAILED_CLOSED"
    assert "source item is not replay-visible" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_ocs_context_assembly_fails_closed_on_authority_bearing_source(tmp_path) -> None:
    source_context = _source_context()
    source_context["ppp_context"][0]["authorizes_execution"] = True
    source_context["ppp_context"][0]["artifact_hash"] = replay_hash(
        {key: value for key, value in source_context["ppp_context"][0].items() if key != "artifact_hash"}
    )

    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-AUTHORITY-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "authority",
        source_context=source_context,
    )

    assert capture["fail_closed"] is True
    assert capture["context_status"] == "FAILED_CLOSED"
    assert "prohibited OCS authority flag" in capture["failure_reason"]
    assert capture["execution_requested"] is False


def test_ocs_context_assembly_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-CORRUPT-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
        source_context=_source_context(),
    )
    path = tmp_path / "corrupt" / "000_ocs_context_assembly_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["context_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ocs_context_assembly_replay(tmp_path / "corrupt")


def test_ocs_context_assembly_preserves_authority_boundaries() -> None:
    import aigol.runtime.ocs_context_assembly_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
