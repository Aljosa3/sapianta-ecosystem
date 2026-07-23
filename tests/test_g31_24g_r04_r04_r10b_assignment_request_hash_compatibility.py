from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import worker_assignment_runtime as assignment
from aigol.runtime import worker_invocation_request_runtime as invocation_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g31_24g_r04_r04_r09b_r08c_invocation_request_compatibility import (
    _request,
)


def test_exact_r09b_request_satisfies_assignment_hash_contract_without_assignment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    capture, selection, authenticated_request, consumption, target, replay_dir = (
        _request(tmp_path, monkeypatch, "R10B")
    )
    artifact = capture["worker_invocation_request_artifact"]

    validated = assignment._validate_request_artifact(artifact)

    assert validated == artifact
    assert assignment._request_hash(artifact) == artifact["request_hash"]
    assert invocation_request._request_hash(artifact) == artifact["request_hash"]
    assert artifact["authorization_reference"] == authenticated_request["authorization_id"]
    assert artifact["authorization_hash"] == authenticated_request["authorization_hash"]
    assert artifact["execution_packet_reference"] == authenticated_request["request_id"]
    assert artifact["execution_packet_hash"] == authenticated_request["request_hash"]
    assert artifact["target_worker_family"] == selection["selected_resource_id"]
    assert artifact["compatibility_lineage"]["consumption_reconstruction"] == consumption
    assert not (replay_dir.parent / "worker-assignment").exists()
    assert target.read_text(encoding="utf-8") != "replacement bytes\n"


@pytest.mark.parametrize(
    "mode",
    (
        "removed",
        "lineage_type",
        "authenticated_request",
        "consumption",
        "selection",
        "certification",
    ),
)
def test_changed_r09b_lineage_fails_assignment_hash_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    capture, _, _, _, _, _ = _request(tmp_path, monkeypatch, f"R10B-{mode}")
    artifact = deepcopy(capture["worker_invocation_request_artifact"])
    compatibility = artifact["compatibility_lineage"]
    if mode == "removed":
        artifact.pop("compatibility_lineage")
    elif mode == "lineage_type":
        compatibility["lineage_type"] = "OTHER_LINEAGE"
    elif mode == "authenticated_request":
        compatibility["authenticated_request"]["request_id"] = "OTHER_REQUEST"
    elif mode == "consumption":
        compatibility["consumption_reconstruction"]["consumption_identity"] = (
            "OTHER_CONSUMPTION"
        )
    elif mode == "selection":
        compatibility["resource_selection_capture"]["resource_selection_artifact"][
            "selected_resource_id"
        ] = "OTHER_WORKER"
    else:
        compatibility["worker_selection_certification_hash"] = (
            "sha256:" + "0" * 64
        )
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    with pytest.raises(
        FailClosedRuntimeError,
        match="worker assignment failed closed: invocation request hash mismatch",
    ):
        assignment._validate_request_artifact(artifact)


def test_hash_compatibility_change_is_lineage_only_and_worker_neutral() -> None:
    source = inspect.getsource(assignment._request_hash)

    assert '"compatibility_lineage"' in source
    assert "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER" not in source
    assert "REPLACE_EXISTING_TEXT_FILE" not in source
    assert "assign_worker_from_invocation_request" not in source
    assert "default_worker_registry_for_request" not in source
