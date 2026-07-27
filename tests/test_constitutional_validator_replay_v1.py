from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import inspect
import json

import pytest

from aigol.constitutional_validator_kernel.models import (
    ConstitutionalValidationResult,
    EvidenceAuthenticationResult,
    RequirementEvaluationResult,
    ValidationCheck,
    ValidationStatus,
)
from aigol.runtime.constitutional_validator_replay import (
    CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED,
    canonical_validator_result,
    record_constitutional_validator_result,
    reconstruct_constitutional_validator_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.constitutional_replay_governance import (
    ConstitutionalGovernanceStatus,
    evaluate_constitutional_replay,
)
from aigol.runtime.constitutional_governance_certification import (
    ConstitutionalCertificationStatus,
    certify_constitutional_governance,
)


RECORDED_AT = "2026-07-27T12:00:00Z"


def _result(status: ValidationStatus = ValidationStatus.PASS) -> ConstitutionalValidationResult:
    requirement_status = status
    reason = "REQUIREMENT_SATISFIED" if status is ValidationStatus.PASS else "REQUIREMENT_VIOLATED"
    result = ConstitutionalValidationResult(
        artifact_type="AUTOMATIC_CONSTITUTIONAL_VALIDATION_RESULT_V1",
        schema_version="1.0.0",
        validator_id="AUTOMATIC_CONSTITUTIONAL_VALIDATOR_KERNEL_V1",
        validator_version="1.0.0",
        status=status,
        contract_id="CERTIFIED-CONTRACT",
        contract_version="1.0.0",
        contract_hash="sha256:" + "a" * 64,
        manifest_id="CERTIFIED-MANIFEST",
        manifest_version="1.0.0",
        manifest_hash="sha256:" + "b" * 64,
        validation_id="VALIDATION-001",
        invocation_id="INVOCATION-001",
        session_id="SESSION-001",
        chain_id="CHAIN-001",
        scheduled_requirements=("REQ-001",),
        checks=(
            ValidationCheck(
                phase="PASS_FAIL_DETERMINATION",
                status=status,
                code="VALIDATION_PASSED" if status is ValidationStatus.PASS else "VALIDATION_FAILED",
                detail="deterministic result",
            ),
        ),
        evidence_results=(
            EvidenceAuthenticationResult(
                evidence_id="PROFILE",
                evidence_type="PROFILE_V1",
                artifact_reference="evidence/profile.json",
                artifact_hash="sha256:" + "c" * 64,
                status=ValidationStatus.PASS,
            ),
        ),
        requirement_results=(
            RequirementEvaluationResult(
                requirement_id="REQ-001",
                status=requirement_status,
                reason_code=reason,
                dependencies=(),
                evidence_ids=("PROFILE",),
                evaluation_detail="deterministic evaluation",
            ),
        ),
        failure_codes=() if status is ValidationStatus.PASS else (reason,),
    )
    return result.with_result_hash()


def test_replay_owner_records_and_reconstructs_one_immutable_validator_result(tmp_path) -> None:
    result = _result()
    before = result.to_dict()

    capture = record_constitutional_validator_result(
        validation_result=result,
        recorded_at=RECORDED_AT,
        replay_dir=tmp_path / "validator-replay",
    )
    reconstructed = reconstruct_constitutional_validator_replay(tmp_path / "validator-replay")

    assert result.to_dict() == before
    assert capture["replay_recording_status"] == CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED
    assert capture["replay_owner"] == "PLATFORM_CORE_REPLAY"
    assert capture["replay_event"]["validator_replay_persisted"] is False
    assert reconstructed["contract"] == {
        "contract_id": "CERTIFIED-CONTRACT",
        "contract_version": "1.0.0",
        "contract_hash": "sha256:" + "a" * 64,
    }
    assert reconstructed["evidence_manifest"] == {
        "manifest_id": "CERTIFIED-MANIFEST",
        "manifest_version": "1.0.0",
        "manifest_hash": "sha256:" + "b" * 64,
    }
    assert reconstructed["validator_result"] == before
    assert reconstructed["overall_status"] == "PASS"
    assert reconstructed["replay_artifact_count"] == 1
    assert all(
        reconstructed[field] is False
        for field in (
            "governance_assessed",
            "certification_performed",
            "authorization_created",
            "worker_assigned",
            "provider_invoked",
            "execution_requested",
        )
    )


def test_canonical_validator_result_is_stable_and_contains_evaluation_summary() -> None:
    first = canonical_validator_result(_result())
    second = canonical_validator_result(_result())

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["rule_count"] == 1
    assert first["passed_rule_count"] == 1
    assert first["failed_rule_count"] == 0
    assert first["skipped_rule_count"] == 0
    assert first["validator_result_hash"] == first["validator_result"]["result_hash"]


def test_fail_result_is_replay_visible_without_governance_or_certification(tmp_path) -> None:
    capture = record_constitutional_validator_result(
        validation_result=_result(ValidationStatus.FAIL),
        recorded_at=RECORDED_AT,
        replay_dir=tmp_path / "failed-validator-replay",
    )
    reconstructed = reconstruct_constitutional_validator_replay(tmp_path / "failed-validator-replay")

    assert capture["overall_status"] == "FAIL"
    assert reconstructed["result_summary"]["failed_rule_count"] == 1
    assert reconstructed["result_summary"]["failure_codes"] == ["REQUIREMENT_VIOLATED"]
    assert reconstructed["governance_assessed"] is False
    assert reconstructed["certification_performed"] is False


def test_replay_is_append_only(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        record_constitutional_validator_result(
            validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
        )


def test_tampered_validator_result_fails_reconstruction(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )
    path = replay_dir / "000_constitutional_validator_result_recorded.json"
    wrapper = load_json(path)
    changed = deepcopy(wrapper)
    changed["artifact"]["validator_result"]["contract_id"] = "SUBSTITUTED-CONTRACT"
    changed["artifact"]["artifact_hash"] = replay_hash(
        {key: value for key, value in changed["artifact"].items() if key != "artifact_hash"}
    )
    changed["replay_hash"] = replay_hash(
        {key: value for key, value in changed.items() if key != "replay_hash"}
    )
    path.write_text(json.dumps(changed), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="result hash mismatch"):
        reconstruct_constitutional_validator_replay(replay_dir)


def test_governance_interprets_verified_replay_without_authority_effect(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )

    assessment = evaluate_constitutional_replay(replay_dir)

    assert assessment.constitutional_status is ConstitutionalGovernanceStatus.COMPLIANT
    assert assessment.validator_status == "PASS"
    assert assessment.governance_assessed is True
    assert assessment.read_only is True
    assert assessment.replay_modified is False
    assert assessment.validator_invoked is False
    assert assessment.certification_performed is False
    assert assessment.authorization_created is False
    assert assessment.worker_assigned is False
    assert assessment.provider_invoked is False
    assert assessment.execution_requested is False
    assert assessment == evaluate_constitutional_replay(replay_dir)


def test_governance_interprets_failed_replay_as_constitutional_non_compliance(tmp_path) -> None:
    replay_dir = tmp_path / "failed-validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(ValidationStatus.FAIL), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )

    assessment = evaluate_constitutional_replay(replay_dir)

    assert assessment.constitutional_status is ConstitutionalGovernanceStatus.NON_COMPLIANT
    assert assessment.failure_codes == ("REQUIREMENT_VIOLATED",)


def test_governance_fails_closed_when_validator_replay_is_tampered(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )
    path = replay_dir / "000_constitutional_validator_result_recorded.json"
    wrapper = load_json(path)
    wrapper["artifact"]["result_summary"]["overall_status"] = "FAIL"
    path.write_text(json.dumps(wrapper), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="wrapper hash mismatch"):
        evaluate_constitutional_replay(replay_dir)


def test_governance_module_is_replay_driven_and_does_not_write_or_invoke_validator() -> None:
    import aigol.runtime.constitutional_replay_governance as replay_governance

    source = inspect.getsource(replay_governance)

    assert "constitutional_validator_kernel" not in source
    assert "write_json_immutable" not in source


def test_certification_consumes_only_a_governance_assessment_without_authority_effect(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )
    assessment = evaluate_constitutional_replay(replay_dir)
    before = assessment.to_dict()

    certification = certify_constitutional_governance(assessment)

    assert assessment.to_dict() == before
    assert certification.certification_status is ConstitutionalCertificationStatus.COMPLIANCE_CERTIFIED
    assert certification.constitutional_status is ConstitutionalGovernanceStatus.COMPLIANT
    assert certification.governance_assessment_hash == assessment.assessment_hash
    assert certification.replay_identity == assessment.replay_identity
    assert certification.certification_performed is True
    assert certification.governance_modified is False
    assert certification.replay_modified is False
    assert certification.validator_invoked is False
    assert certification.evidence_accessed is False
    assert certification.authorization_created is False
    assert certification.worker_assigned is False
    assert certification.provider_invoked is False
    assert certification.execution_requested is False
    assert certification == certify_constitutional_governance(assessment)


def test_certification_certifies_governance_non_compliance_without_execution_effect(tmp_path) -> None:
    replay_dir = tmp_path / "failed-validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(ValidationStatus.FAIL), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )

    certification = certify_constitutional_governance(evaluate_constitutional_replay(replay_dir))

    assert certification.certification_status is ConstitutionalCertificationStatus.NON_COMPLIANCE_CERTIFIED
    assert certification.failure_codes == ("REQUIREMENT_VIOLATED",)
    assert certification.execution_requested is False


def test_certification_fails_closed_when_governance_assessment_is_substituted(tmp_path) -> None:
    replay_dir = tmp_path / "validator-replay"
    record_constitutional_validator_result(
        validation_result=_result(), recorded_at=RECORDED_AT, replay_dir=replay_dir
    )
    assessment = evaluate_constitutional_replay(replay_dir)
    substituted = replace(
        assessment,
        constitutional_status=ConstitutionalGovernanceStatus.NON_COMPLIANT,
    )

    with pytest.raises(FailClosedRuntimeError, match="assessment hash mismatch"):
        certify_constitutional_governance(substituted)

    rehashed_substitution = substituted.with_assessment_hash()
    with pytest.raises(FailClosedRuntimeError, match="assessment identity is invalid"):
        certify_constitutional_governance(rehashed_substitution)


def test_certification_module_has_no_direct_upstream_execution_dependency() -> None:
    import aigol.runtime.constitutional_governance_certification as certification_module

    source = inspect.getsource(certification_module)

    assert "constitutional_validator" not in source
    assert "reconstruct_constitutional" not in source
    assert "write_json_immutable" not in source
