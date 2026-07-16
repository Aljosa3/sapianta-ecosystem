from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime import approved_durable_work_repository_scope_grounding as grounding_runtime
from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1,
    REPOSITORY_SCOPE_GROUNDED,
    REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED,
    ground_approved_durable_work_repository_scope,
    reconstruct_approved_durable_work_repository_scope_grounding,
    validate_approved_durable_work_repository_scope_grounding,
)
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    bind_approved_durable_work_to_worker_payload,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    project_worker_request_repository_scope,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    consume_approved_implementation_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
REQUEST = (
    "Improve the human interface terminal summary behavior. "
    "Include focused tests and validation."
)


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    return artifact


def _workspace(tmp_path: Path, *, name: str = "workspace") -> Path:
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


def _payload(
    tmp_path: Path,
    *,
    workspace: Path | None = None,
    session_id: str = "G31-06",
) -> tuple[dict, dict, dict, Path]:
    repository = workspace or _workspace(tmp_path, name=f"workspace-{session_id}")
    binding = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=REQUEST,
        runtime_root=tmp_path / f"runtime-{session_id}",
        workspace=repository,
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
    return binding, consumption, payload, repository


def _grounding(
    tmp_path: Path,
    *,
    session_id: str = "G31-06-GROUNDING",
) -> tuple[dict, dict, dict, dict, Path]:
    binding, consumption, payload, workspace = _payload(
        tmp_path,
        session_id=session_id,
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"grounding-{session_id}",
    )
    return binding, consumption, payload, grounding, workspace


def test_exact_repository_cognition_match_produces_one_immutable_grounding(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(tmp_path)

    assert grounding["artifact_type"] == (
        CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1
    )
    assert grounding["grounding_status"] == REPOSITORY_SCOPE_GROUNDED
    assert grounding["canonical_capability_target"] == "human_interface"
    assert grounding["grounded_repository_targets"] == [
        "aigol/runtime/human_interface.py",
        "tests/test_human_interface.py",
    ]
    assert grounding["grounded_source_targets"] == [
        "aigol/runtime/human_interface.py"
    ]
    assert grounding["grounded_focused_test_targets"] == [
        "tests/test_human_interface.py"
    ]
    assert grounding["repository_cognition_snapshot_hash"].startswith("sha256:")
    assert grounding["grounding_evidence_hash"].startswith("sha256:")


def test_all_approved_g31_04_and_g31_05_identities_are_consumed_unchanged(
    tmp_path: Path,
) -> None:
    binding, consumption, payload, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-IDENTITIES",
    )

    assert grounding["source_worker_payload_binding_hash"] == payload["artifact_hash"]
    assert grounding["source_implementation_turn_binding_hash"] == binding[
        "artifact_hash"
    ]
    assert grounding["source_approval_consumption_hash"] == consumption[
        "artifact_hash"
    ]
    assert grounding["source_development_composition_plan_hash"] == binding[
        "development_composition_plan_hash"
    ]
    assert grounding["source_durable_governed_work_hash"] == binding[
        "durable_governed_work_hash"
    ]
    assert grounding["source_proposal_preview_hash"] == binding[
        "proposal_preview_hash"
    ]
    assert grounding["source_approval_request_hash"] == binding[
        "approval_request_hash"
    ]


def test_goal_objective_plan_task_and_worker_objective_remain_unchanged(
    tmp_path: Path,
) -> None:
    binding, _, payload, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-CONTINUITY",
    )
    source_worker = payload["worker_implementation_payload_artifact"]
    grounded_worker = grounding["grounded_worker_request_artifact"]

    assert grounded_worker["worker_objective"] == source_worker["worker_objective"]
    assert grounded_worker["implementation_scope"]["original_human_goal"] == REQUEST
    assert grounded_worker["implementation_scope"]["project_objective_hash"] == binding[
        "project_objective_hash"
    ]
    assert grounded_worker["canonical_approved_work_lineage"] == source_worker[
        "canonical_approved_work_lineage"
    ]
    assert grounding["task_package_preserved"] is True
    assert grounding["approved_plan_preserved"] is True


def test_grounded_paths_symbols_tests_layers_and_hashes_come_only_from_cognition(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-EVIDENCE",
    )
    evidence = grounding["target_evidence"]

    assert [item["target_path"] for item in evidence] == grounding[
        "grounded_repository_targets"
    ]
    assert evidence[0]["symbols"][0]["symbol_name"] == "render_summary"
    assert evidence[1]["symbols"][0]["symbol_name"] == "test_render_summary"
    assert evidence[0]["mutation_layer"] == "L2"
    assert evidence[1]["mutation_layer"] == "L4"
    assert all(item["source_content_hash"].startswith("sha256:") for item in evidence)
    assert all(item["target_evidence_hash"].startswith("sha256:") for item in evidence)


def test_existing_worker_request_scope_projection_is_exact_and_non_executing(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-PROJECTION",
    )
    worker = grounding["grounded_worker_request_artifact"]

    assert worker["repository_scope_status"] == (
        "CANONICALLY_GROUNDED_BY_REPOSITORY_COGNITION"
    )
    assert worker["repository_targets"] == grounding["grounded_repository_targets"]
    assert worker["implementation_scope"]["focused_test_requirements"] == [
        "tests/test_human_interface.py"
    ]
    assert worker["ready_for_worker_dispatch_governance"] is True
    assert worker["dispatch_blocked_by_unresolved_repository_scope"] is False
    assert worker["dispatch_requested"] is False
    assert worker["worker_dispatched"] is False
    assert worker["worker_invoked"] is False


def test_no_target_command_placeholder_or_natural_language_bridge_is_invented(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-NO-INVENTION",
    )
    serialized = json.dumps(grounding, sort_keys=True)

    assert grounding["natural_language_target_inference_used"] is False
    assert grounding["placeholder_target_used"] is False
    assert grounding["repository_discovery_framework_created"] is False
    assert '"command"' not in serialized
    assert "AIGOL_GENERIC_DEVELOPMENT_TASK_V1" not in serialized
    assert "WORKER_FOUNDATION" not in serialized


def test_no_exact_compatible_evidence_retains_explicit_unresolved_state(
    tmp_path: Path,
) -> None:
    _, _, payload, workspace = _payload(
        tmp_path,
        session_id="G31-06-NO-MATCH",
    )
    (workspace / "aigol" / "runtime" / "human_interface.py").rename(
        workspace / "aigol" / "runtime" / "unrelated.py"
    )
    (workspace / "tests" / "test_human_interface.py").rename(
        workspace / "tests" / "test_unrelated.py"
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no-match-grounding",
    )

    assert grounding["grounding_status"] == (
        REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    )
    assert grounding["grounded_repository_targets"] == []
    assert grounding["dispatch_blocked"] is True
    assert grounding["grounded_worker_request_artifact"] is None


def test_materially_ambiguous_implementation_evidence_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, payload, workspace = _payload(
        tmp_path,
        session_id="G31-06-AMBIGUOUS",
    )
    monkeypatch.setattr(
        grounding_runtime,
        "detect_capabilities",
        lambda _root: {
            "human_interface": {
                "key": "human_interface",
                "status": "IMPLEMENTED",
                "implementation": [
                    "aigol/runtime/human_interface.py",
                    "aigol/runtime/materially_different.py",
                ],
                "tests": ["tests/test_human_interface.py"],
            }
        },
    )
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous-grounding",
    )

    assert grounding["grounding_status"] == (
        REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    )
    assert "ambiguous" in grounding["failure_reason"]


def test_missing_git_metadata_fails_closed_without_aborting_upstream_payload(
    tmp_path: Path,
) -> None:
    binding, consumption, payload, workspace = _payload(
        tmp_path,
        session_id="G31-06-NO-GIT",
    )
    (workspace / ".git").rmdir()
    grounding = ground_approved_durable_work_repository_scope(
        worker_payload_binding_artifact=payload,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no-git-grounding",
    )

    assert grounding["grounding_status"] == (
        REPOSITORY_SCOPE_UNRESOLVED_FAILED_CLOSED
    )
    assert grounding["source_implementation_turn_binding_hash"] == binding[
        "artifact_hash"
    ]
    assert grounding["source_approval_consumption_hash"] == consumption[
        "artifact_hash"
    ]


def test_stale_repository_evidence_fails_reconstruction(tmp_path: Path) -> None:
    _, _, _, grounding, workspace = _grounding(
        tmp_path,
        session_id="G31-06-STALE",
    )
    (workspace / "aigol" / "runtime" / "human_interface.py").write_text(
        "def render_summary(value):\n    return value.upper()\n",
        encoding="utf-8",
    )

    with pytest.raises(FailClosedRuntimeError, match="stale or substituted"):
        reconstruct_approved_durable_work_repository_scope_grounding(
            grounding["replay_reference"],
            workspace=workspace,
        )


@pytest.mark.parametrize(
    "field",
    [
        "source_implementation_turn_binding_hash",
        "source_approval_consumption_hash",
        "source_development_composition_plan_hash",
        "source_durable_governed_work_hash",
        "source_proposal_preview_hash",
        "source_approval_request_hash",
        "source_ppp_task_package_hash",
        "source_implementation_request_hash",
        "source_worker_implementation_payload_hash",
    ],
)
def test_every_upstream_identity_substitution_fails_closed(
    tmp_path: Path,
    field: str,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id=f"G31-06-TAMPER-{field}",
    )
    tampered = deepcopy(grounding)
    tampered[field] = replay_hash(f"substituted:{field}")
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="upstream identity mismatch"):
        validate_approved_durable_work_repository_scope_grounding(tampered)


@pytest.mark.parametrize(
    "mutation",
    ["outside", "missing_hash", "missing_layer", "immutable_layer", "substituted_path"],
)
def test_invalid_target_evidence_fails_closed(
    tmp_path: Path,
    mutation: str,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id=f"G31-06-TARGET-{mutation}",
    )
    tampered = deepcopy(grounding)
    target = tampered["target_evidence"][0]
    if mutation == "outside":
        target["target_path"] = "../outside.py"
    elif mutation == "missing_hash":
        target["source_content_hash"] = None
    elif mutation == "missing_layer":
        target["mutation_layer"] = None
    elif mutation == "immutable_layer":
        target["mutation_layer"] = "L0"
    else:
        target["target_path"] = "aigol/runtime/substituted.py"
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError):
        validate_approved_durable_work_repository_scope_grounding(tampered)


def test_projection_rejects_out_of_workspace_target(tmp_path: Path) -> None:
    _, _, payload, _, _ = _grounding(
        tmp_path,
        session_id="G31-06-PROJECTION-OUTSIDE",
    )

    with pytest.raises(FailClosedRuntimeError, match="workspace-relative"):
        project_worker_request_repository_scope(
            worker_request_artifact=payload[
                "worker_implementation_payload_artifact"
            ],
            repository_targets=["../outside.py", "tests/test_human_interface.py"],
            focused_test_targets=["tests/test_human_interface.py"],
            repository_scope_grounding_identity="GROUNDING",
            repository_scope_grounding_hash=replay_hash("grounding"),
        )


def test_grounded_worker_scope_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-WORKER-SUBSTITUTION",
    )
    tampered = deepcopy(grounding)
    worker = tampered["grounded_worker_request_artifact"]
    worker["worker_objective"] = "replacement objective"
    _rehash(worker)
    tampered["grounded_worker_request_hash"] = worker["artifact_hash"]
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="changed approved field"):
        validate_approved_durable_work_repository_scope_grounding(tampered)


def test_replay_reconstructs_complete_ordered_grounding_chain(tmp_path: Path) -> None:
    _, _, payload, grounding, workspace = _grounding(
        tmp_path,
        session_id="G31-06-REPLAY",
    )
    reconstructed = reconstruct_approved_durable_work_repository_scope_grounding(
        grounding["replay_reference"],
        workspace=workspace,
    )

    assert reconstructed["artifact_hash"] == grounding["artifact_hash"]
    assert reconstructed["source_worker_payload_binding_hash"] == payload[
        "artifact_hash"
    ]
    assert reconstructed["grounded_worker_request_hash"] == grounding[
        "grounded_worker_request_hash"
    ]


def test_replay_reordering_and_grounding_substitution_fail_closed(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-REPLAY-TAMPER",
    )
    path = Path(grounding["replay_reference"]) / (
        "001_canonical_repository_scope_grounding_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "substituted"
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_approved_durable_work_repository_scope_grounding(
            grounding["replay_reference"]
        )


def test_all_authorization_provider_worker_dispatch_and_mutation_boundaries_false(
    tmp_path: Path,
) -> None:
    _, _, _, grounding, _ = _grounding(
        tmp_path,
        session_id="G31-06-BOUNDARIES",
    )

    for field in (
        "execution_authorized",
        "provider_invoked",
        "worker_selected",
        "worker_assigned",
        "worker_dispatched",
        "worker_invoked",
        "repository_mutated",
        "validation_executed",
        "certification_reached",
        "human_interface_authority",
        "human_interface_semantic_authority",
        "human_interface_repository_selection_authority",
    ):
        assert grounding[field] is False


def test_real_aicli_approval_reaches_positive_grounding_and_stops(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path, name="aicli-workspace")
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-06-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=workspace,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )
    runtime = result["runtime_result"]
    rendered = "\n".join(output)

    assert "Canonical repository-scope grounding" in rendered
    assert runtime["repository_scope_grounding_status"] == REPOSITORY_SCOPE_GROUNDED
    assert runtime["grounded_repository_targets"] == [
        "aigol/runtime/human_interface.py",
        "tests/test_human_interface.py",
    ]
    assert runtime["repository_scope_dispatch_blocked"] is False
    assert runtime["governance_authorization_reached"] is False
    assert runtime["provider_invocation_reached"] is False
    assert runtime["worker_execution_reached"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


def test_aicli_owns_no_repository_selection_or_semantics(tmp_path: Path) -> None:
    source = Path(aicli.__file__).read_text(encoding="utf-8")

    assert "detect_capabilities" not in source
    assert "grounded_repository_targets" in source
    assert "repository_scope_grounding_hash" in source
