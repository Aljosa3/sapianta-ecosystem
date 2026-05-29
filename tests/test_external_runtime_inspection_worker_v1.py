"""Tests for FIRST_EXTERNAL_WORKER_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.external_runtime_inspection_worker import (
    EXECUTION_EVIDENCE_CAPTURED,
    EXECUTION_REQUEST_REFERENCED,
    EXTERNAL_RUNTIME_INSPECTION_WORKER,
    FAILED,
    TERMINATED,
    WORKER_IDENTITY_CAPTURED,
    WORKER_RESULT_CAPTURED,
    execute_external_runtime_inspection_worker,
    reconstruct_external_runtime_inspection_worker_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.read_only_capability_attachment import READ_ONLY_RUNTIME_INSPECTION
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-29T01:00:00+00:00"


def _provider() -> MetadataInspectionProvider:
    return MetadataInspectionProvider(timestamp_provider=lambda: CREATED_AT)


def _authorized_request(**overrides) -> dict:
    request = {
        "execution_id": "EXTERNAL-WORKER-EXECUTION-000001",
        "request_id": "EXTERNAL-WORKER-REQUEST-000001",
        "state": "AUTHORIZED",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "authorization_scope": "READ_ONLY_EXECUTION_BRIDGE",
        "authorization_hash": "sha256:authorized-by-aigol",
        "lineage_parent": "sha256:proposal-governed-by-aigol",
        "read_only": True,
        "filesystem_write_authority": False,
        "network_authority": False,
        "shell_authority": False,
        "api_authority": False,
        "orchestration_authority": False,
        "governance_authority": False,
        "worker_self_authorized": False,
        "hidden_continuation": False,
    }
    request.update(overrides)
    request["artifact_hash"] = replay_hash(request)
    return request


def _run(tmp_path, **overrides) -> dict:
    args = {
        "worker_attachment_id": "EXTERNAL-WORKER-ATTACHMENT-000001",
        "authorized_execution_request": _authorized_request(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path,
        "provider": _provider(),
    }
    args.update(overrides)
    return execute_external_runtime_inspection_worker(**args)


def test_external_worker_executes_authorized_read_only_inspection(tmp_path) -> None:
    capture = _run(tmp_path)
    replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path)

    assert capture["worker_identity"]["worker_identity"] == EXTERNAL_RUNTIME_INSPECTION_WORKER
    assert capture["execution_request_reference"]["worker_receives_authorized_request_only"] is True
    assert capture["execution_evidence"]["execution_evidence"]["operation"] == "inspect_runtime"
    assert capture["worker_result"]["final_worker_execution_status"] == "EXECUTED"
    assert capture["termination_record"]["final_status"] == TERMINATED
    assert replay["lifecycle_transitions"] == [
        WORKER_IDENTITY_CAPTURED,
        EXECUTION_REQUEST_REFERENCED,
        EXECUTION_EVIDENCE_CAPTURED,
        WORKER_RESULT_CAPTURED,
        TERMINATED,
    ]
    assert replay["worker_identity"] == EXTERNAL_RUNTIME_INSPECTION_WORKER
    assert replay["append_only_valid"] is True
    assert replay["read_only"] is True


def test_worker_receives_authorized_execution_request_only(tmp_path) -> None:
    capture = _run(tmp_path)
    reference = capture["execution_request_reference"]

    assert reference["direct_provider_to_worker_path"] is False
    assert reference["direct_human_to_worker_path"] is False
    assert reference["replay_bypass"] is False
    assert reference["authorized_execution_request"]["state"] == "AUTHORIZED"


def test_missing_authorization_fails_closed(tmp_path) -> None:
    request = _authorized_request(state="VALIDATED")
    capture = _run(tmp_path, authorized_execution_request=request)
    replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path)

    assert capture["termination_record"]["state"] == FAILED
    assert "authorized execution request" in capture["termination_record"]["failure_reason"]
    assert replay["final_status"] == FAILED
    assert replay["lifecycle_transitions"] == [
        WORKER_IDENTITY_CAPTURED,
        FAILED,
        FAILED,
        FAILED,
        FAILED,
    ]


def test_invalid_authorization_scope_fails_closed(tmp_path) -> None:
    request = _authorized_request(authorization_scope="UNTRUSTED_WORKER_SELF_AUTHORIZATION")
    capture = _run(tmp_path, authorized_execution_request=request)

    assert capture["termination_record"]["state"] == FAILED
    assert "authorization scope" in capture["termination_record"]["failure_reason"]


def test_identity_corruption_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, worker_id="CORRUPTED_WORKER")
    replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path)

    assert capture["termination_record"]["state"] == FAILED
    assert "identity corruption" in capture["termination_record"]["failure_reason"]
    assert replay["lifecycle_transitions"] == [FAILED, FAILED, FAILED, FAILED, FAILED]


def test_capability_mismatch_fails_closed(tmp_path) -> None:
    request = _authorized_request(target_capability="FILESYSTEM_READ_ONLY_INSPECTION")
    capture = _run(tmp_path, authorized_execution_request=request)

    assert capture["termination_record"]["state"] == FAILED
    assert "capability mismatch" in capture["termination_record"]["failure_reason"]


@pytest.mark.parametrize(
    "field",
    [
        "filesystem_write_authority",
        "network_authority",
        "shell_authority",
        "api_authority",
        "orchestration_authority",
        "governance_authority",
        "worker_self_authorized",
        "hidden_continuation",
    ],
)
def test_boundary_violations_fail_closed(tmp_path, field: str) -> None:
    request = _authorized_request(**{field: True})
    capture = _run(tmp_path, authorized_execution_request=request)

    assert capture["termination_record"]["state"] == FAILED
    assert "boundary violation" in capture["termination_record"]["failure_reason"]


def test_unexpected_mutation_attempt_fails_closed(tmp_path) -> None:
    request = _authorized_request(requested_operation="write runtime metadata")
    capture = _run(tmp_path, authorized_execution_request=request)

    assert capture["termination_record"]["state"] == FAILED
    assert "boundary violation" in capture["termination_record"]["failure_reason"]


def test_replay_reconstruction_detects_mutation(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "002_execution_evidence.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["write_performed"] = True
    artifact_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_external_runtime_inspection_worker_replay(tmp_path)


def test_replay_ordering_corruption_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "001_execution_request_reference.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "worker_result"
    artifact_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_external_runtime_inspection_worker_replay(tmp_path)


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    _run(tmp_path)
    second = _run(tmp_path)

    assert second["termination_record"]["state"] == FAILED
    assert "already exists" in second["termination_record"]["failure_reason"]


def test_repeated_successful_runs_are_deterministic(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(tmp_path / "second")

    assert first == second


def test_repeated_failed_runs_are_reconstructable(tmp_path) -> None:
    for index in range(5):
        request = _authorized_request(state="VALIDATED")
        capture = _run(tmp_path / f"failed-{index}", authorized_execution_request=request)
        replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path / f"failed-{index}")

        assert capture["termination_record"]["state"] == FAILED
        assert replay["final_status"] == FAILED


def test_mixed_operation_sequences_remain_bounded(tmp_path) -> None:
    statuses = []
    for index in range(6):
        if index % 2 == 0:
            capture = _run(tmp_path / f"success-{index}")
        else:
            request = _authorized_request(target_capability="NETWORK_QUERY")
            capture = _run(tmp_path / f"failed-{index}", authorized_execution_request=request)
        statuses.append(capture["termination_record"]["final_status"])

    assert statuses == [TERMINATED, FAILED, TERMINATED, FAILED, TERMINATED, FAILED]


def test_external_worker_source_has_no_mutating_runtime_imports() -> None:
    import aigol.runtime.external_runtime_inspection_worker as worker

    source = inspect.getsource(worker)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
