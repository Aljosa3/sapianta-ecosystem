"""Regression coverage for G15-GOVERNANCE-01 capability certification registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    AUDIT,
    CERTIFIED,
    END_TO_END,
    IMPLEMENTATION,
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    RUNTIME,
    VERIFIED,
    is_platform_capability_certified,
    is_platform_capability_superseded,
    list_platform_capability_certifications,
    lookup_platform_capability_certification,
    platform_capability_certification_evidence,
    platform_capability_certification_milestone,
    platform_capability_certification_registry,
    platform_capability_certification_scope,
    platform_capability_component_owner,
    platform_capability_owner,
)


REQUIRED_CAPABILITIES = {
    "REPLAY_OBSERVATION_LAYER",
    "CLARIFICATION_CONTINUITY",
    "CANONICAL_SEMANTIC_ARTIFACT",
    "DISPATCH_REPLAY_REFERENCE_RESOLUTION",
    "REPLAY_CERTIFICATION_RUNTIME",
    "GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END",
    "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
    "PROVIDER_PLATFORM_OPERATIONAL_COMPLETION",
}


def test_registry_exposes_required_generation_15_capabilities() -> None:
    registry = platform_capability_certification_registry()

    assert REQUIRED_CAPABILITIES.issubset(registry)
    assert list(registry) == sorted(registry)
    assert registry["GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END"]["certification_scope"] == END_TO_END
    assert registry["GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END"]["certification_status"] == CERTIFIED
    assert registry["CANONICAL_SEMANTIC_ARTIFACT"]["certification_status"] == VERIFIED
    assert registry["CANONICAL_SEMANTIC_ARTIFACT"]["certification_scope"] == AUDIT


def test_lookup_answers_required_certification_questions() -> None:
    capability_id = "GOVERNED_DEVELOPMENT_RUNTIME_END_TO_END"

    assert is_platform_capability_certified(capability_id) is True
    assert platform_capability_certification_milestone(capability_id) == "G15-RUNTIME-05"
    assert platform_capability_certification_evidence(capability_id) == (
        "docs/governance/G15_RUNTIME_05_END_TO_END_RUNTIME_COMPLETION_VERIFICATION.md",
    )
    assert platform_capability_certification_scope(capability_id) == END_TO_END
    assert is_platform_capability_superseded(capability_id) is False
    assert platform_capability_owner(capability_id) == "PLATFORM_CORE_RUNTIME"
    assert platform_capability_component_owner(capability_id) == "aigol.cli.aigol_cli"


def test_registry_records_are_metadata_only_and_hash_stable() -> None:
    first = lookup_platform_capability_certification("REPLAY_CERTIFICATION_RUNTIME")
    second = lookup_platform_capability_certification("REPLAY_CERTIFICATION_RUNTIME")

    assert first == second
    assert first["certification_record_hash"].startswith("sha256:")
    assert first["governance_metadata_only"] is True
    assert first["governance_report_evidence_authoritative"] is True
    assert first["runtime_execution_authority"] is False
    assert first["human_interface_authority"] is False
    assert first["provider_invoked"] is False
    assert first["worker_invoked"] is False
    assert first["replay_modified"] is False
    assert first["governance_modified"] is False


def test_governance_report_references_exist_and_remain_evidence() -> None:
    for record in list_platform_capability_certifications():
        assert record["certification_version"]
        assert record["certification_status"] in {CERTIFIED, VERIFIED}
        assert record["certification_scope"] in {AUDIT, IMPLEMENTATION, END_TO_END, RUNTIME}
        for evidence in record["certification_evidence"]:
            assert evidence.startswith("docs/governance/")
            assert Path(evidence).exists(), evidence


def test_unknown_capability_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unknown capability"):
        lookup_platform_capability_certification("NOT_A_CERTIFIED_CAPABILITY")


def test_registry_version_is_generation_15_canonical() -> None:
    assert PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION == (
        "G15_GOVERNANCE_01_PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_V1"
    )
