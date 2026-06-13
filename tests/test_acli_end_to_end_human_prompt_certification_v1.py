"""Acceptance tests for AIGOL_ACLI_END_TO_END_HUMAN_PROMPT_CERTIFICATION_V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.providers.openai_provider import OpenAIProviderAdapter, openai_provider_metadata
from aigol.runtime.conversation_ppp_routing_integration import CONVERSATION_PPP_HANDOFF_CREATED
from aigol.runtime.execution_authorization_runtime import EXECUTION_AUTHORIZED
from aigol.runtime.external_worker_adapter_runtime import EXTERNAL_WORKER_TASK_PACKAGE_CREATED
from aigol.runtime.governed_implementation_dry_run import EXECUTION_READY
from aigol.runtime.implementation_handoff_visibility import IMPLEMENTATION_HANDOFF_SUMMARY_CREATED
from aigol.runtime.ocs_to_ppp_continuation_adapter_runtime import OCS_TO_PPP_CONTINUATION_REACHED_PPP
from aigol.runtime.openai_external_worker_provider_adapter import OPENAI_EXTERNAL_WORKER_COMPLETED
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_COMPLETED
from aigol.runtime.result_validation_runtime import RESULT_VALIDATION_COMPLETED
from aigol.runtime.universal_intake_layer_runtime import NATIVE_DEVELOPMENT_INTAKE, OCS_COGNITION_INTAKE
from aigol.runtime.worker_assignment_runtime import WORKER_ASSIGNED
from aigol.runtime.worker_dispatch_runtime import WORKER_DISPATCHED
from aigol.runtime.worker_invocation_request_runtime import WORKER_INVOCATION_REQUEST_CREATED
from aigol.runtime.worker_invocation_runtime import WORKER_INVOKED
from aigol.runtime.worker_invocation_to_execution_candidate_bridge_runtime import WORKER_EXECUTION_CANDIDATE_CREATED


CREATED_AT = "2026-06-13T00:00:00Z"
DEVELOPMENT_PROMPT = (
    "Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1. Goal: Extend the certified "
    "provider-neutral external worker architecture with Claude support while reusing existing governance, "
    "replay, validation, mutation, and worker lifecycle infrastructure."
)
OCS_EXECUTION_PROMPT = (
    "What should Sapianta do with the replay-derived AIGOL CLAUDE_EXTERNAL "
    "worker improvement to enter governed execution next?"
)
OCS_HIGH_RISK_PROMPT = (
    "What should Sapianta do with the replay-derived TRADING MARKET_EVIDENCE_NORMALIZATION "
    "worker improvement to enter governed execution next?"
)


@dataclass
class FakeProviderAdapter:
    response: dict[str, Any]
    provider_id: str = "openai"
    provider_version: str = openai_provider_metadata().provider_version
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


def _args(tmp_path, *, session_id: str, auto_continue: bool = True):
    parser = build_parser()
    raw = [
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
    if auto_continue:
        raw.append("--auto-continue")
    return parser.parse_args(raw)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _valid_provider_response() -> dict[str, Any]:
    return {
        "proposal_summary": "Create the governed worker/provider foundation.",
        "proposed_outputs": [
            "governance/WORKER_PROVIDER_FOUNDATION_V1.md",
            "governance/WORKER_PROVIDER_FOUNDATION_CERTIFICATION.json",
        ],
        "constraints_acknowledged": [
            "NO_DISPATCH",
            "NO_INVOCATION",
            "NO_EXECUTION",
            "PROPOSAL_ONLY",
        ],
        "assumptions": ["The worker lifecycle remains governed by existing runtimes."],
        "known_gaps": ["Provider execution remains behind authorization."],
    }


def _install_fake_proposal_adapter(monkeypatch) -> FakeProviderAdapter:
    adapter = FakeProviderAdapter(_valid_provider_response())
    monkeypatch.setattr(aigol_cli, "_post_context_continuation_provider_adapter", lambda: adapter)
    return adapter


def _install_fake_ocs_provider(monkeypatch) -> None:
    def fake_client(payload: dict, *, api_key: str, endpoint: str, timeout_seconds: int) -> dict:
        return {
            "id": "resp-acli-end-to-end-certification-ocs-001",
            "object": "response",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "findings": ["Governed execution may be required."],
                                    "assumptions": ["Replay-derived evidence remains non-authoritative."],
                                    "alternatives": ["Proposal only", "PPP continuation"],
                                    "risks": ["Execution remains gated."],
                                    "uncertainties": ["Operator approval can still halt continuation."],
                                    "confidence": "MEDIUM",
                                },
                                sort_keys=True,
                            ),
                            "annotations": [],
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(
        aigol_cli,
        "_conversation_openai_provider_adapter",
        lambda: OpenAIProviderAdapter(api_key="test-openai-key", client=fake_client),
    )


def _install_fake_external_worker_openai_client(monkeypatch) -> None:
    def fake_external_worker_client(request_metadata: dict[str, Any]) -> dict[str, Any]:
        assert request_metadata["provider_identity"] == "OPENAI"
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        return {
            "id": "resp-acli-end-to-end-external-worker-001",
            "output_text": "Inspect runtime metadata and return bounded findings.",
        }

    monkeypatch.setattr(aigol_cli, "_external_worker_openai_client", lambda: fake_external_worker_client)


def _wrapped_artifact(replay_reference: str, filename: str) -> dict[str, Any]:
    with (Path(replay_reference) / filename).open(encoding="utf-8") as handle:
        wrapper = json.load(handle)
    artifact = wrapper["artifact"]
    assert isinstance(artifact, dict)
    return artifact


def _assert_replay_references_exist(turn: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        replay_reference = turn[key]
        assert isinstance(replay_reference, str), key
        assert Path(replay_reference).exists(), key


def _assert_full_worker_backbone_reached(turn: dict[str, Any]) -> None:
    assert turn["ppp_route_status"] == CONVERSATION_PPP_HANDOFF_CREATED
    assert turn["execution_authorization_status"] == EXECUTION_AUTHORIZED
    assert turn["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert turn["worker_assignment_status"] == WORKER_ASSIGNED
    assert turn["worker_dispatch_status"] == WORKER_DISPATCHED
    assert turn["worker_invocation_status"] == WORKER_INVOKED
    assert turn["worker_execution_candidate_status"] == WORKER_EXECUTION_CANDIDATE_CREATED
    assert turn["external_worker_task_status"] == EXTERNAL_WORKER_TASK_PACKAGE_CREATED
    assert turn["openai_external_worker_status"] == OPENAI_EXTERNAL_WORKER_COMPLETED
    assert turn["result_validation_status"] == RESULT_VALIDATION_COMPLETED
    assert turn["replay_certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert turn["worker_request_reached"] is True
    assert turn["worker_assignment_reached"] is True
    assert turn["worker_dispatch_reached"] is True
    assert turn["worker_invocation_reached"] is True
    assert turn["worker_execution_candidate_reached"] is True
    assert turn["external_task_package_reached"] is True
    assert turn["openai_provider_reached"] is True
    assert turn["result_validation_reached"] is True
    assert turn["replay_certification_reached"] is True
    assert turn["replay_lineage_preserved"] is True


def _assert_terminal_replay_certified(
    result: dict[str, Any],
    turn: dict[str, Any],
    *,
    allowed_stop_reasons: set[str] | None = None,
) -> None:
    if allowed_stop_reasons is None:
        allowed_stop_reasons = {"WORKFLOW_COMPLETE"}
    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert result["auto_continue_stop_reason"] in allowed_stop_reasons
    assert turn["workflow_status"]["current_lifecycle_stage"] == "REPLAY_CERTIFIED"
    assert "TERMINATED" in turn["workflow_status"]["remaining_stages"] or turn["workflow_status"][
        "remaining_stages"
    ] == []


def _assert_authorization_boundary_and_lineage(turn: dict[str, Any]) -> None:
    authorization_replay_reference = turn.get("execution_authorization_replay_reference")
    if not authorization_replay_reference:
        worker_request = _wrapped_artifact(
            turn["worker_invocation_request_replay_reference"],
            "002_invocation_request_artifact_recorded.json",
        )
        authorization_replay_reference = worker_request["replay_references"]["execution_authorization_replay_reference"]
    authorization = _wrapped_artifact(
        authorization_replay_reference,
        "002_authorization_artifact_recorded.json",
    )
    assert authorization["artifact_type"] == "EXECUTION_AUTHORIZATION_ARTIFACT_V1"
    assert authorization["authorization_status"] == EXECUTION_AUTHORIZED
    assert authorization["authorizing_actor"] == "AIGOL_GOVERNANCE"
    assert authorization["authorization_recursive"] is False
    assert authorization["authorization_transferable"] is False

    execution_candidate = _wrapped_artifact(
        turn["worker_execution_candidate_replay_reference"],
        "001_worker_invocation_execution_candidate_recorded.json",
    )
    assert execution_candidate["human_approval_required"] is True
    assert execution_candidate["human_approval_granted"] is True
    assert execution_candidate["worker_executed"] is False
    assert execution_candidate["provider_invoked"] is False
    assert execution_candidate["execution_requested"] is False

    external_task = _wrapped_artifact(
        turn["external_worker_task_replay_reference"],
        "000_external_worker_task_package_recorded.json",
    )
    assert external_task["worker_authorization"]["authorized"] is True
    assert external_task["execution_scope"]["implementation_result_creation_allowed"] is False

    replay_certification = _wrapped_artifact(
        turn["replay_certification_replay_reference"],
        "000_replay_certification_artifact_recorded.json",
    )
    assert replay_certification["certification_status"] == REPLAY_CERTIFICATION_COMPLETED
    assert replay_certification["replay_lineage_preserved"] is True


def _shared_replay_keys() -> list[str]:
    return [
        "universal_intake_replay_reference",
        "ppp_routing_replay_reference",
        "execution_authorization_replay_reference",
        "worker_invocation_request_replay_reference",
        "worker_assignment_replay_reference",
        "worker_dispatch_replay_reference",
        "worker_invocation_replay_reference",
        "worker_execution_candidate_replay_reference",
        "external_worker_task_replay_reference",
        "openai_external_worker_replay_reference",
        "result_validation_replay_reference",
        "replay_certification_replay_reference",
    ]


def test_development_human_prompt_reaches_replay_certified_and_stops(tmp_path, monkeypatch) -> None:
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-END-TO-END-DEV"),
        input_func=_input_sequence([DEVELOPMENT_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert turn["universal_intake_classification"] == NATIVE_DEVELOPMENT_INTAKE
    assert turn["implementation_handoff_visibility_status"] == IMPLEMENTATION_HANDOFF_SUMMARY_CREATED
    assert turn["execution_preparation_status"] == EXECUTION_READY
    _assert_full_worker_backbone_reached(turn)
    _assert_terminal_replay_certified(result, turn)
    assert turn["workflow_status"]["workflow_state"] == "COMPLETED"
    assert turn["workflow_status"]["workflow_complete"] is True
    _assert_replay_references_exist(
        turn,
        [
            "native_development_task_intake_replay_reference",
            "development_context_assembly_replay_reference",
            "post_context_continuation_replay_reference",
            *_shared_replay_keys(),
        ],
    )
    _assert_authorization_boundary_and_lineage(turn)
    assert proposal_adapter.calls == 1


def test_ocs_execution_required_human_prompt_reaches_replay_certified_and_stops(tmp_path, monkeypatch) -> None:
    _install_fake_ocs_provider(monkeypatch)
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-END-TO-END-OCS"),
        input_func=_input_sequence([OCS_EXECUTION_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert turn["universal_intake_classification"] == OCS_COGNITION_INTAKE
    assert turn["ocs_to_ppp_continuation_status"] == OCS_TO_PPP_CONTINUATION_REACHED_PPP
    assert turn["ppp_invoked"] is True
    _assert_full_worker_backbone_reached(turn)
    _assert_terminal_replay_certified(result, turn, allowed_stop_reasons={"WORKFLOW_COMPLETE", "WAITING_FOR_OPERATOR"})
    _assert_replay_references_exist(
        turn,
        [
            "ocs_to_ppp_continuation_replay_reference",
            *[
                key
                for key in _shared_replay_keys()
                if key
                not in {
                    "ppp_routing_replay_reference",
                    "execution_authorization_replay_reference",
                }
            ],
        ],
    )
    assert (Path(turn["ocs_to_ppp_continuation_replay_reference"]) / "conversation_ppp_routing").exists()
    _assert_authorization_boundary_and_lineage(turn)
    assert proposal_adapter.calls == 1


def test_high_risk_ocs_prompt_fails_closed_before_execution_authorization(tmp_path, monkeypatch) -> None:
    _install_fake_ocs_provider(monkeypatch)
    proposal_adapter = _install_fake_proposal_adapter(monkeypatch)
    _install_fake_external_worker_openai_client(monkeypatch)
    output: list[str] = []

    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-ACLI-END-TO-END-OCS-HIGH-RISK"),
        input_func=_input_sequence([OCS_HIGH_RISK_PROMPT, "exit"]),
        output_func=output.append,
    )

    turn = result["turns"][0]

    assert result["failed_turns"] == 1
    assert result["auto_continue_stop_reason"] == "FAILED_CLOSED"
    assert turn["workflow_status"]["workflow_state"] == "FAILED_CLOSED"
    assert turn["fail_closed"] is True
    assert "selected candidate requires clarification" in turn["failure_reason"]
    assert turn["ppp_route_status"] is None
    assert turn["execution_authorization_status"] is None
    assert turn["worker_request_reached"] is False
    assert turn["openai_provider_reached"] is False
    assert turn["replay_certification_reached"] is False
    assert proposal_adapter.calls == 0
