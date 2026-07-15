from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED,
    IMPLEMENTATION_TURN_READY_FOR_APPROVAL,
    consume_approved_implementation_turn_binding,
    reconstruct_implementation_turn_approval_consumption,
    reconstruct_implementation_turn_durable_work_binding,
    validate_implementation_turn_durable_work_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
REQUEST = (
    "Improve the human interface runtime and canonical presentation for "
    "terminal development summaries. Include focused tests and validation."
)


def _context(tmp_path: Path, *, session_id: str = "G31-04-CONTEXT") -> dict:
    workspace = tmp_path / "workspace"
    workspace.mkdir(exist_ok=True)
    (workspace / ".git").mkdir(exist_ok=True)
    return prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=session_id,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        created_at=CREATED_AT,
    )


def _binding(tmp_path: Path, *, session_id: str = "G31-04-BINDING") -> dict:
    return _context(tmp_path, session_id=session_id)[
        "canonical_implementation_turn_binding"
    ]


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


def _rehash(artifact: dict) -> dict:
    artifact["artifact_hash"] = replay_hash(
        {key: value for key, value in artifact.items() if key != "artifact_hash"}
    )
    return artifact


def test_ordinary_implementation_turn_composes_existing_plan_and_durable_work(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)
    binding = context["canonical_implementation_turn_binding"]
    plan = binding["development_composition_plan_artifact"]
    durable = binding["durable_governed_work_artifact"]
    preview = binding["proposal_preview_artifact"]

    assert binding["binding_status"] == IMPLEMENTATION_TURN_READY_FOR_APPROVAL
    assert plan["artifact_type"] == "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1"
    assert durable["artifact_type"] == "PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1"
    assert durable["source_development_plan_hash"] == plan["artifact_hash"]
    assert durable["source_project_objective_hash"] == context[
        "project_objective_inference"
    ]["artifact_hash"]
    assert preview["development_composition_plan_hash"] == plan["artifact_hash"]
    assert preview["durable_governed_work_hash"] == durable["artifact_hash"]
    assert context["development_intent_resolution"]["summary_admissible"] is True
    assert context["human_conversation_experience"]["response_mode"] == (
        "APPROVAL_PREPARATION"
    )


def test_preview_is_canonical_traceable_and_does_not_use_generic_marker(
    tmp_path: Path,
) -> None:
    binding = _binding(tmp_path)
    preview = binding["proposal_preview_artifact"]

    assert preview["original_human_goal"] == REQUEST
    assert preview["canonical_project_objective"]
    assert preview["knowledge_reuse_hash"] == binding["knowledge_reuse_hash"]
    assert preview["platform_knowledge_hash"] == binding["platform_knowledge_hash"]
    assert preview["required_implementation_work"]
    assert preview["ordered_implementation_sequence"]
    assert preview["validation_requirements"]
    assert preview["governance_dependencies"]
    assert preview["replay_requirements"]
    assert preview["certification_requirements"]
    assert preview["approval_is_execution_authorization"] is False
    assert preview["generic_marker_fallback_used"] is False
    assert binding["generic_marker_fallback_used"] is False
    assert "acli_governed_development_" not in json.dumps(preview)


def test_repository_scope_is_explicitly_unresolved_without_invented_paths(
    tmp_path: Path,
) -> None:
    preview = _binding(tmp_path)["proposal_preview_artifact"]

    assert preview["repository_scope_status"] == (
        "UNRESOLVED_WITHIN_CANONICAL_CAPABILITY_BOUNDARY"
    )
    assert preview["proposed_repository_paths"] == []
    assert "not invented" in preview["repository_scope_explanation"]


def test_aicli_renders_canonical_proposal_and_exact_identities_before_approval(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G31-04-AICLI-PREAPPROVAL",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        input_reader=_reader([REQUEST, "/send"]),
        output_writer=output.append,
    )
    rendered = "\n".join(output)

    assert result["pending_approval"] is True
    assert "Canonical durable governed-work proposal" in rendered
    assert "development_composition_plan_hash: sha256:" in rendered
    assert "durable_governed_work_hash: sha256:" in rendered
    assert "proposal_preview_hash: sha256:" in rendered
    assert "approval_request_hash: sha256:" in rendered
    assert "approval_is_execution_authorization: False" in rendered
    assert "acli_governed_development_" not in rendered
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False


@pytest.mark.parametrize(
    "nested_field,mutation",
    [
        ("project_objective_artifact", ("canonical_project_objective", "tampered")),
        ("capability_composition_coverage_artifact", ("query", "tampered")),
        ("development_composition_plan_artifact", ("source_request", "tampered")),
        ("durable_governed_work_artifact", ("source_request", "tampered")),
        ("proposal_preview_artifact", ("original_human_goal", "tampered")),
    ],
)
def test_nested_artifact_tampering_fails_closed(
    tmp_path: Path,
    nested_field: str,
    mutation: tuple[str, str],
) -> None:
    binding = deepcopy(_binding(tmp_path, session_id=f"G31-04-{nested_field}"))
    binding[nested_field][mutation[0]] = mutation[1]
    _rehash(binding)

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_implementation_turn_durable_work_binding(binding)


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
    ],
)
def test_outer_identity_substitution_fails_closed(
    tmp_path: Path,
    identity_field: str,
) -> None:
    binding = deepcopy(_binding(tmp_path, session_id=f"G31-04-{identity_field}"))
    binding[identity_field] = replay_hash(f"tampered:{identity_field}")
    _rehash(binding)

    with pytest.raises(FailClosedRuntimeError, match="identity mismatch"):
        validate_implementation_turn_durable_work_binding(binding)


def test_preapproval_authority_boundaries_remain_false(tmp_path: Path) -> None:
    binding = _binding(tmp_path)

    for field in (
        "human_interface_authority",
        "human_interface_semantic_authority",
        "human_interface_planning_authority",
        "human_interface_approval_authority",
        "human_interface_execution_authority",
        "provider_invoked",
        "worker_invoked",
        "execution_authorized",
        "repository_mutated",
        "validation_executed",
        "certification_reached",
    ):
        assert binding[field] is False


def test_textual_approval_cannot_consume_substituted_identity(tmp_path: Path) -> None:
    binding = _binding(tmp_path)

    with pytest.raises(
        FailClosedRuntimeError,
        match="approved implementation turn identity mismatch",
    ):
        consume_approved_implementation_turn_binding(
            binding_artifact=binding,
            development_composition_plan_hash=binding[
                "development_composition_plan_hash"
            ],
            durable_governed_work_hash=binding["durable_governed_work_hash"],
            proposal_preview_hash=replay_hash("substituted-preview"),
            approval_request_hash=binding["approval_request_hash"],
            created_at=CREATED_AT,
            replay_dir=binding["replay_reference"],
        )


def test_canonical_runtime_entry_consumes_exact_approved_identities(
    tmp_path: Path,
) -> None:
    binding = _binding(tmp_path)
    calls: list[dict] = []

    def runtime_runner(args, input_func, output_func):
        calls.append(
            {
                "prompt": input_func(""),
                "binding_hash": args.approved_implementation_turn_binding_hash,
                "consumption_hash": args.approved_identity_consumption_hash,
                "durable_hash": args.approved_durable_governed_work_hash,
                "preview_hash": args.approved_proposal_preview_hash,
                "approval_request_hash": args.approved_approval_request_hash,
            }
        )
        output_func("continued")
        return {
            "command": "aigol conversation",
            "runtime_root": args.runtime_root,
            "turn_count": 1,
            "failed_turns": 0,
            "exit_reason": "EXIT_COMMAND",
            "auto_continue_enabled": True,
            "turns": [
                {
                    "worker_invoked": False,
                    "replay_certification_reached": False,
                    "replay_reference": str(tmp_path / "downstream"),
                }
            ],
        }

    result = run_human_interface_runtime_entry(
        interface_name="aicli",
        session_id="G31-04-BINDING",
        human_requests=[REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        governed_runtime_runner=runtime_runner,
        approved_implementation_turn_binding=binding,
        approved_development_composition_plan_hash=binding[
            "development_composition_plan_hash"
        ],
        approved_durable_governed_work_hash=binding["durable_governed_work_hash"],
        approved_proposal_preview_hash=binding["proposal_preview_hash"],
        approved_approval_request_hash=binding["approval_request_hash"],
    )
    consumption = result["approved_identity_consumption"]

    assert calls[0]["prompt"] == REQUEST
    assert calls[0]["binding_hash"] == binding["artifact_hash"]
    assert calls[0]["consumption_hash"] == consumption["artifact_hash"]
    assert calls[0]["durable_hash"] == binding["durable_governed_work_hash"]
    assert calls[0]["preview_hash"] == binding["proposal_preview_hash"]
    assert calls[0]["approval_request_hash"] == binding["approval_request_hash"]
    assert result["approved_durable_work_identity_consumed"] is True
    assert result["approved_identity_transport_to_canonical_continuation"] is True
    assert consumption["consumption_status"] == (
        IMPLEMENTATION_TURN_APPROVED_IDENTITIES_CONSUMED
    )
    assert consumption["development_composition_plan_hash"] == binding[
        "development_composition_plan_hash"
    ]
    assert consumption["durable_governed_work_hash"] == binding[
        "durable_governed_work_hash"
    ]
    assert consumption["proposal_preview_hash"] == binding["proposal_preview_hash"]
    assert consumption["approval_request_hash"] == binding["approval_request_hash"]
    assert consumption["approval_is_execution_authorization"] is False
    assert consumption["worker_invoked"] is False
    assert consumption["repository_mutated"] is False


def test_binding_and_approval_consumption_reconstruct_from_replay(
    tmp_path: Path,
) -> None:
    binding = _binding(tmp_path)
    consumption = consume_approved_implementation_turn_binding(
        binding_artifact=binding,
        development_composition_plan_hash=binding["development_composition_plan_hash"],
        durable_governed_work_hash=binding["durable_governed_work_hash"],
        proposal_preview_hash=binding["proposal_preview_hash"],
        approval_request_hash=binding["approval_request_hash"],
        created_at=CREATED_AT,
        replay_dir=binding["replay_reference"],
    )

    reconstructed_binding = reconstruct_implementation_turn_durable_work_binding(
        binding["replay_reference"]
    )
    reconstructed_consumption = reconstruct_implementation_turn_approval_consumption(
        binding["replay_reference"]
    )
    assert reconstructed_binding["artifact_hash"] == binding["artifact_hash"]
    assert reconstructed_consumption["artifact_hash"] == consumption["artifact_hash"]


def test_replay_wrapper_tampering_fails_closed(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    path = Path(binding["replay_reference"]) / (
        "000_implementation_turn_binding_recorded.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "substituted"
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="Replay ordering mismatch"):
        reconstruct_implementation_turn_durable_work_binding(
            binding["replay_reference"]
        )


def test_insufficient_goal_uses_existing_clarification_without_binding(
    tmp_path: Path,
) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G31-04-UNRESOLVED",
        message="Improve project.",
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
    )

    assert context["development_intent_resolution"]["clarification_required"] is True
    assert context["canonical_implementation_turn_binding"] is None
    assert context["human_conversation_experience"]["response_mode"] == "CLARIFICATION"
    assert "acli_governed_development_" not in json.dumps(context)


def test_new_capability_decision_projects_existing_gap_without_new_selector(
    tmp_path: Path,
) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G31-04-NEW-CAPABILITY",
        message="Implement a new read-only Platform Core capability.",
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
    )
    binding = context["canonical_implementation_turn_binding"]
    coverage = binding["capability_composition_coverage_artifact"]

    assert binding["binding_status"] == IMPLEMENTATION_TURN_READY_FOR_APPROVAL
    assert coverage["binding_projection"]["semantic_selection_created"] is False
    assert coverage["binding_projection"]["planning_engine_created"] is False
    assert coverage["uncovered_residual_gaps"][0]["facet"] == (
        "PROJECT_CAPABILITY_GAP"
    )
