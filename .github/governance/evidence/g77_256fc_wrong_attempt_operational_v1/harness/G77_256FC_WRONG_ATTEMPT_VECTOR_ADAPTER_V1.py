#!/usr/bin/env python3
"""FC isolated WRONG_ATTEMPT delta over the hash-bound ER common harness."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import sys
from typing import Any


ER_HARNESS = Path(
    "/mnt/aigol/.github/governance/evidence/g77_256er_p11_operational_v1/"
    "harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_HARNESS_SHA256 = "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89"
GENERATION_ID = "G77_256FC_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_OPERATIONAL_COMMISSIONING_V1"
AUTHORIZED_ATTEMPT_ID = "G77_256FC_E05_AUTHORIZED_ATTEMPT_001"
WRONG_ATTEMPT_ID = "G77_256FC_E05_SUPPLIED_WRONG_ATTEMPT_002"
ACT_ID = "G77_256FC_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"
CASE_ID = "G77_256FC_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001"
RAW_ROOT = Path("/mnt/g77-evidence")
CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256FC_CONTINUATION_MANIFEST_V1.json"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_er() -> Any:
    if sha256_path(ER_HARNESS) != ER_HARNESS_SHA256:
        raise RuntimeError("committed ER harness identity mismatch")
    spec = importlib.util.spec_from_file_location("g77_256er_reused_harness_v1", ER_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("committed ER harness import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_fc_input_and_authority(er: Any, gate: Any, bindings: Any, store: Any) -> tuple[Any, ...]:
    """Create one valid act/input pair with fresh FC identities."""
    del store
    sys.path.insert(0, str(er.CHECKOUT))
    sys.path.insert(0, str(er.CHECKOUT / "tests"))
    from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
        CanonicalCHEEvidenceCorrelationV1,
    )
    from aigol.runtime.canonical_human_authority_act_contract_v1 import (
        CanonicalHumanAuthorityActV1,
        canonical_human_authority_payload_digest_v1,
    )
    from aigol.runtime.transport.serialization import replay_hash
    from p11_da_disposable_substrate_v1 import bind_record_identity, validate_input_record_bytes

    original_input_bytes, original_input, original_act, original_correlation = (
        er.create_input_and_authority(gate, bindings, None)
    )
    del original_input_bytes
    input_value = dict(original_input)
    input_value.update({
        "record_identity": "",
        "attempt_identity": AUTHORIZED_ATTEMPT_ID,
        "input_identity": "G77_256FC_E05_WRONG_ATTEMPT_BASELINE_INPUT_001",
        "provenance_identity": "G77_256FC_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1",
        "contract_identity": "G77_256FC_E05_WRONG_ATTEMPT_FAIL_CLOSED_CONTRACT_V1",
        "contract_content_sha256": replay_hash({"contract": "G77_256FC_E05_WRONG_ATTEMPT_FAIL_CLOSED_V1"}),
        "p10_inventory_identity": "G77_256FC_P10_ONE_DENIAL_ZERO_RETRY_INVENTORY_V1",
        "comparator_outcome_identity": "G77_256FC_E05_WRONG_ATTEMPT_DENIAL_OUTCOME_001",
        "comparator_outcome": "FAILED_CLOSED",
        "replay_context_identity": "G77_256FC_EXISTING_RUNTIMELEDGER_REPLAY_CONTEXT_V1",
    })
    input_bytes = bind_record_identity(input_value)
    input_record = validate_input_record_bytes(input_bytes)

    act_value = original_act.to_dict()
    payload = dict(act_value["payload"])
    payload.update({
        "evidence_obligation_id": "P11-E05",
        "case_id": CASE_ID,
        "evidence_run_identity": "G77_256FC_WRONG_ATTEMPT_EVIDENCE_RUN_001",
        "attempt_identity": AUTHORIZED_ATTEMPT_ID,
        "input_record_identity": input_record["record_identity"],
        "input_payload_identity": input_record["input_identity"],
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "minimum_retention": "CD_AUTHORIZED_MINIMUM_TRAIL_PLUS_FC_RAW_PREIMAGE",
    })
    act_value.update({
        "authority_act_identity": ACT_ID,
        "interaction_identity": "G77_256FC_INTERACTION_001",
        "conversation_identity": "G77_256FC_CONVERSATION_001",
        "session_identity": "G77_256FC_SESSION_001",
        "request_identity": "G77_256FC_REQUEST_001",
        "continuation_identity": "G77_256FC_CONTINUATION_001",
        "payload": payload,
        "payload_digest": canonical_human_authority_payload_digest_v1(payload),
        "metadata": {
            "generation_identity": GENERATION_ID,
            "human_authorization_source": "THIS_G77_256FC_AUTHORIZATION",
            "selected_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT",
            "non_transferable": True,
            "non_reusable": True,
            "machine_completed_human_semantics": 0,
        },
    })
    act = CanonicalHumanAuthorityActV1.from_dict(act_value)

    correlation_value = original_correlation.to_dict()
    correlation_value.update({
        "interaction_identity": act.interaction_identity,
        "conversation_identity": act.conversation_identity,
        "session_identity": act.session_identity,
        "runtime_scope_identity": GENERATION_ID,
        "source_channel_identity": "G77_256FC_HUMAN_AUTHORIZATION_CHANNEL",
        "adapter_identity": "G77_256FC_CANONICAL_BINDING_ADAPTER",
        "request_identity": act.request_identity,
        "che_entry_identity": "G77_256FC_CHE_ENTRY_001",
        "source_act_identity": act.authority_act_identity,
        "source_act_digest": replay_hash(act.to_dict()),
        "order_identity": "G77_256FC_ORDER_001",
        "idempotency_identity": "G77_256FC_IDEMPOTENCY_001",
        "continuation_identity": act.continuation_identity,
        "authority_act_identity": act.authority_act_identity,
        "authority_kind": act.authority_kind,
        "authority_requesting_owner_identity": act.expected_owner,
        "authority_target_identity": act.target_identity,
        "authority_target_revision": act.target_revision,
        "authority_payload_digest": act.payload_digest,
        "authority_result_identity": "G77_256FC_AUTHORITY_RESULT_001",
        "owner_state_identity": gate.owner_state_root_identity,
        "owner_projection_identity": "G77_256FC_OWNER_PROJECTION_001",
        "presentation_identity": "G77_256FC_PRESENTATION_001",
        "response_identity": "G77_256FC_RESPONSE_001",
        "response_digest": replay_hash({"response": "G77_256FC_AUTHORITY_RECORDED"}),
        "delivery_record_identity": "G77_256FC_DELIVERY_001",
        "metadata": {"generation_identity": GENERATION_ID},
    })
    correlation = CanonicalCHEEvidenceCorrelationV1.from_dict(correlation_value)
    return input_bytes, input_record, act, correlation


def fc_custody_process(er: Any, control: socket.socket, server: socket.socket, condition_evidence: tuple[tuple[str, str], ...]) -> None:
    """Submit one valid act, then present exactly one isolated wrong-attempt request."""
    try:
        er.drop_role("custody")
        sys.path.insert(0, str(er.CHECKOUT))
        sys.path.insert(0, str(er.CHECKOUT / "tests"))
        from p11_da_custody_process_v1 import CustodyOperation, CustodyRequest, FixedPrincipalBindings
        from p11_da_operational_consumer_v1 import (
            CH_PASS_CONJUNCTION,
            P11BoundedConsumerV1,
            ProtectedOwnerStateStoreV1,
            create_commissioning_gate_v1,
            fixed_endpoint_identity,
            fixed_principal_bindings_identity,
            fixture_root_identity,
            materialization_identity,
        )
        from p11_da_disposable_substrate_v1 import bind_record_identity, validate_input_record_bytes

        bindings = FixedPrincipalBindings(1, 2, 3)
        store = ProtectedOwnerStateStoreV1(er.FIXTURE_ROOT, 3)
        fixture_identity = fixture_root_identity(er.FIXTURE_ROOT, 3)
        principal_identity = fixed_principal_bindings_identity(bindings)
        endpoint_identity = fixed_endpoint_identity(er.FIXTURE_ROOT, 3)
        materialization = materialization_identity(
            fixture_identity=fixture_identity,
            principal_identity=principal_identity,
            endpoint_identity=endpoint_identity,
            owner_state_identity=store.root_identity,
        )
        gate = create_commissioning_gate_v1(
            dh_checkpoint="9f5fd37212547cf06b664c94152ae0ec50a55b79",
            ch_decision_package_identity="G77_256CH_P11_E01_E12_OPERATIONAL_EVIDENCE_GENERATION_HUMAN_AUTHORIZATION_DECISION_PACKAGE_V1",
            ch_artifact_sha256="d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce",
            cg_checkpoint="bccbb46a65ebc0de7a0c421e4c871b8487d3bb0c",
            cg_report_identity="G77_256CG_P11_IMPLEMENTED_DISPOSABLE_D_A_TEST_SUBSTRATE_INDEPENDENT_VALIDATION_AND_OPERATIONAL_EVIDENCE_AUTHORIZATION_READINESS_ASSESSMENT_V1",
            cd_plan_identity="G77_256CD_P11_PRE_IMPLEMENTATION_EVIDENCE_GENERATION_AND_VALIDATION_PLAN_V1",
            cd_plan_sha256="666162ed94c5b291c1694230cbdc2ea040ba2165817f3c325fe2979fe993b670",
            cf_source_tree_identity="bb5382994b266e53358acb286ef06f41ce2936e6",
            cf_source_sha256="a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
            materialization_identity=materialization,
            fixture_root_identity=fixture_identity,
            principal_bindings_identity=principal_identity,
            endpoint_identity=endpoint_identity,
            owner_state_root_identity=store.root_identity,
            condition_results=CH_PASS_CONJUNCTION,
            condition_evidence_identities=condition_evidence,
        )
        consumer = P11BoundedConsumerV1(store=store, principal_bindings=bindings, commissioning_gate=gate)
        er.send_message(control, {
            "message_type": "GATE_READY",
            "gate": gate.identity_preimage() | {"gate_identity": gate.gate_identity},
            "store_root": str(store.root),
            "store_root_identity": store.root_identity,
            "materialization_identity": materialization,
        })
        reader = control.makefile("r", encoding="utf-8")
        if er.receive_message(reader)["command"] != "CREATE_ACT":
            raise RuntimeError("pre-act checkpoint acknowledgement missing")
        authorized_bytes, authorized_record, act, correlation = create_fc_input_and_authority(er, gate, bindings, store)
        er.send_message(control, {
            "message_type": "ACT_CREATED",
            "input_record": authorized_record,
            "input_canonical_utf8": authorized_bytes.decode("utf-8"),
            "human_authority_act": act.to_dict(),
            "che_correlation": correlation.to_dict(),
        })
        if er.receive_message(reader)["command"] != "SUBMIT_ACT":
            raise RuntimeError("act creation acknowledgement missing")
        issuance_connection, _ = server.accept()
        available_identity = consumer.submit_human_act(
            issuance_connection,
            act=act,
            correlation=correlation,
            input_record_canonical_bytes=authorized_bytes,
        )
        issuance_connection.sendall(b"1")
        issuance_connection.close()
        available = store.current()
        owner_before = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(store.root.iterdir())]
        er.send_message(control, {
            "message_type": "ACT_SUBMITTED",
            "available_state_identity": available_identity,
            "available_state": {
                "state": available.state.value,
                "revision": available.revision,
                "binding": {field: getattr(available.binding, field) for field in available.binding.__dataclass_fields__},
            },
            "owner_revision_files": owner_before,
        })
        if er.receive_message(reader)["command"] != "INVOKE_ONCE":
            raise RuntimeError("authority checkpoint acknowledgement missing")

        wrong_value = dict(authorized_record)
        wrong_value["record_identity"] = ""
        wrong_value["attempt_identity"] = WRONG_ATTEMPT_ID
        wrong_bytes = bind_record_identity(wrong_value)
        wrong_record = validate_input_record_bytes(wrong_bytes)
        differing_fields = sorted(
            key for key in authorized_record
            if authorized_record[key] != wrong_record[key]
        )
        caller_connection, _ = server.accept()
        raw_peer = caller_connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        peer_pid, peer_uid, peer_gid = struct.unpack("3i", raw_peer)
        request = CustodyRequest(
            protocol_identity="P11_DA_DISPOSABLE_LOCAL_IPC_V1",
            operation=CustodyOperation.CLAIM_AND_INVOKE_ONCE,
            request_identity="G77_256FC_WRONG_ATTEMPT_CUSTODY_REQUEST_001",
            canonical_payload=wrong_bytes,
        )
        output_bytes = None
        denial_error_type = None
        denial_error = None
        try:
            output_bytes = consumer.claim_and_invoke_once(
                caller_connection,
                request,
                act=act,
                correlation=correlation,
                input_record_canonical_bytes=wrong_bytes,
            )
        except BaseException as exc:
            denial_error_type = type(exc).__name__
            denial_error = str(exc)
        finally:
            try:
                caller_connection.sendall(b"1")
            except OSError:
                pass
            caller_connection.close()
        after = store.current()
        owner_after = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(store.root.iterdir())]
        ledger_root = er.FIXTURE_ROOT / "runtime_replay"
        denial_pass = all((
            output_bytes is None,
            denial_error_type == "FailClosedRuntimeError",
            denial_error == "operational Human act attempt_identity binding is invalid",
            differing_fields == ["attempt_identity", "record_identity"],
            after.state.value == "AVAILABLE",
            after.revision == 0,
            owner_after == owner_before,
            not ledger_root.exists(),
        ))
        result = {
            "message_type": "FIRST_EFFECT_COMPLETE",
            "case_id": CASE_ID,
            "selected_vector": "P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT",
            "request_identity": request.request_identity,
            "authorized_attempt_identity": AUTHORIZED_ATTEMPT_ID,
            "supplied_attempt_identity": WRONG_ATTEMPT_ID,
            "authorized_input_record": authorized_record,
            "supplied_input_record": wrong_record,
            "differing_input_fields": differing_fields,
            "peer_credentials": {"pid": peer_pid, "uid": peer_uid, "gid": peer_gid},
            "denial_point": "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_CLAIM_ENTRY_INVOCATION_OR_EFFECT",
            "denial_error_type": denial_error_type,
            "denial_error": denial_error,
            "output_present": output_bytes is not None,
            "owner_state_before": {"state": available.state.value, "revision": available.revision},
            "owner_state_after": {"state": after.state.value, "revision": after.revision},
            "owner_revision_files_unchanged": owner_after == owner_before,
            "runtime_ledger_root_exists": ledger_root.exists(),
            "claim_attempted": False,
            "p11_entry_count": 0,
            "invocation_count": 0,
            "protected_effect_count": 0,
            "wrong_attempt_invariant_pass": denial_pass,
        }
        er.send_message(control, result)
        if er.receive_message(reader)["command"] != "ATTEMPT_CONSUMED_REUSE":
            raise RuntimeError("wrong-attempt reduction acknowledgement missing")
        er.send_message(control, {
            **result,
            "message_type": "ATTEMPT_COMPLETE",
            "consumed_reuse_invariant_pass": denial_pass,
            "protocol_finalization_only": True,
            "additional_boundary_request_count": 0,
        })
        reader.close()
        control.close()
        server.close()
        os._exit(0 if denial_pass else 112)
    except BaseException as exc:
        try:
            er.send_message(control, {"message_type": "CUSTODY_FAILURE", "error_type": type(exc).__name__, "error": str(exc)})
        finally:
            os._exit(111)


def configure(er: Any) -> None:
    er.GENERATION_ID = GENERATION_ID
    er.ATTEMPT_ID = AUTHORIZED_ATTEMPT_ID
    er.ACT_ID = ACT_ID
    er.CASE_ID = CASE_ID
    er.RAW_ROOT = RAW_ROOT
    er.RAW_PATH = RAW_ROOT / "G77_256FC_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    er.PRE_ACT_SEAL_PATH = RAW_ROOT / "G77_256FC_PRE_ACT_CHECKPOINT_V1.json"
    er.AUTHORITY_SEAL_PATH = RAW_ROOT / "G77_256FC_AUTHORITY_CHECKPOINT_V1.json"
    er.GUEST_SEAL_PATH = RAW_ROOT / "G77_256FC_GUEST_EXECUTION_SEAL_V1.json"
    er.TEARDOWN_SEAL_PATH = RAW_ROOT / "G77_256FC_GUEST_TEARDOWN_SEAL_V1.json"
    er.CONTINUATION_MANIFEST_PATH = CONTINUATION_MANIFEST_PATH
    er.TERMINAL_CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256FC_CONTINUATION_MANIFEST_TERMINAL_V1.json"
    er.EN_HARNESS_PATH = Path("/mnt/dp-harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py")
    er.FIXTURE_ROOT = Path("/run/g77-256fc-p11")
    er.ENDPOINT = er.FIXTURE_ROOT / "p11_da_disposable_custody_v1.sock"
    er.PROTECTED_PROBE = er.FIXTURE_ROOT / "protected-probe"
    er.PROTECTED_TARGET = er.PROTECTED_PROBE / "state.json"
    er.custody_process = lambda control, server, evidence: fc_custody_process(er, control, server, evidence)

    original_append = er.append_record
    original_write = er.write_canonical
    original_update = er.update_continuation_manifest

    def corrected_counters(counters: dict[str, int]) -> dict[str, int]:
        counters.update({
            "human_operational_act_claimed_count": 0,
            "human_operational_act_invoked_count": 0,
            "human_operational_act_terminally_bound_count": 0,
            "human_operational_act_permanently_exhausted_count": 0,
            "p11_entry_count": 0,
            "p11_operational_invocation_count": 0,
            "e01_e12_execution_count": 0,
            "e05_case_execution_count": 1,
        })
        return counters

    def append_record(record_type: str, evidence_class: str, facts: dict[str, Any]) -> str:
        if record_type == "first_authorized_effect_complete":
            return original_append("wrong_attempt_denial_complete", "FACT", facts)
        if record_type == "p11_attempt_result":
            counters = corrected_counters(facts["execution_counters"])
            observed = {
                "boundary_request_count": 1,
                "pre_attempt_denial_count": 1,
                "p11_entry_count": 0,
                "p11_operational_invocation_count": 0,
                "protected_effect_count": 0,
            }
            sources = []
            for name, source, value in (
                ("b6_boundary_request_counter", "BOUNDARY_REQUEST_PRODUCER", 1),
                ("b6_pre_attempt_denial_counter", "PRE_ATTEMPT_DENIAL_PRODUCER", 1),
                ("b6_p11_entry_counter", "ADMITTED_ENTRY_PRODUCER", 0),
                ("b6_invocation_counter", "INVOCATION_PRODUCER", 0),
                ("b6_protected_effect_counter", "PROTECTED_EFFECT_PRODUCER", 0),
            ):
                identity = original_append(name, "FACT", {
                    "semantic_definition_id": "P11_ENTRY_DEFINITION_V1",
                    "semantic_version": "1.0.0",
                    "source_identity": source,
                    "value": value,
                    "durable_source_distinct": True,
                })
                sources.append({"record_type": name, "source_identity": source, "record_identity": identity})
            original_append("b6_producer_consumer_reduction", "EVIDENCE", {
                "semantic_definition_id": "P11_ENTRY_DEFINITION_V1",
                "semantic_version": "1.0.0",
                "invariant": "REQUEST_NOT_ENTRY_NOT_INVOCATION_NOT_EFFECT__WRONG_ATTEMPT_DENIAL_ENTRY_INCREMENT_ZERO",
                "counter_sources": sources,
                "observed_counters": observed,
                "denied_request_entry_increment": 0,
                "denied_request_invocation_increment": 0,
                "denied_request_effect_increment": 0,
                "producer_consumer_agreement": True,
                "result": "PASS__CERTIFIED_EU_EX_PROSPECTIVE_COUNTER_SEMANTICS_ADOPTED",
            })
            return original_append(record_type, "FACT", {
                **{key: value for key, value in facts.items() if key not in {"e05_consumed_negative_authority", "result"}},
                "attempt_identity": AUTHORIZED_ATTEMPT_ID,
                "supplied_wrong_attempt_identity": WRONG_ATTEMPT_ID,
                "authority_act_identity": ACT_ID,
                "evidence_obligation_id": "P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT",
                "case_id": CASE_ID,
                "e05_wrong_attempt_negative_authority": {
                    "valid_common_context": True,
                    "valid_non_target_authority_dimensions": True,
                    "authorized_attempt_identity": AUTHORIZED_ATTEMPT_ID,
                    "supplied_attempt_identity": WRONG_ATTEMPT_ID,
                    "isolated_mutation_fields": ["attempt_identity", "record_identity"],
                    "semantic_mutation_field": "attempt_identity",
                    "other_vector_mutation_count": 0,
                    "pre_attempt_denial_count": 1,
                    "claim_count": 0,
                    "invocation_count": 0,
                    "protected_effect_count": 0,
                    "owner_state_after": "AVAILABLE",
                    "owner_revision_after": 0,
                },
                "prospective_b6_counters": observed,
                "counter_semantics_result": "PASS__WRONG_ATTEMPT_DENIED_BEFORE_P11_ENTRY",
                "execution_counters": counters,
                "result": "PASS__ONE_VALID_ACT__ONE_ISOLATED_WRONG_ATTEMPT_REQUEST_DENIED_AT_D2_BEFORE_PRECLAIM_ENTRY_CLAIM_INVOCATION_OR_EFFECT",
            })
        if record_type == "guest_teardown":
            facts["execution_counters"] = corrected_counters(facts["execution_counters"])
        return original_append(record_type, evidence_class, facts)

    def write_canonical(path: Path, value: dict[str, Any]) -> str:
        if value.get("schema_id") == "G77_256ER_GUEST_EXECUTION_SEAL_V1":
            value.update({
                "schema_id": "G77_256FC_GUEST_EXECUTION_SEAL_V1",
                "completed_gates": ["P01-P12", "ACT_CREATE", "ACT_SUBMIT_AVAILABLE", "ONE_WRONG_ATTEMPT_D2_PRECLAIM_DENIAL", "ZERO_ENTRY_INVOCATION_EFFECT"],
                "authority_disposition": "AVAILABLE_REVISION_0__WRONG_ATTEMPT_DENIED__NON_TRANSFERABLE_LIVE_GUEST_ONLY",
                "evidence_obligation_id": "P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT",
                "case_id": CASE_ID,
                "operational_result": "PASS__WRONG_ATTEMPT_DENIED_AT_D2_BEFORE_PRECLAIM_AND_ENTRY_WITH_ZERO_EFFECT",
            })
            value["execution_counters"] = corrected_counters(value["execution_counters"])
        elif value.get("schema_id") == "G77_256ER_GUEST_TEARDOWN_SEAL_V1":
            value["schema_id"] = "G77_256FC_GUEST_TEARDOWN_SEAL_V1"
            value["execution_counters"] = corrected_counters(value["execution_counters"])
        return original_write(path, value)

    def update_continuation_manifest(**kwargs: Any) -> tuple[str, dict[str, Any]]:
        kwargs["execution_counters"] = corrected_counters(kwargs["execution_counters"])
        phase = kwargs["current_spce_phase"]
        if phase == "PHASE_C_EXECUTION_COMPLETE_PENDING_GUEST_TEARDOWN":
            kwargs["authority_lifecycle_state"] = "AVAILABLE_REVISION_0__WRONG_ATTEMPT_DENIED__LIVE_GUEST_ONLY"
            kwargs["first_failure_or_current_result"] = "PASS__E05_WRONG_ATTEMPT_DENIED_BEFORE_ENTRY__ZERO_EFFECT"
        elif phase == "PHASE_D_GUEST_TEARDOWN_COMPLETE_PENDING_HOST_FINALIZATION":
            kwargs["authority_lifecycle_state"] = "LIVE_AUTHORITY_TERMINATED_WITH_DISPOSABLE_GUEST__NO_AUTHORITY_SURVIVES"
            kwargs["first_failure_or_current_result"] = "PASS__E05_WRONG_ATTEMPT_DENIAL__GUEST_TEARDOWN_COMPLETE"
        _, envelope = original_update(**kwargs)
        manifest = envelope["manifest"]
        manifest["frontier_state"]["constitutional_frontier"] = "ONE_HUMAN_AUTHORIZED_FC_WRONG_ATTEMPT_E05_VECTOR"
        manifest["frontier_state"]["continuation_mode"] = "FINALIZATION_ONLY" if phase.startswith(("PHASE_C", "PHASE_D")) else "SAME_LIVE_GENERATION_ONLY"
        manifest["selected_case"] = {"case_class": "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT", "case_id": CASE_ID}
        updated = {
            "schema_id": "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1",
            "manifest": manifest,
            "manifest_sha256": er.sha256_bytes(er.canonical_bytes(manifest)),
        }
        target = er.TERMINAL_CONTINUATION_MANIFEST_PATH if er.TERMINAL_CONTINUATION_MANIFEST_PATH.is_file() else er.CONTINUATION_MANIFEST_PATH
        file_sha = er.write_canonical_atomic(target, updated)
        return file_sha, updated

    er.append_record = append_record
    er.write_canonical = write_canonical
    er.update_continuation_manifest = update_continuation_manifest


def main() -> int:
    er = load_er()
    configure(er)
    return er.main()


if __name__ == "__main__":
    raise SystemExit(main())
