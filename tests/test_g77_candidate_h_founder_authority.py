from __future__ import annotations

import base64
import inspect
from dataclasses import fields, replace
from pathlib import Path

import pytest

from aigol.runtime.candidate_h_founder.authentication import (
    FixtureAuthenticationContext,
    authenticate_fixture_candidate_h,
    fixture_ed25519_public_key,
)
from aigol.runtime.candidate_h_founder.cj1 import cj1_digest, cj1_identity, sha256_hex
from aigol.runtime.candidate_h_founder.models import MODEL_REGISTRY
from aigol.runtime.candidate_h_founder.orchestration import (
    ROOT_OWNER,
    CandidateOrchestrationError,
    FixtureForwardComposition,
    orchestrate_fixture_candidate_h,
)
from aigol.runtime.candidate_h_founder.persistence import CandidateHStore
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    NESTED_RECORD_CONSTANTS,
    PREDICATE_CODES,
    PREDICATE_ROW_FIELDS,
    expected_artifact_identifiers,
)


OWNER = "fixture:external-premise-authority"
OWNER_BINDINGS = {"RESOLVED_EXTERNAL_PREMISE_AUTHORITY": OWNER}
SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
PUBLIC_KEY = fixture_ed25519_public_key(SEED)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _hash_pair(prefix: str, label: str) -> tuple[str, str]:
    suffix = sha256_hex(label.encode())
    return f"{prefix}:{suffix}", f"sha256:{suffix}"


def _values(model_type: type, **changes: object) -> dict[str, object]:
    values = {field.name: f"fixture:{field.name}" for field in fields(model_type)}
    values.update(model_type.CONSTANTS)
    for name, allowed in model_type.ALLOWED_VALUES.items():
        values[name] = sorted(allowed, key=repr)[0]
    for name in model_type.REQUIRED_NULL_FIELDS:
        values[name] = None
    if "producing_owner" in values:
        rule = getattr(model_type, "OWNER_RULE", None)
        fixed = {
            "HUMAN_AUTHORITY",
            "CONSTITUTIONAL_CERTIFICATION_OWNER",
            "CONSTITUTIONAL_GOVERNANCE_OWNER",
            ROOT_OWNER,
        }
        values["producing_owner"] = rule if rule in fixed else OWNER
    values.update(changes)
    return values


def _nested(class_name: str, **changes: object):
    model_type = MODEL_REGISTRY[class_name]
    values = _values(model_type)
    values.update(NESTED_RECORD_CONSTANTS[class_name])
    values.update(changes)
    values["record_digest"] = "sha256:pending"
    pending = model_type(**values)
    payload = pending.to_cj1_object()
    payload.pop("record_digest")
    return replace(pending, record_digest=cj1_digest(payload))


def _with_identity(model):
    idempotency, identity, digest = expected_artifact_identifiers(model)
    spec = ARTIFACT_IDENTITY_SPECS[type(model)]
    return replace(
        model,
        idempotency_identity=idempotency,
        **{spec.identity_field: identity, spec.digest_field: digest},
    )


def _model(class_name: str, **changes: object):
    model_type = MODEL_REGISTRY[class_name]
    return _with_identity(model_type(**_values(model_type, **changes)))


def _capacity():
    premise = _hash_pair("external-premise-v1", "premise")
    target = _hash_pair("founding-target-v5", "target")
    external_capacity = _hash_pair("human-founder-capacity-v1", "capacity")
    actor = "fixture:human-actor"
    issued_at = "fixture:capacity-issued"
    key_identity = f"human-founder-ed25519-key-v1:{sha256_hex(PUBLIC_KEY)}"
    records = {
        "human_actor_identity_record": _nested(
            "HumanFounderActorIdentityRecordV1", human_actor_identity=actor
        ),
        "external_capacity_record": _nested(
            "HumanFounderExternalCapacityRecordV1",
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
            human_actor_identity=actor,
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            external_constituent_model_identity="HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1",
            target_identity=target[0],
            target_digest=target[1],
            issued_at=issued_at,
        ),
        "authority_provenance_record": _nested(
            "HumanFounderAuthorityProvenanceRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
        ),
        "authority_competence_record": _nested(
            "HumanFounderAuthorityCompetenceRecordV1",
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
            target_identity=target[0],
            target_digest=target[1],
        ),
        "one_shot_scope_record": _nested(
            "HumanFounderOneShotScopeRecordV1",
            target_identity=target[0],
            target_digest=target[1],
        ),
        "authentication_key_binding_record": _nested(
            "HumanFounderAuthenticationKeyBindingRecordV1",
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
            authentication_public_key=_b64(PUBLIC_KEY),
            authentication_key_identity=key_identity,
        ),
        "authentication_verification_profile": _nested(
            "HumanFounderAuthenticationVerificationProfileV1"
        ),
        "capacity_status_read_back_record": _nested(
            "HumanFounderCapacityStatusReadBackRecordV1",
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
        ),
        "capacity_issuance_authentication_record": _nested(
            "HumanFounderCapacityIssuanceAuthenticationRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            capacity_issuer_identity=OWNER,
            capacity_issuer_public_key=_b64(PUBLIC_KEY),
            capacity_issuer_key_identity=key_identity,
            issued_at=issued_at,
        ),
        "capacity_issuance_custody_read_back_record": _nested(
            "HumanFounderCapacityIssuanceCustodyReadBackRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
        ),
    }
    return _model(
        "HumanFounderExternalCapacityEvidenceV2",
        external_premise_identity=premise[0],
        external_premise_digest=premise[1],
        target_identity=target[0],
        target_digest=target[1],
        human_authentication_slot_identity="fixture:authentication-slot",
        human_authentication_epoch=1,
        issued_at=issued_at,
        **records,
    )


def _commitment():
    model_type = MODEL_REGISTRY["HumanFounderAuthenticationCommitmentV2"]
    return model_type(
        **_values(
            model_type,
            candidate_common_base_digest=f"sha256:{sha256_hex(b'one')}",
        )
    )


def _authentication(tmp_path: Path, *, private_seed: bytes | None = SEED):
    capacity = _capacity()
    commitment = _commitment()
    store = CandidateHStore(tmp_path / "store")
    authentication_open = store.compare_and_swap(
        owner=OWNER,
        slot_identity=capacity.human_authentication_slot_identity,
        slot_epoch=capacity.human_authentication_epoch,
        expected_slot_digest=None,
        expected_status=None,
        successor_status="OPEN",
        model=capacity,
        logical_instant="fixture:authentication-open",
        owner_bindings=OWNER_BINDINGS,
    ).read_back
    signer_available = store.compare_and_swap(
        owner=OWNER,
        slot_identity="fixture:signer-operation-slot",
        slot_epoch=1,
        expected_slot_digest=None,
        expected_status=None,
        successor_status="AVAILABLE",
        model=capacity,
        logical_instant="fixture:signer-available",
        owner_bindings=OWNER_BINDINGS,
    ).read_back
    claim = _hash_pair("external-claim-token-v1", "claim")
    proof = _hash_pair("external-one-use-proof-v1", "proof")
    context = FixtureAuthenticationContext(
        capacity=capacity,
        authentication_commitment=commitment,
        authentication_open_read_back=authentication_open,
        signer_available_read_back=signer_available,
        fixture_public_key=PUBLIC_KEY,
        fixture_private_seed=private_seed,
        one_use_claim_token_identity=claim[0],
        one_use_claim_token_digest=claim[1],
        one_use_non_equivocation_proof_identity=proof[0],
        one_use_non_equivocation_proof_digest=proof[1],
        claim_logical_instant="fixture:claim",
        acceptance_logical_instant="fixture:acceptance",
        completion_logical_instant="fixture:completion",
    )
    return store, capacity, commitment, authenticate_fixture_candidate_h(store, context)


def _decision(capacity, commitment, execution, *, disposition="ADOPT_EXACT_TARGET"):
    result = execution.result
    payload = commitment.to_cj1_object()
    pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", payload),
        cj1_digest(payload),
    )
    return _model(
        "ExternalConstituentHumanFirstAdoptionDecisionV2",
        human_founder_external_capacity_evidence_identity=capacity.artifact_identity,
        human_founder_external_capacity_evidence_digest=capacity.artifact_digest,
        authentication_commitment_identity=pair[0],
        authentication_commitment_digest=pair[1],
        authentication_result_read_back_identity=result.artifact_identity,
        authentication_result_read_back_digest=result.artifact_digest,
        human_signature_scheme=result.signature_scheme,
        human_signature_key_identity=result.signature_key_identity,
        human_signature=result.signature,
        decision=disposition,
    )


def _proof_set(decision, commitment, predecessor_root):
    rows = []
    for rank, code in enumerate(PREDICATE_CODES, start=1):
        row = dict.fromkeys(PREDICATE_ROW_FIELDS, "fixture")
        row.update(
            rank=rank,
            predicate_code=code,
            subject_artifact_type="fixture:subject-type",
            subject_artifact_version="V1",
            subject_identity=f"fixture:subject:{rank}",
            subject_digest=f"sha256:subject:{rank}",
            expected_digest=f"sha256:expected:{rank}",
            observed_digest=f"sha256:observed:{rank}",
            result="TRUE",
        )
        rows.append(row)
    rows[11].update(
        subject_artifact_type="ExternalConstituentHumanFirstAdoptionDecisionV2",
        subject_artifact_version="V2",
        subject_identity=decision.artifact_identity,
        subject_digest=decision.artifact_digest,
        expected_digest=decision.authentication_commitment_digest,
        observed_digest=cj1_digest(commitment.to_cj1_object()),
    )
    return _model(
        "ExternalConstituentFoundingEligibilityProofSetV3",
        human_decision_identity=decision.artifact_identity,
        human_decision_digest=decision.artifact_digest,
        ordered_predicate_results=rows,
        predicate_root=cj1_digest(rows),
        proof_result="ELIGIBLE",
        attempt_kind="INITIAL_BEGIN",
        attempt_sequence=1,
        predecessor_attempt_identity=None,
        predecessor_attempt_terminal_read_back_identity=None,
        predecessor_attempt_terminal_read_back_digest=None,
        predecessor_abandoned_commitment_identity=None,
        predecessor_abandoned_commitment_digest=None,
        consuming_disposition_identity=None,
        consuming_disposition_digest=None,
        current_root_identity=predecessor_root.root_identity,
        current_root_digest=predecessor_root.root_digest,
        current_root_generation=predecessor_root.root_generation,
    )


def build_fixture(tmp_path: Path):
    store, capacity, commitment, execution = _authentication(tmp_path)
    decision = _decision(capacity, commitment, execution)
    predecessor_root = _model(
        "ConstitutionalRootEvolutionSnapshotV4",
        predecessor_root_generation=0,
        root_generation=1,
        normative_registry_entry_count=1,
        source_evidence_registry_epoch=1,
        effective_logical_instant="fixture:root-one",
    )
    retained = store.compare_and_swap(
        owner=ROOT_OWNER,
        slot_identity="fixture:retained-root",
        slot_epoch=1,
        expected_slot_digest=None,
        expected_status=None,
        successor_status="CURRENT",
        model=predecessor_root,
        logical_instant=predecessor_root.effective_logical_instant,
    ).read_back
    proof_set = _proof_set(decision, commitment, predecessor_root)
    certification = _model(
        "ExternalConstituentFoundingEligibilityCertificationV3",
        proof_set_identity=proof_set.proof_set_identity,
        proof_set_digest=proof_set.proof_set_digest,
        current_root_identity=predecessor_root.root_identity,
        current_root_digest=predecessor_root.root_digest,
        current_root_generation=predecessor_root.root_generation,
        certification_result="ELIGIBLE",
    )
    transition = _model(
        "ExternalConstituentFoundingAdoptionTransitionV3",
        proof_set_identity=proof_set.proof_set_identity,
        proof_set_digest=proof_set.proof_set_digest,
        certification_identity=certification.certification_identity,
        certification_digest=certification.certification_digest,
        human_decision_identity=decision.artifact_identity,
        human_decision_digest=decision.artifact_digest,
        predecessor_root_identity=predecessor_root.root_identity,
        predecessor_root_digest=predecessor_root.root_digest,
        predecessor_root_generation=predecessor_root.root_generation,
        reserved_successor_root_generation=2,
        reserved_successor_meta_repair_status="DORMANT",
        reserved_successor_cap_status="ACTIVE_SOLE_NORMAL_AMENDMENT_LIFECYCLE",
        reserved_dormancy_status="CONSUMED_DORMANT_ON_SUCCESS",
        begin_transition_mode="BEGIN_REQUIRED_EXACTLY_ONCE",
        root_effect_owner=ROOT_OWNER,
    )
    census = _model(
        "ConstitutionalExistingOrdinaryRepairChainCensusV2",
        ordered_route_entry_count=0,
        applicable_route_count=0,
        g70_chain_result_count=0,
        alternative_constituent_route_count=0,
    )
    cap = _model(
        "OrdinaryCAPReachabilityStateV2",
        ordinary_chain_census_identity=census.ordinary_chain_census_identity,
        ordinary_chain_census_digest=census.ordinary_chain_census_digest,
        reachability_epoch=1,
    )
    guard = _model(
        "CandidateHOneShotDormancyRebaseGuardV2",
        candidate_h_founding_transition_identity=transition.transition_identity,
        candidate_h_founding_transition_digest=transition.transition_digest,
        successor_cap_state_identity=cap.reachability_state_identity,
        successor_cap_state_digest=cap.reachability_state_digest,
        one_shot_lifecycle_predecessor_status="CONSUMING",
        one_shot_lifecycle_terminal_status="CONSUMED_DORMANT",
        reserved_successor_meta_repair_status="DORMANT",
        terminal_commitment_contract_identity="CONSTITUTIONAL_TERMINAL_ROOT_SEMANTIC_IMAGE_COMMITMENT_V3",
        terminal_commitment_contract_version="V3",
        terminal_eligibility_rule="EXACT_CURRENT_CONSUMING_EVENT_ATTEMPT_R1_TOKEN_MATCH",
        attempt_sequence=1,
        expected_consuming_slot_generation=1,
        allocation_root_generation=1,
        token_ordinal=1,
    )
    meta_transition = _model(
        "ConstitutionalMetaRepairTransitionV3",
        transition_kind="ADMIT_ONE_SHOT_FOUNDING_DORMANCY_REBASE_V3",
        reserved_successor_status="DORMANT",
        cap_reachability_state_identity=cap.reachability_state_identity,
        cap_reachability_state_digest=cap.reachability_state_digest,
        authorizing_artifact_type="CandidateHOneShotDormancyRebaseGuard",
        authorizing_artifact_version="V2",
        authorizing_artifact_identity=guard.guard_identity,
        authorizing_artifact_digest=guard.guard_digest,
        candidate_h_founding_transition_identity=transition.transition_identity,
        candidate_h_founding_transition_digest=transition.transition_digest,
        attempt_sequence=1,
        reachability_epoch=1,
    )
    meta_state = _model(
        "ConstitutionalMetaRepairStateV3",
        state_status="DORMANT",
        repair_epoch=1,
        reachability_epoch=1,
        cap_reachability_state_identity=cap.reachability_state_identity,
        cap_reachability_state_digest=cap.reachability_state_digest,
        transition_identity=meta_transition.meta_repair_transition_identity,
        transition_digest=meta_transition.meta_repair_transition_digest,
        one_shot_dormancy_rebase_guard_identity=guard.guard_identity,
        one_shot_dormancy_rebase_guard_digest=guard.guard_digest,
        candidate_h_founding_transition_identity=transition.transition_identity,
        candidate_h_founding_transition_digest=transition.transition_digest,
        attempt_sequence=1,
    )
    root_commitment = _model(
        "ConstitutionalTerminalRootSemanticImageCommitmentV3",
        candidate_h_founding_transition_identity=transition.transition_identity,
        candidate_h_founding_transition_digest=transition.transition_digest,
        successor_cap_reachability_state_identity=cap.reachability_state_identity,
        successor_cap_reachability_state_digest=cap.reachability_state_digest,
        successor_meta_repair_state_identity=meta_state.meta_repair_state_identity,
        successor_meta_repair_state_digest=meta_state.meta_repair_state_digest,
        one_shot_dormancy_rebase_guard_identity=guard.guard_identity,
        one_shot_dormancy_rebase_guard_digest=guard.guard_digest,
        predecessor_root_generation=1,
        allocation_root_generation=1,
        reserved_terminal_root_generation=2,
        attempt_sequence=1,
        token_ordinal=1,
        successor_normative_registry_entry_count=1,
        successor_source_evidence_registry_epoch=1,
        terminal_failure_evidence_identity=None,
        terminal_failure_evidence_digest=None,
        expected_terminal_result="CONSUMED",
    )
    coordinator = _model(
        "ConstitutionalRootSerializationCoordinatorStateV4",
        terminal_root_commitment_identity=root_commitment.terminal_root_commitment_identity,
        terminal_root_commitment_digest=root_commitment.terminal_root_commitment_digest,
        coordinator_status="CONSUMED",
        token_ordinal=1,
        next_token_ordinal=2,
        allocation_root_generation=1,
        terminal_root_generation=2,
        attempt_sequence=1,
        terminal_result="CONSUMED",
        terminal_failure_evidence_identity=None,
        terminal_failure_evidence_digest=None,
        predecessor_attempt_identity=None,
        predecessor_attempt_terminal_read_back_identity=None,
        predecessor_attempt_terminal_read_back_digest=None,
    )
    resulting_root = _model(
        "ConstitutionalRootEvolutionSnapshotV4",
        predecessor_snapshot_root_identity=predecessor_root.root_identity,
        predecessor_snapshot_root_digest=predecessor_root.root_digest,
        predecessor_root_generation=1,
        root_generation=2,
        meta_repair_state_identity=meta_state.meta_repair_state_identity,
        meta_repair_state_digest=meta_state.meta_repair_state_digest,
        cap_reachability_state_identity=cap.reachability_state_identity,
        cap_reachability_state_digest=cap.reachability_state_digest,
        serialization_coordinator_state_identity=coordinator.coordinator_state_identity,
        serialization_coordinator_state_digest=coordinator.coordinator_state_digest,
        normative_registry_entry_count=1,
        source_evidence_registry_epoch=1,
        effective_logical_instant="fixture:root-two",
    )
    terminal = _model(
        "CandidateHFoundingAttemptTerminalReadBackV1",
        candidate_h_founding_transition_identity=transition.transition_identity,
        candidate_h_founding_transition_digest=transition.transition_digest,
        terminal_root_commitment_identity=root_commitment.terminal_root_commitment_identity,
        terminal_root_commitment_digest=root_commitment.terminal_root_commitment_digest,
        terminal_coordinator_state_identity=coordinator.coordinator_state_identity,
        terminal_coordinator_state_digest=coordinator.coordinator_state_digest,
        resulting_root_identity=resulting_root.root_identity,
        resulting_root_digest=resulting_root.root_digest,
        resulting_root_generation=2,
        read_back_current_root_identity=resulting_root.root_identity,
        read_back_current_root_digest=resulting_root.root_digest,
        read_back_current_root_generation=2,
        attempt_sequence=1,
        predecessor_attempt_identity=None,
        predecessor_attempt_terminal_read_back_identity=None,
        predecessor_attempt_terminal_read_back_digest=None,
        terminal_result="CONSUMED",
        terminal_failure_evidence_identity=None,
        terminal_failure_evidence_digest=None,
        next_attempt_sequence=None,
        next_token_ordinal=2,
    )
    composition = FixtureForwardComposition(
        proof_set,
        certification,
        transition,
        census,
        cap,
        guard,
        meta_transition,
        meta_state,
        root_commitment,
        coordinator,
        resulting_root,
        terminal,
        retained,
    )
    return store, capacity, commitment, execution, decision, composition


def _run(fixture):
    store, capacity, commitment, execution, decision, composition = fixture
    return orchestrate_fixture_candidate_h(
        store,
        capacity=capacity,
        authentication_commitment=commitment,
        authentication=execution,
        decision=decision,
        composition=composition,
    )


def test_forward_fixture_preserves_zero_originating_authority(tmp_path: Path) -> None:
    result = _run(build_fixture(tmp_path))
    assert result.outcome == "FIXTURE_EFFECT_CONSUMED"
    assert result.fixture_effects_applied == 1
    assert result.production_effects_applied == 0
    assert result.originating_human_authorities == 0
    assert result.originating_constituent_authorities == 0
    assert result.persistent_founder_authorities == 0


def test_root_human_entry_and_path_cardinality_remain_singular(tmp_path: Path) -> None:
    result = _run(build_fixture(tmp_path))
    assert result.human_entry_points == 1
    assert result.retained_roots == 1
    assert result.retained_root_cas.read_back.slot_identity == "fixture:retained-root"
    assert result.retained_root_cas.read_back.generation == 2


def test_repository_or_signer_cannot_manufacture_human_choice(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    forged = replace(fixture[4], decision="REFUSE_EXACT_TARGET")
    with pytest.raises(CandidateOrchestrationError, match="INVALID_PREDECESSOR"):
        orchestrate_fixture_candidate_h(
            fixture[0],
            capacity=fixture[1],
            authentication_commitment=fixture[2],
            authentication=fixture[3],
            decision=forged,
            composition=None,
        )


def test_certification_cannot_substitute_human_decision(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    wrong = _model(
        "ExternalConstituentHumanFirstAdoptionDecisionV2",
        decision="ADOPT_EXACT_TARGET",
    )
    with pytest.raises(CandidateOrchestrationError):
        orchestrate_fixture_candidate_h(
            fixture[0],
            capacity=fixture[1],
            authentication_commitment=fixture[2],
            authentication=fixture[3],
            decision=wrong,
            composition=fixture[5],
        )


def test_missing_predecessor_and_root_mismatch_fail_closed(tmp_path: Path) -> None:
    fixture = build_fixture(tmp_path)
    with pytest.raises(CandidateOrchestrationError, match="MISSING_FORWARD_PREDECESSOR"):
        orchestrate_fixture_candidate_h(
            fixture[0],
            capacity=fixture[1],
            authentication_commitment=fixture[2],
            authentication=fixture[3],
            decision=fixture[4],
            composition=None,
        )
    mismatched = replace(
        fixture[5],
        retained_root_predecessor=replace(
            fixture[5].retained_root_predecessor,
            owner="fixture:alternate-root-owner",
        ),
    )
    with pytest.raises(CandidateOrchestrationError, match="RETAINED_ROOT_OWNER_MISMATCH"):
        orchestrate_fixture_candidate_h(
            fixture[0],
            capacity=fixture[1],
            authentication_commitment=fixture[2],
            authentication=fixture[3],
            decision=fixture[4],
            composition=mismatched,
        )


def test_refusal_is_terminal_without_forward_effect(tmp_path: Path) -> None:
    store, capacity, commitment, execution, _, _ = build_fixture(tmp_path)
    refusal = _decision(capacity, commitment, execution, disposition="REFUSE_EXACT_TARGET")
    result = orchestrate_fixture_candidate_h(
        store,
        capacity=capacity,
        authentication_commitment=commitment,
        authentication=execution,
        decision=refusal,
        composition=None,
    )
    assert result.outcome == "REFUSED_FINAL_EXHAUSTED"
    assert result.fixture_effects_applied == 0
    assert result.fixture_authority_permanently_exhausted is True


def test_indeterminate_authentication_cannot_continue(tmp_path: Path) -> None:
    store, capacity, commitment, execution = _authentication(tmp_path, private_seed=None)
    decision = _decision(capacity, commitment, execution)
    with pytest.raises(CandidateOrchestrationError, match="INDETERMINATE_AUTHENTICATION_TERMINAL"):
        orchestrate_fixture_candidate_h(
            store,
            capacity=capacity,
            authentication_commitment=commitment,
            authentication=execution,
            decision=decision,
            composition=None,
        )


def test_orchestration_exports_no_begin_activation_or_deployment_entry() -> None:
    public = set(__import__("aigol.runtime.candidate_h_founder.orchestration", fromlist=["__all__"]).__all__)
    assert not public & {"begin", "activate", "deploy", "sign", "authenticate", "replay"}
    signature = inspect.signature(orchestrate_fixture_candidate_h)
    assert "store" in signature.parameters
    assert "decision" in signature.parameters
    assert "root_factory" not in signature.parameters
    assert "human_choice" not in signature.parameters
