"""Fail-closed production admission for the certified G63 Reuse Proof owner.

This module classifies applicability and binds existing G63 and G47 evidence.
It grants no planning, implementation, mutation, execution, or Worker authority.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
from typing import Any

from aigol.runtime.constitutional_reuse_proof_runtime import (
    DECISIONS,
    evaluate_constitutional_reuse_proof,
    project_reuse_proof_to_development_governance,
    validate_constitutional_reuse_proof_input,
    validate_constitutional_reuse_proof_result,
    validate_reuse_proof_g47_handoff,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


REUSE_PROOF_PRODUCTION_GATE_VERSION = (
    "G64_04_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_GATE_V1"
)
REUSE_PROOF_APPLICABILITY_ARTIFACT_V1 = "REUSE_PROOF_APPLICABILITY_ARTIFACT_V1"
REUSE_PROOF_PRODUCTION_ADMISSION_V1 = "REUSE_PROOF_PRODUCTION_ADMISSION_V1"
REUSE_PROOF_G47_SCOPE_BINDING_V1 = "REUSE_PROOF_G47_SCOPE_BINDING_V1"

REQUIRED = "REQUIRED"
NOT_APPLICABLE = "NOT_APPLICABLE"
UNRESOLVED = "UNRESOLVED"

READY_FOR_FRESH_G47 = "READY_FOR_FRESH_G47"
WAITING_FOR_REUSE_PROOF_EVIDENCE = "WAITING_FOR_REUSE_PROOF_EVIDENCE"
APPLICABILITY_UNRESOLVED = "APPLICABILITY_UNRESOLVED"

REQUIRED_SATISFIED = "REQUIRED_SATISFIED"
NOT_APPLICABLE_PROVEN = "NOT_APPLICABLE_PROVEN"

EXEMPTION_CODES = frozenset(
    {
        "UNCHANGED_CERTIFIED_CAPABILITY_EXECUTION",
        "READ_ONLY_NON_PROPOSING_WORK",
        "NON_SEMANTIC_CONTENT_CORRECTION",
        "EXACT_CERTIFIED_BEHAVIOR_REPAIR",
    }
)

ARCHITECTURE_TRIGGERS = (
    "creates_component",
    "extends_component",
    "consolidates_components",
    "replaces_component",
    "registers_component",
    "deprecates_component",
    "rebinds_owner",
    "changes_route_or_default",
    "changes_authority",
    "changes_public_contract",
)

AUTHORITY_FLAGS = {
    "planning_authorized": False,
    "implementation_authorized": False,
    "mutation_performed": False,
    "authorization_created": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_started": False,
}


def classify_reuse_proof_applicability(
    *,
    applicability_id: str,
    request_reference: str,
    request_hash: str,
    project_objective_reference: str | None,
    project_objective_hash: str | None,
    authenticated_baseline: dict[str, Any] | None,
    proposed_scope: dict[str, Any],
    change_characteristics: dict[str, Any],
    created_at: str,
    exemption_code: str | None = None,
    exemption_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify one development request without inferring an exemption."""

    characteristics = _normalize_characteristics(change_characteristics)
    scope = _require_dict(proposed_scope, "proposed_scope")
    baseline = _normalize_optional_baseline(authenticated_baseline)
    any_trigger = any(characteristics[name] for name in ARCHITECTURE_TRIGGERS)
    exemption = deepcopy(exemption_evidence) if exemption_evidence is not None else None

    if any_trigger:
        disposition = REQUIRED
        normalized_exemption = None
        exemption_hash = None
        reason = "ARCHITECTURE_AFFECTING_CHANGE_REQUIRES_REUSE_PROOF"
    elif exemption_code in EXEMPTION_CODES and _valid_exemption_evidence(
        exemption_code, exemption
    ):
        disposition = NOT_APPLICABLE
        normalized_exemption = exemption_code
        exemption_hash = replay_hash(exemption)
        reason = f"PROVEN_EXEMPTION:{exemption_code}"
    else:
        disposition = UNRESOLVED
        normalized_exemption = None
        exemption_hash = None
        reason = "APPLICABILITY_REQUIRES_GOVERNANCE_EVIDENCE"

    artifact = {
        "artifact_type": REUSE_PROOF_APPLICABILITY_ARTIFACT_V1,
        "runtime_version": REUSE_PROOF_PRODUCTION_GATE_VERSION,
        "applicability_id": _require_string(applicability_id, "applicability_id"),
        "request_reference": _require_string(request_reference, "request_reference"),
        "request_hash": _require_hash(request_hash, "request_hash"),
        "project_objective_reference": _optional_string(
            project_objective_reference, "project_objective_reference"
        ),
        "project_objective_hash": _optional_hash(
            project_objective_hash, "project_objective_hash"
        ),
        "authenticated_baseline": baseline,
        "proposed_scope": scope,
        "scope_digest": replay_hash(scope),
        "change_characteristics": characteristics,
        "applicability_disposition": disposition,
        "exemption_code": normalized_exemption,
        "exemption_evidence": exemption if disposition == NOT_APPLICABLE else None,
        "exemption_evidence_hash": exemption_hash,
        "classification_reason": reason,
        "created_at": _require_string(created_at, "created_at"),
        **AUTHORITY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_reuse_proof_applicability(artifact)


def validate_reuse_proof_applicability(artifact: dict[str, Any]) -> dict[str, Any]:
    candidate = _require_dict(artifact, "reuse proof applicability")
    if candidate.get("artifact_type") != REUSE_PROOF_APPLICABILITY_ARTIFACT_V1:
        raise FailClosedRuntimeError("reuse proof applicability artifact type is invalid")
    if candidate.get("runtime_version") != REUSE_PROOF_PRODUCTION_GATE_VERSION:
        raise FailClosedRuntimeError("reuse proof applicability version is invalid")
    _require_string(candidate.get("applicability_id"), "applicability_id")
    _require_string(candidate.get("request_reference"), "request_reference")
    _require_hash(candidate.get("request_hash"), "request_hash")
    _optional_string(candidate.get("project_objective_reference"), "project_objective_reference")
    _optional_hash(candidate.get("project_objective_hash"), "project_objective_hash")
    _normalize_optional_baseline(candidate.get("authenticated_baseline"))
    scope = _require_dict(candidate.get("proposed_scope"), "proposed_scope")
    if candidate.get("scope_digest") != replay_hash(scope):
        raise FailClosedRuntimeError("reuse proof applicability scope digest mismatch")
    characteristics = _normalize_characteristics(candidate.get("change_characteristics"))
    disposition = candidate.get("applicability_disposition")
    any_trigger = any(characteristics[name] for name in ARCHITECTURE_TRIGGERS)
    if disposition == REQUIRED:
        if not any_trigger or candidate.get("exemption_code") is not None:
            raise FailClosedRuntimeError("required reuse proof applicability is contradictory")
    elif disposition == NOT_APPLICABLE:
        exemption_code = candidate.get("exemption_code")
        evidence = candidate.get("exemption_evidence")
        if any_trigger or exemption_code not in EXEMPTION_CODES:
            raise FailClosedRuntimeError("reuse proof exemption conflicts with change scope")
        if not _valid_exemption_evidence(exemption_code, evidence):
            raise FailClosedRuntimeError("reuse proof exemption evidence is invalid")
        if candidate.get("exemption_evidence_hash") != replay_hash(evidence):
            raise FailClosedRuntimeError("reuse proof exemption evidence hash mismatch")
    elif disposition == UNRESOLVED:
        if any_trigger or candidate.get("exemption_code") is not None:
            raise FailClosedRuntimeError("unresolved reuse proof applicability is contradictory")
    else:
        raise FailClosedRuntimeError("reuse proof applicability disposition is invalid")
    _require_string(candidate.get("classification_reason"), "classification_reason")
    _require_string(candidate.get("created_at"), "created_at")
    _validate_authority_flags(candidate)
    _verify_hash(candidate, "artifact_hash", "reuse proof applicability")
    return deepcopy(candidate)


def prepare_reuse_proof_production_admission(
    *,
    admission_id: str,
    applicability_artifact: dict[str, Any],
    repository_root: str | Path,
    created_at: str,
    proof_input: dict[str, Any] | None = None,
    proof_result: dict[str, Any] | None = None,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose a non-authorizing admission, or a deterministic refusal."""

    applicability = validate_reuse_proof_applicability(applicability_artifact)
    disposition = applicability["applicability_disposition"]
    validated_proof = None
    handoff = None
    if disposition == REQUIRED:
        if proof_input is not None and proof_result is not None:
            raise FailClosedRuntimeError("supply proof_input or proof_result, not both")
        if proof_input is not None:
            validated_input = validate_constitutional_reuse_proof_input(proof_input)
            validated_proof = evaluate_constitutional_reuse_proof(
                proof_input=validated_input,
                repository_root=repository_root,
                workspace_state=workspace_state,
            )
        elif proof_result is not None:
            validated_proof = validate_constitutional_reuse_proof_result(proof_result)
        if validated_proof is None:
            status = WAITING_FOR_REUSE_PROOF_EVIDENCE
            requirement = "REQUIRED_UNSATISFIED"
        else:
            if applicability["authenticated_baseline"] is None:
                raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")
            if validated_proof["authenticated_baseline"] != applicability["authenticated_baseline"]:
                raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")
            _validate_current_baseline(
                Path(repository_root), applicability["authenticated_baseline"]
            )
            handoff = project_reuse_proof_to_development_governance(validated_proof)
            validate_reuse_proof_g47_handoff(handoff)
            status = READY_FOR_FRESH_G47
            requirement = REQUIRED_SATISFIED
    elif disposition == NOT_APPLICABLE:
        if proof_input is not None or proof_result is not None:
            raise FailClosedRuntimeError("proven exemption cannot carry fabricated proof")
        if applicability["authenticated_baseline"] is None:
            raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")
        _validate_current_baseline(
            Path(repository_root), applicability["authenticated_baseline"]
        )
        status = READY_FOR_FRESH_G47
        requirement = NOT_APPLICABLE_PROVEN
    else:
        status = APPLICABILITY_UNRESOLVED
        requirement = "UNRESOLVED"

    artifact = {
        "artifact_type": REUSE_PROOF_PRODUCTION_ADMISSION_V1,
        "runtime_version": REUSE_PROOF_PRODUCTION_GATE_VERSION,
        "admission_id": _require_string(admission_id, "admission_id"),
        "applicability_artifact": applicability,
        "applicability_id": applicability["applicability_id"],
        "applicability_hash": applicability["artifact_hash"],
        "request_reference": applicability["request_reference"],
        "request_hash": applicability["request_hash"],
        "project_objective_reference": applicability["project_objective_reference"],
        "project_objective_hash": applicability["project_objective_hash"],
        "authenticated_baseline": deepcopy(applicability["authenticated_baseline"]),
        "proposed_scope": deepcopy(applicability["proposed_scope"]),
        "scope_digest": applicability["scope_digest"],
        "proof_requirement": requirement,
        "reuse_proof_result": deepcopy(validated_proof),
        "reuse_proof_id": validated_proof["proof_id"] if validated_proof else None,
        "reuse_proof_hash": validated_proof["evidence_identity"] if validated_proof else None,
        "reuse_decision": validated_proof["decision"] if validated_proof else None,
        "selected_target": deepcopy(validated_proof["selected_target"]) if validated_proof else None,
        "evolution_classification": validated_proof["additive_or_versioned"] if validated_proof else None,
        "g63_to_g47_handoff": deepcopy(handoff),
        "g63_to_g47_handoff_hash": handoff["artifact_hash"] if handoff else None,
        "exemption_code": applicability["exemption_code"],
        "exemption_evidence_hash": applicability["exemption_evidence_hash"],
        "admission_status": status,
        "created_at": _require_string(created_at, "created_at"),
        **AUTHORITY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_reuse_proof_production_admission(artifact, require_ready=False)


def validate_reuse_proof_production_admission(
    artifact: dict[str, Any], *, require_ready: bool = True
) -> dict[str, Any]:
    candidate = _require_dict(artifact, "reuse proof production admission")
    if candidate.get("artifact_type") != REUSE_PROOF_PRODUCTION_ADMISSION_V1:
        raise FailClosedRuntimeError("FAILED_CLOSED_REUSE_ADMISSION_REQUIRED")
    if candidate.get("runtime_version") != REUSE_PROOF_PRODUCTION_GATE_VERSION:
        raise FailClosedRuntimeError("reuse proof production admission version is invalid")
    applicability = validate_reuse_proof_applicability(
        _require_dict(candidate.get("applicability_artifact"), "applicability_artifact")
    )
    for field, expected in (
        ("applicability_id", applicability["applicability_id"]),
        ("applicability_hash", applicability["artifact_hash"]),
        ("request_reference", applicability["request_reference"]),
        ("request_hash", applicability["request_hash"]),
        ("project_objective_reference", applicability["project_objective_reference"]),
        ("project_objective_hash", applicability["project_objective_hash"]),
        ("authenticated_baseline", applicability["authenticated_baseline"]),
        ("proposed_scope", applicability["proposed_scope"]),
        ("scope_digest", applicability["scope_digest"]),
    ):
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(f"reuse proof admission {field} mismatch")
    status = candidate.get("admission_status")
    if require_ready and status != READY_FOR_FRESH_G47:
        raise FailClosedRuntimeError("FAILED_CLOSED_REUSE_ADMISSION_REQUIRED")
    disposition = applicability["applicability_disposition"]
    if candidate.get("proof_requirement") == REQUIRED_SATISFIED:
        if disposition != REQUIRED or status != READY_FOR_FRESH_G47:
            raise FailClosedRuntimeError("reuse proof required admission is invalid")
        proof = validate_constitutional_reuse_proof_result(
            _require_dict(candidate.get("reuse_proof_result"), "reuse_proof_result")
        )
        handoff = validate_reuse_proof_g47_handoff(
            _require_dict(candidate.get("g63_to_g47_handoff"), "g63_to_g47_handoff")
        )
        if proof["authenticated_baseline"] != candidate["authenticated_baseline"]:
            raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")
        if candidate.get("reuse_proof_hash") != proof["evidence_identity"]:
            raise FailClosedRuntimeError("reuse proof admission proof hash mismatch")
        if candidate.get("reuse_proof_id") != proof["proof_id"]:
            raise FailClosedRuntimeError("reuse proof admission proof identity mismatch")
        if candidate.get("g63_to_g47_handoff_hash") != handoff["artifact_hash"]:
            raise FailClosedRuntimeError("reuse proof admission handoff hash mismatch")
        if handoff["source_proof_hash"] != proof["evidence_identity"]:
            raise FailClosedRuntimeError("reuse proof admission proof handoff mismatch")
        if candidate.get("reuse_decision") not in DECISIONS:
            raise FailClosedRuntimeError("reuse proof admission decision is invalid")
        if candidate.get("reuse_decision") != proof["decision"]:
            raise FailClosedRuntimeError("reuse proof admission decision mismatch")
        if candidate.get("selected_target") != proof["selected_target"]:
            raise FailClosedRuntimeError("reuse proof admission selected target mismatch")
        if candidate.get("evolution_classification") != proof["additive_or_versioned"]:
            raise FailClosedRuntimeError("reuse proof admission evolution mismatch")
        if handoff["source_reuse_decision"] != proof["decision"]:
            raise FailClosedRuntimeError("reuse proof admission handoff decision mismatch")
    elif candidate.get("proof_requirement") == NOT_APPLICABLE_PROVEN:
        if disposition != NOT_APPLICABLE or status != READY_FOR_FRESH_G47:
            raise FailClosedRuntimeError("reuse proof exemption admission is invalid")
        if any(candidate.get(name) is not None for name in (
            "reuse_proof_result", "reuse_proof_id", "reuse_proof_hash",
            "reuse_decision", "selected_target", "evolution_classification",
            "g63_to_g47_handoff", "g63_to_g47_handoff_hash",
        )):
            raise FailClosedRuntimeError("reuse proof exemption admission fabricated proof")
    elif candidate.get("proof_requirement") == "REQUIRED_UNSATISFIED":
        if disposition != REQUIRED or status != WAITING_FOR_REUSE_PROOF_EVIDENCE:
            raise FailClosedRuntimeError("reuse proof waiting admission is invalid")
    elif candidate.get("proof_requirement") == "UNRESOLVED":
        if disposition != UNRESOLVED or status != APPLICABILITY_UNRESOLVED:
            raise FailClosedRuntimeError("reuse proof unresolved admission is invalid")
    else:
        raise FailClosedRuntimeError("reuse proof admission requirement is invalid")
    _require_string(candidate.get("admission_id"), "admission_id")
    _require_string(candidate.get("created_at"), "created_at")
    _validate_authority_flags(candidate)
    _verify_hash(candidate, "artifact_hash", "reuse proof production admission")
    return deepcopy(candidate)


def bind_reuse_proof_admission_to_g47(
    *, admission_artifact: dict[str, Any], g47_operational_record: dict[str, Any]
) -> dict[str, Any]:
    """Bind two separately-owned results without merging their decisions."""

    admission = validate_reuse_proof_production_admission(admission_artifact)
    from aigol.runtime.constitutional_development_governance_operational_integration import (
        G47_OPERATIONAL_INTEGRATION_READY,
        validate_constitutional_development_governance_operational_record,
    )

    g47 = validate_constitutional_development_governance_operational_record(
        g47_operational_record
    )
    if g47.get("reuse_proof_admission_hash") != admission["artifact_hash"]:
        raise FailClosedRuntimeError("reuse proof admission and G47 record mismatch")
    stages = g47.get("stage_outputs", [])
    eligibility = next(
        (item for item in stages if item.get("artifact_type") == "DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1"),
        None,
    )
    artifact = {
        "artifact_type": REUSE_PROOF_G47_SCOPE_BINDING_V1,
        "runtime_version": REUSE_PROOF_PRODUCTION_GATE_VERSION,
        "binding_id": f"{admission['admission_id']}:G47",
        "admission_artifact": admission,
        "admission_id": admission["admission_id"],
        "admission_hash": admission["artifact_hash"],
        "request_hash": admission["request_hash"],
        "project_objective_hash": admission["project_objective_hash"],
        "authenticated_baseline": deepcopy(admission["authenticated_baseline"]),
        "proposed_scope": deepcopy(admission["proposed_scope"]),
        "scope_digest": admission["scope_digest"],
        "reuse_decision": admission["reuse_decision"],
        "g47_operational_record": g47,
        "g47_operational_record_hash": g47["artifact_hash"],
        "g47_governance_bundle_hash": g47["governance_bundle_hash"],
        "planning_eligibility_id": eligibility.get("planning_eligibility_id") if eligibility else None,
        "planning_eligible": g47.get("planning_eligible"),
        "g47_integration_status": g47.get("integration_status"),
        "canonical_owners": deepcopy(g47.get("canonical_owners", [])),
        "governance_prohibitions": deepcopy(g47.get("governance_prohibitions", [])),
        "residual_gap": deepcopy(g47.get("residual_gap", [])),
        "material_drift": False,
        **AUTHORITY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_reuse_proof_g47_scope_binding(artifact)


def validate_reuse_proof_g47_scope_binding(
    artifact: dict[str, Any], *, require_planning_eligible: bool = True
) -> dict[str, Any]:
    candidate = _require_dict(artifact, "reuse proof G47 scope binding")
    if candidate.get("artifact_type") != REUSE_PROOF_G47_SCOPE_BINDING_V1:
        raise FailClosedRuntimeError("reuse proof G47 scope binding type is invalid")
    if candidate.get("runtime_version") != REUSE_PROOF_PRODUCTION_GATE_VERSION:
        raise FailClosedRuntimeError("reuse proof G47 scope binding version is invalid")
    admission = validate_reuse_proof_production_admission(
        _require_dict(candidate.get("admission_artifact"), "admission_artifact")
    )
    from aigol.runtime.constitutional_development_governance_operational_integration import (
        G47_OPERATIONAL_INTEGRATION_READY,
        validate_constitutional_development_governance_operational_record,
    )
    g47 = validate_constitutional_development_governance_operational_record(
        _require_dict(candidate.get("g47_operational_record"), "g47_operational_record")
    )
    for field, expected in (
        ("admission_id", admission["admission_id"]),
        ("admission_hash", admission["artifact_hash"]),
        ("request_hash", admission["request_hash"]),
        ("project_objective_hash", admission["project_objective_hash"]),
        ("authenticated_baseline", admission["authenticated_baseline"]),
        ("proposed_scope", admission["proposed_scope"]),
        ("scope_digest", admission["scope_digest"]),
        ("reuse_decision", admission["reuse_decision"]),
        ("g47_operational_record_hash", g47["artifact_hash"]),
        ("g47_governance_bundle_hash", g47["governance_bundle_hash"]),
        ("planning_eligible", g47["planning_eligible"]),
        ("g47_integration_status", g47["integration_status"]),
    ):
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(f"reuse proof G47 scope binding {field} mismatch")
    if g47.get("reuse_proof_admission_hash") != admission["artifact_hash"]:
        raise FailClosedRuntimeError("G47 record is not bound to reuse proof admission")
    if candidate.get("material_drift") is not False:
        raise FailClosedRuntimeError("PROOF_STALE_REEVALUATION_REQUIRED")
    if require_planning_eligible and (
        candidate.get("planning_eligible") is not True
        or candidate.get("g47_integration_status") != G47_OPERATIONAL_INTEGRATION_READY
    ):
        raise FailClosedRuntimeError("G47 planning eligibility is required")
    _validate_authority_flags(candidate)
    _verify_hash(candidate, "artifact_hash", "reuse proof G47 scope binding")
    return deepcopy(candidate)


def validate_reuse_proof_current_baseline(
    *, scope_binding: dict[str, Any], repository_root: str | Path
) -> dict[str, Any]:
    """Revalidate a clean bound baseline before any development mutation."""

    binding = validate_reuse_proof_g47_scope_binding(scope_binding)
    _validate_current_baseline(
        Path(repository_root),
        _require_dict(binding.get("authenticated_baseline"), "authenticated_baseline"),
    )
    return binding


def _normalize_characteristics(value: Any) -> dict[str, bool]:
    source = _require_dict(value, "change_characteristics")
    unknown = set(source) - set(ARCHITECTURE_TRIGGERS)
    if unknown:
        raise FailClosedRuntimeError("unknown reuse proof change characteristic")
    normalized = {}
    for name in ARCHITECTURE_TRIGGERS:
        item = source.get(name, False)
        if not isinstance(item, bool):
            raise FailClosedRuntimeError(f"{name} must be boolean")
        normalized[name] = item
    return normalized


def _valid_exemption_evidence(code: str, evidence: Any) -> bool:
    if not isinstance(evidence, dict) or not evidence:
        return False
    if evidence.get("evidence_complete") is not True:
        return False
    if evidence.get("architecture_delta") is not False:
        return False
    required = {
        "UNCHANGED_CERTIFIED_CAPABILITY_EXECUTION": "capability_certification_hash",
        "READ_ONLY_NON_PROPOSING_WORK": "read_only_scope_hash",
        "NON_SEMANTIC_CONTENT_CORRECTION": "semantic_equivalence_hash",
        "EXACT_CERTIFIED_BEHAVIOR_REPAIR": "prior_certification_hash",
    }[code]
    value = evidence.get(required)
    try:
        _require_hash(value, required)
    except FailClosedRuntimeError:
        return False
    return True


def _normalize_optional_baseline(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    baseline = _require_dict(value, "authenticated_baseline")
    for field in ("commit", "parent", "tree"):
        _require_git_hash(baseline.get(field), f"authenticated_baseline.{field}")
    if baseline.get("worktree_clean") is not True:
        raise FailClosedRuntimeError("authenticated baseline must be clean")
    sources = baseline.get("governing_sources")
    if not isinstance(sources, list) or not sources:
        raise FailClosedRuntimeError("authenticated baseline governing sources are required")
    for source in sources:
        record = _require_dict(source, "governing source")
        _require_string(record.get("path"), "governing source path")
        _require_hash(record.get("sha256"), "governing source sha256")
    limitations = baseline.get("known_limitations")
    if not isinstance(limitations, list):
        raise FailClosedRuntimeError("authenticated baseline known limitations must be a list")
    return baseline


def _validate_current_baseline(root: Path, baseline: dict[str, Any]) -> None:
    if not root.is_dir():
        raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")

    def git_value(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")
        return completed.stdout.strip()

    if (
        git_value("rev-parse", "HEAD") != baseline["commit"]
        or git_value("rev-parse", "HEAD^") != baseline["parent"]
        or git_value("rev-parse", "HEAD^{tree}") != baseline["tree"]
        or git_value("status", "--porcelain")
    ):
        raise FailClosedRuntimeError("FAILED_CLOSED_BASELINE_MISMATCH")


def _validate_authority_flags(candidate: dict[str, Any]) -> None:
    for field, expected in AUTHORITY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError("reuse proof production gate authority mismatch")


def _require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field} must be an object")
    return deepcopy(value)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_string(value: Any, field: str) -> str | None:
    return None if value is None else _require_string(value, field)


def _require_hash(value: Any, field: str) -> str:
    result = _require_string(value, field)
    digest = result[7:] if result.startswith("sha256:") else result
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise FailClosedRuntimeError(f"{field} must be a lowercase SHA-256")
    return result


def _require_git_hash(value: Any, field: str) -> str:
    result = _require_string(value, field)
    if len(result) not in {40, 64} or any(
        char not in "0123456789abcdef" for char in result
    ):
        raise FailClosedRuntimeError(f"{field} must be an immutable Git object id")
    return result


def _optional_hash(value: Any, field: str) -> str | None:
    return None if value is None else _require_hash(value, field)


def _verify_hash(candidate: dict[str, Any], field: str, label: str) -> None:
    supplied = candidate.get(field)
    payload = deepcopy(candidate)
    payload.pop(field, None)
    if supplied != replay_hash(payload):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


__all__ = [
    "APPLICABILITY_UNRESOLVED",
    "EXEMPTION_CODES",
    "NOT_APPLICABLE",
    "READY_FOR_FRESH_G47",
    "REQUIRED",
    "REUSE_PROOF_APPLICABILITY_ARTIFACT_V1",
    "REUSE_PROOF_G47_SCOPE_BINDING_V1",
    "REUSE_PROOF_PRODUCTION_ADMISSION_V1",
    "REUSE_PROOF_PRODUCTION_GATE_VERSION",
    "UNRESOLVED",
    "WAITING_FOR_REUSE_PROOF_EVIDENCE",
    "bind_reuse_proof_admission_to_g47",
    "classify_reuse_proof_applicability",
    "prepare_reuse_proof_production_admission",
    "validate_reuse_proof_applicability",
    "validate_reuse_proof_g47_scope_binding",
    "validate_reuse_proof_current_baseline",
    "validate_reuse_proof_production_admission",
]
