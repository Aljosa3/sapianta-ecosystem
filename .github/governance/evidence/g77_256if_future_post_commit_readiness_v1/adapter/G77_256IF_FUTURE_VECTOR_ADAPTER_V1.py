#!/usr/bin/env python3
"""Repository-only FUTURE act/CHE projection for the existing P11 route.

This adapter owns no authority, clock, launcher, runtime, or P11 semantics.  It
binds the committed IE semantic payload to one fresh outer act identity and to
the canonical CHE dependency graph.  The deterministic evaluation time is
exposed only as an explicit ``now_unix_ns`` argument for a later, separately
authorized generation.  There is intentionally no operational CLI entrypoint.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
    NOT_APPLICABLE,
    UNAVAILABLE_PRE_WRITE,
    create_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    CanonicalHumanAuthorityActV1,
)
from aigol.runtime.transport.serialization import replay_hash


sys.dont_write_bytecode = True

IE_ROOT = Path(".github/governance/evidence/g77_256ie_future_formalization_v1")
IE_PRODUCER = IE_ROOT / "producer/G77_256IE_FUTURE_VECTOR_PRODUCER_V1.py"
IE_REDUCER = IE_ROOT / "reducer/G77_256IE_FUTURE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
IE_PRODUCER_SHA256 = "a683e65b8f2a84f67851e2516bf50d5d7fc3d0fe25a5b0fecc82bf1c244f9fbc"
IE_REDUCER_SHA256 = "5816e62bca2017672415fd98f5627d23d7481486c0f479a084298a4fa8a16142"
IE_HEAD = "9420764a5bb6db8909334f2a422225687a37a346"
IE_TREE = "b9ebdc1015e9b9459ccd93841cc8d1c7377ddc19"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
EVALUATION_TIME_UNIX_NS = 500
FUTURE_VALID_FROM_UNIX_NS = 600
VALID_UNTIL_UNIX_NS = 1000
ACT_IDENTITY = "G77_256IF_REPOSITORY_ONLY_FUTURE_ACT_REPRESENTATION_001"
GENERATION_IDENTITY = "G77_256IF_POST_COMMIT_FUTURE_LIVE_BINDING_AND_PREOPERATIONAL_READINESS_V1"


class FutureAdapterError(ValueError):
    """One deterministic fail-closed FUTURE projection rejection."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise FutureAdapterError(f"OWNER_IMPORT_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _ie_packet(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    producer_path = root / IE_PRODUCER
    reducer_path = root / IE_REDUCER
    if _sha256(producer_path) != IE_PRODUCER_SHA256:
        raise FutureAdapterError("IE_PRODUCER_HASH_MISMATCH")
    if _sha256(reducer_path) != IE_REDUCER_SHA256:
        raise FutureAdapterError("IE_REDUCER_HASH_MISMATCH")
    producer = _load(producer_path, "g77_256if_ie_producer")
    reducer = _load(reducer_path, "g77_256if_ie_reducer")
    packet = producer.produce_future_vector(root)
    result = reducer.reduce_future_repository_vector(packet)
    if result["future_repository_formalization"] != "VERIFIED":
        raise FutureAdapterError("IE_FORMALIZATION_NOT_VERIFIED")
    if packet["future_payload_digest"] == packet["baseline_payload_digest"]:
        raise FutureAdapterError("FUTURE_PAYLOAD_DIGEST_NOT_RECOMPUTED")
    if packet["differing_payload_fields"] != ["valid_from_unix_ns"]:
        raise FutureAdapterError("FUTURE_MUTATION_NOT_ISOLATED")
    if (
        packet["evaluation_time_unix_ns"],
        packet["future_payload"]["valid_from_unix_ns"],
        packet["future_payload"]["valid_until_unix_ns"],
    ) != (EVALUATION_TIME_UNIX_NS, FUTURE_VALID_FROM_UNIX_NS, VALID_UNTIL_UNIX_NS):
        raise FutureAdapterError("FUTURE_TIME_FIXTURE_DRIFT")
    return packet


def construct_repository_only_future_act(
    repository_root: Path,
) -> CanonicalHumanAuthorityActV1:
    """Create one canonical act representation that confers no authority."""

    packet = _ie_packet(repository_root)
    return CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=ACT_IDENTITY,
        authority_kind=AUTHORIZATION,
        interaction_identity="G77_256IF_REPOSITORY_ONLY_INTERACTION_001",
        conversation_identity="G77_256IF_REPOSITORY_ONLY_CONVERSATION_001",
        session_identity="G77_256IF_REPOSITORY_ONLY_SESSION_001",
        actor_identity="G77_256IF_NONAUTHORITY_FIXTURE_ACTOR",
        request_identity="G77_256IF_REPOSITORY_ONLY_REQUEST_IDENTITY_001",
        continuation_identity="G77_256IF_REPOSITORY_ONLY_CONTINUATION_001",
        target_identity="P11_DA_BOUNDED_OPERATIONAL_CONSUMER_V1",
        target_revision=0,
        producing_owner="HUMAN_AUTHORITY",
        expected_owner="P11_DA_PROTECTED_CUSTODY_OWNER_V1",
        authority_scope="REPOSITORY_ONLY_NONAUTHORIZING_FUTURE_REPRESENTATION",
        payload=packet["future_payload"],
        payload_digest=packet["future_payload_digest"],
        metadata={
            "artifact_class": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
            "committed_ie_head": IE_HEAD,
            "committed_ie_tree": IE_TREE,
            "evaluation_time_unix_ns": EVALUATION_TIME_UNIX_NS,
            "generation_identity": GENERATION_IDENTITY,
            "human_authority_present": False,
            "selected_vector": SELECTED_VECTOR,
        },
    )


def construct_repository_only_che(repository_root: Path, act: Any) -> Any:
    """Propagate the act payload and outer identity through canonical CHE."""

    del repository_root
    return create_canonical_che_evidence_correlation_v1(
        contract_version=CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        interaction_identity=act.interaction_identity,
        conversation_identity=act.conversation_identity,
        session_identity=act.session_identity,
        workspace_identity="G77_256IF_REPOSITORY_WORKSPACE",
        runtime_scope_identity=GENERATION_IDENTITY,
        actor_identity=act.actor_identity,
        source_channel_identity="G77_256IF_REPOSITORY_ONLY_CHANNEL",
        adapter_identity="G77_256IF_FUTURE_VECTOR_ADAPTER_V1",
        request_identity=act.request_identity,
        che_entry_identity="G77_256IF_CHE_ENTRY_REPRESENTATION_001",
        source_act_identity=act.authority_act_identity,
        source_act_digest=replay_hash(act.to_dict()),
        order_identity="G77_256IF_ORDER_REPRESENTATION_001",
        idempotency_identity="G77_256IF_IDEMPOTENCY_REPRESENTATION_001",
        continuation_identity=act.continuation_identity,
        continuation_sequence=NOT_APPLICABLE,
        authority_act_identity=act.authority_act_identity,
        authority_kind=act.authority_kind,
        authority_requesting_owner_identity=act.expected_owner,
        authority_target_identity=act.target_identity,
        authority_target_revision=act.target_revision,
        authority_payload_digest=act.payload_digest,
        authority_result_identity=NOT_APPLICABLE,
        opaque_reference_set_identity=NOT_APPLICABLE,
        ordered_reference_set_digest=NOT_APPLICABLE,
        opaque_reference_correlations=(),
        producing_owner_identity="CANONICAL_HUMAN_ENTRY",
        owner_state_identity=NOT_APPLICABLE,
        owner_revision_before=NOT_APPLICABLE,
        owner_revision_after=NOT_APPLICABLE,
        owner_advancement=NOT_APPLICABLE,
        owner_disposition=NOT_APPLICABLE,
        next_act_identity=NOT_APPLICABLE,
        refusal_identity=NOT_APPLICABLE,
        terminal_identity=NOT_APPLICABLE,
        owner_projection_identity=NOT_APPLICABLE,
        failure_identity=NOT_APPLICABLE,
        presentation_identity=NOT_APPLICABLE,
        response_identity=NOT_APPLICABLE,
        response_digest=NOT_APPLICABLE,
        delivery_record_identity=NOT_APPLICABLE,
        delivery_status=NOT_APPLICABLE,
        duplicate_resolution=NOT_APPLICABLE,
        acknowledgement_state=NOT_APPLICABLE,
        replay_references=(),
        replay_status=NOT_APPLICABLE,
        certification_references=(),
        certification_status=NOT_APPLICABLE,
        evidence_status=UNAVAILABLE_PRE_WRITE,
        metadata={
            "artifact_class": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
            "committed_ie_head": IE_HEAD,
            "committed_ie_tree": IE_TREE,
            "evaluation_time_unix_ns": EVALUATION_TIME_UNIX_NS,
            "generation_identity": GENERATION_IDENTITY,
        },
    )


def build_repository_projection(repository_root: Path) -> dict[str, Any]:
    packet = _ie_packet(repository_root)
    act = construct_repository_only_future_act(repository_root)
    correlation = construct_repository_only_che(repository_root, act)
    return {
        "schema_id": "G77_256IF_FUTURE_ACT_CHE_REPOSITORY_BINDING_V1",
        "artifact_class": "TEST_ONLY__NON_AUTHORITY__NON_OPERATIONAL",
        "committed_ie_head": IE_HEAD,
        "committed_ie_tree": IE_TREE,
        "selected_vector": SELECTED_VECTOR,
        "evaluation_time_unix_ns": EVALUATION_TIME_UNIX_NS,
        "human_authority_act_representation": act.to_dict(),
        "che_correlation": correlation.to_dict(),
        "semantic_independent_mutation_count": packet["independent_mutation_count"],
        "semantic_independent_mutated_coordinate": packet["independent_mutated_coordinate"],
        "live_binding_dependent_recomputation_count": 3,
        "live_binding_dependent_recomputed_coordinates": [
            "che_correlation.authority_payload_digest",
            "che_correlation.source_act_digest",
            "che_correlation.correlation_identity",
        ],
        "human_operational_authority": 0,
        "request_count": 0,
        "operation_attempt_count": 0,
        "p11_entry_count": 0,
        "protected_effect_count": 0,
    }


def deterministic_submission_kwargs(repository_root: Path) -> dict[str, int]:
    """Return the existing P11 explicit-time projection for later operation."""

    _ie_packet(repository_root)
    return {"now_unix_ns": EVALUATION_TIME_UNIX_NS}


if __name__ == "__main__":
    raise SystemExit("repository-only FUTURE adapter; no operational CLI entry point")
