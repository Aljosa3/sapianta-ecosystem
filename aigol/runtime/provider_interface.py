"""Provider contract for the AiGOL runtime engine foundation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ProviderResponse, RuntimePackage


class ProviderInterface(ABC):
    """Abstract provider interface.

    Providers are not authority. They receive a validated runtime package and
    may only return a ProviderResponse to the runtime engine.
    """

    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
        raise NotImplementedError
