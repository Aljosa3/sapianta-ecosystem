"""Replay-owned recording and reconstruction for constitutional Validator results.

This module is deliberately outside ``aigol.constitutional_validator_kernel``.
Callers submit an already immutable Validator result; Platform Replay alone
creates the append-only event and reconstructs it later.  No Governance,
Certification, authorization, Worker, Provider, or execution behavior exists
in this surface.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.constitutional_validator_kernel.canonical import canonical_hash
from aigol.constitutional_validator_kernel.models import (
    ConstitutionalValidationResult,
    ValidationStatus,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION = "AUTOMATIC_CONSTITUTIONAL_VALIDATOR_REPLAY_V1"
CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1 = "CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1"
CONSTITUTIONAL_VALIDATOR_RESULT_V1 = "CONSTITUTIONAL_VALIDATOR_RESULT_V1"
CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED = "CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED"
CONSTITUTIONAL_VALIDATOR_REPLAY_RECONSTRUCTED = "CONSTITUTIONAL_VALIDATOR_REPLAY_RECONSTRUCTED"

CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS = ("constitutional_validator_result_recorded",)
_EVENT_FIELDS = frozenset(
    {
        "artifact_type",
        "schema_version",
        "event_type",
        "replay_service_version",
        "replay_identity",
        "recorded_at",
        "validator_execution_id",
        "validator_result",
        "validator_result_hash",
        "result_summary",
        "lineage_binding",
        "replay_owner",
        "replay_visible",
        "validator_replay_persisted",
        "governance_assessed",
        "certification_performed",
        "authorization_created",
        "worker_assigned",
        "provider_invoked",
        "execution_requested",
        "artifact_hash",
    }
)


def canonical_validator_result(
    validation_result: ConstitutionalValidationResult,
) -> dict[str, Any]:
    """Project one immutable Validator result into its canonical replay model.

    The model is deterministic because every identity is derived from the
    immutable result and no clock, random value, or ambient runtime state is
    consulted.  ``recorded_at`` belongs to the Replay event, not this model.
    """

    if not isinstance(validation_result, ConstitutionalValidationResult):
        raise FailClosedRuntimeError("constitutional Validator replay requires an immutable Validator result")
    result = validation_result.to_dict()
    _verify_validator_result(result)
    execution_id = _validator_execution_id(result)
    requirement_results = result["requirement_results"]
    passed = sum(item["status"] == ValidationStatus.PASS.value for item in requirement_results)
    failed = sum(item["status"] == ValidationStatus.FAIL.value for item in requirement_results)
    canonical = {
        "artifact_type": CONSTITUTIONAL_VALIDATOR_RESULT_V1,
        "schema_version": "1.0.0",
        "validator_execution_id": execution_id,
        "validator_id": result["validator_id"],
        "validator_version": result["validator_version"],
        "contract_id": result["contract_id"],
        "contract_version": result["contract_version"],
        "contract_hash": result["contract_hash"],
        "manifest_id": result["manifest_id"],
        "manifest_version": result["manifest_version"],
        "manifest_hash": result["manifest_hash"],
        "validation_id": result["validation_id"],
        "invocation_id": result["invocation_id"],
        "session_id": result["session_id"],
        "chain_id": result["chain_id"],
        "overall_status": result["status"],
        "rule_count": len(requirement_results),
        "passed_rule_count": passed,
        "failed_rule_count": failed,
        "skipped_rule_count": 0,
        "failure_codes": list(result["failure_codes"]),
        "scheduled_requirements": list(result["scheduled_requirements"]),
        "validator_result": deepcopy(result),
        "validator_result_hash": result["result_hash"],
    }
    canonical["canonical_model_hash"] = replay_hash(canonical)
    return canonical


def record_constitutional_validator_result(
    *,
    validation_result: ConstitutionalValidationResult,
    recorded_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record one immutable Validator result through the Platform Replay owner."""

    replay_path = Path(replay_dir)
    canonical = canonical_validator_result(validation_result)
    recorded = _require_string(recorded_at, "recorded_at")
    _ensure_replay_available(replay_path)
    event = _event_artifact(canonical, recorded)
    wrapper = _wrapper(0, CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS[0], event)
    write_json_immutable(
        replay_path / f"000_{CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS[0]}.json",
        wrapper,
    )
    return {
        "replay_recording_status": CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED,
        "replay_reference": str(replay_path),
        "replay_identity": event["replay_identity"],
        "validator_execution_id": event["validator_execution_id"],
        "validator_result_hash": event["validator_result_hash"],
        "overall_status": event["result_summary"]["overall_status"],
        "replay_visible": True,
        "replay_owner": event["replay_owner"],
        "validator_replay_persisted": False,
        "governance_assessed": False,
        "certification_performed": False,
        "authorization_created": False,
        "worker_assigned": False,
        "provider_invoked": False,
        "execution_requested": False,
        "replay_event": deepcopy(event),
        "replay_hash": wrapper["replay_hash"],
    }


def reconstruct_constitutional_validator_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct ECC -> manifest -> Validator result from one Replay event."""

    replay_path = Path(replay_dir)
    step = CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS[0]
    wrapper = load_json(replay_path / f"000_{step}.json")
    _verify_wrapper(wrapper, 0, step)
    event = wrapper.get("artifact")
    if not isinstance(event, dict):
        raise FailClosedRuntimeError("constitutional Validator replay event is required")
    _verify_event(event)
    canonical = _canonical_from_event(event)
    return {
        "reconstruction_status": CONSTITUTIONAL_VALIDATOR_REPLAY_RECONSTRUCTED,
        "replay_identity": event["replay_identity"],
        "validator_execution_id": event["validator_execution_id"],
        "recorded_at": event["recorded_at"],
        "contract": deepcopy(event["lineage_binding"]["contract"]),
        "evidence_manifest": deepcopy(event["lineage_binding"]["evidence_manifest"]),
        "validator_result": deepcopy(canonical["validator_result"]),
        "validator_result_hash": canonical["validator_result_hash"],
        "result_summary": deepcopy(event["result_summary"]),
        "overall_status": event["result_summary"]["overall_status"],
        "replay_artifact_count": 1,
        "replay_hash": wrapper["replay_hash"],
        "replay_owner": "PLATFORM_CORE_REPLAY",
        "replay_visible": True,
        "governance_assessed": False,
        "certification_performed": False,
        "authorization_created": False,
        "worker_assigned": False,
        "provider_invoked": False,
        "execution_requested": False,
    }


def _event_artifact(canonical: dict[str, Any], recorded_at: str) -> dict[str, Any]:
    lineage = {
        "contract": {
            "contract_id": canonical["contract_id"],
            "contract_version": canonical["contract_version"],
            "contract_hash": canonical["contract_hash"],
        },
        "evidence_manifest": {
            "manifest_id": canonical["manifest_id"],
            "manifest_version": canonical["manifest_version"],
            "manifest_hash": canonical["manifest_hash"],
        },
        "validator_execution_id": canonical["validator_execution_id"],
        "validator_result_hash": canonical["validator_result_hash"],
    }
    event = {
        "artifact_type": CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1,
        "schema_version": "1.0.0",
        "event_type": CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED,
        "replay_service_version": CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION,
        "replay_identity": _replay_identity(canonical),
        "recorded_at": recorded_at,
        "validator_execution_id": canonical["validator_execution_id"],
        "validator_result": deepcopy(canonical["validator_result"]),
        "validator_result_hash": canonical["validator_result_hash"],
        "result_summary": _result_summary(canonical),
        "lineage_binding": lineage,
        "replay_owner": "PLATFORM_CORE_REPLAY",
        "replay_visible": True,
        "validator_replay_persisted": False,
        "governance_assessed": False,
        "certification_performed": False,
        "authorization_created": False,
        "worker_assigned": False,
        "provider_invoked": False,
        "execution_requested": False,
    }
    event["artifact_hash"] = replay_hash(event)
    return event


def _result_summary(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "overall_status": canonical["overall_status"],
        "rule_count": canonical["rule_count"],
        "passed_rule_count": canonical["passed_rule_count"],
        "failed_rule_count": canonical["failed_rule_count"],
        "skipped_rule_count": canonical["skipped_rule_count"],
        "failure_codes": deepcopy(canonical["failure_codes"]),
        "canonical_model_hash": canonical["canonical_model_hash"],
    }


def _canonical_from_event(event: dict[str, Any]) -> dict[str, Any]:
    result = event["validator_result"]
    _verify_validator_result(result)
    execution_id = _validator_execution_id(result)
    if event["validator_execution_id"] != execution_id:
        raise FailClosedRuntimeError("constitutional Validator replay execution identity mismatch")
    canonical = canonical_validator_result(_result_from_dict(result))
    if event["validator_result_hash"] != canonical["validator_result_hash"]:
        raise FailClosedRuntimeError("constitutional Validator replay result hash mismatch")
    if event["replay_identity"] != _replay_identity(canonical):
        raise FailClosedRuntimeError("constitutional Validator replay identity mismatch")
    if event["result_summary"] != _result_summary(canonical):
        raise FailClosedRuntimeError("constitutional Validator replay summary mismatch")
    expected_lineage = _event_artifact(canonical, event["recorded_at"])["lineage_binding"]
    if event["lineage_binding"] != expected_lineage:
        raise FailClosedRuntimeError("constitutional Validator replay lineage mismatch")
    return canonical


def _result_from_dict(result: dict[str, Any]) -> ConstitutionalValidationResult:
    """Use the immutable model solely to reproduce its canonical serialization."""

    from aigol.constitutional_validator_kernel.models import (
        EvidenceAuthenticationResult,
        RequirementEvaluationResult,
        ValidationCheck,
    )

    return ConstitutionalValidationResult(
        artifact_type=result["artifact_type"],
        schema_version=result["schema_version"],
        validator_id=result["validator_id"],
        validator_version=result["validator_version"],
        status=ValidationStatus(result["status"]),
        contract_id=result["contract_id"],
        contract_version=result["contract_version"],
        contract_hash=result["contract_hash"],
        manifest_id=result["manifest_id"],
        manifest_version=result["manifest_version"],
        manifest_hash=result["manifest_hash"],
        validation_id=result["validation_id"],
        invocation_id=result["invocation_id"],
        session_id=result["session_id"],
        chain_id=result["chain_id"],
        scheduled_requirements=tuple(result["scheduled_requirements"]),
        checks=tuple(
            ValidationCheck(
                phase=item["phase"], status=ValidationStatus(item["status"]), code=item["code"], detail=item["detail"]
            )
            for item in result["checks"]
        ),
        evidence_results=tuple(
            EvidenceAuthenticationResult(
                evidence_id=item["evidence_id"],
                evidence_type=item["evidence_type"],
                artifact_reference=item["artifact_reference"],
                artifact_hash=item["artifact_hash"],
                status=ValidationStatus(item["status"]),
            )
            for item in result["evidence_results"]
        ),
        requirement_results=tuple(
            RequirementEvaluationResult(
                requirement_id=item["requirement_id"],
                status=ValidationStatus(item["status"]),
                reason_code=item["reason_code"],
                dependencies=tuple(item["dependencies"]),
                evidence_ids=tuple(item["evidence_ids"]),
                evaluation_detail=item["evaluation_detail"],
            )
            for item in result["requirement_results"]
        ),
        failure_codes=tuple(result["failure_codes"]),
        deterministic=result["deterministic"],
        read_only=result["read_only"],
        authority_effect=result["authority_effect"],
        replay_persisted=result["replay_persisted"],
        governance_assessed=result["governance_assessed"],
        certification_performed=result["certification_performed"],
        result_hash=result["result_hash"],
    )


def _verify_validator_result(result: Any) -> None:
    if not isinstance(result, dict):
        raise FailClosedRuntimeError("constitutional Validator replay result must be an object")
    try:
        model = _result_from_dict(result)
    except (KeyError, TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("constitutional Validator replay result model is invalid") from exc
    if model.to_dict() != result:
        raise FailClosedRuntimeError("constitutional Validator replay result structure mismatch")
    expected = dict(result)
    actual = expected.pop("result_hash", None)
    if not isinstance(actual, str) or actual != canonical_hash(expected):
        raise FailClosedRuntimeError("constitutional Validator replay result hash mismatch")
    if result["deterministic"] is not True or result["read_only"] is not True:
        raise FailClosedRuntimeError("constitutional Validator replay result boundary mismatch")
    if result["authority_effect"] != "NONE":
        raise FailClosedRuntimeError("constitutional Validator replay authority boundary mismatch")
    if any(
        result[field] is not False
        for field in ("replay_persisted", "governance_assessed", "certification_performed")
    ):
        raise FailClosedRuntimeError("constitutional Validator replay result lifecycle boundary mismatch")


def _verify_event(event: dict[str, Any]) -> None:
    if set(event) != _EVENT_FIELDS:
        raise FailClosedRuntimeError("constitutional Validator replay event schema mismatch")
    if event["artifact_type"] != CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1:
        raise FailClosedRuntimeError("constitutional Validator replay event type mismatch")
    if event["schema_version"] != "1.0.0":
        raise FailClosedRuntimeError("constitutional Validator replay schema version mismatch")
    if event["event_type"] != CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED:
        raise FailClosedRuntimeError("constitutional Validator replay event classification mismatch")
    if event["replay_service_version"] != CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION:
        raise FailClosedRuntimeError("constitutional Validator replay service version mismatch")
    for field in ("replay_identity", "recorded_at", "validator_execution_id", "validator_result_hash"):
        _require_string(event[field], field)
    if event["replay_owner"] != "PLATFORM_CORE_REPLAY" or event["replay_visible"] is not True:
        raise FailClosedRuntimeError("constitutional Validator replay ownership mismatch")
    if event["validator_replay_persisted"] is not False:
        raise FailClosedRuntimeError("constitutional Validator cannot claim Replay persistence")
    for field in (
        "governance_assessed",
        "certification_performed",
        "authorization_created",
        "worker_assigned",
        "provider_invoked",
        "execution_requested",
    ):
        if event[field] is not False:
            raise FailClosedRuntimeError("constitutional Validator replay authority boundary mismatch")
    actual = event["artifact_hash"]
    expected = deepcopy(event)
    expected.pop("artifact_hash")
    if not isinstance(actual, str) or actual != replay_hash(expected):
        raise FailClosedRuntimeError("constitutional Validator replay artifact hash mismatch")


def _ensure_replay_available(replay_path: Path) -> None:
    expected = replay_path / f"000_{CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS[0]}.json"
    if expected.exists() or replay_path.exists() and any(replay_path.iterdir()):
        raise FailClosedRuntimeError("constitutional Validator replay already exists")


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "replay_service_version": CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _verify_wrapper(wrapper: Any, index: int, step: str) -> None:
    if not isinstance(wrapper, dict):
        raise FailClosedRuntimeError("constitutional Validator replay wrapper is invalid")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("constitutional Validator replay ordering mismatch")
    if wrapper.get("replay_service_version") != CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION:
        raise FailClosedRuntimeError("constitutional Validator replay wrapper version mismatch")
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or actual != replay_hash(expected):
        raise FailClosedRuntimeError("constitutional Validator replay wrapper hash mismatch")


def _validator_execution_id(result: dict[str, Any]) -> str:
    seed = {
        "validator_id": result["validator_id"],
        "validator_version": result["validator_version"],
        "contract_hash": result["contract_hash"],
        "manifest_hash": result["manifest_hash"],
        "validation_id": result["validation_id"],
        "invocation_id": result["invocation_id"],
        "session_id": result["session_id"],
        "chain_id": result["chain_id"],
        "validator_result_hash": result["result_hash"],
    }
    return "VALIDATOR-EXECUTION-" + replay_hash(seed).split(":", 1)[1]


def _replay_identity(canonical: dict[str, Any]) -> str:
    return "CONSTITUTIONAL-VALIDATOR-REPLAY-" + replay_hash(
        {
            "validator_execution_id": canonical["validator_execution_id"],
            "contract_hash": canonical["contract_hash"],
            "manifest_hash": canonical["manifest_hash"],
            "validator_result_hash": canonical["validator_result_hash"],
        }
    ).split(":", 1)[1]


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"constitutional Validator replay requires {field}")
    return value


__all__ = [
    "CONSTITUTIONAL_VALIDATOR_REPLAY_EVENT_V1",
    "CONSTITUTIONAL_VALIDATOR_REPLAY_RECONSTRUCTED",
    "CONSTITUTIONAL_VALIDATOR_RESULT_RECORDED",
    "CONSTITUTIONAL_VALIDATOR_RESULT_V1",
    "CONSTITUTIONAL_VALIDATOR_REPLAY_STEPS",
    "CONSTITUTIONAL_VALIDATOR_REPLAY_VERSION",
    "canonical_validator_result",
    "record_constitutional_validator_result",
    "reconstruct_constitutional_validator_replay",
]
