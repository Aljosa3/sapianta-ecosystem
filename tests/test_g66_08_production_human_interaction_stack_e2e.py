"""End-to-end G66-08 validation of the production Human Interaction stack.

The defect-characterization tests intentionally assert observed production
behavior. G66-08 is read-only with respect to runtime code and must not repair
the defects it discovers.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from aigol.cli.aicli import (
    run_reference_uhi_session,
    run_reference_uhi_submit_session,
)
from aigol.runtime import human_interface_conversation_runtime_v2 as hir_v2
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.production_conversation_flow_binding import (
    CFA_DEVELOPMENT_GOVERNANCE,
    CFA_EXECUTION,
    CFA_OBJECTIVE_COMMITMENT,
    CFA_PLATFORM_KNOWLEDGE,
    CFA_SELF_KNOWLEDGE,
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-08-03T14:00:00Z"


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def _submit(
    tmp_path: Path,
    request: str,
    *,
    session: str,
) -> dict:
    return run_reference_uhi_submit_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: request,
        input_reader=lambda _prompt: (_ for _ in ()).throw(EOFError()),
        output_writer=lambda _line: None,
    )


def _contexts(tmp_path: Path, session: str) -> list[dict]:
    return [
        load_json(path)
        for path in sorted(
            (tmp_path / session / "uhi_project_services").glob(
                "*_uhi_project_context_recorded.json"
            )
        )
    ]


@pytest.mark.parametrize(
    ("human_text", "target", "service"),
    [
        (
            "Show architecture.",
            CFA_SELF_KNOWLEDGE,
            "SELF_KNOWLEDGE_QUERY_RUNTIME",
        ),
        (
            "What platform capabilities are available?",
            CFA_PLATFORM_KNOWLEDGE,
            "PLATFORM_KNOWLEDGE_RUNTIME",
        ),
    ],
)
def test_default_read_only_conversations_traverse_the_complete_stack(
    tmp_path: Path,
    human_text: str,
    target: str,
    service: str,
) -> None:
    result = _submit(tmp_path, human_text, session="G66-08-READ-ONLY")
    context = result["platform_core_project_services_context"]
    precedence = context["human_intent_precedence_decision"]
    binding = context["production_conversation_flow_binding"]
    work = context["governed_read_only_work_result"]
    event = next(item for item in result["transcript"] if item["event"] == "message")

    assert event["canonical_human_entry_used"] is True
    assert precedence["decision_disposition"] == "NEW_HUMAN_INTENT"
    assert binding["conversation_identity"]
    assert binding["cwm_revision"] == 1
    assert binding["proposal_validation_disposition"] == "ADMISSIBLE"
    assert [
        item["stage"] for item in binding["ordered_predecessor_references"][:4]
    ] == [
        "HUMAN_INTENT_PRECEDENCE",
        "INTERPRETER_PROPOSAL",
        "PROPOSAL_VALIDATION",
        "PROPOSAL_COMMIT",
    ]
    assert binding["platform_service_invoked_by_selection"] is False
    assert binding["requested_target_flow_id"] == target
    assert context["production_conversation_flow_binding_hash"] == binding[
        "artifact_hash"
    ]
    assert context["project_objective_inference"] is None
    assert work["selected_read_only_service"] == service
    assert work["presentation_status"] == "PRESENTATION_READY"
    assert context["human_conversation_experience"]["response_mode"] == (
        "READ_ONLY_RESULT"
    )
    reconstruction = reconstruct_production_conversation_flow_binding_v1(
        Path(binding["owner_local_replay_references"][0]).parent
    )
    assert reconstruction["reconstruction_verified"] is True


def test_repository_launcher_uses_the_default_canonical_stack(tmp_path: Path) -> None:
    session = "G66-08-LAUNCHER"
    completed = subprocess.run(
        [
            "./aicli",
            "--session-id",
            session,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path),
            "--workspace",
            ".",
            "submit",
        ],
        cwd=Path.cwd(),
        input="Show architecture.",
        text=True,
        capture_output=True,
        check=False,
    )
    contexts = _contexts(tmp_path, session)

    assert completed.returncode == 0
    assert len(contexts) == 1
    assert contexts[0]["human_intent_precedence_before_restored_context"] is True
    assert contexts[0]["production_conversation_flow_binding"][
        "requested_target_flow_id"
    ] == CFA_SELF_KNOWLEDGE
    assert "selected_service: SELF_KNOWLEDGE_QUERY_RUNTIME" in completed.stdout


@pytest.mark.parametrize(
    ("human_text", "target"),
    [
        ("Implement a validator.", CFA_DEVELOPMENT_GOVERNANCE),
        ("Run the governed execution workflow.", CFA_EXECUTION),
    ],
)
def test_actionable_requests_stop_at_owner_bound_objective_readiness(
    tmp_path: Path,
    human_text: str,
    target: str,
) -> None:
    result = _submit(tmp_path, human_text, session="G66-08-ACTIONABLE")
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    envelope = context["owner_bound_clarification_envelope"]
    stages = [
        item["stage"] for item in binding["ordered_predecessor_references"]
    ]

    assert binding["requested_target_flow_id"] == target
    assert binding["permitted_next_flow_id"] == CFA_OBJECTIVE_COMMITMENT
    assert stages.index("PROPOSAL_VALIDATION") < stages.index("PROPOSAL_COMMIT")
    assert stages.index("PROPOSAL_COMMIT") < stages.index("OBJECTIVE_READINESS")
    assert stages.index("OBJECTIVE_READINESS") < stages.index(
        "OWNER_BOUND_CLARIFICATION"
    )
    assert envelope["originating_owner"] == (
        "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    )
    assert context["project_objective_inference"] is None
    assert context["admission_precedence"] is None
    assert context["constitutional_development_governance"] is None
    assert binding["authorization_created"] is False
    assert binding["worker_invoked"] is False
    assert binding["execution_invoked"] is False
    assert result["runtime_entered"] is False


def test_conversation_identity_and_revisions_survive_separate_default_turns(
    tmp_path: Path,
) -> None:
    first = _submit(
        tmp_path,
        "Show architecture.",
        session="G66-08-CWM-CONTINUITY",
    )
    second = _submit(
        tmp_path,
        "What platform capabilities are available?",
        session="G66-08-CWM-CONTINUITY",
    )
    first_binding = first["platform_core_project_services_context"][
        "production_conversation_flow_binding"
    ]
    second_binding = second["platform_core_project_services_context"][
        "production_conversation_flow_binding"
    ]

    assert first_binding["conversation_identity"] == second_binding[
        "conversation_identity"
    ]
    assert [first_binding["cwm_revision"], second_binding["cwm_revision"]] == [
        1,
        2,
    ]
    assert first_binding["cwm_state_hash"] != second_binding["cwm_state_hash"]


def test_defect_common_clarification_is_not_restored_for_the_next_reply(
    tmp_path: Path,
) -> None:
    session = "G66-08-COMMON-CLARIFICATION"
    result = run_reference_uhi_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(
            [
                "Implement a validator.",
                "/send",
                "/reply action: implement",
                "/send",
                "/exit",
            ]
        ),
        output_writer=lambda _line: None,
    )
    contexts = _contexts(tmp_path, session)
    first_envelope = contexts[0]["owner_bound_clarification_envelope"]
    second_precedence = contexts[1]["human_intent_precedence_decision"]

    assert first_envelope["originating_owner"] == (
        "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    )
    assert second_precedence["decision_disposition"] == "NEW_HUMAN_INTENT"
    assert second_precedence["active_clarification_identity"] is None
    assert contexts[1]["production_conversation_flow_binding"][
        "requested_target_flow_id"
    ] == CFA_PLATFORM_KNOWLEDGE
    assert result["approval_count"] == 0
    assert result["runtime_entered"] is False


def test_defect_default_typed_multi_turn_never_reaches_objective_commitment(
    tmp_path: Path,
) -> None:
    session = "G66-08-MULTI-TURN"
    result = run_reference_uhi_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(
            [
                "Implement a validator.",
                "/send",
                "action: implement",
                "/send",
                "subject: validator",
                "/send",
                "outcome: validated requests",
                "/send",
                "work-type: implementation",
                "/send",
                "/confirm",
                "/send",
                "/commit",
                "/send",
                "/exit",
            ]
        ),
        output_writer=lambda _line: None,
    )
    contexts = _contexts(tmp_path, session)
    bindings = [item["production_conversation_flow_binding"] for item in contexts]

    assert len(bindings) == 7
    assert len({item["conversation_identity"] for item in bindings}) == 1
    assert [item["cwm_revision"] for item in bindings] == list(range(1, 8))
    assert bindings[0]["requested_target_flow_id"] == CFA_DEVELOPMENT_GOVERNANCE
    assert all(
        item["requested_target_flow_id"] == CFA_PLATFORM_KNOWLEDGE
        for item in bindings[1:]
    )
    assert all(
        item["semantic_commit_identity"] is not None for item in bindings
    )
    assert result["approval_count"] == 0
    assert result["runtime_entered"] is False
    assert not list(tmp_path.rglob("*objective_commitment*.json"))


@pytest.mark.parametrize(
    "human_text",
    [
        "I have an idea.",
        "florbulate the quux matrix",
        "\x00",
    ],
)
def test_repaired_bound_platform_knowledge_requests_do_not_cross_flow_boundary(
    tmp_path: Path,
    human_text: str,
) -> None:
    result = _submit(tmp_path, human_text, session="G66-08-INVALID-REQUEST")
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]

    assert binding["requested_target_flow_id"] == CFA_PLATFORM_KNOWLEDGE
    assert context["project_objective_inference"] is None
    assert context["human_conversation_experience"]["response_mode"] == (
        "READ_ONLY_RESULT"
    )
    assert context["operational_clarification_envelope"] is None
    assert context.get("owner_bound_clarification_envelope") is None


def test_empty_request_fails_closed_at_the_channel_without_downstream_effect(
    tmp_path: Path,
) -> None:
    result = _submit(tmp_path, "   ", session="G66-08-EMPTY")

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_REJECTED_EMPTY_INPUT"
    assert result["submitted_request_count"] == 0
    assert result["transcript"] == [{"event": "empty_submit_rejected"}]
    assert not (tmp_path / "production_conversation_flow_binding").exists()


def test_defect_human_stop_bypasses_canonical_entry_and_binding(tmp_path: Path) -> None:
    result = run_reference_uhi_session(
        session_id="G66-08-STOP",
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["/cancel"]),
        output_writer=lambda _line: None,
    )

    assert result["transcript"] == [{"event": "cancel"}]
    assert result["submitted_request_count"] == 0
    assert _contexts(tmp_path, "G66-08-STOP") == []
    assert not (tmp_path / "production_conversation_flow_binding").exists()


def test_defect_alternate_conversation_mode_bypasses_entry_and_flow_binding(
    tmp_path: Path,
) -> None:
    fixed = iter(
        [
            "action: implement",
            "subject: Human Interaction Stack",
            "outcome: an immutable Objective Commitment",
            "work-type: IMPLEMENTATION",
        ]
    )
    output: list[str] = []
    turn = 0

    def reader(_prompt: str) -> str:
        nonlocal turn
        if turn < 4:
            value = next(fixed)
        else:
            value = next(
                item.removeprefix("next: ")
                for item in reversed(output)
                if item.startswith("next: ")
            )
        turn += 1
        return value

    result = hir_v2.run_hir_conversation_terminal_v2(
        runtime_root=tmp_path,
        workspace_identity=".",
        session_identity="G66-08-ALTERNATE",
        human_identity="local-human",
        created_at=CREATED_AT,
        input_reader=reader,
        output_writer=output.append,
    )

    assert result["terminal_condition"] == hir_v2.OBJECTIVE_COMMITMENT_CREATED
    assert result["execution_pipeline_entered"] is False
    assert not (tmp_path / "production_conversation_flow_binding").exists()
    assert not list(tmp_path.rglob("*human_intent_precedence*.json"))


def test_defect_public_conversation_v2_launcher_bypasses_canonical_entry(
    tmp_path: Path,
) -> None:
    completed = subprocess.run(
        [
            "./aicli",
            "--session-id",
            "G66-08-PUBLIC-ALTERNATE",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path),
            "--workspace",
            ".",
            "conversation-v2",
        ],
        cwd=Path.cwd(),
        input="action: implement\n",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "route: Human -> AiCLI -> HIR -> Conversation Layer V2" in (
        completed.stdout
    )
    assert not (tmp_path / "production_conversation_flow_binding").exists()
    assert not list(tmp_path.rglob("*human_intent_precedence*.json"))


def test_end_to_end_replay_tampering_fails_reconstruction(tmp_path: Path) -> None:
    result = _submit(
        tmp_path,
        "Show architecture.",
        session="G66-08-REPLAY-TAMPER",
    )
    binding = result["platform_core_project_services_context"][
        "production_conversation_flow_binding"
    ]
    replay_root = Path(binding["owner_local_replay_references"][0]).parent
    proposal_path = replay_root / "001_interpreter_proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    proposal["interpreter_version"] = "tampered"
    proposal_path.write_text(json.dumps(proposal), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_production_conversation_flow_binding_v1(replay_root)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("requested_target_owner", "SUBSTITUTED_OWNER"),
        ("requested_target_flow_id", "CFA-UNKNOWN-V1"),
    ],
)
def test_project_services_rejects_invalid_flow_and_owner_substitution(
    tmp_path: Path,
    field: str,
    value: str,
) -> None:
    result = _submit(
        tmp_path,
        "Show architecture.",
        session="G66-08-BINDING-NEGATIVE",
    )
    context = result["platform_core_project_services_context"]
    binding = deepcopy(context["production_conversation_flow_binding"])
    binding[field] = value
    unhashed = dict(binding)
    unhashed.pop("artifact_hash")
    binding["artifact_hash"] = replay_hash(unhashed)

    with pytest.raises(FailClosedRuntimeError):
        prepare_unified_human_interface_project_context(
            interface_name="aicli",
            session_id="G66-08-BINDING-NEGATIVE",
            message="Show architecture.",
            runtime_root=tmp_path,
            workspace=".",
            created_at=CREATED_AT,
            human_intent_precedence_decision=context[
                "human_intent_precedence_decision"
            ],
            production_conversation_flow_binding=binding,
        )
