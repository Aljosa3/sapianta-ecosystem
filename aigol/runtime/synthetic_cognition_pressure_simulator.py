"""Deterministic synthetic pressure artifacts for governed runtime boundaries."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.governance_failure_semantics import (
    FAIL_CLOSED,
    INVALIDATE_LINEAGE,
    QUARANTINE_REQUIRED,
    REJECT,
    TERMINATE_SESSION,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


AMBIGUOUS_CONTRACT = "AMBIGUOUS_CONTRACT"
PROVIDER_ESCALATION_ATTEMPT = "PROVIDER_ESCALATION_ATTEMPT"
REPLAY_CORRUPTION_ATTEMPT = "REPLAY_CORRUPTION_ATTEMPT"
AUTHORITY_DRIFT_ATTEMPT = "AUTHORITY_DRIFT_ATTEMPT"
LONG_CHAIN_ENTROPY_SEQUENCE = "LONG_CHAIN_ENTROPY_SEQUENCE"

DEFAULT_CREATED_AT = "2026-05-26T00:00:00+00:00"

ALLOWED_SIMULATION_TYPES = frozenset(
    {
        AMBIGUOUS_CONTRACT,
        PROVIDER_ESCALATION_ATTEMPT,
        REPLAY_CORRUPTION_ATTEMPT,
        AUTHORITY_DRIFT_ATTEMPT,
        LONG_CHAIN_ENTROPY_SEQUENCE,
    }
)
ALLOWED_GOVERNANCE_EXPECTATIONS = frozenset(
    {
        REJECT,
        FAIL_CLOSED,
        INVALIDATE_LINEAGE,
        TERMINATE_SESSION,
        QUARANTINE_REQUIRED,
    }
)


def _immutable(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _immutable(value[key]) for key in sorted(value)})
    if isinstance(value, list | tuple):
        return tuple(_immutable(item) for item in value)
    return deepcopy(value)


def _plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _simulation_hash_input(simulation: "SyntheticCognitionPressureArtifact") -> dict[str, Any]:
    return {
        "simulation_id": simulation.simulation_id,
        "simulation_type": simulation.simulation_type,
        "expected_governance_result": simulation.expected_governance_result,
        "generated_artifact": _plain(simulation.generated_artifact),
        "created_at": simulation.created_at,
    }


@dataclass(frozen=True)
class SyntheticCognitionPressureArtifact:
    """Immutable replay-visible synthetic pressure evidence."""

    simulation_id: str
    simulation_type: str
    expected_governance_result: str
    generated_artifact: MappingProxyType
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.simulation_id, "simulation_id")
        _require_string(self.created_at, "created_at")
        if self.simulation_type not in ALLOWED_SIMULATION_TYPES:
            raise FailClosedRuntimeError("unknown simulation type")
        if self.expected_governance_result not in ALLOWED_GOVERNANCE_EXPECTATIONS:
            raise FailClosedRuntimeError("unknown governance expectation")
        if not isinstance(self.generated_artifact, dict | MappingProxyType):
            raise FailClosedRuntimeError("generated_artifact must be a JSON object")
        immutable_artifact = _immutable(_plain(self.generated_artifact))
        canonical_serialize(_plain(immutable_artifact))
        object.__setattr__(self, "generated_artifact", immutable_artifact)
        expected_hash = replay_hash(_simulation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("simulation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "simulation_type": self.simulation_type,
            "expected_governance_result": self.expected_governance_result,
            "generated_artifact": _plain(self.generated_artifact),
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "SyntheticCognitionPressureArtifact":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("simulation artifact must be a JSON object")
        required = {
            "simulation_id",
            "simulation_type",
            "expected_governance_result",
            "generated_artifact",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("simulation artifact has malformed structure")
        return cls(
            simulation_id=artifact["simulation_id"],
            simulation_type=artifact["simulation_type"],
            expected_governance_result=artifact["expected_governance_result"],
            generated_artifact=artifact["generated_artifact"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def generate_ambiguous_contract(
    *,
    simulation_id: str = "SIM-AMBIGUOUS-CONTRACT-1",
    created_at: str = DEFAULT_CREATED_AT,
) -> SyntheticCognitionPressureArtifact:
    return SyntheticCognitionPressureArtifact(
        simulation_id=simulation_id,
        simulation_type=AMBIGUOUS_CONTRACT,
        expected_governance_result=REJECT,
        generated_artifact={
            "contract_id": "SYNTH-CONTRACT-AMBIGUOUS-1",
            "ambiguity": "duplicate operation identifiers with divergent provider asks",
            "requested_operations": [
                {
                    "provider": "readonly_http_get_provider",
                    "operation": "fetch",
                    "operation_id": "SYNTH-OP-001",
                    "created_at": "2026-05-26T00:00:01+00:00",
                },
                {
                    "provider": "metadata_inspection_provider",
                    "operation": "inspect_environment",
                    "operation_id": "SYNTH-OP-001",
                    "created_at": "2026-05-26T00:00:02+00:00",
                },
            ],
        },
        created_at=created_at,
    )


def generate_provider_escalation_attempt(
    *,
    simulation_id: str = "SIM-PROVIDER-ESCALATION-1",
    created_at: str = DEFAULT_CREATED_AT,
) -> SyntheticCognitionPressureArtifact:
    return SyntheticCognitionPressureArtifact(
        simulation_id=simulation_id,
        simulation_type=PROVIDER_ESCALATION_ATTEMPT,
        expected_governance_result=FAIL_CLOSED,
        generated_artifact={
            "contract_id": "SYNTH-CONTRACT-ESCALATION-1",
            "requested_provider": "shell_provider",
            "requested_operation": "run_command",
            "authorized_provider_boundary": [
                "readonly_filesystem_provider",
                "readonly_http_get_provider",
                "metadata_inspection_provider",
            ],
        },
        created_at=created_at,
    )


def generate_replay_corruption_attempt(
    *,
    simulation_id: str = "SIM-REPLAY-CORRUPTION-1",
    created_at: str = DEFAULT_CREATED_AT,
) -> SyntheticCognitionPressureArtifact:
    intact_evidence = {
        "operation_id": "SYNTH-OP-REPLAY-1",
        "operation": "inspect_runtime",
        "provider": "metadata_inspection_provider",
        "created_at": "2026-05-26T00:00:01+00:00",
    }
    intact_evidence["evidence_hash"] = replay_hash(intact_evidence)
    corrupted_evidence = deepcopy(intact_evidence)
    corrupted_evidence["operation"] = "inspect_process"
    return SyntheticCognitionPressureArtifact(
        simulation_id=simulation_id,
        simulation_type=REPLAY_CORRUPTION_ATTEMPT,
        expected_governance_result=INVALIDATE_LINEAGE,
        generated_artifact={
            "corruption_vector": "payload changed while evidence_hash remains from original payload",
            "original_evidence": intact_evidence,
            "corrupted_evidence": corrupted_evidence,
        },
        created_at=created_at,
    )


def generate_authority_drift_attempt(
    *,
    simulation_id: str = "SIM-AUTHORITY-DRIFT-1",
    created_at: str = DEFAULT_CREATED_AT,
) -> SyntheticCognitionPressureArtifact:
    return SyntheticCognitionPressureArtifact(
        simulation_id=simulation_id,
        simulation_type=AUTHORITY_DRIFT_ATTEMPT,
        expected_governance_result=QUARANTINE_REQUIRED,
        generated_artifact={
            "contract_id": "SYNTH-CONTRACT-DRIFT-1",
            "declared_allowed_providers": ["metadata_inspection_provider"],
            "later_requested_providers": ["metadata_inspection_provider", "readonly_http_get_provider"],
            "drift_boundary": "provider authorization set changed after declaration",
        },
        created_at=created_at,
    )


def generate_long_chain_entropy_sequence(
    *,
    simulation_id: str = "SIM-LONG-CHAIN-ENTROPY-1",
    created_at: str = DEFAULT_CREATED_AT,
    length: int = 32,
) -> SyntheticCognitionPressureArtifact:
    if not isinstance(length, int) or length < 2 or length > 128:
        raise FailClosedRuntimeError("long-chain entropy length must be between 2 and 128")
    operations = []
    for index in range(length):
        operations.append(
            {
                "operation_index": index,
                "operation_id": f"SYNTH-LINEAGE-OP-{index:03d}",
                "provider": "metadata_inspection_provider",
                "operation": "inspect_runtime",
                "created_at": f"2026-05-26T00:{index // 60:02d}:{index % 60:02d}+00:00",
            }
        )
    pressured_tail = deepcopy(operations[-1])
    pressured_tail["operation_index"] = length
    pressured_tail["created_at"] = operations[-2]["created_at"]
    operations.append(pressured_tail)
    return SyntheticCognitionPressureArtifact(
        simulation_id=simulation_id,
        simulation_type=LONG_CHAIN_ENTROPY_SEQUENCE,
        expected_governance_result=INVALIDATE_LINEAGE,
        generated_artifact={
            "lineage_length": len(operations),
            "entropy_vector": "duplicate terminal operation with non-increasing timestamp",
            "operations": operations,
        },
        created_at=created_at,
    )


def reconstruct_simulation_lineage(
    simulations: list[SyntheticCognitionPressureArtifact | dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(simulations, list):
        raise FailClosedRuntimeError("simulation lineage must be a list")
    reconstructed = []
    seen_simulation_ids: set[str] = set()
    previous_created_at = ""
    for index, simulation in enumerate(simulations):
        simulation_obj = SyntheticCognitionPressureArtifact.from_dict(simulation) if isinstance(simulation, dict) else simulation
        if not isinstance(simulation_obj, SyntheticCognitionPressureArtifact):
            raise FailClosedRuntimeError("simulation lineage entry is invalid")
        artifact = simulation_obj.to_dict()
        if artifact["simulation_id"] in seen_simulation_ids:
            raise FailClosedRuntimeError("simulation lineage contains duplicate simulation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("simulation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_simulation_ids.add(artifact["simulation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "simulation_index": index,
                "simulation_id": artifact["simulation_id"],
                "simulation_type": artifact["simulation_type"],
                "expected_governance_result": artifact["expected_governance_result"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "simulation_count": len(reconstructed),
        "simulations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage
