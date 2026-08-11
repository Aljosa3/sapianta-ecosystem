"""Bounded Candidate H Stage-5 fixture composition.

The module consumes an already durable Stage-4 authentication execution and
already formed constitutional evidence.  It validates the forward identity
DAG, publishes immutable evidence through the existing Candidate store, and
binds retained-root evidence to the authenticated TargetV5 origin coordinate
for one fixture-only CAS.
It does not choose a Human disposition, authenticate, sign, create a store or
root coordinate, execute BEGIN, replay, activate, deploy, or create a
production effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .authentication import FixtureAuthenticationExecution
from .cj1 import cj1_digest, cj1_identity
from .models import (
    CandidateHInputReferenceManifestV2,
    CandidateHFoundingAttemptTerminalReadBackV1,
    CandidateHOneShotDormancyRebaseGuardV2,
    ConstitutionalExistingOrdinaryRepairChainCensusV2,
    ConstitutionalMetaRepairStateV3,
    ConstitutionalMetaRepairInitialAdoptionTargetV5,
    ConstitutionalMetaRepairTransitionV3,
    ConstitutionalRootEvolutionSnapshotV4,
    ConstitutionalRootSerializationCoordinatorStateV4,
    ConstitutionalTerminalRootSemanticImageCommitmentV3,
    ExternalConstituentFoundingAdoptionTransitionV3,
    ExternalConstituentFoundingEligibilityCertificationV3,
    ExternalConstituentFoundingEligibilityProofSetV3,
    ExternalConstituentHumanFirstAdoptionDecisionV2,
    HumanFounderAuthenticationCommitmentV2,
    HumanFounderExternalCapacityEvidenceV2,
    OrdinaryCAPReachabilityStateV2,
)
from .persistence import (
    ArtifactAddress,
    CandidateHStore,
    CandidatePersistenceError,
    CompareAndSwapResult,
    ImmutableWriteResult,
    SlotReadBack,
)
from .validators import (
    CandidateValidationError,
    IdentityDAGNode,
    IdentityDAGValidation,
    PredecessorReference,
    descriptor_for,
    validate_artifact,
    validate_identity_dag,
    validate_p012_structural_bindings,
)


ROOT_OWNER: Final = "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN"
MANIFEST_IDENTITY_PREFIX: Final = "human-founder-candidate-h-input-manifest-v2-sha256:"
TARGET_V5_IDENTITY_PREFIX: Final = "founding-target-v5:"
TARGET_V5_ROOT_BINDING_MODE: Final = "STABLE_EVENT_ORIGIN_PLUS_PER_ATTEMPT_CURRENT_ROOT"


class CandidateOrchestrationError(RuntimeError):
    """Stable fail-closed Stage-5 composition failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


def _fail(code: str, detail: str) -> None:
    raise CandidateOrchestrationError(code, detail)


@dataclass(frozen=True, slots=True)
class FixtureForwardComposition:
    """Already formed forward evidence and one retained-root coordinate."""

    proof_set: ExternalConstituentFoundingEligibilityProofSetV3
    certification: ExternalConstituentFoundingEligibilityCertificationV3
    transition: ExternalConstituentFoundingAdoptionTransitionV3
    ordinary_chain_census: ConstitutionalExistingOrdinaryRepairChainCensusV2
    cap_reachability_state: OrdinaryCAPReachabilityStateV2
    dormancy_guard: CandidateHOneShotDormancyRebaseGuardV2
    meta_repair_transition: ConstitutionalMetaRepairTransitionV3
    meta_repair_state: ConstitutionalMetaRepairStateV3
    terminal_root_commitment: ConstitutionalTerminalRootSemanticImageCommitmentV3
    terminal_coordinator_state: ConstitutionalRootSerializationCoordinatorStateV4
    resulting_root: ConstitutionalRootEvolutionSnapshotV4
    attempt_terminal_read_back: CandidateHFoundingAttemptTerminalReadBackV1
    retained_root_predecessor: SlotReadBack


@dataclass(frozen=True, slots=True)
class FixtureOrchestrationExecution:
    """Non-canonical operational result; never constitutional evidence."""

    outcome: str
    authentication_result_identity: str
    decision_identity: str
    identity_dag: IdentityDAGValidation | None
    immutable_writes: tuple[ImmutableWriteResult, ...]
    retained_root_cas: CompareAndSwapResult | None
    terminal_write: ImmutableWriteResult | None
    fixture_effects_applied: int
    production_effects_applied: int
    originating_human_authorities: int
    originating_constituent_authorities: int
    human_entry_points: int
    retained_roots: int
    persistent_founder_authorities: int
    fixture_authority_permanently_exhausted: bool


def _require_equal(actual: object, expected: object, detail: str) -> None:
    if actual != expected:
        _fail("FORWARD_BINDING_MISMATCH", detail)


def _require_content_pair(
    identity: object,
    digest: object,
    *,
    prefix: str | None,
    token: str,
    detail: str,
) -> tuple[str, str]:
    if not isinstance(identity, str) or not isinstance(digest, str):
        _fail(token, detail)
    if prefix is not None and not identity.startswith(prefix):
        _fail(token, detail)
    if ":" not in identity or not digest.startswith("sha256:"):
        _fail(token, detail)
    identity_hash = identity.rsplit(":", 1)[-1]
    digest_hash = digest.removeprefix("sha256:")
    if (
        len(identity_hash) != 64
        or len(digest_hash) != 64
        or identity_hash != digest_hash
        or any(character not in "0123456789abcdef" for character in identity_hash)
    ):
        _fail(token, detail)
    return identity, digest


def _read_authoritative_immutable(
    store: CandidateHStore,
    model_type: type,
    pair: tuple[str, str],
    *,
    missing_token: str,
    corrupt_token: str,
    address_token: str,
    owner_bindings: dict[str, str],
):
    try:
        model, _ = store.read_immutable(
            model_type,
            ArtifactAddress(pair[0], pair[1]),
            owner_bindings=owner_bindings,
        )
    except CandidatePersistenceError as exc:
        if exc.code == "MISSING_IMMUTABLE_RECORD":
            _fail(missing_token, exc.code)
        if exc.code == "CORRUPT_IMMUTABLE_RECORD":
            _fail(corrupt_token, exc.code)
        if exc.code == "ARTIFACT_ADDRESS_MISMATCH":
            _fail(address_token, exc.code)
        _fail(corrupt_token, exc.code)
    return model


def _reference(evidence: object, owner_bindings: dict[str, str]) -> PredecessorReference:
    descriptor = descriptor_for(evidence, owner_bindings=owner_bindings)
    return PredecessorReference(
        descriptor.artifact_type,
        descriptor.artifact_version,
        descriptor.artifact_identity,
        descriptor.artifact_digest,
    )


def _validate_authentication_predecessor(
    store: CandidateHStore,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    commitment: HumanFounderAuthenticationCommitmentV2,
    authentication: FixtureAuthenticationExecution,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    owner_bindings: dict[str, str],
) -> None:
    if not isinstance(authentication, FixtureAuthenticationExecution):
        _fail("MISSING_AUTHENTICATION_PREDECESSOR", "FixtureAuthenticationExecution")
    result = authentication.result
    try:
        validate_artifact(capacity, owner_bindings=owner_bindings)
        validate_artifact(commitment)
        validate_artifact(result, owner_bindings=owner_bindings)
        validate_artifact(decision, owner_bindings=owner_bindings)
        persisted, read_back = store.read_immutable(
            type(result),
            ArtifactAddress(result.artifact_identity, result.artifact_digest),
            owner_bindings=owner_bindings,
        )
    except (CandidatePersistenceError, CandidateValidationError) as exc:
        _fail("INVALID_PREDECESSOR", str(exc))
    if persisted != result or read_back != authentication.result_write.read_back:
        _fail("AUTHENTICATION_READ_BACK_MISMATCH", result.artifact_identity)
    if (
        authentication.logical_human_authorizations != 1
        or authentication.logical_signer_invocations != 1
        or authentication.admissible_results != 1
        or authentication.founding_effects != 0
    ):
        _fail("AUTHENTICATION_CARDINALITY_MISMATCH", result.artifact_identity)
    if (
        result.retry_permitted is not False
        or result.second_authentication_permitted is not False
        or result.capacity_permanently_exhausted is not True
        or result.terminal is not True
    ):
        _fail("AUTHENTICATION_NOT_EXHAUSTED", result.artifact_identity)
    commitment_payload = commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
    _require_equal(
        (
            result.human_founder_capacity_identity,
            result.human_founder_capacity_digest,
        ),
        (capacity.artifact_identity, capacity.artifact_digest),
        "result/capacity",
    )
    _require_equal(
        (
            decision.human_founder_external_capacity_evidence_identity,
            decision.human_founder_external_capacity_evidence_digest,
        ),
        (capacity.artifact_identity, capacity.artifact_digest),
        "decision/capacity",
    )
    _require_equal(
        (
            decision.authentication_result_read_back_identity,
            decision.authentication_result_read_back_digest,
        ),
        (result.artifact_identity, result.artifact_digest),
        "decision/result",
    )
    _require_equal(
        (decision.authentication_commitment_identity, decision.authentication_commitment_digest),
        commitment_pair,
        "decision/commitment",
    )
    _require_equal(
        (result.authentication_commitment_identity, result.authentication_commitment_digest),
        commitment_pair,
        "result/commitment",
    )
    _require_equal(decision.human_signature, result.signature, "decision/signature")
    _require_equal(
        decision.human_signature_key_identity,
        result.signature_key_identity,
        "decision/signature key",
    )


def _validate_initial_begin(composition: FixtureForwardComposition) -> None:
    if composition.proof_set.attempt_kind != "INITIAL_BEGIN":
        _fail("INITIAL_BEGIN_KIND_MISMATCH", "proof_set")
    if composition.proof_set.attempt_sequence != 1:
        _fail("INITIAL_BEGIN_SEQUENCE_MISMATCH", "proof_set")
    forbidden_presence = (
        ("proof_set.consuming_disposition_identity", composition.proof_set.consuming_disposition_identity),
        ("proof_set.consuming_disposition_digest", composition.proof_set.consuming_disposition_digest),
        ("proof_set.predecessor_attempt_identity", composition.proof_set.predecessor_attempt_identity),
        (
            "proof_set.predecessor_attempt_terminal_read_back_identity",
            composition.proof_set.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "proof_set.predecessor_attempt_terminal_read_back_digest",
            composition.proof_set.predecessor_attempt_terminal_read_back_digest,
        ),
        (
            "proof_set.predecessor_abandoned_commitment_identity",
            composition.proof_set.predecessor_abandoned_commitment_identity,
        ),
        (
            "proof_set.predecessor_abandoned_commitment_digest",
            composition.proof_set.predecessor_abandoned_commitment_digest,
        ),
        (
            "certification.consuming_disposition_identity",
            composition.certification.consuming_disposition_identity,
        ),
        (
            "certification.consuming_disposition_digest",
            composition.certification.consuming_disposition_digest,
        ),
        (
            "certification.predecessor_attempt_terminal_read_back_identity",
            composition.certification.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "certification.predecessor_attempt_terminal_read_back_digest",
            composition.certification.predecessor_attempt_terminal_read_back_digest,
        ),
        ("transition.consuming_disposition_identity", composition.transition.consuming_disposition_identity),
        ("transition.consuming_disposition_digest", composition.transition.consuming_disposition_digest),
        ("transition.predecessor_attempt_identity", composition.transition.predecessor_attempt_identity),
        (
            "transition.predecessor_attempt_terminal_read_back_identity",
            composition.transition.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "transition.predecessor_attempt_terminal_read_back_digest",
            composition.transition.predecessor_attempt_terminal_read_back_digest,
        ),
        (
            "transition.predecessor_abandoned_commitment_identity",
            composition.transition.predecessor_abandoned_commitment_identity,
        ),
        (
            "transition.predecessor_abandoned_commitment_digest",
            composition.transition.predecessor_abandoned_commitment_digest,
        ),
        (
            "terminal_root_commitment.predecessor_attempt_identity",
            composition.terminal_root_commitment.predecessor_attempt_identity,
        ),
        (
            "terminal_root_commitment.predecessor_attempt_terminal_read_back_identity",
            composition.terminal_root_commitment.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "terminal_root_commitment.predecessor_attempt_terminal_read_back_digest",
            composition.terminal_root_commitment.predecessor_attempt_terminal_read_back_digest,
        ),
        (
            "terminal_coordinator_state.predecessor_attempt_identity",
            composition.terminal_coordinator_state.predecessor_attempt_identity,
        ),
        (
            "terminal_coordinator_state.predecessor_attempt_terminal_read_back_identity",
            composition.terminal_coordinator_state.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "terminal_coordinator_state.predecessor_attempt_terminal_read_back_digest",
            composition.terminal_coordinator_state.predecessor_attempt_terminal_read_back_digest,
        ),
        (
            "attempt_terminal_read_back.predecessor_attempt_identity",
            composition.attempt_terminal_read_back.predecessor_attempt_identity,
        ),
        (
            "attempt_terminal_read_back.predecessor_attempt_terminal_read_back_identity",
            composition.attempt_terminal_read_back.predecessor_attempt_terminal_read_back_identity,
        ),
        (
            "attempt_terminal_read_back.predecessor_attempt_terminal_read_back_digest",
            composition.attempt_terminal_read_back.predecessor_attempt_terminal_read_back_digest,
        ),
        (
            "attempt_terminal_read_back.next_attempt_sequence",
            composition.attempt_terminal_read_back.next_attempt_sequence,
        ),
    )
    for field_name, value in forbidden_presence:
        if value is not None:
            _fail("INITIAL_BEGIN_PREDECESSOR_PRESENT", field_name)


def _validate_authoritative_predecessors(
    store: CandidateHStore,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    commitment: HumanFounderAuthenticationCommitmentV2,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    composition: FixtureForwardComposition,
    owner_bindings: dict[str, str],
) -> tuple[tuple[str, str], tuple[str, str, int]]:
    manifest_pair = _require_content_pair(
        commitment.candidate_h_input_reference_manifest_identity,
        commitment.candidate_h_input_reference_manifest_digest,
        prefix=MANIFEST_IDENTITY_PREFIX,
        token="MANIFEST_PAIR_MISMATCH",
        detail="commitment manifest pair",
    )
    manifest = _read_authoritative_immutable(
        store,
        CandidateHInputReferenceManifestV2,
        manifest_pair,
        missing_token="MANIFEST_MISSING",
        corrupt_token="MANIFEST_CORRUPT",
        address_token="MANIFEST_CONTENT_ADDRESS_MISMATCH",
        owner_bindings=owner_bindings,
    )
    if (
        manifest.producing_external_capacity_identity,
        manifest.producing_external_capacity_digest,
    ) != (capacity.artifact_identity, capacity.artifact_digest):
        _fail("MANIFEST_PRODUCING_CAPACITY_MISMATCH", manifest_pair[0])
    target_pair = _require_content_pair(
        manifest.target_v5_identity,
        manifest.target_v5_digest,
        prefix=TARGET_V5_IDENTITY_PREFIX,
        token="TARGET_V5_PAIR_MISMATCH",
        detail="manifest TargetV5 pair",
    )
    if (capacity.target_identity, capacity.target_digest) != target_pair:
        _fail("CAPACITY_TARGET_V5_MISMATCH", capacity.artifact_identity)
    if (decision.target_identity, decision.target_digest) != target_pair:
        _fail("HUMAN_DECISION_TARGET_V5_MISMATCH", decision.artifact_identity)
    target = _read_authoritative_immutable(
        store,
        ConstitutionalMetaRepairInitialAdoptionTargetV5,
        target_pair,
        missing_token="TARGET_V5_MISSING",
        corrupt_token="TARGET_V5_CORRUPT",
        address_token="TARGET_V5_CONTENT_ADDRESS_MISMATCH",
        owner_bindings=owner_bindings,
    )
    if target.root_binding_mode != TARGET_V5_ROOT_BINDING_MODE:
        _fail("TARGET_V5_ROOT_BINDING_MODE_MISMATCH", target.target_identity)
    _validate_initial_begin(composition)
    authoritative_pointer = _require_content_pair(
        target.founding_event_origin_root_pointer_identity,
        target.founding_event_origin_root_pointer_digest,
        prefix=None,
        token="AUTHORITATIVE_P_ROOT_INVALID",
        detail="TargetV5 founding origin pointer",
    )
    authoritative_root = (
        target.founding_event_origin_root_identity,
        target.founding_event_origin_root_digest,
        target.founding_event_origin_root_generation,
    )
    supplied_roots = (
        (
            composition.proof_set.current_root_identity,
            composition.proof_set.current_root_digest,
            composition.proof_set.current_root_generation,
        ),
        (
            composition.certification.current_root_identity,
            composition.certification.current_root_digest,
            composition.certification.current_root_generation,
        ),
        (
            composition.transition.predecessor_root_identity,
            composition.transition.predecessor_root_digest,
            composition.transition.predecessor_root_generation,
        ),
        (
            composition.resulting_root.predecessor_snapshot_root_identity,
            composition.resulting_root.predecessor_snapshot_root_digest,
            composition.resulting_root.predecessor_root_generation,
        ),
    )
    if any(root != authoritative_root for root in supplied_roots):
        _fail("AUTHORITATIVE_ORIGIN_ROOT_MISMATCH", target.target_identity)
    pointer_bindings = (
        (
            "PROOF_SET_AUTHORITATIVE_P_ROOT_MISMATCH",
            composition.proof_set.current_root_pointer_identity,
            composition.proof_set.current_root_pointer_digest,
        ),
        (
            "CERTIFICATION_AUTHORITATIVE_P_ROOT_MISMATCH",
            composition.certification.current_root_pointer_identity,
            composition.certification.current_root_pointer_digest,
        ),
        (
            "TRANSITION_AUTHORITATIVE_P_ROOT_MISMATCH",
            composition.transition.predecessor_root_pointer_identity,
            composition.transition.predecessor_root_pointer_digest,
        ),
        (
            "TERMINAL_COMMITMENT_AUTHORITATIVE_P_ROOT_MISMATCH",
            composition.terminal_root_commitment.predecessor_snapshot_pointer_identity,
            composition.terminal_root_commitment.predecessor_snapshot_pointer_digest,
        ),
        (
            "RESULTING_ROOT_AUTHORITATIVE_P_ROOT_MISMATCH",
            composition.resulting_root.predecessor_snapshot_pointer_identity,
            composition.resulting_root.predecessor_snapshot_pointer_digest,
        ),
    )
    for token, identity, digest in pointer_bindings:
        if (identity, digest) != authoritative_pointer:
            _fail(token, target.target_identity)
    return authoritative_pointer, authoritative_root


def _forward_dag(
    predecessor_root: ConstitutionalRootEvolutionSnapshotV4,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    authentication: FixtureAuthenticationExecution,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    composition: FixtureForwardComposition,
    owner_bindings: dict[str, str],
) -> tuple[IdentityDAGNode, ...]:
    result = authentication.result
    c = composition
    ref = lambda evidence: _reference(evidence, owner_bindings)
    return (
        IdentityDAGNode(predecessor_root),
        IdentityDAGNode(capacity),
        IdentityDAGNode(result, (ref(capacity),)),
        IdentityDAGNode(decision, (ref(capacity), ref(result))),
        IdentityDAGNode(c.proof_set, (ref(decision),)),
        IdentityDAGNode(c.certification, (ref(c.proof_set),)),
        IdentityDAGNode(c.transition, (ref(c.proof_set), ref(c.certification))),
        IdentityDAGNode(c.ordinary_chain_census),
        IdentityDAGNode(c.cap_reachability_state, (ref(c.ordinary_chain_census),)),
        IdentityDAGNode(
            c.dormancy_guard,
            (ref(c.transition), ref(c.cap_reachability_state)),
        ),
        IdentityDAGNode(
            c.meta_repair_transition,
            (ref(c.transition), ref(c.cap_reachability_state), ref(c.dormancy_guard)),
        ),
        IdentityDAGNode(
            c.meta_repair_state,
            (
                ref(c.transition),
                ref(c.cap_reachability_state),
                ref(c.dormancy_guard),
                ref(c.meta_repair_transition),
            ),
        ),
        IdentityDAGNode(
            c.terminal_root_commitment,
            (
                ref(c.transition),
                ref(c.cap_reachability_state),
                ref(c.dormancy_guard),
                ref(c.meta_repair_state),
            ),
        ),
        IdentityDAGNode(
            c.terminal_coordinator_state,
            (ref(c.terminal_root_commitment),),
        ),
        IdentityDAGNode(
            c.resulting_root,
            (
                ref(predecessor_root),
                ref(c.cap_reachability_state),
                ref(c.meta_repair_state),
                ref(c.terminal_coordinator_state),
            ),
        ),
        IdentityDAGNode(
            c.attempt_terminal_read_back,
            (
                ref(c.transition),
                ref(c.terminal_root_commitment),
                ref(c.terminal_coordinator_state),
                ref(c.resulting_root),
            ),
        ),
    )


def _validate_success_semantics(
    capacity: HumanFounderExternalCapacityEvidenceV2,
    commitment: HumanFounderAuthenticationCommitmentV2,
    authentication: FixtureAuthenticationExecution,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    composition: FixtureForwardComposition,
    owner_bindings: dict[str, str],
) -> None:
    c = composition
    try:
        validate_p012_structural_bindings(
            c.proof_set,
            decision,
            capacity,
            authentication.result,
            commitment,
            owner_bindings=owner_bindings,
        )
    except CandidateValidationError as exc:
        _fail("INVALID_P012_PREDECESSOR", str(exc))
    exact_values = (
        (c.proof_set.proof_result, "ELIGIBLE", "proof result"),
        (c.certification.certification_result, "ELIGIBLE", "certification result"),
        (c.transition.begin_transition_mode, "BEGIN_REQUIRED_EXACTLY_ONCE", "transition mode"),
        (c.transition.reserved_successor_meta_repair_status, "DORMANT", "transition meta status"),
        (
            c.transition.reserved_successor_cap_status,
            "ACTIVE_SOLE_NORMAL_AMENDMENT_LIFECYCLE",
            "transition CAP status",
        ),
        (c.transition.reserved_dormancy_status, "CONSUMED_DORMANT_ON_SUCCESS", "transition dormancy"),
        (c.dormancy_guard.one_shot_lifecycle_predecessor_status, "CONSUMING", "guard predecessor"),
        (c.dormancy_guard.one_shot_lifecycle_terminal_status, "CONSUMED_DORMANT", "guard terminal"),
        (c.dormancy_guard.reserved_successor_meta_repair_status, "DORMANT", "guard meta status"),
        (
            c.dormancy_guard.terminal_commitment_contract_identity,
            "CONSTITUTIONAL_TERMINAL_ROOT_SEMANTIC_IMAGE_COMMITMENT_V3",
            "guard commitment contract",
        ),
        (c.dormancy_guard.terminal_commitment_contract_version, "V3", "guard commitment version"),
        (
            c.dormancy_guard.terminal_eligibility_rule,
            "EXACT_CURRENT_CONSUMING_EVENT_ATTEMPT_R1_TOKEN_MATCH",
            "guard eligibility",
        ),
        (
            c.meta_repair_transition.transition_kind,
            "ADMIT_ONE_SHOT_FOUNDING_DORMANCY_REBASE_V3",
            "meta transition kind",
        ),
        (c.meta_repair_transition.reserved_successor_status, "DORMANT", "meta transition status"),
        (
            c.meta_repair_transition.authorizing_artifact_type,
            "CandidateHOneShotDormancyRebaseGuard",
            "meta authorizer type",
        ),
        (c.meta_repair_transition.authorizing_artifact_version, "V2", "meta authorizer version"),
        (c.meta_repair_state.state_status, "DORMANT", "meta state"),
        (
            c.terminal_root_commitment.expected_terminal_result,
            "CONSUMED",
            "terminal commitment result",
        ),
        (c.terminal_coordinator_state.coordinator_status, "CONSUMED", "coordinator status"),
        (c.terminal_coordinator_state.terminal_result, "CONSUMED", "coordinator result"),
        (c.attempt_terminal_read_back.terminal_result, "CONSUMED", "terminal read-back result"),
    )
    for actual, expected, detail in exact_values:
        _require_equal(actual, expected, detail)
    for model, detail in (
        (c.terminal_root_commitment, "terminal commitment failure"),
        (c.terminal_coordinator_state, "coordinator failure"),
        (c.attempt_terminal_read_back, "terminal read-back failure"),
    ):
        _require_equal(
            (model.terminal_failure_evidence_identity, model.terminal_failure_evidence_digest),
            (None, None),
            detail,
        )
    _require_equal(c.attempt_terminal_read_back.next_attempt_sequence, None, "terminal retry")
    _require_equal(
        (
            c.attempt_terminal_read_back.resulting_root_identity,
            c.attempt_terminal_read_back.resulting_root_digest,
            c.attempt_terminal_read_back.resulting_root_generation,
        ),
        (c.resulting_root.root_identity, c.resulting_root.root_digest, c.resulting_root.root_generation),
        "terminal/resulting root",
    )
    _require_equal(
        (
            c.attempt_terminal_read_back.read_back_current_root_identity,
            c.attempt_terminal_read_back.read_back_current_root_digest,
            c.attempt_terminal_read_back.read_back_current_root_generation,
        ),
        (c.resulting_root.root_identity, c.resulting_root.root_digest, c.resulting_root.root_generation),
        "terminal/current root",
    )


def _validate_retained_root(
    store: CandidateHStore,
    composition: FixtureForwardComposition,
    owner_bindings: dict[str, str],
    authoritative_pointer: tuple[str, str],
    authoritative_root: tuple[str, str, int],
) -> ConstitutionalRootEvolutionSnapshotV4:
    c = composition
    predecessor = c.retained_root_predecessor
    if not isinstance(predecessor, SlotReadBack):
        _fail("RETAINED_ROOT_STATE_HISTORY_MISMATCH", "SlotReadBack")
    if predecessor.owner != ROOT_OWNER:
        _fail("RETAINED_ROOT_OWNER_MISMATCH", predecessor.owner)
    if predecessor.slot_identity != authoritative_pointer[0]:
        _fail("RETAINED_ROOT_IDENTITY_MISMATCH", predecessor.slot_identity)
    if predecessor.slot_epoch != authoritative_pointer[1]:
        _fail("RETAINED_ROOT_EPOCH_MISMATCH", str(predecessor.slot_epoch))
    try:
        current = store.read_slot(
            ROOT_OWNER,
            authoritative_pointer[0],
            authoritative_pointer[1],
        )
    except CandidatePersistenceError as exc:
        _fail("RETAINED_ROOT_STATE_HISTORY_MISMATCH", exc.code)
    if current != predecessor:
        identical_terminal = (
            current.predecessor_slot_digest == predecessor.slot_digest
            and current.predecessor_status == predecessor.current_status
            and current.current_status == predecessor.current_status
            and current.artifact_identity == c.resulting_root.root_identity
            and current.artifact_digest == c.resulting_root.root_digest
            and current.logical_instant == c.resulting_root.effective_logical_instant
        )
        if not identical_terminal:
            _fail("RETAINED_ROOT_STATE_HISTORY_MISMATCH", current.artifact_identity)
    try:
        predecessor_root, _ = store.read_immutable(
            ConstitutionalRootEvolutionSnapshotV4,
            ArtifactAddress(predecessor.artifact_identity, predecessor.artifact_digest),
            owner_bindings=owner_bindings,
        )
    except CandidatePersistenceError as exc:
        _fail("RETAINED_ROOT_STATE_HISTORY_MISMATCH", exc.code)
    persisted_root = (
        predecessor_root.root_identity,
        predecessor_root.root_digest,
        predecessor_root.root_generation,
    )
    retained_checks = (
        (persisted_root, authoritative_root),
        (
            (
                c.resulting_root.predecessor_snapshot_root_identity,
                c.resulting_root.predecessor_snapshot_root_digest,
                c.resulting_root.predecessor_root_generation,
            ),
            persisted_root,
        ),
        (c.resulting_root.root_generation, predecessor_root.root_generation + 1),
        (
            (
                c.proof_set.current_root_identity,
                c.proof_set.current_root_digest,
                c.proof_set.current_root_generation,
            ),
            persisted_root,
        ),
        (
            (
                c.certification.current_root_identity,
                c.certification.current_root_digest,
                c.certification.current_root_generation,
            ),
            persisted_root,
        ),
        (
            (
                c.transition.predecessor_root_identity,
                c.transition.predecessor_root_digest,
                c.transition.predecessor_root_generation,
            ),
            persisted_root,
        ),
    )
    if any(actual != expected for actual, expected in retained_checks):
        _fail("RETAINED_ROOT_STATE_HISTORY_MISMATCH", predecessor.artifact_identity)
    return predecessor_root


def orchestrate_fixture_candidate_h(
    store: CandidateHStore,
    *,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    authentication_commitment: HumanFounderAuthenticationCommitmentV2,
    authentication: FixtureAuthenticationExecution,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    composition: FixtureForwardComposition | None,
) -> FixtureOrchestrationExecution:
    """Compose one supplied fixture chain, or return its refusal terminal."""

    if not isinstance(store, CandidateHStore):
        _fail("EXISTING_STORE_REQUIRED", "CandidateHStore")
    if not isinstance(capacity, HumanFounderExternalCapacityEvidenceV2):
        _fail("MISSING_CAPACITY_PREDECESSOR", type(capacity).__name__)
    if not isinstance(authentication_commitment, HumanFounderAuthenticationCommitmentV2):
        _fail("MISSING_COMMITMENT_PREDECESSOR", type(authentication_commitment).__name__)
    if not isinstance(decision, ExternalConstituentHumanFirstAdoptionDecisionV2):
        _fail("MISSING_HUMAN_DECISION", type(decision).__name__)
    owner_bindings = {
        "RESOLVED_EXTERNAL_PREMISE_AUTHORITY": capacity.producing_owner,
        "CAPACITY_PRODUCING_OWNER": capacity.producing_owner,
    }
    _validate_authentication_predecessor(
        store,
        capacity,
        authentication_commitment,
        authentication,
        decision,
        owner_bindings,
    )
    result = authentication.result
    if (
        result.authentication_result != "AUTHENTICATED_VALID"
        or result.terminal_authentication_slot_status != "AUTHENTICATED_FINAL"
        or result.signature_verification_result != "TRUE"
        or result.conflict_status != "NONE"
    ):
        _fail("INDETERMINATE_AUTHENTICATION_TERMINAL", result.authentication_result)
    if decision.decision == "REFUSE_EXACT_TARGET":
        if composition is not None:
            _fail("REFUSAL_FORBIDS_FORWARD_COMPOSITION", type(composition).__name__)
        return FixtureOrchestrationExecution(
            outcome="REFUSED_FINAL_EXHAUSTED",
            authentication_result_identity=result.artifact_identity,
            decision_identity=decision.artifact_identity,
            identity_dag=None,
            immutable_writes=(),
            retained_root_cas=None,
            terminal_write=None,
            fixture_effects_applied=0,
            production_effects_applied=0,
            originating_human_authorities=0,
            originating_constituent_authorities=0,
            human_entry_points=1,
            retained_roots=1,
            persistent_founder_authorities=0,
            fixture_authority_permanently_exhausted=True,
        )
    if decision.decision != "ADOPT_EXACT_TARGET":
        _fail("UNKNOWN_HUMAN_DISPOSITION", str(decision.decision))
    if not isinstance(composition, FixtureForwardComposition):
        _fail("MISSING_FORWARD_PREDECESSOR", "FixtureForwardComposition")
    authoritative_pointer, authoritative_root = _validate_authoritative_predecessors(
        store,
        capacity,
        authentication_commitment,
        decision,
        composition,
        owner_bindings,
    )
    predecessor_root = _validate_retained_root(
        store,
        composition,
        owner_bindings,
        authoritative_pointer,
        authoritative_root,
    )
    _validate_success_semantics(
        capacity,
        authentication_commitment,
        authentication,
        decision,
        composition,
        owner_bindings,
    )
    nodes = _forward_dag(
        predecessor_root,
        capacity,
        authentication,
        decision,
        composition,
        owner_bindings,
    )
    try:
        dag = validate_identity_dag(nodes, owner_bindings=owner_bindings)
    except CandidateValidationError as exc:
        _fail("INVALID_FORWARD_IDENTITY_DAG", str(exc))
    ordered_models = (
        decision,
        composition.proof_set,
        composition.certification,
        composition.transition,
        composition.ordinary_chain_census,
        composition.cap_reachability_state,
        composition.dormancy_guard,
        composition.meta_repair_transition,
        composition.meta_repair_state,
        composition.terminal_root_commitment,
        composition.terminal_coordinator_state,
    )
    writes = tuple(
        store.write_immutable(model, owner_bindings=owner_bindings)
        for model in ordered_models
    )
    predecessor = composition.retained_root_predecessor
    root_cas = store.compare_and_swap(
        owner=ROOT_OWNER,
        slot_identity=authoritative_pointer[0],
        slot_epoch=authoritative_pointer[1],
        expected_slot_digest=predecessor.slot_digest,
        expected_status=predecessor.current_status,
        successor_status=predecessor.current_status,
        model=composition.resulting_root,
        logical_instant=composition.resulting_root.effective_logical_instant,
        owner_bindings=owner_bindings,
    )
    if root_cas.outcome == "CONFLICT":
        _fail("FIXTURE_AUTHORITY_EXHAUSTED", root_cas.read_back.artifact_identity)
    if root_cas.outcome not in {"WON", "IDEMPOTENT"}:
        _fail("RETAINED_ROOT_CAS_FAILED", root_cas.outcome)
    current = root_cas.read_back
    _require_equal(
        (current.artifact_identity, current.artifact_digest),
        (composition.resulting_root.root_identity, composition.resulting_root.root_digest),
        "root CAS read-back",
    )
    terminal_write = store.write_immutable(
        composition.attempt_terminal_read_back,
        owner_bindings=owner_bindings,
    )
    return FixtureOrchestrationExecution(
        outcome=(
            "FIXTURE_EFFECT_CONSUMED"
            if root_cas.outcome == "WON"
            else "IDENTICAL_EXHAUSTED_OBSERVATION"
        ),
        authentication_result_identity=result.artifact_identity,
        decision_identity=decision.artifact_identity,
        identity_dag=dag,
        immutable_writes=writes,
        retained_root_cas=root_cas,
        terminal_write=terminal_write,
        fixture_effects_applied=1 if root_cas.outcome == "WON" else 0,
        production_effects_applied=0,
        originating_human_authorities=0,
        originating_constituent_authorities=0,
        human_entry_points=1,
        retained_roots=1,
        persistent_founder_authorities=0,
        fixture_authority_permanently_exhausted=True,
    )


__all__ = [
    "CandidateOrchestrationError",
    "FixtureForwardComposition",
    "FixtureOrchestrationExecution",
    "ROOT_OWNER",
    "orchestrate_fixture_candidate_h",
]
