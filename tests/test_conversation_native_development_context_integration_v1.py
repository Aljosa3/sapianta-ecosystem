"""Tests for AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_V1."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import json
from pathlib import Path
import shutil
from typing import Any

import pytest

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.provider.providers.openai_provider import (
    OPENAI_PROVIDER_ID,
    OPENAI_PROVIDER_VERSION,
    OpenAIProviderAdapter,
    openai_provider_metadata,
)
from aigol.runtime.context_assembled_to_ppp_routing_continuation import POST_CONTEXT_CONTINUATION_REACHED_PPP
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.conversation_native_development_context_integration import (
    CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED,
    reconstruct_conversation_native_development_context_integration_replay,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.post_entry_continuation_gate_runtime import CONTINUATION_ALLOWED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-02T16:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"
CLAUDE_MILESTONE_ID = "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = OPENAI_PROVIDER_ID
    provider_version: str = OPENAI_PROVIDER_VERSION
    calls: int = 0

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str):
        self.calls += 1
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
            timestamp=timestamp,
        )


def _prompt() -> str:
    return (
        f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
        "No exchange integration. No order placement. No live trading. No dispatch. No execution."
    )


def _claude_prompt() -> str:
    return (
        f"Implement {CLAUDE_MILESTONE_ID}. Goal: Extend the certified provider-neutral external worker "
        "architecture with Claude support while reusing existing governance, replay, validation, mutation, "
        "and worker lifecycle infrastructure."
    )


def _valid_provider_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create a proposal-only Claude external worker provider adapter.",
        "proposed_outputs": [
            "aigol/runtime/claude_external_worker_provider_adapter.py",
            "tests/test_claude_external_worker_provider_adapter_v1.py",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": [
            "Adapter remains provider-neutral above the adapter layer.",
        ],
        "known_gaps": [
            "Real Claude endpoint invocation remains separately certified.",
        ],
    }


def _available_openai_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata(status=AVAILABLE))
    return registry


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt_text: str) -> str:
        return next(iterator)

    return read


def _copy_governance_subset(tmp_path) -> Path:
    target = tmp_path / "governance_subset"
    target.mkdir()
    for source in GOVERNANCE_ROOT.iterdir():
        if source.is_file():
            shutil.copy2(source, target / source.name)
    return target


def test_conversation_native_development_context_integration_assembles_context_and_chain(tmp_path) -> None:
    capture = run_conversation_native_development_context_integration(
        prompt_id="SESSION-NATIVE-CONTEXT-000001:TURN-000001",
        human_prompt=_prompt(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "turn",
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-NATIVE-CONTEXT-000001",
        turn_id="TURN-000001",
    )
    reconstructed = reconstruct_conversation_native_development_context_integration_replay(tmp_path / "turn")

    assert capture["response_status"] == CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
    assert capture["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert capture["task_intake_reference"]
    assert capture["context_assembly_reference"]
    assert capture["context_status"] == "CONTEXT_ASSEMBLED"
    assert capture["context_hash"].startswith("sha256:")
    assert capture["canonical_chain_id"]
    assert capture["missing_context"] == []
    assert capture["ambiguous_context"] == []
    assert capture["provider_necessity_classification"] == "PROVIDER_REQUIRED_FOR_PROPOSAL"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert "prepare governed development proposal contract" in capture["suggested_next_actions"]
    assert reconstructed["context_hash"] == capture["context_hash"]
    assert reconstructed["replay_artifact_count"] == 9


def test_interactive_conversation_development_prompt_outputs_context_status(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-NATIVE-CONTEXT-CLI-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence([_prompt(), "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert result["current_chain_id"] == turn["canonical_chain_id"]
    assert turn["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert turn["task_intake_reference"]
    assert turn["context_assembly_reference"]
    assert turn["context_status"] == "CONTEXT_ASSEMBLED"
    assert turn["context_hash"].startswith("sha256:")
    assert turn["provider_necessity_classification"] == "PROVIDER_REQUIRED_FOR_PROPOSAL"
    assert turn["missing_context"] == []
    assert turn["ambiguous_context"] == []
    assert "context_status: CONTEXT_ASSEMBLED" in output[0]
    assert "context_hash: sha256:" in output[0]
    assert (
        tmp_path
        / "interactive_runtime"
        / "SESSION-NATIVE-CONTEXT-CLI-000001"
        / "TURN-000001"
        / "development_context_assembly"
        / "003_development_context_assembly_recorded.json"
    ).exists()


def test_interactive_conversation_post_entry_clarification_resumes_continuation(tmp_path, monkeypatch) -> None:
    provider_response = _valid_provider_response()
    calls: list[dict[str, Any]] = []

    def fake_provider_client(
        payload: dict[str, Any],
        *,
        api_key: str,
        endpoint: str,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        calls.append(
            {
                "payload": payload,
                "api_key_seen": bool(api_key),
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
            }
        )
        assert "DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible JSON object" in payload["input"]
        assert "Proposal must remain proposal-only" in payload["input"]
        return {
            "id": "resp-native-context-provider-projection-001",
            "output_text": json.dumps(provider_response),
        }

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-native-context-openai-worker-clarification-001",
            "output_text": "Return bounded findings for post-entry clarification continuation.",
        }

    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_registry",
        _available_openai_registry,
    )
    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_provider_client),
    )
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-NATIVE-CONTEXT-CLI-CLARIFICATION-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence([_claude_prompt(), "continue ppp", "exit"]),
        output_func=output.append,
    )
    first, second = result["turns"]

    assert result["failed_turns"] == 0
    assert first["post_entry_continuation_gate_status"] == "CLARIFICATION_REQUIRED"
    assert first["post_entry_continuation_allowed"] is False
    assert first["clarification_required"] is True
    assert first["open_clarification_detected"] is True
    assert first["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert first["workflow_status"]["workflow_complete"] is False
    assert second["canonical_chain_id"] == first["canonical_chain_id"]
    assert second["post_entry_continuation_gate_status"] == CONTINUATION_ALLOWED
    assert second["post_entry_continuation_allowed"] is True
    assert second["post_context_continuation_status"] == POST_CONTEXT_CONTINUATION_REACHED_PPP
    assert second["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert second["execution_summary_reference"]
    assert second["human_confirmation_reference"]
    assert second["execution_authorization_status"] == "EXECUTION_AUTHORIZED"
    assert second["worker_request_reached"] is True
    assert second["worker_invocation_request_status"] == "WORKER_INVOCATION_REQUEST_CREATED"
    assert calls and calls[0]["api_key_seen"] is True
    assert "Workflow State: WAITING_FOR_OPERATOR" in output[0]
    assert "WAITING FOR OPERATOR INPUT" in output[0]
    assert "Post-Context Continuation" in output[1]
    assert (
        tmp_path
        / "interactive_runtime"
        / "SESSION-NATIVE-CONTEXT-CLI-CLARIFICATION-000001"
        / "TURN-000002"
        / "post_entry_continuation_gate"
        / "000_post_entry_continuation_gate_recorded.json"
    ).exists()
    assert (
        tmp_path
        / "interactive_runtime"
        / "SESSION-NATIVE-CONTEXT-CLI-CLARIFICATION-000001"
        / "TURN-000002"
        / "post_context_continuation"
        / "000_post_context_continuation_recorded.json"
    ).exists()


def test_interactive_conversation_auto_continues_context_assembled_to_ppp(tmp_path, monkeypatch) -> None:
    adapter = FakeProviderAdapter(_valid_provider_response())

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-native-context-openai-worker-001",
            "output_text": "Return bounded findings for native context continuation.",
        }

    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_registry",
        _available_openai_registry,
    )
    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_adapter",
        lambda: adapter,
    )
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-NATIVE-CONTEXT-CLI-AUTO-CONTINUE-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
            "--auto-continue",
        ]
    )
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence([_claude_prompt(), "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]

    assert result["failed_turns"] == 0
    assert result["auto_continue_enabled"] is True
    assert turn["context_status"] == "CONTEXT_ASSEMBLED"
    assert turn["provider_necessity_classification"] == "PROVIDER_REQUIRED_FOR_PROPOSAL"
    assert turn["post_entry_continuation_gate_status"] == CONTINUATION_ALLOWED
    assert turn["post_entry_continuation_allowed"] is True
    assert turn["post_entry_execution_summary_required"] is True
    assert turn["post_entry_human_confirmation_required"] is True
    assert turn["post_entry_authorization_required"] is True
    assert turn["post_entry_continuation_gate_replay_reference"]
    assert turn["post_context_continuation_status"] == POST_CONTEXT_CONTINUATION_REACHED_PPP
    assert turn["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert turn["post_context_continuation_replay_reference"]
    assert turn["ppp_routing_replay_reference"]
    assert turn["implementation_handoff_reference"]
    assert adapter.calls == 1
    assert "Post-Context Continuation" in output[0]
    assert (
        tmp_path
        / "interactive_runtime"
        / "SESSION-NATIVE-CONTEXT-CLI-AUTO-CONTINUE-000001"
        / "TURN-000001"
        / "post_entry_continuation_gate"
        / "000_post_entry_continuation_gate_recorded.json"
    ).exists()
    assert (
        tmp_path
        / "interactive_runtime"
        / "SESSION-NATIVE-CONTEXT-CLI-AUTO-CONTINUE-000001"
        / "TURN-000001"
        / "post_context_continuation"
        / "conversation_ppp_routing"
        / "conversation_ppp_route"
        / "000_conversation_ppp_route_recorded.json"
    ).exists()


@pytest.mark.parametrize("continuation_command", ["continue", "continue ppp"])
def test_interactive_conversation_replay_restored_continue_resumes_without_rerouting(
    tmp_path,
    monkeypatch,
    continuation_command: str,
) -> None:
    provider_response = _valid_provider_response()
    calls: list[dict[str, Any]] = []

    def fake_provider_client(
        payload: dict[str, Any],
        *,
        api_key: str,
        endpoint: str,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        calls.append({"api_key_seen": bool(api_key)})
        return {
            "id": "resp-native-context-provider-projection-restored-001",
            "output_text": json.dumps(provider_response),
        }

    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-native-context-openai-worker-restored-001",
            "output_text": "Return bounded findings for restored post-entry continuation.",
        }

    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_registry",
        _available_openai_registry,
    )
    monkeypatch.setattr(
        aigol_cli,
        "_post_context_continuation_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_provider_client),
    )
    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)
    parser = build_parser()
    runtime_root = tmp_path / "interactive_runtime"
    session_id = "SESSION-NATIVE-CONTEXT-CLI-RESTORE-CONTINUE-000001"
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(runtime_root),
        ]
    )
    first_output: list[str] = []

    first_result = run_interactive_conversation(
        args,
        input_func=_input_sequence([_claude_prompt(), "exit"]),
        output_func=first_output.append,
    )

    assert first_result["failed_turns"] == 0
    assert first_result["turns"][0]["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"

    second_output: list[str] = []
    second_result = run_interactive_conversation(
        args,
        input_func=_input_sequence([continuation_command, "exit"]),
        output_func=second_output.append,
    )
    second = second_result["turns"][0]

    assert second_result["failed_turns"] == 0
    assert second["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert second["routing_visibility_workflow_id"] == "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
    assert second["post_entry_continuation_gate_status"] == CONTINUATION_ALLOWED
    assert second["post_context_continuation_status"] == POST_CONTEXT_CONTINUATION_REACHED_PPP
    assert second["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert second["canonical_chain_id"] == first_result["turns"][0]["canonical_chain_id"]
    assert second["worker_request_reached"] is True
    assert calls and calls[0]["api_key_seen"] is True
    assert not (runtime_root / session_id / "TURN-000002" / "conversational_cli_routing").exists()
    assert (
        runtime_root
        / session_id
        / "TURN-000002"
        / "pending_post_entry_continuation_restore"
        / "000_pending_post_entry_continuation_restored.json"
    ).exists()


@pytest.mark.parametrize("lifecycle_command", ["approve", "resume", "retry", "cancel", "clarify"])
def test_interactive_lifecycle_commands_do_not_reroute_while_native_workflow_waits(
    tmp_path,
    lifecycle_command: str,
) -> None:
    parser = build_parser()
    runtime_root = tmp_path / "interactive_runtime"
    session_id = f"SESSION-NATIVE-CONTEXT-LIFECYCLE-{lifecycle_command.upper()}-000001"
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(runtime_root),
        ]
    )

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence([_claude_prompt(), lifecycle_command, "exit"]),
        output_func=lambda _line: None,
    )
    second = result["turns"][1]

    assert result["failed_turns"] == 1
    assert second["fail_closed"] is True
    assert second["routing_visibility_workflow_id"] == "NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION"
    assert "unsupported conversational workflow selection" in str(second["failure_reason"])
    assert not (runtime_root / session_id / "TURN-000002" / "conversational_cli_routing").exists()


def test_conversation_native_development_context_fails_closed_when_context_missing(tmp_path) -> None:
    governance_root = _copy_governance_subset(tmp_path)
    (governance_root / "TRADING_DOMAIN_FOUNDATION_V1.md").unlink()

    capture = run_conversation_native_development_context_integration(
        prompt_id="SESSION-NATIVE-CONTEXT-MISSING-000001:TURN-000001",
        human_prompt=_prompt(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "missing_turn",
        governance_root=governance_root,
        session_id="SESSION-NATIVE-CONTEXT-MISSING-000001",
        turn_id="TURN-000001",
    )

    assert capture["fail_closed"] is True
    assert capture["response_status"] == "FAILED_CLOSED"
    assert capture["context_status"] == "FAILED_CLOSED_MISSING_CONTEXT"
    assert capture["missing_context"]
    assert capture["canonical_chain_id"]
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_conversation_native_development_context_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    run_conversation_native_development_context_integration(
        prompt_id="SESSION-NATIVE-CONTEXT-CORRUPT-000001:TURN-000001",
        human_prompt=_prompt(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_turn",
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-NATIVE-CONTEXT-CORRUPT-000001",
        turn_id="TURN-000001",
    )
    path = (
        tmp_path
        / "corrupt_turn"
        / "native_development_context_integration"
        / "000_conversation_native_development_context_integrated.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["context_hash"] = "sha256:corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_native_development_context_integration_replay(tmp_path / "corrupt_turn")


def test_conversation_native_development_context_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.conversation_native_development_context_integration as runtime

    runtime_source = inspect.getsource(runtime)
    cli_source = inspect.getsource(aigol_cli)

    assert "OpenAIProviderAdapter" not in runtime_source
    assert "run_provider_attachment(" not in runtime_source
    assert "dispatch_worker(" not in runtime_source
    assert "invoke_worker(" not in runtime_source
    assert "create_execution_request(" not in runtime_source
    assert "start_execution(" not in runtime_source
    assert "_post_context_continuation_should_run" in cli_source
    assert "continue_context_assembled_to_ppp_routing(" in cli_source
