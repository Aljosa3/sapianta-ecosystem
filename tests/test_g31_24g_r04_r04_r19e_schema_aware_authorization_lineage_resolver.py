from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

from aigol.runtime import (
    filesystem_replace_worker_schema_aware_authorization_lineage_resolver_runtime
    as resolver,
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


def _rehash(value: dict, field: str = "artifact_hash") -> dict:
    changed = deepcopy(value)
    changed.pop(field, None)
    changed[field] = replay_hash(changed)
    return changed


def _binding_args(result: dict) -> dict:
    return {
        "review_binding_capture": result[
            "filesystem_replace_worker_post_execution_replay_review"
        ],
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


def _review_args(result: dict, replay_dir: Path) -> dict:
    values = _binding_args(result)
    values.pop("review_binding_capture")
    values.update(
        {
            "reviewed_at": "2026-07-25T00:00:04Z",
            "replay_dir": replay_dir,
        }
    )
    return values


def _review_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> tuple[Path, dict, object]:
    root, state = _pending_state(tmp_path, monkeypatch, name)
    supplied: dict = {}
    original = resolver.review_validated_filesystem_replace_worker_result

    def stop_before_review(**kwargs):
        supplied.update(deepcopy(kwargs))
        return {
            "g31_filesystem_post_execution_replay_review_status": (
                resolver.FAILED_CLOSED
            ),
            "failure_reason": "captured R19E boundary",
        }

    monkeypatch.setattr(
        entry.filesystem_post_execution_review,
        "review_validated_filesystem_replace_worker_result",
        stop_before_review,
    )
    with pytest.raises(FailClosedRuntimeError, match="captured R19E boundary"):
        InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    return root, supplied, original


def test_common_entry_resolves_record_hash_lineage_and_reviews_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19E-SUCCESS")
    calls = {"resolver": 0, "canonical": 0}
    original_resolver = resolver.resolve_authorization_lineage
    original_canonical = resolver.replay_review.review_validated_worker_result

    def resolved(**kwargs):
        calls["resolver"] += 1
        return original_resolver(**kwargs)

    def canonical(**kwargs):
        calls["canonical"] += 1
        return original_canonical(**kwargs)

    monkeypatch.setattr(resolver, "resolve_authorization_lineage", resolved)
    monkeypatch.setattr(
        resolver.replay_review,
        "review_validated_worker_result",
        canonical,
    )

    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)
    review_capture = result[
        "filesystem_replace_worker_post_execution_replay_review"
    ]
    review = review_capture["post_execution_replay_review_artifact"]
    validation = result[
        "filesystem_replace_worker_result_validation"
    ]["worker_result_validation_artifact"]
    reconstructed = (
        resolver.reconstruct_filesystem_replace_worker_post_execution_replay_review_binding(
            **_binding_args(result)
        )
    )

    assert calls["canonical"] == 1
    assert calls["resolver"] >= 3
    assert review["review_status"] == resolver.replay_review.REVIEW_COMPLETED
    assert review["worker_result_validation_reference"] == validation[
        "worker_result_validation_id"
    ]
    assert review["worker_result_validation_hash"] == validation[
        "artifact_hash"
    ]
    assert review_capture["authorization_lineage_schema"] == (
        resolver.AUTHENTICATED_REPLACEMENT_SCHEMA
    )
    assert review_capture["authorization_commitment_kind"] == (
        resolver.RECORD_HASH_COMMITMENT
    )
    assert review_capture["authorization_commitment"] == result[
        "authenticated_replacement_request"
    ]["authorization_hash"]
    assert result["result_validated"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert result["result_accepted"] is state["result_accepted"]
    assert result["execution_certified"] is False
    assert result["repository_mutated"] is True
    assert result["provider_invoked"] is False
    assert result["command_executed"] is False
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["post_execution_replay_reviewed"] is True
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )
    assert len(
        list(
            Path(
                result[
                    "filesystem_replace_worker_post_execution_replay_review_replay_reference"
                ]
            ).glob("*.json")
        )
    ) == 4


@pytest.mark.parametrize(
    "case",
    (
        "authorization_replay",
        "compatibility_lineage",
        "validation_artifact",
        "journal",
    ),
)
def test_substituted_lineage_fails_before_unchanged_review(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    root, supplied, original = _review_boundary(
        tmp_path,
        monkeypatch,
        f"R19E-TAMPER-{case}",
    )
    monkeypatch.setattr(
        resolver.replay_review,
        "review_validated_worker_result",
        lambda **_kwargs: pytest.fail("generic Replay Review must not run"),
    )
    changed = deepcopy(supplied)
    if case == "authorization_replay":
        path = (
            Path(changed["authenticated_request"]["authorization_replay_reference"])
            / "000_authorization_owner_resolved.json"
        )
        wrapper = load_json(path)
        wrapper["artifact"]["authorization_hash"] = "SUBSTITUTED"
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
    elif case == "compatibility_lineage":
        invocation_path = Path(
            changed["worker_invocation_replay_reference"]
        )
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
        path = request_path / "002_invocation_request_artifact_recorded.json"
        wrapper = load_json(path)
        wrapper["artifact"]["compatibility_lineage"]["lineage_type"] = (
            "SUBSTITUTED"
        )
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
    elif case == "validation_artifact":
        validation = changed["validation_binding_capture"][
            "worker_result_validation_artifact"
        ]
        validation["authorization_hash"] = "SUBSTITUTED"
        changed["validation_binding_capture"][
            "worker_result_validation_artifact"
        ] = _rehash(validation)
    else:
        request = changed["authenticated_request"]
        path = Path(request["destinations"]["journal"])
        wrapper = load_json(path)
        wrapper["artifact"]["payload"]["preimage_sha256"] = "SUBSTITUTED"
        wrapper["artifact"] = _rehash(wrapper["artifact"])
        wrapper = _rehash(wrapper, "replay_hash")
        path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")
    changed.update(
        {
            "reviewed_at": "2026-07-25T00:00:04Z",
            "replay_dir": root / f"DIRECT-{case}",
        }
    )

    failed = original(**changed)

    assert (
        failed["g31_filesystem_post_execution_replay_review_status"]
        == resolver.FAILED_CLOSED
    )
    assert failed["post_execution_replay_review_performed"] is False
    assert failed["post_execution_replay_reviewed"] is False
    assert failed["result_validated"] is True
    assert failed["repository_mutated"] is True
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )


def test_duplicate_and_cross_session_review_fail_before_second_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R19E-DUPLICATE")
    calls = 0
    original = resolver.replay_review.review_validated_worker_result

    def counted(**kwargs):
        nonlocal calls
        calls += 1
        return original(**kwargs)

    monkeypatch.setattr(
        resolver.replay_review,
        "review_validated_worker_result",
        counted,
    )
    result = InMemoryAdapter(root).transport(state, decision.MUTATION_APPROVED)

    duplicate = resolver.review_validated_filesystem_replace_worker_result(
        **_review_args(result, root / "SECOND-REVIEW")
    )
    cross_session = resolver.review_validated_filesystem_replace_worker_result(
        **_review_args(
            result,
            tmp_path / "OTHER-SESSION" / "REVIEW",
        )
    )

    assert calls == 1
    assert (
        duplicate["g31_filesystem_post_execution_replay_review_status"]
        == resolver.FAILED_CLOSED
    )
    assert "already" in duplicate["failure_reason"]
    assert (
        cross_session["g31_filesystem_post_execution_replay_review_status"]
        == resolver.FAILED_CLOSED
    )
    assert "cross-session" in cross_session["failure_reason"]
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )


def test_canonical_failure_restores_loader_and_preserves_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, supplied, original = _review_boundary(
        tmp_path,
        monkeypatch,
        "R19E-CANONICAL-INVALID",
    )
    monkeypatch.setattr(
        resolver.replay_review,
        "review_validated_worker_result",
        lambda **_kwargs: {
            "review_status": resolver.replay_review.FAILED_CLOSED,
            "failure_reason": "canonical review rejected validation",
        },
    )
    supplied.update(
        {
            "reviewed_at": "2026-07-25T00:00:04Z",
            "replay_dir": root / "CANONICAL-INVALID",
        }
    )

    invalid = original(**supplied)

    assert (
        invalid["g31_filesystem_post_execution_replay_review_status"]
        == resolver.INVALID
    )
    assert invalid["post_execution_replay_review_performed"] is True
    assert invalid["post_execution_replay_reviewed"] is False
    assert invalid["result_validated"] is True
    assert invalid["repository_mutated"] is True
    assert invalid["result_accepted"] is False
    assert invalid["execution_certified"] is False
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )


def test_resolver_is_non_authoritative_and_review_owner_is_unchanged() -> None:
    source = inspect.getsource(entry._authorize_g31_mutation_decision)
    binding_source = inspect.getsource(
        resolver.review_validated_filesystem_replace_worker_result
    )

    assert source.count(
        "review_validated_filesystem_replace_worker_result("
    ) == 1
    assert binding_source.count("review_validated_worker_result(") == 1
    assert "write_json_immutable" not in inspect.getsource(resolver)
    assert "validate_worker_result(" not in binding_source
    assert "capture_worker_result(" not in binding_source
    assert "execute_consumed_authenticated_replace_v2" not in binding_source
    assert resolver.replay_review._load_chain_artifacts is (
        resolver._ORIGINAL_CHAIN_LOADER
    )
