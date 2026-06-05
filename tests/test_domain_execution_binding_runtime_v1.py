"""Tests for AIGOL_DOMAIN_EXECUTION_BINDING_V1."""

from __future__ import annotations

import inspect
import json

from aigol.provider.provider_registry import ProviderRegistry
import pytest

from aigol.runtime.domain_execution_binding_runtime import (
    AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION,
    DEFAULT_OUTPUT_CONTENT,
    DEFAULT_OUTPUT_FILE,
    DOMAIN_EXECUTION_AUTHORIZED,
    DOMAIN_EXECUTION_COMPLETED,
    DOMAIN_EXECUTION_COMPLETED_STATUS,
    DOMAIN_EXECUTION_DISPATCHED,
    DOMAIN_EXECUTION_REJECTED,
    DOMAIN_EXECUTION_REJECTED_STATUS,
    DOMAIN_EXECUTION_REQUESTED,
    execute_domain_request,
    reconstruct_domain_execution_binding_replay,
)
from aigol.runtime.domain_runtime import activate_domain, create_domain, validate_domain
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-05T00:00:00+00:00"


def _active_domain(tmp_path) -> dict:
    created = create_domain(
        domain_id="AI_DECISION_VALIDATION",
        display_name="AI Decision Validation",
        domain_version="1.0.0",
        capabilities=["AI_DECISION_INTAKE", "REPLAY_VISIBLE_DECISION_REVIEW"],
        governance_scope="Product 1 AI Decision Validator governed operational domain",
        governance_policy_refs=[
            "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        ],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_reference="DOMAIN-EXECUTION-BINDING:CREATED",
        replay_dir=tmp_path / "domain",
    )
    validated = validate_domain(
        domain_artifact=created["domain_artifact"],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_reference="DOMAIN-EXECUTION-BINDING:VALIDATED",
        replay_dir=tmp_path / "domain",
    )
    return activate_domain(
        domain_artifact=validated["domain_artifact"],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_reference="DOMAIN-EXECUTION-BINDING:ACTIVE",
        replay_dir=tmp_path / "domain",
    )["domain_artifact"]


def _execute(tmp_path, **overrides) -> dict:
    workspace = tmp_path / "workspace"
    workspace.mkdir(exist_ok=True)
    args = {
        "domain_artifact": _active_domain(tmp_path),
        "domain_execution_id": "DOMAIN-EXECUTION-BINDING-000001",
        "workspace_root": workspace,
        "actor_id": "AIGOL_GOVERNANCE",
        "timestamp": CREATED_AT,
        "replay_dir": tmp_path / "domain_execution",
    }
    args.update(overrides)
    return execute_domain_request(**args)


def test_domain_execution_binding_performs_certified_execution(tmp_path) -> None:
    capture = _execute(tmp_path)
    replay = reconstruct_domain_execution_binding_replay(tmp_path / "domain_execution")
    target = tmp_path / "workspace" / DEFAULT_OUTPUT_FILE

    assert capture["domain_execution_status"] == DOMAIN_EXECUTION_COMPLETED_STATUS
    assert capture["domain_execution_evidence"]["runtime_version"] == AIGOL_DOMAIN_EXECUTION_BINDING_RUNTIME_VERSION
    assert capture["domain_provider_binding"]["provider_invoked"] is True
    assert capture["domain_provider_binding"]["provider_authority"] is False
    assert capture["domain_worker_binding"]["worker_dispatched"] is True
    assert capture["worker_capture"]["filesystem_worker_execution"]["worker_invoked"] is True
    assert replay["domain_execution_status"] == DOMAIN_EXECUTION_COMPLETED_STATUS
    assert replay["lifecycle_events"] == [
        DOMAIN_EXECUTION_REQUESTED,
        DOMAIN_EXECUTION_AUTHORIZED,
        DOMAIN_EXECUTION_DISPATCHED,
        DOMAIN_EXECUTION_COMPLETED,
    ]
    assert target.read_text(encoding="utf-8") == DEFAULT_OUTPUT_CONTENT


def test_domain_execution_binding_records_required_replay_events(tmp_path) -> None:
    _execute(tmp_path)
    expected = [
        ("000_domain_execution_requested.json", DOMAIN_EXECUTION_REQUESTED),
        ("001_domain_execution_authorized.json", DOMAIN_EXECUTION_AUTHORIZED),
        ("002_domain_execution_dispatched.json", DOMAIN_EXECUTION_DISPATCHED),
        ("003_domain_execution_completed.json", DOMAIN_EXECUTION_COMPLETED),
    ]

    for filename, event in expected:
        wrapper = json.loads((tmp_path / "domain_execution" / filename).read_text(encoding="utf-8"))
        assert wrapper["event_type"] == event
        assert wrapper["artifact"]["event_type"] == event


def test_domain_execution_binding_rejects_inactive_domain(tmp_path) -> None:
    created = create_domain(
        domain_id="AI_DECISION_VALIDATION",
        display_name="AI Decision Validation",
        domain_version="1.0.0",
        capabilities=["AI_DECISION_INTAKE"],
        governance_scope="Product 1 AI Decision Validator governed operational domain",
        governance_policy_refs=["docs/governance/CONSTITUTIONAL_INVARIANTS.md"],
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_reference="DOMAIN-EXECUTION-BINDING:CREATED-ONLY",
        replay_dir=tmp_path / "inactive_domain",
    )
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    capture = execute_domain_request(
        domain_artifact=created["domain_artifact"],
        domain_execution_id="DOMAIN-EXECUTION-BINDING-INACTIVE",
        workspace_root=workspace,
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_dir=tmp_path / "rejected_inactive",
    )
    replay = reconstruct_domain_execution_binding_replay(tmp_path / "rejected_inactive")

    assert capture["domain_execution_status"] == DOMAIN_EXECUTION_REJECTED_STATUS
    assert "domain must be ACTIVE" in capture["failure_reason"]
    assert replay["lifecycle_events"] == [DOMAIN_EXECUTION_REJECTED]


def test_domain_execution_binding_rejects_unknown_provider_before_worker_execution(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    capture = execute_domain_request(
        domain_artifact=_active_domain(tmp_path),
        domain_execution_id="DOMAIN-EXECUTION-BINDING-UNKNOWN-PROVIDER",
        workspace_root=workspace,
        actor_id="AIGOL_GOVERNANCE",
        timestamp=CREATED_AT,
        replay_dir=tmp_path / "unknown_provider",
        provider_registry=ProviderRegistry(),
    )
    replay = reconstruct_domain_execution_binding_replay(tmp_path / "unknown_provider")

    assert capture["domain_execution_status"] == DOMAIN_EXECUTION_REJECTED_STATUS
    assert "provider proposal not returned" in capture["failure_reason"]
    assert replay["lifecycle_events"] == [DOMAIN_EXECUTION_REQUESTED, DOMAIN_EXECUTION_REJECTED]
    assert not (workspace / DEFAULT_OUTPUT_FILE).exists()


def test_domain_execution_binding_rejects_invalid_worker_file_path(tmp_path) -> None:
    capture = _execute(
        tmp_path,
        domain_execution_id="DOMAIN-EXECUTION-BINDING-BAD-PATH",
        replay_dir=tmp_path / "bad_path",
        file_path="../escape.txt",
    )
    replay = reconstruct_domain_execution_binding_replay(tmp_path / "bad_path")

    assert capture["domain_execution_status"] == DOMAIN_EXECUTION_REJECTED_STATUS
    assert "file_path must be a single relative filename" in capture["failure_reason"]
    assert replay["lifecycle_events"] == [DOMAIN_EXECUTION_REQUESTED, DOMAIN_EXECUTION_REJECTED]


def test_domain_execution_binding_replay_detects_tampering(tmp_path) -> None:
    _execute(tmp_path)
    path = tmp_path / "domain_execution" / "003_domain_execution_completed.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_execution_hash"] = "sha256:tampered"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_execution_binding_replay(tmp_path / "domain_execution")


def test_domain_execution_binding_uses_existing_provider_authorization_and_worker_runtimes() -> None:
    import aigol.runtime.domain_execution_binding_runtime as binding_runtime

    source = inspect.getsource(binding_runtime)

    assert "run_provider_attachment(" in source
    assert "authorize_worker_request(" in source
    assert "create_authorized_worker_request(" in source
    assert "execute_filesystem_create_request(" in source
    assert "OpenAIProviderAdapter" not in source
    assert "provider_authority\": True" not in source
