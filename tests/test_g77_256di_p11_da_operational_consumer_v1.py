"""Non-operational certification for the minimum P11 consumer.

No test calls either operational entry method.  Synthetic construction values
exercise persistence and validation mechanics without creating or consuming a
real Human operational act, entering P11, or generating E01-E12 evidence.
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import replay_hash
from p11_da_custody_process_v1 import FixedPrincipalBindings
from p11_da_disposable_substrate_v1 import (
    ConstructionOnlyConsumerStub,
    AuthorityBinding,
    DisposableOwnerState,
    OwnerStateName,
    bind_record_identity,
    validate_input_record_bytes,
    validate_output_record_bytes,
)
from p11_da_operational_consumer_v1 import (
    AUTOMATIC_RETRY_COUNT_V1,
    CH_PASS_CONJUNCTION,
    CH_PRECONDITION_IDS,
    E01_E12_EXECUTION_AUTHORIZED_IN_G77_256DI,
    INVOCATIONS_PER_CLAIM_V1,
    OPERATIONAL_ACT_PAYLOAD_FIELDS,
    OPERATIONAL_INVOCATION_AUTHORIZED_IN_G77_256DI,
    OPERATIONAL_P11_ENTRY_AUTHORIZED_IN_G77_256DI,
    OUTPUT_RECORD_COUNT_V1,
    P12_ENTRY_AUTHORIZED_IN_G77_256DI,
    PRODUCTION_ROUTE_COUNT_V1,
    PRODUCTION_ROUTING_AUTHORIZED_IN_G77_256DI,
    P11BoundedConsumerV1,
    ProtectedOwnerStateStoreV1,
    create_commissioning_gate_v1,
    fixed_endpoint_identity,
    fixed_principal_bindings_identity,
    fixture_root_identity,
    materialization_identity,
    validate_operational_act_payload,
)


DH_CHECKPOINT = "9f5fd37212547cf06b664c94152ae0ec50a55b79"
CH_SHA256 = "d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce"
CF_SOURCE_SHA256 = "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
CUSTODY_UID = os.getuid()
ISSUANCE_UID = CUSTODY_UID + 1
CALLER_UID = CUSTODY_UID + 2


def _input_record() -> tuple[bytes, dict[str, object]]:
    value: dict[str, object] = {
        "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
        "schema_version": "1.0.0",
        "record_kind": "P11_BOUNDED_CONSUMER_INPUT",
        "record_identity": "",
        "attempt_identity": "synthetic-certification-attempt",
        "input_identity": "synthetic-certification-input",
        "provenance_identity": "synthetic-certification-provenance",
        "contract_identity": "synthetic-certification-contract",
        "contract_version": "1.0.0",
        "contract_content_sha256": replay_hash({"contract": "certification"}),
        "authorization_reference": "synthetic-human-act-reference",
        "caller_identity_reference": (
            f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{CALLER_UID}"
        ),
        "preflight_binding_identity": "synthetic-gate-placeholder",
        "preflight_status": "PASSED",
        "p10_inventory_identity": "synthetic-p10-inventory",
        "comparator_outcome_identity": "synthetic-comparator-outcome",
        "comparator_outcome": "MISMATCH",
        "replay_context_identity": "synthetic-replay-context",
    }
    serialized = bind_record_identity(value)
    return serialized, validate_input_record_bytes(serialized)


def _binding(input_record: dict[str, object]) -> AuthorityBinding:
    return AuthorityBinding(
        authenticated_caller_principal_identity=(
            f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{CALLER_UID}"
        ),
        authority_act_identity="synthetic-human-act-reference",
        authority_act_content_identity="synthetic-human-act-content",
        authorization_identity="synthetic-human-act-reference",
        attempt_identity=str(input_record["attempt_identity"]),
        input_record_identity=str(input_record["record_identity"]),
        input_identity=str(input_record["input_identity"]),
        provenance_identity=str(input_record["provenance_identity"]),
        contract_identity=str(input_record["contract_identity"]),
        contract_version=str(input_record["contract_version"]),
        contract_content_sha256=str(input_record["contract_content_sha256"]),
        authorized_scope="P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1",
        valid_from_unix_ns=100,
        valid_until_unix_ns=1_000,
    )


def _store(tmp_path: Path) -> ProtectedOwnerStateStoreV1:
    fixture_root = tmp_path / "synthetic-certification-fixture"
    fixture_root.mkdir(mode=0o700)
    fixture_root.chmod(0o700)
    return ProtectedOwnerStateStoreV1(fixture_root, os.getuid())


def _gate(
    store: ProtectedOwnerStateStoreV1,
    bindings: FixedPrincipalBindings,
    *,
    conditions: tuple[tuple[str, str], ...] = CH_PASS_CONJUNCTION,
):
    fixture_identity = fixture_root_identity(store.fixture_root, bindings.custody_uid)
    principal_identity = fixed_principal_bindings_identity(bindings)
    endpoint = fixed_endpoint_identity(store.fixture_root, bindings.custody_uid)
    materialization = materialization_identity(
        fixture_identity=fixture_identity,
        principal_identity=principal_identity,
        endpoint_identity=endpoint,
        owner_state_identity=store.root_identity,
    )
    return create_commissioning_gate_v1(
        dh_checkpoint=DH_CHECKPOINT,
        ch_decision_package_identity=(
            "G77_256CH_P11_E01_E12_OPERATIONAL_EVIDENCE_GENERATION_"
            "HUMAN_AUTHORIZATION_DECISION_PACKAGE_V1"
        ),
        ch_artifact_sha256=CH_SHA256,
        cg_checkpoint="authenticated-cg-checkpoint",
        cg_report_identity="authenticated-cg-report",
        cd_plan_identity="authenticated-cd-plan",
        cd_plan_sha256="1" * 64,
        cf_source_tree_identity="bb5382994b266e53358acb286ef06f41ce2936e6",
        cf_source_sha256=CF_SOURCE_SHA256,
        materialization_identity=materialization,
        fixture_root_identity=fixture_identity,
        principal_bindings_identity=principal_identity,
        endpoint_identity=endpoint,
        owner_state_root_identity=store.root_identity,
        condition_results=conditions,
        condition_evidence_identities=tuple(
            (condition, f"synthetic-certification-evidence-{condition}")
            for condition in CH_PRECONDITION_IDS
        ),
    )


def _operational_payload(
    input_record: dict[str, object],
    gate,
    bindings: FixedPrincipalBindings,
) -> dict[str, object]:
    return {
        "decision_package_identity": gate.ch_decision_package_identity,
        "decision_package_sha256": CH_SHA256,
        "cg_checkpoint": "authenticated-cg-checkpoint",
        "cg_report_identity": "authenticated-cg-report",
        "cd_plan_identity": "authenticated-cd-plan",
        "cd_plan_sha256": "1" * 64,
        "cf_source_tree_identity": gate.cf_source_tree_identity,
        "materialization_identity": gate.materialization_identity,
        "evidence_obligation_id": "P11-E01",
        "case_id": "P11-E01-G1-E12",
        "evidence_run_identity": "synthetic-evidence-run",
        "caller_role": "P11_ORCHESTRATION_CALLER_PRINCIPAL",
        "caller_uid": bindings.caller_uid,
        "custody_role": "AUTHORITY_CUSTODY_PROCESS_PRINCIPAL",
        "custody_uid": bindings.custody_uid,
        "fixed_endpoint_identity": gate.endpoint_identity,
        "protected_owner_state_root_identity": gate.owner_state_root_identity,
        "protected_owner_state_revision": 0,
        "attempt_identity": input_record["attempt_identity"],
        "input_record_identity": input_record["record_identity"],
        "input_payload_identity": input_record["input_identity"],
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "allowed_operation": "CLAIM_AND_INVOKE_ONCE",
        "maximum_attempts": 1,
        "automatic_retries": 0,
        "maximum_duration_ns": 10_000_000_000,
        "authority_effect_outside_bound_attempt": 0,
        "production_routing_effect": 0,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1_000,
        "terminal_consumption_and_non_reuse": "REQUIRED",
        "required_disposal": "REQUIRED",
        "minimum_retention": "CD_AUTHORIZED_MINIMUM_TRAIL_ONLY",
    }


def test_di_hard_execution_boundary_and_separate_consumer_surface() -> None:
    assert OPERATIONAL_P11_ENTRY_AUTHORIZED_IN_G77_256DI is False
    assert OPERATIONAL_INVOCATION_AUTHORIZED_IN_G77_256DI is False
    assert E01_E12_EXECUTION_AUTHORIZED_IN_G77_256DI is False
    assert P12_ENTRY_AUTHORIZED_IN_G77_256DI is False
    assert PRODUCTION_ROUTING_AUTHORIZED_IN_G77_256DI is False
    assert ConstructionOnlyConsumerStub.operational_p11_entry is False
    assert P11BoundedConsumerV1.operational_p11_entry is True
    assert not issubclass(P11BoundedConsumerV1, ConstructionOnlyConsumerStub)


def test_exact_ch_conjunction_is_required_without_evidence_effect(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    bindings = FixedPrincipalBindings(ISSUANCE_UID, CALLER_UID, CUSTODY_UID)
    gate = _gate(store, bindings)
    assert len(CH_PRECONDITION_IDS) == len(gate.condition_results) == 12
    assert gate.condition_results == CH_PASS_CONJUNCTION
    assert len(gate.condition_evidence_identities) == 12
    assert gate.satisfying_evidence_effect == gate.p11_invocation_effect == 0
    failed = tuple(
        (condition, "FAIL" if condition == "P12" else result)
        for condition, result in CH_PASS_CONJUNCTION
    )
    with pytest.raises(FailClosedRuntimeError):
        _gate(store, bindings, conditions=failed)


def test_consumer_reuses_fixed_custody_and_existing_runtimeledger(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    bindings = FixedPrincipalBindings(ISSUANCE_UID, CALLER_UID, CUSTODY_UID)
    consumer = P11BoundedConsumerV1(
        store=store,
        principal_bindings=bindings,
        commissioning_gate=_gate(store, bindings),
    )
    assert consumer.ledger_implementation is RuntimeLedger
    assert consumer.construction_adapter_reused_as_operational_consumer is False
    assert consumer.production_route_count == 0
    assert consumer.automatic_retry_count == 0
    assert consumer.invocations_per_claim == 1
    assert consumer.output_record_count == 1


def test_protected_store_synthetic_revision_lineage_is_one_way(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    serialized_input, input_record = _input_record()
    available = store.initialize_available(_binding(input_record))
    claimed = store.claim(
        available,
        claim_time_unix_ns=500,
        authenticated_caller_principal_identity=(
            f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{CALLER_UID}"
        ),
    )
    with pytest.raises(FailClosedRuntimeError):
        store.claim(
            available,
            claim_time_unix_ns=500,
            authenticated_caller_principal_identity=(
                f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{CALLER_UID}"
            ),
        )
    output = {
        "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_OUTPUT_V1",
        "schema_version": "1.0.0",
        "record_kind": "P11_BOUNDED_CONSUMER_OUTCOME",
        "record_identity": "",
        "attempt_identity": input_record["attempt_identity"],
        "input_identity": input_record["input_identity"],
        "input_record_identity": input_record["record_identity"],
        "authorization_identity": claimed.binding.authorization_identity,
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "provenance_identity": input_record["provenance_identity"],
        "outcome": "MISMATCH",
        "failure_class_or_reason": None,
        "started_at_unix_ns": 500,
        "terminal_at_unix_ns": 600,
        "duration_ns": 100,
        "disposal_completion_proof_identity": None,
    }
    output_bytes = bind_record_identity(output)
    validated_output = validate_output_record_bytes(
        output_bytes,
        input_record,
        validated_authorization_identity=claimed.binding.authorization_identity,
    )
    consumed = store.terminal_bind_and_permanently_exhaust(
        claimed, validated_output
    )
    assert consumed.state is OwnerStateName.CONSUMED
    assert store.current() == consumed
    assert len(tuple(store.root.iterdir())) == 3
    with pytest.raises(FailClosedRuntimeError):
        store.claim(
            consumed,
            claim_time_unix_ns=700,
            authenticated_caller_principal_identity=(
                f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{CALLER_UID}"
            ),
        )
    assert serialized_input


def test_operational_payload_is_exact_current_one_use_and_zero_production(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    bindings = FixedPrincipalBindings(ISSUANCE_UID, CALLER_UID, CUSTODY_UID)
    gate = _gate(store, bindings)
    _, input_record = _input_record()
    payload = _operational_payload(input_record, gate, bindings)
    validated = validate_operational_act_payload(
        payload,
        input_record=input_record,
        gate=gate,
        bindings=bindings,
        owner_revision=0,
        now_unix_ns=500,
    )
    assert set(validated) == OPERATIONAL_ACT_PAYLOAD_FIELDS
    for field_name, bad_value in (
        ("automatic_retries", 1),
        ("maximum_attempts", 2),
        ("production_routing_effect", 1),
        ("protected_owner_state_revision", 1),
    ):
        tampered = dict(payload, **{field_name: bad_value})
        with pytest.raises(FailClosedRuntimeError):
            validate_operational_act_payload(
                tampered,
                input_record=input_record,
                gate=gate,
                bindings=bindings,
                owner_revision=0,
                now_unix_ns=500,
            )


def test_operational_entry_api_has_no_callback_retry_or_route_selection() -> None:
    signature = inspect.signature(P11BoundedConsumerV1.claim_and_invoke_once)
    forbidden = {
        "callback",
        "script",
        "plugin",
        "retry",
        "production_route",
        "endpoint",
        "store",
        "owner_state",
        "principal",
        "credential",
        "resolver",
        "custody_path",
    }
    assert not (set(signature.parameters) & forbidden)
    source = inspect.getsource(P11BoundedConsumerV1.claim_and_invoke_once)
    ordered_markers = (
        "PRECLAIM",
        "self._store.claim(",
        "self._build_one_output(",
        "terminal_bind_and_permanently_exhaust(",
        "PERMANENT_EXHAUSTION",
    )
    positions = tuple(source.index(marker) for marker in ordered_markers)
    assert positions == tuple(sorted(positions))
    assert (AUTOMATIC_RETRY_COUNT_V1, INVOCATIONS_PER_CLAIM_V1) == (0, 1)
    assert (OUTPUT_RECORD_COUNT_V1, PRODUCTION_ROUTE_COUNT_V1) == (1, 0)


def test_revocation_supersession_and_expiry_use_the_same_protected_store() -> None:
    source = inspect.getsource(P11BoundedConsumerV1)
    assert "def terminate_human_act(" in source
    assert "CustodyOperation.REQUEST_REVOCATION" in source
    assert "CustodyOperation.REQUEST_SUPERSESSION" in source
    assert "OwnerStateName.EXPIRED" in source
    assert "self._store.terminate_unclaimed" in source


def test_no_operational_entry_method_was_called_by_certification_suite() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_calls = (
        "." + "submit_human_act(",
        "." + "terminate_human_act(",
        "." + "claim_and_invoke_once(",
    )
    assert all(call not in source for call in forbidden_calls)
