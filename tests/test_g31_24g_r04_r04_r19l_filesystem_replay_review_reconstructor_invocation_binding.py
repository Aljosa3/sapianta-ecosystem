from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime import governed_termination_runtime as termination
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import human_interface_runtime_entry_service as entry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
)
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (
    InMemoryAdapter,
    _pending_state,
)
from test_g31_24g_r04_r04_r19e_schema_aware_authorization_lineage_resolver import (
    _rehash,
)
from test_g31_24g_r04_r04_r19h_schema_aware_replay_review_reconstruction_compatibility import (
    _request_artifact_path,
)


def test_common_entry_supplies_filesystem_reconstructor_per_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19L-SUCCESS")
    supplied: list[object] = []
    original_terminate = termination.terminate_reviewed_operation
    original_reconstruct = termination.reconstruct_governed_termination_replay

    def terminate_once(**kwargs):
        supplied.append(kwargs["replay_review_reconstructor"])
        return original_terminate(**kwargs)

    def reconstruct_once(replay_dir, **kwargs):
        supplied.append(kwargs["replay_review_reconstructor"])
        return original_reconstruct(replay_dir, **kwargs)

    monkeypatch.setattr(
        entry.governed_termination,
        "terminate_reviewed_operation",
        terminate_once,
    )
    monkeypatch.setattr(
        entry.governed_termination,
        "reconstruct_governed_termination_replay",
        reconstruct_once,
    )

    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    capture = result["filesystem_replace_worker_governed_termination"]
    reconstructed = result[
        "filesystem_replace_worker_governed_termination_reconstruction"
    ]
    replay_reference = Path(
        result[
            "filesystem_replace_worker_governed_termination_replay_reference"
        ]
    )

    assert supplied == [
        entry.filesystem_post_execution_review.reconstruct_schema_aware_post_execution_replay_review,
        entry.filesystem_post_execution_review.reconstruct_schema_aware_post_execution_replay_review,
    ]
    assert capture["termination_status"] == termination.TERMINATED
    assert reconstructed["termination_status"] == termination.TERMINATED
    assert reconstructed["post_execution_replay_reviewed"] is True
    assert reconstructed["terminated"] is True
    assert result["terminated"] is True
    assert result["execution_certified"] is False
    assert result["governance_mutated"] is False
    assert result["replay_mutated"] is False
    assert len(list(replay_reference.glob("*.json"))) == 4


def test_unverified_compatibility_projection_fails_before_termination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19L-PROJECTION")

    def unsupported_lineage(**kwargs):
        raise FailClosedRuntimeError(
            "unsupported immutable Authorization lineage"
        )

    monkeypatch.setattr(
        entry.filesystem_post_execution_review,
        "resolve_authorization_lineage",
        unsupported_lineage,
    )
    monkeypatch.setattr(
        entry.governed_termination,
        "terminate_reviewed_operation",
        lambda **_kwargs: pytest.fail(
            "Governed Termination must not run before immutable lineage admission"
        ),
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Post-Execution Replay Review failed",
    ):
        InMemoryAdapter(root).transport(
            state,
            decision.MUTATION_APPROVED,
        )


def test_substituted_immutable_lineage_fails_closed_in_injected_reconstructor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19L-SUBSTITUTED")
    original = termination.terminate_reviewed_operation

    def substitute_then_terminate(**kwargs):
        review_replay = Path(
            kwargs["post_execution_replay_review_replay_reference"]
        )
        review_evidence = load_json(
            review_replay / "000_review_evidence_recorded.json"
        )["artifact"]
        validation_replay = Path(
            review_evidence["worker_result_validation_replay_reference"]
        )
        validation_evidence = load_json(
            validation_replay / "000_validation_evidence_recorded.json"
        )["artifact"]
        result_capture_replay = Path(
            validation_evidence["worker_result_capture_replay_reference"]
        )
        result_capture_evidence = load_json(
            result_capture_replay / "000_result_capture_evidence_recorded.json"
        )["artifact"]
        review_result = {
            "worker_invocation_replay_reference": result_capture_evidence[
                "worker_invocation_replay_reference"
            ]
        }
        path = _request_artifact_path(review_result)
        wrapper = load_json(path)
        wrapper["artifact"]["compatibility_lineage"]["lineage_type"] = (
            "UNSUPPORTED_AUTHORIZATION_LINEAGE"
        )
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
        return original(**kwargs)

    monkeypatch.setattr(
        entry.governed_termination,
        "terminate_reviewed_operation",
        substitute_then_terminate,
    )

    with pytest.raises(
        FailClosedRuntimeError,
        match="Governed Termination failed",
    ):
        InMemoryAdapter(root).transport(
            state,
            decision.MUTATION_APPROVED,
        )

    replay_dirs = list(root.glob("GOVERNED-TERMINATION-*"))
    assert len(replay_dirs) == 1
    assert sorted(path.name for path in replay_dirs[0].glob("*.json")) == [
        "003_termination_result_recorded.json"
    ]
    result = load_json(
        replay_dirs[0] / "003_termination_result_recorded.json"
    )["artifact"]
    assert result["termination_status"] == termination.FAILED_CLOSED
    assert result["governed_termination_reference"] is None
    assert result["terminated"] is False


def test_binding_is_filesystem_scoped_and_generic_defaults_remain_unchanged() -> None:
    entry_source = inspect.getsource(entry)
    termination_source = inspect.getsource(termination)
    terminate_parameter = inspect.signature(
        termination.terminate_reviewed_operation
    ).parameters["replay_review_reconstructor"]
    reconstruct_parameter = inspect.signature(
        termination.reconstruct_governed_termination_replay
    ).parameters["replay_review_reconstructor"]

    assert terminate_parameter.default is (
        termination.reconstruct_post_execution_replay_review
    )
    assert reconstruct_parameter.default is (
        termination.reconstruct_post_execution_replay_review
    )
    assert (
        "filesystem_post_execution_review."
        "reconstruct_schema_aware_post_execution_replay_review"
    ) in entry_source
    assert (
        "filesystem_replace_worker_schema_aware_authorization_lineage"
        not in termination_source
    )
    assert "replay_review_reconstructor_registry" not in entry_source
    assert "contextmanager" not in entry_source
    assert "RLock" not in entry_source
