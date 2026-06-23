"""Certification for replay reproducibility across governed AiGOL executions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.llm_worker_execution_certification_v1 import reconstruct_llm_worker_execution_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_operational_readiness_certification_v1 import (
    reconstruct_multi_provider_operational_readiness_replay,
)
from aigol.runtime.product1_audit_review_certification_v1 import (
    reconstruct_product1_audit_review_certification_v1,
)
from aigol.runtime.product1_end_to_end_certification_v1 import (
    reconstruct_product1_end_to_end_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_selection_certification_v1 import reconstruct_worker_selection_replay


MILESTONE_ID = "AIGOL_REPLAY_REPRODUCIBILITY_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/replay_reproducibility_certification_v1")
CREATED_AT = "2026-06-23T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "REPLAY_REPRODUCIBILITY_CERTIFIED"
FINAL_VERDICT_GAPS = "REPLAY_REPRODUCIBILITY_GAPS_FOUND"
SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


def run_replay_reproducibility_certification_v1(
    *,
    replay_base: str | Path | None = None,
    product1_cert_root: str | Path | None = None,
    worker_selection_cert_root: str | Path | None = None,
    llm_worker_cert_root: str | Path | None = None,
    multi_provider_cert_root: str | Path | None = None,
    audit_review_cert_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    roots = _source_roots(
        product1_cert_root=product1_cert_root,
        worker_selection_cert_root=worker_selection_cert_root,
        llm_worker_cert_root=llm_worker_cert_root,
        multi_provider_cert_root=multi_provider_cert_root,
        audit_review_cert_root=audit_review_cert_root,
    )
    reconstruction = _reconstruct_sources(roots)
    source_reports = _source_reports(roots)
    summaries = _reproducibility_summaries(roots, reconstruction, source_reports)
    secret_free = _source_and_generated_secret_free(roots)
    assertions = _assertions(roots=roots, reconstruction=reconstruction, source_reports=source_reports, summaries=summaries, secret_free=secret_free)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "REPLAY_REPRODUCIBILITY_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "coverage_dimensions": [
                "workflow path reconstruction",
                "worker selection reconstruction",
                "approval chain reconstruction",
                "authorization chain reconstruction",
                "validation outcome reconstruction",
                "multi-provider participation reconstruction",
                "audit review reconstruction",
                "hidden authority absence",
                "audit sufficiency",
            ],
            "source_roots": {key: str(value) for key, value in roots.items()},
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "REPLAY_REPRODUCIBILITY_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "source_roots": {key: str(value) for key, value in roots.items()},
            "source_final_verdicts": {
                key: value.get("final_verdict") for key, value in source_reports.items()
            },
            "reproducibility_summaries": summaries,
            "assertions": assertions,
            "secret_free_evidence": secret_free,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "REPLAY_REPRODUCIBILITY_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "source_roots": {key: str(value) for key, value in roots.items()},
            "reconstruction_hashes": {
                key: replay_hash(value) for key, value in reconstruction.items()
            },
            "replay_reconstructed": all(_reconstruction_ok(value) for value in reconstruction.values()),
            "final_verdict": final_verdict,
        }
    )
    reproducibility = _with_hash(
        {
            "artifact_type": "REPLAY_REPRODUCIBILITY_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": "Can an independent reviewer reconstruct the governed decision path from replay evidence alone?",
            "answer": final_verdict == FINAL_VERDICT_CERTIFIED,
            "workflow_path": summaries["workflow_path"],
            "worker_selection": summaries["worker_selection"],
            "approval_chain": summaries["approval_chain"],
            "authorization_chain": summaries["authorization_chain"],
            "validation_chain": summaries["validation_chain"],
            "hidden_authority_source_exists": not assertions["no_hidden_authority_source_exists"],
            "audit_reconstruction_sufficient": assertions["replay_sufficient_for_audit_reconstruction"],
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "REPLAY_REPRODUCIBILITY_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "reproducibility_report_hash": reproducibility["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "question_answer": (
                "YES: an independent reviewer can reconstruct the governed decision path from replay evidence alone."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: replay reproducibility gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, reproducibility, report):
        _assert_secret_safe(artifact)
    write_json_immutable(cert_root / "coverage_report" / "000_replay_reproducibility_coverage_report.json", coverage)
    write_json_immutable(cert_root / "evidence_package" / "000_replay_reproducibility_evidence_package.json", evidence)
    write_json_immutable(cert_root / "replay_package" / "000_replay_reproducibility_replay_package.json", replay)
    write_json_immutable(cert_root / "reproducibility_report" / "000_replay_reproducibility_report.json", reproducibility)
    write_json_immutable(cert_root / "certification_report" / "000_replay_reproducibility_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "coverage_report_path": str(cert_root / "coverage_report" / "000_replay_reproducibility_coverage_report.json"),
        "evidence_package_path": str(cert_root / "evidence_package" / "000_replay_reproducibility_evidence_package.json"),
        "replay_package_path": str(cert_root / "replay_package" / "000_replay_reproducibility_replay_package.json"),
        "reproducibility_report_path": str(cert_root / "reproducibility_report" / "000_replay_reproducibility_report.json"),
        "certification_report_path": str(cert_root / "certification_report" / "000_replay_reproducibility_certification_report.json"),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _source_roots(
    *,
    product1_cert_root: str | Path | None,
    worker_selection_cert_root: str | Path | None,
    llm_worker_cert_root: str | Path | None,
    multi_provider_cert_root: str | Path | None,
    audit_review_cert_root: str | Path | None,
) -> dict[str, Path]:
    return {
        "product1": Path(product1_cert_root) if product1_cert_root else _latest_cert_root(Path("runtime/product1_end_to_end_certification_v1")),
        "worker_selection": Path(worker_selection_cert_root)
        if worker_selection_cert_root
        else _latest_cert_root(Path("runtime/worker_selection_certification_v1")),
        "llm_worker": Path(llm_worker_cert_root) if llm_worker_cert_root else _latest_cert_root(Path("runtime/llm_worker_execution_certification_v1")),
        "multi_provider": Path(multi_provider_cert_root)
        if multi_provider_cert_root
        else _latest_cert_root(Path("runtime/multi_provider_operational_readiness_certification_v1")),
        "audit_review": Path(audit_review_cert_root)
        if audit_review_cert_root
        else _latest_cert_root(Path("runtime/product1_audit_review_certification_v1")),
    }


def _reconstruct_sources(roots: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {
        "product1": reconstruct_product1_end_to_end_certification_v1(roots["product1"]),
        "worker_selection": reconstruct_worker_selection_replay(roots["worker_selection"]),
        "llm_worker": reconstruct_llm_worker_execution_replay(roots["llm_worker"]),
        "multi_provider": reconstruct_multi_provider_operational_readiness_replay(roots["multi_provider"]),
        "audit_review": reconstruct_product1_audit_review_certification_v1(roots["audit_review"]),
    }


def _source_reports(roots: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {
        "product1": load_json(roots["product1"] / "certification_report" / "000_product1_end_to_end_certification_report.json"),
        "worker_selection": load_json(roots["worker_selection"] / "certification_report" / "000_worker_selection_certification_report.json"),
        "llm_worker": load_json(roots["llm_worker"] / "certification_report" / "000_llm_worker_execution_certification_report.json"),
        "multi_provider": load_json(roots["multi_provider"] / "certification_report" / "000_multi_provider_operational_readiness_certification_report.json"),
        "audit_review": load_json(roots["audit_review"] / "certification_report" / "000_product1_audit_review_certification_report.json"),
    }


def _reproducibility_summaries(
    roots: dict[str, Path],
    reconstruction: dict[str, dict[str, Any]],
    source_reports: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    product1_replay = reconstruction["product1"]["replay_package"]
    worker_selection = reconstruction["worker_selection"]
    llm_worker = reconstruction["llm_worker"]
    audit = reconstruction["audit_review"]["audit_review_package"]
    workflow_path = product1_replay.get("certified_chain", "")
    approval_path = roots["product1"] / "component_runs/acli_live_session_real_worker_execution_certification_v1/CERT-000001/scenarios/ALS-001/replay/004_human_approval_recorded.json"
    authorization_path = roots["product1"] / "component_runs/acli_live_session_real_worker_execution_certification_v1/CERT-000001/scenarios/ALS-001/replay/005_authorization_recorded.json"
    validation_path = roots["product1"] / "component_runs/acli_live_session_real_worker_execution_certification_v1/CERT-000001/scenarios/ALS-001/replay/008_side_effect_verification_recorded.json"
    approval = load_json(approval_path)
    authorization = load_json(authorization_path)
    validation = load_json(validation_path)
    return {
        "workflow_path": {
            "source": str(roots["product1"]),
            "certified_chain": workflow_path,
            "reconstructed_verdict": reconstruction["product1"]["final_verdict"],
            "source_verdict": source_reports["product1"]["final_verdict"],
        },
        "worker_selection": {
            "source": str(roots["worker_selection"]),
            "scenario_count": worker_selection.get("scenario_count"),
            "replay_reconstructed": worker_selection.get("replay_reconstructed"),
            "rationale_reconstructed": all(
                item.get("rationale_recorded") for item in worker_selection.get("scenario_records", [])
            ),
            "source_verdict": source_reports["worker_selection"]["final_verdict"],
        },
        "approval_chain": {
            "approval_reference": str(approval_path),
            "human_approval_recorded": approval["artifact"]["human_approval_recorded"],
            "approved_for_execution": approval["artifact"]["approved_for_execution"],
            "artifact_hash": approval["artifact"]["artifact_hash"],
        },
        "authorization_chain": {
            "authorization_reference": str(authorization_path),
            "authorization_issued": authorization["artifact"]["authorization_issued"],
            "authorization_status": authorization["artifact"]["authorization_status"],
            "artifact_hash": authorization["artifact"]["artifact_hash"],
        },
        "validation_chain": {
            "product1_validation_reference": str(validation_path),
            "product1_verification_passed": validation["artifact"]["verification_passed"],
            "llm_worker_validation_result": llm_worker.get("validation_result"),
            "worker_selection_validation_reconstructed": worker_selection.get("replay_reconstructed"),
        },
        "multi_provider": {
            "source": str(roots["multi_provider"]),
            "replay_reconstructed": reconstruction["multi_provider"]["replay_reconstructed"],
            "source_verdict": source_reports["multi_provider"]["final_verdict"],
        },
        "audit_review": {
            "source": str(roots["audit_review"]),
            "reviewer_can_validate_decision": audit["review_conclusion"]["reviewer_can_validate_decision"],
            "trust_result": audit["trust_verification"]["trust_result"],
            "source_verdict": source_reports["audit_review"]["final_verdict"],
        },
    }


def _assertions(
    *,
    roots: dict[str, Path],
    reconstruction: dict[str, dict[str, Any]],
    source_reports: dict[str, dict[str, Any]],
    summaries: dict[str, Any],
    secret_free: bool,
) -> dict[str, bool]:
    return {
        "certified_executions_selected": all(path.exists() for path in roots.values()),
        "workflow_path_reconstructed": reconstruction["product1"]["replay_reconstructed"] is True
        and bool(summaries["workflow_path"]["certified_chain"]),
        "worker_selection_reconstructed": reconstruction["worker_selection"]["replay_reconstructed"] is True
        and summaries["worker_selection"]["rationale_reconstructed"] is True,
        "approvals_reconstructed": summaries["approval_chain"]["human_approval_recorded"] is True
        and summaries["approval_chain"]["approved_for_execution"] is True,
        "authorizations_reconstructed": summaries["authorization_chain"]["authorization_issued"] is True
        and summaries["authorization_chain"]["authorization_status"] == "AUTHORIZED",
        "validation_outcomes_reconstructed": summaries["validation_chain"]["product1_verification_passed"] is True
        and summaries["validation_chain"]["llm_worker_validation_result"] == "PASS",
        "same_evidence_produces_same_governed_decision": (
            reconstruction["product1"]["final_verdict"] == source_reports["product1"]["final_verdict"]
            and source_reports["worker_selection"]["final_verdict"] == "WORKER_SELECTION_CERTIFIED"
            and source_reports["llm_worker"]["final_verdict"] == "LLM_WORKER_EXECUTION_CERTIFIED"
            and source_reports["multi_provider"]["final_verdict"] == "MULTI_PROVIDER_OPERATIONALLY_READY"
            and source_reports["audit_review"]["final_verdict"] == "PRODUCT1_AUDIT_REVIEW_CERTIFIED"
        ),
        "replay_reconstructs_worker_selection_rationale": summaries["worker_selection"]["rationale_reconstructed"] is True,
        "replay_reconstructs_approval_chain": summaries["approval_chain"]["artifact_hash"].startswith("sha256:"),
        "replay_reconstructs_validation_chain": summaries["validation_chain"]["product1_verification_passed"] is True,
        "no_hidden_authority_source_exists": _no_hidden_authority(roots),
        "replay_sufficient_for_audit_reconstruction": summaries["audit_review"]["reviewer_can_validate_decision"] is True
        and summaries["audit_review"]["trust_result"] == "VALIDATED_WITHOUT_PROVIDER_TRUST",
        "secret_free_evidence": secret_free,
    }


def _no_hidden_authority(roots: dict[str, Path]) -> bool:
    authority_paths = [
        roots["worker_selection"] / "scenarios/WSG-001/007_worker_selection_authority_boundary.json",
        roots["llm_worker"] / "worker_replay/LWE-001/008_llm_worker_authority_boundary.json",
        roots["multi_provider"] / "provider_governance_replay/openai/participation/000_cognition_participation.json",
        roots["audit_review"] / "audit_review_package/000_product1_audit_review_package.json",
    ]
    for path in authority_paths:
        artifact = load_json(path)
        serialized = canonical_serialize(artifact)
        if '"provider_authority":true' in serialized or '"worker_authority":true' in serialized:
            return False
        if '"llm_worker_authority":true' in serialized:
            return False
    return True


def _reconstruction_ok(reconstruction: dict[str, Any]) -> bool:
    if "replay_reconstructed" in reconstruction:
        return reconstruction["replay_reconstructed"] is True
    return reconstruction.get("final_verdict") in {
        "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
        "PRODUCT1_AUDIT_REVIEW_CERTIFIED",
    }


def _source_and_generated_secret_free(roots: dict[str, Path]) -> bool:
    for root in roots.values():
        for path in sorted(root.rglob("*.json")):
            if not _secret_free_payload(load_json(path)):
                return False
    return True


def _latest_cert_root(base: Path) -> Path:
    if not base.exists():
        raise FailClosedRuntimeError(f"replay reproducibility missing runtime root: {base}")
    roots = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            roots.append((int(match.group(1)), path))
    if not roots:
        raise FailClosedRuntimeError(f"replay reproducibility missing CERT root: {base}")
    return sorted(roots)[-1][1]


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


def _secret_free_payload(payload: dict[str, Any]) -> bool:
    serialized = canonical_serialize(payload).lower()
    return not any(marker.lower() in serialized for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    if not _secret_free_payload(payload):
        raise FailClosedRuntimeError("replay reproducibility certification failed closed: secret-like material recorded")


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {"assertion": assertion, "failure_reason": "replay reproducibility assertion failed"}
        for assertion, passed in assertions.items()
        if passed is not True
    ]


def main() -> int:
    result = run_replay_reproducibility_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"REPRODUCIBILITY_REPORT={result['reproducibility_report_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
