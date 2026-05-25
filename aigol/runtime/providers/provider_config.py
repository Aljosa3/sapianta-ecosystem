"""Provider configuration for governed provider activation."""

from __future__ import annotations

from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    api_key_env: str = "AIGOL_OPENAI_API_KEY"
    allowed_invocation_types: tuple[str, ...] = field(default=("prompt_response",))

    def api_key(self) -> str | None:
        return os.environ.get(self.api_key_env)
