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
        self.sandbox_dir = self.root / "runtime_sandboxes"
        self.sandbox_result_dir = self.root / "runtime_sandbox_results"
        self.capability_request_dir = self.root / "runtime_capability_requests"
        self.capability_result_dir = self.root / "runtime_capability_results"
        self.policy_contract_dir = self.root / "runtime_policy_contracts"
        self.policy_result_dir = self.root / "runtime_policy_results"
        self.continuity_contract_dir = self.root / "runtime_continuity_contracts"
        self.continuity_result_dir = self.root / "runtime_continuity_results"
        self.snapshot_dir = self.root / "runtime_snapshots"
        self.goal_dir = self.root / "runtime_goals"
        self.goal_sequence_dir = self.root / "runtime_goal_sequences"
        self.routing_dir = self.root / "runtime_routing"
        self.routing_result_dir = self.root / "runtime_routing_results"
        self.ledger = RuntimeLedger(self.root)

    def dispatch_path(self, runtime_id: str) -> Path:
        return self.dispatch_dir / f"runtime_{runtime_id}.json"

    def result_path(self, runtime_id: str) -> Path:
        return self.result_dir / f"runtime_{runtime_id}.json"

    def provider_envelope_path(self, runtime_id: str) -> Path:
        return self.provider_invocation_dir / f"runtime_{runtime_id}_envelope.json"

    def provider_response_path(self, runtime_id: str) -> Path:
        return self.provider_invocation_dir / f"runtime_{runtime_id}_response.json"

    def sandbox_context_path(self, runtime_id: str) -> Path:
        return self.sandbox_dir / f"runtime_{runtime_id}_sandbox.json"

    def sandbox_validation_path(self, runtime_id: str) -> Path:
        return self.sandbox_dir / f"runtime_{runtime_id}_validation.json"

    def sandbox_result_path(self, runtime_id: str) -> Path:
        return self.sandbox_result_dir / f"runtime_{runtime_id}_sandbox_result.json"

    def capability_request_path(self, runtime_id: str) -> Path:
        return self.capability_request_dir / f"runtime_{runtime_id}_capability_request.json"

    def capability_validation_path(self, runtime_id: str) -> Path:
        return self.capability_request_dir / f"runtime_{runtime_id}_capability_validation.json"

    def capability_result_path(self, runtime_id: str) -> Path:
        return self.capability_result_dir / f"runtime_{runtime_id}_capability_result.json"

    def policy_contract_path(self, runtime_id: str) -> Path:
        return self.policy_contract_dir / f"runtime_{runtime_id}_policy_contract.json"

    def policy_validation_path(self, runtime_id: str) -> Path:
        return self.policy_contract_dir / f"runtime_{runtime_id}_policy_validation.json"

    def policy_result_path(self, runtime_id: str) -> Path:
        return self.policy_result_dir / f"runtime_{runtime_id}_policy_result.json"

    def continuity_contract_path(self, runtime_id: str) -> Path:
        return self.continuity_contract_dir / f"runtime_{runtime_id}_continuity_contract.json"

    def retry_evaluation_path(self, runtime_id: str) -> Path:
        return self.continuity_contract_dir / f"runtime_{runtime_id}_retry_evaluation.json"

    def continuity_result_path(self, runtime_id: str) -> Path:
        return self.continuity_result_dir / f"runtime_{runtime_id}_continuity_result.json"

    def runtime_snapshot_path(self, runtime_id: str) -> Path:
        return self.snapshot_dir / f"runtime_{runtime_id}_snapshot.json"

    def goal_contract_path(self, runtime_id: str) -> Path:
        return self.goal_dir / f"runtime_{runtime_id}_goal_contract.json"

    def goal_validation_path(self, runtime_id: str) -> Path:
        return self.goal_dir / f"runtime_{runtime_id}_goal_validation.json"

    def goal_result_path(self, runtime_id: str) -> Path:
        return self.goal_dir / f"runtime_{runtime_id}_goal_result.json"

    def goal_sequence_path(self, runtime_id: str) -> Path:
        return self.goal_sequence_dir / f"runtime_{runtime_id}_goal_sequence.json"

    def routing_contract_path(self, runtime_id: str) -> Path:
        return self.routing_dir / f"runtime_{runtime_id}_routing_contract.json"

    def capability_route_path(self, runtime_id: str) -> Path:
        return self.routing_dir / f"runtime_{runtime_id}_capability_route.json"

    def routing_validation_path(self, runtime_id: str) -> Path:
        return self.routing_dir / f"runtime_{runtime_id}_routing_validation.json"

    def routing_result_path(self, runtime_id: str) -> Path:
        return self.routing_result_dir / f"runtime_{runtime_id}_routing_result.json"

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

    def persist_sandbox_context(self, runtime_id: str, context: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.sandbox_context_path(runtime_id), context)
        self.ledger.append(
            runtime_id,
            "SANDBOX_CONTEXT_PERSISTED",
            {
                "artifact_ref": str(self.sandbox_context_path(runtime_id)),
                "replay_hash": context["replay_hash"],
            },
        )
        return context

    def persist_sandbox_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.sandbox_validation_path(runtime_id), validation)
        self.ledger.append(
            runtime_id,
            "SANDBOX_VALIDATION_PERSISTED",
            {
                "artifact_ref": str(self.sandbox_validation_path(runtime_id)),
                "replay_hash": validation["replay_hash"],
            },
        )
        return validation

    def persist_sandbox_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.sandbox_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "SANDBOX_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.sandbox_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_sandbox_context(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.sandbox_context_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_sandbox_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.sandbox_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_sandbox_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.sandbox_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_capability_request(self, runtime_id: str, request: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.capability_request_path(runtime_id), request)
        self.ledger.append(
            runtime_id,
            "CAPABILITY_REQUEST_PERSISTED",
            {
                "artifact_ref": str(self.capability_request_path(runtime_id)),
                "replay_hash": request["replay_hash"],
            },
        )
        return request

    def persist_capability_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.capability_validation_path(runtime_id), validation)
        self.ledger.append(
            runtime_id,
            "CAPABILITY_VALIDATION_PERSISTED",
            {
                "artifact_ref": str(self.capability_validation_path(runtime_id)),
                "replay_hash": validation["replay_hash"],
            },
        )
        return validation

    def persist_capability_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.capability_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "CAPABILITY_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.capability_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_capability_request(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.capability_request_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_capability_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.capability_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_capability_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.capability_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_policy_contract(self, runtime_id: str, contract: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.policy_contract_path(runtime_id), contract)
        self.ledger.append(
            runtime_id,
            "POLICY_CONTRACT_PERSISTED",
            {
                "artifact_ref": str(self.policy_contract_path(runtime_id)),
                "replay_hash": contract["replay_hash"],
            },
        )
        return contract

    def persist_policy_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.policy_validation_path(runtime_id), validation)
        self.ledger.append(
            runtime_id,
            "POLICY_VALIDATION_PERSISTED",
            {
                "artifact_ref": str(self.policy_validation_path(runtime_id)),
                "replay_hash": validation["replay_hash"],
            },
        )
        return validation

    def persist_policy_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.policy_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "POLICY_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.policy_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_policy_contract(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.policy_contract_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_policy_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.policy_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_policy_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.policy_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_continuity_contract(self, runtime_id: str, contract: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.continuity_contract_path(runtime_id), contract)
        self.ledger.append(
            runtime_id,
            "CONTINUITY_CONTRACT_PERSISTED",
            {
                "artifact_ref": str(self.continuity_contract_path(runtime_id)),
                "replay_hash": contract["replay_hash"],
            },
        )
        return contract

    def persist_retry_evaluation(self, runtime_id: str, retry_evaluation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.retry_evaluation_path(runtime_id), retry_evaluation)
        self.ledger.append(
            runtime_id,
            "RETRY_EVALUATION_PERSISTED",
            {
                "artifact_ref": str(self.retry_evaluation_path(runtime_id)),
                "replay_hash": retry_evaluation["replay_hash"],
            },
        )
        return retry_evaluation

    def persist_continuity_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.continuity_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "CONTINUITY_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.continuity_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_continuity_contract(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.continuity_contract_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_retry_evaluation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.retry_evaluation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_continuity_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.continuity_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_runtime_snapshot(self, runtime_id: str, snapshot: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.runtime_snapshot_path(runtime_id), snapshot)
        self.ledger.append(
            runtime_id,
            "RUNTIME_SNAPSHOT_PERSISTED",
            {
                "artifact_ref": str(self.runtime_snapshot_path(runtime_id)),
                "replay_hash": snapshot["replay_hash"],
            },
        )
        return snapshot

    def load_runtime_snapshot(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.runtime_snapshot_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_goal_contract(self, runtime_id: str, contract: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.goal_contract_path(runtime_id), contract)
        self.ledger.append(
            runtime_id,
            "GOAL_CONTRACT_PERSISTED",
            {
                "artifact_ref": str(self.goal_contract_path(runtime_id)),
                "replay_hash": contract["replay_hash"],
            },
        )
        return contract

    def persist_goal_sequence(self, runtime_id: str, sequence: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.goal_sequence_path(runtime_id), sequence)
        self.ledger.append(
            runtime_id,
            "GOAL_SEQUENCE_PERSISTED",
            {
                "artifact_ref": str(self.goal_sequence_path(runtime_id)),
                "replay_hash": sequence["replay_hash"],
            },
        )
        return sequence

    def persist_goal_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.goal_validation_path(runtime_id), validation)
        self.ledger.append(
            runtime_id,
            "GOAL_VALIDATION_PERSISTED",
            {
                "artifact_ref": str(self.goal_validation_path(runtime_id)),
                "replay_hash": validation["replay_hash"],
            },
        )
        return validation

    def persist_goal_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.goal_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "GOAL_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.goal_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_goal_contract(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.goal_contract_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_goal_sequence(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.goal_sequence_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_goal_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.goal_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_goal_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.goal_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def persist_routing_contract(self, runtime_id: str, contract: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.routing_contract_path(runtime_id), contract)
        self.ledger.append(
            runtime_id,
            "ROUTING_CONTRACT_PERSISTED",
            {
                "artifact_ref": str(self.routing_contract_path(runtime_id)),
                "replay_hash": contract["replay_hash"],
            },
        )
        return contract

    def persist_capability_route(self, runtime_id: str, route: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.capability_route_path(runtime_id), route)
        self.ledger.append(
            runtime_id,
            "CAPABILITY_ROUTE_PERSISTED",
            {
                "artifact_ref": str(self.capability_route_path(runtime_id)),
                "replay_hash": route["replay_hash"],
            },
        )
        return route

    def persist_routing_validation(self, runtime_id: str, validation: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.routing_validation_path(runtime_id), validation)
        self.ledger.append(
            runtime_id,
            "ROUTING_VALIDATION_PERSISTED",
            {
                "artifact_ref": str(self.routing_validation_path(runtime_id)),
                "replay_hash": validation["replay_hash"],
            },
        )
        return validation

    def persist_routing_result(self, runtime_id: str, result: dict[str, Any]) -> dict[str, Any]:
        write_json_immutable(self.routing_result_path(runtime_id), result)
        self.ledger.append(
            runtime_id,
            "ROUTING_RESULT_PERSISTED",
            {
                "artifact_ref": str(self.routing_result_path(runtime_id)),
                "replay_hash": result["replay_hash"],
            },
        )
        return result

    def load_routing_contract(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.routing_contract_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_capability_route(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.capability_route_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_routing_validation(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.routing_validation_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact

    def load_routing_result(self, runtime_id: str) -> dict[str, Any]:
        artifact = load_json(self.routing_result_path(runtime_id))
        verify_replay_hash(artifact)
        return artifact
