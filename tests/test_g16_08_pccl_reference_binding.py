"""Regression coverage for G16-08 PCCL reference binding."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_certification_evidence,
)
from aigol.runtime.platform_core_cognition_layer import (
    PCCL_REFERENCE_BINDING_ARTIFACT_V1,
    PCCL_REFERENCE_BINDING_VERSION,
    PlatformCoreCognitionLayer,
    create_canonical_context_envelope,
    create_canonical_policy_envelope,
    create_pccl_reference_binding,
    create_pccl_session,
    validate_pccl_reference_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-09T00:00:00Z"


def _session() -> dict:
    return create_pccl_session(
        session_id="PCCL-G16-08-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-08-001",
        replay_reference=".runtime/aicli/g16-08/project_context",
        runtime_reference="RUNTIME-G16-08-001",
        certification_reference="CERT-G16-08-PCCL",
        provider_budget=2,
    )


def _context_envelope(session: dict) -> dict:
    return create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-08-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=[
            {
                "reference_type": "KNOWLEDGE_REUSE",
                "reference": "PROJECT-KNOWLEDGE-REUSE-G16-08",
                "artifact_hash": replay_hash({"artifact": "KNOWLEDGE_REUSE_G16_08"}),
                "certification_reference": "CERT-KNOWLEDGE-REUSE-G16-08",
            }
        ],
    )


def _policy_envelope(session: dict, context: dict) -> dict:
    return create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-08-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=[
            {
                "reference_type": "GOVERNANCE_POLICY",
                "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                "artifact_hash": replay_hash({"artifact": "GOVERNANCE_POLICY_G16_08"}),
                "certification_reference": "CERT-GOVERNANCE-G16-08",
            }
        ],
    )


def _service_references() -> list[dict[str, str]]:
    return [
        {
            "reference_type": "HUMAN_INTENT_RESOLUTION",
            "reference": "aigol.runtime.platform_core_project_services.resolve_development_intent",
            "artifact_hash": replay_hash({"artifact": "HIR_G16_08"}),
            "certification_reference": "G14-19-G14-47",
        },
        {
            "reference_type": "KNOWLEDGE_REUSE",
            "reference": "aigol.runtime.platform_core_project_services.project_knowledge_context_from_workspace",
            "artifact_hash": replay_hash({"artifact": "KNOWLEDGE_REUSE_BINDING_G16_08"}),
            "certification_reference": "G14-08",
        },
        {
            "reference_type": "CLARIFICATION",
            "reference": "PLATFORM_CORE_DETERMINISTIC_CLARIFICATION",
            "artifact_hash": replay_hash({"artifact": "CLARIFICATION_G16_08"}),
            "certification_reference": "G15-HIR",
        },
        {
            "reference_type": "RUNTIME",
            "reference": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "artifact_hash": replay_hash({"artifact": "RUNTIME_ENTRY_G16_08"}),
            "certification_reference": "G14-41",
        },
        {
            "reference_type": "GOVERNANCE",
            "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
            "artifact_hash": replay_hash({"artifact": "GOVERNANCE_G16_08"}),
            "certification_reference": "CERT-GOVERNANCE-G16-08",
        },
        {
            "reference_type": "REPLAY",
            "reference": "aigol.runtime.replay_certification_runtime",
            "artifact_hash": replay_hash({"artifact": "REPLAY_G16_08"}),
            "certification_reference": "G15-REPLAY-01",
        },
        {
            "reference_type": "CERTIFICATION_REGISTRY",
            "reference": "aigol.runtime.platform_capability_certification_registry",
            "artifact_hash": replay_hash({"artifact": "CERTIFICATION_REGISTRY_G16_08"}),
            "certification_reference": "G15-GOVERNANCE-01",
        },
        {
            "reference_type": "PROVIDER_PLATFORM",
            "reference": "aigol.provider.certified_provider_attachment",
            "artifact_hash": replay_hash({"artifact": "PROVIDER_PLATFORM_G16_08"}),
            "certification_reference": "G14-44",
        },
        {
            "reference_type": "WORKER_RESOLUTION",
            "reference": "aigol.runtime.domain_and_worker_resolution_registry",
            "artifact_hash": replay_hash({"artifact": "WORKER_RESOLUTION_G16_08"}),
            "certification_reference": "DOMAIN-WORKER-REGISTRY",
        },
    ]


def _binding() -> dict:
    session = _session()
    context = _context_envelope(session)
    policy = _policy_envelope(session, context)
    return create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-08-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=_service_references(),
    )


def test_pccl_reference_binding_connects_existing_services_by_reference_only() -> None:
    binding = _binding()

    assert binding["artifact_type"] == PCCL_REFERENCE_BINDING_ARTIFACT_V1
    assert binding["pccl_reference_binding_version"] == PCCL_REFERENCE_BINDING_VERSION
    assert binding["reference_only_binding"] is True
    assert binding["platform_core_services_bound"] is True
    assert binding["binding_reference_count"] == 12
    assert "HUMAN_INTENT_RESOLUTION" in binding["included_binding_reference_types"]
    assert "PROVIDER_PLATFORM" in binding["included_binding_reference_types"]
    assert "WORKER_RESOLUTION" in binding["included_binding_reference_types"]
    assert binding["platform_core_service_invoked"] is False
    assert binding["provider_runtime_created"] is False
    assert binding["capability_resolver_created"] is False
    assert binding["capability_resolution_performed"] is False
    assert binding["governance_logic_duplicated"] is False
    assert binding["governance_invoked"] is False
    assert binding["provider_invoked"] is False
    assert binding["worker_invoked"] is False
    assert binding["replay_modified"] is False
    assert binding["prompt_generated"] is False
    assert binding["artifact_hash"].startswith("sha256:")
    assert validate_pccl_reference_binding(binding) == binding


def test_pccl_reference_binding_is_order_independent_and_deduplicated() -> None:
    session = _session()
    context = _context_envelope(session)
    policy = _policy_envelope(session, context)
    first = create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-08-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=_service_references() + [_service_references()[0]],
    )
    second = create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-08-ORDERED",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=list(reversed(_service_references())),
    )

    assert first["binding_references"] == second["binding_references"]
    assert first["binding_reference_count"] == second["binding_reference_count"] == 12
    assert first["artifact_hash"] == second["artifact_hash"]


def test_platform_core_cognition_layer_exposes_reference_binding_without_runtime_behavior() -> None:
    service = PlatformCoreCognitionLayer()
    session = service.create_session(
        session_id="PCCL-G16-08-SERVICE-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-08-SERVICE",
        provider_budget=1,
    )
    context = service.create_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-08-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
    )
    policy = service.create_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-08-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
    )
    binding = service.create_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-08-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=_service_references(),
    )

    assert binding["pccl_session_id"] == "PCCL-G16-08-SERVICE-001"
    assert binding["new_runtime_behavior_introduced"] is False
    assert binding["provider_invoked"] is False
    assert binding["worker_invoked"] is False


def test_pccl_reference_binding_fails_closed_on_invalid_reference_and_mismatched_policy() -> None:
    session = _session()
    context = _context_envelope(session)
    policy = _policy_envelope(session, context)
    with pytest.raises(FailClosedRuntimeError, match="unsupported reference type"):
        create_pccl_reference_binding(
            binding_id="PCCL-REFERENCE-BINDING-G16-08-BAD-TYPE",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=context,
            policy_envelope=policy,
            service_references=[{"reference_type": "PROVIDER_RUNTIME", "reference": "not allowed"}],
        )

    with pytest.raises(FailClosedRuntimeError, match="artifact_hash"):
        create_pccl_reference_binding(
            binding_id="PCCL-REFERENCE-BINDING-G16-08-BAD-HASH",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=context,
            policy_envelope=policy,
            service_references=[
                {
                    "reference_type": "GOVERNANCE",
                    "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                    "artifact_hash": "not-a-sha256",
                }
            ],
        )

    other_session = create_pccl_session(
        session_id="PCCL-G16-08-OTHER-SESSION",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-08-OTHER",
    )
    other_context = _context_envelope(other_session)
    other_policy = _policy_envelope(other_session, other_context)
    with pytest.raises(FailClosedRuntimeError, match="policy session mismatch"):
        create_pccl_reference_binding(
            binding_id="PCCL-REFERENCE-BINDING-G16-08-MISMATCH",
            created_at=CREATED_AT,
            pccl_session=session,
            context_envelope=context,
            policy_envelope=other_policy,
        )


def test_pccl_reference_binding_fails_closed_on_rehashed_provider_invocation_tampering() -> None:
    tampered = deepcopy(_binding())
    tampered["provider_invoked"] = True
    tampered["artifact_hash"] = replay_hash({key: value for key, value in tampered.items() if key != "artifact_hash"})

    with pytest.raises(FailClosedRuntimeError, match="provider_invoked must be false"):
        validate_pccl_reference_binding(tampered)


def test_pccl_reference_binding_registry_certification_is_replay_visible() -> None:
    assert is_platform_capability_certified("PCCL_REFERENCE_BINDING") is True
    assert platform_capability_certification_evidence("PCCL_REFERENCE_BINDING") == (
        "docs/governance/G16_08_PCCL_REFERENCE_BINDING.md",
    )
