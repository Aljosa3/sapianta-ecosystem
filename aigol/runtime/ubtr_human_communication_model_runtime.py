"""UBTR-owned canonical human communication model runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


RUNTIME_VERSION = "UBTR_HUMAN_COMMUNICATION_MODEL_RUNTIME_V1"
COMMUNICATION_ARTIFACT_TYPE = "UBTR_CANONICAL_HUMAN_COMMUNICATION_ARTIFACT_V1"
COMMUNICATION_SCHEMA_VERSION = "UBTR_CANONICAL_HUMAN_COMMUNICATION_MODEL_V1"
REPLAY_STEP = "ubtr_human_communication_artifact_recorded"

DOMAIN_UNDERSTANDING = "UNDERSTANDING"
DOMAIN_EXPLANATION = "EXPLANATION"
DOMAIN_RECOMMENDATION = "RECOMMENDATION"
DOMAIN_GUIDANCE = "GUIDANCE"
DOMAIN_HUMAN_CONFIRMATION = "HUMAN_CONFIRMATION"
DOMAIN_TRANSPARENCY = "TRANSPARENCY"
DOMAIN_CONVERSATION = "CONVERSATION"

COMMUNICATION_DOMAINS = {
    DOMAIN_UNDERSTANDING,
    DOMAIN_EXPLANATION,
    DOMAIN_RECOMMENDATION,
    DOMAIN_GUIDANCE,
    DOMAIN_HUMAN_CONFIRMATION,
    DOMAIN_TRANSPARENCY,
    DOMAIN_CONVERSATION,
}

LEVEL_CONCISE = "CONCISE"
LEVEL_STANDARD = "STANDARD"
LEVEL_DETAILED = "DETAILED"
LEVEL_BEGINNER = "BEGINNER"
LEVEL_TECHNICAL = "TECHNICAL"
LEVEL_AUDITOR = "AUDITOR"
LEVEL_EXECUTIVE = "EXECUTIVE"

COMMUNICATION_LEVELS = {
    LEVEL_CONCISE,
    LEVEL_STANDARD,
    LEVEL_DETAILED,
    LEVEL_BEGINNER,
    LEVEL_TECHNICAL,
    LEVEL_AUDITOR,
    LEVEL_EXECUTIVE,
}

SECTION_FIELDS = {
    "understanding": "understanding_section",
    "explanation": "explanation_section",
    "recommendation": "recommendation_section",
    "guidance": "guidance_section",
    "confirmation": "confirmation_section",
    "transparency": "transparency_section",
    "conversation_continuation": "conversation_continuation_section",
}


def create_ubtr_human_communication_artifact(
    *,
    communication_id: str,
    source_component: str,
    target_human_context: str,
    communication_domain: str,
    communication_level: str,
    created_at: str,
    replay_dir: str | Path,
    required_human_action: str,
    replay_lineage: list[dict[str, Any]],
    rollback_reference: str,
    csa_reference: str | None = None,
    csa_hash: str | None = None,
    ocs_reference: str | None = None,
    ocs_hash: str | None = None,
    understanding_section: dict[str, Any] | None = None,
    explanation_section: dict[str, Any] | None = None,
    recommendation_section: dict[str, Any] | None = None,
    guidance_section: dict[str, Any] | None = None,
    confirmation_section: dict[str, Any] | None = None,
    transparency_section: dict[str, Any] | None = None,
    conversation_continuation_section: dict[str, Any] | None = None,
    non_authority_notices: list[str] | None = None,
) -> dict[str, Any]:
    """Create a deterministic, replay-visible, interface-neutral communication artifact."""

    replay_path = Path(replay_dir)
    domain = _require_choice(communication_domain, COMMUNICATION_DOMAINS, "communication_domain")
    level = _require_choice(communication_level, COMMUNICATION_LEVELS, "communication_level")
    sections = _communication_sections(
        understanding_section=understanding_section,
        explanation_section=explanation_section,
        recommendation_section=recommendation_section,
        guidance_section=guidance_section,
        confirmation_section=confirmation_section,
        transparency_section=transparency_section,
        conversation_continuation_section=conversation_continuation_section,
    )
    if not sections:
        raise FailClosedRuntimeError("at least one communication section is required")

    lineage = _require_lineage(replay_lineage)
    source_refs = _source_references(
        csa_reference=csa_reference,
        csa_hash=csa_hash,
        ocs_reference=ocs_reference,
        ocs_hash=ocs_hash,
        sections=sections,
        replay_lineage=lineage,
    )
    artifact = {
        "artifact_type": COMMUNICATION_ARTIFACT_TYPE,
        "schema_version": COMMUNICATION_SCHEMA_VERSION,
        "runtime_version": RUNTIME_VERSION,
        "communication_id": _require_string(communication_id, "communication_id"),
        "source_component": _require_string(source_component, "source_component"),
        "target_human_context": _require_string(target_human_context, "target_human_context"),
        "communication_domain": domain,
        "communication_level": level,
        "source_references": source_refs,
        "sections": sections,
        "sections_rendered": sorted(sections.keys()),
        "required_human_action": _require_string(required_human_action, "required_human_action"),
        "non_authority_notices": _non_authority_notices(non_authority_notices),
        "replay_lineage": lineage,
        "replay_reference": str(replay_path),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "authority_flags": _authority_flags(),
        "interface_neutral": True,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_communication_artifact(artifact)

    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "runtime_version": RUNTIME_VERSION,
        "communication_artifact": deepcopy(artifact),
        "communication_artifact_hash": artifact["artifact_hash"],
        "communication_replay_reference": str(replay_path),
        "communication_domain": domain,
        "communication_level": level,
        "sections_rendered": list(artifact["sections_rendered"]),
        "authority_granted": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "interface_specific_rendering": False,
        "replay_visible": True,
    }


def reconstruct_ubtr_human_communication_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct UBTR human communication replay evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("UBTR human communication replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = _require_mapping(wrapper.get("artifact"), "communication_artifact")
    _validate_communication_artifact(artifact)
    return {
        "runtime_version": RUNTIME_VERSION,
        "communication_artifact": deepcopy(artifact),
        "communication_artifact_hash": artifact["artifact_hash"],
        "communication_replay_reference": str(replay_path),
        "communication_domain": artifact["communication_domain"],
        "communication_level": artifact["communication_level"],
        "sections_rendered": list(artifact["sections_rendered"]),
        "replay_hash": wrapper["replay_hash"],
        "authority_granted": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "interface_specific_rendering": False,
        "replay_visible": True,
    }


def _communication_sections(
    *,
    understanding_section: dict[str, Any] | None,
    explanation_section: dict[str, Any] | None,
    recommendation_section: dict[str, Any] | None,
    guidance_section: dict[str, Any] | None,
    confirmation_section: dict[str, Any] | None,
    transparency_section: dict[str, Any] | None,
    conversation_continuation_section: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    raw = {
        "understanding": understanding_section,
        "explanation": explanation_section,
        "recommendation": recommendation_section,
        "guidance": guidance_section,
        "confirmation": confirmation_section,
        "transparency": transparency_section,
        "conversation_continuation": conversation_continuation_section,
    }
    return {
        key: _optional_mapping(value, SECTION_FIELDS[key])
        for key, value in raw.items()
        if value is not None
    }


def _source_references(
    *,
    csa_reference: str | None,
    csa_hash: str | None,
    ocs_reference: str | None,
    ocs_hash: str | None,
    sections: dict[str, dict[str, Any]],
    replay_lineage: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "csa_reference": _optional_string(csa_reference),
        "csa_hash": _optional_hash(csa_hash, "csa_hash"),
        "ocs_reference": _optional_string(ocs_reference),
        "ocs_hash": _optional_hash(ocs_hash, "ocs_hash"),
        "sections_hash": replay_hash(sections),
        "replay_lineage_hash": replay_hash(replay_lineage),
    }


def _validate_communication_artifact(artifact: dict[str, Any]) -> None:
    candidate = _require_mapping(artifact, "communication_artifact")
    if candidate.get("artifact_type") != COMMUNICATION_ARTIFACT_TYPE:
        raise FailClosedRuntimeError("UBTR human communication artifact type mismatch")
    if candidate.get("schema_version") != COMMUNICATION_SCHEMA_VERSION:
        raise FailClosedRuntimeError("UBTR human communication schema version mismatch")
    for field in (
        "communication_id",
        "source_component",
        "target_human_context",
        "required_human_action",
        "replay_reference",
        "rollback_reference",
        "created_at",
    ):
        _require_string(candidate.get(field), field)
    _require_choice(candidate.get("communication_domain"), COMMUNICATION_DOMAINS, "communication_domain")
    _require_choice(candidate.get("communication_level"), COMMUNICATION_LEVELS, "communication_level")
    _require_mapping(candidate.get("source_references"), "source_references")
    sections = _require_mapping(candidate.get("sections"), "sections")
    if not sections:
        raise FailClosedRuntimeError("communication sections cannot be empty")
    sections_rendered = _string_list(candidate.get("sections_rendered"), "sections_rendered")
    if sections_rendered != sorted(sections.keys()):
        raise FailClosedRuntimeError("communication sections_rendered mismatch")
    _require_lineage(candidate.get("replay_lineage"))
    notices = _string_list(candidate.get("non_authority_notices"), "non_authority_notices")
    if not notices:
        raise FailClosedRuntimeError("non_authority_notices cannot be empty")
    flags = _require_mapping(candidate.get("authority_flags"), "authority_flags")
    for key, value in flags.items():
        if value is not False:
            raise FailClosedRuntimeError(f"UBTR human communication artifact cannot grant {key}")
    if candidate.get("interface_neutral") is not True:
        raise FailClosedRuntimeError("UBTR human communication artifact must be interface-neutral")
    if candidate.get("replay_visible") is not True:
        raise FailClosedRuntimeError("UBTR human communication artifact must be replay-visible")
    actual = candidate.get("artifact_hash")
    expected = deepcopy(candidate)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("UBTR human communication artifact hash mismatch")


def _authority_flags() -> dict[str, bool]:
    return {
        "semantic_authority": False,
        "governance_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "execution_authority": False,
        "mutation_authority": False,
        "provider_authority": False,
        "worker_authority": False,
        "replay_mutation_authority": False,
    }


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("UBTR human communication replay hash mismatch")


def _non_authority_notices(value: list[str] | None) -> list[str]:
    notices = _string_list(value, "non_authority_notices") if value is not None else []
    default = "This UBTR communication artifact explains platform evidence. It does not approve, authorize, execute, invoke providers, invoke workers, or mutate repositories."
    if default not in notices:
        notices.append(default)
    return notices


def _require_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("replay_lineage must be a non-empty list")
    lineage: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError(f"replay_lineage[{index}] must be a JSON object")
        reference = _require_string(item.get("replay_reference"), f"replay_lineage[{index}].replay_reference")
        item_hash = _require_hash(item.get("replay_hash"), f"replay_lineage[{index}].replay_hash")
        copied = deepcopy(item)
        copied["replay_reference"] = reference
        copied["replay_hash"] = item_hash
        lineage.append(copied)
    return lineage


def _require_choice(value: Any, choices: set[str], field_name: str) -> str:
    candidate = _require_string(value, field_name).upper()
    if candidate not in choices:
        raise FailClosedRuntimeError(f"{field_name} is not supported")
    return candidate


def _optional_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _require_hash(value: Any, field_name: str) -> str:
    candidate = _require_string(value, field_name)
    if not candidate.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a sha256 replay hash")
    return candidate


def _optional_hash(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_hash(value, field_name)


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{field_name} must be a list")
    items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if len(items) != len(value):
        raise FailClosedRuntimeError(f"{field_name} must contain only non-empty strings")
    return items
