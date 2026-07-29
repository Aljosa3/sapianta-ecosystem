from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.constitutional_development_governance_operational_integration import (
    G47_OPERATIONAL_INTEGRATION_READY,
    reconstruct_constitutional_development_governance_operational_replay,
)
from aigol.runtime.constitutional_development_governance_orchestration import (
    DevelopmentGovernanceRuntimeError,
    compose_governance_eligible_implementation_turn_durable_work_binding,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime import platform_implementation_turn_durable_work_binding
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-07-29T00:00:00Z"
READY_REQUEST = (
    "Improve the human interface runtime and canonical presentation for "
    "terminal development summaries. Include focused tests and validation."
)
REVIEW_REQUEST = "Implement a new read-only Platform Core capability."


def _context(tmp_path: Path, request: str, session_id: str) -> dict:
    workspace = tmp_path / f"{session_id}_workspace"
    workspace.mkdir()
    (workspace / ".git").mkdir()
    return prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=request,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        created_at=CREATED_AT,
    )


def test_planning_eligible_governance_enters_existing_durable_work(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path, READY_REQUEST, "G47-01D-READY")
    governance = context["constitutional_development_governance"]
    binding = context["canonical_implementation_turn_binding"]

    assert governance["integration_status"] == G47_OPERATIONAL_INTEGRATION_READY
    assert governance["governance_disposition"] == "BOUNDED_PLANNING_PERMITTED"
    assert governance["planning_eligible"] is True
    assert binding["binding_status"] == "IMPLEMENTATION_TURN_READY_FOR_APPROVAL"
    assert governance["planner_semantics_modified"] is False
    assert governance["replay_protocol_modified"] is False
    assert context["development_intent_resolution"]["summary_admissible"] is True


def test_existing_capability_framework_bounds_new_realization(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path, REVIEW_REQUEST, "G47-01D-REVIEW")
    governance = context["constitutional_development_governance"]
    resolution = context["development_intent_resolution"]

    assert governance["integration_status"] == G47_OPERATIONAL_INTEGRATION_READY
    assert governance["governance_disposition"] == "BOUNDED_PLANNING_PERMITTED"
    assert governance["planning_eligible"] is True
    need = governance["stage_outputs"][3]
    assert need["outcome"] == "NEW_REALIZATION_JUSTIFIED"
    assert context["canonical_implementation_turn_binding"] is not None
    assert resolution["summary_admissible"] is True


def test_direct_planner_bypass_without_bundle_fails_closed() -> None:
    with pytest.raises(
        DevelopmentGovernanceRuntimeError,
        match="requires the complete bundle",
    ):
        compose_governance_eligible_implementation_turn_durable_work_binding(
            planning_eligibility=None,  # type: ignore[arg-type]
            request=READY_REQUEST,
            project_objective_artifact={},
            knowledge_reuse_artifact={},
            workspace_state=None,
            workspace=".",
            created_at=CREATED_AT,
            replay_dir=".",
        )


def test_planner_scope_expansion_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        platform_implementation_turn_durable_work_binding,
        "implementation_turn_planning_scope_from_plan",
        lambda _artifact: ("UNAUTHORIZED_SCOPE_EXPANSION",),
    )
    with pytest.raises(
        DevelopmentGovernanceRuntimeError,
        match="planner output scope differs",
    ):
        _context(tmp_path, READY_REQUEST, "G47-01D-SCOPE-MISMATCH")


def test_additive_replay_reconstructs_and_tampering_fails_closed(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path, READY_REQUEST, "G47-01D-REPLAY")
    expected = context["constitutional_development_governance"]
    replay_file = next(
        (tmp_path / "runtime").rglob(
            "000_development_governance_integration_recorded.json"
        )
    )
    reconstructed = (
        reconstruct_constitutional_development_governance_operational_replay(
            replay_file.parent
        )
    )
    assert reconstructed["artifact_hash"] == expected["artifact_hash"]

    wrapper = load_json(replay_file)
    wrapper["artifact"]["planning_eligible"] = False
    wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in wrapper.items() if key != "replay_hash"}
    )
    tampered_dir = tmp_path / "tampered"
    tampered_dir.mkdir()
    from aigol.runtime.transport.serialization import write_json_immutable

    write_json_immutable(
        tampered_dir / replay_file.name,
        deepcopy(wrapper),
    )
    with pytest.raises(
        DevelopmentGovernanceRuntimeError,
        match="integration hash mismatch",
    ):
        reconstruct_constitutional_development_governance_operational_replay(
            tampered_dir
        )


def test_aicli_transports_and_renders_governance_projection(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    values = iter((READY_REQUEST, "/send"))
    result = aicli.run_reference_uhi_session(
        session_id="G47-01D-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(values),
        output_writer=output.append,
        runtime_runner=lambda **_kwargs: {},
    )
    rendered = "\n".join(output)

    assert result["pending_approval"] is True
    assert "Development Governance pre-planning barrier" in rendered
    assert "governance_disposition: BOUNDED_PLANNING_PERMITTED" in rendered
    assert "planning_eligible: True" in rendered
    assert "governance_bundle_hash: sha256:" in rendered
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
