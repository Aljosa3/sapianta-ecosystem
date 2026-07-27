from __future__ import annotations

from copy import deepcopy
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
