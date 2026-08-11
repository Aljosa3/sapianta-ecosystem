from __future__ import annotations

import base64
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
from pathlib import Path

import pytest

from aigol.runtime.candidate_h_founder import authentication
from aigol.runtime.candidate_h_founder.authentication import (
    CandidateAuthenticationError,
    FixtureAuthenticationContext,
    authenticate_fixture_candidate_h,
    fixture_ed25519_public_key,
    fixture_ed25519_verify,
)
from aigol.runtime.candidate_h_founder.cj1 import (
    cj1_decode,
    cj1_digest,
    sha256_hex,
)
from aigol.runtime.candidate_h_founder.models import MODEL_REGISTRY
from aigol.runtime.candidate_h_founder.persistence import (
    CandidateHStore,
    CandidatePersistenceError,
    InjectedPersistenceCrash,
    SubcontractAddress,
    SUBCONTRACT_KIND_SPECS,
)
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    NESTED_RECORD_CONSTANTS,
    expected_artifact_identifiers,
    validate_artifact,
)


OWNER = "fixture:external-premise-authority"
OWNER_BINDINGS = {"RESOLVED_EXTERNAL_PREMISE_AUTHORITY": OWNER}
SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
PUBLIC_KEY = fixture_ed25519_public_key(SEED)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _hash_pair(prefix: str, label: str) -> tuple[str, str]:
    suffix = sha256_hex(label.encode("utf-8"))
    return f"{prefix}:{suffix}", f"sha256:{suffix}"


def _values(model_type: type, **changes: object) -> dict[str, object]:
    values = {field.name: f"fixture:{field.name}" for field in fields(model_type)}
    values.update(model_type.CONSTANTS)
    for name, allowed in model_type.ALLOWED_VALUES.items():
        values[name] = sorted(allowed, key=repr)[0]
    for name in model_type.REQUIRED_NULL_FIELDS:
        values[name] = None
    if "producing_owner" in values:
        values["producing_owner"] = OWNER
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
    model_type = MODEL_REGISTRY["HumanFounderExternalCapacityEvidenceV2"]
    model = model_type(
        **_values(
            model_type,
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            target_identity=target[0],
            target_digest=target[1],
            human_authentication_slot_identity="fixture:authentication-slot",
            human_authentication_epoch=1,
            issued_at=issued_at,
            **records,
        )
    )
    return _with_identity(model)


def _commitment(label: str = "one"):
    model_type = MODEL_REGISTRY["HumanFounderAuthenticationCommitmentV2"]
    return model_type(
        **_values(
            model_type,
            candidate_common_base_digest=f"sha256:{sha256_hex(label.encode())}",
        )
    )


def _seed_context(
    tmp_path: Path,
    *,
    private_seed: bytes | None = SEED,
    commitment_label: str = "one",
) -> tuple[CandidateHStore, FixtureAuthenticationContext]:
    capacity = _capacity()
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
    claim_token = _hash_pair("external-claim-token-v1", "claim-token")
    proof = _hash_pair("external-one-use-proof-v1", "one-use-proof")
    context = FixtureAuthenticationContext(
        capacity=capacity,
        authentication_commitment=_commitment(commitment_label),
        authentication_open_read_back=authentication_open,
        signer_available_read_back=signer_available,
        fixture_public_key=PUBLIC_KEY,
        fixture_private_seed=private_seed,
        one_use_claim_token_identity=claim_token[0],
        one_use_claim_token_digest=claim_token[1],
        one_use_non_equivocation_proof_identity=proof[0],
        one_use_non_equivocation_proof_digest=proof[1],
        claim_logical_instant="fixture:claim",
        acceptance_logical_instant="fixture:acceptance",
        completion_logical_instant="fixture:completion",
    )
    return store, context


def _subcontract_bodies(store: CandidateHStore, execution) -> dict[str, dict[str, object]]:
    addresses = {
        "AUTHENTICATION_OPERATION_V1": execution.operation.read_back.address,
        "AUTHENTICATION_CLAIM_CAS_V1": execution.result.authentication_claim_cas_identity,
        "SIGNER_INVOCATION_INTENT_V1": execution.result.signer_invocation_intent_identity,
        "SIGNER_ACCEPTANCE_CAS_V1": execution.result.signer_acceptance_cas_identity,
        "SIGNER_INVOCATION_RECEIPT_V1": execution.result.signer_invocation_receipt_identity,
        "SIGNER_OUTCOME_V1": execution.result.signer_outcome_identity,
        "SIGNER_OUTCOME_READ_BACK_V1": execution.result.signer_outcome_read_back_identity,
        "AUTHENTICATION_TERMINAL_CAS_V1": execution.result.authentication_terminal_cas_identity,
        "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1": execution.result.authoritative_read_back_identity,
    }
    bodies: dict[str, dict[str, object]] = {}
    for kind, raw in addresses.items():
        if hasattr(raw, "identity"):
            address = raw
        else:
            digest_name = {
                "AUTHENTICATION_CLAIM_CAS_V1": execution.result.authentication_claim_cas_digest,
                "SIGNER_INVOCATION_INTENT_V1": execution.result.signer_invocation_intent_digest,
                "SIGNER_ACCEPTANCE_CAS_V1": execution.result.signer_acceptance_cas_digest,
                "SIGNER_INVOCATION_RECEIPT_V1": execution.result.signer_invocation_receipt_digest,
                "SIGNER_OUTCOME_V1": execution.result.signer_outcome_digest,
                "SIGNER_OUTCOME_READ_BACK_V1": execution.result.signer_outcome_read_back_digest,
                "AUTHENTICATION_TERMINAL_CAS_V1": execution.result.authentication_terminal_cas_digest,
                "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1": execution.result.authoritative_read_back_digest,
            }[kind]
            address = SubcontractAddress(kind, raw, digest_name)
        body = cj1_decode(store.read_subcontract(address).canonical_bytes)
        assert isinstance(body, dict)
        bodies[kind] = body
    return bodies


def _filesystem_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def _record_bodies(root: Path) -> list[dict[str, object]]:
    bodies: list[dict[str, object]] = []
    for path in (root / "records").glob("*.cj1"):
        body = cj1_decode(path.read_bytes())
        if isinstance(body, dict):
            bodies.append(body)
    return bodies


def _result_identities(root: Path) -> set[str]:
    return {
        identity
        for body in _record_bodies(root)
        if isinstance((identity := body.get("artifact_identity")), str)
        and identity.startswith("human-founder-auth-result-readback-v2:")
    }


def test_nine_subcontract_schema_golden_vectors(tmp_path: Path) -> None:
    store, context = _seed_context(tmp_path)
    execution = authenticate_fixture_candidate_h(store, context)
    bodies = _subcontract_bodies(store, execution)

    assert set(bodies) == set(SUBCONTRACT_KIND_SPECS)
    for kind, body in bodies.items():
        assert tuple(body) == tuple(sorted(SUBCONTRACT_KIND_SPECS[kind].field_names))
    assert len(bodies["AUTHENTICATION_CLAIM_CAS_V1"]) == 14
    assert len(bodies["SIGNER_ACCEPTANCE_CAS_V1"]) == 21
    assert len(bodies["SIGNER_OUTCOME_V1"]) == 30
    assert len(bodies["AUTHENTICATION_TERMINAL_CAS_V1"]) == 20
    assert execution.result.authentication_result == "AUTHENTICATED_VALID"


def test_fixture_ed25519_uses_exact_rfc8032_pure_direct_bytes() -> None:
    expected_public = bytes.fromhex(
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    )
    expected_signature = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    signature = authentication._ed25519_sign(SEED, b"")
    assert fixture_ed25519_public_key(SEED) == expected_public
    assert signature == expected_signature
    assert fixture_ed25519_verify(expected_public, b"", signature)
    assert not fixture_ed25519_verify(expected_public, b"changed", signature)
    assert not fixture_ed25519_verify(expected_public, b"", signature[:-1])


def test_signer_is_never_called_before_durable_acceptance_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    real_sign = authentication._ed25519_sign

    def checked_sign(seed: bytes, message: bytes) -> bytes:
        bodies = []
        for path in (tmp_path / "store" / "records").glob("*.cj1"):
            value = cj1_decode(path.read_bytes())
            if isinstance(value, dict):
                bodies.append(value)
        assert any("accepted_slot_digest" in body for body in bodies)
        assert store.read_slot(
            OWNER, context.signer_available_read_back.slot_identity, 1
        ).current_status == "ACCEPTED_IN_PROGRESS"
        return real_sign(seed, message)

    monkeypatch.setattr(authentication, "_ed25519_sign", checked_sign)
    authenticate_fixture_candidate_h(store, context)


@pytest.mark.parametrize(
    "mismatch",
    ("public_key", "claim_pair", "authentication_slot"),
)
def test_g77_77_retry_tuple_requires_resolved_exact_byte_equality(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mismatch: str,
) -> None:
    store, context = _seed_context(tmp_path)
    if mismatch == "public_key":
        context = replace(context, fixture_public_key=b"\x00" * 32)
    elif mismatch == "claim_pair":
        context = replace(context, one_use_claim_token_digest="sha256:" + "0" * 64)
    else:
        context = replace(
            context,
            authentication_open_read_back=replace(
                context.authentication_open_read_back,
                slot_identity="fixture:wrong-slot",
            ),
        )
    calls = 0

    def forbidden_sign(_: bytes, __: bytes) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError("signer reached after tuple mismatch")

    monkeypatch.setattr(authentication, "_ed25519_sign", forbidden_sign)
    with pytest.raises(CandidateAuthenticationError):
        authenticate_fixture_candidate_h(store, context)
    assert calls == 0


def test_same_accepted_operation_continues_after_pre_outcome_crash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    real_sign = authentication._ed25519_sign
    first = True

    def crash_once(seed: bytes, message: bytes) -> bytes:
        nonlocal first
        if first:
            first = False
            raise InjectedPersistenceCrash("PRE_OUTCOME")
        return real_sign(seed, message)

    monkeypatch.setattr(authentication, "_ed25519_sign", crash_once)
    with pytest.raises(InjectedPersistenceCrash, match="PRE_OUTCOME"):
        authenticate_fixture_candidate_h(store, context)
    assert store.read_slot(
        OWNER, context.signer_available_read_back.slot_identity, 1
    ).current_status == "ACCEPTED_IN_PROGRESS"
    execution = authenticate_fixture_candidate_h(store, context)
    assert execution.result.authentication_result == "AUTHENTICATED_VALID"
    assert execution.logical_signer_invocations == 1


def test_competing_acceptances_have_one_winner_and_no_second_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    winner = authenticate_fixture_candidate_h(store, context)
    competing = replace(context, authentication_commitment=_commitment("different"))
    calls = 0

    def forbidden_sign(_: bytes, __: bytes) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError("second invocation")

    monkeypatch.setattr(authentication, "_ed25519_sign", forbidden_sign)
    with pytest.raises(CandidateAuthenticationError, match="RETRY_TUPLE_MISMATCH"):
        authenticate_fixture_candidate_h(store, competing)
    assert calls == 0
    assert store.read_slot(
        OWNER, context.signer_available_read_back.slot_identity, 1
    ).artifact_identity == winner.result.signer_outcome_identity


def test_terminal_restart_binds_persisted_completion_and_one_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    first = authenticate_fixture_candidate_h(store, context)
    root = tmp_path / "store"
    initial = _filesystem_snapshot(root)
    changed = replace(
        context,
        completion_logical_instant="fixture:different-completion",
    )

    def forbidden_sign(_: bytes, __: bytes) -> bytes:
        raise AssertionError("terminal recovery invoked signer")

    monkeypatch.setattr(authentication, "_ed25519_sign", forbidden_sign)
    with pytest.raises(
        CandidateAuthenticationError,
        match="RETRY_TUPLE_MISMATCH:completion_logical_instant",
    ):
        authenticate_fixture_candidate_h(CandidateHStore(root), changed)
    assert _filesystem_snapshot(root) == initial
    assert _result_identities(root) == {first.result.artifact_identity}

    for _ in range(3):
        recovered = authenticate_fixture_candidate_h(CandidateHStore(root), context)
        assert recovered.result == first.result
        assert recovered.result_write.read_back == first.result_write.read_back
    assert _result_identities(root) == {first.result.artifact_identity}


def test_identical_signer_outcome_conflict_adopts_authoritative_winner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    real_cas = CandidateHStore.compare_and_swap_subcontract
    forced = False

    def report_identical_conflict(self, **arguments):
        nonlocal forced
        result = real_cas(self, **arguments)
        if (
            not forced
            and arguments["address"].subcontract_kind == "SIGNER_OUTCOME_V1"
        ):
            forced = True
            return replace(result, outcome="CONFLICT")
        return result

    monkeypatch.setattr(
        CandidateHStore,
        "compare_and_swap_subcontract",
        report_identical_conflict,
    )
    execution = authenticate_fixture_candidate_h(store, context)
    assert forced
    assert execution.outcome.outcome == "CONFLICT"
    assert execution.outcome.read_back.artifact_identity == (
        execution.result.signer_outcome_identity
    )
    assert _result_identities(tmp_path / "store") == {
        execution.result.artifact_identity
    }


def test_competing_signer_outcomes_reject_loser_before_downstream_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, context = _seed_context(tmp_path)
    root = tmp_path / "store"
    real_cas = CandidateHStore.compare_and_swap_subcontract
    barrier = threading.Barrier(2)
    proposed_addresses: list[SubcontractAddress] = []

    def synchronize_outcomes(self, **arguments):
        if arguments["address"].subcontract_kind == "SIGNER_OUTCOME_V1":
            proposed_addresses.append(arguments["address"])
            barrier.wait(timeout=5)
        return real_cas(self, **arguments)

    monkeypatch.setattr(
        CandidateHStore,
        "compare_and_swap_subcontract",
        synchronize_outcomes,
    )
    contexts = (
        replace(context, completion_logical_instant="fixture:completion-a"),
        replace(context, completion_logical_instant="fixture:completion-b"),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(
                authenticate_fixture_candidate_h,
                CandidateHStore(root),
                competing_context,
            )
            for competing_context in contexts
        ]
    executions = []
    errors = []
    for future in futures:
        try:
            executions.append(future.result())
        except CandidateAuthenticationError as exc:
            errors.append(exc)

    assert len(executions) == 1
    assert len(errors) == 1
    assert errors[0].code == "RETRY_TUPLE_MISMATCH"
    winner = executions[0]
    assert _result_identities(root) == {winner.result.artifact_identity}
    assert len({address.identity for address in proposed_addresses}) == 2
    losing_address = next(
        address
        for address in proposed_addresses
        if address.identity != winner.result.signer_outcome_identity
    )
    with pytest.raises(CandidatePersistenceError, match="MISSING_IMMUTABLE_RECORD"):
        CandidateHStore(root).read_subcontract(losing_address)
    assert all(
        body.get("signer_outcome_identity") != losing_address.identity
        for body in _record_bodies(root)
    )


def test_identical_outer_terminal_conflict_adopts_authoritative_winner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    real_cas = CandidateHStore.compare_and_swap_subcontract
    forced = False

    def report_identical_conflict(self, **arguments):
        nonlocal forced
        result = real_cas(self, **arguments)
        if (
            not forced
            and arguments["address"].subcontract_kind
            == "AUTHENTICATION_TERMINAL_CAS_V1"
        ):
            forced = True
            return replace(result, outcome="CONFLICT")
        return result

    monkeypatch.setattr(
        CandidateHStore,
        "compare_and_swap_subcontract",
        report_identical_conflict,
    )
    execution = authenticate_fixture_candidate_h(store, context)
    assert forced
    assert execution.terminal.outcome == "CONFLICT"
    assert execution.terminal.read_back.artifact_identity == (
        execution.result.authentication_terminal_cas_identity
    )
    assert _result_identities(tmp_path / "store") == {
        execution.result.artifact_identity
    }


def test_divergent_outer_terminal_conflict_stops_before_second_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    first = authenticate_fixture_candidate_h(store, context)
    root = tmp_path / "store"
    initial = _filesystem_snapshot(root)
    proof_identity, proof_digest = _hash_pair(
        "external-one-use-proof-v1", "different-proof"
    )
    divergent = replace(
        context,
        one_use_non_equivocation_proof_identity=proof_identity,
        one_use_non_equivocation_proof_digest=proof_digest,
    )

    def forbidden_sign(_: bytes, __: bytes) -> bytes:
        raise AssertionError("terminal recovery invoked signer")

    monkeypatch.setattr(authentication, "_ed25519_sign", forbidden_sign)
    with pytest.raises(CandidateAuthenticationError, match="RETRY_TUPLE_MISMATCH"):
        authenticate_fixture_candidate_h(CandidateHStore(root), divergent)
    assert _filesystem_snapshot(root) == initial
    assert _result_identities(root) == {first.result.artifact_identity}


def test_crash_after_signer_outcome_binds_completion_on_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    root = tmp_path / "store"
    real_write = CandidateHStore.write_subcontract
    fired = False

    class LostOutcomeReadBackResponse(RuntimeError):
        pass

    def lose_outcome_read_back_response(
        self,
        address,
        canonical_bytes,
        **arguments,
    ):
        nonlocal fired
        result = real_write(self, address, canonical_bytes, **arguments)
        if (
            not fired
            and address.subcontract_kind == "SIGNER_OUTCOME_READ_BACK_V1"
        ):
            fired = True
            raise LostOutcomeReadBackResponse
        return result

    monkeypatch.setattr(
        CandidateHStore,
        "write_subcontract",
        lose_outcome_read_back_response,
    )
    with pytest.raises(LostOutcomeReadBackResponse):
        authenticate_fixture_candidate_h(store, context)
    assert fired
    assert _result_identities(root) == set()
    after_crash = _filesystem_snapshot(root)
    monkeypatch.setattr(CandidateHStore, "write_subcontract", real_write)

    changed = replace(
        context,
        completion_logical_instant="fixture:different-after-outcome",
    )
    with pytest.raises(
        CandidateAuthenticationError,
        match="RETRY_TUPLE_MISMATCH:completion_logical_instant",
    ):
        authenticate_fixture_candidate_h(CandidateHStore(root), changed)
    assert _filesystem_snapshot(root) == after_crash
    assert _result_identities(root) == set()

    completed = authenticate_fixture_candidate_h(CandidateHStore(root), context)
    replayed = authenticate_fixture_candidate_h(CandidateHStore(root), context)
    assert replayed.result == completed.result
    assert _result_identities(root) == {completed.result.artifact_identity}


@pytest.mark.parametrize(
    "boundary",
    (
        "before_outer_claim",
        "outer_claim_response_lost",
        "after_claim_before_signer_acceptance",
        "signer_acceptance_response_lost",
        "signer_invocation_accepted",
        "signer_executing",
        "valid_signature_before_outcome_commit",
        "rejected_signature_before_outcome_response",
        "outcome_response_lost",
        "before_outer_terminal",
        "outer_terminal_response_lost",
        "outer_read_back_before_result",
        "restart_signer_available",
        "restart_accepted_in_progress",
        "restart_terminal_signer_outcome",
        "permanent_exhaustion",
    ),
)
def test_all_sixteen_lost_response_boundaries_converge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    boundary: str,
) -> None:
    private_seed: bytes | None = SEED
    if boundary == "rejected_signature_before_outcome_response":
        private_seed = b"short"
    elif boundary == "permanent_exhaustion":
        private_seed = None
    store, context = _seed_context(tmp_path, private_seed=private_seed)

    class LostResponse(RuntimeError):
        pass

    cas_targets = {
        "outer_claim_response_lost": "AUTHENTICATION_CLAIM_CAS_V1",
        "signer_acceptance_response_lost": "SIGNER_ACCEPTANCE_CAS_V1",
        "rejected_signature_before_outcome_response": "SIGNER_OUTCOME_V1",
        "outcome_response_lost": "SIGNER_OUTCOME_V1",
        "outer_terminal_response_lost": "AUTHENTICATION_TERMINAL_CAS_V1",
        "restart_terminal_signer_outcome": "SIGNER_OUTCOME_V1",
    }
    write_targets = {
        "after_claim_before_signer_acceptance": "SIGNER_INVOCATION_INTENT_V1",
        "signer_invocation_accepted": "SIGNER_INVOCATION_RECEIPT_V1",
        "before_outer_terminal": "SIGNER_OUTCOME_READ_BACK_V1",
        "outer_read_back_before_result": "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1",
        "restart_accepted_in_progress": "SIGNER_INVOCATION_RECEIPT_V1",
    }
    fired = False
    if boundary in cas_targets:
        real_cas = CandidateHStore.compare_and_swap_subcontract

        def lose_cas_response(self, **arguments):
            nonlocal fired
            result = real_cas(self, **arguments)
            if not fired and arguments["address"].subcontract_kind == cas_targets[boundary]:
                fired = True
                raise LostResponse(boundary)
            return result

        monkeypatch.setattr(
            CandidateHStore, "compare_and_swap_subcontract", lose_cas_response
        )
    elif boundary in write_targets:
        real_write = CandidateHStore.write_subcontract

        def lose_write_response(self, address, canonical_bytes, **arguments):
            nonlocal fired
            result = real_write(self, address, canonical_bytes, **arguments)
            if not fired and address.subcontract_kind == write_targets[boundary]:
                fired = True
                raise LostResponse(boundary)
            return result

        monkeypatch.setattr(CandidateHStore, "write_subcontract", lose_write_response)
    elif boundary in {"signer_executing", "valid_signature_before_outcome_commit"}:
        real_sign = authentication._ed25519_sign

        def lose_sign_result(seed: bytes, message: bytes) -> bytes:
            nonlocal fired
            signature = real_sign(seed, message)
            if not fired:
                fired = True
                raise LostResponse(boundary)
            return signature

        monkeypatch.setattr(authentication, "_ed25519_sign", lose_sign_result)

    if boundary in {
        "before_outer_claim",
        "restart_signer_available",
        "permanent_exhaustion",
    }:
        first = authenticate_fixture_candidate_h(store, context)
    else:
        with pytest.raises(LostResponse, match=boundary):
            authenticate_fixture_candidate_h(store, context)
        first = authenticate_fixture_candidate_h(store, context)
    restarted = CandidateHStore(tmp_path / "store")
    replayed = authenticate_fixture_candidate_h(restarted, context)
    assert replayed.result == first.result
    assert replayed.result_write.read_back == first.result_write.read_back
    assert replayed.logical_human_authorizations == 1
    assert replayed.logical_signer_invocations == 1
    assert replayed.founding_effects == 0


def test_terminal_signer_outcome_makes_recovery_read_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, context = _seed_context(tmp_path)
    first = authenticate_fixture_candidate_h(store, context)

    def forbidden_sign(_: bytes, __: bytes) -> bytes:
        raise AssertionError("terminal recovery invoked signer")

    monkeypatch.setattr(authentication, "_ed25519_sign", forbidden_sign)
    recovered = authenticate_fixture_candidate_h(
        CandidateHStore(tmp_path / "store"), context
    )
    assert recovered.result == first.result


@pytest.mark.parametrize(
    ("private_seed", "outcome", "result", "verification"),
    [
        (b"short", "REJECTED_FINAL", "AUTHENTICATION_REJECTED_FINAL", "FALSE"),
        (
            None,
            "INDETERMINATE_FINAL",
            "INDETERMINATE_NO_VALID_RESULT",
            "NOT_APPLICABLE",
        ),
    ],
)
def test_rejected_and_indeterminate_outcomes_have_exact_closed_mapping(
    tmp_path: Path,
    private_seed: bytes | None,
    outcome: str,
    result: str,
    verification: str,
) -> None:
    store, context = _seed_context(tmp_path, private_seed=private_seed)
    execution = authenticate_fixture_candidate_h(store, context)
    assert execution.result.signer_outcome_status == outcome
    assert execution.result.authentication_result == result
    assert execution.result.signature_verification_result == verification
    assert execution.result.signature is None
    assert execution.result.terminal_authentication_slot_status == "INDETERMINATE_EXHAUSTED"


def test_only_complete_result_v2_validates_persists_and_reads_back(
    tmp_path: Path,
) -> None:
    store, context = _seed_context(tmp_path)
    execution = authenticate_fixture_candidate_h(store, context)
    result = execution.result
    assert len(type(result).SEMANTIC_FIELDS) == 50
    assert result.artifact_version == "V2"
    assert validate_artifact(result, owner_bindings=OWNER_BINDINGS) == result
    reconstructed, read_back = store.read_immutable(
        type(result), execution.result_write.read_back.address, owner_bindings=OWNER_BINDINGS
    )
    assert reconstructed == result
    assert read_back == execution.result_write.read_back
    assert "ResultV3" not in MODEL_REGISTRY


def test_restart_histories_do_not_multiply_constitutional_effects(
    tmp_path: Path,
) -> None:
    store, context = _seed_context(tmp_path)
    executions = [authenticate_fixture_candidate_h(store, context)]
    for _ in range(3):
        executions.append(
            authenticate_fixture_candidate_h(CandidateHStore(tmp_path / "store"), context)
        )
    identities = {execution.result.artifact_identity for execution in executions}
    assert len(identities) == 1
    assert {execution.logical_human_authorizations for execution in executions} == {1}
    assert {execution.logical_signer_invocations for execution in executions} == {1}
    assert {execution.admissible_results for execution in executions} == {1}
    assert {execution.founding_effects for execution in executions} == {0}


def test_fixture_authentication_dependency_and_authority_boundary() -> None:
    source = Path(authentication.__file__).read_text(encoding="utf-8")
    assert "CandidateHStore(" not in source
    assert "orchestration" not in source
    assert "from .replay" not in source
    assert "BEGIN(" not in source
    assert "activate(" not in source
    assert "deploy(" not in source
