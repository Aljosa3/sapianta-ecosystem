"""Governance-artifact answer resolution for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import GOVERNANCE, select_resolution_strategy
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


GOVERNANCE_RESOLUTION_STRATEGY_VERSION = "GOVERNANCE_RESOLUTION_STRATEGY_V1"
GOVERNANCE_RESOLUTION_ARTIFACT_V1 = "GOVERNANCE_RESOLUTION_ARTIFACT_V1"
GOVERNANCE_RESOLUTION_CREATED = "GOVERNANCE_RESOLUTION_CREATED"
GOVERNANCE_RESOLUTION_RETURNED = "GOVERNANCE_RESOLUTION_RETURNED"
RESOLVED = "RESOLVED"

REPLAY_STEPS = ("governance_resolution_created", "governance_resolution_returned")

GOVERNANCE_PROMPT_MARKERS = (
    "what governance exists",
    "what was certified",
    "which milestone was completed",
    "governance guarantees",
    "what adrs define this capability",
    "status of a governance milestone",
)

GOVERNANCE_ARTIFACT_CATALOG: dict[str, dict[str, Any]] = {
    "GOVERNANCE_ARTIFACT_INVENTORY_CERTIFICATION": {
        "path": "governance/GOVERNANCE_ARTIFACT_INVENTORY_CERTIFICATION.json",
        "classification": "CERTIFICATION",
        "question_scope": "GOVERNANCE_EXISTS",
    },
    "CONVERSATIONAL_RUNTIME_CERTIFICATION": {
        "path": "governance/CONVERSATIONAL_RUNTIME_CERTIFICATION.json",
        "classification": "CERTIFICATION",
        "question_scope": "CERTIFIED_STATUS",
    },
    "FIFTH_REAL_CONVERSATIONAL_USAGE_CERTIFICATION": {
        "path": "governance/FIFTH_REAL_CONVERSATIONAL_USAGE_CERTIFICATION.json",
        "classification": "CERTIFICATION",
        "question_scope": "COMPLETED_MILESTONE",
    },
    "OPERATIONAL_EPOCH_GUARANTEES": {
        "path": "governance/OPERATIONAL_EPOCH_GUARANTEES_V1.md",
        "classification": "GUARANTEE",
        "question_scope": "GOVERNANCE_GUARANTEES",
    },
    "RESOLUTION_STRATEGY_ADR": {
        "path": "governance/RESOLUTION_STRATEGY_ADR_V1.md",
        "classification": "ADR",
        "question_scope": "CAPABILITY_ADRS",
    },
    "MILESTONE_CONTINUITY_MODEL": {
        "path": "governance/MILESTONE_CONTINUITY_MODEL_V1.md",
        "classification": "GOVERNANCE_MODEL",
        "question_scope": "MILESTONE_STATUS",
    },
}


def is_governance_oriented_prompt(human_prompt: str) -> bool:
    """Return whether the prompt asks for governance artifact evidence."""

    prompt = _normalize_text(human_prompt, "human_prompt").lower().rstrip("?.! ")
    return any(marker in prompt for marker in GOVERNANCE_PROMPT_MARKERS)


def resolve_governance_question(
    *,
    resolution_id: str,
    strategy_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
    replay_dir: str | Path,
    repository_root: str | Path | None = None,
    artifact_catalog: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve a governance question from governance artifacts only."""

    replay_path = Path(replay_dir)
    _ensure_resolution_replay_available(replay_path)
    if not is_governance_oriented_prompt(human_prompt):
        raise FailClosedRuntimeError("governance resolution failed closed: prompt is not governance-oriented")

    strategy_capture = select_resolution_strategy(
        strategy_id=strategy_id,
        selected_strategy=GOVERNANCE,
        selection_reason="Prompt asks for governance artifact evidence.",
        human_prompt_reference=human_prompt_reference,
        created_at=created_at,
        replay_dir=replay_path / "strategy_selection",
    )
    evidence = _collect_governance_evidence(
        artifact_query=_artifact_query(human_prompt),
        repository_root=Path(repository_root) if repository_root is not None else Path.cwd(),
        artifact_catalog=GOVERNANCE_ARTIFACT_CATALOG if artifact_catalog is None else artifact_catalog,
    )
    strategy_artifact = strategy_capture["resolution_strategy_artifact"]
    resolution = _resolution_artifact(
        resolution_id=resolution_id,
        strategy_artifact=strategy_artifact,
        evidence=evidence,
        human_prompt_reference=human_prompt_reference,
        human_prompt=human_prompt,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], resolution)
    returned = _resolution_returned(resolution)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(strategy_artifact, resolution, returned)


def reconstruct_governance_resolution(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct governance resolution replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("governance resolution ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governance resolution artifact must be a JSON object")
        _verify_artifact_hash(artifact, "governance resolution artifact")
        wrappers.append(wrapper)

    resolution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("resolution_reference") != resolution["resolution_id"]:
        raise FailClosedRuntimeError("governance resolution reference mismatch")
    if returned.get("resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("governance resolution hash mismatch")
    _validate_resolution(resolution)
    return {
        "resolution_id": resolution["resolution_id"],
        "selected_strategy": resolution["selected_strategy"],
        "human_prompt_reference": resolution["human_prompt_reference"],
        "answer_text": resolution["answer_text"],
        "evidence_count": resolution["evidence_count"],
        "source_references": deepcopy(resolution["source_references"]),
        "resolution_status": resolution["resolution_status"],
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _artifact_query(human_prompt: str) -> str:
    prompt = _normalize_text(human_prompt, "human_prompt").lower()
    if "what was certified" in prompt or "was certified" in prompt:
        return "CONVERSATIONAL_RUNTIME_CERTIFICATION"
    if "which milestone was completed" in prompt or "milestone was completed" in prompt:
        return "FIFTH_REAL_CONVERSATIONAL_USAGE_CERTIFICATION"
    if "governance guarantees" in prompt:
        return "OPERATIONAL_EPOCH_GUARANTEES"
    if "adrs define this capability" in prompt:
        return "RESOLUTION_STRATEGY_ADR"
    if "status of a governance milestone" in prompt:
        return "MILESTONE_CONTINUITY_MODEL"
    return "GOVERNANCE_ARTIFACT_INVENTORY_CERTIFICATION"


def _collect_governance_evidence(
    *,
    artifact_query: str,
    repository_root: Path,
    artifact_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(artifact_catalog, dict) or not artifact_catalog:
        raise FailClosedRuntimeError("governance resolution failed closed: missing governance evidence")
    artifact_id = _normalize_token(artifact_query, "artifact_query")
    entry = artifact_catalog.get(artifact_id)
    if not isinstance(entry, dict):
        raise FailClosedRuntimeError("governance resolution failed closed: missing governance evidence")
    path = repository_root / _require_string(entry.get("path"), "artifact_path")
    _validate_governance_source(path)
    source_hash = _source_hash(path)
    source = {
        "artifact_identity": artifact_id,
        "artifact_classification": _normalize_token(entry.get("classification"), "artifact_classification"),
        "artifact_path": str(entry["path"]),
        "question_scope": _normalize_token(entry.get("question_scope"), "question_scope"),
        "source_hash": source_hash,
        "source_reference": f"{entry['path']}#{source_hash}",
        "authority_status": "REFERENCE_ONLY",
    }
    return {
        "source_references": [source],
        "primary_source": source,
    }


def _validate_governance_source(path: Path) -> None:
    if not path.exists():
        raise FailClosedRuntimeError("governance resolution failed closed: missing governance evidence")
    if not path.is_file():
        raise FailClosedRuntimeError("governance resolution failed closed: invalid governance reference")
    if path.suffix == ".json":
        try:
            load_json(path)
        except (json.JSONDecodeError, OSError, FailClosedRuntimeError) as exc:
            raise FailClosedRuntimeError("governance resolution failed closed: corrupt governance artifacts") from exc


def _source_hash(path: Path) -> str:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid governance reference") from exc
    return replay_hash({"path": str(path), "content": content.decode("utf-8")})


def _resolution_artifact(
    *,
    resolution_id: str,
    strategy_artifact: dict[str, Any],
    evidence: dict[str, Any],
    human_prompt_reference: str,
    human_prompt: str,
    created_at: str,
) -> dict[str, Any]:
    sources = evidence.get("source_references")
    if not isinstance(sources, list) or not sources:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid references")
    primary = evidence["primary_source"]
    artifact = {
        "artifact_type": GOVERNANCE_RESOLUTION_ARTIFACT_V1,
        "governance_resolution_version": GOVERNANCE_RESOLUTION_STRATEGY_VERSION,
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "strategy_id": strategy_artifact["strategy_id"],
        "strategy_hash": strategy_artifact["artifact_hash"],
        "selected_strategy": GOVERNANCE,
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt": _normalize_text(human_prompt, "human_prompt"),
        "evidence_count": len(sources),
        "source_references": deepcopy(sources),
        "answer_text": _answer_text(primary, len(sources)),
        "resolution_status": RESOLVED,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "reference_only": True,
        "authority": False,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_resolution(artifact)
    return artifact


def _resolution_returned(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution, "governance resolution artifact")
    returned = {
        "event_type": GOVERNANCE_RESOLUTION_RETURNED,
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "selected_strategy": GOVERNANCE,
        "resolution_status": resolution["resolution_status"],
        "evidence_count": resolution["evidence_count"],
        "replay_visible": True,
        "reference_only": True,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _answer_text(primary: dict[str, Any], evidence_count: int) -> str:
    return (
        f"Governance evidence contains {evidence_count} artifact reference(s). "
        f"Primary governance artifact: {primary['artifact_identity']} at {primary['artifact_path']}. "
        "The result is reference-only and carries no provider, worker, approval, or execution authority."
    )


def _capture(strategy: dict[str, Any], resolution: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "resolution_strategy_artifact": deepcopy(strategy),
        "governance_resolution_artifact": deepcopy(resolution),
        "governance_resolution_replay": deepcopy(returned),
    }
    capture["governance_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_resolution_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("governance resolution step ordering mismatch")
    _verify_artifact_hash(artifact, "governance resolution artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": GOVERNANCE_RESOLUTION_CREATED if index == 0 else GOVERNANCE_RESOLUTION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_resolution(resolution: dict[str, Any]) -> None:
    if resolution.get("artifact_type") != GOVERNANCE_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid artifact")
    if resolution.get("selected_strategy") != GOVERNANCE:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid strategy")
    if resolution.get("resolution_status") != RESOLVED:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid status")
    if int(resolution.get("evidence_count", 0)) < 1:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid references")
    sources = resolution.get("source_references")
    if not isinstance(sources, list) or not sources:
        raise FailClosedRuntimeError("governance resolution failed closed: invalid references")
    for source in sources:
        if not isinstance(source, dict):
            raise FailClosedRuntimeError("governance resolution failed closed: invalid references")
        _require_string(source.get("artifact_identity"), "artifact_identity")
        _require_string(source.get("artifact_path"), "artifact_path")
        _require_string(source.get("source_reference"), "source_reference")
        _require_string(source.get("source_hash"), "source_hash")
        if source.get("authority_status") != "REFERENCE_ONLY":
            raise FailClosedRuntimeError("governance resolution failed closed: authority introduced")
    if resolution.get("replay_visible") is not True:
        raise FailClosedRuntimeError("governance resolution failed closed: replay visibility missing")
    if resolution.get("reference_only") is not True:
        raise FailClosedRuntimeError("governance resolution failed closed: reference boundary missing")
    if resolution.get("authority") is not False:
        raise FailClosedRuntimeError("governance resolution failed closed: authority introduced")
    if resolution.get("provider_used") is not False:
        raise FailClosedRuntimeError("governance resolution failed closed: provider use introduced")
    if resolution.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("governance resolution failed closed: worker invocation detected")
    if resolution.get("execution_requested") is not False:
        raise FailClosedRuntimeError("governance resolution failed closed: execution requested")
    if resolution.get("approval_created") is not False:
        raise FailClosedRuntimeError("governance resolution failed closed: approval introduced")
    _require_string(resolution.get("resolution_id"), "resolution_id")
    _require_string(resolution.get("strategy_id"), "strategy_id")
    _require_string(resolution.get("strategy_hash"), "strategy_hash")
    _require_string(resolution.get("human_prompt_reference"), "human_prompt_reference")
    _require_string(resolution.get("answer_text"), "answer_text")
    _require_string(resolution.get("created_at"), "created_at")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("governance resolution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governance resolution replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
