"""Generation 4 governed natural-language development loop scaffold."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_uhcl_adapter_rendering import (
    capture_uhcl_human_response,
    reconstruct_acli_uhcl_adapter_replay,
    render_uhcl_artifact_for_acli,
)
from aigol.runtime.canonical_semantic_artifact_runtime import (
    create_canonical_semantic_artifact_from_translation,
    reconstruct_canonical_semantic_artifact_replay,
)
from aigol.runtime.human_to_governance_translation_runtime import (
    translate_human_to_governance,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_human_communication_model_runtime import (
    DOMAIN_RECOMMENDATION,
    LEVEL_STANDARD,
    SOURCE_COMPONENT_OCS,
    create_shared_confirmation_model,
    create_ubtr_human_communication_artifact,
    reconstruct_shared_confirmation_replay,
    reconstruct_ubtr_human_communication_replay,
)
from aigol.runtime.ubtr_semantic_cognition_orchestration_runtime import (
    orchestrate_ubtr_semantic_cognition,
    reconstruct_ubtr_semantic_cognition_orchestration_replay,
)


G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION = (
    "G4_GOVERNED_DEVELOPMENT_LOOP_EXECUTION_SCAFFOLD_V1"
)
ACLI_INPUT_ARTIFACT_V1 = "G4_ACLI_NATURAL_LANGUAGE_INPUT_ARTIFACT_V1"
OCS_PROPOSAL_ARTIFACT_V1 = "G4_OCS_GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1"
GOVERNANCE_CHECKPOINT_ARTIFACT_V1 = "G4_GOVERNED_DEVELOPMENT_CHECKPOINT_ARTIFACT_V1"
EXECUTION_INTENT_ARTIFACT_V1 = "G4_ADVISORY_EXECUTION_INTENT_ARTIFACT_V1"
SCAFFOLD_SUMMARY_ARTIFACT_V1 = "G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_SUMMARY_ARTIFACT_V1"

SCAFFOLD_RECORDED = "G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_RECORDED"
ADVISORY_ONLY_CHECKPOINT_PASSED = "ADVISORY_ONLY_CHECKPOINT_PASSED"
BLOCKED_PENDING_GOVERNANCE = "BLOCKED_PENDING_GOVERNANCE"

REPLAY_STEPS = (
    "acli_natural_language_input_recorded",
    "ubtr_semantic_artifact_recorded",
    "csa_structured_intent_recorded",
    "ocs_proposal_recorded",
    "governance_checkpoints_recorded",
    "uhcl_communication_recorded",
    "acli_render_recorded",
    "human_response_recorded",
    "advisory_execution_intent_recorded",
    "g4_loop_scaffold_summary_recorded",
)


def run_g4_governed_development_loop_scaffold(
    *,
    scaffold_id: str,
    human_intent: str,
    operator_response: str,
    created_at: str,
    replay_dir: str | Path,
    communication_level: str = LEVEL_STANDARD,
    session_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the deterministic G4 governed development loop scaffold."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)

    input_artifact = _acli_input_artifact(
        scaffold_id=scaffold_id,
        human_intent=human_intent,
        session_context=session_context or {},
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], input_artifact)

    translation_capture = translate_human_to_governance(
        translation_request_id=f"{scaffold_id}:UBTR-TRANSLATION",
        human_request=input_artifact["human_intent"],
        created_at=created_at,
        replay_dir=replay_path / "ubtr_translation",
        session_context=session_context or {},
        available_workflows=["GOVERNED_DEVELOPMENT_WORKFLOW"],
    )
    translation_artifact = translation_capture["translation_artifact"]
    _persist_step(replay_path, 1, REPLAY_STEPS[1], _lineage_projection("UBTR", translation_artifact, translation_capture))

    semantic_capture = create_canonical_semantic_artifact_from_translation(
        semantic_artifact_id=f"{scaffold_id}:CSA-STRUCTURED-INTENT",
        translation_artifact=translation_artifact,
        conversation_id=f"{scaffold_id}:ACLI-CONVERSATION",
        workflow_id=None,
        created_at=created_at,
        replay_dir=replay_path / "csa_structured_intent",
    )
    semantic_artifact = semantic_capture["semantic_artifact"]
    _persist_step(replay_path, 2, REPLAY_STEPS[2], _lineage_projection("CSA", semantic_artifact, semantic_capture))

    orchestration_capture = orchestrate_ubtr_semantic_cognition(
        orchestration_id=f"{scaffold_id}:UBTR-OCS-HANDOFF",
        canonical_semantic_artifact=semantic_artifact,
        created_at=created_at,
        replay_dir=replay_path / "ubtr_ocs_handoff",
    )
    orchestration_artifact = orchestration_capture["orchestration_artifact"]

    ocs_proposal = _ocs_proposal_artifact(
        scaffold_id=scaffold_id,
        semantic_artifact=semantic_artifact,
        orchestration_artifact=orchestration_artifact,
        created_at=created_at,
    )
    _persist_step(replay_path, 3, REPLAY_STEPS[3], ocs_proposal)

    governance_checkpoint = _governance_checkpoint_artifact(
        scaffold_id=scaffold_id,
        input_artifact=input_artifact,
        semantic_artifact=semantic_artifact,
        ocs_proposal=ocs_proposal,
        created_at=created_at,
    )
    _persist_step(replay_path, 4, REPLAY_STEPS[4], governance_checkpoint)

    evidence = _evidence_references(
        input_artifact=input_artifact,
        semantic_artifact=semantic_artifact,
        ocs_proposal=ocs_proposal,
        governance_checkpoint=governance_checkpoint,
    )
    lineage = _replay_lineage(
        input_artifact=input_artifact,
        translation_capture=translation_capture,
        semantic_capture=semantic_capture,
        orchestration_capture=orchestration_capture,
        ocs_proposal=ocs_proposal,
        governance_checkpoint=governance_checkpoint,
    )
    confirmation_capture = create_shared_confirmation_model(
        confirmation_id=f"{scaffold_id}:UHCL-CONFIRMATION",
        source_component=SOURCE_COMPONENT_OCS,
        target_human_context="ACLI_OPERATOR",
        communication_level=communication_level,
        confirmation_prompt="Review the governed development proposal and choose confirm, modify, reject, clarify, or continue.",
        required_human_action="choose a canonical UHCL response class",
        evidence_references=evidence,
        source_evidence_bindings=_source_evidence_bindings(semantic_artifact, ocs_proposal, governance_checkpoint),
        csa_reference=semantic_artifact["semantic_artifact_id"],
        csa_hash=semantic_artifact["artifact_hash"],
        ocs_reference=ocs_proposal["proposal_id"],
        ocs_hash=ocs_proposal["artifact_hash"],
        replay_lineage=lineage,
        rollback_reference=f"{scaffold_id}:ROLLBACK-ADVISORY-ONLY",
        created_at=created_at,
        replay_dir=replay_path / "uhcl_confirmation",
    )
    communication_capture = create_ubtr_human_communication_artifact(
        communication_id=f"{scaffold_id}:UHCL-COMMUNICATION",
        source_component=SOURCE_COMPONENT_OCS,
        target_human_context="ACLI_OPERATOR",
        communication_domain=DOMAIN_RECOMMENDATION,
        communication_level=communication_level,
        created_at=created_at,
        replay_dir=replay_path / "uhcl_communication",
        required_human_action="review advisory proposal; no execution will occur from this scaffold",
        replay_lineage=lineage,
        rollback_reference=f"{scaffold_id}:ROLLBACK-ADVISORY-ONLY",
        csa_reference=semantic_artifact["semantic_artifact_id"],
        csa_hash=semantic_artifact["artifact_hash"],
        ocs_reference=ocs_proposal["proposal_id"],
        ocs_hash=ocs_proposal["artifact_hash"],
        explanation_section=_communication_section(
            "The scaffold translated the natural-language request through UBTR, produced a CSA structured intent, and prepared an OCS advisory proposal.",
            ocs_proposal,
        ),
        recommendation_section=_communication_section(ocs_proposal["recommended_next_step"], ocs_proposal),
        confirmation_section=confirmation_capture["confirmation_section"],
        risks_section={
            "summary": "Execution remains blocked until approval, authorization, worker readiness, and mutation gates are certified.",
            "risks": deepcopy(ocs_proposal["risks"]),
        },
        assumptions_section={
            "summary": "Provider and Worker execution are advisory-only in G4-02.",
            "assumptions": deepcopy(ocs_proposal["assumptions"]),
        },
        non_authority_notices=[
            "UHCL communication is informational and does not grant execution authority.",
            "ACLI rendering is presentation-only.",
            "Provider invocation, worker execution, deployment, and repository mutation are disabled.",
        ],
    )
    communication_artifact = communication_capture["communication_artifact"]
    _persist_step(replay_path, 5, REPLAY_STEPS[5], _lineage_projection("UHCL", communication_artifact, communication_capture))

    render_capture = render_uhcl_artifact_for_acli(
        render_id=f"{scaffold_id}:ACLI-RENDER",
        uhcl_artifact=communication_artifact,
        communication_level=communication_level,
        rendered_at=created_at,
        replay_dir=replay_path / "acli_adapter",
    )
    render_artifact = render_capture["artifact"]
    _persist_step(replay_path, 6, REPLAY_STEPS[6], _lineage_projection("ACLI_RENDER", render_artifact, render_capture))

    response_capture = capture_uhcl_human_response(
        response_id=f"{scaffold_id}:HUMAN-RESPONSE",
        rendered_artifact=render_artifact,
        operator_input=operator_response,
        captured_at=created_at,
        replay_dir=replay_path / "acli_adapter",
    )
    response_artifact = response_capture["artifact"]
    _persist_step(replay_path, 7, REPLAY_STEPS[7], _lineage_projection("HUMAN_RESPONSE", response_artifact, response_capture))

    execution_intent = _execution_intent_artifact(
        scaffold_id=scaffold_id,
        semantic_artifact=semantic_artifact,
        ocs_proposal=ocs_proposal,
        governance_checkpoint=governance_checkpoint,
        response_artifact=response_artifact,
        created_at=created_at,
    )
    _persist_step(replay_path, 8, REPLAY_STEPS[8], execution_intent)

    summary = _summary_artifact(
        scaffold_id=scaffold_id,
        input_artifact=input_artifact,
        translation_artifact=translation_artifact,
        semantic_artifact=semantic_artifact,
        orchestration_artifact=orchestration_artifact,
        ocs_proposal=ocs_proposal,
        governance_checkpoint=governance_checkpoint,
        confirmation_artifact=confirmation_capture["shared_confirmation_artifact"],
        communication_artifact=communication_artifact,
        render_artifact=render_artifact,
        response_artifact=response_artifact,
        execution_intent=execution_intent,
        replay_reference=str(replay_path),
        created_at=created_at,
    )
    _persist_step(replay_path, 9, REPLAY_STEPS[9], summary)
    return _capture(summary, replay_path)


def reconstruct_g4_governed_development_loop_scaffold_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct G4 governed development loop scaffold replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("G4 development loop scaffold replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = _require_mapping(wrapper.get("artifact"), "artifact")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    summary = wrappers[-1]["artifact"]
    _validate_no_authority(summary)

    translation_replay = load_json(
        replay_path / "ubtr_translation" / "000_human_to_governance_translation_recorded.json"
    )
    csa_replay = reconstruct_canonical_semantic_artifact_replay(replay_path / "csa_structured_intent")
    ubtr_ocs_replay = reconstruct_ubtr_semantic_cognition_orchestration_replay(replay_path / "ubtr_ocs_handoff")
    confirmation_replay = reconstruct_shared_confirmation_replay(replay_path / "uhcl_confirmation")
    uhcl_replay = reconstruct_ubtr_human_communication_replay(replay_path / "uhcl_communication")
    acli_replay = reconstruct_acli_uhcl_adapter_replay(replay_path / "acli_adapter")

    if translation_replay["artifact"]["artifact_hash"] != summary["ubtr_translation_hash"]:
        raise FailClosedRuntimeError("G4 development loop scaffold translation hash mismatch")
    if csa_replay["semantic_artifact_hash"] != summary["csa_structured_intent_hash"]:
        raise FailClosedRuntimeError("G4 development loop scaffold CSA hash mismatch")
    if ubtr_ocs_replay["orchestration_artifact"]["artifact_hash"] != summary["ubtr_ocs_handoff_hash"]:
        raise FailClosedRuntimeError("G4 development loop scaffold UBTR/OCS hash mismatch")
    if confirmation_replay["shared_confirmation_artifact_hash"] != summary["uhcl_confirmation_hash"]:
        raise FailClosedRuntimeError("G4 development loop scaffold confirmation hash mismatch")
    if uhcl_replay["communication_artifact_hash"] != summary["uhcl_communication_hash"]:
        raise FailClosedRuntimeError("G4 development loop scaffold UHCL hash mismatch")
    if acli_replay["render_count"] != 1 or acli_replay["response_count"] != 1:
        raise FailClosedRuntimeError("G4 development loop scaffold ACLI replay mismatch")

    return {
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "scaffold_id": summary["scaffold_id"],
        "scaffold_status": summary["scaffold_status"],
        "replay_artifact_count": len(wrappers),
        "sub_replay_artifact_count": (
            1
            + int(csa_replay.get("replay_visible", False))
            + int(ubtr_ocs_replay.get("replay_visible", False))
            + int(confirmation_replay.get("replay_visible", False))
            + int(uhcl_replay.get("replay_visible", False))
            + acli_replay["artifact_count"]
        ),
        "integrated_components": deepcopy(summary["integrated_components"]),
        "governance_checkpoint_status": summary["governance_checkpoint_status"],
        "canonical_response_class": summary["canonical_response_class"],
        "execution_intent_status": summary["execution_intent_status"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _acli_input_artifact(
    *,
    scaffold_id: str,
    human_intent: str,
    session_context: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_INPUT_ARTIFACT_V1,
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "input_id": f"{_require_string(scaffold_id, 'scaffold_id')}:ACLI-INPUT",
        "adapter": "ACLI",
        "adapter_scope": "INPUT_CAPTURE_ONLY",
        "human_intent": _require_string(human_intent, "human_intent"),
        "human_intent_hash": replay_hash(_require_string(human_intent, "human_intent")),
        "session_context": deepcopy(session_context),
        "created_at": _require_string(created_at, "created_at"),
        "semantic_translation_performed": False,
        "communication_generated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ocs_proposal_artifact(
    *,
    scaffold_id: str,
    semantic_artifact: dict[str, Any],
    orchestration_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    execution_requested = semantic_artifact["execution_intent"]["execution_requested"] is True
    artifact = {
        "artifact_type": OCS_PROPOSAL_ARTIFACT_V1,
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "proposal_id": f"{_require_string(scaffold_id, 'scaffold_id')}:OCS-PROPOSAL",
        "ocs_owner": "OCS",
        "source_semantic_artifact_id": semantic_artifact["semantic_artifact_id"],
        "source_semantic_hash": semantic_artifact["artifact_hash"],
        "ubtr_ocs_handoff_hash": orchestration_artifact["artifact_hash"],
        "proposal_summary": semantic_artifact["human_readable_projection"]["summary"],
        "recommended_next_step": (
            "Collect explicit approval, authorization readiness, worker readiness, and mutation boundary evidence before execution."
            if execution_requested
            else "Continue advisory review; no execution path is requested by this scaffold."
        ),
        "alternatives": [
            "Ask the operator for clarification.",
            "Record advisory proposal evidence only.",
            "Prepare a future governed execution request after approval and authorization are certified.",
        ],
        "assumptions": [
            "ACLI is an adapter only.",
            "Provider Services and Worker Services remain advisory-only in this scaffold.",
            "Repository mutation is unavailable in G4-02.",
        ],
        "risks": [
            "Execution before approval would violate governance boundaries.",
            "Worker execution before Worker Services activation would duplicate platform ownership.",
            "Repository mutation before authorization would break replay-safe governance.",
        ],
        "proposal_only": True,
        "provider_services_status": "ADVISORY_ONLY",
        "worker_services_status": "ADVISORY_ONLY",
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _governance_checkpoint_artifact(
    *,
    scaffold_id: str,
    input_artifact: dict[str, Any],
    semantic_artifact: dict[str, Any],
    ocs_proposal: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    missing = [
        "approval evidence",
        "authorization evidence",
        "worker readiness evidence",
        "repository mutation certification",
    ]
    artifact = {
        "artifact_type": GOVERNANCE_CHECKPOINT_ARTIFACT_V1,
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "checkpoint_id": f"{_require_string(scaffold_id, 'scaffold_id')}:GOVERNANCE-CHECKPOINT",
        "input_hash": input_artifact["artifact_hash"],
        "semantic_hash": semantic_artifact["artifact_hash"],
        "proposal_hash": ocs_proposal["artifact_hash"],
        "checkpoint_status": ADVISORY_ONLY_CHECKPOINT_PASSED,
        "missing_execution_prerequisites": missing,
        "provider_boundary_preserved": True,
        "worker_boundary_preserved": True,
        "approval_boundary_preserved": True,
        "authorization_boundary_preserved": True,
        "mutation_boundary_preserved": True,
        "replay_boundary_preserved": True,
        "semantic_owner": "UBTR",
        "structured_intent_owner": "CSA",
        "proposal_owner": "OCS",
        "communication_owner": "UHCL",
        "adapter_owner": "ACLI",
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execution_intent_artifact(
    *,
    scaffold_id: str,
    semantic_artifact: dict[str, Any],
    ocs_proposal: dict[str, Any],
    governance_checkpoint: dict[str, Any],
    response_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_INTENT_ARTIFACT_V1,
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "execution_intent_id": f"{_require_string(scaffold_id, 'scaffold_id')}:ADVISORY-EXECUTION-INTENT",
        "semantic_hash": semantic_artifact["artifact_hash"],
        "proposal_hash": ocs_proposal["artifact_hash"],
        "governance_checkpoint_hash": governance_checkpoint["artifact_hash"],
        "human_response_hash": response_artifact["artifact_hash"],
        "canonical_response_class": response_artifact["canonical_response_class"],
        "execution_intent_status": BLOCKED_PENDING_GOVERNANCE,
        "block_reason": "G4-02 scaffold records execution intent evidence only; execution requires separate approval, authorization, Worker Services activation, and mutation certification.",
        "required_before_execution": deepcopy(governance_checkpoint["missing_execution_prerequisites"]),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _summary_artifact(
    *,
    scaffold_id: str,
    input_artifact: dict[str, Any],
    translation_artifact: dict[str, Any],
    semantic_artifact: dict[str, Any],
    orchestration_artifact: dict[str, Any],
    ocs_proposal: dict[str, Any],
    governance_checkpoint: dict[str, Any],
    confirmation_artifact: dict[str, Any],
    communication_artifact: dict[str, Any],
    render_artifact: dict[str, Any],
    response_artifact: dict[str, Any],
    execution_intent: dict[str, Any],
    replay_reference: str,
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": SCAFFOLD_SUMMARY_ARTIFACT_V1,
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "scaffold_id": _require_string(scaffold_id, "scaffold_id"),
        "scaffold_status": SCAFFOLD_RECORDED,
        "integrated_components": ["ACLI", "UBTR", "CSA", "OCS", "GOVERNANCE", "UHCL", "REPLAY"],
        "acli_input_hash": input_artifact["artifact_hash"],
        "ubtr_translation_hash": translation_artifact["artifact_hash"],
        "csa_structured_intent_hash": semantic_artifact["artifact_hash"],
        "ubtr_ocs_handoff_hash": orchestration_artifact["artifact_hash"],
        "ocs_proposal_hash": ocs_proposal["artifact_hash"],
        "governance_checkpoint_hash": governance_checkpoint["artifact_hash"],
        "governance_checkpoint_status": governance_checkpoint["checkpoint_status"],
        "uhcl_confirmation_hash": confirmation_artifact["artifact_hash"],
        "uhcl_communication_hash": communication_artifact["artifact_hash"],
        "acli_render_hash": render_artifact["artifact_hash"],
        "human_response_hash": response_artifact["artifact_hash"],
        "canonical_response_class": response_artifact["canonical_response_class"],
        "execution_intent_hash": execution_intent["artifact_hash"],
        "execution_intent_status": execution_intent["execution_intent_status"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "authority_granted": False,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(summary: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "scaffold_id": summary["scaffold_id"],
        "scaffold_status": summary["scaffold_status"],
        "summary_artifact": deepcopy(summary),
        "summary_hash": summary["artifact_hash"],
        "replay_reference": str(replay_path),
        "integrated_components": deepcopy(summary["integrated_components"]),
        "governance_checkpoint_status": summary["governance_checkpoint_status"],
        "canonical_response_class": summary["canonical_response_class"],
        "execution_intent_status": summary["execution_intent_status"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }


def _lineage_projection(component: str, artifact: dict[str, Any], capture: dict[str, Any]) -> dict[str, Any]:
    projection = {
        "artifact_type": f"G4_{component}_LINEAGE_PROJECTION_V1",
        "runtime_version": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "component": component,
        "source_artifact_type": artifact["artifact_type"],
        "source_artifact_hash": artifact["artifact_hash"],
        "capture_keys": sorted(capture.keys()),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "replay_visible": True,
    }
    projection["artifact_hash"] = replay_hash(projection)
    return projection


def _evidence_references(
    *,
    input_artifact: dict[str, Any],
    semantic_artifact: dict[str, Any],
    ocs_proposal: dict[str, Any],
    governance_checkpoint: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_reference": input_artifact["input_id"],
            "evidence_hash": input_artifact["artifact_hash"],
            "evidence_role": "ACLI_INPUT",
        },
        {
            "evidence_reference": semantic_artifact["semantic_artifact_id"],
            "evidence_hash": semantic_artifact["artifact_hash"],
            "evidence_role": "CSA_STRUCTURED_INTENT",
        },
        {
            "evidence_reference": ocs_proposal["proposal_id"],
            "evidence_hash": ocs_proposal["artifact_hash"],
            "evidence_role": "OCS_PROPOSAL",
        },
        {
            "evidence_reference": governance_checkpoint["checkpoint_id"],
            "evidence_hash": governance_checkpoint["artifact_hash"],
            "evidence_role": "GOVERNANCE_CHECKPOINT",
        },
    ]


def _source_evidence_bindings(
    semantic_artifact: dict[str, Any],
    ocs_proposal: dict[str, Any],
    governance_checkpoint: dict[str, Any],
) -> dict[str, Any]:
    return {
        "specific_sources": {
            "csa": {
                "reference": semantic_artifact["semantic_artifact_id"],
                "hash": semantic_artifact["artifact_hash"],
            },
            "ocs": {
                "reference": ocs_proposal["proposal_id"],
                "hash": ocs_proposal["artifact_hash"],
            },
            "governance": {
                "reference": governance_checkpoint["checkpoint_id"],
                "hash": governance_checkpoint["artifact_hash"],
            },
        }
    }


def _replay_lineage(
    *,
    input_artifact: dict[str, Any],
    translation_capture: dict[str, Any],
    semantic_capture: dict[str, Any],
    orchestration_capture: dict[str, Any],
    ocs_proposal: dict[str, Any],
    governance_checkpoint: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {"replay_reference": input_artifact["input_id"], "replay_hash": input_artifact["artifact_hash"]},
        {
            "replay_reference": translation_capture["translation_replay_reference"],
            "replay_hash": translation_capture["translation_artifact"]["artifact_hash"],
        },
        {
            "replay_reference": semantic_capture["semantic_replay_reference"],
            "replay_hash": semantic_capture["semantic_artifact_hash"],
        },
        {
            "replay_reference": orchestration_capture["orchestration_replay_reference"],
            "replay_hash": orchestration_capture["orchestration_artifact"]["artifact_hash"],
        },
        {"replay_reference": ocs_proposal["proposal_id"], "replay_hash": ocs_proposal["artifact_hash"]},
        {
            "replay_reference": governance_checkpoint["checkpoint_id"],
            "replay_hash": governance_checkpoint["artifact_hash"],
        },
    ]


def _communication_section(summary: str, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": _require_string(summary, "summary"),
        "source_artifact_type": source["artifact_type"],
        "source_artifact_hash": source["artifact_hash"],
        "non_authoritative": True,
    }


def _persist_step(replay_path: Path, replay_index: int, replay_step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": replay_index,
        "replay_step": replay_step,
        "event_type": G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{replay_index:03d}_{replay_step}.json", wrapper)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("G4 development loop scaffold replay already exists")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected = deepcopy(wrapper)
    actual = expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4 development loop scaffold replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("G4 development loop scaffold artifact hash mismatch")


def _validate_no_authority(artifact: dict[str, Any]) -> None:
    for field in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
        "authority_granted",
    ):
        if artifact.get(field) is not False:
            raise FailClosedRuntimeError(f"G4 development loop scaffold cannot set {field}")


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
