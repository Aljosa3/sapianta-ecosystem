"""Tests for UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_V1."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.universal_translation_artifact_schema import (
    GOVERNANCE_ONLY,
    GOVERNANCE_TO_HUMAN,
    HIGH,
    HUMAN_TO_GOVERNANCE,
    MATERIAL_AMBIGUITY,
    UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_VERSION,
    UNIVERSAL_TRANSLATION_ARTIFACT_TYPE,
    authority_flags_for_translation,
    create_universal_translation_artifact,
    translation_artifact_hash,
    validate_universal_translation_artifact,
)


CREATED_AT = "2026-06-25T00:00:00Z"


def _translation_request() -> dict:
    return {
        "translation_request_id": "TRANSLATION-REQUEST-001",
        "operator_context": "test-operator",
        "created_at": CREATED_AT,
    }


def test_human_to_governance_translation_artifact_is_valid_and_hash_stable() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-001",
        translation_request=_translation_request(),
        source_direction=HUMAN_TO_GOVERNANCE,
        source_payload={"human_prompt": "Create security artifact INCIDENT_REVIEW_V1."},
        normalized_intent={"intent_family": "SECURITY_ARTIFACT_CREATION"},
        translated_governance_payload={
            "domain_candidate": "SECURITY",
            "workflow_candidate": "SECURITY_GOVERNED_ARTIFACT_WORKFLOW",
            "approval_required": True,
        },
        ambiguity_flags={"ambiguity_status": "NO_AMBIGUITY", "clarification_required": False, "clarification_questions": []},
        confidence=HIGH,
        replay_reference="/tmp/replay/translation-001",
        created_at=CREATED_AT,
    )

    validated = validate_universal_translation_artifact(artifact)
    without_hash = deepcopy(validated)
    artifact_hash = without_hash.pop("artifact_hash")

    assert validated["artifact_type"] == UNIVERSAL_TRANSLATION_ARTIFACT_TYPE
    assert validated["schema_version"] == UNIVERSAL_TRANSLATION_ARTIFACT_SCHEMA_VERSION
    assert validated["source_direction"] == HUMAN_TO_GOVERNANCE
    assert validated["authority_flags"] == authority_flags_for_translation()
    assert validated["provider_metadata"]["provider_used"] is False
    assert validated["deterministic_fallback_status"]["fallback_used"] is False
    assert artifact_hash == replay_hash(without_hash)
    assert translation_artifact_hash(validated) == artifact_hash


def test_governance_to_human_translation_artifact_is_valid() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-002",
        translation_request=_translation_request(),
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={"workflow_state": "APPROVAL_REQUIRED"},
        normalized_intent={"intent_family": "GOVERNED_DEVELOPMENT"},
        human_readable_payload={
            "summary": "ACLI is waiting for your approval.",
            "next_action": "APPROVE, REJECT, or REQUEST_MODIFICATION",
        },
        confidence=GOVERNANCE_ONLY,
        deterministic_fallback_status={
            "fallback_used": True,
            "fallback_reason": "PROVIDER_DISABLED_BY_CONFIGURATION",
            "deterministic_rule_ids": ["GOVERNANCE_STATE_APPROVAL_REQUIRED_V1"],
        },
        replay_reference="/tmp/replay/translation-002",
        created_at=CREATED_AT,
    )

    validated = validate_universal_translation_artifact(artifact)

    assert validated["source_direction"] == GOVERNANCE_TO_HUMAN
    assert validated["human_readable_payload"]["summary"] == "ACLI is waiting for your approval."
    assert validated["deterministic_fallback_status"]["fallback_used"] is True
    assert validated["confidence"] == GOVERNANCE_ONLY


def test_provider_metadata_supports_comparison_without_authority() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-003",
        translation_request=_translation_request(),
        source_direction=HUMAN_TO_GOVERNANCE,
        source_payload={"human_prompt": "Review this security incident."},
        normalized_intent={"intent_family": "SECURITY_REVIEW"},
        translated_governance_payload={"domain_candidate": "SECURITY", "clarification_required": True},
        ambiguity_flags={
            "ambiguity_status": MATERIAL_AMBIGUITY,
            "clarification_required": True,
            "clarification_questions": ["Which incident should ACLI review?"],
        },
        confidence="MEDIUM",
        provider_metadata={
            "provider_used": True,
            "provider_count": 2,
            "providers": [
                {"provider_id": "provider-a", "role": "TRANSLATION_PROVIDER", "authority_granted": False},
                {"provider_id": "provider-b", "role": "TRANSLATION_PROVIDER", "authority_granted": False},
            ],
            "comparison_used": True,
        },
        replay_reference="/tmp/replay/translation-003",
        created_at=CREATED_AT,
    )

    validated = validate_universal_translation_artifact(artifact)

    assert validated["provider_metadata"]["provider_used"] is True
    assert validated["provider_metadata"]["comparison_used"] is True
    assert validated["authority_flags"]["provider_authority"] is False


def test_translation_artifact_rejects_authority_grant() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-004",
        translation_request=_translation_request(),
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={"workflow_state": "APPROVAL_REQUIRED"},
        normalized_intent={},
        human_readable_payload={"summary": "Waiting for approval."},
        confidence=HIGH,
        replay_reference="/tmp/replay/translation-004",
        created_at=CREATED_AT,
    )
    artifact["authority_flags"]["approval_authority"] = True
    artifact["artifact_hash"] = replay_hash({k: v for k, v in artifact.items() if k != "artifact_hash"})

    with pytest.raises(FailClosedRuntimeError, match="cannot grant authority"):
        validate_universal_translation_artifact(artifact)


def test_translation_artifact_rejects_hash_mismatch() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-005",
        translation_request=_translation_request(),
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={"workflow_state": "APPROVAL_REQUIRED"},
        normalized_intent={},
        human_readable_payload={"summary": "Waiting for approval."},
        confidence=HIGH,
        replay_reference="/tmp/replay/translation-005",
        created_at=CREATED_AT,
    )
    artifact["human_readable_payload"]["summary"] = "Tampered."

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_universal_translation_artifact(artifact)


def test_direction_specific_payload_requirements_fail_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="requires governance payload"):
        create_universal_translation_artifact(
            translation_id="TRANSLATION-006",
            translation_request=_translation_request(),
            source_direction=HUMAN_TO_GOVERNANCE,
            source_payload={"human_prompt": "Create something."},
            normalized_intent={},
            confidence=HIGH,
            replay_reference="/tmp/replay/translation-006",
            created_at=CREATED_AT,
        )

    with pytest.raises(FailClosedRuntimeError, match="requires human-readable payload"):
        create_universal_translation_artifact(
            translation_id="TRANSLATION-007",
            translation_request=_translation_request(),
            source_direction=GOVERNANCE_TO_HUMAN,
            source_payload={"workflow_state": "APPROVAL_REQUIRED"},
            normalized_intent={},
            confidence=HIGH,
            replay_reference="/tmp/replay/translation-007",
            created_at=CREATED_AT,
        )


def test_malformed_artifacts_fail_closed() -> None:
    artifact = create_universal_translation_artifact(
        translation_id="TRANSLATION-008",
        translation_request=_translation_request(),
        source_direction=GOVERNANCE_TO_HUMAN,
        source_payload={"workflow_state": "APPROVAL_REQUIRED"},
        normalized_intent={},
        human_readable_payload={"summary": "Waiting for approval."},
        confidence=HIGH,
        replay_reference="/tmp/replay/translation-008",
        created_at=CREATED_AT,
    )

    missing_field = deepcopy(artifact)
    missing_field.pop("confidence")
    with pytest.raises(FailClosedRuntimeError, match="malformed structure"):
        validate_universal_translation_artifact(missing_field)

    bad_provider_count = deepcopy(artifact)
    bad_provider_count["provider_metadata"]["provider_count"] = 1
    bad_provider_count["artifact_hash"] = replay_hash(
        {k: v for k, v in bad_provider_count.items() if k != "artifact_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="provider_count mismatch"):
        validate_universal_translation_artifact(bad_provider_count)

    bad_serialization = deepcopy(artifact)
    bad_serialization["source_payload"] = {"bad": object()}
    with pytest.raises(FailClosedRuntimeError, match="JSON serializable"):
        validate_universal_translation_artifact(bad_serialization)
