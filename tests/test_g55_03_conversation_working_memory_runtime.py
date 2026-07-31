from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import inspect
import json
import os
from pathlib import Path
import stat

import pytest

from aigol.runtime import (
    platform_core_conversation_working_memory_runtime as cwm_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_conversation_working_memory_runtime import (
    CANDIDATE_READY,
    COMMITTED,
    COMMITTING,
    EXPLORING,
    MAX_COLLECTION_ITEMS,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1,
    cleanup_conversation_working_memory_state,
    conversation_working_memory_state_path,
    create_conversation_working_memory_state,
    load_conversation_working_memory_state,
    recover_conversation_working_memory_state,
    replace_conversation_working_memory_state_atomically,
    update_conversation_working_memory_state,
    validate_conversation_working_memory_state,
)


WORKSPACE = "/workspace/sapianta"
SESSION = "G55-03-CWM-SESSION"
CREATED = "2026-07-31T10:00:00Z"
UPDATED = "2026-07-31T10:01:00Z"
OBSERVED = "2026-07-31T10:02:00Z"


def _create(tmp_path: Path, **overrides):
    arguments = {
        "runtime_root": tmp_path,
        "workspace_identity": WORKSPACE,
        "session_identity": SESSION,
        "created_at": CREATED,
    }
    arguments.update(overrides)
    return create_conversation_working_memory_state(**arguments)


def _canonical_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _with_integrity(state: dict) -> dict:
    candidate = deepcopy(state)
    candidate.pop("integrity_checksum", None)
    candidate["integrity_checksum"] = (
        "sha256:" + hashlib.sha256(_canonical_bytes(candidate)).hexdigest()
    )
    return candidate


def test_create_state_is_bounded_non_authoritative_and_owner_only(
    tmp_path: Path,
) -> None:
    state = _create(
        tmp_path,
        topic="  Conversation   memory ",
        entities=["Platform Core", "Human"],
        inferred_intent=" Explore a design ",
        confirmed_facts=["CWM is temporary"],
        assumptions=["A later gate will commit"],
        unresolved_ambiguity=["Exact Objective is unresolved"],
        confidence=0.5,
        discarded_interpretations=["Immediate execution"],
        context_references=["human-turn:local-only"],
        candidate_objective_snapshot={"subject": "CWM"},
    )

    assert state["runtime_version"] == (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V1
    )
    assert state["runtime_owner"] == (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER
    )
    assert state["revision"] == 0
    assert state["lifecycle_state"] == EXPLORING
    assert state["topic"] == "Conversation memory"
    assert state["candidate_digest"].startswith("sha256:")
    assert state["constitutional_artifact"] is False
    assert state["constitutional_authority"] is False
    assert state["replay_visible"] is False
    assert state["authorization_eligible"] is False
    assert state["worker_eligible"] is False
    assert state["objective_creation_supported"] is False
    assert state["capability_routing_supported"] is False
    assert "artifact_hash" not in state
    assert "artifact_type" not in state
    assert "replay_hash" not in state
    assert "replay_reference" not in state

    path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    assert path.exists()
    assert WORKSPACE not in str(path)
    assert SESSION not in str(path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    store_root = path.parents[2]
    assert store_root.name == "conversation"
    assert store_root.parent.name == ".platform-core-working"
    for owned_directory in (
        path.parent,
        path.parent.parent,
        store_root,
        store_root.parent,
    ):
        assert stat.S_IMODE(owned_directory.stat().st_mode) == 0o700
    assert stat.S_IMODE((store_root / ".cwm.lock").stat().st_mode) == 0o600
    assert len(path.read_bytes()) <= 65_536
    assert not list(path.parent.glob("*.tmp"))


def test_load_and_restart_recovery_are_deterministic(tmp_path: Path) -> None:
    created = _create(tmp_path, topic="Restart-safe state")
    path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    exact_bytes = path.read_bytes()

    loaded = load_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED,
    )
    recovered = recover_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED,
    )

    assert loaded == created
    assert recovered == created
    assert path.read_bytes() == exact_bytes
    assert validate_conversation_working_memory_state(recovered) == created


def test_update_increments_revision_and_replaces_state_atomically(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    original_inode = path.stat().st_ino
    snapshot = {
        "subject": "Conversation Working Memory runtime",
        "outcome": "isolated mutable state",
    }

    updated = update_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        updated_at=UPDATED,
        lifecycle_state=CANDIDATE_READY,
        topic="CWM runtime",
        entities=["Platform Core"],
        inferred_intent="Prepare an Objective candidate",
        unresolved_ambiguity=[],
        candidate_objective_snapshot=snapshot,
        confidence=0.9,
    )

    assert updated["revision"] == 1
    assert updated["lifecycle_state"] == CANDIDATE_READY
    assert updated["candidate_objective_snapshot"] == snapshot
    assert updated["candidate_digest"].startswith("sha256:")
    assert path.stat().st_ino != original_inode
    assert not list(path.parent.glob(".state.*.tmp"))
    assert (
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )
        == updated
    )


def test_stale_revision_and_commit_lifecycle_fail_closed(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    update_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        updated_at=UPDATED,
        topic="First update",
    )

    with pytest.raises(FailClosedRuntimeError, match="revision is stale"):
        update_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=OBSERVED,
            topic="Stale update",
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="reserved for a future commitment runtime",
    ):
        update_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=1,
            updated_at=OBSERVED,
            lifecycle_state=COMMITTING,
        )


def test_placeholder_commit_lifecycle_is_schema_supported_only(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    for lifecycle in (COMMITTING, COMMITTED):
        placeholder = deepcopy(state)
        placeholder["lifecycle_state"] = lifecycle
        placeholder = _with_integrity(placeholder)
        assert (
            validate_conversation_working_memory_state(placeholder)[
                "lifecycle_state"
            ]
            == lifecycle
        )


def test_public_atomic_replacement_validates_revision_and_invariants(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    replacement = deepcopy(state)
    replacement["revision"] = 1
    replacement["updated_at"] = UPDATED
    replacement["topic"] = "Prepared replacement"
    replacement = _with_integrity(replacement)

    stored = replace_conversation_working_memory_state_atomically(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=replacement,
        observed_at=UPDATED,
    )

    assert stored == replacement
    changed_owner = deepcopy(stored)
    changed_owner["revision"] = 2
    changed_owner["updated_at"] = OBSERVED
    changed_owner["runtime_owner"] = "OTHER_OWNER"
    changed_owner = _with_integrity(changed_owner)
    with pytest.raises(
        FailClosedRuntimeError, match="authority boundary is invalid"
    ):
        replace_conversation_working_memory_state_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=1,
            replacement_state=changed_owner,
            observed_at=OBSERVED,
        )


def test_integrity_corruption_fails_closed(tmp_path: Path) -> None:
    _create(tmp_path, topic="Untampered")
    path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    corrupt = json.loads(path.read_text(encoding="utf-8"))
    corrupt["topic"] = "Tampered without checksum"
    path.write_text(json.dumps(corrupt), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="integrity mismatch"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )
    with pytest.raises(FailClosedRuntimeError, match="integrity mismatch"):
        recover_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )


def test_invalid_json_and_oversized_state_fail_closed(tmp_path: Path) -> None:
    _create(tmp_path)
    path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    path.write_bytes(b"{not-json")
    with pytest.raises(FailClosedRuntimeError, match="state is corrupt"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )

    cleanup_root = tmp_path / "bounded"
    _create(cleanup_root)
    with pytest.raises(FailClosedRuntimeError, match="exceeds item bound"):
        update_conversation_working_memory_state(
            runtime_root=cleanup_root,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=UPDATED,
            entities=[
                f"entity-{index}"
                for index in range(MAX_COLLECTION_ITEMS + 1)
            ],
        )
    with pytest.raises(
        FailClosedRuntimeError,
        match="candidate Objective snapshot exceeds storage bound",
    ):
        update_conversation_working_memory_state(
            runtime_root=cleanup_root,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=UPDATED,
            candidate_objective_snapshot={"content": "x" * 17_000},
        )
    with pytest.raises(
        FailClosedRuntimeError,
        match="contains forbidden identity",
    ):
        update_conversation_working_memory_state(
            runtime_root=cleanup_root,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=UPDATED,
            candidate_objective_snapshot={
                "subject": "provisional",
                "nested": {"artifact_hash": "not-permitted"},
            },
        )


def test_session_and_workspace_isolation(tmp_path: Path) -> None:
    first = _create(tmp_path, topic="First")
    second = create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity="/workspace/other",
        session_identity="OTHER-SESSION",
        created_at=CREATED,
        topic="Second",
    )

    assert first["workspace_identity_hash"] != second["workspace_identity_hash"]
    assert first["session_identity_hash"] != second["session_identity_hash"]
    assert conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    ) != conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity="/workspace/other",
        session_identity="OTHER-SESSION",
    )
    assert (
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity="OTHER-SESSION",
            observed_at=OBSERVED,
        )
        is None
    )


def test_copied_state_is_rejected_under_different_session_and_workspace(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    source = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )
    other_workspace = "/workspace/other"
    other_session = "OTHER-SESSION"
    target = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=other_workspace,
        session_identity=other_session,
    )
    target.parent.mkdir(parents=True, mode=0o700)
    target.write_bytes(source.read_bytes())
    os.chmod(target, 0o600)

    with pytest.raises(FailClosedRuntimeError, match="workspace mismatch"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=other_workspace,
            session_identity=other_session,
            observed_at=OBSERVED,
        )

    other_session_path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=other_session,
    )
    other_session_path.parent.mkdir(parents=True, mode=0o700)
    other_session_path.write_bytes(source.read_bytes())
    os.chmod(other_session_path, 0o600)
    with pytest.raises(FailClosedRuntimeError, match="session mismatch"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=other_session,
            observed_at=OBSERVED,
        )


def test_cleanup_requires_current_revision_and_removes_state(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    with pytest.raises(FailClosedRuntimeError, match="revision is stale"):
        cleanup_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=1,
        )

    assert cleanup_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
    )
    assert not conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    ).exists()
    assert not cleanup_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    )


def test_expiration_fails_closed_and_recovery_cleans_state(
    tmp_path: Path,
) -> None:
    _create(tmp_path, ttl_seconds=60)
    expired_at = "2026-07-31T10:01:00Z"

    with pytest.raises(FailClosedRuntimeError, match="state is expired"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=expired_at,
        )
    assert recover_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=expired_at,
    ) is None
    assert not conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
    ).exists()


def test_update_can_extend_expiration_explicitly(tmp_path: Path) -> None:
    _create(tmp_path, ttl_seconds=60)
    updated = update_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        updated_at="2026-07-31T10:00:30Z",
        ttl_seconds=120,
        topic="Still active",
    )

    assert updated["expires_at"] == "2026-07-31T10:02:30Z"
    assert load_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-07-31T10:02:00Z",
    ) == updated


def test_schema_revision_confidence_and_ttl_bounds_fail_closed(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)

    invalid_revision = deepcopy(state)
    invalid_revision["revision"] = -1
    invalid_revision = _with_integrity(invalid_revision)
    with pytest.raises(FailClosedRuntimeError, match="revision is invalid"):
        validate_conversation_working_memory_state(invalid_revision)

    with pytest.raises(
        FailClosedRuntimeError,
        match="confidence must be a number between zero and one",
    ):
        update_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=UPDATED,
            confidence=float("nan"),
        )

    excessive_expiration = deepcopy(state)
    excessive_expiration["expires_at"] = "2027-07-31T10:00:00Z"
    excessive_expiration = _with_integrity(excessive_expiration)
    with pytest.raises(
        FailClosedRuntimeError,
        match="expiration exceeds TTL bound",
    ):
        validate_conversation_working_memory_state(excessive_expiration)


def test_concurrent_updates_allow_one_revision_and_reject_the_other(
    tmp_path: Path,
) -> None:
    _create(tmp_path)

    def update(topic: str):
        return update_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            updated_at=UPDATED,
            topic=topic,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(update, "Concurrent A"),
            executor.submit(update, "Concurrent B"),
        ]
    outcomes = []
    for future in futures:
        try:
            outcomes.append(("success", future.result()))
        except FailClosedRuntimeError as exc:
            outcomes.append(("error", str(exc)))

    assert [kind for kind, _ in outcomes].count("success") == 1
    assert [kind for kind, _ in outcomes].count("error") == 1
    assert "revision is stale" in next(
        value for kind, value in outcomes if kind == "error"
    )
    stored = load_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED,
    )
    assert stored["revision"] == 1
    assert stored["topic"] in {"Concurrent A", "Concurrent B"}


def test_create_rejects_duplicate_and_path_inputs_remain_safe(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _create(tmp_path)

    traversal = create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity="../../outside-workspace",
        session_identity="../../outside-session",
        created_at=CREATED,
    )
    traversal_path = conversation_working_memory_state_path(
        runtime_root=tmp_path,
        workspace_identity="../../outside-workspace",
        session_identity="../../outside-session",
    )
    assert traversal["session_identity"] == "../../outside-session"
    assert traversal_path.is_relative_to(tmp_path.resolve())
    assert ".." not in traversal_path.relative_to(tmp_path.resolve()).parts


def test_runtime_has_no_downstream_integration_imports() -> None:
    source = inspect.getsource(cwm_runtime)
    prohibited_imports = (
        "from aigol.runtime.platform_project_objective_inference",
        "from aigol.runtime.platform_core_conversation_boundary",
        "from aigol.runtime.execution_authorization_runtime",
        "from aigol.runtime.worker_runtime",
        "from aigol.runtime.semantic_capability_selection_runtime",
        "from aigol.runtime.human_interface_runtime_entry_service",
        "from aigol.runtime.constitutional_development_governance",
    )

    assert not any(item in source for item in prohibited_imports)
