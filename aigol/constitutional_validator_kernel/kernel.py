"""Automatic Constitutional Validator Kernel V1.

The kernel authenticates explicit immutable inputs, schedules and evaluates the
certified ECC V1 requirements, and returns one immutable PASS/FAIL result. It
does not persist Replay, assess Governance, perform Certification, authorize,
assign, dispatch, invoke, execute, repair, or mutate any input.
"""

from __future__ import annotations

from typing import Any, Mapping

from .canonical import JsonSource
from .errors import ConstitutionalValidationInputError
from .loaders import (
    AuthenticatedContract,
    AuthenticatedEvidenceManifest,
    load_authenticated_contract,
    load_authenticated_evidence_manifest,
)
from .models import (
    ConstitutionalValidationResult,
    RequirementEvaluationResult,
    ValidationCheck,
    ValidationStatus,
    ValidationTrustAnchors,
)
from .rules import evaluate_rule

VALIDATOR_ID = "AUTOMATIC_CONSTITUTIONAL_VALIDATOR_KERNEL_V1"
VALIDATOR_VERSION = "1.0.0"
RESULT_ARTIFACT_TYPE = "AUTOMATIC_CONSTITUTIONAL_VALIDATION_RESULT_V1"
RESULT_SCHEMA_VERSION = "1.0.0"


def validate_constitutional_evidence(
    *,
    contract_source: JsonSource,
    manifest_source: JsonSource,
    evidence_sources: Mapping[str, JsonSource],
    trust_anchors: ValidationTrustAnchors,
) -> ConstitutionalValidationResult:
    """Validate one authenticated ECC and evidence manifest deterministically."""

    checks: list[ValidationCheck] = []
    try:
        _validate_trust_anchors(trust_anchors)
        contract = load_authenticated_contract(contract_source, trust_anchors)
    except ConstitutionalValidationInputError as exc:
        checks.append(_failed_check("CONTRACT_AUTHENTICATION", exc))
        return _failed_result(
            trust_anchors=trust_anchors,
            checks=checks,
            failure_codes=(exc.code,),
        )
    checks.extend(
        (
            _passed_check(
                "CONTRACT_AUTHENTICATION",
                "CONTRACT_AUTHENTICATED",
                "contract identity and trust anchor match",
            ),
            _passed_check(
                "CONTRACT_INTEGRITY",
                "CONTRACT_INTEGRITY_VERIFIED",
                "contract canonical hash and closed ECC V1 structure verified",
            ),
            _passed_check(
                "REQUIREMENT_SCHEDULING",
                "REQUIREMENTS_SCHEDULED",
                "requirement dependency graph scheduled deterministically",
            ),
        )
    )

    try:
        manifest = load_authenticated_evidence_manifest(
            manifest_source,
            contract=contract,
            evidence_sources=evidence_sources,
            trust_anchors=trust_anchors,
        )
    except ConstitutionalValidationInputError as exc:
        checks.append(_failed_check("EVIDENCE_AUTHENTICATION", exc))
        return _failed_result(
            trust_anchors=trust_anchors,
            contract=contract,
            checks=checks,
            failure_codes=(exc.code,),
        )
    checks.append(
        _passed_check(
            "EVIDENCE_AUTHENTICATION",
            "EVIDENCE_AUTHENTICATED",
            "manifest, evidence, wrappers, Replay references and lineage commitments verified",
        )
    )

    requirement_results = _evaluate_requirements(contract, manifest)
    dependency_failures = tuple(
        result.requirement_id
        for result in requirement_results
        if result.reason_code == "DEPENDENCY_FAILED"
    )
    rule_failures = tuple(
        result.requirement_id
        for result in requirement_results
        if result.status is ValidationStatus.FAIL and result.reason_code != "DEPENDENCY_FAILED"
    )
    if dependency_failures:
        checks.append(
            ValidationCheck(
                phase="DEPENDENCY_EVALUATION",
                status=ValidationStatus.FAIL,
                code="DEPENDENCY_EVALUATION_FAILED",
                detail="one or more requirements have failed dependencies",
            )
        )
    else:
        checks.append(
            _passed_check(
                "DEPENDENCY_EVALUATION",
                "DEPENDENCIES_SATISFIED",
                "all scheduled requirement dependencies passed",
            )
        )
    if rule_failures:
        checks.append(
            ValidationCheck(
                phase="RULE_EVALUATION",
                status=ValidationStatus.FAIL,
                code="RULE_EVALUATION_FAILED",
                detail="one or more constitutional requirement rules failed",
            )
        )
    else:
        checks.append(
            _passed_check(
                "RULE_EVALUATION",
                "RULES_SATISFIED",
                "all evaluated constitutional requirement rules passed",
            )
        )

    failed_requirements = tuple(
        result for result in requirement_results if result.status is ValidationStatus.FAIL
    )
    status = ValidationStatus.FAIL if failed_requirements else ValidationStatus.PASS
    checks.append(
        ValidationCheck(
            phase="PASS_FAIL_DETERMINATION",
            status=status,
            code="VALIDATION_PASSED" if status is ValidationStatus.PASS else "VALIDATION_FAILED",
            detail=(
                "all mandatory constitutional requirements passed"
                if status is ValidationStatus.PASS
                else "at least one mandatory constitutional requirement failed"
            ),
        )
    )
    failure_codes = _ordered_unique(
        result.reason_code for result in failed_requirements
    )
    return _build_result(
        status=status,
        trust_anchors=trust_anchors,
        contract=contract,
        manifest=manifest,
        checks=tuple(checks),
        requirement_results=requirement_results,
        failure_codes=failure_codes,
    )


def _evaluate_requirements(
    contract: AuthenticatedContract,
    manifest: AuthenticatedEvidenceManifest,
) -> tuple[RequirementEvaluationResult, ...]:
    requirements = {
        requirement["requirement_id"]: requirement
        for requirement in contract.data["requirements"]
    }
    statuses: dict[str, ValidationStatus] = {}
    results: list[RequirementEvaluationResult] = []
    evidence = manifest.evidence_by_contract_id
    for requirement_id in contract.schedule:
        requirement = requirements[requirement_id]
        dependencies = tuple(requirement["dependencies"])
        evidence_ids = tuple(
            dict.fromkeys(item["evidence_id"] for item in requirement["evidence"])
        )
        failed_dependencies = tuple(
            dependency
            for dependency in dependencies
            if statuses[dependency] is ValidationStatus.FAIL
        )
        if failed_dependencies:
            result = RequirementEvaluationResult(
                requirement_id=requirement_id,
                status=ValidationStatus.FAIL,
                reason_code="DEPENDENCY_FAILED",
                dependencies=dependencies,
                evidence_ids=evidence_ids,
                evaluation_detail="failed dependencies: " + ",".join(failed_dependencies),
            )
        else:
            evaluation = evaluate_rule(requirement["rule"], evidence)
            status = ValidationStatus.PASS if evaluation.passed else ValidationStatus.FAIL
            criteria = requirement["pass_criteria"] if evaluation.passed else requirement["fail_criteria"]
            result = RequirementEvaluationResult(
                requirement_id=requirement_id,
                status=status,
                reason_code=criteria["reason_code"],
                dependencies=dependencies,
                evidence_ids=evidence_ids,
                evaluation_detail=evaluation.detail,
            )
        statuses[requirement_id] = result.status
        results.append(result)
    return tuple(results)


def _failed_result(
    *,
    trust_anchors: Any,
    checks: list[ValidationCheck],
    failure_codes: tuple[str, ...],
    contract: AuthenticatedContract | None = None,
) -> ConstitutionalValidationResult:
    return _build_result(
        status=ValidationStatus.FAIL,
        trust_anchors=trust_anchors,
        contract=contract,
        manifest=None,
        checks=tuple(checks),
        requirement_results=(),
        failure_codes=failure_codes,
    )


def _build_result(
    *,
    status: ValidationStatus,
    trust_anchors: Any,
    contract: AuthenticatedContract | None,
    manifest: AuthenticatedEvidenceManifest | None,
    checks: tuple[ValidationCheck, ...],
    requirement_results: tuple[RequirementEvaluationResult, ...],
    failure_codes: tuple[str, ...],
) -> ConstitutionalValidationResult:
    contract_data = contract.data if contract is not None else {}
    manifest_data = manifest.data if manifest is not None else {}
    context = manifest_data.get("validation_context", {})
    anchors = (
        trust_anchors
        if isinstance(trust_anchors, ValidationTrustAnchors)
        else ValidationTrustAnchors(
            contract_id="",
            contract_hash="",
            manifest_id="",
            manifest_hash="",
            constitutional_version="",
            platform_core_version="",
        )
    )
    result = ConstitutionalValidationResult(
        artifact_type=RESULT_ARTIFACT_TYPE,
        schema_version=RESULT_SCHEMA_VERSION,
        validator_id=VALIDATOR_ID,
        validator_version=VALIDATOR_VERSION,
        status=status,
        contract_id=str(contract_data.get("contract_id", anchors.contract_id)),
        contract_version=str(contract_data.get("contract_version", "")),
        contract_hash=contract.contract_hash if contract is not None else anchors.contract_hash,
        manifest_id=str(manifest_data.get("manifest_id", anchors.manifest_id)),
        manifest_version=str(manifest_data.get("manifest_version", "")),
        manifest_hash=manifest.manifest_hash if manifest is not None else anchors.manifest_hash,
        validation_id=str(context.get("validation_id", "")),
        invocation_id=str(context.get("invocation_id", "")),
        session_id=str(context.get("session_id", "")),
        chain_id=str(context.get("chain_id", "")),
        scheduled_requirements=contract.schedule if contract is not None else (),
        checks=checks,
        evidence_results=manifest.evidence_results if manifest is not None else (),
        requirement_results=requirement_results,
        failure_codes=failure_codes,
    )
    return result.with_result_hash()


def _validate_trust_anchors(trust_anchors: Any) -> None:
    if not isinstance(trust_anchors, ValidationTrustAnchors):
        raise ConstitutionalValidationInputError(
            "INVALID_TRUST_ANCHORS",
            "validation trust anchors must use the immutable V1 model",
        )
    for field in (
        "contract_id",
        "contract_hash",
        "manifest_id",
        "manifest_hash",
        "constitutional_version",
        "platform_core_version",
    ):
        value = getattr(trust_anchors, field)
        if not isinstance(value, str) or not value.strip():
            raise ConstitutionalValidationInputError(
                "INVALID_TRUST_ANCHORS",
                f"trust anchor {field} must be non-empty",
            )


def _passed_check(phase: str, code: str, detail: str) -> ValidationCheck:
    return ValidationCheck(
        phase=phase,
        status=ValidationStatus.PASS,
        code=code,
        detail=detail,
    )


def _failed_check(phase: str, error: ConstitutionalValidationInputError) -> ValidationCheck:
    return ValidationCheck(
        phase=phase,
        status=ValidationStatus.FAIL,
        code=error.code,
        detail=error.detail,
    )


def _ordered_unique(values: Any) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


__all__ = [
    "RESULT_ARTIFACT_TYPE",
    "RESULT_SCHEMA_VERSION",
    "VALIDATOR_ID",
    "VALIDATOR_VERSION",
    "validate_constitutional_evidence",
]
