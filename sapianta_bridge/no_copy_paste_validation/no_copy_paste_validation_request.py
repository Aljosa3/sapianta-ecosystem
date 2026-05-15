"""Request model for no-copy/paste flow validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NoCopyPasteValidationRequest:
    ingress_path: str
    egress_path: str
    workspace_path: str
    codex_executable: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingress_path": self.ingress_path,
            "egress_path": self.egress_path,
            "workspace_path": self.workspace_path,
            "codex_executable": self.codex_executable,
            "single_ingress_only": True,
            "single_provider_only": True,
            "single_execution_only": True,
            "single_egress_only": True,
            "manual_prompt_relay_present": False,
        }


def create_validation_request(*, ingress_path: str | Path, egress_path: str | Path, workspace_path: str | Path, codex_executable: str | Path) -> NoCopyPasteValidationRequest:
    return NoCopyPasteValidationRequest(str(ingress_path), str(egress_path), str(workspace_path), str(codex_executable))
