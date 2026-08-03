from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_conversation_flow_binding import (
    reconstruct_production_conversation_flow_binding_v1,
)
from aigol.runtime.transport.serialization import replay_hash


SESSION = "G66-13-CANONICAL-TYPED"
CREATED = "2026-08-03T18:00:00Z"


def _time(second: int) -> str:
    return f"2026-08-03T18:00:{second:02d}Z"


def _manifest(root: Path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G66-13-000001",
        canonical_chain_id="CHAIN-G66-13-000001",
        implementation_bundle_id="G66_13_CANONICAL_TYPED_COMPOSITION",
        source_candidate_reference="CANDIDATE-G66-13-000001",
        source_candidate_hash=replay_hash({"source": "G66-13"}),
        implementation_handoff_reference="HANDOFF-G66-13-000001",
        implementation_handoff_hash=replay_hash({"handoff": "G66-13"}),
        provider_generation_authorization_reference="AUTH-G66-13-000001",
        provider_generation_authorization_hash=replay_hash({"auth": "G66-13"}),
        provider_response_reference="RESPONSE-G66-13-000001",
        provider_response_hash=replay_hash({"response": "G66-13"}),
        target_domain="PLATFORM_CORE",
        target_resource="G66_13_COMPLETION",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G66-13-000001",
                "target_path": "bounded/g66_13_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED,
        replay_dir=root / "manifest",
    )["implementation_manifest_artifact"]


def _entry(
    root: Path,
    workspace: Path,
    request: str,
    *,
    second: int,
    artifacts: list[dict] | None = None,
) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="aicli",
        session_id=SESSION,
        human_requests=[request],
        created_at=_time(second),
        runtime_root=root,
        workspace=workspace,
        governed_runtime_runner=run_interactive_conversation,
        explicit_canonical_artifacts=artifacts or [],
    )


def test_default_canonical_entry_composes_existing_typed_protocol_to_admission(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    turns = (
        "action: Implement and normalize",
        "subject: a repository implementation change",
        "outcome: canonical change evidence",
        "work-type: ANALYSIS",
    )
    initial = _entry(
        root,
        workspace,
        "Implement a validator.",
        second=1,
    )
    assert initial["canonical_typed_semantic_composition"] is None
    captures = [
        _entry(root, workspace, text, second=index)
        for index, text in enumerate(turns, start=2)
    ]

    expected_classes = (
        "OPERATIVE_ACTION",
        "OPERATIVE_SUBJECT",
        "DESIRED_OUTCOME",
        "WORK_TYPE",
    )
    revisions = []
    semantic_revisions = []
    for capture, expected_class in zip(captures, expected_classes):
        composition = capture["canonical_typed_semantic_composition"]
        binding_capture = capture["production_conversation_binding"]
        state = binding_capture["conversation_state"]
        slots = state["semantic_memory"]["semantic_slots"]
        assert composition["control"] == "SEMANTIC_TURN"
        assert any(slot["slot_class"] == expected_class for slot in slots)
        assert binding_capture["proposal_validation"][
            "validation_disposition"
        ] == "ADMISSIBLE"
        assert binding_capture["proposal_commit"]["disposition"] == "COMMITTED"
        assert reconstruct_production_conversation_flow_binding_v1(
            binding_capture["production_conversation_replay_reference"]
        )["reconstruction_verified"] is True
        revisions.append(state["revision"])
        semantic_revisions.append(state["semantic_revision"])

    assert revisions == sorted(revisions)
    assert semantic_revisions == sorted(semantic_revisions)
    assert len(set(revisions)) == 4
    assert len(set(semantic_revisions)) == 4

    confirmation_action = captures[-1]["canonical_typed_semantic_composition"][
        "expected_confirmation_action"
    ]
    assert confirmation_action is not None, captures[-1][
        "production_conversation_binding"
    ]["objective_readiness_report"]["refusal_reasons"]
    assert confirmation_action.startswith("/confirm sha256:")
    confirmed = _entry(root, workspace, confirmation_action, second=6)
    confirmed_composition = confirmed["canonical_typed_semantic_composition"]
    assert confirmed_composition["control"] == "CANDIDATE_CONFIRMATION"
    assert confirmed["production_conversation_binding"][
        "objective_readiness_report"
    ]["readiness_disposition"] == "READY"
    commit_action = confirmed_composition["expected_commit_action"]
    assert commit_action.startswith("/commit sha256:")

    committed = _entry(
        root,
        workspace,
        commit_action,
        second=7,
        artifacts=[_manifest(tmp_path / "artifact")],
    )
    composition = committed["canonical_typed_semantic_composition"]
    admission = committed["committed_objective_admission"]
    assert composition["control"] == "OBJECTIVE_COMMITMENT"
    assert composition["objective_commitment"]["commitment_record_created"] is True
    assert admission["admission_status"] == (
        "COMMITTED_OBJECTIVE_ADMITTED_TO_PLATFORM_CORE"
    )
    assert admission["platform_core_admission"]["admission_status"] == (
        "EXPLICIT_CERTIFIED_CAPABILITY_REQUEST_ADMITTED"
    )
    assert committed["platform_core_project_services_context"][
        "project_objective_inference"
    ]["objective_sufficient"] is True
    assert admission["authorization_granted"] is False
    assert admission["worker_dispatched"] is False
    assert admission["execution_started"] is False
    assert reconstruct_production_conversation_flow_binding_v1(
        committed["production_conversation_binding"][
            "production_conversation_replay_reference"
        ]
    )["reconstruction_verified"] is True


def test_exact_confirmation_and_commitment_controls_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    workspace = tmp_path / "workspace"
    _entry(
        root,
        workspace,
        "Implement a validator.",
        second=1,
    )
    for index, text in enumerate(
        (
            "action: Implement",
            "subject: a repository change",
            "outcome: governed evidence",
            "work-type: ANALYSIS",
        ),
        start=2,
    ):
        _entry(root, workspace, text, second=index)

    with pytest.raises(FailClosedRuntimeError, match="exact /confirm"):
        _entry(root, workspace, "/confirm sha256:" + "0" * 64, second=6)

    cwm_files = list((root / "production_conversation_cwm").rglob("state.json"))
    assert len(cwm_files) == 1
    assert not list(root.rglob("*worker*dispatch*recorded.json"))
    assert not list(root.rglob("*execution*authorization*recorded.json"))


def test_default_aicli_multiturn_reaches_ready_with_exact_confirmation(
    tmp_path: Path,
) -> None:
    outputs: list[str] = []
    fixed = iter(
        [
            "Implement a validator.",
            "/send",
            "action: Implement and normalize",
            "/send",
            "subject: a repository implementation change",
            "/send",
            "outcome: canonical change evidence",
            "/send",
            "work-type: ANALYSIS",
            "/send",
        ]
    )
    phase = 0

    def reader(_prompt: str) -> str:
        nonlocal phase
        try:
            return next(fixed)
        except StopIteration:
            if phase == 0:
                matches = re.findall(r"/confirm sha256:[0-9a-f]{64}", "\n".join(outputs))
                assert matches
                phase = 1
                return matches[-1]
            if phase == 1:
                phase = 2
                return "/send"
            return "/exit"

    result = run_reference_uhi_session(
        session_id="G66-13-DEFAULT-AICLI",
        created_at=CREATED,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path / "workspace",
        input_reader=reader,
        output_writer=outputs.append,
    )

    contexts = sorted(
        (tmp_path / "runtime" / "G66-13-DEFAULT-AICLI").rglob(
            "*_uhi_project_context_recorded.json"
        )
    )
    assert len(contexts) == 6
    binding = result["platform_core_project_services_context"][
        "production_conversation_flow_binding"
    ]
    assert any(
        predecessor["stage"] == "HUMAN_CONFIRMATION"
        for predecessor in binding["ordered_predecessor_references"]
    )
    readiness_reference = next(
        predecessor["replay_reference"]
        for predecessor in binding["ordered_predecessor_references"]
        if predecessor["stage"] == "OBJECTIVE_READINESS"
    )
    readiness = json.loads(Path(readiness_reference).read_text(encoding="utf-8"))
    assert readiness["readiness_disposition"] == "READY"
    assert result["runtime_entered"] is False
    assert not list((tmp_path / "runtime").rglob("*worker*dispatch*recorded.json"))
