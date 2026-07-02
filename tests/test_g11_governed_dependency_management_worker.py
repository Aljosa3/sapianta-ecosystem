"""Tests for G11-10 governed Dependency Management Worker."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_dependency_governance import (
    create_governed_dependency_management_authorization_record,
    register_governed_dependency_management_worker,
)
from aigol.runtime.transport.serialization import load_json
from aigol.runtime.worker_runtime import reconstruct_worker_registration_replay
from aigol.workers.dependency_management_worker import (
    AUTHORIZED_DEPENDENCY_SCOPE,
    DEPENDENCY_WORKER_ID,
    OPERATION_DEPENDENCY_INSTALL,
    OPERATION_DEPENDENCY_INSPECTION,
    OPERATION_DEPENDENCY_VERIFICATION,
    OPERATION_LOCK_SYNCHRONIZATION,
    create_authorized_dependency_management_request,
    execute_dependency_management_request,
    reconstruct_dependency_management_worker_replay,
    validate_authorized_dependency_management_request,
)


CREATED_AT = "2026-07-02T00:00:00Z"


def _authorization() -> dict:
    return create_governed_dependency_management_authorization_record(
        authorization_id="G11-10-DEPENDENCY-AUTHORIZATION",
        proposal_id="G11-10-DEPENDENCY-PROPOSAL",
        authorization_timestamp=CREATED_AT,
    )


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "package.json").write_text('{"dependencies":{}}\n', encoding="utf-8")
    (project / "package-lock.json").write_text('{"lockfileVersion":3}\n', encoding="utf-8")
    return project


def _request(
    *,
    operation: str,
    package_manager: str = "npm",
    dependency_name: str | None = "left-pad",
    protected_dependency: bool = False,
    protected_dependency_authorized: bool = False,
    registry_private: bool = False,
    private_registry_authorized: bool = False,
) -> dict:
    return create_authorized_dependency_management_request(
        authorization_record=_authorization(),
        request_id=f"G11-10-DEPENDENCY-{operation}",
        operation=operation,
        project_id="TEMP-DEPENDENCY-PROJECT",
        package_manager=package_manager,
        project_root=".",
        manifest_paths=["package.json"],
        lockfile_paths=["package-lock.json"],
        dependency_name=dependency_name,
        dependency_version="1.3.0" if dependency_name else None,
        version_constraint=None,
        registry_url="https://registry.npmjs.org",
        registry_private=registry_private,
        private_registry_authorized=private_registry_authorized,
        credential_reference="credential://dependency/npm/public",
        protected_dependency=protected_dependency,
        protected_dependency_authorized=protected_dependency_authorized,
        package_policy_reference="policy://dependency/default",
        validation_artifact_hash="validation-artifact-hash",
        validation_suite_reference="validation-suite:dependency-default",
        rollback_reference="rollback:dependency:manifest-lockfile",
        request_timestamp=CREATED_AT,
        proposal_reference={"proposal_id": "G11-10-DEPENDENCY-PROPOSAL"},
        replay_reference="replay:g11-10:dependency",
    )


def _fake_npm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    npm = bin_dir / "npm"
    npm.write_text(
        "#!/usr/bin/env sh\n"
        "if [ \"$1\" = \"--version\" ]; then echo '9.9.9-test'; exit 0; fi\n"
        "if [ \"$1\" = \"install\" ]; then printf '\\n// fake npm install\\n' >> package-lock.json; exit 0; fi\n"
        "if [ \"$1\" = \"ls\" ]; then echo '{\"dependencies\":{}}'; exit 0; fi\n"
        "echo fake npm invoked\n"
        "exit 0\n",
        encoding="utf-8",
    )
    npm.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")


def test_dependency_worker_registers_through_worker_runtime(tmp_path):
    result = register_governed_dependency_management_worker(
        replay_dir=tmp_path / "registration",
        created_at=CREATED_AT,
    )
    reconstructed = reconstruct_worker_registration_replay(tmp_path / "registration")

    assert result["worker_artifact"]["worker_id"] == DEPENDENCY_WORKER_ID
    assert reconstructed["worker_id"] == DEPENDENCY_WORKER_ID
    assert reconstructed["governance_authority"] is False
    assert reconstructed["provider_authority"] is False
    assert reconstructed["execution_performed"] is False


def test_dependency_inspection_records_replay_without_package_manager_execution(tmp_path):
    project = _project(tmp_path)
    request = _request(operation=OPERATION_DEPENDENCY_INSPECTION, dependency_name=None)

    capture = execute_dependency_management_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_dependency_management_worker_replay(tmp_path / "replay")

    assert capture["execution_status"] == "DEPENDENCY_OPERATION_COMPLETED"
    assert capture["dependency_operation_performed"] is True
    assert capture["worker_invoked"] is False
    assert reconstructed["operation"] == OPERATION_DEPENDENCY_INSPECTION
    assert reconstructed["architectural_health_advisory_only"] is True


def test_dependency_install_uses_adapter_and_records_changed_lockfile(tmp_path, monkeypatch):
    project = _project(tmp_path)
    _fake_npm(tmp_path, monkeypatch)
    request = _request(operation=OPERATION_DEPENDENCY_INSTALL)

    capture = execute_dependency_management_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "install-replay",
    )
    execution = load_json(tmp_path / "install-replay" / "002_dependency_worker_execution.json")["artifact"]

    assert capture["execution_status"] == "DEPENDENCY_OPERATION_COMPLETED"
    assert capture["dependency_operation_performed"] is True
    assert capture["worker_invoked"] is True
    assert execution["argv"] == ["npm", "install", "--ignore-scripts", "left-pad@1.3.0"]
    assert execution["repository_files_changed"] is True
    assert execution["changed_paths"] == ["package-lock.json"]
    assert execution["validation_executed_by_worker"] is False
    assert execution["rollback_executed_by_worker"] is False
    assert execution["provider_invoked"] is False
    assert execution["git_operation_performed"] is False
    assert execution["architectural_health_advisory_input"]["advisory_only"] is True


def test_dependency_lock_synchronization_uses_package_manager_adapter(tmp_path, monkeypatch):
    project = _project(tmp_path)
    _fake_npm(tmp_path, monkeypatch)
    request = _request(operation=OPERATION_LOCK_SYNCHRONIZATION, dependency_name=None)

    capture = execute_dependency_management_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "lock-replay",
    )
    execution = load_json(tmp_path / "lock-replay" / "002_dependency_worker_execution.json")["artifact"]

    assert capture["execution_status"] == "DEPENDENCY_OPERATION_COMPLETED"
    assert execution["argv"] == ["npm", "install", "--package-lock-only", "--ignore-scripts"]


def test_dependency_verification_remains_worker_execution_only(tmp_path, monkeypatch):
    project = _project(tmp_path)
    _fake_npm(tmp_path, monkeypatch)
    request = _request(operation=OPERATION_DEPENDENCY_VERIFICATION, dependency_name=None)

    capture = execute_dependency_management_request(
        authorized_request=request,
        repository_root=project,
        replay_dir=tmp_path / "verify-replay",
    )
    execution = load_json(tmp_path / "verify-replay" / "002_dependency_worker_execution.json")["artifact"]

    assert capture["execution_status"] == "DEPENDENCY_OPERATION_COMPLETED"
    assert execution["argv"] == ["npm", "ls", "--json", "--depth=0"]
    assert execution["validation_outcome"] == "VALIDATION_SEQUENCING_REQUIRED_BY_PLATFORM_CORE"
    assert execution["orchestration_performed"] is False


def test_dependency_request_rejects_forbidden_execution_surfaces():
    request = _request(operation=OPERATION_DEPENDENCY_INSTALL)
    request["shell_command"] = "npm install left-pad"

    with pytest.raises(FailClosedRuntimeError, match="forbidden field"):
        validate_authorized_dependency_management_request(request)


def test_dependency_private_registry_requires_explicit_authorization():
    with pytest.raises(FailClosedRuntimeError, match="private registry authorization required"):
        _request(
            operation=OPERATION_DEPENDENCY_INSTALL,
            registry_private=True,
            private_registry_authorized=False,
        )


def test_dependency_protected_package_requires_explicit_authorization():
    with pytest.raises(FailClosedRuntimeError, match="protected dependency authorization required"):
        _request(
            operation=OPERATION_DEPENDENCY_INSTALL,
            protected_dependency=True,
            protected_dependency_authorized=False,
        )


def test_dependency_authorization_uses_governance_scope():
    authorization = _authorization()

    assert authorization["worker_id"] == DEPENDENCY_WORKER_ID
    assert authorization["authorization_scope"] == AUTHORIZED_DEPENDENCY_SCOPE
    assert authorization["provider_can_authorize"] is False
    assert authorization["worker_can_self_authorize"] is False
