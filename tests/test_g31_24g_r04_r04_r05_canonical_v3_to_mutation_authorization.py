from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from test_g31_24g_r04_r04_r04_r01_common_entry_adapter_repair import (  # noqa: E402
    ACTOR,
    CREATED,
    InMemoryAdapter,
    _pending_state,
)

from aigol.authorization import authorization_runtime
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.workers import filesystem_replace_worker


def _transport(
    root: Path,
    state: dict,
    value: str,
    *,
    session: str | None = None,
    workspace: str = "/isolated/repository",
    actor: str = ACTOR,
) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="in_memory_r05_adapter",
        session_id=session or root.name,
        human_requests=[],
        created_at=CREATED,
        runtime_root=root.parent,
        workspace=workspace,
        governed_runtime_runner=lambda *_args, **_kwargs: {},
        g31_application_state=state,
        g31_human_action=value,
        g31_human_actor_id=actor,
    )


def _forbid_downstream(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls: dict[str, int] = {}
    targets = (
        (governance, "execute_g31_authenticated_replace"),
        (governance, "recover_g31_authenticated_replace"),
        (filesystem_replace_worker, "execute_filesystem_replace_request"),
        (filesystem_replace_worker, "_execute_authenticated_replace_v2"),
        (filesystem_replace_worker, "_recover_authenticated_replace_v2"),
    )
    for owner, symbol in targets:
        calls[symbol] = 0

        def forbidden(*_args, _symbol=symbol, **_kwargs):
            calls[_symbol] += 1
            raise AssertionError(f"forbidden downstream call: {_symbol}")

        monkeypatch.setattr(owner, symbol, forbidden)
    return calls


def _contains_key(value: object, forbidden: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(forbidden.intersection(value)) or any(
            _contains_key(item, forbidden) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden) for item in value)
    return False


def test_exact_approved_uses_one_canonical_authorization_and_actor_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R05-APPROVED")
    downstream = _forbid_downstream(monkeypatch)
    original = governance.create_authorization_record
    calls = {"authorization_records": 0}

    def observed(*args, **kwargs):
        calls["authorization_records"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(governance, "create_authorization_record", observed)
    state["terminal_prompt"] = "APPROVED?"
    state["slash_command"] = "/approve"
    result = _transport(root, state, decision.MUTATION_APPROVED)

    candidate = result["existing_file_mutation_candidate_capture"][
        "existing_file_mutation_candidate_artifact"
    ]
    provenance = candidate["candidate_provenance"]
    human = result["human_mutation_decision_capture"][
        "human_mutation_decision_artifact"
    ]
    authorization = result["mutation_authorization_capture"]
    reconstructed = result["mutation_authorization_actor_replay_reconstruction"]
    evidence = authorization["authorization_evidence"]

    assert calls["authorization_records"] == 1
    assert evidence["candidate_id"] == candidate["candidate_id"]
    assert evidence["candidate_hash"] == candidate["artifact_hash"]
    assert evidence["candidate_provenance_binding_hash"] == provenance["binding_hash"]
    assert evidence["mutation_decision_id"] == human["human_decision_id"]
    assert evidence["mutation_decision_hash"] == human["artifact_hash"]
    assert evidence["session_id"] == root.name
    assert evidence["repository_grounding_hash"] == provenance["repository_grounding_hash"]
    assert evidence["target_path"] == provenance["target_path"]
    assert evidence["expected_source_sha256"] == provenance["preimage_sha256"]
    assert reconstructed["canonical_authorization_actor"] == (
        authorization_runtime.CANONICAL_AUTHORIZATION_ACTOR
    )
    assert reconstructed["mutation_decision_actor"] == ACTOR
    assert reconstructed["mutation_authorized"] is True
    assert reconstructed["authorization_actor_bound"] is True
    assert reconstructed["authorization_replay_recorded"] is True
    assert reconstructed["authorization_consumed"] is False
    assert reconstructed["replace_request_created"] is False
    assert result["replace_request_created"] is True
    assert result["authenticated_replacement_request"]["authorization_hash"] == (
        reconstructed["authorization_hash"]
    )
    assert result["g31_pending_action"] is None
    assert result["repository_mutated"] is False
    assert result["main_repository_mutated"] is False
    assert len(list((root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").glob("*.json"))) == 3
    assert "Canonical Existing-File Mutation Authorization" in "\n".join(
        result["g31_canonical_presentations"]
    )
    assert not _contains_key(
        {
            "authorization": authorization,
            "actor_replay": result["mutation_authorization_actor_replay_capture"],
        },
        {"terminal_prompt", "slash_command", "interface_name"},
    )
    assert all(count == 0 for count in downstream.values())


def test_exact_rejected_is_terminal_and_calls_no_authorization_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R05-REJECTED")
    downstream = _forbid_downstream(monkeypatch)
    calls = {"authorize": 0, "bind": 0}

    def forbidden_authorize(*_args, **_kwargs):
        calls["authorize"] += 1
        raise AssertionError("REJECTED cannot authorize")

    def forbidden_bind(*_args, **_kwargs):
        calls["bind"] += 1
        raise AssertionError("REJECTED cannot bind authorization Replay")

    monkeypatch.setattr(
        governance, "authorize_g31_approved_existing_file_mutation", forbidden_authorize
    )
    monkeypatch.setattr(
        governance, "bind_g31_mutation_authorization_actor_and_replay", forbidden_bind
    )
    result = _transport(root, state, decision.REJECTED)

    assert result["human_mutation_decision_reconstruction"]["decision_outcome"] == (
        decision.REJECTED
    )
    assert result["mutation_decision_approved"] is False
    assert result["mutation_authorized"] is False
    assert result["authorization_actor_bound"] is False
    assert result["authorization_replay_recorded"] is False
    assert result["g31_pending_action"] is None
    assert calls == {"authorize": 0, "bind": 0}
    assert not (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists()
    assert all(count == 0 for count in downstream.values())


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("existing_file_mutation_candidate_reconstruction", {"replay_hash": "changed"}),
        ("codex_worker_activation_binding_reconstruction", {"lineage": {}}),
        ("repository_grounding_artifact", {"grounding_evidence_hash": "changed"}),
    ),
)
def test_changed_candidate_activation_or_grounding_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: dict,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R05-TAMPER-{field}")
    state[field] = value
    with pytest.raises(FailClosedRuntimeError):
        _transport(root, state, decision.MUTATION_APPROVED)
    assert not (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists()


def test_decision_replay_substitution_fails_before_authorization_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R05-DECISION-REPLAY")
    original = decision.reconstruct_existing_file_mutation_decision_replay
    calls = {"count": 0}

    def changing_reconstruction(*args, **kwargs):
        calls["count"] += 1
        result = original(*args, **kwargs)
        if calls["count"] > 1:
            result = {**result, "replay_hash": "substituted"}
        return result

    monkeypatch.setattr(
        decision,
        "reconstruct_existing_file_mutation_decision_replay",
        changing_reconstruction,
    )
    with pytest.raises(FailClosedRuntimeError, match="reconstructed V3 decision"):
        _transport(root, state, decision.MUTATION_APPROVED)
    assert calls["count"] >= 2
    assert not (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists()


@pytest.mark.parametrize(
    "change",
    ("actor", "repository", "session"),
)
def test_actor_repository_and_session_substitution_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, f"R05-{change}")
    kwargs = {}
    if change == "actor":
        kwargs["actor"] = "OTHER_ACTOR"
    elif change == "repository":
        kwargs["workspace"] = "/other/repository"
    else:
        kwargs["session"] = "OTHER-SESSION"
    with pytest.raises(FailClosedRuntimeError):
        _transport(root, state, decision.MUTATION_APPROVED, **kwargs)
    assert not (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").exists()


def test_duplicate_public_transition_fails_before_second_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, state = _pending_state(tmp_path, monkeypatch, "R05-DUPLICATE")
    original = governance.authorize_g31_approved_existing_file_mutation
    calls = {"authorize": 0}

    def observed(*args, **kwargs):
        calls["authorize"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        governance, "authorize_g31_approved_existing_file_mutation", observed
    )
    first = _transport(root, state, decision.MUTATION_APPROVED)
    replay_files = sorted(
        (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").glob("*.json")
    )
    with pytest.raises(FailClosedRuntimeError):
        _transport(root, state, decision.MUTATION_APPROVED)
    assert calls["authorize"] == 1
    assert replay_files == sorted(
        (root / "G31_MUTATION_AUTHORIZATION_REPLAY_V1").glob("*.json")
    )
    assert first["authorization_consumed"] is False


def test_shared_entry_and_static_adapter_boundaries() -> None:
    repository = Path(__file__).resolve().parents[1]
    aicli = (repository / "aigol/cli/aicli.py").read_text(encoding="utf-8")
    service = (
        repository / "aigol/runtime/human_interface_runtime_entry_service.py"
    ).read_text(encoding="utf-8")
    canonical = (
        repository / "aigol/runtime/platform_core_existing_file_governance.py"
    ).read_text(encoding="utf-8")

    assert "run_human_interface_runtime_entry(" in aicli
    assert "authorize_g31_approved_existing_file_mutation(" not in aicli
    assert "bind_g31_mutation_authorization_actor_and_replay(" not in aicli
    assert "create_g31_authenticated_replace_request(" in service
    assert "create_g31_authenticated_replace_request(" not in aicli
    assert "record_authenticated_replace_request_v2(" not in aicli
    assert "aigol.cli" not in service
    assert "aigol.cli" not in canonical
    assert "aicli" not in InMemoryAdapter.transport.__code__.co_names
