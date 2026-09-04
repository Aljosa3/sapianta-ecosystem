#!/usr/bin/env python3
"""Focused repository-only proofs for G77-256HR WRONG_CONTRACT formalization."""

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
BASE = ROOT / ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1"
SPEC_PATH = BASE / "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
PRODUCER_PATH = BASE / "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
REDUCER_PATH = BASE / "reducer/G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_REDUCER_V1.py"
TERMINAL_PATH = BASE / "G77_256HR_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT_PATH = ROOT / "docs/governance/G77_256HR_REPOSITORY_ONLY_WRONG_CONTRACT_FORMALIZATION_V1.md"
HQ_INVENTORY_PATH = ROOT / (
    ".github/governance/evidence/g77_256hq_post_hp_frontier_reconnaissance_v1/"
    "G77_256HQ_E05_FRONTIER_INVENTORY_V1.json"
)
P11_CONSUMER_PATH = ROOT / "tests/p11_da_operational_consumer_v1.py"
FM_LAUNCHER_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
EX_PATH = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


PRODUCER = load_module(PRODUCER_PATH, "g77_256hr_producer_test")
REDUCER = load_module(REDUCER_PATH, "g77_256hr_reducer_test")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    result = json.loads(path.read_bytes(), object_pairs_hook=unique)
    assert isinstance(result, dict)
    return result


def produced_value() -> dict[str, Any]:
    return PRODUCER.produce_wrong_contract_vector(
        repository_root=ROOT,
        wrong_contract_identity="G77_256HR_E05_SUPPLIED_WRONG_CONTRACT_002",
    )


def produced_bytes() -> bytes:
    return PRODUCER.produce_wrong_contract_vector_bytes(
        repository_root=ROOT,
        wrong_contract_identity="G77_256HR_E05_SUPPLIED_WRONG_CONTRACT_002",
    )


def rebound_bytes(value: dict[str, Any]) -> bytes:
    supplied = value["candidate_input_record"]
    supplied["record_identity"] = REDUCER._record_identity(supplied)
    value["candidate_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        supplied
    ).decode("utf-8")
    return canonical_bytes(value)


def test_exact_hq_entry_checkpoint_frontier_and_e05_state() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "fb5c7c5e32e41e19abae4fe1290951ee37ca0648"
    )
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == (
        "16e740679ded2a34919f9e1257d33374856852e6"
    )
    inventory = load_unique(HQ_INVENTORY_PATH)
    assert inventory["e05_frontier"]["before_hq"] == inventory["e05_frontier"]["after_hq"] == "8/18"
    assert inventory["selection"]["selected_next_e05_candidate"] == "WRONG_CONTRACT"
    assert inventory["selection"]["selection_status"].endswith("NOT_IMPLEMENTED__NOT_OPERATIONAL")


def test_formal_specification_is_sealed_and_exactly_one_semantic_mutation() -> None:
    envelope = load_unique(SPEC_PATH)
    assert SPEC_PATH.read_bytes() == PRODUCER.canonical_document_bytes(envelope)
    specification = envelope["specification"]
    inner = hashlib.sha256(canonical_bytes(specification)).hexdigest()
    assert inner == envelope["specification_sha256"]
    assert inner == PRODUCER.SPECIFICATION_INNER_SHA256
    assert inner == REDUCER.FORMAL_SPECIFICATION_SHA256
    assert specification["mutation_rule"]["target_field"] == "contract_identity"
    assert specification["mutation_rule"]["semantic_mutation_count"] == 1
    assert specification["dependent_recomputation"]["fields"] == ["record_identity"]
    assert specification["expected_denial"]["contract_specific_comparison_reached"] is False
    assert set(specification["operational_counters"].values()) == {0}


def test_authenticated_source_is_structurally_valid_and_contract_bound() -> None:
    substrate = PRODUCER._load_substrate(ROOT)
    source = PRODUCER._authenticated_source(ROOT, substrate)
    validated = substrate.validate_input_record_bytes(source["input_canonical_bytes"])
    assert validated == source["input_record"]
    assert all(
        source["authorized_contract_binding"][field] == validated[field]
        for field in ("contract_identity", "contract_version", "contract_content_sha256")
    )


def test_producer_is_deterministic_and_mutates_only_contract_identity() -> None:
    first = produced_value()
    assert produced_bytes() == canonical_bytes(first) == produced_bytes()
    assert first["semantic_mutation_count"] == 1
    assert first["target_mutated_coordinate"] == "contract_identity"
    assert first["dependent_recomputation_fields"] == ["record_identity"]
    assert first["differing_input_fields"] == ["contract_identity", "record_identity"]
    assert set(first["preserved_dimension_proof"].values()) == {True}
    assert first["source_input_record"]["contract_version"] == first["candidate_input_record"]["contract_version"]
    assert first["source_input_record"]["contract_content_sha256"] == first["candidate_input_record"]["contract_content_sha256"]
    assert first["expected_error_reason"] == "operational Human act input_record_identity binding is invalid"
    with pytest.raises(PRODUCER.WrongContractProducerError, match="NOT_MUTATED"):
        PRODUCER.produce_wrong_contract_vector(
            repository_root=ROOT,
            wrong_contract_identity=first["source_input_record"]["contract_identity"],
        )
    with pytest.raises(PRODUCER.WrongContractProducerError, match="MALFORMED"):
        PRODUCER.produce_wrong_contract_vector(
            repository_root=ROOT, wrong_contract_identity=""
        )


def test_reducer_accepts_repository_vector_but_withholds_binding_and_credit() -> None:
    result = REDUCER.reduce_wrong_contract_candidate(
        produced_bytes(), repository_root=ROOT
    )
    assert result["repository_capability"] == "VERIFIED"
    assert result["binding_status"] == "NOT_PROVEN"
    assert result["preoperational_readiness"] == "NOT_PROVEN"
    assert result["operational_capability"] == "NOT_PROVEN"
    assert result["e05_credit"] == 0
    assert result["e05_before"] == result["e05_after"] == "8/18"
    assert result["auto_continuable"] is False
    assert result["human_review_required"] is True


def _no_contract_mutation(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"] = deepcopy(value["source_input_record"])
    value["candidate_input_canonical_utf8"] = value["source_input_canonical_utf8"]
    return canonical_bytes(value)


def _second_contract_coordinate(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"]["contract_version"] = "2.0.0"
    return rebound_bytes(value)


def _unrelated_input_mutation(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"]["input_identity"] = "G77_256HR_UNAUTHORIZED_INPUT_MUTATION"
    return rebound_bytes(value)


def _unauthorized_identity_recomputation(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"]["contract_content_sha256"] = "sha256:" + "0" * 64
    return rebound_bytes(value)


def _stale_record_identity(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"]["record_identity"] = value["source_input_record"]["record_identity"]
    value["candidate_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        value["candidate_input_record"]
    ).decode("utf-8")
    return canonical_bytes(value)


def _malformed_contract_identity(value: dict[str, Any]) -> bytes:
    value["candidate_input_record"]["contract_identity"] = ""
    return rebound_bytes(value)


def _invalid_source(value: dict[str, Any]) -> bytes:
    value["source_input_record"]["record_identity"] = "sha256:" + "0" * 64
    value["source_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        value["source_input_record"]
    ).decode("utf-8")
    return canonical_bytes(value)


def _unbound_provenance(value: dict[str, Any]) -> bytes:
    value["source_provenance"]["sha256"] = "0" * 64
    return canonical_bytes(value)


def _wrong_semantic_class(value: dict[str, Any]) -> bytes:
    value["selected_vector"] = "P11-E05/NEGATIVE_AUTHORITY/WRONG_INPUT"
    return canonical_bytes(value)


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (_no_contract_mutation, "CONTRACT_IDENTITY_NOT_MUTATED"),
        (_second_contract_coordinate, "MULTIPLE_OR_UNRELATED_SEMANTIC_MUTATION"),
        (_unrelated_input_mutation, "MULTIPLE_OR_UNRELATED_SEMANTIC_MUTATION"),
        (_unauthorized_identity_recomputation, "MULTIPLE_OR_UNRELATED_SEMANTIC_MUTATION"),
        (_stale_record_identity, "CANDIDATE_RECORD_IDENTITY_STALE"),
        (_malformed_contract_identity, "CANDIDATE_CONTRACT_IDENTITY_MALFORMED"),
        (_invalid_source, "SOURCE_RECORD_IDENTITY_STALE"),
        (_unbound_provenance, "SOURCE_PROVENANCE_BINDING_INVALID"),
        (_wrong_semantic_class, "MUTATION_CLASS_NOT_WRONG_CONTRACT"),
    ],
)
def test_semantic_firewall_rejects_malformed_or_broadened_vectors(
    mutator: Callable[[dict[str, Any]], bytes], code: str
) -> None:
    with pytest.raises(REDUCER.WrongContractReductionError, match=code):
        REDUCER.reduce_wrong_contract_candidate(
            mutator(produced_value()), repository_root=ROOT
        )


def test_reducer_rejects_duplicate_keys_and_noncanonical_json() -> None:
    duplicate = produced_bytes().replace(
        b'{"authority_created":false,',
        b'{"authority_created":false,"authority_created":false,',
        1,
    )
    with pytest.raises(REDUCER.WrongContractReductionError, match="DUPLICATE_JSON_KEY"):
        REDUCER.reduce_wrong_contract_candidate(duplicate, repository_root=ROOT)
    with pytest.raises(REDUCER.WrongContractReductionError, match="NOT_CANONICAL_JSON"):
        REDUCER.reduce_wrong_contract_candidate(
            json.dumps(produced_value(), indent=2).encode("utf-8"), repository_root=ROOT
        )


def test_p11_denial_order_and_contract_triple_binding_are_exact() -> None:
    source = P11_CONSUMER_PATH.read_text(encoding="utf-8")
    assert '"input_record_identity": input_record["record_identity"]' in source
    assert '"contract_identity": input_record["contract_identity"]' in source
    assert '"contract_version": input_record["contract_version"]' in source
    assert '"contract_content_sha256": input_record["contract_content_sha256"]' in source
    assert source.index('"input_record_identity": input_record["record_identity"]') < source.index(
        '"contract_identity": input_record["contract_identity"]'
    )
    validation_index = source.index("binding = self._validate_authority_sources(")
    preclaim_append_index = source.index(
        '"P11_DA_OPERATIONAL_PRECLAIM"', validation_index
    )
    assert validation_index < preclaim_append_index


def test_ex_17_of_17_reused_and_single_route_owner_preserved() -> None:
    certificate = load_unique(EX_PATH)["certificate"]
    certified = [
        item
        for item in certificate["component_certification_matrix"]
        if item["proposed_ex_classification"] == "CERTIFIED"
    ]
    assert len(certified) == 17
    launcher_tree = ast.parse(FM_LAUNCHER_PATH.read_text(encoding="utf-8"))
    main = next(
        node
        for node in launcher_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    qemu_calls = [
        node
        for node in ast.walk(main)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(qemu_calls) == 1
    assert subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD", "--", FM_LAUNCHER_PATH.relative_to(ROOT)],
        cwd=ROOT,
        text=True,
    ).strip() == ""


def test_repository_modules_expose_no_operational_call_site() -> None:
    for path in (PRODUCER_PATH, REDUCER_PATH):
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        assert "subprocess" not in source
        assert "claim_and_invoke_once(" not in source
        assert "qemu-system" not in source
        assert "PRE(" not in source


def test_terminal_artifact_and_g48_report_are_bounded_and_canonical() -> None:
    terminal = load_unique(TERMINAL_PATH)
    assert TERMINAL_PATH.read_bytes() == PRODUCER.canonical_document_bytes(terminal)
    reduction = terminal["reduction"]
    assert hashlib.sha256(canonical_bytes(reduction)).hexdigest() == terminal["reduction_sha256"]
    assert reduction["capability_status"] == {
        "binding_status": "NOT_PROVEN",
        "formal_spec_status": "VERIFIED",
        "operational_capability": "NOT_PROVEN",
        "preoperational_readiness": "NOT_PROVEN",
        "producer_status": "VERIFIED",
        "reducer_status": "VERIFIED",
        "repository_capability": "VERIFIED",
        "semantic_firewall_status": "VERIFIED",
    }
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"after": "8/18", "before": "8/18", "credit": 0}
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    assert report.rstrip().endswith(terminal["reduction"]["terminal_verdict"])
    for metric in terminal["reduction"]["required_metrics"]:
        assert metric in report
