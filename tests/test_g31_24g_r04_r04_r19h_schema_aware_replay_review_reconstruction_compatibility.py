from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from aigol.runtime import governed_termination_runtime as termination
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import (
    filesystem_replace_worker_schema_aware_authorization_lineage_resolver_runtime
    as resolver,
)
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


def _request_artifact_path(result: dict) -> Path:
    invocation_path = Path(result["worker_invocation_replay_reference"])
    invocation_evidence = load_json(
        invocation_path / "000_invocation_evidence_recorded.json"
    )["artifact"]
    dispatch_path = Path(
        invocation_evidence["worker_dispatch_replay_reference"]
    )
    dispatch_evidence = load_json(
        dispatch_path / "000_dispatch_evidence_recorded.json"
    )["artifact"]
    assignment_path = Path(
        dispatch_evidence["worker_assignment_replay_reference"]
    )
    assignment_evidence = load_json(
        assignment_path / "000_assignment_evidence_recorded.json"
    )["artifact"]
    request_path = Path(
        assignment_evidence["worker_invocation_request_replay_reference"]
    )
    return request_path / "002_invocation_request_artifact_recorded.json"


def test_stable_reference_only_reconstruction_is_invocation_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19H-STABLE")
    original_loader = resolver.replay_review._load_chain_artifacts
    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    replay_reference = result[
        "filesystem_replace_worker_post_execution_replay_review_replay_reference"
    ]
    calls = 0
    original_reconstructor = (
        resolver.replay_review.reconstruct_post_execution_replay_review
    )

    def counted(reference, **kwargs):
        nonlocal calls
        calls += 1
        assert kwargs["chain_artifact_loader"] is (
            resolver._load_schema_aware_chain_artifacts
        )
        return original_reconstructor(reference, **kwargs)

    monkeypatch.setattr(
        resolver.replay_review,
        "reconstruct_post_execution_replay_review",
        counted,
    )

    reconstructed = (
        resolver.reconstruct_schema_aware_post_execution_replay_review(
            replay_reference
        )
    )

    assert calls == 1
    assert reconstructed["review_status"] == (
        resolver.replay_review.REVIEW_COMPLETED
    )
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["post_execution_replay_reviewed"] is True
    assert reconstructed["terminated"] is False
    assert resolver.replay_review._load_chain_artifacts is original_loader


def test_stable_reconstruction_rejects_unsupported_immutable_lineage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19H-UNSUPPORTED")
    original_loader = resolver.replay_review._load_chain_artifacts
    result = InMemoryAdapter(root).transport(
        state,
        decision.MUTATION_APPROVED,
    )
    path = _request_artifact_path(result)
    wrapper = load_json(path)
    wrapper["artifact"]["compatibility_lineage"]["lineage_type"] = (
        "UNSUPPORTED_AUTHORIZATION_LINEAGE"
    )
    wrapper["artifact"] = _rehash(wrapper["artifact"])
    wrapper = _rehash(wrapper, "replay_hash")
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        resolver.reconstruct_schema_aware_post_execution_replay_review(
            result[
                "filesystem_replace_worker_post_execution_replay_review_replay_reference"
            ]
        )

    assert resolver.replay_review._load_chain_artifacts is original_loader


def test_historical_default_and_generic_replay_owner_remain_unchanged() -> None:
    generic_source = inspect.getsource(
        resolver.replay_review.reconstruct_post_execution_replay_review
    )
    validation_source = inspect.getsource(
        resolver.replay_review._load_validation_lineage
    )
    resolver_source = inspect.getsource(resolver)

    assert "chain_artifact_loader: ChainArtifactLoader | None = None" in (
        generic_source
    )
    assert "chain_artifact_loader or _load_chain_artifacts" in (
        validation_source
    )
    assert "replay_review._load_chain_artifacts =" not in resolver_source
    assert "write_json_immutable" not in resolver_source
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )


def test_downstream_termination_uses_stable_compatibility_entry() -> None:
    assert termination.reconstruct_post_execution_replay_review is (
        resolver.reconstruct_schema_aware_post_execution_replay_review
    )
    assert "write_json_immutable" not in inspect.getsource(
        resolver.reconstruct_schema_aware_post_execution_replay_review
    )
