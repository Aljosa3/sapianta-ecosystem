"""Replay-visible operator summary for implementation handoff artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.conversation_to_implementation_handoff_runtime import (
    IMPLEMENTATION_HANDOFF_ARTIFACT_V1,
    IMPLEMENTATION_HANDOFF_CREATED,
    reconstruct_conversation_to_implementation_handoff_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPLEMENTATION_HANDOFF_VISIBILITY_VERSION = "AIGOL_IMPLEMENTATION_HANDOFF_VISIBILITY_V1"
IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1 = "IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1"
IMPLEMENTATION_HANDOFF_SUMMARY_CREATED = "IMPLEMENTATION_HANDOFF_SUMMARY_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "implementation_handoff_summary_recorded",
    "implementation_handoff_summary_returned",
)


def create_implementation_handoff_visibility_summary(
    *,
    visibility_id: str,
    handoff_replay_reference: str,
    approval_status: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a read-only human-readable summary from a certified handoff replay."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        handoff_reference = _require_string(handoff_replay_reference, "handoff_replay_reference")
        handoff = _load_handoff_artifact(Path(handoff_reference))
        reconstructed = reconstruct_conversation_to_implementation_handoff_replay(handoff_reference)
        _validate_handoff_lineage(handoff, reconstructed)
        artifact = _summary_artifact(
            visibility_id=visibility_id,
            handoff=handoff,
            handoff_replay_reference=handoff_reference,
            approval_status=approval_status,
            created_at=created_at,
            summary_status=IMPLEMENTATION_HANDOFF_SUMMARY_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_summary_artifact(
            visibility_id=visibility_id,
            handoff_replay_reference=handoff_replay_reference,
            approval_status=approval_status,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_implementation_handoff_visibility_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct implementation handoff visibility replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation handoff visibility replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("implementation handoff visibility replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "implementation handoff visibility")
        wrappers.append(wrapper)
    summary = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("summary_reference") != summary["summary_id"]:
        raise FailClosedRuntimeError("implementation handoff visibility replay reference mismatch")
    if returned.get("summary_hash") != summary["artifact_hash"]:
        raise FailClosedRuntimeError("implementation handoff visibility replay hash mismatch")
    if summary.get("summary_status") == IMPLEMENTATION_HANDOFF_SUMMARY_CREATED:
        if summary.get("summary_hash") != _summary_hash(summary):
            raise FailClosedRuntimeError("implementation handoff visibility summary hash mismatch")
        handoff = _load_handoff_artifact(Path(summary["handoff_replay_reference"]))
        if handoff["handoff_id"] != summary["handoff_reference"]:
            raise FailClosedRuntimeError("implementation handoff visibility handoff lineage mismatch")
        if handoff["artifact_hash"] != summary["handoff_artifact_hash"]:
            raise FailClosedRuntimeError("implementation handoff visibility handoff hash mismatch")
        if handoff["handoff_hash"] != summary["handoff_hash"]:
            raise FailClosedRuntimeError("implementation handoff visibility handoff summary lineage mismatch")
        if handoff["output_targets"] != summary["source_output_targets"]:
            raise FailClosedRuntimeError("implementation handoff visibility artifact lineage mismatch")
    return {
        "summary_id": summary["summary_id"],
        "summary_status": summary["summary_status"],
        "handoff_reference": summary["handoff_reference"],
        "target_domain": summary["target_domain"],
        "target_resource": summary["target_resource"],
        "target_worker": summary["target_worker"],
        "planned_artifacts": deepcopy(summary["planned_artifacts"]),
        "required_resource_roles": deepcopy(summary["required_resource_roles"]),
        "estimated_scope": deepcopy(summary["estimated_scope"]),
        "approval_status": summary["approval_status"],
        "summary_hash": summary["summary_hash"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "failure_reason": summary["failure_reason"],
    }


def render_implementation_handoff_visibility_summary(capture: dict[str, Any]) -> str:
    """Render the operator-facing handoff summary."""

    if capture.get("summary_status") == FAILED_CLOSED:
        return "\n".join(
            [
                "Handoff Summary",
                "",
                "FAILED_CLOSED",
                "",
                f"failure_reason: {capture.get('failure_reason')}",
            ]
        )
    lines = [
        "",
        "Handoff Summary",
        "",
        "Target Domain:",
        str(capture.get("target_domain")),
        "",
        "Target Resource:",
        str(capture.get("target_resource")),
        "",
        "Target Worker:",
        str(capture.get("target_worker") or "N/A"),
        "",
        "Planned Artifacts:",
        "",
    ]
    lines.extend(f"* {artifact}" for artifact in capture.get("planned_artifacts", []))
    lines.extend(["", "Required Resource Roles:", ""])
    lines.extend(f"* {role}" for role in capture.get("required_resource_roles", []))
    scope = capture.get("estimated_scope", {})
    lines.extend(
        [
            "",
            "Estimated Scope:",
            "",
            f"* governance artifacts: {scope.get('governance_artifacts')}",
            f"* runtime artifacts: {scope.get('runtime_artifacts')}",
            f"* tests: {scope.get('tests')}",
            "",
            "Approval Status:",
            str(capture.get("approval_status")),
            "",
            "Handoff Reference:",
            str(capture.get("handoff_reference")),
            "",
            "Summary Reference:",
            str(capture.get("implementation_handoff_visibility_replay_reference")),
        ]
    )
    return "\n".join(lines)


def _load_handoff_artifact(handoff_replay_path: Path) -> dict[str, Any]:
    wrapper = load_json(handoff_replay_path / "000_implementation_handoff_created.json")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: invalid handoff artifact")
    _verify_artifact_hash(artifact, "implementation handoff")
    if artifact.get("artifact_type") != IMPLEMENTATION_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: invalid handoff type")
    if artifact.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: handoff not created")
    return artifact


def _validate_handoff_lineage(handoff: dict[str, Any], reconstructed: dict[str, Any]) -> None:
    if reconstructed.get("handoff_id") != handoff["handoff_id"]:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: handoff lineage invalid")
    if reconstructed.get("handoff_status") != IMPLEMENTATION_HANDOFF_CREATED:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: handoff lineage invalid")
    if reconstructed.get("output_targets") != handoff["output_targets"]:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: artifact lineage invalid")


def _summary_artifact(
    *,
    visibility_id: str,
    handoff: dict[str, Any],
    handoff_replay_reference: str,
    approval_status: str,
    created_at: str,
    summary_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    target_resource = _target_resource(handoff)
    planned_artifacts = _planned_artifacts(handoff, target_resource)
    source_output_targets = deepcopy(handoff.get("output_targets", []))
    if not source_output_targets or not planned_artifacts:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: artifact plan invalid")
    artifact = {
        "artifact_type": IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_HANDOFF_VISIBILITY_VERSION,
        "summary_id": f"{_require_string(visibility_id, 'visibility_id')}:SUMMARY",
        "summary_status": summary_status,
        "handoff_reference": handoff["handoff_id"],
        "handoff_hash": handoff["handoff_hash"],
        "handoff_artifact_hash": handoff["artifact_hash"],
        "handoff_replay_reference": handoff_replay_reference,
        "proposal_reference": handoff["proposal_reference"],
        "proposal_hash": handoff["proposal_hash"],
        "target_domain": handoff["domain_reference"],
        "target_resource": target_resource,
        "target_worker": _target_worker(handoff, target_resource),
        "planned_artifacts": planned_artifacts,
        "source_output_targets": source_output_targets,
        "required_resource_roles": _required_resource_roles(handoff, target_resource),
        "estimated_scope": _estimated_scope(planned_artifacts, target_resource),
        "approval_status": _approval_display(approval_status),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "visibility_only": True,
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["summary_hash"] = _summary_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_summary_artifact(
    *,
    visibility_id: str,
    handoff_replay_reference: str,
    approval_status: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPLEMENTATION_HANDOFF_SUMMARY_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPLEMENTATION_HANDOFF_VISIBILITY_VERSION,
        "summary_id": f"{visibility_id}:SUMMARY",
        "summary_status": FAILED_CLOSED,
        "handoff_reference": None,
        "handoff_hash": None,
        "handoff_artifact_hash": None,
        "handoff_replay_reference": handoff_replay_reference,
        "proposal_reference": None,
        "proposal_hash": None,
        "target_domain": None,
        "target_resource": None,
        "target_worker": None,
        "planned_artifacts": [],
        "source_output_targets": [],
        "required_resource_roles": [],
        "estimated_scope": {"governance_artifacts": 0, "runtime_artifacts": 0, "tests": 0},
        "approval_status": _approval_display(approval_status),
        "created_at": created_at,
        "replay_visible": True,
        "visibility_only": True,
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "governance_modified": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": failure_reason,
    }
    artifact["summary_hash"] = _summary_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _target_resource(handoff: dict[str, Any]) -> str:
    milestone = handoff.get("milestone_reference")
    if milestone == "DOMAIN_FOUNDATION":
        return "DOMAIN"
    if milestone == "PROVIDER_FOUNDATION":
        return "PROVIDER"
    if milestone == "CAPABILITY_IMPROVEMENT":
        return "CAPABILITY"
    if milestone == "GOVERNANCE_POLICY":
        return "GOVERNANCE_POLICY"
    return "WORKER"


def _target_worker(handoff: dict[str, Any], target_resource: str) -> str | None:
    if target_resource == "WORKER":
        return handoff.get("worker_reference")
    return None


def _planned_artifacts(handoff: dict[str, Any], target_resource: str) -> list[str]:
    source_targets = list(handoff.get("output_targets", []))
    if target_resource == "WORKER":
        if any(target.startswith(("aigol/runtime/", "tests/")) for target in source_targets):
            return source_targets
        stem = _stem_from_targets(source_targets)
        runtime_name = stem.lower().replace("_worker_foundation_v1", "_worker_runtime")
        return [
            f"governance/{stem}.md",
            f"governance/{stem.replace('WORKER_FOUNDATION_V1', 'WORKER_MODEL_V1')}.md",
            f"governance/{stem.replace('WORKER_FOUNDATION_V1', 'WORKER_CERTIFICATION')}.json",
            f"aigol/runtime/{runtime_name}.py",
            f"tests/test_{runtime_name}_v1.py",
            f"tests/test_{stem.lower()}.py",
        ]
    if target_resource == "DOMAIN":
        stem = _stem_from_targets(source_targets)
        if any(target.startswith("aigol/runtime/") for target in source_targets) or any(
            target.startswith("tests/") for target in source_targets
        ):
            return source_targets
        artifacts = [
            f"governance/{stem}.md",
            f"governance/{stem.replace('DOMAIN_FOUNDATION_V1', 'DOMAIN_MODEL_V1')}.md",
            f"governance/{stem.replace('DOMAIN_FOUNDATION_V1', 'DOMAIN_CERTIFICATION')}.json",
        ]
        if stem == "MARKETING_DOMAIN_FOUNDATION_V1":
            artifacts.extend(
                [
                    "aigol/runtime/marketing_domain_runtime.py",
                    "tests/test_marketing_domain_runtime_v1.py",
                ]
            )
        return artifacts
    if target_resource == "PROVIDER":
        stem = _stem_from_targets(source_targets)
        return [
            f"governance/{stem}.md",
            f"governance/{stem.replace('ATTACHMENT_V1', 'CAPABILITY_MODEL_V1')}.md",
            f"governance/{stem.replace('ATTACHMENT_V1', 'CERTIFICATION')}.json",
        ]
    return source_targets


def _stem_from_targets(output_targets: list[str]) -> str:
    if not output_targets:
        raise FailClosedRuntimeError("implementation handoff visibility failed closed: artifact plan invalid")
    first = Path(output_targets[0]).name
    if first.endswith(".md"):
        return first[:-3]
    if first.endswith(".json"):
        return first[:-5]
    if first and "." not in first:
        return first
    raise FailClosedRuntimeError("implementation handoff visibility failed closed: artifact plan invalid")


def _required_resource_roles(handoff: dict[str, Any], target_resource: str) -> list[str]:
    if target_resource == "WORKER":
        return ["CLAUDE_CODE (WORKER_ROLE)"]
    if target_resource == "PROVIDER":
        return ["CLAUDE_CODE (PROVIDER_ROLE)"]
    return ["CLAUDE_CODE (PROVIDER_ROLE)"]


def _estimated_scope(planned_artifacts: list[str], target_resource: str) -> dict[str, int]:
    governance = sum(1 for artifact in planned_artifacts if artifact.startswith("governance/"))
    runtime = sum(1 for artifact in planned_artifacts if artifact.startswith("aigol/runtime/"))
    tests = sum(1 for artifact in planned_artifacts if artifact.startswith("tests/"))
    if target_resource == "WORKER":
        runtime = max(runtime, 1)
        tests = max(tests, 2)
    return {
        "governance_artifacts": governance,
        "runtime_artifacts": runtime,
        "tests": tests,
    }


def _approval_display(approval_status: str) -> str:
    if approval_status == "APPROVAL_NOT_REQUIRED_FOR_HANDOFF":
        return "NOT REQUIRED"
    return approval_status or "UNKNOWN"


def _summary_hash(summary: dict[str, Any]) -> str:
    return replay_hash(
        {
            "handoff_reference": summary.get("handoff_reference"),
            "handoff_hash": summary.get("handoff_hash"),
            "planned_artifacts": summary.get("planned_artifacts", []),
            "required_resource_roles": summary.get("required_resource_roles", []),
            "estimated_scope": summary.get("estimated_scope", {}),
            "approval_status": summary.get("approval_status"),
        }
    )


def _returned_artifact(summary: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(summary, "implementation handoff visibility")
    artifact = {
        "event_type": "IMPLEMENTATION_HANDOFF_SUMMARY_RETURNED",
        "summary_reference": summary["summary_id"],
        "summary_hash": summary["artifact_hash"],
        "handoff_reference": summary["handoff_reference"],
        "handoff_hash": summary["handoff_hash"],
        "approval_status": summary["approval_status"],
        "replay_visible": True,
        "visibility_only": True,
        "implementation_authorized": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "failure_reason": summary["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(summary: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = deepcopy(summary)
    capture.update(
        {
            "implementation_handoff_visibility_artifact": deepcopy(summary),
            "implementation_handoff_visibility_replay": deepcopy(returned),
            "implementation_handoff_visibility_replay_reference": str(replay_path),
            "fail_closed": summary["summary_status"] == FAILED_CLOSED,
        }
    )
    capture["implementation_handoff_visibility_capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "implementation handoff visibility")
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
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("implementation handoff visibility replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("implementation handoff visibility replay hash mismatch")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"implementation handoff visibility failed closed: {label} missing")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    reason = str(exc).strip()
    return reason or "implementation handoff visibility failed closed"
