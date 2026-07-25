from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import (
    filesystem_replace_worker_output_to_result_capture_binding_runtime as bridge,
)
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
    replay_hash,
)
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)


WORKER_ID = "FILESYSTEM_REPLACE_EXISTING_TEXT_FILE_WORKER"
OPERATION = "REPLACE_EXISTING_TEXT_FILE"


def _binding_args(result: dict) -> dict:
    return {
        "binding_capture": result["filesystem_replace_worker_result_capture"],
        "authenticated_request": result["authenticated_replacement_request"],
        "filesystem_worker_capture": result[
            "filesystem_replace_worker_capture"
        ],
        "filesystem_worker_reconstruction": result[
            "filesystem_replace_worker_reconstruction"
        ],
        "worker_invocation_artifact": result["worker_invocation_capture"][
            "worker_invocation_artifact"
        ],
        "worker_invocation_replay_reference": result[
            "worker_invocation_replay_reference"
        ],
        "worker_assignment_artifact": result["worker_assignment_capture"][
            "worker_assignment_artifact"
        ],
        "execution_artifact": result["worker_execution_capture"][
            "execution_artifact"
        ],
        "execution_replay": result["worker_execution_capture"][
            "execution_replay"
        ],
        "execution_reconstruction": result["worker_execution_reconstruction"],
        "execution_replay_reference": result["worker_execution_replay_reference"],
    }


def _capture_args(result: dict, replay_dir: Path) -> dict:
    values = _binding_args(result)
    values.pop("binding_capture")
    values.update(
        {
            "captured_at": "2026-07-21T00:00:01Z",
            "replay_dir": replay_dir,
        }
    )
    return values


def _rehash(artifact: dict, field: str = "artifact_hash") -> dict:
    changed = deepcopy(artifact)
    changed.pop(field, None)
    changed[field] = replay_hash(changed)
    return changed


def _capture_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[Path, dict, object]:
    root, state = _pending_state(tmp_path, monkeypatch, name)
    supplied: dict = {}
    original = bridge.capture_completed_filesystem_replace_worker_result

    def stop_before_capture(**kwargs):
        supplied.update(deepcopy(kwargs))
        return {
            "g31_filesystem_result_capture_status": bridge.FAILED_CLOSED,
            "failure_reason": "captured R17C boundary",
        }

    monkeypatch.setattr(
        entry.filesystem_result_capture,
        "capture_completed_filesystem_replace_worker_result",
        stop_before_capture,
    )
    with pytest.raises(FailClosedRuntimeError, match="captured R17C boundary"):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    return root, supplied, original


def test_common_entry_captures_exact_worker_output_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R17C-SUCCESS")
    calls = {"binding": 0, "canonical": 0}
    original_binding = (
        entry.filesystem_result_capture.capture_completed_filesystem_replace_worker_result
    )
    original_canonical = bridge.result_capture.capture_worker_result

    def binding(**kwargs):
        calls["binding"] += 1
        return original_binding(**kwargs)

    def canonical(**kwargs):
        calls["canonical"] += 1
        return original_canonical(**kwargs)

    monkeypatch.setattr(
        entry.filesystem_result_capture,
        "capture_completed_filesystem_replace_worker_result",
        binding,
    )
    monkeypatch.setattr(bridge.result_capture, "capture_worker_result", canonical)

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    output = result["filesystem_replace_worker_output_artifact"]
    payload = output["payload"]
    request = result["authenticated_replacement_request"]
    journal = load_json(Path(request["destinations"]["journal"]))
    completion = load_json(Path(request["destinations"]["completion"]))
    reconstructed = (
        bridge.reconstruct_filesystem_replace_worker_result_capture_binding(
            **_binding_args(result)
        )
    )

    assert calls == {"binding": 1, "canonical": 1}
    assert (
        result["filesystem_replace_worker_result_capture_status"]
        == bridge.SUCCESS
    )
    assert output["artifact_type"] == bridge.FILESYSTEM_REPLACE_WORKER_OUTPUT_ARTIFACT_V1
    assert output["artifact_hash"] == replay_hash(
        {key: value for key, value in output.items() if key != "artifact_hash"}
    )
    assert output["worker_id"] == WORKER_ID
    assert output["produced_outputs"] == [request["target_path"]]
    assert output["operations"] == [OPERATION]
    assert payload["filesystem_replace_worker_capture_hash"] == result[
        "filesystem_replace_worker_capture"
    ]["capture_hash"]
    assert payload["filesystem_replace_worker_replay_hash"] == result[
        "filesystem_replace_worker_reconstruction"
    ]["replay_hash"]
    assert payload["journal_wrapper_hash"] == journal["replay_hash"]
    assert payload["completion_wrapper_hash"] == completion["replay_hash"]
    invocation = result["worker_invocation_capture"]["worker_invocation_artifact"]
    assignment = result["worker_assignment_capture"]["worker_assignment_artifact"]
    execution = result["worker_execution_capture"]["execution_artifact"]
    assert payload["worker_invocation_hash"] == invocation["artifact_hash"]
    assert payload["worker_dispatch_hash"] == invocation["worker_dispatch_hash"]
    assert payload["worker_assignment_hash"] == assignment["artifact_hash"]
    assert payload["assignment_derived_capability"] == OPERATION
    assert payload["execution_packet_hash"] == invocation["execution_packet_hash"]
    assert payload["canonical_chain_id"] == invocation["chain_id"]
    assert payload["execution_hash"] == execution["artifact_hash"]
    assert result["worker_result_captured"] is True
    assert result["result_created"] is True
    assert result["result_validated"] is True
    assert result["post_execution_replay_reviewed"] is False
    assert result["execution_certified"] is False
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert result["repository_mutated"] is True
    assert reconstructed["worker_output_hash"] == output["artifact_hash"]
    assert reconstructed["replay_artifact_count"] == 4
    assert "Filesystem Replace Worker Result Captured: True" in "\n".join(
        result["g31_canonical_presentations"]
    )


@pytest.mark.parametrize(
    "case",
    (
        "terminal_capture",
        "invocation",
        "assignment_capability",
        "execution",
        "journal",
        "completion",
    ),
)
def test_changed_worker_output_lineage_fails_before_result_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        f"R17C-TAMPER-{case}",
    )
    monkeypatch.setattr(
        bridge.result_capture,
        "capture_worker_result",
        lambda **_kwargs: pytest.fail("Result Capture must not run"),
    )
    changed = deepcopy(supplied)
    if case == "terminal_capture":
        changed["filesystem_worker_capture"]["execution_status"] = "SUBSTITUTED"
        changed["filesystem_worker_capture"] = _rehash(
            changed["filesystem_worker_capture"],
            "capture_hash",
        )
    elif case == "invocation":
        changed["worker_invocation_artifact"][
            "worker_dispatch_reference"
        ] = "SUBSTITUTED"
        changed["worker_invocation_artifact"] = _rehash(
            changed["worker_invocation_artifact"]
        )
    elif case == "assignment_capability":
        changed["worker_assignment_artifact"]["capability_id"] = "SUBSTITUTED"
        changed["worker_assignment_artifact"] = _rehash(
            changed["worker_assignment_artifact"]
        )
    elif case == "execution":
        changed["execution_artifact"]["capability_id"] = "SUBSTITUTED"
        changed["execution_artifact"] = _rehash(changed["execution_artifact"])
    else:
        key = "journal" if case == "journal" else "completion"
        path = Path(changed["authenticated_request"]["destinations"][key])
        wrapper = load_json(path)
        wrapper["artifact"]["payload"]["execution_status"] = "SUBSTITUTED"
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    changed.update(
        {
            "captured_at": "2026-07-21T00:00:01Z",
            "replay_dir": root / f"DIRECT-{case}",
        }
    )
    failed = original(**changed)

    assert (
        failed["g31_filesystem_result_capture_status"]
        == bridge.FAILED_CLOSED
    )
    assert failed["result_created"] is False


def test_duplicate_completion_and_cross_session_destination_fail_before_second_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R17C-DUPLICATE")
    calls = 0
    canonical = bridge.result_capture.capture_worker_result

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return canonical(**kwargs)

    monkeypatch.setattr(bridge.result_capture, "capture_worker_result", counted)
    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    duplicate = bridge.capture_completed_filesystem_replace_worker_result(
        **_capture_args(result, root / "SECOND-CAPTURE")
    )
    cross_session = bridge.capture_completed_filesystem_replace_worker_result(
        **_capture_args(result, tmp_path / "OTHER-SESSION" / "CAPTURE")
    )

    assert calls == 1
    assert duplicate["g31_filesystem_result_capture_status"] == bridge.FAILED_CLOSED
    assert "already captured" in duplicate["failure_reason"]
    assert (
        cross_session["g31_filesystem_result_capture_status"]
        == bridge.FAILED_CLOSED
    )
    assert "cross-session" in cross_session["failure_reason"]


def test_common_entry_uses_one_narrow_binding_and_no_generic_output() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)
    binding_source = inspect.getsource(
        bridge.capture_completed_filesystem_replace_worker_result
    )

    assert source.count(
        "capture_completed_filesystem_replace_worker_result("
    ) == 1
    assert "default_worker_output_for_invocation" not in source
    assert binding_source.count("capture_worker_result(") == 1
    assert "execute_consumed_authenticated_replace_v2" not in binding_source
    assert "default_worker_output_for_invocation" not in binding_source
