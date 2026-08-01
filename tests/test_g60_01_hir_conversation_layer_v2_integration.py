from __future__ import annotations

import ast
from pathlib import Path
import stat

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime import platform_core_conversation_objective_readiness_runtime_v2 as readiness_v2
from aigol.runtime import platform_core_conversation_working_memory_runtime_v2 as cwm_v2
from aigol.runtime import platform_core_objective_commitment_runtime_v2 as commitment_v2


WORKSPACE = "/workspace/sapianta"
SESSION = "G60-01-HIR-CONVERSATION"
CREATED = "2026-08-01T12:00:00Z"


def _time(second: int) -> str:
    return f"2026-08-01T12:00:{second:02d}Z"


def _start(tmp_path: Path, *, session: str = SESSION) -> dict:
    return hir_v2.create_hir_conversation_session_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        human_identity="local-human",
        created_at=CREATED,
    )


def _semantic_turns(tmp_path: Path, *, session: str = SESSION) -> list[dict]:
    turns = (
        "action: implement",
        "subject: Human Interface Runtime integration",
        "outcome: an immutable Objective Commitment without execution",
        "work-type: IMPLEMENTATION",
    )
    return [
        hir_v2.admit_hir_semantic_turn_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=session,
            source_turn_text=text,
            observed_at=_time(index),
        )
        for index, text in enumerate(turns, start=1)
    ]


def _confirm(tmp_path: Path, semantic_result: dict, *, session: str = SESSION) -> dict:
    digest = semantic_result["candidate_review"]["presentation"]["candidate_digest"]
    return hir_v2.confirm_hir_candidate_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_confirmation_action=f"/confirm {digest}",
        observed_at=_time(5),
    )


def _commit(tmp_path: Path, confirmation: dict, *, session: str = SESSION) -> dict:
    return hir_v2.create_hir_objective_commitment_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=session,
        explicit_commit_action=confirmation["expected_commit_action"],
        observed_at=_time(6),
    )


def test_hir_creates_native_envelope_with_explicit_participant_ownership(
    tmp_path: Path,
) -> None:
    result = _start(tmp_path)
    state = result["state"]

    assert state["envelope"]["origin_interface_identity"] == cwm_v2.LOCAL_CONVERSATION_V2
    assert [item["participant_role"] for item in state["envelope"]["participants"]] == [
        cwm_v2.CONVERSATION_OWNER_RUNTIME,
        cwm_v2.HUMAN_ORIGINATOR,
        cwm_v2.INTERFACE_TRANSPORT,
    ]
    assert result["session_status"] == hir_v2.SESSION_ACTIVE
    assert result["execution_pipeline_entered"] is False


def test_semantic_turns_use_proposal_validation_commit_and_state_progression(
    tmp_path: Path,
) -> None:
    _start(tmp_path)
    results = _semantic_turns(tmp_path)

    assert [item["proposal_validation_disposition"] for item in results] == [
        "ADMISSIBLE"
    ] * 4
    assert [item["proposal_commit_disposition"] for item in results] == [
        "COMMITTED"
    ] * 4
    assert [item["state"]["revision"] for item in results] == [2, 4, 6, 8]
    assert [item["protocol_state"] for item in results] == [
        "CLARIFYING",
        "CLARIFYING",
        "CLARIFYING",
        "CANDIDATE_REVIEW",
    ]
    assert all(item["execution_pipeline_entered"] is False for item in results)


def test_required_slot_dependencies_are_complete_and_canonical(tmp_path: Path) -> None:
    _start(tmp_path)
    state = _semantic_turns(tmp_path)[-1]["state"]
    by_class = {
        slot["slot_class"]: slot
        for slot in state["semantic_memory"]["semantic_slots"]
    }

    action_id = by_class[cwm_v2.OPERATIVE_ACTION]["slot_id"]
    subject_id = by_class[cwm_v2.OPERATIVE_SUBJECT]["slot_id"]
    assert by_class[cwm_v2.OPERATIVE_SUBJECT]["depends_on"] == [action_id]
    assert by_class[cwm_v2.DESIRED_OUTCOME]["depends_on"] == sorted(
        [action_id, subject_id]
    )
    assert by_class[cwm_v2.WORK_TYPE]["depends_on"] == [action_id]
    assert all(slot["status"] == cwm_v2.ASSERTED for slot in by_class.values())


def test_out_of_order_or_unstructured_turn_fails_closed_without_mutation(
    tmp_path: Path,
) -> None:
    initial = _start(tmp_path)["state"]
    with pytest.raises(FailClosedRuntimeError, match="next required semantic field"):
        hir_v2.admit_hir_semantic_turn_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            source_turn_text="subject: wrong order",
            observed_at=_time(1),
        )
    with pytest.raises(FailClosedRuntimeError, match="named field"):
        hir_v2.admit_hir_semantic_turn_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            source_turn_text="please implement something",
            observed_at=_time(1),
        )
    persisted = cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(1),
    )
    assert persisted == initial


def test_confirmation_requires_exact_candidate_binding(tmp_path: Path) -> None:
    _start(tmp_path)
    final_semantic = _semantic_turns(tmp_path)[-1]

    with pytest.raises(FailClosedRuntimeError, match="exact /confirm"):
        hir_v2.confirm_hir_candidate_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            explicit_confirmation_action="/confirm sha256:" + "0" * 64,
            observed_at=_time(5),
        )

    confirmed = _confirm(tmp_path, final_semantic)
    assert confirmed["confirmation_disposition"] == "CONFIRMATION_RECORDED"
    assert confirmed["readiness_report"]["readiness_disposition"] == "READY"
    assert confirmed["readiness_report"]["objective_commitment_eligible"] is True
    assert confirmed["execution_pipeline_entered"] is False


def test_commit_before_readiness_is_refused_and_creates_no_record(tmp_path: Path) -> None:
    _start(tmp_path)
    with pytest.raises(readiness_v2.ObjectiveReadinessError):
        hir_v2.create_hir_objective_commitment_v2(
            runtime_root=tmp_path,
            workspace_identity=WORKSPACE,
            session_identity=SESSION,
            explicit_commit_action="/commit sha256:" + "0" * 64,
            observed_at=_time(1),
        )
    commitment_root = cwm_v2._conversation_root(tmp_path) / "_objective_commitments_v2"
    assert not commitment_root.exists()


def test_objective_commitment_is_terminal_and_removes_mutable_cwm(tmp_path: Path) -> None:
    _start(tmp_path)
    confirmation = _confirm(tmp_path, _semantic_turns(tmp_path)[-1])
    result = _commit(tmp_path, confirmation)
    record_path = commitment_v2._record_path(
        commitment_v2._commitment_root(cwm_v2._conversation_root(tmp_path)),
        result["commitment_identity"],
    )

    assert result["terminal_condition"] == hir_v2.OBJECTIVE_COMMITMENT_CREATED
    assert result["session_status"] == hir_v2.SESSION_STOPPED_AT_COMMITMENT
    assert result["commitment_record_created"] is True
    assert stat.S_IMODE(record_path.stat().st_mode) == 0o400
    assert cwm_v2.load_conversation_working_memory_state_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        observed_at=_time(6),
    ) is None
    for field in (
        "platform_core_admission_reached",
        "development_governance_reached",
        "capability_selection_reached",
        "authorization_reached",
        "worker_reached",
        "replay_execution_reached",
        "execution_pipeline_entered",
        "external_llm_invoked",
    ):
        assert result[field] is False


def test_repeated_identical_conversations_have_deterministic_commitment_identity(
    tmp_path: Path,
) -> None:
    identities = []
    for index in range(2):
        root = tmp_path / str(index)
        _start(root)
        confirmation = _confirm(root, _semantic_turns(root)[-1])
        identities.append(_commit(root, confirmation)["commitment_identity"])
    assert identities[0] == identities[1]


def test_terminal_runner_produces_complete_human_to_commitment_trace(
    tmp_path: Path,
) -> None:
    fixed = iter(
        [
            "action: implement",
            "subject: Human Interface Runtime integration",
            "outcome: an immutable Objective Commitment without execution",
            "work-type: IMPLEMENTATION",
        ]
    )
    outputs: list[str] = []
    turn = 0

    def reader(prompt: str) -> str:
        nonlocal turn
        if turn < 4:
            value = next(fixed)
        else:
            value = next(
                item.removeprefix("next: ")
                for item in reversed(outputs)
                if item.startswith("next: ")
            )
        turn += 1
        outputs.append(prompt + value)
        return value

    result = hir_v2.run_hir_conversation_terminal_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        human_identity="local-human",
        created_at=CREATED,
        input_reader=reader,
        output_writer=outputs.append,
    )
    transcript = "\n".join(outputs)

    assert "route: Human -> AiCLI -> HIR -> Conversation Layer V2" in transcript
    assert transcript.count("proposal_validation: ADMISSIBLE") == 4
    assert transcript.count("proposal_commit: COMMITTED") == 4
    assert "objective_readiness: READY" in transcript
    assert "objective_commitment: COMMITTED" in transcript
    assert "platform_core_admission_reached: false" in transcript
    assert "execution_pipeline_entered: false" in transcript
    assert transcript.endswith("session_stopped: OBJECTIVE_COMMITMENT_CREATED")
    assert result["terminal_condition"] == hir_v2.OBJECTIVE_COMMITMENT_CREATED


def test_eof_before_commitment_is_non_executing_and_leaves_session_active(
    tmp_path: Path,
) -> None:
    result = hir_v2.run_hir_conversation_terminal_v2(
        runtime_root=tmp_path,
        workspace_identity=WORKSPACE,
        session_identity=SESSION,
        human_identity="local-human",
        created_at=CREATED,
        input_reader=lambda _prompt: (_ for _ in ()).throw(EOFError()),
        output_writer=lambda _line: None,
    )
    assert result["terminal_condition"] == "EOF_BEFORE_OBJECTIVE_COMMITMENT"
    assert result["session_status"] == hir_v2.SESSION_ACTIVE
    assert result["execution_pipeline_entered"] is False


def test_aicli_explicit_mode_routes_to_isolated_hir(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_runner(**kwargs):
        captured.update(kwargs)
        return {"terminal_condition": hir_v2.OBJECTIVE_COMMITMENT_CREATED}

    monkeypatch.setattr(aicli, "run_hir_conversation_terminal_v2", fake_runner)
    assert aicli.main(
        [
            "--session-id",
            SESSION,
            "--created-at",
            CREATED,
            "--runtime-root",
            "/tmp/g60",
            "--workspace",
            WORKSPACE,
            "--human-identity",
            "local-human",
            "conversation-v2",
        ]
    ) == 0
    assert captured["session_identity"] == SESSION
    assert captured["workspace_identity"] == WORKSPACE


def test_integration_module_has_no_execution_pipeline_import_or_call() -> None:
    source_path = Path(hir_v2.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden_tokens = {
        "execution_runtime",
        "worker_dispatch_runtime",
        "worker_invocation_runtime",
        "execution_authorization_runtime",
        "development_governance",
        "capability_selection",
        "condensation_replay",
        "central_language",
        "external_language_model",
    }
    names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    combined = " ".join(sorted(names | imports)).lower()
    assert all(token not in combined for token in forbidden_tokens)
