"""Tests for AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_human_prompt_regression_suite_certification_runtime import (
    REQUIRED_COVERAGE,
    run_acli_lifecycle_regression_certification,
)
from aigol.runtime.conversation_native_development_context_integration import (
    CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED,
    reconstruct_conversation_native_development_context_integration_replay,
    run_conversation_native_development_context_integration,
)
from aigol.runtime.native_development_domain_resolution_bridge import (
    AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_VERSION,
    DOMAIN_RESOLVED,
    GOVERNED_DEVELOPMENT_DOMAIN,
)
from aigol.runtime.native_development_task_intake_runtime import run_native_development_task_intake


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_ROOT = ROOT / "governance"
CREATED_AT = "2026-06-12T00:00:00Z"
CLAUDE_MILESTONE = "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1"


def _claude_prompt() -> str:
    return (
        f"Implement {CLAUDE_MILESTONE}. Create the missing provider adapter proposal request only. "
        "No dispatch. No invocation. No execution."
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_claude_provider_adapter_prompt_resolves_governed_development_domain(tmp_path) -> None:
    capture = run_native_development_task_intake(
        intake_id="INTAKE-CLAUDE-PROVIDER-ADAPTER-000001",
        human_prompt_reference="PROMPT-CLAUDE-PROVIDER-ADAPTER-000001",
        human_prompt=_claude_prompt(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
        session_id="SESSION-CLAUDE-PROVIDER-ADAPTER-000001",
        turn_id="TURN-000001",
    )
    bridge = capture["native_development_task_intake_artifact"]["domain_resolution_bridge"]

    assert capture["fail_closed"] is False
    assert capture["requested_domain"] == GOVERNED_DEVELOPMENT_DOMAIN
    assert bridge["runtime_version"] == AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_VERSION
    assert bridge["resolution_status"] == DOMAIN_RESOLVED
    assert bridge["bridge_applied"] is True
    assert bridge["resolved_domain"] == GOVERNED_DEVELOPMENT_DOMAIN
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_claude_provider_adapter_prompt_assembles_context_without_requested_domain_failure(tmp_path) -> None:
    capture = run_conversation_native_development_context_integration(
        prompt_id="SESSION-CLAUDE-CONTEXT-000001:TURN-000001",
        human_prompt=_claude_prompt(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "turn",
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-CLAUDE-CONTEXT-000001",
        turn_id="TURN-000001",
    )
    reconstructed = reconstruct_conversation_native_development_context_integration_replay(tmp_path / "turn")

    assert capture["response_status"] == CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
    assert capture["fail_closed"] is False
    assert capture["failure_reason"] is None
    assert capture["development_context_assembly"]["requested_domain"] == GOVERNED_DEVELOPMENT_DOMAIN
    assert capture["context_status"] == "CONTEXT_ASSEMBLED"
    assert capture["missing_context"] == []
    assert capture["ambiguous_context"] == []
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["context_hash"] == capture["context_hash"]


def test_explicit_aigol_provider_adapter_prompt_no_longer_hits_unsupported_domain_context(tmp_path) -> None:
    capture = run_conversation_native_development_context_integration(
        prompt_id="SESSION-AIGOL-CONTEXT-000001:TURN-000001",
        human_prompt=(
            f"Implement {CLAUDE_MILESTONE} for AIGOL. Create the missing provider adapter proposal request only. "
            "No dispatch. No invocation. No execution."
        ),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "turn",
        governance_root=GOVERNANCE_ROOT,
        session_id="SESSION-AIGOL-CONTEXT-000001",
        turn_id="TURN-000001",
    )

    assert capture["response_status"] == CONVERSATION_NATIVE_DEVELOPMENT_CONTEXT_INTEGRATED
    assert capture["fail_closed"] is False
    assert capture["failure_reason"] is None
    assert capture["development_context_assembly"]["requested_domain"] == GOVERNED_DEVELOPMENT_DOMAIN
    assert capture["context_status"] == "CONTEXT_ASSEMBLED"
    assert "unsupported domain context" not in str(capture["failure_reason"])


def test_interactive_claude_provider_adapter_prompt_routes_to_context_assembly(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-CLAUDE-BRIDGE-CLI-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
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
    assert turn["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert turn["context_status"] == "CONTEXT_ASSEMBLED"
    assert turn["requested_domain"] == GOVERNED_DEVELOPMENT_DOMAIN
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert "requested_domain is required" not in "\n".join(output)


def test_existing_certified_domain_lifecycle_still_passes(tmp_path) -> None:
    result = run_acli_lifecycle_regression_certification(
        run_id="ACLI-LIFECYCLE-BRIDGE-REGRESSION-000001",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "regression_certification",
        workspace=tmp_path,
        domains=("FreshDomain", "PilotDomain"),
        auto_continue=True,
    )
    run_artifact = result["regression_run_artifact"]
    certification = result["regression_certification_artifact"]

    assert result["regression_suite_certified"] is True
    assert run_artifact["termination_rate"] == 1.0
    assert run_artifact["fail_closed_rate"] == 0.0
    assert run_artifact["replay_lineage_integrity"] is True
    assert all(run_artifact["coverage"][item] is True for item in REQUIRED_COVERAGE)
    assert certification["certification_status"] == "CERTIFIED"
