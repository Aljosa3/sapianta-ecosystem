"""Focused G30-05 operational canonical-artifact completion tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from aigol.cli.aicli import run_reference_uhi_submit_session
from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
    INGRESS_COMPLETED,
    INGRESS_FAILED_CLOSED,
    reconstruct_explicit_canonical_artifact_ingress,
)
from aigol.runtime.platform_capability_composition_coverage import (
    create_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_core_project_services import (
    OPERATIONAL_CLARIFICATION_REPLY,
    reconstruct_operational_turn_binding,
)
from aigol.runtime.project_context_semantic_capability_route import (
    ROUTE_COMPLETED,
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
SESSION_ID = "SESSION-G30-05"
REQUEST = "Analyze Platform Capability Composition Coverage.\nAudit only."
ARTIFACT_REPLY = "Supplying the requested existing canonical artifact."


def _canonical_reference(tmp_path: Path, *, tampered: bool = False) -> Path:
    artifact = create_platform_capability_composition_coverage_request(
        request_id="G30-05-COMPOSITION-COVERAGE-REQUEST",
        query="Assess reusable Platform capability coverage and residual gaps.",
        created_at=CREATED_AT,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": "composition_coverage_request_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    if tampered:
        wrapper["artifact"]["query"] = "tampered after immutable recording"
    reference = (
        tmp_path
        / "canonical-input"
        / "000_composition_coverage_request_recorded.json"
    )
    reference.parent.mkdir(parents=True)
    reference.write_text(
        json.dumps(wrapper, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return reference


def _open_clarification(tmp_path: Path, output: list[str] | None = None) -> dict:
    return run_reference_uhi_submit_session(
        session_id=SESSION_ID,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        stdin_reader=lambda: REQUEST,
        input_reader=None,
        output_writer=output.append if output is not None else (lambda _line: None),
    )


def _submit_artifact(
    tmp_path: Path,
    reference: Path,
    output: list[str] | None = None,
) -> dict:
    return run_reference_uhi_submit_session(
        session_id=SESSION_ID,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        stdin_reader=lambda: ARTIFACT_REPLY,
        input_reader=None,
        output_writer=output.append if output is not None else (lambda _line: None),
        artifact_references=[str(reference)],
    )


def test_artifact_submission_completes_existing_g29_clarification(
    tmp_path: Path,
) -> None:
    clarification_output: list[str] = []
    first = _open_clarification(tmp_path, clarification_output)
    envelope = first["platform_core_project_services_context"][
        "operational_clarification_envelope"
    ]

    completion_output: list[str] = []
    second = _submit_artifact(
        tmp_path,
        _canonical_reference(tmp_path),
        completion_output,
    )
    context = second["platform_core_project_services_context"]
    ingress = context["explicit_canonical_artifact_ingress"]
    route = context["semantic_capability_runtime_route"]
    result = context["governed_read_only_work_result"]
    turn = context["operational_turn_binding"]

    assert first["session_status"] == "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"
    assert envelope["semantic_slot"] == "input_artifact_family"
    assert "Clarification required before governed execution." in "\n".join(
        clarification_output
    )
    assert ingress["ingress_status"] == INGRESS_COMPLETED
    assert route["route_status"] == ROUTE_COMPLETED
    assert route["lifecycle_status"] == (
        "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_COMPLETED"
    )
    assert route["canonical_platform_presentation"]["presentation_status"] == (
        "PRESENTATION_READY"
    )
    assert "PRESENTATION_READY" in "\n".join(completion_output)
    assert turn["turn_kind"] == OPERATIONAL_CLARIFICATION_REPLY
    assert turn["originating_semantic_slot"] == "input_artifact_family"
    assert turn["continuation_semantic_slot"] == "input_artifact_family"
    assert context["development_intent_resolution"]["project_objective_restarted"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_completed_operational_chain_reconstructs_ingress_route_and_turn(
    tmp_path: Path,
) -> None:
    _open_clarification(tmp_path)
    completion = _submit_artifact(tmp_path, _canonical_reference(tmp_path))
    context = completion["platform_core_project_services_context"]
    route = context["semantic_capability_runtime_route"]
    turn = context["operational_turn_binding"]

    ingress = reconstruct_explicit_canonical_artifact_ingress(
        context["explicit_canonical_artifact_ingress_reference"]
    )
    reconstructed_route = reconstruct_project_context_semantic_capability_route(
        route["replay_reference"]
    )
    reconstructed_turn = reconstruct_operational_turn_binding(turn["turn_reference"])

    assert ingress["downstream_route_hash"] == route["artifact_hash"]
    assert reconstructed_route["artifact_hash"] == route["artifact_hash"]
    assert reconstructed_turn["artifact_hash"] == turn["artifact_hash"]
    assert reconstructed_turn["originating_clarification_envelope_hash"] == (
        context["clarification_continuity"]["active_clarification_envelope_hash"]
    )


def test_invalid_artifact_after_clarification_fails_closed(
    tmp_path: Path,
) -> None:
    _open_clarification(tmp_path)
    completion_output: list[str] = []
    completion = _submit_artifact(
        tmp_path,
        _canonical_reference(tmp_path, tampered=True),
        completion_output,
    )
    context = completion["platform_core_project_services_context"]
    ingress = context["explicit_canonical_artifact_ingress"]
    result = context["governed_read_only_work_result"]
    turn = context["operational_turn_binding"]

    assert ingress["ingress_status"] == INGRESS_FAILED_CLOSED
    assert "wrapper hash mismatch" in ingress["failure_reason"]
    assert context["semantic_capability_runtime_route"] is None
    assert result["binding_status"] == "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED"
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED" in "\n".join(completion_output)
    assert turn["originating_semantic_slot"] == "input_artifact_family"
    assert turn["continuation_semantic_slot"] == "input_artifact_family"
    assert reconstruct_explicit_canonical_artifact_ingress(
        context["explicit_canonical_artifact_ingress_reference"]
    )["ingress_status"] == INGRESS_FAILED_CLOSED
