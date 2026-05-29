"""Tests for SECOND_READ_ONLY_CAPABILITY_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.filesystem_read_only_capability import (
    AUTHORIZED,
    EXECUTED,
    FAILED,
    FILESYSTEM_READ_ONLY_INSPECTION,
    REQUESTED,
    TERMINATED,
    VALIDATED,
    authorize_filesystem_read_only_capability,
    create_filesystem_read_only_request,
    execute_filesystem_read_only_capability,
    reconstruct_filesystem_read_only_replay,
    validate_filesystem_read_only_request,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-29T02:00:00+00:00"


def _fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    denied = root / "denied"
    allowed.mkdir(parents=True)
    denied.mkdir()
    target = allowed / "visible.txt"
    target.write_text("bounded visible content", encoding="utf-8")
    secret = denied / "secret.txt"
    secret.write_text("not allowed", encoding="utf-8")
    return root, allowed, target, secret


def _run(tmp_path, *, requested_path=None, allowed_paths=None, authorize=True, capability_id=FILESYSTEM_READ_ONLY_INSPECTION):
    root, allowed, target, _secret = _fixture(tmp_path)
    return execute_filesystem_read_only_capability(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
        root_path=root,
        requested_path=requested_path or target,
        allowed_paths=allowed_paths if allowed_paths is not None else [allowed],
        capability_id=capability_id,
        authorize=authorize,
    )


def test_filesystem_read_only_file_inspection_executes(tmp_path) -> None:
    capture = _run(tmp_path)
    replay = reconstruct_filesystem_read_only_replay(tmp_path / "replay")

    assert capture["termination"]["state"] == TERMINATED
    assert capture["execution"]["capability_id"] == FILESYSTEM_READ_ONLY_INSPECTION
    assert capture["execution"]["read_only"] is True
    assert capture["execution"]["write_performed"] is False
    assert capture["execution"]["execution_evidence"]["metadata"]["text_preview"] == "bounded visible content"
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]
    assert replay["final_status"] == TERMINATED


def test_filesystem_read_only_directory_listing_executes(tmp_path) -> None:
    root, allowed, _target, _secret = _fixture(tmp_path)
    capture = execute_filesystem_read_only_capability(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
        root_path=root,
        requested_path=allowed,
        allowed_paths=[allowed],
    )

    assert capture["execution"]["execution_evidence"]["metadata"]["is_dir"] is True
    assert capture["execution"]["execution_evidence"]["metadata"]["entries"] == ["visible.txt"]


def test_execution_outcome_contains_required_evidence(tmp_path) -> None:
    capture = _run(tmp_path)
    execution = capture["execution"]

    assert execution["execution_id"] == "FS-READONLY-EXECUTION-000001"
    assert execution["capability_id"] == FILESYSTEM_READ_ONLY_INSPECTION
    assert execution["authorization_hash"] == capture["authorization"]["artifact_hash"]
    assert execution["execution_evidence_hash"] == execution["execution_evidence"]["evidence_hash"]
    assert execution["final_status"] == EXECUTED


def test_unauthorized_execution_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, authorize=False)
    replay = reconstruct_filesystem_read_only_replay(tmp_path / "replay")

    assert capture["termination"]["state"] == FAILED
    assert "authorization missing" in capture["termination"]["failure_reason"]
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, FAILED, FAILED, FAILED]


def test_forbidden_path_access_fails_closed(tmp_path) -> None:
    root, allowed, _target, secret = _fixture(tmp_path)
    capture = execute_filesystem_read_only_capability(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
        root_path=root,
        requested_path=secret,
        allowed_paths=[allowed],
    )

    assert capture["termination"]["state"] == FAILED
    assert "forbidden filesystem path access" in capture["termination"]["failure_reason"]


def test_path_outside_root_fails_closed(tmp_path) -> None:
    root, allowed, _target, _secret = _fixture(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    capture = execute_filesystem_read_only_capability(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
        root_path=root,
        requested_path=outside,
        allowed_paths=[allowed],
    )

    assert capture["termination"]["state"] == FAILED
    assert "path ambiguity" in capture["termination"]["failure_reason"]


def test_invalid_capability_classification_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, capability_id="FILESYSTEM_WRITE")

    assert capture["termination"]["state"] == FAILED
    assert "invalid filesystem capability classification" in capture["termination"]["failure_reason"]


def test_boundary_mutation_flag_fails_closed(tmp_path) -> None:
    root, allowed, target, _secret = _fixture(tmp_path)
    request = create_filesystem_read_only_request(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        capability_id=FILESYSTEM_READ_ONLY_INSPECTION,
        created_at=CREATED_AT,
        root_path=root,
        requested_path=target,
        allowed_paths=[allowed],
    )
    request["write"] = True
    without_hash = dict(request)
    without_hash.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(without_hash)

    with pytest.raises(FailClosedRuntimeError, match="boundary violation"):
        validate_filesystem_read_only_request(request)


def test_authorization_requires_validated_state(tmp_path) -> None:
    root, allowed, target, _secret = _fixture(tmp_path)
    request = create_filesystem_read_only_request(
        execution_id="FS-READONLY-EXECUTION-000001",
        request_id="FS-READONLY-REQUEST-000001",
        capability_id=FILESYSTEM_READ_ONLY_INSPECTION,
        created_at=CREATED_AT,
        root_path=root,
        requested_path=target,
        allowed_paths=[allowed],
    )

    with pytest.raises(FailClosedRuntimeError, match="VALIDATED"):
        authorize_filesystem_read_only_capability(request)


def test_replay_artifacts_are_append_only(tmp_path) -> None:
    _run(tmp_path)

    root = tmp_path / "root"
    allowed = root / "allowed"
    target = allowed / "visible.txt"
    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        execute_filesystem_read_only_capability(
            execution_id="FS-READONLY-EXECUTION-000001",
            request_id="FS-READONLY-REQUEST-000001",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "replay",
            root_path=root,
            requested_path=target,
            allowed_paths=[allowed],
        )


def test_replay_discontinuity_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "replay" / "003_execution.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["write_performed"] = True
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_filesystem_read_only_replay(tmp_path / "replay")


def test_replay_ordering_corruption_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "replay" / "002_authorization.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "execution"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_filesystem_read_only_replay(tmp_path / "replay")


def test_runtime_artifacts_are_deterministic(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(tmp_path / "second")

    assert first["request"]["capability_id"] == second["request"]["capability_id"]
    assert first["request"]["classification"] == second["request"]["classification"]
    assert first["validation"]["capability_classification"] == second["validation"]["capability_classification"]
    assert first["authorization"]["authorization_scope"] == second["authorization"]["authorization_scope"]
    assert first["execution"]["execution_evidence"]["metadata"]["text_preview"] == second["execution"]["execution_evidence"]["metadata"]["text_preview"]
    assert first["termination"]["final_status"] == second["termination"]["final_status"]


def test_no_mutating_runtime_imports() -> None:
    import aigol.runtime.filesystem_read_only_capability as capability

    source = inspect.getsource(capability)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
