"""Compatibility wrapper wiring into canonical UHCL communication artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.ubtr_human_communication_model_runtime import (
    BINDING_PRODUCT1_AUDIT_PACKET_SUMMARY,
    BINDING_PRODUCT1_DECISION_PACKET_SUMMARY,
    BINDING_PRODUCT1_WORKFLOW_SUMMARY,
    BINDING_PROVIDER_COGNITION_SUMMARY,
    BINDING_PROVIDER_PROVENANCE,
    BINDING_WORKER_EXECUTION_SUMMARY,
    BINDING_WORKER_LIFECYCLE_SUMMARY,
    LEVEL_STANDARD,
    SECTION_TYPE_EXPLANATION,
    SECTION_TYPE_GUIDANCE,
    SECTION_TYPE_TRANSPARENCY,
    SOURCE_COMPONENT_AUTHORIZATION,
    SOURCE_COMPONENT_GOVERNANCE,
    SOURCE_COMPONENT_PROVIDER,
    SOURCE_COMPONENT_REPLAY,
    SOURCE_COMPONENT_UBTR,
    create_communication_binding,
    create_recovery_guidance_model,
    create_shared_confirmation_model,
    create_typed_communication_section,
)


PLATFORM_COMMUNICATION_WRAPPER_WIRING_VERSION = (
    "G3_04_PHASE_8B_PLATFORM_COMMUNICATION_WRAPPER_WIRING_V1"
)

DEFAULT_NON_AUTHORITY_NOTICES = [
    "This compatibility wrapper consumes UHCL communication artifacts only.",
    "The wrapper does not create approval, authorization, execution, worker, provider, mutation, or replay authority.",
]


def wire_explanation_wrapper_to_uhcl(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    summary_content: dict[str, Any],
    evidence_references: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
    source_component: str = SOURCE_COMPONENT_UBTR,
    replay_lineage: list[dict[str, Any]] | None = None,
    rollback_reference: str | None = None,
) -> dict[str, Any]:
    """Create a UHCL explanation section for a legacy explanation wrapper."""

    replay_path = Path(replay_dir)
    evidence = _normalize_evidence(evidence_references, wrapper_surface, summary_content)
    capture = create_typed_communication_section(
        section_id=f"{_stable_id(wrapper_id)}:UHCL-EXPLANATION-WIRING",
        section_type=SECTION_TYPE_EXPLANATION,
        communication_level=LEVEL_STANDARD,
        structured_content={
            "wrapper_surface": _require_string(wrapper_surface, "wrapper_surface"),
            "legacy_contract_preserved": True,
            "summary_content": deepcopy(summary_content),
            "communication_semantics_source": "UHCL",
            "new_communication_semantics_introduced": False,
        },
        evidence_references=evidence,
        created_at=created_at,
        replay_dir=replay_path,
        source_component=source_component,
        replay_lineage=replay_lineage,
        rollback_reference=rollback_reference,
        non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
    )
    return _wiring_summary(
        wrapper_surface=wrapper_surface,
        wrapper_id=wrapper_id,
        uhcl_capture=capture,
        uhcl_artifact_key="typed_section_artifact",
        replay_dir=replay_path,
    )


def wire_transparency_wrapper_to_uhcl(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    transparency_content: dict[str, Any],
    evidence_references: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
    source_component: str = SOURCE_COMPONENT_GOVERNANCE,
    replay_lineage: list[dict[str, Any]] | None = None,
    rollback_reference: str | None = None,
) -> dict[str, Any]:
    """Create a UHCL transparency section for legacy wording wrappers."""

    replay_path = Path(replay_dir)
    evidence = _normalize_evidence(evidence_references, wrapper_surface, transparency_content)
    capture = create_typed_communication_section(
        section_id=f"{_stable_id(wrapper_id)}:UHCL-TRANSPARENCY-WIRING",
        section_type=SECTION_TYPE_TRANSPARENCY,
        communication_level=LEVEL_STANDARD,
        structured_content={
            "wrapper_surface": _require_string(wrapper_surface, "wrapper_surface"),
            "legacy_contract_preserved": True,
            "transparency_content": deepcopy(transparency_content),
            "communication_semantics_source": "UHCL",
            "new_communication_semantics_introduced": False,
        },
        evidence_references=evidence,
        created_at=created_at,
        replay_dir=replay_path,
        source_component=source_component,
        replay_lineage=replay_lineage,
        rollback_reference=rollback_reference,
        non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
    )
    return _wiring_summary(
        wrapper_surface=wrapper_surface,
        wrapper_id=wrapper_id,
        uhcl_capture=capture,
        uhcl_artifact_key="typed_section_artifact",
        replay_dir=replay_path,
    )


def wire_confirmation_wrapper_to_uhcl(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    confirmation_prompt: str,
    required_human_action: str,
    evidence_references: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
    source_component: str = SOURCE_COMPONENT_GOVERNANCE,
    replay_lineage: list[dict[str, Any]] | None = None,
    rollback_reference: str | None = None,
    approval_reference: str | None = None,
    approval_hash: str | None = None,
    authorization_reference: str | None = None,
    authorization_hash: str | None = None,
) -> dict[str, Any]:
    """Create a UHCL shared confirmation artifact for approval/confirmation wrappers."""

    replay_path = Path(replay_dir)
    evidence_seed = {
        "confirmation_prompt": confirmation_prompt,
        "required_human_action": required_human_action,
    }
    capture = create_shared_confirmation_model(
        confirmation_id=f"{_stable_id(wrapper_id)}:UHCL-CONFIRMATION-WIRING",
        source_component=source_component,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        confirmation_prompt=confirmation_prompt,
        required_human_action=required_human_action,
        evidence_references=_normalize_evidence(evidence_references, wrapper_surface, evidence_seed),
        created_at=created_at,
        replay_dir=replay_path,
        approval_reference=approval_reference,
        approval_hash=approval_hash,
        authorization_reference=authorization_reference,
        authorization_hash=authorization_hash,
        replay_lineage=replay_lineage,
        rollback_reference=rollback_reference,
        non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
    )
    return _wiring_summary(
        wrapper_surface=wrapper_surface,
        wrapper_id=wrapper_id,
        uhcl_capture=capture,
        uhcl_artifact_key="shared_confirmation_artifact",
        replay_dir=replay_path,
    )


def wire_authorization_wrapper_to_uhcl(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    readiness_status: str,
    cannot_continue_reason: str | None,
    missing_prerequisites: list[dict[str, Any]] | None,
    summary_content: dict[str, Any],
    evidence_references: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
    replay_lineage: list[dict[str, Any]] | None = None,
    rollback_reference: str | None = None,
) -> dict[str, Any]:
    """Wire authorization readiness wording to UHCL without creating authority."""

    replay_path = Path(replay_dir)
    if missing_prerequisites:
        actions = [
            {
                "action_id": "PROVIDE_REQUIRED_APPROVAL_EVIDENCE",
                "description": "Provide the missing approval evidence.",
                "authority_required": "HUMAN_AUTHORITY",
                "automatic": False,
            },
            {
                "action_id": "REVISE_OR_REJECT_PROPOSAL",
                "description": "Revise, clarify, or reject the proposal before authorization.",
                "authority_required": "HUMAN_AUTHORITY",
                "automatic": False,
            },
        ]
        capture = create_recovery_guidance_model(
            recovery_id=f"{_stable_id(wrapper_id)}:UHCL-AUTHORIZATION-RECOVERY-WIRING",
            source_component=SOURCE_COMPONENT_AUTHORIZATION,
            target_human_context="ACLI_OPERATOR",
            communication_level=LEVEL_STANDARD,
            blocked_operation="ACLI authorization readiness",
            cannot_continue_reason=cannot_continue_reason or "Authorization readiness preconditions are not satisfied.",
            missing_prerequisites=missing_prerequisites,
            available_recovery_actions=actions,
            recommended_next_action={
                "action_id": actions[0]["action_id"],
                "description": actions[0]["description"],
                "reason": "UHCL preserves the fail-closed recovery path without creating authorization.",
                "automatic": False,
            },
            evidence_references=_normalize_evidence(evidence_references, wrapper_surface, summary_content),
            created_at=created_at,
            replay_dir=replay_path,
            replay_lineage=replay_lineage,
            rollback_reference=rollback_reference,
            non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
        )
        return _wiring_summary(
            wrapper_surface=wrapper_surface,
            wrapper_id=wrapper_id,
            uhcl_capture=capture,
            uhcl_artifact_key="recovery_guidance_artifact",
            replay_dir=replay_path,
        )

    capture = create_typed_communication_section(
        section_id=f"{_stable_id(wrapper_id)}:UHCL-AUTHORIZATION-GUIDANCE-WIRING",
        section_type=SECTION_TYPE_GUIDANCE,
        communication_level=LEVEL_STANDARD,
        structured_content={
            "wrapper_surface": _require_string(wrapper_surface, "wrapper_surface"),
            "readiness_status": _require_string(readiness_status, "readiness_status"),
            "summary_content": deepcopy(summary_content),
            "authorization_created": False,
            "execution_authorized": False,
            "communication_semantics_source": "UHCL",
            "new_communication_semantics_introduced": False,
        },
        evidence_references=_normalize_evidence(evidence_references, wrapper_surface, summary_content),
        created_at=created_at,
        replay_dir=replay_path,
        source_component=SOURCE_COMPONENT_AUTHORIZATION,
        replay_lineage=replay_lineage,
        rollback_reference=rollback_reference,
        non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
    )
    return _wiring_summary(
        wrapper_surface=wrapper_surface,
        wrapper_id=wrapper_id,
        uhcl_capture=capture,
        uhcl_artifact_key="typed_section_artifact",
        replay_dir=replay_path,
    )


def wire_binding_wrapper_to_uhcl(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    binding_type: str,
    summary_content: dict[str, Any],
    evidence_references: list[dict[str, Any]] | None,
    created_at: str,
    replay_dir: str | Path,
    replay_lineage: list[dict[str, Any]] | None = None,
    rollback_reference: str | None = None,
) -> dict[str, Any]:
    """Create a UHCL Provider/Worker/Product binding for summary wrappers."""

    replay_path = Path(replay_dir)
    capture = create_communication_binding(
        binding_id=f"{_stable_id(wrapper_id)}:UHCL-BINDING-WIRING",
        binding_type=binding_type,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        summary_content={
            "wrapper_surface": _require_string(wrapper_surface, "wrapper_surface"),
            "legacy_contract_preserved": True,
            "summary_content": deepcopy(summary_content),
            "communication_semantics_source": "UHCL",
            "new_communication_semantics_introduced": False,
        },
        evidence_references=_normalize_evidence(evidence_references, wrapper_surface, summary_content),
        created_at=created_at,
        replay_dir=replay_path,
        replay_lineage=replay_lineage,
        rollback_reference=rollback_reference,
        non_authority_notices=DEFAULT_NON_AUTHORITY_NOTICES,
    )
    return _wiring_summary(
        wrapper_surface=wrapper_surface,
        wrapper_id=wrapper_id,
        uhcl_capture=capture,
        uhcl_artifact_key="communication_binding_artifact",
        replay_dir=replay_path,
    )


def provider_cognition_summary_binding_type() -> str:
    return BINDING_PROVIDER_COGNITION_SUMMARY


def provider_provenance_binding_type() -> str:
    return BINDING_PROVIDER_PROVENANCE


def worker_execution_summary_binding_type() -> str:
    return BINDING_WORKER_EXECUTION_SUMMARY


def worker_lifecycle_summary_binding_type() -> str:
    return BINDING_WORKER_LIFECYCLE_SUMMARY


def product1_workflow_summary_binding_type() -> str:
    return BINDING_PRODUCT1_WORKFLOW_SUMMARY


def product1_decision_packet_summary_binding_type() -> str:
    return BINDING_PRODUCT1_DECISION_PACKET_SUMMARY


def product1_audit_packet_summary_binding_type() -> str:
    return BINDING_PRODUCT1_AUDIT_PACKET_SUMMARY


def replay_source_component() -> str:
    return SOURCE_COMPONENT_REPLAY


def provider_source_component() -> str:
    return SOURCE_COMPONENT_PROVIDER


def _wiring_summary(
    *,
    wrapper_surface: str,
    wrapper_id: str,
    uhcl_capture: dict[str, Any],
    uhcl_artifact_key: str,
    replay_dir: Path,
) -> dict[str, Any]:
    artifact = uhcl_capture[uhcl_artifact_key]
    return {
        "wiring_version": PLATFORM_COMMUNICATION_WRAPPER_WIRING_VERSION,
        "wrapper_surface": _require_string(wrapper_surface, "wrapper_surface"),
        "wrapper_id": _require_string(wrapper_id, "wrapper_id"),
        "uhcl_consumed": True,
        "uhcl_artifact_type": artifact["artifact_type"],
        "uhcl_artifact_hash": artifact["artifact_hash"],
        "uhcl_replay_reference": str(replay_dir),
        "legacy_contract_preserved": True,
        "replay_compatibility_preserved": True,
        "rollback_capability_preserved": True,
        "deterministic": True,
        "new_communication_semantics_introduced": False,
        "provider_invoked_by_wiring": False,
        "worker_invoked_by_wiring": False,
        "approval_created_by_wiring": False,
        "authorization_created_by_wiring": False,
        "execution_authorized_by_wiring": False,
        "repository_mutated_by_wiring": False,
        "interface_neutral": True,
        "non_authority_notices": list(DEFAULT_NON_AUTHORITY_NOTICES),
    }


def _normalize_evidence(
    evidence_references: list[dict[str, Any]] | None,
    wrapper_surface: str,
    seed: Any,
) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for index, item in enumerate(evidence_references or []):
        if not isinstance(item, dict):
            continue
        reference = item.get("evidence_reference") or item.get("reference") or item.get("id")
        evidence_hash = item.get("evidence_hash") or item.get("hash") or item.get("artifact_hash")
        if not isinstance(reference, str) or not reference.strip():
            reference = f"{wrapper_surface}:EVIDENCE:{index}"
        evidence.append(
            {
                "evidence_reference": reference,
                "evidence_hash": _stable_hash(evidence_hash, {"reference": reference, "seed": seed}),
            }
        )
    if evidence:
        return evidence
    return [
        {
            "evidence_reference": f"{wrapper_surface}:COMPATIBILITY-WRAPPER",
            "evidence_hash": replay_hash({"wrapper_surface": wrapper_surface, "seed": seed}),
        }
    ]


def _stable_hash(value: Any, fallback_seed: Any) -> str:
    if isinstance(value, str) and value.startswith("sha256:"):
        return value
    return replay_hash({"value": value, "fallback_seed": fallback_seed})


def _stable_id(value: str) -> str:
    return _require_string(value, "wrapper_id").replace("/", ":")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value
