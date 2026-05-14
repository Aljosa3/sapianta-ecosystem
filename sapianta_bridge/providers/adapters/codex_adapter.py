"""Structural Codex provider adapter.

This adapter does not call Codex. It models the provider contract only.
"""

from __future__ import annotations

from sapianta_bridge.providers.execution_provider import ExecutionProvider
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult
from sapianta_bridge.providers.provider_contracts import ProviderContract


class CodexAdapter(ExecutionProvider):
    contract = ProviderContract(provider_id="codex", provider_type="REMOTE_LLM")

    def execute(self, envelope: dict) -> NormalizedExecutionResult:  # noqa: ANN001
        validation = self.validate_envelope(envelope)
        if not validation["valid"]:
            return NormalizedExecutionResult(provider_id=self.contract.provider_id, execution_status="BLOCKED")
        return NormalizedExecutionResult(provider_id=self.contract.provider_id, execution_status="NOT_EXECUTED")
