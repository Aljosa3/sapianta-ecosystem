"""Conversational CLI workflow routing for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_CONVERSATIONAL_CLI_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_CONVERSATIONAL_CLI_RUNTIME_STATUS"

CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1 = "CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1"
CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1 = "CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1"

WORKFLOW_SELECTED = "WORKFLOW_SELECTED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
FAILED_CLOSED = "FAILED_CLOSED"

CREATE_DOMAIN_TRADING = "CREATE_DOMAIN_TRADING"
CREATE_DOMAIN_MARKETING = "CREATE_DOMAIN_MARKETING"
CREATE_DOMAIN_COMPLIANCE_CLARIFICATION = "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
DOMAIN_ADAPTATION_REFERENCE = "DOMAIN_ADAPTATION_REFERENCE"
OPERATOR_DECISION_SUPPORT = "OPERATOR_DECISION_SUPPORT"
SHOW_LATEST_REPLAY_CHAIN = "SHOW_LATEST_REPLAY_CHAIN"
REVIEW_LATEST_AUDIT = "REVIEW_LATEST_AUDIT"
IMPROVE_PROVIDER_LAYER = "IMPROVE_PROVIDER_LAYER"
SHOW_STATUS = "SHOW_STATUS"
SHOW_DASHBOARD = "SHOW_DASHBOARD"

REPLAY_STEPS = (
    "conversational_routing_decision_recorded",
    "conversational_workflow_selection_recorded",
    "conversational_routing_returned",
)


def route_conversational_cli_intent(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Route natural language to an existing certified workflow selection."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        analysis = _classify_workflow(human_prompt)
        decision = _routing_decision_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            analysis=analysis,
            failure_reason=None,
        )
        selection = _workflow_selection_artifact(
            routing_id=routing_id,
            decision=decision,
            analysis=analysis,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=None,
        )
        returned = _returned_artifact(decision, selection)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], selection)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(decision, selection, returned, replay_path)
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "conversational CLI routing failed closed"
        decision = _failed_decision_artifact(
            routing_id=routing_id,
            prompt_id=prompt_id,
            human_prompt=human_prompt,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        selection = _failed_selection_artifact(
            routing_id=routing_id,
            decision=decision,
            created_at=created_at,
            replay_reference=str(replay_path),
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(decision, selection)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], decision)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], selection)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], returned)
        return _capture(decision, selection, returned, replay_path)


def reconstruct_conversational_cli_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversational CLI routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversational CLI routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversational CLI routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    selection = wrappers[1]["artifact"]
    returned = wrappers[2]["artifact"]
    if selection.get("routing_decision_reference") != decision["routing_decision_id"]:
        raise FailClosedRuntimeError("conversational CLI routing decision reference mismatch")
    if selection.get("routing_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("conversational CLI routing decision hash mismatch")
    if returned.get("workflow_selection_reference") != selection["workflow_selection_id"]:
        raise FailClosedRuntimeError("conversational CLI routing returned reference mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "routing_status": returned["routing_status"],
        "workflow_id": returned["workflow_id"],
        "existing_runtime": selection.get("existing_runtime"),
        "existing_cli_command": selection.get("existing_cli_command"),
        "coverage": deepcopy(selection["coverage"]),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "replay_hash": replay_hash(wrappers),
    }


def render_conversational_cli_routing_summary(capture: dict[str, Any]) -> str:
    selection = capture.get("workflow_selection_artifact") or {}
    coverage = selection.get("coverage", {})
    lines = [
        f"routing_status: {capture.get('routing_status')}",
        f"workflow_id: {capture.get('workflow_id')}",
        f"existing_runtime: {selection.get('existing_runtime')}",
        f"existing_cli_command: {selection.get('existing_cli_command')}",
        f"operator_summary: {selection.get('operator_summary')}",
        f"coverage: {coverage.get('conversationally_accessible_workflows')}/{coverage.get('registered_workflows')}",
        f"replay_reference: {capture.get('conversational_cli_routing_replay_reference')}",
        f"provider_invoked: {capture.get('provider_invoked')}",
        f"worker_invoked: {capture.get('worker_invoked')}",
        f"execution_requested: {capture.get('execution_requested')}",
        f"fail_closed: {capture.get('fail_closed')}",
        f"failure_reason: {capture.get('failure_reason') or ''}",
    ]
    return "\n".join(lines)


def workflow_registry() -> tuple[dict[str, Any], ...]:
    """Return the deterministic conversational workflow registry."""

    return (
        _workflow(CREATE_DOMAIN_TRADING, "aigol conversation", "conversation_native_development_intent_routing"),
        _workflow(CREATE_DOMAIN_MARKETING, "aigol conversation", "conversation_native_development_intent_routing"),
        _workflow(
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
            "aigol conversation",
            "unknown_domain_clarification_runtime",
            clarification=True,
        ),
        _workflow(
            DOMAIN_ADAPTATION_REFERENCE,
            "aigol domain-reference resolve",
            "semantic_similarity_domain_reference_runtime",
        ),
        _workflow(
            OPERATOR_DECISION_SUPPORT,
            "aigol decision-support recommend",
            "operator_decision_support_runtime",
        ),
        _workflow(SHOW_LATEST_REPLAY_CHAIN, "aigol show-latest-chain", "cli_chain_inspection_runtime"),
        _workflow(REVIEW_LATEST_AUDIT, "aigol conversational route", "capability_audit_artifact_review"),
        _workflow(IMPROVE_PROVIDER_LAYER, "aigol conversational route", "provider_layer_review_guidance"),
        _workflow(SHOW_STATUS, "aigol status", "status_summary"),
        _workflow(SHOW_DASHBOARD, "aigol dashboard", "session_dashboard_runtime"),
    )


def _classify_workflow(human_prompt: str) -> dict[str, Any]:
    prompt = _require_string(human_prompt, "human_prompt")
    normalized = prompt.lower().strip().rstrip(".?!")
    if _is_domain_adaptation_reference_prompt(normalized):
        return _analysis(DOMAIN_ADAPTATION_REFERENCE, "HIGH", ["domain", "reference", "adaptation"])
    if _is_operator_decision_support_prompt(normalized):
        return _analysis(OPERATOR_DECISION_SUPPORT, "HIGH", ["operator", "decision", "support"])
    if "create" in normalized and "trading" in normalized and "domain" in normalized:
        return _analysis(CREATE_DOMAIN_TRADING, "HIGH", ["create", "trading", "domain"])
    if "create" in normalized and "marketing" in normalized and "domain" in normalized:
        return _analysis(CREATE_DOMAIN_MARKETING, "HIGH", ["create", "marketing", "domain"])
    if "create" in normalized and "domain" in normalized and (
        "compliance" in normalized or "regulatory" in normalized
    ):
        return _analysis(CREATE_DOMAIN_COMPLIANCE_CLARIFICATION, "HIGH", ["create", "compliance", "domain"])
    if "latest" in normalized and ("replay chain" in normalized or "chain" in normalized):
        return _analysis(SHOW_LATEST_REPLAY_CHAIN, "HIGH", ["latest", "replay", "chain"])
    if "review" in normalized and "audit" in normalized:
        return _analysis(REVIEW_LATEST_AUDIT, "HIGH", ["review", "audit"])
    if "improve" in normalized and "provider" in normalized and "layer" in normalized:
        return _analysis(IMPROVE_PROVIDER_LAYER, "MEDIUM", ["improve", "provider", "layer"])
    if normalized in {"status", "show status", "what is status"}:
        return _analysis(SHOW_STATUS, "HIGH", ["status"])
    if "dashboard" in normalized:
        return _analysis(SHOW_DASHBOARD, "HIGH", ["dashboard"])
    raise FailClosedRuntimeError("conversational CLI routing failed closed: no certified workflow mapping")


def _analysis(workflow_id: str, confidence: str, matched_terms: list[str]) -> dict[str, Any]:
    entry = _workflow_by_id(workflow_id)
    return {
        "workflow_id": workflow_id,
        "routing_status": CLARIFICATION_REQUIRED if entry.get("clarification_required") else WORKFLOW_SELECTED,
        "confidence": confidence,
        "matched_terms": list(matched_terms),
        "existing_runtime": entry["existing_runtime"],
        "existing_cli_command": entry["existing_cli_command"],
        "operator_summary": _operator_summary(workflow_id),
    }


def _is_domain_adaptation_reference_prompt(normalized: str) -> bool:
    markers = (
        "similar to",
        "based on",
        "derived from",
        "version of",
        "adaptation of",
        "same as but",
        "as a basis",
    )
    domains = ("trading", "marketing", "compliance", "healthcare", "public services", "server management")
    return any(marker in normalized for marker in markers) and any(domain in normalized for domain in domains)


def _is_operator_decision_support_prompt(normalized: str) -> bool:
    return (
        ("first real" in normalized and ("product domain" in normalized or "aigol product domain" in normalized))
        or "which capability" in normalized
        or ("capability" in normalized and "next" in normalized)
        or "which provider" in normalized
        or ("provider" in normalized and "first" in normalized)
        or "which worker" in normalized
        or ("worker" in normalized and "compare" in normalized)
        or "roadmap" in normalized
        or "prioritize" in normalized
        or "priority" in normalized
        or "sequencing" in normalized
    )


def _routing_decision_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: str,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    analysis: dict[str, Any],
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "routing_decision_id": f"{_require_string(routing_id, 'routing_id')}:DECISION",
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "workflow_id": analysis["workflow_id"],
        "routing_status": analysis["routing_status"],
        "confidence": analysis["confidence"],
        "matched_terms": deepcopy(analysis["matched_terms"]),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _workflow_selection_artifact(
    *,
    routing_id: str,
    decision: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    _verify_artifact_hash(decision)
    artifact = {
        "artifact_type": CONVERSATIONAL_WORKFLOW_SELECTION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "workflow_selection_id": f"{_require_string(routing_id, 'routing_id')}:WORKFLOW-SELECTION",
        "routing_decision_reference": decision["routing_decision_id"],
        "routing_decision_hash": decision["artifact_hash"],
        "canonical_chain_id": decision["canonical_chain_id"],
        "workflow_id": analysis["workflow_id"],
        "routing_status": analysis["routing_status"],
        "existing_runtime": analysis["existing_runtime"],
        "existing_cli_command": analysis["existing_cli_command"],
        "operator_summary": analysis["operator_summary"],
        "coverage": _coverage(),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "approval_required_if_downstream_requires_approval": True,
        "authorization_required_if_downstream_requires_authorization": True,
        "provider_controls_preserved": True,
        "worker_controls_preserved": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(decision: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(decision)
    _verify_artifact_hash(selection)
    artifact = {
        "event_type": "CONVERSATIONAL_CLI_ROUTING_RETURNED",
        "milestone_id": MILESTONE_ID,
        "routing_decision_reference": decision["routing_decision_id"],
        "routing_decision_hash": decision["artifact_hash"],
        "workflow_selection_reference": selection["workflow_selection_id"],
        "workflow_selection_hash": selection["artifact_hash"],
        "routing_status": selection["routing_status"],
        "workflow_id": selection["workflow_id"],
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": selection["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_decision_artifact(
    *,
    routing_id: str,
    prompt_id: str,
    human_prompt: Any,
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CONVERSATIONAL_ROUTING_DECISION_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "routing_decision_id": f"{routing_id}:DECISION",
        "prompt_id": prompt_id if isinstance(prompt_id, str) else None,
        "human_prompt_hash": replay_hash(human_prompt) if isinstance(human_prompt, str) else None,
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "workflow_id": None,
        "routing_status": FAILED_CLOSED,
        "confidence": "NONE",
        "matched_terms": [],
        "created_at": created_at if isinstance(created_at, str) else "",
        "replay_reference": replay_reference,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_selection_artifact(
    *,
    routing_id: str,
    decision: dict[str, Any],
    created_at: str,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _workflow_selection_artifact(
        routing_id=routing_id,
        decision=decision,
        analysis={
            "workflow_id": None,
            "routing_status": FAILED_CLOSED,
            "existing_runtime": None,
            "existing_cli_command": None,
            "operator_summary": "",
        },
        created_at=created_at,
        replay_reference=replay_reference,
        failure_reason=failure_reason,
    )


def _capture(decision: dict[str, Any], selection: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "command": "aigol conversational route",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "routing_status": returned["routing_status"],
        "workflow_id": returned["workflow_id"],
        "routing_decision_artifact": deepcopy(decision),
        "workflow_selection_artifact": deepcopy(selection),
        "conversational_routing_returned": deepcopy(returned),
        "conversational_cli_routing_replay_reference": str(replay_path),
        "coverage": deepcopy(selection.get("coverage", _coverage())),
        "fail_closed": returned["routing_status"] == FAILED_CLOSED,
        "failure_reason": returned.get("failure_reason"),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "approval_bypassed": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    capture["conversational_cli_routing_hash"] = replay_hash(capture)
    return capture


def _workflow(workflow_id: str, cli_command: str, runtime: str, *, clarification: bool = False) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "existing_cli_command": cli_command,
        "existing_runtime": runtime,
        "conversationally_accessible": True,
        "clarification_required": clarification,
    }


def _workflow_by_id(workflow_id: str) -> dict[str, Any]:
    for entry in workflow_registry():
        if entry["workflow_id"] == workflow_id:
            return entry
    raise FailClosedRuntimeError("conversational CLI routing failed closed: workflow is not registered")


def _coverage() -> dict[str, Any]:
    registry = workflow_registry()
    accessible = [entry for entry in registry if entry["conversationally_accessible"] is True]
    return {
        "registered_workflows": len(registry),
        "conversationally_accessible_workflows": len(accessible),
        "coverage_ratio": f"{len(accessible)}/{len(registry)}",
        "workflow_ids": [entry["workflow_id"] for entry in registry],
    }


def _operator_summary(workflow_id: str) -> str:
    summaries = {
        CREATE_DOMAIN_TRADING: "Route to existing native-development domain workflow.",
        CREATE_DOMAIN_MARKETING: "Route to existing native-development domain workflow.",
        CREATE_DOMAIN_COMPLIANCE_CLARIFICATION: "Use certified unknown-domain clarification workflow.",
        DOMAIN_ADAPTATION_REFERENCE: "Resolve semantic domain references into a governed adaptation candidate.",
        OPERATOR_DECISION_SUPPORT: "Generate a governed non-authoritative recommendation for human review.",
        SHOW_LATEST_REPLAY_CHAIN: "Show latest replay chain through read-only chain inspection.",
        REVIEW_LATEST_AUDIT: "Review existing capability audit artifacts without regenerating them.",
        IMPROVE_PROVIDER_LAYER: "Route to provider-layer improvement review guidance without execution.",
        SHOW_STATUS: "Show AiGOL status.",
        SHOW_DASHBOARD: "Show read-only operator dashboard.",
    }
    return summaries.get(workflow_id, "")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("conversational CLI routing replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {"replay_index": index, "replay_step": step, "artifact": deepcopy(artifact)}
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        return


def _ensure_replay_available(replay_dir: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_dir / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError("conversational CLI routing failed closed: replay already exists")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("conversational CLI routing artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversational CLI routing artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("conversational CLI routing replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversational CLI routing replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
