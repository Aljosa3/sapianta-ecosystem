from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli, aigol_cli
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
    run_human_interface_runtime_entry,
)


def _runtime_runner(calls: list[dict]):
    def run(args, input_func, output_func):
        prompt = input_func("")
        calls.append(
            {
                "session_id": args.session_id,
                "operator_context": args.operator_context,
                "prompt": prompt,
            }
        )
        output_func("canonical runtime accepted")
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": True,
                    "replay_certification_reached": True,
                    "execution_authorization_status": "EXECUTION_AUTHORIZED",
                    "openai_provider_reached": True,
                    "execution_preparation_status": "EXECUTION_READY",
                    "worker_assignment_status": "WORKER_ASSIGNED",
                    "worker_dispatch_status": "WORKER_DISPATCHED",
                    "worker_invocation_status": "WORKER_INVOKED",
                    "result_validation_status": "RESULT_VALIDATION_COMPLETED",
                    "replay_certification_status": "REPLAY_CERTIFICATION_COMPLETED",
                    "execution_summary_reference": "summary",
                    "human_confirmation_reference": "approval",
                    "replay_reference": str(Path(args.runtime_root) / "runtime" / "TURN-000001"),
                }
            ],
        }

    return run


def test_canonical_runtime_entry_service_owns_shared_runtime_binding(tmp_path: Path) -> None:
    calls: list[dict] = []

    result = run_human_interface_runtime_entry(
        interface_name="reference test interface",
        session_id="UHI-CANONICAL",
        human_requests=["Implement governance validation utility."],
        created_at="2026-07-05T00:00:00Z",
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_runtime_runner(calls),
    )

    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["runtime_entered"] is True
    assert result["platform_core_project_services_delegated"] is True
    assert result["human_interface_runtime_entry_orchestrates"] is False
    assert result["development_intent_resolution"]["development_intent_resolution_authority"] == "PLATFORM_CORE"
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    assert calls[0]["prompt"] == "Implement governance validation utility."
    assert (
        tmp_path
        / "UHI-CANONICAL"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()


def test_aicli_default_approval_uses_canonical_runtime_entry(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(aicli, "run_interactive_conversation", _runtime_runner(calls))

    result = aicli.run_reference_uhi_session(
        session_id="AICLI-G14-30",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(["Implement replay evidence utility.", "/approve", "/exit"]),
        output_writer=lambda _line: None,
    )

    runtime_result = result["runtime_result"]
    assert result["runtime_status"] == aicli.REFERENCE_UHI_BOUND
    assert runtime_result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert runtime_result["human_interface_runtime_entry_service_used"] is True
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"


def test_aigol_next_uses_same_canonical_runtime_entry(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []

    def presentation(**kwargs):
        return {
            "artifact_hash": "sha256:presentation",
            "command": "aigol next",
            "replay_reference": str(tmp_path / "presentation"),
            "session_id": kwargs["session_id"],
        }

    monkeypatch.setattr(aigol_cli, "run_acli_next_conversational_session", presentation)
    monkeypatch.setattr(aigol_cli, "run_interactive_conversation", _runtime_runner(calls))

    result = aigol_cli._run_acli_next_runtime_bound_session(
        session_id="AIGOL-NEXT-G14-30",
        prompts=["Implement governance validation utility."],
        created_at="2026-07-05T00:00:00Z",
        replay_dir=tmp_path,
        workspace=".",
    )

    assert result["runtime_binding_status"] == aigol_cli.ACLI_NEXT_RUNTIME_BOUND
    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    assert result["human_interface_runtime_entry_service_used"] is True
    assert calls[0]["operator_context"] == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    assert (
        tmp_path
        / "AIGOL-NEXT-G14-30"
        / "workspace_state"
        / "001_platform_core_workspace_state_recorded.json"
    ).exists()


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read
