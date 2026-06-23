"""System-level readiness certification for integrated AiGOL governance."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_SYSTEM_READINESS_CERTIFICATION_V1"
DEFAULT_REPLAY_BASE = Path("runtime/system_readiness_certification_v1")
CREATED_AT = "2026-06-23T00:00:00Z"
FINAL_VERDICT_READY = "AIGOL_SYSTEM_READY"
FINAL_VERDICT_GAPS = "AIGOL_SYSTEM_GAPS_FOUND"

EXPECTED_VERDICTS = {
    "human_intent_resolution": "HIRR_REAL_WORLD_READY",
    "product1_end_to_end": "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
    "multi_provider_operational": "MULTI_PROVIDER_OPERATIONALLY_READY",
    "worker_selection": "WORKER_SELECTION_CERTIFIED",
    "replay_reproducibility": "REPLAY_REPRODUCIBILITY_CERTIFIED",
    "product1_audit_review": "PRODUCT1_AUDIT_REVIEW_CERTIFIED",
    "replay_derived_improvement": "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFIED",
    "provider_governance": "PROVIDER_GOVERNANCE_CERTIFIED",
    "cognition_governance": "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
}

SOURCE_BASES = {
    "human_intent_resolution": Path("runtime/hirr_real_world_gaps_remediation_v1"),
    "product1_end_to_end": Path("runtime/product1_end_to_end_certification_v1"),
    "multi_provider_operational": Path("runtime/multi_provider_operational_readiness_certification_v1"),
    "worker_selection": Path("runtime/worker_selection_certification_v1"),
    "replay_reproducibility": Path("runtime/replay_reproducibility_certification_v1"),
    "product1_audit_review": Path("runtime/product1_audit_review_certification_v1"),
    "replay_derived_improvement": Path(
        "runtime/replay_derived_improvement_operationalization_certification_v1"
    ),
    "provider_governance": Path("runtime/provider_governance_certification_v1"),
    "cognition_governance": Path("runtime/first_live_cognition_provider_certification_v1"),
}

SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)


def run_system_readiness_certification_v1(
    *,
    replay_base: str | Path | None = None,
    source_roots: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Execute system-level readiness certification."""

    base = Path(replay_base) if replay_base is not None else DEFAULT_REPLAY_BASE
    cert_root = _next_cert_root(base)
    roots = _source_roots(source_roots)
    reports = _load_source_reports(roots)
    matrix = _readiness_matrix(roots, reports)
    executive_review = _executive_review_evidence()
    invariants = _invariant_evidence(roots, reports, executive_review)
    assertions = _assertions(matrix=matrix, invariants=invariants, cert_root=cert_root)
    final_verdict = FINAL_VERDICT_READY if all(assertions.values()) else FINAL_VERDICT_GAPS

    coverage = _with_hash(
        {
            "artifact_type": "AIGOL_SYSTEM_READINESS_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "coverage_dimensions": [
                "human intent resolution",
                "cognition governance",
                "provider governance",
                "worker governance",
                "worker selection",
                "replay generation",
                "replay reconstruction",
                "audit review",
                "executive review",
                "replay-derived improvement",
                "authority boundary preservation",
                "autonomous modification prevention",
                "proposal-only LLM participation",
            ],
            "source_roots": {key: str(value) for key, value in roots.items()},
            "readiness_matrix": matrix,
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "AIGOL_SYSTEM_READINESS_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "source_certifications": matrix,
            "architectural_chain_evidence": _architectural_chain_evidence(matrix, executive_review),
            "invariant_evidence": invariants,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "AIGOL_SYSTEM_READINESS_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "source_replay_roots": {key: str(value) for key, value in roots.items()},
            "source_report_hashes": {
                key: report.get("artifact_hash") or replay_hash(report) for key, report in reports.items()
            },
            "replay_reconstructed": matrix["replay_reproducibility"]["certified"]
            and matrix["product1_audit_review"]["certified"]
            and matrix["replay_derived_improvement"]["certified"],
            "replay_as_source_of_truth": invariants["replay_as_source_of_truth"],
            "final_verdict": final_verdict,
        }
    )
    readiness = _with_hash(
        {
            "artifact_type": "AIGOL_SYSTEM_READINESS_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "question": "Is AiGOL architecturally ready as an integrated governed cognition platform?",
            "answer": final_verdict == FINAL_VERDICT_READY,
            "major_chains_verified": _major_chain_summary(matrix, executive_review),
            "architectural_invariants": invariants,
            "remaining_blockers": [] if final_verdict == FINAL_VERDICT_READY else _blockers(assertions),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "AIGOL_SYSTEM_READINESS_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "readiness_report_hash": readiness["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_READY else _blockers(assertions),
            "question_answer": (
                "YES: AiGOL is architecturally ready as an integrated governed cognition platform."
                if final_verdict == FINAL_VERDICT_READY
                else "NO: AiGOL system readiness gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (coverage, evidence, replay, readiness, report):
        _assert_secret_safe(artifact)
    write_json_immutable(cert_root / "readiness_coverage_report" / "000_system_readiness_coverage_report.json", coverage)
    write_json_immutable(cert_root / "evidence_package" / "000_system_readiness_evidence_package.json", evidence)
    write_json_immutable(cert_root / "replay_package" / "000_system_readiness_replay_package.json", replay)
    write_json_immutable(cert_root / "readiness_report" / "000_system_readiness_report.json", readiness)
    write_json_immutable(cert_root / "certification_report" / "000_system_readiness_certification_report.json", report)
    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "readiness_coverage_report_path": str(
            cert_root / "readiness_coverage_report" / "000_system_readiness_coverage_report.json"
        ),
        "evidence_package_path": str(cert_root / "evidence_package" / "000_system_readiness_evidence_package.json"),
        "replay_package_path": str(cert_root / "replay_package" / "000_system_readiness_replay_package.json"),
        "readiness_report_path": str(cert_root / "readiness_report" / "000_system_readiness_report.json"),
        "certification_report_path": str(
            cert_root / "certification_report" / "000_system_readiness_certification_report.json"
        ),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def _source_roots(overrides: dict[str, str | Path] | None) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for key, base in SOURCE_BASES.items():
        roots[key] = Path(overrides[key]) if overrides and key in overrides else _latest_cert_root(base)
    return roots


def _load_source_reports(roots: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {key: load_json(_single_report_path(root)) for key, root in roots.items()}


def _readiness_matrix(roots: dict[str, Path], reports: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    matrix = {}
    for key, report in reports.items():
        assertions = report.get("assertions")
        assertions_ok = all(assertions.values()) if isinstance(assertions, dict) else True
        expected = EXPECTED_VERDICTS[key]
        actual = report.get("final_verdict")
        matrix[key] = {
            "source_root": str(roots[key]),
            "expected_verdict": expected,
            "actual_verdict": actual,
            "assertions_available": isinstance(assertions, dict),
            "assertions_ok": assertions_ok,
            "certified": actual == expected and assertions_ok,
        }
    return matrix


def _executive_review_evidence() -> dict[str, Any]:
    path = Path("docs/governance/AIGOL_PRODUCT1_EXECUTIVE_REVIEW_EXPERIENCE_V1.md")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_terms = (
        "what was requested",
        "what was decided",
        "why it was decided",
        "which evidence was used",
        "approval",
        "execution",
        "provider trust",
        "residual risk",
    )
    lowered = text.lower()
    return {
        "artifact_type": "AIGOL_SYSTEM_EXECUTIVE_REVIEW_EVIDENCE_V1",
        "source_path": str(path),
        "defined": path.exists() and "PRODUCT1_EXECUTIVE_REVIEW_EXPERIENCE_DEFINED" in text,
        "required_terms_present": {term: term in lowered for term in required_terms},
        "non_technical_layer_defined": "non-technical" in lowered,
        "links_to_audit_and_replay": "Audit Review Package" in text and "Replay" in text,
    }


def _invariant_evidence(
    roots: dict[str, Path],
    reports: dict[str, dict[str, Any]],
    executive_review: dict[str, Any],
) -> dict[str, bool]:
    generated_roots_secret_free = all(_path_secret_free(root) for root in roots.values())
    proposal_only_report = reports["replay_derived_improvement"]
    replay_report = reports["replay_reproducibility"]
    product1_report = reports["product1_end_to_end"]
    worker_report = reports["worker_selection"]
    multi_provider_report = reports["multi_provider_operational"]
    return {
        "no_authority_transfer": _assertion_or_verdict(product1_report, "authority_boundary_preserved")
        and _assertion_or_verdict(worker_report, "governance_authority_preserved")
        and _assertion_or_verdict(multi_provider_report, "governance_provider_agnostic")
        and _assertion_or_verdict(proposal_only_report, "no_authority_transfer"),
        "no_autonomous_modification": _assertion_or_verdict(proposal_only_report, "no_autonomous_modification"),
        "replay_as_source_of_truth": replay_report.get("final_verdict") == "REPLAY_REPRODUCIBILITY_CERTIFIED",
        "proposal_only_llm_participation": _assertion_or_verdict(proposal_only_report, "proposal_only_behavior_preserved"),
        "executive_review_defined": executive_review["defined"]
        and all(executive_review["required_terms_present"].values())
        and executive_review["links_to_audit_and_replay"],
        "secret_free_evidence": generated_roots_secret_free,
    }


def _architectural_chain_evidence(
    matrix: dict[str, dict[str, Any]],
    executive_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "human_intent_resolution": matrix["human_intent_resolution"]["certified"],
        "cognition_governance": matrix["cognition_governance"]["certified"],
        "provider_governance": matrix["provider_governance"]["certified"],
        "worker_governance": matrix["product1_end_to_end"]["certified"],
        "worker_selection": matrix["worker_selection"]["certified"],
        "replay_generation": matrix["product1_end_to_end"]["certified"],
        "replay_reconstruction": matrix["replay_reproducibility"]["certified"],
        "audit_review": matrix["product1_audit_review"]["certified"],
        "executive_review": executive_review["defined"],
        "replay_derived_improvement": matrix["replay_derived_improvement"]["certified"],
    }


def _major_chain_summary(matrix: dict[str, dict[str, Any]], executive_review: dict[str, Any]) -> dict[str, bool]:
    evidence = _architectural_chain_evidence(matrix, executive_review)
    evidence["all_major_chains_verified"] = all(evidence.values())
    return evidence


def _assertions(
    *,
    matrix: dict[str, dict[str, Any]],
    invariants: dict[str, bool],
    cert_root: Path,
) -> dict[str, bool]:
    return {
        "human_intent_resolution_verified": matrix["human_intent_resolution"]["certified"],
        "cognition_governance_verified": matrix["cognition_governance"]["certified"],
        "provider_governance_verified": matrix["provider_governance"]["certified"],
        "worker_governance_verified": matrix["product1_end_to_end"]["certified"],
        "worker_selection_verified": matrix["worker_selection"]["certified"],
        "replay_generation_verified": matrix["product1_end_to_end"]["certified"],
        "replay_reconstruction_verified": matrix["replay_reproducibility"]["certified"],
        "audit_review_verified": matrix["product1_audit_review"]["certified"],
        "executive_review_verified": invariants["executive_review_defined"],
        "replay_derived_improvement_verified": matrix["replay_derived_improvement"]["certified"],
        "multi_provider_operation_verified": matrix["multi_provider_operational"]["certified"],
        "no_authority_transfer": invariants["no_authority_transfer"],
        "no_autonomous_modification": invariants["no_autonomous_modification"],
        "replay_as_source_of_truth": invariants["replay_as_source_of_truth"],
        "proposal_only_llm_participation": invariants["proposal_only_llm_participation"],
        "secret_free_evidence": invariants["secret_free_evidence"] and _path_secret_free(cert_root),
    }


def _assertion_or_verdict(report: dict[str, Any], assertion_key: str) -> bool:
    assertions = report.get("assertions")
    if isinstance(assertions, dict) and assertion_key in assertions:
        return assertions[assertion_key] is True
    return bool(report.get("final_verdict"))


def _single_report_path(root: Path) -> Path:
    report_dir = root / "certification_report"
    matches = sorted(report_dir.glob("*.json"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one certification report under {report_dir}")
    return matches[0]


def _latest_cert_root(base: Path) -> Path:
    if not base.exists():
        raise ValueError(f"certification root base missing: {base}")
    candidates = []
    for child in base.iterdir():
        if child.is_dir() and re.fullmatch(r"CERT-\d{6}", child.name):
            candidates.append(child)
    if not candidates:
        raise ValueError(f"no CERT roots found under {base}")
    return sorted(candidates)[-1]


def _next_cert_root(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    max_index = 0
    for child in base.iterdir():
        if child.is_dir():
            match = re.fullmatch(r"CERT-(\d{6})", child.name)
            if match:
                max_index = max(max_index, int(match.group(1)))
    return base / f"CERT-{max_index + 1:06d}"


def _with_hash(artifact: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(artifact)
    payload.pop("artifact_hash", None)
    payload["artifact_hash"] = replay_hash(payload)
    return payload


def _path_secret_free(path: Path) -> bool:
    if not path.exists():
        return True
    for artifact_path in path.rglob("*.json"):
        text = artifact_path.read_text(encoding="utf-8")
        if any(marker in text for marker in SECRET_MARKERS):
            return False
    return True


def _assert_secret_safe(artifact: dict[str, Any]) -> None:
    serialized = canonical_serialize(artifact)
    if any(marker in serialized for marker in SECRET_MARKERS):
        raise ValueError("system readiness artifact contains secret marker")


def _blockers(assertions: dict[str, bool]) -> list[str]:
    return [key for key, value in assertions.items() if value is not True]


def main() -> None:
    result = run_system_readiness_certification_v1()
    print("CERT_ROOT=" + result["cert_root"])
    print("FINAL_VERDICT=" + result["final_verdict"])


if __name__ == "__main__":
    main()
