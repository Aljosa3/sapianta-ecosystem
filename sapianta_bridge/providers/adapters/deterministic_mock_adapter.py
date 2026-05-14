"""Deterministic mock provider adapter for tests and replay modeling."""

from __future__ import annotations

from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult
from sapianta_bridge.providers.provider_contracts import ProviderContract


class DeterministicMockAdapter(ExecutionProvider):
    contract = ProviderContract(provider_id="deterministic_mock", provider_type="DETERMINISTIC_MOCK")

    def execute(self, envelope: dict) -> NormalizedExecutionResult:  # noqa: ANN001
        validation = self.validate_envelope(envelope)
        if not validation["valid"]:
            return NormalizedExecutionResult(provider_id=self.contract.provider_id, execution_status="BLOCKED")
        artifacts = tuple(sorted(envelope.get("expected_artifacts", ())))
        return NormalizedExecutionResult(
            provider_id=self.contract.provider_id,
            execution_status="SUCCESS",
            artifacts_created=artifacts,
            execution_time_ms=0,
        )
