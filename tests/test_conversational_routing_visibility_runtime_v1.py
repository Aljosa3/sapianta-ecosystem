"""Tests for AIGOL_CONVERSATIONAL_ROUTING_VISIBILITY_RUNTIME_V1."""

from __future__ import annotations

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import (
    CREATE_DOMAIN_MARKETING,
    DEFAULT_PROVIDER_ASSISTED_CONVERSATION,
    OCS_LLM_COGNITION,
    OPERATOR_DECISION_SUPPORT,
    SHOW_LATEST_REPLAY_CHAIN,
)
from aigol.runtime.conversational_routing_visibility_runtime import (
    CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1,
    MEDIUM,
    ROUTING_SELECTED,
    reconstruct_conversational_routing_visibility_replay,
)


CREATED_AT = "2026-06-06T00:00:00Z"


def _args(tmp_path, *, session_id: str):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _routing_replay(tmp_path, session_id: str):
    return reconstruct_conversational_routing_visibility_replay(
        tmp_path / "interactive_runtime" / session_id / "TURN-000001" / "routing_visibility"
    )


def test_ocs_cognition_prompt_renders_and_reconstructs_competing_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-OCS-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(
            [
                "Should Sapianta primarily sell domains, license the platform, or offer managed services?",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)
    turn = result["turns"][0]

    assert turn["routing_visibility_artifact_type"] == CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1
    assert replay["workflow_id"] == OCS_LLM_COGNITION
    assert replay["routing_status"] == ROUTING_SELECTED
    assert replay["routing_confidence"] == MEDIUM
    assert replay["competing_signals"] == []
    assert replay["matched_signals"] == ["ocs", "llm", "cognition"]
    assert "OCS LLM cognition" in replay["routing_reason"]
    assert output[0].splitlines()[0:4] == [
        "================================",
        "ROUTING DECISION",
        "workflow: OCS_LLM_COGNITION",
        "confidence: MEDIUM",
    ]
    assert "[1/8] Routing" in output[0]


def test_sapianta_commercial_product_prompt_renders_ocs_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-SAPIANTA-OCS-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(
            [
                "I want to create the first real commercial Sapianta product.",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)
    turn = result["turns"][0]

    assert turn["routing_visibility_artifact_type"] == CONVERSATIONAL_ROUTING_VISIBILITY_ARTIFACT_V1
    assert turn["routing_visibility_workflow_id"] == OCS_LLM_COGNITION
    assert replay["workflow_id"] == OCS_LLM_COGNITION
    assert replay["routing_status"] == ROUTING_SELECTED
    assert replay["routing_confidence"] == MEDIUM
    assert replay["matched_signals"] == ["ocs", "llm", "cognition"]
    assert "workflow: OCS_LLM_COGNITION" in output[0]


def test_extended_sapianta_product_prompt_renders_ocs_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-SAPIANTA-OCS-EXTENDED-000001"
    output: list[str] = []
    prompt = "\n".join(
        [
            "I want to create the first real commercial Sapianta product.",
            "",
            "Use the current AiGOL architecture and repository state.",
            "Assume existing product domains remain read-only evidence.",
            "Do not create a new domain or mutate governance.",
            "Produce findings, risks, uncertainties, and the recommended next milestone.",
        ]
    )

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)
    turn = result["turns"][0]

    assert turn["routing_visibility_workflow_id"] == OCS_LLM_COGNITION
    assert turn["conversational_workflow_id"] == OCS_LLM_COGNITION
    assert replay["workflow_id"] == OCS_LLM_COGNITION
    assert replay["routing_status"] == ROUTING_SELECTED
    assert "workflow: OCS_LLM_COGNITION" in output[0]


def test_operator_decision_support_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-OPERATOR-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Which capability should we prioritize next?", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["failed_turns"] == 0
    assert replay["workflow_id"] == OPERATOR_DECISION_SUPPORT
    assert replay["routing_confidence"] == "HIGH"
    assert replay["matched_signals"] == ["operator", "decision", "support"]
    assert "non-authoritative recommendation" in replay["routing_reason"]
    assert "workflow: OPERATOR_DECISION_SUPPORT" in output[0]


def test_domain_creation_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-DOMAIN-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Create a marketing domain.", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert replay["workflow_id"] == CREATE_DOMAIN_MARKETING
    assert replay["routing_confidence"] == "HIGH"
    assert "create" in replay["matched_signals"]
    assert "domain" in replay["matched_signals"]
    assert "native-development domain workflow" in replay["routing_reason"]
    assert "workflow: CREATE_DOMAIN_MARKETING" in output[0]


def test_replay_review_prompt_renders_visibility(tmp_path) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-REPLAY-000001"
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Show latest replay chain.", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert replay["workflow_id"] == SHOW_LATEST_REPLAY_CHAIN
    assert replay["routing_confidence"] == "HIGH"
    assert "read-only chain inspection" in replay["routing_reason"]
    assert "latest" in replay["matched_signals"]
    assert "workflow: SHOW_LATEST_REPLAY_CHAIN" in output[0]


def test_default_fallback_prompt_renders_authoritative_visibility_before_failure(tmp_path, monkeypatch) -> None:
    session_id = "SESSION-ROUTING-VISIBILITY-FAILED-000001"
    output: list[str] = []

    def provider_unavailable(**kwargs):
        prompt_id = kwargs["prompt_id"]
        return {
            "prompt_id": prompt_id,
            "response_status": "FAILED_CLOSED",
            "response_source": "UNAVAILABLE",
            "response_text": "",
            "conversation_replay_reference": "provider/conversation_response",
            "prompt_to_conversation_capture_hash": "sha256:provider-failure",
            "provider_used": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "dispatch_requested": False,
            "fail_closed": True,
            "failure_reason": "provider-assisted conversation failed closed: OpenAI provider unavailable",
            "canonical_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
            "current_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
            "latest_chain_id": "CHAIN-ROUTING-VISIBILITY-FAILED",
        }

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", provider_unavailable)

    result = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["nonsense followup", "exit"]),
        output_func=output.append,
    )

    replay = _routing_replay(tmp_path, session_id)

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 1
    assert replay["workflow_id"] == DEFAULT_PROVIDER_ASSISTED_CONVERSATION
    assert replay["routing_status"] == ROUTING_SELECTED
    assert replay["routing_confidence"] == "LOW"
    assert replay["matched_signals"] == ["provider", "conversation", "fallback"]
    assert replay["competing_signals"] == []
    assert "provider-assisted conversation" in replay["routing_reason"]
    assert output[0].splitlines()[0:3] == [
        "================================",
        "ROUTING DECISION",
        "workflow: DEFAULT_PROVIDER_ASSISTED_CONVERSATION",
    ]
    assert output[0].splitlines()[3:4] == [
        "confidence: LOW",
    ]
    assert output[-2].startswith("FAILED_CLOSED:")
    assert output[-1].startswith("Workflow Name:")
