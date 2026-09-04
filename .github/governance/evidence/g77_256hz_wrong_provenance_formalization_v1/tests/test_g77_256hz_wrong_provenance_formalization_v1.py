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


ROOT = Path(__file__).resolve().parents[5]
EVIDENCE_ROOT = ROOT / ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1"
PRODUCER_PATH = EVIDENCE_ROOT / "producer/G77_256HZ_WRONG_PROVENANCE_VECTOR_PRODUCER_V1.py"
REDUCER_PATH = EVIDENCE_ROOT / "reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
SPEC_PATH = EVIDENCE_ROOT / "G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_V1.json"
TERMINAL_PATH = EVIDENCE_ROOT / "G77_256HZ_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT_PATH = ROOT / "docs/governance/G77_256HZ_REPOSITORY_ONLY_WRONG_PROVENANCE_FORMALIZATION_V1.md"
HY_REPORT_PATH = ROOT / "docs/governance/G77_256HY_AUTHENTICATED_E05_9_OF_18_FRONTIER_SELECTION_MINIMUM_DELTA_REUSE_ANALYSIS_AND_NEXT_OBLIGATION_DESIGN_V1.md"
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


PRODUCER = load_module(PRODUCER_PATH, "g77_256hz_producer_test")
REDUCER = load_module(REDUCER_PATH, "g77_256hz_reducer_test")


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
    return PRODUCER.produce_wrong_provenance_vector(
        repository_root=ROOT,
        wrong_provenance_identity="G77_256HZ_SUPPLIED_WRONG_PROVENANCE_002",
    )


def produced_bytes() -> bytes:
    return PRODUCER.produce_wrong_provenance_vector_bytes(
        repository_root=ROOT,
        wrong_provenance_identity="G77_256HZ_SUPPLIED_WRONG_PROVENANCE_002",
    )


def rebound_bytes(value: dict[str, Any]) -> bytes:
    supplied = value["supplied_input_record"]
    supplied["record_identity"] = REDUCER._record_identity(supplied)
    value["supplied_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        supplied
    ).decode("utf-8")
    return canonical_bytes(value)


def test_exact_hy_entry_checkpoint_and_reconstructed_e05_selection() -> None:
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == (
        "451fafdeafc935c352a27f75fbddb473423ce7b3"
    )
    assert subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip() == (
        "98a5f94880cae12e91ab3173fad36de8c90d0d23"
    )
    report = HY_REPORT_PATH.read_text(encoding="utf-8")
    assert "E05_BEFORE_HY = 9/18" in report
    assert "E05_AFTER_HY = 9/18" in report
    assert "SELECTED_NEXT_E05_VECTOR = WRONG_PROVENANCE" in report


def test_formal_specification_is_canonical_sealed_and_exactly_bounded() -> None:
    envelope = load_unique(SPEC_PATH)
    assert SPEC_PATH.read_bytes() == PRODUCER.canonical_document_bytes(envelope)
    specification = envelope["specification"]
    inner = hashlib.sha256(canonical_bytes(specification)).hexdigest()
    assert inner == envelope["specification_sha256"]
    assert inner == PRODUCER.SPECIFICATION_INNER_SHA256
    assert inner == REDUCER.FORMAL_SPECIFICATION_SHA256
    mutation = specification["mutation_rule"]
    assert mutation["independent_mutation_count"] == 1
    assert mutation["independent_mutated_coordinate"] == "provenance_identity"
    assert mutation["dependent_recomputation_count"] == 1
    assert mutation["dependent_recomputed_coordinate"] == "record_identity"
    assert specification["expected_denial"]["provenance_specific_comparison_reached"] is False
    assert set(specification["operational_counters"].values()) == {0}


def test_authoritative_source_is_protected_owner_and_uniquely_resolved() -> None:
    substrate = PRODUCER._load_substrate(ROOT)
    source = PRODUCER._authenticated_source(ROOT, substrate)
    resolution = source["resolution"]
    assert resolution["authoritative_owner_identity"] == "AUTHORITY_CUSTODY_PROCESS_PRINCIPAL"
    assert resolution["source_observation_count"] == 2
    assert source["input_record"]["provenance_identity"] == resolution["authoritative_provenance_identity"]
    assert {item["record_sequence"] for item in source["observations"]} == {17, 18}
    assert {item["source_role"] for item in source["observations"]} == {
        "PROTECTED_CUSTODY_OWNER_STATE"
    }


def test_producer_is_deterministic_and_mutates_only_provenance() -> None:
    first = produced_value()
    assert produced_bytes() == canonical_bytes(first) == produced_bytes()
    assert first["independent_mutation_count"] == 1
    assert first["independent_mutated_coordinate"] == "provenance_identity"
    assert first["dependent_recomputation_count"] == 1
    assert first["dependent_recomputed_coordinate"] == "record_identity"
    assert first["differing_input_fields"] == ["provenance_identity", "record_identity"]
    assert set(first["preserved_independent_coordinate_proof"].values()) == {True}
    assert first["baseline_input_record"]["provenance_identity"] == (
        first["authoritative_provenance_resolution"]["authoritative_provenance_identity"]
    )
    assert first["supplied_input_record"]["provenance_identity"] != (
        first["authoritative_provenance_resolution"]["authoritative_provenance_identity"]
    )
    with pytest.raises(PRODUCER.WrongProvenanceProducerError, match="NOT_MUTATED"):
        PRODUCER.produce_wrong_provenance_vector(
            repository_root=ROOT,
            wrong_provenance_identity=first["baseline_input_record"]["provenance_identity"],
        )


def test_reducer_accepts_repository_vector_but_withholds_route_operation_and_credit() -> None:
    result = REDUCER.reduce_wrong_provenance_candidate(
        produced_bytes(), repository_root=ROOT
    )
    assert result["repository_capability"] == "VERIFIED"
    assert result["authoritative_provenance_resolution"].startswith("VERIFIED")
    assert result["route_support"] == "NOT_PROVEN"
    assert result["binding_status"] == "NOT_PROVEN"
    assert result["preoperational_readiness"] == "NOT_PROVEN"
    assert result["operational_capability"] == "NOT_PROVEN"
    assert result["e05_credit"] == 0
    assert result["e05_before"] == result["e05_after"] == "9/18"


def _no_provenance_mutation(value: dict[str, Any]) -> bytes:
    value["supplied_input_record"] = deepcopy(value["baseline_input_record"])
    value["supplied_input_canonical_utf8"] = value["baseline_input_canonical_utf8"]
    return canonical_bytes(value)


def _wrong_target_coordinate(value: dict[str, Any]) -> bytes:
    value["supplied_input_record"]["provenance_identity"] = value["baseline_input_record"]["provenance_identity"]
    value["supplied_input_record"]["input_identity"] = "G77_256HZ_UNAUTHORIZED_WRONG_TARGET"
    return rebound_bytes(value)


def _second_independent_mutation(value: dict[str, Any]) -> bytes:
    value["supplied_input_record"]["input_identity"] = "G77_256HZ_UNAUTHORIZED_SECOND_MUTATION"
    return rebound_bytes(value)


def _stale_record_identity(value: dict[str, Any]) -> bytes:
    value["supplied_input_record"]["record_identity"] = value["baseline_input_record"]["record_identity"]
    value["supplied_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        value["supplied_input_record"]
    ).decode("utf-8")
    return canonical_bytes(value)


def _baseline_provenance_mismatch(value: dict[str, Any]) -> bytes:
    baseline = value["baseline_input_record"]
    baseline["provenance_identity"] = "G77_256HZ_FALSE_BASELINE_PROVENANCE"
    baseline["record_identity"] = REDUCER._record_identity(baseline)
    value["baseline_input_canonical_utf8"] = REDUCER._canonical_record_bytes(
        baseline
    ).decode("utf-8")
    return canonical_bytes(value)


def _wrong_generation(value: dict[str, Any]) -> bytes:
    value["generation_identity"] = "G77_256IA_NOT_HZ"
    return canonical_bytes(value)


def _wrong_base(value: dict[str, Any]) -> bytes:
    value["base_head"] = "0" * 40
    return canonical_bytes(value)


def _wrong_vector(value: dict[str, Any]) -> bytes:
    value["selected_vector"] = "P11-E05/NEGATIVE_AUTHORITY/WRONG_INPUT"
    return canonical_bytes(value)


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (_no_provenance_mutation, "PROVENANCE_IDENTITY_NOT_MUTATED"),
        (_wrong_target_coordinate, "PROVENANCE_IDENTITY_NOT_MUTATED"),
        (_second_independent_mutation, "MULTIPLE_OR_UNRELATED_INDEPENDENT_MUTATION"),
        (_stale_record_identity, "SUPPLIED_RECORD_IDENTITY_STALE"),
        (_baseline_provenance_mismatch, "BASELINE_INPUT_NOT_AUTHENTICATED"),
        (_wrong_generation, "GENERATION_IDENTITY_MISMATCH"),
        (_wrong_base, "BASE_HEAD_MISMATCH"),
        (_wrong_vector, "MUTATION_CLASS_NOT_WRONG_PROVENANCE"),
    ],
)
def test_semantic_firewall_rejects_unisolated_stale_or_misbound_vectors(
    mutator: Callable[[dict[str, Any]], bytes], code: str
) -> None:
    with pytest.raises(REDUCER.WrongProvenanceReductionError, match=code):
        REDUCER.reduce_wrong_provenance_candidate(
            mutator(produced_value()), repository_root=ROOT
        )


def test_missing_authoritative_provenance_source_rejects() -> None:
    with pytest.raises(
        REDUCER.WrongProvenanceReductionError,
        match="AUTHORITATIVE_PROVENANCE_SOURCE_MISSING",
    ):
        REDUCER.resolve_authoritative_provenance([])


def test_conflicting_authoritative_provenance_resolution_rejects() -> None:
    observations = deepcopy(
        produced_value()["authoritative_provenance_resolution"]["observations"]
    )
    observations[1]["provenance_identity"] = "G77_256HZ_CONFLICTING_PROVENANCE"
    with pytest.raises(
        REDUCER.WrongProvenanceReductionError,
        match="AUTHORITATIVE_PROVENANCE_RESOLUTION_AMBIGUOUS",
    ):
        REDUCER.resolve_authoritative_provenance(observations)


def test_supplied_provenance_cannot_become_authoritative_source() -> None:
    observations = deepcopy(
        produced_value()["authoritative_provenance_resolution"]["observations"]
    )
    observations[0]["source_role"] = "SUPPLIED_INPUT"
    with pytest.raises(
        REDUCER.WrongProvenanceReductionError,
        match="SUPPLIED_PROVENANCE_CANNOT_BE_AUTHORITATIVE",
    ):
        REDUCER.resolve_authoritative_provenance(observations)


def test_candidate_provenance_proof_tamper_rejects() -> None:
    value = produced_value()
    value["authoritative_provenance_resolution"]["observations"] = []
    with pytest.raises(
        REDUCER.WrongProvenanceReductionError,
        match="AUTHORITATIVE_PROVENANCE_PROOF_INVALID",
    ):
        REDUCER.reduce_wrong_provenance_candidate(
            canonical_bytes(value), repository_root=ROOT
        )


def test_reducer_rejects_duplicate_keys_noncanonical_and_malformed_json() -> None:
    duplicate = produced_bytes().replace(
        b'"authority_created":false,',
        b'"authority_created":false,"authority_created":false,',
        1,
    )
    with pytest.raises(REDUCER.WrongProvenanceReductionError, match="DUPLICATE_JSON_KEY"):
        REDUCER.reduce_wrong_provenance_candidate(duplicate, repository_root=ROOT)
    with pytest.raises(REDUCER.WrongProvenanceReductionError, match="NOT_CANONICAL_JSON"):
        REDUCER.reduce_wrong_provenance_candidate(
            json.dumps(produced_value(), indent=2).encode("utf-8"),
            repository_root=ROOT,
        )
    with pytest.raises(REDUCER.WrongProvenanceReductionError, match="NOT_CANONICAL_JSON"):
        REDUCER.reduce_wrong_provenance_candidate(b"{", repository_root=ROOT)


def test_p11_denial_order_and_provenance_binding_reachability_are_exact() -> None:
    source = P11_CONSUMER_PATH.read_text(encoding="utf-8")
    payload_function = source[source.index("def validate_operational_act_payload("):]
    record_check = payload_function.index('"input_record_identity": input_record["record_identity"]')
    binding_return = payload_function.index("return AuthorityBinding(")
    protected_compare = source.index("if binding != available.binding:")
    preclaim_append = source.index('"P11_DA_OPERATIONAL_PRECLAIM"', protected_compare)
    assert record_check < binding_return
    assert binding_return < protected_compare < preclaim_append
    assert 'provenance_identity=input_record["provenance_identity"]' in source
    assert 'PRECLAIM authority binding differs from protected custody' in source


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
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"] == {"after": "9/18", "before": "9/18", "credit": 0}
    assert reduction["ex"] == {"reconstructed": 0, "reused": "17/17"}
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    for metric in reduction["required_metrics"]:
        assert metric in report
    assert report.rstrip().endswith(reduction["terminal_verdict"])
