from __future__ import annotations

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.provider_runtime import (
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.runtime.external_runtime_inspection_worker import (
    execute_external_runtime_inspection_worker,
    reconstruct_external_runtime_inspection_worker_replay,
)
from aigol.runtime.minimal_execution_runtime_prototype import AUTHORIZED
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.read_only_capability_attachment import READ_ONLY_RUNTIME_INSPECTION
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-31T00:00:00Z"
PROVIDER_REQUEST = {"prompt": "Inspect metadata visibility."}
PROVIDER_RESPONSE = {"proposal_text": "Metadata is descriptive evidence only."}


class StaticProviderAdapter:
    provider_id = "metadata_provider"
    provider_version = "v1"

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=PROVIDER_RESPONSE,
            timestamp=timestamp,
        )


def _provider_registry(**metadata_overrides) -> ProviderRegistry:
    registry = ProviderRegistry()
    args = {
        "provider_id": "metadata_provider",
        "provider_type": "llm",
        "provider_version": "v1",
        "provider_status": AVAILABLE,
    }
    args.update(metadata_overrides)
    registry.register_provider(ProviderMetadata(**args))
    return registry


def _run_provider(tmp_path, *, registry=None):
    return run_provider_attachment(
        provider_id="metadata_provider",
        request=PROVIDER_REQUEST,
        proposal_id="metadata-proposal-0001",
        timestamp=CREATED_AT,
        registry=registry or _provider_registry(),
        adapter=StaticProviderAdapter(),
        replay_dir=tmp_path,
    )


def _authorized_request(**overrides) -> dict:
    request = {
        "execution_id": "METADATA-WORKER-EXECUTION-000001",
        "request_id": "METADATA-WORKER-REQUEST-000001",
        "state": AUTHORIZED,
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "authorization_scope": "READ_ONLY_EXECUTION_BRIDGE",
        "authorization_hash": "sha256:authorized-by-aigol",
        "lineage_parent": "sha256:proposal-governed-by-aigol",
        "read_only": True,
        "filesystem_write_authority": False,
        "network_authority": False,
        "shell_authority": False,
        "api_authority": False,
        "orchestration_authority": False,
        "governance_authority": False,
        "worker_self_authorized": False,
        "hidden_continuation": False,
    }
    request.update(overrides)
    request["artifact_hash"] = replay_hash(request)
    return request


def _run_worker(tmp_path, **overrides):
    args = {
        "worker_attachment_id": "METADATA-WORKER-ATTACHMENT-000001",
        "authorized_execution_request": _authorized_request(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path,
        "provider": MetadataInspectionProvider(timestamp_provider=lambda: CREATED_AT),
    }
    args.update(overrides)
    return execute_external_runtime_inspection_worker(**args)


def test_provider_metadata_is_optional_and_uses_safe_defaults(tmp_path):
    capture = _run_provider(tmp_path)
    replay = reconstruct_provider_attachment_replay(tmp_path)

    assert capture["provider_proposal_created"]["provider_metadata"] == {
        "domain": "unspecified",
        "capability": "proposal_generation",
        "resource_type": "provider",
        "metadata_authority": False,
        "metadata_routing_enabled": False,
        "metadata_selection_enabled": False,
        "metadata_execution_enabled": False,
    }
    assert replay["provider_metadata"] == capture["provider_proposal_created"]["provider_metadata"]


def test_provider_metadata_is_stored_and_replay_visible(tmp_path):
    registry = _provider_registry(domain="Marketing", capability="Content Generation", resource_type="Text")
    capture = _run_provider(tmp_path, registry=registry)
    replay = reconstruct_provider_attachment_replay(tmp_path)

    assert capture["provider_proposal_created"]["provider_metadata"]["domain"] == "marketing"
    assert capture["provider_proposal_created"]["provider_metadata"]["capability"] == "content_generation"
    assert capture["provider_proposal_created"]["provider_metadata"]["resource_type"] == "text"
    assert replay["provider_metadata"] == capture["provider_proposal_created"]["provider_metadata"]


def test_provider_metadata_does_not_affect_runtime_behavior(tmp_path):
    without_metadata = _run_provider(tmp_path / "without")
    with_metadata = _run_provider(
        tmp_path / "with",
        registry=_provider_registry(domain="finance", capability="analysis", resource_type="text"),
    )

    assert without_metadata["provider_proposal_returned"]["event_type"] == with_metadata["provider_proposal_returned"]["event_type"]
    assert without_metadata["provider_proposal_created"]["response"] == with_metadata["provider_proposal_created"]["response"]
    assert without_metadata["provider_proposal_created"]["authority"] is False
    assert with_metadata["provider_proposal_created"]["authority"] is False
    assert with_metadata["provider_proposal_created"]["provider_metadata"]["metadata_execution_enabled"] is False


def test_worker_metadata_is_optional_and_uses_safe_defaults(tmp_path):
    capture = _run_worker(tmp_path)
    replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path)

    assert capture["worker_identity"]["worker_metadata"] == {
        "domain": "infrastructure",
        "capability": "read_only_runtime_inspection",
        "resource_type": "runtime_metadata",
        "metadata_authority": False,
        "metadata_routing_enabled": False,
        "metadata_selection_enabled": False,
        "metadata_execution_enabled": False,
    }
    assert replay["worker_metadata"] == capture["worker_identity"]["worker_metadata"]


def test_worker_metadata_is_stored_and_replay_visible(tmp_path):
    capture = _run_worker(
        tmp_path,
        domain="Infrastructure",
        capability="Runtime Inspection",
        resource_type="Runtime Metadata",
    )
    replay = reconstruct_external_runtime_inspection_worker_replay(tmp_path)

    assert capture["worker_identity"]["worker_metadata"]["domain"] == "infrastructure"
    assert capture["worker_identity"]["worker_metadata"]["capability"] == "runtime_inspection"
    assert capture["worker_identity"]["worker_metadata"]["resource_type"] == "runtime_metadata"
    assert replay["worker_metadata"] == capture["worker_identity"]["worker_metadata"]


def test_worker_metadata_does_not_affect_execution_or_governance(tmp_path):
    without_metadata = _run_worker(tmp_path / "without")
    with_metadata = _run_worker(
        tmp_path / "with",
        domain="trading",
        capability="portfolio_readonly_inspection",
        resource_type="analytics",
    )

    assert without_metadata["termination_record"]["final_status"] == with_metadata["termination_record"]["final_status"]
    assert without_metadata["worker_result"]["final_worker_execution_status"] == with_metadata["worker_result"]["final_worker_execution_status"]
    assert with_metadata["worker_identity"]["authorization_authority"] is False
    assert with_metadata["worker_result"]["governance_authority"] is False
    assert with_metadata["worker_identity"]["worker_metadata"]["metadata_execution_enabled"] is False
