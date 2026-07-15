"""Focused G30-06 in-session opaque artifact attachment tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli.aicli import run_reference_uhi_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    create_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_core_project_services import (
    G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER,
    reconstruct_operational_turn_binding,
    validate_operational_clarification_envelope,
    validate_operational_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
REQUEST_LINES = [
    "Analyze Platform Capability Composition Coverage.",
    "Audit only.",
]


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def _reference(
    tmp_path: Path,
    *,
    name: str = "valid",
    tampered: bool = False,
    unsupported: bool = False,
) -> Path:
    if unsupported:
        artifact = {
            "artifact_type": "UNSUPPORTED_G30_06_ARTIFACT_V1",
            "replay_visible": True,
        }
        artifact["artifact_hash"] = replay_hash(artifact)
    else:
        artifact = create_platform_capability_composition_coverage_request(
            request_id=f"G30-06-{name.upper()}",
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
        wrapper["artifact"]["request_id"] = "TAMPERED-AFTER-RECORDING"
    path = tmp_path / "canonical-input" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(wrapper, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _run(
    tmp_path: Path,
    commands: list[str],
    *,
    session_id: str = "SESSION-G30-06",
) -> tuple[dict, list[str]]:
    output: list[str] = []
    result = run_reference_uhi_session(
        session_id=session_id,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        input_reader=_reader(commands),
        output_writer=output.append,
    )
    return result, output


def _successful_session(tmp_path: Path) -> tuple[dict, list[str]]:
    reference = _reference(tmp_path)
    return _run(
        tmp_path,
        [*REQUEST_LINES, "/send", f"/attach {reference}", "/exit"],
    )


def test_in_session_attachment_completes_certified_runtime_without_hi_authority(
    tmp_path: Path,
) -> None:
    result, output = _successful_session(tmp_path)
    context = result["platform_core_project_services_context"]
    turn = context["operational_turn_binding"]
    route = context["semantic_capability_runtime_route"]
    rendered = "\n".join(output)

    assert "Clarification required before governed execution." in rendered
    assert "Opaque artifact reference attached" in rendered
    assert "presentation_status: PRESENTATION_READY" in rendered
    assert turn["in_session_opaque_artifact_attachment"] is True
    assert turn["originating_semantic_slot"] == "input_artifact_family"
    assert turn["continuation_semantic_slot"] == "input_artifact_family"
    assert turn["explicit_canonical_artifact_ingress_status"] == (
        "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_COMPLETED"
    )
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert route["lifecycle_status"] == (
        "SEMANTIC_CAPABILITY_INVOCATION_LIFECYCLE_COMPLETED"
    )
    assert context["development_intent_resolution"]["project_objective_restarted"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["repository_mutated"] is False


def test_replay_reconstructs_attachment_ingress_continuation_and_presentation(
    tmp_path: Path,
) -> None:
    result, _output = _successful_session(tmp_path)
    context = result["platform_core_project_services_context"]
    turn = context["operational_turn_binding"]
    reconstructed = reconstruct_operational_turn_binding(turn["turn_reference"])

    assert reconstructed["artifact_hash"] == turn["artifact_hash"]
    assert reconstructed["explicit_canonical_artifact_ingress_hash"] == (
        context["explicit_canonical_artifact_ingress"]["artifact_hash"]
    )
    assert reconstructed["continuation_route_hash"] == (
        context["semantic_capability_runtime_route"]["artifact_hash"]
    )


def test_attachment_requires_active_non_cancelled_clarification(tmp_path: Path) -> None:
    reference = _reference(tmp_path)
    without, without_output = _run(
        tmp_path / "without",
        [f"/attach {reference}", "/exit"],
        session_id="G30-06-WITHOUT",
    )
    cancelled, cancelled_output = _run(
        tmp_path / "cancelled",
        [*REQUEST_LINES, "/send", "/cancel", f"/attach {reference}", "/exit"],
        session_id="G30-06-CANCELLED",
    )

    assert "No active Platform Core clarification" in "\n".join(without_output)
    assert without["submitted_message_count"] == 0
    assert "No active Platform Core clarification" in "\n".join(cancelled_output)
    assert cancelled["canceled_compose_count"] == 0


def test_generic_clarification_does_not_accept_artifact_attachment(
    tmp_path: Path,
) -> None:
    reference = _reference(tmp_path)
    result, output = _run(
        tmp_path,
        ["I have an idea.", "/send", f"/attach {reference}", "/exit"],
        session_id="G30-06-GENERIC",
    )

    assert "does not accept an artifact attachment" in "\n".join(output)
    assert result["submitted_message_count"] == 1
    assert result["platform_core_project_services_context"][
        "operational_clarification_envelope"
    ] is None


def test_completed_clarification_rejects_duplicate_attachment(tmp_path: Path) -> None:
    reference = _reference(tmp_path)
    result, output = _run(
        tmp_path,
        [
            *REQUEST_LINES,
            "/send",
            f"/attach {reference}",
            f"/attach {reference}",
            "/exit",
        ],
        session_id="G30-06-DUPLICATE",
    )

    assert "\n".join(output).count("Opaque artifact reference attached") == 1
    assert "No active Platform Core clarification" in "\n".join(output)
    assert result["submitted_message_count"] == 2


@pytest.mark.parametrize(
    ("reference_kind", "failure_text"),
    [
        ("missing", "reference missing"),
        ("tampered", "wrapper hash mismatch"),
        ("unsupported", "unsupported artifact type"),
    ],
)
def test_invalid_or_unsupported_attachment_fails_closed(
    tmp_path: Path,
    reference_kind: str,
    failure_text: str,
) -> None:
    if reference_kind == "missing":
        reference = tmp_path / "canonical-input" / "missing.json"
    else:
        reference = _reference(
            tmp_path,
            name=reference_kind,
            tampered=reference_kind == "tampered",
            unsupported=reference_kind == "unsupported",
        )
    result, output = _run(
        tmp_path,
        [*REQUEST_LINES, "/send", f"/attach {reference}", "/exit"],
        session_id=f"G30-06-{reference_kind.upper()}",
    )
    context = result["platform_core_project_services_context"]
    ingress = context["explicit_canonical_artifact_ingress"]
    work = context["governed_read_only_work_result"]

    assert ingress["ingress_status"] == (
        "EXPLICIT_CANONICAL_ARTIFACT_INGRESS_FAILED_CLOSED"
    )
    assert failure_text in ingress["failure_reason"]
    assert work["binding_status"] == "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED"
    assert work["provider_invoked"] is False
    assert work["worker_invoked"] is False
    assert work["repository_mutated"] is False
    assert "GOVERNED_READ_ONLY_WORK_FAILED_CLOSED" in "\n".join(output)


def test_clarification_rejects_wrong_session_and_owner_substitution(
    tmp_path: Path,
) -> None:
    result, _output = _run(
        tmp_path,
        [*REQUEST_LINES, "/send", "/exit"],
        session_id="G30-06-ENVELOPE",
    )
    envelope = result["platform_core_project_services_context"][
        "operational_clarification_envelope"
    ]

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        validate_operational_clarification_envelope(
            envelope,
            expected_session_id="WRONG-SESSION",
        )

    owner = deepcopy(envelope)
    owner["clarification_owner"] = "SUBSTITUTED_OWNER"
    owner["artifact_hash"] = replay_hash(
        {key: value for key, value in owner.items() if key != "artifact_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="owner substitution"):
        validate_operational_clarification_envelope(owner)

    assert envelope["clarification_owner"] == (
        G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    )


def test_replay_rejects_attachment_substitution_and_route_tampering(
    tmp_path: Path,
) -> None:
    result, _output = _successful_session(tmp_path)
    context = result["platform_core_project_services_context"]
    turn = context["operational_turn_binding"]
    turn_path = Path(turn["turn_reference"])

    stale = deepcopy(turn)
    stale["originating_clarification_envelope_hash"] = replay_hash(
        "stale-clarification"
    )
    stale["artifact_hash"] = replay_hash(
        {key: value for key, value in stale.items() if key != "artifact_hash"}
    )
    turn_path.write_text(json.dumps(stale), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="stale clarification lineage"):
        reconstruct_operational_turn_binding(turn_path)

    substituted = deepcopy(turn)
    substituted["explicit_canonical_artifact_ingress_hash"] = replay_hash(
        "substituted-attachment"
    )
    substituted["artifact_hash"] = replay_hash(
        {key: value for key, value in substituted.items() if key != "artifact_hash"}
    )
    turn_path.write_text(json.dumps(substituted), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="attachment substitution"):
        reconstruct_operational_turn_binding(turn_path)

    turn_path.write_text(json.dumps(turn), encoding="utf-8")
    route_path = Path(turn["continuation_route_reference"]) / (
        "project_context_semantic_capability_route.json"
    )
    route = json.loads(route_path.read_text(encoding="utf-8"))
    route["failure_reason"] = "tampered"
    route_path.write_text(json.dumps(route), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="artifact hash mismatch"):
        reconstruct_operational_turn_binding(turn_path)


def test_attachment_turn_validator_rejects_non_clarification_binding(
    tmp_path: Path,
) -> None:
    result, _output = _successful_session(tmp_path)
    turn = deepcopy(result["platform_core_project_services_context"][
        "operational_turn_binding"
    ])
    turn["turn_kind"] = "OPERATIONAL_GOVERNED_WORK"
    turn["artifact_hash"] = replay_hash(
        {key: value for key, value in turn.items() if key != "artifact_hash"}
    )

    with pytest.raises(FailClosedRuntimeError):
        validate_operational_turn_binding(turn)
