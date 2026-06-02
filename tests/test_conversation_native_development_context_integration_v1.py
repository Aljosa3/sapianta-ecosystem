"""Tests for AIGOL_CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
import shutil

import pytest

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_context_integration import (
    CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED,
    reconstruct_conversation_native_development_context_integration_replay,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-02T16:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"


def _prompt() -> str:
    return (
        f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
        "No exchange integration. No order placement. No live trading. No dispatch. No execution."
    )


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

    for source in (runtime_source, cli_source):
        assert "OpenAIProviderAdapter" not in source
        assert "run_provider_attachment(" not in source
        assert "dispatch_worker(" not in source
        assert "invoke_worker(" not in source
        assert "create_execution_request(" not in source
        assert "start_execution(" not in source
