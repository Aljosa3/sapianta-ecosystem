#!/usr/bin/env python3
"""Repository-only G77-256JG post-JF live-binding tests."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
from pathlib import Path
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JG = ROOT / ".github/governance/evidence/g77_256jg_future_post_jf_commit_live_binding_and_operational_readiness_certification_v1"
FORMALIZER = JG / "analysis/G77_256JG_POST_JF_LIVE_BINDING_FORMALIZER_V1.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jg_formalizer")


def test_exact_jf_entry_scope_and_nested_authority() -> None:
    result = F.authenticate_entry()
    assert result["head"] == F.ENTRY_HEAD
    assert result["tree"] == F.ENTRY_TREE
    assert result["remote_tracking_head"] == F.ENTRY_HEAD
    assert result["index_empty"] is True
    assert result["tracked_delta"] == []
    assert set(result["untracked_jg_files"]) == F.EXPECTED_JG_FILES
    assert result["nested_head"] == F.NESTED_HEAD
    assert result["nested_tree"] == F.NESTED_TREE
    assert result["nested_detached"] is result["nested_clean"] is True


def test_committed_jf_terminal_and_option_a_reconstruct() -> None:
    result = F.reconstruct_jf()
    assert result["terminal"] == F.JF_TERMINAL_ID
    assert result["inner_seal"] == "VERIFIED"
    assert result["option_a_authority"].endswith("SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT")
    assert result["future_operational_status"] == "NOT_PROVEN_OPERATIONALLY"


def test_current_fm_owner_is_exactly_committed_and_launcher_bound() -> None:
    result = F.verify_committed_owner_binding()
    assert result["current_fm_owner_sha256"] == F.OWNER_SHA256
    assert result["committed_binding"] == "VERIFIED"
    assert result["launcher_binding"].startswith("VERIFIED")


def test_owner_hash_is_recomputed_from_committed_bytes() -> None:
    assert hashlib.sha256(F.committed_bytes(F.FM_OWNER)).hexdigest() == F.OWNER_SHA256
    assert (ROOT / F.FM_OWNER).read_bytes() == F.committed_bytes(F.FM_OWNER)


def test_exact_namespace_accepts_and_substitutions_reject() -> None:
    result = F.verify_namespaces()
    assert result["je_exact_namespace"] == "VERIFIED__ACCEPTED_REPOSITORY_ONLY"
    for key in ("vector_only_namespace", "cross_generation", "cross_operation", "namespace_escape"):
        assert result[key] == "VERIFIED__REJECTED"
    assert result["caller_selectable_namespace_count"] == 0


def test_option_a_has_no_je_special_case_or_caller_namespace() -> None:
    owner = load(ROOT / F.FM_OWNER, "g77_256jg_owner_static")
    source = inspect.getsource(owner._derive_sealed_host_repository_root)
    assert "G77_256JE" not in source
    assert "g77_256je" not in source
    assert "caller" not in source.lower()
    assert "GOVERNED_OPERATION_NAMESPACE.fullmatch" in source


def test_v2_post_commit_live_binding_closes_precommit_drift() -> None:
    result = F.verify_v2_post_commit_binding()
    assert result["result"] == "VERIFIED__POST_COMMIT_LIVE_BINDING_PASS"
    assert result["drift"] == "VERIFIED__CLOSED_AFTER_COMMITTED_JF_BASELINE"
    assert result["runtime_target"] == {"head": F.TARGET_HEAD, "tree": F.TARGET_TREE}
    assert result["certification_baseline"] == {"head": F.ENTRY_HEAD, "tree": F.ENTRY_TREE}
    assert result["du_negative_cases"] == 10
    assert result["eb_cases"] == 13
    assert result["ee_cases"] == 17


def test_target_and_certification_roles_remain_distinct() -> None:
    assert (F.TARGET_HEAD, F.TARGET_TREE) != (F.ENTRY_HEAD, F.ENTRY_TREE)


def test_projection_is_read_only_three_member_and_one_route() -> None:
    result = F.verify_projection_and_reuse()
    assert result["jc_jd_projection"].startswith("VERIFIED")
    assert len(result["harness_members"]) == 3
    assert result["production_route_before"] == 1
    assert result["production_route_after"] == 1
    assert result["production_route_delta"] == 0


def test_ex_is_reused_not_reconstructed() -> None:
    result = F.verify_projection_and_reuse()
    assert result["ex_reused"] == "VERIFIED__17_OF_17"
    assert result["ex_reconstructed"] == "VERIFIED__0"


def test_future_p11_history_and_shadow_firewalls() -> None:
    result = F.verify_firewalls()
    assert result["future_semantics"].startswith("VERIFIED__UNCHANGED")
    assert result["p11_mutation_count"] == 0
    assert result["historical_evidence_mutation_count"] == 0
    assert result["shadow_automation_status"] == "VERIFIED__ABSENT"


def test_no_production_code_or_existing_evidence_is_mutated() -> None:
    assert F.git("diff", "--name-only", "HEAD") == ""
    assert F.git("diff", "--cached", "--name-only") == ""


def test_launcher_retains_exactly_one_main_and_qemu_call_site() -> None:
    tree = ast.parse((ROOT / F.FM_LAUNCHER).read_text())
    mains = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    calls = [
        node for node in ast.walk(mains[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    assert len(mains) == 1
    assert len(calls) == 1


def test_terminal_is_canonical_inner_sealed_and_operationally_zero() -> None:
    envelope = F.load_canonical(F.TERMINAL)
    assert envelope == F.terminal_envelope()
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(F.canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == F.TERMINAL_ID
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["after"] == "VERIFIED__10_OF_18"
    assert reduction["e05"]["credit"] == "VERIFIED__0"
    assert reduction["human_review_required"] is True
    assert reduction["auto_continuable"] is False


def test_report_has_exactly_six_g48_h1_sections_and_required_metrics() -> None:
    report = F.REPORT.read_text()
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for label in (
        "Reuse Impact Assessment", "CONSTITUTIONAL_FRONTIER_DISTANCE =",
        "CONSTITUTIONAL_FRONTIER_DISTANCe =", "COGNITION_ASSISTED_HANDOFF =",
        "CCWIM_MATURITY_LEVEL", "CANDIDATE_CAPABILITY =",
        "FUTURE_OPERATIONAL_STATUS = NOT_PROVEN_OPERATIONALLY",
    ):
        assert label in report

