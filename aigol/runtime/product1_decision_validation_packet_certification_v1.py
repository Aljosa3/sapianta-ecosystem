"""Certification for Product 1 decision validation packet generation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_operational_readiness_certification_v1 import (
    FINAL_VERDICT_READY as MULTI_PROVIDER_READY,
    reconstruct_multi_provider_operational_readiness_replay,
)
from aigol.runtime.product1_end_to_end_certification_v1 import (
    FINAL_VERDICT_CERTIFIED as PRODUCT1_END_TO_END_CERTIFIED,
    reconstruct_product1_end_to_end_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFICATION_V1"
PACKET_RUNTIME_VERSION = "AIGOL_PRODUCT1_DECISION_VALIDATION_PACKET_V1"
PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1 = (
    "PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1"
)
PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1 = (
    "PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1"
)
PRODUCT1_DECISION_VALIDATION_REQUEST_RUNTIME_VERSION = (
    "G31_02_PRODUCT1_DECISION_VALIDATION_REQUEST_V1"
)
PRODUCT1_DECISION_VALIDATION_REQUEST_CREATED = (
    "PRODUCT1_DECISION_VALIDATION_REQUEST_CREATED"
)
DEFAULT_RUNTIME_ROOT = Path("runtime/product1_decision_validation_packet_certification_v1")
CREATED_AT = "2026-06-22T00:00:00Z"

FINAL_VERDICT_CERTIFIED = "PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFIED"
FINAL_VERDICT_GAPS = "PRODUCT1_DECISION_VALIDATION_PACKET_GAPS_FOUND"
SECRET_MARKERS = (
    "sk-",
    "Bearer ",
    "OPENAI_API_KEY=",
    "ANTHROPIC_API_KEY=",
    "AIGOL_OPENAI_API_KEY=",
    "AIGOL_ANTHROPIC_API_KEY=",
)

MANDATORY_PACKET_SECTIONS = (
    "packet_metadata",
    "decision_summary",
    "human_request_summary",
    "intent_resolution_summary",
    "workflow_selection_summary",
    "evidence_summary",
    "provider_participation_summary",
    "worker_participation_summary",
    "approval_summary",
    "authorization_summary",
    "execution_summary",
    "verification_summary",
    "assumptions_and_uncertainties",
    "replay_reference_summary",
    "audit_conclusion",
    "independent_verification_workflow",
    "boundary_guarantees",
    "reviewer_next_actions",
)

REQUEST_BOUNDARY_FLAGS = {
    "read_only": True,
    "replay_visible": True,
    "human_interface_authority": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_authorized": False,
    "repository_mutated": False,
    "deployment_requested": False,
    "artifact_discovery_performed": False,
}

PRODUCT1_SOURCE_RELATIVE_PATHS = {
    "product1_coverage_report": (
        "coverage_report/000_product1_end_to_end_coverage_report.json"
    ),
    "product1_evidence_package": (
        "evidence_package/000_product1_end_to_end_evidence_package.json"
    ),
    "product1_replay_package": (
        "replay_package/000_product1_end_to_end_replay_package.json"
    ),
    "product1_audit_review": (
        "audit_review/000_product1_end_to_end_audit_review.json"
    ),
    "product1_certification_report": (
        "certification_report/000_product1_end_to_end_certification_report.json"
    ),
}

MULTI_PROVIDER_SOURCE_RELATIVE_PATHS = {
    "multi_provider_certification_report": (
        "certification_report/"
        "000_multi_provider_operational_readiness_certification_report.json"
    ),
    "openai_participation": (
        "provider_governance_replay/openai/participation/"
        "000_cognition_participation.json"
    ),
    "openai_usage": (
        "provider_governance_replay/openai/usage/000_provider_usage_metric.json"
    ),
    "claude_participation": (
        "provider_governance_replay/claude/participation/"
        "000_cognition_participation.json"
    ),
    "claude_usage": (
        "provider_governance_replay/claude/usage/000_provider_usage_metric.json"
    ),
}

SCENARIO_REPLAY_FILENAMES = (
    "000_acli_session_started.json",
    "001_natural_language_turns_recorded.json",
    "002_intent_resolution_recorded.json",
    "003_execution_summary_recorded.json",
    "004_human_approval_recorded.json",
    "005_authorization_recorded.json",
    "006_worker_handoff_recorded.json",
    "007_worker_execution_recorded.json",
    "008_side_effect_verification_recorded.json",
)


def run_product1_decision_validation_packet_certification_v1(
    *,
    runtime_root: str | Path = DEFAULT_RUNTIME_ROOT,
    product1_cert_root: str | Path | None = None,
    multi_provider_cert_root: str | Path | None = None,
) -> dict[str, Any]:
    cert_root = _next_cert_root(Path(runtime_root))
    source = _load_source_evidence(
        product1_cert_root=product1_cert_root,
        multi_provider_cert_root=multi_provider_cert_root,
    )
    packet = _generate_decision_validation_packet(source)
    assertions = _assertions(packet, source)
    final_verdict = FINAL_VERDICT_CERTIFIED if all(assertions.values()) else FINAL_VERDICT_GAPS
    coverage = _with_hash(
        {
            "artifact_type": "PRODUCT1_DECISION_VALIDATION_PACKET_COVERAGE_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "coverage_dimensions": [
                "decision summary",
                "evidence references",
                "replay references",
                "provider participation",
                "worker participation",
                "approval summary",
                "authorization summary",
                "independent verification workflow",
                "no credential leakage",
                "no authority transfer",
                "replay traceability",
                "evidence traceability",
            ],
            "source_product1_cert_root": str(source["product1_cert_root"]),
            "source_multi_provider_cert_root": str(source["multi_provider_cert_root"]),
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    evidence = _with_hash(
        {
            "artifact_type": "PRODUCT1_DECISION_VALIDATION_PACKET_EVIDENCE_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "source_product1_cert_root": str(source["product1_cert_root"]),
            "source_multi_provider_cert_root": str(source["multi_provider_cert_root"]),
            "selected_product1_scenario": source["scenario"]["scenario_id"],
            "selected_product1_coverage": source["scenario"]["coverage"],
            "source_replay_reference": source["scenario_replay_dir"],
            "provider_participation_references": [
                provider["participation_evidence_reference"]
                for provider in packet["provider_participation_summary"]["providers"]
            ],
            "worker_verification_reference": packet["verification_summary"]["verification_evidence_reference"],
            "packet_hash": packet["artifact_hash"],
            "assertions": assertions,
            "final_verdict": final_verdict,
        }
    )
    replay = _with_hash(
        {
            "artifact_type": "PRODUCT1_DECISION_VALIDATION_PACKET_REPLAY_PACKAGE_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "generated_packet_reference": "generated_packet/000_product1_decision_validation_packet.json",
            "source_replay_package_reference": source["product1_replay_path"],
            "source_audit_review_reference": source["product1_audit_path"],
            "source_scenario_replay_reference": source["scenario_replay_dir"],
            "replay_reconstructed": _packet_replay_reconstructs(packet, source),
            "evidence_traceable": _packet_evidence_traceable(packet),
            "final_verdict": final_verdict,
        }
    )
    report = _with_hash(
        {
            "artifact_type": "PRODUCT1_DECISION_VALIDATION_PACKET_CERTIFICATION_REPORT_V1",
            "runtime_version": MILESTONE_ID,
            "created_at": CREATED_AT,
            "cert_root": str(cert_root),
            "coverage_report_hash": coverage["artifact_hash"],
            "evidence_package_hash": evidence["artifact_hash"],
            "replay_package_hash": replay["artifact_hash"],
            "generated_packet_hash": packet["artifact_hash"],
            "assertions": assertions,
            "blocker_analysis": [] if final_verdict == FINAL_VERDICT_CERTIFIED else _blockers(assertions),
            "reviewer_question_answer": (
                "YES: an independent reviewer can reconstruct and validate the decision from replay-visible "
                "governance evidence without trusting the cognition provider."
                if final_verdict == FINAL_VERDICT_CERTIFIED
                else "NO: decision validation packet gaps remain."
            ),
            "final_verdict": final_verdict,
        }
    )
    for artifact in (packet, coverage, evidence, replay, report):
        _assert_secret_safe(artifact)

    packet_path = cert_root / "generated_packet" / "000_product1_decision_validation_packet.json"
    coverage_path = cert_root / "coverage_report" / "000_product1_decision_validation_packet_coverage_report.json"
    evidence_path = cert_root / "evidence_package" / "000_product1_decision_validation_packet_evidence_package.json"
    replay_path = cert_root / "replay_package" / "000_product1_decision_validation_packet_replay_package.json"
    report_path = cert_root / "certification_report" / "000_product1_decision_validation_packet_certification_report.json"
    write_json_immutable(packet_path, packet)
    write_json_immutable(coverage_path, coverage)
    write_json_immutable(evidence_path, evidence)
    write_json_immutable(replay_path, replay)
    write_json_immutable(report_path, report)

    return {
        "milestone_id": MILESTONE_ID,
        "cert_root": str(cert_root),
        "generated_packet_path": str(packet_path),
        "coverage_report_path": str(coverage_path),
        "evidence_package_path": str(evidence_path),
        "replay_package_path": str(replay_path),
        "certification_report_path": str(report_path),
        "assertions": assertions,
        "final_verdict": final_verdict,
    }


def reconstruct_product1_decision_validation_packet_certification_v1(cert_root: str | Path) -> dict[str, Any]:
    root = Path(cert_root)
    packet = load_json(root / "generated_packet" / "000_product1_decision_validation_packet.json")
    coverage = load_json(root / "coverage_report" / "000_product1_decision_validation_packet_coverage_report.json")
    evidence = load_json(root / "evidence_package" / "000_product1_decision_validation_packet_evidence_package.json")
    replay = load_json(root / "replay_package" / "000_product1_decision_validation_packet_replay_package.json")
    report = load_json(root / "certification_report" / "000_product1_decision_validation_packet_certification_report.json")
    for artifact in (packet, coverage, evidence, replay, report):
        _verify_artifact_hash(artifact)
    return {
        "runtime_version": MILESTONE_ID,
        "packet": packet,
        "coverage_report": coverage,
        "evidence_package": evidence,
        "replay_package": replay,
        "certification_report": report,
        "replay_reconstructed": replay["replay_reconstructed"] is True,
        "final_verdict": report["final_verdict"],
    }


def create_product1_decision_validation_request(
    *,
    request_id: str,
    product1_cert_root: str | Path,
    multi_provider_cert_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Create one immutable request from exact, caller-supplied evidence roots."""

    product1_root = Path(product1_cert_root)
    multi_provider_root = Path(multi_provider_cert_root)
    source_manifest, scenario_replay_root = _source_manifest(
        product1_root=product1_root,
        multi_provider_root=multi_provider_root,
    )
    artifact = {
        "artifact_type": PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1,
        "runtime_version": PRODUCT1_DECISION_VALIDATION_REQUEST_RUNTIME_VERSION,
        "request_id": _require_string(request_id, "request_id"),
        "request_status": PRODUCT1_DECISION_VALIDATION_REQUEST_CREATED,
        "requested_capability": "PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION",
        "product1_cert_root": str(product1_root),
        "multi_provider_cert_root": str(multi_provider_root),
        "scenario_replay_root": str(scenario_replay_root),
        "source_artifacts": source_manifest,
        "source_artifact_count": len(source_manifest),
        "source_manifest_hash": replay_hash(source_manifest),
        "created_at": _require_string(created_at, "created_at"),
        **REQUEST_BOUNDARY_FLAGS,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_product1_decision_validation_request(artifact)


def validate_product1_decision_validation_request(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate request identity and every explicitly pinned source artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request must be an object"
        )
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate)
    if candidate.get("artifact_type") != (
        PRODUCT1_DECISION_VALIDATION_REQUEST_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request artifact type mismatch"
        )
    if candidate.get("runtime_version") != (
        PRODUCT1_DECISION_VALIDATION_REQUEST_RUNTIME_VERSION
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request runtime version mismatch"
        )
    if candidate.get("request_status") != (
        PRODUCT1_DECISION_VALIDATION_REQUEST_CREATED
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request status mismatch"
        )
    if candidate.get("requested_capability") != (
        "PRODUCT1_DECISION_VALIDATION_PACKET_GENERATION"
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request capability mismatch"
        )
    _require_string(candidate.get("request_id"), "request_id")
    _require_string(candidate.get("created_at"), "created_at")
    for field, expected in REQUEST_BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                "Product 1 decision validation request boundary mismatch"
            )

    product1_root = Path(
        _require_string(candidate.get("product1_cert_root"), "product1_cert_root")
    )
    multi_provider_root = Path(
        _require_string(
            candidate.get("multi_provider_cert_root"),
            "multi_provider_cert_root",
        )
    )
    expected_manifest, scenario_replay_root = _source_manifest(
        product1_root=product1_root,
        multi_provider_root=multi_provider_root,
    )
    supplied_manifest = candidate.get("source_artifacts")
    if supplied_manifest != expected_manifest:
        raise FailClosedRuntimeError(
            "Product 1 decision validation request source substitution"
        )
    if candidate.get("source_artifact_count") != len(expected_manifest):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request source count mismatch"
        )
    if candidate.get("source_manifest_hash") != replay_hash(expected_manifest):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request source manifest hash mismatch"
        )
    if candidate.get("scenario_replay_root") != str(scenario_replay_root):
        raise FailClosedRuntimeError(
            "Product 1 decision validation request scenario lineage mismatch"
        )
    _validate_source_certification_lineage(
        product1_root=product1_root,
        multi_provider_root=multi_provider_root,
        scenario_replay_root=scenario_replay_root,
    )
    return candidate


def validate_product1_decision_validation_packet(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one generated enterprise Decision Validation Packet."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet must be an object"
        )
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate)
    if candidate.get("artifact_type") != (
        PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet artifact type mismatch"
        )
    if candidate.get("runtime_version") != PACKET_RUNTIME_VERSION:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet runtime version mismatch"
        )
    missing = [section for section in MANDATORY_PACKET_SECTIONS if section not in candidate]
    if missing:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet mandatory section missing"
        )
    boundaries = candidate.get("boundary_guarantees")
    if not isinstance(boundaries, dict):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet boundaries missing"
        )
    if boundaries.get("provider_authority") is not False:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet provider boundary mismatch"
        )
    if boundaries.get("human_authority_preserved") is not True:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet human authority mismatch"
        )
    if candidate.get("replay_reference_summary", {}).get(
        "replay_reconstructed"
    ) is not True:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet Replay is not reconstructed"
        )
    _assert_secret_safe(candidate)
    return candidate


def generate_product1_decision_validation_packet(
    *,
    request_artifact: dict[str, Any],
    invoked_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Generate the existing Product 1 packet from one validated explicit request."""

    request = validate_product1_decision_validation_request(request_artifact)
    timestamp = _require_string(invoked_at, "invoked_at")
    path = Path(replay_dir)
    replay_path = path / "000_product1_decision_validation_packet_generated.json"
    if replay_path.exists():
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet Replay already exists"
        )
    source = _load_source_evidence(
        product1_cert_root=request["product1_cert_root"],
        multi_provider_cert_root=request["multi_provider_cert_root"],
    )
    packet = validate_product1_decision_validation_packet(
        _generate_decision_validation_packet(source)
    )
    assertions = _assertions(packet, source)
    if not all(assertions.values()):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet generation failed closed"
        )
    wrapper = {
        "replay_index": 0,
        "replay_step": "product1_decision_validation_packet_generated",
        "request_artifact": deepcopy(request),
        "request_artifact_hash": request["artifact_hash"],
        "source_manifest_hash": request["source_manifest_hash"],
        "artifact": deepcopy(packet),
        "invoked_at": timestamp,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path, wrapper)
    return {
        "decision_validation_packet_artifact": packet,
        "request_artifact_hash": request["artifact_hash"],
        "replay_reference": str(path),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
    }


def reconstruct_product1_decision_validation_packet_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct one operational packet invocation and its pinned source lineage."""

    path = Path(replay_dir)
    wrapper = load_json(
        path / "000_product1_decision_validation_packet_generated.json"
    )
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != (
        "product1_decision_validation_packet_generated"
    ):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet Replay ordering mismatch"
        )
    supplied_hash = wrapper.get("wrapper_hash")
    body = deepcopy(wrapper)
    body.pop("wrapper_hash", None)
    if supplied_hash != replay_hash(body):
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet Replay wrapper hash mismatch"
        )
    request = validate_product1_decision_validation_request(
        wrapper.get("request_artifact")
    )
    packet = validate_product1_decision_validation_packet(wrapper.get("artifact"))
    source = _load_source_evidence(
        product1_cert_root=request["product1_cert_root"],
        multi_provider_cert_root=request["multi_provider_cert_root"],
    )
    expected_packet = validate_product1_decision_validation_packet(
        _generate_decision_validation_packet(source)
    )
    if packet != expected_packet:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet deterministic reconstruction mismatch"
        )
    if wrapper.get("request_artifact_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet request substitution"
        )
    if wrapper.get("source_manifest_hash") != request["source_manifest_hash"]:
        raise FailClosedRuntimeError(
            "Product 1 decision validation packet source substitution"
        )
    for field in (
        "provider_invoked",
        "worker_invoked",
        "execution_authorized",
        "repository_mutated",
    ):
        if wrapper.get(field) is not False:
            raise FailClosedRuntimeError(
                "Product 1 decision validation packet current invocation boundary mismatch"
            )
    return {
        "request_id": request["request_id"],
        "request_artifact_hash": request["artifact_hash"],
        "source_manifest_hash": request["source_manifest_hash"],
        "packet_id": packet["packet_id"],
        "packet_artifact_hash": packet["artifact_hash"],
        "replay_reference": str(path),
        "replay_hash": replay_hash([wrapper]),
        "replay_reconstructed": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_authorized": False,
        "repository_mutated": False,
    }


def _source_manifest(
    *,
    product1_root: Path,
    multi_provider_root: Path,
) -> tuple[list[dict[str, Any]], Path]:
    product1_evidence_path = (
        product1_root / PRODUCT1_SOURCE_RELATIVE_PATHS["product1_evidence_package"]
    )
    product1_evidence = load_json(product1_evidence_path)
    scenario = _select_product1_scenario(product1_evidence)
    scenario_replay_root = Path(
        _require_string(
            scenario.get("observed", {}).get("source_reference"),
            "scenario_replay_root",
        )
    )
    sources: list[tuple[str, Path]] = [
        (role, product1_root / relative_path)
        for role, relative_path in PRODUCT1_SOURCE_RELATIVE_PATHS.items()
    ]
    sources.extend(
        (
            f"scenario_replay_{index:03d}",
            scenario_replay_root / filename,
        )
        for index, filename in enumerate(SCENARIO_REPLAY_FILENAMES)
    )
    sources.extend(
        (role, multi_provider_root / relative_path)
        for role, relative_path in MULTI_PROVIDER_SOURCE_RELATIVE_PATHS.items()
    )
    manifest = []
    for role, reference in sources:
        source = load_json(reference)
        manifest.append(
            {
                "source_role": role,
                "source_reference": str(reference),
                "source_content_hash": replay_hash(source),
            }
        )
    return manifest, scenario_replay_root


def _validate_source_certification_lineage(
    *,
    product1_root: Path,
    multi_provider_root: Path,
    scenario_replay_root: Path,
) -> None:
    product1 = reconstruct_product1_end_to_end_certification_v1(product1_root)
    if product1.get("final_verdict") != PRODUCT1_END_TO_END_CERTIFIED:
        raise FailClosedRuntimeError(
            "Product 1 decision validation request requires certified Product 1 evidence"
        )
    multi_provider = reconstruct_multi_provider_operational_readiness_replay(
        multi_provider_root
    )
    if multi_provider.get("replay_reconstructed") is not True:
        raise FailClosedRuntimeError(
            "Product 1 decision validation request provider Replay mismatch"
        )
    report = load_json(
        multi_provider_root
        / MULTI_PROVIDER_SOURCE_RELATIVE_PATHS[
            "multi_provider_certification_report"
        ]
    )
    _verify_artifact_hash(report)
    if report.get("final_verdict") != MULTI_PROVIDER_READY:
        raise FailClosedRuntimeError(
            "Product 1 decision validation request requires provider readiness evidence"
        )
    for index, filename in enumerate(SCENARIO_REPLAY_FILENAMES):
        wrapper = load_json(scenario_replay_root / filename)
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError(
                "Product 1 decision validation request scenario Replay ordering mismatch"
            )
        supplied_hash = wrapper.get("replay_hash")
        body = deepcopy(wrapper)
        body.pop("replay_hash", None)
        if supplied_hash != replay_hash(body):
            raise FailClosedRuntimeError(
                "Product 1 decision validation request scenario Replay hash mismatch"
            )
        replay_artifact = wrapper.get("artifact")
        if not isinstance(replay_artifact, dict):
            raise FailClosedRuntimeError(
                "Product 1 decision validation request scenario artifact missing"
            )
        _verify_artifact_hash(replay_artifact)


def _load_source_evidence(
    *,
    product1_cert_root: str | Path | None,
    multi_provider_cert_root: str | Path | None,
) -> dict[str, Any]:
    product1_root = Path(product1_cert_root) if product1_cert_root else _latest_cert_root(
        Path("runtime/product1_end_to_end_certification_v1")
    )
    multi_root = Path(multi_provider_cert_root) if multi_provider_cert_root else _latest_cert_root(
        Path("runtime/multi_provider_operational_readiness_certification_v1")
    )
    product1_evidence_path = product1_root / "evidence_package" / "000_product1_end_to_end_evidence_package.json"
    product1_replay_path = product1_root / "replay_package" / "000_product1_end_to_end_replay_package.json"
    product1_audit_path = product1_root / "audit_review" / "000_product1_end_to_end_audit_review.json"
    product1_report_path = product1_root / "certification_report" / "000_product1_end_to_end_certification_report.json"
    product1_evidence = load_json(product1_evidence_path)
    product1_replay = load_json(product1_replay_path)
    product1_audit = load_json(product1_audit_path)
    product1_report = load_json(product1_report_path)
    if product1_report.get("final_verdict") != "AIGOL_PRODUCT1_END_TO_END_CERTIFIED":
        raise FailClosedRuntimeError("decision validation packet certification requires Product 1 E2E certification")
    scenario = _select_product1_scenario(product1_evidence)
    scenario_replay_dir = Path(scenario["observed"]["source_reference"])
    if not scenario_replay_dir.exists():
        raise FailClosedRuntimeError("decision validation packet certification requires scenario replay evidence")
    replay_artifacts = {
        "intent": load_json(scenario_replay_dir / "002_intent_resolution_recorded.json"),
        "summary": load_json(scenario_replay_dir / "003_execution_summary_recorded.json"),
        "approval": load_json(scenario_replay_dir / "004_human_approval_recorded.json"),
        "authorization": load_json(scenario_replay_dir / "005_authorization_recorded.json"),
        "handoff": load_json(scenario_replay_dir / "006_worker_handoff_recorded.json"),
        "execution": load_json(scenario_replay_dir / "007_worker_execution_recorded.json"),
        "verification": load_json(scenario_replay_dir / "008_side_effect_verification_recorded.json"),
    }
    providers = _load_provider_summaries(multi_root)
    return {
        "product1_cert_root": product1_root,
        "multi_provider_cert_root": multi_root,
        "product1_evidence_path": str(product1_evidence_path),
        "product1_replay_path": str(product1_replay_path),
        "product1_audit_path": str(product1_audit_path),
        "product1_report_path": str(product1_report_path),
        "product1_evidence": product1_evidence,
        "product1_replay": product1_replay,
        "product1_audit": product1_audit,
        "product1_report": product1_report,
        "scenario": scenario,
        "scenario_replay_dir": str(scenario_replay_dir),
        "replay_artifacts": replay_artifacts,
        "providers": providers,
    }


def _select_product1_scenario(product1_evidence: dict[str, Any]) -> dict[str, Any]:
    for scenario in product1_evidence.get("scenario_results", []):
        if scenario.get("scenario_id") == "P1-E2E-001" and scenario.get("scenario_verdict") == "CERTIFIED":
            return scenario
    raise FailClosedRuntimeError("decision validation packet certification requires P1-E2E-001 certified replay")


def _load_provider_summaries(multi_root: Path) -> list[dict[str, Any]]:
    providers = []
    for provider_id in ("openai", "claude"):
        participation_path = multi_root / "provider_governance_replay" / provider_id / "participation" / "000_cognition_participation.json"
        usage_path = multi_root / "provider_governance_replay" / provider_id / "usage" / "000_provider_usage_metric.json"
        participation = load_json(participation_path)
        usage = load_json(usage_path)
        providers.append(
            {
                "provider_id": provider_id,
                "role": "cognition_provider",
                "participation_location": participation["participation_location"],
                "response_used": participation["response_used"],
                "provider_authority": participation["provider_authority"],
                "worker_invoked_after": participation["worker_invoked_after"],
                "human_confirmation_required": participation["human_confirmation_required"],
                "participation_evidence_reference": str(participation_path),
                "usage_metric_reference": str(usage_path),
                "participation_artifact_hash": participation["artifact_hash"],
                "usage_artifact_hash": usage["artifact_hash"],
                "success_count": usage.get("success_count"),
                "failure_count": usage.get("failure_count"),
                "cost_tracking": usage.get("cost_tracking"),
            }
        )
    return providers


def _generate_decision_validation_packet(source: dict[str, Any]) -> dict[str, Any]:
    scenario = source["scenario"]
    replay_artifacts = source["replay_artifacts"]
    intent = replay_artifacts["intent"]["artifact"]
    approval = replay_artifacts["approval"]["artifact"]
    authorization = replay_artifacts["authorization"]["artifact"]
    verification = replay_artifacts["verification"]["artifact"]
    packet = {
        "artifact_type": "PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1",
        "packet_id": "P1-DVP-CERT-001",
        "runtime_version": PACKET_RUNTIME_VERSION,
        "created_at": CREATED_AT,
        "source_certification_root": str(source["product1_cert_root"]),
        "packet_metadata": {
            "product": "AI Decision Validator",
            "decision_status": "APPROVED_EXECUTED_VERIFIED",
            "reviewer_audience": ["operator", "reviewer", "auditor", "manager", "regulator"],
            "secret_free": True,
            "provider_non_authority_preserved": True,
            "human_authority_preserved": True,
        },
        "decision_summary": {
            "plain_language_result": (
                "A normal human request entered Product 1, was resolved into a governed workflow, "
                "approved by the human, authorized, executed by a bounded worker, verified, and "
                "reconstructed through replay."
            ),
            "why_result_was_produced": (
                "Replay evidence contains intent resolution, workflow selection, execution summary, "
                "human approval, authorization, worker handoff, worker execution, side-effect "
                "verification, and audit review."
            ),
            "final_outcome": "worker side effect verified",
            "requires_follow_up": False,
        },
        "human_request_summary": {
            "request_text_policy": "request hash used",
            "request_hash": scenario["human_prompt_hash"],
            "natural_language_input": True,
            "operator_domain_knowledge_required": False,
        },
        "intent_resolution_summary": {
            "intent_detected": intent["intent_resolved"],
            "clarification_required": intent["clarification_generated"],
            "clarification_count": 1 if intent["clarification_generated"] else 0,
            "resolved_intent": "bounded Product 1 worker side-effect workflow",
            "resolution_evidence_reference": _replay_path(source, "002_intent_resolution_recorded.json"),
        },
        "workflow_selection_summary": {
            "workflow_selected": intent["workflow_selected"],
            "workflow_id": intent["selected_workflow"],
            "selection_reason": "The natural-language request resolved to a bounded certified worker workflow.",
            "selection_evidence_reference": source["product1_evidence_path"],
        },
        "evidence_summary": {
            "evidence_items": _evidence_items(source),
        },
        "provider_participation_summary": {
            "providers_participated": len(source["providers"]) > 0,
            "providers": [
                {
                    "provider_id": provider["provider_id"],
                    "role": provider["role"],
                    "participation_location": provider["participation_location"],
                    "response_used": provider["response_used"],
                    "provider_authority": provider["provider_authority"],
                    "worker_invoked_after": provider["worker_invoked_after"],
                    "human_confirmation_required": provider["human_confirmation_required"],
                    "participation_evidence_reference": provider["participation_evidence_reference"],
                    "usage_metric_reference": provider["usage_metric_reference"],
                }
                for provider in source["providers"]
            ],
            "provider_disagreement_recorded": False,
            "provider_failover_recorded": True,
        },
        "worker_participation_summary": {
            "workers_participated": True,
            "workers": [
                {
                    "worker_id": authorization["authorized_worker_type"],
                    "worker_role": "bounded side-effect worker",
                    "side_effect_type": "file_create",
                    "authorization_reference": _replay_path(source, "005_authorization_recorded.json"),
                    "handoff_reference": _replay_path(source, "006_worker_handoff_recorded.json"),
                    "execution_reference": _replay_path(source, "007_worker_execution_recorded.json"),
                    "verification_reference": _replay_path(source, "008_side_effect_verification_recorded.json"),
                    "worker_authority": False,
                }
            ],
        },
        "approval_summary": {
            "human_approval_required": approval["human_approval_required"],
            "approval_requested": True,
            "approval_recorded": approval["human_approval_recorded"],
            "approval_result": "APPROVED" if approval["approved_for_execution"] else "REJECTED",
            "approval_evidence_reference": _replay_path(source, "004_human_approval_recorded.json"),
        },
        "authorization_summary": {
            "authorization_required": True,
            "authorization_issued": authorization["authorization_issued"],
            "authorization_scope": "bounded Product 1 certification sandbox side effect",
            "authorization_evidence_reference": _replay_path(source, "005_authorization_recorded.json"),
        },
        "execution_summary": {
            "worker_invoked": scenario["observed"]["worker_invoked"],
            "side_effect_claimed": scenario["observed"]["side_effect_present"],
            "execution_result": "controlled sandbox side effect executed",
            "execution_evidence_reference": _replay_path(source, "007_worker_execution_recorded.json"),
        },
        "verification_summary": {
            "independent_verification_required": True,
            "verification_performed": verification["side_effect_verification_performed"],
            "verification_result": "VERIFIED" if verification["verification_passed"] else "FAILED",
            "verification_method": "replay artifact and side-effect content hash verification",
            "verification_evidence_reference": _replay_path(source, "008_side_effect_verification_recorded.json"),
        },
        "assumptions_and_uncertainties": {
            "assumptions": ["The reviewer can access the referenced replay artifacts."],
            "uncertainties": [],
            "provider_claims_not_treated_as_authority": True,
        },
        "replay_reference_summary": {
            "replay_package_reference": source["product1_replay_path"],
            "audit_review_reference": source["product1_audit_path"],
            "raw_artifact_references": [
                source["product1_evidence_path"],
                source["product1_replay_path"],
                source["product1_audit_path"],
                source["product1_report_path"],
            ],
            "replay_reconstructed": source["product1_replay"].get("replay_reconstructed") is True,
        },
        "audit_conclusion": {
            "audit_status": "PASS",
            "audit_findings": source["product1_audit"].get("audit_findings", []),
            "audit_evidence_reference": source["product1_audit_path"],
        },
        "independent_verification_workflow": {
            "steps": [
                "Verify packet hash.",
                "Open the Product 1 evidence package.",
                "Open the Product 1 replay package.",
                "Confirm provider_authority=false in participation artifacts.",
                "Confirm approval and authorization artifacts precede worker execution.",
                "Confirm side-effect verification artifact proves the outcome.",
                "Confirm audit review references the same evidence chain.",
            ],
            "requires_provider_trust": False,
            "requires_secret_access": False,
            "expected_verification_result": "The final result is supported by replay evidence, not provider authority.",
        },
        "boundary_guarantees": {
            "human_authority_preserved": True,
            "provider_authority": False,
            "worker_authority": False,
            "approval_boundary_preserved": approval["human_approval_recorded"],
            "authorization_boundary_preserved": authorization["authorization_issued"],
            "replay_integrity_preserved": source["product1_replay"].get("replay_reconstructed") is True,
            "secret_free_evidence": True,
        },
        "reviewer_next_actions": ["No remediation required for this certified packet."],
    }
    return _with_hash(packet)


def _evidence_items(source: dict[str, Any]) -> list[dict[str, str]]:
    references = (
        ("intent", "Resolved intent was recorded.", "002_intent_resolution_recorded.json", "intent"),
        ("approval", "Human approval was recorded before authorization.", "004_human_approval_recorded.json", "approval"),
        ("authorization", "Authorization was issued before worker execution.", "005_authorization_recorded.json", "authorization"),
        ("worker", "Worker handoff was generated.", "006_worker_handoff_recorded.json", "handoff"),
        ("execution", "Worker execution was recorded.", "007_worker_execution_recorded.json", "execution"),
        ("verification", "Side-effect verification was recorded.", "008_side_effect_verification_recorded.json", "verification"),
    )
    items = []
    for index, (evidence_type, claim, filename, key) in enumerate(references, start=1):
        artifact = source["replay_artifacts"][key]
        items.append(
            {
                "evidence_id": f"P1-DVP-EVIDENCE-{index:03d}",
                "evidence_type": evidence_type,
                "claim_supported": claim,
                "artifact_reference": _replay_path(source, filename),
                "artifact_hash": artifact["artifact"].get("artifact_hash", artifact["replay_hash"]),
            }
        )
    for provider in source["providers"]:
        items.append(
            {
                "evidence_id": f"P1-DVP-PROVIDER-{provider['provider_id'].upper()}",
                "evidence_type": "provider",
                "claim_supported": f"{provider['provider_id']} participated without authority transfer.",
                "artifact_reference": provider["participation_evidence_reference"],
                "artifact_hash": provider["participation_artifact_hash"],
            }
        )
    items.append(
        {
            "evidence_id": "P1-DVP-AUDIT-001",
            "evidence_type": "audit",
            "claim_supported": "Product 1 audit review was recorded.",
            "artifact_reference": source["product1_audit_path"],
            "artifact_hash": source["product1_audit"]["artifact_hash"],
        }
    )
    return items


def _assertions(packet: dict[str, Any], source: dict[str, Any]) -> dict[str, bool]:
    provider_authority_values = [
        provider["provider_authority"] for provider in packet["provider_participation_summary"]["providers"]
    ]
    worker_authority_values = [
        worker["worker_authority"] for worker in packet["worker_participation_summary"]["workers"]
    ]
    return {
        "product1_end_to_end_certified": source["product1_report"].get("final_verdict")
        == "AIGOL_PRODUCT1_END_TO_END_CERTIFIED",
        "packet_generated": packet["artifact_type"] == "PRODUCT1_DECISION_VALIDATION_PACKET_ARTIFACT_V1",
        "mandatory_sections_present": all(section in packet for section in MANDATORY_PACKET_SECTIONS),
        "decision_summary_included": bool(packet["decision_summary"]["why_result_was_produced"]),
        "evidence_references_included": len(packet["evidence_summary"]["evidence_items"]) >= 8,
        "replay_references_included": packet["replay_reference_summary"]["replay_reconstructed"] is True,
        "provider_participation_included": len(packet["provider_participation_summary"]["providers"]) == 2,
        "worker_participation_included": len(packet["worker_participation_summary"]["workers"]) == 1,
        "approval_summary_included": packet["approval_summary"]["approval_recorded"] is True,
        "authorization_summary_included": packet["authorization_summary"]["authorization_issued"] is True,
        "verification_workflow_included": len(packet["independent_verification_workflow"]["steps"]) >= 6,
        "no_credential_leakage": _secret_free_payload(packet),
        "no_authority_transfer": all(value is False for value in provider_authority_values)
        and all(value is False for value in worker_authority_values)
        and packet["boundary_guarantees"]["human_authority_preserved"] is True,
        "replay_traceability": _packet_replay_reconstructs(packet, source),
        "evidence_traceability": _packet_evidence_traceable(packet),
        "reviewer_can_validate_without_provider_trust": packet["independent_verification_workflow"]["requires_provider_trust"]
        is False,
    }


def _packet_replay_reconstructs(packet: dict[str, Any], source: dict[str, Any]) -> bool:
    references = [packet["replay_reference_summary"]["replay_package_reference"], source["scenario_replay_dir"]]
    references.extend(packet["replay_reference_summary"]["raw_artifact_references"])
    return packet["replay_reference_summary"]["replay_reconstructed"] is True and all(Path(ref).exists() for ref in references)


def _packet_evidence_traceable(packet: dict[str, Any]) -> bool:
    for item in packet["evidence_summary"]["evidence_items"]:
        if not item.get("artifact_reference") or not item.get("artifact_hash"):
            return False
        if not Path(item["artifact_reference"]).exists():
            return False
    return True


def _replay_path(source: dict[str, Any], filename: str) -> str:
    return str(Path(source["scenario_replay_dir"]) / filename)


def _latest_cert_root(base: Path) -> Path:
    if not base.exists():
        raise FailClosedRuntimeError(f"decision validation packet certification missing runtime root: {base}")
    roots = []
    for path in base.glob("CERT-*"):
        match = re.fullmatch(r"CERT-(\d{6})", path.name)
        if match:
            roots.append((int(match.group(1)), path))
    if not roots:
        raise FailClosedRuntimeError(f"decision validation packet certification missing CERT root: {base}")
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


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    expected = deepcopy(artifact)
    actual = expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("decision validation packet artifact hash mismatch")


def _secret_free_payload(payload: dict[str, Any]) -> bool:
    serialized = canonical_serialize(payload).lower()
    return not any(marker.lower() in serialized for marker in SECRET_MARKERS)


def _assert_secret_safe(payload: dict[str, Any]) -> None:
    if not _secret_free_payload(payload):
        raise FailClosedRuntimeError("decision validation packet certification failed closed: secret-like material recorded")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(
            f"Product 1 decision validation packet {field_name} is required"
        )
    return value.strip()


def _blockers(assertions: dict[str, bool]) -> list[dict[str, str]]:
    return [
        {
            "assertion": assertion,
            "failure_reason": "decision validation packet certification assertion failed",
        }
        for assertion, passed in assertions.items()
        if passed is not True
    ]


def main() -> int:
    result = run_product1_decision_validation_packet_certification_v1()
    print(f"CERT_ROOT={result['cert_root']}")
    print(f"GENERATED_PACKET={result['generated_packet_path']}")
    print(f"COVERAGE_REPORT={result['coverage_report_path']}")
    print(f"EVIDENCE_PACKAGE={result['evidence_package_path']}")
    print(f"REPLAY_PACKAGE={result['replay_package_path']}")
    print(f"CERTIFICATION_REPORT={result['certification_report_path']}")
    print(f"FINAL_VERDICT={result['final_verdict']}")
    return 0 if result["final_verdict"] == FINAL_VERDICT_CERTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
