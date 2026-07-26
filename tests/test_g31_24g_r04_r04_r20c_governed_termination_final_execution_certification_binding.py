from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import (
    governed_termination_to_final_execution_certification_binding_runtime
    as binding,
)
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime.models import FailClosedRuntimeError
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)


def _capture_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[Path, dict, object]:
    root, state = _pending_state(tmp_path, monkeypatch, name)
    supplied: dict = {}
    original = binding.certify_governed_termination

    def stop_before_certification(**kwargs):
        supplied.update(kwargs)
        return {
            "binding_status": binding.FAILED_CLOSED,
            "failure_reason": "captured R20C boundary",
        }

    monkeypatch.setattr(
        entry.final_execution_certification,
        "certify_governed_termination",
        stop_before_certification,
    )
    with pytest.raises(FailClosedRuntimeError, match="captured R20C boundary"):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    return root, supplied, original


def test_common_entry_certifies_exact_terminal_lifecycle_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R20C-SUCCESS")
    calls = {"binding": 0, "owner": 0, "reconstruction": 0}
    original_binding = binding.certify_governed_termination
    original_owner = binding.replay_certification.certify_validated_replay

    def bind_once(**kwargs):
        calls["binding"] += 1
        supplied_reconstructor = kwargs["termination_reconstructor"]

        def reconstruct_once(replay_reference):
            calls["reconstruction"] += 1
            return supplied_reconstructor(replay_reference)

        kwargs["termination_reconstructor"] = reconstruct_once
        return original_binding(**kwargs)

    def certify_once(**kwargs):
        calls["owner"] += 1
        return original_owner(**kwargs)

    monkeypatch.setattr(
        entry.final_execution_certification,
        "certify_governed_termination",
        bind_once,
    )
    monkeypatch.setattr(
        binding.replay_certification,
        "certify_validated_replay",
        certify_once,
    )

    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    capture = result[
        "filesystem_replace_worker_final_execution_certification"
    ]
    projection = capture[
        "result_validation_compatibility_projection"
    ]
    certification = capture["final_execution_certification"][
        "replay_certification_artifact"
    ]

    assert calls == {"binding": 1, "owner": 1, "reconstruction": 1}
    assert capture["binding_status"] == binding.SUCCESS
    assert capture["certification_called"] is True
    assert capture["execution_certified"] is True
    assert result["execution_certified"] is True
    assert projection["artifact_type"] == binding.RESULT_VALIDATION_ARTIFACT_V1
    assert projection["non_authoritative"] is True
    assert projection["source_governed_termination_hash"] == result[
        "filesystem_replace_worker_governed_termination"
    ]["governed_termination_artifact"]["artifact_hash"]
    assert projection["replay_references"] == capture[
        "ordered_replay_references"
    ]
    assert projection["replay_hashes"] == capture["ordered_replay_hashes"]
    assert len(projection["replay_references"]) == 5
    assert certification["source_result_validation_hash"] == projection[
        "artifact_hash"
    ]
    assert certification["replay_references"] == projection[
        "replay_references"
    ]
    assert certification["replay_hashes"] == projection["replay_hashes"]
    assert capture["authority_flags"] == binding.AUTHORITY_FLAGS
    assert capture["governance_mutated"] is False
    assert capture["replay_mutated"] is False


def test_substituted_terminal_capture_rejected_before_certification(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        "R20C-SUBSTITUTED",
    )
    terminal = deepcopy(supplied["terminal_capture"])
    terminal["governed_termination_artifact"]["worker_id"] = (
        "SUBSTITUTED-WORKER"
    )
    owner_calls = 0

    def owner_must_not_run(**_kwargs):
        nonlocal owner_calls
        owner_calls += 1
        pytest.fail("Certification must not run for substituted evidence")

    monkeypatch.setattr(
        binding.replay_certification,
        "certify_validated_replay",
        owner_must_not_run,
    )
    supplied["terminal_capture"] = terminal
    supplied["replay_dir"] = root / "R20C-SUBSTITUTED-CERTIFICATION"
    result = original(**supplied)

    assert owner_calls == 0
    assert result["binding_status"] == binding.FAILED_CLOSED
    assert result["certification_called"] is False
    assert result["execution_certified"] is False
    assert "substituted" in result["failure_reason"]


def test_cross_session_and_unsupported_lineage_rejected_before_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        "R20C-CROSS-SESSION",
    )
    owner_calls = 0

    def owner_must_not_run(**_kwargs):
        nonlocal owner_calls
        owner_calls += 1
        pytest.fail("Certification must not run before lineage admission")

    monkeypatch.setattr(
        binding.replay_certification,
        "certify_validated_replay",
        owner_must_not_run,
    )
    cross_session = dict(supplied)
    cross_session["replay_dir"] = tmp_path / "OTHER-SESSION" / "CERTIFICATION"
    crossed = original(**cross_session)
    assert crossed["binding_status"] == binding.FAILED_CLOSED
    assert crossed["certification_called"] is False
    assert "crosses session" in crossed["failure_reason"]

    unsupported = dict(supplied)
    unsupported["replay_dir"] = root / "R20C-UNSUPPORTED-CERTIFICATION"

    def unsupported_reconstruction(_replay_reference):
        raise FailClosedRuntimeError("unsupported immutable lineage")

    unsupported["termination_reconstructor"] = unsupported_reconstruction
    rejected = original(**unsupported)
    assert rejected["binding_status"] == binding.FAILED_CLOSED
    assert rejected["certification_called"] is False
    assert rejected["failure_reason"] == "unsupported immutable lineage"
    assert owner_calls == 0


def test_duplicate_terminal_certification_rejected_before_second_owner_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, supplied, original = _capture_boundary(
        tmp_path,
        monkeypatch,
        "R20C-DUPLICATE",
    )
    owner_calls = 0
    original_owner = binding.replay_certification.certify_validated_replay

    def owner_once(**kwargs):
        nonlocal owner_calls
        owner_calls += 1
        return original_owner(**kwargs)

    monkeypatch.setattr(
        binding.replay_certification,
        "certify_validated_replay",
        owner_once,
    )
    supplied["replay_dir"] = root / "R20C-FIRST-CERTIFICATION"
    first = original(**supplied)
    assert first["binding_status"] == binding.SUCCESS
    assert owner_calls == 1

    duplicate_args = dict(supplied)
    duplicate_args["binding_id"] = "R20C-ALTERNATE-BINDING"
    duplicate_args["replay_dir"] = root / "R20C-SECOND-CERTIFICATION"
    duplicate = original(**duplicate_args)
    assert duplicate["binding_status"] == binding.FAILED_CLOSED
    assert duplicate["certification_called"] is False
    assert "duplicate certification" in duplicate["failure_reason"]
    assert owner_calls == 1


def test_binding_is_adapter_neutral_and_non_authoritative() -> None:
    source = inspect.getsource(binding)

    assert "filesystem_replace_worker" not in source
    assert "registry" not in source
    assert "contextmanager" not in source
    assert "ContextVar" not in source
    assert "RLock" not in source
    assert all(value is False for value in binding.AUTHORITY_FLAGS.values())
    assert (
        binding.replay_certification.certify_validated_replay
        is not None
    )
