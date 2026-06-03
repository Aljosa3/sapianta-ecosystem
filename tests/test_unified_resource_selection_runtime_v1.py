"""Tests for UNIFIED_RESOURCE_SELECTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_PROHIBITED, PROVIDER_REQUIRED
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unified_resource_selection_runtime import (
    GOVERNANCE_RUNTIME_ROLE,
    HYBRID_PROVIDER_WORKER,
    PROVIDER,
    PROVIDER_ROLE,
    RESOURCE_SELECTION_ARTIFACT_V1,
    RESOURCE_SELECTION_SUCCEEDED,
    UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION,
    WORKER,
    WORKER_ROLE,
    default_resource_registry,
    reconstruct_unified_resource_selection_replay,
    select_unified_resource,
)


CREATED_AT = "2026-06-03T15:00:00+00:00"


def test_selects_provider_resource_for_required_proposal_and_reconstructs(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-PROVIDER-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="PROPOSAL_GENERATION",
        requested_role_type=PROVIDER_ROLE,
        domain_id="TRADING",
        provider_necessity_classification=PROVIDER_REQUIRED,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "provider",
        context_assembly_output={"context_id": "CONTEXT-000001", "context_hash": "sha256:context"},
    )
    reconstructed = reconstruct_unified_resource_selection_replay(tmp_path / "provider")
    artifact = capture["resource_selection_artifact"]

    assert artifact["artifact_type"] == RESOURCE_SELECTION_ARTIFACT_V1
    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "OPENAI"
    assert capture["selected_resource_category"] == PROVIDER
    assert capture["selected_role_type"] == PROVIDER_ROLE
    assert artifact["runtime_version"] == UNIFIED_RESOURCE_SELECTION_RUNTIME_VERSION
    assert artifact["capability_matches"] is True
    assert artifact["trust_matches"] is True
    assert artifact["authority_matches"] is True
    assert artifact["context_reference"] == "CONTEXT-000001"
    assert artifact["context_hash"] == "sha256:context"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["selected_resource_id"] == "OPENAI"
    assert reconstructed["replay_artifact_count"] == 2


def test_selects_worker_resource_only_with_worker_authorization_requirement(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-WORKER-000001",
        workflow_type="REPLAY_INSPECTION",
        required_capability="REPLAY_INSPECTION",
        requested_role_type=WORKER_ROLE,
        domain_id="REPLAY",
        worker_authorization_required=True,
        min_trust_level="HIGH",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker",
    )

    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "REPLAY_INSPECTOR_WORKER"
    assert capture["selected_resource_category"] == WORKER
    assert capture["selected_role_type"] == WORKER_ROLE
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False


def test_selects_hybrid_resource_with_explicit_active_worker_role(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-HYBRID-WORKER-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="IMPLEMENTATION_ASSISTANCE",
        requested_role_type=WORKER_ROLE,
        domain_id="NATIVE_DEVELOPMENT",
        worker_authorization_required=True,
        preferred_resource_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hybrid_worker",
    )

    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == WORKER_ROLE
    assert "as WORKER_ROLE" in capture["selection_rationale"]
    assert capture["worker_invoked"] is False


def test_selects_hybrid_resource_with_explicit_active_provider_role(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-HYBRID-PROVIDER-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="IMPLEMENTATION_ASSISTANCE",
        requested_role_type=PROVIDER_ROLE,
        domain_id="NATIVE_DEVELOPMENT",
        provider_necessity_classification=PROVIDER_REQUIRED,
        preferred_resource_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hybrid_provider",
    )

    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == PROVIDER_ROLE
    assert capture["provider_invoked"] is False


def test_selects_governance_runtime_resource(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-GOVERNANCE-000001",
        workflow_type="REPLAY_INSPECTION",
        required_capability="GOVERNANCE_VALIDATION",
        requested_role_type=GOVERNANCE_RUNTIME_ROLE,
        domain_id="GOVERNANCE",
        min_trust_level="HIGH",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "governance_runtime",
    )

    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "UNIFIED_REPLAY_RECONSTRUCTION_RUNTIME"
    assert capture["selected_role_type"] == GOVERNANCE_RUNTIME_ROLE


def test_provider_prohibited_fails_closed(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-PROHIBITED-000001",
        workflow_type="OPERATOR_INSPECTION",
        required_capability="PROPOSAL_GENERATION",
        requested_role_type=PROVIDER_ROLE,
        domain_id="GOVERNANCE",
        provider_necessity_classification=PROVIDER_PROHIBITED,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "provider_prohibited",
    )

    assert capture["fail_closed"] is True
    assert "provider is prohibited" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_worker_selection_without_authorization_requirement_fails_closed(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-WORKER-NO-AUTH-000001",
        workflow_type="REPLAY_INSPECTION",
        required_capability="REPLAY_INSPECTION",
        requested_role_type=WORKER_ROLE,
        domain_id="REPLAY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_no_auth",
    )

    assert capture["fail_closed"] is True
    assert "worker authorization requirement is missing" in capture["failure_reason"]


def test_no_eligible_resource_fails_closed_on_trust_mismatch(tmp_path) -> None:
    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-TRUST-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="IMPLEMENTATION_ASSISTANCE",
        requested_role_type=WORKER_ROLE,
        domain_id="NATIVE_DEVELOPMENT",
        worker_authorization_required=True,
        min_trust_level="HIGH",
        preferred_resource_id="CODEX",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "trust",
    )

    assert capture["fail_closed"] is True
    assert "no eligible resource" in capture["failure_reason"]
    codex_rejection = next(
        item for item in capture["resource_selection_diagnostics"]["rejected_resources"] if item["resource_id"] == "CODEX"
    )
    assert codex_rejection["reason"] == "trust mismatch"


def test_duplicate_resource_registration_fails_closed(tmp_path) -> None:
    registry = default_resource_registry()
    registry["resources"].append(dict(registry["resources"][0]))
    registry.pop("registry_hash", None)

    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-DUPLICATE-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="PROPOSAL_GENERATION",
        requested_role_type=PROVIDER_ROLE,
        domain_id="TRADING",
        provider_necessity_classification=PROVIDER_REQUIRED,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "duplicate",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "duplicate resource registration" in capture["failure_reason"]


def test_ambiguous_resource_resolution_fails_closed(tmp_path) -> None:
    registry = default_resource_registry()
    registry["resources"][1]["selection_priority"] = registry["resources"][0]["selection_priority"]
    registry.pop("registry_hash", None)

    capture = select_unified_resource(
        selection_id="RESOURCE-SELECTION-AMBIGUOUS-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="PROPOSAL_GENERATION",
        requested_role_type=PROVIDER_ROLE,
        domain_id="TRADING",
        provider_necessity_classification=PROVIDER_REQUIRED,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "ambiguous resource resolution" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_resource_selection_replay(tmp_path) -> None:
    select_unified_resource(
        selection_id="RESOURCE-SELECTION-CORRUPT-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="PROPOSAL_GENERATION",
        requested_role_type=PROVIDER_ROLE,
        domain_id="TRADING",
        provider_necessity_classification=PROVIDER_REQUIRED,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_resource_selection_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_resource_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_unified_resource_selection_replay(tmp_path / "corrupt")


def test_unified_resource_selection_runtime_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.unified_resource_selection_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
