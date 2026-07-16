from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    REPOSITORY_SCOPE_GROUNDED,
    ground_approved_durable_work_repository_scope,
)
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    bind_approved_durable_work_to_worker_payload,
)
from aigol.runtime.execution_summary_runtime import (
    EXECUTION_SUMMARY_ARTIFACT_V1,
    PENDING_HUMAN_CONFIRMATION,
)
from aigol.runtime.grounded_worker_request_execution_authorization_binding import (
    EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED,
    EXECUTION_AUTHORIZATION_REVIEW_REQUIRED,
    GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1,
    bind_grounded_worker_request_to_execution_authorization_review,
    reconstruct_grounded_worker_request_execution_authorization_review,
    validate_grounded_worker_request_execution_authorization_review,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED,
    consume_approved_implementation_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-16T00:00:00Z"
REQUEST = (
    "Improve the human interface terminal summary behavior. "
    "Include focused tests and validation."
)


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    return artifact


def _workspace(tmp_path: Path, *, name: str) -> Path:
    workspace = tmp_path / name
    (workspace / ".git").mkdir(parents=True)
    (workspace / "aigol" / "runtime").mkdir(parents=True)
    (workspace / "tests").mkdir()
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return f'Summary: {value}'\n",
        encoding="utf-8",
    )
    (workspace / "tests" / "test_human_interface.py").write_text(
        "from aigol.runtime.human_interface import render_summary\n\n"
        "def test_render_summary():\n"
        "    assert render_summary('ready') == 'Summary: ready'\n",
        encoding="utf-8",
    )
    return workspace


def _grounding(
    tmp_path: Path,
    *,
    session_id: str,
) -> tuple[dict, dict, dict, dict, Path]:
    workspace = _workspace(tmp_path, name=f"workspace-{session_id}")
    binding = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=REQUEST,
        runtime_root=tmp_path / f"runtime-{session_id}",
        workspace=workspace,
        created_at=CREATED_AT,
    )["canonical_implementation_turn_binding"]
    consumption = consume_approved_implementation_turn_binding(
        binding_artifact=binding,
        development_composition_plan_hash=binding[
            "development_composition_plan_hash"
        ],
        durable_governed_work_hash=binding["durable_governed_work_hash"],
        proposal_preview_hash=binding["proposal_preview_hash"],
        approval_request_hash=binding["approval_request_hash"],
        created_at=CREATED_AT,
        replay_dir=binding["replay_reference"],
    )
    payload = bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=binding,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"payload-{session_id}",
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"grounding-{session_id}",
    )
    assert grounding["grounding_status"] == REPOSITORY_SCOPE_GROUNDED
    return binding, consumption, payload, grounding, workspace


def _review(
    tmp_path: Path,
    *,
    session_id: str,
) -> tuple[dict, dict, dict, dict, dict, Path]:
    binding, consumption, payload, grounding, workspace = _grounding(
        tmp_path,
        session_id=session_id,
    )
    review = bind_grounded_worker_request_to_execution_authorization_review(
        repository_scope_grounding_artifact=grounding,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"review-{session_id}",
    )
    return binding, consumption, payload, grounding, review, workspace


def test_grounded_request_creates_existing_pending_execution_review(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, review, _ = _review(
        tmp_path,
        session_id="G31-08-POSITIVE",
    )

    assert review["artifact_type"] == (
        GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1
    )
    assert review["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_REQUIRED
    )
    assert review["source_repository_scope_grounding_hash"] == grounding[
        "artifact_hash"
    ]
    assert review["execution_summary_artifact"]["artifact_type"] == (
        EXECUTION_SUMMARY_ARTIFACT_V1
    )
    assert review["execution_summary_artifact"]["summary_status"] == (
        PENDING_HUMAN_CONFIRMATION
    )


def test_authorization_scope_exactly_equals_grounded_evidence(tmp_path: Path) -> None:
    binding, _, _, grounding, review, workspace = _review(
        tmp_path,
        session_id="G31-08-SCOPE",
    )
    scope = review["authorization_scope"]
    worker = grounding["grounded_worker_request_artifact"]

    assert scope["workspace_root"] == str(workspace.resolve())
    assert scope["repository_targets"] == grounding["grounded_repository_targets"]
    assert scope["source_paths"] == grounding["grounded_source_targets"]
    assert scope["focused_test_paths"] == grounding[
        "grounded_focused_test_targets"
    ]
    assert scope["target_evidence"] == grounding["target_evidence"]
    assert scope["original_human_goal"] == REQUEST
    assert scope["project_objective_hash"] == binding["project_objective_hash"]
    assert scope["approved_bounded_work"] == worker["implementation_scope"][
        "bounded_work_scope"
    ]
    assert review["execution_summary_artifact"]["execution_scope"] == scope


@pytest.mark.parametrize(
    "field",
    [
        "source_repository_scope_grounding_hash",
        "source_grounding_evidence_hash",
        "source_repository_cognition_snapshot_hash",
        "source_worker_payload_binding_hash",
        "source_implementation_turn_binding_hash",
        "source_approval_consumption_hash",
        "source_development_composition_plan_hash",
        "source_durable_governed_work_hash",
        "source_proposal_preview_hash",
        "source_approval_request_hash",
        "source_ppp_task_package_hash",
        "source_implementation_request_hash",
        "source_worker_implementation_payload_hash",
        "source_grounded_worker_request_hash",
    ],
)
def test_every_upstream_identity_is_consumed_unchanged(
    tmp_path: Path,
    field: str,
) -> None:
    _, _, _, grounding, review, _ = _review(
        tmp_path,
        session_id=f"G31-08-IDENTITY-{field}",
    )

    expected = {
        "source_repository_scope_grounding_hash": grounding["artifact_hash"],
        "source_grounding_evidence_hash": grounding["grounding_evidence_hash"],
        "source_repository_cognition_snapshot_hash": grounding[
            "repository_cognition_snapshot_hash"
        ],
        "source_worker_payload_binding_hash": grounding[
            "source_worker_payload_binding_hash"
        ],
        "source_implementation_turn_binding_hash": grounding[
            "source_implementation_turn_binding_hash"
        ],
        "source_approval_consumption_hash": grounding[
            "source_approval_consumption_hash"
        ],
        "source_development_composition_plan_hash": grounding[
            "source_development_composition_plan_hash"
        ],
        "source_durable_governed_work_hash": grounding[
            "source_durable_governed_work_hash"
        ],
        "source_proposal_preview_hash": grounding["source_proposal_preview_hash"],
        "source_approval_request_hash": grounding["source_approval_request_hash"],
        "source_ppp_task_package_hash": grounding["source_ppp_task_package_hash"],
        "source_implementation_request_hash": grounding[
            "source_implementation_request_hash"
        ],
        "source_worker_implementation_payload_hash": grounding[
            "source_worker_implementation_payload_hash"
        ],
        "source_grounded_worker_request_hash": grounding[
            "grounded_worker_request_hash"
        ],
    }
    assert review[field] == expected[field]


def test_proposal_approval_is_distinct_from_execution_authorization(
    tmp_path: Path,
) -> None:
    _, consumption, _, _, review, _ = _review(
        tmp_path,
        session_id="G31-08-DISTINCT-AUTHORIZATION",
    )

    assert consumption["consumption_status"] == (
        IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED
    )
    assert review["proposal_approval_is_execution_authorization"] is False
    assert review["distinct_human_execution_authorization_required"] is True
    assert review["human_confirmation_artifact"] is None
    assert review["authorization_request_created"] is False
    assert review["authorization_decision_created"] is False
    assert review["execution_authorization_created"] is False
    assert review["execution_authorized"] is False


def test_no_command_target_authority_or_execution_is_invented(tmp_path: Path) -> None:
    _, _, _, _, review, _ = _review(
        tmp_path,
        session_id="G31-08-NO-INVENTION",
    )
    serialized = json.dumps(review, sort_keys=True)

    assert '"command"' not in serialized
    for field in (
        "worker_selected",
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "provider_invoked",
        "execution_started",
        "repository_mutated",
        "human_interface_authority",
        "human_interface_authorization_authority",
        "human_interface_policy_authority",
        "human_interface_worker_authority",
    ):
        assert review[field] is False
    assert review["dispatch_blocked_pending_authorization"] is True
    assert review["stop_before_worker_selection"] is True


def test_unresolved_grounding_fails_closed_before_review(tmp_path: Path) -> None:
    _, _, _, grounding, workspace = _grounding(
        tmp_path,
        session_id="G31-08-UNRESOLVED-SOURCE",
    )
    unresolved = deepcopy(grounding)
    unresolved["grounding_status"] = "REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED"
    unresolved["fail_closed"] = True
    unresolved["failure_reason"] = "ambiguous repository evidence"
    _rehash(unresolved)

    review = bind_grounded_worker_request_to_execution_authorization_review(
        repository_scope_grounding_artifact=unresolved,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unresolved-review",
    )

    assert review["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED
    )
    assert review["authorization_scope"] == {}
    assert review["execution_summary_artifact"] is None
    assert review["execution_authorized"] is False


def test_stale_repository_cognition_evidence_fails_closed(tmp_path: Path) -> None:
    _, _, _, grounding, workspace = _grounding(
        tmp_path,
        session_id="G31-08-STALE",
    )
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return value.upper()\n",
        encoding="utf-8",
    )

    review = bind_grounded_worker_request_to_execution_authorization_review(
        repository_scope_grounding_artifact=grounding,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "stale-review",
    )

    assert review["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED
    )
    assert "stale or substituted" in review["failure_reason"]


@pytest.mark.parametrize(
    "mutation",
    ["broadened_path", "substituted_symbol", "changed_layer", "changed_validation"],
)
def test_broadened_or_substituted_authorization_scope_fails_closed(
    tmp_path: Path,
    mutation: str,
) -> None:
    _, _, _, _, review, _ = _review(
        tmp_path,
        session_id=f"G31-08-SCOPE-TAMPER-{mutation}",
    )
    tampered = deepcopy(review)
    scope = tampered["authorization_scope"]
    if mutation == "broadened_path":
        scope["repository_targets"].append("aigol/runtime/extra.py")
    elif mutation == "substituted_symbol":
        scope["symbols_by_path"][0]["symbols"][0]["symbol_name"] = "other"
    elif mutation == "changed_layer":
        scope["mutation_layers"][0]["mutation_layer"] = "L4"
    else:
        scope["validation_requirements"].append("invented command")
    scope["scope_hash"] = replay_hash(
        {key: value for key, value in scope.items() if key != "scope_hash"}
    )
    tampered["authorization_scope_hash"] = scope["scope_hash"]
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="scope mismatch"):
        validate_grounded_worker_request_execution_authorization_review(tampered)


def test_upstream_identity_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, _, _, review, _ = _review(
        tmp_path,
        session_id="G31-08-UPSTREAM-TAMPER",
    )
    tampered = deepcopy(review)
    tampered["source_approval_request_hash"] = replay_hash("substituted")
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="upstream identity mismatch"):
        validate_grounded_worker_request_execution_authorization_review(tampered)


def test_execution_summary_scope_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, _, _, review, _ = _review(
        tmp_path,
        session_id="G31-08-SUMMARY-TAMPER",
    )
    tampered = deepcopy(review)
    summary = tampered["execution_summary_artifact"]
    summary["execution_scope"]["repository_targets"].append("outside.py")
    _rehash(summary)
    tampered["execution_summary_hash"] = summary["artifact_hash"]
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="summary scope differs"):
        validate_grounded_worker_request_execution_authorization_review(tampered)


def test_replay_reconstructs_grounding_and_pending_authorization_review(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, review, workspace = _review(
        tmp_path,
        session_id="G31-08-REPLAY",
    )

    reconstructed = (
        reconstruct_grounded_worker_request_execution_authorization_review(
            review["replay_reference"],
            workspace=workspace,
        )
    )
    assert reconstructed["artifact_hash"] == review["artifact_hash"]
    assert reconstructed["source_repository_scope_grounding_hash"] == grounding[
        "artifact_hash"
    ]


def test_replay_reordering_fails_closed(tmp_path: Path) -> None:
    _, _, _, _, review, workspace = _review(
        tmp_path,
        session_id="G31-08-REORDER",
    )
    path = Path(review["replay_reference"]) / (
        "001_execution_authorization_review_binding_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "repository_scope_grounding_source_recorded"
    wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in wrapper.items() if key != "replay_hash"}
    )
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_grounded_worker_request_execution_authorization_review(
            review["replay_reference"],
            workspace=workspace,
        )


def test_replay_grounding_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, _, _, review, workspace = _review(
        tmp_path,
        session_id="G31-08-REPLAY-SUBSTITUTION",
    )
    path = Path(review["replay_reference"]) / (
        "000_repository_scope_grounding_source_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["artifact_hash"] = replay_hash("substituted grounding")
    wrapper["replay_hash"] = replay_hash(
        {key: value for key, value in wrapper.items() if key != "replay_hash"}
    )
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_grounded_worker_request_execution_authorization_review(
            review["replay_reference"],
            workspace=workspace,
        )


def test_failed_review_replay_reconstructs_without_partial_authority(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, workspace = _grounding(
        tmp_path,
        session_id="G31-08-FAILED-REPLAY",
    )
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return value.upper()\n",
        encoding="utf-8",
    )
    review = bind_grounded_worker_request_to_execution_authorization_review(
        repository_scope_grounding_artifact=grounding,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failed-review-replay",
    )

    reconstructed = (
        reconstruct_grounded_worker_request_execution_authorization_review(
            review["replay_reference"],
            workspace=workspace,
        )
    )
    assert reconstructed["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED
    )
    assert reconstructed["execution_authorized"] is False
    assert reconstructed["authorization_scope"] == {}


def test_binding_uses_public_validation_without_copying_g31_06_helpers() -> None:
    source = Path(
        "aigol/runtime/grounded_worker_request_execution_authorization_binding.py"
    ).read_text(encoding="utf-8")

    assert "verify_replay_hash" in source
    assert "def _verify_hash" not in source
    assert "def _relative_path" not in source
    assert "def _unique_relative_paths" not in source


def test_real_aicli_reaches_distinct_authorization_review_and_stops(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path, name="aicli-workspace")
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-08-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]
    rendered = "\n".join(output)

    assert "Grounded Worker request execution-authorization review" in rendered
    assert runtime["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_REQUIRED
    )
    assert runtime["distinct_human_execution_authorization_required"] is True
    assert runtime["proposal_approval_is_execution_authorization"] is False
    assert runtime["execution_authorized"] is False
    assert runtime["worker_selected"] is False
    assert runtime["authorization_dispatch_blocked"] is True
    assert runtime["governance_authorization_reached"] is False
    assert runtime["provider_invocation_reached"] is False
    assert runtime["worker_execution_reached"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


def test_aicli_only_renders_authorization_review_evidence() -> None:
    source = Path(aicli.__file__).read_text(encoding="utf-8")

    assert "authorization_review_status" in source
    assert "execution_authorized" in source
    assert "authorize_execution_ready" not in source
    assert "select_worker" not in source
