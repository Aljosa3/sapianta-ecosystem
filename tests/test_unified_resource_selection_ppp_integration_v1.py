"""Tests for UNIFIED_RESOURCE_SELECTION_PPP_INTEGRATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import PROVIDER_REQUIRED
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unified_resource_selection_ppp_integration import (
    PPP_PROVIDER_PROPOSAL_READY,
    PPP_WORKER_HANDOFF_REFERENCE_READY,
    RESOURCE_PPP_INTEGRATED,
    RESOURCE_PPP_INTEGRATION_ARTIFACT_V1,
    reconstruct_resource_selection_ppp_integration_replay,
    integrate_resource_selection_with_ppp,
)
from aigol.runtime.unified_resource_selection_runtime import (
    HYBRID_PROVIDER_WORKER,
    PROVIDER,
    PROVIDER_ROLE,
    WORKER_ROLE,
    select_unified_resource,
)


CREATED_AT = "2026-06-03T16:00:00+00:00"


def _provider_selection(tmp_path, *, preferred_resource_id: str | None = None) -> dict:
    return select_unified_resource(
        selection_id=f"RESOURCE-SELECTION-{preferred_resource_id or 'OPENAI'}-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="PROPOSAL_GENERATION" if preferred_resource_id is None else "IMPLEMENTATION_ASSISTANCE",
        requested_role_type=PROVIDER_ROLE,
        domain_id="TRADING" if preferred_resource_id is None else "NATIVE_DEVELOPMENT",
        provider_necessity_classification=PROVIDER_REQUIRED,
        preferred_resource_id=preferred_resource_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"selection_{preferred_resource_id or 'openai'}",
        context_assembly_output={"context_id": "CONTEXT-PPP-000001", "context_hash": "sha256:context"},
    )["resource_selection_artifact"]


def _worker_selection(tmp_path, *, preferred_resource_id: str = "CODEX") -> dict:
    return select_unified_resource(
        selection_id=f"RESOURCE-SELECTION-{preferred_resource_id}-WORKER-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        required_capability="IMPLEMENTATION_ASSISTANCE",
        requested_role_type=WORKER_ROLE,
        domain_id="NATIVE_DEVELOPMENT",
        worker_authorization_required=True,
        preferred_resource_id=preferred_resource_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"selection_{preferred_resource_id}_worker",
    )["resource_selection_artifact"]


def _rehash(artifact: dict) -> dict:
    updated = deepcopy(artifact)
    updated.pop("artifact_hash", None)
    updated["artifact_hash"] = replay_hash(updated)
    return updated


def test_integrates_provider_selection_for_ppp_proposal_production(tmp_path) -> None:
    selection = _provider_selection(tmp_path)
    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-PROVIDER-000001",
        resource_selection_artifact=selection,
        context_assembly_artifact={"context_id": "CONTEXT-PPP-000001", "context_hash": "sha256:context"},
        ppp_stage="PROPOSAL_PRODUCTION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration_provider",
    )
    reconstructed = reconstruct_resource_selection_ppp_integration_replay(tmp_path / "integration_provider")

    assert capture["integration_status"] == RESOURCE_PPP_INTEGRATED
    assert capture["ppp_resource_status"] == PPP_PROVIDER_PROPOSAL_READY
    assert capture["selected_resource_id"] == "OPENAI"
    assert capture["selected_resource_category"] == PROVIDER
    assert capture["selected_role_type"] == PROVIDER_ROLE
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["selected_resource_id"] == "OPENAI"
    assert reconstructed["replay_artifact_count"] == 2
    assert capture["resource_ppp_integration_artifact"]["artifact_type"] == RESOURCE_PPP_INTEGRATION_ARTIFACT_V1


def test_integrates_hybrid_provider_role_with_explicit_role(tmp_path) -> None:
    selection = _provider_selection(tmp_path, preferred_resource_id="CODEX")
    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-HYBRID-PROVIDER-000001",
        resource_selection_artifact=selection,
        ppp_stage="PROPOSAL_PRODUCTION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration_hybrid_provider",
    )

    assert capture["integration_status"] == RESOURCE_PPP_INTEGRATED
    assert capture["ppp_resource_status"] == PPP_PROVIDER_PROPOSAL_READY
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == PROVIDER_ROLE


def test_integrates_hybrid_worker_role_as_handoff_reference_only(tmp_path) -> None:
    selection = _worker_selection(tmp_path)
    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-HYBRID-WORKER-000001",
        resource_selection_artifact=selection,
        ppp_stage="IMPLEMENTATION_HANDOFF",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "integration_hybrid_worker",
    )

    assert capture["integration_status"] == RESOURCE_PPP_INTEGRATED
    assert capture["ppp_resource_status"] == PPP_WORKER_HANDOFF_REFERENCE_READY
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_resource_category"] == HYBRID_PROVIDER_WORKER
    assert capture["selected_role_type"] == WORKER_ROLE
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_missing_resource_selection_fails_closed(tmp_path) -> None:
    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-MISSING-000001",
        resource_selection_artifact={},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "missing",
    )

    assert capture["fail_closed"] is True
    assert "resource selection missing" in capture["failure_reason"]


def test_ambiguous_role_fails_closed(tmp_path) -> None:
    selection = deepcopy(_provider_selection(tmp_path))
    selection["selected_role_type"] = None
    selection = _rehash(selection)

    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-AMBIGUOUS-000001",
        resource_selection_artifact=selection,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
    )

    assert capture["fail_closed"] is True
    assert "resource role ambiguous" in capture["failure_reason"] or "selected_role_type is required" in capture["failure_reason"]


def test_capability_trust_and_authority_mismatches_fail_closed(tmp_path) -> None:
    base = _provider_selection(tmp_path)

    for field, expected, path_name in (
        ("capability_matches", "capability mismatch", "capability"),
        ("trust_matches", "trust mismatch", "trust"),
        ("authority_matches", "authority mismatch", "authority"),
    ):
        selection = deepcopy(base)
        selection[field] = False
        selection = _rehash(selection)
        capture = integrate_resource_selection_with_ppp(
            integration_id=f"RESOURCE-PPP-INTEGRATION-{path_name.upper()}-000001",
            resource_selection_artifact=selection,
            created_at=CREATED_AT,
            replay_dir=tmp_path / path_name,
        )

        assert capture["fail_closed"] is True
        assert expected in capture["failure_reason"]


def test_worker_role_for_proposal_production_fails_closed(tmp_path) -> None:
    selection = _worker_selection(tmp_path)
    capture = integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-WORKER-PROPOSAL-000001",
        resource_selection_artifact=selection,
        ppp_stage="PROPOSAL_PRODUCTION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_for_proposal",
    )

    assert capture["fail_closed"] is True
    assert "capability mismatch" in capture["failure_reason"]
    assert capture["worker_invoked"] is False


def test_reconstruction_detects_corrupt_resource_ppp_replay(tmp_path) -> None:
    selection = _provider_selection(tmp_path)
    integrate_resource_selection_with_ppp(
        integration_id="RESOURCE-PPP-INTEGRATION-CORRUPT-000001",
        resource_selection_artifact=selection,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_resource_ppp_integration_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_resource_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_resource_selection_ppp_integration_replay(tmp_path / "corrupt")


def test_resource_ppp_integration_has_no_invocation_or_execution_imports() -> None:
    import aigol.runtime.unified_resource_selection_ppp_integration as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
