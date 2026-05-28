"""Minimal executable bounded real LLM session for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


BOUNDED_LLM_SESSION = "BOUNDED_LLM_SESSION"
BOUNDED_SEMANTIC_CONTRIBUTION = "BOUNDED_SEMANTIC_CONTRIBUTION"
COMPLETED = "COMPLETED"
FAILED = "FAILED"
ALLOWED_REQUESTED_CAPABILITIES = ("metadata_inspection_provider",)
REPLAY_STEPS = ("ingress", "raw_contribution", "normalized_contribution", "validation", "egress")
CONTRIBUTION_FIELDS = frozenset(
    {
        "contribution_id",
        "contribution_text",
        "contribution_type",
        "requested_capabilities",
        "proposed_contract_reference",
        "created_at",
        "response_hash",
    }
)
AUTHORITY_ESCALATION_TERMS = (
    "execute tool",
    "execute runtime",
    "mutate governance",
    "orchestrate",
    "autonomous loop",
    "continue autonomously",
    "auto-retry",
    "agent runtime",
    "planning runtime",
    "governance authority",
)


def create_llm_session_ingress(
    *,
    session_id: str,
    request_id: str,
    human_input: str,
    created_at: str,
    lineage_parent: str | None = None,
) -> dict[str, Any]:
    """Create deterministic bounded ingress envelope."""

    artifact = {
        "session_id": _require_string(session_id, "session_id"),
        "request_id": _require_string(request_id, "request_id"),
        "human_input": _normalize_text(human_input, "human_input"),
        "governance_mode": BOUNDED_LLM_SESSION,
        "timestamp": _require_string(created_at, "created_at"),
        "lineage_parent": lineage_parent,
    }
    if lineage_parent is not None:
        _require_string(lineage_parent, "lineage_parent")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def external_llm_contribution_hash(contribution: dict[str, Any]) -> str:
    """Compute deterministic hash for an external LLM contribution."""

    if not isinstance(contribution, dict):
        raise FailClosedRuntimeError("external LLM contribution must be a JSON object")
    expected_fields = CONTRIBUTION_FIELDS.difference({"response_hash"})
    if set(contribution) != expected_fields:
        raise FailClosedRuntimeError("external LLM contribution hash input has malformed structure")
    return replay_hash(contribution)


def normalize_llm_contribution(raw_contribution: dict[str, Any]) -> dict[str, Any]:
    """Normalize one untrusted external LLM contribution into bounded evidence."""

    if not isinstance(raw_contribution, dict):
        raise FailClosedRuntimeError("external LLM contribution must be a JSON object")
    if set(raw_contribution) != CONTRIBUTION_FIELDS:
        raise FailClosedRuntimeError("external LLM contribution has malformed structure")
    expected_hash = external_llm_contribution_hash(
        {
            "contribution_id": raw_contribution["contribution_id"],
            "contribution_text": raw_contribution["contribution_text"],
            "contribution_type": raw_contribution["contribution_type"],
            "requested_capabilities": raw_contribution["requested_capabilities"],
            "proposed_contract_reference": raw_contribution["proposed_contract_reference"],
            "created_at": raw_contribution["created_at"],
        }
    )
    if raw_contribution["response_hash"] != expected_hash:
        raise FailClosedRuntimeError("external LLM contribution hash mismatch")
    contribution_type = _require_string(raw_contribution["contribution_type"], "contribution_type")
    if contribution_type != BOUNDED_SEMANTIC_CONTRIBUTION:
        raise FailClosedRuntimeError("external LLM contribution type is not bounded")
    requested_capabilities = raw_contribution["requested_capabilities"]
    if requested_capabilities != list(ALLOWED_REQUESTED_CAPABILITIES):
        raise FailClosedRuntimeError("external LLM contribution requested capability is not allowed")
    proposed_contract_reference = _require_string(
        raw_contribution["proposed_contract_reference"],
        "proposed_contract_reference",
    )
    if not proposed_contract_reference.startswith("contract:"):
        raise FailClosedRuntimeError("external LLM contribution contract reference is invalid")
    contribution_text = _normalize_text(raw_contribution["contribution_text"], "contribution_text")
    _reject_authority_escalation(contribution_text)
    normalized = {
        "contribution_id": _require_string(raw_contribution["contribution_id"], "contribution_id"),
        "contribution_text": contribution_text,
        "contribution_type": contribution_type,
        "requested_capabilities": list(ALLOWED_REQUESTED_CAPABILITIES),
        "proposed_contract_reference": proposed_contract_reference,
        "created_at": _require_string(raw_contribution["created_at"], "created_at"),
        "source_response_hash": raw_contribution["response_hash"],
        "untrusted_contribution": True,
        "execution_authority": False,
        "governance_authority": False,
        "hidden_continuation": False,
    }
    normalized["artifact_hash"] = replay_hash(normalized)
    return normalized


def execute_minimal_real_llm_session(
    *,
    session_id: str,
    request_id: str,
    human_input: str,
    contribution_callable: Callable[[dict[str, Any]], dict[str, Any]],
    created_at: str,
    replay_dir: str | Path,
    lineage_parent: str | None = None,
) -> dict[str, Any]:
    """Execute one bounded LLM contribution session and persist replay evidence."""

    replay_path = Path(replay_dir)
    raw_contribution: dict[str, Any] | None = None
    normalized_contribution: dict[str, Any] | None = None
    ingress = create_llm_session_ingress(
        session_id=session_id,
        request_id=request_id,
        human_input=human_input,
        created_at=created_at,
        lineage_parent=lineage_parent,
    )
    _persist_step(replay_path, 0, "ingress", ingress)
    try:
        if not callable(contribution_callable):
            raise FailClosedRuntimeError("contribution_callable must be callable")
        raw_contribution = contribution_callable(deepcopy(ingress))
        _persist_step(replay_path, 1, "raw_contribution", _raw_contribution_artifact(raw_contribution))
        normalized_contribution = normalize_llm_contribution(raw_contribution)
        _persist_step(replay_path, 2, "normalized_contribution", normalized_contribution)
        validation = validate_llm_session_continuity(
            ingress=ingress,
            raw_contribution=raw_contribution,
            normalized_contribution=normalized_contribution,
        )
        _persist_step(replay_path, 3, "validation", validation)
        egress = create_governed_llm_session_egress(
            ingress=ingress,
            validation=validation,
            status=COMPLETED,
            failure_reason="",
        )
        _persist_step(replay_path, 4, "egress", egress)
        return _session_capture(
            ingress=ingress,
            raw_contribution=raw_contribution,
            normalized_contribution=normalized_contribution,
            validation=validation,
            egress=egress,
        )
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        validation = _failure_validation(ingress=ingress, failure_reason=failure_reason)
        if not (replay_path / "001_raw_contribution.json").exists():
            _persist_step(replay_path, 1, "raw_contribution", _failed_placeholder("raw_contribution", failure_reason))
        if normalized_contribution is None:
            _persist_step(replay_path, 2, "normalized_contribution", _failed_placeholder("normalized_contribution", failure_reason))
        _persist_step(replay_path, 3, "validation", validation)
        egress = create_governed_llm_session_egress(
            ingress=ingress,
            validation=validation,
            status=FAILED,
            failure_reason=failure_reason,
        )
        _persist_step(replay_path, 4, "egress", egress)
        return _session_capture(
            ingress=ingress,
            raw_contribution=raw_contribution,
            normalized_contribution=normalized_contribution,
            validation=validation,
            egress=egress,
        )


def validate_llm_session_continuity(
    *,
    ingress: dict[str, Any],
    raw_contribution: dict[str, Any],
    normalized_contribution: dict[str, Any],
) -> dict[str, Any]:
    """Verify single-chain continuity across ingress, contribution, and egress."""

    _verify_artifact_hash(ingress)
    if not isinstance(raw_contribution, dict):
        raise FailClosedRuntimeError("raw contribution is missing")
    if not isinstance(normalized_contribution, dict):
        raise FailClosedRuntimeError("normalized contribution is missing")
    if normalized_contribution.get("source_response_hash") != raw_contribution.get("response_hash"):
        raise FailClosedRuntimeError("contribution lineage mismatch")
    if normalized_contribution.get("execution_authority") is not False:
        raise FailClosedRuntimeError("execution authority escalation detected")
    if normalized_contribution.get("governance_authority") is not False:
        raise FailClosedRuntimeError("governance authority escalation detected")
    if normalized_contribution.get("hidden_continuation") is not False:
        raise FailClosedRuntimeError("hidden continuation signal detected")
    _verify_artifact_hash(normalized_contribution)
    validation = {
        "session_id": ingress["session_id"],
        "request_id": ingress["request_id"],
        "ingress_hash": ingress["artifact_hash"],
        "raw_contribution_hash": raw_contribution["response_hash"],
        "normalized_contribution_hash": normalized_contribution["artifact_hash"],
        "lineage_continuity_preserved": True,
        "hidden_state_transition_detected": False,
        "authority_escalation_detected": False,
        "implicit_execution_semantics_detected": False,
        "continuity_validated": True,
        "replay_chain_complete": True,
        "bounded_interaction": True,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def create_governed_llm_session_egress(
    *,
    ingress: dict[str, Any],
    validation: dict[str, Any],
    status: str,
    failure_reason: str,
) -> dict[str, Any]:
    """Create final bounded governed egress artifact."""

    if status not in {COMPLETED, FAILED}:
        raise FailClosedRuntimeError("egress status must be COMPLETED or FAILED")
    _verify_artifact_hash(ingress)
    _verify_artifact_hash(validation)
    continuity_validated = status == COMPLETED and validation.get("continuity_validated") is True
    egress = {
        "session_id": ingress["session_id"],
        "request_id": ingress["request_id"],
        "status": status,
        "continuity_validated": continuity_validated,
        "authority_escalation_detected": bool(validation.get("authority_escalation_detected", True)),
        "replay_chain_complete": True,
        "bounded_interaction": True,
        "governance_authority_delegated": False,
        "execution_authority_activated": False,
        "failure_reason": failure_reason,
        "ingress_hash": ingress["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
    }
    egress["artifact_hash"] = replay_hash(egress)
    return egress


def reconstruct_minimal_real_llm_session_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate persisted single-session replay chain."""

    replay_path = Path(replay_dir)
    artifacts: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if not path.exists():
            raise FailClosedRuntimeError("minimal real LLM session replay artifact missing")
        import json

        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise FailClosedRuntimeError("minimal real LLM session replay artifact must be a JSON object")
        if loaded.get("replay_step") != step or loaded.get("replay_index") != index:
            raise FailClosedRuntimeError("minimal real LLM session replay ordering mismatch")
        _verify_artifact_hash(loaded["artifact"])
        artifacts.append(loaded)
    egress = artifacts[-1]["artifact"]
    return {
        "replay_artifact_count": len(artifacts),
        "replay_steps": [artifact["replay_step"] for artifact in artifacts],
        "session_id": egress["session_id"],
        "status": egress["status"],
        "append_only_valid": True,
        "replay_visible": True,
        "lineage_valid": egress["replay_chain_complete"],
        "governance_authority_delegated": False,
        "replay_hash": replay_hash(artifacts),
    }


def _raw_contribution_artifact(raw_contribution: Any) -> dict[str, Any]:
    if not isinstance(raw_contribution, dict):
        raise FailClosedRuntimeError("external LLM contribution must be a JSON object")
    canonical_serialize(raw_contribution)
    artifact = deepcopy(raw_contribution)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if step not in REPLAY_STEPS or REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("minimal real LLM session replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapped = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapped["replay_hash"] = replay_hash(wrapped)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapped)


def _session_capture(
    *,
    ingress: dict[str, Any],
    raw_contribution: dict[str, Any] | None,
    normalized_contribution: dict[str, Any] | None,
    validation: dict[str, Any],
    egress: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "ingress": deepcopy(ingress),
        "raw_contribution": deepcopy(raw_contribution),
        "normalized_contribution": deepcopy(normalized_contribution),
        "validation": deepcopy(validation),
        "egress": deepcopy(egress),
    }
    capture["session_hash"] = replay_hash(capture)
    return capture


def _failed_placeholder(step: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "step": step,
        "status": FAILED,
        "failure_reason": failure_reason,
        "continuity_validated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_validation(*, ingress: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    validation = {
        "session_id": ingress["session_id"],
        "request_id": ingress["request_id"],
        "ingress_hash": ingress["artifact_hash"],
        "lineage_continuity_preserved": False,
        "hidden_state_transition_detected": False,
        "authority_escalation_detected": _is_authority_failure(failure_reason),
        "implicit_execution_semantics_detected": _is_authority_failure(failure_reason),
        "continuity_validated": False,
        "replay_chain_complete": True,
        "bounded_interaction": True,
        "failure_reason": failure_reason,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def _is_authority_failure(failure_reason: str) -> bool:
    lowered = failure_reason.lower()
    return "authority" in lowered or "continuation" in lowered or "execution" in lowered


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("session replay artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("session replay artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError("session replay artifact hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "minimal real LLM session failed closed"


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _reject_authority_escalation(text: str) -> None:
    lowered = text.lower()
    for term in AUTHORITY_ESCALATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("external LLM contribution authority escalation detected")
