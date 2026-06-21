"""Provider configuration for governed provider activation."""

from __future__ import annotations

from dataclasses import dataclass, field
import os

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_credential_vault import (
    DEFAULT_VAULT_PATH,
    retrieve_provider_credential,
)


@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    credential_reference: str = "vault://provider/openai"
    api_key_env: str = "AIGOL_OPENAI_API_KEY"
    vault_path: str | None = None
    allow_env_fallback: bool = True
    allowed_invocation_types: tuple[str, ...] = field(default=("prompt_response",))

    def api_key(self) -> str | None:
        if self.credential_reference.startswith("vault://provider/"):
            try:
                credential = retrieve_provider_credential(
                    provider_id=self.provider,
                    authorization_context={"provider_config": "ProviderConfig.api_key"},
                    vault_path=self.vault_path or DEFAULT_VAULT_PATH,
                    allow_env_fallback=self.allow_env_fallback,
                )
            except FailClosedRuntimeError as exc:
                if "credential unavailable" in str(exc):
                    return None
                raise
            return credential["_credential_secret"]
        return os.environ.get(self.api_key_env)
