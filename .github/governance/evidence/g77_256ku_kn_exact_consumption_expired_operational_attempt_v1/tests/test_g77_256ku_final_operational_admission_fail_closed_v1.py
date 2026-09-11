from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
KU = ROOT / ".github/governance/evidence/g77_256ku_kn_exact_consumption_expired_operational_attempt_v1"
ASSESSOR = KU / "analysis/G77_256KU_FINAL_OPERATIONAL_ADMISSION_ASSESSOR_V1.py"
REDUCTION = KU / "G77_256KU_SPCE_TERMINAL_FINAL_ADMISSION_FAIL_CLOSED_V1.json"
REPORT = KU / "G77_256KU_G48_IMPLEMENTATION_REPORT_V1.md"


def load_assessor():
    specification = importlib.util.spec_from_file_location("g77_256ku_test_assessor", ASSESSOR)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_entry_human_source_and_kt_terminal_authenticate() -> None:
    module = load_assessor()
    module.authenticate_entry()
    _, context, handoff, binding = module.authenticate_inputs()
    assert context["repository_head"] == module.CONTEXT_HEAD
    assert handoff["authorization"]["authorized_repository_head"] == module.CONTEXT_HEAD
    assert binding["authority_consumption_count"] == 0
    assert hashlib.sha256(module.SOURCE.read_bytes()).hexdigest() == module.SOURCE_SHA256


def test_handoff_and_binding_are_exact_canonical_committed_kt_inputs() -> None:
    module = load_assessor()
    fm, _, handoff, binding = module.authenticate_inputs()
    assert len(module.HANDOFF.read_bytes()) == 1715
    assert module.sha256_path(module.HANDOFF) == module.HANDOFF_SHA256
    assert handoff["authorization_sha256"] == module.HANDOFF_INNER_SHA256
    assert module.sha256_path(module.BINDING) == module.BINDING_SHA256
    assert {binding[name] for name in (
        "authenticated_canonical_authority_digest",
        "sealed_invocation_authority_digest",
        "final_fm_argv_authority_digest",
    )} == {module.HANDOFF_SHA256}
    assert fm.parse_authority_handoff_bytes(module.HANDOFF.read_bytes()) == handoff


def test_preconsumption_namespace_is_fresh_and_all_counters_are_zero() -> None:
    module = load_assessor()
    _, context, _, _ = module.authenticate_inputs()
    module.authenticate_collision_barrier(context)
    assert all(not path.exists() and not path.is_symlink() for path in (
        module.CONSUMPTION, module.INVOCATION, module.RESULT, module.PHASE_B_CHECKPOINT,
    ))
    assert len(module.zero_counters()) == 15
    assert set(module.zero_counters().values()) == {0}


def test_existing_fm_owner_rejects_stale_repository_binding_before_consumption() -> None:
    module = load_assessor()
    fm, context, handoff, _ = module.authenticate_inputs()
    assert module.CONTEXT_HEAD != module.HEAD and module.CONTEXT_TREE != module.TREE
    assert module.reproduce_final_admission_failure(fm, context, handoff) == module.FM_ADMISSION_ERROR


def test_terminal_reduction_is_canonical_sealed_and_deterministic() -> None:
    module = load_assessor()
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    reduction = envelope["reduction"]
    assert raw == module.canonical_bytes(envelope)
    assert envelope["reduction_sha256"] == hashlib.sha256(module.canonical_bytes(reduction)).hexdigest()
    assert reduction == module.build_reduction()
    assert reduction["terminal"] == module.TERMINAL
    assert reduction["phase_a"]["final_admission_status"].startswith("NOT_PROVEN__")
    assert reduction["materialized_authority"]["authority_state_after"] == "VERIFIED__GRANTED_UNCONSUMED"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["phase_b_started"] is reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_e05_ex_architecture_and_proof_yield_remain_bounded() -> None:
    reduction = load_assessor().load_envelope(REDUCTION, "reduction")
    assert reduction["e05"]["before"] == reduction["e05"]["after"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["credit"] == reduction["e05"]["kn_e05_credit"] == "VERIFIED__0"
    assert reduction["e05"]["expired"] == "NOT_PROVEN_OPERATIONALLY"
    assert reduction["ex"] == {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0"}
    architecture = reduction["architecture"]
    assert architecture["production_route_before"] == architecture["production_route_after"] == 1
    assert architecture["parallel_flow"] == "NO"
    assert set(value for key, value in architecture.items() if key.endswith("_count")) == {0}
    assert reduction["proof_yield"]["new_operational_observation_count"] == "VERIFIED__0"


def test_assessor_has_no_consumption_or_operational_entrypoint() -> None:
    module = ast.parse(ASSESSOR.read_text(encoding="utf-8"))
    functions = {node.name for node in ast.walk(module) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "consume" not in functions and "consume_and_operate" not in functions
    source = ASSESSOR.read_text(encoding="utf-8")
    assert "qemu-system" not in source
    assert "subprocess.Popen" not in source
    assert source.count("subprocess.run(") == 1
    assert '["git", "merge-base", "--is-ancestor"' in source


def test_python_ast_and_exact_g48_ria_structure() -> None:
    ast.parse(ASSESSOR.read_text(encoding="utf-8"))
    ast.parse(Path(__file__).read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    assert re.findall(r"^# (.+)$", report, flags=re.MULTILINE) == [
        "1. Implementation Summary", "2. Code Evidence",
        "3. Constitutional Self-Assessment", "4. Validation Matrix",
        "5. Repository Mutation Summary", "6. Certification Verdict",
    ]
    assert re.findall(r"^[1-5]\. (.+\?)$", report, flags=re.MULTILINE) == [
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    ]
