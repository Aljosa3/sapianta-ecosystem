"""Canonical Certified Provider Attachment for AiGOL.

This module is the stable Platform Core provider attachment boundary. Runtime
components call this API instead of invoking provider transport directly.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_registry import ProviderRegistry
from aigol.provider.provider_runtime import (
    PROVIDER_ATTACHMENT_RUNTIME_VERSION,
    run_provider_attachment,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


CERTIFIED_PROVIDER_ATTACHMENT_VERSION = "G14_44_CERTIFIED_PROVIDER_ATTACHMENT_V1"
CERTIFIED_PROVIDER_ATTACHMENT_API = "run_certified_provider_attachment"


def run_certified_provider_attachment(
    *,
    provider_id: str,
    request: Any,
    proposal_id: str,
    timestamp: str,
    registry: ProviderRegistry,
    adapter: ProviderAdapter,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Attach a provider through the canonical certified provider boundary.

    The underlying Provider Platform runtime remains responsible for registry
    lookup, readiness, adapter validation, transport invocation, diagnostics,
    response capture, and fail-closed replay evidence. This wrapper makes that
    boundary explicit and stable for all Platform Core callers.
    """

    capture = run_provider_attachment(
        provider_id=provider_id,
        request=request,
        proposal_id=proposal_id,
        timestamp=timestamp,
        registry=registry,
        adapter=adapter,
        replay_dir=replay_dir,
    )
    certification = _certification_artifact(
        provider_id=provider_id,
        proposal_id=proposal_id,
        replay_dir=replay_dir,
        capture=capture,
    )
    capture["certified_provider_attachment"] = certification
    _persist_certification_artifact(Path(replay_dir), certification)
    return capture


def _certification_artifact(
    *,
    provider_id: str,
    proposal_id: str,
    replay_dir: str | Path,
    capture: dict[str, Any],
) -> dict[str, Any]:
    created = capture.get("provider_proposal_created")
    returned = capture.get("provider_proposal_returned")
    if not isinstance(created, dict):
        created = {}
    if not isinstance(returned, dict):
        returned = {}
    artifact = {
        "artifact_type": "CERTIFIED_PROVIDER_ATTACHMENT_ARTIFACT_V1",
        "runtime_version": CERTIFIED_PROVIDER_ATTACHMENT_VERSION,
        "certified_provider_attachment_api": CERTIFIED_PROVIDER_ATTACHMENT_API,
        "provider_platform_runtime": PROVIDER_ATTACHMENT_RUNTIME_VERSION,
        "provider_id": provider_id,
        "proposal_id": proposal_id,
        "provider_invoked": created.get("provider_invoked") is True,
        "provider_status": created.get("provider_status"),
        "failure_reason": returned.get("failure_reason") or created.get("failure_reason"),
        "request_construction_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "request_metadata_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "transport_invocation_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "response_normalization_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "provider_diagnostics_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "failure_normalization_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "retry_entry_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "provider_evidence_owner": "CERTIFIED_PROVIDER_ATTACHMENT",
        "transport_authority": False,
        "governance_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "replay_authority": False,
        "replay_visible": True,
        "replay_reference": str(Path(replay_dir)),
    }
    diagnostics = created.get("failure_diagnostics") or returned.get("failure_diagnostics")
    if isinstance(diagnostics, dict):
        artifact["failure_diagnostics"] = deepcopy(diagnostics)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist_certification_artifact(replay_dir: Path, artifact: dict[str, Any]) -> None:
    wrapper = {
        "event_type": "CERTIFIED_PROVIDER_ATTACHMENT_RECORDED",
        "replay_step": "certified_provider_attachment_recorded",
        "replay_index": 2,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / "002_certified_provider_attachment_recorded.json", wrapper)
