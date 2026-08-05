"""Full constitutional workflow-branch Replay correlation and CRO coverage.

This B9 composition correlates already-produced G69-15 branch provenance and
the certified G69-16/G69-17 composition results.  It is immutable, post-hoc,
and fail closed.  It does not invoke CHE or HIC, select or execute a branch,
mutate owner state, replace owner-local Replay, or perform production cutover.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from aigol.runtime.constitutional_g64_completion_branch_composition_v1 import (
    COMPLETION_BRANCH_ESTABLISHED,
    validate_constitutional_g64_completion_branch_composition_result_v1,
)
from aigol.runtime.constitutional_natural_conversation_branch_composition_v1 import (
    NATURAL_CONVERSATION_COMMITTED,
    validate_constitutional_natural_conversation_composition_result_v1,
)
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    CANONICAL_WORKFLOW_BRANCH_ORDER,
    CERTIFIED_REUSE,
    CONSTITUTIONAL_COMPLETION,
    CONTENT_OR_REPOSITORY_MUTATION,
    GOVERNED_ACTION,
    GOVERNED_DEVELOPMENT,
    HUMAN_RETURN,
    NON_MUTATING_CAPABILITY,
    READ_ONLY,
    CanonicalProductionWorkflowBranchModelV1,
    CanonicalWorkflowBranchProvenanceV1,
    create_canonical_production_workflow_branch_model_v1,
    validate_canonical_production_workflow_branch_model_v1,
    validate_canonical_workflow_branch_journey_v1,
)
from aigol.runtime.constitutional_runtime_observatory.core import (
    GAP_PRECEDENCE,
    JOURNEY_ARCHITECTURE_VERSION,
    OBSERVATORY_CORE_VERSION,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CONSTITUTIONAL_FULL_BRANCH_REPLAY_CORRELATION_V1 = (
    "G69_18_CONSTITUTIONAL_FULL_BRANCH_REPLAY_CORRELATION_V1"
)
CONSTITUTIONAL_FULL_BRANCH_REPLAY_RECORD_V1 = (
    "G69_18_CONSTITUTIONAL_FULL_BRANCH_REPLAY_RECORD_V1"
)
CONSTITUTIONAL_FULL_BRANCH_RECONSTRUCTION_V1 = (
    "G69_18_CONSTITUTIONAL_FULL_BRANCH_RECONSTRUCTION_V1"
)
CONSTITUTIONAL_FULL_BRANCH_CRO_OBSERVATION_V1 = (
    "G69_18_CONSTITUTIONAL_FULL_BRANCH_CRO_OBSERVATION_V1"
)

FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED = (
    "FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED"
)

# These five canonical journeys cover every branch and every reciprocal edge
# in the closed G69-15 model.  They describe coverage classes, not new routes.
CERTIFIED_COMPLETE_BRANCH_JOURNEYS = (
    (READ_ONLY, HUMAN_RETURN),
    (GOVERNED_ACTION, CERTIFIED_REUSE, NON_MUTATING_CAPABILITY, HUMAN_RETURN),
    (
        GOVERNED_ACTION,
        GOVERNED_DEVELOPMENT,
        NON_MUTATING_CAPABILITY,
        HUMAN_RETURN,
    ),
    (
        GOVERNED_ACTION,
        CERTIFIED_REUSE,
        CONTENT_OR_REPOSITORY_MUTATION,
        HUMAN_RETURN,
    ),
    (
        GOVERNED_ACTION,
        GOVERNED_DEVELOPMENT,
        CONTENT_OR_REPOSITORY_MUTATION,
        CONSTITUTIONAL_COMPLETION,
        HUMAN_RETURN,
    ),
)

_CORRELATION_FIELDS = {
    "correlation_version",
    "correlation_identity",
    "coverage_status",
    "workflow_model",
    "certified_journeys",
    "branch_coverage",
    "edge_coverage",
    "natural_conversation_result",
    "g64_completion_result",
    "natural_conversation_provenance_identity",
    "g64_completion_provenance_identity",
    "che_definition_count",
    "production_hic_family_count",
    "production_owner_chain_count",
    "production_path_count",
    "parallel_production_path_count",
    "hic_responsibility",
    "hic_semantic_capability",
    "owner_local_replay_replaced",
    "branch_selected_or_executed",
    "owner_state_mutated",
    "cro_runtime_authority",
    "production_cutover_performed",
    "correlated_at",
}
_RECORD_FIELDS = {"record_version", "correlation", "integrity_hash"}
_PASSIVE_OBSERVATION = {
    "read_only": True,
    "post_hoc": True,
    "out_of_band": True,
    "authoritative": False,
    "runtime_predecessor": False,
    "inference_performed": False,
    "repair_performed": False,
    "branch_selected_or_executed": False,
    "owner_state_mutated": False,
    "production_cutover_performed": False,
}


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"full branch Replay/CRO {field_name} is absent or malformed")
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _definition(model: CanonicalProductionWorkflowBranchModelV1, branch_kind: str):
    return next(
        item for item in model.branch_definitions if item.branch_kind == branch_kind
    )


def _canonical_edges(
    model: CanonicalProductionWorkflowBranchModelV1,
) -> tuple[str, ...]:
    return tuple(
        f"{definition.branch_kind}->{successor}"
        for definition in model.branch_definitions
        for successor in definition.allowed_successor_branches
    )


def _validate_complete_journeys(
    *,
    model: CanonicalProductionWorkflowBranchModelV1,
    journeys: Any,
) -> tuple[tuple[CanonicalWorkflowBranchProvenanceV1, ...], ...]:
    if not isinstance(journeys, (tuple, list)) or len(journeys) != len(
        CERTIFIED_COMPLETE_BRANCH_JOURNEYS
    ):
        _fail("full branch Replay journey set is incomplete")
    validated = []
    provenance_identities: list[str] = []
    source_bindings: list[tuple[str, str]] = []
    for expected, journey_value in zip(CERTIFIED_COMPLETE_BRANCH_JOURNEYS, journeys):
        if not isinstance(journey_value, (tuple, list)):
            _fail("full branch Replay journey is malformed")
        journey = tuple(
            item
            if isinstance(item, CanonicalWorkflowBranchProvenanceV1)
            else CanonicalWorkflowBranchProvenanceV1.from_dict(item)
            for item in journey_value
        )
        journey = validate_canonical_workflow_branch_journey_v1(
            model=model,
            provenances=journey,
        )
        if tuple(item.branch_kind for item in journey) != expected:
            _fail("full branch Replay journey class is not canonical")
        validated.append(journey)
        source_bindings.append(
            (journey[0].source_request_identity, journey[0].source_interaction_identity)
        )
        provenance_identities.extend(item.provenance_identity for item in journey)
    if len(source_bindings) != len(set(source_bindings)):
        _fail("full branch Replay journey source bindings are duplicated")
    if len(provenance_identities) != len(set(provenance_identities)):
        _fail("full branch Replay provenance identities are duplicated")
    actual_branches = {
        item.branch_kind for journey in validated for item in journey
    }
    actual_edges = {
        f"{previous.branch_kind}->{current.branch_kind}"
        for journey in validated
        for previous, current in zip(journey, journey[1:])
    }
    if actual_branches != set(CANONICAL_WORKFLOW_BRANCH_ORDER):
        _fail("full branch Replay branch coverage is incomplete")
    if actual_edges != set(_canonical_edges(model)):
        _fail("full branch Replay edge coverage is incomplete")
    return tuple(validated)


def _evidence_digest(
    provenance: CanonicalWorkflowBranchProvenanceV1,
    role: str,
) -> tuple[str, str]:
    for item in provenance.evidence_references:
        if item.evidence_role == role:
            return item.artifact_identity, item.artifact_digest
    _fail(f"full branch Replay required evidence role {role} is absent")


def _correlation_identity(value: Mapping[str, Any]) -> str:
    body = {
        key: _plain(value[key])
        for key in sorted(_CORRELATION_FIELDS - {"correlation_identity"})
    }
    return "FULL-BRANCH-CORRELATION-" + replay_hash(body).removeprefix("sha256:")


def _validate_composition_bindings(
    *,
    model: CanonicalProductionWorkflowBranchModelV1,
    journeys: tuple[tuple[CanonicalWorkflowBranchProvenanceV1, ...], ...],
    natural_conversation_result: Any,
    g64_completion_result: Any,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    natural = validate_constitutional_natural_conversation_composition_result_v1(
        natural_conversation_result
    )
    completion = validate_constitutional_g64_completion_branch_composition_result_v1(
        g64_completion_result
    )
    if (
        natural["composition_status"] != NATURAL_CONVERSATION_COMMITTED
        or natural["selection_result"]["workflow_model_identity"]
        != model.model_identity
        or completion["composition_status"] != COMPLETION_BRANCH_ESTABLISHED
        or completion["completion_provenance"]["model_identity"]
        != model.model_identity
    ):
        _fail("full branch Replay composition result is not established")

    # The successful Natural Conversation owner hand-off is correlated to the
    # proposal-commit evidence of the certified-reuse/non-mutating journey.
    natural_provenance = journeys[1][0]
    proposal_identity, proposal_digest = _evidence_digest(
        natural_provenance,
        "PROPOSAL_COMMIT",
    )
    if (
        proposal_identity != natural["commit_identity"]
        or proposal_digest != natural["commit_receipt_checksum"]
    ):
        _fail("full branch Replay Natural Conversation correlation is invalid")

    completion_journey = tuple(
        item.to_dict() for item in journeys[-1]
    )
    if completion["branch_journey"] != list(completion_journey):
        _fail("full branch Replay G64 completion correlation is invalid")
    completion_provenance = journeys[-1][-2].provenance_identity
    if (
        completion["completion_provenance"][
            "completion_branch_provenance_identity"
        ]
        != completion_provenance
    ):
        _fail("full branch Replay G64 completion provenance is invalid")
    return (
        natural,
        completion,
        natural_provenance.provenance_identity,
        completion_provenance,
    )


def create_constitutional_full_branch_replay_correlation_v1(
    *,
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    certified_journeys: Any,
    natural_conversation_result: Mapping[str, Any],
    g64_completion_result: Mapping[str, Any],
    correlated_at: str,
) -> dict[str, Any]:
    """Correlate certified owner artifacts without routing or mutation."""

    model = validate_canonical_production_workflow_branch_model_v1(workflow_model)
    journeys = _validate_complete_journeys(model=model, journeys=certified_journeys)
    natural, completion, natural_provenance, completion_provenance = (
        _validate_composition_bindings(
            model=model,
            journeys=journeys,
            natural_conversation_result=natural_conversation_result,
            g64_completion_result=g64_completion_result,
        )
    )
    value = {
        "correlation_version": CONSTITUTIONAL_FULL_BRANCH_REPLAY_CORRELATION_V1,
        "correlation_identity": "PENDING",
        "coverage_status": FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED,
        "workflow_model": model.to_dict(),
        "certified_journeys": [
            [item.to_dict() for item in journey] for journey in journeys
        ],
        "branch_coverage": list(CANONICAL_WORKFLOW_BRANCH_ORDER),
        "edge_coverage": list(_canonical_edges(model)),
        "natural_conversation_result": natural,
        "g64_completion_result": completion,
        "natural_conversation_provenance_identity": natural_provenance,
        "g64_completion_provenance_identity": completion_provenance,
        "che_definition_count": model.che_definition_count,
        "production_hic_family_count": model.production_hic_family_count,
        "production_owner_chain_count": model.production_owner_chain_count,
        "production_path_count": model.production_path_count,
        "parallel_production_path_count": model.parallel_production_path_count,
        "hic_responsibility": model.hic_responsibility,
        "hic_semantic_capability": model.hic_semantic_capability,
        "owner_local_replay_replaced": False,
        "branch_selected_or_executed": False,
        "owner_state_mutated": False,
        "cro_runtime_authority": False,
        "production_cutover_performed": False,
        "correlated_at": _text(correlated_at, "correlated_at"),
    }
    value["correlation_identity"] = _correlation_identity(value)
    return validate_constitutional_full_branch_replay_correlation_v1(value)


def validate_constitutional_full_branch_replay_correlation_v1(
    value: Any,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _CORRELATION_FIELDS:
        _fail("full branch Replay correlation is malformed")
    candidate = deepcopy(dict(value))
    if candidate["correlation_version"] != CONSTITUTIONAL_FULL_BRANCH_REPLAY_CORRELATION_V1:
        _fail("full branch Replay correlation version is invalid")
    model = validate_canonical_production_workflow_branch_model_v1(
        candidate["workflow_model"]
    )
    journeys = _validate_complete_journeys(
        model=model,
        journeys=candidate["certified_journeys"],
    )
    natural, completion, natural_provenance, completion_provenance = (
        _validate_composition_bindings(
            model=model,
            journeys=journeys,
            natural_conversation_result=candidate["natural_conversation_result"],
            g64_completion_result=candidate["g64_completion_result"],
        )
    )
    expected = (
        candidate["coverage_status"],
        candidate["branch_coverage"],
        candidate["edge_coverage"],
        candidate["natural_conversation_provenance_identity"],
        candidate["g64_completion_provenance_identity"],
        candidate["che_definition_count"],
        candidate["production_hic_family_count"],
        candidate["production_owner_chain_count"],
        candidate["production_path_count"],
        candidate["parallel_production_path_count"],
        candidate["hic_responsibility"],
        candidate["hic_semantic_capability"],
        candidate["owner_local_replay_replaced"],
        candidate["branch_selected_or_executed"],
        candidate["owner_state_mutated"],
        candidate["cro_runtime_authority"],
        candidate["production_cutover_performed"],
    )
    canonical = (
        FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED,
        list(CANONICAL_WORKFLOW_BRANCH_ORDER),
        list(_canonical_edges(model)),
        natural_provenance,
        completion_provenance,
        1,
        1,
        1,
        1,
        0,
        "TRANSPORT_ONLY",
        "NO_SEMANTIC_CAPABILITY",
        False,
        False,
        False,
        False,
        False,
    )
    if expected != canonical:
        _fail("full branch Replay coverage or constitutional boundary is invalid")
    if (
        candidate["natural_conversation_result"] != natural
        or candidate["g64_completion_result"] != completion
        or candidate["correlation_identity"] != _correlation_identity(candidate)
    ):
        _fail("full branch Replay correlation integrity is invalid")
    _text(candidate["correlated_at"], "correlated_at")
    canonical_serialize(candidate)
    return candidate


def constitutional_full_branch_replay_record_path_v1(
    replay_root: str | Path,
    correlation_identity: str,
) -> Path:
    _text(correlation_identity, "correlation_identity")
    digest = replay_hash({"correlation_identity": correlation_identity}).removeprefix(
        "sha256:"
    )
    return Path(replay_root) / "constitutional_full_branch_replay_v1" / (
        f"correlation-{digest}.json"
    )


def persist_constitutional_full_branch_replay_correlation_v1(
    *,
    replay_root: str | Path,
    correlation: Mapping[str, Any],
) -> Path:
    validated = validate_constitutional_full_branch_replay_correlation_v1(correlation)
    path = constitutional_full_branch_replay_record_path_v1(
        replay_root,
        validated["correlation_identity"],
    )
    record = {
        "record_version": CONSTITUTIONAL_FULL_BRANCH_REPLAY_RECORD_V1,
        "correlation": validated,
        "integrity_hash": "",
    }
    record["integrity_hash"] = replay_hash(
        {key: item for key, item in record.items() if key != "integrity_hash"}
    )
    if path.exists():
        if read_constitutional_full_branch_replay_correlation_v1(path) != validated:
            _fail("full branch Replay correlation identity conflicts")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".full-branch-replay-",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(canonical_serialize(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        _fail("full branch Replay correlation write failed")
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return path


def read_constitutional_full_branch_replay_correlation_v1(
    path: str | Path,
) -> dict[str, Any]:
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError("full branch Replay record is unreadable") from exc
    if not isinstance(record, dict) or set(record) != _RECORD_FIELDS:
        _fail("full branch Replay record is malformed")
    if record["record_version"] != CONSTITUTIONAL_FULL_BRANCH_REPLAY_RECORD_V1:
        _fail("full branch Replay record version is invalid")
    expected_hash = replay_hash(
        {key: item for key, item in record.items() if key != "integrity_hash"}
    )
    if record["integrity_hash"] != expected_hash:
        _fail("full branch Replay record integrity is invalid")
    return validate_constitutional_full_branch_replay_correlation_v1(
        record["correlation"]
    )


def reconstruct_constitutional_full_branch_replay_v1(
    path: str | Path,
) -> dict[str, Any]:
    correlation = read_constitutional_full_branch_replay_correlation_v1(path)
    events = []
    for journey_index, journey in enumerate(correlation["certified_journeys"], start=1):
        for provenance in journey:
            definition = _definition(
                CanonicalProductionWorkflowBranchModelV1.from_dict(
                    correlation["workflow_model"]
                ),
                provenance["branch_kind"],
            )
            events.append(
                {
                    "journey_index": journey_index,
                    "branch_sequence": provenance["branch_sequence"],
                    "branch_kind": provenance["branch_kind"],
                    "decision_owner": definition.decision_owner,
                    "provenance_identity": provenance["provenance_identity"],
                    "source_request_identity": provenance["source_request_identity"],
                    "source_interaction_identity": provenance[
                        "source_interaction_identity"
                    ],
                    "evidence_references": deepcopy(provenance["evidence_references"]),
                }
            )
    reconstruction = {
        "reconstruction_version": CONSTITUTIONAL_FULL_BRANCH_RECONSTRUCTION_V1,
        "correlation_identity": correlation["correlation_identity"],
        "coverage_status": correlation["coverage_status"],
        "branch_coverage": deepcopy(correlation["branch_coverage"]),
        "edge_coverage": deepcopy(correlation["edge_coverage"]),
        "events": events,
        "explicit_gaps": [],
        "inference_performed": False,
        "repair_performed": False,
    }
    reconstruction["reconstruction_hash"] = replay_hash(reconstruction)
    return reconstruction


def validate_constitutional_full_branch_cro_observation_v1(
    value: Any,
) -> dict[str, Any]:
    expected_fields = {
        "observation_version",
        "observatory_core_version",
        "journey_architecture_version",
        "gap_precedence",
        "correlation_identity",
        "reconstruction",
        "observed_branch_kinds",
        "observed_edges",
        "observation_gaps",
        *_PASSIVE_OBSERVATION,
        "observation_hash",
    }
    if not isinstance(value, Mapping) or set(value) != expected_fields:
        _fail("full branch CRO observation is malformed")
    candidate = deepcopy(dict(value))
    body = deepcopy(candidate)
    actual_hash = body.pop("observation_hash", None)
    if actual_hash != replay_hash(body):
        _fail("full branch CRO observation integrity is invalid")
    if (
        candidate["observation_version"]
        != CONSTITUTIONAL_FULL_BRANCH_CRO_OBSERVATION_V1
        or candidate["observatory_core_version"] != OBSERVATORY_CORE_VERSION
        or candidate["journey_architecture_version"] != JOURNEY_ARCHITECTURE_VERSION
        or candidate["gap_precedence"] != list(GAP_PRECEDENCE)
        or candidate["observed_branch_kinds"]
        != list(CANONICAL_WORKFLOW_BRANCH_ORDER)
        or candidate["observed_edges"]
        != list(
            _canonical_edges(
                create_canonical_production_workflow_branch_model_v1()
            )
        )
        or candidate["observation_gaps"] != []
        or any(candidate[key] != expected for key, expected in _PASSIVE_OBSERVATION.items())
    ):
        _fail("full branch CRO observation boundary or coverage is invalid")
    reconstruction = candidate["reconstruction"]
    if (
        not isinstance(reconstruction, dict)
        or set(reconstruction)
        != {
            "reconstruction_version",
            "correlation_identity",
            "coverage_status",
            "branch_coverage",
            "edge_coverage",
            "events",
            "explicit_gaps",
            "inference_performed",
            "repair_performed",
            "reconstruction_hash",
        }
        or reconstruction.get("reconstruction_version")
        != CONSTITUTIONAL_FULL_BRANCH_RECONSTRUCTION_V1
        or reconstruction.get("correlation_identity")
        != candidate["correlation_identity"]
        or reconstruction.get("coverage_status")
        != FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED
        or reconstruction.get("explicit_gaps") != []
        or reconstruction.get("branch_coverage")
        != candidate["observed_branch_kinds"]
        or reconstruction.get("edge_coverage") != candidate["observed_edges"]
        or reconstruction.get("inference_performed") is not False
        or reconstruction.get("repair_performed") is not False
    ):
        _fail("full branch CRO reconstruction is incomplete")
    model = create_canonical_production_workflow_branch_model_v1()
    events = reconstruction.get("events")
    expected_positions = tuple(
        (journey_index, branch_sequence, branch_kind)
        for journey_index, journey in enumerate(
            CERTIFIED_COMPLETE_BRANCH_JOURNEYS,
            start=1,
        )
        for branch_sequence, branch_kind in enumerate(journey, start=1)
    )
    if not isinstance(events, list) or len(events) != len(expected_positions):
        _fail("full branch CRO event coverage is incomplete")
    for event, (journey_index, branch_sequence, branch_kind) in zip(
        events,
        expected_positions,
    ):
        if (
            not isinstance(event, dict)
            or set(event)
            != {
                "journey_index",
                "branch_sequence",
                "branch_kind",
                "decision_owner",
                "provenance_identity",
                "source_request_identity",
                "source_interaction_identity",
                "evidence_references",
            }
            or event["journey_index"] != journey_index
            or event["branch_sequence"] != branch_sequence
            or event["branch_kind"] != branch_kind
            or event["decision_owner"]
            != _definition(model, branch_kind).decision_owner
            or not all(
                isinstance(event[field], str) and event[field]
                for field in (
                    "provenance_identity",
                    "source_request_identity",
                    "source_interaction_identity",
                )
            )
            or not isinstance(event["evidence_references"], list)
            or not event["evidence_references"]
        ):
            _fail("full branch CRO event provenance is invalid")
    reconstruction_body = deepcopy(reconstruction)
    reconstruction_hash = reconstruction_body.pop("reconstruction_hash", None)
    if reconstruction_hash != replay_hash(reconstruction_body):
        _fail("full branch CRO reconstruction integrity is invalid")
    canonical_serialize(candidate)
    return candidate


def observe_constitutional_full_branch_coverage_for_cro_v1(
    path: str | Path,
) -> dict[str, Any]:
    """Passively observe one authenticated full-coverage Replay record."""

    reconstruction = reconstruct_constitutional_full_branch_replay_v1(path)
    observation = {
        "observation_version": CONSTITUTIONAL_FULL_BRANCH_CRO_OBSERVATION_V1,
        "observatory_core_version": OBSERVATORY_CORE_VERSION,
        "journey_architecture_version": JOURNEY_ARCHITECTURE_VERSION,
        "gap_precedence": list(GAP_PRECEDENCE),
        "correlation_identity": reconstruction["correlation_identity"],
        "reconstruction": reconstruction,
        "observed_branch_kinds": deepcopy(reconstruction["branch_coverage"]),
        "observed_edges": deepcopy(reconstruction["edge_coverage"]),
        "observation_gaps": [],
        **deepcopy(_PASSIVE_OBSERVATION),
    }
    observation["observation_hash"] = replay_hash(observation)
    return validate_constitutional_full_branch_cro_observation_v1(observation)
