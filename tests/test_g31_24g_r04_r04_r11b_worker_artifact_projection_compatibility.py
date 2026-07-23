from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime import worker_assignment_runtime as assignment
from aigol.runtime import worker_invocation_request_runtime as invocation_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g31_12b_g31_selection_to_g24_worker_assignment_binding import (
    _request_and_assignment,
)
from test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility import (
    CREATED,
    _request,
)


def _rehash_request(artifact: dict) -> None:
    artifact["request_hash"] = invocation_request._request_hash(artifact)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


def _rehash_selection(artifact: dict) -> None:
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)


def test_exact_certified_lineage_projects_existing_worker_artifact_without_assignment(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    capture, selection_capture, request, _, target, replay_dir = _request(
        tmp_path, monkeypatch, "R11B"
    )
    artifact = capture["worker_invocation_request_artifact"]
    selection = selection_capture["resource_selection_artifact"]

    worker = assignment.default_worker_registry_for_request(
        artifact, created_at=CREATED
    )[0]

    assert worker["artifact_type"] == assignment.WORKER_ARTIFACT_V1
    assert worker["worker_id"] == selection["selected_resource_id"]
    assert worker["worker_version"] == selection["selected_resource_version"]
    assert worker["worker_family"] == artifact["target_worker_family"]
    assert worker["worker_roles"] == [selection["selected_role_type"]]
    assert worker["capability_id"] == selection["required_capability"]
    assert worker["selected_resource_category"] == selection["selected_resource_category"]
    assert worker["selected_authority_profile"] == selection["selected_authority_profile"]
    assert worker["selected_domain_id"] == selection["domain_id"]
    assert worker["selection_artifact_hash"] == selection["artifact_hash"]
    assert worker["selection_context_hash"] == selection["context_hash"]
    assert worker["selection_registry_hash"] == selection["registry_hash"]
    assert worker["replay_reference"] == selection_capture[
        "resource_selection_replay_reference"
    ]
    assert worker["compatible_execution_packets"] == [request["request_id"]]
    assert worker["allowed_outputs"] == [request["target_path"]]
    assert worker["governance_authority"] is False
    assert worker["provider_authority"] is False
    assert worker["worker_dispatched"] is False
    assert worker["worker_invoked"] is False
    assert not (replay_dir.parent / "worker-assignment").exists()
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


@pytest.mark.parametrize(
    "mode",
    (
        "worker_id",
        "worker_version",
        "capability",
        "category",
        "authority",
        "domain",
        "selection_replay",
        "certification",
        "assigned",
        "ambiguous",
    ),
)
def test_tampered_or_ambiguous_certified_projection_fails_before_assignment(
    tmp_path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    capture, _, _, _, target, replay_dir = _request(
        tmp_path, monkeypatch, f"R11B-{mode}"
    )
    artifact = deepcopy(capture["worker_invocation_request_artifact"])
    compatibility = artifact["compatibility_lineage"]
    selection_capture = compatibility["resource_selection_capture"]
    selection = selection_capture["resource_selection_artifact"]
    if mode == "worker_id":
        selection["selected_resource_id"] = "OTHER_WORKER"
        _rehash_selection(selection)
    elif mode == "worker_version":
        selection["selected_resource_version"] = "OTHER_VERSION"
        _rehash_selection(selection)
    elif mode == "capability":
        selection["required_capability"] = "OTHER_CAPABILITY"
        _rehash_selection(selection)
    elif mode == "category":
        selection["selected_resource_category"] = "OTHER_CATEGORY"
        _rehash_selection(selection)
    elif mode == "authority":
        selection["selected_authority_profile"] = "OTHER_AUTHORITY"
        _rehash_selection(selection)
    elif mode == "domain":
        selection["domain_id"] = "OTHER_DOMAIN"
        _rehash_selection(selection)
    elif mode == "selection_replay":
        selection_capture["resource_selection_replay_reference"] = ""
    elif mode == "certification":
        compatibility["worker_selection_certification_hash"] = "sha256:" + "0" * 64
    elif mode == "assigned":
        selection_capture["worker_assigned"] = True
    else:
        artifact["g31_lineage"] = {"resource_selection_artifact": selection}
    _rehash_request(artifact)

    with pytest.raises(FailClosedRuntimeError, match="worker assignment failed closed"):
        assignment.default_worker_registry_for_request(artifact, created_at=CREATED)

    assert not (replay_dir.parent / "worker-assignment").exists()
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


def test_existing_g31_projection_remains_unchanged_without_assignment(tmp_path) -> None:
    request, _, selection, _ = _request_and_assignment(
        tmp_path, "R11B-G31", assign=False
    )
    artifact = request["worker_invocation_request_artifact"]

    worker = assignment.default_worker_registry_for_request(
        artifact, created_at=CREATED
    )[0]

    assert worker["worker_id"] == "CODEX"
    assert worker["worker_version"] == selection["resource_selection_artifact"][
        "selected_resource_version"
    ]
    assert worker["selected_resource_category"] == "HYBRID_PROVIDER_WORKER"
    assert worker["selected_role_type"] == "WORKER_ROLE"
    assert worker["selected_authority_profile"] == "WORKER_AUTHORIZED_TASK_ONLY"


def test_compatibility_projection_is_worker_neutral_and_stops_before_assignment() -> None:
    source = inspect.getsource(assignment._certified_compatibility_worker_projection)

    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "CODEX" not in source
    assert "assign_worker_from_invocation_request" not in source
    assert "dispatch_assigned_worker" not in source
    assert "invoke_dispatched_worker" not in source
