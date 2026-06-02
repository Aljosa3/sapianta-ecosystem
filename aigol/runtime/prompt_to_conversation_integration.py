"""Prompt-to-conversation integration for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.provider.providers.openai_provider import OPENAI_PROVIDER_ID, OpenAIProviderAdapter, openai_provider_metadata
from aigol.runtime.intent_classifier import CONVERSATION
from aigol.runtime.minimal_human_prompt_interface import (
    DEFAULT_CREATED_AT,
    DEFAULT_PROMPT_ID,
    submit_human_prompt,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.conversation_chain_continuity_runtime import (
    attach_conversation_chain_continuity,
    reconstruct_conversation_chain_continuity_replay,
)
from aigol.runtime.provider_assisted_conversation_runtime import (
    CREATED,
    FAILED_CLOSED,
    reconstruct_provider_assisted_conversation_replay,
    run_provider_assisted_conversation,
)
from aigol.runtime.transport.serialization import replay_hash


PROMPT_TO_CONVERSATION_INTEGRATION_VERSION = "PROMPT_TO_CONVERSATION_INTEGRATION_V1"


def submit_prompt_to_conversation(
    *,
    human_prompt: str,
    prompt_id: str = DEFAULT_PROMPT_ID,
    created_at: str = DEFAULT_CREATED_AT,
    replay_dir: str | Path = ".aigol_prompt_runtime",
    operator_context: str = "operator_cli",
    provider_id: str = OPENAI_PROVIDER_ID,
    registry: ProviderRegistry | None = None,
    adapter: ProviderAdapter | None = None,
    session_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
    related_chain_id: str | None = None,
) -> dict[str, Any]:
    """Submit a prompt and activate conversation response when valid."""

    prompt_capture = submit_human_prompt(
        human_prompt=human_prompt,
        prompt_id=prompt_id,
        created_at=created_at,
        replay_dir=replay_dir,
        operator_context=operator_context,
    )
    prompt_replay_path = Path(prompt_capture["replay_reference"])
    try:
        if prompt_capture["prompt_status"] != "HUMAN_PROMPT_ACCEPTED":
            raise FailClosedRuntimeError(prompt_capture.get("failure_reason") or "prompt submit failed closed")
        if prompt_capture.get("routing_destination") not in {CONVERSATION, None}:
            raise FailClosedRuntimeError("prompt-to-conversation failed closed: prompt is not conversation intent")

        provider_registry, provider_adapter = _provider_dependencies(registry=registry, adapter=adapter)
        conversation = run_provider_assisted_conversation(
            conversation_id=f"{prompt_capture['prompt_id']}:CONVERSATION",
            prompt_id=prompt_capture["prompt_id"],
            human_prompt=human_prompt,
            created_at=created_at,
            provider_id=provider_id,
            registry=provider_registry,
            adapter=provider_adapter,
            replay_dir=prompt_replay_path / "conversation_response",
        )
        response = conversation["provider_assisted_conversation_response"]
        if response.get("conversation_status") != CREATED:
            raise FailClosedRuntimeError(response.get("failure_reason") or "conversation response missing")
        capture = _capture(prompt_capture, conversation)
        return _attach_chain_continuity(
            capture,
            prompt_id=prompt_capture["prompt_id"],
            created_at=created_at,
            replay_dir=prompt_replay_path / "chain_continuity",
            session_id=session_id,
            current_chain_id=current_chain_id,
            latest_chain_id=latest_chain_id,
            related_chain_id=related_chain_id,
        )
    except Exception as exc:
        failed = _failed_capture(prompt_capture, failure_reason=_failure_reason(exc))
        return _attach_chain_continuity(
            failed,
            prompt_id=prompt_capture.get("prompt_id", prompt_id),
            created_at=created_at,
            replay_dir=prompt_replay_path / "chain_continuity",
            session_id=session_id,
            current_chain_id=current_chain_id,
            latest_chain_id=latest_chain_id,
            related_chain_id=related_chain_id,
        )


def reconstruct_prompt_to_conversation_replay(replay_dir: str | Path, *, prompt_id: str) -> dict[str, Any]:
    """Reconstruct conversation response evidence from a prompt replay root."""

    prompt_replay_path = Path(replay_dir) / _require_string(prompt_id, "prompt_id")
    conversation = reconstruct_provider_assisted_conversation_replay(prompt_replay_path / "conversation_response")
    continuity = None
    continuity_path = prompt_replay_path / "chain_continuity"
    if continuity_path.exists():
        continuity = reconstruct_conversation_chain_continuity_replay(continuity_path)
    return {
        "prompt_id": prompt_id,
        "prompt_replay_reference": str(prompt_replay_path),
        "conversation_response": deepcopy(conversation),
        "canonical_chain_id": continuity.get("canonical_chain_id") if continuity else None,
        "current_chain_id": continuity.get("current_chain_id") if continuity else None,
        "latest_chain_id": continuity.get("latest_chain_id") if continuity else None,
        "related_chain_id": continuity.get("related_chain_id") if continuity else None,
        "suggested_inspection_commands": deepcopy(continuity.get("suggested_inspection_commands", []))
        if continuity
        else [],
        "response_status": conversation["conversation_status"],
        "response_text": conversation["response_text"],
        "response_source": _response_source(conversation["provider_assistance_required"]),
        "provider_used": conversation["provider_assistance_required"],
        "replay_visible": True,
        "authority": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_hash": replay_hash(conversation),
    }


def _capture(prompt_capture: dict[str, Any], conversation: dict[str, Any]) -> dict[str, Any]:
    response = conversation["provider_assisted_conversation_response"]
    provider_used = bool(conversation["provider_assistance_required"])
    capture = deepcopy(prompt_capture)
    capture.update(
        {
            "prompt_to_conversation_integration_version": PROMPT_TO_CONVERSATION_INTEGRATION_VERSION,
            "conversation_response": deepcopy(conversation),
            "response_status": response["conversation_status"],
            "response_source": _response_source(provider_used),
            "response_text": response["response_text"],
            "conversation_replay_reference": str(Path(prompt_capture["replay_reference"]) / "conversation_response"),
            "provider_used": provider_used,
            "provider_invoked": provider_used,
            "worker_invoked": False,
            "execution_requested": False,
            "fail_closed": False,
            "failure_reason": None,
        }
    )
    capture["prompt_to_conversation_capture_hash"] = replay_hash(capture)
    return capture


def _failed_capture(prompt_capture: dict[str, Any], *, failure_reason: str) -> dict[str, Any]:
    capture = deepcopy(prompt_capture)
    capture.update(
        {
            "prompt_to_conversation_integration_version": PROMPT_TO_CONVERSATION_INTEGRATION_VERSION,
            "conversation_response": None,
            "response_status": FAILED_CLOSED,
            "response_source": "UNAVAILABLE",
            "response_text": "",
            "conversation_replay_reference": str(Path(prompt_capture.get("replay_reference", ".")) / "conversation_response"),
            "provider_used": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "execution_requested": False,
            "fail_closed": True,
            "failure_reason": failure_reason,
        }
    )
    capture["prompt_to_conversation_capture_hash"] = replay_hash(capture)
    return capture


def _attach_chain_continuity(
    capture: dict[str, Any],
    *,
    prompt_id: str,
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None,
    current_chain_id: str | None,
    latest_chain_id: str | None,
    related_chain_id: str | None,
) -> dict[str, Any]:
    continuity = attach_conversation_chain_continuity(
        prompt_id=prompt_id,
        conversation_capture=capture,
        created_at=created_at,
        replay_dir=replay_dir,
        session_id=session_id,
        current_chain_id=current_chain_id,
        latest_chain_id=latest_chain_id,
        related_chain_id=related_chain_id,
    )
    updated = deepcopy(capture)
    updated.update(
        {
            "canonical_chain_id": continuity["canonical_chain_id"],
            "current_chain_id": continuity["current_chain_id"],
            "latest_chain_id": continuity["latest_chain_id"],
            "related_chain_id": continuity["related_chain_id"],
            "suggested_inspection_commands": deepcopy(continuity["suggested_inspection_commands"]),
            "conversation_chain_continuity_replay_reference": continuity[
                "conversation_chain_continuity_replay_reference"
            ],
            "conversation_chain_continuity_hash": continuity["conversation_chain_continuity_capture_hash"],
        }
    )
    updated["prompt_to_conversation_capture_hash"] = replay_hash(updated)
    return updated


def _provider_dependencies(
    *,
    registry: ProviderRegistry | None,
    adapter: ProviderAdapter | None,
) -> tuple[ProviderRegistry, ProviderAdapter]:
    if registry is not None and adapter is not None:
        return registry, adapter
    provider_registry = ProviderRegistry()
    provider_registry.register_provider(openai_provider_metadata(status=AVAILABLE))
    provider_adapter = OpenAIProviderAdapter()
    return provider_registry, provider_adapter


def _response_source(provider_used: bool) -> str:
    return "PROVIDER_ASSISTED" if provider_used else "SELF_RESOLUTION"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "prompt-to-conversation integration failed closed"
