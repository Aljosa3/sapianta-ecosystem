"""Domain resolution bridge for native development prompts."""

from __future__ import annotations

from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_VERSION = (
    "AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_V1"
)
NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_ARTIFACT_V1 = (
    "NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_ARTIFACT_V1"
)
DOMAIN_RESOLVED = "DOMAIN_RESOLVED"
FAILED_CLOSED = "FAILED_CLOSED"

GOVERNED_DEVELOPMENT_DOMAIN = "AIGOL"
PROVIDER_ADAPTER_MARKERS = (
    "_EXTERNAL_WORKER_PROVIDER_ADAPTER_",
    "_PROVIDER_ADAPTER_",
    "OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER",
    "CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER",
    "MISTRAL_EXTERNAL_WORKER_PROVIDER_ADAPTER",
)
SUPPORTED_DEVELOPMENT_DOMAINS = ("TRADING", "AIGOL")


def resolve_native_development_domain(
    *,
    human_prompt: str,
    requested_milestone_id: str,
    detected_domain: str | None,
) -> dict[str, Any]:
    """Resolve a native development prompt to a governed development domain."""

    try:
        prompt = _require_string(human_prompt, "human_prompt")
        milestone = _require_string(requested_milestone_id, "requested_milestone_id")
        normalized_detected = _normalize_domain(detected_domain)
        resolved_domain = normalized_detected
        resolution_reason = "detected supported native development domain"
        bridge_applied = False

        if _is_provider_adapter_milestone(milestone):
            resolved_domain = GOVERNED_DEVELOPMENT_DOMAIN
            resolution_reason = "provider adapter milestone mapped to governed development domain"
            bridge_applied = True
        elif resolved_domain is None and _mentions_provider_adapter(prompt):
            resolved_domain = GOVERNED_DEVELOPMENT_DOMAIN
            resolution_reason = "provider adapter prompt mapped to governed development domain"
            bridge_applied = True

        if resolved_domain is None:
            status = FAILED_CLOSED
            failure_reason = "native development domain resolution failed closed: requested_domain cannot be resolved"
        elif resolved_domain not in SUPPORTED_DEVELOPMENT_DOMAINS:
            status = FAILED_CLOSED
            failure_reason = "native development domain resolution failed closed: unsupported development domain"
        else:
            status = DOMAIN_RESOLVED
            failure_reason = None

        return _artifact(
            human_prompt=prompt,
            requested_milestone_id=milestone,
            detected_domain=normalized_detected,
            resolved_domain=resolved_domain,
            bridge_applied=bridge_applied,
            resolution_reason=resolution_reason if status == DOMAIN_RESOLVED else failure_reason,
            resolution_status=status,
            failure_reason=failure_reason,
        )
    except Exception as exc:
        milestone = requested_milestone_id if isinstance(requested_milestone_id, str) else None
        return _artifact(
            human_prompt=human_prompt if isinstance(human_prompt, str) else "",
            requested_milestone_id=milestone,
            detected_domain=_normalize_domain(detected_domain),
            resolved_domain=None,
            bridge_applied=False,
            resolution_reason=_failure_reason(exc),
            resolution_status=FAILED_CLOSED,
            failure_reason=_failure_reason(exc),
        )


def _artifact(
    *,
    human_prompt: str,
    requested_milestone_id: str | None,
    detected_domain: str | None,
    resolved_domain: str | None,
    bridge_applied: bool,
    resolution_reason: str | None,
    resolution_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_ARTIFACT_V1,
        "runtime_version": AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_VERSION,
        "requested_milestone_id": requested_milestone_id,
        "human_prompt_hash": replay_hash({"human_prompt": human_prompt}),
        "detected_domain": detected_domain,
        "resolved_domain": resolved_domain,
        "supported_development_domains": list(SUPPORTED_DEVELOPMENT_DOMAINS),
        "bridge_applied": bridge_applied,
        "resolution_reason": resolution_reason,
        "resolution_status": resolution_status,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _is_provider_adapter_milestone(milestone: str) -> bool:
    upper = milestone.upper()
    return any(marker in upper for marker in PROVIDER_ADAPTER_MARKERS)


def _mentions_provider_adapter(prompt: str) -> bool:
    upper = prompt.upper()
    return "PROVIDER" in upper and "ADAPTER" in upper


def _normalize_domain(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().upper()
    return normalized or None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    return str(exc) or "native development domain resolution failed closed"


__all__ = [
    "AIGOL_NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_VERSION",
    "DOMAIN_RESOLVED",
    "FAILED_CLOSED",
    "GOVERNED_DEVELOPMENT_DOMAIN",
    "NATIVE_DEVELOPMENT_DOMAIN_RESOLUTION_BRIDGE_ARTIFACT_V1",
    "SUPPORTED_DEVELOPMENT_DOMAINS",
    "resolve_native_development_domain",
]
