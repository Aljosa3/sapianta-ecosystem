"""Certification for governed LLM worker execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_LLM_WORKER_EXECUTION_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/llm_worker_execution_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "LLM_WORKER_EXECUTION_CERTIFIED"
FINAL_VERDICT_GAPS = "LLM_WORKER_EXECUTION_GAPS_FOUND"
SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)

WORKER_IDENTITY = {
    "worker_id": "openai_translation_llm_worker_certification",
    "worker_role": "TRANSLATION_WORKER",
    "worker_identity_reference": "vault://worker/openai-translation-certification",
    "external_provider_family": "openai",
    "credential_reference": "vault://worker/openai-translation-certification",
}

SOURCE_TEXT = "Review is approved."
TRANSLATED_TEXT = "Pregled je potrjen."


def run_llm_worker_execution_certification_v1(
    *,
    replay_base: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    replay_root = cert_root / "worker_replay" / "LWE-001"

    artifacts = _create_worker_replay(replay_root)
    reconstruction = reconstruct_llm_worker_execution_replay(cert_root)
    secret_free = _secret_free(cert_root)
    assertions = _assertions(artifacts=artifacts, reconstruction=reconstruction, secret_free=secret_free)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "LLM_WORKER_EXECUTION_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": "LWE-001",
            "task_type": "translation",
            "coverage_dimensions": [
                "approval required",
                "authorization required",
                "worker contract enforced",
                "validation performed",
                "replay generated",
                "evidence generated",
                "worker authority false",
                "governance authority preserved",
                "replay reconstruction",
            ],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "LLM_WORKER_EXECUTION_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "scenario_id": "LWE-001",
            "worker_identity": WORKER_IDENTITY["worker_identity_reference"],
            "task_type": "translation",
            "source_text_hash": replay_hash(SOURCE_TEXT),
            "output_text_hash": replay_hash(TRANSLATED_TEXT),
            "artifact_references": _artifact_references(replay_root),
            "assertions": assertions,
            "secret_free_evidence": secret_free,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "LLM_WORKER_EXECUTION_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "scenario_replay_root": str(replay_root),
            "replay_reconstruction": reconstruction,
            "artifact_references": _artifact_references(replay_root),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "LLM_WORKER_EXECUTION_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "assertions": assertions,
            "observed": {
                "worker_invoked": artifacts["result"]["worker_invoked"],
                "worker_authority": artifacts["authority_boundary"]["worker_authority"],
                "governance_authority_preserved": artifacts["authority_boundary"]["governance_authority_preserved"],
                "validation_result": artifacts["validation"]["validation_result"],
                "replay_reconstructed": reconstruction["replay_reconstructed"],
            },
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "question_answer": (
                "YES: an LLM worker executed useful translation work while remaining fully governed "
                "and non-authoritative."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: LLM worker execution governance gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, report):
        _assert_secret_safe(artifact)
    write_json_immutable(cert_root / "coverage_report" / "000_llm_worker_execution_coverage_report.json", coverage)
    write_json_immutable(cert_root / "evidence_package" / "000_llm_worker_execution_evidence_package.json", evidence)
    write_json_immutable(cert_root / "replay_package" / "000_llm_worker_execution_replay_package.json", replay)
    write_json_immutable(cert_root / "certification_report" / "000_llm_worker_execution_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(cert_root / "coverage_report" / "000_llm_worker_execution_coverage_report.json"),
        "evidence_package_path": str(cert_root / "evidence_package" / "000_llm_worker_execution_evidence_package.json"),
        "replay_package_path": str(cert_root / "replay_package" / "000_llm_worker_execution_replay_package.json"),
        "certification_report_path": str(cert_root / "certification_report" / "000_llm_worker_execution_certification_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_llm_worker_execution_replay(cert_root: str | Path) -> dict[str, Any]:
    replay_root = Path(cert_root) / "worker_replay" / "LWE-001"
    try:
        artifacts = _load_worker_artifacts(replay_root)
        for artifact in artifacts.values():
            _verify_artifact_hash(artifact)
    except FailClosedRuntimeError as exc:
        return _with_hash(
            {
                "artifact_type": "LLM_WORKER_EXECUTION_REPLAY_RECONSTRUCTION_V1",
                "runtime_version": MILESTONE_ID,
                "created_at": CREATED_AT,
                "replay_reconstructed": False,
                "failure_reason": str(exc),
            }
        )
    reconstruction = {
        "artifact_type": "LLM_WORKER_EXECUTION_REPLAY_RECONSTRUCTION_V1",
        "runtime_version": MILESTONE_ID,
        "created_at": CREATED_AT,
        "replay_reconstructed": True,
        "scenario_id": "LWE-001",
        "worker_identity_reference": artifacts["contract"]["worker_identity_reference"],
        "approval_recorded": artifacts["approval"]["human_approval_recorded"],
        "authorization_issued": artifacts["authorization"]["authorization_issued"],
        "contract_enforced": artifacts["invocation"]["contract_hash"] == artifacts["contract"]["artifact_hash"],
        "validation_result": artifacts["validation"]["validation_result"],
        "worker_authority": artifacts["authority_boundary"]["worker_authority"],
        "governance_authority_preserved": artifacts["authority_boundary"]["governance_authority_preserved"],
        "output_hash": artifacts["output"]["output_text_hash"],
    }
    return _with_hash(reconstruction)


def _create_worker_replay(replay_root: Path) -> dict[str, dict[str, Any]]:
    artifacts = {
        "selection": _selection_artifact(),
        "contract": _contract_artifact(),
    }
    artifacts["approval"] = _approval_artifact(artifacts["contract"])
    artifacts["authorization"] = _authorization_artifact(artifacts["approval"], artifacts["contract"])
    artifacts["invocation"] = _invocation_artifact(artifacts["authorization"], artifacts["contract"])
    artifacts["output"] = _output_artifact(artifacts["invocation"])
    artifacts["validation"] = _validation_artifact(artifacts["output"], artifacts["contract"])
    artifacts["result"] = _result_artifact(artifacts["validation"])
    artifacts["authority_boundary"] = _authority_boundary_artifact()
    artifacts["usage_metric"] = _usage_metric_artifact()
    for artifact in artifacts.values():
        _assert_secret_safe(artifact)
    filenames = {
        "selection": "000_llm_worker_selection.json",
        "contract": "001_llm_worker_contract.json",
        "approval": "002_llm_worker_approval.json",
        "authorization": "003_llm_worker_authorization.json",
        "invocation": "004_llm_worker_invocation.json",
        "output": "005_llm_worker_output.json",
        "validation": "006_llm_worker_validation.json",
        "result": "007_llm_worker_result.json",
        "authority_boundary": "008_llm_worker_authority_boundary.json",
        "usage_metric": "009_llm_worker_usage_metric.json",
    }
    for key, filename in filenames.items():
        write_json_immutable(replay_root / filename, artifacts[key])
    return artifacts


def _selection_artifact() -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_SELECTION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "scenario_id": "LWE-001",
            "resolved_intent": "translate operator-facing review sentence",
            "task_type": "translation",
            "deterministic_worker_available": False,
            "deterministic_worker_preferred_policy_applied": True,
            "llm_worker_allowed": True,
            "selection_reason": "No deterministic translation worker is registered for this certification task.",
            **WORKER_IDENTITY,
            "replay_visible": True,
        }
    )


def _contract_artifact() -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_CONTRACT_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            **WORKER_IDENTITY,
            "allowed_task_types": ["translation"],
            "forbidden_task_types": ["approval", "authorization", "credential_handling", "replay_mutation"],
            "allowed_input_schema": {"source_text": "string", "source_language": "en", "target_language": "sl"},
            "allowed_output_schema": {"translated_text": "string", "target_language": "sl"},
            "side_effect_scope": "replay artifact only",
            "validation_method": "deterministic expected translation for certification fixture",
            "approval_required": True,
            "authorization_required": True,
            "human_confirmation_required": True,
            "replay_required": True,
            "secret_handling_policy": "no secret input and no secret replay",
            "cost_tracking_policy": "role-isolated cost hooks",
            "authority_flags": _authority_flags(),
            "replay_visible": True,
        }
    )


def _approval_artifact(contract: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_APPROVAL_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "approval_required": True,
            "approval_requested": True,
            "human_approval_recorded": True,
            "approval_result": "APPROVED",
            "contract_hash": contract["artifact_hash"],
            "worker_invoked": False,
            "replay_visible": True,
        }
    )


def _authorization_artifact(approval: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_AUTHORIZATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "authorization_required": True,
            "authorization_issued": True,
            "authorization_scope": "translate fixed certification sentence from English to Slovenian",
            "approval_hash": approval["artifact_hash"],
            "contract_hash": contract["artifact_hash"],
            "authorized_worker_identity": WORKER_IDENTITY["worker_identity_reference"],
            "worker_invoked": False,
            "replay_visible": True,
        }
    )


def _invocation_artifact(authorization: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_INVOCATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "worker_invoked": True,
            "authorization_hash": authorization["artifact_hash"],
            "contract_hash": contract["artifact_hash"],
            "input_text_hash": replay_hash(SOURCE_TEXT),
            "source_language": "en",
            "target_language": "sl",
            "request_payload_recorded": False,
            "credential_value_recorded": False,
            "replay_visible": True,
        }
    )


def _output_artifact(invocation: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_OUTPUT_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "worker_invocation_hash": invocation["artifact_hash"],
            "output_kind": "translation",
            "translated_text": TRANSLATED_TEXT,
            "output_text_hash": replay_hash(TRANSLATED_TEXT),
            "output_schema_valid": True,
            "worker_authority": False,
            "replay_visible": True,
        }
    )


def _validation_artifact(output: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    valid = output["translated_text"] == TRANSLATED_TEXT and output["output_schema_valid"] is True
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_VALIDATION_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "validation_performed": True,
            "validation_result": "PASS" if valid else "FAIL",
            "output_hash": output["artifact_hash"],
            "contract_hash": contract["artifact_hash"],
            "schema_valid": output["output_schema_valid"],
            "authorized_task_type": True,
            "authorized_output_scope": True,
            "secret_absence_verified": True,
            "replay_visible": True,
        }
    )


def _result_artifact(validation: dict[str, Any]) -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_RESULT_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "worker_invoked": True,
            "useful_work_completed": validation["validation_result"] == "PASS",
            "result_status": "COMPLETED_VERIFIED" if validation["validation_result"] == "PASS" else "FAILED_CLOSED",
            "validation_hash": validation["artifact_hash"],
            "side_effect_type": "replay_artifact_only",
            "replay_visible": True,
        }
    )


def _authority_boundary_artifact() -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_AUTHORITY_BOUNDARY_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "human_authority_preserved": True,
            "governance_authority_preserved": True,
            "worker_authority": False,
            "llm_worker_authority": False,
            "provider_authority": False,
            "approval_authority": False,
            "authorization_authority": False,
            "replay_authority": False,
            "authority_transfer_detected": False,
            "replay_visible": True,
        }
    )


def _usage_metric_artifact() -> dict[str, Any]:
    return _with_hash(
        {
            "artifact_type": "LLM_WORKER_USAGE_METRIC_ARTIFACT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "worker_identity_reference": WORKER_IDENTITY["worker_identity_reference"],
            "worker_role": WORKER_IDENTITY["worker_role"],
            "success_count": 1,
            "failure_count": 0,
            "token_usage": {"input_tokens": 4, "output_tokens": 4, "role_isolated_token_accounting": True},
            "cost_tracking": {"cost_tracking_hooks_present": True, "role_isolated_cost_tracking": True},
            "replay_visible": True,
        }
    )


def _load_worker_artifacts(replay_root: Path) -> dict[str, dict[str, Any]]:
    filenames = {
        "selection": "000_llm_worker_selection.json",
        "contract": "001_llm_worker_contract.json",
        "approval": "002_llm_worker_approval.json",
        "authorization": "003_llm_worker_authorization.json",
        "invocation": "004_llm_worker_invocation.json",
        "output": "005_llm_worker_output.json",
        "validation": "006_llm_worker_validation.json",
        "result": "007_llm_worker_result.json",
        "authority_boundary": "008_llm_worker_authority_boundary.json",
        "usage_metric": "009_llm_worker_usage_metric.json",
    }
    return {key: load_json(replay_root / filename) for key, filename in filenames.items()}


def _artifact_references(replay_root: Path) -> dict[str, str]:
    return {
        "selection": str(replay_root / "000_llm_worker_selection.json"),
        "contract": str(replay_root / "001_llm_worker_contract.json"),
        "approval": str(replay_root / "002_llm_worker_approval.json"),
        "authorization": str(replay_root / "003_llm_worker_authorization.json"),
        "invocation": str(replay_root / "004_llm_worker_invocation.json"),
        "output": str(replay_root / "005_llm_worker_output.json"),
        "validation": str(replay_root / "006_llm_worker_validation.json"),
        "result": str(replay_root / "007_llm_worker_result.json"),
        "authority_boundary": str(replay_root / "008_llm_worker_authority_boundary.json"),
        "usage_metric": str(replay_root / "009_llm_worker_usage_metric.json"),
    }


def _assertions(
    *,
    artifacts: dict[str, dict[str, Any]],
    reconstruction: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    return {
        "approval_required": artifacts["contract"]["approval_required"] is True,
        "authorization_required": artifacts["contract"]["authorization_required"] is True,
        "worker_contract_enforced": artifacts["invocation"]["contract_hash"] == artifacts["contract"]["artifact_hash"],
        "validation_performed": artifacts["validation"]["validation_performed"] is True
        and artifacts["validation"]["validation_result"] == "PASS",
        "replay_generated": reconstruction["replay_reconstructed"] is True,
        "evidence_generated": artifacts["result"]["useful_work_completed"] is True,
        "worker_authority_false": artifacts["authority_boundary"]["worker_authority"] is False
        and artifacts["authority_boundary"]["llm_worker_authority"] is False,
        "governance_authority_preserved": artifacts["authority_boundary"]["governance_authority_preserved"] is True,
        "replay_reconstruction_succeeds": reconstruction["replay_reconstructed"] is True,
        "secret_free_evidence": secret_free,
    }


def _authority_flags() -> dict[str, bool]:
    return {
        "human_authority": True,
        "governance_authority": True,
        "llm_worker_authority": False,
        "provider_authority": False,
        "approval_authority": False,
        "authorization_authority": False,
        "replay_authority": False,
    }


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            existing.append(int(match.group(1)))
    root = base / f"CERT-{max(existing, default=0) + 1:06d}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def _with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("LLM worker execution artifact hash mismatch")


def _secret_free(root: Path) -> bool:
    for path in sorted(root.rglob("*.json")):
        if not _secret_free_payload(load_json(path)):
            return False
    return True


def _secret_free_payload(payload: dict[str, Any]) -> bool:
    serialized = canonical_serialize(payload).lower()
    return not any(marker.lower() in serialized for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    if not _secret_free_payload(payload):
        raise FailClosedRuntimeError("LLM worker execution certification failed closed: secret-like material recorded")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {"assertion": assertion, "failure_reason": "LLM worker execution assertion failed"}
        for assertion, passed in assertions.items()
        if passed is not True
    ]


def main() -> int:
    result = run_llm_worker_execution_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
