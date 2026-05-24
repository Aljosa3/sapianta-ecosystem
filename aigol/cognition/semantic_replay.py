"""Read-only semantic replay continuity verification.

The checker verifies deterministic continuity signals across replay-visible
artifacts. It does not certify semantic truth, execute, authorize, dispatch,
repair evidence, infer hidden context, or mutate governance state.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from agol_bridge.transport.local_governed_transport import canonical_hash

from aigol.cognition.state_envelope import (
    GENERATED_AT,
    UNKNOWN,
    build_cognition_state_envelope,
    load_cognition_artifacts,
)

ARTIFACT_TYPE = "SEMANTIC_REPLAY_CONTINUITY_CHECK_V1"
SCHEMA_VERSION = "1.0"

VERIFIED_STABLE = "VERIFIED_STABLE"
VERIFIED_WITH_WARNINGS = "VERIFIED_WITH_WARNINGS"
UNKNOWN_INSUFFICIENT_EVIDENCE = "UNKNOWN_INSUFFICIENT_EVIDENCE"
DRIFT_DETECTED = "DRIFT_DETECTED"
AUTHORITY_DRIFT_DETECTED = "AUTHORITY_DRIFT_DETECTED"
REPLAY_DISCONTINUITY = "REPLAY_DISCONTINUITY"
INVALID_TRANSITION_CHAIN = "INVALID_TRANSITION_CHAIN"

ALLOWED_STATUSES = {
    VERIFIED_STABLE,
    VERIFIED_WITH_WARNINGS,
    UNKNOWN_INSUFFICIENT_EVIDENCE,
    DRIFT_DETECTED,
    AUTHORITY_DRIFT_DETECTED,
    REPLAY_DISCONTINUITY,
    INVALID_TRANSITION_CHAIN,
}

BOUNDARY_ORDER = {
    "ACCEPTED_FOR_GOVERNED_PREVIEW": 10,
    "READY_FOR_HUMAN_APPROVAL": 20,
    "APPROVED_FOR_GOVERNED_HANDOFF": 30,
    "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION": 40,
    "READY_FOR_DISPATCH_AUTHORIZATION": 40,
    "DISPATCH_AUTHORIZED": 50,
    "READY_FOR_CONTROLLED_EXECUTION_CONTINUITY": 55,
    "READY_FOR_CONTROLLED_EXECUTION_HANDOFF": 60,
    "EXECUTION_COMPLETED": 70,
    "EXECUTION_FAILED": 70,
    "EXECUTION_BLOCKED": 70,
}

BOUNDARY_FIELDS = (
    "gate_status",
    "governance_status",
    "validation_status",
    "status",
    "execution_boundary_state",
    "approval_status",
    "handoff_boundary_state",
    "handoff_preview_status",
    "provider_boundary_state",
    "dispatch_authorization_status",
    "execution_continuity_status",
    "execution_status",
)

AUTHORITY_ESCALATION_FIELDS = (
    "execution_authority",
    "execution_authorized",
    "governance_execution_approved",
    "orchestration_authority",
    "mutation_authority",
    "autonomous_continuation",
    "autonomous_continuation_authorized",
    "autonomous_continuation_performed",
    "provider_dispatch_authorized",
    "provider_dispatch_performed",
    "codex_dispatch_authorized",
)

ALLOWED_TRUE_FIELDS = {
    "human_approved",
    "dispatch_authorized",
    "preview_only",
    "explicit_dispatch_authorization_required",
    "read_only",
    "fail_closed_unknown_handling",
}


def _as_artifacts(artifacts: Any) -> list[dict[str, Any]]:
    if artifacts is None:
        return []
    if isinstance(artifacts, dict):
        return [artifacts]
    if isinstance(artifacts, list):
        return [item for item in artifacts if isinstance(item, dict)]
    return []


def _artifact_type(artifact: dict[str, Any]) -> str:
    return str(artifact.get("artifact_type") or artifact.get("gate_type") or UNKNOWN)


def _check(name: str, status: str, passed: bool, findings: list[str] | None = None) -> dict[str, Any]:
    return {
        "check_name": name,
        "status": status,
        "passed": passed,
        "findings": list(findings or []),
    }


def _artifact_hash(artifact: dict[str, Any]) -> str:
    hashes = artifact.get("hashes", {}) if isinstance(artifact.get("hashes"), dict) else {}
    for key in (
        "artifact_hash",
        "proposal_candidate_hash",
        "contract_candidate_hash",
        "decision_hash",
        "preview_hash",
        "approval_hash",
        "handoff_preview_hash",
        "dispatch_authorization_hash",
        "continuity_preview_hash",
        "execution_governance_hash",
        "governed_return_hash",
    ):
        value = artifact.get(key, hashes.get(key))
        if isinstance(value, str) and value.strip():
            return value
    return UNKNOWN


def _evidence_refs(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[dict[str, str]]:
    refs = [
        {"artifact_type": _artifact_type(artifact), "hash": _artifact_hash(artifact)}
        for artifact in artifacts
    ]
    if envelope:
        refs.append({"artifact_type": envelope.get("artifact_type", UNKNOWN), "hash": envelope.get("envelope_hash", UNKNOWN)})
    return refs


def _collect_replay_identities(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
    identities: list[str] = []
    for artifact in artifacts:
        value = artifact.get("replay_identity")
        if isinstance(value, str) and value.strip():
            identities.append(value)
    value = envelope.get("replay_identity")
    if isinstance(value, str) and value.strip() and value != UNKNOWN:
        identities.append(value)
    return identities


def _collect_normalized_intents(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
    intents: list[str] = []
    for artifact in artifacts:
        value = artifact.get("normalized_intent")
        if isinstance(value, str) and value.strip() and value != UNKNOWN:
            intents.append(value.strip())
    value = envelope.get("normalized_intent")
    if isinstance(value, str) and value.strip() and value != UNKNOWN:
        intents.append(value.strip())
    return intents


def _nested_bool_findings(value: Any, *, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if key in AUTHORITY_ESCALATION_FIELDS and child is True:
                findings.append(f"{child_path}=true")
            findings.extend(_nested_bool_findings(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_nested_bool_findings(child, path=f"{path}[{index}]"))
    return findings


def _authority_findings(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for artifact in artifacts:
        for key, value in artifact.items():
            if key in AUTHORITY_ESCALATION_FIELDS and value is True and key not in ALLOWED_TRUE_FIELDS:
                findings.append(f"{_artifact_type(artifact)}.{key}=true")
        findings.extend(f"{_artifact_type(artifact)}.{finding}" for finding in _nested_bool_findings(artifact))
    for key in ("execution_authority", "orchestration_authority", "mutation_authority", "autonomous_continuation"):
        if envelope.get(key) is not False:
            findings.append(f"envelope.{key} is not false")
    return sorted(set(findings))


def _lineage_unknowns(envelope: dict[str, Any]) -> list[str]:
    lineage = envelope.get("lineage_refs", {})
    if not isinstance(lineage, dict):
        return ["lineage_refs"]
    return sorted(key for key, value in lineage.items() if value in ("", UNKNOWN, None))


def _has_minimum_lineage(envelope: dict[str, Any]) -> bool:
    lineage = envelope.get("lineage_refs", {})
    if not isinstance(lineage, dict):
        return False
    for key in (
        "ingress_artifact_hash",
        "task_package_preview_hash",
        "human_approval_hash",
        "handoff_preview_hash",
        "dispatch_authorization_hash",
    ):
        value = lineage.get(key)
        if not isinstance(value, str) or not value.strip() or value == UNKNOWN:
            return False
    return True


def _boundary_states(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
    states: list[str] = []
    for artifact in artifacts:
        artifact_states: list[str] = []
        for field in BOUNDARY_FIELDS:
            value = artifact.get(field)
            if isinstance(value, str) and value.strip() and value in BOUNDARY_ORDER:
                artifact_states.append(value)
        if "DISPATCH_AUTHORIZED" in artifact_states:
            artifact_states = [state for state in artifact_states if state != "READY_FOR_CONTROLLED_EXECUTION_CONTINUITY"]
        states.extend(artifact_states)
    current = envelope.get("current_boundary_state")
    if isinstance(current, str) and current in BOUNDARY_ORDER:
        states.append(current)
    return states


def _transition_findings(states: list[str]) -> list[str]:
    findings: list[str] = []
    last_order = -1
    last_state = UNKNOWN
    for state in states:
        order = BOUNDARY_ORDER[state]
        if order < last_order:
            findings.append(f"{last_state} -> {state}")
        last_order = max(last_order, order)
        last_state = state
    return findings


def _ambiguity_values(artifacts: list[dict[str, Any]], envelope: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for artifact in artifacts:
        candidate = artifact.get("ambiguities")
        if isinstance(candidate, list):
            values.extend(str(item) for item in candidate)
        child = artifact.get("semantic_contract_candidate")
        if isinstance(child, dict) and isinstance(child.get("ambiguities"), list):
            values.extend(str(item) for item in child["ambiguities"])
    ambiguity_state = envelope.get("ambiguity_state", {})
    if isinstance(ambiguity_state, dict):
        candidate = ambiguity_state.get("ambiguities")
        if isinstance(candidate, list):
            values.extend(str(item) for item in candidate)
        status = ambiguity_state.get("status")
        if isinstance(status, str) and status != UNKNOWN:
            values.append(status)
    return values


def _ambiguity_findings(values: list[str]) -> list[str]:
    if not values:
        return []
    blocking = [value for value in values if value not in {"NO_BLOCKING_AMBIGUITY_DETECTED", "UNKNOWN"}]
    if blocking and "NO_BLOCKING_AMBIGUITY_DETECTED" in values:
        return [f"ambiguity growth detected: {', '.join(sorted(set(blocking)))}"]
    if blocking:
        return [f"unresolved ambiguity present: {', '.join(sorted(set(blocking)))}"]
    return []


def _continuity_confidence(status: str) -> str:
    if status == VERIFIED_STABLE:
        return "HIGH_STRUCTURAL"
    if status == VERIFIED_WITH_WARNINGS:
        return "MEDIUM_WITH_WARNINGS"
    if status in {AUTHORITY_DRIFT_DETECTED, INVALID_TRANSITION_CHAIN, REPLAY_DISCONTINUITY, DRIFT_DETECTED}:
        return "LOW_FAIL_CLOSED"
    return "UNKNOWN_INSUFFICIENT_EVIDENCE"


def _semantic_drift_level(status: str, warnings_present: bool) -> str:
    if status in {DRIFT_DETECTED, AUTHORITY_DRIFT_DETECTED, INVALID_TRANSITION_CHAIN}:
        return "HIGH"
    if warnings_present:
        return "LOW_WARNING"
    if status == UNKNOWN_INSUFFICIENT_EVIDENCE:
        return UNKNOWN
    return "NONE_DETECTED"


def _final_status(
    *,
    artifacts: list[dict[str, Any]],
    intent_findings: list[str],
    authority_findings: list[str],
    replay_findings: list[str],
    transition_findings: list[str],
    ambiguity_findings: list[str],
    unknowns: list[str],
) -> str:
    if authority_findings:
        return AUTHORITY_DRIFT_DETECTED
    if transition_findings:
        return INVALID_TRANSITION_CHAIN
    if replay_findings:
        return REPLAY_DISCONTINUITY
    if intent_findings:
        return DRIFT_DETECTED
    if not artifacts or unknowns:
        return UNKNOWN_INSUFFICIENT_EVIDENCE
    if ambiguity_findings:
        return VERIFIED_WITH_WARNINGS
    return VERIFIED_STABLE


def _hash_input(check: dict[str, Any]) -> dict[str, Any]:
    safe = deepcopy(check)
    safe.pop("semantic_replay_check_hash", None)
    return safe


def build_semantic_replay_continuity_check(
    artifacts: Any = None,
    *,
    generated_at: str = GENERATED_AT,
) -> dict[str, Any]:
    safe_artifacts = _as_artifacts(artifacts)
    envelope = build_cognition_state_envelope(safe_artifacts, generated_at=generated_at)
    identities = _collect_replay_identities(safe_artifacts, envelope)
    unique_identities = sorted(set(identities))
    replay_identity = unique_identities[0] if len(unique_identities) == 1 else UNKNOWN

    intents = _collect_normalized_intents(safe_artifacts, envelope)
    unique_intents = sorted(set(intents))
    intent_findings = []
    if len(unique_intents) > 1:
        intent_findings.append("normalized intent mismatch across replay artifacts")

    authority_findings = _authority_findings(safe_artifacts, envelope)

    lineage_unknowns = _lineage_unknowns(envelope)
    replay_findings = []
    if len(unique_identities) > 1:
        replay_findings.append("multiple replay identities detected")
    if safe_artifacts and identities and not _has_minimum_lineage(envelope):
        replay_findings.append("minimum lineage continuity missing")

    states = _boundary_states(safe_artifacts, envelope)
    transition_findings = _transition_findings(states)

    ambiguity_values = _ambiguity_values(safe_artifacts, envelope)
    ambiguity_findings = _ambiguity_findings(ambiguity_values)

    unknowns = []
    if not safe_artifacts:
        unknowns.append("no replay-visible artifacts provided")
    if not intents:
        unknowns.append("normalized_intent")
    if not identities:
        unknowns.append("replay_identity")
    if safe_artifacts and not _has_minimum_lineage(envelope) and not replay_findings:
        unknowns.extend(lineage_unknowns)

    status = _final_status(
        artifacts=safe_artifacts,
        intent_findings=intent_findings,
        authority_findings=authority_findings,
        replay_findings=replay_findings,
        transition_findings=transition_findings,
        ambiguity_findings=ambiguity_findings,
        unknowns=sorted(set(unknowns)),
    )
    warnings_present = bool(ambiguity_findings)
    checks = [
        _check("Intent Continuity", DRIFT_DETECTED if intent_findings else ("UNKNOWN" if not intents else VERIFIED_STABLE), not intent_findings and bool(intents), intent_findings or ([] if intents else ["normalized intent missing"])),
        _check("Authority Continuity", AUTHORITY_DRIFT_DETECTED if authority_findings else VERIFIED_STABLE, not authority_findings, authority_findings),
        _check("Admissibility Continuity", UNKNOWN if envelope.get("admissibility_state") == UNKNOWN else VERIFIED_STABLE, envelope.get("admissibility_state") != UNKNOWN, [] if envelope.get("admissibility_state") != UNKNOWN else ["admissibility state missing"]),
        _check("Replay Identity Continuity", REPLAY_DISCONTINUITY if replay_findings else (UNKNOWN if not identities else VERIFIED_STABLE), not replay_findings and bool(identities), replay_findings or ([] if identities else ["replay identity missing"])),
        _check("Boundary Transition Continuity", INVALID_TRANSITION_CHAIN if transition_findings else (UNKNOWN if not states else VERIFIED_STABLE), not transition_findings and bool(states), transition_findings or ([] if states else ["boundary states missing"])),
        _check("Ambiguity Continuity", VERIFIED_WITH_WARNINGS if ambiguity_findings else (UNKNOWN if not ambiguity_values else VERIFIED_STABLE), not ambiguity_findings and bool(ambiguity_values), ambiguity_findings or ([] if ambiguity_values else ["ambiguity evidence missing"])),
    ]

    result = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "generated_at": str(generated_at),
        "continuity_status": status,
        "semantic_drift_level": _semantic_drift_level(status, warnings_present),
        "authority_drift_detected": bool(authority_findings),
        "ambiguity_growth_detected": bool(ambiguity_findings),
        "continuity_confidence": _continuity_confidence(status),
        "replay_identity": replay_identity,
        "checks": checks,
        "evidence_refs": _evidence_refs(safe_artifacts, envelope),
        "forbidden_findings": sorted(set(authority_findings + transition_findings)),
        "unknowns": sorted(set(unknowns)),
        "notes": [
            "read-only semantic continuity verification only",
            "no semantic truth certification",
            "UNKNOWN is preferred over guessed meaning",
        ],
        "governance_boundary_integrity": {
            "execution_authority": False,
            "orchestration_authority": False,
            "mutation_authority": False,
            "autonomous_continuation": False,
            "provider_invocation_performed": False,
            "replay_repair_performed": False,
            "artifact_mutation_performed": False,
        },
        "semantic_continuity": {
            "normalized_intents": unique_intents,
            "intent_findings": intent_findings,
        },
        "authority_continuity": {
            "findings": authority_findings,
            "execution_authority": False,
            "orchestration_authority": False,
            "mutation_authority": False,
            "autonomous_continuation": False,
        },
        "replay_continuity": {
            "replay_identities": unique_identities,
            "lineage_unknowns": lineage_unknowns,
            "findings": replay_findings,
        },
        "transition_continuity": {
            "boundary_states": states,
            "findings": transition_findings,
        },
        "ambiguity_continuity": {
            "ambiguity_values": sorted(set(ambiguity_values)),
            "findings": ambiguity_findings,
        },
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "mutation_authority_added": False,
        "provider_invocation_added": False,
    }
    result["semantic_replay_check_hash"] = canonical_hash(_hash_input(result))
    return result


def write_semantic_replay_check(check: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(check, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return {"written": True, "output_path": str(path)}


def inspect_semantic_replay_continuity(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    artifacts: Any = None,
) -> dict[str, Any]:
    loaded = _as_artifacts(artifacts)
    if not loaded:
        loaded = load_cognition_artifacts(input_path)
    check = build_semantic_replay_continuity_check(loaded)
    result = {
        "command": "aigol cognition continuity-check",
        "input_path": str(input_path or ""),
        "artifact_count": len(loaded),
        "semantic_replay_continuity_check": check,
        "read_only": True,
        "execution_authority_added": False,
        "orchestration_authority_added": False,
        "autonomous_continuation_added": False,
        "mutation_authority_added": False,
        "provider_invocation_added": False,
    }
    if output_path:
        result["output"] = write_semantic_replay_check(check, output_path)
    return result


def render_semantic_replay_report(check: dict[str, Any]) -> str:
    def _find_check(name: str) -> dict[str, Any]:
        for item in check.get("checks", []):
            if item.get("check_name") == name:
                return item
        return {}

    sections = [
        "Continuity Status",
        f"  {check.get('continuity_status')}",
        "Intent Continuity",
        f"  {_find_check('Intent Continuity').get('status', UNKNOWN)}",
        "Authority Continuity",
        f"  {_find_check('Authority Continuity').get('status', UNKNOWN)}",
        "Replay Continuity",
        f"  {_find_check('Replay Identity Continuity').get('status', UNKNOWN)}",
        "Transition Continuity",
        f"  {_find_check('Boundary Transition Continuity').get('status', UNKNOWN)}",
        "Ambiguity Continuity",
        f"  {_find_check('Ambiguity Continuity').get('status', UNKNOWN)}",
        "Drift Findings",
        f"  {json.dumps(check.get('forbidden_findings', []), sort_keys=True)}",
        "Unknown Areas",
        f"  {json.dumps(check.get('unknowns', []), sort_keys=True)}",
        "Governance Boundary Integrity",
        "  execution_authority: false",
        "  orchestration_authority: false",
        "  mutation_authority: false",
        "  autonomous_continuation: false",
        "  provider_invocation_performed: false",
    ]
    return "\n".join(sections)


__all__ = [
    "ALLOWED_STATUSES",
    "ARTIFACT_TYPE",
    "AUTHORITY_DRIFT_DETECTED",
    "DRIFT_DETECTED",
    "INVALID_TRANSITION_CHAIN",
    "REPLAY_DISCONTINUITY",
    "SCHEMA_VERSION",
    "UNKNOWN_INSUFFICIENT_EVIDENCE",
    "VERIFIED_STABLE",
    "VERIFIED_WITH_WARNINGS",
    "build_semantic_replay_continuity_check",
    "inspect_semantic_replay_continuity",
    "render_semantic_replay_report",
    "write_semantic_replay_check",
]
