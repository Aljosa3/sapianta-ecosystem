"""Tests for AIGOL_ERR_V0."""

from __future__ import annotations

import pytest

from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    AIGOL_ERR_V0_RUNTIME_VERSION,
    COGNITION_PROVIDER,
    ERR_RESOURCE_SELECTION_EVIDENCE_V0,
    EXECUTION_WORKER,
    INACTIVE,
    MOCK_FILESYSTEM_WORKER_ID,
    MOCK_PROVIDER_ID,
    create_err_v0_registry,
    default_err_v0_registry,
    demonstrate_err_v0_hirr_to_resource_selection,
    find_resources_by_capability,
    get_resource_by_id,
    reconstruct_err_v0_selection_replay,
    register_resource,
    select_resource_for_capability,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-06-16T00:00:00+00:00"


def test_resource_can_be_registered() -> None:
    registry = create_err_v0_registry()
    resource = register_resource(
        registry,
        {
            "resource_id": "test_provider",
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )

    assert registry["registry_version"] == AIGOL_ERR_V0_RUNTIME_VERSION
    assert resource == {
        "resource_id": "test_provider",
        "resource_type": COGNITION_PROVIDER,
        "capabilities": ["reasoning"],
        "status": ACTIVE,
    }
    assert registry["resources"] == [resource]


def test_resource_can_be_retrieved_by_id() -> None:
    registry = default_err_v0_registry()

    resource = get_resource_by_id(registry, MOCK_PROVIDER_ID)

    assert resource["resource_id"] == MOCK_PROVIDER_ID
    assert resource["resource_type"] == COGNITION_PROVIDER
    assert resource["capabilities"] == ["reasoning"]


def test_capability_search_returns_correct_resources() -> None:
    registry = default_err_v0_registry()

    reasoning = find_resources_by_capability(registry, "reasoning")
    file_write = find_resources_by_capability(registry, "file_write")

    assert [resource["resource_id"] for resource in reasoning] == [MOCK_PROVIDER_ID]
    assert [resource["resource_id"] for resource in file_write] == [MOCK_FILESYSTEM_WORKER_ID]
    assert file_write[0]["resource_type"] == EXECUTION_WORKER


def test_inactive_resources_are_excluded_from_capability_search() -> None:
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": "inactive_provider",
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": INACTIVE,
        },
    )
    register_resource(
        registry,
        {
            "resource_id": MOCK_PROVIDER_ID,
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )

    matches = find_resources_by_capability(registry, "reasoning")

    assert [resource["resource_id"] for resource in matches] == [MOCK_PROVIDER_ID]


def test_selection_creates_replay_visible_evidence(tmp_path) -> None:
    capture = select_resource_for_capability(
        selection_id="ERR-SELECTION-000001",
        required_capability="reasoning",
        replay_dir=tmp_path / "err_selection",
        created_at=CREATED_AT,
        registry=default_err_v0_registry(),
        resource_type=COGNITION_PROVIDER,
    )
    reconstructed = reconstruct_err_v0_selection_replay(tmp_path / "err_selection")
    evidence = capture["err_selection_evidence_artifact"]

    assert capture["selected_resource_id"] == MOCK_PROVIDER_ID
    assert evidence["artifact_type"] == ERR_RESOURCE_SELECTION_EVIDENCE_V0
    assert evidence["replay_visible"] is True
    assert evidence["provider_invoked"] is False
    assert evidence["worker_invoked"] is False
    assert evidence["provider_invoked_worker"] is False
    assert evidence["worker_invoked_provider"] is False
    assert evidence["orchestration_performed"] is False
    assert reconstructed["selected_resource_id"] == MOCK_PROVIDER_ID
    assert reconstructed["replay_artifact_count"] == 2


def test_required_demonstration_workflow_selects_mock_provider(tmp_path) -> None:
    capture = demonstrate_err_v0_hirr_to_resource_selection(
        selection_id="ERR-HIRR-DEMO-000001",
        human_intent="Explain the decision boundary for this governed action.",
        hirr_output={
            "hirr_status": "RESOLVED",
            "required_capability": "reasoning",
            "resource_type": COGNITION_PROVIDER,
        },
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hirr_demo",
        registry=default_err_v0_registry(),
    )
    reconstructed = reconstruct_err_v0_selection_replay(tmp_path / "hirr_demo")

    assert capture["selected_resource_id"] == MOCK_PROVIDER_ID
    assert capture["selected_resource_type"] == COGNITION_PROVIDER
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["human_intent"] == "Explain the decision boundary for this governed action."
    assert reconstructed["hirr_output"]["required_capability"] == "reasoning"


def test_no_active_capability_match_fails_closed(tmp_path) -> None:
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": "inactive_worker",
            "resource_type": EXECUTION_WORKER,
            "capabilities": ["file_write"],
            "status": INACTIVE,
        },
    )

    with pytest.raises(FailClosedRuntimeError, match="no active resource"):
        select_resource_for_capability(
            selection_id="ERR-NO-MATCH-000001",
            required_capability="file_write",
            replay_dir=tmp_path / "no_match",
            created_at=CREATED_AT,
            registry=registry,
            resource_type=EXECUTION_WORKER,
        )
