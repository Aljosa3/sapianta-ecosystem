"""File-backed deterministic runtime transport store."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import GovernedReturnArtifact, RuntimePackage

from .ledger import RuntimeLedger
from .serialization import load_json, verify_replay_hash, with_replay_hash, write_json_immutable


class RuntimeStore:
    """Append-only persistence for runtime dispatch and return artifacts."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.dispatch_dir = self.root / "runtime_dispatch"
        self.result_dir = self.root / "runtime_results"
        self.replay_dir = self.root / "runtime_replay"
        self.provider_invocation_dir = self.root / "runtime_provider_invocations"
        self.ledger = RuntimeLedger(self.root)

    def dispatch_path(self, runtime_id: str) -> Path:
        return self.dispatch_dir / f"runtime_{runtime_id}.json"

    def result_path(self, runtime_id: str) -> Path:
        return self.result_dir / f"runtime_{runtime_id}.json"

    def provider_envelope_path(self, runtime_id: str) -> Path:
        return self.provider_invocation_dir / f"runtime_{runtime_id}_envelope.json"

    def provider_response_path(self, runtime_id: str) -> Path:
        return self.provider_invocation_dir / f"runtime_{runtime_id}_response.json"

    def persist_dispatch(self, runtime_package: RuntimePackage, dispatch_artifact: dict[str, Any]) -> dict[str, Any]:
        artifact = with_replay_hash(
            {
                "artifact_type": "RUNTIME_TRANSPORT_DISPATCH",
                "runtime_id": runtime_package.runtime_id,
                "package_id": runtime_package.package_id,
                "worker_id": runtime_package.worker_id,
                "provider": runtime_package.provider,
                "governance_state": runtime_package.governance_state,
                "lifecycle_state": dispatch_artifact["lifecycle_state"],
                "lineage_refs": deepcopy(runtime_package.lineage_refs),
                "dispatch_timestamp": runtime_package.created_at,
                "source_dispatch_replay_hash": dispatch_artifact.get("dispatch_replay_hash"),
            }
        )
        write_json_immutable(self.dispatch_path(runtime_package.runtime_id), artifact)
        self.ledger.append(
            runtime_package.runtime_id,
            "DISPATCH_PERSISTED",
            {
                "artifact_ref": str(self.dispatch_path(runtime_package.runtime_id)),
                "replay_hash": artifact["replay_hash"],
            },
        )
        return artifact

    def persist_lifecycle_transitions(self, runtime_id: str, transitions: list[dict[str, str]]) -> None:
        for transition in transitions:
            self.ledger.append(runtime_id, "LIFECYCLE_TRANSITION", transition)

    def persist_result(self, runtime_package: RuntimePackage, result: GovernedReturnArtifact) -> dict[str, Any]:
        result_dict = result.to_dict()
        artifact = with_replay_hash(
            {
                "artifact_type": "RUNTIME_TRANSPORT_RESULT",
                "runtime_id": runtime_package.runtime_id,
                "package_id": runtime_package.package_id,
                "worker_id": runtime_package.worker_id,
                "provider": runtime_package.provider,
                "provider_response": deepcopy(result_dict["provider_response"]),
                "lifecycle_state": result_dict["lifecycle_state"],
                "status": result_dict["status"],
                "boundary_guarantees": deepcopy(result_dict["boundary_guarantees"]),
                "closure_timestamp": runtime_package.created_at,
                "governed_return_replay_hash": result_dict["replay_hash"],
            }
        )
        write_json_immutable(self.result_path(runtime_package.runtime_id), artifact)
        self.ledger.append(
            runtime_package.runtime_id,
            "RESULT_PERSISTED",
            {
                "artifact_ref": str(self.result_path(runtime_package.runtime_id)),
                "replay_hash": artifact["replay_hash"],
            },
        )
        self.ledger.append(
            runtime_package.runtime_id,
            "RUNTIME_CLOSED",
            {
                "lifecycle_state": result_dict["lifecycle_state"],
                "status": result_dict["status"],
                "replay_hash": artifact["replay_hash"],
            },
        )
        return artifact

    def load_dispatch(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.dispatch_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_provider_envelope(self, runtime_id: str, envelope: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.provider_envelope_path(runtime_id), envelope)
        self.ledger.append(
            runtime_id,
            "PROVIDER_ENVELOPE_PERSISTED",
            {
                "artifact_ref": str(self.provider_envelope_path(runtime_id)),
                "replay_hash": envelope["replay_hash"],
            },
        )
        return envelope

    def persist_provider_response(self, runtime_id: str, response: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.provider_response_path(runtime_id), response)
        self.ledger.append(
            runtime_id,
            "PROVIDER_RESPONSE_PERSISTED",
            {
                "artifact_ref": str(self.provider_response_path(runtime_id)),
                "replay_hash": response["replay_hash"],
            },
        )
        return response

    def load_provider_envelope(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.provider_envelope_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_provider_response(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.provider_response_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact
