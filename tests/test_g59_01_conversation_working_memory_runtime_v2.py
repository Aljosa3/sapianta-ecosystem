from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import inspect
import json
import os
from pathlib import Path

import pytest

from aigol.runtime import (
    platform_core_conversation_working_memory_runtime_v2 as cwm_v2,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_conversation_working_memory_runtime import (
    COMMITTED,
    create_conversation_working_memory_state,
    load_conversation_working_memory_state,
)
from aigol.runtime.platform_core_conversation_working_memory_runtime_v2 import (
    ACCEPTANCE,
    ASSERTED,
    ASSERTED_NOT_AUTHENTICATED,
    COMPLETE,
    CONDITIONAL,
    DESIRED_OUTCOME,
    EVIDENCE,
    GOVERNING_QUALIFIER,
    HUMAN_ASSERTED,
    HUMAN_ORIGINATOR,
    HUMAN_TURN,
    LOCAL_ASSERTION,
    OPERATIVE_ACTION,
    OPERATIVE_SUBJECT,
    OUTPUT,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2,
    PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2,
    PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
    PRESERVATION,
    PRIMARY,
    REQUIRED,
    SCOPE,
    SEMANTIC_REFERENCE,
    SEMANTIC_SLOT_CLASSES,
    WORK_TYPE,
    conversation_working_memory_conversation_identity_v2,
    create_conversation_working_memory_state_v2,
    create_semantic_cwm_slot_v2,
    load_conversation_working_memory_state_v2,
    migrate_conversation_working_memory_state_v1_to_v2,
    recover_conversation_working_memory_state_v2,
    replace_conversation_working_memory_state_v2_atomically,
    validate_conversation_working_memory_state_v2,
    validate_semantic_cwm_slot_v2,
)


WORKSPACE = "/workspace/sapianta"
SESSION = "G59-01-CWM-V2-SESSION"
CREATED = "2026-07-31T10:00:00Z"
UPDATED = "2026-07-31T10:01:00Z"
OBSERVED = "2026-07-31T10:02:00Z"


def _canonical_bytes(value) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _checksum(value) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _with_integrity(state: dict) -> dict:
    candidate = deepcopy(state)
    candidate.pop("integrity_checksum", None)
    candidate["integrity_checksum"] = _checksum(candidate)
    return candidate


def _conversation() -> str:
    return conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )


def _provenance(fragment: str, *, source_revision: int = 0) -> list[dict]:
    return [
        {
            "source_kind": HUMAN_TURN,
            "turn_number": 1,
            "source_revision": source_revision,
            "source_span": fragment,
            "content_digest": _checksum(fragment),
            "normalization_rule_ids": [],
            "human_disposition": "ASSERTED",
        }
    ]


def _slot(
    *,
    slot_class: str,
    slot_role: str,
    cardinality_key: str,
    value: str,
    materiality: str = REQUIRED,
    depends_on=(),
) -> dict:
    return create_semantic_cwm_slot_v2(
        conversation_identity=_conversation(),
        slot_class=slot_class,
        slot_role=slot_role,
        cardinality_key=cardinality_key,
        surface_value=value,
        canonical_value=value,
        status=ASSERTED,
        completeness=COMPLETE,
        confidence_class=HUMAN_ASSERTED,
        materiality=materiality,
        provenance=_provenance(value),
        depends_on=sorted(depends_on),
        created_at=CREATED,
    )


def _six_class_slots() -> list[dict]:
    action = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="implement",
    )
    subject = _slot(
        slot_class=OPERATIVE_SUBJECT,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="Conversation Working Memory V2",
        depends_on=[action["slot_id"]],
    )
    outcome = _slot(
        slot_class=DESIRED_OUTCOME,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="isolated typed semantic state",
        depends_on=[action["slot_id"], subject["slot_id"]],
    )
    work_type = _slot(
        slot_class=WORK_TYPE,
        slot_role="IMPLEMENTATION",
        cardinality_key=PRIMARY,
        value="IMPLEMENTATION",
        depends_on=[action["slot_id"]],
    )
    qualifier = _slot(
        slot_class=GOVERNING_QUALIFIER,
        slot_role=PRESERVATION,
        cardinality_key="preserve-runtime-isolation",
        value="preserve runtime isolation",
        materiality=CONDITIONAL,
        depends_on=[subject["slot_id"]],
    )
    reference = _slot(
        slot_class=SEMANTIC_REFERENCE,
        slot_role=SCOPE,
        cardinality_key="runtime-path",
        value="aigol/runtime/platform_core_conversation_working_memory_runtime_v2.py",
        materiality=CONDITIONAL,
        depends_on=[subject["slot_id"]],
    )
    return [reference, qualifier, work_type, outcome, subject, action]


def _participants() -> list[dict]:
    return [
        {
            "participant_role": HUMAN_ORIGINATOR,
            "asserted_identity": "local-human",
            "identity_source": LOCAL_ASSERTION,
            "binding_disposition": ASSERTED_NOT_AUTHENTICATED,
            "first_bound_revision": 0,
            "last_confirmed_revision": 0,
        }
    ]


def _create(tmp_path: Path, **overrides) -> dict:
    arguments = {
        "runtime_root": tmp_path,
        "workspace_identity": WORKSPACE,
        "session_identity": SESSION,
        "created_at": CREATED,
        "participants": _participants(),
    }
    arguments.update(overrides)
    return create_conversation_working_memory_state_v2(**arguments)


def _replacement_with_slots(state: dict, slots: list[dict]) -> dict:
    replacement = deepcopy(state)
    replacement["revision"] += 1
    replacement["envelope_revision"] += 1
    replacement["semantic_revision"] += 1
    replacement["envelope"]["updated_at"] = UPDATED
    replacement["semantic_memory"]["semantic_slots"] = sorted(
        slots,
        key=lambda item: (
            SEMANTIC_SLOT_CLASSES.index(item["slot_class"]),
            item["slot_role"],
            item["cardinality_key"],
            item["slot_id"],
        ),
    )
    replacement["envelope"]["semantic_memory_binding"] = {
        "semantic_memory_type": PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2,
        "global_revision": replacement["revision"],
        "semantic_revision": replacement["semantic_revision"],
        "semantic_memory_digest": _checksum(replacement["semantic_memory"]),
    }
    return _with_integrity(replacement)


def _revised_slot(slot: dict, value: str) -> dict:
    replacement = deepcopy(slot)
    replacement["surface_value"] = value
    replacement["canonical_value"] = value
    replacement["equivalence_key"] = cwm_v2._equivalence_key(
        replacement["slot_class"],
        replacement["slot_role"],
        value,
    )
    replacement["slot_revision"] = 1
    replacement["history"].append(
        {
            "slot_revision": 1,
            "changed_at": UPDATED,
            "change_kind": "REFINED",
            "prior_value_digest": _checksum(slot["canonical_value"]),
            "resulting_value_digest": _checksum(value),
        }
    )
    return replacement


def test_create_v2_document_integrates_envelope_and_semantic_memory(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path, semantic_slots=_six_class_slots())

    assert state["working_memory_type"] == (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2
    )
    assert state["runtime_version"] == (
        PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2
    )
    assert state["revision"] == 0
    assert state["envelope_revision"] == 0
    assert state["semantic_revision"] == 0
    assert state["envelope"]["conversation_identity"] == _conversation()
    assert state["envelope"]["availability_state"] == "ACTIVE"
    assert state["envelope"]["conversation_phase"] == "COLLECTING"
    assert state["semantic_memory"]["semantic_memory_type"] == (
        PLATFORM_CORE_SEMANTIC_CWM_SCHEMA_V2
    )
    assert {
        item["slot_class"]
        for item in state["semantic_memory"]["semantic_slots"]
    } == set(SEMANTIC_SLOT_CLASSES)
    for boundary in (state, state["envelope"]):
        assert boundary["constitutional_artifact"] is False
        assert boundary["constitutional_authority"] is False
        assert boundary["replay_visible"] is False
        assert boundary["authorization_eligible"] is False
        assert boundary["worker_eligible"] is False
        assert boundary["objective_creation_supported"] is False
        assert boundary["capability_routing_supported"] is False
    assert state["envelope"]["active_objective_candidate_binding"] is None


def test_v2_serialization_and_identity_are_deterministic(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = _create(first_root, semantic_slots=_six_class_slots())
    second = _create(
        second_root, semantic_slots=list(reversed(_six_class_slots()))
    )

    first_path = cwm_v2._state_path(
        cwm_v2._conversation_root(first_root), WORKSPACE, SESSION
    )
    second_path = cwm_v2._state_path(
        cwm_v2._conversation_root(second_root), WORKSPACE, SESSION
    )
    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes() == _canonical_bytes(first) + b"\n"
    assert all(
        item["slot_id"].startswith("conversation-slot-sha256:")
        for item in first["semantic_memory"]["semantic_slots"]
    )


def test_slot_identity_is_session_local_and_stable_for_semantic_key() -> None:
    first = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="implement",
    )
    second = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="revise",
    )
    other_conversation = conversation_working_memory_conversation_identity_v2(
        workspace_identity=WORKSPACE,
        session_identity="OTHER-SESSION",
        created_at=CREATED,
    )
    other = create_semantic_cwm_slot_v2(
        conversation_identity=other_conversation,
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        surface_value="implement",
        canonical_value="implement",
        status=ASSERTED,
        completeness=COMPLETE,
        confidence_class=HUMAN_ASSERTED,
        materiality=REQUIRED,
        provenance=_provenance("implement"),
        created_at=CREATED,
    )

    assert first["slot_id"] == second["slot_id"]
    assert first["equivalence_key"] != second["equivalence_key"]
    assert first["slot_id"] != other["slot_id"]
    assert first["slot_revision"] == 0
    assert first["history"][0]["slot_revision"] == 0


@pytest.mark.parametrize(
    ("slot_class", "role", "cardinality", "value"),
    [
        (OPERATIVE_ACTION, PRIMARY, PRIMARY, "implement"),
        (OPERATIVE_SUBJECT, PRIMARY, PRIMARY, "CWM V2"),
        (DESIRED_OUTCOME, PRIMARY, PRIMARY, "typed state"),
        (WORK_TYPE, "IMPLEMENTATION", PRIMARY, "IMPLEMENTATION"),
        (GOVERNING_QUALIFIER, OUTPUT, "output-1", "return JSON"),
        (SEMANTIC_REFERENCE, EVIDENCE, "evidence-1", "opaque-ref:1"),
    ],
)
def test_all_six_slot_classes_have_closed_role_validation(
    slot_class: str, role: str, cardinality: str, value: str
) -> None:
    slot = _slot(
        slot_class=slot_class,
        slot_role=role,
        cardinality_key=cardinality,
        value=value,
        materiality=REQUIRED if cardinality == PRIMARY else CONDITIONAL,
    )
    assert slot["slot_class"] == slot_class

    invalid = deepcopy(slot)
    invalid["slot_role"] = "UNBOUNDED_ROLE"
    with pytest.raises(FailClosedRuntimeError, match="slot_role is invalid"):
        validate_semantic_cwm_slot_v2(
            invalid, conversation_identity=_conversation()
        )


def test_closed_schema_and_authority_smuggling_fail_closed(tmp_path: Path) -> None:
    state = _create(tmp_path)
    unknown = deepcopy(state)
    unknown["unbounded"] = True
    unknown = _with_integrity(unknown)
    with pytest.raises(FailClosedRuntimeError, match="schema fields are invalid"):
        validate_conversation_working_memory_state_v2(unknown)

    promoted = deepcopy(state)
    promoted["envelope"]["replay_visible"] = True
    promoted = _with_integrity(promoted)
    with pytest.raises(FailClosedRuntimeError, match="authority boundary is invalid"):
        validate_conversation_working_memory_state_v2(promoted)

    forbidden = deepcopy(state)
    forbidden["semantic_memory"]["legacy_import"] = {
        "objective_id": "forbidden"
    }
    forbidden = _with_integrity(forbidden)
    with pytest.raises(FailClosedRuntimeError, match="forbidden identity"):
        validate_conversation_working_memory_state_v2(forbidden)


def test_slot_provenance_history_and_single_cardinality_fail_closed() -> None:
    slot = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="implement",
    )
    bad_provenance = deepcopy(slot)
    bad_provenance["provenance"][0]["content_digest"] = _checksum(
        "different source"
    )
    with pytest.raises(
        FailClosedRuntimeError,
        match="provenance content digest is invalid",
    ):
        validate_semantic_cwm_slot_v2(
            bad_provenance, conversation_identity=_conversation()
        )

    bad_history = deepcopy(slot)
    bad_history["slot_revision"] = 1
    with pytest.raises(
        FailClosedRuntimeError,
        match="history revision is invalid",
    ):
        validate_semantic_cwm_slot_v2(
            bad_history, conversation_identity=_conversation()
        )

    with pytest.raises(
        FailClosedRuntimeError,
        match="duplicate identity",
    ):
        cwm_v2._semantic_memory(
            conversation_identity=_conversation(),
            semantic_slots=[slot, deepcopy(slot)],
            legacy_import=None,
        )


def test_participants_are_asserted_not_authenticated(tmp_path: Path) -> None:
    state = _create(tmp_path)
    assert state["envelope"]["participants"][0]["binding_disposition"] == (
        ASSERTED_NOT_AUTHENTICATED
    )

    authenticated = deepcopy(state)
    authenticated["envelope"]["participants"][0][
        "binding_disposition"
    ] = "AUTHENTICATED"
    authenticated = _with_integrity(authenticated)
    with pytest.raises(FailClosedRuntimeError, match="authentication is not implemented"):
        validate_conversation_working_memory_state_v2(authenticated)


def test_integrity_corruption_and_copied_state_fail_closed(
    tmp_path: Path,
) -> None:
    _create(tmp_path)
    source_path = cwm_v2._state_path(
        cwm_v2._conversation_root(tmp_path), WORKSPACE, SESSION
    )
    exact = source_path.read_bytes()
    corrupt = json.loads(exact.decode("utf-8"))
    corrupt["integrity_checksum"] = "sha256:" + ("0" * 64)
    source_path.write_bytes(_canonical_bytes(corrupt) + b"\n")
    with pytest.raises(FailClosedRuntimeError, match="integrity mismatch"):
        load_conversation_working_memory_state_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )

    source_path.write_bytes(exact)
    other_workspace = "/workspace/other"
    other_session = "OTHER-SESSION"
    target = cwm_v2._state_path(
        cwm_v2._conversation_root(tmp_path), other_workspace, other_session
    )
    target.parent.mkdir(parents=True, mode=0o700)
    target.write_bytes(exact)
    os.chmod(target, 0o600)
    with pytest.raises(FailClosedRuntimeError, match="workspace mismatch"):
        load_conversation_working_memory_state_v2(
            runtime_root=tmp_path,
            workspace_identity=other_workspace,
            session_identity=other_session,
            observed_at=OBSERVED,
        )


def test_v2_whole_document_size_bound_fails_closed(tmp_path: Path) -> None:
    oversized_slots = [
        _slot(
            slot_class=GOVERNING_QUALIFIER,
            slot_role=ACCEPTANCE,
            cardinality_key=f"acceptance-{index}",
            value=f"{index}-" + ("x" * 4_000),
            materiality=CONDITIONAL,
        )
        for index in range(6)
    ]
    with pytest.raises(FailClosedRuntimeError, match="exceeds storage bound"):
        _create(tmp_path, semantic_slots=oversized_slots)


def test_load_recover_and_expiration_reuse_g55_store(tmp_path: Path) -> None:
    state = _create(tmp_path, ttl_seconds=60)
    assert load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-07-31T10:00:30Z",
    ) == state
    with pytest.raises(FailClosedRuntimeError, match="state is expired"):
        load_conversation_working_memory_state_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at="2026-07-31T10:01:00Z",
        )
    assert recover_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at="2026-07-31T10:01:00Z",
    ) is None


def test_v2_replacement_uses_global_and_semantic_revision_cas(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    replacement = _replacement_with_slots(state, _six_class_slots())
    stored = replace_conversation_working_memory_state_v2_atomically(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=replacement,
        observed_at=UPDATED,
    )
    assert stored["revision"] == 1
    assert stored["envelope_revision"] == 1
    assert stored["semantic_revision"] == 1
    assert len(stored["semantic_memory"]["semantic_slots"]) == 6

    with pytest.raises(FailClosedRuntimeError, match="revision is stale"):
        replace_conversation_working_memory_state_v2_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=replacement,
            observed_at=UPDATED,
        )


def test_existing_slot_change_requires_one_slot_revision_increment(
    tmp_path: Path,
) -> None:
    action = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="implement",
    )
    state = _create(tmp_path, semantic_slots=[action])
    stale_slot = {
        **deepcopy(action),
        "surface_value": "revise",
        "canonical_value": "revise",
        "equivalence_key": cwm_v2._equivalence_key(
            OPERATIVE_ACTION, PRIMARY, "revise"
        ),
    }
    stale_slot["history"][0]["resulting_value_digest"] = _checksum("revise")
    stale_slot_revision = _replacement_with_slots(state, [stale_slot])
    with pytest.raises(
        FailClosedRuntimeError,
        match="slot revision transition is invalid",
    ):
        replace_conversation_working_memory_state_v2_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=stale_slot_revision,
            observed_at=UPDATED,
        )

    replacement = _replacement_with_slots(
        state,
        [_revised_slot(action, "revise")],
    )
    stored = replace_conversation_working_memory_state_v2_atomically(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        replacement_state=replacement,
        observed_at=UPDATED,
    )
    revised = stored["semantic_memory"]["semantic_slots"][0]
    assert revised["slot_id"] == action["slot_id"]
    assert revised["slot_revision"] == 1
    assert [item["slot_revision"] for item in revised["history"]] == [0, 1]


def test_existing_slot_cannot_be_deleted_by_foundation_replace(
    tmp_path: Path,
) -> None:
    action = _slot(
        slot_class=OPERATIVE_ACTION,
        slot_role=PRIMARY,
        cardinality_key=PRIMARY,
        value="implement",
    )
    state = _create(tmp_path, semantic_slots=[action])
    replacement = _replacement_with_slots(state, [])
    with pytest.raises(
        FailClosedRuntimeError,
        match="semantic slots cannot be deleted",
    ):
        replace_conversation_working_memory_state_v2_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=replacement,
            observed_at=UPDATED,
        )


def test_v2_foundation_rejects_envelope_state_machine_mutation(
    tmp_path: Path,
) -> None:
    state = _create(tmp_path)
    replacement = deepcopy(state)
    replacement["revision"] = 1
    replacement["envelope_revision"] = 1
    replacement["envelope"]["updated_at"] = UPDATED
    replacement["envelope"]["participants"][0][
        "last_confirmed_revision"
    ] = 1
    replacement["envelope"]["semantic_memory_binding"][
        "global_revision"
    ] = 1
    replacement = _with_integrity(replacement)

    with pytest.raises(
        FailClosedRuntimeError,
        match="Envelope mutation is reserved for the future state machine",
    ):
        replace_conversation_working_memory_state_v2_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=replacement,
            observed_at=UPDATED,
        )


def test_concurrent_v2_replacements_admit_one_revision(tmp_path: Path) -> None:
    state = _create(tmp_path)
    first = _replacement_with_slots(
        state,
        [
            _slot(
                slot_class=OPERATIVE_ACTION,
                slot_role=PRIMARY,
                cardinality_key=PRIMARY,
                value="implement",
            )
        ],
    )
    second = _replacement_with_slots(
        state,
        [
            _slot(
                slot_class=OPERATIVE_ACTION,
                slot_role=PRIMARY,
                cardinality_key=PRIMARY,
                value="revise",
            )
        ],
    )

    def replace(candidate):
        return replace_conversation_working_memory_state_v2_atomically(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            replacement_state=candidate,
            observed_at=UPDATED,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(replace, first), executor.submit(replace, second)]
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


def test_v1_and_v2_share_path_but_never_auto_migrate(tmp_path: Path) -> None:
    create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        topic="legacy",
    )
    with pytest.raises(FailClosedRuntimeError, match="V2 state schema fields are invalid"):
        load_conversation_working_memory_state_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )
    assert load_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED,
    )["topic"] == "legacy"


def test_explicit_v1_migration_preserves_legacy_only_as_review_required(
    tmp_path: Path,
) -> None:
    source = create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        topic="legacy topic",
        entities=["legacy entity"],
        inferred_intent="legacy inferred intent",
        assumptions=["legacy assumption"],
        candidate_objective_snapshot={"subject": "legacy candidate"},
    )
    migrated = migrate_conversation_working_memory_state_v1_to_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        expected_revision=0,
        migrated_at=OBSERVED,
    )

    assert migrated["revision"] == source["revision"] + 1
    assert migrated["semantic_revision"] == 0
    assert migrated["semantic_memory"]["semantic_slots"] == []
    assert migrated["semantic_memory"]["legacy_import"]["topic"] == (
        "legacy topic"
    )
    assert migrated["migration_metadata"]["migration_status"] == (
        "LEGACY_REVIEW_REQUIRED"
    )
    assert migrated["migration_metadata"]["source_revision"] == 0
    assert migrated["migration_metadata"]["participant_binding_status"] == (
        "PARTICIPANT_BINDING_REQUIRED"
    )
    assert migrated["envelope"]["participants"] == []
    assert migrated["envelope"]["active_objective_candidate_binding"] is None
    assert not cwm_v2._state_path(
        cwm_v2._conversation_root(tmp_path), WORKSPACE, SESSION
    ).with_name("state.v1.migration-backup.json").exists()
    assert load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=OBSERVED,
    ) == migrated
    with pytest.raises(FailClosedRuntimeError, match="schema fields are invalid"):
        load_conversation_working_memory_state(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            observed_at=OBSERVED,
        )


def test_migration_rejects_reserved_commitment_and_preserves_v1(
    tmp_path: Path,
) -> None:
    source = create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
    )
    path = cwm_v2._state_path(
        cwm_v2._conversation_root(tmp_path), WORKSPACE, SESSION
    )
    reserved = deepcopy(source)
    reserved["lifecycle_state"] = COMMITTED
    reserved = _with_integrity(reserved)
    path.write_bytes(_canonical_bytes(reserved) + b"\n")
    exact = path.read_bytes()

    with pytest.raises(
        FailClosedRuntimeError,
        match="reserved commitment lifecycle cannot be migrated",
    ):
        migrate_conversation_working_memory_state_v1_to_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            migrated_at=OBSERVED,
        )
    assert path.read_bytes() == exact
    assert not path.with_name("state.v1.migration-backup.json").exists()


def test_migration_rejects_expired_or_stale_v1_without_partial_v2(
    tmp_path: Path,
) -> None:
    create_conversation_working_memory_state(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        created_at=CREATED,
        ttl_seconds=60,
    )
    path = cwm_v2._state_path(
        cwm_v2._conversation_root(tmp_path), WORKSPACE, SESSION
    )
    exact = path.read_bytes()
    with pytest.raises(FailClosedRuntimeError, match="state is expired"):
        migrate_conversation_working_memory_state_v1_to_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=0,
            migrated_at="2026-07-31T10:01:00Z",
        )
    assert path.read_bytes() == exact

    with pytest.raises(FailClosedRuntimeError, match="revision is stale"):
        migrate_conversation_working_memory_state_v1_to_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            expected_revision=1,
            migrated_at="2026-07-31T10:00:30Z",
        )
    assert path.read_bytes() == exact


def test_v2_runtime_has_no_execution_pipeline_imports() -> None:
    source = inspect.getsource(cwm_v2)
    prohibited_imports = (
        "from aigol.runtime.platform_core_project_services",
        "from aigol.runtime.platform_project_objective_inference",
        "from aigol.runtime.platform_core_conversation_boundary",
        "from aigol.runtime.execution_authorization_runtime",
        "from aigol.runtime.worker_runtime",
        "from aigol.runtime.semantic_capability_selection_runtime",
        "from aigol.runtime.human_interface_runtime_entry_service",
        "from aigol.runtime.constitutional_development_governance",
        "from aigol.runtime.replay",
    )
    assert not any(item in source for item in prohibited_imports)
