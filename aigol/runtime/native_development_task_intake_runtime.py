"""Replay-visible native development task intake runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_domain_resolution_bridge import (
    DOMAIN_RESOLVED,
    resolve_native_development_domain,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RUNTIME_VERSION = "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RUNTIME_V1"
AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1 = "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1"
NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED = "NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED"
FAILED_CLOSED = "FAILED_CLOSED"
REPLAY_STEPS = ("native_development_task_intake_recorded", "native_development_task_intake_returned")

MILESTONE_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+_V\d+)\b")
GENERIC_DEVELOPMENT_MILESTONE_ID = "AIGOL_GENERIC_DEVELOPMENT_TASK_V1"
SUPPORTED_DOMAINS = ("TRADING", "MARKETING", "GOVERNANCE", "COGNITION", "AIGOL")
FORBIDDEN_AUTHORITY_TERMS = (
    "dispatch",
    "invoke",
    "execute",
    "create execution request",
    "order placement",
    "place order",
    "live trading",
    "broker integration",
    "exchange integration",
    "authority mutation",
    "mutate governance",
    "mutate replay",
)
CONSTRAINT_TERMS = (
    "review only",
    "foundation only",
    "no broker integration",
    "no exchange integration",
    "no order placement",
    "no live trading",
    "no financial claims",
    "no dispatch",
    "no invocation",
    "no execution",
    "no governance mutation",
    "no replay mutation",
)


def is_native_development_prompt(human_prompt: str) -> bool:
    """Return whether a prompt looks like a native development request."""

    prompt = _normalize_text(human_prompt, "human_prompt")
    lowered = prompt.lower()
    return (
        bool(MILESTONE_PATTERN.search(prompt))
        and any(marker in lowered for marker in ("implement", "create", "open", "foundation", "runtime", "worker", "domain"))
    ) or is_plain_native_development_prompt(prompt)


def is_plain_native_development_prompt(human_prompt: str) -> bool:
    """Return whether a non-milestone prompt is a low-risk deterministic development request."""

    prompt = _normalize_text(human_prompt, "human_prompt")
    lowered = prompt.lower()
    if MILESTONE_PATTERN.search(prompt):
        return False
    if _has_unacceptable_authority(prompt):
        return False
    if any(term in lowered for term in ("deploy", "production", "external users", "domain", "business")):
        return False
    freeform_development_subject = any(
        term in lowered
        for term in (
            "calculator utility",
            "python tool",
            "validation script",
            "csv",
        )
    )
    if freeform_development_subject and any(term in lowered for term in ("need", "create", "build")):
        return True
    return (
        lowered.startswith(("implement ", "build ", "add ", "create "))
        and any(
            term in lowered
            for term in (
                "function",
                "test",
                "runtime",
                "helper",
                "validator",
                "parser",
                "support",
                "workflow",
                "ci",
                "github actions",
            )
        )
    )


def run_native_development_task_intake(
    *,
    intake_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None = None,
    turn_id: str | None = None,
) -> dict[str, Any]:
    """Persist a replay-visible native development task intake result."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        prompt = _normalize_text(human_prompt, "human_prompt")
        analysis = _analyze_prompt(prompt)
        artifact = _intake_artifact(
            intake_id=intake_id,
            human_prompt_reference=human_prompt_reference,
            human_prompt=prompt,
            created_at=created_at,
            session_id=session_id,
            turn_id=turn_id,
            intake_status=NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED,
            failure_reason=None,
            **analysis,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_artifact(
            intake_id=intake_id,
            human_prompt_reference=human_prompt_reference,
            human_prompt=human_prompt,
            created_at=created_at,
            session_id=session_id,
            turn_id=turn_id,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_native_development_task_intake_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct native development task intake replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("native development task intake replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("native development task intake replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    intake = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("intake_reference") != intake["intake_id"]:
        raise FailClosedRuntimeError("native development task intake replay reference mismatch")
    if returned.get("intake_hash") != intake["artifact_hash"]:
        raise FailClosedRuntimeError("native development task intake replay hash mismatch")
    return {
        "intake_id": intake["intake_id"],
        "intake_status": intake["intake_status"],
        "requested_milestone_id": intake["requested_milestone_id"],
        "requested_domain": intake["requested_domain"],
        "requested_worker_family": intake["requested_worker_family"],
        "requested_output_scope": deepcopy(intake["requested_output_scope"]),
        "explicit_constraints": deepcopy(intake["explicit_constraints"]),
        "task_kind": intake["task_kind"],
        "safe_for_native_development": intake["safe_for_native_development"],
        "codex_assisted_handoff_required": intake["codex_assisted_handoff_required"],
        "suggested_next_safe_handoff": intake["suggested_next_safe_handoff"],
        "failure_reason": intake["failure_reason"],
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def render_native_development_task_summary(capture: dict[str, Any]) -> str:
    artifact = capture["native_development_task_intake_artifact"]
    lines = [
        f"recognized_development_task: {artifact['intake_status']}",
        f"requested_milestone_id: {artifact['requested_milestone_id']}",
        f"requested_domain: {artifact['requested_domain']}",
        f"requested_worker_family: {artifact['requested_worker_family']}",
        f"task_kind: {artifact['task_kind']}",
        f"explicit_constraints: {', '.join(artifact['explicit_constraints']) or 'NONE'}",
        f"safe_for_native_development: {artifact['safe_for_native_development']}",
        f"codex_assisted_handoff_required: {artifact['codex_assisted_handoff_required']}",
        f"suggested_next_safe_handoff: {artifact['suggested_next_safe_handoff']}",
    ]
    if artifact.get("failure_reason"):
        lines.append(f"failure_reason: {artifact['failure_reason']}")
    return "\n".join(lines)


def _analyze_prompt(prompt: str) -> dict[str, Any]:
    milestone_ids = MILESTONE_PATTERN.findall(prompt)
    unique_milestones = sorted(set(milestone_ids))
    if not unique_milestones and is_plain_native_development_prompt(prompt):
        milestone_id = GENERIC_DEVELOPMENT_MILESTONE_ID
        domain_resolution = resolve_native_development_domain(
            human_prompt=prompt,
            requested_milestone_id=milestone_id,
            detected_domain="AIGOL",
        )
        if domain_resolution["resolution_status"] != DOMAIN_RESOLVED:
            raise FailClosedRuntimeError(domain_resolution["failure_reason"])
        return {
            "requested_milestone_id": milestone_id,
            "requested_domain": domain_resolution["resolved_domain"],
            "domain_resolution_bridge": domain_resolution,
            "requested_worker_family": "CLAUDE_EXTERNAL",
            "requested_output_scope": _output_scope("WORKER", milestone_id),
            "explicit_constraints": _constraints(prompt),
            "task_kind": "WORKER",
            "safe_for_native_development": True,
            "codex_assisted_handoff_required": True,
            "suggested_next_safe_handoff": "Codex-assisted implementation handoff for generic development task",
        }
    if len(unique_milestones) != 1:
        raise FailClosedRuntimeError("native development task intake failed closed: milestone id cannot be identified")
    if _has_unacceptable_authority(prompt):
        raise FailClosedRuntimeError("native development task intake failed closed: request implies prohibited authority")
    milestone_id = unique_milestones[0]
    task_kind = _task_kind(prompt, milestone_id)
    if task_kind == "AMBIGUOUS":
        raise FailClosedRuntimeError("native development task intake failed closed: requested scope is ambiguous")
    domain_resolution = resolve_native_development_domain(
        human_prompt=prompt,
        requested_milestone_id=milestone_id,
        detected_domain=_detect_domain(prompt, milestone_id),
    )
    if domain_resolution["resolution_status"] != DOMAIN_RESOLVED:
        raise FailClosedRuntimeError(domain_resolution["failure_reason"])
    domain = domain_resolution["resolved_domain"]
    worker_family = _detect_worker_family(milestone_id)
    return {
        "requested_milestone_id": milestone_id,
        "requested_domain": domain,
        "domain_resolution_bridge": domain_resolution,
        "requested_worker_family": worker_family,
        "requested_output_scope": _output_scope(task_kind, milestone_id),
        "explicit_constraints": _constraints(prompt),
        "task_kind": task_kind,
        "safe_for_native_development": True,
        "codex_assisted_handoff_required": True,
        "suggested_next_safe_handoff": f"Codex-assisted implementation handoff for {milestone_id}",
    }


def _intake_artifact(
    *,
    intake_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
    session_id: str | None,
    turn_id: str | None,
    requested_milestone_id: str | None,
    requested_domain: str | None,
    domain_resolution_bridge: dict[str, Any] | None,
    requested_worker_family: str | None,
    requested_output_scope: list[str],
    explicit_constraints: list[str],
    task_kind: str,
    safe_for_native_development: bool,
    codex_assisted_handoff_required: bool,
    suggested_next_safe_handoff: str | None,
    intake_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1,
        "runtime_version": AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RUNTIME_VERSION,
        "intake_id": _require_string(intake_id, "intake_id"),
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt_hash": replay_hash({"human_prompt": _normalize_text(human_prompt, "human_prompt")}),
        "session_id": session_id,
        "turn_id": turn_id,
        "requested_milestone_id": requested_milestone_id,
        "requested_domain": requested_domain,
        "domain_resolution_bridge": deepcopy(domain_resolution_bridge),
        "requested_worker_family": requested_worker_family,
        "requested_output_scope": list(requested_output_scope),
        "explicit_constraints": list(explicit_constraints),
        "task_kind": task_kind,
        "safe_for_native_development": safe_for_native_development,
        "codex_assisted_handoff_required": codex_assisted_handoff_required,
        "suggested_next_safe_handoff": suggested_next_safe_handoff,
        "intake_status": intake_status,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_artifact(
    *,
    intake_id: str,
    human_prompt_reference: str,
    human_prompt: Any,
    created_at: str,
    session_id: str | None,
    turn_id: str | None,
    failure_reason: str,
) -> dict[str, Any]:
    prompt = human_prompt if isinstance(human_prompt, str) and human_prompt.strip() else "INVALID_PROMPT"
    milestone_ids = sorted(set(MILESTONE_PATTERN.findall(prompt))) if isinstance(prompt, str) else []
    return _intake_artifact(
        intake_id=intake_id,
        human_prompt_reference=human_prompt_reference,
        human_prompt=prompt,
        created_at=created_at,
        session_id=session_id,
        turn_id=turn_id,
        requested_milestone_id=milestone_ids[0] if len(milestone_ids) == 1 else None,
        requested_domain=_detect_domain(prompt, milestone_ids[0]) if len(milestone_ids) == 1 else None,
        domain_resolution_bridge=None,
        requested_worker_family=_detect_worker_family(milestone_ids[0]) if len(milestone_ids) == 1 else None,
        requested_output_scope=[],
        explicit_constraints=_constraints(prompt) if isinstance(prompt, str) else [],
        task_kind="FAILED_CLOSED",
        safe_for_native_development=False,
        codex_assisted_handoff_required=True,
        suggested_next_safe_handoff=None,
        intake_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(intake: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(intake)
    returned = {
        "event_type": "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RETURNED",
        "intake_reference": intake["intake_id"],
        "intake_hash": intake["artifact_hash"],
        "intake_status": intake["intake_status"],
        "requested_milestone_id": intake["requested_milestone_id"],
        "safe_for_native_development": intake["safe_for_native_development"],
        "codex_assisted_handoff_required": intake["codex_assisted_handoff_required"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "failure_reason": intake["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(intake: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "native_development_task_intake_artifact": deepcopy(intake),
        "native_development_task_intake_replay": deepcopy(returned),
        "native_development_task_intake_replay_reference": str(replay_path),
        "intake_status": intake["intake_status"],
        "requested_milestone_id": intake["requested_milestone_id"],
        "requested_domain": intake["requested_domain"],
        "requested_worker_family": intake["requested_worker_family"],
        "requested_output_scope": deepcopy(intake["requested_output_scope"]),
        "explicit_constraints": deepcopy(intake["explicit_constraints"]),
        "task_kind": intake["task_kind"],
        "safe_for_native_development": intake["safe_for_native_development"],
        "codex_assisted_handoff_required": intake["codex_assisted_handoff_required"],
        "suggested_next_safe_handoff": intake["suggested_next_safe_handoff"],
        "fail_closed": intake["intake_status"] == FAILED_CLOSED,
        "failure_reason": intake["failure_reason"],
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
    }
    capture["native_development_task_intake_capture_hash"] = replay_hash(capture)
    return capture


def _task_kind(prompt: str, milestone_id: str) -> str:
    lowered = prompt.lower()
    kinds = []
    if "review-only" in lowered or "review only" in lowered:
        kinds.append("REVIEW_ONLY")
    if "foundation" in lowered or "_FOUNDATION_" in milestone_id:
        kinds.append("FOUNDATION_ONLY")
    if "runtime" in lowered or "_RUNTIME_" in milestone_id:
        kinds.append("RUNTIME")
    if " cli" in lowered or "_CLI_" in milestone_id:
        kinds.append("CLI")
    if "worker" in lowered or "_WORKER_" in milestone_id:
        kinds.append("WORKER")
    if "domain" in lowered or "_DOMAIN_" in milestone_id:
        kinds.append("DOMAIN")
    if not kinds:
        return "AMBIGUOUS"
    return "+".join(dict.fromkeys(kinds))


def _detect_domain(prompt: str, milestone_id: str) -> str | None:
    text = f"{prompt} {milestone_id}".upper()
    for domain in SUPPORTED_DOMAINS:
        if domain in text:
            return domain
    return None


def _detect_worker_family(milestone_id: str) -> str | None:
    if "_WORKER" not in milestone_id:
        return None
    before_worker = milestone_id.split("_WORKER", 1)[0]
    for prefix in SUPPORTED_DOMAINS:
        prefix_token = f"{prefix}_"
        if before_worker.startswith(prefix_token):
            before_worker = before_worker[len(prefix_token) :]
    return before_worker or None


def _output_scope(task_kind: str, milestone_id: str) -> list[str]:
    scope = [milestone_id]
    if "WORKER" in task_kind:
        scope.append("WORKER_FOUNDATION")
    if "DOMAIN" in task_kind:
        scope.append("DOMAIN_ARTIFACTS")
    if "RUNTIME" in task_kind:
        scope.append("RUNTIME_MODULE")
    if "CLI" in task_kind:
        scope.append("CLI_SURFACE")
    if "REVIEW_ONLY" in task_kind:
        scope.append("REVIEW_ARTIFACTS")
    return scope


def _constraints(prompt: str) -> list[str]:
    lowered = prompt.lower()
    constraints = []
    for term in CONSTRAINT_TERMS:
        if term in lowered:
            constraints.append(term.upper().replace(" ", "_").replace("-", "_"))
    return sorted(set(constraints))


def _has_unacceptable_authority(prompt: str) -> bool:
    lowered = prompt.lower()
    for term in FORBIDDEN_AUTHORITY_TERMS:
        if term in lowered and not _is_negated(lowered, term):
            return True
    return False


def _is_negated(lowered_prompt: str, term: str) -> bool:
    negated_forms = (
        f"no {term}",
        f"do not {term}",
        f"must not {term}",
        f"without {term}",
    )
    return any(form in lowered_prompt for form in negated_forms)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("native development task intake replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RECORDED" if index == 0 else "AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_RETURNED",
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("native development task intake artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("native development task intake artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("native development task intake replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("native development task intake replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "native development task intake failed closed"
