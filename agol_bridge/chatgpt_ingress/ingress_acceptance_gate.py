"""Deterministic acceptance gate for ChatGPT ingress import previews.

The gate decides whether imported semantic ingress is admissible for future
governed handoff preview. It does not execute, dispatch providers, create task
packages, approve governance execution, or verify semantic correctness.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from .ingress_import_validation import (
    ACCEPTED_FOR_STRUCTURAL_IMPORT,
    import_chatgpt_ingress_artifact,
)

ACCEPTED_FOR_GOVERNED_PREVIEW = "ACCEPTED_FOR_GOVERNED_PREVIEW"
REJECTED_BY_GOVERNANCE_GATE = "REJECTED_BY_GOVERNANCE_GATE"
ALLOWED_GATE_STATUSES = (
    ACCEPTED_FOR_GOVERNED_PREVIEW,
    REJECTED_BY_GOVERNANCE_GATE,
)


def _canonical_copy(value: Any) -> Any:
    return deepcopy(value)


def _decision_hash(evidence: dict) -> str:
    evidence_copy = _canonical_copy(evidence)
    evidence_copy.pop("decision_hash", None)
    return canonical_hash(evidence_copy)


def _check(name: str, passed: bool, detail: str) -> dict:
    return {"check": name, "passed": passed, "detail": detail}


def _import_errors(import_result: dict) -> list[str]:
    validation = import_result.get("ingress_validation", {})
    return [
        f"{error.get('field', 'artifact')}: {error.get('error', 'invalid')}"
        for error in validation.get("errors", [])
        if isinstance(error, dict)
    ] or list(validation.get("errors", []))


def evaluate_import_acceptance_gate(import_result: dict) -> dict:
    """Evaluate an import result for admissibility into governed preview."""

    safe_result = _canonical_copy(import_result or {})
    proposal = safe_result.get("semantic_proposal_candidate", {})
    contract = safe_result.get("semantic_contract_candidate", {})
    report = safe_result.get("governance_acceptance_report", {})
    preserved_hashes = report.get("preserved_hashes", {})
    validation_passed = safe_result.get("status") == ACCEPTED_FOR_STRUCTURAL_IMPORT
    replay_identity = report.get("replay_identity", "UNKNOWN")
    ingress_hash = preserved_hashes.get("ingress_artifact_hash", "UNKNOWN")
    proposal_hash = preserved_hashes.get("proposal_candidate_hash", "NONE")
    contract_hash = preserved_hashes.get("contract_candidate_hash", "NONE")
    actual_proposal_hash = proposal.get("proposal_candidate_hash", "NONE")
    actual_contract_hash = contract.get("contract_candidate_hash", "NONE")

    authority_boundary_check = _check(
        "authority_boundary_check",
        validation_passed
        and proposal.get("execution_authority") is False
        and proposal.get("governance_authority") is False
        and contract.get("governance_approved") is False
        and report.get("authority_boundary", {}).get("execution_authority") is False,
        "ChatGPT/import candidates carry no governance, approval, or execution authority.",
    )
    replay_continuity_check = _check(
        "replay_continuity_check",
        validation_passed
        and isinstance(replay_identity, str)
        and replay_identity not in {"", "UNKNOWN"}
        and proposal.get("replay_identity") == replay_identity
        and contract.get("replay_identity") == replay_identity,
        "Replay identity is preserved across import, proposal candidate, and contract candidate.",
    )
    provenance_check = _check(
        "provenance_check",
        validation_passed
        and bool(report.get("provenance_lineage"))
        and bool(proposal.get("provenance_references")),
        "Provenance lineage is present and carried into candidate state.",
    )
    hash_integrity_check = _check(
        "hash_integrity_check",
        validation_passed
        and isinstance(ingress_hash, str)
        and ingress_hash.startswith("sha256:")
        and isinstance(proposal_hash, str)
        and proposal_hash.startswith("sha256:")
        and isinstance(contract_hash, str)
        and contract_hash.startswith("sha256:")
        and proposal_hash == actual_proposal_hash
        and contract_hash == actual_contract_hash,
        "Ingress, proposal candidate, and contract candidate hashes are present.",
    )
    semantic_correctness_check = _check(
        "semantic_correctness_check",
        validation_passed
        and contract.get("semantic_correctness_verified") is False
        and report.get("semantic_correctness_verified") is False,
        "Semantic correctness remains unverified.",
    )
    execution_boundary_check = _check(
        "execution_boundary_check",
        safe_result.get("execution_performed") is False
        and report.get("execution_performed") is False
        and contract.get("execution_authorized") is False,
        "No execution was performed or authorized.",
    )
    provider_dispatch_check = _check(
        "provider_dispatch_check",
        safe_result.get("codex_dispatch_performed") is False
        and report.get("codex_dispatch_performed") is False
        and contract.get("provider_dispatch_authorized") is False
        and proposal.get("codex_dispatch_allowed") is False,
        "No Codex or provider dispatch was performed or authorized.",
    )
    autonomous_continuation_check = _check(
        "autonomous_continuation_check",
        safe_result.get("autonomous_continuation_performed") is False
        and report.get("autonomous_continuation_performed") is False
        and proposal.get("autonomous_continuation_allowed") is False,
        "No autonomous continuation was performed or authorized.",
    )

    checks = [
        authority_boundary_check,
        replay_continuity_check,
        provenance_check,
        hash_integrity_check,
        semantic_correctness_check,
        execution_boundary_check,
        provider_dispatch_check,
        autonomous_continuation_check,
    ]
    rejection_reasons = _import_errors(safe_result)
    rejection_reasons.extend(check["detail"] for check in checks if not check["passed"])
    accepted = validation_passed and not rejection_reasons

    evidence = {
        "gate_type": "CHATGPT_INGRESS_ACCEPTANCE_GATE_V1",
        "gate_status": ACCEPTED_FOR_GOVERNED_PREVIEW if accepted else REJECTED_BY_GOVERNANCE_GATE,
        "admissibility_reasons": [check["detail"] for check in checks if check["passed"]],
        "rejection_reasons": rejection_reasons,
        "authority_boundary_check": authority_boundary_check,
        "replay_continuity_check": replay_continuity_check,
        "provenance_check": provenance_check,
        "hash_integrity_check": hash_integrity_check,
        "semantic_correctness_check": semantic_correctness_check,
        "execution_boundary_check": execution_boundary_check,
        "provider_dispatch_check": provider_dispatch_check,
        "autonomous_continuation_check": autonomous_continuation_check,
        "ingress_artifact_hash": ingress_hash,
        "proposal_candidate_hash": proposal_hash,
        "contract_candidate_hash": contract_hash,
        "replay_identity": replay_identity,
        "execution_authorized": False,
        "codex_dispatch_authorized": False,
        "provider_dispatch_authorized": False,
        "semantic_correctness_verified": False,
        "governance_execution_approval": False,
        "autonomous_continuation_authorized": False,
        "replay_visible": True,
        "durable_replay_persistence": False,
    }
    evidence["decision_hash"] = _decision_hash(evidence)
    return evidence


def evaluate_chatgpt_ingress_acceptance_gate(artifact: Any) -> dict:
    """Import an ingress artifact, evaluate the gate, and stop."""

    import_result = import_chatgpt_ingress_artifact(artifact)
    decision_evidence = evaluate_import_acceptance_gate(import_result)
    return {
        "gate_status": decision_evidence["gate_status"],
        "import_result": import_result,
        "decision_evidence": decision_evidence,
        "gate_only": True,
        "execution_performed": False,
        "codex_dispatch_performed": False,
        "provider_dispatch_performed": False,
        "autonomous_continuation_performed": False,
    }


__all__ = [
    "ACCEPTED_FOR_GOVERNED_PREVIEW",
    "ALLOWED_GATE_STATUSES",
    "REJECTED_BY_GOVERNANCE_GATE",
    "evaluate_chatgpt_ingress_acceptance_gate",
    "evaluate_import_acceptance_gate",
]
