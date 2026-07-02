"""Tests for G9-07 Architectural Health advisory runtime."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.architectural_health_advisory import (
    ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1,
    ARCHITECTURE_REVIEW_REQUIRED,
    INSUFFICIENT_EVIDENCE,
    NO_ADVISORY_FINDINGS,
    create_platform_digital_twin_evidence_bundle,
    generate_architectural_health_advisory,
    reconstruct_architectural_health_advisory_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-02T00:00:00Z"


def _record(**overrides: object) -> dict:
    record = {
        "evidence_id": "EVIDENCE-001",
        "source_path": "docs/governance/G9_04A_SINGLE_FILE_PATCH_LEVEL_MUTATION_ARCHITECTURE_REVIEW_V1.md",
        "source_title": "G9-04A Single-File Patch-Level Mutation Architecture Review V1",
        "milestone_id": "G9-04A",
        "source_class": "architecture_review",
        "status": "confirmed",
        "final_verdict": "SINGLE_FILE_PATCH_LEVEL_MUTATION_ARCHITECTURE_CONFIRMED",
        "component_scope": "single-file patch-level mutation",
        "expected_owner": "Platform Core",
        "observed_owner": "Platform Core",
        "evidence_type": "ownership_boundary",
        "boundary_status": "preserved",
        "responsibility_status": "preserved",
        "replay_status": "present",
        "governance_status": "present",
        "canonical_mapping_status": "consistent",
        "implementation_scope_status": "within_scope",
        "known_gap_status": "visible",
        "replay_reference": "replay:g9-04a",
        "governance_reference": "verdict:SINGLE_FILE_PATCH_LEVEL_MUTATION_ARCHITECTURE_CONFIRMED",
        "canonical_mapping_reference": "mapping:platform-core-owner",
        "validation_evidence": {"git_diff_check": "clean"},
        "known_gaps": [],
    }
    record.update(overrides)
    return record


def _bundle(records: list[dict]) -> dict:
    return create_platform_digital_twin_evidence_bundle(
        bundle_id="PDT-BUNDLE-G9-07-001",
        component_scope="architectural health advisory",
        evidence_records=records,
        created_at=CREATED_AT,
    )


def test_architectural_health_projection_emits_no_findings_with_replay(tmp_path) -> None:
    bundle = _bundle([_record()])

    report = generate_architectural_health_advisory(
        projection_id="AH-PROJECTION-G9-07-001",
        digital_twin_evidence=bundle,
        generated_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_architectural_health_advisory_replay(tmp_path / "replay")

    assert report["projection_type"] == ARCHITECTURAL_HEALTH_ADVISORY_PROJECTION_V1
    assert report["overall_advisory_status"] == NO_ADVISORY_FINDINGS
    assert report["finding_count"] == 0
    assert report["advisory_only"] is True
    assert report["approves_execution"] is False
    assert report["rejects_execution"] is False
    assert report["authorizes_execution"] is False
    assert report["modifies_implementation"] is False
    assert report["triggers_repairs"] is False
    assert report["replaces_governance"] is False
    assert report["replaces_replay"] is False
    assert reconstructed["projection_id"] == report["projection_id"]
    assert reconstructed["replay_artifact_count"] == 1


def test_architectural_health_generates_deterministic_findings_and_severity() -> None:
    records = [
        _record(
            evidence_id="EVIDENCE-BOUNDARY",
            expected_owner="Governance",
            observed_owner="Worker Platform",
            affected_owner="Governance",
            boundary_status="violated",
            responsibility_status="leaked",
        ),
        _record(
            evidence_id="EVIDENCE-REPLAY",
            source_path="docs/governance/G9_06_ARCHITECTURAL_HEALTH_ADVISORY_WORKFLOW_SPECIFICATION_V1.md",
            milestone_id="G9-06",
            replay_status="missing",
            replay_reference="",
        ),
    ]

    report = generate_architectural_health_advisory(
        projection_id="AH-PROJECTION-G9-07-FINDINGS",
        digital_twin_evidence=_bundle(records),
        generated_at=CREATED_AT,
    )

    finding_types = {finding["finding_type"] for finding in report["findings"]}
    severities = {finding["severity"] for finding in report["findings"]}

    assert "responsibility_leakage" in finding_types
    assert "ownership_inconsistency" in finding_types
    assert "architectural_boundary_violation" in finding_types
    assert "missing_replay_evidence" in finding_types
    assert "critical" in severities
    assert report["overall_advisory_status"] == ARCHITECTURE_REVIEW_REQUIRED
    for finding in report["findings"]:
        assert finding["authority_boundary_statement"].endswith("does not certify or authorize.")
        assert finding["recommended_human_review"]


def test_missing_replay_or_governance_evidence_is_advisory_insufficient_evidence() -> None:
    bundle = _bundle(
        [
            _record(
                evidence_id="EVIDENCE-MISSING-GOVERNANCE",
                governance_status="missing",
                governance_reference="",
            )
        ]
    )

    report = generate_architectural_health_advisory(
        projection_id="AH-PROJECTION-G9-07-MISSING",
        digital_twin_evidence=bundle,
        generated_at=CREATED_AT,
    )

    assert report["overall_advisory_status"] == INSUFFICIENT_EVIDENCE
    assert report["findings"][0]["finding_type"] == "missing_governance_evidence"
    assert report["certifies_artifacts"] is False


def test_evidence_order_does_not_change_projection_hash() -> None:
    first = _record(evidence_id="A", source_path="b.md", milestone_id="G9-B")
    second = _record(evidence_id="B", source_path="a.md", milestone_id="G9-A")

    bundle_a = _bundle([first, second])
    bundle_b = _bundle([second, first])
    report_a = generate_architectural_health_advisory(
        projection_id="AH-PROJECTION-G9-07-DETERMINISTIC",
        digital_twin_evidence=bundle_a,
        generated_at=CREATED_AT,
    )
    report_b = generate_architectural_health_advisory(
        projection_id="AH-PROJECTION-G9-07-DETERMINISTIC",
        digital_twin_evidence=bundle_b,
        generated_at=CREATED_AT,
    )

    assert bundle_a["artifact_hash"] == bundle_b["artifact_hash"]
    assert report_a["artifact_hash"] == report_b["artifact_hash"]


def test_tampered_digital_twin_evidence_fails_closed() -> None:
    bundle = _bundle([_record()])
    tampered = deepcopy(bundle)
    tampered["record_count"] = 99

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        generate_architectural_health_advisory(
            projection_id="AH-PROJECTION-G9-07-TAMPERED",
            digital_twin_evidence=tampered,
            generated_at=CREATED_AT,
        )


def test_source_does_not_use_execution_or_repair_surfaces() -> None:
    from pathlib import Path

    source = Path("aigol/runtime/architectural_health_advisory.py").read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "approve_execution" not in source
    assert "trigger_repair" not in source
    assert replay_hash({"source": "inspection"}).startswith("sha256:")
