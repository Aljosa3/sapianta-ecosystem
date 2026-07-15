from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli, aigol_cli
from aigol.runtime.approved_durable_work_worker_payload_binding import (
    APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE,
    APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1,
    WORKER_PAYLOAD_BOUND,
    WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED,
    bind_approved_durable_work_to_worker_payload,
    reconstruct_approved_durable_work_worker_payload_binding,
    validate_approved_durable_work_worker_payload_binding,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    consume_approved_implementation_turn_binding,
    validate_implementation_turn_durable_work_binding,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CREATED_AT = "2026-07-15T00:00:00Z"
REQUEST = (
    "Improve the human interface runtime and canonical presentation for "
    "terminal development summaries. Include focused tests and validation."
)


def _rehash(artifact: dict) -> dict:
    body = {key: value for key, value in artifact.items() if key != "artifact_hash"}
    artifact["artifact_hash"] = replay_hash(body)
    return artifact


def _binding(tmp_path: Path, *, session_id: str = "G31-05") -> dict:
    workspace = tmp_path / f"workspace-{session_id}"
    workspace.mkdir()
    (workspace / ".git").mkdir()
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        created_at=CREATED_AT,
    )
    return context["canonical_implementation_turn_binding"]


def _consume(binding: dict) -> dict:
    return consume_approved_implementation_turn_binding(
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


def _payload(
    tmp_path: Path, *, session_id: str = "G31-05-PAYLOAD"
) -> tuple[dict, dict, dict]:
    binding = _binding(tmp_path, session_id=session_id)
    consumption = _consume(binding)
    payload = bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=binding,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"payload-{session_id}",
    )
    return binding, consumption, payload


def _grounded_binding(tmp_path: Path) -> dict:
    binding = deepcopy(_binding(tmp_path, session_id="G31-05-GROUNDED-SOURCE"))
    preview = binding["proposal_preview_artifact"]
    preview["repository_scope_status"] = "CANONICALLY_GROUNDED"
    preview["proposed_repository_paths"] = [
        "aigol/cli/aicli.py",
        "tests/test_aicli.py",
    ]
    preview["repository_scope_explanation"] = "Paths supplied by canonical repository evidence."
    _rehash(preview)
    binding["proposal_preview_hash"] = preview["artifact_hash"]
    grounded_replay = tmp_path / "grounded-binding-replay"
    binding["replay_reference"] = str(grounded_replay)
    _rehash(binding)
    validate_implementation_turn_durable_work_binding(binding, require_ready=True)
    wrapper = {
        "replay_index": 0,
        "replay_step": "implementation_turn_binding_recorded",
        "artifact": deepcopy(binding),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(
        grounded_replay / "000_implementation_turn_binding_recorded.json",
        wrapper,
    )
    return binding


def test_existing_native_artifact_contracts_receive_exact_approved_identities(
    tmp_path: Path,
) -> None:
    binding, consumption, payload = _payload(tmp_path)
    task = payload["ppp_task_package_artifact"]
    request = payload["implementation_request_artifact"]
    worker = payload["worker_implementation_payload_artifact"]

    assert payload["artifact_type"] == (
        APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1
    )
    assert task["artifact_type"] == "PPP_CANDIDATE_ARTIFACT_V1"
    assert request["artifact_type"] == "IMPLEMENTATION_REQUEST_ARTIFACT_V1"
    assert worker["artifact_type"] == "WORKER_REQUEST_ARTIFACT_V1"
    assert task["candidate_source_type"] == (
        APPROVED_DURABLE_WORK_PPP_TASK_PACKAGE_SOURCE
    )
    lineage = task["source_approved_work_lineage"]
    assert lineage["implementation_turn_binding_hash"] == binding["artifact_hash"]
    assert lineage["approval_consumption_hash"] == consumption["artifact_hash"]
    assert lineage["development_composition_plan_hash"] == binding[
        "development_composition_plan_hash"
    ]
    assert lineage["durable_governed_work_hash"] == binding[
        "durable_governed_work_hash"
    ]
    assert request["canonical_approved_work_lineage"] == lineage
    assert worker["canonical_approved_work_lineage"] == lineage


def test_worker_payload_is_goal_and_project_objective_faithful(tmp_path: Path) -> None:
    binding, _, payload = _payload(tmp_path)
    scope = payload["worker_implementation_payload_artifact"][
        "implementation_scope"
    ]

    assert scope["original_human_goal"] == REQUEST
    assert scope["original_human_goal_hash"] == binding["original_request_hash"]
    assert scope["canonical_project_objective"] == binding[
        "project_objective_artifact"
    ]["canonical_project_objective"]
    assert scope["project_objective_hash"] == binding["project_objective_hash"]
    assert payload["worker_implementation_payload_artifact"]["worker_objective"] == (
        binding["project_objective_artifact"]["canonical_project_objective"]
    )


def test_generic_marker_and_worker_foundation_fallbacks_are_absent(
    tmp_path: Path,
) -> None:
    _, _, payload = _payload(tmp_path)
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["generic_marker_fallback_used"] is False
    assert payload["generic_worker_foundation_payload_used"] is False
    assert "AIGOL_GENERIC_DEVELOPMENT_TASK_V1" not in serialized
    assert "WORKER_FOUNDATION" not in serialized
    assert "marker_module" not in serialized


def test_every_required_payload_group_has_approved_field_lineage(
    tmp_path: Path,
) -> None:
    _, _, payload = _payload(tmp_path)
    lineage = payload["payload_field_lineage"]
    required = {
        "original_human_goal",
        "project_objective",
        "platform_knowledge",
        "knowledge_reuse",
        "capability_coverage",
        "development_plan",
        "durable_governed_work",
        "proposal_preview",
        "approval_request",
        "approval_consumption",
        "work_scope_and_sequence",
        "repository_scope",
        "test_validation_governance_replay_certification",
    }

    assert set(lineage) == required
    for source in lineage.values():
        assert source["source_artifact_type"]
        assert source["source_identity"]
        assert source["source_hash"].startswith("sha256:")


def test_payload_projects_all_available_approved_work_requirements(
    tmp_path: Path,
) -> None:
    binding, consumption, payload = _payload(tmp_path)
    scope = payload["implementation_request_artifact"]["implementation_scope"]
    plan = binding["development_composition_plan_artifact"]
    durable = binding["durable_governed_work_artifact"]

    assert scope["platform_knowledge_hash"] == binding["platform_knowledge_hash"]
    assert scope["knowledge_reuse_hash"] == binding["knowledge_reuse_hash"]
    assert scope["capability_composition_coverage_hash"] == binding[
        "capability_composition_coverage_hash"
    ]
    assert scope["development_composition_plan_hash"] == plan["artifact_hash"]
    assert scope["durable_governed_work_id"] == durable["governed_work_id"]
    assert scope["durable_governed_work_hash"] == durable["artifact_hash"]
    assert scope["proposal_preview_hash"] == binding["proposal_preview_hash"]
    assert scope["approval_request_hash"] == binding["approval_request_hash"]
    assert scope["approval_consumption_hash"] == consumption["artifact_hash"]
    assert scope["bounded_work_scope"] == plan[
        "minimal_required_platform_extension"
    ]
    assert scope["residual_implementation_gaps"] == plan[
        "residual_capability_gaps"
    ]
    assert scope["ordered_implementation_sequence"] == plan[
        "ordered_implementation_sequence"
    ]
    assert scope["focused_test_requirements"] == binding[
        "proposal_preview_artifact"
    ]["focused_tests"]
    assert scope["validation_requirements"] == durable["validation_requirements"]
    assert scope["governance_requirements"] == durable["governance_dependencies"]
    assert scope["replay_requirements"] == durable["replay_dependencies"]
    assert scope["certification_requirements"] == durable[
        "certification_dependencies"
    ]
    assert scope["acceptance_requirements"] == []


def test_unresolved_scope_is_preserved_and_fails_closed_before_dispatch(
    tmp_path: Path,
) -> None:
    _, _, payload = _payload(tmp_path)
    scope = payload["worker_implementation_payload_artifact"][
        "implementation_scope"
    ]

    assert payload["binding_status"] == (
        WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED
    )
    assert payload["repository_scope_unresolved"] is True
    assert payload["repository_targets"] == []
    assert scope["repository_targets"] == []
    assert payload["dispatch_blocked"] is True
    assert payload["worker_implementation_payload_artifact"][
        "ready_for_worker_dispatch_governance"
    ] is False
    assert "aigol/" not in json.dumps(scope["repository_targets"])


def test_canonically_grounded_repository_scope_is_preserved_exactly(
    tmp_path: Path,
) -> None:
    binding = _grounded_binding(tmp_path)
    consumption = _consume(binding)
    payload = bind_approved_durable_work_to_worker_payload(
        implementation_turn_binding=binding,
        approval_consumption_artifact=consumption,
        requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "grounded-payload",
    )

    assert payload["binding_status"] == WORKER_PAYLOAD_BOUND
    assert payload["repository_scope_status"] == "CANONICALLY_GROUNDED"
    assert payload["repository_targets"] == [
        "aigol/cli/aicli.py",
        "tests/test_aicli.py",
    ]
    assert payload["dispatch_blocked"] is False
    assert payload["ready_for_separate_dispatch_governance"] is True


@pytest.mark.parametrize(
    "identity_field",
    [
        "project_objective_hash",
        "knowledge_reuse_hash",
        "platform_knowledge_hash",
        "capability_composition_coverage_hash",
        "development_composition_plan_hash",
        "durable_governed_work_hash",
        "proposal_preview_hash",
        "approval_request_hash",
        "approval_request_id",
        "durable_governed_work_id",
        "binding_hash",
    ],
)
def test_every_approved_identity_substitution_fails_before_task_acceptance(
    tmp_path: Path,
    identity_field: str,
) -> None:
    binding = _binding(tmp_path, session_id=f"G31-05-TAMPER-{identity_field}")
    consumption = _consume(binding)
    tampered = deepcopy(consumption)
    tampered[identity_field] = replay_hash(f"substituted:{identity_field}")
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="continuity mismatch"):
        bind_approved_durable_work_to_worker_payload(
            implementation_turn_binding=binding,
            approval_consumption_artifact=tampered,
            requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"rejected-{identity_field}",
        )


def test_original_goal_substitution_fails_before_task_acceptance(
    tmp_path: Path,
) -> None:
    binding = _binding(tmp_path, session_id="G31-05-GOAL-TAMPER")
    consumption = _consume(binding)
    tampered = deepcopy(binding)
    tampered["original_request"] = "Replacement goal"
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError):
        bind_approved_durable_work_to_worker_payload(
            implementation_turn_binding=tampered,
            approval_consumption_artifact=consumption,
            requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "rejected-goal",
        )


def test_approval_consumption_record_tampering_fails_before_task_acceptance(
    tmp_path: Path,
) -> None:
    binding = _binding(tmp_path, session_id="G31-05-CONSUMPTION-TAMPER")
    consumption = deepcopy(_consume(binding))
    consumption["created_at"] = "2026-07-15T00:00:01Z"

    with pytest.raises(FailClosedRuntimeError, match="consumption hash mismatch"):
        bind_approved_durable_work_to_worker_payload(
            implementation_turn_binding=binding,
            approval_consumption_artifact=consumption,
            requested_by="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "rejected-consumption",
        )


def test_task_package_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, payload = _payload(tmp_path)
    tampered = deepcopy(payload)
    task = tampered["ppp_task_package_artifact"]
    task["proposal_summary"] = "replacement objective"
    _rehash(task)
    tampered["ppp_task_package_hash"] = task["artifact_hash"]
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="PPP task-package mismatch"):
        validate_approved_durable_work_worker_payload_binding(tampered)


def test_worker_payload_substitution_fails_closed(tmp_path: Path) -> None:
    _, _, payload = _payload(tmp_path)
    tampered = deepcopy(payload)
    worker = tampered["worker_implementation_payload_artifact"]
    worker["worker_objective"] = "replacement objective"
    _rehash(worker)
    tampered["worker_implementation_payload_hash"] = worker["artifact_hash"]
    _rehash(tampered)

    with pytest.raises(FailClosedRuntimeError, match="objective mismatch"):
        validate_approved_durable_work_worker_payload_binding(tampered)


def test_approval_is_not_execution_authorization_and_no_actor_is_invoked(
    tmp_path: Path,
) -> None:
    _, _, payload = _payload(tmp_path)

    assert payload["approval_is_execution_authorization"] is False
    for field in (
        "execution_authorized",
        "provider_invoked",
        "worker_invoked",
        "worker_assigned",
        "worker_dispatched",
        "repository_mutated",
        "validation_executed",
        "certification_reached",
    ):
        assert payload[field] is False


def test_aicli_has_no_semantic_planning_or_execution_authority(tmp_path: Path) -> None:
    _, _, payload = _payload(tmp_path)

    for field in (
        "human_interface_authority",
        "human_interface_semantic_authority",
        "human_interface_planning_authority",
        "human_interface_provider_authority",
        "human_interface_worker_authority",
        "human_interface_mutation_authority",
        "human_interface_approval_authority",
        "human_interface_authorization_authority",
        "human_interface_replay_authority",
    ):
        assert payload[field] is False


def test_replay_reconstructs_upstream_approval_task_and_worker_payload(
    tmp_path: Path,
) -> None:
    binding, consumption, payload = _payload(tmp_path)
    reconstructed = reconstruct_approved_durable_work_worker_payload_binding(
        payload["replay_reference"]
    )

    assert reconstructed["source_implementation_turn_binding_hash"] == binding[
        "artifact_hash"
    ]
    assert reconstructed["source_approval_consumption_hash"] == consumption[
        "artifact_hash"
    ]
    assert reconstructed["ppp_task_package_hash"] == payload[
        "ppp_task_package_hash"
    ]
    assert reconstructed["implementation_request_hash"] == payload[
        "implementation_request_hash"
    ]
    assert reconstructed["worker_implementation_payload_hash"] == payload[
        "worker_implementation_payload_hash"
    ]


def test_replay_order_or_wrapper_tampering_fails_closed(tmp_path: Path) -> None:
    _, _, payload = _payload(tmp_path)
    path = Path(payload["replay_reference"]) / (
        "001_approved_durable_work_worker_payload_binding_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "reordered"
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_approved_durable_work_worker_payload_binding(
            payload["replay_reference"]
        )


def test_real_aicli_approval_uses_canonical_payload_path(tmp_path: Path) -> None:
    output: list[str] = []
    inputs = iter([REQUEST, "/send", "/approve", "/exit"])
    result = aicli.run_reference_uhi_session(
        session_id="G31-05-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=lambda _prompt: next(inputs),
        output_writer=output.append,
    )
    rendered = "\n".join(output)
    runtime = result["runtime_result"]

    assert "Approved durable governed work Worker payload" in rendered
    assert "APPROVED_DURABLE_WORK_WORKER_PAYLOAD_SCOPE_UNRESOLVED_FAILED_CLOSED" in rendered
    assert "AIGOL_GENERIC_DEVELOPMENT_TASK_V1" not in rendered
    assert "WORKER_FOUNDATION" not in rendered
    assert runtime["approved_worker_payload_binding_hash"].startswith("sha256:")
    assert runtime["approved_ppp_task_package_hash"].startswith("sha256:")
    assert runtime["approved_implementation_request_hash"].startswith("sha256:")
    assert runtime["approved_worker_implementation_payload_hash"].startswith(
        "sha256:"
    )
    assert runtime["approved_worker_payload_dispatch_blocked"] is True
    assert runtime["provider_invocation_reached"] is False
    assert runtime["worker_execution_reached"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


def test_historical_governed_development_compatibility_remains_outside_g31_path(
    tmp_path: Path,
) -> None:
    args = argparse.Namespace(
        session_id="G31-05-HISTORICAL",
        created_at=CREATED_AT,
        runtime_root=str(tmp_path / "runtime"),
        workspace=str(tmp_path),
        operator_context="HUMAN_OPERATOR",
        auto_continue=False,
        enable_llm_assisted_explanation=False,
        llm_explanation_provider_id="UNSPECIFIED_EXPLANATION_PROVIDER",
    )
    assert aigol_cli._approved_durable_work_worker_payload_binding_active(args) is False
    assert callable(aigol_cli.propose_acli_governed_development_execution)
