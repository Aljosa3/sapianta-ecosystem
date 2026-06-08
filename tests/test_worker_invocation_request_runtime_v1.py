"""Tests for AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import (
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.execution_authorization_runtime import authorize_execution_ready
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_execution_readiness_runtime import evaluate_ocs_execution_readiness
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import run_ocs_llm_cognition_end_to_end
from aigol.runtime.ocs_to_execution_handoff_runtime import create_ocs_execution_handoff
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_INVOCATION_REQUEST_ARTIFACT_V1,
    WORKER_INVOCATION_REQUEST_CREATED,
    create_worker_invocation_request,
    reconstruct_worker_invocation_request_replay,
)

import pytest


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-WORKER-INVOCATION-REQUEST-000001"


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
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _ppp_capture(tmp_path, *, prompt: str, suffix: str):
    session_id = f"{SESSION_ID}-{suffix}"
    allocation = resume_conversation_session(
        session_id=session_id,
        runtime_root=tmp_path / f"routing_runtime_{suffix}",
        created_at=CREATED_AT,
    )
    prompt_id = f"{session_id}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"routing_{suffix}",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ppp_{suffix}",
    )


def _execution_ready(tmp_path, *, prompt: str, suffix: str):
    ppp = _ppp_capture(tmp_path, prompt=prompt, suffix=suffix)
    upstream = ppp["conversation_to_ppp_handoff_execution_artifact"]
    handoff_replay_reference = ppp.get("handoff_replay_reference")
    approval_status = ppp["approval_status"]
    if ppp["terminal_status"] == HUMAN_APPROVAL_REQUIRED:
        request = upstream["approval_resume_packet"]["approval_request_artifact"]
        approval = create_human_implementation_approval(
            approval_id=f"HUMAN-APPROVAL-{suffix}",
            approval_request_artifact=request,
            approving_actor="human.operator",
            approval_timestamp=CREATED_AT,
        )
        resumed = resume_implementation_after_approval(
            resume_id=f"APPROVAL-RESUME-{suffix}",
            approval_required_replay_reference=ppp["conversation_to_ppp_handoff_execution_replay_reference"],
            human_approval_artifact=approval,
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"approval_resume_{suffix}",
        )
        upstream = resumed["implementation_approval_resume_artifact"]
        handoff_replay_reference = resumed["implementation_handoff_replay_reference"]
        approval_status = "APPROVED"
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id=f"VISIBILITY-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=approval_status,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"visibility_{suffix}",
    )
    return prepare_governed_implementation_dry_run(
        dry_run_id=f"DRY-RUN-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=upstream,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"dry_run_{suffix}",
    )


def _authorization(tmp_path, *, prompt: str, suffix: str, expires_at: str = "NEVER") -> dict:
    ready = _execution_ready(tmp_path, prompt=prompt, suffix=suffix)
    return authorize_execution_ready(
        authorization_id=f"AUTHORIZATION-{suffix}",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        authorization_expires_at=expires_at,
        replay_dir=tmp_path / f"authorization_{suffix}",
    )


def _invocation_request(tmp_path, *, prompt: str, suffix: str, expires_at: str = "NEVER") -> dict:
    authorization = _authorization(tmp_path, prompt=prompt, suffix=suffix, expires_at=expires_at)
    return create_worker_invocation_request(
        invocation_request_id=f"WORKER-INVOCATION-REQUEST-{suffix}",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / f"invocation_request_{suffix}",
    )


def _ocs_source_context() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-WORKER-REQUEST-OCS-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks OCS to create a bounded execution intake candidate.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return {"conversation_context": [artifact]}


def _ocs_authorization(tmp_path: Path, *, suffix: str) -> dict:
    response = json.dumps(
        {
            "findings": ["OCS found a bounded execution candidate for human review."],
            "assumptions": ["Execution remains downstream of human approval and authorization."],
            "risks": ["Worker selection must remain bounded."],
            "uncertainties": ["Exact worker implementation scope requires review."],
            "clarification_questions": ["Should this become a worker request candidate?"],
            "recommended_next_milestone": "Create OCS execution handoff artifact.",
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )

    def transport(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {
            "model": "gpt-5.1",
            "output_text": response,
            "usage": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        }

    ocs = run_ocs_llm_cognition_end_to_end(
        end_to_end_id=f"OCS-WORKER-REQUEST-E2E-{suffix}",
        human_question="Turn this OCS cognition into a bounded execution candidate.",
        source_context=_ocs_source_context(),
        provider_contracts=[create_default_cognition_provider_contract(provider_id="openai", created_at=CREATED_AT)],
        transport_registry={"openai": transport},
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ocs_e2e_{suffix}",
        source_chain_id=f"CHAIN-OCS-WORKER-REQUEST-{suffix}",
        source_request_reference="HUMAN-REQUEST-WORKER-REQUEST-OCS-001",
        single_provider_primary_mode=True,
    )
    handoff = create_ocs_execution_handoff(
        handoff_id=f"OCS-HANDOFF-WORKER-REQUEST-{suffix}",
        ocs_cognition_replay_reference=ocs["replay_reference"],
        execution_intake_id=f"OCS-EXECUTION-INTAKE-WORKER-REQUEST-{suffix}",
        execution_intent_summary="Prepare a bounded worker request candidate.",
        execution_candidate_scope={
            "mode": "EXECUTION_INTAKE_ONLY",
            "domain": "product_build",
            "execution_authorized": False,
        },
        requested_outcomes=["worker invocation request candidate"],
        non_goals=["approval creation", "worker assignment", "worker dispatch", "worker invocation"],
        allowed_outputs=["worker invocation request proposal"],
        forbidden_operations=["AUTHORIZE_EXECUTION", "INVOKE_WORKER", "DISPATCH_WORKER", "RETRY", "REPAIR"],
        worker_role_requirements=["bounded implementation worker"],
        target_worker_family="IMPLEMENTATION",
        candidate_worker_constraints={"single_worker_only": True, "human_review_required": True},
        worker_capability_requirements=["bounded file generation after downstream authorization"],
        worker_exclusion_rules=["no provider-as-worker", "no unregistered worker"],
        worker_registry_requirements=["registered worker identity required"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ocs_handoff_{suffix}",
        source_chain_id=f"CHAIN-OCS-WORKER-REQUEST-{suffix}",
    )
    readiness = evaluate_ocs_execution_readiness(
        readiness_id=f"OCS-READINESS-WORKER-REQUEST-{suffix}",
        ocs_handoff_replay_reference=handoff["ocs_execution_handoff_replay_reference"],
        approval_status="APPROVED",
        approval_reference=f"HUMAN-APPROVAL-OCS-WORKER-REQUEST-{suffix}",
        approval_hash=f"sha256:approvalhash{suffix:0>52}"[:71],
        approving_actor="human_operator",
        approved_at=CREATED_AT,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ocs_readiness_{suffix}",
    )
    return authorize_execution_ready(
        authorization_id=f"AUTHORIZATION-OCS-WORKER-REQUEST-{suffix}",
        execution_ready_replay_reference=readiness["ocs_execution_readiness_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / f"ocs_authorization_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_execution_authorized_becomes_worker_invocation_request_created(
    tmp_path,
    prompt: str,
    suffix: str,
) -> None:
    capture = _invocation_request(tmp_path, prompt=prompt, suffix=suffix)
    request = capture["worker_invocation_request_artifact"]
    reconstructed = reconstruct_worker_invocation_request_replay(tmp_path / f"invocation_request_{suffix}")

    assert capture["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert request["artifact_type"] == WORKER_INVOCATION_REQUEST_ARTIFACT_V1
    assert request["authorization_reference"] == f"AUTHORIZATION-{suffix}"
    assert request["execution_packet_reference"].endswith(":PACKET")
    assert request["worker_role"]
    assert request["target_worker_family"]
    assert request["allowed_outputs"]
    assert "INVOKE_WORKER" in request["forbidden_operations"]
    assert "CHAIN_CONTINUITY" in request["validation_requirements"]
    assert request["request_hash"].startswith("sha256:")
    assert request["worker_assigned"] is False
    assert request["worker_dispatched"] is False
    assert request["worker_invoked"] is False
    assert request["execution_started"] is False
    assert reconstructed["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert reconstructed["request_hash"] == request["request_hash"]


def test_worker_invocation_request_persists_replay_evidence(tmp_path) -> None:
    _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="replay-events")

    replay_dir = tmp_path / "invocation_request_replay-events"
    assert (replay_dir / "000_invocation_request_evidence_recorded.json").exists()
    assert (replay_dir / "001_invocation_request_classification_recorded.json").exists()
    assert (replay_dir / "002_invocation_request_artifact_recorded.json").exists()
    assert (replay_dir / "003_invocation_request_result_recorded.json").exists()


def test_ocs_readiness_authorization_becomes_worker_invocation_request_created(tmp_path) -> None:
    authorization = _ocs_authorization(tmp_path, suffix="compat")
    capture = create_worker_invocation_request(
        invocation_request_id="WORKER-INVOCATION-REQUEST-OCS-COMPAT",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_request_ocs_compat",
    )
    request = capture["worker_invocation_request_artifact"]
    reconstructed = reconstruct_worker_invocation_request_replay(tmp_path / "invocation_request_ocs_compat")

    assert capture["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert request["authorization_reference"] == "AUTHORIZATION-OCS-WORKER-REQUEST-compat"
    assert request["execution_packet_reference"].endswith(":PACKET")
    assert request["worker_role"] == "bounded implementation worker"
    assert request["target_worker_family"] == "IMPLEMENTATION"
    assert request["worker_assigned"] is False
    assert request["worker_dispatched"] is False
    assert request["worker_invoked"] is False
    assert request["execution_started"] is False
    assert reconstructed["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert reconstructed["request_hash"] == request["request_hash"]


def test_worker_invocation_request_fails_closed_when_authorization_missing(tmp_path) -> None:
    capture = create_worker_invocation_request(
        invocation_request_id="WORKER-INVOCATION-REQUEST-MISSING",
        execution_authorization_replay_reference=str(tmp_path / "missing_authorization"),
        requested_by="AIGOL_GOVERNANCE",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_request_missing",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "missing" in capture["failure_reason"]


def test_worker_invocation_request_fails_closed_when_authorization_expired(tmp_path) -> None:
    capture = _invocation_request(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="expired",
        expires_at="2026-06-03T23:59:59+00:00",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "authorization expired" in capture["failure_reason"]


def test_worker_invocation_request_fails_closed_on_authority_violation(tmp_path) -> None:
    authorization = _authorization(tmp_path, prompt="Create a filesystem worker.", suffix="authority")
    path = tmp_path / "authorization_authority" / "002_authorization_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_assigned"] = True
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result_path = tmp_path / "authorization_authority" / "003_authorization_result_recorded.json"
    result_wrapper = json.loads(result_path.read_text(encoding="utf-8"))
    result_wrapper["artifact"]["execution_authorization_hash"] = wrapper["artifact"]["artifact_hash"]
    result_wrapper["artifact"].pop("artifact_hash")
    result_wrapper["artifact"]["artifact_hash"] = replay_hash(result_wrapper["artifact"])
    result_wrapper.pop("replay_hash")
    result_wrapper["replay_hash"] = replay_hash(result_wrapper)
    result_path.write_text(canonical_serialize(result_wrapper) + "\n", encoding="utf-8")

    capture = create_worker_invocation_request(
        invocation_request_id="WORKER-INVOCATION-REQUEST-AUTHORITY",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="AIGOL_GOVERNANCE",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "invocation_request_authority",
    )

    assert capture["request_status"] == "FAILED_CLOSED"
    assert "authority" in capture["failure_reason"] or "lineage continuity" in capture["failure_reason"]


def test_worker_invocation_request_reconstruction_detects_replay_corruption(tmp_path) -> None:
    _invocation_request(tmp_path, prompt="Create a filesystem worker.", suffix="corrupt")
    path = tmp_path / "invocation_request_corrupt" / "002_invocation_request_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_invocation_request_replay(tmp_path / "invocation_request_corrupt")


def test_cli_acceptance_flows_reach_worker_invocation_request_created(tmp_path) -> None:
    filesystem_output: list[str] = []
    filesystem = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-INVOCATION-REQUEST-CLI-FILESYSTEM"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=filesystem_output.append,
    )
    trading_output: list[str] = []
    trading = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-INVOCATION-REQUEST-CLI-TRADING"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=trading_output.append,
    )

    assert filesystem["turns"][0]["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert "Request Status: WORKER_INVOCATION_REQUEST_CREATED" in filesystem_output[0]
    assert "No Worker has been assigned, dispatched, invoked, or executed." in filesystem_output[0]
    assert trading["turns"][1]["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert "Request Status: WORKER_INVOCATION_REQUEST_CREATED" in trading_output[1]


def test_worker_invocation_request_runtime_preserves_authority_boundaries() -> None:
    import aigol.runtime.worker_invocation_request_runtime as runtime

    source = inspect.getsource(runtime)

    assert "assign_worker(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_result(" not in source
    assert "create_human_implementation_approval(" not in source
    assert "mutate_governance(" not in source
    assert "subprocess" not in source
    assert "requests" not in source
