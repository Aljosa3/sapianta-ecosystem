"""Regression coverage for G16-03 canonical context envelope."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_certification_evidence,
)
from aigol.runtime.platform_core_cognition_layer import (
    CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1,
    PCCL_CONTEXT_ENVELOPE_VERSION,
    PlatformCoreCognitionLayer,
    create_canonical_context_envelope,
    create_pccl_session,
    validate_canonical_context_envelope,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-08T00:00:00Z"


def _session() -> dict:
    return create_pccl_session(
        session_id="PCCL-G16-03-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-03-001",
        replay_reference=".runtime/aicli/g16-03/project_context",
        runtime_reference="RUNTIME-G16-03-001",
        certification_reference="CERT-G16-03-PCCL",
        provider_budget=2,
    )


def _references() -> list[dict[str, str]]:
    return [
        {
            "reference_type": "CANONICAL_SEMANTIC_ARTIFACT",
            "reference": "CSA-G16-03-001",
            "artifact_hash": replay_hash({"artifact": "CSA-G16-03-001"}),
            "certification_reference": "CERT-CSA-G16-03-001",
        },
        {
            "reference_type": "KNOWLEDGE_REUSE",
            "reference": "KNOWLEDGE-REUSE-G16-03-001",
            "artifact_hash": replay_hash({"artifact": "KNOWLEDGE-REUSE-G16-03-001"}),
            "certification_reference": "CERT-KNOWLEDGE-G16-03-001",
        },
        {
            "reference_type": "CLARIFICATION_RESULT",
            "reference": "CLARIFICATION-G16-03-001",
            "artifact_hash": replay_hash({"artifact": "CLARIFICATION-G16-03-001"}),
            "certification_reference": "CERT-CLARIFICATION-G16-03-001",
        },
        {
            "reference_type": "RUNTIME_REFERENCE",
            "reference": "RUNTIME-G16-03-001",
            "artifact_hash": replay_hash({"artifact": "RUNTIME-G16-03-001"}),
            "certification_reference": "CERT-RUNTIME-G16-03-001",
        },
        {
            "reference_type": "REPLAY_REFERENCE",
            "reference": ".runtime/aicli/g16-03/project_context",
            "artifact_hash": replay_hash({"artifact": "REPLAY-G16-03-001"}),
            "certification_reference": "CERT-REPLAY-G16-03-001",
        },
        {
            "reference_type": "GOVERNANCE_REFERENCE",
            "reference": "docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md",
            "artifact_hash": replay_hash({"artifact": "GOVERNANCE-G16-03-001"}),
            "certification_reference": "CERT-GOVERNANCE-G16-03-001",
        },
        {
            "reference_type": "CERTIFICATION_REFERENCE",
            "reference": "CANONICAL_CONTEXT_ENVELOPE",
            "artifact_hash": replay_hash({"artifact": "CERTIFICATION-G16-03-001"}),
            "certification_reference": "CERT-G16-03-PCCL",
        },
    ]


def test_canonical_context_envelope_aggregates_platform_core_references_only() -> None:
    session = _session()
    envelope = create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-03-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=_references(),
    )

    assert envelope["artifact_type"] == CANONICAL_CONTEXT_ENVELOPE_ARTIFACT_V1
    assert envelope["pccl_context_envelope_version"] == PCCL_CONTEXT_ENVELOPE_VERSION
    assert envelope["pccl_session_id"] == session["session_id"]
    assert envelope["pccl_session_hash"] == session["artifact_hash"]
    assert envelope["human_goal_reference"] == "HUMAN-GOAL-G16-03-001"
    assert envelope["context_reference_count"] == 9
    assert "HUMAN_GOAL" in envelope["included_reference_types"]
    assert "PCCL_SESSION" in envelope["included_reference_types"]
    assert envelope["reference_only_envelope"] is True
    assert envelope["context_references_aggregated"] is True
    assert envelope["certified_artifact_payload_embedded"] is False
    assert envelope["semantic_interpretation_performed"] is False
    assert envelope["prompt_generated"] is False
    assert envelope["provider_invoked"] is False
    assert envelope["governance_modified"] is False
    assert envelope["replay_modified"] is False
    assert envelope["artifact_hash"].startswith("sha256:")
    assert validate_canonical_context_envelope(envelope) == envelope


def test_canonical_context_envelope_is_order_independent_and_deduplicated() -> None:
    session = _session()
    first = create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-03-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=_references() + [_references()[0]],
    )
    second = create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-03-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=list(reversed(_references())),
    )

    assert first["context_references"] == second["context_references"]
    assert first["context_reference_count"] == second["context_reference_count"] == 9
    assert first["artifact_hash"] == second["artifact_hash"]


def test_platform_core_cognition_layer_exposes_context_envelope_without_future_behavior() -> None:
    service = PlatformCoreCognitionLayer()
    session = service.create_session(
        session_id="PCCL-G16-03-SERVICE-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-03-SERVICE",
        provider_budget=1,
    )
    envelope = service.create_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-03-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=_references(),
    )

    assert envelope["pccl_session_id"] == "PCCL-G16-03-SERVICE-001"
    assert envelope["provider_invoked"] is False
    assert envelope["proposal_generated"] is False
    assert envelope["policy_evaluated"] is False
    assert envelope["runtime_invoked"] is False
    assert envelope["worker_invoked"] is False


def test_canonical_context_envelope_fails_closed_on_invalid_reference_and_tampering() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unsupported reference type"):
        create_canonical_context_envelope(
            envelope_id="CONTEXT-ENVELOPE-G16-03-BAD-TYPE",
            created_at=CREATED_AT,
            pccl_session=_session(),
            context_references=[{"reference_type": "PROMPT", "reference": "not allowed"}],
        )

    with pytest.raises(FailClosedRuntimeError, match="artifact_hash"):
        create_canonical_context_envelope(
            envelope_id="CONTEXT-ENVELOPE-G16-03-BAD-HASH",
            created_at=CREATED_AT,
            pccl_session=_session(),
            context_references=[
                {
                    "reference_type": "KNOWLEDGE_REUSE",
                    "reference": "KNOWLEDGE-REUSE-G16-03-BAD",
                    "artifact_hash": "not-a-sha256",
                }
            ],
        )

    tampered = deepcopy(
        create_canonical_context_envelope(
            envelope_id="CONTEXT-ENVELOPE-G16-03-TAMPERED",
            created_at=CREATED_AT,
            pccl_session=_session(),
            context_references=_references(),
        )
    )
    tampered["provider_invoked"] = True
    tampered["artifact_hash"] = replay_hash({key: value for key, value in tampered.items() if key != "artifact_hash"})
    with pytest.raises(FailClosedRuntimeError, match="provider_invoked must be false"):
        validate_canonical_context_envelope(tampered)


def test_canonical_context_envelope_registry_certification_is_replay_visible() -> None:
    assert is_platform_capability_certified("CANONICAL_CONTEXT_ENVELOPE") is True
    assert platform_capability_certification_evidence("CANONICAL_CONTEXT_ENVELOPE") == (
        "docs/governance/G16_03_CANONICAL_CONTEXT_ENVELOPE.md",
    )
