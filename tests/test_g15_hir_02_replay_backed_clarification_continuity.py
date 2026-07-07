from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aicli


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _successful_runner(calls: list[dict]):
    def run(**kwargs):
        calls.append(kwargs)
        return {
            "runtime_binding_status": aicli.REFERENCE_UHI_BOUND,
            "runtime_entered": True,
            "governance_authorization_reached": True,
            "provider_invocation_reached": True,
            "worker_execution_reached": True,
            "replay_certification_reached": True,
            "runtime_replay_reference": "/tmp/g15-hir-02-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def _load_contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _load_continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_clarification_continuity").glob("*.json"))
    ]


def test_submit_clarification_reply_binds_to_replay_backed_active_clarification(tmp_path: Path) -> None:
    calls: list[dict] = []
    session_id = "G15-HIR-02-RESOLVED"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(["Implement governance documentation indexing utility.", "/send", "/approve"]),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_contexts(tmp_path, session_id)
    continuities = _load_continuity(tmp_path, session_id)
    continuity_context = contexts[1]
    continuity = continuities[0]
    resolution = continuity_context["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["clarification_question_count"] == 1
    assert calls[0]["prompt"] == "Implement governance documentation indexing utility."
    assert continuity["reply_bound_to_active_clarification"] is True
    assert continuity["clarification_continuity_status"] == "CLARIFICATION_RESOLVED"
    assert continuity["clarification_resolved"] is True
    assert continuity["new_governed_request_created"] is False
    assert continuity["replay_lineage_preserved"] is True
    assert continuity["semantic_lineage_preserved"] is True
    assert continuity["human_interface_authority"] is False
    assert continuity["active_clarification_state"]["original_message"] == "I have an idea."
    assert resolution["clarification_reply_bound"] is True
    assert resolution["clarification_resolved"] is True
    assert resolution["new_governed_request_created"] is False
    assert resolution["summary_admissible"] is True
    assert continuity_context["clarification_continuity"]["artifact_hash"] == continuity["artifact_hash"]


def test_insufficient_submit_clarification_reply_remains_replay_continuous(tmp_path: Path) -> None:
    calls: list[dict] = []
    session_id = "G15-HIR-02-STILL-REQUIRED"

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "I have an idea.",
        input_reader=_reader(
            [
                "Improve this.",
                "/send",
                "Implement replay observation diagnostics utility.",
                "/send",
                "/approve",
            ]
        ),
        output_writer=lambda _line: None,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_contexts(tmp_path, session_id)
    continuities = _load_continuity(tmp_path, session_id)
    unresolved_context = contexts[1]
    resolved_context = contexts[2]
    unresolved = continuities[0]
    resolved = continuities[1]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 3
    assert result["clarification_question_count"] == 2
    assert calls[0]["prompt"] == "Implement replay observation diagnostics utility."
    assert unresolved["reply_bound_to_active_clarification"] is True
    assert unresolved["clarification_continuity_status"] == "CLARIFICATION_STILL_REQUIRED"
    assert unresolved["clarification_resolved"] is False
    assert unresolved["new_governed_request_created"] is False
    assert unresolved_context["development_intent_resolution"]["clarification_reply_bound"] is True
    assert unresolved_context["development_intent_resolution"]["clarification_required"] is True
    assert resolved["reply_bound_to_active_clarification"] is True
    assert resolved["clarification_continuity_status"] == "CLARIFICATION_RESOLVED"
    assert resolved["new_governed_request_created"] is False
    assert resolved_context["development_intent_resolution"]["summary_admissible"] is True
