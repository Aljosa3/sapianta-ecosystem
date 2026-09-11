from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[5]
KV = ROOT / ".github/governance/evidence/g77_256kv_current_head_operational_binding_owner_and_authority_impact_discovery_v1"
FORMALIZER = KV / "analysis/G77_256KV_BINDING_OWNER_DISCOVERY_FORMALIZER_V1.py"
REDUCTION = KV / "G77_256KV_SPCE_TERMINAL_BINDING_OWNER_DISCOVERY_V1.json"
REPORT = KV / "G77_256KV_G48_IMPLEMENTATION_REPORT_V1.md"


def load_formalizer():
    specification = importlib.util.spec_from_file_location("g77_256kv_formalizer", FORMALIZER)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_entry_nested_authority_and_kn_ku_chain_authenticate() -> None:
    module = load_formalizer()
    entry = module.authenticate_entry()
    chain = module.authenticate_kn_ku()
    assert entry["head"] == module.HEAD
    assert entry["remote_equality"].startswith("VERIFIED__")
    assert entry["nested_authority"]["detached"] is True
    assert chain["context"]["repository_head"] == module.KN_HEAD
    assert chain["handoff"]["authorized_repository_head"] == module.KN_HEAD
    assert chain["ku"]["phase_b_started"] is False
    assert set(chain["ku"]["operational_counters"].values()) == {0}


def test_existing_owner_is_authority_free_and_does_not_rebind_old_act() -> None:
    module = load_formalizer()
    owners = module.authenticate_fm_and_post_commit_owner()
    assert owners["repository_readiness_is_authority"] == "VERIFIED__NO"
    assert owners["old_authority_rebinding_owner"].startswith("NOT_PROVEN__")
    assert owners["final_admission_owner"] == "FM_VALIDATE_EXECUTION_ADMISSION"


def test_successful_precedents_bind_authority_and_execution_to_same_head() -> None:
    precedents = load_formalizer().authenticate_success_precedents()
    assert [item["precedent"] for item in precedents] == [
        "HP_WRONG_INPUT", "HX_WRONG_CONTRACT", "IC_WRONG_PROVENANCE"
    ]
    for item in precedents:
        assert item["human_authority_head"] == item["preconsumption_binding_head"] == item["execution_head"]
        assert item["authority_rebound"] == "VERIFIED__NO"
        assert item["authority_consumed"] == item["operation_succeeded"] == "VERIFIED__YES"


def test_terminal_classification_lifecycle_and_authority_impact() -> None:
    reduction = load_formalizer().build_reduction()
    assert reduction["terminal"] == load_formalizer().TERMINAL
    assert reduction["failure_novelty_and_convergence_check"]["failure_class"] == "EVIDENCE_OR_REPORTING_DEFECT"
    assert reduction["existing_owner_mechanism_decision"]["result"] == "B__EXISTING_MECHANISM_FOUND_BUT_NOT_APPLICABLE_TO_KN"
    assert reduction["authority_impact_analysis"]["does_it_require_new_human_act"] == "VERIFIED__YES"
    assert reduction["authority_impact_analysis"]["does_it_create_authority_transfer"] == "VERIFIED__NO"
    assert reduction["circular_binding_check"]["circular_binding_status"].startswith("VERIFIED__RESOLVED")
    assert len(reduction["repository_binding_lifecycle"]) == 5


def test_terminal_reduction_is_canonical_sealed_and_deterministic() -> None:
    module = load_formalizer()
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    reduction = envelope["reduction"]
    assert raw == module.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(module.canonical_bytes(reduction)).hexdigest()
    assert reduction == module.build_reduction()
    assert reduction["phase_b_started"] is reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_e05_ex_architecture_and_zero_counters_are_preserved() -> None:
    reduction = load_formalizer().load_envelope(REDUCTION, "reduction")
    assert reduction["e05"] == {
        "state": "VERIFIED__11_OF_18", "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
        "credit": "VERIFIED__0", "kn_e05_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY",
    }
    assert reduction["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}
    assert set(reduction["operational_counters"].values()) == {0}
    assert len(reduction["operational_counters"]) == 15
    architecture = reduction["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert set(value for key, value in architecture.items() if key.endswith("_count")) == {0}


def test_formalizer_has_no_authority_or_operational_path() -> None:
    source = FORMALIZER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "consume" not in functions and "consume_and_operate" not in functions
    assert "qemu-system" not in source
    assert "subprocess.Popen" not in source
    assert source.count("subprocess.run(") == 1
    assert '["git", "merge-base", "--is-ancestor"' in source


def test_python_ast_and_exact_g48_ria_structure() -> None:
    ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# (.+)$", report, flags=re.MULTILINE) == [
        "1. Implementation Summary", "2. Code Evidence", "3. Constitutional Self-Assessment",
        "4. Validation Matrix", "5. Repository Mutation Summary", "6. Certification Verdict",
    ]
    assert re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE) == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
