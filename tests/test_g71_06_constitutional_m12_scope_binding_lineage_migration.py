from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.cli import aicli
from aigol.runtime import (
    codex_satisfied_outcome_disposable_validation_binding_runtime as disposable,
)
from aigol.runtime import human_interface_runtime_entry_service as human_entry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g64_04_constitutional_reuse_proof_production_integration import (
    CREATED_AT,
    REQUEST,
    _project_context,
)


def _authenticated_context(tmp_path, name: str) -> dict:
    context = _project_context(tmp_path, name, admitted=True)
    assert context["reuse_proof_production_admission"]["admission_status"] == (
        "READY_FOR_FRESH_G47"
    )
    assert context["constitutional_development_governance"][
        "integration_status"
    ] == "G47_OPERATIONAL_INTEGRATION_READY"
    return context


def _owner_result(context: dict, tmp_path) -> dict:
    turn = context["canonical_implementation_turn_binding"]

    def governed_runner(_args, **_kwargs):
        return {
            "command": "G71-06-FOCUSED",
            "runtime_root": str(tmp_path / "governed-runtime"),
            "turn_count": 0,
            "failed_turns": 0,
            "exit_reason": "FOCUSED_OWNER_RETURN",
            "auto_continue_enabled": True,
            "auto_continue_stop_reason": None,
            "turns": [],
        }

    return human_entry._run_human_interface_runtime_entry_owner_execution_v1(
        interface_name="aicli",
        session_id="G71-06-OWNER",
        human_requests=[REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path / "owner-runtime",
        workspace=context["workspace"],
        governed_runtime_runner=governed_runner,
        approved_implementation_turn_binding=turn,
        approved_development_composition_plan_hash=turn[
            "development_composition_plan_hash"
        ],
        approved_durable_governed_work_hash=turn["durable_governed_work_hash"],
        approved_proposal_preview_hash=turn["proposal_preview_hash"],
        approved_approval_request_hash=turn["approval_request_hash"],
        explicit_canonical_artifacts=(context["reuse_proof_g47_scope_binding"],),
    )


def test_authenticated_binding_is_preserved_by_existing_che_owner_state(
    tmp_path,
) -> None:
    context = _authenticated_context(tmp_path, "G71-06-OWNER")
    binding = context["reuse_proof_g47_scope_binding"]

    result = _owner_result(context, tmp_path)

    assert result["reuse_proof_g47_scope_binding"] == binding
    assert result["reuse_proof_g47_scope_binding"] is not binding
    assert result["reuse_proof_g47_scope_binding_hash"] == binding["artifact_hash"]
    assert result["approved_implementation_turn_binding"]["artifact_hash"] == (
        binding["g47_operational_record"]["implementation_turn_binding_hash"]
    )


def test_scope_binding_tamper_and_cross_turn_substitution_fail_closed(
    tmp_path,
) -> None:
    context = _authenticated_context(tmp_path, "G71-06-TAMPER")
    binding = deepcopy(context["reuse_proof_g47_scope_binding"])
    binding["scope_digest"] = replay_hash("tampered scope")
    turn = context["canonical_implementation_turn_binding"]

    with pytest.raises(FailClosedRuntimeError, match="scope_digest mismatch"):
        human_entry._run_human_interface_runtime_entry_owner_execution_v1(
            interface_name="aicli",
            session_id="G71-06-TAMPER",
            human_requests=[REQUEST],
            created_at=CREATED_AT,
            runtime_root=tmp_path / "tamper-runtime",
            workspace=context["workspace"],
            governed_runtime_runner=lambda *_args, **_kwargs: {},
            approved_implementation_turn_binding=turn,
            approved_development_composition_plan_hash=turn[
                "development_composition_plan_hash"
            ],
            approved_durable_governed_work_hash=turn[
                "durable_governed_work_hash"
            ],
            approved_proposal_preview_hash=turn["proposal_preview_hash"],
            approved_approval_request_hash=turn["approval_request_hash"],
            explicit_canonical_artifacts=(binding,),
        )

    substituted_turn = deepcopy(turn)
    substituted_turn["artifact_hash"] = replay_hash("different approved turn")
    with pytest.raises(FailClosedRuntimeError, match="implementation-turn lineage mismatch"):
        human_entry._run_human_interface_runtime_entry_owner_execution_v1(
            interface_name="aicli",
            session_id="G71-06-SUBSTITUTION",
            human_requests=[REQUEST],
            created_at=CREATED_AT,
            runtime_root=tmp_path / "substitution-runtime",
            workspace=context["workspace"],
            governed_runtime_runner=lambda *_args, **_kwargs: {},
            approved_implementation_turn_binding=substituted_turn,
            approved_development_composition_plan_hash=turn[
                "development_composition_plan_hash"
            ],
            approved_durable_governed_work_hash=turn[
                "durable_governed_work_hash"
            ],
            approved_proposal_preview_hash=turn["proposal_preview_hash"],
            approved_approval_request_hash=turn["approval_request_hash"],
            explicit_canonical_artifacts=(
                context["reuse_proof_g47_scope_binding"],
            ),
        )


def test_aicli_approval_handoff_transports_exact_project_services_binding(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _authenticated_context(tmp_path, "G71-06-AICLI")
    binding = context["reuse_proof_g47_scope_binding"]
    calls: list[dict] = []

    def fake_entry(**kwargs):
        calls.append(kwargs)
        if kwargs.get("operator_context") == "AICLI_NEW_TURN_PRE_APPROVAL":
            return {
                "platform_core_project_services_context": deepcopy(context),
                "production_conversation_flow_binding": {
                    "artifact_hash": replay_hash("G71-06 flow")
                },
                "owner_bound_clarification_envelope": None,
                "human_interface_runtime_entry_service_used": True,
            }
        if kwargs.get("g31_synthesis_preflight_prompt") is not None:
            return {
                "codex_synthesis_preflight_capture": {
                    "synthesis_preflight_status": "SYNTHESIS_PREFLIGHT_READY",
                    "synthesis_preflight_hash": replay_hash("G71-06 preflight"),
                    "synthesis_preflight_performed": True,
                    "synthesis_within_bound": True,
                    "raw_character_count": len(REQUEST),
                    "prefix_character_count": 0,
                    "final_character_count": len(REQUEST),
                    "maximum_character_count": 100000,
                    "human_decision_count": 0,
                    "process_start_count": 0,
                },
                "g31_canonical_presentations": [],
            }
        return {
            "canonical_runtime_entry_status": (
                "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED"
            ),
            "runtime_binding_status": (
                "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED"
            ),
            "runtime_entered": False,
            "g31_canonical_presentations": [],
        }

    monkeypatch.setattr(aicli, "run_human_interface_runtime_entry", fake_entry)
    values = iter([REQUEST, "/send", "/approve", "exit"])
    aicli.run_reference_uhi_session(
        session_id="G71-06-AICLI",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-runtime",
        workspace=context["workspace"],
        input_reader=lambda _prompt: next(values),
        output_writer=lambda _line: None,
    )

    approval_call = next(
        call
        for call in calls
        if call.get("operator_context")
        == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    )
    transported = approval_call["explicit_canonical_artifacts"]
    assert len(transported) == 1
    assert transported[0] == binding
    assert transported[0]["artifact_hash"] == (
        binding["artifact_hash"]
    )

    calls.clear()
    submit_values = iter(["/approve"])
    aicli.run_reference_uhi_submit_session(
        session_id="G71-06-AICLI-SUBMIT",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "aicli-submit-runtime",
        workspace=context["workspace"],
        stdin_reader=lambda: REQUEST,
        input_reader=lambda _prompt: next(submit_values),
        output_writer=lambda _line: None,
    )
    submit_approval_call = next(
        call
        for call in calls
        if call.get("operator_context")
        == "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY"
    )
    submit_transport = submit_approval_call["explicit_canonical_artifacts"]
    assert len(submit_transport) == 1
    assert submit_transport[0] == binding
    assert submit_transport[0]["artifact_hash"] == binding["artifact_hash"]


def test_existing_m12_owner_receives_exact_binding_and_discharge_continues(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _authenticated_context(tmp_path, "G71-06-M12")
    binding = context["reuse_proof_g47_scope_binding"]
    observed: dict = {}

    def execute_spy(**kwargs):
        observed["binding"] = kwargs["reuse_proof_g47_scope_binding"]
        artifact = {
            "artifact_hash": replay_hash("G71-06 M12 outcome"),
            "disposable_patch_application_attempted": True,
            "disposable_patch_applied": True,
            "content_validation_performed": True,
            "content_validation_passed": True,
            "grounded_test_execution_performed": True,
            "grounded_test_validation_passed": True,
            "ready_for_generated_content_acceptance": True,
            "repository_mutation_authorized": False,
            "failure_reason": None,
        }
        return {
            "outcome_artifact": artifact,
            **{
                key: artifact[key]
                for key in (
                    "disposable_patch_applied",
                    "content_validation_performed",
                    "content_validation_passed",
                    "grounded_test_execution_performed",
                    "grounded_test_validation_passed",
                    "ready_for_generated_content_acceptance",
                    "repository_mutation_authorized",
                    "failure_reason",
                )
            },
        }

    monkeypatch.setattr(human_entry, "_g31_disposable_lineage", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(disposable, "execute_disposable_patch_validation", execute_spy)
    monkeypatch.setattr(
        disposable,
        "reconstruct_disposable_patch_validation_outcome",
        lambda **_kwargs: {"execution_status": "COMPLETED"},
    )
    state = {
        "reuse_proof_g47_scope_binding": deepcopy(binding),
        "reuse_proof_g47_scope_binding_hash": binding["artifact_hash"],
        "disposable_patch_validation_review_capture": {
            "disposable_patch_validation_plan_artifact": {
                "artifact_hash": replay_hash("G71-06 M12 plan")
            }
        },
        "disposable_patch_validation_human_decision_capture": {},
    }

    result = human_entry._execute_g31_disposable_patch_validation(
        session="G71-06-M12",
        root=tmp_path,
        workspace_path=str(context["workspace"]),
        created=CREATED_AT,
        runtime_result=state,
        actor="HUMAN_OPERATOR",
    )

    assert observed["binding"] == binding
    assert observed["binding"]["artifact_hash"] == binding["artifact_hash"]
    assert result["disposable_patch_validation_executed"] is True
    assert result["focused_validation_succeeded"] is True
    assert result["ready_for_generated_content_acceptance"] is True
    assert result["result_accepted"] is False
    assert result["main_repository_mutated"] is False
