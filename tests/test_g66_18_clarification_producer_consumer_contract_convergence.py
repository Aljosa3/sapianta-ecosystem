from __future__ import annotations

import json
from pathlib import Path
import subprocess

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.production_conversation_flow_binding import (
    reconstruct_production_conversation_flow_binding_v1,
)


CREATED = "2026-08-04T10:00:00Z"
SESSION = "G66-18-CLARIFICATION-CONTRACT"
REPOSITORY = Path(__file__).resolve().parents[1]


def _entry(root: Path, workspace: Path, request: str, second: int) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="aicli",
        session_id=SESSION,
        human_requests=[request],
        created_at=f"2026-08-04T10:00:{second:02d}Z",
        runtime_root=root,
        workspace=workspace,
        governed_runtime_runner=run_interactive_conversation,
    )


def _question(capture: dict) -> str:
    return capture["platform_core_project_services_context"][
        "human_conversation_experience"
    ]["clarification_questions"][0]


def _contexts(root: Path, session: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (root / session).rglob("*_uhi_project_context_recorded.json")
        )
    ]


def test_objective_readiness_presents_only_the_exact_next_g60_control(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"

    initial = _entry(root, workspace, "Implement a validator.", 1)
    envelope = initial["owner_bound_clarification_envelope"]

    assert envelope["reason_code"] == "OBJECTIVE_READINESS_REQUIRED"
    assert envelope["required_field_or_evidence_codes"] == ["action: <value>"]
    assert _question(initial) == (
        "Provide the next Conversation field exactly as: action: <value>."
    )
    assert "OPERATIVE_ACTION" not in _question(initial)
    assert initial["canonical_typed_semantic_composition"] is None

    rejected = _entry(root, workspace, "OPERATIVE_ACTION: implement", 2)
    assert rejected["canonical_typed_semantic_composition"] is None
    assert rejected["production_conversation_flow_binding"] == initial[
        "production_conversation_flow_binding"
    ]
    assert _question(rejected) == _question(initial)


def test_presented_controls_advance_cwm_to_candidate_review(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    initial = _entry(root, workspace, "Implement a validator.", 1)
    captures = [initial]
    turns = (
        ("action: implement", "subject: <value>"),
        ("subject: validator", "outcome: <value>"),
        ("outcome: validated requests", "work-type: <value>"),
        ("work-type: ANALYSIS", None),
    )

    for second, (turn, next_control) in enumerate(turns, start=2):
        capture = _entry(root, workspace, turn, second)
        captures.append(capture)
        composition = capture["canonical_typed_semantic_composition"]
        assert composition["control"] == "SEMANTIC_TURN"
        assert capture["production_conversation_binding"]["proposal_validation"][
            "validation_disposition"
        ] == "ADMISSIBLE"
        assert capture["production_conversation_binding"]["proposal_commit"][
            "disposition"
        ] == "COMMITTED"
        if next_control is not None:
            assert capture["owner_bound_clarification_envelope"][
                "required_field_or_evidence_codes"
            ] == [next_control]
            assert _question(capture) == (
                "Provide the next Conversation field exactly as: "
                f"{next_control}."
            )

    states = [
        capture["production_conversation_binding"]["conversation_state"]
        for capture in captures
    ]
    assert [state["revision"] for state in states] == [1, 4, 6, 8, 10]
    assert len(
        {
            capture["production_conversation_binding"][
                "objective_readiness_report"
            ]["report_checksum"]
            for capture in captures
        }
    ) == 5
    final = captures[-1]
    final_state = states[-1]
    slot_classes = {
        slot["slot_class"]
        for slot in final_state["semantic_memory"]["semantic_slots"]
    }
    assert {
        "OPERATIVE_ACTION",
        "OPERATIVE_SUBJECT",
        "DESIRED_OUTCOME",
        "WORK_TYPE",
    } <= slot_classes
    assert final["canonical_typed_semantic_composition"][
        "expected_confirmation_action"
    ].startswith("/confirm sha256:")
    assert final["owner_bound_clarification_envelope"]["reason_code"] == (
        "EXACT_HUMAN_CANDIDATE_CONFIRMATION_REQUIRED"
    )
    assert final["canonical_typed_semantic_composition"]["candidate_review"] is not None
    assert final["committed_objective_admission"] is None

    for capture in captures:
        reconstruction = reconstruct_production_conversation_flow_binding_v1(
            capture["production_conversation_binding"][
                "production_conversation_replay_reference"
            ]
        )
        assert reconstruction["reconstruction_verified"] is True


def test_repository_aicli_follows_presented_controls_to_candidate_review(
    tmp_path: Path,
) -> None:
    session = "G66-18-REAL-AICLI"
    completed = subprocess.run(
        [
            "./aicli",
            "--session-id",
            session,
            "--created-at",
            CREATED,
            "--runtime-root",
            str(tmp_path),
            "--workspace",
            str(tmp_path / "workspace"),
        ],
        cwd=REPOSITORY,
        input=(
            "Implement a validator.\n/send\n"
            "action: implement\n/send\n"
            "subject: validator\n/send\n"
            "outcome: validated requests\n/send\n"
            "work-type: ANALYSIS\n/send\n"
            "/exit\n"
        ),
        text=True,
        capture_output=True,
        check=False,
    )
    contexts = _contexts(tmp_path, session)

    assert completed.returncode == 0, completed.stderr
    assert len(contexts) == 5
    assert "exactly as: action: <value>" in completed.stdout
    assert "exactly as: subject: <value>" in completed.stdout
    assert "exactly as: outcome: <value>" in completed.stdout
    assert "exactly as: work-type: <value>" in completed.stdout
    assert "/confirm sha256:" in completed.stdout
    revisions = [
        context["production_conversation_flow_binding"]["cwm_revision"]
        for context in contexts
    ]
    assert revisions == [1, 4, 6, 8, 10]
    final_envelope = contexts[-1]["owner_bound_clarification_envelope"]
    assert final_envelope["reason_code"] == (
        "EXACT_HUMAN_CANDIDATE_CONFIRMATION_REQUIRED"
    )
    assert all(context["project_objective_inference"] is None for context in contexts)
    assert not list(tmp_path.rglob("*execution_authorization*.json"))
    assert not list(tmp_path.rglob("*worker_invocation*.json"))
