"""Tests for AIGOL_REAL_PROVIDER_REGISTRATION_V1."""

from __future__ import annotations

import inspect
from copy import deepcopy

from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    CLAUDE_PROVIDER_ID,
    COGNITION_PROVIDER,
    GEMINI_PROVIDER_ID,
    INACTIVE,
    MISTRAL_PROVIDER_ID,
    OPENAI_PROVIDER_ID,
    REAL_COGNITION_PROVIDER_CAPABILITIES,
    REAL_COGNITION_PROVIDER_IDS,
    create_err_v0_registry,
    find_resources_by_capability,
    get_resource_by_id,
    real_provider_err_v1_registry,
    reconstruct_err_v0_selection_replay,
    register_real_cognition_providers,
    select_resource_for_capability,
)
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import run_ocs_llm_cognition_end_to_end


CREATED_AT = "2026-06-16T00:00:00+00:00"


def test_real_cognition_providers_register_successfully() -> None:
    registry = create_err_v0_registry()

    registered = register_real_cognition_providers(registry)

    assert [resource["resource_id"] for resource in registered] == list(REAL_COGNITION_PROVIDER_IDS)
    assert [resource["resource_id"] for resource in registry["resources"]] == list(REAL_COGNITION_PROVIDER_IDS)
    assert all(resource["resource_type"] == COGNITION_PROVIDER for resource in registered)
    assert all(resource["status"] == ACTIVE for resource in registered)
    assert all(resource["capabilities"] == list(REAL_COGNITION_PROVIDER_CAPABILITIES) for resource in registered)


def test_real_cognition_providers_can_be_retrieved_by_id() -> None:
    registry = real_provider_err_v1_registry()

    openai = get_resource_by_id(registry, OPENAI_PROVIDER_ID)
    claude = get_resource_by_id(registry, CLAUDE_PROVIDER_ID)
    gemini = get_resource_by_id(registry, GEMINI_PROVIDER_ID)
    mistral = get_resource_by_id(registry, MISTRAL_PROVIDER_ID)

    assert openai["resource_type"] == COGNITION_PROVIDER
    assert claude["resource_type"] == COGNITION_PROVIDER
    assert gemini["resource_type"] == COGNITION_PROVIDER
    assert mistral["resource_type"] == COGNITION_PROVIDER
    assert openai["capabilities"] == list(REAL_COGNITION_PROVIDER_CAPABILITIES)


def test_reasoning_capability_lookup_returns_real_providers() -> None:
    registry = real_provider_err_v1_registry()

    matches = find_resources_by_capability(
        registry,
        "reasoning",
        resource_type=COGNITION_PROVIDER,
    )

    assert [resource["resource_id"] for resource in matches] == list(REAL_COGNITION_PROVIDER_IDS)
    assert all(resource["status"] == ACTIVE for resource in matches)


def test_inactive_real_providers_are_excluded_from_capability_lookup() -> None:
    registry = real_provider_err_v1_registry()
    registry["resources"][0] = deepcopy(registry["resources"][0])
    registry["resources"][0]["status"] = INACTIVE

    matches = find_resources_by_capability(
        registry,
        "reasoning",
        resource_type=COGNITION_PROVIDER,
    )

    assert [resource["resource_id"] for resource in matches] == [
        CLAUDE_PROVIDER_ID,
        GEMINI_PROVIDER_ID,
        MISTRAL_PROVIDER_ID,
    ]


def test_openai_selection_creates_replay_visible_evidence(tmp_path) -> None:
    capture = select_resource_for_capability(
        selection_id="REAL-PROVIDER-OPENAI-SELECTION-000001",
        required_capability="reasoning",
        replay_dir=tmp_path / "openai_selection",
        created_at=CREATED_AT,
        registry=real_provider_err_v1_registry(),
        resource_type=COGNITION_PROVIDER,
    )
    reconstructed = reconstruct_err_v0_selection_replay(tmp_path / "openai_selection")
    evidence = capture["err_selection_evidence_artifact"]

    assert capture["selected_resource_id"] == OPENAI_PROVIDER_ID
    assert capture["selected_resource_type"] == COGNITION_PROVIDER
    assert evidence["active_resource_ids"] == list(REAL_COGNITION_PROVIDER_IDS)
    assert evidence["provider_invoked"] is False
    assert evidence["worker_invoked"] is False
    assert evidence["orchestration_performed"] is False
    assert evidence["governance_modified"] is False
    assert reconstructed["selected_resource_id"] == OPENAI_PROVIDER_ID
    assert reconstructed["replay_visible"] is True


def test_claude_selection_uses_standard_err_lookup_when_openai_inactive(tmp_path) -> None:
    registry = real_provider_err_v1_registry()
    registry["resources"][0] = deepcopy(registry["resources"][0])
    registry["resources"][0]["status"] = INACTIVE

    capture = select_resource_for_capability(
        selection_id="REAL-PROVIDER-CLAUDE-SELECTION-000001",
        required_capability="reasoning",
        replay_dir=tmp_path / "claude_selection",
        created_at=CREATED_AT,
        registry=registry,
        resource_type=COGNITION_PROVIDER,
    )
    reconstructed = reconstruct_err_v0_selection_replay(tmp_path / "claude_selection")
    evidence = capture["err_selection_evidence_artifact"]

    assert capture["selected_resource_id"] == CLAUDE_PROVIDER_ID
    assert evidence["active_resource_ids"] == [
        CLAUDE_PROVIDER_ID,
        GEMINI_PROVIDER_ID,
        MISTRAL_PROVIDER_ID,
    ]
    assert evidence["provider_invoked"] is False
    assert evidence["worker_invoked"] is False
    assert reconstructed["selected_resource_id"] == CLAUDE_PROVIDER_ID


def test_ocs_err_path_accepts_registry_without_architecture_change() -> None:
    signature = inspect.signature(run_ocs_llm_cognition_end_to_end)

    assert "use_err_resource_lookup" in signature.parameters
    assert "err_required_capability" in signature.parameters
    assert "err_registry" in signature.parameters


def test_real_provider_registration_preserves_err_passive_boundary() -> None:
    import aigol.runtime.external_resource_registry_runtime as runtime

    source = inspect.getsource(runtime)
    forbidden_fragments = (
        "invoke_provider(",
        "provider_transport",
        "api_key",
        "authenticate",
        "dispatch_worker(",
        "authorize_",
        "rank_",
        "optimize_",
        "lifecycle",
        "requests",
        "httpx",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
