from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

import aigol.runtime.constitutional_reuse_proof_runtime as reuse_runtime
from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.constitutional_certification_completion_gate import (
    CONSTITUTIONAL_COMPLETION_FAILED_CLOSED,
    create_g48_completion_report_evidence,
    finalize_governed_development_completion,
    reconstruct_constitutional_completion_replay,
)
from aigol.runtime.constitutional_governance_certification import (
    certify_constitutional_governance,
)
from aigol.runtime.constitutional_replay_governance import (
    CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1,
    CONSTITUTIONAL_REPLAY_GOVERNANCE_VERSION,
    REPLAY_RECONSTRUCTION_VERIFIED,
    VALIDATOR_OUTCOME_INTERPRETED,
    ConstitutionalGovernanceAssessment,
    ConstitutionalGovernanceStatus,
)
from aigol.runtime.governance_promotion_discipline import (
    BLOCKED,
    ELIGIBLE,
    GovernancePromotionResult,
    evaluate_governance_promotion,
)
from aigol.runtime.governance_resilience_certification_gate import (
    certify_governance_resilience,
)
from aigol.runtime.governed_development_workflow_runtime import (
    AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.synthetic_cognition_pressure_simulator import (
    generate_ambiguous_contract,
    generate_authority_drift_attempt,
    generate_long_chain_entropy_sequence,
    generate_provider_escalation_attempt,
    generate_replay_corruption_attempt,
)
from aigol.runtime.transport.serialization import replay_hash
from test_g64_06_acli_positive_constitutional_lineage import (
    REQUEST,
    SESSION_ID,
    _args,
    _input_sequence,
    _proof_input,
    _workspace,
)


CREATED_AT = "2026-08-02T12:00:00+00:00"
REPORT_ID = "G64_07_CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_IMPLEMENTATION_REPORT_V1"
VERDICT = "CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_ESTABLISHED"


def _pending_capture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    workspace = _workspace(tmp_path)
    composed = {
        "governance_conformance": {"critical_violations": 0},
        "existing_owners_reused": [
            "PLATFORM_CORE_PROJECT_SERVICES",
            "GOVERNANCE_CONFORMANCE_ENGINE",
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
    }
    composed["composition_evidence_hash"] = replay_hash(composed)
    monkeypatch.setattr(
        reuse_runtime,
        "_compose_existing_owner_evidence",
        lambda **_: deepcopy(composed),
    )
    result = run_interactive_conversation(
        _args(tmp_path, workspace, _proof_input(workspace)),
        input_func=_input_sequence([REQUEST, "APPROVE", "exit"]),
        output_func=lambda _line: None,
    )
    assert result["failed_turns"] == 0
    assert result["turns"][1]["response_status"] == (
        AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION
    )
    replay_files = list(
        (tmp_path / "runtime" / SESSION_ID).glob(
            "TURN-*/acli_governed_development_execution_bridge/"
            "001_acli_governed_development_execution_recorded.json"
        )
    )
    assert len(replay_files) == 1
    bridge = json.loads(replay_files[0].read_text(encoding="utf-8"))["artifact"]
    pending = bridge["workflow_capture"]
    assert pending["execution_status"] == AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION
    assert pending["governed_development_outcome"]["constitutional_completion_reached"] is False
    return pending


def _assessment() -> ConstitutionalGovernanceAssessment:
    seed = {
        "replay_identity": "REPLAY-G64-07",
        "replay_hash": replay_hash("replay-g64-07"),
        "validator_execution_id": "VALIDATOR-G64-07",
        "validator_result_hash": replay_hash("validator-g64-07"),
        "constitutional_status": ConstitutionalGovernanceStatus.COMPLIANT.value,
    }
    assessment = ConstitutionalGovernanceAssessment(
        artifact_type=CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1,
        schema_version="1.0.0",
        governance_version=CONSTITUTIONAL_REPLAY_GOVERNANCE_VERSION,
        assessment_id=(
            "CONSTITUTIONAL-GOVERNANCE-ASSESSMENT-"
            + replay_hash(seed).split(":", 1)[1]
        ),
        replay_identity=seed["replay_identity"],
        replay_hash=seed["replay_hash"],
        validator_execution_id=seed["validator_execution_id"],
        validator_result_hash=seed["validator_result_hash"],
        contract_hash=replay_hash("contract-g64-07"),
        manifest_hash=replay_hash("manifest-g64-07"),
        validator_status="PASS",
        constitutional_status=ConstitutionalGovernanceStatus.COMPLIANT,
        assessment_basis=(
            REPLAY_RECONSTRUCTION_VERIFIED,
            VALIDATOR_OUTCOME_INTERPRETED,
        ),
        failure_codes=(),
    )
    return assessment.with_assessment_hash()


def _promotion(change_id: str) -> GovernancePromotionResult:
    evidence = [
        generate_ambiguous_contract(simulation_id="G64-07-1", created_at="2026-08-02T11:00:00+00:00"),
        generate_authority_drift_attempt(simulation_id="G64-07-2", created_at="2026-08-02T11:00:01+00:00"),
        generate_long_chain_entropy_sequence(simulation_id="G64-07-3", created_at="2026-08-02T11:00:02+00:00", length=4),
        generate_provider_escalation_attempt(simulation_id="G64-07-4", created_at="2026-08-02T11:00:03+00:00"),
        generate_replay_corruption_attempt(simulation_id="G64-07-5", created_at="2026-08-02T11:00:04+00:00"),
    ]
    resilience = certify_governance_resilience(
        certification_id="RESILIENCE-G64-07",
        related_change_id=change_id,
        resilience_suite_version="SYNTHETIC_COGNITION_PRESSURE_SIMULATOR_V1",
        resilience_evidence=evidence,
        created_at="2026-08-02T11:30:00+00:00",
    )
    promotion = evaluate_governance_promotion(
        promotion_id="PROMOTION-G64-07",
        related_change_id=change_id,
        certification=resilience,
        created_at=CREATED_AT,
    )
    assert promotion.promotion_status == ELIGIBLE
    return promotion


def _report(path: Path, *, verdict: str = VERDICT, validation: str = "PASS") -> None:
    path.write_text(
        f"""# 1. Implementation Summary

Generation: G64-07

Report identity:
{REPORT_ID}

Reporting date: 2026-08-02

Constitutional baseline:
AICLI_POSITIVE_CONSTITUTIONAL_LINEAGE_ESTABLISHED

Implementation contracts:
- G48 Constitutional Evidence Reporting Standard V1

# 2. Code Evidence

Externally authored evidence.

# 3. Constitutional Self-Assessment

## Verified

- Certification evidence is external.

## Not Verified

- None within the bounded test fixture.

# 4. Validation Matrix

| Requirement | Result |
|---|---|
| Completion evidence | `{validation}` |

# 5. Repository Mutation Summary

No mutation by certification finalization.

# 6. Certification Verdict

{verdict}
""",
        encoding="utf-8",
    )


def _evidence(path: Path, pending: dict, assessment, certification, promotion):
    _report(path)
    return create_g48_completion_report_evidence(
        report_path=path,
        report_id=REPORT_ID,
        generation="G64-07",
        certification_verdict=VERDICT,
        related_change_id=pending["execution_id"],
        scope_binding_hash=pending["governed_development_outcome"][
            "reuse_proof_g47_scope_binding_hash"
        ],
        governance_assessment_hash=assessment.assessment_hash,
        constitutional_certification_hash=certification.certification_hash,
        promotion_evidence_hash=promotion.evidence_hash,
        created_at=CREATED_AT,
    )


def test_certified_completion_is_terminal_and_replay_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    assessment = _assessment()
    certification = certify_constitutional_governance(assessment)
    promotion = _promotion(pending["execution_id"])
    report_evidence = _evidence(
        tmp_path / "G64_07_REPORT.md",
        pending,
        assessment,
        certification,
        promotion,
    )

    capture = finalize_governed_development_completion(
        finalization_id="G64-07-FINALIZATION",
        governed_development_capture=pending,
        g48_report_evidence=report_evidence,
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=promotion,
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=CREATED_AT,
        replay_dir=tmp_path / "completion-replay",
    )

    assert capture["completion_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert capture["constitutional_completion_reached"] is True
    assert capture["promotion_eligible"] is True
    assert capture["repository_mutated"] is False
    assert capture["worker_invoked"] is False
    replay = reconstruct_constitutional_completion_replay(tmp_path / "completion-replay")
    assert replay["completion_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert replay["replay_artifact_count"] == 6


def test_missing_or_incomplete_g48_certification_never_reaches_completion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    assessment = _assessment()
    certification = certify_constitutional_governance(assessment)
    promotion = _promotion(pending["execution_id"])

    capture = finalize_governed_development_completion(
        finalization_id="G64-07-MISSING-REPORT",
        governed_development_capture=pending,
        g48_report_evidence={},
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=promotion,
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=CREATED_AT,
        replay_dir=tmp_path / "missing-report-replay",
    )
    assert capture["completion_status"] == CONSTITUTIONAL_COMPLETION_FAILED_CLOSED
    assert capture["constitutional_completion_reached"] is False
    assert capture["promotion_eligible"] is False

    report_path = tmp_path / "incomplete-report.md"
    _report(report_path, validation="PARTIAL")
    with pytest.raises(FailClosedRuntimeError, match="VALIDATION_INCOMPLETE"):
        create_g48_completion_report_evidence(
            report_path=report_path,
            report_id=REPORT_ID,
            generation="G64-07",
            certification_verdict=VERDICT,
            related_change_id=pending["execution_id"],
            scope_binding_hash=pending["governed_development_outcome"]["reuse_proof_g47_scope_binding_hash"],
            governance_assessment_hash=assessment.assessment_hash,
            constitutional_certification_hash=certification.certification_hash,
            promotion_evidence_hash=promotion.evidence_hash,
            created_at=CREATED_AT,
        )


def test_blocked_promotion_and_duplicate_finalization_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    assessment = _assessment()
    certification = certify_constitutional_governance(assessment)
    blocked = GovernancePromotionResult(
        promotion_id="PROMOTION-BLOCKED-G64-07",
        related_change_id=pending["execution_id"],
        certification_id="",
        promotion_status=BLOCKED,
        promotion_reason="certification incomplete",
        created_at=CREATED_AT,
    )
    evidence = _evidence(
        tmp_path / "blocked-report.md",
        pending,
        assessment,
        certification,
        blocked,
    )
    replay_dir = tmp_path / "blocked-replay"
    blocked_capture = finalize_governed_development_completion(
        finalization_id="G64-07-BLOCKED",
        governed_development_capture=pending,
        g48_report_evidence=evidence,
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=blocked,
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    assert blocked_capture["completion_status"] == CONSTITUTIONAL_COMPLETION_FAILED_CLOSED
    assert blocked_capture["promotion_eligible"] is False
    duplicate = finalize_governed_development_completion(
        finalization_id="G64-07-DUPLICATE",
        governed_development_capture=pending,
        g48_report_evidence=evidence,
        governance_assessment=assessment,
        constitutional_certification=certification,
        promotion_evidence=blocked,
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    assert duplicate["completion_status"] == CONSTITUTIONAL_COMPLETION_FAILED_CLOSED
    assert "DUPLICATE_FINALIZATION" in duplicate["failure_reason"]
