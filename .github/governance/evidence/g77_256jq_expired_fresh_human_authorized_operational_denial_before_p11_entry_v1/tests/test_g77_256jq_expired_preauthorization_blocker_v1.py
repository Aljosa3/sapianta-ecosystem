#!/usr/bin/env python3
"""Focused authority-free validation for G77-256JQ."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JQ = ROOT / (
    ".github/governance/evidence/"
    "g77_256jq_expired_fresh_human_authorized_operational_denial_before_"
    "p11_entry_v1"
)
FORMALIZER = JQ / "analysis/G77_256JQ_EXPIRED_PREAUTHORIZATION_BLOCKER_FORMALIZER_V1.py"
REDUCTION = JQ / "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_REDUCTION_V1.json"
REPORT = JQ / "G77_256JQ_G48_IMPLEMENTATION_REPORT_V1.md"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


F = load(FORMALIZER, "g77_256jq_formalizer")


def test_entry_nested_and_jp_reconstruction_are_exact() -> None:
    entry = F.authenticate_entry()
    assert entry["head"] == entry["remote_tracking_head"] == F.ENTRY_HEAD
    assert entry["tree"] == F.ENTRY_TREE
    assert entry["subject"] == F.ENTRY_SUBJECT
    assert entry["nested_authority"] == {
        "origin": F.NESTED_ORIGIN, "head": F.NESTED_HEAD,
        "tree": F.NESTED_TREE, "clean": True, "detached": True,
        "tag": F.NESTED_TAG,
    }
    jp = F.reconstruct_jp()
    assert jp["terminal"] == F.JP_TERMINAL
    assert jp["production_route_count"] == "VERIFIED__1"
    assert jp["ex_reused"] == "VERIFIED__17_OF_17"
    assert jp["ex_reconstructed"] == "VERIFIED__0"
    assert jp["e05"] == "VERIFIED__11_OF_18"
    assert jp["e05_credit"] == "VERIFIED__0"
    assert jp["expired_operational_status"] == "NOT_PROVEN_OPERATIONALLY"


def test_same_generation_recovery_provenance_is_exact() -> None:
    reduction = F.build_reduction()
    recovery = reduction["recovery_provenance"]
    assert recovery["recovery_type"] == "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY"
    assert recovery["original_generation"] == "G77-256JQ"
    assert recovery["new_generation_created"] == "VERIFIED__NO"
    assert recovery["recovered_file_count"] == "VERIFIED__2"
    assert recovery["recovered_addition_count"] == "VERIFIED__624"
    assert recovery["recovered_files_at_entry"] == F.RECOVERED_JQ_FILES
    assert recovery["previous_worker_conversation_required"] == "VERIFIED__NO"
    assert recovery["previous_worker_memory_required"] == "VERIFIED__NO"


def test_exact_committed_source_identities_are_unchanged() -> None:
    assert F.authenticate_sources() == {
        path.as_posix(): digest for path, digest in F.SOURCE_SHA256.items()
    }


def test_closed_context_and_human_presentation_contracts_exclude_expired() -> None:
    assert F.assigned_string_set(F.CONTEXT_OWNER, "SUPPORTED_OPERATION_VECTORS") == F.SUPPORTED
    assert F.assigned_string_set(F.GN_PRESENTATION, "SUPPORTED_VECTORS") == F.SUPPORTED
    assert "EXPIRED" not in F.SUPPORTED
    blocker = F.formalize_blocker()
    assert blocker["expired_context_vector_supported"] == "VERIFIED__NO"
    assert blocker["expired_human_presentation_vector_supported"] == "VERIFIED__NO"
    assert blocker["human_presentation_rejection"] == "SEALED_REQUEST_VECTOR_INVALID"


def test_act_validity_domain_cannot_produce_required_expired_operation() -> None:
    blocker = F.formalize_blocker()
    assert blocker["sealed_preclaim_coordinate_unix_ns"] == 1000
    assert blocker["required_act_interval"] == {
        "valid_from_unix_ns": 100, "valid_until_unix_ns": 1000,
    }
    assert blocker["current_er_result_at_sealed_coordinate"].startswith("FUTURE_")
    assert blocker["fixed_required_interval_at_wall_clock_submission"].startswith("REJECTED_")
    assert blocker["only_fixed_interval_specialization"].startswith("JC_FUTURE__")
    assert blocker["critical_semantic_answer"] == "VERIFIED__NO"
    assert blocker["valid_until_1000_truth_table"] == {
        "999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED",
    }
    assert blocker["wall_clock_is_governed_preclaim_authority"] == "VERIFIED__NO"
    assert blocker["exact_expired_candidate_materializable_without_implementation"] == "VERIFIED__NO"
    assert blocker["exact_expired_preauthorization_checkpoint_materializable"] == "VERIFIED__NO"


def test_terminal_reduction_is_sealed_exact_and_all_counters_zero() -> None:
    envelope = json.loads(REDUCTION.read_bytes())
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(
        F.canonical_bytes(reduction)
    ).hexdigest()
    assert reduction == F.build_reduction()
    assert reduction["terminal"] == F.TERMINAL
    assert F.TERMINAL == "M__EXPIRED_PREAUTHORIZATION_ROUTE_CONTRACT_NOT_AVAILABLE"
    assert set(reduction["operational_counters"].values()) == {"VERIFIED__0"}
    assert reduction["authority_boundary"]["candidate_materialized"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["preauthorization_checkpoint_materialized"] == "VERIFIED__0"
    assert reduction["authority_boundary"]["human_authority_required"].startswith("NOT_APPLICABLE__")
    assert reduction["e05"]["after"] == "VERIFIED__11_OF_18"
    assert reduction["e05"]["credit"] == "VERIFIED__0"
    assert reduction["reuse"]["ex_reused"] == "VERIFIED__17_OF_17"
    assert reduction["reuse"]["ex_reconstructed"] == "VERIFIED__0"
    assert set(reduction["architecture"].values()) <= {
        "VERIFIED__0", "VERIFIED__1", "VERIFIED__NO"
    }
    assert reduction["auto_continuable"] is False
    assert reduction["human_review_required"] is True


def test_no_candidate_checkpoint_authority_or_operational_artifacts_exist() -> None:
    forbidden_tokens = (
        "CANDIDATE", "PREAUTHORIZATION_SAFE_STOP_CHECKPOINT",
        "HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST",
        "HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION",
        "HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE",
        "AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT",
        "SERIAL_CONSOLE", "POST_EXECUTED_QEMU_ARGV_RECEIPT",
    )
    names = {path.name for path in JQ.rglob("*") if path.is_file()}
    assert all(not any(token in name for name in names) for token in forbidden_tokens)


def test_formalizer_has_no_operational_or_authority_execution_surface() -> None:
    tree = ast.parse(FORMALIZER.read_text(encoding="utf-8"))
    imports = {
        alias.name for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names
    }
    assert not {"time", "datetime", "socket", "os"} & imports
    text = FORMALIZER.read_text(encoding="utf-8")
    for forbidden in ("qemu-system", "PRE_OPERATIONAL", "claim_and_invoke_once(", "submit_human_act("):
        assert forbidden not in text


def test_g48_exactly_six_h1_reuse_questions_and_compact_ccwim() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert [line for line in report.splitlines() if line.startswith("# ")] == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    for token in (
        "## Reuse Impact Assessment",
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
        "## Compact CCWIM", "AUTO_CONTINUABLE = NO",
        "HUMAN_REVIEW_REQUIRED = YES", F.TERMINAL,
    ):
        assert token in report


def test_mutation_scope_is_evidence_only_and_index_is_empty() -> None:
    changed = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    assert {line[3:] for line in changed} == {
        path.as_posix() for path in F.JQ_FILES
    }
    assert subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True
    ).strip() == ""
