"""Replay-visible post-execution review runtime for the current AiGOL chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.executable_domain_bundle_runtime import (
    EXECUTABLE_BUNDLE_VERIFIED,
    EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1,
    reconstruct_executable_domain_bundle_replay,
)
from aigol.runtime.multi_artifact_domain_bundle_runtime import (
    BUNDLE_VERIFIED,
    MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1,
    reconstruct_multi_artifact_domain_bundle_replay,
)
from aigol.runtime.real_output_binding_runtime import (
    ARTIFACT_VERIFIED,
    REAL_OUTPUT_BINDING_ARTIFACT_V1,
    reconstruct_real_output_binding_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_result_validation_runtime import (
    RESULT_VALIDATED,
    WORKER_RESULT_VALIDATION_ARTIFACT_V1,
    reconstruct_worker_result_validation_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    _domain_execution_ready_bridge_index,
    _matching_bridge_for_dispatch,
    _resolve_replay_reference,
)


AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION = "AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_V1"
POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1"
POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1 = "POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1"
REVIEW_COMPLETED = "REVIEW_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"

REPLAY_STEPS = (
    "review_evidence_recorded",
    "review_classification_recorded",
    "review_artifact_recorded",
    "review_result_recorded",
)


def detect_domain_post_execution_replay_review_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for post-execution replay review."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^review\s+post[-\s]execution\s+replay\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^review\s+execution\s+replay\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+replay\s+review$",
        r"^create\s+post[-\s]execution\s+replay\s+review\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_POST_EXECUTION_REPLAY_REVIEW"
            elif lowered.startswith("create"):
                action = "CREATE_POST_EXECUTION_REPLAY_REVIEW"
            else:
                action = "REVIEW_POST_EXECUTION_REPLAY"
            return {
                "post_execution_replay_review_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "post_execution_replay_review_action": action,
                "matched_prompt": normalized,
            }
    return {
        "post_execution_replay_review_entry_intent_detected": False,
        "domain_name": None,
        "post_execution_replay_review_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_result_validation_for_replay_review(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest validated Worker result for a domain without replay review."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("post-execution replay review failed closed: session root missing")
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/worker_result_validation")):
        try:
            reconstructed = reconstruct_worker_result_validation_replay(path)
            evidence_wrapper = load_json(path / "000_validation_evidence_recorded.json")
            wrapper = load_json(path / "002_validation_artifact_recorded.json")
            _verify_wrapper_hash(evidence_wrapper)
            _verify_wrapper_hash(wrapper)
            evidence = evidence_wrapper.get("artifact")
            validation = wrapper.get("artifact")
            if not isinstance(evidence, dict) or not isinstance(validation, dict):
                continue
            _verify_artifact_hash(evidence, "worker result validation evidence")
            _verify_artifact_hash(validation, "worker result validation artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("validation_status") != RESULT_VALIDATED:
            continue
        if _validation_domain(root, evidence, domain=domain, anchor=path) != domain.lower():
            continue
        if _validation_already_reviewed(
            root,
            validation_reference=str(validation.get("worker_result_validation_id") or ""),
            validation_hash=str(validation.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "worker_result_validation_replay_reference": str(path),
                "worker_result_validation_artifact": deepcopy(validation),
                "domain_name": domain_name,
                "worker_result_validation_reference": validation["worker_result_validation_id"],
                "worker_result_validation_hash": validation["artifact_hash"],
                "chain_id": validation["chain_id"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("post-execution replay review failed closed: matching validation not found")
    return candidates[-1]


def review_validated_worker_result(
    *,
    post_execution_replay_review_id: str,
    worker_result_validation_artifact: dict[str, Any],
    worker_result_validation_replay_reference: str,
    real_output_binding_artifact: dict[str, Any] | None = None,
    real_output_binding_replay_reference: str | None = None,
    domain_bundle_artifact: dict[str, Any] | None = None,
    domain_bundle_replay_reference: str | None = None,
    executable_bundle_artifact: dict[str, Any] | None = None,
    executable_bundle_replay_reference: str | None = None,
    reviewed_by: str,
    reviewed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Review a validated execution chain without retry, mutation, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_validation_lineage(
            Path(worker_result_validation_replay_reference),
            worker_result_validation_artifact,
        )
        output_binding = _load_output_binding_lineage(
            real_output_binding_artifact,
            real_output_binding_replay_reference,
            lineage["validation"],
        )
        domain_bundle = _load_domain_bundle_lineage(
            domain_bundle_artifact,
            domain_bundle_replay_reference,
            lineage["validation"],
        )
        executable_bundle = _load_executable_bundle_lineage(
            executable_bundle_artifact,
            executable_bundle_replay_reference,
            lineage["validation"],
        )
        if sum(item is not None for item in (output_binding, domain_bundle, executable_bundle)) > 1:
            raise FailClosedRuntimeError("post-execution replay review failed closed: multiple output realizations")
        validation = lineage["validation"]
        evidence = _evidence_artifact(
            review_id=post_execution_replay_review_id,
            validation=validation,
            lineage=lineage,
            output_binding=output_binding,
            domain_bundle=domain_bundle,
            executable_bundle=executable_bundle,
            validation_replay_reference=worker_result_validation_replay_reference,
            output_binding_replay_reference=real_output_binding_replay_reference,
            domain_bundle_replay_reference=domain_bundle_replay_reference,
            executable_bundle_replay_reference=executable_bundle_replay_reference,
            reviewed_at=reviewed_at,
        )
        classification = _classification_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            reviewed_at=reviewed_at,
        )
        review = _review_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            classification=classification,
            validation=validation,
            output_binding=output_binding,
            domain_bundle=domain_bundle,
            executable_bundle=executable_bundle,
            reviewed_by=reviewed_by,
            reviewed_at=reviewed_at,
        )
        result = _result_artifact(
            review_id=post_execution_replay_review_id,
            evidence=evidence,
            classification=classification,
            review=review,
            reviewed_at=reviewed_at,
            status=REVIEW_COMPLETED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], review)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, review, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            review_id=post_execution_replay_review_id,
            validation_reference=(
                worker_result_validation_artifact.get("worker_result_validation_id")
                if isinstance(worker_result_validation_artifact, dict)
                else None
            ),
            validation_replay_reference=worker_result_validation_replay_reference,
            reviewed_at=reviewed_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_post_execution_replay_review(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct post-execution replay review deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("post-execution replay review ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("post-execution replay review artifact must be a JSON object")
        _verify_artifact_hash(artifact, "post-execution replay review artifact")
        wrappers.append(wrapper)

    evidence, classification, review, result = (wrapper["artifact"] for wrapper in wrappers)
    if classification.get("review_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review evidence lineage mismatch")
    if review.get("review_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review classification lineage mismatch")
    if result.get("post_execution_replay_review_hash") != review["artifact_hash"]:
        raise FailClosedRuntimeError("post-execution replay review continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], review["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("post-execution replay review chain mismatch")
    _validate_review_artifact(review)
    _load_validation_lineage(Path(evidence["worker_result_validation_replay_reference"]), None, review=review)
    _load_output_binding_lineage(
        None,
        evidence.get("real_output_binding_replay_reference"),
        review,
    )
    _load_domain_bundle_lineage(
        None,
        evidence.get("domain_bundle_replay_reference"),
        review,
    )
    _load_executable_bundle_lineage(
        None,
        evidence.get("executable_bundle_replay_reference"),
        review,
    )
    return {
        "post_execution_replay_review_id": review["post_execution_replay_review_id"],
        "review_status": result["review_status"],
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_capture_reference": review["worker_result_capture_reference"],
        "execution_reference": review.get("execution_reference"),
        "execution_hash": review.get("execution_hash"),
        "execution_replay_hash": review.get("execution_replay_hash"),
        "execution_replay_reference": review.get("execution_replay_reference"),
        "execution_status": review.get("execution_status"),
        "worker_invocation_reference": review["worker_invocation_reference"],
        "worker_dispatch_reference": review["worker_dispatch_reference"],
        "authorization_reference": review["authorization_reference"],
        "execution_packet_reference": review["execution_packet_reference"],
        "worker_id": review["worker_id"],
        "chain_id": review["chain_id"],
        "replay_integrity_assessment": review["replay_integrity_assessment"],
        "authority_integrity_assessment": review["authority_integrity_assessment"],
        "execution_integrity_assessment": review["execution_integrity_assessment"],
        "validation_integrity_assessment": review["validation_integrity_assessment"],
        "output_binding_integrity_assessment": review["output_binding_integrity_assessment"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_review_boundary_flags(execution_bound=_validation_execution_bound(review)),
        "failure_reason": result["failure_reason"],
    }


def render_post_execution_replay_review_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Post-Execution Replay Review",
        "",
        f"Replay Review Status: {capture.get('review_status')}",
        f"Post-Execution Replay Review Reference: {capture.get('post_execution_replay_review_reference')}",
        f"Worker Result Validation Reference: {capture.get('worker_result_validation_reference')}",
        f"Reviewed Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('post_execution_replay_review_replay_reference')}",
        "",
        "Termination is a separate downstream stage.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_validation_lineage(
    validation_replay_path: Path,
    provided_validation: dict[str, Any] | None,
    *,
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reconstructed = reconstruct_worker_result_validation_replay(validation_replay_path)
    if reconstructed.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: validation invalid")
    wrappers = _load_wrappers(
        validation_replay_path,
        (
            "validation_evidence_recorded",
            "validation_classification_recorded",
            "validation_artifact_recorded",
            "validation_result_recorded",
        ),
        "worker result validation lineage artifact",
    )
    validation_evidence, validation_classification, validation, validation_result = (
        wrapper["artifact"] for wrapper in wrappers
    )
    if validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: validation inconsistency")
    if provided_validation is not None:
        _verify_artifact_hash(provided_validation, "provided worker result validation artifact")
        if provided_validation.get("worker_result_validation_id") != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
        if provided_validation.get("artifact_hash") != validation["artifact_hash"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
    if review is not None:
        if review.get("worker_result_validation_reference") != validation["worker_result_validation_id"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
        if review.get("worker_result_validation_hash") != validation["artifact_hash"]:
            raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_replay_reference",
            "execution_status",
        ):
            if review.get(field) != validation.get(field):
                raise FailClosedRuntimeError("post-execution replay review failed closed: validation mismatch")

    chain = _load_chain_artifacts(validation_evidence)
    checks = {
        "review_continuity": review is None or review.get("worker_result_validation_hash") == validation["artifact_hash"],
        "validation_continuity": validation_result["worker_result_validation_hash"] == validation["artifact_hash"],
        "result_capture_lineage": validation["worker_result_capture_hash"] == chain["result_capture"]["artifact_hash"],
        "invocation_lineage": validation["worker_invocation_hash"] == chain["invocation"]["artifact_hash"],
        "dispatch_lineage": validation["worker_dispatch_hash"] == chain["dispatch"]["artifact_hash"],
        "assignment_lineage": validation["worker_assignment_hash"] == chain["assignment"]["artifact_hash"],
        "authorization_lineage": validation["authorization_hash"] == chain["authorization"]["artifact_hash"],
        "handoff_lineage": bool(chain["request_evidence"].get("handoff_reference"))
        and bool(chain["request_evidence"].get("handoff_hash")),
        "packet_continuity": validation["execution_packet_reference"] == chain["request"]["execution_packet_reference"]
        and validation["execution_packet_hash"] == chain["request"]["execution_packet_hash"],
        "worker_continuity": validation["worker_id"] == chain["invocation"]["worker_id"]
        == chain["dispatch"]["worker_id"],
        "chain_continuity": len(
            {
                validation["chain_id"],
                chain["result_capture"]["chain_id"],
                chain["invocation"]["chain_id"],
                chain["dispatch"]["chain_id"],
                chain["assignment"]["canonical_chain_id"],
                chain["request"]["chain_id"],
                chain["authorization"]["chain_id"],
            }
        )
        == 1,
        "replay_continuity": reconstructed["validation_status"] == RESULT_VALIDATED,
        "authority_continuity": _validation_authority_continuity(validation),
        "execution_binding_lineage": _validation_execution_binding_continuity(
            validation_evidence,
            validation_classification,
            validation,
            validation_result,
        ),
        "hash_continuity": all(bool(artifact.get("artifact_hash")) for artifact in chain.values())
        and validation_classification["validation_evidence_hash"] == validation_evidence["artifact_hash"],
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("post-execution replay review failed closed: lineage continuity invalid")
    return {
        "validation_evidence": validation_evidence,
        "validation_classification": validation_classification,
        "validation": validation,
        "validation_result": validation_result,
        "chain": chain,
        "lineage_checks": checks,
    }


def _load_chain_artifacts(validation_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result_capture_evidence = _load_artifact(
        Path(validation_evidence["worker_result_capture_replay_reference"]),
        0,
        "result_capture_evidence_recorded",
    )
    result_capture = _load_artifact(
        Path(validation_evidence["worker_result_capture_replay_reference"]),
        2,
        "result_capture_artifact_recorded",
    )
    invocation_evidence = _load_artifact(
        Path(result_capture_evidence["worker_invocation_replay_reference"]),
        0,
        "invocation_evidence_recorded",
    )
    invocation = _load_artifact(
        Path(result_capture_evidence["worker_invocation_replay_reference"]),
        2,
        "invocation_artifact_recorded",
    )
    dispatch_evidence = _load_artifact(
        Path(invocation_evidence["worker_dispatch_replay_reference"]),
        0,
        "dispatch_evidence_recorded",
    )
    dispatch = _load_artifact(
        Path(invocation_evidence["worker_dispatch_replay_reference"]),
        2,
        "dispatch_artifact_recorded",
    )
    assignment_evidence = _load_artifact(
        Path(dispatch_evidence["worker_assignment_replay_reference"]),
        0,
        "assignment_evidence_recorded",
    )
    assignment = _load_artifact(
        Path(dispatch_evidence["worker_assignment_replay_reference"]),
        2,
        "assignment_artifact_recorded",
    )
    request_evidence = _load_artifact(
        Path(assignment_evidence["worker_invocation_request_replay_reference"]),
        0,
        "invocation_request_evidence_recorded",
    )
    request = _load_artifact(
        Path(assignment_evidence["worker_invocation_request_replay_reference"]),
        2,
        "invocation_request_artifact_recorded",
    )
    authorization = _load_artifact(
        Path(request_evidence["execution_authorization_replay_reference"]),
        2,
        "authorization_artifact_recorded",
    )
    return {
        "result_capture": result_capture,
        "invocation": invocation,
        "dispatch": dispatch,
        "assignment": assignment,
        "request": request,
        "request_evidence": request_evidence,
        "authorization": authorization,
    }


def _load_output_binding_lineage(
    provided_binding: dict[str, Any] | None,
    replay_reference: str | None,
    validation: dict[str, Any],
) -> dict[str, Any] | None:
    if provided_binding is None and replay_reference is None:
        return None
    if replay_reference is None:
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding lineage incomplete")
    reconstructed = reconstruct_real_output_binding_replay(Path(replay_reference))
    if reconstructed.get("verification_status") != ARTIFACT_VERIFIED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding verification invalid")
    wrapper = load_json(Path(replay_reference) / "002_output_binding_artifact_recorded.json")
    _verify_wrapper_hash(wrapper)
    binding = wrapper.get("artifact")
    if not isinstance(binding, dict):
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding replay corruption")
    _verify_artifact_hash(binding, "real output binding lineage artifact")
    if binding.get("artifact_type") != REAL_OUTPUT_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid output binding artifact")
    if provided_binding is not None:
        _verify_artifact_hash(provided_binding, "provided real output binding artifact")
        if provided_binding.get("real_output_binding_id") != binding.get("real_output_binding_id"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: output binding mismatch")
        if provided_binding.get("artifact_hash") != binding.get("artifact_hash"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: output binding mismatch")
    validation_reference = validation.get("worker_result_validation_id")
    validation_hash = validation.get("artifact_hash")
    if validation_reference is None:
        validation_reference = validation.get("worker_result_validation_reference")
        validation_hash = validation.get("worker_result_validation_hash")
    if binding.get("worker_result_validation_reference") != validation_reference:
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding validation mismatch")
    if binding.get("worker_result_validation_hash") != validation_hash:
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding validation mismatch")
    if binding.get("chain_id") != validation.get("chain_id"):
        raise FailClosedRuntimeError("post-execution replay review failed closed: output binding chain mismatch")
    return binding


def _load_domain_bundle_lineage(
    provided_bundle: dict[str, Any] | None,
    replay_reference: str | None,
    validation: dict[str, Any],
) -> dict[str, Any] | None:
    if provided_bundle is None and replay_reference is None:
        return None
    if replay_reference is None:
        raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle lineage incomplete")
    reconstructed = reconstruct_multi_artifact_domain_bundle_replay(Path(replay_reference))
    if reconstructed.get("bundle_verification_status") != BUNDLE_VERIFIED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle verification invalid")
    wrapper = load_json(Path(replay_reference) / "003_bundle_verification_result_recorded.json")
    _verify_wrapper_hash(wrapper)
    bundle = wrapper.get("artifact")
    _verify_artifact_hash(bundle, "domain bundle lineage artifact")
    if bundle.get("artifact_type") != MULTI_ARTIFACT_DOMAIN_BUNDLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid domain bundle artifact")
    if provided_bundle is not None:
        _verify_artifact_hash(provided_bundle, "provided domain bundle artifact")
        if provided_bundle.get("domain_bundle_runtime_id") != bundle.get("domain_bundle_runtime_id"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle mismatch")
        if provided_bundle.get("artifact_hash") != bundle.get("artifact_hash"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle mismatch")
    validation_reference = validation.get("worker_result_validation_id")
    validation_hash = validation.get("artifact_hash")
    if validation_reference is None:
        validation_reference = validation.get("worker_result_validation_reference")
        validation_hash = validation.get("worker_result_validation_hash")
    if bundle.get("worker_result_validation_reference") != validation_reference:
        raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle validation mismatch")
    if bundle.get("worker_result_validation_hash") != validation_hash:
        raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle validation mismatch")
    if bundle.get("chain_id") != validation.get("chain_id"):
        raise FailClosedRuntimeError("post-execution replay review failed closed: domain bundle chain mismatch")
    return bundle


def _load_executable_bundle_lineage(
    provided_bundle: dict[str, Any] | None,
    replay_reference: str | None,
    validation: dict[str, Any],
) -> dict[str, Any] | None:
    if provided_bundle is None and replay_reference is None:
        return None
    if replay_reference is None:
        raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle lineage incomplete")
    reconstructed = reconstruct_executable_domain_bundle_replay(Path(replay_reference))
    if reconstructed.get("executable_bundle_verification_status") != EXECUTABLE_BUNDLE_VERIFIED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle verification invalid")
    wrapper = load_json(Path(replay_reference) / "003_executable_bundle_verification_result_recorded.json")
    _verify_wrapper_hash(wrapper)
    bundle = wrapper.get("artifact")
    _verify_artifact_hash(bundle, "executable bundle lineage artifact")
    if bundle.get("artifact_type") != EXECUTABLE_DOMAIN_BUNDLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid executable bundle artifact")
    if provided_bundle is not None:
        _verify_artifact_hash(provided_bundle, "provided executable bundle artifact")
        if provided_bundle.get("executable_bundle_runtime_id") != bundle.get("executable_bundle_runtime_id"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle mismatch")
        if provided_bundle.get("artifact_hash") != bundle.get("artifact_hash"):
            raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle mismatch")
    validation_reference = validation.get("worker_result_validation_id")
    validation_hash = validation.get("artifact_hash")
    if validation_reference is None:
        validation_reference = validation.get("worker_result_validation_reference")
        validation_hash = validation.get("worker_result_validation_hash")
    if bundle.get("worker_result_validation_reference") != validation_reference:
        raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle validation mismatch")
    if bundle.get("worker_result_validation_hash") != validation_hash:
        raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle validation mismatch")
    if bundle.get("chain_id") != validation.get("chain_id"):
        raise FailClosedRuntimeError("post-execution replay review failed closed: executable bundle chain mismatch")
    return bundle


def _evidence_artifact(
    *,
    review_id: str,
    validation: dict[str, Any],
    lineage: dict[str, Any],
    output_binding: dict[str, Any] | None,
    domain_bundle: dict[str, Any] | None,
    executable_bundle: dict[str, Any] | None,
    validation_replay_reference: str,
    output_binding_replay_reference: str | None,
    domain_bundle_replay_reference: str | None,
    executable_bundle_replay_reference: str | None,
    reviewed_at: str,
) -> dict[str, Any]:
    chain = lineage["chain"]
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_evidence_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:EVIDENCE",
        "chain_id": validation["chain_id"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_validation_replay_reference": _require_string(
            validation_replay_reference, "worker_result_validation_replay_reference"
        ),
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "worker_invocation_reference": validation["worker_invocation_reference"],
        "worker_invocation_hash": validation["worker_invocation_hash"],
        "worker_dispatch_reference": validation["worker_dispatch_reference"],
        "worker_dispatch_hash": validation["worker_dispatch_hash"],
        "worker_assignment_reference": validation["worker_assignment_reference"],
        "worker_assignment_hash": validation["worker_assignment_hash"],
        "authorization_reference": validation["authorization_reference"],
        "authorization_hash": validation["authorization_hash"],
        "execution_packet_reference": validation["execution_packet_reference"],
        "execution_packet_hash": validation["execution_packet_hash"],
        "execution_reference": validation.get("execution_reference"),
        "execution_hash": validation.get("execution_hash"),
        "execution_replay_hash": validation.get("execution_replay_hash"),
        "execution_replay_reference": validation.get("execution_replay_reference"),
        "execution_status": validation.get("execution_status"),
        "handoff_reference": chain["request_evidence"]["handoff_reference"],
        "handoff_hash": chain["request_evidence"]["handoff_hash"],
        "worker_id": validation["worker_id"],
        "worker_hash": validation["worker_hash"],
        "worker_family": validation["worker_family"],
        "worker_role": validation["worker_role"],
        "validation_requirements": deepcopy(validation["validation_requirements"]),
        "real_output_binding_reference": output_binding["real_output_binding_id"] if output_binding else None,
        "real_output_binding_hash": output_binding["artifact_hash"] if output_binding else None,
        "real_output_binding_replay_reference": (
            _require_string(output_binding_replay_reference, "real_output_binding_replay_reference")
            if output_binding
            else None
        ),
        "artifact_creation_review_required": output_binding is not None,
        "domain_bundle_reference": domain_bundle["domain_bundle_runtime_id"] if domain_bundle else None,
        "domain_bundle_hash": domain_bundle["artifact_hash"] if domain_bundle else None,
        "domain_bundle_replay_reference": (
            _require_string(domain_bundle_replay_reference, "domain_bundle_replay_reference")
            if domain_bundle
            else None
        ),
        "bundle_creation_review_required": domain_bundle is not None,
        "executable_bundle_reference": executable_bundle["executable_bundle_runtime_id"] if executable_bundle else None,
        "executable_bundle_hash": executable_bundle["artifact_hash"] if executable_bundle else None,
        "executable_bundle_replay_reference": (
            _require_string(executable_bundle_replay_reference, "executable_bundle_replay_reference")
            if executable_bundle
            else None
        ),
        "executable_bundle_review_required": executable_bundle is not None,
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(execution_bound=_validation_execution_bound(validation)),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(*, review_id: str, evidence: dict[str, Any], reviewed_at: str) -> dict[str, Any]:
    checks = evidence["lineage_checks"]
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_classification_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:CLASSIFICATION",
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "chain_id": evidence["chain_id"],
        "review_classification": "EXECUTION_CHAIN_INTEGRITY_VERIFIED",
        "replay_integrity_assessment": INTEGRITY_VERIFIED if checks["replay_continuity"] and checks["hash_continuity"] else FAILED_CLOSED,
        "authority_integrity_assessment": INTEGRITY_VERIFIED if checks["authority_continuity"] else FAILED_CLOSED,
        "execution_integrity_assessment": INTEGRITY_VERIFIED if all(
            checks[key]
            for key in (
                "handoff_lineage",
                "authorization_lineage",
                "invocation_lineage",
                "dispatch_lineage",
                "assignment_lineage",
                "result_capture_lineage",
                "packet_continuity",
                "worker_continuity",
                "chain_continuity",
                "execution_binding_lineage",
            )
        )
        else FAILED_CLOSED,
        "validation_integrity_assessment": INTEGRITY_VERIFIED if checks["validation_continuity"] else FAILED_CLOSED,
        "output_binding_integrity_assessment": INTEGRITY_VERIFIED,
        "classified_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(execution_bound=evidence.get("execution_started") is True),
    }
    if FAILED_CLOSED in (
        artifact["replay_integrity_assessment"],
        artifact["authority_integrity_assessment"],
        artifact["execution_integrity_assessment"],
        artifact["validation_integrity_assessment"],
        artifact["output_binding_integrity_assessment"],
    ):
        raise FailClosedRuntimeError("post-execution replay review failed closed: integrity assessment failed")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _review_artifact(
    *,
    review_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    validation: dict[str, Any],
    output_binding: dict[str, Any] | None,
    domain_bundle: dict[str, Any] | None,
    executable_bundle: dict[str, Any] | None,
    reviewed_by: str,
    reviewed_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "post_execution_replay_review_id": _require_string(review_id, "post_execution_replay_review_id"),
        "review_status": REVIEW_COMPLETED,
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "review_classification_reference": classification["review_classification_id"],
        "review_classification_hash": classification["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "worker_invocation_reference": validation["worker_invocation_reference"],
        "worker_invocation_hash": validation["worker_invocation_hash"],
        "worker_dispatch_reference": validation["worker_dispatch_reference"],
        "worker_dispatch_hash": validation["worker_dispatch_hash"],
        "authorization_reference": validation["authorization_reference"],
        "authorization_hash": validation["authorization_hash"],
        "execution_packet_reference": validation["execution_packet_reference"],
        "execution_packet_hash": validation["execution_packet_hash"],
        "execution_reference": validation.get("execution_reference"),
        "execution_hash": validation.get("execution_hash"),
        "execution_replay_hash": validation.get("execution_replay_hash"),
        "execution_replay_reference": validation.get("execution_replay_reference"),
        "execution_status": validation.get("execution_status"),
        "handoff_reference": evidence["handoff_reference"],
        "handoff_hash": evidence["handoff_hash"],
        "worker_id": validation["worker_id"],
        "worker_hash": validation["worker_hash"],
        "worker_family": validation["worker_family"],
        "worker_role": validation["worker_role"],
        "chain_id": validation["chain_id"],
        "replay_integrity_assessment": classification["replay_integrity_assessment"],
        "authority_integrity_assessment": classification["authority_integrity_assessment"],
        "execution_integrity_assessment": classification["execution_integrity_assessment"],
        "validation_integrity_assessment": classification["validation_integrity_assessment"],
        "output_binding_integrity_assessment": classification["output_binding_integrity_assessment"],
        "real_output_binding_reference": output_binding["real_output_binding_id"] if output_binding else None,
        "real_output_binding_hash": output_binding["artifact_hash"] if output_binding else None,
        "artifact_creation_reviewed": output_binding is not None,
        "domain_bundle_reference": domain_bundle["domain_bundle_runtime_id"] if domain_bundle else None,
        "domain_bundle_hash": domain_bundle["artifact_hash"] if domain_bundle else None,
        "bundle_creation_reviewed": domain_bundle is not None,
        "executable_bundle_reference": executable_bundle["executable_bundle_runtime_id"] if executable_bundle else None,
        "executable_bundle_hash": executable_bundle["artifact_hash"] if executable_bundle else None,
        "executable_bundle_reviewed": executable_bundle is not None,
        "reviewed_by": _require_string(reviewed_by, "reviewed_by"),
        "reviewed_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(execution_bound=_validation_execution_bound(validation)),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_review_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    review_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    review: dict[str, Any],
    reviewed_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_result_id": f"{_require_string(review_id, 'post_execution_replay_review_id')}:RESULT",
        "review_status": status,
        "review_evidence_reference": evidence["review_evidence_id"],
        "review_evidence_hash": evidence["artifact_hash"],
        "review_classification_reference": classification["review_classification_id"],
        "review_classification_hash": classification["artifact_hash"],
        "post_execution_replay_review_reference": review["post_execution_replay_review_id"],
        "post_execution_replay_review_hash": review["artifact_hash"],
        "worker_result_validation_reference": review["worker_result_validation_reference"],
        "worker_result_validation_hash": review["worker_result_validation_hash"],
        "execution_reference": review.get("execution_reference"),
        "execution_hash": review.get("execution_hash"),
        "execution_replay_hash": review.get("execution_replay_hash"),
        "execution_replay_reference": review.get("execution_replay_reference"),
        "execution_status": review.get("execution_status"),
        "chain_id": review["chain_id"],
        "completed_at": _require_string(reviewed_at, "reviewed_at"),
        "replay_visible": True,
        **_post_review_boundary_flags(execution_bound=_validation_execution_bound(review)),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    review_id: str,
    validation_reference: str | None,
    validation_replay_reference: str,
    reviewed_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": POST_EXECUTION_REPLAY_REVIEW_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_VERSION,
        "review_result_id": f"{review_id}:RESULT",
        "review_status": FAILED_CLOSED,
        "review_evidence_reference": None,
        "review_evidence_hash": None,
        "review_classification_reference": None,
        "review_classification_hash": None,
        "post_execution_replay_review_reference": None,
        "post_execution_replay_review_hash": None,
        "worker_result_validation_reference": validation_reference,
        "worker_result_validation_hash": None,
        "worker_result_validation_replay_reference": validation_replay_reference,
        "chain_id": None,
        "completed_at": reviewed_at,
        "replay_visible": True,
        **_pre_review_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    review: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "review_evidence_artifact": deepcopy(evidence),
            "review_classification_artifact": deepcopy(classification),
            "post_execution_replay_review_artifact": deepcopy(review),
            "review_result_artifact": deepcopy(result),
            "post_execution_replay_review_reference": review.get("post_execution_replay_review_id") if review else None,
            "worker_result_validation_reference": review.get("worker_result_validation_reference") if review else None,
            "execution_reference": review.get("execution_reference") if review else None,
            "execution_hash": review.get("execution_hash") if review else None,
            "execution_replay_reference": review.get("execution_replay_reference") if review else None,
            "worker_id": review.get("worker_id") if review else None,
            "post_execution_replay_review_replay_reference": str(replay_path),
            "fail_closed": result["review_status"] == FAILED_CLOSED,
        }
    )
    capture["post_execution_replay_review_capture_hash"] = replay_hash(capture)
    return capture


def _validation_domain(root: Path, evidence: dict[str, Any], *, domain: str, anchor: Path) -> str | None:
    try:
        result_capture_replay = _resolve_replay_reference(
            evidence.get("worker_result_capture_replay_reference"),
            anchor=anchor,
        )
        result_capture_evidence = _load_artifact(result_capture_replay, 0, "result_capture_evidence_recorded")
        invocation_replay = _resolve_replay_reference(
            result_capture_evidence.get("worker_invocation_replay_reference"),
            anchor=result_capture_replay,
        )
        invocation_evidence = _load_artifact(invocation_replay, 0, "invocation_evidence_recorded")
        dispatch_replay = _resolve_replay_reference(
            invocation_evidence.get("worker_dispatch_replay_reference"),
            anchor=invocation_replay,
        )
        dispatch = _load_artifact(dispatch_replay, 2, "dispatch_artifact_recorded")
        bridge = _matching_bridge_for_dispatch(
            dispatch_replay,
            dispatch,
            _domain_execution_ready_bridge_index(root, domain),
        )
        if bridge is not None:
            return str(bridge["approved_domain"]).lower()
    except FailClosedRuntimeError:
        return None
    return None


def _validation_already_reviewed(
    root: Path,
    *,
    validation_reference: str,
    validation_hash: str,
) -> bool:
    for path in root.glob("TURN-*/post_execution_replay_review"):
        try:
            reconstructed = reconstruct_post_execution_replay_review(path)
            wrapper = load_json(path / "002_review_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            review = wrapper.get("artifact")
            if not isinstance(review, dict):
                continue
            _verify_artifact_hash(review, "post-execution replay review artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("review_status") != REVIEW_COMPLETED:
            continue
        if (
            review.get("worker_result_validation_reference") == validation_reference
            and review.get("worker_result_validation_hash") == validation_hash
        ):
            return True
    return False


def _validate_review_artifact(review: dict[str, Any]) -> None:
    if review.get("artifact_type") != POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid review artifact")
    if review.get("review_status") != REVIEW_COMPLETED:
        raise FailClosedRuntimeError("post-execution replay review failed closed: invalid review status")
    execution_bound = _validation_execution_bound(review)
    for field, expected in _post_review_boundary_flags(execution_bound=execution_bound).items():
        if review.get(field) is not expected:
            raise FailClosedRuntimeError("post-execution replay review failed closed: authority drift")
    for field in (
        "post_execution_replay_review_id",
        "worker_result_validation_reference",
        "worker_result_validation_hash",
        "worker_result_capture_reference",
        "worker_result_capture_hash",
        "worker_invocation_reference",
        "worker_invocation_hash",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "handoff_reference",
        "handoff_hash",
        "worker_id",
        "worker_hash",
        "chain_id",
        "reviewed_by",
        "reviewed_at",
    ):
        _require_string(review.get(field), field)
    if execution_bound:
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_replay_reference",
            "execution_status",
        ):
            _require_string(review.get(field), field)
        if review.get("execution_status") != "EXECUTING":
            raise FailClosedRuntimeError("post-execution replay review failed closed: invalid execution state")
    for assessment in (
        "replay_integrity_assessment",
        "authority_integrity_assessment",
        "execution_integrity_assessment",
        "validation_integrity_assessment",
        "output_binding_integrity_assessment",
    ):
        if review.get(assessment) != INTEGRITY_VERIFIED:
            raise FailClosedRuntimeError("post-execution replay review failed closed: integrity assessment failed")


def _validation_authority_continuity(validation: dict[str, Any]) -> bool:
    execution_bound = _validation_execution_bound(validation)
    return all(
        validation.get(field) is expected
        for field, expected in _pre_review_boundary_flags(execution_bound=execution_bound).items()
    )


def _validation_execution_binding_continuity(
    validation_evidence: dict[str, Any],
    validation_classification: dict[str, Any],
    validation: dict[str, Any],
    validation_result: dict[str, Any],
) -> bool:
    execution_bound = _validation_execution_bound(validation)
    if not execution_bound:
        return not _has_execution_binding(validation_evidence, validation_classification, validation, validation_result)
    required = (
        "execution_reference",
        "execution_hash",
        "execution_replay_hash",
        "execution_replay_reference",
        "execution_status",
    )
    if any(not _nonempty_string(validation.get(field)) for field in required):
        return False
    if validation.get("execution_started") is not True:
        return False
    for artifact in (validation_evidence, validation_classification, validation_result):
        if artifact.get("execution_reference") != validation["execution_reference"]:
            return False
        if artifact.get("execution_hash") != validation["execution_hash"]:
            return False
    if validation_evidence.get("execution_replay_hash") != validation["execution_replay_hash"]:
        return False
    if validation_evidence.get("execution_replay_reference") != validation["execution_replay_reference"]:
        return False
    if validation_result.get("execution_replay_reference") != validation["execution_replay_reference"]:
        return False
    if validation_evidence.get("execution_status") != validation["execution_status"]:
        return False
    if validation.get("execution_status") != "EXECUTING":
        return False
    return True


def _validation_execution_bound(validation: dict[str, Any]) -> bool:
    if validation.get("execution_started") is True:
        return True
    return _has_execution_binding(validation)


def _has_execution_binding(*artifacts: dict[str, Any]) -> bool:
    fields = (
        "execution_reference",
        "execution_hash",
        "execution_replay_hash",
        "execution_replay_reference",
        "execution_status",
    )
    return any(artifact.get(field) is not None for artifact in artifacts for field in fields)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _pre_review_boundary_flags(*, execution_bound: bool = False) -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": execution_bound,
        "result_created": True,
        "worker_result_captured": True,
        "result_validated": True,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_review_boundary_flags(*, execution_bound: bool = False) -> dict[str, bool]:
    flags = _pre_review_boundary_flags(execution_bound=execution_bound)
    flags["post_execution_replay_reviewed"] = True
    return flags


def _load_wrappers(path: Path, steps: tuple[str, ...], label: str) -> list[dict[str, Any]]:
    wrappers = []
    for index, step in enumerate(steps):
        wrapper = load_json(path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(f"{label} must be a JSON object")
        _verify_artifact_hash(artifact, label)
        wrappers.append(wrapper)
    return wrappers


def _load_artifact(path: Path, index: int, step: str) -> dict[str, Any]:
    wrapper = load_json(path / f"{index:03d}_{step}.json")
    if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
        raise FailClosedRuntimeError("post-execution replay review failed closed: replay continuity mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("post-execution replay review failed closed: replay corruption")
    _verify_artifact_hash(artifact, "post-execution chain artifact")
    return artifact


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("post-execution replay review ordering mismatch")
    _verify_artifact_hash(artifact, "post-execution replay review artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("post-execution replay review replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("post-execution replay review replay hash mismatch")


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"post-execution replay review failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"post-execution replay review failed closed: {exc}"
