"""Tests for AIGOL_WORKER_INVOCATION_TO_EXECUTION_CANDIDATE_BRIDGE_V1."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from aigol.runtime.external_worker_adapter_runtime import (
    EXTERNAL_WORKER_TASK_PACKAGE_CREATED,
    EXTERNAL_WORKER_TASK_PACKAGE_V1,
    create_external_worker_task_package,
)
from aigol.runtime.governed_implementation_request_runtime import APPROVED, HUMAN_APPROVAL_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import (
    APPROVAL_SCOPE,
    WORKER_EXECUTION_CANDIDATE_CREATED,
    bridge_worker_invocation_to_execution_candidate,
    reconstruct_worker_invocation_to_execution_candidate_bridge_replay,
)
from aigol.runtime.worker_invocation_to_execution_governance_runtime import (
    WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1,
)


CREATED_AT = "2026-06-12T00:00:00Z"


def _load_worker_invocation_helper():
    helper_path = Path(__file__).with_name("test_worker_invocation_runtime_v1.py")
    spec = importlib.util.spec_from_file_location("worker_invocation_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("worker invocation helper could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._invoke


_invoke = _load_worker_invocation_helper()


def _bridge_approval(invocation: dict, *, granted: bool = True) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-WORKER-INVOCATION-BRIDGE-000001",
        "approval_status": APPROVED if granted else "PENDING",
        "approval_granted": granted,
        "source_worker_invocation": invocation["worker_invocation_id"],
        "source_worker_invocation_hash": invocation["artifact_hash"],
        "approval_scope": APPROVAL_SCOPE,
        "worker_execution_allowed": False,
        "provider_invocation_allowed": False,
        "implementation_result_creation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _task_approval(execution_candidate: dict) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_id": "HUMAN-APPROVAL-WORKER-INVOCATION-TASK-000001",
        "approval_status": APPROVED,
        "approval_granted": True,
        "source_execution_candidate": execution_candidate["execution_candidate_id"],
        "source_execution_candidate_hash": execution_candidate["artifact_hash"],
        "approval_scope": "CREATE_EXTERNAL_WORKER_TASK_PACKAGE_ONLY",
        "external_worker_task_allowed": True,
        "implementation_result_creation_allowed": False,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capability(worker_interface: str = "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1") -> dict:
    return {
        "worker_interface": worker_interface,
        "worker_family": "REAL_PROVIDER_EXTERNAL_LLM_WORKER",
        "capabilities": [
            "EXECUTE_EXTERNAL_WORKER_TASK_PACKAGE_V1",
            "RETURN_EXTERNAL_WORKER_RESULT_PACKAGE_V1",
        ],
        "provider_neutral_contract": True,
    }


def test_domain_worker_invocation_becomes_external_worker_task_package(tmp_path) -> None:
    invocation_capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="external-task-package-bridge",
    )
    invocation = invocation_capture["worker_invocation_artifact"]
    bridge_capture = bridge_worker_invocation_to_execution_candidate(
        candidate_id="WORKER-EXECUTION-CANDIDATE-FROM-INVOCATION-000001",
        worker_invocation_artifact=invocation,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        human_approval_artifact=_bridge_approval(invocation),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_invocation_to_execution_candidate_bridge",
    )
    execution_candidate = bridge_capture["worker_execution_candidate_artifact"]
    reconstructed = reconstruct_worker_invocation_to_execution_candidate_bridge_replay(
        tmp_path / "worker_invocation_to_execution_candidate_bridge"
    )
    task_capture = create_external_worker_task_package(
        task_id="EXTERNAL-WORKER-TASK-FROM-DOMAIN-INVOCATION-000001",
        execution_candidate_artifact=execution_candidate,
        human_approval_artifact=_task_approval(execution_candidate),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "external_worker_task_package",
        worker_capability_declaration=_capability(),
    )
    task = task_capture["external_worker_task_package"]

    assert bridge_capture["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED
    assert bridge_capture["worker_invocation_accepted"] is True
    assert bridge_capture["worker_execution_candidate_generated"] is True
    assert bridge_capture["approval_boundary_preserved"] is True
    assert bridge_capture["execution_prevented"] is True
    assert execution_candidate["artifact_type"] == WORKER_EXECUTION_CANDIDATE_ARTIFACT_V1
    assert execution_candidate["source_worker_invocation"] == invocation["worker_invocation_id"]
    assert execution_candidate["source_worker_invocation_hash"] == invocation["artifact_hash"]
    assert execution_candidate["source_dispatch_candidate"] == invocation["worker_dispatch_reference"]
    assert execution_candidate["source_dispatch_candidate_hash"] == invocation["worker_dispatch_hash"]
    assert execution_candidate["worker_identity"]["worker_id"] == invocation["worker_id"]
    assert execution_candidate["implementation_result_created"] is False
    assert execution_candidate["provider_invoked"] is False
    assert execution_candidate["code_modified"] is False
    assert reconstructed["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED
    assert reconstructed["source_worker_invocation"] == invocation["worker_invocation_id"]
    assert reconstructed["replay_lineage_preserved"] is True
    assert task_capture["task_status"] == EXTERNAL_WORKER_TASK_PACKAGE_CREATED
    assert task_capture["task_package_generated"] is True
    assert task["artifact_type"] == EXTERNAL_WORKER_TASK_PACKAGE_V1
    assert task["source_execution_candidate"] == execution_candidate["execution_candidate_id"]
    assert task["source_execution_candidate_hash"] == execution_candidate["artifact_hash"]
    assert task["source_invocation_candidate"] == invocation["worker_invocation_id"]
    assert task["worker_authorization"]["authorized"] is True


def test_worker_invocation_bridge_resolves_repository_relative_dispatch_replay_reference(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    replay_root = (
        Path(".runtime")
        / "aicli"
        / "AICLI-REFERENCE-SESSION"
        / "TURN-000010"
        / "certified_development_continuation"
        / "worker_lifecycle_continuation"
    )
    invocation_capture = _invoke(
        replay_root,
        prompt="Create a filesystem worker.",
        suffix="repository-relative-dispatch",
    )
    invocation = invocation_capture["worker_invocation_artifact"]

    assert invocation_capture["worker_invocation_replay_reference"].startswith(".runtime/")

    bridge_capture = bridge_worker_invocation_to_execution_candidate(
        candidate_id="WORKER-EXECUTION-CANDIDATE-REPOSITORY-RELATIVE-DISPATCH-000001",
        worker_invocation_artifact=invocation,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        human_approval_artifact=_bridge_approval(invocation),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=replay_root / "worker_invocation_to_execution_candidate_bridge",
    )
    execution_candidate = bridge_capture["worker_execution_candidate_artifact"]

    assert bridge_capture["candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED
    assert bridge_capture["worker_execution_candidate_generated"] is True
    assert bridge_capture["replay_lineage_preserved"] is True
    assert execution_candidate["source_dispatch_candidate"] == invocation["worker_dispatch_reference"]
    assert execution_candidate["replay_references"]
    assert execution_candidate["replay_hashes"]


def test_worker_invocation_bridge_fails_closed_without_explicit_approval(tmp_path) -> None:
    invocation_capture = _invoke(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="external-task-package-approval-required",
    )
    invocation = invocation_capture["worker_invocation_artifact"]
    bridge_capture = bridge_worker_invocation_to_execution_candidate(
        candidate_id="WORKER-EXECUTION-CANDIDATE-FROM-INVOCATION-FAILED-000001",
        worker_invocation_artifact=invocation,
        worker_invocation_replay_reference=invocation_capture["worker_invocation_replay_reference"],
        human_approval_artifact=_bridge_approval(invocation, granted=False),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_invocation_to_execution_candidate_bridge_failed",
    )

    assert bridge_capture["candidate_status"] == "FAILED_CLOSED"
    assert bridge_capture["worker_invocation_accepted"] is False
    assert bridge_capture["worker_execution_candidate_generated"] is False
    assert bridge_capture["approval_boundary_preserved"] is True
    assert bridge_capture["execution_prevented"] is True
    assert "explicit human approval required" in bridge_capture["failure_reason"]
