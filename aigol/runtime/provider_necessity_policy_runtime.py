"""Deterministic provider necessity policy runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION = "AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_V1"
PROVIDER_NECESSITY_POLICY_ARTIFACT_V1 = "PROVIDER_NECESSITY_POLICY_ARTIFACT_V1"
PROVIDER_NECESSITY_CLASSIFIED = "PROVIDER_NECESSITY_CLASSIFIED"
FAILED_CLOSED = "FAILED_CLOSED"

PROVIDER_REQUIRED = "PROVIDER_REQUIRED"
PROVIDER_OPTIONAL = "PROVIDER_OPTIONAL"
PROVIDER_PROHIBITED = "PROVIDER_PROHIBITED"

REPLAY_STEPS = (
    "provider_necessity_policy_classified",
    "provider_necessity_policy_returned",
)

DEFAULT_POLICY_RULES = (
    {
        "rule_id": "OPERATOR_SHOW_CHAIN_PROHIBITED",
        "workflow_type": "OPERATOR_INSPECTION",
        "command": "SHOW_CHAIN",
        "classification": PROVIDER_PROHIBITED,
        "reason": "Chain inspection is replay reconstruction and must not require provider assistance.",
    },
    {
        "rule_id": "OPERATOR_DASHBOARD_PROHIBITED",
        "workflow_type": "OPERATOR_INSPECTION",
        "command": "DASHBOARD",
        "classification": PROVIDER_PROHIBITED,
        "reason": "Dashboard summaries are local operator state and must not invoke providers.",
    },
    {
        "rule_id": "REPLAY_INSPECTION_PROHIBITED",
        "workflow_type": "REPLAY_INSPECTION",
        "command": None,
        "classification": PROVIDER_PROHIBITED,
        "reason": "Replay inspection must remain deterministic and evidence-bound.",
    },
    {
        "rule_id": "WORKER_FOUNDATION_DESIGN_REQUIRED",
        "workflow_type": "NATIVE_DEVELOPMENT",
        "task_kind": "WORKER_FOUNDATION",
        "classification": PROVIDER_REQUIRED,
        "reason": "Worker foundation design requires proposal drafting after deterministic context assembly.",
    },
    {
        "rule_id": "DOMAIN_ARCHITECTURE_PROPOSAL_REQUIRED",
        "workflow_type": "NATIVE_DEVELOPMENT",
        "task_kind": "DOMAIN_ARCHITECTURE_PROPOSAL",
        "classification": PROVIDER_REQUIRED,
        "reason": "Domain architecture proposal drafting requires provider assistance after context assembly.",
    },
    {
        "rule_id": "GOVERNANCE_REVIEW_OPTIONAL",
        "workflow_type": "GOVERNANCE_REVIEW",
        "command": None,
        "classification": PROVIDER_OPTIONAL,
        "reason": "Governance review can be performed deterministically, with provider assistance optional for drafting.",
    },
)


def default_provider_necessity_policy() -> dict[str, Any]:
    """Return the canonical provider necessity policy with deterministic hash."""

    policy = {
        "policy_version": AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION,
        "rules": deepcopy(list(DEFAULT_POLICY_RULES)),
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    _validate_policy(policy)
    policy["policy_hash"] = replay_hash(_policy_hash_input(policy))
    return policy


def classify_provider_necessity(
    *,
    policy_decision_id: str,
    workflow_type: str,
    created_at: str,
    replay_dir: str | Path,
    command: str | None = None,
    task_kind: str | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify provider necessity without invoking providers."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_policy = deepcopy(policy) if policy is not None else default_provider_necessity_policy()
        _validate_policy(active_policy)
        policy_hash = active_policy.get("policy_hash") or replay_hash(_policy_hash_input(active_policy))
        rule = _resolve_rule(active_policy, workflow_type=workflow_type, command=command, task_kind=task_kind)
        artifact = _policy_artifact(
            policy_decision_id=policy_decision_id,
            policy=active_policy,
            policy_hash=policy_hash,
            workflow_type=workflow_type,
            command=command,
            task_kind=task_kind,
            classification=rule["classification"],
            reason=rule["reason"],
            matched_rule_id=rule["rule_id"],
            created_at=created_at,
            policy_status=PROVIDER_NECESSITY_CLASSIFIED,
            failure_reason=None,
        )
        returned = _returned_artifact(artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)
    except Exception as exc:
        artifact = _failed_policy_artifact(
            policy_decision_id=policy_decision_id,
            workflow_type=workflow_type,
            command=command,
            task_kind=task_kind,
            created_at=created_at,
            policy=policy,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(artifact)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], artifact)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(artifact, returned, replay_path)


def reconstruct_provider_necessity_policy_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct provider necessity policy replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("provider necessity policy replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("provider necessity policy replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    decision = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("policy_decision_reference") != decision["policy_decision_id"]:
        raise FailClosedRuntimeError("provider necessity policy replay reference mismatch")
    if returned.get("policy_decision_hash") != decision["artifact_hash"]:
        raise FailClosedRuntimeError("provider necessity policy replay hash mismatch")
    return {
        "policy_decision_id": decision["policy_decision_id"],
        "policy_status": decision["policy_status"],
        "necessity_classification": decision["necessity_classification"],
        "reason": decision["reason"],
        "matched_rule_id": decision["matched_rule_id"],
        "workflow_type": decision["workflow_type"],
        "command": decision["command"],
        "task_kind": decision["task_kind"],
        "policy_version": decision["policy_version"],
        "policy_hash": decision["policy_hash"],
        "failure_reason": decision["failure_reason"],
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _resolve_rule(
    policy: dict[str, Any],
    *,
    workflow_type: str,
    command: str | None,
    task_kind: str | None,
) -> dict[str, Any]:
    workflow = _normalize_key(workflow_type, "workflow_type")
    normalized_command = _optional_key(command)
    normalized_task_kind = _optional_key(task_kind)
    matches = []
    for rule in policy["rules"]:
        if _normalize_key(rule.get("workflow_type"), "rule_workflow_type") != workflow:
            continue
        rule_command = _optional_key(rule.get("command"))
        rule_task_kind = _optional_key(rule.get("task_kind"))
        command_matches = rule_command is None or rule_command == normalized_command
        task_matches = rule_task_kind is None or rule_task_kind == normalized_task_kind
        if command_matches and task_matches:
            matches.append(rule)
    if not matches:
        raise FailClosedRuntimeError("provider necessity policy failed closed: necessity cannot be determined")
    if len(matches) > 1:
        raise FailClosedRuntimeError("provider necessity policy failed closed: ambiguous necessity classification")
    return deepcopy(matches[0])


def _policy_artifact(
    *,
    policy_decision_id: str,
    policy: dict[str, Any],
    policy_hash: str,
    workflow_type: str,
    command: str | None,
    task_kind: str | None,
    classification: str | None,
    reason: str,
    matched_rule_id: str | None,
    created_at: str,
    policy_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
        "runtime_version": AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION,
        "policy_version": policy.get("policy_version", AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION),
        "policy_hash": _require_string(policy_hash, "policy_hash"),
        "policy_decision_id": _require_string(policy_decision_id, "policy_decision_id"),
        "workflow_type": _require_string(workflow_type, "workflow_type"),
        "command": command,
        "task_kind": task_kind,
        "necessity_classification": classification,
        "reason": _require_string(reason, "reason"),
        "matched_rule_id": matched_rule_id,
        "policy_status": policy_status,
        "provider_invoked": False,
        "provider_authority": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_policy_artifact(
    *,
    policy_decision_id: str,
    workflow_type: str,
    command: str | None,
    task_kind: str | None,
    created_at: str,
    policy: dict[str, Any] | None,
    failure_reason: str,
) -> dict[str, Any]:
    active_policy = deepcopy(policy) if isinstance(policy, dict) else default_provider_necessity_policy()
    policy_hash = active_policy.get("policy_hash") or replay_hash(_policy_hash_input(active_policy))
    return _policy_artifact(
        policy_decision_id=policy_decision_id,
        policy=active_policy,
        policy_hash=policy_hash,
        workflow_type=workflow_type,
        command=command,
        task_kind=task_kind,
        classification=None,
        reason="provider necessity policy failed closed",
        matched_rule_id=None,
        created_at=created_at,
        policy_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(decision: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(decision)
    returned = {
        "event_type": "PROVIDER_NECESSITY_POLICY_RETURNED",
        "policy_decision_reference": decision["policy_decision_id"],
        "policy_decision_hash": decision["artifact_hash"],
        "policy_status": decision["policy_status"],
        "necessity_classification": decision["necessity_classification"],
        "reason": decision["reason"],
        "policy_version": decision["policy_version"],
        "policy_hash": decision["policy_hash"],
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": decision["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(decision: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "provider_necessity_policy_artifact": deepcopy(decision),
        "provider_necessity_policy_replay": deepcopy(returned),
        "provider_necessity_policy_replay_reference": str(replay_path),
        "policy_status": decision["policy_status"],
        "necessity_classification": decision["necessity_classification"],
        "reason": decision["reason"],
        "matched_rule_id": decision["matched_rule_id"],
        "workflow_type": decision["workflow_type"],
        "command": decision["command"],
        "task_kind": decision["task_kind"],
        "policy_version": decision["policy_version"],
        "policy_hash": decision["policy_hash"],
        "fail_closed": decision["policy_status"] == FAILED_CLOSED,
        "failure_reason": decision["failure_reason"],
        "provider_invoked": False,
        "proposal_generated": False,
        "worker_created": False,
        "domain_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["provider_necessity_policy_capture_hash"] = replay_hash(capture)
    return capture


def _validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("policy_version") != AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION:
        raise FailClosedRuntimeError("provider necessity policy failed closed: invalid policy version")
    rules = _require_list(policy.get("rules"), "rules")
    rule_ids = []
    for rule in rules:
        if not isinstance(rule, dict):
            raise FailClosedRuntimeError("provider necessity policy failed closed: invalid rule")
        rule_ids.append(_normalize_key(rule.get("rule_id"), "rule_id"))
        classification = rule.get("classification")
        if classification not in {PROVIDER_REQUIRED, PROVIDER_OPTIONAL, PROVIDER_PROHIBITED}:
            raise FailClosedRuntimeError("provider necessity policy failed closed: invalid classification")
        _require_string(rule.get("workflow_type"), "rule_workflow_type")
        _require_string(rule.get("reason"), "rule_reason")
    if len(set(rule_ids)) != len(rule_ids):
        raise FailClosedRuntimeError("provider necessity policy failed closed: duplicate rule")


def _policy_hash_input(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_version": policy.get("policy_version"),
        "rules": policy.get("rules"),
    }


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("provider necessity policy replay step ordering mismatch")
    _verify_artifact_hash(artifact)
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


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("provider necessity policy artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider necessity policy artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("provider necessity policy replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("provider necessity policy replay hash mismatch")


def _optional_key(value: Any) -> str | None:
    if value is None:
        return None
    return _normalize_key(value, "optional_key")


def _normalize_key(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "provider necessity policy failed closed"

