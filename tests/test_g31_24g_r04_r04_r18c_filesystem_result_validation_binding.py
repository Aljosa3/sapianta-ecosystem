from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import (
    filesystem_replace_worker_result_capture_to_result_validation_binding_runtime
    as bridge,
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


def _rehash(artifact: dict, field: str = "artifact_hash") -> dict:
    changed = deepcopy(artifact)
    changed.pop(field, None)
    changed[field] = replay_hash(changed)
    return changed


def _binding_args(result: dict) -> dict:
    return {
        "validation_binding_capture": result[
            "filesystem_replace_worker_result_validation"
        ],
        "result_capture_binding_capture": result[
            "filesystem_replace_worker_result_capture"
        ],
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


def _validation_args(result: dict, replay_dir: Path) -> dict:
    values = _binding_args(result)
    values.pop("validation_binding_capture")
    values.update(
        {
            "validated_at": "2026-07-21T00:00:02Z",
            "replay_dir": replay_dir,
        }
    )
    return values


def _capture_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[Path, dict, object]:
    root, state = _pending_state(tmp_path, monkeypatch, name)
    supplied: dict = {}
    original = bridge.validate_captured_filesystem_replace_worker_result

    def stop_before_validation(**kwargs):
        supplied.update(deepcopy(kwargs))
        return {
            "g31_filesystem_result_validation_status": bridge.FAILED_CLOSED,
            "failure_reason": "captured R18C boundary",
        }

    monkeypatch.setattr(
        entry.filesystem_result_validation,
        "validate_captured_filesystem_replace_worker_result",
        stop_before_validation,
    )
    with pytest.raises(FailClosedRuntimeError, match="captured R18C boundary"):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    return root, supplied, original


def test_common_entry_validates_exact_filesystem_result_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R18C-SUCCESS")
    calls = {"binding": 0, "canonical": 0}
    original_binding = (
        bridge.validate_captured_filesystem_replace_worker_result
    )
    original_canonical = bridge.result_validation.validate_worker_result

    def binding(**kwargs):
        calls["binding"] += 1
        return original_binding(**kwargs)

    def canonical(**kwargs):
        calls["canonical"] += 1
        return original_canonical(**kwargs)

    monkeypatch.setattr(
        entry.filesystem_result_validation,
        "validate_captured_filesystem_replace_worker_result",
        binding,
    )
    monkeypatch.setattr(
        bridge.result_validation,
        "validate_worker_result",
        canonical,
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    validation_capture = result[
        "filesystem_replace_worker_result_validation"
    ]
    validation = validation_capture["worker_result_validation_artifact"]
    request_binding = validation_capture["validation_request_binding"]
    result_capture = result[
        "filesystem_replace_worker_result_capture"
    ]["worker_result_capture_artifact"]
    output = result["filesystem_replace_worker_output_artifact"]
    reconstructed = (
        bridge.reconstruct_filesystem_replace_worker_result_validation_binding(
            **_binding_args(result)
        )
    )

    assert calls == {"binding": 1, "canonical": 1}
    assert (
        result["filesystem_replace_worker_result_validation_status"]
        == bridge.SUCCESS
    )
    assert validation["validation_status"] == bridge.result_validation.RESULT_VALIDATED
    assert validation["worker_result_capture_reference"] == result_capture[
        "worker_result_capture_id"
    ]
    assert validation["worker_result_capture_hash"] == result_capture[
        "artifact_hash"
    ]
    assert validation["worker_output_reference"] == output["worker_output_id"]
    assert validation["worker_output_hash"] == output["artifact_hash"]
    assert request_binding["worker_output_payload_hash"] == replay_hash(
        output["payload"]
    )
    assert request_binding["filesystem_replace_worker_capture_hash"] == result[
        "filesystem_replace_worker_capture"
    ]["capture_hash"]
    assert request_binding["filesystem_replace_worker_replay_hash"] == result[
        "filesystem_replace_worker_reconstruction"
    ]["replay_hash"]
    assert result["worker_result_captured"] is True
    assert result["result_created"] is True
    assert result["result_validated"] is True
    assert result["repository_mutated"] is True
    assert result["main_repository_mutated"] is True
    assert result["post_execution_replay_reviewed"] is False
    assert result["execution_certified"] is False
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert validation["task_outcome_satisfaction_evaluated"] is False
    assert validation["task_outcome_satisfied"] is False
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["result_validated"] is True
    assert reconstructed["repository_mutated"] is True
    assert len(
        list(
            Path(
                result[
                    "filesystem_replace_worker_result_validation_replay_reference"
                ]
            ).glob("*.json")
        )
    ) == 4
    rendered = "\n".join(result["g31_canonical_presentations"])
    assert "Filesystem Replace Worker Result Validated: True" in rendered
    assert (
        "validated for governance policy and lineage" in rendered
    )
    assert "Task outcome satisfaction has not been evaluated." in rendered


@pytest.mark.parametrize(
    "case",
    (
        "worker_output",
        "terminal_capture",
        "worker_replay",
        "journal",
        "result_capture",
        "assignment",
    ),
)
def test_substituted_filesystem_evidence_fails_before_generic_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        f"R18C-TAMPER-{case}",
    )
    monkeypatch.setattr(
        bridge.result_validation,
        "validate_worker_result",
        lambda **_kwargs: pytest.fail("generic Result Validation must not run"),
    )
    changed = deepcopy(supplied)
    if case == "worker_output":
        output = changed["result_capture_binding_capture"][
            "filesystem_replace_worker_output_artifact"
        ]
        output["payload"]["postimage_sha256"] = "SUBSTITUTED"
        changed["result_capture_binding_capture"][
            "filesystem_replace_worker_output_artifact"
        ] = _rehash(output)
    elif case == "terminal_capture":
        capture = changed["filesystem_worker_capture"]
        capture["execution_status"] = "SUBSTITUTED"
        changed["filesystem_worker_capture"] = _rehash(capture, "capture_hash")
    elif case == "worker_replay":
        changed["filesystem_worker_reconstruction"]["replay_hash"] = "SUBSTITUTED"
    elif case == "journal":
        request = changed["authenticated_request"]
        path = Path(request["destinations"]["journal"])
        wrapper = load_json(path)
        wrapper["artifact"]["payload"]["preimage_sha256"] = "SUBSTITUTED"
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
    elif case == "result_capture":
        capture = changed["result_capture_binding_capture"][
            "worker_result_capture_artifact"
        ]
        capture["worker_output_hash"] = "SUBSTITUTED"
        changed["result_capture_binding_capture"][
            "worker_result_capture_artifact"
        ] = _rehash(capture)
    else:
        assignment = changed["worker_assignment_artifact"]
        assignment["capability_id"] = "SUBSTITUTED"
        changed["worker_assignment_artifact"] = _rehash(assignment)
    changed.update(
        {
            "validated_at": "2026-07-21T00:00:02Z",
            "replay_dir": root / f"DIRECT-{case}",
        }
    )

    failed = original(**changed)

    assert (
        failed["g31_filesystem_result_validation_status"]
        == bridge.FAILED_CLOSED
    )
    assert failed["semantic_validation_performed"] is False
    assert failed["result_validated"] is False
    assert failed["repository_mutated"] is True


def test_duplicate_and_cross_session_validation_fail_before_second_canonical_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R18C-DUPLICATE")
    calls = 0
    original = bridge.result_validation.validate_worker_result

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return original(**kwargs)

    monkeypatch.setattr(bridge.result_validation, "validate_worker_result", counted)
    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    duplicate = bridge.validate_captured_filesystem_replace_worker_result(
        **_validation_args(result, root / "SECOND-VALIDATION")
    )
    cross_session = bridge.validate_captured_filesystem_replace_worker_result(
        **_validation_args(
            result,
            tmp_path / "OTHER-SESSION" / "VALIDATION",
        )
    )

    assert calls == 1
    assert (
        duplicate["g31_filesystem_result_validation_status"]
        == bridge.FAILED_CLOSED
    )
    assert "already" in duplicate["failure_reason"]
    assert duplicate["repository_mutated"] is True
    assert (
        cross_session["g31_filesystem_result_validation_status"]
        == bridge.FAILED_CLOSED
    )
    assert "cross-session" in cross_session["failure_reason"]
    assert cross_session["repository_mutated"] is True


def test_canonical_failed_closed_is_reported_without_erasing_worker_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        "R18C-CANONICAL-INVALID",
    )
    monkeypatch.setattr(
        bridge.result_validation,
        "validate_worker_result",
        lambda **_kwargs: {
            "validation_status": bridge.result_validation.FAILED_CLOSED,
            "failure_reason": "canonical validation rejected result",
        },
    )
    supplied.update(
        {
            "validated_at": "2026-07-21T00:00:02Z",
            "replay_dir": root / "CANONICAL-INVALID",
        }
    )

    invalid = original(**supplied)

    assert invalid["g31_filesystem_result_validation_status"] == bridge.INVALID
    assert invalid["semantic_validation_performed"] is True
    assert invalid["result_validated"] is False
    assert invalid["repository_mutated"] is True
    assert invalid["result_accepted"] is False
    assert invalid["post_execution_replay_reviewed"] is False
    assert invalid["execution_certified"] is False


def test_common_entry_uses_one_validation_binding_and_no_second_owner() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)
    binding_source = inspect.getsource(
        bridge.validate_captured_filesystem_replace_worker_result
    )

    assert source.count(
        "validate_captured_filesystem_replace_worker_result("
    ) == 1
    assert binding_source.count("validate_worker_result(") == 1
    assert "capture_worker_result(" not in binding_source
    assert "execute_consumed_authenticated_replace_v2" not in binding_source
    assert "write_json_immutable" not in binding_source
