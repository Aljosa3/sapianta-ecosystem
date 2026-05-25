"""Deterministic mock provider for the runtime engine foundation."""

from __future__ import annotations

from copy import deepcopy

from .models import ProviderResponse, RuntimePackage, replay_hash
from .provider_interface import ProviderInterface


class MockProvider(ProviderInterface):
    """Mock-only provider that echoes payload evidence deterministically."""

    def provider_name(self) -> str:
        return "mock"

    def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
        payload = deepcopy(runtime_package.payload)
        return ProviderResponse(
            provider=self.provider_name(),
            status="MOCK_RETURNED",
            output={
                "echo": payload,
                "task_type": runtime_package.task_type,
                "payload_hash": replay_hash(payload),
            },
            metadata={
                "real_execution": False,
                "external_api_called": False,
                "subprocess_spawned": False,
            },
        )
