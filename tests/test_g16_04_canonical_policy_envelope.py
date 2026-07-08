"""Regression coverage for G16-04 canonical policy envelope."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_certification_evidence,
)
from aigol.runtime.platform_core_cognition_layer import (
    CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1,
    PCCL_POLICY_ENVELOPE_VERSION,
    PlatformCoreCognitionLayer,
    create_canonical_context_envelope,
    create_canonical_policy_envelope,
    create_pccl_session,
    validate_canonical_policy_envelope,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-08T00:00:00Z"


def _session() -> dict:
    return create_pccl_session(
        session_id="PCCL-G16-04-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-04-001",
        replay_reference=".runtime/aicli/g16-04/project_context",
        runtime_reference="RUNTIME-G16-04-001",
        certification_reference="CERT-G16-04-PCCL",
        provider_budget=2,
    )


def _context_envelope(session: dict) -> dict:
    return create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-04-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=[
            {
                "reference_type": "GOVERNANCE_REFERENCE",
                "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                "artifact_hash": replay_hash({"artifact": "GOVERNANCE_ENFORCEMENT_HIERARCHY"}),
                "certification_reference": "CERT-GOVERNANCE-G16-04-001",
            },
            {
                "reference_type": "REPLAY_REFERENCE",
                "reference": ".runtime/aicli/g16-04/project_context",
                "artifact_hash": replay_hash({"artifact": "REPLAY-G16-04-001"}),
                "certification_reference": "CERT-REPLAY-G16-04-001",
            },
        ],
    )


def _policy_references() -> list[dict[str, str]]:
    return [
        {
            "reference_type": "GOVERNANCE_POLICY",
            "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
            "artifact_hash": replay_hash({"artifact": "GOVERNANCE_POLICY_G16_04"}),
            "certification_reference": "CERT-GOVERNANCE-POLICY-G16-04",
        },
        {
            "reference_type": "CONSTITUTIONAL_CONSTRAINT",
            "reference": "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "artifact_hash": replay_hash({"artifact": "CONSTITUTIONAL_CONSTRAINT_G16_04"}),
            "certification_reference": "CERT-CONSTITUTIONAL-G16-04",
        },
        {
            "reference_type": "REPLAY_REQUIREMENT",
            "reference": "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
            "artifact_hash": replay_hash({"artifact": "REPLAY_REQUIREMENT_G16_04"}),
            "certification_reference": "CERT-REPLAY-REQUIREMENT-G16-04",
        },
        {
            "reference_type": "HUMAN_APPROVAL_REQUIREMENT",
            "reference": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "artifact_hash": replay_hash({"artifact": "HUMAN_APPROVAL_REQUIREMENT_G16_04"}),
            "certification_reference": "CERT-HUMAN-APPROVAL-G16-04",
        },
        {
            "reference_type": "PROVIDER_PERMISSION",
            "reference": "PROVIDER_PLATFORM_OPERATIONAL_COMPLETION",
            "artifact_hash": replay_hash({"artifact": "PROVIDER_PERMISSION_G16_04"}),
            "certification_reference": "CERT-PROVIDER-PERMISSION-G16-04",
        },
        {
            "reference_type": "WORKER_BOUNDARY",
            "reference": "WORKER_PLATFORM_EXECUTION_ONLY",
            "artifact_hash": replay_hash({"artifact": "WORKER_BOUNDARY_G16_04"}),
            "certification_reference": "CERT-WORKER-BOUNDARY-G16-04",
        },
        {
            "reference_type": "CERTIFICATION_REQUIREMENT",
            "reference": "CANONICAL_POLICY_ENVELOPE",
            "artifact_hash": replay_hash({"artifact": "CERTIFICATION_REQUIREMENT_G16_04"}),
            "certification_reference": "CERT-G16-04-PCCL",
        },
    ]


def test_canonical_policy_envelope_aggregates_governance_boundary_references_only() -> None:
    session = _session()
    context = _context_envelope(session)
    envelope = create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-04-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=_policy_references(),
    )

    assert envelope["artifact_type"] == CANONICAL_POLICY_ENVELOPE_ARTIFACT_V1
    assert envelope["pccl_policy_envelope_version"] == PCCL_POLICY_ENVELOPE_VERSION
    assert envelope["pccl_session_id"] == session["session_id"]
    assert envelope["pccl_session_hash"] == session["artifact_hash"]
    assert envelope["context_envelope_id"] == context["envelope_id"]
    assert envelope["context_envelope_hash"] == context["artifact_hash"]
    assert envelope["policy_reference_count"] == 9
    assert "PCCL_SESSION" in envelope["included_policy_reference_types"]
    assert "CONTEXT_ENVELOPE" in envelope["included_policy_reference_types"]
    assert envelope["reference_only_envelope"] is True
    assert envelope["policy_references_aggregated"] is True
    assert envelope["governance_policy_payload_embedded"] is False
    assert envelope["policy_executed"] is False
    assert envelope["policy_evaluated"] is False
    assert envelope["authorization_granted"] is False
    assert envelope["governance_invoked"] is False
    assert envelope["provider_invoked"] is False
    assert envelope["worker_invoked"] is False
    assert envelope["artifact_hash"].startswith("sha256:")
    assert validate_canonical_policy_envelope(envelope) == envelope


def test_canonical_policy_envelope_is_order_independent_and_deduplicated() -> None:
    session = _session()
    context = _context_envelope(session)
    first = create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-04-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=_policy_references() + [_policy_references()[0]],
    )
    second = create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-04-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=list(reversed(_policy_references())),
    )

    assert first["policy_references"] == second["policy_references"]
    assert first["policy_reference_count"] == second["policy_reference_count"] == 9
    assert first["artifact_hash"] == second["artifact_hash"]


def test_platform_core_cognition_layer_exposes_policy_envelope_without_policy_execution() -> None:
    service = PlatformCoreCognitionLayer()
    session = service.create_session(
        session_id="PCCL-G16-04-SERVICE-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-04-SERVICE",
        provider_budget=1,
    )
    context = service.create_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-04-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
    )
    envelope = service.create_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-04-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=_policy_references(),
    )

    assert envelope["pccl_session_id"] == "PCCL-G16-04-SERVICE-001"
    assert envelope["policy_executed"] is False
    assert envelope["policy_evaluated"] is False
    assert envelope["authorization_granted"] is False
    assert envelope["governance_invoked"] is False
    assert envelope["provider_invoked"] is False
    assert envelope["worker_invoked"] is False


def test_canonical_policy_envelope_fails_closed_on_invalid_reference_and_context_mismatch() -> None:
    session = _session()
    context = _context_envelope(session)
    with pytest.raises(FailClosedRuntimeError, match="unsupported reference type"):
        create_canonical_policy_envelope(
            policy_envelope_id="POLICY-ENVELOPE-G16-04-BAD-TYPE",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=context,
            policy_references=[{"reference_type": "PROMPT", "reference": "not allowed"}],
        )

    with pytest.raises(FailClosedRuntimeError, match="artifact_hash"):
        create_canonical_policy_envelope(
            policy_envelope_id="POLICY-ENVELOPE-G16-04-BAD-HASH",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=context,
            policy_references=[
                {
                    "reference_type": "GOVERNANCE_POLICY",
                    "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                    "artifact_hash": "not-a-sha256",
                }
            ],
        )

    other_session = create_pccl_session(
        session_id="PCCL-G16-04-OTHER-SESSION",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-04-OTHER",
    )
    with pytest.raises(FailClosedRuntimeError, match="context session mismatch"):
        create_canonical_policy_envelope(
            policy_envelope_id="POLICY-ENVELOPE-G16-04-MISMATCH",
            created_at=CREATED_AT,
            pccl_session=other_session,
            context_envelope=context,
        )


def test_canonical_policy_envelope_fails_closed_on_rehashed_authorization_tampering() -> None:
    session = _session()
    tampered = deepcopy(
        create_canonical_policy_envelope(
            policy_envelope_id="POLICY-ENVELOPE-G16-04-TAMPERED",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=_context_envelope(session),
            policy_references=_policy_references(),
        )
    )
    tampered["authorization_granted"] = True
    tampered["artifact_hash"] = replay_hash({key: value for key, value in tampered.items() if key != "artifact_hash"})
    with pytest.raises(FailClosedRuntimeError, match="authorization_granted must be false"):
        validate_canonical_policy_envelope(tampered)


def test_canonical_policy_envelope_registry_certification_is_replay_visible() -> None:
    assert is_platform_capability_certified("CANONICAL_POLICY_ENVELOPE") is True
    assert platform_capability_certification_evidence("CANONICAL_POLICY_ENVELOPE") == (
        "docs/governance/G16_04_CANONICAL_POLICY_ENVELOPE.md",
    )
