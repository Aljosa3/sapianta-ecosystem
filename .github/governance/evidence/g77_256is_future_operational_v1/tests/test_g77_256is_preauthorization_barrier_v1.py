#!/usr/bin/env python3
"""Focused reconstruction of the G77-256IS fail-closed Human barrier."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
IS_ROOT = ROOT / ".github/governance/evidence/g77_256is_future_operational_v1"
MATERIALIZER_PATH = IS_ROOT / "orchestration/G77_256IS_PREAUTHORIZATION_MATERIALIZER_V1.py"
REDUCER_PATH = IS_ROOT / "analysis/G77_256IS_PREAUTHORIZATION_BLOCKER_REDUCER_V1.py"
TERMINAL_PATH = IS_ROOT / "G77_256IS_SPCE_TERMINAL_PREAUTHORIZATION_BLOCKER_V1.json"
REPORT_PATH = IS_ROOT / "G77_256IS_G48_PREAUTHORIZATION_BLOCKER_REPORT_V1.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


IS = load_module(MATERIALIZER_PATH, "g77_256is_test_materializer")


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=IS.unique_object)
    assert isinstance(value, dict)
    assert raw == IS.canonical_bytes(value)
    return value


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def test_exact_ir_entry_nested_and_committed_reconstruction() -> None:
    assert git("branch", "--show-current") == IS.BRANCH
    assert git("rev-parse", "HEAD") == IS.HEAD
    assert git("rev-parse", "HEAD^{tree}") == IS.TREE
    assert git("show", "-s", "--format=%s", "HEAD") == IS.SUBJECT
    assert git("rev-parse", f"origin/{IS.BRANCH}") == IS.HEAD
    assert git("status", "--porcelain", "--untracked-files=no") == ""
    assert git("diff", "--cached", "--name-only") == ""
    reconstruction = IS.reconstruct_ir()
    assert reconstruction["status"] == "VERIFIED"
    assert reconstruction["artifact_count"] == 4
    assert reconstruction["ex_reused"] == "VERIFIED__17_OF_17"
    nested = ROOT / "sapianta_system"
    assert git("rev-parse", "HEAD", cwd=nested) == IS.NESTED_HEAD
    assert git("rev-parse", "HEAD^{tree}", cwd=nested) == IS.NESTED_TREE
    assert git("branch", "--show-current", cwd=nested) == ""
    assert git("status", "--porcelain", cwd=nested) == ""


def test_future_semantics_identity_and_v2_role_separation() -> None:
    future = IS.authenticate_future_semantics()
    assert (future["evaluation"], future["valid_from"], future["valid_until"]) == (500, 600, 1000)
    assert future["future_semantic_mutation_count"] == future["wall_clock_dependency_count"] == 0
    assert IS.derive_identity()["committed_history_collision"] == "VERIFIED__NO"
    candidate = IS_ROOT / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    runtime = IS_ROOT / "live_binding/runtime_projection/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
    assert candidate.read_bytes() == runtime.read_bytes()
    assert IS.sha256_path(candidate) == IS.FUTURE_CANDIDATE_SHA
    eb = load_unique(IS_ROOT / "live_binding/v2_readiness/bindings/G77_256IS_EB_RECEIPT_V2.json")["receipt"]
    ee = load_unique(IS_ROOT / "live_binding/v2_readiness/bindings/G77_256IS_EE_RECEIPT_V2.json")["receipt"]
    assert eb["runtime_target_selection_binding"]["head"] == IS.IF_HEAD
    assert eb["certification_baseline"] == {"head": IS.HEAD, "tree": IS.TREE}
    assert ee["runtime_target_selection_binding"] == eb["runtime_target_selection_binding"]
    assert ee["certification_baseline"] == eb["certification_baseline"]


def test_full_fm_static_readiness_reproduces_exact_bootstrap_blocker() -> None:
    context = IS.FM.fresh_context.load_context(
        IS_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        repository_root=ROOT,
    )
    with pytest.raises(RuntimeError, match="^cloud-init adapter bootstrap consumer mismatch$"):
        IS.FM.prove_guest_adapter_binding(ROOT, context)
    cloud_text = (ROOT / IS.FM.FUTURE_CLOUD_INIT).read_text(encoding="utf-8")
    assert context["guest_adapter_binding"]["bootstrap_guest_path"] not in cloud_text
    assert "G77_256IF_FUTURE_BOOTSTRAP_PROHIBITED_UNTIL_POST_COMMIT_REBIND" in cloud_text


def test_terminal_is_sealed_zero_counter_and_no_presentation() -> None:
    envelope = load_unique(TERMINAL_PATH)
    reduction = envelope["reduction"]
    assert envelope["reduction_sha256"] == hashlib.sha256(IS.canonical_bytes(reduction)).hexdigest()
    assert reduction["terminal"] == "E__CONSTITUTIONAL_REGRESSION"
    assert set(reduction["operational_counters"].values()) == {0}
    assert reduction["e05"]["after"] == "10/18"
    assert reduction["authority_boundary"]["human_authorization_action_available"] == "VERIFIED__NO"
    for name in (
        "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        "G77_256IS_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        "G77_256IS_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        "G77_256IS_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json",
    ):
        assert not (IS_ROOT / name).exists()


def test_all_is_json_canonical_and_g48_has_exact_six_headings() -> None:
    for path in sorted(IS_ROOT.rglob("*.json")):
        load_unique(path)
    headings = [line for line in REPORT_PATH.read_text(encoding="utf-8").splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary", "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment", "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary", "# 6. Certification Verdict",
    ]
    ast.parse(MATERIALIZER_PATH.read_text(encoding="utf-8"), filename=str(MATERIALIZER_PATH))
    ast.parse(REDUCER_PATH.read_text(encoding="utf-8"), filename=str(REDUCER_PATH))
    ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)


def test_no_authority_operation_receipt_or_protected_effect() -> None:
    context = load_unique(IS_ROOT / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    forbidden = [
        Path(context["pre_receipt_path"]), Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(Path(context["runtime_export_root"]) / relative for relative in context["guest_output_relative_paths"]),
    ]
    assert all(not path.exists() and not path.is_symlink() for path in forbidden)
    changed = git("status", "--short").splitlines()
    assert changed and all("g77_256is_future_operational_v1" in line for line in changed)
