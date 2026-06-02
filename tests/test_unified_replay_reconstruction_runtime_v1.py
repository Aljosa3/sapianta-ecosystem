"""Tests for UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable
from aigol.runtime.unified_replay_reconstruction_runtime import (
    FAILED_CLOSED,
    RECONSTRUCTED,
    UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1,
    reconstruct_chain_by_id,
    reconstruct_execution_lifecycle,
    reconstruct_full_lineage,
    reconstruct_latest_chain,
    reconstruct_learning_lifecycle,
    reconstruct_unified_replay_reconstruction_report,
)


CREATED_AT = "2026-06-02T10:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-UNIFIED-000001"


def _artifact(**values) -> dict:
    artifact = dict(values)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist(tmp_path, dirname: str, step: str, artifact: dict, *, index: int = 0) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": artifact.get("event_type") or step.upper(),
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(tmp_path / dirname / f"{index:03d}_{step}.json", wrapper)


def _chain(tmp_path, *, canonical_chain_id: str = CANONICAL_CHAIN_ID, suffix: str = "000001") -> dict[str, dict]:
    conversation = _artifact(
        event_type="CONVERSATION_RESPONSE_CREATED",
        conversation_id=f"CONVERSATION-{suffix}",
        canonical_chain_id=canonical_chain_id,
        created_at=CREATED_AT,
        replay_visible=True,
    )
    router = _artifact(
        artifact_type="SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1",
        router_id=f"ROUTER-{suffix}",
        canonical_chain_id=canonical_chain_id,
        created_at=CREATED_AT,
        selected_source="REPLAY",
        replay_visible=True,
    )
    approval = _artifact(
        artifact_type="IMPROVEMENT_APPROVAL_ARTIFACT_V1",
        improvement_approval_id=f"APPROVAL-{suffix}",
        canonical_chain_id=canonical_chain_id,
        created_at=CREATED_AT,
        replay_visible=True,
    )
    plan = _artifact(
        artifact_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_id=f"PLAN-{suffix}",
        canonical_chain_id=canonical_chain_id,
        improvement_approval_reference=approval["improvement_approval_id"],
        improvement_approval_hash=approval["artifact_hash"],
        created_at=CREATED_AT,
        replay_visible=True,
    )
    request = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id=f"REQUEST-{suffix}",
        canonical_chain_id=canonical_chain_id,
        implementation_plan_reference=plan["implementation_plan_id"],
        implementation_plan_hash=plan["artifact_hash"],
        improvement_approval_reference=approval["improvement_approval_id"],
        improvement_approval_hash=approval["artifact_hash"],
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        created_at=CREATED_AT,
        replay_visible=True,
    )
    bridge = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        bridge_id=f"BRIDGE-{suffix}",
        canonical_chain_id=canonical_chain_id,
        execution_request_reference=request["execution_request_id"],
        execution_request_hash=request["artifact_hash"],
        implementation_plan_reference=plan["implementation_plan_id"],
        implementation_plan_hash=plan["artifact_hash"],
        improvement_approval_reference=approval["improvement_approval_id"],
        improvement_approval_hash=approval["artifact_hash"],
        created_at=CREATED_AT,
        replay_visible=True,
    )
    worker = _artifact(
        artifact_type="WORKER_ARTIFACT_V1",
        worker_id=f"WORKER-{suffix}",
        canonical_chain_id=canonical_chain_id,
        created_at=CREATED_AT,
        replay_visible=True,
    )
    execution = _artifact(
        artifact_type="EXECUTION_ARTIFACT_V1",
        execution_id=f"EXECUTION-{suffix}",
        canonical_chain_id=canonical_chain_id,
        execution_request_reference=request["execution_request_id"],
        worker_reference=worker["worker_id"],
        worker_hash=worker["artifact_hash"],
        started_at=CREATED_AT,
        replay_visible=True,
    )
    artifacts = {
        "conversation": conversation,
        "router": router,
        "approval": approval,
        "plan": plan,
        "request": request,
        "bridge": bridge,
        "worker": worker,
        "execution": execution,
    }
    for index, (name, artifact) in enumerate(artifacts.items()):
        _persist(tmp_path, name, name, artifact, index=index)
    return artifacts


def test_chain_by_id_reconstructs_unified_report(tmp_path) -> None:
    _chain(tmp_path)

    report = reconstruct_chain_by_id(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=tmp_path,
        report_dir=tmp_path / "unified_report",
        created_at=CREATED_AT,
    )
    persisted = reconstruct_unified_replay_reconstruction_report(tmp_path / "unified_report")

    assert report["artifact_type"] == UNIFIED_REPLAY_RECONSTRUCTION_REPORT_V1
    assert report["reconstruction_status"] == RECONSTRUCTED
    assert report["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert report["conversation"]["present"] is True
    assert report["source_routing"]["present"] is True
    assert report["execution_lifecycle"]["present"] is True
    assert report["learning_lifecycle"]["present"] is True
    assert report["implementation_execution_bridge"]["present"] is True
    assert report["worker_evidence"]["present"] is True
    assert report["authority_boundary"]["execution_requests_created"] is False
    assert report["authority_boundary"]["workers_dispatched"] is False
    assert report["authority_boundary"]["workers_invoked"] is False
    assert persisted["report_id"] == report["report_id"]


def test_latest_chain_reconstructs_most_recent_chain(tmp_path) -> None:
    _chain(tmp_path, canonical_chain_id="CHAIN-OLDER", suffix="OLDER")
    latest = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id="REQUEST-LATEST",
        canonical_chain_id="CHAIN-LATEST",
        created_at="2026-06-02T11:00:00+00:00",
        replay_visible=True,
    )
    _persist(tmp_path, "latest", "latest", latest)

    report = reconstruct_latest_chain(
        replay_root=tmp_path,
        report_dir=tmp_path / "latest_report",
        created_at=CREATED_AT,
    )

    assert report["canonical_chain_id"] == "CHAIN-LATEST"


def test_lifecycle_specific_reconstruction_filters_sections(tmp_path) -> None:
    _chain(tmp_path)

    execution = reconstruct_execution_lifecycle(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=tmp_path,
        report_dir=tmp_path / "execution_report",
        created_at=CREATED_AT,
    )
    learning = reconstruct_learning_lifecycle(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=tmp_path,
        report_dir=tmp_path / "learning_report",
        created_at=CREATED_AT,
    )
    full = reconstruct_full_lineage(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=tmp_path,
        report_dir=tmp_path / "full_report",
        created_at=CREATED_AT,
    )

    assert execution["reconstruction_scope"] == "EXECUTION_LIFECYCLE"
    assert execution["execution_lifecycle"]["artifact_count"] >= 2
    assert learning["reconstruction_scope"] == "LEARNING_LIFECYCLE"
    assert learning["learning_lifecycle"]["artifact_count"] >= 2
    assert full["reconstruction_scope"] == "FULL_LINEAGE"
    assert full["replay_evidence"]["artifact_count"] >= 8


def test_reconstruction_detects_hash_mismatch_and_persists_failed_report(tmp_path) -> None:
    _chain(tmp_path)
    path = tmp_path / "execution" / "007_execution.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_chain_by_id(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=tmp_path,
            report_dir=tmp_path / "failed_report",
            created_at=CREATED_AT,
        )

    failed = reconstruct_unified_replay_reconstruction_report(tmp_path / "failed_report")
    assert failed["reconstruction_status"] == FAILED_CLOSED


def test_reconstruction_detects_invalid_references(tmp_path) -> None:
    _chain(tmp_path)
    path = tmp_path / "bridge" / "005_bridge.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_request_reference"] = "MISSING-REQUEST"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="invalid references"):
        reconstruct_full_lineage(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=tmp_path,
            report_dir=tmp_path / "invalid_reference_report",
            created_at=CREATED_AT,
        )


def test_reconstruction_detects_multiple_chain_ownership(tmp_path) -> None:
    _chain(tmp_path)
    duplicate = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id="REQUEST-000001",
        canonical_chain_id="CHAIN-OTHER",
        created_at=CREATED_AT,
        replay_visible=True,
    )
    _persist(tmp_path, "duplicate", "duplicate", duplicate)

    with pytest.raises(FailClosedRuntimeError, match="multiple chain ownership"):
        reconstruct_chain_by_id(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=tmp_path,
            report_dir=tmp_path / "ownership_report",
            created_at=CREATED_AT,
        )


def test_missing_chain_evidence_fails_closed(tmp_path) -> None:
    _chain(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="missing evidence"):
        reconstruct_chain_by_id(
            canonical_chain_id="CHAIN-MISSING",
            replay_root=tmp_path,
            report_dir=tmp_path / "missing_report",
            created_at=CREATED_AT,
        )


def test_runtime_is_read_only_and_does_not_invoke_workers_or_create_execution_requests() -> None:
    source = inspect.getsource(reconstruct_full_lineage)
    module_source = inspect.getsource(__import__("aigol.runtime.unified_replay_reconstruction_runtime").runtime.unified_replay_reconstruction_runtime)

    assert "create_execution_request(" not in module_source
    assert "dispatch_worker(" not in module_source
    assert "invoke_worker(" not in module_source
    assert "start_execution(" not in module_source
    assert "write_json_immutable" in module_source
    assert "reconstruct_full_lineage" in source
