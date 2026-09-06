from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import ast
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Iterator

import jsonschema
import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IN_ROOT = ROOT / ".github/governance/evidence/g77_256in_family_local_v2_option_b_dispatch_v1"
FORMALIZER = IN_ROOT / "analysis/G77_256IN_FAMILY_LOCAL_V2_OPTION_B_GATE_FORMALIZER_V1.py"
REPORT = IN_ROOT / "G77_256IN_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL = IN_ROOT / "G77_256IN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
DU_PATH = ROOT / ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
EB_PATH = ROOT / ".github/governance/evidence/g77_256eb_candidate_bound_validation_receipt_v2/validator/G77_256EB_CANDIDATE_BOUND_PRE_MATERIALIZATION_VALIDATOR_V2.py"
EE_PATH = ROOT / ".github/governance/evidence/g77_256ee_runtime_consumer_binding_v2/validator/G77_256EE_RUNTIME_CONSUMER_BINDING_VALIDATOR_V2.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IN = load("g77_256in_gate", FORMALIZER)
DU = load("g77_256in_du_v2", DU_PATH)
EB = load("g77_256in_eb_v2", EB_PATH)
EE = load("g77_256in_ee_v2", EE_PATH)


@contextmanager
def chain(version: int) -> Iterator[tuple[Any, Any, Any]]:
    du = DU if version == 2 else load("g77_256in_du_v1", ROOT / DU.V1_VALIDATOR_RELATIVE_PATH)
    eb = EB if version == 2 else load("g77_256in_eb_v1", ROOT / EB.V1_VALIDATOR_RELATIVE_PATH)
    ee = EE if version == 2 else load("g77_256in_ee_v1", ROOT / EE.V1_VALIDATOR_RELATIVE_PATH)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip()
    with tempfile.TemporaryDirectory(prefix=f".g77_256in_v{version}_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / f"candidate-v{version}.json"
        du_envelope = du.build_du_fixture(ROOT)
        candidate.write_bytes(du.canonical_bytes(du_envelope))
        if version == 2:
            eb_envelope = eb.validate_candidate(ROOT, candidate)
        else:
            eb_envelope = eb.validate_candidate(
                ROOT, candidate, required_head=head, required_tree=tree
            )
        eb_path = temporary / f"eb-v{version}.json"
        eb_path.write_bytes(eb.canonical_bytes(eb_envelope))
        runtime = temporary / "runtime"
        runtime.mkdir()
        runtime_name = "G77_256EC_CONTINUATION_MANIFEST_V1.json"
        (runtime / runtime_name).write_bytes(candidate.read_bytes())
        harness = ROOT / ".github/governance/evidence/g77_256ec_p11_operational_v1/harness/G77_256EC_P11_OPERATIONAL_HARNESS_V1.py"
        if version == 2:
            ee_envelope = ee.validate_binding(
                ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence"
            )
        else:
            ee_envelope = ee.validate_binding(
                ROOT, candidate, eb_path, harness, runtime, "/mnt/g77-evidence",
                required_head=head, required_tree=tree,
            )
        yield du_envelope, eb_envelope, ee_envelope


@contextmanager
def v2_assets() -> Iterator[tuple[Path, Path, Path, Path, str]]:
    with tempfile.TemporaryDirectory(prefix=".g77_256in_v2_assets_", dir=ROOT) as raw:
        temporary = Path(raw)
        candidate = temporary / "candidate-v2.json"
        candidate.write_bytes(DU.canonical_bytes(DU.build_du_fixture(ROOT)))
        eb_path = temporary / "eb-v2.json"
        eb_path.write_bytes(EB.canonical_bytes(EB.validate_candidate(ROOT, candidate)))
        runtime = temporary / "runtime"
        runtime.mkdir()
        (runtime / "G77_256EC_CONTINUATION_MANIFEST_V1.json").write_bytes(
            candidate.read_bytes()
        )
        harness = ROOT / ".github/governance/evidence/g77_256ec_p11_operational_v1/harness/G77_256EC_P11_OPERATIONAL_HARNESS_V1.py"
        yield candidate, eb_path, harness, runtime, "/mnt/g77-evidence"


def rehash(module: Any, envelope: dict[str, Any]) -> None:
    envelope["receipt_inner_sha256"] = module.sha256_bytes(
        module.canonical_bytes(envelope["receipt"])
    )


def test_exact_im_entry_ancestry_and_reconstruction() -> None:
    entry = IN.authenticate_entry(ROOT)
    assert entry["head"] == IN.IM_HEAD
    assert entry["tree"] == IN.IM_TREE
    assert entry["index"] == ""
    assert entry["recovery_classification"].startswith("VERIFIED__SAME_GENERATION")
    assert entry["uncommitted_delta"]["file_count"] == 10
    assert entry["uncommitted_delta"]["scope"].startswith("VERIFIED__EXACT_SIX")
    assert entry["nested_authority"]["head"] == IN.NESTED_HEAD
    assert entry["nested_authority"]["tree"] == IN.NESTED_TREE
    assert IN.reconstruct_im(ROOT)["inner_seal"] == "VERIFIED"


def test_human_decision_closes_im_dispatch_ambiguity() -> None:
    decision = IN.human_dispatch_decision()
    assert decision["dispatch_realization"].startswith("COLOCATED_EXPLICIT")
    assert decision["separate_dispatcher_modules"] is False
    assert decision["new_dispatcher_identities"] is False
    assert decision["human_operational_authority"] == 0


def test_preimplementation_gate_and_exact_owner_set() -> None:
    gate = IN.preimplementation_gate(ROOT)
    assert gate["pre_implementation_gate"] == "PASS__IMPLEMENTATION_ALLOWED"
    assert gate["exact_implementation_file_set"] == "VERIFIED__UNIQUE__SIX_V2_OWNER_FILES"
    assert len(IN.V2_FILES) == 6
    assert all((ROOT / path).is_file() for path in IN.V2_FILES)


def test_v1_owner_bytes_are_immutable() -> None:
    assert {
        path: IN.sha256_path(ROOT / path) for path in IN.V1_HASHES
    } == IN.V1_HASHES


@pytest.mark.parametrize("path", IN.V2_FILES[::2])
def test_v2_schema_is_valid_and_closed(path: Path) -> None:
    schema = json.loads((ROOT / path).read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False


def test_option_b_is_exactly_head_and_tree_in_eb_and_ee() -> None:
    for path in (IN.V2_FILES[2], IN.V2_FILES[4]):
        schema = json.loads((ROOT / path).read_bytes())
        receipt = schema["properties"]["receipt"]
        assert "certification_baseline" in receipt["required"]
        assert "required_head" not in receipt["required"]
        assert "required_tree" not in receipt["required"]
        baseline = receipt["properties"]["certification_baseline"]
        if "$ref" in baseline:
            baseline = schema["$defs"][baseline["$ref"].rsplit("/", 1)[-1]]
        assert baseline["required"] == ["head", "tree"]
        assert baseline["additionalProperties"] is False


def test_du_v2_positive_and_negative_self_test() -> None:
    _, evidence = DU.run_self_test(ROOT)
    assert evidence["producer_consumer_compatibility"] == "PASS"
    assert evidence["negative_case_count"] == 10
    assert all(case["result"].startswith("PASS") for case in evidence["negative_validation"])


def test_eb_and_ee_v2_complete_self_tests_and_no_caller_selected_baseline() -> None:
    assert "required_head" not in inspect.signature(EB.validate_candidate).parameters
    assert "required_tree" not in inspect.signature(EB.validate_candidate).parameters
    assert "required_head" not in inspect.signature(EE.validate_binding).parameters
    assert "required_tree" not in inspect.signature(EE.validate_binding).parameters
    assert "--required-head" not in EB_PATH.read_text()
    assert "--required-tree" not in EB_PATH.read_text()
    assert "--required-head" not in EE_PATH.read_text()
    assert "--required-tree" not in EE_PATH.read_text()
    with v2_assets() as (candidate, eb_path, harness, runtime, guest_root):
        eb_evidence = EB.run_self_test(ROOT, candidate)
        assert eb_evidence["case_count"] == 13
        assert eb_evidence["overall_self_test_result"] == "PASS"
        ee_evidence = EE.run_self_test(
            ROOT, candidate, eb_path, harness, runtime, guest_root
        )
        assert ee_evidence["case_count"] == 17
        assert ee_evidence["overall_result"] == "PASS"


def test_v1_dispatch_reachability_is_preserved() -> None:
    with chain(1) as (du, eb, ee):
        assert DU.dispatch_validate(
            du, ROOT, contract_tuple=DU.V1_CONTRACT_TUPLE
        )["structural_schema_validity"] == "PASS"
        assert EB.dispatch_verify_receipt(
            ROOT, eb, contract_tuple=EB.V1_CONTRACT_TUPLE
        )["overall_result"] == "PASS"
        assert EE.dispatch_verify_receipt(
            ROOT, ee, contract_tuple=EE.V1_CONTRACT_TUPLE
        )["schema_validity"] == "PASS"


def test_v2_chain_and_dispatch_are_valid() -> None:
    with chain(2) as (du, eb, ee):
        assert DU.dispatch_validate(
            du, ROOT, contract_tuple=DU.V2_CONTRACT_TUPLE
        )["constitutional_admissibility"] == "PASS"
        assert EB.dispatch_verify_receipt(
            ROOT, eb, contract_tuple=EB.V2_CONTRACT_TUPLE
        )["overall_result"] == "PASS"
        assert EE.dispatch_verify_receipt(
            ROOT, ee, contract_tuple=EE.V2_CONTRACT_TUPLE
        )["schema_validity"] == "PASS"
        assert eb["receipt"]["certification_baseline"] == ee["receipt"]["certification_baseline"]


@pytest.mark.parametrize("module", (DU, EB, EE))
def test_unknown_partial_mixed_downgrade_and_cross_family_tuples_reject(module: Any) -> None:
    verifier = module.dispatch_validate if module is DU else module.dispatch_verify_receipt
    valid = deepcopy(module.V2_CONTRACT_TUPLE)
    payload = DU.build_du_fixture(ROOT) if module is DU else {}
    args = (payload, ROOT) if module is DU else (ROOT, payload)
    invalid = [
        {},
        {"family": valid["family"]},
        {**valid, "version": "99.0.0"},
        {**valid, "version": "1.0.0"},
        {**valid, "family": "DU" if valid["family"] != "DU" else "EB"},
    ] + [{**valid, key: "UNKNOWN"} for key in valid if key != "family"]
    for identity_tuple in invalid:
        with pytest.raises(Exception):
            verifier(*args, contract_tuple=identity_tuple)
    with pytest.raises(TypeError):
        verifier(*args, contract_tuple=valid, version="2.0.0")
    with pytest.raises(TypeError):
        verifier(*args, contract_tuple=valid, validator="caller-selected")
    with pytest.raises(TypeError):
        verifier(*args, contract_tuple=valid, profile="caller-selected")


def test_v2_bytes_with_v1_label_and_v1_bytes_with_v2_label_reject() -> None:
    with chain(1) as v1, chain(2) as v2:
        with pytest.raises(Exception):
            DU.dispatch_validate(v2[0], ROOT, contract_tuple=DU.V1_CONTRACT_TUPLE)
        with pytest.raises(Exception):
            DU.dispatch_validate(v1[0], ROOT, contract_tuple=DU.V2_CONTRACT_TUPLE)
        with pytest.raises(Exception):
            EB.dispatch_verify_receipt(ROOT, v2[1], contract_tuple=EB.V1_CONTRACT_TUPLE)
        with pytest.raises(Exception):
            EB.dispatch_verify_receipt(ROOT, v1[1], contract_tuple=EB.V2_CONTRACT_TUPLE)
        with pytest.raises(Exception):
            EE.dispatch_verify_receipt(ROOT, v2[2], contract_tuple=EE.V1_CONTRACT_TUPLE)
        with pytest.raises(Exception):
            EE.dispatch_verify_receipt(ROOT, v1[2], contract_tuple=EE.V2_CONTRACT_TUPLE)


def test_exact_cross_family_tuple_substitutions_reject() -> None:
    payload = DU.build_du_fixture(ROOT)
    with pytest.raises(Exception):
        DU.dispatch_validate(payload, ROOT, contract_tuple=EB.V2_CONTRACT_TUPLE)
    with pytest.raises(Exception):
        DU.dispatch_validate(payload, ROOT, contract_tuple=EE.V2_CONTRACT_TUPLE)
    for module, other in (
        (EB, DU.V2_CONTRACT_TUPLE), (EB, EE.V2_CONTRACT_TUPLE),
        (EE, DU.V2_CONTRACT_TUPLE), (EE, EB.V2_CONTRACT_TUPLE),
    ):
        with pytest.raises(Exception):
            module.dispatch_verify_receipt(ROOT, {}, contract_tuple=other)


def test_non_future_wrong_attempt_vector_is_v2_contract_applicable() -> None:
    envelope = DU.build_du_fixture(ROOT)
    envelope["manifest"]["selected_case"] = {
        "case_class": "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT",
        "case_id": "G77_256IN_SYNTHETIC_NON_FUTURE_APPLICABILITY_ONLY",
    }
    envelope["manifest_sha256"] = DU.sha256_bytes(
        DU.canonical_bytes(envelope["manifest"])
    )
    result = DU.dispatch_validate(envelope, ROOT, contract_tuple=DU.V2_CONTRACT_TUPLE)
    assert result["constitutional_admissibility"] == "PASS"
    assert envelope["manifest"]["selected_case"]["case_class"] == "E05_NEGATIVE_AUTHORITY_WRONG_ATTEMPT"


def test_certification_baseline_stale_wrong_tree_nonexistent_and_open_object_reject() -> None:
    with chain(2) as (_, eb, ee):
        cases = []
        nonexistent = deepcopy(eb)
        nonexistent["receipt"]["certification_baseline"]["head"] = "0" * 40
        rehash(EB, nonexistent)
        cases.append((nonexistent, "CERTIFICATION_BASELINE_COMMIT_NONEXISTENT"))
        wrong_tree = deepcopy(eb)
        wrong_tree["receipt"]["certification_baseline"]["tree"] = "0" * 40
        rehash(EB, wrong_tree)
        cases.append((wrong_tree, "CERTIFICATION_BASELINE_TREE_MISMATCH"))
        stale = deepcopy(eb)
        old = IN.ANCESTRY[0]
        old_tree = subprocess.check_output(["git", "rev-parse", f"{old}^{{tree}}"], cwd=ROOT, text=True).strip()
        stale["receipt"]["certification_baseline"] = {"head": old, "tree": old_tree}
        rehash(EB, stale)
        cases.append((stale, "CERTIFICATION_BASELINE_STALE"))
        opened = deepcopy(eb)
        opened["receipt"]["certification_baseline"]["branch"] = IN.BRANCH
        rehash(EB, opened)
        cases.append((opened, "UNKNOWN_RECEIPT_FIELD"))
        for envelope, code in cases:
            with pytest.raises(EB.ReceiptError) as raised:
                EB.verify_receipt_envelope(ROOT, envelope)
            assert raised.value.code == code
        disagreement = deepcopy(ee)
        disagreement["receipt"]["certification_baseline"] = stale["receipt"]["certification_baseline"]
        rehash(EE, disagreement)
        with pytest.raises(EE.BindingError) as raised:
            EE.verify_receipt_envelope(ROOT, disagreement)
        assert raised.value.code == "CERTIFICATION_BASELINE_STALE"


def test_v2_receipt_parsers_reject_duplicate_keys() -> None:
    with tempfile.TemporaryDirectory(prefix=".g77_256in_duplicate_", dir=ROOT) as raw:
        path = Path(raw) / "duplicate.json"
        path.write_text('{"schema_id":"x","schema_id":"y"}\n')
        with pytest.raises(EB.ReceiptError) as eb_error:
            EB.verify_receipt_file(ROOT, path)
        assert eb_error.value.code == "DUPLICATE_KEY"
        with pytest.raises(EE.BindingError) as ee_error:
            EE.verify_receipt_file(ROOT, path)
        assert ee_error.value.code == "DUPLICATE_KEY"


def test_no_global_registry_generic_dispatcher_or_separate_dispatch_file() -> None:
    for path in (DU_PATH, EB_PATH, EE_PATH):
        source = path.read_text()
        tree = ast.parse(source)
        functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        assert any(name.startswith("dispatch_") for name in functions)
        assert "GLOBAL_VERSION_REGISTRY" not in source
        assert "GENERIC_DISPATCH_FRAMEWORK" not in source
    assert not list(ROOT.glob(".github/governance/evidence/**/*DISPATCHER*.py"))


def test_terminal_is_canonical_duplicate_safe_and_inner_sealed() -> None:
    envelope = IN.load_canonical(TERMINAL)
    assert envelope["reduction_sha256"] == IN.sha256_bytes(
        IN.canonical_bytes(envelope["reduction"])
    )
    assert envelope == IN.terminal_envelope(ROOT)


def test_g48_has_exactly_six_top_level_headings() -> None:
    headings = [line for line in REPORT.read_text().splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]


def test_operational_zero_e05_and_terminal_frontier() -> None:
    reduction = IN.terminal_reduction(ROOT)
    assert set(reduction["operational_zero"].values()) == {0}
    assert reduction["e05"]["after"] == "10/18"
    assert reduction["continuation"]["future_preoperational_readiness"] == "NOT_PROVEN"
    assert reduction["continuation"]["minimum_legal_next_delta"] == "SEPARATE_POST_COMMIT_V2_LIVE_BINDING_AND_READINESS_CERTIFICATION"
    assert reduction["ccwim"]["uncommitted_delta_recovery"].startswith("VERIFIED__EXACT_TEN_FILE")
    assert reduction["ccwim"]["worker_identity_continuity"].startswith("NOT_PROVEN")


def test_mutation_scope_is_six_owners_plus_in_evidence_and_unstaged() -> None:
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True
    ).splitlines()
    allowed = {path.as_posix() for path in IN.V2_FILES}
    for line in status:
        path = line[3:]
        assert path in allowed or path.startswith(IN.IN_ROOT.as_posix() + "/")
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
