"""Deterministic Generation Certification composition for Platform Core.

The service composes existing certification, governance, runtime, and replay
evidence.  It does not replace the capability registry, Replay Certification,
Replay Observation Layer, query router, or presentation layer.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.replay_certification_runtime import REPLAY_CERTIFICATION_ARTIFACT_V1
from aigol.runtime.replay_observation_layer import REPLAY_OBSERVATION_LAYER_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash


GENERATION_CERTIFICATION_COMPOSITION_VERSION = (
    "G20_01_GENERATION_CERTIFICATION_COMPOSITION_SERVICE_V1"
)
GENERATION_EVIDENCE_PROFILE_V1 = "GENERATION_EVIDENCE_PROFILE_V1"
GENERATION_CERTIFICATION_RESULT_V1 = "GENERATION_CERTIFICATION_RESULT_V1"

GENERATION_CERTIFICATION_READY = "GENERATION_CERTIFICATION_READY"
GENERATION_CERTIFICATION_INCOMPLETE = "GENERATION_CERTIFICATION_INCOMPLETE"
GENERATION_CERTIFICATION_FAILED_CLOSED = "GENERATION_CERTIFICATION_FAILED_CLOSED"
GENERATION_CERTIFIED = "GENERATION_CERTIFIED"

GENERATION_19 = "GENERATION_19"

COMPOSITION_BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "composition_service_only": True,
    "new_certification_engine_created": False,
    "capability_registry_replaced": False,
    "replay_certification_replaced": False,
    "replay_observation_layer_replaced": False,
    "platform_knowledge_replaced": False,
    "human_interface_authority": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "repository_mutated": False,
    "governance_modified": False,
}


def canonical_generation_evidence_profile(
    generation_identifier: str = GENERATION_19,
) -> dict[str, Any]:
    """Return the canonical deterministic evidence profile for a generation."""

    generation = _normalize_generation_identifier(generation_identifier)
    if generation != GENERATION_19:
        raise FailClosedRuntimeError("generation evidence profile failed closed: unknown generation")
    profile = {
        "artifact_type": GENERATION_EVIDENCE_PROFILE_V1,
        "profile_version": GENERATION_CERTIFICATION_COMPOSITION_VERSION,
        "generation_identifier": generation,
        "required_capabilities": [
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        ],
        "required_certification_records": [
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        ],
        "required_governance_artifacts": [
            {"reference": "docs/governance/G19_02_PLATFORM_KNOWLEDGE_RUNTIME_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_06_CANONICAL_PLATFORM_PRESENTATION_LAYER_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_HI_02_GOVERNED_WORK_TYPE_PRESERVATION_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_HI_04_CLARIFICATION_COMPLETION_LIFECYCLE_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_HI_06_FIRST_PASS_CONTEXT_SUFFICIENCY_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_HI_08_PREPARED_WORK_TYPE_RESOLUTION_REFACTORING_IMPLEMENTATION.md"},
            {"reference": "docs/governance/G19_HI_10_GOVERNED_READ_ONLY_RUNTIME_BINDING_IMPLEMENTATION.md"},
        ],
        "required_runtime_evidence": [],
        "required_replay_evidence": [],
        "acceptance_policy": {
            "all_required_capabilities_certified": True,
            "all_required_certification_records_present": True,
            "all_required_governance_artifacts_present": True,
            "all_declared_hashes_match": True,
            "all_required_runtime_evidence_present": True,
            "all_required_replay_evidence_present": True,
            "required_lineage_complete": True,
            "fail_closed_on_contradiction": True,
        },
        "known_observations": [
            "Generation Certification is composed from existing Platform Core evidence.",
            "Durable certification evidence is required before GENERATION_CERTIFIED is emitted.",
        ],
        "supersession_policy": {
            "superseded_capability_rejected": True,
            "superseded_evidence_requires_canonical_replacement": True,
        },
        "durable_certification_evidence": None,
        "profile_authority": "PLATFORM_CORE_CERTIFICATION",
        "human_interface_authority": False,
    }
    profile["profile_hash"] = replay_hash(profile)
    return profile


def compose_generation_certification(
    *,
    generation_identifier: str,
    generation_evidence_profile: dict[str, Any] | None = None,
    query: str | None = None,
    workspace_state: dict[str, Any] | None = None,
    governance_root: str | Path = ".",
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Compose one generation certification result without recording certification."""

    generation = _normalize_generation_identifier(generation_identifier)
    try:
        profile = deepcopy(
            generation_evidence_profile
            if generation_evidence_profile is not None
            else canonical_generation_evidence_profile(generation)
        )
        _validate_profile(profile, generation)
        capabilities = _resolve_capabilities(profile, workspace_state)
        governance = _resolve_governance_artifacts(profile, Path(governance_root))
        runtime = _resolve_embedded_evidence(profile, "required_runtime_evidence", "RUNTIME")
        replay = _resolve_embedded_evidence(profile, "required_replay_evidence", "REPLAY")
        durable = _resolve_durable_certification(profile, generation)
        findings = _findings(capabilities, governance, runtime, replay)
        state = _state(findings, durable)
        failure_reason = None
    except Exception as exc:
        profile = (
            deepcopy(generation_evidence_profile)
            if isinstance(generation_evidence_profile, dict)
            else None
        )
        capabilities, governance, runtime, replay, durable = [], [], [], [], None
        findings = [{"code": "COMPOSITION_FAILED_CLOSED", "detail": str(exc)}]
        state = GENERATION_CERTIFICATION_FAILED_CLOSED
        failure_reason = str(exc) or "generation certification composition failed closed"

    result = {
        "artifact_type": GENERATION_CERTIFICATION_RESULT_V1,
        "runtime_version": GENERATION_CERTIFICATION_COMPOSITION_VERSION,
        "query": query,
        "query_hash": replay_hash(query) if isinstance(query, str) else None,
        "generation_identifier": generation,
        "created_at": _require_string(created_at, "created_at"),
        "certification_status": state,
        "generation_certified": state == GENERATION_CERTIFIED,
        "generation_certification_ready": state in {
            GENERATION_CERTIFICATION_READY,
            GENERATION_CERTIFIED,
        },
        "generation_evidence_profile": profile,
        "generation_evidence_profile_hash": profile.get("profile_hash") if isinstance(profile, dict) else None,
        "capability_certification_evidence": capabilities,
        "governance_evidence": governance,
        "runtime_evidence": runtime,
        "replay_evidence": replay,
        "durable_certification_evidence": durable,
        "completeness_findings": findings,
        "required_evidence_count": _required_count(profile),
        "resolved_evidence_count": _resolved_count(capabilities, governance, runtime, replay),
        "failure_reason": failure_reason,
        "replay_visible": True,
        "replay_modified": False,
        "durable_certification_recorded": durable is not None,
        "reused_platform_core_services": [
            "CAPABILITY_CERTIFICATION_REGISTRY",
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "REPLAY_OBSERVATION_LAYER",
            "REPLAY_CERTIFICATION_RUNTIME",
            "PCCL_CERTIFICATION_METADATA",
            "UNIFIED_PLATFORM_QUERY_ROUTER",
            "CANONICAL_PLATFORM_PRESENTATION_LAYER",
        ],
        **COMPOSITION_BOUNDARY_FLAGS,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def validate_generation_certification_result(result: dict[str, Any]) -> dict[str, Any]:
    """Validate a generation certification composition artifact."""

    if not isinstance(result, dict):
        raise FailClosedRuntimeError("generation certification result must be a dict")
    if result.get("artifact_type") != GENERATION_CERTIFICATION_RESULT_V1:
        raise FailClosedRuntimeError("generation certification result artifact type is invalid")
    if result.get("runtime_version") != GENERATION_CERTIFICATION_COMPOSITION_VERSION:
        raise FailClosedRuntimeError("generation certification result version is invalid")
    if result.get("certification_status") not in {
        GENERATION_CERTIFICATION_READY,
        GENERATION_CERTIFICATION_INCOMPLETE,
        GENERATION_CERTIFICATION_FAILED_CLOSED,
        GENERATION_CERTIFIED,
    }:
        raise FailClosedRuntimeError("generation certification result status is invalid")
    for field, expected in COMPOSITION_BOUNDARY_FLAGS.items():
        if result.get(field) is not expected:
            raise FailClosedRuntimeError("generation certification boundary flags invalid")
    if result.get("generation_certified") is True and result.get("durable_certification_recorded") is not True:
        raise FailClosedRuntimeError("generation certification durable evidence is required")
    _verify_hash(result, "artifact_hash", "generation certification result hash mismatch")
    return deepcopy(result)


def _validate_profile(profile: dict[str, Any], generation: str) -> None:
    if not isinstance(profile, dict) or profile.get("artifact_type") != GENERATION_EVIDENCE_PROFILE_V1:
        raise FailClosedRuntimeError("generation evidence profile artifact type is invalid")
    if profile.get("generation_identifier") != generation:
        raise FailClosedRuntimeError("generation evidence profile identifier mismatch")
    _verify_hash(profile, "profile_hash", "generation evidence profile hash mismatch")
    for field in (
        "required_capabilities",
        "required_certification_records",
        "required_governance_artifacts",
        "required_runtime_evidence",
        "required_replay_evidence",
        "known_observations",
    ):
        if not isinstance(profile.get(field), list):
            raise FailClosedRuntimeError(f"generation evidence profile {field} must be a list")
    if not isinstance(profile.get("acceptance_policy"), dict):
        raise FailClosedRuntimeError("generation evidence profile acceptance policy is required")
    if not isinstance(profile.get("supersession_policy"), dict):
        raise FailClosedRuntimeError("generation evidence profile supersession policy is required")


def _resolve_capabilities(profile: dict[str, Any], workspace_state: dict[str, Any] | None) -> list[dict[str, Any]]:
    required = _unique_strings(
        [*profile["required_capabilities"], *profile["required_certification_records"]]
    )
    resolved = []
    for capability in required:
        record = lookup_platform_capability_certification(capability)
        knowledge = query_platform_knowledge(
            query=f"Where is certified capability {capability} implemented?",
            capability_identifier=capability,
            workspace_state=workspace_state,
        )
        resolved.append(
            {
                "capability_identifier": capability,
                "certified": is_platform_capability_certified(capability),
                "certification_status": record["certification_status"],
                "certification_scope": record["certification_scope"],
                "certification_record_hash": record["certification_record_hash"],
                "certification_evidence": list(record["certification_evidence"]),
                "superseded_by": record["superseded_by"],
                "platform_knowledge_artifact_hash": knowledge["artifact_hash"],
                "lineage_complete": bool(record["certification_evidence"]),
            }
        )
    return resolved


def _resolve_governance_artifacts(profile: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    resolved = []
    for requirement in profile["required_governance_artifacts"]:
        if not isinstance(requirement, dict):
            raise FailClosedRuntimeError("governance evidence requirement must be an object")
        reference = _require_string(requirement.get("reference"), "governance evidence reference")
        path = root / reference
        if not path.is_file():
            resolved.append({"reference": reference, "present": False, "lineage_complete": False})
            continue
        digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        expected = requirement.get("artifact_hash")
        resolved.append(
            {
                "reference": reference,
                "present": True,
                "artifact_hash": digest,
                "expected_artifact_hash": expected,
                "hash_matches": expected is None or expected == digest,
                "lineage_complete": True,
            }
        )
    return resolved


def _resolve_embedded_evidence(profile: dict[str, Any], field: str, evidence_class: str) -> list[dict[str, Any]]:
    resolved = []
    for requirement in profile[field]:
        if not isinstance(requirement, dict):
            raise FailClosedRuntimeError(f"{evidence_class.lower()} evidence requirement must be an object")
        evidence = requirement.get("evidence")
        required_type = requirement.get("artifact_type")
        if not isinstance(evidence, dict):
            resolved.append({"evidence_class": evidence_class, "present": False, "requirement": deepcopy(requirement)})
            continue
        actual_type = evidence.get("artifact_type")
        actual_hash = evidence.get("artifact_hash")
        expected_hash = requirement.get("artifact_hash")
        hash_matches = _hash_matches(evidence, actual_hash) and (
            expected_hash is None or expected_hash == actual_hash
        )
        type_matches = required_type is None or actual_type == required_type
        lineage_complete = evidence.get("replay_lineage_preserved", evidence.get("lineage_complete", True)) is True
        resolved.append(
            {
                "evidence_class": evidence_class,
                "present": True,
                "artifact_type": actual_type,
                "artifact_hash": actual_hash,
                "expected_artifact_hash": expected_hash,
                "type_matches": type_matches,
                "hash_matches": hash_matches,
                "lineage_complete": lineage_complete,
                "replay_observation": actual_type == REPLAY_OBSERVATION_LAYER_ARTIFACT_V1,
                "replay_certification": actual_type == REPLAY_CERTIFICATION_ARTIFACT_V1,
            }
        )
    return resolved


def _resolve_durable_certification(profile: dict[str, Any], generation: str) -> dict[str, Any] | None:
    evidence = profile.get("durable_certification_evidence")
    if evidence is None:
        return None
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("durable certification evidence must be an object")
    if evidence.get("generation_identifier") != generation:
        raise FailClosedRuntimeError("durable certification generation mismatch")
    _require_string(evidence.get("artifact_type"), "durable certification artifact type")
    _require_string(evidence.get("replay_reference"), "durable certification replay reference")
    if evidence.get("certification_status") != GENERATION_CERTIFIED:
        raise FailClosedRuntimeError("durable certification status is invalid")
    if evidence.get("recorded") is not True or evidence.get("replay_visible") is not True:
        raise FailClosedRuntimeError("durable certification evidence is not recorded")
    _verify_hash(evidence, "artifact_hash", "durable certification evidence hash mismatch")
    return deepcopy(evidence)


def _findings(*evidence_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings = []
    for item in evidence_groups[0]:
        if item.get("certified") is not True or item.get("superseded_by") is not None:
            findings.append({"code": "REQUIRED_CAPABILITY_UNCERTIFIED", "reference": item.get("capability_identifier")})
        if item.get("lineage_complete") is not True:
            findings.append({"code": "EVIDENCE_LINEAGE_INCOMPLETE", "reference": item.get("capability_identifier")})
    for group in evidence_groups[1:]:
        for item in group:
            reference = item.get("reference") or item.get("artifact_type") or item.get("evidence_class")
            if item.get("present") is not True:
                findings.append({"code": "REQUIRED_EVIDENCE_MISSING", "reference": reference})
            elif item.get("hash_matches", True) is not True:
                findings.append({"code": "EVIDENCE_HASH_MISMATCH", "reference": reference})
            elif item.get("type_matches", True) is not True:
                findings.append({"code": "EVIDENCE_TYPE_MISMATCH", "reference": reference})
            elif item.get("lineage_complete", True) is not True:
                findings.append({"code": "EVIDENCE_LINEAGE_INCOMPLETE", "reference": reference})
    return findings


def _state(findings: list[dict[str, Any]], durable: dict[str, Any] | None) -> str:
    if any(item["code"] in {"REQUIRED_CAPABILITY_UNCERTIFIED", "EVIDENCE_HASH_MISMATCH", "EVIDENCE_TYPE_MISMATCH", "EVIDENCE_LINEAGE_INCOMPLETE"} for item in findings):
        return GENERATION_CERTIFICATION_FAILED_CLOSED
    if findings:
        return GENERATION_CERTIFICATION_INCOMPLETE
    return GENERATION_CERTIFIED if durable is not None else GENERATION_CERTIFICATION_READY


def _required_count(profile: Any) -> int:
    if not isinstance(profile, dict):
        return 0
    capabilities = _unique_strings(
        [*profile.get("required_capabilities", []), *profile.get("required_certification_records", [])]
    )
    return len(capabilities) + sum(
        len(profile.get(field, []))
        for field in ("required_governance_artifacts", "required_runtime_evidence", "required_replay_evidence")
    )


def _resolved_count(*groups: list[dict[str, Any]]) -> int:
    return sum(1 for group in groups for item in group if item.get("present", True) is True)


def _verify_hash(artifact: dict[str, Any], field: str, message: str) -> None:
    actual = artifact.get(field)
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        raise FailClosedRuntimeError(message)
    body = deepcopy(artifact)
    body.pop(field, None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(message)


def _hash_matches(artifact: dict[str, Any], actual: Any) -> bool:
    if not isinstance(actual, str) or not actual.startswith("sha256:"):
        return False
    body = deepcopy(artifact)
    body.pop("artifact_hash", None)
    return replay_hash(body) == actual


def _normalize_generation_identifier(value: Any) -> str:
    return _require_string(value, "generation_identifier").upper().replace("-", "_").replace(" ", "_")


def _unique_strings(values: list[Any]) -> list[str]:
    return list(dict.fromkeys(_require_string(value, "evidence identifier") for value in values))


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


__all__ = [
    "GENERATION_CERTIFICATION_COMPOSITION_VERSION",
    "GENERATION_CERTIFICATION_FAILED_CLOSED",
    "GENERATION_CERTIFICATION_INCOMPLETE",
    "GENERATION_CERTIFICATION_READY",
    "GENERATION_CERTIFICATION_RESULT_V1",
    "GENERATION_CERTIFIED",
    "GENERATION_EVIDENCE_PROFILE_V1",
    "canonical_generation_evidence_profile",
    "compose_generation_certification",
    "validate_generation_certification_result",
]
