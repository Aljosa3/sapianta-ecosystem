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
            "runtime_replay_reference": "/tmp/g15-hir-07-runtime/TURN-000001",
            "platform_core_runtime_delegated": True,
            "governance_authority_preserved": True,
            "provider_platform_preserved": True,
            "worker_execution_authority_preserved": True,
            "replay_authority_preserved": True,
        }

    return run


def _load_project_contexts(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "uhi_project_services").glob("*.json"))
    ]


def _load_workspace_states(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((runtime_root / session_id / "workspace_state").glob("*.json"))
    ]


def _load_clarification_continuity(runtime_root: Path, session_id: str) -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (runtime_root / session_id / "uhi_clarification_continuity").glob("*.json")
        )
    ]


def test_answered_clarification_is_consumed_and_not_reopened(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []
    session_id = "G15-HIR-07-RESOLVED-CLARIFICATION"
    reply = (
        "Change clarification state management so answered questions are recorded "
        "as reusable Platform Core behavior."
    )

    result = aicli.run_reference_uhi_submit_session(
        session_id=session_id,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Should this human interface clarification behavior belong in Platform Core architecture?",
        input_reader=_reader([reply, "/send", "/approve"]),
        output_writer=output.append,
        runtime_runner=_successful_runner(calls),
    )

    contexts = _load_project_contexts(tmp_path, session_id)
    workspace_states = _load_workspace_states(tmp_path, session_id)
    continuity = _load_clarification_continuity(tmp_path, session_id)
    resolution = contexts[1]["development_intent_resolution"]

    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_CONVERSATION_COMPLETED"
    assert result["submitted_request_count"] == 2
    assert result["clarification_question_count"] == 1
    assert len(contexts) == 2
    assert len(continuity) == 1
    assert calls
    assert "\n".join(output).count("Clarification required before governed execution.") == 1

    assert resolution["clarification_reply_bound"] is True
    assert resolution["clarification_resolved"] is True
    assert resolution["clarification_reply_resolution_source"] == (
        "ORIGINAL_REQUEST_WITH_BOUND_CLARIFICATION_REPLY"
    )
    assert resolution["clarification_required"] is False
    assert resolution["summary_admissible"] is True
    assert resolution["runtime_binding_admissible"] is True
    assert resolution["answered_clarification_question_ids"]
    assert resolution["clarification_question_bindings"]
    assert {
        binding["question_id"] for binding in resolution["clarification_question_bindings"]
    } == set(resolution["answered_clarification_question_ids"])

    continuity_artifact = continuity[0]
    assert continuity_artifact["clarification_resolved"] is True
    assert continuity_artifact["answered_clarification_question_ids"] == resolution[
        "answered_clarification_question_ids"
    ]
    assert workspace_states[-1]["pending_clarification_request"] is None
    assert result["pending_approval"] is False
    assert result["runtime_entered"] is True
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
