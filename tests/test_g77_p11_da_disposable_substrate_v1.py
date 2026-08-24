"""Construction-only validation for the disposable P11 D-A S1-S7 substrate.

These tests create no canonical Human operational authority act, enter no P11
runtime, and satisfy none of E01-E12.
"""

from __future__ import annotations

from dataclasses import fields
import inspect
import json
import os
from pathlib import Path

import pytest

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from p11_da_custody_process_v1 import (
    CUSTODY_REQUEST_FIELDS,
    FIXED_ENDPOINT_NAME,
    FORBIDDEN_REQUEST_SELECTION_FIELDS,
    ROLE_COUNT,
    ROLE_DESCRIPTORS,
    CustodyOperation,
    CustodyPeerCredentialVerifier,
    FixedLocalIPCConfiguration,
    FixedPrincipalBindings,
    PeerCredentials,
    PrincipalRole,
    decode_local_frame,
    encode_local_frame,
    read_kernel_peer_credentials,
)
from p11_da_disposable_substrate_v1 import (
    ALLOWED_OWNER_STATE_TRANSITIONS,
    AUTOMATIC_RETRY_COUNT,
    CHE_CORRELATION_VALIDATOR,
    HUMAN_ACT_VALIDATOR,
    INPUT_FIELDS,
    INVOCATIONS_PER_CLAIM,
    MAXIMUM_DURATION_NS,
    OPERATIONAL_EVIDENCE_GENERATION_AUTHORIZED,
    OUTPUT_FIELDS,
    OUTPUT_RECORD_COUNT,
    OUTCOME_VOCABULARY,
    PRODUCTION_ROUTE_COUNT,
    REUSED_LEDGER_SURFACES,
    REUSED_SERIALIZATION_SURFACES,
    AuthorityBinding,
    ConstructionOnlyConsumerStub,
    D3Phase,
    D3TransactionPlan,
    DisposableOwnerState,
    OwnerStateName,
    P11CaptureReplayAdapter,
    atomically_claim_construction_state,
    bind_record_identity,
    replay_binding_identity,
    terminal_bind_and_consume,
    transition_owner_state,
    validate_input_record_bytes,
    validate_output_record_bytes,
    write_record_immutable,
)
from p11_da_fault_observation_v1 import (
    AUTHORITY_EFFECT,
    BACKGROUND_WATCHER_COUNT,
    FAULT_CONTROL_FIELDS,
    FORBIDDEN_FAULT_CONTROL_FIELDS,
    OWNER_STATE_WRITE_EFFECT,
    P11_INVOCATION_EFFECT,
    PRODUCTION_MONITORING_INTEGRATION_COUNT,
    ROUTING_EFFECT,
    DeterministicFaultControl,
    FaultLabel,
    FaultPoint,
    build_incident_review,
    observe_authenticated_entries,
)


EXPECTED_FILES = frozenset(
    {
        "p11_da_disposable_substrate_v1.py",
        "p11_da_custody_process_v1.py",
        "p11_da_fault_observation_v1.py",
        "test_g77_p11_da_disposable_substrate_v1.py",
    }
)


def _input_record() -> tuple[bytes, dict[str, object]]:
    value: dict[str, object] = {
        "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
        "schema_version": "1.0.0",
        "record_kind": "P11_BOUNDED_CONSUMER_INPUT",
        "record_identity": "",
        "attempt_identity": "attempt-construction-1",
        "input_identity": "input-construction-1",
        "provenance_identity": "provenance-construction-1",
        "contract_identity": "p11-contract-construction-1",
        "contract_version": "1.0.0",
        "contract_content_sha256": replay_hash({"contract": "construction"}),
        "authorization_reference": "opaque-authorization-construction-1",
        "caller_identity_reference": "opaque-caller-construction-1",
        "preflight_binding_identity": "preflight-construction-1",
        "preflight_status": "PASSED",
        "p10_inventory_identity": "p10-inventory-construction-1",
        "comparator_outcome_identity": "comparator-construction-1",
        "comparator_outcome": "EQUAL",
        "replay_context_identity": "replay-context-construction-1",
    }
    serialized = bind_record_identity(value)
    return serialized, validate_input_record_bytes(serialized)


def _binding(input_record: dict[str, object]) -> AuthorityBinding:
    return AuthorityBinding(
        authenticated_caller_principal_identity="fixed-caller-principal",
        authority_act_identity="construction-act-reference",
        authority_act_content_identity="construction-act-content-reference",
        authorization_identity="construction-authorization-identity",
        attempt_identity=str(input_record["attempt_identity"]),
        input_record_identity=str(input_record["record_identity"]),
        input_identity=str(input_record["input_identity"]),
        provenance_identity=str(input_record["provenance_identity"]),
        contract_identity=str(input_record["contract_identity"]),
        contract_version=str(input_record["contract_version"]),
        contract_content_sha256=str(input_record["contract_content_sha256"]),
        authorized_scope="P11_DA_CONSTRUCTION_ONLY",
        valid_from_unix_ns=100,
        valid_until_unix_ns=1_000,
    )


def test_exact_authorized_four_file_construction_surface_exists() -> None:
    test_root = Path(__file__).resolve().parent
    assert all((test_root / name).is_file() for name in EXPECTED_FILES)
    assert len(EXPECTED_FILES) == 4


def test_s1_exact_closed_schemas_canonical_identity_and_lineage() -> None:
    serialized_input, input_record = _input_record()
    assert len(INPUT_FIELDS) == 18
    assert len(OUTPUT_FIELDS) == 18
    assert set(input_record) == INPUT_FIELDS
    assert serialized_input == canonical_serialize(input_record).encode("utf-8")
    assert OUTCOME_VOCABULARY == {"EQUAL", "MISMATCH", "FAILED_CLOSED"}

    for outcome in sorted(OUTCOME_VOCABULARY):
        failed = outcome == "FAILED_CLOSED"
        serialized_output = ConstructionOnlyConsumerStub.invoke_once(
            serialized_input,
            validated_authorization_identity="construction-authorization-identity",
            outcome=outcome,
            started_at_unix_ns=1_000,
            terminal_at_unix_ns=1_100,
            failure_class_or_reason="CONSTRUCTION_FAILURE" if failed else None,
            disposal_completion_proof_identity=(
                "construction-disposal-proof" if failed else None
            ),
        )
        output = validate_output_record_bytes(
            serialized_output,
            input_record,
            validated_authorization_identity="construction-authorization-identity",
        )
        assert set(output) == OUTPUT_FIELDS
        assert output["input_record_identity"] == input_record["record_identity"]
        assert replay_binding_identity(input_record, output).startswith("sha256:")


def test_s1_rejects_unknown_duplicate_noncanonical_and_bad_lineage() -> None:
    serialized, input_record = _input_record()
    unknown = dict(input_record, unauthorized_field="no")
    with pytest.raises(FailClosedRuntimeError):
        validate_input_record_bytes(canonical_serialize(unknown).encode())
    with pytest.raises(FailClosedRuntimeError):
        validate_input_record_bytes(b'{"schema_id":"a","schema_id":"b"}')
    with pytest.raises(FailClosedRuntimeError):
        validate_input_record_bytes(serialized + b"\n")

    output_bytes = ConstructionOnlyConsumerStub.invoke_once(
        serialized,
        validated_authorization_identity="construction-authorization-identity",
        outcome="EQUAL",
        started_at_unix_ns=1,
        terminal_at_unix_ns=2,
    )
    output = json.loads(output_bytes)
    output["attempt_identity"] = "wrong-attempt"
    tampered = bind_record_identity(output)
    with pytest.raises(FailClosedRuntimeError):
        validate_output_record_bytes(
            tampered,
            input_record,
            validated_authorization_identity="construction-authorization-identity",
        )


def test_s1_reuses_immutable_transport_helper(tmp_path: Path) -> None:
    serialized, input_record = _input_record()
    path = tmp_path / "construction-input.json"
    write_record_immutable(path, serialized, kind="INPUT")
    assert path.read_text(encoding="utf-8") == canonical_serialize(input_record) + "\n"
    with pytest.raises(FailClosedRuntimeError):
        write_record_immutable(path, serialized, kind="INPUT")


def test_s3_state_vocabulary_transitions_and_no_return_to_available() -> None:
    _, input_record = _input_record()
    assert {state.value for state in OwnerStateName} == {
        "AVAILABLE",
        "CLAIMED",
        "CONSUMED",
        "REVOKED",
        "SUPERSEDED",
        "EXPIRED",
        "RECONCILIATION_REQUIRED",
    }
    assert ALLOWED_OWNER_STATE_TRANSITIONS == {
        (OwnerStateName.AVAILABLE, OwnerStateName.CLAIMED),
        (OwnerStateName.AVAILABLE, OwnerStateName.REVOKED),
        (OwnerStateName.AVAILABLE, OwnerStateName.SUPERSEDED),
        (OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED),
        (OwnerStateName.CLAIMED, OwnerStateName.CONSUMED),
        (OwnerStateName.CLAIMED, OwnerStateName.RECONCILIATION_REQUIRED),
        (OwnerStateName.RECONCILIATION_REQUIRED, OwnerStateName.CONSUMED),
    }
    for terminal in (
        OwnerStateName.REVOKED,
        OwnerStateName.SUPERSEDED,
        OwnerStateName.EXPIRED,
    ):
        state = transition_owner_state(
            DisposableOwnerState(_binding(input_record)), terminal
        )
        with pytest.raises(FailClosedRuntimeError):
            transition_owner_state(state, OwnerStateName.AVAILABLE)


def test_s3_s4_claim_one_construction_invocation_terminal_bind_exhaustion() -> None:
    serialized_input, input_record = _input_record()
    available = DisposableOwnerState(_binding(input_record))
    claimed = atomically_claim_construction_state(
        available,
        claim_time_unix_ns=500,
        authenticated_caller_principal_identity="fixed-caller-principal",
    )
    assert claimed.state is OwnerStateName.CLAIMED
    with pytest.raises(FailClosedRuntimeError):
        atomically_claim_construction_state(
            claimed,
            claim_time_unix_ns=500,
            authenticated_caller_principal_identity="fixed-caller-principal",
        )

    output_bytes = ConstructionOnlyConsumerStub.invoke_once(
        serialized_input,
        validated_authorization_identity=claimed.binding.authorization_identity,
        outcome="MISMATCH",
        started_at_unix_ns=500,
        terminal_at_unix_ns=600,
    )
    output = validate_output_record_bytes(
        output_bytes,
        input_record,
        validated_authorization_identity=claimed.binding.authorization_identity,
    )
    consumed = terminal_bind_and_consume(claimed, output)
    assert consumed.state is OwnerStateName.CONSUMED
    assert consumed.output_record_identity == output["record_identity"]
    with pytest.raises(FailClosedRuntimeError):
        transition_owner_state(consumed, OwnerStateName.AVAILABLE)

    tampered_output = dict(output, provenance_identity="wrong-provenance")
    tampered_output_bytes = bind_record_identity(tampered_output)
    tampered_output = json.loads(tampered_output_bytes)
    with pytest.raises(FailClosedRuntimeError):
        terminal_bind_and_consume(claimed, tampered_output)


def test_s3_ambiguous_claim_is_permanently_non_reusable() -> None:
    _, input_record = _input_record()
    claimed = transition_owner_state(
        DisposableOwnerState(_binding(input_record)), OwnerStateName.CLAIMED
    )
    ambiguous = transition_owner_state(
        claimed, OwnerStateName.RECONCILIATION_REQUIRED
    )
    with pytest.raises(FailClosedRuntimeError):
        transition_owner_state(ambiguous, OwnerStateName.AVAILABLE)
    with pytest.raises(FailClosedRuntimeError):
        transition_owner_state(ambiguous, OwnerStateName.CONSUMED)


def test_s4_exact_continuous_transaction_shape_and_zero_production() -> None:
    plan = D3TransactionPlan()
    assert plan.phases == (
        D3Phase.PRECLAIM,
        D3Phase.CLAIM,
        D3Phase.ONE_BOUNDED_INVOCATION,
        D3Phase.TERMINAL_BIND,
        D3Phase.PERMANENT_EXHAUSTION,
    )
    assert MAXIMUM_DURATION_NS == 10_000_000_000
    assert AUTOMATIC_RETRY_COUNT == 0
    assert INVOCATIONS_PER_CLAIM == 1
    assert OUTPUT_RECORD_COUNT == 1
    assert PRODUCTION_ROUTE_COUNT == 0
    assert ConstructionOnlyConsumerStub.authority_effect == 0
    assert ConstructionOnlyConsumerStub.operational_p11_entry is False


def test_s2_fixed_three_roles_closed_request_and_kernel_peer_credentials() -> None:
    assert len(PrincipalRole) == ROLE_COUNT == 3
    assert len(ROLE_DESCRIPTORS) == 3
    assert not (CUSTODY_REQUEST_FIELDS & FORBIDDEN_REQUEST_SELECTION_FIELDS)
    config = FixedLocalIPCConfiguration()
    assert config.endpoint_name == FIXED_ENDPOINT_NAME
    assert config.local_only is True
    assert config.remote_fallback_allowed is False
    assert config.caller_endpoint_parameter_allowed is False

    current_uid = os.getuid()
    bindings = FixedPrincipalBindings(
        issuance_uid=current_uid + 1,
        caller_uid=current_uid,
        custody_uid=current_uid + 2,
    )
    verifier = CustodyPeerCredentialVerifier(bindings)
    # CF validates the peer-credential mechanism structurally.  It does not
    # provision or exercise operational principal isolation.
    assert "SO_PEERCRED" in inspect.getsource(read_kernel_peer_credentials)
    peer = PeerCredentials(pid=os.getpid(), uid=current_uid, gid=os.getgid())
    assert verifier.authenticate(
        CustodyOperation.CLAIM_AND_INVOKE_ONCE, peer
    ) is PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL
    with pytest.raises(FailClosedRuntimeError):
        verifier.authenticate(CustodyOperation.SUBMIT_CANONICAL_HUMAN_ACT, peer)


def test_s2_canonical_fixed_local_frame_round_trip() -> None:
    value = {"operation": "READ_ONLY_AUDIT", "request_identity": "construction"}
    assert decode_local_frame(encode_local_frame(value)) == value


def test_s5_directly_reuses_existing_canonical_and_ledger_surfaces(
    tmp_path: Path,
) -> None:
    assert HUMAN_ACT_VALIDATOR is validate_canonical_human_authority_act_v1
    assert CHE_CORRELATION_VALIDATOR is validate_canonical_che_evidence_correlation_v1
    assert RuntimeLedger.append in REUSED_LEDGER_SURFACES
    assert RuntimeLedger.read in REUSED_LEDGER_SURFACES
    assert canonical_serialize in REUSED_SERIALIZATION_SURFACES
    assert replay_hash in REUSED_SERIALIZATION_SURFACES

    adapter = P11CaptureReplayAdapter(tmp_path)
    assert adapter.ledger_implementation is RuntimeLedger
    adapter.append_construction_capture(
        "fixture-construction-1",
        "P11_DA_CONSTRUCTION_STATE",
        {"state": "AVAILABLE", "operational_authority_effect": 0},
    )
    entries = adapter.read_only_validate("fixture-construction-1")
    assert len(entries) == 1
    assert entries[0]["sequence"] == 0


def test_s6_fault_catalog_is_closed_and_has_no_executable_extension_fields() -> None:
    assert not (FAULT_CONTROL_FIELDS & FORBIDDEN_FAULT_CONTROL_FIELDS)
    control = DeterministicFaultControl(
        FaultLabel.CLAIM_AMBIGUITY, FaultPoint.CLAIM_COMMIT
    )
    assert control.identity.startswith("sha256:")
    with pytest.raises(FailClosedRuntimeError):
        DeterministicFaultControl(
            FaultLabel.CLAIM_AMBIGUITY, FaultPoint.BOUNDED_INVOCATION
        )
    assert "callback" not in {field.name for field in fields(control)}


def test_s7_observation_and_incident_review_are_read_only(tmp_path: Path) -> None:
    adapter = P11CaptureReplayAdapter(tmp_path)
    adapter.append_construction_capture(
        "fixture-construction-2",
        "P11_DA_CONSTRUCTION_OUTPUT",
        {"outcome": "FAILED_CLOSED", "authority_effect": 0},
    )
    observations = observe_authenticated_entries(
        adapter.read_only_validate("fixture-construction-2")
    )
    review = build_incident_review(observations, "REVIEW_ONLY")
    assert len(observations) == 1
    assert review.observation_identities == (observations[0].observation_identity,)
    assert (
        AUTHORITY_EFFECT,
        ROUTING_EFFECT,
        OWNER_STATE_WRITE_EFFECT,
        P11_INVOCATION_EFFECT,
        BACKGROUND_WATCHER_COUNT,
        PRODUCTION_MONITORING_INTEGRATION_COUNT,
    ) == (0, 0, 0, 0, 0, 0)
    tampered = dict(adapter.read_only_validate("fixture-construction-2")[0])
    tampered["payload"] = {"outcome": "EQUAL", "authority_effect": 1}
    with pytest.raises(FailClosedRuntimeError):
        observe_authenticated_entries((tampered,))


def test_construction_boundary_has_zero_operational_authority_or_evidence() -> None:
    assert OPERATIONAL_EVIDENCE_GENERATION_AUTHORIZED is False
    assert not hasattr(ConstructionOnlyConsumerStub, "production_route")
    signature = inspect.signature(ConstructionOnlyConsumerStub.invoke_once)
    assert not (
        set(signature.parameters)
        & {
            "principal",
            "endpoint",
            "credential",
            "resolver",
            "store",
            "owner_state",
            "custody_path",
            "retry_count",
            "production_route",
        }
    )
