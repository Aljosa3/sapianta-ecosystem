#!/usr/bin/env python3
"""Focused repository-only proofs for the G77-256GY WRONG_INPUT case."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1"
SPEC_PATH = BASE / "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1.json"
CANDIDATE_PATH = BASE / "candidate/G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1.json"
PRODUCER_PATH = BASE / "producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
REDUCER_PATH = BASE / "reducer/G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_REDUCER_V1.py"
BINDING_PATH = BASE / "binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
TERMINAL_PATH = BASE / "G77_256GY_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT_PATH = ROOT / "docs/governance/G77_256GY_REPOSITORY_ONLY_WRONG_INPUT_FORMALIZATION_V1.md"
GV_RAW_PATH = ROOT / (
    ".github/governance/evidence/g77_256gv_wrong_attempt_operational_v1/"
    "operation_state/runtime_export/G77_256GV_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
GD_TEMPLATE_PATH = ROOT / (
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/candidate/"
    "G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
GF_PATH = ROOT / (
    ".github/governance/evidence/g77_256gf_post_commit_live_binding_v1/binding/"
    "G77_256GF_POST_COMMIT_LIVE_EXECUTION_BINDING_V1.py"
)
DU_PATH = ROOT / (
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v1/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V1.py"
)
SUBSTRATE_PATH = ROOT / "tests/p11_da_disposable_substrate_v1.py"
CONSUMER_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


PRODUCER = load_module(PRODUCER_PATH, "g77_256gy_producer_test")
REDUCER = load_module(REDUCER_PATH, "g77_256gy_reducer_test")
BINDING = load_module(BINDING_PATH, "g77_256gy_binding_test")
DU = load_module(DU_PATH, "g77_256gy_du_test")
SUBSTRATE = load_module(SUBSTRATE_PATH, "g77_256gy_substrate_test")


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(value, dict)
    return value


def authorized_input_bytes() -> bytes:
    for line in GV_RAW_PATH.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("record_type") == "wrong_attempt_denial_complete":
            return SUBSTRATE.bind_record_identity(record["facts"]["authorized_input_record"])
    raise AssertionError("authenticated GV baseline input not found")


def produced_request() -> dict[str, Any]:
    return PRODUCER.produce_wrong_input_request(
        repository_root=ROOT,
        authorized_input_canonical_bytes=authorized_input_bytes(),
        wrong_input_identity="G77_256GY_E05_SUPPLIED_WRONG_INPUT_002",
        request_identity="G77_256GY_WRONG_INPUT_CUSTODY_REQUEST_001",
    )


def complete_evidence() -> dict[str, Any]:
    request = produced_request()
    provenance_facts = {
        "case_id": PRODUCER.CASE_ID,
        "selected_vector": PRODUCER.SELECTED_VECTOR,
        "request_identity": request["request_identity"],
        "evidence_provenance": REDUCER.EVIDENCE_PROVENANCE,
    }
    raw_records = [
        {"record_type": "wrong_input_request", "facts": dict(provenance_facts)},
        {"record_type": "wrong_input_denial_complete", "facts": dict(provenance_facts)},
        {"record_type": "request_counter", "facts": {"count": 1}},
        {"record_type": "p11_entry_counter", "facts": {"count": 0}},
        {"record_type": "protected_invocation_counter", "facts": {"count": 0}},
        {"record_type": "protected_effect_counter", "facts": {"count": 0}},
    ]
    return {
        "schema_id": "G77_256GY_WRONG_INPUT_OPERATIONAL_EVIDENCE_V1",
        "case_id": PRODUCER.CASE_ID,
        "selected_vector": PRODUCER.SELECTED_VECTOR,
        "formal_specification_identity": REDUCER.FORMAL_SPECIFICATION_IDENTITY,
        "formal_specification_sha256": REDUCER.FORMAL_SPECIFICATION_SHA256,
        "candidate_identity": REDUCER.CANDIDATE_IDENTITY,
        "evidence_provenance": REDUCER.EVIDENCE_PROVENANCE,
        "request_identity": request["request_identity"],
        "authorized_input_record": request["authorized_input_record"],
        "supplied_input_record": request["supplied_input_record"],
        "differing_input_fields": request["differing_input_fields"],
        "semantic_mutation_field": request["target_mutated_coordinate"],
        "dependent_recomputation_fields": request["dependent_recomputation_fields"],
        "preserved_dimension_proof": request["preserved_dimension_proof"],
        "denial_boundary": request["expected_denial_boundary"],
        "denial_error_type": request["expected_error_type"],
        "denial_error_reason": request["expected_error_reason"],
        "request_count": 1,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "claim_attempted": False,
        "owner_state_unchanged": True,
        "runtime_ledger_exists": False,
        "output_present": False,
        "raw_evidence_records": raw_records,
    }


def test_exact_gx_entry_checkpoint_is_preserved() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "d9a243a0e47decf02f4f1fce7ade627bafc42e61"
    )
    assert subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True
    ).strip() == "7dc5fc912c3e43ae5c27d92bdb157f9d66f18a38"
    assert subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip() == "g77-256fl-wrong-attempt-preboot-blocker"


def test_formal_specification_is_canonical_sealed_and_complete() -> None:
    envelope = load_unique(SPEC_PATH)
    assert SPEC_PATH.read_bytes() == canonical_bytes(envelope)
    assert hashlib.sha256(canonical_bytes(envelope["specification"])).hexdigest() == envelope[
        "specification_sha256"
    ] == REDUCER.FORMAL_SPECIFICATION_SHA256
    specification = envelope["specification"]
    mutation = specification["mutation_rule"]
    assert mutation["target_mutated_coordinate"] == "input_identity"
    assert mutation["dependent_recomputations"] == ["record_identity"]
    assert mutation["dependent_recomputation_is_second_semantic_mutation"] is False
    assert mutation["semantic_mutation_count"] == 1
    expected_preserved = set(SUBSTRATE.INPUT_FIELDS) - {"input_identity", "record_identity"}
    assert set(specification["preserved_non_target_dimensions"]) == expected_preserved
    assert set(specification["repository_only_boundary"].values()) >= {0, False, True, "7/18"}


def test_producer_is_deterministic_and_mutates_one_semantic_coordinate() -> None:
    first = produced_request()
    second = produced_request()
    assert canonical_bytes(first) == canonical_bytes(second)
    assert first["semantic_mutation_count"] == 1
    assert first["target_mutated_coordinate"] == "input_identity"
    assert first["dependent_recomputation_fields"] == ["record_identity"]
    assert first["differing_input_fields"] == ["input_identity", "record_identity"]
    assert first["authorized_input_record"]["input_identity"] != first["supplied_input_record"]["input_identity"]
    assert first["authorized_input_record"]["record_identity"] != first["supplied_input_record"]["record_identity"]
    assert SUBSTRATE.validate_input_record_bytes(
        first["supplied_input_canonical_utf8"].encode("utf-8")
    ) == first["supplied_input_record"]
    assert set(first["preserved_dimension_proof"].values()) == {True}
    with pytest.raises(PRODUCER.WrongInputProducerError, match="NOT_DISTINCT"):
        PRODUCER.produce_wrong_input_request(
            repository_root=ROOT,
            authorized_input_canonical_bytes=authorized_input_bytes(),
            wrong_input_identity=first["authorized_input_record"]["input_identity"],
            request_identity="G77_256GY_WRONG_INPUT_CUSTODY_REQUEST_001",
        )


def test_existing_p11_owner_proves_dependent_recomputation_and_d2_reason() -> None:
    consumer = CONSUMER_PATH.read_text(encoding="utf-8")
    assert '"input_record_identity": input_record["record_identity"]' in consumer
    assert '"input_payload_identity": input_record["input_identity"]' in consumer
    assert '_fail(f"operational Human act {field_name} binding is invalid")' in consumer
    assert consumer.index("input_record = validate_input_record_bytes") < consumer.index(
        "self._append_operational_event(\n            \"P11_DA_OPERATIONAL_PRECLAIM\""
    )


def test_candidate_is_canonical_du_valid_and_semantically_distinct() -> None:
    candidate = load_unique(CANDIDATE_PATH)
    assert CANDIDATE_PATH.read_bytes() == canonical_bytes(candidate)
    assert candidate == PRODUCER.build_candidate(ROOT)
    assert set(DU.validate_envelope(candidate, ROOT, expected_head=candidate["manifest"]["required_head"]).values()) == {"PASS"}
    assert hashlib.sha256(CANDIDATE_PATH.read_bytes()).hexdigest() == BINDING.TEMPLATE_SHA256
    assert BINDING.semantic_sha256(candidate) == BINDING.TEMPLATE_SEMANTIC_SHA256
    gd = load_unique(GD_TEMPLATE_PATH)
    assert gd["manifest"]["selected_case"]["case_class"] == "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
    assert candidate["manifest"]["selected_case"]["case_class"] == "E05_NEGATIVE_AUTHORITY_WRONG_INPUT"
    assert candidate["manifest"]["selected_case"] != gd["manifest"]["selected_case"]
    gf = load_module(GF_PATH, "g77_256gy_gf_firewall")
    assert gf.authenticate_certified_template(ROOT) == gd


def test_candidate_semantics_changed_guard_rejects_relabeling() -> None:
    template = load_unique(CANDIDATE_PATH)
    changed = deepcopy(template)
    changed["manifest"]["selected_case"]["case_class"] = "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"
    changed["manifest_sha256"] = hashlib.sha256(canonical_bytes(changed["manifest"])).hexdigest()
    with pytest.raises(BINDING.WrongInputBindingError, match="CANDIDATE_SEMANTICS_CHANGED"):
        BINDING.validate_candidate_semantics(changed, template)
    rebound = deepcopy(template)
    rebound["manifest"]["required_head"] = "1" * 40
    rebound["manifest"]["source_tree"] = "2" * 40
    rebound["manifest_sha256"] = hashlib.sha256(canonical_bytes(rebound["manifest"])).hexdigest()
    BINDING.validate_candidate_semantics(rebound, template)


def test_post_commit_binding_refuses_uncommitted_gy_identity() -> None:
    with pytest.raises(BINDING.WrongInputBindingError, match="POST_COMMIT_LIVE_BINDING_REQUIRED"):
        BINDING.build_post_commit_candidate(ROOT)
    assert BINDING.BINDING_CLASSIFICATION.startswith("NEW_VECTOR_SPECIFIC_BINDING_OWNER_REQUIRED")


def test_terminal_reducer_accepts_complete_packet_but_awards_no_credit() -> None:
    result = REDUCER.reduce_wrong_input_terminal_evidence(complete_evidence())
    assert result["terminal_acceptance"].startswith("PASS__COMPLETE_WRONG_INPUT")
    assert result["e05_credit"] == 0
    assert result["repository_only_generation"] is True
    assert result["auto_continuable"] is False
    assert result["human_review_required"] is True


def _delete_field(value: dict[str, Any]) -> None:
    value.pop("preserved_dimension_proof")


def _second_semantic_mutation(value: dict[str, Any]) -> None:
    supplied = value["supplied_input_record"]
    supplied["attempt_identity"] = "G77_256GY_UNAUTHORIZED_SECOND_MUTATION"
    supplied["record_identity"] = REDUCER._record_identity(supplied)
    value["differing_input_fields"] = ["attempt_identity", "input_identity", "record_identity"]


def _raw_provenance_drift(value: dict[str, Any]) -> None:
    value["raw_evidence_records"][0]["facts"]["evidence_provenance"] = "UNBOUND"


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (_delete_field, "EVIDENCE_FIELDS_INCOMPLETE_OR_UNKNOWN"),
        (lambda value: value.update(semantic_mutation_field="attempt_identity"), "SEMANTIC_MUTATION_FIELD_INVALID"),
        (_second_semantic_mutation, "DECLARED_MUTATION_IDENTITY_INVALID"),
        (lambda value: value.update(dependent_recomputation_fields=[]), "DEPENDENT_RECOMPUTATION_INVALID"),
        (lambda value: value["preserved_dimension_proof"].pop("attempt_identity"), "PRESERVED_DIMENSION_SET_INVALID"),
        (lambda value: value.update(denial_boundary="D3"), "P11_DENIAL_BOUNDARY_INVALID"),
        (lambda value: value.update(p11_entry_count=1), "UNEXPECTED_P11_ENTRY"),
        (lambda value: value.update(protected_invocation_count=1), "UNEXPECTED_PROTECTED_INVOCATION"),
        (lambda value: value.update(protected_effect_count=1), "UNEXPECTED_PROTECTED_EFFECT"),
        (lambda value: value.update(formal_specification_sha256="0" * 64), "FORMAL_SPECIFICATION_SHA256_MISMATCH"),
        (lambda value: value.update(candidate_identity="WRONG_ATTEMPT_TEMPLATE"), "CANDIDATE_IDENTITY_MISMATCH"),
        (lambda value: value.update(evidence_provenance="UNBOUND"), "EVIDENCE_PROVENANCE_MISMATCH"),
        (_raw_provenance_drift, "RAW_EVIDENCE_PROVENANCE_INVALID"),
        (lambda value: value.update(raw_evidence_records=[]), "RAW_EVIDENCE_MISSING"),
    ],
)
def test_terminal_reducer_rejects_incomplete_or_reinterpreted_evidence(
    mutator: Callable[[dict[str, Any]], None], code: str
) -> None:
    evidence = complete_evidence()
    mutator(evidence)
    with pytest.raises(REDUCER.WrongInputReductionError, match=code):
        REDUCER.reduce_wrong_input_terminal_evidence(evidence)


def test_repository_only_modules_have_zero_operational_call_sites() -> None:
    for path in (PRODUCER_PATH, REDUCER_PATH, BINDING_PATH):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        assert calls == []
        assert "qemu-system" not in source
        assert "claim_and_invoke_once(" not in source
    assert "invoke through focused tests or the post-commit binder" in PRODUCER_PATH.read_text(encoding="utf-8")
    assert "no CLI operational entry point" in REDUCER_PATH.read_text(encoding="utf-8")
    assert "no operational CLI entry point" in BINDING_PATH.read_text(encoding="utf-8")


def test_terminal_reduction_and_g48_report_are_canonical_and_consistent() -> None:
    envelope = load_unique(TERMINAL_PATH)
    assert TERMINAL_PATH.read_bytes() == canonical_bytes(envelope)
    assert set(envelope) == {"schema_id", "reduction", "reduction_sha256"}
    assert hashlib.sha256(canonical_bytes(envelope["reduction"])).hexdigest() == envelope[
        "reduction_sha256"
    ]
    reduction = envelope["reduction"]
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "7/18"
    assert reduction["capability_status"]["post_commit_live_binding_status"] == (
        "REQUIRED_AFTER_HUMAN_COMMIT"
    )
    assert reduction["capability_status"]["preoperational_readiness_status"] == "NOT_PROVEN"
    report = REPORT_PATH.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(reduction["terminal_control"]["verdict"])
    assert "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?" in report
