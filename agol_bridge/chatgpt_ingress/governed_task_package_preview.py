"""Governed task package preview after ChatGPT ingress acceptance.

This module creates an execution-boundary preview only. It does not create an
executable task package, call providers, dispatch Codex, invoke Native
Messaging, approve governance execution, or continue autonomously.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .ingress_acceptance_gate import (
    ACCEPTED_FOR_GOVERNED_PREVIEW,
    REJECTED_BY_GOVERNANCE_GATE,
    evaluate_chatgpt_ingress_acceptance_gate,
    evaluate_import_acceptance_gate,
)

ARTIFACT_TYPE = "GOVERNED_TASK_PACKAGE_PREVIEW_V1"
SCHEMA_VERSION = "1.0"
READY_FOR_HUMAN_APPROVAL = "READY_FOR_HUMAN_APPROVAL"
PREVIEW_REJECTED = "PREVIEW_REJECTED"
ALLOWED_PREVIEW_STATUSES = (READY_FOR_HUMAN_APPROVAL, PREVIEW_REJECTED)
BOUNDARY_STATEMENT = (
    "This artifact is an execution-boundary preview only. It is not executable, "
    "not dispatchable, and requires explicit future human approval before any "
    "separately governed execution path may be considered."
)

FORBIDDEN_OPERATIONS = (
    "codex_dispatch",
    "native_messaging_execution",
    "provider_dispatch",
    "governance_execution_approval",
    "automatic_execution",
    "autonomous_continuation",
    "orchestration",
    "retries",
    "fallback_routing",
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _hash_without(value: dict, field: str) -> str:
    value_copy = _canonical_copy(value)
    value_copy.pop(field, None)
    return canonical_hash(value_copy)


def _empty_hashes() -> dict:
    return {
        "ingress_artifact_hash": "UNKNOWN",
        "proposal_candidate_hash": "NONE",
        "contract_candidate_hash": "NONE",
        "admissibility_gate_hash": "NONE",
    }


def _preview_hash_input(preview: dict) -> dict:
    return {
        "source_ingress_artifact_hash": preview["source_ingress_artifact_hash"],
        "semantic_proposal_candidate_hash": preview["semantic_proposal_candidate_hash"],
        "semantic_contract_candidate_hash": preview["semantic_contract_candidate_hash"],
        "admissibility_gate_hash": preview["admissibility_gate_hash"],
        "replay_identity": preview["replay_identity"],
        "governance_status": preview["governance_status"],
        "execution_boundary_state": preview["execution_boundary_state"],
    }


def _reject_preview(*, replay_identity: str = "UNKNOWN", reason: str, hashes: dict | None = None) -> dict:
    safe_hashes = {**_empty_hashes(), **_canonical_copy(hashes or {})}
    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": replay_identity or "UNKNOWN",
        "provenance": {},
        "source_ingress_artifact_hash": safe_hashes["ingress_artifact_hash"],
        "semantic_proposal_candidate_hash": safe_hashes["proposal_candidate_hash"],
        "semantic_contract_candidate_hash": safe_hashes["contract_candidate_hash"],
        "admissibility_gate_hash": safe_hashes["admissibility_gate_hash"],
        "normalized_intent": "",
        "expected_artifacts": [],
        "constraints": [],
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "execution_boundary_state": PREVIEW_REJECTED,
        "human_approval_required": True,
        "governance_status": PREVIEW_REJECTED,
        "preview_only": True,
        "executable": False,
        "dispatchable": False,
        "governance_finalized": False,
        "execution_authorized": False,
        "codex_dispatch_authorized": False,
        "provider_dispatch_authorized": False,
        "governance_execution_approved": False,
        "autonomous_continuation_authorized": False,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
        "boundary_statement": BOUNDARY_STATEMENT,
        "rejection_reasons": [reason],
    }
    preview["preview_hash"] = canonical_hash(_preview_hash_input(preview))
    return preview


def create_governed_task_package_preview_from_import_result(import_result: dict) -> dict:
    """Create a governed task package preview from an existing import result.

    The preview is emitted only after the acceptance gate accepts the imported
    semantic candidates. Rejected or malformed inputs produce a deterministic
    PREVIEW_REJECTED artifact with all execution authority flags false.
    """

    safe_result = _canonical_copy(import_result or {})
    gate = evaluate_import_acceptance_gate(safe_result)
    report = safe_result.get("governance_acceptance_report", {})
    proposal = safe_result.get("semantic_proposal_candidate", {})
    contract = safe_result.get("semantic_contract_candidate", {})
    preserved_hashes = report.get("preserved_hashes", {})
    hashes = {
        "ingress_artifact_hash": preserved_hashes.get("ingress_artifact_hash", "UNKNOWN"),
        "proposal_candidate_hash": preserved_hashes.get("proposal_candidate_hash", "NONE"),
        "contract_candidate_hash": preserved_hashes.get("contract_candidate_hash", "NONE"),
        "admissibility_gate_hash": gate.get("decision_hash", "NONE"),
    }

    if gate.get("gate_status") != ACCEPTED_FOR_GOVERNED_PREVIEW:
        return _reject_preview(
            replay_identity=gate.get("replay_identity", report.get("replay_identity", "UNKNOWN")),
            reason="acceptance gate did not accept imported semantic ingress",
            hashes=hashes,
        )

    if gate.get("execution_authorized") is not False:
        return _reject_preview(
            replay_identity=gate.get("replay_identity", "UNKNOWN"),
            reason="execution authorization cannot be present in preview",
            hashes=hashes,
        )
    if gate.get("codex_dispatch_authorized") is not False or gate.get("provider_dispatch_authorized") is not False:
        return _reject_preview(
            replay_identity=gate.get("replay_identity", "UNKNOWN"),
            reason="provider dispatch authorization cannot be present in preview",
            hashes=hashes,
        )
    if gate.get("governance_execution_approval") is not False:
        return _reject_preview(
            replay_identity=gate.get("replay_identity", "UNKNOWN"),
            reason="governance execution approval cannot be present in preview",
            hashes=hashes,
        )
    if gate.get("autonomous_continuation_authorized") is not False:
        return _reject_preview(
            replay_identity=gate.get("replay_identity", "UNKNOWN"),
            reason="autonomous continuation cannot be present in preview",
            hashes=hashes,
        )

    preview = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "replay_identity": gate["replay_identity"],
        "provenance": {
            "source": "CHATGPT_INGRESS_ACCEPTANCE_GATE_V1",
            "provenance_lineage": _canonical_copy(report.get("provenance_lineage", {})),
            "source_candidate_references": _canonical_copy(proposal.get("provenance_references", {})),
        },
        "source_ingress_artifact_hash": hashes["ingress_artifact_hash"],
        "semantic_proposal_candidate_hash": hashes["proposal_candidate_hash"],
        "semantic_contract_candidate_hash": hashes["contract_candidate_hash"],
        "admissibility_gate_hash": hashes["admissibility_gate_hash"],
        "normalized_intent": contract.get("normalized_intent", proposal.get("normalized_intent", "")),
        "expected_artifacts": _canonical_copy(contract.get("expected_artifacts", proposal.get("expected_artifacts", []))),
        "constraints": _canonical_copy(contract.get("constraints", proposal.get("constraints", []))),
        "forbidden_operations": list(dict.fromkeys(list(contract.get("forbidden_operations", [])) + list(FORBIDDEN_OPERATIONS))),
        "execution_boundary_state": READY_FOR_HUMAN_APPROVAL,
        "human_approval_required": True,
        "governance_status": READY_FOR_HUMAN_APPROVAL,
        "preview_only": True,
        "executable": False,
        "dispatchable": False,
        "governance_finalized": False,
        "execution_authorized": False,
        "codex_dispatch_authorized": False,
        "provider_dispatch_authorized": False,
        "governance_execution_approved": False,
        "autonomous_continuation_authorized": False,
        "classification": ["STRUCTURAL_ONLY", "ADVISORY_ONLY"],
        "admissibility_continuity": {
            "gate_status": gate["gate_status"],
            "decision_hash": gate["decision_hash"],
            "replay_visible": gate.get("replay_visible") is True,
            "semantic_correctness_verified": False,
        },
        "boundary_statement": BOUNDARY_STATEMENT,
    }
    preview["preview_hash"] = canonical_hash(_preview_hash_input(preview))
    return preview


def create_governed_task_package_preview(artifact: Any) -> dict:
    """Run import validation, acceptance gate, and preview creation, then stop."""

    result = evaluate_chatgpt_ingress_acceptance_gate(artifact)
    if result.get("gate_status") == REJECTED_BY_GOVERNANCE_GATE:
        gate = result.get("decision_evidence", {})
        return _reject_preview(
            replay_identity=gate.get("replay_identity", "UNKNOWN"),
            reason="acceptance gate rejected ingress artifact",
            hashes={
                "ingress_artifact_hash": gate.get("ingress_artifact_hash", "UNKNOWN"),
                "proposal_candidate_hash": gate.get("proposal_candidate_hash", "NONE"),
                "contract_candidate_hash": gate.get("contract_candidate_hash", "NONE"),
                "admissibility_gate_hash": gate.get("decision_hash", "NONE"),
            },
        )
    return create_governed_task_package_preview_from_import_result(result["import_result"])


def validate_governed_task_package_preview(preview: Any) -> dict:
    """Validate that a preview remains an inert execution-boundary artifact."""

    errors: list[str] = []
    if not isinstance(preview, dict):
        return {"valid": False, "status": PREVIEW_REJECTED, "errors": ["preview must be a dict"]}
    if preview.get("artifact_type") != ARTIFACT_TYPE:
        errors.append("artifact_type invalid")
    if preview.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version invalid")
    if preview.get("governance_status") not in ALLOWED_PREVIEW_STATUSES:
        errors.append("governance_status invalid")
    if preview.get("execution_boundary_state") not in ALLOWED_PREVIEW_STATUSES:
        errors.append("execution_boundary_state invalid")
    for field in (
        "source_ingress_artifact_hash",
        "semantic_proposal_candidate_hash",
        "semantic_contract_candidate_hash",
        "admissibility_gate_hash",
        "replay_identity",
        "preview_hash",
    ):
        if not isinstance(preview.get(field), str) or not preview.get(field):
            errors.append(f"{field} is required")
    for field in (
        "preview_only",
        "human_approval_required",
    ):
        if preview.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in (
        "executable",
        "dispatchable",
        "governance_finalized",
        "execution_authorized",
        "codex_dispatch_authorized",
        "provider_dispatch_authorized",
        "governance_execution_approved",
        "autonomous_continuation_authorized",
    ):
        if preview.get(field) is not False:
            errors.append(f"{field} must be false")
    expected_hash = canonical_hash(_preview_hash_input(preview)) if not errors else None
    if expected_hash is not None and preview.get("preview_hash") != expected_hash:
        errors.append("preview_hash mismatch")
    return {
        "valid": not errors,
        "status": preview.get("governance_status", PREVIEW_REJECTED),
        "errors": errors,
    }


__all__ = [
    "ALLOWED_PREVIEW_STATUSES",
    "ARTIFACT_TYPE",
    "BOUNDARY_STATEMENT",
    "PREVIEW_REJECTED",
    "READY_FOR_HUMAN_APPROVAL",
    "SCHEMA_VERSION",
    "create_governed_task_package_preview",
    "create_governed_task_package_preview_from_import_result",
    "validate_governed_task_package_preview",
]
