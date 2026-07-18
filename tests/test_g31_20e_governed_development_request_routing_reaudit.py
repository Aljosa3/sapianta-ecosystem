from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
    validate_operational_clarification_envelope,
)
from aigol.runtime.platform_query_router import (
    GOVERNED_DEVELOPMENT_ROUTE,
    PLATFORM_KNOWLEDGE_ROUTE,
    route_platform_query,
    validate_platform_query_router_response,
)


CREATED_AT = "2026-07-18T00:00:00Z"
PRIOR_MARKER_REQUEST = (
    "Improve the human interface terminal summary behavior. Read KNOWN_INPUT.txt "
    "and include its exact marker in your short read-only final response. Do not "
    "modify files."
)
GROUNDED_DEVELOPMENT_REQUEST = (
    "Fix the failing addition test in calc.py and test_calc.py. Return a minimal "
    "unified diff only; do not edit files."
)


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def _must_not_start_process(*_args, **_kwargs):
    raise AssertionError("a non-execution route must not start a Worker process")


def _session(tmp_path, *, session_id: str, request: str) -> dict:
    return aicli.run_reference_uhi_session(
        session_id=session_id,
        created_at=CREATED_AT,
        runtime_root=tmp_path / session_id / "runtime",
        workspace=tmp_path / session_id / "workspace",
        input_reader=_reader([request, "/send", "/approve", "/exit"]),
        output_writer=lambda _line: None,
        worker_process_runner=_must_not_start_process,
    )


def test_prior_marker_read_request_remains_knowledge_routed_without_approval(
    tmp_path,
) -> None:
    route = route_platform_query(query=PRIOR_MARKER_REQUEST, created_at=CREATED_AT)
    result = _session(
        tmp_path,
        session_id="G31-20E-PRIOR-KNOWLEDGE",
        request=PRIOR_MARKER_REQUEST,
    )

    assert route["selected_service"] == PLATFORM_KNOWLEDGE_ROUTE
    assert route["classification_evidence"]["development_intent_summary_admissible"] is False
    assert result["approval_count"] == 0
    assert result["runtime_entered"] is False
    assert result["process_start_count"] == 0


def test_repository_grounded_patch_request_selects_existing_development_path(
    tmp_path,
) -> None:
    route = route_platform_query(query=GROUNDED_DEVELOPMENT_REQUEST, created_at=CREATED_AT)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G31-20E-GROUNDED",
        message=GROUNDED_DEVELOPMENT_REQUEST,
        runtime_root=tmp_path / "grounded-runtime",
        workspace=tmp_path / "grounded-workspace",
        created_at=CREATED_AT,
    )
    resolution = context["development_intent_resolution"]

    assert len(GROUNDED_DEVELOPMENT_REQUEST) < 180
    assert route["selected_service"] == GOVERNED_DEVELOPMENT_ROUTE
    assert route["classification_evidence"]["development_intent_summary_admissible"] is True
    assert resolution["summary_admissible"] is True
    assert resolution["runtime_binding_admissible"] is True
    assert resolution["requires_human_approval"] is True


@pytest.mark.parametrize(
    "prompt",
    (
        "Improve this.",
        "Summarize calc.py and test_calc.py. Do not edit files.",
    ),
)
def test_ambiguous_and_pure_summary_requests_do_not_activate_worker(
    tmp_path, prompt: str
) -> None:
    result = _session(
        tmp_path,
        session_id=f"G31-20E-NONEXEC-{len(prompt)}",
        request=prompt,
    )

    assert result["approval_count"] == 0
    assert result["runtime_entered"] is False
    assert result["process_start_count"] == 0


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("selected_service", GOVERNED_DEVELOPMENT_ROUTE),
        ("classification_evidence", {"development_intent_summary_admissible": True}),
    ),
)
def test_route_and_summary_admissibility_substitution_fail_closed(
    field: str, replacement: object
) -> None:
    route = route_platform_query(query=PRIOR_MARKER_REQUEST, created_at=CREATED_AT)
    substituted = deepcopy(route)
    substituted[field] = replacement

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_platform_query_router_response(substituted)


def test_cross_session_clarification_routing_evidence_fails_closed(tmp_path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G31-20E-SESSION-A",
        message="Analyze Platform Capability Composition Coverage.\nAudit only.",
        runtime_root=tmp_path / "cross-session-runtime",
        workspace=tmp_path / "cross-session-workspace",
        created_at=CREATED_AT,
    )
    envelope = context["operational_clarification_envelope"]

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        validate_operational_clarification_envelope(
            envelope,
            expected_session_id="G31-20E-SESSION-B",
        )
