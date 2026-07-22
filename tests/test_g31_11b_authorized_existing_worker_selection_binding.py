from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime import confirmed_grounded_execution_authorization_binding as binding
from aigol.runtime.confirmed_grounded_execution_authorization_binding import (
    reconstruct_authorized_grounded_worker_selection,
    select_authorized_grounded_worker,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, with_replay_hash
from aigol.runtime.unified_resource_selection_runtime import (
    RESOURCE_SELECTION_SUCCEEDED,
    _registry_hash_input,
)
from test_g31_09_distinct_human_execution_decision_binding import CREATED_AT, REQUEST, _workspace
from test_g31_10_confirmed_grounded_execution_authorization_binding import _authorized


def _selected(tmp_path: Path, session: str = "G31-11B") -> tuple[dict, dict, Path, Path]:
    authorization, _, workspace, session_root = _authorized(tmp_path, session)
    capture = select_authorized_grounded_worker(
        execution_authorization_capture=authorization,
        session_root=session_root,
        replay_dir=session_root / "worker-selection",
    )
    return capture, authorization, workspace, session_root


def _registry_hash(registry: dict) -> dict:
    candidate = deepcopy(registry)
    candidate["registry_hash"] = replay_hash(_registry_hash_input(candidate))
    return candidate


def _rewrite_selection(root: Path, mutation) -> None:
    recorded_path = root / "000_resource_selection_recorded.json"
    recorded = load_json(recorded_path)
    selection = deepcopy(recorded["artifact"])
    mutation(selection)
    selection = with_replay_hash(selection, hash_field="artifact_hash")
    recorded["artifact"] = selection
    recorded_path.write_text(
        json.dumps(with_replay_hash(recorded, hash_field="replay_hash")), encoding="utf-8"
    )
    returned_path = root / "001_resource_selection_returned.json"
    returned = load_json(returned_path)
    returned["artifact"]["selection_hash"] = selection["artifact_hash"]
    returned["artifact"] = with_replay_hash(returned["artifact"], hash_field="artifact_hash")
    returned_path.write_text(
        json.dumps(with_replay_hash(returned, hash_field="replay_hash")), encoding="utf-8"
    )


def test_exact_authorization_selects_existing_certified_worker_and_stops(tmp_path: Path) -> None:
    capture, authorization, _, _ = _selected(tmp_path)

    assert capture["selection_status"] == RESOURCE_SELECTION_SUCCEEDED
    assert capture["selected_resource_id"] == "CODEX"
    assert capture["selected_role_type"] == "WORKER_ROLE"
    assert capture["execution_authorization_hash"] == authorization[
        "execution_authorization_artifact"
    ]["artifact_hash"]
    assert capture["complete_g31_lineage_reconstructed"] is True
    assert capture["worker_selected"] is True
    for field in (
        "worker_assigned", "worker_dispatched", "provider_invoked", "worker_invoked",
        "command_executed", "repository_mutated",
    ):
        assert capture[field] is False


@pytest.mark.parametrize("mode", ("NO_MATCH", "AMBIGUOUS"))
def test_existing_no_match_and_ambiguity_remain_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    registry = binding.default_resource_registry()
    if mode == "NO_MATCH":
        for resource in registry["resources"]:
            for role in resource["role_bindings"]:
                if role["role_type"] == "WORKER_ROLE":
                    role["capability_ids"] = tuple(
                        value for value in role["capability_ids"]
                        if value != "IMPLEMENTATION_ASSISTANCE"
                    )
    else:
        registry["resources"][3]["selection_priority"] = registry["resources"][2][
            "selection_priority"
        ]
    registry = _registry_hash(registry)
    monkeypatch.setattr(binding, "default_resource_registry", lambda: deepcopy(registry))

    with pytest.raises(FailClosedRuntimeError, match="certification is not valid"):
        _selected(tmp_path, f"G31-11B-{mode}")


@pytest.mark.parametrize(
    "mutation",
    (
        lambda capture: capture.update(authorization_status="FAILED_CLOSED"),
        lambda capture: capture["execution_authorization_artifact"].update(
            authorization_expires_at="2020-01-01T00:00:00Z"
        ),
        lambda capture: capture["execution_authorization_artifact"][
            "authorized_scope"
        ]["source_paths"].append("broadened.py"),
    ),
)
def test_failed_expired_or_broadened_authorization_fails_before_selection(
    tmp_path: Path, mutation
) -> None:
    authorization, _, _, session_root = _authorized(tmp_path, f"AUTH-{id(mutation)}")
    tampered = deepcopy(authorization)
    mutation(tampered)
    artifact = tampered.get("execution_authorization_artifact")
    if isinstance(artifact, dict):
        tampered["execution_authorization_artifact"] = with_replay_hash(
            artifact, hash_field="artifact_hash"
        )

    with pytest.raises(FailClosedRuntimeError):
        select_authorized_grounded_worker(
            execution_authorization_capture=tampered,
            session_root=session_root,
            replay_dir=session_root / "invalid-selection",
        )
    assert not (session_root / "invalid-selection").exists()


def test_cross_session_replay_and_stale_repository_evidence_fail(tmp_path: Path) -> None:
    authorization, _, workspace, session_root = _authorized(tmp_path, "G31-11B-STALE")
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        select_authorized_grounded_worker(
            execution_authorization_capture=authorization,
            session_root=tmp_path / "OTHER",
            replay_dir=tmp_path / "OTHER" / "selection",
        )
    Path(workspace, "aigol/runtime/human_interface.py").write_text(
        "def changed():\n    return True\n", encoding="utf-8"
    )
    with pytest.raises(FailClosedRuntimeError):
        select_authorized_grounded_worker(
            execution_authorization_capture=authorization,
            session_root=session_root,
            replay_dir=session_root / "stale-selection",
        )


def test_authorization_is_consumed_once_for_selection(tmp_path: Path) -> None:
    _, authorization, _, session_root = _selected(tmp_path, "G31-11B-REPLAYED")
    with pytest.raises(FailClosedRuntimeError, match="already used"):
        select_authorized_grounded_worker(
            execution_authorization_capture=authorization,
            session_root=session_root,
            replay_dir=session_root / "second-selection",
        )


@pytest.mark.parametrize(
    "mutation",
    (
        lambda artifact: artifact.update(context_hash="sha256:" + "0" * 64),
        lambda artifact: artifact.update(registry_hash="sha256:" + "1" * 64),
        lambda artifact: artifact.update(required_capability="UNSUPPORTED"),
        lambda artifact: artifact.update(domain_id="UNSUPPORTED"),
        lambda artifact: artifact.update(requested_role_type="PROVIDER_ROLE"),
    ),
)
def test_context_registry_and_vocabulary_substitution_fail_reconstruction(
    tmp_path: Path, mutation
) -> None:
    capture, authorization, _, _ = _selected(tmp_path, f"SELECT-{id(mutation)}")
    selection_root = Path(capture["resource_selection_replay_reference"])
    _rewrite_selection(selection_root, mutation)

    with pytest.raises(FailClosedRuntimeError, match="mismatch"):
        reconstruct_authorized_grounded_worker_selection(
            selection_replay_dir=selection_root,
            execution_authorization_replay_dir=authorization[
                "execution_authorization_replay_reference"
            ],
        )


def test_hash_invalid_worker_certification_fails_before_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authorization, _, _, session_root = _authorized(tmp_path, "G31-11B-CERT")
    certification = load_json(binding.WORKER_SELECTION_CERTIFICATION_PATH)
    certification["final_verdict"] = "WORKER_SELECTION_GAPS_FOUND"
    path = tmp_path / "tampered-certification.json"
    path.write_text(json.dumps(certification), encoding="utf-8")
    monkeypatch.setattr(binding, "WORKER_SELECTION_CERTIFICATION_PATH", path)

    with pytest.raises(FailClosedRuntimeError, match="worker selection artifact hash mismatch"):
        select_authorized_grounded_worker(
            execution_authorization_capture=authorization,
            session_root=session_root,
            replay_dir=session_root / "certification-selection",
        )


def test_reordered_selection_replay_fails_closed(tmp_path: Path) -> None:
    capture, authorization, _, _ = _selected(tmp_path, "G31-11B-ORDER")
    root = Path(capture["resource_selection_replay_reference"])
    path = root / "001_resource_selection_returned.json"
    wrapper = load_json(path)
    wrapper["replay_index"] = 0
    path.write_text(
        json.dumps(with_replay_hash(wrapper, hash_field="replay_hash")), encoding="utf-8"
    )
    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_authorized_grounded_worker_selection(
            selection_replay_dir=root,
            execution_authorization_replay_dir=authorization[
                "execution_authorization_replay_reference"
            ],
        )


def test_real_aicli_selection_remains_exact_when_later_assignment_continues(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, "g31-11b-aicli")
    output: list[str] = []
    values = iter([REQUEST, "/send", "/approve", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-11B-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(values),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]
    rendered = "\n".join(output)

    assert runtime["execution_authorized"] is True
    assert runtime["worker_selected"] is True
    assert runtime["authorized_worker_selection_capture"]["worker_assigned"] is False
    assert runtime["authorized_worker_selection_capture"]["worker_dispatched"] is False
    assert runtime["authorized_worker_selection_capture"]["worker_invoked"] is False
    assert runtime["worker_assigned"] is True
    assert runtime["worker_dispatched"] is True
    assert runtime["worker_invoked"] is True
    assert runtime["selected_resource_id"] == "CODEX"
    assert "Certified Worker Selection" in rendered
    assert "selected_resource_id: CODEX" in rendered
    assert "Worker Invocation Request" in rendered
    assert "Worker Assignment" in rendered
    assert "worker_dispatched: False" in rendered


def test_no_copied_helpers_and_production_change_stays_bounded() -> None:
    source = Path(
        "aigol/runtime/confirmed_grounded_execution_authorization_binding.py"
    ).read_text(encoding="utf-8")
    for helper in (
        "def _verify_hash", "def _relative_path", "def _unique_relative_paths",
        "def _persist", "def _verify_wrapper", "def _require_string",
        "def _ensure_replay_available",
    ):
        assert helper not in source
    assert "select_unified_resource(" in source
    assert "assign_worker_from_invocation_request" not in source
