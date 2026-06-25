"""Deterministic human-friendly ACLI explanation layer."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "HUMAN_FRIENDLY_ACLI_EXPLANATION_IMPLEMENTATION_V1"
FINAL_CLASSIFICATION = "CERTIFIED_HUMAN_FRIENDLY_ACLI_EXPLANATION_LAYER"

ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1 = "ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1"

REPLAY_STEP = "acli_human_friendly_explanation_recorded"


def create_acli_human_friendly_explanation(
    *,
    explanation_id: str,
    turn_id: str,
    prompt_id: str,
    human_prompt: str,
    workflow_id: str,
    routing_visibility_artifact: dict[str, Any],
    universal_intake_artifact: dict[str, Any],
    proposal_capture: dict[str, Any] | None,
    replay_dir: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Create and persist a deterministic, non-authoritative operator explanation."""

    replay_path = Path(replay_dir)
    routing = _require_artifact(routing_visibility_artifact, "routing_visibility_artifact")
    intake = _require_artifact(universal_intake_artifact, "universal_intake_artifact")
    proposal = deepcopy(proposal_capture) if isinstance(proposal_capture, dict) else None
    sections = _build_sections(
        human_prompt=human_prompt,
        workflow_id=workflow_id,
        routing_visibility_artifact=routing,
        universal_intake_artifact=intake,
        proposal_capture=proposal,
        explanation_replay_reference=str(replay_path),
    )
    rendered = render_acli_human_friendly_explanation_sections(sections)
    transparency = _deterministic_transparency_artifact()
    rendered_operator_view = _append_explanation_transparency(
        rendered,
        transparency,
    )
    artifact = {
        "artifact_type": ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "explanation_id": _require_string(explanation_id, "explanation_id"),
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "routing_visibility_reference": _require_string(
            routing.get("routing_visibility_id"),
            "routing_visibility_reference",
        ),
        "routing_visibility_hash": _require_string(routing.get("artifact_hash"), "routing_visibility_hash"),
        "universal_intake_reference": _require_string(
            intake.get("universal_intake_id"),
            "universal_intake_reference",
        ),
        "universal_intake_hash": _require_string(intake.get("artifact_hash"), "universal_intake_hash"),
        "proposal_reference": _proposal_reference(proposal),
        "proposal_hash": _proposal_hash(proposal),
        "sections": sections,
        "rendered_explanation": rendered,
        "rendered_explanation_hash": replay_hash(rendered),
        "explanation_transparency_artifact": transparency,
        "authoritative_state": "AiGOL Governance",
        "deterministic_explanation": rendered,
        "provider_request": None,
        "provider_response": None,
        "provider_name": None,
        "provider_role": None,
        "provider_tier": None,
        "provider_status": "DISABLED_BY_CONFIGURATION",
        "provider_confidence": None,
        "explanation_confidence": "GOVERNANCE_ONLY",
        "explanation_completeness": "COMPLETE",
        "fallback_reason": None,
        "render_mode": "DETERMINISTIC_ONLY",
        "escalation_level": "TIER_1",
        "rendered_operator_view": rendered_operator_view,
        "rendered_operator_view_hash": replay_hash(rendered_operator_view),
        "explanation_accepted": None,
        "explanation_modified": None,
        "operator_confusion_detected": None,
        "clarification_requested": None,
        "operator_satisfaction": None,
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "visibility_only": True,
        "authority_granted": False,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_granted": False,
        "repository_mutation_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "human_friendly_explanation_artifact": deepcopy(artifact),
        "human_friendly_explanation_replay_reference": str(replay_path),
        "operator_explanation": rendered,
        "operator_explanation_with_transparency": rendered_operator_view,
        "replay_visible": True,
        "visibility_only": True,
    }


def reconstruct_acli_human_friendly_explanation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify human-friendly explanation replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("ACLI explanation replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI explanation artifact must be a JSON object")
    _verify_artifact_hash(artifact)
    if artifact.get("artifact_type") != ACLI_HUMAN_FRIENDLY_EXPLANATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI explanation artifact type mismatch")
    if artifact.get("rendered_explanation_hash") != replay_hash(artifact.get("rendered_explanation")):
        raise FailClosedRuntimeError("ACLI explanation rendered output hash mismatch")
    if artifact.get("rendered_operator_view_hash") != replay_hash(artifact.get("rendered_operator_view")):
        raise FailClosedRuntimeError("ACLI explanation rendered operator view hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "explanation_id": artifact["explanation_id"],
        "turn_id": artifact["turn_id"],
        "prompt_id": artifact["prompt_id"],
        "workflow_id": artifact["workflow_id"],
        "sections": deepcopy(artifact["sections"]),
        "rendered_explanation": artifact["rendered_explanation"],
        "rendered_explanation_hash": artifact["rendered_explanation_hash"],
        "explanation_transparency_artifact": deepcopy(artifact["explanation_transparency_artifact"]),
        "rendered_operator_view": artifact["rendered_operator_view"],
        "rendered_operator_view_hash": artifact["rendered_operator_view_hash"],
        "explanation_confidence": artifact["explanation_confidence"],
        "explanation_completeness": artifact["explanation_completeness"],
        "render_mode": artifact["render_mode"],
        "replay_visible": True,
        "visibility_only": True,
        "authority_granted": artifact["authority_granted"],
        "provider_authority": artifact["provider_authority"],
        "approval_authority": artifact["approval_authority"],
        "execution_authority": artifact["execution_authority"],
        "worker_authority": artifact["worker_authority"],
        "replay_artifact_count": 1,
        "replay_hash": replay_hash(wrapper),
    }


def render_acli_human_friendly_explanation(capture: dict[str, Any]) -> str:
    """Render a persisted explanation capture."""

    artifact = capture.get("human_friendly_explanation_artifact")
    if not isinstance(artifact, dict):
        artifact = capture
    rendered = artifact.get("rendered_explanation")
    transparency = artifact.get("explanation_transparency_artifact")
    operator_view = artifact.get("rendered_operator_view")
    if isinstance(operator_view, str) and operator_view.strip():
        return operator_view
    if isinstance(rendered, str) and rendered.strip() and isinstance(transparency, dict):
        return _append_explanation_transparency(rendered, transparency)
    return _append_explanation_transparency(
        render_acli_human_friendly_explanation_sections(artifact.get("sections")),
        _deterministic_transparency_artifact(),
    )


def render_acli_human_friendly_explanation_sections(sections: Any) -> str:
    if not isinstance(sections, dict):
        raise FailClosedRuntimeError("ACLI explanation sections must be a JSON object")
    ordered = [
        "WHAT I UNDERSTOOD",
        "WHAT WILL HAPPEN",
        "WHAT WILL NOT HAPPEN",
        "WHAT REQUIRES YOUR APPROVAL",
        "WHAT TO TYPE NEXT",
        "REPLAY VISIBILITY",
    ]
    lines = ["================================", "HUMAN-FRIENDLY EXPLANATION"]
    for heading in ordered:
        body = sections.get(heading)
        if not isinstance(body, list) or not body:
            raise FailClosedRuntimeError(f"ACLI explanation section missing: {heading}")
        lines.extend(["", heading, ""])
        lines.extend(_render_body_lines(body))
    lines.append("================================")
    return "\n".join(lines)


def _deterministic_transparency_artifact() -> dict[str, Any]:
    return {
        "artifact_type": "ACLI_EXPLANATION_SOURCE_TRANSPARENCY_V2",
        "authoritative_state": "AiGOL Governance",
        "explanation_sources": ["Deterministic ACLI"],
        "provider_name": None,
        "provider_role": None,
        "provider_tier": None,
        "provider_status": "DISABLED_BY_CONFIGURATION",
        "provider_confidence": None,
        "explanation_role": "Advisory Only",
        "explanation_confidence": "GOVERNANCE_ONLY",
        "explanation_completeness": "COMPLETE",
        "fallback": "Not applicable",
        "fallback_reason": None,
        "replay_status": "Deterministic explanation recorded.",
        "render_mode": "DETERMINISTIC_ONLY",
        "escalation_level": "TIER_1",
        "explanation_pipeline": [
            {
                "tier": "Tier 1",
                "source": "Local deterministic explanation",
                "status": "USED",
            },
            {
                "tier": "Tier 2",
                "source": "Provider-assisted explanation",
                "status": "DISABLED_BY_CONFIGURATION",
            },
            {
                "tier": "Tier 3",
                "source": "Multi-provider comparison",
                "status": "NOT_REQUIRED",
            },
        ],
        "authoritative_items": [
            "workflow",
            "proposal",
            "approval",
            "proposal hash",
            "replay",
            "execution",
            "validation",
        ],
        "advisory_items": [
            "explanation",
            "examples",
            "natural-language interpretation",
            "simplification",
            "clarification",
        ],
        "learning_evidence": {
            "explanation_accepted": None,
            "explanation_modified": None,
            "operator_confusion_detected": None,
            "clarification_requested": None,
            "operator_satisfaction": None,
        },
    }


def _append_explanation_transparency(rendered: str, transparency: dict[str, Any]) -> str:
    return "\n".join([rendered, "", render_explanation_source_transparency(transparency)])


def render_explanation_source_transparency(transparency: dict[str, Any]) -> str:
    if not isinstance(transparency, dict):
        raise FailClosedRuntimeError("ACLI explanation transparency must be a JSON object")
    lines = [
        "====================================================",
        "EXPLANATION TRANSPARENCY",
        "",
        "Authoritative State",
        str(transparency.get("authoritative_state") or "AiGOL Governance"),
        "",
        "Explanation Source",
    ]
    for source in transparency.get("explanation_sources") or ["Deterministic ACLI"]:
        lines.append(str(source))
    provider_name = transparency.get("provider_name")
    if provider_name:
        lines.extend(["", "Provider Name", str(provider_name)])
        lines.extend(["", "Role", str(transparency.get("provider_role") or "Explanation Provider")])
        lines.extend(["", "Authority", "None"])
        lines.extend(["", "Provider Tier", str(transparency.get("provider_tier") or "Unspecified")])
    provider_status = transparency.get("provider_status")
    if provider_status:
        lines.extend(["", "Provider", _humanize_status(str(provider_status))])
    lines.extend(
        [
            "",
            "Explanation Role",
            str(transparency.get("explanation_role") or "Advisory Only"),
            "",
            "Explanation Confidence",
            _humanize_status(str(transparency.get("explanation_confidence") or "UNKNOWN")),
            "",
            "Explanation Completeness",
            _humanize_status(str(transparency.get("explanation_completeness") or "UNKNOWN")),
            "",
            "Fallback",
            str(transparency.get("fallback") or "Not used"),
        ]
    )
    fallback_reason = transparency.get("fallback_reason")
    if fallback_reason:
        lines.extend(["", "Reason", _humanize_status(str(fallback_reason))])
    lines.extend(["", "Replay Status", str(transparency.get("replay_status") or "Explanation recorded.")])
    pipeline = transparency.get("explanation_pipeline")
    if isinstance(pipeline, list) and pipeline:
        lines.extend(["", "Explanation Pipeline"])
        for step in pipeline:
            if not isinstance(step, dict):
                continue
            lines.append(
                f"{step.get('tier')}: {step.get('source')} - {_humanize_status(str(step.get('status') or 'UNKNOWN'))}"
            )
    lines.append("====================================================")
    return "\n".join(lines)


def _humanize_status(value: str) -> str:
    return value.replace("_", " ").title()


def _build_sections(
    *,
    human_prompt: str,
    workflow_id: str,
    routing_visibility_artifact: dict[str, Any],
    universal_intake_artifact: dict[str, Any],
    proposal_capture: dict[str, Any] | None,
    explanation_replay_reference: str,
) -> dict[str, list[Any]]:
    prompt = _require_string(human_prompt, "human_prompt")
    workflow = _require_string(workflow_id, "workflow_id")
    proposal = proposal_capture if isinstance(proposal_capture, dict) else {}
    proposal_artifact = proposal.get("proposal_artifact") if isinstance(proposal.get("proposal_artifact"), dict) else {}
    target_paths = proposal.get("target_paths") if isinstance(proposal.get("target_paths"), list) else []
    bridge_replay = proposal.get("replay_reference") if isinstance(proposal.get("replay_reference"), str) else None
    routing_reason = routing_visibility_artifact.get("routing_reason")
    intake_classification = universal_intake_artifact.get("intake_classification")
    what_understood = [
        f"I understood that you want ACLI to handle this request: {prompt}",
        f"Selected workflow: {workflow}",
    ]
    if isinstance(intake_classification, str) and intake_classification:
        what_understood.append(f"Intake classification: {intake_classification}")
    if isinstance(routing_reason, str) and routing_reason:
        what_understood.append(f"Routing reason: {routing_reason}")
    if proposal_artifact:
        what_understood.append(
            f"Proposal id: {_require_string(proposal_artifact.get('proposal_id'), 'proposal_id')}"
        )
    if target_paths:
        what_understood.append({"Target paths": [str(path) for path in target_paths]})

    will_happen = [
        "If approved:",
        [
            "the current governed proposal will be used",
            "repository artifacts may be created or modified",
            "validation will run",
            "replay evidence will be recorded",
        ],
    ]
    will_not_happen = [
        [
            "no worker will execute before approval",
            "no repository mutation will occur before approval",
            "no provider will be invoked unless required by the selected workflow",
            "ACLI will not treat provider output as authority",
        ]
    ]
    approval = [
        "Approval is required because the selected workflow may create or modify repository artifacts.",
        "Approval binds to the proposal hash. A changed proposal requires a new approval.",
    ]
    proposal_hash = proposal_artifact.get("artifact_hash")
    if isinstance(proposal_hash, str) and proposal_hash:
        approval.append(f"Current proposal hash: {proposal_hash}")
    what_next = [
        "Type APPROVE to continue.",
        "Type REJECT to cancel.",
        "Type REQUEST_MODIFICATION to stop execution and request changes.",
    ]
    replay_lines = [
        "Replay evidence is recorded for this explanation.",
        f"Explanation replay location: {_require_string(explanation_replay_reference, 'explanation_replay_reference')}",
    ]
    if bridge_replay:
        replay_lines.append(f"Proposal replay location: {bridge_replay}")
    return {
        "WHAT I UNDERSTOOD": what_understood,
        "WHAT WILL HAPPEN": will_happen,
        "WHAT WILL NOT HAPPEN": will_not_happen,
        "WHAT REQUIRES YOUR APPROVAL": approval,
        "WHAT TO TYPE NEXT": what_next,
        "REPLAY VISIBILITY": replay_lines,
    }


def _render_body_lines(body: list[Any]) -> list[str]:
    rendered: list[str] = []
    for item in body:
        if isinstance(item, str):
            rendered.append(item)
        elif isinstance(item, list):
            rendered.extend(f"- {_require_string(value, 'section_item')}" for value in item)
        elif isinstance(item, dict):
            for key, values in item.items():
                rendered.append(f"{_require_string(key, 'section_label')}:")
                if not isinstance(values, list):
                    raise FailClosedRuntimeError("ACLI explanation nested section values must be a list")
                rendered.extend(f"- {_require_string(value, 'section_item')}" for value in values)
        else:
            raise FailClosedRuntimeError("ACLI explanation section item is invalid")
    return rendered


def _proposal_reference(proposal_capture: dict[str, Any] | None) -> str | None:
    if not isinstance(proposal_capture, dict):
        return None
    proposal = proposal_capture.get("proposal_artifact")
    if not isinstance(proposal, dict):
        return None
    value = proposal.get("proposal_id")
    return value if isinstance(value, str) and value.strip() else None


def _proposal_hash(proposal_capture: dict[str, Any] | None) -> str | None:
    if not isinstance(proposal_capture, dict):
        return None
    proposal = proposal_capture.get("proposal_artifact")
    if not isinstance(proposal, dict):
        return None
    value = proposal.get("artifact_hash")
    return value if isinstance(value, str) and value.strip() else None


def _require_artifact(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"ACLI explanation {field_name} must be a JSON object")
    artifact_hash = value.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not artifact_hash.strip():
        raise FailClosedRuntimeError(f"ACLI explanation {field_name} artifact_hash is required")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI explanation {field_name} is required")
    return value.strip()


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("ACLI explanation artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("ACLI explanation replay hash mismatch")
