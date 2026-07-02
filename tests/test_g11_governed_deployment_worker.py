"""Tests for G11-12 governed Deployment Worker."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_deployment_governance import (
    create_governed_deployment_authorization_record,
    register_governed_deployment_worker,
)
from aigol.runtime.transport.serialization import load_json
from aigol.runtime.worker_runtime import reconstruct_worker_registration_replay
from aigol.workers.deployment_worker import (
    ADAPTER_LOCAL_STATIC_COPY,
    AUTHORIZED_DEPLOYMENT_SCOPE,
    DEPLOYMENT_WORKER_ID,
    OPERATION_DEPLOYMENT_EXECUTION,
    OPERATION_DEPLOYMENT_PLANNING,
    OPERATION_DEPLOYMENT_STATUS_REPORTING,
    OPERATION_DEPLOYMENT_VERIFICATION,
    create_authorized_deployment_request,
    execute_deployment_request,
    reconstruct_deployment_worker_replay,
    validate_authorized_deployment_request,
)


CREATED_AT = "2026-07-02T00:00:00Z"


def _authorization() -> dict:
    return create_governed_deployment_authorization_record(
        authorization_id="G11-12-DEPLOYMENT-AUTHORIZATION",
        proposal_id="G11-12-DEPLOYMENT-PROPOSAL",
        authorization_timestamp=CREATED_AT,
    )


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    release = project / "release.txt"
    release.write_text("release-v1\n", encoding="utf-8")
    (project / "target").mkdir()
    return project


def _sha(path: Path) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _projection(*, release_hash: str, target_path: str = "target/current.txt") -> dict:
    return {
        "projection_owner": "Platform Digital Twin",
        "expected_deployment_state": {
            "release_artifact_fingerprint": release_hash,
            "target_path": target_path,
            "expected_services": ["static-artifact"],
            "expected_rollback_point": "rollback:deployment:previous-release",
        },
        "projection_authority": False,
    }


def _request(
    project: Path,
    *,
    operation: str,
    target_adapter: str = ADAPTER_LOCAL_STATIC_COPY,
    protected_environment: bool = False,
    protected_environment_authorized: bool = False,
    production_approval_reference: str | None = None,
    target_path: str = "target/current.txt",
) -> dict:
    release = project / "release.txt"
    release_hash = _sha(release)
    return create_authorized_deployment_request(
        authorization_record=_authorization(),
        request_id=f"G11-12-DEPLOYMENT-{operation}",
        operation=operation,
        deployment_id="TEMP-DEPLOYMENT",
        target_adapter=target_adapter,
        target_id="local-static-target",
        target_environment="demo",
        protected_environment=protected_environment,
        protected_environment_authorized=protected_environment_authorized,
        production_approval_reference=production_approval_reference,
        release_artifact_path="release.txt",
        release_artifact_fingerprint=release_hash,
        target_path=target_path,
        expected_active_release_fingerprint=None,
        deployment_strategy="replace-static-artifact",
        credential_reference="credential://deployment/local-none",
        git_remote_evidence_reference="replay:g11-08:git-remote",
        dependency_evidence_reference="replay:g11-10:dependency",
        validation_artifact_hash="validation-artifact-hash",
        validation_suite_reference="validation-suite:deployment-default",
        rollback_reference="rollback:deployment:previous-release",
        platform_digital_twin_projection=_projection(release_hash=release_hash, target_path=target_path),
        request_timestamp=CREATED_AT,
        proposal_reference={"proposal_id": "G11-12-DEPLOYMENT-PROPOSAL"},
        replay_reference="replay:g11-12:deployment",
    )


def test_deployment_worker_registers_through_worker_runtime(tmp_path):
    result = register_governed_deployment_worker(
        replay_dir=tmp_path / "registration",
        created_at=CREATED_AT,
    )
    reconstructed = reconstruct_worker_registration_replay(tmp_path / "registration")

    assert result["worker_artifact"]["worker_id"] == DEPLOYMENT_WORKER_ID
    assert reconstructed["worker_id"] == DEPLOYMENT_WORKER_ID
    assert reconstructed["governance_authority"] is False
    assert reconstructed["provider_authority"] is False
    assert reconstructed["execution_performed"] is False


def test_deployment_planning_records_replay_without_target_mutation(tmp_path):
    project = _project(tmp_path)
    request = _request(project, operation=OPERATION_DEPLOYMENT_PLANNING)

    capture = execute_deployment_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "plan-replay",
    )
    reconstructed = reconstruct_deployment_worker_replay(tmp_path / "plan-replay")

    assert capture["execution_status"] == "DEPLOYMENT_OPERATION_COMPLETED"
    assert capture["deployment_operation_performed"] is True
    assert capture["target_state_changed"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["platform_digital_twin_projection_consumed"] is True
    assert reconstructed["architectural_health_advisory_only"] is True
    assert not (project / "target" / "current.txt").exists()


def test_local_static_deployment_executes_exact_authorized_copy_with_replay(tmp_path):
    project = _project(tmp_path)
    request = _request(project, operation=OPERATION_DEPLOYMENT_EXECUTION)

    capture = execute_deployment_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "deploy-replay",
    )
    execution = load_json(tmp_path / "deploy-replay" / "002_deployment_worker_execution.json")["artifact"]

    assert capture["execution_status"] == "DEPLOYMENT_OPERATION_COMPLETED"
    assert capture["deployment_operation_performed"] is True
    assert capture["target_state_changed"] is True
    assert capture["worker_invoked"] is True
    assert (project / "target" / "current.txt").read_text(encoding="utf-8") == "release-v1\n"
    assert execution["platform_digital_twin_projection_consumed"] is True
    assert execution["validation_executed_by_worker"] is False
    assert execution["rollback_executed_by_worker"] is False
    assert execution["git_operation_performed"] is False
    assert execution["dependency_operation_performed"] is False
    assert execution["provider_invoked"] is False


def test_deployment_verification_observes_existing_target_without_orchestration(tmp_path):
    project = _project(tmp_path)
    (project / "target" / "current.txt").write_text("release-v1\n", encoding="utf-8")
    request = _request(project, operation=OPERATION_DEPLOYMENT_VERIFICATION)

    capture = execute_deployment_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "verify-replay",
    )
    execution = load_json(tmp_path / "verify-replay" / "002_deployment_worker_execution.json")["artifact"]

    assert capture["execution_status"] == "DEPLOYMENT_OPERATION_COMPLETED"
    assert capture["target_state_changed"] is False
    assert execution["orchestration_performed"] is False
    assert execution["validation_outcome"] == "VALIDATION_SEQUENCING_REQUIRED_BY_PLATFORM_CORE"


def test_deployment_status_reporting_does_not_mutate_target(tmp_path):
    project = _project(tmp_path)
    request = _request(project, operation=OPERATION_DEPLOYMENT_STATUS_REPORTING)

    capture = execute_deployment_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "status-replay",
    )

    assert capture["execution_status"] == "DEPLOYMENT_OPERATION_COMPLETED"
    assert capture["target_state_changed"] is False
    assert not (project / "target" / "current.txt").exists()


def test_deployment_request_rejects_forbidden_surfaces(tmp_path):
    project = _project(tmp_path)
    request = _request(project, operation=OPERATION_DEPLOYMENT_EXECUTION)
    request["shell_command"] = "deploy now"

    with pytest.raises(FailClosedRuntimeError, match="forbidden field"):
        validate_authorized_deployment_request(request)


def test_protected_environment_requires_explicit_authorization(tmp_path):
    project = _project(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="protected environment authorization required"):
        _request(project, operation=OPERATION_DEPLOYMENT_EXECUTION, protected_environment=True)


def test_protected_environment_requires_production_approval_reference(tmp_path):
    project = _project(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="production approval reference required"):
        _request(
            project,
            operation=OPERATION_DEPLOYMENT_EXECUTION,
            protected_environment=True,
            protected_environment_authorized=True,
        )


def test_deployment_authorization_uses_governance_scope():
    authorization = _authorization()

    assert authorization["worker_id"] == DEPLOYMENT_WORKER_ID
    assert authorization["authorization_scope"] == AUTHORIZED_DEPLOYMENT_SCOPE
    assert authorization["provider_can_authorize"] is False
    assert authorization["worker_can_self_authorize"] is False
