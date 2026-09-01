#!/usr/bin/env python3
"""Repository-only authentication and reduction of completed GV evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
EVIDENCE_ROOT = REPOSITORY_ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1"
)
RUNTIME_ROOT = EVIDENCE_ROOT / "operation_state/runtime_export"
RECEIPT_ROOT = EVIDENCE_ROOT / "operation_state/receipts"
EXPECTED_HEAD = "9dc91fc93cb0d5131ecf2350211b106c60bcead5"
EXPECTED_TREE = "c01929747475bd3def8a140ec126f170d5432927"
GENERATION = (
    "G77_256GV_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_ATTEMPT_"
    "OPERATIONAL_COMMISSIONING_V1"
)
OPERATION = "G77_256GV_E05_WRONG_ATTEMPT_DENIAL_BEFORE_ENTRY_001"
REQUEST_INNER_SHA256 = (
    "2828a2a5182c77d2571e301a08fa1643a9bfd34196d023670d83b3e3eb1e7af1"
)
PRESENTATION_SHA256 = (
    "1f5aa11869862e303b7d93dead8fb32981c54e943070fc7909979abd51fc482c"
)
CHECKPOINT_INNER_SHA256 = (
    "34063831e5db8c12dd278486502a997c04ce20d80462b22eb3d7d22601475ef7"
)
HANDOFF_FILE_SHA256 = (
    "b06fb75633f496943311071298ae59d2399d1d89841d61e9909fdfcde65d63df"
)
RAW_SHA256 = "e41d9d0f666c4784a3459224cfa0fd5260bca6b187c4ef7f087c6940b77b7cc9"
SERIAL_SHA256 = (
    "3a5e53d9bc913aae8b17593de7cf0a77043006cc9aedb5261d3fe22d88d0e390"
)
CANONICAL_ARGV_SHA256 = (
    "edea95ac4bdb4c72bb41e29dcc2285eac27f9ed5d4c9d04927b3093bab6e8721"
)
EXPECTED_LINEAGE_SEALS = {
    "GP": "f8948b4ecc0a07b865d06d404e830ba216b8aa4fd841e54cae18883561d3269b",
    "GQ": "2c46a847854b566d33a679ed8bfd0b3897c3dec2c586f0b3c17bb7b14e1c62a4",
    "GR": "9f1c9d04e693a57cf494ee3bd30bd6a040a2a5b13e0fd624d3cd15e5b9debbc3",
    "GS": "76b1a282d3abcd6055cb100a6279d67cb01e3e206e86b77470be5fb98ba79f51",
    "GT": "fe28c8dedaf4afb2df0d68fd45693c162a61645d83a23e2c044d9c0ce1c3c572",
    "GU": "2bbe4a255c872a4541d111d7503c032dd964a225be4bbd696ab589404665181b",
}
LINEAGE_REDUCTIONS = {
    "GP": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gp_guest_checkout_tree_precondition_v1/G77_256GP_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GQ": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gq_guest_self_contained_checkout_v1/G77_256GQ_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GR": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gr_post_commit_live_binding_readiness_v1/G77_256GR_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GS": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gs_wrong_attempt_operational_v1/G77_256GS_SPCE_FINAL_FAIL_CLOSED_REDUCTION_V1.json",
    "GT": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gt_checkout_lifecycle_correction_v1/G77_256GT_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    "GU": REPOSITORY_ROOT / ".github/governance/evidence/g77_256gu_post_commit_live_binding_readiness_v1/G77_256GU_SPCE_FINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_unique(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def assert_inner_seal(path: Path, payload_key: str, seal_key: str) -> dict[str, Any]:
    envelope = load_unique(path)
    calculated = hashlib.sha256(canonical_bytes(envelope[payload_key])).hexdigest()
    assert envelope[seal_key] == calculated
    return envelope


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def raw_records() -> list[dict[str, Any]]:
    records = []
    raw = RUNTIME_ROOT / "G77_256GV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    for line in raw.read_text(encoding="utf-8").splitlines():
        records.append(json.loads(line, object_pairs_hook=unique_object))
    return records


def test_exact_repository_predecessor_lineage_and_seals() -> None:
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY_ROOT, text=True
    ).strip() == EXPECTED_HEAD
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=REPOSITORY_ROOT, text=True
    ).strip() == EXPECTED_TREE

    for identity, path in LINEAGE_REDUCTIONS.items():
        envelope = assert_inner_seal(path, "reduction", "reduction_sha256")
        assert envelope["reduction_sha256"] == EXPECTED_LINEAGE_SEALS[identity]

    checkpoint = assert_inner_seal(
        EVIDENCE_ROOT / "G77_256GV_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        "checkpoint",
        "checkpoint_sha256",
    )
    assert checkpoint["checkpoint_sha256"] == CHECKPOINT_INNER_SHA256
    assert checkpoint["checkpoint"]["entry_checkpoint"]["head"] == EXPECTED_HEAD
    assert checkpoint["checkpoint"]["entry_checkpoint"]["tree"] == EXPECTED_TREE
    assert checkpoint["checkpoint"]["ex"]["reused"] == "17/17"
    assert checkpoint["checkpoint"]["ex"]["reconstructed"] == 0


def test_sealed_request_presentation_human_source_and_handoff() -> None:
    request_path = EVIDENCE_ROOT / "G77_256GV_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
    presentation_path = EVIDENCE_ROOT / "G77_256GV_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
    source_path = EVIDENCE_ROOT / "G77_256GV_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
    handoff_path = EVIDENCE_ROOT / "G77_256GV_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
    presentation_owner_path = REPOSITORY_ROOT / (
        ".github/governance/evidence/g77_256gn_human_authorization_"
        "presentation_binding_v1/presentation/"
        "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
    )
    presentation_owner = load_module(presentation_owner_path, "g77_256gv_gn_owner")

    request = presentation_owner.load_validated_sealed_request(request_path)
    assert request["request_sha256"] == REQUEST_INNER_SHA256
    presentation = presentation_path.read_bytes()
    result = presentation_owner.validate_human_authorization_presentation(
        request_path, presentation
    )
    assert result["presentation_sha256"] == PRESENTATION_SHA256
    assert result["reviewed_field_count"] == 44

    source = source_path.read_text(encoding="utf-8")
    assert REQUEST_INNER_SHA256 in source
    assert PRESENTATION_SHA256 in source
    assert "exactly one fresh, explicit, one-shot, non-reusable" in source
    assert "non-transferable" in source
    assert source.rstrip().endswith("GRANT.")

    handoff = assert_inner_seal(handoff_path, "authorization", "authorization_sha256")
    assert sha256_path(handoff_path) == HANDOFF_FILE_SHA256
    authorization = handoff["authorization"]
    assert authorization["authorization_source_sha256"] == sha256_path(source_path)
    assert authorization["authorized_generation_identity"] == GENERATION
    assert authorization["authorized_operation_identity"] == OPERATION
    assert authorization["authorized_repository_head"] == EXPECTED_HEAD
    assert authorization["authorized_repository_tree"] == EXPECTED_TREE
    assert authorization["authorization_reusable"] is False
    assert authorization["auto_continuable"] is False
    assert authorization["retry_limit"] == 0
    assert authorization["repair_limit"] == 0
    assert authorization["replay_limit"] == 0


def test_live_binding_pre_post_receipts_and_exact_argv() -> None:
    candidate = EVIDENCE_ROOT / "live_binding/candidate/G77_256GV_CONTINUATION_MANIFEST_V1.json"
    live_runtime = EVIDENCE_ROOT / "live_binding/ee_runtime_projection/G77_256GV_CONTINUATION_MANIFEST_V1.json"
    operation_runtime = RUNTIME_ROOT / "G77_256GV_CONTINUATION_MANIFEST_V1.json"
    assert candidate.read_bytes() == live_runtime.read_bytes()
    assert candidate.read_bytes() == operation_runtime.read_bytes()

    assert_inner_seal(
        EVIDENCE_ROOT / "live_binding/bindings/CANDIDATE_BOUND_EB_RECEIPT_V1.json",
        "receipt",
        "receipt_inner_sha256",
    )
    ee = assert_inner_seal(
        EVIDENCE_ROOT / "live_binding/bindings/RUNTIME_CONSUMER_EE_RECEIPT_V1.json",
        "receipt",
        "receipt_inner_sha256",
    )
    assert ee["receipt"]["identity_results"] == {
        "candidate_runtime_byte_identity": "PASS",
        "candidate_runtime_semantic_identity": "PASS",
        "harness_expected_path_identity": "PASS",
    }

    pre_path = RECEIPT_ROOT / "G77_256GV_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
    post_path = RECEIPT_ROOT / "G77_256GV_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
    pre = load_unique(pre_path)
    post = load_unique(post_path)
    assert pre["vector"]["argv"] == post["vector"]["argv"]
    assert pre["vector"]["canonical_argv_sha256"] == CANONICAL_ARGV_SHA256
    assert post["vector"]["canonical_argv_sha256"] == CANONICAL_ARGV_SHA256
    canonicalizer = load_module(
        REPOSITORY_ROOT / pre["canonicalizer"]["path"],
        "g77_256gv_argv_owner",
    )
    assert canonicalizer.argv_sha256(pre["vector"]["argv"]) == CANONICAL_ARGV_SHA256
    assert pre["execution_attempt_count"] == 1
    assert post["execution_attempt_count"] == 1
    assert post["process_exit_status"] == 0
    assert pre["automatic_retry_count"] == 0
    assert post["automatic_retry_count"] == 0


def test_raw_schema_sequence_che_seals_and_independent_counter_reduction() -> None:
    records = raw_records()
    assert len(records) == 31
    assert [record["record_sequence"] for record in records] == list(range(31))
    for record in records:
        assert set(record) == {
            "schema_id", "record_sequence", "record_type", "evidence_class", "facts"
        }
        assert record["schema_id"] == "G77_256ER_RAW_EXECUTION_EVIDENCE_V1"
        assert isinstance(record["facts"], dict)
    raw_path = RUNTIME_ROOT / "G77_256GV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
    assert sha256_path(raw_path) == RAW_SHA256
    assert sha256_path(EVIDENCE_ROOT / "G77_256GV_SERIAL_CONSOLE_V1.log") == SERIAL_SHA256

    checkpoint_files = {
        14: RUNTIME_ROOT / "G77_256GV_PRE_ACT_CHECKPOINT_V1.json",
        18: RUNTIME_ROOT / "G77_256GV_AUTHORITY_CHECKPOINT_V1.json",
        28: RUNTIME_ROOT / "G77_256GV_GUEST_EXECUTION_SEAL_V1.json",
    }
    for sequence, path in checkpoint_files.items():
        assert records[sequence]["facts"]["preimage"] == load_unique(path)
        assert records[sequence]["facts"]["sha256"] == sha256_path(path)

    from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
        validate_canonical_che_evidence_correlation_v1,
    )

    correlation = validate_canonical_che_evidence_correlation_v1(
        records[16]["facts"]["che_correlation"]
    )
    assert correlation.to_dict() == records[16]["facts"]["che_correlation"]

    counter_types = [
        "b6_boundary_request_counter",
        "b6_pre_attempt_denial_counter",
        "b6_p11_entry_counter",
        "b6_invocation_counter",
        "b6_protected_effect_counter",
    ]
    expected_values = [1, 1, 0, 0, 0]
    for record, record_type, value in zip(
        records[21:26], counter_types, expected_values, strict=True
    ):
        assert record["record_type"] == record_type
        assert record["facts"]["value"] == value
        assert record["facts"]["durable_source_distinct"] is True

    reduction = records[26]["facts"]
    assert reduction["producer_consumer_agreement"] is True
    for source, record in zip(reduction["counter_sources"], records[21:26], strict=True):
        expected_identity = "sha256:" + hashlib.sha256(canonical_bytes(record)).hexdigest()
        assert source["record_identity"] == expected_identity
        assert source["record_type"] == record["record_type"]
        assert source["source_identity"] == record["facts"]["source_identity"]
    assert reduction["observed_counters"] == {
        "boundary_request_count": 1,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "pre_attempt_denial_count": 1,
        "protected_effect_count": 0,
    }

    result = records[27]["facts"]
    assert result["selected_vector"] == "P11-E05/NEGATIVE_AUTHORITY/WRONG_ATTEMPT"
    assert result["differing_input_fields"] == ["attempt_identity", "record_identity"]
    assert result["e05_wrong_attempt_negative_authority"]["other_vector_mutation_count"] == 0
    assert result["claim_attempted"] is False
    assert result["p11_entry_count"] == 0
    assert result["invocation_count"] == 0
    assert result["protected_effect_count"] == 0
    assert result["wrong_attempt_invariant_pass"] is True


def test_unchanged_fk_reducer_awards_exactly_one_e05_credit() -> None:
    source_path = REPOSITORY_ROOT / (
        ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/"
        "harness/G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    )
    source = source_path.read_text(encoding="utf-8")
    specialized: dict[str, Any] = {
        "__name__": "g77_256gv_independent_fk_reduction",
        "__file__": str(source_path),
        "__package__": None,
    }
    exec(compile(source.replace("G77_256FC", "G77_256GV"), str(source_path), "exec"), specialized)

    terminal_manifest = load_unique(
        RUNTIME_ROOT / "G77_256GV_CONTINUATION_MANIFEST_TERMINAL_V1.json"
    )
    authority = load_unique(RUNTIME_ROOT / "G77_256GV_AUTHORITY_CHECKPOINT_V1.json")
    execution = load_unique(RUNTIME_ROOT / "G77_256GV_GUEST_EXECUTION_SEAL_V1.json")
    reduced = specialized["reduce_wrong_attempt_terminal_state"](
        phase=terminal_manifest["manifest"]["current_spce_phase"],
        counters=execution["execution_counters"],
        first_failure_or_current_result=terminal_manifest["manifest"][
            "first_failure_or_current_result"
        ],
        first_failure=execution["first_failure"],
        authority_checkpoint=authority,
        execution_seal=execution,
    )
    assert reduced["success_evidence_complete"] is True
    assert reduced["e05_credit"] == 1
    assert reduced["execution_counters"]["e05_case_execution_count"] == 1
    assert reduced["execution_counters"]["p11_entry_count"] == 0
    assert reduced["execution_counters"]["p11_operational_invocation_count"] == 0


def test_guest_teardown_and_current_host_absence_with_stale_host_inner_seals() -> None:
    guest_teardown = load_unique(RUNTIME_ROOT / "G77_256GV_GUEST_TEARDOWN_SEAL_V1.json")
    assert guest_teardown["teardown_state"] == "COMPLETE"
    assert guest_teardown["raw_record_count"] == 31
    assert guest_teardown["raw_evidence_sha256"] == RAW_SHA256

    pre_path = EVIDENCE_ROOT / "G77_256GV_SPCE_HOST_PRE_TEARDOWN_CHECKPOINT_V1.json"
    teardown_path = EVIDENCE_ROOT / "G77_256GV_SPCE_HOST_TEARDOWN_CHECKPOINT_V1.json"
    pre = load_unique(pre_path)
    teardown = load_unique(teardown_path)
    pre_calculated = hashlib.sha256(canonical_bytes(pre["checkpoint"])).hexdigest()
    teardown_calculated = hashlib.sha256(canonical_bytes(teardown["checkpoint"])).hexdigest()
    assert pre["checkpoint_sha256"] == (
        "8ead3ad53c1470e33e492e32c4bc21df0edc17f7dabf5f2fe3ddc2a5c0be17da"
    )
    assert pre_calculated == (
        "a0fea946eb22412283af6f1d22574c251ec74ddddc8cf08f82996d5b01f047e9"
    )
    assert teardown["checkpoint_sha256"] == (
        "aaaae6b5fb795548b6793fc20dbf74e40190a9c5da8cb80a2cdd36485a1ddca8"
    )
    assert teardown_calculated == (
        "4d03aa48afbe22d84a6db8f37ca2e654eed7c81fda8747d3039f3df7862f094c"
    )
    assert pre["checkpoint_sha256"] != pre_calculated
    assert teardown["checkpoint_sha256"] != teardown_calculated
    assert teardown["checkpoint"]["host_pre_teardown_checkpoint"]["file_sha256"] == sha256_path(
        pre_path
    )
    assert teardown["checkpoint"]["host_pre_teardown_checkpoint"]["inner_sha256"] == pre[
        "checkpoint_sha256"
    ]
    assert teardown["checkpoint"]["host_teardown"]["transient_root_absent"] is True
    assert teardown["checkpoint"]["host_teardown"]["persistent_decisive_evidence_preserved"] is True
    assert teardown["checkpoint"]["base_image"]["byte_identical"] is True
    assert not Path("/tmp/g77_256gv_wrong_attempt_operational_v1").exists()
    base = Path(teardown["checkpoint"]["base_image"]["path"])
    assert base.is_file()
    assert sha256_path(base) == teardown["checkpoint"]["base_image"]["sha256_after"]
