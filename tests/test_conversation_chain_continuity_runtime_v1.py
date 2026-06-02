"""Tests for CONVERSATION_CHAIN_CONTINUITY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_chain_continuity_runtime import (
    CONVERSATION_CHAIN_CONTINUITY_RECORD_V1,
    CONTINUITY_PRESERVED,
    attach_conversation_chain_continuity,
    reconstruct_conversation_chain_continuity_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.prompt_to_conversation_integration import (
    reconstruct_prompt_to_conversation_replay,
    submit_prompt_to_conversation,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-02T13:00:00+00:00"
CURRENT_CHAIN_ID = "CHAIN-20260602-CONVERSATION-000001"


def _conversation_capture() -> dict:
    return {
        "prompt_id": "PROMPT-CHAIN-000001",
        "prompt_status": "HUMAN_PROMPT_ACCEPTED",
        "response_status": "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED",
        "response_text": "AiGOL preserves governed replay-visible operation.",
        "conversation_replay_reference": "PROMPT-CHAIN-000001/conversation_response",
        "replay_reference": "PROMPT-CHAIN-000001",
        "fail_closed": False,
        "worker_invoked": False,
        "execution_requested": False,
    }


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_attach_conversation_chain_continuity_persists_replay_visible_record(tmp_path) -> None:
    capture = attach_conversation_chain_continuity(
        prompt_id="PROMPT-CHAIN-000001",
        conversation_capture=_conversation_capture(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain_continuity",
        session_id="SESSION-CHAIN-000001",
        current_chain_id=CURRENT_CHAIN_ID,
    )
    reconstructed = reconstruct_conversation_chain_continuity_replay(tmp_path / "chain_continuity")
    record = capture["conversation_chain_continuity_record"]

    assert record["artifact_type"] == CONVERSATION_CHAIN_CONTINUITY_RECORD_V1
    assert record["continuity_status"] == CONTINUITY_PRESERVED
    assert capture["canonical_chain_id"] == CURRENT_CHAIN_ID
    assert reconstructed["canonical_chain_id"] == CURRENT_CHAIN_ID
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False
    assert f"show-chain {CURRENT_CHAIN_ID}" in reconstructed["suggested_inspection_commands"]


def test_prompt_to_conversation_exposes_canonical_chain_and_suggestions(tmp_path) -> None:
    result = submit_prompt_to_conversation(
        human_prompt="What is AiGOL?",
        prompt_id="PROMPT-CHAIN-000002",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "prompt_runtime",
        session_id="SESSION-CHAIN-000002",
        current_chain_id=CURRENT_CHAIN_ID,
    )
    reconstructed = reconstruct_prompt_to_conversation_replay(
        tmp_path / "prompt_runtime",
        prompt_id="PROMPT-CHAIN-000002",
    )

    assert result["canonical_chain_id"] == CURRENT_CHAIN_ID
    assert result["current_chain_id"] == CURRENT_CHAIN_ID
    assert result["latest_chain_id"] == CURRENT_CHAIN_ID
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    assert "show-full-lineage " + CURRENT_CHAIN_ID in result["suggested_inspection_commands"]
    assert reconstructed["canonical_chain_id"] == CURRENT_CHAIN_ID


def test_interactive_conversation_preserves_current_chain_across_turns(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-CHAIN-INTERACTIVE-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["What is AiGOL?", "What is replay?", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 2
    assert result["current_chain_id"]
    assert result["latest_chain_id"] == result["current_chain_id"]
    assert result["turns"][0]["canonical_chain_id"] == result["current_chain_id"]
    assert result["turns"][1]["canonical_chain_id"] == result["current_chain_id"]
    assert result["turns"][1]["suggested_inspection_commands"][0].startswith("show-chain ")
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False


def test_related_chain_reference_is_preserved_without_execution(tmp_path) -> None:
    related_chain_id = "CHAIN-RELATED-000001"
    capture = attach_conversation_chain_continuity(
        prompt_id="PROMPT-CHAIN-000003",
        conversation_capture=_conversation_capture(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "related_chain_continuity",
        current_chain_id=CURRENT_CHAIN_ID,
        related_chain_id=related_chain_id,
    )

    assert capture["related_chain_id"] == related_chain_id
    assert capture["execution_requested"] is False
    assert capture["worker_invoked"] is False


def test_reconstruction_detects_corrupt_continuity_replay(tmp_path) -> None:
    attach_conversation_chain_continuity(
        prompt_id="PROMPT-CHAIN-000004",
        conversation_capture=_conversation_capture(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_chain_continuity",
        current_chain_id=CURRENT_CHAIN_ID,
    )
    path = tmp_path / "corrupt_chain_continuity" / "000_conversation_chain_continuity_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-CORRUPT"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_chain_continuity_replay(tmp_path / "corrupt_chain_continuity")


def test_authority_bearing_conversation_capture_fails_closed(tmp_path) -> None:
    capture = _conversation_capture()
    capture["execution_requested"] = True

    with pytest.raises(FailClosedRuntimeError, match="execution request detected"):
        attach_conversation_chain_continuity(
            prompt_id="PROMPT-CHAIN-000005",
            conversation_capture=capture,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "authority_chain_continuity",
            current_chain_id=CURRENT_CHAIN_ID,
        )


def test_conversation_chain_continuity_has_no_execution_authority_imports() -> None:
    import aigol.runtime.conversation_chain_continuity_runtime as runtime

    source = inspect.getsource(runtime)
    cli_source = inspect.getsource(aigol_cli)

    assert "create_execution_request(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "dispatch_worker(" not in cli_source
    assert "invoke_worker(" not in cli_source
