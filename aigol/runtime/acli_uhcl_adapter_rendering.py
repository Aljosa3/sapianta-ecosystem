"""ACLI adapter rendering for UHCL communication artifacts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.cli.render.terminal_cards import render_card
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_human_communication_model_runtime import (
    COMMUNICATION_ARTIFACT_TYPE,
    COMMUNICATION_BINDING_ARTIFACT_TYPE,
    COMMUNICATION_LEVELS,
    PROGRESSIVE_EXPLANATION_ARTIFACT_TYPE,
    RECOVERY_GUIDANCE_ARTIFACT_TYPE,
    RESPONSE_CLARIFICATION,
    RESPONSE_CONFIRMATION,
    RESPONSE_CONTINUATION,
    RESPONSE_MODIFICATION,
    RESPONSE_REJECTION,
    SHARED_CONFIRMATION_ARTIFACT_TYPE,
    TYPED_SECTION_ARTIFACT_TYPE,
)


ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION = "G3_04_PHASE_4_ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_V1"
ACLI_UHCL_RENDER_ARTIFACT_V1 = "ACLI_UHCL_RENDER_ARTIFACT_V1"
ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1 = "ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1"
EVENT_UHCL_ARTIFACT_RENDERED = "acli_uhcl_artifact_rendered"
EVENT_UHCL_HUMAN_RESPONSE_CAPTURED = "acli_uhcl_human_response_captured"

UHCL_ARTIFACT_TYPES = {
    COMMUNICATION_ARTIFACT_TYPE,
    TYPED_SECTION_ARTIFACT_TYPE,
    PROGRESSIVE_EXPLANATION_ARTIFACT_TYPE,
    SHARED_CONFIRMATION_ARTIFACT_TYPE,
    COMMUNICATION_BINDING_ARTIFACT_TYPE,
    RECOVERY_GUIDANCE_ARTIFACT_TYPE,
}

CANONICAL_RESPONSE_CLASSES = {
    RESPONSE_CONFIRMATION,
    RESPONSE_CLARIFICATION,
    RESPONSE_MODIFICATION,
    RESPONSE_REJECTION,
    RESPONSE_CONTINUATION,
}


def render_uhcl_artifact_for_acli(
    *,
    render_id: str,
    uhcl_artifact: dict[str, Any],
    communication_level: str,
    rendered_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Render a UHCL artifact as deterministic terminal text."""

    replay_path = Path(replay_dir)
    source = _validated_uhcl_artifact(uhcl_artifact)
    level = _require_choice(communication_level, COMMUNICATION_LEVELS, "communication_level")
    event_index = _next_event_index(replay_path)
    lines = _render_lines(source, level)
    rendered_text = render_card("UHCL", lines)
    event = _event(
        event_index=event_index,
        event_type=EVENT_UHCL_ARTIFACT_RENDERED,
        occurred_at=rendered_at,
        event_payload={
            "render_id": _require_string(render_id, "render_id"),
            "source_artifact_type": source["artifact_type"],
            "source_artifact_hash": source["artifact_hash"],
            "communication_level": level,
        },
    )
    artifact = {
        "artifact_type": ACLI_UHCL_RENDER_ARTIFACT_V1,
        "runtime_version": ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION,
        "render_id": _require_string(render_id, "render_id"),
        "source_artifact_type": source["artifact_type"],
        "source_artifact_hash": source["artifact_hash"],
        "source_artifact_reference": source.get("replay_reference"),
        "communication_level": level,
        "terminal_format": "PLAIN_TEXT_CARD",
        "rendered_sections": _rendered_sections(source),
        "render_lines": lines,
        "render_text": rendered_text,
        "render_text_hash": replay_hash({"render_text": rendered_text}),
        "render_evidence": {
            "adapter": "ACLI",
            "adapter_scope": "PRESENTATION_ONLY",
            "source_artifact_hash": source["artifact_hash"],
            "communication_level": level,
            "terminal_format": "PLAIN_TEXT_CARD",
        },
        "rendered_at": _require_string(rendered_at, "rendered_at"),
        "semantic_translation_performed": False,
        "explanation_generated": False,
        "confirmation_logic_performed": False,
        "provider_orchestration_performed": False,
        "worker_orchestration_performed": False,
        "governance_performed": False,
        "replay_logic_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "interface_neutral_source_preserved": True,
        "replay_visible": True,
        "event": event,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, event_index, EVENT_UHCL_ARTIFACT_RENDERED, artifact)
    return _capture(artifact, replay_path)


def capture_uhcl_human_response(
    *,
    response_id: str,
    rendered_artifact: dict[str, Any],
    operator_input: str,
    captured_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Capture ACLI human input as a canonical UHCL confirmation response class."""

    render = _validated_render_artifact(rendered_artifact)
    replay_path = Path(replay_dir)
    event_index = _next_event_index(replay_path)
    response_class = _canonical_response_class(operator_input)
    input_hash = replay_hash({"operator_input": _require_string(operator_input, "operator_input")})
    event = _event(
        event_index=event_index,
        event_type=EVENT_UHCL_HUMAN_RESPONSE_CAPTURED,
        occurred_at=captured_at,
        event_payload={
            "response_id": _require_string(response_id, "response_id"),
            "render_id": render["render_id"],
            "canonical_response_class": response_class,
            "operator_input_hash": input_hash,
        },
    )
    artifact = {
        "artifact_type": ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1,
        "runtime_version": ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION,
        "response_id": _require_string(response_id, "response_id"),
        "render_id": render["render_id"],
        "render_artifact_hash": render["artifact_hash"],
        "source_artifact_type": render["source_artifact_type"],
        "source_artifact_hash": render["source_artifact_hash"],
        "operator_input_hash": input_hash,
        "canonical_response_class": response_class,
        "canonical_response_class_set": sorted(CANONICAL_RESPONSE_CLASSES),
        "captured_at": _require_string(captured_at, "captured_at"),
        "confirmation_evidence_only": True,
        "semantic_translation_performed": False,
        "explanation_generated": False,
        "confirmation_logic_performed": False,
        "provider_orchestration_performed": False,
        "worker_orchestration_performed": False,
        "governance_performed": False,
        "replay_logic_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
        "event": event,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, event_index, EVENT_UHCL_HUMAN_RESPONSE_CAPTURED, artifact)
    return _capture(artifact, replay_path)


def reconstruct_acli_uhcl_adapter_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct ACLI UHCL adapter render and response evidence."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI UHCL adapter replay failed closed: replay is empty")
    artifacts = [wrapper["artifact"] for wrapper in wrappers]
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI UHCL adapter replay ordering mismatch")
        event = _require_mapping(wrapper["artifact"].get("event"), "event")
        if event.get("event_index") != index:
            raise FailClosedRuntimeError("ACLI UHCL adapter event ordering mismatch")
        _verify_hash_field(event, "event_hash", "ACLI UHCL adapter event hash mismatch")
    render_artifacts = [
        artifact for artifact in artifacts if artifact["artifact_type"] == ACLI_UHCL_RENDER_ARTIFACT_V1
    ]
    response_artifacts = [
        artifact for artifact in artifacts if artifact["artifact_type"] == ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1
    ]
    return {
        "runtime_version": ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION,
        "artifact_count": len(artifacts),
        "render_count": len(render_artifacts),
        "response_count": len(response_artifacts),
        "source_artifact_hashes": sorted({artifact["source_artifact_hash"] for artifact in artifacts}),
        "canonical_response_classes": [
            artifact["canonical_response_class"] for artifact in response_artifacts
        ],
        "semantic_translation_performed": False,
        "explanation_generated": False,
        "confirmation_logic_performed": False,
        "provider_orchestration_performed": False,
        "worker_orchestration_performed": False,
        "governance_performed": False,
        "replay_logic_performed": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _render_lines(source: dict[str, Any], level: str) -> list[str]:
    lines = [
        f"Artifact: {source['artifact_type']}",
        f"Hash: {source['artifact_hash']}",
        f"Level: {level}",
    ]
    for key in _rendered_sections(source):
        value = source.get(key)
        if isinstance(value, str):
            lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            lines.append(f"{key}: {len(value)} item(s)")
        elif isinstance(value, dict):
            lines.append(f"{key}: {', '.join(sorted(value.keys()))}")
    lines.append("Authority: presentation only; no semantic, governance, provider, worker, execution, replay, deployment, or mutation action.")
    return lines


def _rendered_sections(source: dict[str, Any]) -> list[str]:
    candidates = [
        "sections_rendered",
        "section_type",
        "derived_explanations",
        "confirmation_section",
        "typed_section_artifact",
        "recovery_section",
        "required_human_action",
        "non_authority_notices",
    ]
    return [key for key in candidates if key in source]


def _canonical_response_class(operator_input: str) -> str:
    text = _require_string(operator_input, "operator_input").lower()
    words = set(text.replace(".", " ").replace(",", " ").split())
    if words & {"confirm", "approve", "approved", "yes", "y"}:
        return RESPONSE_CONFIRMATION
    if words & {"clarify", "question", "why", "explain"}:
        return RESPONSE_CLARIFICATION
    if words & {"modify", "change", "edit", "revise"}:
        return RESPONSE_MODIFICATION
    if words & {"reject", "rejected", "no", "cancel", "stop"}:
        return RESPONSE_REJECTION
    if words & {"continue", "proceed", "next"}:
        return RESPONSE_CONTINUATION
    raise FailClosedRuntimeError("operator_input does not map to a canonical UHCL confirmation class")


def _validated_uhcl_artifact(value: dict[str, Any]) -> dict[str, Any]:
    artifact = _require_mapping(value, "uhcl_artifact")
    if artifact.get("artifact_type") not in UHCL_ARTIFACT_TYPES:
        raise FailClosedRuntimeError("ACLI UHCL adapter unsupported artifact type")
    _verify_artifact_hash(artifact, "UHCL source artifact hash mismatch")
    return artifact


def _validated_render_artifact(value: dict[str, Any]) -> dict[str, Any]:
    artifact = _require_mapping(value, "rendered_artifact")
    if artifact.get("artifact_type") != ACLI_UHCL_RENDER_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI UHCL render artifact type mismatch")
    _verify_artifact_hash(artifact, "ACLI UHCL render artifact hash mismatch")
    return artifact


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "runtime_version": ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
        "artifact_hash": artifact["artifact_hash"],
        "replay_reference": str(replay_path),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }


def _event(*, event_index: int, event_type: str, occurred_at: str, event_payload: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "event_payload": deepcopy(event_payload),
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, replay_index: int, replay_step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": replay_index,
        "replay_step": replay_step,
        "event_type": ACLI_UHCL_ADAPTER_RENDERING_RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{replay_index:03d}_{replay_step}.json", wrapper)


def _load_verified_wrapper(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    actual = wrapper.get("replay_hash")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError("ACLI UHCL adapter replay hash mismatch")
    artifact = _require_mapping(wrapper.get("artifact"), "artifact")
    if artifact.get("artifact_type") == ACLI_UHCL_RENDER_ARTIFACT_V1:
        _validated_render_artifact(artifact)
    elif artifact.get("artifact_type") == ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1:
        _validate_response_artifact(artifact)
    else:
        raise FailClosedRuntimeError("ACLI UHCL adapter unknown artifact type")
    return wrapper


def _validate_response_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("artifact_type") != ACLI_UHCL_HUMAN_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI UHCL response artifact type mismatch")
    if artifact.get("canonical_response_class") not in CANONICAL_RESPONSE_CLASSES:
        raise FailClosedRuntimeError("ACLI UHCL response class mismatch")
    if artifact.get("confirmation_evidence_only") is not True:
        raise FailClosedRuntimeError("ACLI UHCL response must be evidence only")
    for key in (
        "semantic_translation_performed",
        "explanation_generated",
        "confirmation_logic_performed",
        "provider_orchestration_performed",
        "worker_orchestration_performed",
        "governance_performed",
        "replay_logic_performed",
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError(f"ACLI UHCL response cannot set {key}")
    _verify_artifact_hash(artifact, "ACLI UHCL response artifact hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], message: str) -> None:
    actual = artifact.get("artifact_hash")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _verify_hash_field(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    expected = deepcopy(value)
    expected.pop(field_name, None)
    if not isinstance(actual, str) or replay_hash(expected) != actual:
        raise FailClosedRuntimeError(message)


def _next_event_index(replay_path: Path) -> int:
    if not replay_path.exists():
        return 0
    return len(sorted(replay_path.glob("*.json")))


def _require_choice(value: Any, choices: set[str], field_name: str) -> str:
    candidate = _require_string(value, field_name).upper()
    if candidate not in choices:
        raise FailClosedRuntimeError(f"{field_name} is not supported")
    return candidate


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field_name} must be a JSON object")
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
